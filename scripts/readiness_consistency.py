"""Validate SkillWatch's structured current readiness state and scoreboard."""

from __future__ import annotations

import json
import math
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, cast

ROOT = Path(__file__).resolve().parents[1]
STATUS_PATH = ROOT / "docs" / "readiness-status.json"
SHIP_PATH = ROOT / "SHIP-READINESS.md"
LEDGER_PATH = ROOT / "OPEN-ITEMS.md"
CURRENT_OPEN = "<!-- readiness:current -->"
CURRENT_CLOSE = "<!-- readiness:end -->"
VALID_STATUSES = {"pass", "fail", "not_demonstrated", "pending"}
METRIC_DIRECTIONS = {"benign_false_positive_rate": "lower_is_better"}


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
    conditions = {int(item["id"]): item for item in status["conditions"]}
    if set(conditions) != {1, 2, 3, 4, 5}:
        raise AssertionError("readiness status must define conditions 1 through 5 exactly once")
    return conditions


def validate_status(status: dict[str, Any], metrics: dict[str, tuple[int, int]]) -> list[str]:
    errors: list[str] = []
    conditions = condition_map(status)
    nonpassing = [number for number, item in conditions.items() if item["status"] != "pass"]
    for number, item in conditions.items():
        if item["status"] not in VALID_STATUSES:
            errors.append(f"condition {number} has invalid status {item['status']}")
    if not nonpassing and status["verdict"] != "GO":
        errors.append("all conditions pass but verdict is not GO")
    if nonpassing and status["verdict"] == "GO":
        errors.append(f"verdict GO contradicts non-passing conditions {nonpassing}")
    if status.get("only_remaining_gate") and len(nonpassing) != 1:
        errors.append("only_remaining_gate requires exactly one non-passing condition")
    if status["commercial_constraint"] == status["readiness_gate"]:
        errors.append("commercial constraint and readiness gate must be distinct concepts")

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
    fp_k, fp_n = metrics["benign_false_positive_rate"]
    low, high = wilson_interval(fp_k, fp_n)
    lines.extend(
        [
            "",
            f"**Verdict: {status['verdict']}.** Condition 2 is not demonstrated; condition 5 fails.",
            f"Condition 2 evidence: {fp_k}/{fp_n} ({fp_k / fp_n:.1%}), 95% Wilson interval "
            f"[{low:.1%}, {high:.1%}]. This lower-is-better gate uses the upper bound.",
            "Zero users is the binding commercial constraint, distinct from the unresolved condition 2 evidence gate.",
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
    for row in re.findall(r"^\| \d+ \|.*$", open_text, re.MULTILINE):
        status = row.split("|")[4].strip()
        if not re.match(r"^\*\*(?:Open|Partial|Partly)", status, re.I):
            errors.append(f"non-open status under Open: {row[:80]}")
    for row in re.findall(r"^\| \d+ \|.*$", closed_text, re.MULTILINE):
        status = row.split("|")[4]
        if re.match(r"^\*\*(?:Open|Partial|Partly)", status, re.I):
            errors.append(f"open/partial row under Closed: {row[:80]}")
    return errors


def main() -> int:
    status = load_status()
    metrics = harness_metrics()
    errors = validate_status(status, metrics)
    ship = SHIP_PATH.read_text(encoding="utf-8")
    if current_block(ship) != render_current(status, metrics):
        errors.append("SHIP-READINESS current block differs from generated readiness status")
    errors.extend(ledger_section_errors(LEDGER_PATH.read_text(encoding="utf-8")))
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print("Readiness status, generated scoreboard, harness metrics, and ledger sections agree.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
