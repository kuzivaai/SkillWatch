"""Rule-based suspicious pattern detection on content changes."""

import re

from bs4 import BeautifulSoup
from confusable_homoglyphs import confusables


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

# --- Pattern 7: Prompt injection ---
# Comprehensive patterns derived from ATR-2026-00001 (Agent Threat Rules, MIT licensed).
# 38 patterns covering English, German, Spanish, French, Arabic, Russian, Serbian/Croatian,
# plus obfuscation techniques (base64, zero-width, spaced letters, URL-encoding).
# Only the subset applicable to static web page text is included; patterns requiring
# conversation context (praise-redirect, task switching) are excluded.
_PROMPT_INJECTION_PATTERNS: list[re.Pattern[str]] = [re.compile(p, re.IGNORECASE) for p in [
    # English instruction override (broad)
    r"\b(ignore|disregard|forget|override|bypass|skip|abandon|drop|cancel|suppress|nullify|void|revoke|dismiss|discard|reject)\s+"
    r"(all\s+)?(the\s+|your\s+|my\s+|any\s+|these\s+|those\s+)?"
    r"(previous|prior|above|earlier|preceding|original|existing|current|initial|default|given|assigned|preset|established)?\s*"
    r"(instructions?|prompts?|rules?|guidelines?|directives?|constraints?|context|programming|training|protocols?|policies|configuration|parameters|boundaries|guardrails?|safeguards?|restrictions?|tasks?|assignments?|information|directions?|orders?|commands?)",
    # Forget-everything shorthand
    r"\b(forget|ignore|disregard)\s+(everything|all\s+(of\s+)?that|all\s+about|about\s+all|that|what\s+(I|we|you)\s+(said|told|asked|mentioned))\s*(before|earlier|previously|above|\.|,|!|$)",
    # Broad forget-everything variants
    r"\b(forget|ignore|disregard|discard)\s+(about\s+)?(everything|all|that|this|what\s+was|what\s+I|anything\s+you)\s*(previously|before|earlier|said|told|above|prior|were|was|have)?",
    # Ignore-above with action verb
    r"\b(ignore|forget|disregard)\s+(the\s+)?(above|everything\s+above|what\s+came\s+before|what\s+was\s+said)\s*(and|,|\.|;|\b(say|print|write|output|tell|just|instead))",
    # System prompt extraction
    r"(reveal|show|display|output|print|repeat|provide|give|share|tell|what\s+are|what\s+were|what\s+is)\s+(me\s+)?(your|the|all)\s+(secret|hidden|internal|system|original|previous|initial|complete|full|given|guard|entire)?\s*(instructions?|prompts?|passwords?|secrets?|embeddings?|configuration|directives?|guidelines?|rules)",
    # Persona switching
    r"\b(you\s+are\s+now|you\s+have\s+become|you\s+will\s+act\s+as|you\s+will\s+be|you\s+shall\s+be|transform\s+into|switch\s+to\s+being|become|morph\s+into|adopt\s+the\s+persona|now\s+you\s+are)\s+(a|an|the|my)?\s*[a-zA-Z\u00C0-\u024F]+",
    # Pretend-to-be-evil
    r"(pretend|imagine)\s+(you\s+)?(are|can|could|to\s+be)\s+(a\s+|an\s+)?(evil|malicious|unrestricted|unfiltered|bad|rogue|dangerous|dark|unethical)",
    # Role redefinition
    r"\b(your\s+new\s+role|your\s+new\s+purpose|your\s+new\s+identity|your\s+new\s+persona|your\s+real\s+purpose|your\s+true\s+identity|your\s+actual\s+role)\s+(is|shall\s+be|will\s+be)\b",
    # Temporal override
    r"(from\s+now\s+on|from\s+this\s+point|starting\s+now|starting\s+immediately|henceforth|hereafter|going\s+forward|for\s+the\s+rest\s+of|until\s+I\s+say\s+otherwise),?\s+(you|your|act|behave|respond|operate|function|answer|reply|work)",
    # New instruction assignment (extended: delimiter OR 'is/are')
    r"\b(new|updated|revised|replacement|corrected|actual|real|true|overriding)\s+(instructions?|rules?|directives?|guidelines?|orders?|commands?)\s*([:=\-]|\b(is|are)\b)",
    # Authoritative compliance demands
    r"\b(you\s+(must|shall|will|need\s+to|have\s+to|are\s+(required|obligated|commanded|ordered)\s+to)\s+(obey|comply|listen|submit|respond\s+to|follow)\s+(me|my|this|these|the\s+following|every|all)|I\s+(command|order|demand|direct|instruct|require)\s+you\s+to)\b",
    # Hypothetical restriction removal
    r"(pretend|act\s+as\s+if|imagine|assume|suppose|consider|envision|behave\s+as\s+though)\s+(you\s+)?(are|have|were|had|can|could)\s+(no|zero|removed|disabled|eliminated|free\s+from|without|lacking|void\s+of|devoid\s+of)\s+(restrictions?|limits?|limitations?|boundaries|guardrails?|safety|filters?|constraints?|rules?|guidelines?|content\s+policy)",
    # Fake system-level delimiters
    r"(\[\s*(SYSTEM|INST|INSTRUCTION|SYS|ADMIN|ROOT|OVERRIDE|CONTROL|PRIORITY|URGENT)\s*\]|<<\s*(SYS|SYSTEM|INST)\s*>>|\{\{\s*(SYSTEM|INSTRUCTION|OVERRIDE)\s*\}\})",
    # --- Obfuscation patterns ---
    # Base64-encoded injection keywords (ignore, disregard, override, forget, bypass, system prompt)
    r"(aWdub3Jl|ZGlzcmVnYXJk|b3ZlcnJpZGU|Zm9yZ2V0|YnlwYXNz|c3lzdGVtIHByb21wdA|aWdub3JlIHByZXZpb3Vz|aWdub3JlIGFsbCBwcmV2aW91cw)",
    # Cyrillic/Greek homoglyph substitution in injection keywords
    r"[\u0400-\u04FF\u0370-\u03FF\u2100-\u214F]+(gn[\u0400-\u04FF\u0370-\u03FF]re|verr[\u0400-\u04FF\u0370-\u03FF]de|yst[\u0400-\u04FF\u0370-\u03FF]m)",
    # Zero-width character insertion splitting 'ignore'
    r"i[\u200B\u200C\u200D\uFEFF\u2060]+g[\u200B\u200C\u200D\uFEFF\u2060]*n[\u200B\u200C\u200D\uFEFF\u2060]*o[\u200B\u200C\u200D\uFEFF\u2060]*r[\u200B\u200C\u200D\uFEFF\u2060]*e",
    # URL-encoded or hex-escaped injection keywords
    r"(%69%67%6[eE]%6[fF]%72%65|%64%69%73%72%65%67%61%72%64|%6[fF]%76%65%72%72%69%64%65|\\x69\\x67\\x6e\\x6f\\x72\\x65)",
    # Spaced-out injection keywords
    r"(i\s+g\s+n\s+o\s+r\s+e|f\s+o\s+r\s+g\s+e\s+t|o\s+v\s+e\s+r\s+r\s+i\s+d\s+e|b\s+y\s+p\s+a\s+s\s+s|s\s+y\s+s\s+t\s+e\s+m|d\s+i\s+s\s+r\s+e\s+g\s+a\s+r\s+d)",
    # ALL-CAPS embedded commands
    r"(DO\s+NOT\s+(ANSWER|LOOK|READ|USE|FOLLOW|CHECK|RESPOND)|FORGET\s+EVERYTHING|IGNORE\s+ALL)",
    # Markdown-hidden injection
    r"(```\s*(system|instruction|override|hidden)[\s\S]{0,200}```|\*\*\*[\s\S]{0,10}(ignore|override|disregard)[\s\S]{0,200}\*\*\*)",
    # Bare imperative "act as" (not in ATR, which requires "I want you to act as")
    r"\bact\s+as\s+(a\s+|an\s+)?[a-zA-Z\u00C0-\u024F]+",
    # Decode-and-execute instructions
    r"(decode|interpret|execute|run|process|follow|read)\s+(this|the\s+following)?\s*:?\s*[A-Za-z0-9+/]{20,}={0,2}",
    # --- Multilingual injection (German, Spanish, French, Arabic, Russian, Serbian/Croatian) ---
    # German (whitespace fix: added \s* between optional groups 2 and 3)
    r"(ignoriere|vergiss|missachte|umgehe|verwirf)\s+(alle[sn]?|die\s+)?\s*(vorherigen?|bisherigen?|aktuellen?|bestehenden?)?\s*(Anweisungen|Regeln|Richtlinien|Anordnungen|Vorgaben|Instruktionen|Beschraenkungen|Aufgaben|Informationen|alles)",
    r"(vergiss|ignoriere|vergessen\s+Sie)\s+(alles|das|dies)\s*(was|davor|zuvor|vorher|bisher)?\b",
    r"neue\s+(Aufgabe|Aufgaben|Anweisung|Anweisungen)\s*(folgen|kommen|sind|:|,)",
    r"(ignorieren\s+Sie|vergessen\s+Sie|beachten\s+Sie\s+nicht)\s+(die\s+)?(obigen?|vorherigen?|bisherigen?)?\s*(Anweisungen|Regeln|Richtlinien|alles)",
    r"ACHTUNG\s*[-:!]?\s*(STOPP|STOP|HALT)\s*[-:!]?",
    # Spanish
    r"(ignora|ignorar|olvida|olvidar|descarta|descartar|omite|omitir|anula|anular)\s+(todas?\s+)?(las?\s+)?(instrucciones|reglas|directrices|restricciones|indicaciones|limitaciones)\s*(previas|anteriores|originales|existentes|actuales)?",
    # French
    r"(oubliez?|ignorez?|ne\s+tenez\s+pas\s+compte)\s+(de\s+)?(toutes?\s+)?(les\s+)?(instructions?|regles|consignes|directives)\s*(precedentes?|anterieures?|ci-dessus)?",
    # Arabic
    "\u062A\u062C\u0627\u0647\u0644|\u0627\u0646\u0633\u064E|\u062A\u062E\u0637\u0651\u0649|\u0623\u0644\u063A\u0650|\u0623\u0647\u0645\u0644|\u0627\u062A\u0631\u0643|\u0627\u0633\u0642\u0637",
    # Russian
    r"(\u0437\u0430\u0431\u0443\u0434\u044C|\u0437\u0430\u0431\u0443\u0434\u044C\u0442\u0435|\u0438\u0433\u043D\u043E\u0440\u0438\u0440\u0443\u0439|\u0438\u0433\u043D\u043E\u0440\u0438\u0440\u0443\u0439\u0442\u0435|\u043F\u0440\u043E\u0438\u0433\u043D\u043E\u0440\u0438\u0440\u0443\u0439|\u043E\u0442\u0431\u0440\u043E\u0441\u044C|\u043E\u0442\u0431\u0440\u043E\u0441\u044C\u0442\u0435)\s+(\u0432\u0441\u0435|\u0432\u0441\u0451|\u043F\u0440\u0435\u0434\u044B\u0434\u0443\u0449\u0438\u0435|\u043F\u0440\u0435\u0436\u043D\u0438\u0435)?\s*(\u0438\u043D\u0441\u0442\u0440\u0443\u043A\u0446\u0438\u0438|\u043F\u0440\u0430\u0432\u0438\u043B\u0430|\u0443\u043A\u0430\u0437\u0430\u043D\u0438\u044F|\u043A\u043E\u043C\u0430\u043D\u0434\u044B|\u043E\u0433\u0440\u0430\u043D\u0438\u0447\u0435\u043D\u0438\u044F)",
    # Serbian/Croatian
    r"(zaboravi|ignoriraj|zanemari|presko\u010Di|preskoci)\s+(sve|prethodne|ranije)?\s*(instrukcije|pravila|upute|naredbe|ograni\u010Denja|ogranicenja|instrukci)",
]]

