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

A table of names is not enough, and that gap is also closed here. Recording that a
gate HAS a status validates its identity, not its behaviour: a job rewritten under
the same name keeps its old row and its old verdict. That is not hypothetical, it
is what happened. The `security` job was rewritten on 2026-07-30 (separate venv,
`pip freeze --exclude-editable`, the `-r` shape, `--strict` for `--skip-editable`)
and silently carried forward a never-observed-red status under an unchanged name.
An accounting that certifies something it has not examined is the same shape as
every other defect in this repository's ledger under that heading.

So each job's row also records a hash of what the job actually executes, and the
suite fails if a job's current hash no longer matches. A changed hash forces the
row's status to `unknown`: the gate changed materially and needs a fresh negative
control before it is relied on again.

**Why the hash covers the whole job spec and not only `run:` lines.** Hashing a
whole workflow *file* was considered and rejected earlier, correctly, because it
fires on comment edits and gets switched off. The natural narrowing is "executable
`run:` lines only", mirroring `pip_audit_run_lines()` in tests/test_ci_scope.py.
That narrowing is wrong here, and measurably so: `publish.yml`'s `publish` job has
**zero** `run:` lines, so a run-lines-only hash is `sha256("[]")` for it, a
constant. It could not see `needs: build` (the ordering that keeps a failed build
from ever reaching PyPI, and the safety property the 2026-07-30 build control
depends on), nor `environment: pypi`, nor `permissions: id-token: write`, nor the
pinned SHA of `pypa/gh-action-pypi-publish`. A hash blind to all of that would
certify a job it had not examined, which is the defect being closed rather than a
fix for it.

The hash is therefore over the parsed job specification with cosmetic keys removed.
Parsing as YAML drops comments, blank lines and trailing whitespace *inherently*,
which is a stronger normalisation than stripping them by regex, and it makes step
order significant, which is correct: step ordering is what isolated the pip-audit
step from the floor step in the 2026-07-30 control.

What deliberately does NOT move the hash: `name:` on a job or a step. Renaming a
step changes nothing that executes. Note the cost, since it is real: the evidence
cells in the table quote step names, so a rename can leave the *prose* stale while
the hash stays green. That is a documentation problem, not a gate-behaviour one.

What this cannot see, stated here because that is this project's rule:

1. It checks that a status is *recorded*, not that the status is *true*. Someone
   can write "RED OBSERVED" beside a URL to a green run. The evidence cell must
   carry a link or an exit code so a reviewer can check it, but the checking is a
   reviewer's job, not this file's.
2. **Repository-side gates are not hashed.** `scripts/*.py` and
   `analysis/verify_capture.py` can be rewritten under the same name and keep their
   status, exactly as `security` did. A hash of the source text would fire on
   comment edits, which is the rejected shape; the right instrument is a hash over
   the parsed AST with docstrings stripped. That was not built here, and the gap is
   logged in the ledger rather than left implied.
3. A job that calls a script whose *contents* changed keeps its hash. The hash sees
   `python3 scripts/figure_rules.py`, not what that file now does. Point 2 is the
   same hole seen from the other side.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any

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


# --- the executable-surface hash ---------------------------------------------

# Keys whose value changes nothing that executes. `name` is a display label on a
# job or a step; renaming "Audit installed dependencies" to "Audit resolved
# dependencies" was part of the 2026-07-30 rewrite and is not itself a behaviour
# change. Everything else in the spec is in scope, including `needs`, `if`,
# `environment`, `permissions`, `strategy` and every `uses`/`with`.
COSMETIC_KEYS = frozenset({"name"})

HASH_LENGTH = 12


def _canonicalise(node: Any) -> Any:
    """Drop cosmetic keys and normalise scalars so only behaviour remains.

    Strings are stripped and their lines right-trimmed. That matters for block
    scalars: a `run:` line gaining trailing whitespace is not a behaviour change,
    and a hash that moved on it would be the noisy check this design rejects.
    """
    if isinstance(node, dict):
        return {k: _canonicalise(v) for k, v in sorted(node.items()) if k not in COSMETIC_KEYS}
    if isinstance(node, list):
        return [_canonicalise(v) for v in node]
    if isinstance(node, str):
        return "\n".join(line.rstrip() for line in node.strip().splitlines())
    return node


