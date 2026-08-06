"""LICENSE, SECURITY.md and docs/ARCHITECTURE.md must still be true.

Ledger item 83. `CLAUDE.md` has had a currency test since 2026-07-30, deriving its
counts and its declared version from the artefacts they describe. Three other
public-facing documents had no test at all, and by 2026-08-06 all three had drifted:

* `LICENSE` held only the 18 line Apache 2.0 short notice, not the licence text, so
  GitHub's detection returned `spdx_id: NOASSERTION` and licence `Other`. The
  repository was not machine-detectable as open source, while `README.md` claimed the
  file contained the full text.
* `SECURITY.md` listed `0.2.x` as the supported series at version 0.4.1, three
  releases stale, directly beneath a sentence saying only the latest release was
  supported.
* `docs/ARCHITECTURE.md` documented 9 modules where 13 existed and 3 database tables
  where 7 existed.

Fixing three documents by hand closes three instances. This file closes the class,
which is the only thing that stops a fourth.

**Every check takes its subject as an argument** rather than reading the file itself,
so each one can be run against historical content. That is what makes the
fail-before demonstration possible: `tests/test_public_document_fail_before.py` runs
these same functions against `git show` of the pre-fix files and asserts they object.
A guard that has only ever been green is indistinguishable from a guard that cannot
go red.

**What this cannot see**, stated rather than implied. It checks mechanically derivable
facts: a distinctive clause and a length for the licence, a version literal for the
security policy, two counts for the architecture document. Prose in any of the three
can still go stale silently. `docs/ARCHITECTURE.md` in particular carries a pipeline
diagram and a decisions table that nothing here checks.
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
LICENSE = REPO / "LICENSE"
SECURITY = REPO / "SECURITY.md"
ARCHITECTURE = REPO / "docs" / "ARCHITECTURE.md"
PYPROJECT = REPO / "pyproject.toml"

# The clause is chosen because it appears in the licence body and NOT in the short
# notice, which is exactly the difference that made GitHub return NOASSERTION.
APACHE_BODY_CLAUSE = "TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION"
APACHE_APPENDIX_CLAUSE = "APPENDIX: How to apply the Apache License"
# The canonical text is 202 lines. The floor is set below that rather than at it so a
# trailing-newline or copyright-line difference is not a failure, while the 17 line
# short notice is nowhere near passing.
APACHE_MIN_LINES = 180

_MODULE_ROW_RE = re.compile(r"^\|\s*`([A-Za-z_][A-Za-z0-9_]*\.py)`", re.MULTILINE)
_TABLE_ROW_RE = re.compile(r"^\|\s*`([a-z_]+)`\s*\|", re.MULTILINE)
_VERSION_LITERAL_RE = re.compile(r"\b(\d+)\.(\d+)(?:\.(?:\d+|x))?\b")


def declared_version() -> str:
    with PYPROJECT.open("rb") as handle:
        return str(tomllib.load(handle)["project"]["version"])


def tracked_module_count() -> int:
    """How many Python modules the package actually has, per git."""
    out = subprocess.run(
        ["git", "ls-files", "skillwatch/*.py"],
        cwd=REPO, capture_output=True, text=True, check=True,
    )
    return len([line for line in out.stdout.splitlines() if line.strip()])


def defined_table_count() -> int:
    """How many tables the package actually creates, per the source."""
    names = set()
    for path in sorted(REPO.glob("skillwatch/*.py")):
        for match in re.finditer(
            r"CREATE TABLE IF NOT EXISTS\s+([a-z_]+)", path.read_text(encoding="utf-8")
        ):
            names.add(match.group(1))
    return len(names)


def section(text: str, heading: str) -> str:
    """The body under `heading`, up to the next heading of the same or higher level."""
    if heading not in text:
        return ""
    body = text.split(heading, 1)[1]
    return re.split(r"^#{1,2} ", body, maxsplit=1, flags=re.MULTILINE)[0]


def license_errors(text: str) -> list[str]:
    """The licence file must be the Apache 2.0 text, not the short notice."""
    errors: list[str] = []
    lines = len(text.splitlines())
    if lines < APACHE_MIN_LINES:
        errors.append(
            f"LICENSE is {lines} lines, below the {APACHE_MIN_LINES} line floor for the "
            "full Apache 2.0 text. The short notice alone makes GitHub report "
            "spdx_id NOASSERTION"
        )
    if APACHE_BODY_CLAUSE not in text:
        errors.append(f"LICENSE does not contain the clause {APACHE_BODY_CLAUSE!r}")
    if APACHE_APPENDIX_CLAUSE not in text:
        errors.append(f"LICENSE does not contain the clause {APACHE_APPENDIX_CLAUSE!r}")
    return errors


def security_errors(text: str, version: str) -> list[str]:
    """A version named in the supported-version table must be the current series.

    Naming no version at all is permitted and is the current design: the table states
    the policy instead of restating a fact that lives in pyproject.toml. What is not
    permitted is naming a version that is not the declared one, which is what `0.2.x`
    was doing at 0.4.1.
    """
    body = section(text, "## Supported versions")
    if not body.strip():
        return ["SECURITY.md has no '## Supported versions' section"]
    errors: list[str] = []
    declared_major_minor = ".".join(version.split(".")[:2])
    for line in body.splitlines():
        if not line.lstrip().startswith("|"):
            continue
        for match in _VERSION_LITERAL_RE.finditer(line):
            literal = match.group(0)
            if f"{match.group(1)}.{match.group(2)}" != declared_major_minor:
                errors.append(
                    f"SECURITY.md supported-version table names {literal!r}, which is "
                    f"not the declared version {version}. Either name the current "
                    "series or, better, name no version at all"
                )
    return errors


def architecture_errors(text: str, modules: int, tables: int) -> list[str]:
    """The architecture document's two counts must match the code."""
    errors: list[str] = []
    documented_modules = len(set(_MODULE_ROW_RE.findall(text)))
    if documented_modules != modules:
        errors.append(
            f"docs/ARCHITECTURE.md documents {documented_modules} modules; "
            f"git ls-files 'skillwatch/*.py' returns {modules}"
        )
    schema = section(text, "## SQLite Schema")
    documented_tables = len(set(_TABLE_ROW_RE.findall(schema)))
    if documented_tables != tables:
        errors.append(
            f"docs/ARCHITECTURE.md documents {documented_tables} tables; "
            f"the source defines {tables}"
        )
    return errors


# --- the live checks -----------------------------------------------------------


def test_the_licence_is_the_full_apache_text_not_the_short_notice() -> None:
    assert license_errors(LICENSE.read_text(encoding="utf-8")) == []


def test_the_security_policy_names_no_stale_version() -> None:
    assert security_errors(SECURITY.read_text(encoding="utf-8"), declared_version()) == []


def test_the_architecture_counts_match_the_code() -> None:
    assert architecture_errors(
        ARCHITECTURE.read_text(encoding="utf-8"),
        tracked_module_count(),
        defined_table_count(),
    ) == []


def test_the_counts_are_derived_not_hardcoded() -> None:
    """The derivation must reach the real artefacts, not a constant in this file."""
    assert tracked_module_count() >= 10, "git ls-files returned an implausible count"
    assert defined_table_count() >= 5, "schema scan returned an implausible count"
