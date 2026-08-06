"""CLAUDE.md's checkable facts must still be true.

CLAUDE.md briefs every session. On 2026-07-30 it said *"PyPI serves 0.3.0
(2026-07-11); `main` is 0.4.0"* when PyPI had served 0.4.1 since 2026-07-29 and
`main` was 0.4.1. Both halves were false, and nothing anywhere would have noticed.
The same sentence had already gone stale once before (ledger item 12: "10 modules,
v0.2.0, Pages disabled").

This is the identical class the figure check closes for published proportions:
a number written once into prose, true on the day it was written, with no
relationship to the thing it describes. `scripts/figure_rules.py` fixed it for
`k/n (p%)` on public surfaces by deriving the allowed set from the harness rather
than maintaining a second copy. This file does the same for CLAUDE.md's counts and
version, deriving each from the artefact it claims to describe.

**The split is deliberate, and mirrors the gate/report split already documented in
CLAUDE.md.** Two claims of different kinds cannot be checked the same way:

* *"this repository declares X"* is answerable offline from `pyproject.toml`, so it
  is checked **here**, in the blocking suite, with no network.
* *"PyPI serves X"* can only be answered by asking PyPI, and a release is the only
  thing that can make it true. Checking it here would make the suite fail whenever
  the repository is ahead of the published version, which is the normal state
  between a correction and a release. It therefore lives in
  `scripts/check_published_claims.py` (THE REPORT, non-blocking), for exactly the
  reason `check_release_claims.py` and `check_published_claims.py` are separate.

**What this cannot see.** It checks the facts that are mechanically derivable:
version and file counts. Prose claims in CLAUDE.md ("Pages is live", the AST05
positioning, the base-rate reasoning) are not checkable this way and are not
covered. Stated rather than implied, per this repository's own rule.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

if sys.version_info >= (3, 11):
    import tomllib
else:  # pragma: no cover - exercised only on 3.10
    import tomli as tomllib

REPO = Path(__file__).resolve().parents[1]
CLAUDE = REPO / "CLAUDE.md"
PYPROJECT = REPO / "pyproject.toml"

NUMBER_WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7,
    "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13,
    "fourteen": 14, "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18,
    "nineteen": 19, "twenty": 20,
}


def claude_text() -> str:
    return CLAUDE.read_text(encoding="utf-8")


def declared_version() -> str:
    with PYPROJECT.open("rb") as handle:
        return str(tomllib.load(handle)["project"]["version"])


def tracked(pattern: str) -> list[str]:
    out = subprocess.run(
        ["git", "ls-files", pattern], cwd=REPO, capture_output=True, text=True, check=True
    )
    return sorted(p for p in out.stdout.split() if p)


def _word_to_int(word: str) -> int:
    return NUMBER_WORDS[word.lower()]


# --- guarding the guard -------------------------------------------------------


def test_the_pyproject_version_is_readable() -> None:
    """If this returned nothing, the version assertion below would be vacuous."""
    assert re.fullmatch(r"\d+\.\d+\.\d+", declared_version()), declared_version()


def test_the_number_word_map_covers_the_counts_in_use() -> None:
    for count in (len(tracked("skillwatch/*.py")), len(tracked("scripts/*.py"))):
        assert count in NUMBER_WORDS.values(), (
            f"count {count} has no word in NUMBER_WORDS; the claim below would be "
            f"unparseable and the check would pass without checking anything"
        )


# --- the claims ---------------------------------------------------------------


def test_claude_md_states_the_version_this_repository_declares() -> None:
    """The offline half. The networked half is in check_published_claims.py."""
    match = re.search(
        r"this repository declares (\d+\.\d+\.\d+) in `pyproject\.toml`", claude_text()
    )
    assert match, (
        "CLAUDE.md must state the version this repository declares, in the exact "
        "form 'this repository declares X.Y.Z in `pyproject.toml`', so it can be "
        "checked rather than trusted. It previously claimed a version for `main` "
        "and was wrong about it for a day."
    )
    assert match.group(1) == declared_version(), (
        f"CLAUDE.md says this repository declares {match.group(1)}; pyproject.toml "
        f"says {declared_version()}. Correct the sentence, not this test."
    )


def test_claude_md_does_not_claim_a_pypi_version_without_a_date() -> None:
    """A bare version with no date cannot be aged by a reader."""
    match = re.search(r"PyPI serves (\d+\.\d+\.\d+) \((\d{4}-\d{2}-\d{2})\)", claude_text())
    assert match, (
        "CLAUDE.md's PyPI claim must carry both a version and the date it was "
        "checked, as 'PyPI serves X.Y.Z (YYYY-MM-DD)'. Its currency is verified "
        "against the live index by scripts/check_published_claims.py, which is a "
        "report rather than a gate because only a release can make it true."
    )


def test_claude_md_counts_the_skillwatch_modules_correctly() -> None:
    modules = tracked("skillwatch/*.py")
    match = re.search(r"(\w+) Python modules under `skillwatch/`", claude_text())
    assert match, "CLAUDE.md must state how many modules `skillwatch/` has"
    assert _word_to_int(match.group(1)) == len(modules), (
        f"CLAUDE.md claims {match.group(1)} modules under skillwatch/; "
        f"git ls-files finds {len(modules)}: {modules}"
    )


def test_claude_md_counts_and_names_the_tracked_scripts_correctly() -> None:
    scripts = tracked("scripts/*.py")
    match = re.search(r"(\w+) tracked scripts under `scripts/`", claude_text())
    assert match, "CLAUDE.md must state how many tracked scripts `scripts/` has"
    assert _word_to_int(match.group(1)) == len(scripts), (
        f"CLAUDE.md claims {match.group(1)} tracked scripts; git ls-files finds "
        f"{len(scripts)}: {scripts}. This claim read 'Two' while there were six."
    )
    text = claude_text()
    missing = [p for p in scripts if Path(p).name not in text]
    assert not missing, f"tracked scripts not named anywhere in CLAUDE.md: {missing}"


def test_claude_md_counts_and_names_the_tracked_analysis_modules_correctly() -> None:
    modules = tracked("analysis/*.py")
    match = re.search(r"(\w+) tracked modules under `analysis/`", claude_text())
    assert match, "CLAUDE.md must state how many tracked modules `analysis/` has"
    assert _word_to_int(match.group(1)) == len(modules), (
        f"CLAUDE.md claims {match.group(1)} tracked analysis modules; git ls-files "
        f"finds {len(modules)}: {modules}"
    )
    text = claude_text()
    missing = [p for p in modules if Path(p).name not in text]
    assert not missing, f"tracked analysis modules not named in CLAUDE.md: {missing}"
