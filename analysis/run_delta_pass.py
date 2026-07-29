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

**What the rehearsal proves, and what it does not.** `--rehearse` runs every stage
over stored HTML, fetching nothing. It establishes that the code executes and
returns the documented shape. It establishes **nothing** about the false-positive
rate: each page is fed in as both sides of the diff, so the zero-change result is
arithmetic. Specifically —

* PROVEN: source loading, text extraction, per-set diffing, the
  `detect_suspicious_changes` call, the five re-derived HTML checks, the
  reachability of the two checks guarded behind `if old_text:`, aggregation and
  report formatting.
* NOT PROVEN: anything involving the network — SSRF validation on live hosts, DNS
  pinning, redirect handling, timeouts, partial responses, hosts that have since
  disappeared. Those run for the first time on 2026-08-05.
* NOT PROVEN: behaviour on pages that changed. Every rehearsal input is identical
  on both sides or diffed against an empty/synthetic baseline, so no real
  before/after pair has ever gone through this code.

REASONED, not evidenced: that a pipeline which handles 201 stored pages will handle
201 freshly fetched ones. The assumption is that the only new failure surface is
the fetch itself, which is `skillwatch.fetcher` — already exercised by the 2026-07-29
capture and by the tool's own test suite. What would overturn it: a failure on
2026-08-05 in aggregation or reporting rather than in fetching.

**One divergence risk, stated.** Text-based flags are produced by calling the
detector's own `detect_suspicious_changes` with the real stored `old_text` and the
project's own `generate_diff`, exactly as `cli.py` calls them, so they cannot drift
from it. The five HTML checks are re-derived here as "the new set has a member the
old set lacks", mirroring `_check_html_changes`. That is a second implementation of
a five-line rule. If `_check_html_changes` ever becomes more than a set difference,
this script must be updated with it — `tests/test_delta_pass.py` pins the
correspondence.

