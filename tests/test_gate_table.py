"""Every gate must have its negative-control status recorded before it is relied on.

The defect this closes is not a bug in any one gate. It is a habit: a gate gets
added or rewritten, it reports green, and green is read as "it works" when all it
establishes is "it did not object today". A gate that has never been observed
refusing anything is not known to be a gate at all.

That shape has now been logged repeatedly in this repository (ledger items 17, 35,
36, 42/45, 16, and 59). Item 16 was closed for `lowest-direct` by running a
negative control, and the very same commit rewrote the `security` job, which then
inherited the identical problem: relied upon, never seen red.

So the fix is an accounting rather than another one-off demonstration. `CLAUDE.md`
carries a table of every gate with whether it has ever been observed red, and this
file asserts the table stays complete:

* every job in every tracked workflow appears in it, so adding a CI job without
  recording its negative-control status fails the suite. The scope is *every*
  workflow file rather than `ci.yml` alone: `publish.yml` gates the most public
  surface this project has, and a table that could not see it would reproduce the
  exact out-of-scope defect this accounting exists to close;
* every tracked script under `scripts/` and `analysis/` is accounted for, either as
  a gate row or in an explicit not-a-gate list with a reason, so a new gate cannot
  slip in unclassified. This mirrors `NO_FLOOR_EXPECTED` in the floor auditor,
  where opting out is a declaration rather than an omission;
* the status is drawn from a controlled vocabulary, so "we think it is fine" cannot
  be written where "never observed red" or "unknown" belongs.

What this cannot see, stated here because that is this project's rule: it checks
that a status is *recorded*, not that the status is *true*. Someone can write
"RED OBSERVED" beside a URL to a green run. The evidence cell is required to carry
a link or an exit code so a reviewer can check it, but the checking is a reviewer's
job, not this file's.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
CLAUDE = REPO / "CLAUDE.md"

TABLE_START = "<!-- gate-table:start -->"
TABLE_END = "<!-- gate-table:end -->"
NOT_A_GATE_START = "<!-- gate-table:not-a-gate -->"
NOT_A_GATE_END = "<!-- gate-table:not-a-gate-end -->"
RULE_START = "<!-- gate-table:rule -->"
RULE_END = "<!-- gate-table:rule-end -->"

# The only three things a status cell may say. "Probably fine" is not one of them,
# and neither is silence.
STATUSES = ("RED OBSERVED", "never observed red", "unknown")


def claude_text() -> str:
    return CLAUDE.read_text(encoding="utf-8")


def tracked_workflows() -> list[str]:
    """Every workflow file under version control.

    Derived, not listed. A hand-written list of workflow files is the same defect
    the CI mypy scope had (ledger item 58): it passes today and rots the moment a
    file is added.
    """
    out = subprocess.run(
        ["git", "ls-files", ".github/workflows/*.yml", ".github/workflows/*.yaml"],
        cwd=REPO, capture_output=True, text=True, check=True,
    )
    return sorted(p for p in out.stdout.split() if p)


def ci_jobs() -> list[str]:
    """Job names across every tracked workflow, parsed as YAML rather than grepped.

    A regex over `^  [a-z-]+:` also matches `push:` under `on:` and `contents:`
    under `permissions:`, which would make this check assert the presence of
    things that are not jobs while still missing a real one.
    """
    jobs: set[str] = set()
    for path in tracked_workflows():
        data = yaml.safe_load((REPO / path).read_text(encoding="utf-8"))
        jobs.update(data.get("jobs") or {})
    return sorted(jobs)


def tracked_scripts() -> list[str]:
    out = subprocess.run(
        ["git", "ls-files", "scripts/*.py", "analysis/*.py"],
        cwd=REPO, capture_output=True, text=True, check=True,
    )
    return sorted(p for p in out.stdout.split() if p)


def _region(text: str, start: str, end: str) -> str:
    """The text between two markers.

    An unclosed region raises rather than silently returning the rest of the file,
    which is the difference between a missing table and a table that swallowed the
    document.
    """
    if start not in text:
        raise AssertionError(f"CLAUDE.md has no {start} marker")
    if end not in text:
        raise AssertionError(f"CLAUDE.md has {start} but no {end}: the region is unclosed")
    body = text.split(start, 1)[1].split(end, 1)[0]
    return body


def table_region() -> str:
    return _region(claude_text(), TABLE_START, TABLE_END)


def table_rows() -> list[list[str]]:
    """Body rows of the gate table, header and separator dropped."""
    rows: list[list[str]] = []
    for line in table_region().splitlines():
        stripped = line.strip()
        if not (stripped.startswith("|") and stripped.endswith("|")):
            continue
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if all(set(c) <= set("-: ") and c for c in cells):  # separator row
            continue
        rows.append(cells)
    return rows[1:] if rows else rows  # drop the header


def table_subjects() -> set[str]:
    """Every backticked token in the first column: the things the table covers."""
    subjects: set[str] = set()
    for row in table_rows():
        subjects.update(re.findall(r"`([^`]+)`", row[0]))
    return subjects


def not_a_gate_entries() -> dict[str, str]:
    """Declared non-gates, mapped to the stated reason."""
    entries: dict[str, str] = {}
    for line in _region(claude_text(), NOT_A_GATE_START, NOT_A_GATE_END).splitlines():
        stripped = line.strip()
        if not stripped.startswith("-"):
            continue
        names = re.findall(r"`([^`]+)`", stripped)
        if not names:
            continue
        reason = stripped.split("`")[-1].strip(" :.")
        for name in names:
            entries[name] = reason
    return entries


# --- guarding the guard -------------------------------------------------------
#
# Every assertion below is quantified over a parsed set. A parser that returns
# nothing makes all of them pass vacuously, which is precisely the failure mode
# this file exists to close, so each parser is asserted non-empty first.


def test_the_workflow_parser_finds_the_workflows_that_exist() -> None:
    workflows = tracked_workflows()
    assert len(workflows) >= 2, f"parsed only {workflows}; ci.yml and publish.yml exist"


def test_the_ci_job_parser_finds_the_jobs_that_exist() -> None:
    jobs = ci_jobs()
    assert len(jobs) >= 5, f"parsed only {jobs}; every check below would be vacuous"
    # ci.yml's three, and publish.yml's two. publish.yml gates the most public
    # surface here, so its omission would be the defect, not an acceptable scope.
    for expected in ("test", "security", "lowest-direct", "build", "publish"):
        assert expected in jobs, f"{expected} missing from parsed jobs {jobs}"


def test_the_job_parser_does_not_mistake_on_or_permissions_keys_for_jobs() -> None:
    """`push`, `pull_request` and `contents` are not jobs. A grep thinks they are."""
    jobs = ci_jobs()
    for not_a_job in ("push", "pull_request", "contents", "jobs"):
        assert not_a_job not in jobs, f"{not_a_job} parsed as a job name"


def test_the_script_parser_finds_the_scripts_that_exist() -> None:
    scripts = tracked_scripts()
    assert len(scripts) >= 6, f"parsed only {scripts}; checks below would be vacuous"


def test_the_table_has_rows() -> None:
    rows = table_rows()
    assert len(rows) >= 10, (
        f"gate table has {len(rows)} body rows; expected one for every CI job "
        f"({len(ci_jobs())}) and every repository-side gate. Rows: {rows}"
    )


def test_an_unclosed_table_region_is_a_failure_not_a_silent_exemption() -> None:
    text = claude_text()
    assert text.count(TABLE_START) == 1, "exactly one gate table region expected"
    assert text.count(TABLE_END) == 1, "exactly one gate table end marker expected"
    assert text.index(TABLE_START) < text.index(TABLE_END), "markers are inverted"


# --- the rule itself ----------------------------------------------------------


def test_every_ci_job_appears_in_the_gate_table() -> None:
    """The brief's requirement: a new job without a recorded status fails here."""
    subjects = table_subjects()
    missing = [j for j in ci_jobs() if j not in subjects]
    assert not missing, (
        f"these CI jobs are not in the CLAUDE.md gate table: {missing}. A gate that "
        f"is added or materially changed needs a negative control before it is "
        f"relied on; record it in the table between {TABLE_START} and {TABLE_END}. "
        f"Table currently covers: {sorted(subjects)}"
    )


