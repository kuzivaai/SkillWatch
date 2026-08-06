"""The capture verifier must tell absence apart from corruption.

The 2026-07-29 real-page capture is irreplaceable: it is the only artefact from
which DELTA-BASELINE.json's derivation can be re-verified, and the only rehearsal
source that exercises the TEXT checks. It lived in one directory on one disk with
nothing detecting its absence.

A second copy alone does not close that. A copy nobody checks is indistinguishable
from no copy on the day it silently rots. So the verifier has to fail — and the two
failures call for different responses:

  "cannot find it"            -> restore from another copy
  "found it and it is wrong"  -> do NOT overwrite the others from this one

Those must never collapse into one exit code or one message.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import socket
import subprocess
import sys
from pathlib import Path
from types import ModuleType

import pytest

REPO = Path(__file__).resolve().parents[1]
VERIFIER = REPO / "analysis" / "verify_capture.py"
REAL_MANIFEST = REPO / "analysis" / "corpus" / "realpage" / "CAPTURE-INTEGRITY.json"

# Exit codes are part of the contract: a caller scripts against them.
EXIT_OK = 0
EXIT_MISSING = 2
EXIT_CORRUPT = 3
EXIT_UNUSABLE = 4

MISSING_PHRASE = "cannot find it"
CORRUPT_PHRASE = "found it and it is wrong"


def run(*args: str) -> subprocess.CompletedProcess[str]:
    """Invoke the verifier as a subprocess so the real exit code is observed."""
    return subprocess.run(
        [sys.executable, str(VERIFIER), *args],
        capture_output=True,
        text=True,
        cwd=REPO,
    )


def _page(url: str, html: str) -> dict[str, object]:
    return {
        "url": url,
        "raw_html": html,
        "raw_html_hash": hashlib.sha256(html.encode("utf-8")).hexdigest(),
        "content_hash": hashlib.sha256(html.encode("utf-8")).hexdigest()[:32],
        "error": None,
        "has_html": True,
        "status_code": 200,
        "fetched_at": "2026-07-29T00:00:00Z",
        "sources": [],
    }


@pytest.fixture
def synthetic(tmp_path: Path) -> dict[str, Path]:
    """A miniature archive plus a manifest in the real manifest's shape.

    Hermetic: nothing here touches the real capture, so a test that corrupts a
    copy can never corrupt the artefact the whole exercise exists to protect.
    """
    pages = [_page(f"https://example.invalid/{i}", f"<html><body>page {i}</body></html>")
             for i in range(12)]
    archive = tmp_path / "fetched_pages.json"
    archive.write_text(json.dumps(pages), encoding="utf-8")

    manifest = {
        "archive": "synthetic fixture",
        "archive_file": {
            "name": "fetched_pages.json",
            "bytes": archive.stat().st_size,
            "sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
        },
        "file_count": 1,
        "pages": len(pages),
        "per_page": {
            p["url"]: {
                "bytes": len(p["raw_html"]),  # characters, matching the real manifest
                "content_hash": p["content_hash"],
                "raw_html_sha256": p["raw_html_hash"],
            }
            for p in pages
        },
        "copies": [{"path": str(archive), "medium": "tmp_path"}],
        "holders": [socket.gethostname()],
    }
    manifest_path = tmp_path / "MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    return {"archive": archive, "manifest": manifest_path, "root": tmp_path}


# --- the three cases the brief names -----------------------------------------


def test_clean_copy_exits_zero(synthetic: dict[str, Path]) -> None:
    r = run("--manifest", str(synthetic["manifest"]))
    assert r.returncode == EXIT_OK, r.stdout + r.stderr
    assert "VERIFIED" in r.stdout


def test_absent_copy_exits_nonzero_and_says_it_cannot_find_it(
    synthetic: dict[str, Path], tmp_path: Path
) -> None:
    absent = tmp_path / "no" / "such" / "fetched_pages.json"
    r = run("--manifest", str(synthetic["manifest"]), "--copy", str(absent))
    assert r.returncode == EXIT_MISSING, r.stdout + r.stderr
    out = (r.stdout + r.stderr).lower()
    assert MISSING_PHRASE in out
    assert CORRUPT_PHRASE not in out


def test_corrupt_copy_exits_nonzero_with_a_different_message(
    synthetic: dict[str, Path], tmp_path: Path
) -> None:
    corrupt = tmp_path / "corrupt" / "fetched_pages.json"
    corrupt.parent.mkdir(parents=True)
    shutil.copy2(synthetic["archive"], corrupt)
    raw = bytearray(corrupt.read_bytes())
    raw[len(raw) // 2] = raw[len(raw) // 2] ^ 0x20  # flip one bit in one byte
    corrupt.write_bytes(bytes(raw))

    r = run("--manifest", str(synthetic["manifest"]), "--copy", str(corrupt))
    assert r.returncode == EXIT_CORRUPT, r.stdout + r.stderr
    out = (r.stdout + r.stderr).lower()
    assert CORRUPT_PHRASE in out
    assert MISSING_PHRASE not in out


def test_absent_and_corrupt_do_not_share_an_exit_code() -> None:
    assert EXIT_MISSING != EXIT_CORRUPT


# --- the distinctions that make the two cases actionable ---------------------


def test_corruption_is_localised_to_the_offending_url(
    synthetic: dict[str, Path], tmp_path: Path
) -> None:
    """The archive hash says 'wrong'; the per-page hashes say 'wrong HERE'."""
    pages = json.loads(synthetic["archive"].read_text())
    pages[3]["raw_html"] = "<html><body>tampered</body></html>"
    damaged = tmp_path / "damaged" / "fetched_pages.json"
    damaged.parent.mkdir(parents=True)
    damaged.write_text(json.dumps(pages), encoding="utf-8")

    r = run("--manifest", str(synthetic["manifest"]), "--copy", str(damaged), "--all-pages")
    assert r.returncode == EXIT_CORRUPT, r.stdout + r.stderr
    assert "https://example.invalid/3" in r.stdout + r.stderr


def test_corrupt_wins_over_missing_when_both_occur(
    synthetic: dict[str, Path], tmp_path: Path
) -> None:
    """A corrupt copy is the more urgent signal: it must not be overwritten from.

    Reporting only 'missing' here would invite restoring the absent copy FROM the
    corrupt one.
    """
    corrupt = tmp_path / "c" / "fetched_pages.json"
    corrupt.parent.mkdir(parents=True)
    corrupt.write_text("{}", encoding="utf-8")
    absent = tmp_path / "gone" / "fetched_pages.json"

    r = run("--manifest", str(synthetic["manifest"]),
            "--copy", str(corrupt), "--copy", str(absent))
    assert r.returncode == EXIT_CORRUPT, r.stdout + r.stderr
    out = (r.stdout + r.stderr).lower()
    assert CORRUPT_PHRASE in out
    assert MISSING_PHRASE in out  # both are still reported


def test_every_recorded_copy_is_checked_not_just_the_first(
    synthetic: dict[str, Path], tmp_path: Path
) -> None:
    good = synthetic["archive"]
    absent = tmp_path / "second" / "fetched_pages.json"
    r = run("--manifest", str(synthetic["manifest"]),
            "--copy", str(good), "--copy", str(absent))
    assert r.returncode == EXIT_MISSING, r.stdout + r.stderr
    assert str(absent) in r.stdout + r.stderr
    assert str(good) in r.stdout + r.stderr


# --- fail closed rather than vacuously -------------------------------------


def test_an_unusable_manifest_is_not_a_pass(tmp_path: Path) -> None:
    """A check that could not inspect its subject has not passed.

    Same shape as the four recurrences already in this repository's ledger.
    """
    bad = tmp_path / "MANIFEST.json"
    bad.write_text("{not json", encoding="utf-8")
    r = run("--manifest", str(bad))
    assert r.returncode == EXIT_UNUSABLE, r.stdout + r.stderr
    assert "NOT passed" in r.stdout + r.stderr


def test_a_missing_manifest_is_not_a_pass(tmp_path: Path) -> None:
    r = run("--manifest", str(tmp_path / "absent.json"))
    assert r.returncode == EXIT_UNUSABLE, r.stdout + r.stderr


def test_a_manifest_recording_no_copies_is_not_a_pass(tmp_path: Path) -> None:
    """Zero copies must not verify vacuously — that is 'no copy' spelled quietly."""
    m = tmp_path / "MANIFEST.json"
    m.write_text(json.dumps({
        "archive_file": {"name": "x", "bytes": 1, "sha256": "00" * 32},
        "per_page": {}, "copies": [],
    }), encoding="utf-8")
    r = run("--manifest", str(m))
    assert r.returncode != EXIT_OK, r.stdout + r.stderr


@pytest.mark.parametrize("copies", [[None], ["not-an-object"], [{}], [{"path": 42}]])
def test_a_manifest_with_malformed_copies_is_unusable(
    synthetic: dict[str, Path], copies: list[object]
) -> None:
    """Valid JSON with an invalid copy registry must honour the exit-4 contract."""
    manifest = json.loads(synthetic["manifest"].read_text(encoding="utf-8"))
    manifest["copies"] = copies
    synthetic["manifest"].write_text(json.dumps(manifest), encoding="utf-8")

    r = run("--manifest", str(synthetic["manifest"]))

    assert r.returncode == EXIT_UNUSABLE, r.stdout + r.stderr
    assert "UNUSABLE" in r.stdout + r.stderr
    assert "Traceback" not in r.stdout + r.stderr


def test_page_sample_is_deterministic(synthetic: dict[str, Path]) -> None:
    """Two runs must sample the same pages, or a passing run proves nothing."""
    a = run("--manifest", str(synthetic["manifest"]), "--pages", "4", "--verbose")
    b = run("--manifest", str(synthetic["manifest"]), "--pages", "4", "--verbose")
    assert a.returncode == EXIT_OK == b.returncode, a.stdout + b.stdout
    sampled_a = [ln for ln in a.stdout.splitlines() if "example.invalid" in ln]
    sampled_b = [ln for ln in b.stdout.splitlines() if "example.invalid" in ln]
    assert sampled_a == sampled_b
    assert len(sampled_a) == 4


# --- the real artefact -------------------------------------------------------


def test_the_real_manifest_records_where_every_copy_lives() -> None:
    m = json.loads(REAL_MANIFEST.read_text())
    assert m.get("copies"), "the manifest must record every copy's location"
    for c in m["copies"]:
        assert c.get("path"), c
        assert c.get("medium"), f"a copy must say what it is stored on: {c}"
    assert m.get("holders"), "the manifest must record which machines hold a copy"


def test_the_real_capture_verifies_on_a_machine_that_holds_it() -> None:
    """On a holder, absence or rot is a hard failure. Elsewhere, the absent path
    is exercised instead — so nothing is skipped and nothing passes vacuously.
    """
    m = json.loads(REAL_MANIFEST.read_text())
    r = run("--manifest", str(REAL_MANIFEST), "--pages", "6")
    if socket.gethostname() in m["holders"]:
        assert r.returncode == EXIT_OK, (
            "this machine is recorded as holding the capture, so a non-zero exit "
            "means a copy is gone or has rotted:\n" + r.stdout + r.stderr
        )
    else:
        assert r.returncode == EXIT_MISSING, r.stdout + r.stderr
        assert MISSING_PHRASE in (r.stdout + r.stderr).lower()


def test_the_real_manifest_copies_are_not_all_on_one_medium() -> None:
    """A second copy sharing every failure mode with the first is not redundancy."""
    m = json.loads(REAL_MANIFEST.read_text())
    media = {c["medium"] for c in m["copies"]}
    assert len(media) > 1, f"all copies share one medium: {media}"


# --- the consumer must refuse a corrupt capture, not silently use it ----------
#
# A verifier nobody runs is the same defect one level up. `--source capture` chose
# the first path that existed and loaded it without checking a single hash, so a
# rotted copy would have been fed into a rehearsal and reported as a result.


def _load_delta() -> ModuleType:
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "run_delta_pass", REPO / "analysis" / "run_delta_pass.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules["run_delta_pass"] = mod
    spec.loader.exec_module(mod)
    return mod


def test_capture_source_refuses_a_corrupt_copy(tmp_path: Path) -> None:
    delta = _load_delta()
    corrupt = tmp_path / "fetched_pages.json"
    corrupt.write_text(json.dumps([_page("https://example.invalid/x", "<html>x</html>")]),
                       encoding="utf-8")
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(delta, "_CAPTURE_CANDIDATES", (str(corrupt),))
        with pytest.raises(SystemExit) as exc:
            delta._load_rehearsal_pages("capture")
    assert CORRUPT_PHRASE in str(exc.value).lower(), str(exc.value)


def test_capture_source_says_cannot_find_it_when_no_copy_exists(tmp_path: Path) -> None:
    delta = _load_delta()
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(delta, "_CAPTURE_CANDIDATES", (str(tmp_path / "nope.json"),))
        with pytest.raises(SystemExit) as exc:
            delta._load_rehearsal_pages("capture")
    assert MISSING_PHRASE in str(exc.value).lower(), str(exc.value)


def test_capture_candidates_are_driven_by_the_manifest() -> None:
    """One registry of copies, not two lists free to drift apart.

    A second hand-maintained copy of the copy list is the figure-drift defect in
    another costume.
    """
    delta = _load_delta()
    recorded = [c["path"] for c in json.loads(REAL_MANIFEST.read_text())["copies"]]
    for path in recorded:
        assert path in delta._CAPTURE_CANDIDATES, (
            f"{path} is recorded in the manifest but run_delta_pass would not look "
            f"there: {delta._CAPTURE_CANDIDATES}")


def test_an_explicit_path_that_is_a_recorded_copy_is_verified(tmp_path: Path) -> None:
    """`make_baseline.py --source <path>` reaches the same loader.

    Naming a recorded copy explicitly must not be a way to bypass the hash check —
    that is how a corrupt copy gets promoted into a regenerated baseline.
    """
    delta = _load_delta()
    recorded = json.loads(REAL_MANIFEST.read_text())["copies"][0]["path"]
    corrupt = tmp_path / "fetched_pages.json"
    corrupt.write_text(json.dumps([_page("https://example.invalid/y", "<html>y</html>")]),
                       encoding="utf-8")
    with pytest.MonkeyPatch.context() as mp:
        # The path the caller names is a recorded copy; its bytes are wrong.
        mp.setattr(delta._verify_capture, "recorded_copies", lambda *a, **k: (str(corrupt),))
        mp.setattr(delta, "_CAPTURE_CANDIDATES", (str(corrupt),))
        with pytest.raises(SystemExit) as exc:
            delta._load_rehearsal_pages(str(corrupt))
    assert CORRUPT_PHRASE in str(exc.value).lower(), str(exc.value)
    assert str(recorded) not in str(exc.value)  # the real copies were not touched


def test_an_unrecorded_explicit_path_loads_but_is_flagged_unverified(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """An arbitrary path may legitimately be a different capture — so it loads.

    But it must not look verified. Silence here would read as a clean bill of health.
    """
    delta = _load_delta()
    other = tmp_path / "fetched_pages.json"
    other.write_text(json.dumps([
        dict(_page("https://example.invalid/z", "<html><body>z</body></html>"),
             has_html=True)
    ]), encoding="utf-8")
    pages = delta._load_rehearsal_pages(str(other))
    assert len(pages) == 1
    err = capsys.readouterr().err
    assert "UNVERIFIED" in err, err


def test_the_four_level_scratchpad_glob_is_preserved() -> None:
    """A three-level glob finds nothing and makes a present file look lost.

    That near-miss is recorded in ledger item 51; this asserts the fix stays.
    """
    delta = _load_delta()
    globs = [c for c in delta._CAPTURE_CANDIDATES if "*" in c]
    assert globs, "the surviving-scratchpad glob was dropped"
    for g in globs:
        if "/tmp/claude-" in g:
            before_file = g.rsplit("/", 1)[0]
            depth = before_file.strip("/").count("/") + 1
            assert depth >= 4, f"{g} is only {depth} levels deep; four are needed"
