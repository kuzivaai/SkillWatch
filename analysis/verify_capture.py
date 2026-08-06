"""Verify every recorded copy of the 2026-07-29 real-page capture.

Run this before anything relies on the archive:

    python3 analysis/verify_capture.py

Exit codes are the contract, because "cannot find it" and "found it and it is
wrong" call for opposite responses:

    0  every recorded copy is present and its hashes match
    2  MISSING  — a recorded copy is absent.  Restore it FROM a verified copy.
    3  CORRUPT  — a recorded copy is present and wrong.  Do NOT restore FROM it.
    4  UNUSABLE — this manifest is absent, unparseable, or records no copies.

Why 3 outranks 2 when both occur: reporting only the absence would invite
restoring the missing copy from the corrupt one, which propagates the damage.

Why this exists
---------------
The capture is irreplaceable. It is the only artefact from which
DELTA-BASELINE.json's derivation can be re-verified, and the only rehearsal source
that exercises the TEXT checks — the committed html_v1 corpus runs only the five
HTML checks, which is exactly why a corpus-only rehearsal could not see the
old_text=None defect.

Until now it sat in one directory on one disk with nothing detecting its absence.
A second copy alone does not close that: a copy nobody checks is indistinguishable
from no copy on the day it silently rots. This script is the part that fails.

What it cannot see
------------------
It verifies the copies the manifest RECORDS. A copy made and never recorded is
invisible to it, and so is the manifest's own corruption — the manifest is the
reference, so it cannot check itself. Recording a new copy is a manifest edit,
which is why `copies` is committed and reviewable rather than discovered by
scanning the disk. This is the same failure shape the repository has hit four
times: a check that reports green because what it should examine is out of its
scope. Stated here rather than left implied.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import socket
import sys
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = REPO / "analysis" / "corpus" / "realpage" / "CAPTURE-INTEGRITY.json"

EXIT_OK = 0
EXIT_MISSING = 2
EXIT_CORRUPT = 3
EXIT_UNUSABLE = 4

# The two phrases the tests pin. They are the whole point of separate exit codes,
# so they are constants rather than inline strings that could drift apart.
MISSING_PHRASE = "cannot find it"
CORRUPT_PHRASE = "found it and it is wrong"

# Reading a 60 MB JSON per copy is the expensive part, so per-page verification
# samples by default. The archive-level SHA-256 already covers every byte; the
# per-page hashes exist to LOCALISE damage to specific URLs, which only matters
# once something has already mismatched.
DEFAULT_SAMPLE = 8


def sha256_file(path: Path) -> tuple[str, int]:
    """Stream the hash. The archive is ~60 MB and may sit on a 9p mount."""
    h = hashlib.sha256()
    size = 0
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
            size += len(chunk)
    return h.hexdigest(), size


def sample_urls(per_page: dict[str, Any], n: int) -> list[str]:
    """A deterministic spread across the sorted URL list.

    Deterministic because a passing run has to mean something: if the sample
    varied per run, a clean result would only say "the pages we happened to look
    at today were fine". Sorted-with-stride rather than random-with-seed so no
    RNG implementation detail can change which pages are covered.
    """
    urls = sorted(per_page)
    if n <= 0 or n >= len(urls):
        return urls
    stride = len(urls) / n
    return [urls[int(i * stride)] for i in range(n)]


def verify_pages(
    archive: Path, per_page: dict[str, Any], want: list[str], verbose: bool
) -> list[str]:
    """Return the URLs whose stored HTML no longer matches its recorded hash."""
    records = json.loads(archive.read_text(encoding="utf-8"))
    by_url = {r["url"]: r for r in records if isinstance(r, dict) and "url" in r}
    bad: list[str] = []
    for url in want:
        expected = per_page[url]
        record = by_url.get(url)
        if record is None or "raw_html" in record and record["raw_html"] is None:
            bad.append(f"{url} (absent from this copy)")
            continue
        if "raw_html" not in record:
            bad.append(f"{url} (this copy has no raw_html for it)")
            continue
        html = record["raw_html"]
        got = hashlib.sha256(html.encode("utf-8")).hexdigest()
        # `bytes` in the manifest is len() of the Python str — a character count,
        # not a UTF-8 byte count. Verified against all 201 pages before relying
        # on it; comparing it as UTF-8 length would false-positive on 182 of them.
        if got != expected["raw_html_sha256"]:
            bad.append(f"{url} (raw_html hash differs)")
        elif len(html) != expected["bytes"]:
            bad.append(f"{url} (length {len(html)} != recorded {expected['bytes']})")
        elif verbose:
            print(f"    ok  {url}")
    return bad


# --- the API consumers use ----------------------------------------------------
#
# `recorded_copies` is deliberately the ONLY registry of where the capture lives.
# A consumer keeping its own second list of paths is the figure-drift defect in
# another costume: two copies of the same facts, free to diverge, with the stale
# one still looking authoritative.


def _copy_paths(manifest: Any) -> tuple[str, ...]:
    """Return a validated copy registry or raise ``ValueError``."""
    if not isinstance(manifest, dict):
        raise ValueError("the manifest root is not an object")
    copies = manifest.get("copies")
    if not isinstance(copies, list):
        raise ValueError("copies is not a list")
    paths: list[str] = []
    for index, copy in enumerate(copies):
        if not isinstance(copy, dict):
            raise ValueError(f"copies[{index}] is not an object")
        path = copy.get("path")
        if not isinstance(path, str) or not path.strip():
            raise ValueError(f"copies[{index}].path is not a non-empty string")
        paths.append(path)
    return tuple(paths)


def recorded_copies(manifest_path: Path | str = DEFAULT_MANIFEST) -> tuple[str, ...]:
    """Every validated path the manifest records; empty if it is unusable."""
    try:
        manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
        return _copy_paths(manifest)
    except (OSError, json.JSONDecodeError, UnicodeDecodeError, ValueError):
        return ()


def assert_capture_trustworthy(
    path: Path | str, manifest_path: Path | str = DEFAULT_MANIFEST
) -> None:
    """Raise SystemExit unless `path` matches the manifest's recorded archive hash.

    Uses the same two phrases the standalone script prints, so a caller who greps
    output and a caller who catches SystemExit see one vocabulary rather than two.

    A verifier nobody runs is the defect one level up from the one it fixes, which
    is why the consumers call this rather than relying on someone remembering to
    run the script.
    """
    path = Path(path)
    try:
        manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
        expected_sha = manifest["archive_file"]["sha256"]
        expected_bytes = manifest["archive_file"]["bytes"]
    except (OSError, json.JSONDecodeError, UnicodeDecodeError, KeyError, TypeError) as exc:
        raise SystemExit(
            f"FAIL: cannot verify {path}: the integrity manifest {manifest_path} is "
            f"unusable ({exc}). This has NOT passed — proceeding would use bytes "
            f"nothing has checked."
        ) from exc

    if not path.exists():
        raise SystemExit(
            f"FAIL: {MISSING_PHRASE} — nothing is at {path}.\n"
            f"  Restore it from another copy recorded in {manifest_path}, then "
            f"re-run `python3 analysis/verify_capture.py`.\n"
            f"  If no copy survives, the capture is lost: DELTA-BASELINE.json can no "
            f"longer be re-derived and --source corpus is the only rehearsal left. "
            f"This is a FINDING about reproducibility, not a reason to fetch."
        )

    got_sha, got_bytes = sha256_file(path)
    if got_sha != expected_sha:
        raise SystemExit(
            f"FAIL: {CORRUPT_PHRASE} — {path}\n"
            f"  sha256 {got_sha}\n"
            f"  wanted {expected_sha}\n"
            f"  {got_bytes} bytes, recorded {expected_bytes}.\n"
            f"  Do NOT restore other copies from this one. Run "
            f"`python3 analysis/verify_capture.py --all-pages` to localise the damage "
            f"and to find a copy that still verifies."
        )


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--manifest", default=str(DEFAULT_MANIFEST),
                    help="integrity manifest to verify against")
    ap.add_argument("--copy", action="append", default=None, metavar="PATH",
                    help="verify these paths instead of the manifest's copies list "
                         "(repeatable; used by the tests)")
    ap.add_argument("--pages", type=int, default=DEFAULT_SAMPLE,
                    help=f"how many per-page hashes to check (default {DEFAULT_SAMPLE})")
    ap.add_argument("--all-pages", action="store_true",
                    help="check every recorded per-page hash, not a sample")
    ap.add_argument("--verbose", action="store_true",
                    help="name each page checked")
    args = ap.parse_args()

    manifest_path = Path(args.manifest)
    if not manifest_path.exists():
        print(f"UNUSABLE: no manifest at {manifest_path}.", file=sys.stderr)
        print("This check has NOT passed — it could not inspect its subject.",
              file=sys.stderr)
        return EXIT_UNUSABLE
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        print(f"UNUSABLE: {manifest_path} will not parse: {exc}", file=sys.stderr)
        print("This check has NOT passed — it could not inspect its subject.",
              file=sys.stderr)
        return EXIT_UNUSABLE

    try:
        expected_sha = manifest["archive_file"]["sha256"]
        expected_bytes = manifest["archive_file"]["bytes"]
        per_page = manifest["per_page"]
    except (KeyError, TypeError) as exc:
        print(f"UNUSABLE: {manifest_path} lacks {exc}.", file=sys.stderr)
        print("This check has NOT passed — it could not inspect its subject.",
              file=sys.stderr)
        return EXIT_UNUSABLE

    if args.copy:
        paths = [Path(p) for p in args.copy]
    else:
        try:
            paths = [Path(path) for path in _copy_paths(manifest)]
        except ValueError as exc:
            print(f"UNUSABLE: {manifest_path} has an invalid copy registry: {exc}.",
                  file=sys.stderr)
            print("This check has NOT passed — it could not inspect its subject.",
                  file=sys.stderr)
            return EXIT_UNUSABLE
        if not paths:
            # Zero copies must not verify vacuously. That is "no copy" spelled quietly.
            print(f"UNUSABLE: {manifest_path} records no copies, so there is nothing "
                  f"to verify. An empty copies list is not a pass.", file=sys.stderr)
            print("This check has NOT passed — it could not inspect its subject.",
                  file=sys.stderr)
            return EXIT_UNUSABLE

    want = sorted(per_page) if args.all_pages else sample_urls(per_page, args.pages)

    print(f"manifest      {manifest_path}")
    print(f"expected      sha256 {expected_sha}  ({expected_bytes} bytes)")
    print(f"per-page      {len(want)} of {len(per_page)} recorded hashes checked"
          f"{' (all)' if len(want) == len(per_page) else ' (deterministic sample)'}")
    holders = manifest.get("holders") or []
    here = socket.gethostname()
    print(f"host          {here}"
          f"{' (recorded holder)' if here in holders else ' (not a recorded holder)'}")
    print()

    missing: list[Path] = []
    corrupt: list[tuple[Path, str]] = []
    verified: list[Path] = []

    for path in paths:
        if not path.exists():
            missing.append(path)
            print(f"MISSING   {path}")
            print(f"          {MISSING_PHRASE} — nothing is at this path.")
            continue
        got_sha, got_bytes = sha256_file(path)
        if got_sha != expected_sha:
            detail = f"sha256 {got_sha} != {expected_sha}"
            if got_bytes != expected_bytes:
                detail += f"; {got_bytes} bytes, recorded {expected_bytes}"
            corrupt.append((path, detail))
            print(f"CORRUPT   {path}")
            print(f"          {CORRUPT_PHRASE} — {detail}")
            try:
                bad = verify_pages(path, per_page, want, args.verbose)
            except (json.JSONDecodeError, UnicodeDecodeError, KeyError, TypeError) as exc:
                print(f"          per-page localisation impossible: {exc}")
            else:
                if bad:
                    print(f"          damage localised to {len(bad)} of {len(want)} "
                          f"checked pages:")
                    for b in bad:
                        print(f"            {b}")
                else:
                    print("          none of the checked pages differ — the damage is "
                          "outside the sample. Re-run with --all-pages.")
            continue

        bad = verify_pages(path, per_page, want, args.verbose)
        if bad:
            # The archive hash matched but a page did not. That means the manifest
            # and the file disagree about the SAME bytes, which is a manifest bug,
            # not disk rot. Still non-zero: it is not verified either way.
            detail = (f"archive sha256 matched but {len(bad)} checked page(s) did not: "
                      f"{bad}. The manifest and the file disagree about identical "
                      f"bytes, which is a manifest defect rather than disk rot.")
            corrupt.append((path, detail))
            print(f"CORRUPT   {path}")
            print(f"          {CORRUPT_PHRASE} — {detail}")
            continue

        verified.append(path)
        print(f"VERIFIED  {path}")
        print(f"          sha256 matches; {len(want)} per-page hashes match.")

    print()
    print(f"{len(verified)} verified, {len(missing)} missing, {len(corrupt)} corrupt, "
          f"of {len(paths)} recorded copies.")

    if corrupt:
        print()
        print("EXIT 3 (CORRUPT). A copy is present and wrong. Do NOT restore the "
              "others from it. Restore it from a copy this run reported VERIFIED.")
        if missing:
            print(f"{len(missing)} copy/copies are also absent; that is reported above "
                  f"but 3 outranks 2 so the corrupt copy is not used as a source.")
        return EXIT_CORRUPT
    if missing:
        print()
        print("EXIT 2 (MISSING). Restore each absent copy from one reported VERIFIED "
              "above. If none was verified, the capture is lost and "
              "analysis/corpus/realpage/DELTA-BASELINE.json can no longer be "
              "re-derived — say so rather than proceeding.")
        return EXIT_MISSING
    print("All recorded copies verified against the manifest.")
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