# --- Pattern 8: Unicode confusable characters ---
# Uses the confusable_homoglyphs library backed by the Unicode Consortium's
# official confusables database, covering thousands of confusable characters
# across all scripts — far more comprehensive than a hand-built map.

# --- Pattern 9: Data URI detection ---
_DATA_URI_RE = re.compile(
    r"data:\s*(?:text/html|application/javascript|text/javascript)"
    r"[^\"'\s>]*",
    re.IGNORECASE,
)


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

    # 7. Prompt injection (ATR-derived, 32 patterns covering 7 languages + obfuscation)
    # This is the core MCP/AI attack vector: page content that tells
    # an AI agent to ignore its instructions.
    injection_evidence: list[str] = []
    for pattern in _PROMPT_INJECTION_PATTERNS:
        match = pattern.search(added_lines)
        if match:
            injection_evidence.append(match.group(0).strip()[:80])
            if len(injection_evidence) >= 3:
                break
    if injection_evidence:
        flags.append(Flag(
            code="prompt_injection",
            severity="critical",
            description="Prompt injection language detected in new content",
            evidence="; ".join(injection_evidence)[:200],
        ))

    # 8. Unicode homoglyph characters in added text
    homoglyph_hits = _find_confusables(added_lines)
    if homoglyph_hits:
        flags.append(Flag(
            code="unicode_homoglyph",
            severity="warning",
            description="Text contains Unicode characters that visually imitate ASCII letters",
            evidence="; ".join(
                f"U+{cp:04X} ({chr(cp)}) looks like '{ascii_char}'"
                for cp, ascii_char in homoglyph_hits[:5]
            ),
        ))

    # 9. Data URI payloads in added text
    data_uri_matches = _DATA_URI_RE.findall(added_lines)
    if data_uri_matches:
        flags.append(Flag(
            code="data_uri_payload",
            severity="warning",
            description="Data URI with executable content type detected",
            evidence=data_uri_matches[0][:100],
        ))

    return flags


