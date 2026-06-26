"""Hash comparison and diff generation."""

import difflib


def content_changed(old_hash: str, new_hash: str) -> bool:
    """Check if content has changed based on hash comparison."""
    return old_hash != new_hash


def generate_diff(old_text: str, new_text: str, url: str = "") -> str:
    """Generate a unified diff between old and new content."""
    old_lines = old_text.splitlines(keepends=True)
    new_lines = new_text.splitlines(keepends=True)

    diff = difflib.unified_diff(
        old_lines,
        new_lines,
        fromfile=f"previous: {url}" if url else "previous",
        tofile=f"current: {url}" if url else "current",
        lineterm="",
    )
    return "\n".join(diff)


