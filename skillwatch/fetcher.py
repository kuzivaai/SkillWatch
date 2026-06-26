"""Fetch URL content and extract text using trafilatura."""

import hashlib
import re
from urllib.parse import urljoin

import requests
import trafilatura

from .ssrf import SSRFError, validate_url

_DEFAULT_TIMEOUT = 10
_MAX_RESPONSE_SIZE = 5 * 1024 * 1024  # 5 MB
_MAX_REDIRECTS = 5
_DEFAULT_USER_AGENT = "SkillWatch/0.1 (+https://github.com/kuzivaai/SkillWatch)"

# Strip ANSI/VT escape sequences from fetched content.
# Covers CSI, OSC (clipboard write risk), DCS, C1 control codes.
_ESCAPE_RE = re.compile(
    r"\x1b\[[0-9;]*[ -/]*[@-~]"       # CSI sequences
    r"|\x1b\][^\x07\x1b]*[\x07]"       # OSC sequences (BEL-terminated)
    r"|\x1b\][^\x1b]*\x1b\\"           # OSC sequences (ST-terminated)
    r"|\x1bP[^\x1b]*\x1b\\"            # DCS sequences
    r"|\x1b[@-Z\\-_]"                  # Fe sequences
    r"|\x9b[0-9;]*[@-~]"              # C1 CSI (8-bit)
    r"|\x9d[^\x9c]*\x9c"              # C1 OSC (8-bit)
)


class FetchResult:
    __slots__ = ("url", "content_text", "content_hash", "raw_html", "raw_html_hash", "status_code", "error")

    def __init__(
        self, url: str, content_text: str | None = None, content_hash: str = "",
        raw_html: str | None = None, raw_html_hash: str = "",
        status_code: int | None = None, error: str | None = None,
    ):
        self.url = url
        self.content_text = content_text
        self.content_hash = content_hash
        self.raw_html = raw_html
        self.raw_html_hash = raw_html_hash
        self.status_code = status_code
        self.error = error

    @property
    def ok(self) -> bool:
        return self.error is None and self.content_text is not None


def fetch_url(
    url: str,
    timeout: int = _DEFAULT_TIMEOUT,
    user_agent: str = _DEFAULT_USER_AGENT,
    max_size: int = _MAX_RESPONSE_SIZE,
) -> FetchResult:
    """Fetch a URL, extract text content, and compute hashes."""
    # SSRF check on initial URL
    try:
        validate_url(url)
    except SSRFError as exc:
        return FetchResult(url=url, error=str(exc))

    # Fetch with manual redirect following (validate each hop BEFORE following)
    try:
        current_url = url
        for _ in range(_MAX_REDIRECTS + 1):
            resp = requests.get(
                current_url,
                timeout=timeout,
                headers={"User-Agent": user_agent},
                allow_redirects=False,
                stream=True,
            )

            if resp.is_redirect:
                location = resp.headers.get("Location", "")
                if not location:
                    return FetchResult(url=url, error="Redirect with no Location header")
                next_url = urljoin(current_url, location)
                try:
                    validate_url(next_url)
                except SSRFError as exc:
                    return FetchResult(url=url, error=f"Redirect blocked: {exc}")
                resp.close()
                current_url = next_url
                continue

            break
        else:
            return FetchResult(url=url, error=f"Too many redirects (>{_MAX_REDIRECTS})")

        # Read with size limit
        chunks = []
        total_size = 0
        for chunk in resp.iter_content(chunk_size=8192):
            chunks.append(chunk)
            total_size += len(chunk)
            if total_size > max_size:
                return FetchResult(
                    url=url,
                    status_code=resp.status_code,
                    error=f"Response exceeds {max_size // (1024*1024)} MB limit",
                )

        content_bytes = b"".join(chunks)
        resp.close()

        if resp.status_code >= 400:
            return FetchResult(
                url=url,
                status_code=resp.status_code,
                error=f"HTTP {resp.status_code}",
            )

        raw_html = content_bytes.decode(resp.encoding or "utf-8", errors="replace")

    except requests.exceptions.Timeout:
        return FetchResult(url=url, error=f"Timeout after {timeout}s")
    except requests.exceptions.ConnectionError as exc:
        return FetchResult(url=url, error=f"Connection error: {exc}")
    except requests.exceptions.RequestException as exc:
        return FetchResult(url=url, error=f"Request error: {exc}")

    # Extract text via trafilatura
    extracted = trafilatura.extract(raw_html, include_links=True, include_tables=True)

    if not extracted:
        extracted = trafilatura.extract(raw_html, include_links=True, no_fallback=False)

    if not extracted:
        extracted = f"[SkillWatch: could not extract text from {len(raw_html)} bytes of HTML]"

    # Strip escape sequences (defence layer 1 — also stripped at display time)
    extracted = strip_escape_sequences(extracted)
    extracted = _normalise_whitespace(extracted)

    # Compute hashes
    content_hash = hashlib.sha256(extracted.encode("utf-8")).hexdigest()
    raw_html_hash = hashlib.sha256(raw_html.encode("utf-8")).hexdigest()

    return FetchResult(
        url=url,
        content_text=extracted,
        content_hash=content_hash,
        raw_html=raw_html,
        raw_html_hash=raw_html_hash,
        status_code=resp.status_code,
    )


def strip_escape_sequences(text: str) -> str:
    """Strip ANSI/VT escape sequences from text. Used at fetch and display time."""
    return _ESCAPE_RE.sub("", text)


def _normalise_whitespace(text: str) -> str:
    """Collapse whitespace sequences to single spaces, strip trailing whitespace per line."""
    lines = []
    for line in text.splitlines():
        line = " ".join(line.split())
        if line:
            lines.append(line)
    return "\n".join(lines)
