"""Validate SkillWatch's structured current readiness state and scoreboard."""

from __future__ import annotations

import json
import math
import re
import subprocess
import sys
from datetime import date
from pathlib import Path
from typing import Any, cast

ROOT = Path(__file__).resolve().parents[1]
STATUS_PATH = ROOT / "docs" / "readiness-status.json"
SHIP_PATH = ROOT / "SHIP-READINESS.md"
LEDGER_PATH = ROOT / "OPEN-ITEMS.md"
HANDOVER_POINTER_PATH = ROOT / "docs" / "current-handover.txt"
CURRENT_OPEN = "<!-- readiness:current -->"
CURRENT_CLOSE = "<!-- readiness:end -->"
VALID_STATUSES = {"pass", "fail", "not_demonstrated", "pending"}
METRIC_DIRECTIONS = {"benign_false_positive_rate": "lower_is_better"}
VALID_VERDICTS = {"GO", "HOLD"}
EXPECTED_BASES = {
    1: "documentation_route",
    2: "wilson_bound",
    3: "named_owner_and_cadence",
    4: "independent_premise_source",
    5: "zero_users",
}
VALID_TOP_LEVEL = {
    "commercial_constraint": {"zero_users"},
    "readiness_gate": {"condition_2"},
    "organic_delta": {"pending", "complete"},
    "pilot_status": {"permissible_evidence_gathering", "not_permissible"},
    "general_commercial_readiness": {"not_demonstrated", "demonstrated"},
}


def wilson_interval(k: int, n: int) -> tuple[float, float]:
    """Return the 95% Wilson interval for k successes in n trials."""
    if n == 0:
        return (0.0, 1.0)
    z = 1.959963984540054
    point = k / n
    denominator = 1 + z**2 / n
    centre = (point + z**2 / (2 * n)) / denominator
    margin = z / denominator * math.sqrt(point * (1 - point) / n + z**2 / (4 * n**2))
    return max(0.0, centre - margin), min(1.0, centre + margin)


def load_status() -> dict[str, Any]:
    return cast(dict[str, Any], json.loads(STATUS_PATH.read_text(encoding="utf-8")))


