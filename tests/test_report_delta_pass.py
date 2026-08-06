"""The organic real-page result must reach published surfaces without hand-copying.

Three pieces of plumbing were added on 2026-08-05, when `run_delta_pass.py` finally
ran and returned 18/38 (47.4%). Each is tested here for the property that makes it
worth having rather than merely for executing:

* `analysis/report_delta_pass.py` prints the artefact's proportions and FAILS CLOSED
  when it cannot read the artefact. A reporter that printed nothing on a missing file
  would silently shrink the figure gate's allowed set, which is the "check that passes
  because its subject is out of scope" shape this repository has logged four times.
* `figure_rules.classify_metric` separates the organic rate from the synthetic one.
  Without the split both are `false-positive-rate` and therefore interchangeable, so
  the flattering synthetic 16.2% could be published under a real-page label and every
  rule would pass. The negative control for this is recorded in the gate table.
* `readiness_consistency.organic_errors` derives the organic status from the artefact
  and the Wilson arithmetic instead of trusting the declaration, and distinguishes a
  REFUTED gate from an UNDEMONSTRATED one. Condition 2's own validator cannot: it
  returns only `pass` or `not_demonstrated`, so it has no way to say "decided, and
  against us", which is exactly what 18/38 means.
"""

from __future__ import annotations

import importlib.util
import json

from pathlib import Path
from typing import Any

import pytest

REPO = Path(__file__).resolve().parents[1]


def _load(name: str, relative: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, REPO / relative)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


report_delta_pass = _load("report_delta_pass", "analysis/report_delta_pass.py")
figure_rules = _load("figure_rules", "scripts/figure_rules.py")
readiness_consistency = _load("readiness_consistency", "scripts/readiness_consistency.py")


ARTEFACT: dict[str, Any] = {
    "ran": "2026-08-05",
    "baseline_captured": "2026-07-29",
    "urls": 201,
    "refetched_ok": 197,
    "gate_open": 38,
    "flagged": 18,
    "by_code": {"suspicious_script": 11, "hidden_content": 3},
}


# --- the reporter ------------------------------------------------------------


def test_the_reporter_prints_the_overall_organic_rate_as_a_parseable_proportion() -> None:
    rendered = report_delta_pass.render(ARTEFACT)
    assert "Organic real-page false-positive rate (overall): 18/38 (47.4%)" in rendered


def test_every_proportion_the_reporter_prints_is_arithmetically_correct() -> None:
    """The figure gate checks arithmetic on surfaces; the harness must not seed it wrong."""
    rendered = report_delta_pass.render(ARTEFACT)
    found = list(figure_rules.PROPORTION_RE.finditer(rendered))
    assert found, "the reporter printed no parseable proportion"
    for match in found:
        k, n, pct = int(match.group(1)), int(match.group(2)), float(match.group(3))
        assert abs(pct - (k / n * 100)) <= figure_rules.PCT_TOLERANCE


def test_the_reporter_fails_closed_when_the_artefact_is_absent(tmp_path: Path) -> None:
    with pytest.raises(SystemExit) as excinfo:
        report_delta_pass.load(tmp_path / "nope.json")
    assert "has NOT passed" in str(excinfo.value)


def test_the_reporter_fails_closed_on_unreadable_or_incomplete_json(tmp_path: Path) -> None:
    broken = tmp_path / "DELTA-PASS.json"
    broken.write_text("{not json", encoding="utf-8")
    with pytest.raises(SystemExit):
        report_delta_pass.load(broken)

    partial = tmp_path / "partial.json"
    partial.write_text(json.dumps({"ran": "2026-08-05"}), encoding="utf-8")
    with pytest.raises(SystemExit) as excinfo:
        report_delta_pass.load(partial)
    assert "missing keys" in str(excinfo.value)


def test_a_rate_over_no_trials_prints_no_percentage() -> None:
    """A zero denominator must not become a fabricated 0.0%: it is not a rate."""
    empty = dict(ARTEFACT, gate_open=0, flagged=0, by_code={})
    rendered = report_delta_pass.render(empty)
    assert "0/0 (no trials)" in rendered
    assert "0/0 (0.0%)" not in rendered


