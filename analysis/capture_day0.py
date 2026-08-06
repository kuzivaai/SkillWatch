"""Capture a day-0 snapshot of the committed 201 URL corpus, with instrumentation.

Ledger item 85. The K3 measurement design fixes a seven day interval on the same
corpus. The repository holds one baseline, captured 2026-07-29, so measuring against
it on any date after 2026-08-05 gives an interval longer than seven days and a result
not comparable with the 47.4% figure, which is itself a seven day number. This script
takes a fresh day-0 capture so the next measurement is a true seven day window.

**It measures nothing and computes no delta.** It fetches, stores and hashes. The
comparison happens in a later cycle on the registered due date.

Why a tracked module rather than a throwaway script
---------------------------------------------------
It generates committed evidence: the integrity manifest, and the archive the next
measurement reads. This repository has logged that defect three times, in ledger items
24, 30 and 34, each time as an untracked generator behind a committed artefact. The
generator of a committed artefact belongs in the repository.

What it records that the 2026-07-29 capture did not
----------------------------------------------------
Every fetch outcome carries `failure_reason`, a label from
`run_delta_pass.FETCH_FAILURE_REASONS`. That is item 82's failure-reason half meeting
the world for the first time: until now it had only ever seen planted inputs. The
technique-attribution half cannot be exercised by a capture, because attribution is a
property of a diff and there is nothing yet to diff against. Items 82 and 43 therefore
stay open and close only at the measurement run.

The URL set is read from the committed `MANIFEST.json` rather than re-derived, so the
corpus is the same 201 URLs by construction and not by resemblance. `--check-urls`
prints the set difference against the manifest and exits without fetching.
"""

import argparse
import concurrent.futures
import datetime
import hashlib
import importlib.util
import json
import sys

from pathlib import Path
from typing import Any

from skillwatch.fetcher import fetch_url

_HERE = Path(__file__).resolve().parent
CORPUS = _HERE / "corpus" / "realpage"
MANIFEST = CORPUS / "MANIFEST.json"


