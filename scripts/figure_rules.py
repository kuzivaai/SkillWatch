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
    context: str = ""


class AllowedFigures(NamedTuple):
    """What the harness currently produces.

    `labels` carries the metric each proportion was printed under, which is what
    makes correspondence checking possible. Discarding it — as the first version of
    this module did — reduces the check to set membership, and set membership cannot
    see a substitution: `evasive recall 27/42` passes, because 27/42 is a real
    current proportion. It is overall recall.
    """

    pairs: set[tuple[int, int]]
    raw: str
    labels: dict[tuple[int, int], set[str]] = {}
    per_command: dict[str, int] = {}


# --- 3c. The fail-closed floor, derived rather than picked -------------------
#
# The floor was `< 20`, a hand-picked constant against an actual count of 34. A
# single global threshold cannot notice one command returning nothing while the
# other's output alone clears it: measure_efficacy alone yields ~24 proportions, so
# a total failure of measure_base_rate would still pass a global floor of 20.
#
# The floor is now the SUM of a per-command minimum, and each command is checked
# against its own minimum, so a partial parse of either fails.
#
# Each minimum is the count of proportions that command must print for its report
# to be structurally complete, derived by counting them in the current output and
# subtracting a small margin for figures that legitimately come and go (a family
# with zero members prints no interval, an empty FP breakdown prints no rows).
MIN_PROPORTIONS_PER_COMMAND = {
    "measure_efficacy.py": 18,   # 3 corpora x (fp, fn, precision, recall) + families
    "measure_base_rate.py": 10,  # 10 techniques, plus exposure and delta rows
}


# THERE IS DELIBERATELY NO GLOBAL FLOOR.
#
# `derived_floor()` used to return the SUM of the per-command minimums (28) and that
# number was printed beside the DEDUPLICATED distinct count (34). Those two are not
# comparable: five proportions are produced by BOTH commands, so the sum
# double-counts what the distinct set collapses. Printing them together invited the
# reader — and a future maintainer — to treat 28 as a threshold for 34.
#
# Worse, a global check would reject healthy output. If measure_efficacy parses 18
# (meeting its minimum of 18) and measure_base_rate parses 10 (meeting its minimum of
# 10) with eight overlapping, both per-command checks pass while the distinct set is
# 20 — below 28. A gate that fails on healthy output is a gate someone removes.
#
# Decision: per-command minimums are compared against per-command PARSES, and never
# against the deduplicated total. The only global assertion left is that the set is
# non-empty, which is a different claim and cannot be confused with a threshold.
#
# REASONED, not evidenced: that per-command minimums alone are sufficient to catch a
# partial parse. The assumption is that a degradation shows up as one command's count
# dropping, which is what a format change or a crashed corpus load produces. What
# would overturn it: a failure where both commands parse enough rows but the WRONG
# rows — which a count floor of any shape cannot see (see the note below).
#
# A COUNT FLOOR CANNOT DETECT A PARSE RETURNING THE WRONG PROPORTIONS. Scraping
# confidence-interval bounds as fractions, for instance, would keep every count high.
# Detecting that needs the parsed values compared against an independently computed
# expectation — recomputing a known metric and asserting the parse contains it.


# --- 3a. Metric families, for correspondence --------------------------------
#
# HOW A LABEL IS RECOGNISED, and the alternatives rejected.
#
# Chosen: classify both sides — the harness's printed label and the surface's
# surrounding text — into a small set of METRIC FAMILIES by keyword, then require
# the families to agree. Keyword classification is crude but symmetric: the same
# function runs on both sides, so a surface phrased like the harness always matches,
# and the failure mode is an unclassified figure that is skipped and counted rather
# than a wrong verdict.
#
# Rejected: EXACT LABEL STRING MATCHING. The harness prints "False-positive rate
# (overall)"; the README says "Benign false positives". Both are correct English for
# the same quantity and no exact match survives ordinary editing, so the rule would
# fire constantly on correct text and be disabled within a week — the same failure
# the figures:exempt mechanism exists to avoid.
#
# Rejected: REQUIRING AN EXPLICIT ANNOTATION on every published figure, e.g.
# `27/42 <!--metric:recall-overall-->`. It would be exact and machine-checkable, and
# it would put markup beside every number a reader sees, on six surfaces, for a rule
# that catches one class of error. Rejected on cost, and because an annotation a
# human writes by hand can itself be wrong in exactly the way being guarded against.
#
# Rejected: POSITIONAL TABLE PARSING — read the row header, resolve the column. It
# handles tables well and prose not at all, and prose carries most of the figures on
# these surfaces.
#
# REASONED, not evidenced: that keyword families are specific enough to catch real
# substitutions and loose enough not to fire on correct prose. The assumption is
# that a surface naming a metric uses at least one of its discriminating words.
# What would overturn it: a mislabelled figure this rule misses, or a correct figure
# it flags. Cheapest to reverse: the keyword table below is data, not logic.
FAMILY_PRECISION = "precision"
FAMILY_RECALL_OVERALL = "recall-overall"
FAMILY_RECALL_EVASIVE = "recall-evasive"
FAMILY_FP = "false-positive-rate"
FAMILY_FN = "false-negative-rate"