def _find_confusables(text: str) -> list[tuple[int, str]]:
    """Find Unicode characters that visually imitate Latin letters.

    Uses the confusable_homoglyphs library backed by the Unicode Consortium's
    official confusables database. Returns (codepoint, latin_equivalent) tuples.
    Only flags characters from non-Latin scripts (Cyrillic, Greek, etc.) that
    have Latin lookalikes. Skips COMMON script (digits, punctuation) to avoid
    false positives on normal content.
    """
    result = confusables.is_confusable(text, greedy=True, preferred_aliases=["latin"])
    if not result:
        return []

    # Scripts that indicate actual homoglyph attacks.
    # COMMON (digits, punctuation) and LATIN are excluded — they are legitimate.
    _SUSPICIOUS_SCRIPTS = frozenset({
        "CYRILLIC", "GREEK", "ARMENIAN", "CHEROKEE",
        "COPTIC", "MYANMAR", "GEORGIAN", "ETHIOPIC",
    })

    found: dict[int, str] = {}
    for entry in result:
        alias = entry.get("alias", "")
        if alias not in _SUSPICIOUS_SCRIPTS:
            continue

        ch = entry["character"]
        cp = ord(ch)
        if cp not in found:
            latin_match = ""
            for h in entry.get("homoglyphs", []):
                if h.get("n", "").startswith("LATIN"):
                    latin_match = h["c"]
                    break
            found[cp] = latin_match or "?"
    return list(found.items())


