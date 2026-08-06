"""The item 83 guards must refuse the defects they were written for.

This repository's rule: a gate that has never been observed red is indistinguishable
from a gate that cannot go red. `tests/test_public_document_currency.py` is green, and
green alone proves nothing about whether it would object to anything.

So each check is run here against the actual pre-fix content, fetched from git at a
pinned commit, and asserted to FAIL. The same checks are asserted to PASS against the
corrected content in the currency module. Fail-before and pass-after, both mechanical,
both in the blocking suite.

**Why a pinned SHA rather than `HEAD~1` or a fixture.** A relative reference moves as
commits land and would silently start comparing the wrong thing. A copied fixture is a
second copy of the defect, free to drift from what the defect actually was. `git show`
at a fixed commit is the artefact itself, and 99decb0 is the last commit before any of
the three corrections.
"""

from __future__ import annotations

import subprocess

import pytest

from tests.test_public_document_currency import (
    REPO,
    architecture_errors,
    license_errors,
    security_errors,
)

# The commit immediately before the 2026-08-06 corrections. All three documents are in
# their defective state here.
PRE_FIX = "99decb0"


def show(path: str) -> str:
    result = subprocess.run(
        ["git", "show", f"{PRE_FIX}:{path}"],
        cwd=REPO, capture_output=True, text=True, check=True,
    )
    return result.stdout


@pytest.fixture(scope="module")
def old_license() -> str:
    return show("LICENSE")


@pytest.fixture(scope="module")
def old_security() -> str:
    return show("SECURITY.md")


@pytest.fixture(scope="module")
def old_architecture() -> str:
    return show("docs/ARCHITECTURE.md")


def test_the_pre_fix_licence_really_was_the_short_notice(old_license: str) -> None:
    """Guards the fixture itself: if this stops being the defect, the control is void."""
    assert len(old_license.splitlines()) < 30
    assert "TERMS AND CONDITIONS" not in old_license


def test_the_licence_guard_fails_against_the_short_notice(old_license: str) -> None:
    errors = license_errors(old_license)
    assert errors, "the licence guard passed the 17 line short notice; it cannot go red"
    joined = " ".join(errors)
    assert "line floor" in joined
    assert "TERMS AND CONDITIONS" in joined


def test_the_security_guard_fails_against_the_stale_series(old_security: str) -> None:
    errors = security_errors(old_security, "0.4.1")
    assert errors, "the security guard passed a table naming 0.2.x at version 0.4.1"
    assert "0.2.x" in " ".join(errors)


def test_the_security_guard_would_also_have_passed_a_correct_literal() -> None:
    """The rule is not 'no digits allowed'. Naming the CURRENT series is legitimate."""
    correct = "## Supported versions\n\n| Version | Supported |\n| 0.4.x | Yes |\n"
    assert security_errors(correct, "0.4.1") == []


def test_the_architecture_guard_fails_against_the_stale_counts(
    old_architecture: str,
) -> None:
    errors = architecture_errors(old_architecture, modules=13, tables=7)
    assert errors, "the architecture guard passed a document listing 9 modules and 3 tables"
    joined = " ".join(errors)
    assert "documents 9 modules" in joined
    assert "returns 13" in joined
    # The old schema section was a raw SQL block, so it carried no table ROWS at all.
    assert "documents 0 tables" in joined or "documents 3 tables" in joined
