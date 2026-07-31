"""Continuity evidence must remain durable and internally current."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
LEDGER = REPO / "OPEN-ITEMS.md"


def _ledger_item(number: int) -> str:
    text = LEDGER.read_text(encoding="utf-8")
    matches = re.findall(rf"^\| {number} \|.*$", text, re.MULTILINE)
    rows = [row for row in matches if row.count("|") >= 6]
    assert len(rows) == 1, f"OPEN-ITEMS.md must have one ledger row for item {number}"
    return str(rows[0])


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


def test_existing_session_logs_are_tracked() -> None:
    """Every existing permanent evidence log must survive a fresh clone."""
    logs = sorted((REPO / "analysis").glob("session-log-*.md"))
    assert logs, "no permanent session evidence logs exist"
    relative_logs = [str(path.relative_to(REPO)) for path in logs]
    result = subprocess.run(
        ["git", "ls-files", "--error-unmatch", *relative_logs],
        cwd=REPO,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        "existing session logs are not tracked and will disappear on a fresh clone: "
        f"{result.stderr.strip()}"
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


def test_supersession_index_records_item_22_to_60() -> None:
    """Machine-readable lineage prevents two closed rows remaining co-current."""
    text = LEDGER.read_text(encoding="utf-8")
    assert "## Supersession index" in text
    assert re.search(r"^\| 22 \| 60 \|", text, re.MULTILINE)
