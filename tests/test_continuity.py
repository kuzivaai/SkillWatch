"""Continuity evidence must remain durable and internally current."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
LEDGER = REPO / "OPEN-ITEMS.md"


def _ledger_item(number: int) -> str:
    text = LEDGER.read_text(encoding="utf-8")
    match = re.search(rf"^\| {number} \|.*$", text, re.MULTILINE)
    assert match, f"OPEN-ITEMS.md has no row for item {number}"
    return match.group(0)


def test_dated_session_logs_are_not_ignored() -> None:
    """An ignored evidence log disappears on the next clone or machine."""
    probe = "analysis/session-log-2099-12-31.md"
    result = subprocess.run(
        ["git", "check-ignore", "--no-index", "--quiet", probe],
        cwd=REPO,
        check=False,
    )
    assert result.returncode == 1, (
        f"{probe} is ignored; a session cutoff would strand its evidence on one "
        "machine. Re-include dated session logs in .gitignore."
    )


def test_item_22_names_the_later_strict_demonstration() -> None:
    """A closed historical row must not contradict the later class closure."""
    item_22 = _ledger_item(22)
    assert "Superseded by item 60" in item_22, (
        "item 22 retains its earlier 'no case was found' conclusion without "
        "pointing to item 60, which later demonstrated --strict changing the outcome"
    )
    assert "no case was found in which `--strict` changed the outcome" not in item_22


def test_item_60_links_back_to_the_superseded_record() -> None:
    """The correcting row must identify the historical row it supersedes."""
    assert "item 22" in _ledger_item(60).lower()
