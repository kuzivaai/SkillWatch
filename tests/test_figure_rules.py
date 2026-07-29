"""A published proportion must be one the harness currently produces.

Why this exists
---------------
On 2026-07-29 the concealment check was rewritten, the efficacy harness was re-run,
and the new figures were propagated to none of the six surfaces that publish them.
README, `docs/llms.txt`, `docs/index.html`, `docs/LAUNCH-FACTS.md`, `PATTERNS.md`
and `CHANGELOG.md` went on advertising a benign false-positive rate of 4/32 (12.5%)
while the harness produced 7/37 (18.9%). `SHIP-READINESS.md` contradicted itself
inside one file. Nothing caught any of it, because `scripts/claim_rules.py` checks
**citations** on public surfaces and is blind to **figures** on the same surfaces.

That is the fourth recurrence of one shape in this repository:

  1. `specifier_allows` treated an unparseable specifier as satisfied  (item 17)
  2. the claims guard could not see the published artefact               (item 35)
  3. `MITIGATION_OVERCLAIM_RE` could never match                         (item 36)
  4. the claims guard cannot see figures                                 (item 42)

Each is *a check that reports green because what it should examine is out of its
scope*. This module closes the fourth as the class rather than fixing the six
surfaces and moving on.

The fixture that matters
------------------------
`test_the_real_drift_is_caught` reproduces the actual defect: a surface asserting
12.5% while the harness produces 16.2%. It was written before the implementation
and failed against its absence.
"""
from __future__ import annotations

import importlib.util
import sys

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
MODULE = REPO_ROOT / "scripts" / "figure_rules.py"


def _load():
    spec = importlib.util.spec_from_file_location("figure_rules", MODULE)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["figure_rules"] = module
    spec.loader.exec_module(module)
    return module


figure_rules = _load()


# The harness is run once per session, not once per test — it executes the
# detector over three corpora and costs seconds, not milliseconds.
@pytest.fixture(scope="module")
def allowed():
    return figure_rules.harness_proportions()


class TestTheHarnessIsActuallyReachable:
    """Guarding the guard. An empty allowed-set would make everything pass."""

    def test_harness_yields_proportions(self, allowed):
        assert len(allowed.pairs) >= 20, (
            f"only {len(allowed.pairs)} proportions parsed out of the harness "
            f"output — if its format changed, this check is inspecting nothing "
            f"and would pass against any surface. Fail closed instead."
        )

    def test_harness_includes_the_headline_figures(self, allowed):
        # If these ever stop appearing, the parser has silently stopped working.
        for pair in [(6, 37), (27, 33), (27, 42), (17, 32)]:
            assert pair in allowed.pairs, f"{pair} missing from harness output"

    def test_harness_includes_base_rate_figures(self, allowed):
        # Answering explicitly: yes, the base-rate figures are covered too.
        for pair in [(111, 201), (103, 201), (141, 201)]:
            assert pair in allowed.pairs, f"base-rate {pair} missing"

    def test_a_stale_pair_is_not_in_the_allowed_set(self, allowed):
        # The pre-rewrite rate. If this were present the check could not fire.
        assert (4, 32) not in allowed.pairs


class TestExtraction:
    def test_extracts_k_n_and_percentage(self):
        found = figure_rules.extract_proportions("rate is 6/37 (16.2%, 95% CI [7.7%, 31.1%])")
        assert len(found) == 1
        assert (found[0].k, found[0].n) == (6, 37)
        assert found[0].pct == pytest.approx(16.2)

    def test_extracts_several_from_one_line(self):
        found = figure_rules.extract_proportions("15/20 (75.0%) then 21/35 (60.0%)")
        assert [(p.k, p.n) for p in found] == [(15, 20), (21, 35)]

    def test_ignores_bare_fractions_without_a_percentage(self):
        # "10/10" in a comparison column carries no percentage and no claim.
        assert figure_rules.extract_proportions("| Non-evasive | 10/10 | 10/10 |") == []

    def test_records_the_line_number(self):
        found = figure_rules.extract_proportions("first\nsecond 6/37 (16.2%)")
        assert found[0].line == 2


class TestArithmetic:
    def test_percentage_inconsistent_with_the_fraction_is_flagged(self, allowed):
        # Catches transcription errors independently of currency.
        text = "benign false positives 6/37 (61.2%)"
        violations = figure_rules.find_figure_violations(text, allowed=allowed)
        assert any(v.rule == "figure-arithmetic" for v in violations)

    def test_consistent_percentage_passes_arithmetic(self, allowed):
        text = "benign false positives 6/37 (16.2%)"
        assert not [v for v in figure_rules.find_figure_violations(text, allowed=allowed)
                    if v.rule == "figure-arithmetic"]

    def test_rounding_at_one_decimal_is_tolerated(self, allowed):
        # 27/42 = 64.2857...; both 64.3 and 64.29 are honest renderings.
        for rendering in ["27/42 (64.3%)", "27/42 (64.29%)"]:
            assert not [v for v in figure_rules.find_figure_violations(rendering, allowed=allowed)
                        if v.rule == "figure-arithmetic"]