**The defect the rehearsal found.** Until 2026-07-29 this file passed
`old_text=None` and the baseline stored only hashes of text lines. `detector.py`
guards `new_domains` (line 401) and `major_deletion` (line 414) behind
`if old_text:`, so neither could ever fire — and `new_domains` is one of the four
checks that produce false positives in the synthetic corpus. The scheduled pass
would have under-reported the real-page rate by omitting a quarter of the checks
that generate it, and nothing in the code or the tests said so. Fixed by storing the
extracted text (1.78 MB) rather than line hashes. A reachability probe now asserts
both codes can be emitted, and fails the rehearsal if either cannot.
"""

import argparse
import concurrent.futures
import datetime
import glob
import hashlib
import importlib.util
import json
import sys

from pathlib import Path
from types import ModuleType
from typing import Any

import trafilatura

from bs4 import BeautifulSoup

from skillwatch.differ import generate_diff
from skillwatch.detector import (
    _extract_data_uri_sources,
    _extract_hidden_texts,
    _extract_meta_refreshes,
    _extract_suspicious_script_contents,
    detect_suspicious_changes,
)
from skillwatch.fetcher import _normalise_whitespace, fetch_url, strip_escape_sequences

_HERE = Path(__file__).resolve().parent
CORPUS = _HERE / "corpus" / "realpage"
MANIFEST = CORPUS / "MANIFEST.json"
BASELINE = CORPUS / "DELTA-BASELINE.json"

# Rehearsal output goes here and nowhere else. A zero-change delta is not a
# measurement and must never reach README.md, SHIP-READINESS.md, PATTERNS.md,
# CHANGELOG.md or docs/, where a reader would take it for one.
REHEARSAL_OUTPUT_DIR = _HERE

# Where rehearsal HTML can come from, in preference order.
#
#   "capture" — the raw HTML fetched on 2026-07-29, from which DELTA-BASELINE.json
#               was built. This is the faithful source: the same bytes the real
#               pass will diff against. It lives in an ephemeral session scratchpad
#               and WILL disappear. Its absence is a finding about the baseline's
#               reproducibility, not a reason to fetch.
#   "corpus"  — the committed html_v1 corpus. Twelve small documents, always
#               present, so a later session can always rehearse. Proves the code
#               runs; says nothing about real-page scale.
#
# REASONED, not evidenced: that exercising the pipeline over 12 committed
# documents proves the same code paths as exercising it over 201 captured pages.
# The assumption is that the stages are size-independent, which they are by
# inspection (per-page loop, set operations, one detector call). What would
# overturn it: a failure on 2026-08-05 in a path that only large or malformed
# input reaches — a memory ceiling, a parser timeout, a pathological selector.
# Cheapest mitigation, taken: the "capture" source rehearses at real scale
# whenever it is available, and this session ran it there.
REHEARSAL_SOURCES = ("capture", "corpus")

_CAPTURE_GLOB = "/tmp/claude-1000/-home-mkuziva-skillwatch/*/scratchpad/fetched_pages.json"

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


def flags_for(page: dict[str, Any], baseline: dict[str, Any],
              stages: dict[str, bool] | None = None) -> list[str]:
    """Every flag that would fire on this page's change since the baseline.

    `stages`, when passed, records which pipeline stages actually executed. The
    rehearsal uses it to report proven paths rather than assumed ones.
    """
    codes: set[str] = set()

    def ran(name: str) -> None:
        if stages is not None:
            stages[name] = True

    # Text checks — called exactly as cli.py calls them, with the REAL old text and
    # the project's own differ. Nothing is re-derived on this side.
    #
    # This was not always so. Until the 2026-07-29 rehearsal the baseline stored
    # only hashes of old text LINES, and this function passed `old_text=None`.
    # detector.py guards two checks behind `if old_text:` — `new_domains` (line
    # 401) and `major_deletion` (line 414) — so NEITHER COULD EVER FIRE, and
    # `new_domains` is one of the four checks that actually produce false positives
    # in the synthetic corpus. The scheduled pass would have under-reported the
    # real-page rate by omitting a quarter of the checks that generate it. Found by
    # rehearsing, not by reading.
    old_text = baseline.get("text", "")
    new_text = page["content_text"] or ""
    diff_text = generate_diff(old_text, new_text, url=page.get("url", ""))
    ran("text_line_diff")
    if diff_text.strip():
        for flag in detect_suspicious_changes(
            old_text=old_text or None, new_text=new_text,
            diff_text=diff_text, old_html=None, new_html=None,
        ):
            codes.add(flag.code)
        ran("detect_suspicious_changes")

    # HTML checks — a flag fires when the new set has a member the old set lacks.
    new_sets = extract_sets(page["raw_html"])
    ran("extract_sets")
    for key, code in HTML_CHECKS:
        if new_sets[key] - set(baseline.get(key, [])):
            codes.add(code)
    ran("html_set_diff")
    return sorted(codes)


def extract_text_offline(raw_html: str) -> str:
    """Reproduce fetcher.fetch_url's text extraction from stored HTML, no network.

    The same trafilatura path and the same post-processing, so the result is the
    text the tool would have ingested. `make_baseline.py` uses this to build
    DELTA-BASELINE.json, and the rehearsal uses it to feed stored HTML through the
    pipeline. One implementation, so the two cannot disagree.
    """
    raw = raw_html.encode("utf-8", "replace")
    extracted = trafilatura.extract(raw, include_links=True, include_tables=True) or \
        trafilatura.extract(raw, include_links=True, no_fallback=False)
    if not extracted:
        extracted = f"[SkillWatch: could not extract text from {len(raw_html)} bytes of HTML]"
    return _normalise_whitespace(strip_escape_sequences(extracted))


def baseline_from_page(page: dict[str, Any]) -> dict[str, Any]:
    """Build a baseline from a page itself, so diffing it against that is empty."""
    sets = extract_sets(page["raw_html"])
    out: dict[str, Any] = {
        key: sorted(sets[key]) for key, _code in HTML_CHECKS
    }
    out["text"] = page["content_text"] or ""
    return out


def _load_rehearsal_pages(source: str) -> list[dict[str, Any]]:
    """Load stored HTML for a rehearsal. Never fetches."""
    if source not in REHEARSAL_SOURCES:
        raise SystemExit(
            f"FAIL: unknown rehearsal source {source!r}; expected one of "
            f"{list(REHEARSAL_SOURCES)}."
        )

    if source == "capture":
        matches = sorted(glob.glob(_CAPTURE_GLOB))
        if not matches:
            raise SystemExit(
                "FAIL: the 2026-07-29 HTML capture is no longer on disk.\n"
                f"  looked for: {_CAPTURE_GLOB}\n"
                "This is a FINDING about the baseline's reproducibility, not a "
                "reason to fetch: DELTA-BASELINE.json was derived from bytes that "
                "no longer exist anywhere, so its derivation cannot be re-checked. "
                "Rehearse with --source corpus instead, which uses committed HTML."
            )
        with open(matches[-1]) as handle:
            records = json.load(handle)
        pages: list[dict[str, Any]] = []
        for record in records:
            if not record.get("has_html"):
                continue
            pages.append({
                "url": record["url"],
                "raw_html": record["raw_html"],
                "content_text": extract_text_offline(record["raw_html"]),
            })
        return pages

    items = sorted((CORPUS.parent / "html_v1").glob("*.json"))
    if not items:
        raise SystemExit(
            "FAIL: the committed html_v1 corpus is missing. Nothing to rehearse "
            "against, and this is not a reason to fetch."
        )
    pages = []
    for path in items:
        with path.open() as handle:
            item = json.load(handle)
        if not item.get("new_html"):
            continue
        pages.append({
            "url": f"corpus:{item['id']}",
            "raw_html": item["new_html"],
            "content_text": item.get("new") or "",
        })
    return pages


def rehearse(source: str = "corpus", out_path: str | None = None) -> dict[str, Any]:
    """Run the whole delta pipeline over stored HTML. Fetches nothing.

    Each page is fed in as BOTH sides of the diff, so the delta is empty by
    construction. **The result is not a measurement** — it cannot be, since nothing
    changed. What it establishes is that every stage executes and returns the shape
    the real pass returns.

    Because an empty delta never reaches `detect_suspicious_changes` (there are no
    added lines), a second maximal pass runs each page against an EMPTY baseline,
    so every line counts as added and the detector call executes. That pass is also
    not a measurement; it exists to prove the code path runs.
    """
    stages: dict[str, bool] = {
        "load_source": False, "extract_sets": False, "text_line_diff": False,
        "detect_suspicious_changes": False, "html_set_diff": False,
        "reachability_probe": False, "aggregate": False, "format_report": False,
    }

    pages = _load_rehearsal_pages(source)
    stages["load_source"] = bool(pages)

    # Pass A — the true zero-change delta. Must produce nothing.
    flagged = 0
    by_code: dict[str, int] = {}
    gate_open = 0
    for page in pages:
        baseline = baseline_from_page(page)
        # cli.py:443 — identical text means the gate never opens.
        codes = flags_for(page, baseline, stages)
        if codes:
            flagged += 1
        for code in codes:
            by_code[code] = by_code.get(code, 0) + 1

    # Pass B — maximal: an empty baseline makes every line and element new, which
    # is the only way to execute the detector call offline. NOT a measurement.
    exercise: dict[str, int] = {}
    empty: dict[str, Any] = {}
    for page in pages:
        for code in flags_for(page, empty, stages):
            exercise[code] = exercise.get(code, 0) + 1
    # Pass C — reachability probe for the two checks detector.py guards behind
    # `if old_text:`. Pass B uses an EMPTY baseline, so old_text is falsy and those
    # two are unreachable there — which proves the guard, not the fix. This pass
    # supplies a real, non-empty old text so both become reachable. Synthetic
    # inputs, and NOT a measurement: it answers "can this code be emitted at all
    # through flags_for", which is the question the 2026-07-29 defect turned on.
    reachability: dict[str, bool] = {}
    probes = (
        ("new_domains",
         {"text": "Reference documentation."},
         {"url": "probe", "raw_html": "<html><body>x</body></html>",
          "content_text": "Reference documentation.\nSee https://evil.example.com/x"}),
        ("major_deletion",
         {"text": "A" * 400},
         {"url": "probe", "raw_html": "<html><body>x</body></html>",
          "content_text": "A" * 20}),
    )
    for code, probe_baseline, probe_page in probes:
        reachability[code] = code in flags_for(probe_page, probe_baseline)
    stages["reachability_probe"] = True
    stages["aggregate"] = True

    report: dict[str, Any] = {
        "source": source,
        "reachability": reachability,
        "pages_loaded": len(pages),
        "stages": stages,
        "gate_open": gate_open,
        "flagged": flagged,
        "by_code": by_code,
        "exercise_with_empty_baseline": exercise,
        "is_measurement": False,
        "warning": (
            "NOT A MEASUREMENT. Every page was fed in as both sides of the diff, so "
            "the zero-change result is arithmetic, not evidence. The real delta "
            "false-positive rate is scheduled for 2026-08-05. This output exists "
            "only to prove the pipeline executes, and must not be published on any "
            "documentation surface."
        ),
    }
    stages["format_report"] = True

    if out_path:
        target = Path(out_path)
        if REHEARSAL_OUTPUT_DIR not in target.resolve().parents and \
                target.resolve().parent != REHEARSAL_OUTPUT_DIR:
            raise SystemExit(
                f"FAIL: refusing to write a rehearsal result to {target}. "
                f"Allowed only under {REHEARSAL_OUTPUT_DIR}."
            )
        target.write_text(json.dumps(report, indent=2) + "\n")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--i-understand-this-is-early", action="store_true",
        help="run before 2026-08-05 anyway. The result must not be published.",
    )
    parser.add_argument("--out", default=str(CORPUS / "DELTA-PASS.json"))
    parser.add_argument(
        "--rehearse", action="store_true",
        help="run the whole pipeline over STORED html, fetching nothing. The result "
             "is a zero-change delta and is NOT a measurement.",
    )
    parser.add_argument(
        "--source", default="capture", choices=list(REHEARSAL_SOURCES),
        help="rehearsal HTML source (default: capture, the 2026-07-29 bytes)",
    )
    parser.add_argument(
        "--rehearsal-out", default=None,
        help=f"optional JSON path, must be under {REHEARSAL_OUTPUT_DIR}",
    )
    args = parser.parse_args()

    if args.rehearse:
        report = rehearse(args.source, args.rehearsal_out)
        print("=" * 70)
        print("DELTA PIPELINE REHEARSAL — NOT A MEASUREMENT")
        print("=" * 70)
        print(f"\nsource        {report['source']}")
        print(f"pages loaded  {report['pages_loaded']}")
        print("\npipeline stages:")
        for name, executed in report["stages"].items():
            print(f"  {'EXECUTED    ' if executed else 'NOT EXECUTED'}  {name}")
        not_run = [n for n, ok in report["stages"].items() if not ok]
        print("\nzero-change delta (each page fed in as both snapshots):")
        print(f"  gate opened on   {report['gate_open']}/{report['pages_loaded']} pages")
        print(f"  pages flagged    {report['flagged']}")
        print(f"  by flag code     {report['by_code'] or '{}'}")
        print("\nmaximal pass (empty baseline — every line and element counts as new;")
        print("this is what executes the detector call offline):")
        for code, count in sorted(report["exercise_with_empty_baseline"].items(),
                                  key=lambda kv: -kv[1]):
            print(f"  {code:<24} {count}")
        if not report["exercise_with_empty_baseline"]:
            print("  (nothing fired even against an empty baseline — investigate)")
        print("\nreachability probe (synthetic; the two checks detector.py guards")
        print("behind `if old_text:`, which an empty baseline cannot reach):")
        for code, reachable in sorted(report["reachability"].items()):
            print(f"  {'REACHABLE    ' if reachable else 'UNREACHABLE  '}{code}")
        unreachable = [c for c, ok in report["reachability"].items() if not ok]
        print(f"\n{report['warning']}")
        if not_run or unreachable:
            if not_run:
                print(f"\nSTAGES NOT PROVEN: {not_run}")
            if unreachable:
                print(f"FLAG CODES UNREACHABLE THROUGH flags_for: {unreachable}")
            return 1
        if args.rehearsal_out:
            print(f"\nwrote {args.rehearsal_out}")
        return 0

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
