"""Tests for SQLite storage."""

import tempfile
from pathlib import Path

import pytest

from skillwatch.store import Store


@pytest.fixture
def store():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        s = Store(db_path=db_path)
        yield s
        s.close()


class TestURLStorage:
    def test_add_url(self, store):
        url_id = store.add_url("https://example.com/docs", "manual")
        assert url_id > 0

    def test_add_duplicate_url(self, store):
        id1 = store.add_url("https://example.com/docs", "manual")
        id2 = store.add_url("https://example.com/docs", "manual")
        assert id1 == id2

    def test_get_urls(self, store):
        store.add_url("https://a.com", "manual")
        store.add_url("https://b.com", "skill_md", "/path/to/skill.md")
        urls = store.get_urls()
        assert len(urls) == 2
        assert urls[0]["url"] == "https://a.com"
        assert urls[1]["source_path"] == "/path/to/skill.md"

    def test_remove_url(self, store):
        store.add_url("https://example.com", "manual")
        assert store.remove_url("https://example.com")
        assert store.url_count() == 0

    def test_remove_nonexistent(self, store):
        assert not store.remove_url("https://nonexistent.com")

    def test_url_count(self, store):
        assert store.url_count() == 0
        store.add_url("https://a.com", "manual")
        store.add_url("https://b.com", "manual")
        assert store.url_count() == 2


class TestSnapshots:
    def test_add_and_get_snapshot(self, store):
        url_id = store.add_url("https://example.com", "manual")
        snap_id = store.add_snapshot(url_id, "abc123", "Hello world", status_code=200)
        assert snap_id > 0

        latest = store.get_latest_snapshot(url_id)
        assert latest["content_hash"] == "abc123"
        assert latest["content_text"] == "Hello world"
        assert latest["status_code"] == 200

    def test_latest_snapshot_is_most_recent(self, store):
        url_id = store.add_url("https://example.com", "manual")
        store.add_snapshot(url_id, "hash1", "Old content")
        store.add_snapshot(url_id, "hash2", "New content")

        latest = store.get_latest_snapshot(url_id)
        assert latest["content_hash"] == "hash2"

    def test_snapshot_history(self, store):
        url_id = store.add_url("https://example.com", "manual")
        store.add_snapshot(url_id, "h1", "v1")
        store.add_snapshot(url_id, "h2", "v2")
        store.add_snapshot(url_id, "h3", "v3")

        history = store.get_snapshot_history(url_id, limit=2)
        assert len(history) == 2
        assert history[0]["content_hash"] == "h3"  # most recent first

    def test_no_snapshot(self, store):
        url_id = store.add_url("https://example.com", "manual")
        assert store.get_latest_snapshot(url_id) is None

    def test_error_snapshot(self, store):
        url_id = store.add_url("https://example.com", "manual")
        store.add_snapshot(url_id, "", None, error="Timeout")
        latest = store.get_latest_snapshot(url_id)
        assert latest["error"] == "Timeout"


class TestAlerts:
    def test_add_and_get_alert(self, store):
        url_id = store.add_url("https://example.com", "manual")
        snap1 = store.add_snapshot(url_id, "h1", "old")
        snap2 = store.add_snapshot(url_id, "h2", "new")

        alert_id = store.add_alert(url_id, snap1, snap2, "diff text", ["new_script_tag"], "critical")
        assert alert_id > 0

        alert = store.get_alert(alert_id)
        assert alert["severity"] == "critical"
        assert alert["flags"] == ["new_script_tag"]
        assert alert["reviewed"] == 0

    def test_mark_reviewed(self, store):
        url_id = store.add_url("https://example.com", "manual")
        snap1 = store.add_snapshot(url_id, "h1", "old")
        snap2 = store.add_snapshot(url_id, "h2", "new")
        alert_id = store.add_alert(url_id, snap1, snap2, "diff", [], "info")

        assert store.mark_alert_reviewed(alert_id)
        alert = store.get_alert(alert_id)
        assert alert["reviewed"] == 1

    def test_unreviewed_filter(self, store):
        url_id = store.add_url("https://example.com", "manual")
        snap1 = store.add_snapshot(url_id, "h1", "old")
        snap2 = store.add_snapshot(url_id, "h2", "new")

        a1 = store.add_alert(url_id, snap1, snap2, "diff1", [], "info")
        a2 = store.add_alert(url_id, snap1, snap2, "diff2", [], "warning")
        store.mark_alert_reviewed(a1)

        unreviewed = store.get_alerts(unreviewed_only=True)
        assert len(unreviewed) == 1
        assert unreviewed[0]["id"] == a2

    def test_remove_url_cascades(self, store):
        url_id = store.add_url("https://example.com", "manual")
        snap1 = store.add_snapshot(url_id, "h1", "old")
        snap2 = store.add_snapshot(url_id, "h2", "new")
        store.add_alert(url_id, snap1, snap2, "diff", [], "info")

        store.remove_url("https://example.com")
        assert store.url_count() == 0
        assert store.get_alerts() == []