_EVASIVE_RE = re.compile(r"\bevasive\b", re.IGNORECASE)
_RECALL_RE = re.compile(r"\brecall\b|\bcatch(?:es)?\b", re.IGNORECASE)
_PRECISION_RE = re.compile(r"\bprecision\b", re.IGNORECASE)
_FP_RE = re.compile(r"false[\s-]?positive|\bfp\b", re.IGNORECASE)
_FN_RE = re.compile(r"false[\s-]?negative|\bfn\b", re.IGNORECASE)


# The context is stored as "before\x00after" so classify_metric can prefer the text
# that PRECEDES a figure. A label almost always precedes its number — "Overall
# recall is 27/42", "| Precision | 27/33 |" — and preferring the trailing window
# misread both figures in one README sentence.
_CONTEXT_SEP = "\x00"


def _join_context(before: str, after: str) -> str:
    return f"{before}{_CONTEXT_SEP}{after}"


def classify_metric(context: str) -> str | None:
    """Which metric family does this text name? None if it names none.

    Run on the harness's own label and on a surface's surrounding text, so both
    sides are classified by identical rules. Text before the figure wins; the text
    after is consulted only when nothing before it names a metric.
    """
    if _CONTEXT_SEP in context:
        before, after = context.split(_CONTEXT_SEP, 1)
        return _classify_one(before) or _classify_one(after)
    return _classify_one(context)


def _classify_one(context: str) -> str | None:
    if _FP_RE.search(context):
        return FAMILY_FP
    if _FN_RE.search(context):
        return FAMILY_FN
    if _PRECISION_RE.search(context):
        return FAMILY_PRECISION
    if _RECALL_RE.search(context):
        return (FAMILY_RECALL_EVASIVE if _EVASIVE_RE.search(context)
                else FAMILY_RECALL_OVERALL)
    return None


# How much text after a proportion may still carry its label. "catches 27/42
# (64.3%) against evasive payloads" puts the discriminating word after the figure.
# Truncated at the first clause boundary: on a long line, an untruncated window
# bleeds into the NEXT figure's clause and misreads the label. That produced two
# false positives on README.md before the boundary was added.
_CONTEXT_AFTER = 80
_CLAUSE_END_RE = re.compile(r"[;.,]")


def extract_proportions(text: str) -> list[Proportion]:
    """Every `k/n (p%` in `text`, with its line number and label context.

    The context is the text on the same line between the previous proportion (or the
    line start) and this one, plus a short window after it. That covers a table row
    (`| Precision | 27/33 (81.8%) |`) and prose in either direction.
    """
    out: list[Proportion] = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        previous_end = 0
        for match in PROPORTION_RE.finditer(line):
            k, n, pct = int(match.group(1)), int(match.group(2)), float(match.group(3))
            before = line[previous_end:match.start()]
            after = line[match.end():match.end() + _CONTEXT_AFTER]
            # Drop the closing ")%" fragment, then stop at the first clause end.
            after = after.lstrip(")% ")
            boundary = _CLAUSE_END_RE.search(after)
            if boundary is not None:
                after = after[:boundary.start()]
            out.append(Proportion(
                k=k, n=n, pct=pct, line=line_no,
                excerpt=match.group(0).strip(),
                context=_join_context(before, after)))
            previous_end = match.end()
    return out


def count_unlabelled(text: str) -> int:
    """How many proportions name no metric, so correspondence cannot be checked.

    Reported rather than hidden: this is the honest measure of what the rule does
    not cover.
    """
    return sum(1 for p in extract_proportions(text) if classify_metric(p.context) is None)


def harness_proportions() -> AllowedFigures:
    """Run the harness and take the proportions it prints.

    Deliberately not a maintained table of expected values: a second copy of the
    figures is free to drift from the first, which is the defect one level up.
    """
    chunks: list[str] = []
    per_command: dict[str, int] = {}
    labels: dict[tuple[int, int], set[str]] = {}

    for command in HARNESS_COMMANDS:
        name = str(Path(command[-1]).name)
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
        found = extract_proportions(result.stdout)
        per_command[name] = len(found)
        for prop in found:
            labels.setdefault((prop.k, prop.n), set()).add(prop.context.strip())

    raw = "\n".join(chunks)
    pairs = {(p.k, p.n) for p in extract_proportions(raw)}
    return AllowedFigures(pairs=pairs, raw=raw, labels=labels, per_command=per_command)