def _load_sibling(name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, _HERE / f"{name}.py")
    if spec is None or spec.loader is None:
        raise SystemExit(f"FAIL: cannot load analysis/{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def manifest_urls() -> list[str]:
    """The corpus URL list, read from the committed manifest, never re-derived."""
    if not MANIFEST.is_file():
        raise SystemExit(f"FAIL: no manifest at {MANIFEST}. Nothing to capture against.")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    return [item["url"] for item in manifest["items"]]


def sha256_of(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def capture(urls: list[str], classify: Any, workers: int = 3,
            timeout: int = 30) -> list[dict[str, Any]]:
    """Fetch every URL once, recording the outcome and a closed-vocabulary reason.

    The defaults are deliberately gentler than `run_delta_pass.py`, which uses ten
    workers and a fifteen second timeout. On 2026-08-06 those settings produced 53
    timeouts across 31 hosts on this corpus, and 55 of those 56 failures succeeded
    immediately on a sequential retry at thirty seconds. The failures were an artefact
    of concurrency, not the world, and a day-0 baseline missing a quarter of its pages
    for non-random reasons would silently degrade the measurement it exists to support.
    A baseline is taken once and read for a week, so it is worth the extra minutes.
    """
    def one(url: str) -> dict[str, Any]:
        stamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        try:
            result = fetch_url(url, timeout=timeout)
        except Exception as exc:
            message = f"EXCEPTION: {exc!r}"
            return {
                "url": url, "fetched_at": stamp, "status_code": None,
                "error": message, "failure_reason": classify(message),
                "content_hash": None, "content_text": None,
                "raw_html": None, "raw_html_hash": None, "has_html": False,
            }
        raw = result.raw_html or ""
        return {
            "url": url, "fetched_at": stamp,
            "status_code": getattr(result, "status_code", None),
            "error": result.error,
            "failure_reason": classify(result.error) if result.error else None,
            "content_hash": result.content_hash,
            "content_text": result.content_text,
            "raw_html": raw or None,
            "raw_html_hash": sha256_of(raw) if raw else None,
            "has_html": bool(raw),
        }

    pages: list[dict[str, Any]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        for i, record in enumerate(pool.map(one, urls), 1):
            pages.append(record)
            if i % 50 == 0:
                print(f"  {i}/{len(urls)}", flush=True)
    return pages


def integrity_manifest(pages: list[dict[str, Any]], archive_path: Path,
                       file_hash: str, size: int, copies: list[str]) -> dict[str, Any]:
    """The same shape verify_capture reads for the 2026-07-29 archive."""
    return {
        "archive": f"realpage-{datetime.date.today().isoformat()} raw HTML capture",
        "archive_file": archive_path.name,
        "file_count": 1,
        "location": str(archive_path),
        "not_committed": "third-party HTML, deliberately outside the repository.",
        "note": (
            "One file, so the file-level manifest is one hash. The per-page hashes "
            "are the useful granularity: they localise a partial or corrupted copy to "
            "specific URLs rather than only detecting that something is wrong."
        ),
        "pages": len(pages),
        "sha256": file_hash,
        "bytes": size,
        "per_page": {
            page["url"]: page["raw_html_hash"] for page in pages if page["raw_html_hash"]
        },
        "copies": [{"path": path, "role": "primary" if i == 0 else "copy"}
                   for i, path in enumerate(copies)],
        "why": (
            "Day-0 for the K3 seven day measurement. Without it the next measurement "
            "would run against the 2026-07-29 baseline and produce a fourteen day or "
            "longer interval, not comparable with the 47.4% seven day result."
        ),
        "independence": (
            "PARTIAL, and the limit is physical, exactly as recorded for the "
            "2026-07-29 archive. All copies share one physical disk on this machine."
        ),
        "verify_with": "python3 analysis/capture_day0.py --verify",
    }


def verify(manifest_path: Path) -> int:
    """Re-hash every recorded copy against the manifest. Exit codes mirror verify_capture."""
    if not manifest_path.is_file():
        print(f"FAIL: no integrity manifest at {manifest_path}", file=sys.stderr)
        return 4
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    expected = data["sha256"]
    missing = corrupt = verified = 0
    for entry in data["copies"]:
        path = Path(entry["path"])
        if not path.is_file():
            print(f"MISSING   {path}")
            missing += 1
            continue
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual == expected:
            print(f"VERIFIED  {path}")
            verified += 1
        else:
            print(f"CORRUPT   {path}\n          expected {expected}\n          actual   {actual}")
            corrupt += 1
    print(f"\n{verified} verified, {missing} missing, {corrupt} corrupt, "
          f"of {len(data['copies'])} recorded copies.")
    if corrupt:
        return 3
    if missing:
        return 2
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-urls", action="store_true",
                        help="print the URL set difference against the manifest and exit")
    parser.add_argument("--verify", action="store_true",
                        help="verify recorded copies against the integrity manifest")
    parser.add_argument("--out-manifest", default=str(CORPUS / "CAPTURE-INTEGRITY-DAY0.json"))
    parser.add_argument("--archive-dir", action="append", default=None,
                        help="archive directory, repeatable; first is primary")
    parser.add_argument("--workers", type=int, default=3,
                        help="concurrent fetches (default 3, gentler than the delta pass)")
    parser.add_argument("--timeout", type=int, default=30,
                        help="per-request timeout in seconds (default 30)")
    args = parser.parse_args()

    manifest_path = Path(args.out_manifest)
    if args.verify:
        return verify(manifest_path)

    urls = manifest_urls()
    if args.check_urls:
        print(f"manifest URLs: {len(urls)}")
        print(f"distinct:      {len(set(urls))}")
        return 0

    run_delta_pass = _load_sibling("run_delta_pass")
    classify = run_delta_pass.classify_fetch_failure

    today = datetime.date.today().isoformat()
    dirs = args.archive_dir or [
        f"/home/mkuziva/.skillwatch-archive/realpage-{today}",
        f"/mnt/d/skillwatch-archive/realpage-{today}",
        f"/mnt/c/Users/mkuzi/skillwatch-archive/realpage-{today}",
    ]

    print(f"capturing {len(urls)} URLs (day-0 for the K3 measurement, {today})")
    pages = capture(urls, classify, workers=args.workers, timeout=args.timeout)

    payload = json.dumps(pages, indent=1)
    primary = Path(dirs[0]) / "fetched_pages.json"
    written: list[str] = []
    for directory in dirs:
        target = Path(directory)
        try:
            target.mkdir(parents=True, exist_ok=True)
            (target / "fetched_pages.json").write_text(payload, encoding="utf-8")
            written.append(str(target / "fetched_pages.json"))
        except OSError as exc:
            print(f"  WARNING: could not write {target}: {exc}", file=sys.stderr)

    file_hash = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    manifest_path.write_text(
        json.dumps(integrity_manifest(pages, primary, file_hash, len(payload.encode()), written),
                   indent=2) + "\n", encoding="utf-8")

    ok = sum(1 for p in pages if p["has_html"])
    reasons: dict[str, int] = {}
    for page in pages:
        if page["failure_reason"]:
            reasons[page["failure_reason"]] = reasons.get(page["failure_reason"], 0) + 1
    print(f"\nfetched OK   {ok}/{len(urls)}")
    for reason in sorted(reasons, key=lambda r: -reasons[r]):
        print(f"  failure     {reason:<24} {reasons[reason]}")
    print(f"\nsha256 {file_hash}")
    print(f"copies written: {len(written)}")
    for path in written:
        print(f"  {path}")
    print(f"\nwrote {manifest_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
