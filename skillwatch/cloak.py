"""Cloaking check: fetch a URL under several User-Agents and report whether the
server returns different content to different clients.

This is best-effort and User-Agent-based: it varies only the User-Agent, through
the SSRF-protected fetcher (`fetcher.fetch_url`). It is not semantic detection and
does not replace human review. Local-only: it contacts only the URL you pass it.

A server that returns benign documentation to a monitor but malicious instructions
to an agent is the case this catches — the "response variety" a single fetch misses.
"""
from __future__ import annotations

import difflib
import hashlib
from collections.abc import Callable
from dataclasses import dataclass

from .fetcher import FetchResult, fetch_url

# Browser vs agent vs bot is the axis servers most commonly cloak on.
PERSONAS: dict[str, str] = {
    "browser": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    ),
    "agent": "ClaudeBot/1.0 (+https://docs.anthropic.com)",
    "bot": "curl/8.4.0",
}

# (url, user_agent) -> FetchResult
FetchFn = Callable[[str, str], FetchResult]


def _normalise(text: str) -> str:
    """Collapse whitespace so trivial formatting differences aren't seen as change."""
    return " ".join(text.split())


def _hash(text: str) -> str:
    return hashlib.sha256(_normalise(text).encode("utf-8")).hexdigest()


@dataclass
class CloakResult:
    url: str
    varies: bool
    groups: dict[str, list[str]]  # content hash -> persona names sharing it
    min_similarity: float  # lowest pairwise similarity among successful fetches (0..1)
    ok_personas: list[str]
    failed_personas: list[str]

    @property
    def comparable(self) -> bool:
        return len(self.ok_personas) >= 2


def _compare(url: str, contents: dict[str, str]) -> CloakResult:
    """Group personas by content hash and measure the worst pairwise similarity."""
    ok = {name: text for name, text in contents.items() if text}
    failed = [name for name in contents if name not in ok]

    groups: dict[str, list[str]] = {}
    for name, text in ok.items():
        groups.setdefault(_hash(text), []).append(name)

    if len(ok) < 2:
        return CloakResult(url, False, groups, 1.0, list(ok), failed)

    texts = [_normalise(t) for t in ok.values()]
    min_sim = 1.0
    for i in range(len(texts)):
        for j in range(i + 1, len(texts)):
            ratio = difflib.SequenceMatcher(None, texts[i], texts[j]).ratio()
            min_sim = min(min_sim, ratio)

    return CloakResult(url, len(groups) > 1, groups, round(min_sim, 4), list(ok), failed)


def _default_fetch(url: str, user_agent: str) -> FetchResult:
    return fetch_url(url, user_agent=user_agent)


def check_url(
    url: str,
    fetch_fn: FetchFn = _default_fetch,
    personas: dict[str, str] | None = None,
) -> CloakResult:
    """Fetch `url` under each persona and compare. `fetch_fn` is injectable for tests."""
    persona_map = personas if personas is not None else PERSONAS
    contents: dict[str, str] = {}
    for name, user_agent in persona_map.items():
        result = fetch_fn(url, user_agent)
        if result.ok and result.content_text is not None:
            contents[name] = result.content_text
        else:
            contents[name] = ""
    return _compare(url, contents)
