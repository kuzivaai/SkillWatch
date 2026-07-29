"""A published proportion must be one the harness currently produces.

The class this closes
---------------------
`scripts/claim_rules.py` checks **citations** on public surfaces. It is blind to
**figures** on those same surfaces. On 2026-07-29 the concealment check was
rewritten and re-measured, and six surfaces went on publishing the pre-rewrite
numbers — a benign false-positive rate of 4/32 (12.5%) where the harness produced
7/37 (18.9%). `SHIP-READINESS.md` contradicted itself inside one file, and the
README told the reader to reproduce its table with a command that disproved it.

That is the fourth recurrence of one shape here: *a check that reports green
because what it should examine is out of its scope.* The others were an
unparseable specifier treated as satisfied (item 17), a guard that could not see
the published artefact (item 35), and a regex that could never match (item 36).

Where the allowed figures come from
-----------------------------------
**The harness's own stdout, parsed.** Not a table of expected values maintained
alongside it — that would be a second copy free to drift from the first, which is
the defect restated one level up. `harness_proportions()` runs
`analysis/measure_efficacy.py` and `analysis/measure_base_rate.py` and takes
whatever proportions they print. If their output format changes, the parsed set
collapses and the check **fails closed** rather than passing vacuously.

**Yes, this covers the base-rate figures**, because `measure_base_rate.py` is one
of the two commands. Its 201-page proportions (`111/201 (55.2%)` and the rest) are
in the allowed set on the same terms as the efficacy figures. There is one
asymmetry worth stating: the efficacy figures are recomputed from the corpus on
every run, so a detector change moves them immediately; the base-rate figures are
read from a committed manifest, so they move only when the corpus is rebuilt. Both
are checked against what their producer currently emits, which is the property
that matters.

Historical and hypothetical figures
-----------------------------------
Release-to-release comparison tables legitimately carry superseded figures, and
the README legitimately reasons about a counterfactual ("deleting all four checks
would drop recall to 16/42"). A check that fails on those is a check somebody
disables within a week, and a disabled check is worth less than no check because
it still looks like coverage.

The mechanism is an explicit marked region with a stated reason:

    <!-- figures:exempt reason="0.3.0 to 0.4.1 release comparison" -->
    | Overall recall | 15/20 (75.0%) | 21/35 (60.0%) | 27/42 (64.3%) |
    <!-- figures:end -->

**Why a marker rather than inferring it.** Three alternatives were considered and
rejected. *Heading-scoped exemption* (anything under a heading matching /histor|
superseded/) infers intent from prose a later edit can silently change. *Table
-scoped exemption* (skip any markdown table with a version column) would have
exempted the 0.4.1 column too, which is a current claim sitting in the same table.
*Age-based exemption* (allow any figure a previous release published) is the
weakest of the three: it would have allowed every one of the six stale surfaces,
because each stale figure was a previous release's real output. The marker is
explicit, greppable, requires a written reason a reviewer can audit, and is
cheapest to reverse — deleting a marker re-arms the check on that region.

**REASONED, not evidenced:** that an explicit marker will be used honestly rather
than sprayed over a file to silence the check. Nothing here prevents that; the
`reason=` requirement makes it visible in review and `git log -S "figures:exempt"`
finds every one. What would overturn it: a session adding a marker without a
defensible reason. The cheapest counter, if that happens, is to cap the number of
exempt regions per file rather than to remove the mechanism.

Fail-closed rules
-----------------
An unclosed region would silently exempt the rest of the file — the exact shape
this module exists to close — so it is a violation, and the region does not extend
past it. A region with no `reason=` is a violation. A stray `figures:end` with no
opening marker is a violation.
"""
from __future__ import annotations

import re
import subprocess
import sys

from pathlib import Path
from typing import NamedTuple

REPO_ROOT = Path(__file__).resolve().parent.parent

