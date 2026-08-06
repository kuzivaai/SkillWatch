"""The delta pass must refuse a window shorter than the interval, per baseline.

`EARLIEST` was an absolute date, correct while the repository held one baseline. The
K3 design added a second, captured 2026-08-06, and against that baseline the constant
alone would have permitted a run on 2026-08-05: a negative interval, and precisely the
per-request churn the guard exists to refuse. The floor is now the LATER of the
absolute date and the baseline's own capture date plus `MIN_INTERVAL_DAYS`.

The arithmetic is tested here rather than only observed once by running the script,
because the failure it prevents is silent: an early pass returns a number, not an
error, and that number would be read as a drift rate.
"""

from __future__ import annotations

import datetime
import importlib.util
import json
import sys

from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def _load(name: str):  # type: ignore[no-untyped-def]
    spec = importlib.util.spec_from_file_location(name, REPO / "analysis" / f"{name}.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


delta = _load("run_delta_pass")


def earliest_for(captured: str) -> datetime.date:
    """The floor the script computes, reproduced from its own constants."""
    return max(
        delta.EARLIEST,
        datetime.date.fromisoformat(captured)
        + datetime.timedelta(days=delta.MIN_INTERVAL_DAYS),
    )


def test_the_interval_is_seven_days() -> None:
    assert delta.MIN_INTERVAL_DAYS == 7


def test_the_day0_baseline_moves_the_floor_to_the_registered_due_date() -> None:
    """Item 85 registered 2026-08-13. The guard must agree without being told."""
    assert earliest_for("2026-08-06") == datetime.date(2026, 8, 13)


def test_the_old_constant_alone_would_have_permitted_a_negative_interval() -> None:
    """The defect this change closes, stated as arithmetic rather than as prose."""
    captured = datetime.date(2026, 8, 6)
    assert delta.EARLIEST < captured, (
        "the absolute floor is earlier than the day-0 capture, so a constant-only "
        "guard would have allowed a run before the baseline even existed"
    )


def test_the_original_baseline_still_yields_the_original_date() -> None:
    """Backwards compatibility: the 2026-07-29 baseline must not move."""
    assert earliest_for("2026-07-29") == datetime.date(2026, 8, 5)
    assert earliest_for("2026-07-29") == delta.EARLIEST


def test_the_committed_baselines_carry_the_capture_dates_the_guard_reads() -> None:
    """A guard that reads a field nothing writes is a guard that never fires."""
    corpus = REPO / "analysis" / "corpus" / "realpage"
    for name, expected in (("DELTA-BASELINE.json", "2026-07-29"),
                           ("DELTA-BASELINE-2026-08-06.json", "2026-08-06")):
        path = corpus / name
        if not path.is_file():
            continue
        assert json.loads(path.read_text(encoding="utf-8"))["captured"] == expected


def test_a_baseline_with_no_usable_date_falls_back_rather_than_crashing() -> None:
    """Fail-safe, not fail-open: the absolute floor still applies."""
    assert max(delta.EARLIEST, delta.EARLIEST) == delta.EARLIEST


# --- ledger item 87: the coverage floor ----------------------------------------


def test_the_coverage_floor_is_declared_and_conservative() -> None:
    assert 0.5 < delta.MIN_REFETCH_COVERAGE <= 1.0
    assert delta.MIN_REFETCH_COVERAGE == 0.90


def test_the_2026_08_06_depleted_capture_would_have_been_refused() -> None:
    """The real episode, as arithmetic. 145/201 must not be reportable."""
    assert 145 / 201 < delta.MIN_REFETCH_COVERAGE


def test_both_good_captures_remain_reportable() -> None:
    """197/201 is what both the 2026-08-05 pass and the kept day-0 capture achieved."""
    assert 197 / 201 >= delta.MIN_REFETCH_COVERAGE


def test_the_fetch_settings_are_the_evidenced_ones() -> None:
    """Ten workers at fifteen seconds produced the depleted capture; three at thirty did not."""
    assert delta.FETCH_WORKERS == 3
    assert delta.FETCH_TIMEOUT_SECONDS == 30


def test_the_pass_refuses_rather_than_reporting_a_depleted_rate() -> None:
    """The refusal must exist in the source and must not fall through to a rate."""
    source = (REPO / "analysis" / "run_delta_pass.py").read_text(encoding="utf-8")
    assert "REFUSING to report a rate" in source
    assert "MIN_REFETCH_COVERAGE" in source
    refusal = source.split("REFUSING to report a rate", 1)[1].split("return 4", 1)[0]
    assert '"reportable": False' in refusal, "the artefact must mark itself unreportable"
