"""Extract URLs from SKILL.md files, MCP configs, and URL lists."""

import ipaddress
import json
import re
from pathlib import Path
from urllib.parse import urlparse

import yaml

# Matches markdown links [text](url).
# Allows one level of balanced parentheses inside the URL (CommonMark spec).
_MD_LINK_RE = re.compile(r"\[.*?\]\((https?://(?:[^\s()]*\([^\s()]*\))*[^\s()]*)\)")
_RAW_URL_RE = re.compile(r"(?<!\()(https?://[^\s\)\]\"'>]+)")


def extract_urls_from_file(path: str) -> list[dict]:
    """Extract URLs from a file. Returns list of {url, source_type, source_path}."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"File not found: {path}")

    suffix = p.suffix.lower()
    name = p.name.lower()

    if name == "skill.md" or suffix == ".md":
        return _extract_from_markdown(p)
    elif suffix == ".json":
        return _extract_from_json(p)
    elif suffix in (".yaml", ".yml"):
        return _extract_from_yaml(p)
    elif suffix == ".txt":
        return _extract_from_url_list(p)
    else:
        # Try markdown extraction as fallback
        return _extract_from_markdown(p)


def extract_urls_from_text(text: str, source_type: str = "text", source_path: str = "") -> list[dict]:
    """Extract URLs from raw text."""
    urls = set()
    for match in _MD_LINK_RE.finditer(text):
        urls.add(match.group(1))
    for match in _RAW_URL_RE.finditer(text):
        urls.add(match.group(1))

    return _build_results(urls, source_type, source_path)


def _extract_from_markdown(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8", errors="replace")
    return extract_urls_from_text(text, "skill_md", str(path))


_MAX_CONFIG_SIZE = 1_000_000  # 1 MB cap for config files (billion-laughs mitigation)


def _extract_from_json(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8", errors="replace")
    urls = set()

    if len(text) > _MAX_CONFIG_SIZE:
        return _build_results(urls, "mcp_config", str(path))

    try:
        data = json.loads(text)
        _walk_json(data, urls)
    except (json.JSONDecodeError, RecursionError):
        pass

    # Also extract any raw URLs from the text (catches URLs in string values)
    for match in _RAW_URL_RE.finditer(text):
        urls.add(match.group(1))

    return _build_results(urls, "mcp_config", str(path))


def _extract_from_yaml(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8", errors="replace")
    urls = set()

    if len(text) > _MAX_CONFIG_SIZE:
        return _build_results(urls, "mcp_config", str(path))

    try:
        data = yaml.safe_load(text)
        if isinstance(data, (dict, list)):
            _walk_json(data, urls)
    except (yaml.YAMLError, RecursionError, MemoryError):
        pass

    for match in _RAW_URL_RE.finditer(text):
        urls.add(match.group(1))

    return _build_results(urls, "mcp_config", str(path))


def _extract_from_url_list(path: Path) -> list[dict]:
    urls = set()
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            if re.match(r"https?://", line):
                urls.add(line)
    return _build_results(urls, "manual", str(path))


def _walk_json(obj: object, urls: set[str], _depth: int = 0) -> None:
    """Recursively extract URLs from JSON-like structures."""
    if _depth > 50:
        return
    if isinstance(obj, str):
        for match in _RAW_URL_RE.finditer(obj):
            urls.add(match.group(1))
    elif isinstance(obj, dict):
        for v in obj.values():
            _walk_json(v, urls, _depth + 1)
    elif isinstance(obj, list):
        for item in obj:
            _walk_json(item, urls, _depth + 1)


def _build_results(urls: set[str], source_type: str, source_path: str) -> list[dict]:
    """Lightweight URL validation (scheme + obvious IP blocks). Full SSRF check at fetch time."""
    results = []
    for url in sorted(urls):
        url = url.rstrip(".,;:!?")
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            continue
        if not parsed.hostname:
            continue
        # Block obvious private IPs at parse time (no DNS resolution)
        try:
            ip = ipaddress.ip_address(parsed.hostname)
            if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
                continue
        except ValueError:
            pass  # Hostname, not IP — allow through, SSRF checked at fetch time
        results.append({
            "url": url,
            "source_type": source_type,
            "source_path": source_path,
        })
    return results