# Surfaces that publish figures and must therefore carry only current ones.
# docs/index.html is deliberately absent: it renders percentages in prose
# ("64% recall") rather than as `k/n (p%)`, so this parser sees nothing there.
# That is a STATED GAP, not coverage — see the module docstring in
# tests/test_figure_rules.py and ledger item 42.
FIGURE_SURFACES = [
    "README.md",
    "docs/llms.txt",
    "docs/LAUNCH-FACTS.md",
    "PATTERNS.md",
    "SHIP-READINESS.md",
    "CHANGELOG.md",
]

# The commands whose stdout defines "what the harness currently produces".
HARNESS_COMMANDS = [
    [sys.executable, str(REPO_ROOT / "analysis" / "measure_efficacy.py")],
    [sys.executable, str(REPO_ROOT / "analysis" / "measure_base_rate.py")],
]

# `6/37 (16.2%` — a fraction immediately followed by a parenthesised percentage.
# A bare `10/10` in a comparison column carries no percentage and asserts nothing
# about a rate, so it is deliberately not matched.
PROPORTION_RE = re.compile(r"(?<![\d./])(\d+)\s*/\s*(\d+)\s*\(\s*(\d+(?:\.\d+)?)\s*%")

EXEMPT_OPEN_RE = re.compile(r"<!--\s*figures:exempt(?P<attrs>[^>]*?)-->")
EXEMPT_END_RE = re.compile(r"<!--\s*figures:end\s*-->")
REASON_RE = re.compile(r'reason\s*=\s*"([^"]+)"')

# One decimal place is the project's convention; allow two so a more precise
# rendering of the same number is not called an error.
PCT_TOLERANCE = 0.06


class Violation(NamedTuple):
    """One figure-rule breach. Same shape as claim_rules.Violation."""

    rule: str
    message: str
    excerpt: str
    source: str


class Proportion(NamedTuple):
    k: int
    n: int
    pct: float
    line: int
    excerpt: str


class AllowedFigures(NamedTuple):
    """What the harness currently produces."""

    pairs: set[tuple[int, int]]
    raw: str


def extract_proportions(text: str) -> list[Proportion]:
    """Every `k/n (p%` in `text`, with its 1-indexed line number."""
    out: list[Proportion] = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        for match in PROPORTION_RE.finditer(line):
            k, n, pct = int(match.group(1)), int(match.group(2)), float(match.group(3))
            out.append(Proportion(k=k, n=n, pct=pct, line=line_no,
                                  excerpt=match.group(0).strip()))
    return out


def harness_proportions() -> AllowedFigures:
    """Run the harness and take the proportions it prints.

    Deliberately not a maintained table of expected values: a second copy of the
    figures is free to drift from the first, which is the defect one level up.
    """
    chunks: list[str] = []
    for command in HARNESS_COMMANDS:
        result = subprocess.run(command, capture_output=True, text=True,
                                cwd=str(REPO_ROOT), check=False)
        if result.returncode != 0:
            raise SystemExit(
                f"FAIL: harness command exited {result.returncode}: "
                f"{' '.join(command)}\n{result.stderr[:800]}\n"
                "This check has NOT passed — it could not establish what the "
                "current figures are."
            )
        chunks.append(result.stdout)
    raw = "\n".join(chunks)
    pairs = {(p.k, p.n) for p in extract_proportions(raw)}
    return AllowedFigures(pairs=pairs, raw=raw)