def _triggers(data: dict[str, Any]) -> Any:
    """A workflow's `on:` block.

    Under YAML 1.1 the bare key `on` parses to the boolean True, not the string
    "on". Reading `data["on"]` returns None on every workflow in this repository
    and would silently drop the trigger from every hash, which is the vacuous-check
    shape this file exists to prevent. Both spellings are tried.
    """
    if "on" in data:
        return data["on"]
    return data.get(True)


def job_specs() -> dict[str, Any]:
    """Every job across every tracked workflow, keyed by job name.

    Each job carries its workflow's trigger block alongside it. A job's behaviour
    is not only what it runs but WHEN it runs: changing ci.yml's `on:` from
    `[push, pull_request]` to `[push]` would stop every pull request being gated
    at all, without touching a single job. A digest blind to that would keep
    reporting the gate unchanged while the gate had stopped applying.

    This was found by doing rather than by reasoning: the 2026-07-30 build control
    added `workflow_dispatch:` to publish.yml to make an unreachable workflow
    reachable, and an earlier draft of this hash did not notice.
    """
    specs: dict[str, Any] = {}
    for path in tracked_workflows():
        data = yaml.safe_load((REPO / path).read_text(encoding="utf-8"))
        trig = _triggers(data)
        for job, spec in (data.get("jobs") or {}).items():
            specs[job] = {"triggers": trig, "job": spec}
    return specs


def job_hash(job: str) -> str:
    """A stable digest of what a job executes, and of when it runs."""
    canon = json.dumps(_canonicalise(job_specs()[job]), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canon.encode("utf-8")).hexdigest()[:HASH_LENGTH]


def current_job_hashes() -> dict[str, str]:
    return {job: job_hash(job) for job in job_specs()}


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


def _raw_table_lines() -> list[list[str]]:
    """Every pipe-delimited row in the table region, separator rows dropped."""
    rows: list[list[str]] = []
    for line in table_region().splitlines():
        stripped = line.strip()
        if not (stripped.startswith("|") and stripped.endswith("|")):
            continue
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if all(set(c) <= set("-: ") and c for c in cells):  # separator row
            continue
        rows.append(cells)
    return rows


def table_rows() -> list[dict[str, str]]:
    """Body rows keyed by their column heading, lowercased.

    Keyed rather than indexed on purpose. Positional access (`row[2]` for the
    status) silently reads the wrong column the moment a column is inserted, and
    a column was inserted: the executable hash. A checker that keeps passing while
    reading the wrong cell is the shape this whole file exists to prevent.
    """
    raw = _raw_table_lines()
    if not raw:
        return []
    header = [h.lower() for h in raw[0]]
    return [dict(zip(header, cells)) for cells in raw[1:]]


def table_subjects() -> set[str]:
    """Every backticked token in the gate column: the things the table covers."""
    subjects: set[str] = set()
    for row in table_rows():
        subjects.update(re.findall(r"`([^`]+)`", row.get("gate", "")))
    return subjects


def recorded_job_hashes() -> dict[str, str]:
    """Job name -> the hash the table records for it.

    Only rows whose gate is a workflow job are returned; repository-side gates
    carry `n/a` and are excluded rather than silently treated as a hash.
    """
    jobs = set(job_specs())
    recorded: dict[str, str] = {}
    for row in table_rows():
        names = re.findall(r"`([^`]+)`", row.get("gate", ""))
        cell = row.get("executable hash", "")
        for name in names:
            if name in jobs:
                found = re.findall(r"`([0-9a-f]{%d})`" % HASH_LENGTH, cell)
                if found:
                    recorded[name] = found[0]
    return recorded


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


def test_the_table_has_the_columns_the_checks_read() -> None:
    """Guarding the guard: a renamed heading must fail loudly, not silently.

    Every row lookup below is by column name. If a heading were renamed, `.get()`
    would return "" and several checks would pass while reading nothing at all.
    """
    raw = _raw_table_lines()
    assert raw, "gate table has no rows at all"
    header = [h.lower() for h in raw[0]]
    for column in ("gate", "kind", "executable hash", "ever observed red", "evidence"):
        assert column in header, (
            f"gate table is missing the {column!r} column; found {header}. The "
            f"checks read cells by name, so a renamed heading disables them."
        )


def test_every_gate_row_is_complete() -> None:
    for cells in _raw_table_lines()[1:]:
        assert len(cells) >= 5, f"gate table row has {len(cells)} cells, expected 5: {cells}"
        blank = [i for i, cell in enumerate(cells) if not cell]
        assert not blank, f"gate table row has empty cells at {blank}: {cells}"


