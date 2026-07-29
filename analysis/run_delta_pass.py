"""Re-fetch the real-page corpus and measure the delta false-positive rate.

**Do not run this before 2026-08-05.** The script refuses to, and says why.

What it settles
---------------
The real-page *false-positive rate* is the figure that transfers to deployment,
and this project does not have it. Three open items turn on it:

* item 37 — external validity. The base-rate half is closed; this is the other.
* item 38 — ship-readiness condition 2. Whether the benign false-positive gate's
  failure (upper bound 31.1% against a 30% gate) is a small-sample artefact or
  structural.
* item 43 — whether `display:none` and `visibility:hidden` should have stayed in
  the flagged bucket when the HTML `hidden` attribute was moved out of it. That
  split rests on a churn argument this pass tests directly.

Why it cannot be run early
--------------------------
The first pass, on 2026-07-29, took both snapshots minutes apart. Across 199
paired pages the raw HTML changed on 97 (48.7%) but the *extracted text* on only
3 (1.5%), and detection runs only on a text change. `0/3` has a 95% interval of
[0.0%, 56.1%] and supports nothing. Minutes capture per-request churn — rotating
tokens, timestamps, ad slots — not editorial drift, which needs days.

How the baseline works without storing 56 MB of HTML
----------------------------------------------------
`corpus/realpage/DELTA-BASELINE.json` holds, per page, a truncated SHA-256 of each
member of every set the detector diffs: extracted text lines, hidden texts,
suspicious script contents, iframe sources, meta refreshes, data URI sources. Set
membership is all a delta needs — a flag fires when the new set has a member the
old set lacks — and hashing both sides preserves that exactly.

The baseline was reconstructed offline from the HTML captured on 2026-07-29 and
verified: all 201 pages re-extracted to text whose SHA-256 equals the
`content_hash` already recorded in `MANIFEST.json`. The reconstruction is
byte-exact, so these hashes describe the text the tool actually ingested that day.

**What this costs.** The evidence *string* on an alert is not recoverable, only
whether a flag fires. That is enough for a rate and not enough for an alert
message, and the file says so.

**One divergence risk, stated.** Text-based flags are produced by calling the
detector's own `detect_suspicious_changes` on a synthetic diff of added lines, so
they cannot drift from it. The five HTML checks are re-derived here as "the new
set has a member the old set lacks", mirroring `_check_html_changes`. That is a
second implementation of a five-line rule. If `_check_html_changes` ever becomes
more than a set difference, this script must be updated with it —
`tests/test_delta_pass.py` pins the correspondence.
"""

import argparse
import concurrent.futures
import datetime
import hashlib
import importlib.util
import json
import sys

from pathlib import Path
from types import ModuleType
from typing import Any

from bs4 import BeautifulSoup

from skillwatch.detector import (
    _extract_data_uri_sources,
    _extract_hidden_texts,
    _extract_meta_refreshes,
    _extract_suspicious_script_contents,
    detect_suspicious_changes,
)
from skillwatch.fetcher import fetch_url

_HERE = Path(__file__).resolve().parent
CORPUS = _HERE / "corpus" / "realpage"
MANIFEST = CORPUS / "MANIFEST.json"
BASELINE = CORPUS / "DELTA-BASELINE.json"

# Seven days after the first snapshots. Below this the measurement cannot say
# anything the first pass did not already fail to say.
EARLIEST = datetime.date(2026, 8, 5)

# Which extractor feeds which flag. Mirrors _check_html_changes in detector.py.
HTML_CHECKS = (
    ("hidden_texts", "hidden_content"),
    ("script_contents", "suspicious_script"),
    ("iframe_srcs", "iframe_detected"),
    ("meta_refreshes", "meta_refresh_redirect"),
    ("data_uri_sources", "data_uri_embed"),
)


