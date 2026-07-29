"""Rebuild the real-page benign corpus in `analysis/corpus/realpage/`.

This script is tracked deliberately. Ledger item 30 records that the corpus behind
0.3.0's published figures was never committed, so those figures cannot be
reproduced at that tag. A corpus that no one can rebuild is evidence no one can
check. Ledger item 24 records the same defect for an untracked generator.

Network access is required and the run takes several minutes. It is NOT part of
any gate: CI must not depend on third-party pages staying up. `measure_base_rate.py`
reads the committed manifest and needs no network.

What it does, in order:

1. GitHub code search for `filename:SKILL.md`, capped at 3 files per repository so
   one monorepo cannot dominate the sample.
2. Download each SKILL.md and extract its external URLs with SkillWatch's own
   `parser.extract_urls_from_text` — the URL set is what the tool itself would
   monitor, not a re-implementation.
3. Fetch each URL twice with SkillWatch's own `fetcher.fetch_url`, so snapshots go
   through the same SSRF validation, DNS pinning and hashing as a real scan.
4. Record per-page technique counts using the detector's own parsing primitives.

Fetched content is stored inert — hashes and counts only — and is never executed.
"""

import argparse
import concurrent.futures
import datetime
import json
import re
import subprocess
import sys

from pathlib import Path
from typing import Any

import requests

from bs4 import BeautifulSoup

# `skillwatch` is installed editable (`pip install -e ".[dev]"`), so these are
# ordinary top-level imports. No sys.path manipulation, and so no E402 suppression:
# the import pattern that needed one was the defect, not the linter.
from skillwatch.detector import (
    TECHNIQUE_BUCKETS,
    _parse_declarations,
    _style_block_rules,
    detect_suspicious_changes,
)
from skillwatch.fetcher import fetch_url
from skillwatch.parser import extract_urls_from_text

_HERE = Path(__file__).resolve().parent
OUT_DIR = _HERE / "corpus" / "realpage"
BLOB_RE = re.compile(r"https://github\.com/([^/]+)/([^/]+)/blob/([^/]+)/(.+)")
NEG_OFFSET = re.compile(r"^-\d{4,}(px|pt|em|rem)?$", re.IGNORECASE)
ZERO = re.compile(r"^0(\.0+)?(px|pt|em|rem|%)?$", re.IGNORECASE)
CLIP_INSET = re.compile(r"inset\(\s*\d+%|rect\(", re.IGNORECASE)
PER_REPO_CAP = 3


def _now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def search_skill_files(target: int) -> list[dict[str, str]]:
    """Collect SKILL.md paths from GitHub code search, deduped for repo diversity."""
    seen: dict[str, int] = {}
    rows: list[dict[str, str]] = []
    for page in range(1, 11):
        query = f"search/code?q=filename:SKILL.md&per_page=100&page={page}"
        proc = subprocess.run(
            ["gh", "api", query, "--jq",
             ".items[] | {repo: .repository.full_name, path: .path, url: .html_url}"],
            capture_output=True, text=True, check=False,
        )
        if proc.returncode != 0:
            print(f"  code search page {page} failed: {proc.stderr[:200]}", file=sys.stderr)
            break
        lines = [line for line in proc.stdout.splitlines() if line.strip()]
        if not lines:
            break
        for line in lines:
            item = json.loads(line)
            if seen.get(item["repo"], 0) >= PER_REPO_CAP:
                continue
            seen[item["repo"]] = seen.get(item["repo"], 0) + 1
            rows.append(item)
        if len(rows) >= target:
            break
    print(f"  {len(rows)} SKILL.md files across {len(seen)} repositories")
    return rows


def _raw_url(html_url: str) -> str | None:
    match = BLOB_RE.match(html_url)
    if match is None:
        return None
    owner, repo, ref, path = match.groups()
    return f"https://raw.githubusercontent.com/{owner}/{repo}/{ref}/{path}"


