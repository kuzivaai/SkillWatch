"""The delta pipeline must be proven to run before 2026-08-05, without fetching.

`analysis/run_delta_pass.py` is ~235 lines of which only the date guard had ever
executed. On 2026-08-05 its fetch, extraction, set-diff, detector-call, aggregation
and report paths run for the first time, against live third-party pages, with the
result deciding ledger items 37, 38 and 43 and no window to debug.

Rehearsal mode feeds one stored snapshot in as BOTH sides of the diff. The result is
a zero-change delta and is worthless as a finding — it cannot be, since nothing
changed. What it proves is that every stage executes and returns the shape the real
pass will return.

These tests assert the pipeline completes and that every field a caller reads is
populated. They make no network request and they do not run the real pass.
"""
from __future__ import annotations

import importlib.util
import sys

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent


def _load(name: str):
    spec = importlib.util.spec_from_file_location(
        name, REPO_ROOT / "analysis" / f"{name}.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


delta = _load("run_delta_pass")

# The committed HTML corpus is always present, so the rehearsal is runnable by any
# later session regardless of whether a scratchpad capture survived.
COMMITTED_SOURCE = "corpus"

EXPECTED_FIELDS = {
    "source", "pages_loaded", "stages", "gate_open", "flagged", "by_code",
    "is_measurement", "warning", "reachability", "exercise_with_empty_baseline",
}

EXPECTED_STAGES = {
    "load_source",
    "extract_sets",
    "text_line_diff",
    "detect_suspicious_changes",
    "html_set_diff",
    "reachability_probe",
    "aggregate",
    "format_report",
}

# The two checks detector.py guards behind `if old_text:`. Until 2026-07-29 the
# delta pass passed old_text=None, so NEITHER could ever fire — and new_domains is
# one of the four checks that produce false positives in the synthetic corpus.
GUARDED_CHECKS = ("new_domains", "major_deletion")


def emittable_codes() -> set[str]:
    """Every flag code detector.py can emit, read from its source.

    NOTE the character class includes DIGITS. A `[a-z_]*` pattern silently omits
    `new_base64`, which is how a 13-code set gets reported as 12.
    """
    import re
    source = (REPO_ROOT / "skillwatch" / "detector.py").read_text(encoding="utf-8")
    return set(re.findall(r'code="([a-z0-9_]+)"', source))


class TestRehearsalModeExists:
    def test_the_module_exposes_a_rehearse_entry_point(self):
        assert hasattr(delta, "rehearse"), (
            "run_delta_pass.py must expose rehearse() so the pipeline can be "
            "exercised without a network call"
        )

    def test_rehearsal_is_reachable_from_the_cli(self):
        assert hasattr(delta, "REHEARSAL_SOURCES")
        assert COMMITTED_SOURCE in delta.REHEARSAL_SOURCES


@pytest.fixture(scope="module")
def report():
    """One rehearsal per module — it runs the whole pipeline and costs seconds."""
    return delta.rehearse(COMMITTED_SOURCE)


class TestRehearsalCompletes:
    def test_report_has_every_expected_field(self, report):
        missing = EXPECTED_FIELDS - set(report)
        assert not missing, f"rehearsal report is missing {sorted(missing)}"

    def test_no_expected_field_is_none(self, report):
        empty = [k for k in EXPECTED_FIELDS if report.get(k) is None]
        assert not empty, f"rehearsal report left {sorted(empty)} unpopulated"

    def test_pages_were_actually_loaded(self, report):
        assert report["pages_loaded"] > 0, (
            "a rehearsal over zero pages executes nothing and proves nothing"
        )

    def test_every_pipeline_stage_is_reported(self, report):
        missing = EXPECTED_STAGES - set(report["stages"])
        assert not missing, f"stages not reported: {sorted(missing)}"

    def test_every_pipeline_stage_executed(self, report):
        skipped = [name for name, ran in report["stages"].items() if not ran]
        assert not skipped, (
            f"these stages did not execute, so they remain unproven: {skipped}"
        )

    def test_the_result_is_labelled_not_a_measurement(self, report):
        assert report["is_measurement"] is False
        assert "not a measurement" in report["warning"].lower()

    def test_a_zero_change_delta_produces_no_flags(self, report):
        # Feeding one snapshot as both sides must yield an empty delta. If it does
        # not, the set-diff is wrong and the real pass would over-report.
        assert report["flagged"] == 0, (
            f"identical snapshots produced {report['flagged']} flagged pages and "
            f"{report['by_code']} — the set difference is not empty when it must be"
        )
        assert report["by_code"] == {}

    def test_the_gate_is_closed_for_identical_snapshots(self, report):
        # cli.py:443 — detection runs only on a text-hash change. Identical text
        # means the gate never opens, which the report must show honestly.
        assert report["gate_open"] == 0


class TestTheGuardedChecksAreReachable:
    """The defect the rehearsal found, pinned so it cannot return."""

    def test_reachability_is_reported_for_both_guarded_checks(self, report):
        for code in GUARDED_CHECKS:
            assert code in report["reachability"], (
                f"{code} is guarded behind `if old_text:` in detector.py and must "
                f"be probed explicitly — an empty baseline cannot reach it"
            )

    @pytest.mark.parametrize("code", GUARDED_CHECKS)
    def test_the_guarded_check_is_reachable(self, code, report):
        assert report["reachability"][code] is True, (
            f"{code} cannot be emitted through flags_for. The delta pass would "
            f"silently under-report it on 2026-08-05."
        )

    def test_the_baseline_stores_text_not_only_line_hashes(self):
        # The fix: storing full old text rather than hashes of lines, so
        # detect_suspicious_changes receives a truthy old_text.
        import json
        baseline = json.loads(
            (REPO_ROOT / "analysis" / "corpus" / "realpage"
             / "DELTA-BASELINE.json").read_text())
        first = next(iter(baseline["items"].values()))
        assert "text" in first, (
            "DELTA-BASELINE.json must store the extracted text; line hashes alone "
            "leave old_text falsy and disable two checks"
        )
        assert isinstance(first["text"], str)

    def test_baseline_reconstruction_was_verified(self):
        import json
        baseline = json.loads(
            (REPO_ROOT / "analysis" / "corpus" / "realpage"
             / "DELTA-BASELINE.json").read_text())
        v = baseline["verification"]
        assert v["content_hash_mismatched"] == 0
        assert v["content_hash_verified"] == v["pages"]


class TestEveryEmittableCodeIsProvenReachable:
    """The CLASS, not the instance.

    Two codes were found unable to fire through this pipeline because detector.py
    guards them behind a truthy `old_text` and the pipeline passed None. Probing only
    those two is the weakest possible sample — they are the two already known broken.
    Every code detector.py can emit must be proven emittable through `flags_for`, and
    the count checked must equal the count emittable, so adding a flag without a
    reachability assertion fails the suite.
    """

    def test_the_probe_covers_every_emittable_code(self, report):
        emittable = emittable_codes()
        probed = set(report["reachability"])
        missing = emittable - probed
        assert not missing, (
            f"{len(missing)} code(s) detector.py can emit have no reachability "
            f"assertion: {sorted(missing)}. A probe covering a hardcoded subset is "
            f"the defect being closed here."
        )

    def test_the_probe_checks_nothing_that_cannot_be_emitted(self, report):
        stray = set(report["reachability"]) - emittable_codes()
        assert not stray, (
            f"probe asserts codes detector.py cannot emit: {sorted(stray)}"
        )

    def test_the_counts_are_asserted_equal_inside_the_probe(self, report):
        assert report["reachability_complete"] is True, (
            "the probe must assert that the number of codes checked equals the "
            "number emittable, not merely happen to match"
        )

    @pytest.mark.parametrize("code", sorted(emittable_codes()))
    def test_every_code_is_reachable(self, code, report):
        assert report["reachability"].get(code) is True, (
            f"{code} cannot be emitted through flags_for. The delta pass would "
            f"silently under-report it on 2026-08-05 — the same defect as the "
            f"old_text=None one, in a different check."
        )


class TestRehearsalMakesNoNetworkRequest:
    def test_fetch_url_is_never_called(self, monkeypatch):
        def explode(*args, **kwargs):
            raise AssertionError(
                "rehearsal attempted a network fetch; it must read stored HTML only"
            )

        monkeypatch.setattr(delta, "fetch_url", explode)
        report = delta.rehearse(COMMITTED_SOURCE)
        assert report["pages_loaded"] > 0


class TestRehearsalOutputIsConfined:
    def test_documentation_surfaces_are_not_writable_targets(self):
        # A zero-change delta must never reach a surface a reader would take for a
        # measurement. The allowed output roots are stdout and analysis/.
        assert delta.REHEARSAL_OUTPUT_DIR.name == "analysis"
        for forbidden in ("README.md", "SHIP-READINESS.md", "PATTERNS.md",
                          "CHANGELOG.md", "docs"):
            assert forbidden not in str(delta.REHEARSAL_OUTPUT_DIR)

    def test_a_missing_source_is_reported_not_fetched(self):
        # "If the stored HTML is no longer on disk, say so plainly — that is a
        # finding about the baseline's reproducibility, not a reason to fetch."
        with pytest.raises(SystemExit) as excinfo:
            delta.rehearse("definitely-not-a-source")
        assert "not a reason to fetch" in str(excinfo.value).lower() or \
            "unknown rehearsal source" in str(excinfo.value).lower()