def families_for(allowed: AllowedFigures, pair: tuple[int, int]) -> set[str | None]:
    """Every metric family the harness printed this proportion under."""
    return {classify_metric(label) for label in allowed.labels.get(pair, set())}


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

    # Guarding the guard, per command. An empty or near-empty allowed-set would make
    # every surface pass — the vacuous-rule failure of ledger item 36. Checked per
    # command because a global floor cannot see one command returning nothing while
    # the other's output alone clears the threshold.
    for name, minimum in MIN_PROPORTIONS_PER_COMMAND.items():
        actual = allowed.per_command.get(name)
        if actual is None:
            raise SystemExit(
                f"FAIL: {name} produced no parsed output at all. This check has NOT "
                f"passed; it cannot verify anything against a missing reference set."
            )
        if actual < minimum:
            raise SystemExit(
                f"FAIL: {name} yielded only {actual} proportions, below its minimum "
                f"of {minimum}. A partial parse would silently shrink the reference "
                f"set and let stale figures through. This check has NOT passed."
            )
    if len(allowed.pairs) < 1:
        raise SystemExit("FAIL: the reference set is empty. This check has NOT passed.")

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
            continue

        # Correspondence, not membership. A real current proportion under the wrong
        # metric label is the defect set membership cannot see.
        claimed = classify_metric(prop.context)
        if claimed is None:
            continue  # names no metric — see count_unlabelled(), reported not hidden
        harness_families = families_for(allowed, (prop.k, prop.n))
        if claimed not in harness_families:
            named = sorted(f for f in harness_families if f) or ["no metric family"]
            out.append(Violation(
                rule="figure-mislabelled",
                message=(f"{source}:{prop.line}: {prop.k}/{prop.n} is published as "
                         f"{claimed} but the harness prints it as {', '.join(named)}. "
                         f"The value is real and current; the label is wrong."),
                excerpt=prop.excerpt.strip(), source=source))
    return out


def main() -> int:
    """Check every declared surface. Used by CI and by the pre-release gate."""
    allowed = harness_proportions()
    print(f"Harness currently produces {len(allowed.pairs)} distinct proportions.")
    print("Per-command parses are checked against per-command minimums. There is no "
          "global floor: the minimums sum without deduplication and the distinct "
          "count deduplicates, so the two are not comparable.")
    for name, count in sorted(allowed.per_command.items()):
        minimum = MIN_PROPORTIONS_PER_COMMAND.get(name, 0)
        print(f"  {name:<24} {count:>3} parsed, minimum {minimum}")

    total = 0
    labelled_total = 0
    unlabelled_total = 0
    print()
    for rel in FIGURE_SURFACES:
        path = REPO_ROOT / rel
        if not path.exists():
            print(f"FAIL: declared surface {rel} does not exist.")
            total += 1
            continue
        text = path.read_text(encoding="utf-8")
        violations = find_figure_violations(text, source=rel, allowed=allowed)
        for violation in violations:
            print(f"  [{violation.rule}] {violation.message}")
            print(f"      excerpt: {violation.excerpt}")
        total += len(violations)

        # Correspondence coverage, reported rather than assumed. A figure naming no
        # metric cannot be label-checked; saying how many is the honest measure of
        # what this rule does NOT cover.
        exempt, _ = _exempt_lines(text, rel)
        checkable = [p for p in extract_proportions(text) if p.line not in exempt]
        unlabelled = [p for p in checkable if classify_metric(p.context) is None]
        labelled_total += len(checkable) - len(unlabelled)
        unlabelled_total += len(unlabelled)
        print(f"  {rel:<24} {len(checkable) - len(unlabelled):>3} label-checked, "
              f"{len(unlabelled):>3} name no metric")

    print(f"\ncorrespondence coverage: {labelled_total} of "
          f"{labelled_total + unlabelled_total} non-exempt proportions carry a "
          f"recognisable metric label.")
    print(f"the remaining {unlabelled_total} are NOT correspondence-checked — they "
          f"are still checked for currency and arithmetic. See ledger item 42.")

    if total:
        print(f"\n{total} figure violation(s).")
        return 1
    print("\nNo figure violations: every published proportion is one the harness "
          "currently produces, under a label consistent with the harness's own.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
