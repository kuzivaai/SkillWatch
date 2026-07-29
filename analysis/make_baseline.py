"""Build `corpus/realpage/DELTA-BASELINE.json` from stored HTML. Fetches nothing.

Why this file is tracked
------------------------
It generated committed evidence. `DELTA-BASELINE.json` is what the scheduled delta
pass (2026-08-05) reads to decide ledger items 37, 38 and 43, and until 2026-07-29
this generator existed only in an ephemeral session scratchpad — it would have
vanished, leaving a committed artefact nobody could regenerate or audit.

That is the third instance of one shape in this repository: `COMPETITORS.md`
untracked while feeding launch copy (item 34), `analysis/build_corpus.py` untracked
while generating corpus items (item 24), and this. The generator of a committed
artefact belongs in the repository.

What it stores, and why each form
---------------------------------
* **`text`** — the extracted text, in full. Not hashes. The first version of this
  file stored only SHA-256 hashes of text *lines*, on the reasoning that set
  membership is all a diff needs. That was wrong: `detector.py` guards
  `new_domains` (line 401) and `major_deletion` (line 414) behind `if old_text:`,
  so passing `old_text=None` meant neither could ever fire — and `new_domains` is
  one of the four checks that produce false positives in the synthetic corpus. The
  scheduled pass would have under-reported the real-page rate. Storing the text
  costs 1.78 MB and lets `run_delta_pass.py` call `detect_suspicious_changes`
  exactly as `cli.py` calls it, with nothing re-derived on the text side.
* **The five HTML sets** — truncated SHA-256 per member. These are diffed by set
  membership, so hashes are sufficient, and reconstructing them needs the raw HTML,
  which is 56.2 MB and deliberately not committed.

Verification
------------
Extracted text is reconstructed offline through the same trafilatura path as
`fetcher.fetch_url` and hashed; the result must equal the `content_hash` already
recorded in `MANIFEST.json`. A match proves the reconstruction is byte-exact, so
the stored text is the text the tool actually ingested on 2026-07-29. A mismatch is
reported per URL and makes the run fail.

Input
-----
The 2026-07-29 HTML capture, discovered by the same glob `run_delta_pass.py` uses.
If it is gone, that is a finding about the baseline's reproducibility and this
script says so rather than fetching anything.
"""

import argparse
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
)

_HERE = Path(__file__).resolve().parent
CORPUS = _HERE / "corpus" / "realpage"
MANIFEST = CORPUS / "MANIFEST.json"
BASELINE = CORPUS / "DELTA-BASELINE.json"


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


def build(source: str) -> int:
    delta = _load_sibling("run_delta_pass")
    pages = delta._load_rehearsal_pages(source)
    if not pages:
        print("FAIL: no pages loaded; nothing to build.", file=sys.stderr)
        return 2

    if not MANIFEST.exists():
        print(f"FAIL: {MANIFEST} is missing; cannot verify the reconstruction.",
              file=sys.stderr)
        print("A generator that cannot check its own output has not verified it.",
              file=sys.stderr)
        return 2
    manifest = json.loads(MANIFEST.read_text())
    by_url = {item["url"]: item for item in manifest["items"]}

    items: dict[str, Any] = {}
    verified = 0
    mismatched: list[str] = []
    unknown: list[str] = []

    for page in pages:
        url = page["url"]
        text = page["content_text"] or ""
        entry = by_url.get(url)
        if entry is None:
            unknown.append(url)
        else:
            recomputed = hashlib.sha256(text.encode()).hexdigest()
            if recomputed == entry["snapshot_1"]["content_hash"]:
                verified += 1
            else:
                mismatched.append(url)

        soup = BeautifulSoup(page["raw_html"], "html.parser")
        items[url] = {
            "text": text,
            "hidden_texts": sorted({short_hash(x) for x in _extract_hidden_texts(soup)}),
            "script_contents": sorted(
                {short_hash(x) for x in _extract_suspicious_script_contents(soup)}),
            "iframe_srcs": sorted(
                {short_hash(f.get("src", "") or "") for f in soup.find_all("iframe")}),
            "meta_refreshes": sorted(
                {short_hash(x) for x in _extract_meta_refreshes(soup)}),
            "data_uri_sources": sorted(
                {short_hash(x) for x in _extract_data_uri_sources(soup)}),
        }

    print(f"pages: {len(pages)}")
    print(f"content_hash verified: {verified}/{len(pages)}   "
          f"mismatched: {len(mismatched)}   not in manifest: {len(unknown)}")
    for url in mismatched[:5]:
        print(f"  MISMATCH {url}")
    for url in unknown[:5]:
        print(f"  NOT IN MANIFEST {url}")
    if mismatched:
        print("FAIL: reconstruction does not match the recorded content hashes, so "
              "the stored text is not what the tool ingested.", file=sys.stderr)
        return 1

    out = {
        "baseline": "realpage_v1 snapshot_1",
        "captured": "2026-07-29",
        "purpose": (
            "Everything a future delta pass needs to run the detector against a "
            "fresh fetch, without storing 56.2 MB of raw HTML. `text` is the full "
            "extracted text, so detect_suspicious_changes can be called exactly as "
            "cli.py calls it — including new_domains and major_deletion, which are "
            "guarded behind `if old_text:` and could not fire when this file stored "
            "only line hashes. The five HTML sets are truncated SHA-256 per member, "
            "because they are diffed by set membership and reconstructing them "
            "needs the raw HTML. For those five the evidence STRING is not "
            "recoverable, only whether a flag fires."
        ),
        "verification": {
            "method": (
                "Extracted text was reconstructed offline from the raw HTML captured "
                "on 2026-07-29 using the same trafilatura path as "
                "fetcher.fetch_url, then hashed and compared against the "
                "content_hash already in MANIFEST.json. A match proves the "
                "reconstruction is byte-exact."
            ),
            "pages": len(pages),
            "content_hash_verified": verified,
            "content_hash_mismatched": len(mismatched),
            "not_in_manifest": len(unknown),
        },
        "sets": {
            "text": "full extracted text -> every text check, natively",
            "hidden_texts": "_extract_hidden_texts -> hidden_content",
            "script_contents": "_extract_suspicious_script_contents -> suspicious_script",
            "iframe_srcs": "iframe src attributes -> iframe_detected",
            "meta_refreshes": "_extract_meta_refreshes -> meta_refresh_redirect",
            "data_uri_sources": "_extract_data_uri_sources -> data_uri_embed",
        },
        "items": items,
    }
    CORPUS.mkdir(parents=True, exist_ok=True)
    with BASELINE.open("w") as handle:
        json.dump(out, handle, indent=1, sort_keys=True)
        handle.write("\n")
    print(f"wrote {BASELINE} ({BASELINE.stat().st_size / 1e6:.2f} MB)")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", default="capture",
                        help="HTML source: 'capture' (2026-07-29 bytes) or 'corpus'")
    args = parser.parse_args()
    return build(args.source)


if __name__ == "__main__":
    raise SystemExit(main())
