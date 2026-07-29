"""Tests for the efficacy harness (analysis/measure_efficacy.py).

The harness produces every efficacy figure this project publishes. Until now it
had no tests at all, which meant the numbers in the README, on PyPI and in
SHIP-READINESS.md rested on code nothing guarded.

Scope is the reporting contract, not the detector. Three things matter:

1. Wilson intervals are arithmetically right, because published gates are
   evaluated on the lower bound.
2. Gates are decided on that lower bound and never on the point estimate.
3. *Every* corpus report carries an interval. A bare percentage is the exact
   failure mode the project corrected elsewhere: "100%" on n=6 reads as
   certainty when its lower bound is 61%.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "analysis" / "measure_efficacy.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("measure_efficacy", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["measure_efficacy"] = module
    spec.loader.exec_module(module)
    return module


efficacy = _load_module()


class TestWilsonInterval:
    """Guards the arithmetic behind every published figure."""

    @pytest.mark.parametrize(
        "k,n,low,high",
        [
            # The three headline figures, to the decimal place they are published at.
            (21, 25, 0.653, 0.936),  # precision
            (21, 35, 0.436, 0.744),  # overall recall
            (11, 25, 0.267, 0.629),  # evasive recall
            # Holdout, published alongside them.
            (9, 10, 0.596, 0.982),
            (9, 12, 0.468, 0.911),
            # A perfect proportion still carries uncertainty at small n. This is
            # the case the html corpus report used to print bare.
            (6, 6, 0.610, 1.000),
            # A zero proportion has an upper bound well above zero.
            (0, 38, 0.000, 0.092),
        ],
    )
    def test_matches_published_intervals(self, k, n, low, high):
        got_low, got_high = efficacy.wilson_interval(k, n)
        assert got_low == pytest.approx(low, abs=0.001)
        assert got_high == pytest.approx(high, abs=0.001)

    def test_no_data_is_not_certainty(self):
        assert efficacy.wilson_interval(0, 0) == (0.0, 1.0)

    def test_interval_stays_inside_unit_range(self):
        for k, n in [(0, 3), (3, 3), (1, 2)]:
            low, high = efficacy.wilson_interval(k, n)
            assert 0.0 <= low <= high <= 1.0


class TestGateVerdict:
    """A gate is met when the data demonstrates it, not when the point clears it."""

    def test_point_clears_but_lower_bound_does_not(self):
        verdict = efficacy.gate_verdict(5, 10, 0.50)
        assert verdict.startswith("NOT DEMONSTRATED")

    def test_demonstrated_requires_lower_bound(self):
        verdict = efficacy.gate_verdict(100, 100, 0.75)
        assert verdict.startswith("DEMONSTRATED")

    def test_no_data_is_not_demonstrated(self):
        assert efficacy.gate_verdict(0, 0, 0.5).startswith("NOT DEMONSTRATED")


class TestEveryCorpusReportCarriesIntervals:
    """No corpus may publish a bare percentage.

    The html corpus report printed `Precision: 100.0%` with no interval while the
    other two reports carried Wilson bounds. Same convention, three reports.
    """

    def _html_items(self):
        """Minimal items in the real corpus shape (see analysis/corpus/html_v1)."""
        return [
            {
                "id": f"T-MAL-{i}",
                "label": "malicious",
                "subset": "html_malicious",
                "old": "Overview page.",
                "new": "Overview page.\nEmbedded content below.",
                "old_html": "<html><body><p>Overview page.</p></body></html>",
                "new_html": (
                    "<html><body><p>Overview page.</p>"
                    "<iframe src='https://evil.example/x'></iframe></body></html>"
                ),
            }
            for i in range(3)
        ] + [
            {
                "id": f"T-BEN-{i}",
                "label": "benign",
                "subset": "html_benign",
                "old": "Overview page.",
                "new": "Overview page. Now with a second sentence.",
                "old_html": "<html><body><p>Overview page.</p></body></html>",
                "new_html": (
                    "<html><body><p>Overview page. Now with a second sentence.</p></body></html>"
                ),
            }
            for i in range(3)
        ]

    def test_html_report_prints_confidence_intervals(self, capsys):
        efficacy._print_html_report(self._html_items())
        out = capsys.readouterr().out
        assert "95% CI" in out, "html corpus report published a point estimate with no interval"
        # Both headline proportions, not just one of them.
        assert out.count("95% CI") >= 2

    def test_html_report_returns_intervals_for_downstream_use(self):
        result = efficacy._print_html_report(self._html_items())
        assert "precision_ci" in result
        assert "recall_ci" in result
        low, high = result["precision_ci"]
        assert 0.0 <= low <= high <= 1.0
