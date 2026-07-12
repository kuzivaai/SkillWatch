"""PROTOTYPE — cloaking detection. NOT shipped, NOT wired into the skillwatch CLI.

Fetch the same URL under several "personas" and detect when a server returns
materially different content to different requesters — e.g. a benign page to a
monitor but malicious instructions to the victim. This is the requisite-variety
"response-variety matching" idea from docs/adr/0001-two-plane-architecture.md.

Backends:
  - LocalBackend  : multi-User-Agent/Accept-Language fetches from THIS machine.
                    Free; no geo variety; preserves skillwatch's local-only model
                    (Plane 1 "cloaking-lite").
  - ApifyBackend  : fetches via Apify's website-content-crawler with residential
                    geo proxies + per-persona headers (Plane 2, maintainer-side).
                    Implemented but NOT fired here — needs APIFY_TOKEN and an
                    explicit opt-in, because it spends Apify credits.

The comparison logic (`compare_personas`) is backend-agnostic and unit-tested.
Run the free demo:  python prototypes/cloaking_prototype.py https://example.com
"""
from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass, field

DEFAULT_TIMEOUT = 20
_MAX_BYTES = 2_000_000  # bound the read; cloaking payloads are small


@dataclass(frozen=True)
class Persona:
    """A way of presenting to the server. `country` is used by geo-proxy backends."""

    name: str
    user_agent: str
    accept_language: str = "en-US,en;q=0.9"
    country: str | None = None
    extra_headers: dict = field(default_factory=dict)

    def headers(self) -> dict:
        h = {"User-Agent": self.user_agent, "Accept-Language": self.accept_language}
        h.update(self.extra_headers)
        return h


DEFAULT_PERSONAS: list[Persona] = [
    Persona(
        "browser_chrome_us",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0 Safari/537.36",
        "en-US,en;q=0.9",
        country="US",
    ),
    Persona(
        "agent_generic",
        "ClaudeBot/1.0 (+https://example.com/agent-docs)",
        "en-US,en;q=0.9",
        country="US",
    ),
    Persona("bot_curl", "curl/8.4.0", "*", country="US"),
    Persona(
        "mobile_safari_de",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 "
        "(KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
        "de-DE,de;q=0.9",
        country="DE",
    ),
]


def _normalise(text: str) -> str:
    """Collapse whitespace so trivial formatting differences aren't seen as change."""
    return " ".join(text.split())


@dataclass
class FetchResult:
    persona: str
    url: str
    ok: bool
    text: str = ""
    status: int | None = None
    error: str = ""

    @property
    def text_hash(self) -> str:
        return hashlib.sha256(_normalise(self.text).encode("utf-8")).hexdigest()


@dataclass
class CloakingResult:
    url: str
    varies: bool
    groups: dict  # text_hash -> [persona names]
    min_similarity: float  # lowest pairwise similarity among successful fetches (0..1)
    n_ok: int
    n_error: int
    detail: str

    def summary(self) -> str:
        head = "⚠️  CLOAKING SUSPECTED" if self.varies else "✓ no variation"
        return (
            f"{head} — {self.url}\n"
            f"  personas ok/err: {self.n_ok}/{self.n_error}  "
            f"min similarity: {self.min_similarity}\n"
            f"  {self.detail}"
        )


def _group(results: list[FetchResult]) -> dict:
    groups: dict = {}
    for r in results:
        groups.setdefault(r.text_hash, []).append(r.persona)
    return groups


def compare_personas(results: list[FetchResult]) -> CloakingResult:
    """Backend-agnostic core: do the personas disagree on the content?"""
    url = results[0].url if results else ""
    ok = [r for r in results if r.ok and _normalise(r.text)]
    n_ok = len(ok)
    n_err = len(results) - n_ok

    if n_ok < 2:
        return CloakingResult(
            url, False, _group(ok), 1.0, n_ok, n_err,
            "insufficient successful fetches to compare",
        )

    groups = _group(ok)
    varies = len(groups) > 1

    min_sim = 1.0
    for i in range(len(ok)):
        for j in range(i + 1, len(ok)):
            sim = difflib.SequenceMatcher(
                None, _normalise(ok[i].text), _normalise(ok[j].text)
            ).ratio()
            min_sim = min(min_sim, sim)

    if varies:
        detail = "content differs across personas: " + "; ".join(
            f"{h[:8]}=[{','.join(names)}]" for h, names in groups.items()
        )
    else:
        detail = "all personas returned identical content"

    return CloakingResult(url, varies, groups, round(min_sim, 4), n_ok, n_err, detail)


