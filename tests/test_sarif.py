"""Tests for SARIF 2.1.0 output."""

from skillwatch.detector import explain
from skillwatch.sarif import build_sarif


def test_empty_sarif_is_well_formed():
    doc = build_sarif([])
    assert doc["version"] == "2.1.0"
    assert doc["$schema"].endswith("sarif-2.1.0.json")
    driver = doc["runs"][0]["tool"]["driver"]
    assert driver["name"] == "SkillWatch"
    assert doc["runs"][0]["results"] == []


def test_sarif_maps_flags_to_results_and_levels():
    changed = [
        {
            "url": "https://docs.example.com/setup",
            "severity": "critical",
            "flags": [
                {"code": "new_exec_command", "severity": "critical"},
                {"code": "hidden_content", "severity": "info"},
            ],
        }
    ]
    doc = build_sarif(changed)
    run = doc["runs"][0]
    results = run["results"]
    assert len(results) == 2

    levels = {r["ruleId"]: r["level"] for r in results}
    assert levels["new_exec_command"] == "error"   # critical -> error
    assert levels["hidden_content"] == "note"       # info -> note

    # Location is the monitored URL
    loc = results[0]["locations"][0]["physicalLocation"]["artifactLocation"]["uri"]
    assert loc == "https://docs.example.com/setup"

    # Rules registered once per code, with plain-language descriptions
    rule_ids = {r["id"] for r in run["tool"]["driver"]["rules"]}
    assert rule_ids == {"new_exec_command", "hidden_content"}
    assert explain("new_exec_command") in results[0]["message"]["text"]