def test_every_tracked_script_is_either_a_gate_or_declared_not_one() -> None:
    """A new gate cannot arrive unclassified.

    Same shape as NO_FLOOR_EXPECTED in the floor auditor: opting out is a written
    declaration with a reason, not an omission nobody notices.
    """
    subjects = table_subjects()
    declared = not_a_gate_entries()
    unaccounted = [s for s in tracked_scripts() if s not in subjects and s not in declared]
    assert not unaccounted, (
        f"these tracked scripts are neither in the gate table nor declared as "
        f"not-a-gate: {unaccounted}. Add a table row with its negative-control "
        f"status, or list it under {NOT_A_GATE_START} with a reason."
    )


def test_every_declared_non_gate_carries_a_reason() -> None:
    entries = not_a_gate_entries()
    assert entries, "the not-a-gate list is empty; every parser here must be non-empty"
    blank = [name for name, reason in entries.items() if len(reason) < 10]
    assert not blank, f"declared not-a-gate without a stated reason: {blank}"


def test_every_gate_row_is_complete() -> None:
    for row in table_rows():
        assert len(row) >= 4, f"gate table row has {len(row)} cells, expected 4: {row}"
        blank = [i for i, cell in enumerate(row) if not cell]
        assert not blank, f"gate table row has empty cells at {blank}: {row}"


def test_every_gate_status_uses_the_controlled_vocabulary() -> None:
    """So that vague prose cannot stand where a verdict belongs."""
    for row in table_rows():
        status = row[2]
        assert any(status.startswith(s) for s in STATUSES), (
            f"status {status!r} for {row[0]!r} is not one of {STATUSES}. If the "
            f"history cannot be established, write 'unknown' rather than guessing."
        )


def test_a_red_observed_claim_carries_checkable_evidence() -> None:
    """Not proof the run was red. Proof a reviewer can go and look."""
    for row in table_rows():
        if not row[2].startswith("RED OBSERVED"):
            continue
        evidence = row[3]
        assert "http" in evidence or "exit" in evidence, (
            f"{row[0]!r} claims RED OBSERVED but its evidence cell carries neither "
            f"a run URL nor an exit code: {evidence!r}"
        )


def test_the_negative_control_rule_is_stated_beside_the_table() -> None:
    rule = _region(claude_text(), RULE_START, RULE_END)
    assert "negative control" in rule.lower(), (
        "the rule beside the gate table must state the negative-control requirement"
    )
    assert len(rule.strip()) >= 80, "the rule is too short to say anything useful"