def _check_html_changes(old_html: str | None, new_html: str) -> list[Flag]:
    """Compare old and new HTML to flag only NEWLY INTRODUCED suspicious elements.

    This prevents false positives from pre-existing scripts, iframes, etc.
    """
    flags: list[Flag] = []

    new_soup = BeautifulSoup(new_html, "html.parser")
    old_suspicious_scripts = set()
    old_iframe_srcs = set()
    old_hidden_texts = set()
    old_meta_refreshes: set[str] = set()
    old_data_uri_iframes: set[str] = set()

    if old_html:
        old_soup = BeautifulSoup(old_html, "html.parser")
        old_suspicious_scripts = _extract_suspicious_script_contents(old_soup)
        old_iframe_srcs = {f.get("src", "") for f in old_soup.find_all("iframe")}
        old_hidden_texts = _extract_hidden_texts(old_soup)
        old_meta_refreshes = _extract_meta_refreshes(old_soup)
        old_data_uri_iframes = _extract_data_uri_sources(old_soup)

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

    # Meta refresh redirects — only flag NEW ones (pattern 10)
    new_meta_refreshes = _extract_meta_refreshes(new_soup)
    added_refreshes = new_meta_refreshes - old_meta_refreshes
    if added_refreshes:
        flags.append(Flag(
            code="meta_refresh_redirect",
            severity="warning",
            description="New meta refresh redirect detected",
            evidence="; ".join(sorted(added_refreshes)[:3]),
        ))

    # Data URI iframes/embeds — only flag NEW ones
    new_data_uri_iframes = _extract_data_uri_sources(new_soup)
    added_data_uris = new_data_uri_iframes - old_data_uri_iframes
    if added_data_uris:
        flags.append(Flag(
            code="data_uri_embed",
            severity="critical",
            description="New iframe/embed with data: URI payload",
            evidence=next(iter(added_data_uris))[:100],
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


def _extract_meta_refreshes(soup: BeautifulSoup) -> set[str]:
    """Extract meta refresh redirect URLs as a set for comparison."""
    result = set()
    for meta in soup.find_all("meta", attrs={"http-equiv": re.compile(r"refresh", re.IGNORECASE)}):
        content = meta.get("content", "")
        if content:
            result.add(content)
    return result


def _extract_data_uri_sources(soup: BeautifulSoup) -> set[str]:
    """Extract data: URI sources from iframes, embeds, and objects."""
    result = set()
    for tag in soup.find_all(["iframe", "embed", "object"]):
        src = tag.get("src", "") or tag.get("data", "")
        if src and src.strip().lower().startswith("data:"):
            result.add(src.strip())
    return result


def severity_rank(severity: str) -> int:
    """Return numeric rank for sorting (higher = more severe)."""
    return {"info": 0, "warning": 1, "critical": 2}.get(severity, 0)


def max_severity(flags: list[Flag]) -> str:
    """Return the highest severity among flags."""
    if not flags:
        return "info"
    return max((f.severity for f in flags), key=severity_rank)
