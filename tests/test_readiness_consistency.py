"""Current readiness claims must agree with evidence and ledger structure."""

from __future__ import annotations

import json
import importlib.util
import re
from datetime import date, timedelta
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SHIP = REPO / "SHIP-READINESS.md"
LEDGER = REPO / "OPEN-ITEMS.md"
EVASIVE = REPO / "analysis" / "corpus" / "adversarial_b"
SPEC = importlib.util.spec_from_file_location(
    "readiness_consistency", REPO / "scripts" / "readiness_consistency.py"
)
assert SPEC and SPEC.loader
readiness_consistency = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(readiness_consistency)


def _condition_rows(text: str) -> dict[int, str]:
    rows: dict[int, str] = {}
    for match in re.finditer(r"^\| ([1-5]) \|.*$", text, re.MULTILINE):
        rows[int(match.group(1))] = match.group(0)
    return rows


def _section(text: str, heading: str, next_heading: str | None = None) -> str:
    start = text.index(heading)
    end = text.find(next_heading, start + len(heading)) if next_heading else -1
    return text[start:] if end == -1 else text[start:end]


def test_nonpassing_condition_cannot_coexist_with_all_one_to_four_pass() -> None:
    text = SHIP.read_text(encoding="utf-8")
    rows = _condition_rows(text)
    assert re.search(r"NOT[_ ]DEMONSTRATED", rows[2])
    verdict = _section(text, "**Verdict:", "## Condition 1")
    assert not re.search(r"conditions?\s+1[–-]4\s+pass", verdict, re.IGNORECASE)


def test_confidence_bound_rule_is_directional() -> None:
    text = SHIP.read_text(encoding="utf-8")
    evaluation = _section(text, "## Evaluation rule", "## Current scoreboard")
    assert re.search(r"higher-is-better.{0,100}lower bound", evaluation, re.I | re.S)
    assert re.search(r"lower-is-better.{0,100}upper bound", evaluation, re.I | re.S)
    assert not re.search(r"all gates.{0,80}lower bound", evaluation, re.I | re.S)


def test_retracted_original_ten_claim_is_not_current() -> None:
    text = SHIP.read_text(encoding="utf-8")
    current = readiness_consistency.current_block(text)
    assert "same five are caught" not in current.lower()


def test_current_evasive_corpus_total_and_families_are_authoritative() -> None:
    items = [json.loads(path.read_text(encoding="utf-8")) for path in EVASIVE.glob("*.json")]
    family_counts: dict[str, int] = {}
    for item in items:
        family = str(item["family"])
        family_counts[family] = family_counts.get(family, 0) + 1
    assert len(items) == 32
    assert family_counts == {
        "semantic": 13,
        "structural": 10,
        "mechanical": 7,
        "language": 2,
    }
    current = readiness_consistency.current_block(SHIP.read_text(encoding="utf-8"))
    assert "25 evasive items" not in current
    assert "Semantic / framing (no obfuscation, no trigger words) | 13 | 2" not in current


def test_ledger_sections_agree_with_row_statuses() -> None:
    text = LEDGER.read_text(encoding="utf-8")
    open_section = _section(text, "## Open", "## Closed")
    closed_section = _section(text, "## Closed", "## Standing decisions")
    open_statuses = [row.split("|")[4].strip() for row in re.findall(r"^\| \d+ \|.*$", open_section, re.M)]
    closed_statuses = [row.split("|")[4].strip() for row in re.findall(r"^\| \d+ \|.*$", closed_section, re.M)]
    assert all(re.match(r"^\*\*(?:Open|Partial|Partly)", status, re.I) for status in open_statuses)
    assert not any(re.match(r"^\*\*(?:Open|Partial|Partly)", status, re.I) for status in closed_statuses)


def test_structured_status_matches_harness_and_current_scoreboard() -> None:
    status = readiness_consistency.load_status()
    metrics = readiness_consistency.harness_metrics()
    assert readiness_consistency.validate_status(status, metrics) == []
    ship = SHIP.read_text(encoding="utf-8")
    assert readiness_consistency.current_block(ship) == readiness_consistency.render_current(status, metrics)


def test_duplicate_condition_ids_are_rejected() -> None:
    status = readiness_consistency.load_status()
    status["conditions"][1]["id"] = 1
    try:
        readiness_consistency.condition_map(status)
    except AssertionError:
        pass
    else:
        raise AssertionError("duplicate condition IDs were accepted")


def test_verdict_and_non_wilson_evidence_are_validated() -> None:
    status = readiness_consistency.load_status()
    metrics = readiness_consistency.harness_metrics()
    status["verdict"] = "MAYBE"
    assert "invalid verdict MAYBE" in readiness_consistency.validate_status(status, metrics)

    status = readiness_consistency.load_status()
    status["conditions"][4]["status"] = "pending"
    errors = readiness_consistency.validate_status(status, metrics)
    assert "condition 5 zero-demand evidence is absent or status is not fail" in errors

    status = readiness_consistency.load_status()
    status["conditions"][0]["basis"] = "unchecked_new_basis"
    errors = readiness_consistency.validate_status(status, metrics)
    assert "condition 1 has unvalidated basis unchecked_new_basis" in errors


def test_current_metadata_fields_reject_arbitrary_or_stale_values() -> None:
    metrics = readiness_consistency.harness_metrics()
    for field in readiness_consistency.VALID_TOP_LEVEL:
        status = readiness_consistency.load_status()
        status[field] = "arbitrary"
        assert f"invalid {field} arbitrary" in readiness_consistency.validate_status(status, metrics)

    status = readiness_consistency.load_status()
    status["evaluated_at"] = (date.today() - timedelta(days=8)).isoformat()
    assert "evaluated_at is not current: age 8 days" in readiness_consistency.validate_status(
        status, metrics
    )

    status = readiness_consistency.load_status()
    status["general_commercial_readiness"] = "demonstrated"
    assert (
        "commercial readiness requires and must agree with GO/all conditions pass"
        in readiness_consistency.validate_status(status, metrics)
    )

    status = readiness_consistency.load_status()
    status["pilot_status"] = "not_permissible"
    assert (
        "pilot status must agree with the evidence-gathering pilot document"
        in readiness_consistency.validate_status(status, metrics)
    )

    status = readiness_consistency.load_status()
    status["organic_delta"] = "complete"
    assert (
        "organic delta status must agree with the registered result artefact"
        in readiness_consistency.validate_status(status, metrics)
    )


def test_condition_one_warning_requires_its_unique_current_heading() -> None:
    warning = "**Treat the triage as decorative against semantic evasion.**"
    current = f"preamble\n### Measured detection rates\n{warning}\n## Next\n"
    assert warning in readiness_consistency.current_measured_section(current)
    assert readiness_consistency.current_measured_section(f"historical: {warning}") == ""
    duplicate = current + f"### Measured detection rates\n{warning}\n"
    assert readiness_consistency.current_measured_section(duplicate) == ""


def test_legacy_handover_is_explicitly_superseded() -> None:
    assert readiness_consistency.handover_errors() == []


def test_ledger_review_date_cannot_predate_item_history() -> None:
    ledger = LEDGER.read_text(encoding="utf-8")
    assert readiness_consistency.ledger_section_errors(ledger) == []
    stale = re.sub(r"(\*\*Last reviewed:\*\* )\d{4}-\d{2}-\d{2}", r"\g<1>2026-07-31", ledger)
    errors = readiness_consistency.ledger_section_errors(stale)
    assert "ledger Last reviewed 2026-07-31 predates item history 2026-08-01" in errors
