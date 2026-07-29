"""Tests for the shared claim rules (scripts/claim_rules.py).

These test the *rules engine*, not any particular document. The engine takes
arbitrary text and returns violations, which is what lets the same rules run
against three different things: repository files (tests/test_published_claims.py),
a freshly built sdist's PKG-INFO (scripts/check_release_claims.py), and the live
PyPI long description (scripts/check_published_claims.py).

Before this module existed the rules lived inside the pytest file and could only
ever see the repository. That is why the published artefact drifted from HEAD
without anything noticing.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RULES = REPO_ROOT / "scripts" / "claim_rules.py"


def _load():
    spec = importlib.util.spec_from_file_location("claim_rules", RULES)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["claim_rules"] = module
    spec.loader.exec_module(module)
    return module


rules = _load()


# The two distortions this project actually shipped, as they appeared.
STALE_TRAIL_OF_BITS = (
    "That document's incident timeline cites Trail of Bits for the finding that "
    "every public skill scanner tested was bypassed in under an hour. "
    "See https://blog.trailofbits.com/2026/06/03/the-sorry-state-of-skill-distribution/"
)
STALE_OWASP_MITIGATIONS = (
    "The mitigations that document lists against AST05 — source inventory, "
    "content pinning, repeated rescanning — describe what this tool does. "
    "See https://owasp.org/www-project-agentic-skills-top-10/"
)


class TestEntryPointExists:
    def test_find_violations_is_callable(self) -> None:
        assert callable(rules.find_violations)

    def test_returns_a_list(self) -> None:
        assert isinstance(rules.find_violations("nothing to see here"), list)


class TestCatchesTheShippedDistortions:
    def test_flags_the_compressed_trail_of_bits_claim(self) -> None:
        found = rules.find_violations(STALE_TRAIL_OF_BITS, source="fixture")
        assert found, "the compressed 'bypassed in under an hour' claim was not flagged"
        assert any("under an hour" in v.message or "hour" in v.excerpt.lower() for v in found)

    def test_flags_the_reworded_owasp_mitigation(self) -> None:
        found = rules.find_violations(STALE_OWASP_MITIGATIONS, source="fixture")
        assert found, "'repeated rescanning' rewording of OWASP's 'continuous' was not flagged"

    def test_flags_the_mitigations_overclaim(self) -> None:
        found = rules.find_violations(STALE_OWASP_MITIGATIONS, source="fixture")
        assert any("describe what this tool does" in v.message.lower() for v in found), (
            "the 'describe what this tool does' overclaim was not flagged"
        )

    def test_flags_an_unsourced_attribution(self) -> None:
        text = "Trail of Bits found that scanners are weak. No link here."
        found = rules.find_violations(text, source="fixture")
        assert any("blog.trailofbits.com" in v.message for v in found), (
            "naming Trail of Bits with no link to them was not flagged"
        )

    def test_flags_trail_of_bits_cited_without_the_quantifier(self) -> None:
        text = (
            "Trail of Bits bypassed several scanners. "
            "https://blog.trailofbits.com/2026/06/03/the-sorry-state-of-skill-distribution/"
        )
        found = rules.find_violations(text, source="fixture")
        assert any("three of the four" in v.message for v in found)


class TestCurrentReadmeIsClean:
    """The corrected README must produce no violations. This is the pass-after half."""

    def test_readme_has_no_violations(self) -> None:
        text = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        found = rules.find_violations(text, source="README.md")
        assert found == [], "corrected README produced violations:\n" + "\n".join(
            f"  {v.rule}: {v.message}" for v in found
        )


class TestUseVersusMention:
    """Quoting a bad claim in order to retract it must not itself be a violation."""

    def test_retraction_is_not_a_violation(self) -> None:
        text = (
            "An earlier version of this README said every scanner tested was bypassed "
            "in under an hour; that is corrected here. Trail of Bits actually wrote that "
            "it took under an hour to build three of the four attacks. "
            "https://blog.trailofbits.com/2026/06/03/the-sorry-state-of-skill-distribution/"
        )
        found = rules.find_violations(text, source="fixture")
        assert found == [], (
            "a marked retraction was flagged as an assertion:\n"
            + "\n".join(f"  {v.rule}: {v.message}" for v in found)
        )

    def test_blockquoted_source_text_is_not_a_violation(self) -> None:
        text = (
            "Trail of Bits wrote:\n\n"
            "> every public skill scanner tested was bypassed in under an hour\n\n"
            "which we quote to correct: the hour covers three of the four attacks.\n"
            "https://blog.trailofbits.com/2026/06/03/the-sorry-state-of-skill-distribution/"
        )
        found = rules.find_violations(text, source="fixture")
        assert found == []


class TestViolationShape:
    def test_violation_carries_rule_message_and_excerpt(self) -> None:
        found = rules.find_violations(STALE_TRAIL_OF_BITS, source="fixture")
        v = found[0]
        assert v.rule and isinstance(v.rule, str)
        assert v.message and isinstance(v.message, str)
        assert isinstance(v.excerpt, str)
        assert v.source == "fixture"