class TestCurrency:
    def test_the_real_drift_is_caught(self, allowed):
        """THE fixture. The defect this repository actually shipped.

        A surface asserting a 12.5% benign false-positive rate while the harness
        produces 16.2%. Written before the implementation existed.
        """
        text = (
            "The transferable number is the **false-positive rate: 4/32 (12.5%, "
            "95% CI [5.0%, 28.1%])** on the original benign corpus."
        )
        violations = figure_rules.find_figure_violations(text, source="README.md", allowed=allowed)
        assert any(v.rule == "figure-not-current" for v in violations), (
            "a surface claiming 4/32 (12.5%) while the harness produces 6/37 "
            "(16.2%) must be flagged — this is the exact drift of 2026-07-29"
        )

    def test_a_current_figure_passes(self, allowed):
        text = "benign false-positive rate: 6/37 (16.2%, 95% CI [7.7%, 31.1%])"
        assert figure_rules.find_figure_violations(text, allowed=allowed) == []

    def test_several_stale_figures_are_each_reported(self, allowed):
        text = "recall 21/35 (60.0%) and evasive 11/25 (44.0%) and FP 4/32 (12.5%)"
        violations = [v for v in figure_rules.find_figure_violations(text, allowed=allowed)
                      if v.rule == "figure-not-current"]
        assert len(violations) == 3


class TestHistoricalExemption:
    """Release-to-release tables legitimately carry superseded figures.

    A check that fails on those is a check someone disables. The mechanism is an
    explicit marked region carrying a stated reason.
    """

    def test_figures_inside_an_exempt_region_are_allowed(self, allowed):
        text = (
            "<!-- figures:exempt reason=\"0.3.0 to 0.4.1 release comparison\" -->\n"
            "| Overall recall | 15/20 (75.0%) | 21/35 (60.0%) |\n"
            "<!-- figures:end -->\n"
        )
        assert figure_rules.find_figure_violations(text, allowed=allowed) == []

    def test_figures_after_the_region_closes_are_checked_again(self, allowed):
        text = (
            "<!-- figures:exempt reason=\"history\" -->\n"
            "21/35 (60.0%)\n"
            "<!-- figures:end -->\n"
            "current rate is 4/32 (12.5%)\n"
        )
        violations = [v for v in figure_rules.find_figure_violations(text, allowed=allowed)
                      if v.rule == "figure-not-current"]
        assert len(violations) == 1
        assert violations[0].excerpt.startswith("4/32")

    def test_an_exempt_region_without_a_reason_is_a_violation(self, allowed):
        # Forces the author to say why, and lets a later session audit the reasons.
        text = "<!-- figures:exempt -->\n21/35 (60.0%)\n<!-- figures:end -->\n"
        violations = figure_rules.find_figure_violations(text, allowed=allowed)
        assert any(v.rule == "figure-exempt-no-reason" for v in violations)

    def test_an_unclosed_exempt_region_is_a_violation(self, allowed):
        # FAIL CLOSED. An unclosed marker would silently exempt the rest of the
        # file — the very shape this module exists to close.
        text = "<!-- figures:exempt reason=\"history\" -->\n21/35 (60.0%)\n"
        violations = figure_rules.find_figure_violations(text, allowed=allowed)
        assert any(v.rule == "figure-exempt-unclosed" for v in violations)

    def test_an_unclosed_region_does_not_swallow_later_drift(self, allowed):
        text = (
            "<!-- figures:exempt reason=\"history\" -->\n"
            "21/35 (60.0%)\n"
            "much later, a current claim: 4/32 (12.5%)\n"
        )
        rules_hit = {v.rule for v in figure_rules.find_figure_violations(text, allowed=allowed)}
        assert "figure-exempt-unclosed" in rules_hit

    def test_a_stray_end_marker_is_a_violation(self, allowed):
        text = "21/35 (60.0%)\n<!-- figures:end -->\n"
        violations = figure_rules.find_figure_violations(text, allowed=allowed)
        assert any(v.rule == "figure-exempt-stray-end" for v in violations)


class TestTheRealSurfaces:
    """The published surfaces must be clean under this check."""

    @pytest.mark.parametrize("rel", figure_rules.FIGURE_SURFACES)
    def test_surface_carries_no_drifted_figure(self, rel, allowed):
        path = REPO_ROOT / rel
        assert path.exists(), f"{rel} is a declared surface and must exist"
        violations = figure_rules.find_figure_violations(
            path.read_text(encoding="utf-8"), source=rel, allowed=allowed
        )
        assert not violations, "\n".join(
            f"  [{v.rule}] {v.message}\n      {v.excerpt}" for v in violations
        )