def collect_urls(skill_files: list[dict[str, str]]) -> dict[str, list[str]]:
    """Download each SKILL.md and extract the external URLs it references."""
    def one(item: dict[str, str]) -> tuple[str, str] | None:
        raw = _raw_url(item["url"])
        if raw is None:
            return None
        try:
            response = requests.get(raw, timeout=20)
        except requests.RequestException:
            return None
        if response.status_code != 200:
            return None
        return (f"{item['repo']}/{item['path']}", response.text)

    url_to_sources: dict[str, list[str]] = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=12) as pool:
        for result in pool.map(one, skill_files):
            if result is None:
                continue
            source, text = result
            for entry in extract_urls_from_text(text, "markdown", source):
                url_to_sources.setdefault(entry["url"], []).append(source)
    print(f"  {len(url_to_sources)} unique external URLs")
    return url_to_sources


def techniques_in(declarations: dict[str, str]) -> set[str]:
    """Which taxonomy techniques does this declaration block use?

    Measured independently of bucket, because the whole point is to check whether
    the bucket assignments are right.
    """
    found: set[str] = set()
    positioned = declarations.get("position", "").lower() in {"absolute", "fixed"}
    clips = declarations.get("overflow", "").lower() in {"hidden", "clip"}

    if declarations.get("display", "").lower() == "none":
        found.add("display:none")
    if declarations.get("visibility", "").lower() in {"hidden", "collapse"}:
        found.add("visibility:hidden")
    if "opacity" in declarations and ZERO.match(declarations["opacity"]):
        found.add("opacity:0")
    if "font-size" in declarations and ZERO.match(declarations["font-size"]):
        found.add("font-size:0")
    for prop in ("left", "top"):
        if prop in declarations and NEG_OFFSET.match(declarations[prop]) and positioned:
            found.add("offscreen-position")
    for prop in ("height", "width"):
        if prop in declarations and ZERO.match(declarations[prop]) and clips:
            found.add("zero-box-clipped")
    for prop in ("clip-path", "clip"):
        if prop in declarations and CLIP_INSET.search(declarations[prop]):
            found.add("clip-path-inset")
    if "text-indent" in declarations and NEG_OFFSET.match(declarations["text-indent"]):
        found.add("text-indent-negative")
    return found


def count_techniques(html: str) -> dict[str, int]:
    """Count concealed elements per technique on one page."""
    soup = BeautifulSoup(html, "html.parser")
    counts: dict[str, int] = {}

    def bump(name: str, amount: int) -> None:
        counts[name] = counts.get(name, 0) + amount

    hidden_attr = len(soup.find_all(hidden=True))
    if hidden_attr:
        bump("html-hidden-attr", hidden_attr)
    aria = len(soup.find_all(attrs={"aria-hidden": "true"}))
    if aria:
        bump("aria-hidden", aria)

    for element in soup.find_all(style=True):
        declarations, _ = _parse_declarations(str(element.get("style", "")))
        for technique in techniques_in(declarations):
            bump(f"{technique} (inline)", 1)
            bump(technique, 1)

    rules, _ = _style_block_rules(soup)
    for selector, declarations, _parsed in rules:
        found = techniques_in(declarations)
        if not found:
            continue
        try:
            matched = soup.select(selector)
        except Exception:  # an unusable selector is not a crash
            continue
        for technique in found:
            bump(f"{technique} (style block)", len(matched))
            bump(technique, len(matched))
    return counts


def _snapshot(url: str) -> dict[str, Any]:
    stamp = _now()
    try:
        result = fetch_url(url, timeout=15)
    except Exception as exc:  # a crash must be recorded, not lost
        return {"url": url, "fetched_at": stamp, "error": f"EXCEPTION: {exc!r}"}
    return {
        "url": url, "fetched_at": stamp, "error": result.error,
        "status_code": result.status_code, "content_hash": result.content_hash,
        "raw_html_hash": result.raw_html_hash, "raw_html": result.raw_html,
    }


