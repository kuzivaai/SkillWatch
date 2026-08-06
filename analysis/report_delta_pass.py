"""Print the organic delta pass result from its committed artefact, offline.

`run_delta_pass.py` measures the real-page false-positive rate by re-fetching 201
URLs. That is a network operation and cannot be a harness command: CI would
re-fetch the live web on every run, and the answer would change under it.

This module is the offline half. It reads the committed artefact
`corpus/realpage/DELTA-PASS.json` and prints the proportions it records, in the
`k/n (p%)` form `scripts/figure_rules.py` parses. That makes the organic figure a
first-class member of the allowed set, checked for currency and arithmetic on every
CI run, exactly as the synthetic efficacy figures are, rather than a number typed
onto a documentation surface by hand and free to drift from the artefact.

**It measures nothing.** It reports what the measurement recorded. The distinction
matters because the two failure modes differ: a measurement can be wrong about the
world, a report can only be wrong about the measurement.

**Fail-closed.** A missing or unreadable artefact exits non-zero rather than
printing an empty allowed set. `figure_rules.py` turns a non-zero harness command
into a hard failure, so an absent artefact cannot silently widen what the figure
gate will accept. That is the same shape as the dependency auditor treating an
unparseable specifier as satisfied: the defect this repository has logged four
times and does not intend to log a fifth.

**Why the labels say "organic real-page".** `classify_metric` in `figure_rules.py`
groups figures into metric families so a published figure must match the metric it
is *labelled* with. Both this rate and the synthetic benign false-positive rate
would otherwise classify as the same `false-positive-rate` family, which would make
them interchangeable to the correspondence check, and publishing the flattering
synthetic number under a real-page label is the single most consequential
substitution available on this project's surfaces. The labels below carry the
discriminating words that separate the families.
"""

import json
import sys

from pathlib import Path
from typing import Any

_HERE = Path(__file__).resolve().parent
ARTEFACT = _HERE / "corpus" / "realpage" / "DELTA-PASS.json"

# The three summary proportions are printed unconditionally whenever the artefact
# parses. The per-code rows are data: a flag that fired on no page prints no row,
# so they legitimately come and go and cannot be part of a floor.
STRUCTURAL_PROPORTIONS = 3


def load(path: Path = ARTEFACT) -> dict[str, Any]:
    if not path.is_file():
        raise SystemExit(
            f"FAIL: no delta pass artefact at {path}.\n"
            "This report has NOT passed: it could not inspect its subject. "
            "Run `python3 analysis/run_delta_pass.py` (2026-08-05 or later)."
        )
    try:
        data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"FAIL: delta pass artefact is not valid JSON: {exc}") from exc
    missing = [
        key for key in ("ran", "urls", "refetched_ok", "gate_open", "flagged", "by_code")
        if key not in data
    ]
    if missing:
        raise SystemExit(f"FAIL: delta pass artefact is missing keys: {missing}")
    return data


def _proportion(label: str, k: int, n: int) -> str:
    """Render one `label: k/n (p%)` line, or a bare label when n is zero.

    A zero denominator prints no percentage rather than a divide-by-zero or a
    fabricated 0.0%: a rate over no trials is not a rate.
    """
    if n == 0:
        return f"{label}: {k}/{n} (no trials)"
    return f"{label}: {k}/{n} ({k / n:.1%})"


def render(data: dict[str, Any]) -> str:
    gate_open = int(data["gate_open"])
    lines = [
        "=" * 70,
        "ORGANIC DELTA PASS: REAL-PAGE RESULT",
        "=" * 70,
        "",
        f"measured        {data['ran']}",
        f"baseline        {data.get('baseline_captured', 'unknown')}",
        "",
        "This is a REPORT of a stored measurement, not a measurement.",
        "",
        _proportion("Re-fetched successfully", int(data["refetched_ok"]), int(data["urls"])),
        _proportion("Text-change gate opened", gate_open, int(data["refetched_ok"])),
        "",
        _proportion(
            "Organic real-page false-positive rate (overall)",
            int(data["flagged"]),
            gate_open,
        ),
        "",
        "By flag code:",
    ]
    by_code: dict[str, int] = dict(data["by_code"])
    for code, count in sorted(by_code.items(), key=lambda kv: (-kv[1], kv[0])):
        lines.append(
            "  " + _proportion(
                f"Organic real-page false-positive rate, {code}", int(count), gate_open
            )
        )
    if not by_code:
        lines.append("  (no flag fired on any changed page)")
    return "\n".join(lines)


def main() -> int:
    data = load()
    print(render(data))
    return 0


if __name__ == "__main__":
    sys.exit(main())
