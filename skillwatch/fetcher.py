"""Fetch URL content and extract text using trafilatura."""

import hashlib
import re
import time

import requests
import trafilatura

from .ssrf import SSRFError, validate_url

_DEFAULT_TIMEOUT = 10
_DEFAULT_DELAY = 1.0
_MAX_RESPONSE_SIZE = 5 * 1024 * 1024  # 5 MB
_DEFAULT_USER_AGENT = "SkillWatch/0.1 (+https://github.com/kuzivaai/skillwatch)"

# Strip ANSI escape sequences from fetched content
_ANSI_RE = re.compile(r"\x1b\[[0-9;]*[a-zA-Z]")


class FetchError(Exception):
    """Raised when a URL cannot be fetched."""


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
    # SSRF check
    try:
        validate_url(url)
    except SSRFError as exc:
        return FetchResult(url=url, error=str(exc))

    # Fetch
    try:
        resp = requests.get(
            url,
            timeout=timeout,
            headers={"User-Agent": user_agent},
            allow_redirects=True,
            stream=True,
        )

        # Check redirects for SSRF
        if resp.history:
            for r in resp.history:
                try:
                    validate_url(r.url)
                except SSRFError as exc:
                    return FetchResult(url=url, error=f"Redirect blocked: {exc}")
            try:
                validate_url(resp.url)
            except SSRFError as exc:
                return FetchResult(url=url, error=f"Final redirect blocked: {exc}")

        # Read with size limit
        content_bytes = b""
        for chunk in resp.iter_content(chunk_size=8192):
            content_bytes += chunk
            if len(content_bytes) > max_size:
                return FetchResult(
                    url=url,
                    status_code=resp.status_code,
                    error=f"Response exceeds {max_size // (1024*1024)} MB limit",
                )

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
        # Fallback: use raw text (strip HTML tags roughly)
        extracted = trafilatura.extract(raw_html, include_links=True, no_fallback=False)

    if not extracted:
        # Last resort: just note we got HTML but couldn't extract
        extracted = f"[SkillWatch: could not extract text from {len(raw_html)} bytes of HTML]"

    # Clean extracted text
    extracted = _ANSI_RE.sub("", extracted)
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


def fetch_urls(
    urls: list[str],
    delay: float = _DEFAULT_DELAY,
    timeout: int = _DEFAULT_TIMEOUT,
    user_agent: str = _DEFAULT_USER_AGENT,
) -> list[FetchResult]:
    """Fetch multiple URLs with a delay between requests."""
    results = []
    for i, url in enumerate(urls):
        if i > 0 and delay > 0:
            time.sleep(delay)
        results.append(fetch_url(url, timeout=timeout, user_agent=user_agent))
    return results


def _normalise_whitespace(text: str) -> str:
    """Collapse whitespace sequences to single spaces, strip trailing whitespace per line."""
    lines = []
    for line in text.splitlines():
        line = " ".join(line.split())
        if line:
            lines.append(line)
    return "\n".join(lines)