def harness_metrics() -> dict[str, tuple[int, int]]:
    result = subprocess.run(
        [sys.executable, str(ROOT / "analysis" / "measure_efficacy.py")],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    original = result.stdout.split("DETECTION EFFICACY RESULTS — ORIGINAL CORPUS", 1)[1]
    original = original.split("PER-ITEM RESULTS", 1)[0]
    patterns = {
        "benign_false_positive_rate": r"False-positive rate \(overall\):\s+(\d+)/(\d+)",
        "overall_recall": r"Overall recall:\s+(\d+)/(\d+)",
        "evasive_recall": r"Evasive recall:\s+(\d+)/(\d+)",
    }
    metrics: dict[str, tuple[int, int]] = {}
    for name, pattern in patterns.items():
        match = re.search(pattern, original)
        if not match:
            raise AssertionError(f"harness did not emit {name}")
        metrics[name] = (int(match.group(1)), int(match.group(2)))
    return metrics


def condition_map(status: dict[str, Any]) -> dict[int, dict[str, Any]]:
    if len(status["conditions"]) != 5:
        raise AssertionError("readiness status must define exactly five conditions")
    conditions = {int(item["id"]): item for item in status["conditions"]}
    if set(conditions) != {1, 2, 3, 4, 5}:
        raise AssertionError("readiness status must define conditions 1 through 5 exactly once")
    return conditions


def current_measured_section(readme: str) -> str:
    """Return the uniquely headed current measurement section, or no evidence."""
    heading = "### Measured detection rates"
    parts = readme.split(heading)
    return parts[1].split("\n## ", 1)[0] if len(parts) == 2 else ""


def validate_status(status: dict[str, Any], metrics: dict[str, tuple[int, int]]) -> list[str]:
    errors: list[str] = []
    conditions = condition_map(status)
    nonpassing = [number for number, item in conditions.items() if item["status"] != "pass"]
    if status["verdict"] not in VALID_VERDICTS:
        errors.append(f"invalid verdict {status['verdict']}")
    try:
        evaluated_at = date.fromisoformat(str(status["evaluated_at"]))
    except ValueError:
        errors.append(f"invalid evaluated_at {status['evaluated_at']}")
    else:
        age = (date.today() - evaluated_at).days
        if age < 0 or age > 7:
            errors.append(f"evaluated_at is not current: age {age} days")
    for field, allowed in VALID_TOP_LEVEL.items():
        if status.get(field) not in allowed:
            errors.append(f"invalid {field} {status.get(field)}")
    for number, item in conditions.items():
        if item["status"] not in VALID_STATUSES:
            errors.append(f"condition {number} has invalid status {item['status']}")
        if item.get("basis") != EXPECTED_BASES[number]:
            errors.append(f"condition {number} has unvalidated basis {item.get('basis')}")
    if not nonpassing and status["verdict"] != "GO":
        errors.append("all conditions pass but verdict is not GO")
    if nonpassing and status["verdict"] == "GO":
        errors.append(f"verdict GO contradicts non-passing conditions {nonpassing}")
    if status.get("only_remaining_gate") and len(nonpassing) != 1:
        errors.append("only_remaining_gate requires exactly one non-passing condition")
    if status["commercial_constraint"] == status["readiness_gate"]:
        errors.append("commercial constraint and readiness gate must be distinct concepts")

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    maintenance = (ROOT / "MAINTENANCE.md").read_text(encoding="utf-8")
    launch_facts = (ROOT / "docs" / "LAUNCH-FACTS.md").read_text(encoding="utf-8")
    ledger = LEDGER_PATH.read_text(encoding="utf-8")
    measured_section = current_measured_section(readme)
    if (
        conditions[1]["status"] != "pass"
        or "**Treat the triage as decorative against semantic evasion.**" not in measured_section
    ):
        errors.append("condition 1 documentation-route evidence is absent or status is not pass")
    owner = re.search(r"^## Owner\s+\*\*[^*]+\*\* — sole contributor and maintainer\.$", maintenance, re.M)
    cadence = re.search(r"^### Quarterly pattern review\s+Every calendar quarter \([^)]+\), review", maintenance, re.M)
    if conditions[3]["status"] != "pass" or not owner or not cadence:
        errors.append("condition 3 owner/cadence evidence is absent or status is not pass")
    if (
        conditions[4]["status"] != "pass"
        or "https://arxiv.org/abs/2605.05274" not in conditions[4]["summary"]
        or "[arXiv 2605.05274, SIGIL](https://arxiv.org/abs/2605.05274)" not in launch_facts
        or "Preprint, not peer-reviewed" not in launch_facts
    ):
        errors.append("condition 4 primary-source evidence is absent or status is not pass")
    if conditions[5]["status"] != "fail" or not re.search(
        r"\| 9 \|.*(?:zero users|No users|No evidence of demand)", ledger, re.IGNORECASE
    ):
        errors.append("condition 5 zero-demand evidence is absent or status is not fail")
    if status["commercial_constraint"] == "zero_users" and conditions[5]["status"] != "fail":
        errors.append("zero_users commercial constraint requires condition 5 fail")
    if status["readiness_gate"] == "condition_2" and conditions[2]["status"] == "pass":
        errors.append("condition_2 readiness gate cannot point to a passing condition")
    all_pass = all(item["status"] == "pass" for item in conditions.values())
    commercially_ready = status["general_commercial_readiness"] == "demonstrated"
    if commercially_ready != (status["verdict"] == "GO" and all_pass):
        errors.append("commercial readiness requires and must agree with GO/all conditions pass")
    pilot_exists = (ROOT / "docs" / "DESIGN-PARTNER-PILOT.md").is_file()
    pilot_permissible = status["pilot_status"] == "permissible_evidence_gathering"
    if pilot_permissible != pilot_exists:
        errors.append("pilot status must agree with the evidence-gathering pilot document")
    delta_complete = (ROOT / "analysis" / "corpus" / "realpage" / "DELTA-PASS.json").is_file()
    if (status["organic_delta"] == "complete") != delta_complete:
        errors.append("organic delta status must agree with the registered result artefact")

    for number, item in conditions.items():
        if item.get("basis") != "wilson_bound":
            continue
        metric = str(item["metric"])
        observed = metrics.get(metric)
        claimed = (int(item["successes"]), int(item["trials"]))
        if observed != claimed:
            errors.append(f"condition {number} claims {claimed}, harness emits {observed}")
            continue
        low, high = wilson_interval(*claimed)
        threshold = float(item["threshold"])
        direction = item["direction"]
        expected_direction = METRIC_DIRECTIONS.get(metric)
        if direction != expected_direction:
            errors.append(
                f"condition {number} direction {direction} conflicts with "
                f"{metric} direction {expected_direction}"
            )
            continue
        demonstrated = low >= threshold if direction == "higher_is_better" else high <= threshold
        expected = "pass" if demonstrated else "not_demonstrated"
        if item["status"] != expected:
            bound = low if direction == "higher_is_better" else high
            errors.append(
                f"condition {number} status {item['status']} conflicts with {direction} "
                f"Wilson bound {bound:.3f} and threshold {threshold:.3f}"
            )
    return errors


def render_current(status: dict[str, Any], metrics: dict[str, tuple[int, int]]) -> str:
    conditions = condition_map(status)
    lines = [
        CURRENT_OPEN,
        "| # | Status | Current basis |",
        "|---:|---|---|",
    ]
    for number in range(1, 6):
        item = conditions[number]
        lines.append(f"| {number} | **{str(item['status']).upper()}** | {item['summary']} |")
    nonpassing = [item for item in conditions.values() if item["status"] != "pass"]
    clauses = [
        f"Condition {item['id']} {str(item['status']).replace('_', ' ')}"
        for item in nonpassing
    ]
    evidence_lines: list[str] = []
    for item in conditions.values():
        if item.get("basis") != "wilson_bound":
            continue
        k, n = metrics[str(item["metric"])]
        low, high = wilson_interval(k, n)
        bound_name = "lower" if item["direction"] == "higher_is_better" else "upper"
        evidence_lines.append(
            f"Condition {item['id']} evidence: {k}/{n} ({k / n:.1%}), 95% Wilson interval "
            f"[{low:.1%}, {high:.1%}]. This {str(item['direction']).replace('_', '-')} "
            f"gate uses the {bound_name} bound."
        )
    lines.extend(
        [
            "",
            f"**Verdict: {status['verdict']}.** " + "; ".join(clauses) + ".",
            *evidence_lines,
            f"{str(status['commercial_constraint']).replace('_', ' ').capitalize()} is the binding commercial constraint, distinct from the unresolved {str(status['readiness_gate']).replace('_', ' ')} evidence gate.",
            f"Organic delta evidence: {status['organic_delta']}. Private pilot: {status['pilot_status']}. "
            f"General commercial readiness: {status['general_commercial_readiness']}.",
            CURRENT_CLOSE,
        ]
    )
    return "\n".join(lines)


def current_block(text: str) -> str:
    start = text.index(CURRENT_OPEN)
    end = text.index(CURRENT_CLOSE, start) + len(CURRENT_CLOSE)
    return text[start:end]


def ledger_section_errors(text: str) -> list[str]:
    open_text = text.split("## Open", 1)[1].split("## Closed", 1)[0]
    closed_text = text.split("## Closed", 1)[1].split("## Standing decisions", 1)[0]
    errors: list[str] = []
    reviewed = re.search(r"^\*\*Last reviewed:\*\* (\d{4}-\d{2}-\d{2})", text, re.MULTILINE)
    recorded_dates: list[str] = []
    for row in re.findall(r"^\| \d+ \|.*$", open_text, re.MULTILINE):
        recorded_dates.extend(re.findall(r"\b\d{4}-\d{2}-\d{2}\b", row.split("|")[3]))
        status = row.split("|")[4].strip()
        if not re.match(r"^\*\*(?:Open|Partial|Partly)", status, re.I):
            errors.append(f"non-open status under Open: {row[:80]}")
    for row in re.findall(r"^\| \d+ \|.*$", closed_text, re.MULTILINE):
        columns = row.split("|")
        recorded_dates.extend(re.findall(r"\b\d{4}-\d{2}-\d{2}\b", columns[3]))
        recorded_dates.extend(re.findall(r"\b\d{4}-\d{2}-\d{2}\b", columns[4]))
        status = columns[4]
        if re.match(r"^\*\*(?:Open|Partial|Partly)", status, re.I):
            errors.append(f"open/partial row under Closed: {row[:80]}")
    if not reviewed:
        errors.append("ledger has no Last reviewed date")
    elif recorded_dates and reviewed.group(1) < max(recorded_dates):
        errors.append(
            f"ledger Last reviewed {reviewed.group(1)} predates item history {max(recorded_dates)}"
        )
    return errors


def handover_errors() -> list[str]:
    """Ensure one movable pointer identifies authority and every sibling opts out."""
    name = HANDOVER_POINTER_PATH.read_text(encoding="utf-8").strip()
    if not re.fullmatch(r"HANDOVER[A-Z0-9-]*\.md", name):
        return [f"invalid current handover pointer: {name}"]
    current = ROOT / "docs" / name
    errors: list[str] = []
    if not current.is_file():
        errors.append(f"current handover does not exist: {name}")
    else:
        current_opening = "\n".join(current.read_text(encoding="utf-8").splitlines()[:12])
        if "> **AUTHORITATIVE HANDOVER:**" not in current_opening:
            errors.append(f"current handover lacks authoritative marker: {name}")
        if "> **SUPERSEDED:**" in current_opening:
            errors.append(f"current handover disclaims authority: {name}")
    for handover in (ROOT / "docs").glob("HANDOVER*.md"):
        if handover == current:
            continue
        opening = "\n".join(handover.read_text(encoding="utf-8").splitlines()[:12])
        if "> **SUPERSEDED:**" not in opening or f"`{name}`" not in opening:
            errors.append(f"legacy handover does not explicitly defer to {name}: {handover.name}")
    return errors


def main() -> int:
    status = load_status()
    metrics = harness_metrics()
    errors = validate_status(status, metrics)
    ship = SHIP_PATH.read_text(encoding="utf-8")
    if current_block(ship) != render_current(status, metrics):
        errors.append("SHIP-READINESS current block differs from generated readiness status")
    errors.extend(ledger_section_errors(LEDGER_PATH.read_text(encoding="utf-8")))
    errors.extend(handover_errors())
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print("Readiness status, generated scoreboard, harness metrics, and ledger sections agree.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