def test_every_gate_status_uses_the_controlled_vocabulary() -> None:
    """So that vague prose cannot stand where a verdict belongs."""
    for row in table_rows():
        status = row.get("ever observed red", "")
        assert any(status.startswith(s) for s in STATUSES), (
            f"status {status!r} for {row.get('gate')!r} is not one of {STATUSES}. If "
            f"the history cannot be established, write 'unknown' rather than guessing."
        )


# --- behaviour, not just identity ---------------------------------------------


def test_the_hash_parser_finds_a_hash_for_every_job() -> None:
    """Guarding the guard: an unparsed hash column makes the next test vacuous."""
    recorded = recorded_job_hashes()
    missing = [j for j in job_specs() if j not in recorded]
    assert not missing, (
        f"no executable hash recorded in the gate table for these jobs: {missing}. "
        f"A row without a hash records the gate's identity but not its behaviour, "
        f"so a rewrite under the same name would keep its old verdict. Current "
        f"hashes are: {current_job_hashes()}"
    )


def test_no_job_has_changed_since_its_negative_control() -> None:
    """The class fix: a job rewritten under its own name must not keep its status.

    This is exactly what went unnoticed when `security` was rewritten on
    2026-07-30 and inherited a never-observed-red verdict.
    """
    recorded = recorded_job_hashes()
    current = current_job_hashes()
    drifted = {job: (recorded[job], current[job])
               for job in recorded if current.get(job) != recorded[job]}
    assert not drifted, (
        "these jobs changed materially since their recorded negative control, so "
        "their status in the gate table is no longer evidence of anything and must "
        "be read as `unknown` until a fresh control is run:\n"
        + "\n".join(f"  {job}: recorded {was}, now {now}" for job, (was, now) in drifted.items())
        + "\n\nRun a fresh negative control against each, then update both the "
          "status/evidence cells and the executable hash. Do not update the hash "
          "alone: that records that the change happened and asserts nothing about "
          "whether the gate still refuses anything."
    )


def test_a_job_whose_hash_drifted_may_not_claim_red_observed() -> None:
    """Belt and braces: if the hash check is ever relaxed, the verdict still can't stand.

    Kept separate from the test above so that weakening one does not silently
    weaken the other.
    """
    recorded = recorded_job_hashes()
    current = current_job_hashes()
    for row in table_rows():
        for name in re.findall(r"`([^`]+)`", row.get("gate", "")):
            if name not in recorded or current.get(name) == recorded[name]:
                continue
            assert row.get("ever observed red", "").startswith("unknown"), (
                f"job {name!r} has drifted from its recorded hash but still claims "
                f"{row.get('ever observed red')!r}. A changed gate has no history."
            )


def test_a_comment_edit_does_not_move_a_job_hash() -> None:
    """The rejected whole-file hash fired on comments and would have been disabled.

    Parsing as YAML drops comments before hashing, so this holds structurally
    rather than by careful regex. Asserted on real workflow text, not a fixture.
    """
    for path in tracked_workflows():
        original = (REPO / path).read_text(encoding="utf-8")
        commented = original.replace(
            "jobs:", "jobs:\n  # a comment that changes nothing executable", 1
        )
        assert commented != original, f"could not inject a comment into {path}"
        before = yaml.safe_load(original)
        after = yaml.safe_load(commented)
        for job in (before.get("jobs") or {}):
            hb = hashlib.sha256(json.dumps(
                _canonicalise(before["jobs"][job]), sort_keys=True, separators=(",", ":")
            ).encode()).hexdigest()[:HASH_LENGTH]
            ha = hashlib.sha256(json.dumps(
                _canonicalise(after["jobs"][job]), sort_keys=True, separators=(",", ":")
            ).encode()).hexdigest()[:HASH_LENGTH]
            assert hb == ha, f"a comment edit moved {job}'s hash in {path}: {hb} -> {ha}"