def build(target_files: int) -> int:
    print("1. searching GitHub for SKILL.md files")
    skill_files = search_skill_files(target_files)
    if len(skill_files) < 30:
        print(f"FAIL: only {len(skill_files)} SKILL.md files found; need >= 30",
              file=sys.stderr)
        return 2

    print("2. downloading them and extracting URLs")
    url_to_sources = collect_urls(skill_files)
    urls = sorted(url_to_sources)

    print(f"3. fetching {len(urls)} URLs (snapshot 1)")
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as pool:
        first = list(pool.map(_snapshot, urls))
    usable = [s for s in first if s.get("raw_html")]
    print(f"   {len(usable)} pages returned HTML")

    print(f"4. fetching {len(usable)} URLs again (snapshot 2)")
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as pool:
        second = {s["url"]: s for s in pool.map(_snapshot, [u["url"] for u in usable])}

    print("5. measuring techniques and flags")
    items: list[dict[str, Any]] = []
    for snap in usable:
        html = snap["raw_html"]
        flags = detect_suspicious_changes(
            old_text=None, new_text="", diff_text="", old_html=None, new_html=html,
        )
        item: dict[str, Any] = {
            "url": snap["url"],
            "snapshot_1": {
                "fetched_at": snap["fetched_at"], "content_hash": snap["content_hash"],
                "raw_html_hash": snap["raw_html_hash"],
                "status_code": snap["status_code"], "bytes": len(html),
            },
            "techniques": count_techniques(html),
            "flags_first_observation": sorted({f.code for f in flags}),
            "referenced_by": sorted(set(url_to_sources[snap["url"]]))[:5],
            "referenced_by_count": len(set(url_to_sources[snap["url"]])),
        }
        other = second.get(snap["url"])
        if other is not None and other.get("raw_html"):
            delta = detect_suspicious_changes(
                old_text=None, new_text="", diff_text="",
                old_html=html, new_html=other["raw_html"],
            )
            item["snapshot_2"] = {
                "fetched_at": other["fetched_at"],
                "content_hash": other["content_hash"],
                "raw_html_hash": other["raw_html_hash"],
                "raw_html_changed": other["raw_html_hash"] != snap["raw_html_hash"],
                "extracted_text_changed": other["content_hash"] != snap["content_hash"],
            }
            item["flags_on_delta"] = sorted({f.code for f in delta})
        items.append(item)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    manifest = {
        "corpus": "realpage_v1",
        "description": (
            "Benign real-page corpus. Every page is referenced by a real SKILL.md "
            "sampled from public GitHub repositories. None of these pages was "
            "written by this project. No page is known or assumed to carry a "
            "payload; every technique occurrence recorded here is therefore a "
            "legitimate use, which is what makes this a base rate rather than a "
            "detection result."
        ),
        "built": _now()[:10],
        "method": {
            "registry": "GitHub code search, filename:SKILL.md",
            "skill_files_sampled": len(skill_files),
            "distinct_repositories": len({s["repo"] for s in skill_files}),
            "per_repository_cap": PER_REPO_CAP,
            "urls_extracted_with": "skillwatch.parser.extract_urls_from_text",
            "urls_extracted": len(urls),
            "fetched_with": "skillwatch.fetcher.fetch_url (SSRF validation + DNS pinning)",
            "pages_with_html": len(items),
            "snapshot_interval": "minutes, not days — see LIMITATIONS",
        },
        "limitations": [
            "Raw HTML is NOT committed: it runs to tens of megabytes and would "
            "permanently bloat the repository. The content hashes pin exactly what "
            "was measured, but the live pages can change, so byte-exact "
            "re-derivation from the network is not guaranteed.",
            "The two snapshots are minutes apart, not days. That captures "
            "per-request churn but not editorial drift, so the delta figure is a "
            "LOWER bound.",
            "Sampling is by GitHub code-search ranking, not uniform random. Pages "
            "referenced by popular skills are over-represented relative to a "
            "uniform sample of all skills.",
        ],
        "technique_buckets_at_build_time": dict(TECHNIQUE_BUCKETS),
        "items": items,
    }
    path = OUT_DIR / "MANIFEST.json"
    with path.open("w") as handle:
        json.dump(manifest, handle, indent=2)
        handle.write("\n")
    print(f"\nwrote {path} ({path.stat().st_size / 1024:.0f} KB, {len(items)} pages)")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target-files", type=int, default=120,
                        help="how many SKILL.md files to sample (default 120)")
    args = parser.parse_args()
    return build(args.target_files)


if __name__ == "__main__":
    raise SystemExit(main())