def _exempt_lines(text: str, source: str) -> tuple[set[int], list[Violation]]:
    """Line numbers inside a well-formed exempt region, plus marker violations.

    Fails closed: an unclosed region does NOT extend to end of file, because a
    stray marker would otherwise silence every figure after it.
    """
    exempt: set[int] = set()
    problems: list[Violation] = []
    open_line: int | None = None
    open_excerpt = ""

    for line_no, line in enumerate(text.splitlines(), start=1):
        open_match = EXEMPT_OPEN_RE.search(line)
        end_match = EXEMPT_END_RE.search(line)

        if open_match is not None:
            if open_line is not None:
                problems.append(Violation(
                    rule="figure-exempt-unclosed",
                    message=(f"{source}: a figures:exempt region opened at line "
                             f"{open_line} was never closed before another opened "
                             f"at line {line_no}."),
                    excerpt=open_excerpt, source=source))
            if REASON_RE.search(open_match.group("attrs") or "") is None:
                problems.append(Violation(
                    rule="figure-exempt-no-reason",
                    message=(f'{source}: figures:exempt at line {line_no} has no '
                             f'reason="...". State why these figures are not '
                             f"current, so a reviewer can audit the exemption."),
                    excerpt=open_match.group(0), source=source))
            open_line = line_no
            open_excerpt = open_match.group(0)
            continue

        if end_match is not None:
            if open_line is None:
                problems.append(Violation(
                    rule="figure-exempt-stray-end",
                    message=(f"{source}: figures:end at line {line_no} closes "
                             f"nothing. Either a region marker was deleted or this "
                             f"one is spurious."),
                    excerpt=end_match.group(0), source=source))
            else:
                exempt.update(range(open_line, line_no + 1))
                open_line = None
            continue

    if open_line is not None:
        problems.append(Violation(
            rule="figure-exempt-unclosed",
            message=(f"{source}: figures:exempt opened at line {open_line} is never "
                     f"closed. An unclosed region would silence every figure after "
                     f"it, so it exempts nothing and is reported instead."),
            excerpt=open_excerpt, source=source))
    return exempt, problems


def find_figure_violations(
    text: str, *, source: str = "<text>", allowed: AllowedFigures | None = None,
) -> list[Violation]:
    """Every figure-rule violation in `text`.

    The single entry point, mirroring `claim_rules.find_violations`. `allowed`
    may be passed in to avoid re-running the harness per surface.
    """
    if allowed is None:
        allowed = harness_proportions()

    if len(allowed.pairs) < 20:
        # Guarding the guard. An empty or near-empty allowed-set would make every
        # surface pass — the vacuous-rule failure of ledger item 36.
        raise SystemExit(
            f"FAIL: only {len(allowed.pairs)} proportions parsed from harness "
            f"output. This check has NOT passed; it cannot verify anything "
            f"against an empty reference set."
        )

    exempt, out = _exempt_lines(text, source)

    for prop in extract_proportions(text):
        if prop.line in exempt:
            continue

        expected_pct = 100.0 * prop.k / prop.n if prop.n else 0.0
        if abs(expected_pct - prop.pct) > PCT_TOLERANCE:
            out.append(Violation(
                rule="figure-arithmetic",
                message=(f"{source}:{prop.line}: {prop.k}/{prop.n} is "
                         f"{expected_pct:.1f}%, not {prop.pct}%."),
                excerpt=prop.excerpt, source=source))
            continue

        if (prop.k, prop.n) not in allowed.pairs:
            out.append(Violation(
                rule="figure-not-current",
                message=(f"{source}:{prop.line}: {prop.k}/{prop.n} is not a "
                         f"proportion the harness currently produces. Either "
                         f"re-run the harness and update this surface, or mark "
                         f"the region <!-- figures:exempt reason=\"...\" --> if "
                         f"it is deliberately historical."),
                excerpt=prop.excerpt, source=source))
    return out


def main() -> int:
    """Check every declared surface. Used by CI and by the pre-release gate."""
    allowed = harness_proportions()
    print(f"Harness currently produces {len(allowed.pairs)} distinct proportions.")

    total = 0
    for rel in FIGURE_SURFACES:
        path = REPO_ROOT / rel
        if not path.exists():
            print(f"FAIL: declared surface {rel} does not exist.")
            total += 1
            continue
        violations = find_figure_violations(
            path.read_text(encoding="utf-8"), source=rel, allowed=allowed)
        for violation in violations:
            print(f"  [{violation.rule}] {violation.message}")
            print(f"      excerpt: {violation.excerpt}")
        total += len(violations)

    if total:
        print(f"\n{total} figure violation(s).")
        return 1
    print("\nNo figure violations: every published proportion is one the harness "
          "currently produces.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