def test_the_trigger_block_is_part_of_every_job_hash() -> None:
    """A gate that stops running is not a gate, and no job line need change for it.

    Found by doing: the build negative control added `workflow_dispatch:` to
    publish.yml, and an earlier draft of this hash did not notice, because `on:`
    sits outside `jobs:`.
    """
    for path in tracked_workflows():
        data = yaml.safe_load((REPO / path).read_text(encoding="utf-8"))
        assert _triggers(data) is not None, (
            f"{path} has no parseable `on:` block. Under YAML 1.1 the bare key `on` "
            f"becomes the boolean True; if this returned None the trigger would be "
            f"silently absent from every hash."
        )

    def digest(node: Any) -> str:
        return hashlib.sha256(json.dumps(
            _canonicalise(node), sort_keys=True, separators=(",", ":")
        ).encode()).hexdigest()[:HASH_LENGTH]

    spec = job_specs()["build"]
    widened = json.loads(json.dumps(spec))
    widened["triggers"] = {**(widened["triggers"] or {}), "workflow_dispatch": None}
    assert digest(widened) != digest(spec), (
        "adding a workflow_dispatch trigger did not move the build job's hash. A "
        "workflow becoming manually invocable is a change to when the gate runs."
    )

    narrowed = json.loads(json.dumps(job_specs()["test"]))
    trig = dict(narrowed["triggers"] or {})
    trig.pop("pull_request", None)
    narrowed["triggers"] = trig
    assert digest(narrowed) != digest(job_specs()["test"]), (
        "dropping the pull_request trigger did not move the test job's hash. That "
        "change would stop every pull request being gated while every job line "
        "stayed byte-identical."
    )


def test_an_executable_change_does_move_a_job_hash() -> None:
    """The other half. A hash that never moves is not a check."""
    spec = job_specs()["security"]["job"]

    def digest(node: Any) -> str:
        return hashlib.sha256(json.dumps(
            _canonicalise(node), sort_keys=True, separators=(",", ":")
        ).encode()).hexdigest()[:HASH_LENGTH]

    baseline = digest(spec)

    # The mutation is deliberately CONTENT-INDEPENDENT: append a marker to
    # whichever step happens to be the first with a `run:`. Two earlier drafts
    # were coupled to real text and both broke. Targeting "pip-audit" hit the
    # step that merely *installs* it, mutated nothing, and passed vacuously until
    # the assertion caught it. Targeting "--strict" then broke the moment a
    # negative control removed that flag from the file, and would break
    # permanently if the flag were ever retired. A mutation test that depends on
    # the code under test still saying a particular thing is a test with a
    # scheduled expiry date.
    mutated = json.loads(json.dumps(spec))
    for step in mutated["steps"]:
        if "run" in step:
            step["run"] = step["run"] + " --a-flag-that-changes-behaviour"
            break
    else:  # pragma: no cover - defensive
        raise AssertionError(f"job has no run: step to mutate: {mutated}")
    assert digest(mutated) != baseline, "changing an executable line did not move the hash"

    # `needs:` is the ordering that keeps a failed build from reaching PyPI.
    pub = yaml.safe_load(
        (REPO / ".github/workflows/publish.yml").read_text(encoding="utf-8")
    )["jobs"]["publish"]
    without_needs = {k: v for k, v in pub.items() if k != "needs"}
    assert digest(without_needs) != digest(pub), (
        "removing `needs: build` from the publish job did not move its hash. That "
        "is the safety property the build negative control relies on, and a "
        "run-lines-only hash would have been blind to it: publish has none."
    )


def test_a_step_rename_does_not_move_a_job_hash() -> None:
    """Documented as a deliberate non-trigger, so it is asserted rather than assumed."""
    data = yaml.safe_load((REPO / ".github/workflows/ci.yml").read_text(encoding="utf-8"))
    spec = data["jobs"]["security"]

    def digest(node: Any) -> str:
        return hashlib.sha256(json.dumps(
            _canonicalise(node), sort_keys=True, separators=(",", ":")
        ).encode()).hexdigest()[:HASH_LENGTH]

    renamed = json.loads(json.dumps(spec))
    renamed["steps"][-1]["name"] = "Totally different display name"
    assert digest(renamed) == digest(spec), "a step rename moved the hash"


def test_a_red_observed_claim_carries_checkable_evidence() -> None:
    """Not proof the run was red. Proof a reviewer can go and look."""
    for row in table_rows():
        if not row.get("ever observed red", "").startswith("RED OBSERVED"):
            continue
        evidence = row.get("evidence", "")
        assert "http" in evidence or "exit" in evidence, (
            f"{row.get('gate')!r} claims RED OBSERVED but its evidence cell carries "
            f"neither a run URL nor an exit code: {evidence!r}"
        )


def test_the_negative_control_rule_is_stated_beside_the_table() -> None:
    rule = _region(claude_text(), RULE_START, RULE_END)
    assert "negative control" in rule.lower(), (
        "the rule beside the gate table must state the negative-control requirement"
    )
    assert len(rule.strip()) >= 80, "the rule is too short to say anything useful"
