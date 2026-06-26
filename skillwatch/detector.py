"""Rule-based suspicious pattern detection on content changes."""

import re

from bs4 import BeautifulSoup


# Patterns that indicate potentially malicious content changes
_SUSPICIOUS_COMMANDS = re.compile(
    r"\b(curl\s|wget\s|pip\s+install|npm\s+install|npx\s|"
    r"bash\s+-c|sh\s+-c|eval\s*\(|exec\s*\(|os\.system|"
    r"subprocess\.|powershell|iex\s|invoke-expression|"
    r"python\s+-c|ruby\s+-e|node\s+-e)\b",
    re.IGNORECASE,
)

_BASE64_PATTERN = re.compile(r"[A-Za-z0-9+/]{40,}={0,2}")

_DATA_EXFIL_PATTERN = re.compile(
    r"\b(api[_-]?key|secret|token|password|credential|auth|"
    r"\.env|private[_-]?key|access[_-]?key)\b",
    re.IGNORECASE,
)

_DOMAIN_CHANGE_RE = re.compile(r"https?://([a-zA-Z0-9.-]+)")

_SUSPICIOUS_SCRIPT_KEYWORDS = [
    "eval(", "document.cookie", "fetch(", "xmlhttprequest",
    "websocket", "atob(", "btoa(",
]


class Flag:
    """A single suspicious finding."""
    __slots__ = ("code", "severity", "description", "evidence")

    def __init__(self, code: str, severity: str, description: str, evidence: str = ""):
        self.code = code
        self.severity = severity
        self.description = description
        self.evidence = evidence


def detect_suspicious_changes(
    old_text: str | None,
    new_text: str,
    diff_text: str,
    old_html: str | None = None,
    new_html: str | None = None,
) -> list[Flag]:
    """Analyse content changes and return a list of suspicious flags."""
    flags: list[Flag] = []

    # Only added lines in the diff
    added_lines = "\n".join(
        line[1:] for line in diff_text.splitlines()
        if line.startswith("+") and not line.startswith("+++")
    )

    if not added_lines.strip():
        return flags

    # 1. New download/execution commands
    commands = _SUSPICIOUS_COMMANDS.findall(added_lines)
    if commands:
        flags.append(Flag(
            code="new_exec_command",
            severity="critical",
            description="New download or code execution command detected",
            evidence="; ".join(set(c.strip() for c in commands[:5])),
        ))

    # 2. New base64-encoded strings (potential obfuscated payloads)
    b64_matches = _BASE64_PATTERN.findall(added_lines)
    if b64_matches:
        flags.append(Flag(
            code="new_base64",
            severity="warning",
            description="New base64-encoded string detected (possible obfuscated payload)",
            evidence=f"{len(b64_matches)} occurrence(s), first: {b64_matches[0][:40]}...",
        ))

    # 3. Credential/secret references in new content
    cred_matches = _DATA_EXFIL_PATTERN.findall(added_lines)
    if cred_matches:
        flags.append(Flag(
            code="credential_reference",
            severity="warning",
            description="New references to credentials or secrets",
            evidence="; ".join(set(cred_matches[:5])),
        ))

    # 4. Domain changes (URLs in old content point to different domains in new content)
    if old_text:
        old_domains = set(_DOMAIN_CHANGE_RE.findall(old_text))
        new_domains = set(_DOMAIN_CHANGE_RE.findall(new_text))
        added_domains = new_domains - old_domains
        if added_domains:
            flags.append(Flag(
                code="new_domains",
                severity="warning",
                description="New external domains referenced",
                evidence="; ".join(sorted(added_domains)[:10]),
            ))

    # 5. Large content deletion (>50% removed)
    if old_text:
        old_len = len(old_text)
        new_len = len(new_text)
        if old_len > 100 and new_len < old_len * 0.5:
            pct = round((1 - new_len / old_len) * 100)
            flags.append(Flag(
                code="major_deletion",
                severity="warning",
                description=f"{pct}% of content was removed",
                evidence=f"Old: {old_len} chars → New: {new_len} chars",
            ))

    # 6. HTML-specific checks — compare old vs new to avoid false positives
    if new_html:
        flags.extend(_check_html_changes(old_html, new_html))

    return flags


def _check_html_changes(old_html: str | None, new_html: str) -> list[Flag]:
    """Compare old and new HTML to flag only NEWLY INTRODUCED suspicious elements.

    This prevents false positives from pre-existing scripts, iframes, etc.
    """
    flags: list[Flag] = []

    new_soup = BeautifulSoup(new_html, "html.parser")
    old_suspicious_scripts = set()
    old_iframe_srcs = set()
    old_hidden_texts = set()

    if old_html:
        old_soup = BeautifulSoup(old_html, "html.parser")
        old_suspicious_scripts = _extract_suspicious_script_contents(old_soup)
        old_iframe_srcs = {f.get("src", "") for f in old_soup.find_all("iframe")}
        old_hidden_texts = _extract_hidden_texts(old_soup)

    # Suspicious scripts — only flag NEW ones
    new_suspicious = _extract_suspicious_script_contents(new_soup)
    added_scripts = new_suspicious - old_suspicious_scripts
    if added_scripts:
        sample = next(iter(added_scripts))
        flags.append(Flag(
            code="suspicious_script",
            severity="critical",
            description=f"{len(added_scripts)} new script(s) with suspicious content",
            evidence=sample[:100],
        ))

    # Iframes — only flag NEW ones
    new_iframe_srcs = {f.get("src", "") for f in new_soup.find_all("iframe")}
    added_iframes = new_iframe_srcs - old_iframe_srcs
    if added_iframes:
        flags.append(Flag(
            code="iframe_detected",
            severity="warning",
            description=f"{len(added_iframes)} new iframe(s) detected",
            evidence="; ".join(sorted(added_iframes)[:3]),
        ))

    # Hidden elements — only flag NEW ones
    new_hidden_texts = _extract_hidden_texts(new_soup)
    added_hidden = new_hidden_texts - old_hidden_texts
    if added_hidden:
        flags.append(Flag(
            code="hidden_content",
            severity="info",
            description="New hidden HTML elements contain text",
            evidence=next(iter(added_hidden))[:200],
        ))

    return flags


def _extract_suspicious_script_contents(soup: BeautifulSoup) -> set[str]:
    """Extract text content of suspicious script tags as a set for comparison."""
    result = set()
    for script in soup.find_all("script"):
        if script.string:
            lower = script.string.lower()
            if any(kw in lower for kw in _SUSPICIOUS_SCRIPT_KEYWORDS):
                result.add(script.string.strip())
    return result


def _extract_hidden_texts(soup: BeautifulSoup) -> set[str]:
    """Extract text from hidden elements as a set for comparison."""
    result = set()
    for elem in soup.find_all(style=re.compile(r"display:\s*none|visibility:\s*hidden")):
        text = elem.get_text(strip=True)
        if text:
            result.add(text)
    return result


def severity_rank(severity: str) -> int:
    """Return numeric rank for sorting (higher = more severe)."""
    return {"info": 0, "warning": 1, "critical": 2}.get(severity, 0)


def max_severity(flags: list[Flag]) -> str:
    """Return the highest severity among flags."""
    if not flags:
        return "info"
    return max((f.severity for f in flags), key=severity_rank)
