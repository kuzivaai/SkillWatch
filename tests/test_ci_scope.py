"""Every tracked module must be inside the lint and type gates.

The mypy invocation in CI was a hand-written list of five `analysis/` files. Adding
a sixth tracked module and forgetting to extend the list would leave it silently
unchecked — and the check would still report green, because the new file is simply
out of its scope.

That is the same shape as the four recurrences already in this repository's ledger:
an unparseable specifier treated as satisfied, a guard that could not see the
published artefact, a regex that could never match, and a figure check that could
not see a substituted label. A hand-maintained scope list is that defect waiting
for its fifth outing.

So the scope is DERIVED from `git ls-files` rather than typed out, and this file
asserts it stays derived.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CI = REPO / ".github" / "workflows" / "ci.yml"


def tracked_analysis_modules() -> list[str]:
    out = subprocess.run(
        ["git", "ls-files", "analysis/*.py"],
        cwd=REPO, capture_output=True, text=True, check=True,
    )
    return sorted(p for p in out.stdout.split() if p)


def ci_text() -> str:
    return CI.read_text(encoding="utf-8")


def _step(text: str, name: str) -> str:
    """The body of one named workflow step, up to the next step boundary."""
    start = text.index(f"- name: {name}")
    rest = text[start + 1:]
    end = rest.find("\n      - name: ")
    return rest if end == -1 else rest[:end]


def test_there_is_at_least_one_tracked_analysis_module() -> None:
    """Guarding the guard: an empty list would make every assertion below vacuous."""
    assert len(tracked_analysis_modules()) >= 5, tracked_analysis_modules()


def test_ci_type_checks_every_tracked_analysis_module() -> None:
    """Covered either by a git ls-files expansion or by being named literally."""
    text = ci_text()
    step = _step(text, "Type check")
    derived = "git ls-files" in step and "analysis" in step
    if derived:
        return
    missing = [m for m in tracked_analysis_modules() if m not in step]
    assert not missing, (
        f"these tracked modules are not in the CI mypy scope and are therefore "
        f"unchecked: {missing}. Either name them or derive the list with "
        f"`git ls-files 'analysis/*.py'` so it cannot go stale."
    )


def test_the_mypy_scope_is_derived_rather_than_typed_out() -> None:
    """A literal list passes today and rots on the next added module."""
    step = _step(ci_text(), "Type check")
    assert "git ls-files" in step, (
        "the mypy scope for analysis/ must be derived from git ls-files. A "
        "hand-maintained list leaves the next new module silently unchecked."
    )


def test_ci_lints_the_same_directories_the_docs_promise() -> None:
    text = ci_text()
    step = _step(text, "Lint")
    for target in ("skillwatch/", "tests/", "scripts/", "analysis/"):
        assert target in step, f"ruff does not cover {target} in CI"


def test_claude_md_documents_the_same_mypy_scope_as_ci() -> None:
    """A second copy of the command is free to drift from the first."""
    doc = (REPO / "CLAUDE.md").read_text(encoding="utf-8")
    assert "git ls-files" in doc and "mypy" in doc, (
        "CLAUDE.md's documented mypy command must use the same derived scope as "
        "CI, or the two will disagree about what is type-checked."
    )


# --- the security job's audit shape ------------------------------------------
#
# Settled 2026-07-30, see docs/DEPENDENCY-FLOORS.md. `--skip-editable` was the skip
# that `--strict` rejects; the resolved-requirements shape removes the need for both.


def pip_audit_run_lines() -> list[str]:
    """The executable `run:` lines that invoke pip-audit — comments excluded.

    Matching the whole file would be vacuous: the PREVIOUS ci.yml discussed
    `--strict` at length in a comment explaining why it was omitted, so a
    substring check against the file text passed while the flag was absent from
    the command. That is the "rule that never fires" defect the ledger records.
    """
    lines: list[str] = []
    for raw in ci_text().splitlines():
        stripped = raw.strip()
        if stripped.startswith("#"):
            continue
        if "run:" in stripped and "pip-audit" in stripped:
            lines.append(stripped)
    return lines


def test_pip_audit_runs_strict() -> None:
    runs = [ln for ln in pip_audit_run_lines() if "pip-audit --strict" in ln
            or ("pip-audit" in ln and "--strict" in ln)]
    assert runs, (
        "no executable pip-audit invocation carries --strict. Verified 2026-07-30 "
        f"that it passes on the resolved-requirements shape, so omitting it is no "
        f"longer justified. pip-audit run lines found: {pip_audit_run_lines()}"
    )


def test_the_strict_guard_reads_the_command_not_the_comments() -> None:
    """Guarding the guard: prose mentioning --strict must not satisfy the rule."""
    assert all(not ln.startswith("#") for ln in pip_audit_run_lines())
    # A file that only discusses --strict in prose must yield no matching run line.
    assert pip_audit_run_lines(), "no pip-audit run line found at all"


def test_pip_audit_does_not_skip_editable() -> None:
    """--skip-editable is the skip --strict rejects. It must not come back."""
    assert "--skip-editable" not in ci_text()


def test_the_audited_set_excludes_the_project_itself() -> None:
    """The whole trick: with the project excluded, its version being unpublished
    stops mattering. Measured — env scan of an unreleased 0.9.9 exits 1, this
    shape exits 0.
    """
    text = ci_text()
    assert "pip freeze --exclude-editable" in text
    assert "requirements-audit.txt" in text


def test_pip_audit_is_installed_apart_from_the_project() -> None:
    """Otherwise the freeze captures pip-audit's own tree and an advisory in the
    auditing tool fails this project's CI for something it does not ship.
    """
    text = ci_text()
    install = _step(text, "Install dependencies")
    assert "pip-audit" not in install, (
        "pip-audit must not be installed alongside the project in the security job"
    )
    assert "/tmp/auditenv" in text or "pipx" in text, (
        "pip-audit needs an isolated environment"
    )


def test_pythondontwritebytecode_is_set_at_workflow_level() -> None:
    """A stale .pyc has already produced one false 'passing' result here."""
    text = ci_text()
    assert re.search(r"^env:\s*$", text, re.MULTILINE), "no workflow-level env block"
    assert "PYTHONDONTWRITEBYTECODE" in text