def _load_sibling(name: str) -> ModuleType:
    """Load a sibling module in `analysis/` by path (see measure_base_rate.py)."""
    spec = importlib.util.spec_from_file_location(name, _HERE / f"{name}.py")
    if spec is None or spec.loader is None:
        raise SystemExit(f"FAIL: cannot load analysis/{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def short_hash(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()[:16]


def extract_sets(html: str) -> dict[str, set[str]]:
    """The five HTML sets the detector diffs, hashed."""
    soup = BeautifulSoup(html, "html.parser")
    return {
        "hidden_texts": {short_hash(x) for x in _extract_hidden_texts(soup)},
        "script_contents": {short_hash(x) for x in _extract_suspicious_script_contents(soup)},
        "iframe_srcs": {short_hash(f.get("src", "") or "") for f in soup.find_all("iframe")},
        "meta_refreshes": {short_hash(x) for x in _extract_meta_refreshes(soup)},
        "data_uri_sources": {short_hash(x) for x in _extract_data_uri_sources(soup)},
    }


def flags_for(page: dict[str, Any], baseline: dict[str, list[str]]) -> list[str]:
    """Every flag that would fire on this page's change since the baseline."""
    codes: set[str] = set()

    # Text checks — delegated to the detector so they cannot drift from it.
    old_lines = set(baseline.get("text_lines", []))
    added = [line for line in (page["content_text"] or "").splitlines()
             if line.strip() and short_hash(line) not in old_lines]
    if added:
        synthetic_diff = "\n".join(f"+{line}" for line in added)
        for flag in detect_suspicious_changes(
            old_text=None, new_text=page["content_text"] or "",
            diff_text=synthetic_diff, old_html=None, new_html=None,
        ):
            codes.add(flag.code)

    # HTML checks — a flag fires when the new set has a member the old set lacks.
    new_sets = extract_sets(page["raw_html"])
    for key, code in HTML_CHECKS:
        if new_sets[key] - set(baseline.get(key, [])):
            codes.add(code)
    return sorted(codes)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--i-understand-this-is-early", action="store_true",
        help="run before 2026-08-05 anyway. The result must not be published.",
    )
    parser.add_argument("--out", default=str(CORPUS / "DELTA-PASS.json"))
    args = parser.parse_args()

    today = datetime.date.today()
    if today < EARLIEST and not args.i_understand_this_is_early:
        print(f"REFUSING: today is {today}; this pass is scheduled for {EARLIEST} "
              f"or later.", file=sys.stderr)
        print("The first snapshots were 2026-07-29. A second pass sooner than seven "
              "days measures per-request churn, not editorial drift — which is "
              "exactly what made the first attempt return 0/3.", file=sys.stderr)
        return 3

    if not MANIFEST.exists() or not BASELINE.exists():
        print(f"FAIL: need both {MANIFEST.name} and {BASELINE.name}.", file=sys.stderr)
        print("This check has NOT passed — it could not inspect its subject.",
              file=sys.stderr)
        return 2

    efficacy = _load_sibling("measure_efficacy")
    manifest = json.loads(MANIFEST.read_text())
    baseline = json.loads(BASELINE.read_text())
    urls = [i["url"] for i in manifest["items"] if i["url"] in baseline["items"]]
    print(f"re-fetching {len(urls)} URLs (baseline captured {baseline['captured']}, "
          f"today {today})")

    def one(url: str) -> dict[str, Any]:
        try:
            result = fetch_url(url, timeout=15)
        except Exception as exc:  # a crash must be recorded, not lost
            return {"url": url, "error": f"EXCEPTION: {exc!r}"}
        return {
            "url": url, "error": result.error, "content_text": result.content_text,
            "raw_html": result.raw_html, "content_hash": result.content_hash,
        }

    fetched: list[dict[str, Any]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as pool:
        for i, record in enumerate(pool.map(one, urls), 1):
            fetched.append(record)
            if i % 50 == 0:
                print(f"  {i}/{len(urls)}", flush=True)

    usable = [f for f in fetched if not f.get("error") and f.get("raw_html")]
    by_url = {i["url"]: i for i in manifest["items"]}

    # cli.py:443 — detection runs only when the extracted text hash changed.
    gate_open = [f for f in usable
                 if f["content_hash"] != by_url[f["url"]]["snapshot_1"]["content_hash"]]

    per_page = []
    flagged = 0
    by_code: dict[str, int] = {}
    for page in gate_open:
        codes = flags_for(page, baseline["items"][page["url"]])
        if codes:
            flagged += 1
        for code in codes:
            by_code[code] = by_code.get(code, 0) + 1
        per_page.append({"url": page["url"], "flags": codes})

    n = len(gate_open)
    print(f"\nre-fetched OK          {len(usable)}/{len(urls)}")
    print(f"extracted text changed {efficacy.fmt_prop(n, len(usable))}")
    print("  ^ the gate: cli.py runs detection only on a text diff.\n")
    print(f"DELTA FALSE-POSITIVE RATE  {efficacy.fmt_prop(flagged, n)}")
    for code in sorted(by_code, key=lambda c: -by_code[c]):
        print(f"  {code:<24} {efficacy.fmt_prop(by_code[code], n)}")
    if not by_code:
        print("  (no flag fired on any text-diffing page)")

    if n < 30:
        print(f"\nWARNING: n={n}. Too small to support a claim. Do not publish this "
              f"as a rate; report it as n and say so.")

    Path(args.out).write_text(json.dumps({
        "ran": today.isoformat(), "baseline_captured": baseline["captured"],
        "urls": len(urls), "refetched_ok": len(usable), "gate_open": n,
        "flagged": flagged, "by_code": by_code, "per_page": per_page,
    }, indent=2) + "\n")
    print(f"\nwrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