class LocalBackend:
    """Multi-persona fetch from the local machine. Free; no geo variety.

    NB: a shipped Plane-1 version MUST route through skillwatch.ssrf for SSRF/DNS
    protection. This prototype fetches directly and is not the shipped path.
    """

    def __init__(self, timeout: int = DEFAULT_TIMEOUT):
        self.timeout = timeout

    def fetch(self, url: str, persona: Persona) -> FetchResult:
        req = urllib.request.Request(url, headers=persona.headers())
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                raw = resp.read(_MAX_BYTES)
                text = raw.decode(resp.headers.get_content_charset() or "utf-8", "replace")
                return FetchResult(persona.name, url, True, text=text, status=resp.status)
        except urllib.error.HTTPError as exc:
            return FetchResult(persona.name, url, False, status=exc.code, error=str(exc))
        except Exception as exc:  # noqa: BLE001 — prototype: any fetch failure is non-fatal
            return FetchResult(persona.name, url, False, error=str(exc))


class ApifyBackend:
    """Fetch via Apify website-content-crawler with residential geo proxies.

    Paid, maintainer-side (Plane 2). Requires APIFY_TOKEN. Not fired in tests.
    """

    ACTOR = "apify~website-content-crawler"

    def __init__(self, token: str | None = None, timeout: int = 120):
        self.token = token or os.environ.get("APIFY_TOKEN", "")
        self.timeout = timeout

    def fetch(self, url: str, persona: Persona) -> FetchResult:
        if not self.token:
            raise RuntimeError(
                "ApifyBackend needs APIFY_TOKEN (this call spends Apify credits)."
            )
        proxy: dict = {"useApifyProxy": True, "apifyProxyGroups": ["RESIDENTIAL"]}
        if persona.country:
            # NB: verify this field name against the actor's input schema before
            # the first real run (Apify proxy input uses apifyProxyCountry).
            proxy["apifyProxyCountry"] = persona.country
        payload = {
            "startUrls": [{"url": url}],
            "crawlerType": "cheerio",
            "maxCrawlPages": 1,
            "maxCrawlDepth": 0,
            "proxyConfiguration": proxy,
            "customHttpHeaders": persona.headers(),
            "saveMarkdown": True,
        }
        endpoint = (
            f"https://api.apify.com/v2/acts/{self.ACTOR}"
            f"/run-sync-get-dataset-items?token={self.token}"
        )
        req = urllib.request.Request(
            endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                items = json.loads(resp.read().decode("utf-8"))
            text = ""
            if isinstance(items, list) and items:
                first = items[0]
                text = first.get("text") or first.get("markdown") or ""
            return FetchResult(persona.name, url, bool(text), text=text, status=200)
        except Exception as exc:  # noqa: BLE001
            return FetchResult(persona.name, url, False, error=str(exc))


def run(url: str, backend, personas: list[Persona] | None = None) -> CloakingResult:
    personas = personas or DEFAULT_PERSONAS
    results = [backend.fetch(url, p) for p in personas]
    return compare_personas(results)


def _main() -> int:
    ap = argparse.ArgumentParser(description="Cloaking-detection prototype.")
    ap.add_argument("url")
    ap.add_argument("--backend", choices=["local", "apify"], default="local")
    ap.add_argument("--country", action="append", default=[],
                    help="Country code(s) for apify geo personas (repeatable).")
    ap.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)
    args = ap.parse_args()

    if args.backend == "apify":
        backend = ApifyBackend(timeout=max(args.timeout, 120))
        personas = (
            [Persona(f"browser_{c}", DEFAULT_PERSONAS[0].user_agent, country=c)
             for c in args.country]
            if args.country
            else DEFAULT_PERSONAS
        )
    else:
        backend = LocalBackend(timeout=args.timeout)
        personas = DEFAULT_PERSONAS

    print(run(args.url, backend, personas).summary())
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
