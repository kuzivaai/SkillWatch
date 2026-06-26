"""Tests for diff generation and hash comparison."""

from skillwatch.differ import content_changed, generate_diff, diff_stats


class TestContentChanged:
    def test_same_hashes(self):
        assert not content_changed("abc123", "abc123")

    def test_different_hashes(self):
        assert content_changed("abc123", "def456")

    def test_empty_hashes(self):
        assert not content_changed("", "")


class TestGenerateDiff:
    def test_shows_added_lines(self):
        old = "line 1\nline 2\n"
        new = "line 1\nline 2\nline 3\n"
        diff = generate_diff(old, new)
        assert "+line 3" in diff

    def test_shows_removed_lines(self):
        old = "line 1\nline 2\nline 3\n"
        new = "line 1\nline 2\n"
        diff = generate_diff(old, new)
        assert "-line 3" in diff

    def test_shows_url_in_header(self):
        diff = generate_diff("old", "new", url="https://example.com")
        assert "example.com" in diff

    def test_identical_content_empty_diff(self):
        diff = generate_diff("same\n", "same\n")
        assert diff == ""

    def test_empty_to_content(self):
        diff = generate_diff("", "new content\n")
        assert "+new content" in diff


class TestDiffStats:
    def test_counts_additions_and_removals(self):
        diff = "--- old\n+++ new\n-removed\n+added1\n+added2\n context\n"
        stats = diff_stats(diff)
        assert stats["added"] == 2
        assert stats["removed"] == 1

    def test_empty_diff(self):
        stats = diff_stats("")
        assert stats["added"] == 0
        assert stats["removed"] == 0

    def test_ignores_header_lines(self):
        diff = "--- a/file\n+++ b/file\n+real addition\n"
        stats = diff_stats(diff)
        assert stats["added"] == 1
        assert stats["removed"] == 0
