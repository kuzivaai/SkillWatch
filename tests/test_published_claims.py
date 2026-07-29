"""Guards on claims this project makes about other people's work, in-repository.

The rules themselves live in `scripts/claim_rules.py` and are shared with two
release-time checks. This file applies them to the repository's own files.

Why the split matters. These tests read repository paths and nothing else. On
2026-07-29 that was enough to report green while the live PyPI long description
still served both distortions the repository had just corrected — the guard could
not see the most public surface this project has. `scripts/check_release_claims.py`
(a gate) and `scripts/check_published_claims.py` (a report) close that, using the
same rules module so the three checks cannot drift apart.

A test cannot check whether a paraphrase is faithful; that needs a human with the
source open. What it can check is the mechanical precondition for anyone ever
noticing: that a cited finding carries a link to where it came from.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent


def _load_rules():
    spec = importlib.util.spec_from_file_location(
        "claim_rules", REPO_ROOT / "scripts" / "claim_rules.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["claim_rules"] = module
    spec.loader.exec_module(module)
    return module


rules = _load_rules()

# Surfaces a user or an indexer actually reads, inside this repository.
# NOTE: this list is necessarily incomplete — the PyPI long description is not a
# file here. That gap is covered by scripts/check_release_claims.py, not by
# widening this list.
PUBLIC_SURFACES = [
    "README.md",
    "docs/llms.txt",
    "docs/index.html",
    "SHIP-READINESS.md",
]


def _read(rel: str) -> str:
    """Read a public surface, failing loudly if it is missing.

    Deliberately not `pytest.skip`. A first draft skipped when the file was
    absent, which meant deleting README.md would turn every guard in this file
    green — the same fail-open shape as a check whose subject is out of scope.
    """
    path = REPO_ROOT / rel
    assert path.exists(), (
        f"{rel} is missing. It is a tracked public surface these guards depend on; "
        f"its absence is a failure, not a reason to skip."
    )
    return path.read_text(encoding="utf-8")


class TestEveryPublicSurfaceIsClean:
    """No repository surface may carry a claim violation."""

    @pytest.mark.parametrize("rel", PUBLIC_SURFACES)
    def test_surface_has_no_violations(self, rel: str) -> None:
        found = rules.find_violations(_read(rel), source=rel)
        assert found == [], "\n" + rules.format_violations(found)


class TestTheRulesCanActuallyFire:
    """A rule that has never fired has not been tested.

    One of the negative rules shipped vacuous: its span was too short to match
    the text it was written to catch, so it passed against the pre-correction
    README and was not among the failures when that file was used as a
    fail-before fixture. These assert each rule fires on text that breaches it.
    """

    def test_compressed_quantifier_rule_fires(self) -> None:
        text = "Every public skill scanner tested was bypassed in under an hour."
        assert any(v.rule == "tob-compressed-quantifier" for v in rules.find_violations(text))

    def test_mitigation_overclaim_rule_fires(self) -> None:
        text = (
            "The mitigations that document lists against AST05 — source inventory,\n"
            "content pinning, repeated rescanning — describe what this tool\ndoes."
        )
        assert any(v.rule == "ast05-mitigation-overclaim" for v in rules.find_violations(text))

    def test_reworded_continuous_rule_fires(self) -> None:
        text = "The mitigations it lists are source inventory and repeated rescanning."
        assert any(v.rule == "owasp-continuous-reworded" for v in rules.find_violations(text))

    def test_unsourced_attribution_rule_fires(self) -> None:
        assert any(
            v.rule == "unsourced-attribution"
            for v in rules.find_violations("SIGIL says the audit-runtime gap is real.")
        )