def test_the_reporter_is_registered_as_a_harness_command() -> None:
    """Unregistering it would silently drop the organic figures from the allowed set."""
    commands = [Path(command[-1]).name for command in figure_rules.HARNESS_COMMANDS]
    assert "report_delta_pass.py" in commands
    assert "report_delta_pass.py" in figure_rules.MIN_PROPORTIONS_PER_COMMAND


# --- the metric family split -------------------------------------------------


@pytest.mark.parametrize(
    "label",
    [
        "Organic real-page false-positive rate (overall)",
        "organic false-positive rate",
        "real page false positive rate",
        "delta false-positive rate",
    ],
)
def test_organic_labels_are_a_different_family_from_the_synthetic_rate(label: str) -> None:
    assert figure_rules.classify_metric(label) == figure_rules.FAMILY_FP_ORGANIC


@pytest.mark.parametrize(
    "label",
    ["False-positive rate (overall)", "benign false positive rate", "FP rate"],
)
def test_plain_false_positive_labels_keep_the_original_family(label: str) -> None:
    assert figure_rules.classify_metric(label) == figure_rules.FAMILY_FP


def test_the_two_false_positive_families_are_not_equal() -> None:
    """If these ever collapse, 16.2% becomes publishable under a real-page label."""
    assert figure_rules.FAMILY_FP != figure_rules.FAMILY_FP_ORGANIC


# --- the organic readiness validator -----------------------------------------


def _status(**overrides: Any) -> dict[str, Any]:
    declared = {
        "metric": "organic_real_page_false_positive_rate",
        "direction": "lower_is_better",
        "successes": 18,
        "trials": 38,
        "threshold": 0.30,
        "status": "fail",
    }
    declared.update(overrides)
    return {"organic_delta_result": declared}


@pytest.fixture()
def artefact_on_disk(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    path = tmp_path / "DELTA-PASS.json"
    path.write_text(json.dumps(ARTEFACT), encoding="utf-8")
    monkeypatch.setattr(readiness_consistency, "DELTA_PASS_PATH", path)
    return path


def test_the_real_measurement_validates(artefact_on_disk: Path) -> None:
    assert readiness_consistency.organic_errors(_status()) == []


def test_a_declaration_that_disagrees_with_the_artefact_is_caught(
    artefact_on_disk: Path,
) -> None:
    errors = readiness_consistency.organic_errors(_status(successes=6, trials=37))
    assert errors and "artefact records" in errors[0]


def test_calling_a_refuted_gate_merely_undemonstrated_is_caught(
    artefact_on_disk: Path,
) -> None:
    """18/38's whole interval is above 30%. That is refuted, and must not read softer."""
    errors = readiness_consistency.organic_errors(_status(status="not_demonstrated"))
    assert errors and "expected fail" in errors[0]


def test_a_straddling_interval_is_not_demonstrated_rather_than_failed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The third outcome must survive: an interval crossing the gate decides nothing."""
    path = tmp_path / "DELTA-PASS.json"
    path.write_text(json.dumps(dict(ARTEFACT, flagged=6, gate_open=37)), encoding="utf-8")
    monkeypatch.setattr(readiness_consistency, "DELTA_PASS_PATH", path)
    low, high = readiness_consistency.wilson_interval(6, 37)
    assert low < 0.30 < high, "fixture no longer straddles the gate"
    assert readiness_consistency.organic_errors(
        _status(successes=6, trials=37, status="not_demonstrated")
    ) == []


def test_a_declared_result_with_no_artefact_is_caught(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(readiness_consistency, "DELTA_PASS_PATH", tmp_path / "absent.json")
    errors = readiness_consistency.organic_errors(_status())
    assert errors and "no result artefact exists" in errors[0]


def test_an_artefact_with_no_declared_result_is_caught(artefact_on_disk: Path) -> None:
    """Running the pass and not recording it is how a measurement gets quietly lost."""
    errors = readiness_consistency.organic_errors({})
    assert errors and "is not declared" in errors[0]


def test_the_committed_status_matches_the_committed_artefact() -> None:
    """No monkeypatching: the real files must agree with each other."""
    assert readiness_consistency.organic_errors(readiness_consistency.load_status()) == []
