"""Tests for SQLite storage."""

import tempfile
from pathlib import Path

import pytest

from skillwatch.store import Store


@pytest.fixture
def store():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        with Store(db_path=db_path) as s:
            yield s


class TestURLStorage:
    def test_add_url(self, store):
        url_id, is_new = store.add_url("https://example.com/docs", "manual")
        assert url_id > 0
        assert is_new is True

    def test_add_duplicate_url(self, store):
        id1, new1 = store.add_url("https://example.com/docs", "manual")
        id2, new2 = store.add_url("https://example.com/docs", "manual")
        assert id1 == id2
        assert new1 is True
        assert new2 is False

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
        url_id, _ = store.add_url("https://example.com", "manual")
        snap_id = store.add_snapshot(url_id, "abc123", "Hello world", status_code=200)
        assert snap_id > 0

        latest = store.get_latest_snapshot(url_id)
        assert latest["content_hash"] == "abc123"
        assert latest["content_text"] == "Hello world"
        assert latest["status_code"] == 200

    def test_stores_raw_html(self, store):
        url_id, _ = store.add_url("https://example.com", "manual")
        html = "<html><body>Hello</body></html>"
        store.add_snapshot(url_id, "abc", "Hello", raw_html=html, raw_html_hash="xyz")
        latest = store.get_latest_snapshot(url_id)
        assert latest["raw_html"] == html
        assert latest["raw_html_hash"] == "xyz"

    def test_latest_snapshot_is_most_recent(self, store):
        url_id, _ = store.add_url("https://example.com", "manual")
        store.add_snapshot(url_id, "hash1", "Old content")
        store.add_snapshot(url_id, "hash2", "New content")

        latest = store.get_latest_snapshot(url_id)
        assert latest["content_hash"] == "hash2"

    def test_snapshot_history(self, store):
        url_id, _ = store.add_url("https://example.com", "manual")
        store.add_snapshot(url_id, "h1", "v1")
        store.add_snapshot(url_id, "h2", "v2")
        store.add_snapshot(url_id, "h3", "v3")

        history = store.get_snapshot_history(url_id, limit=2)
        assert len(history) == 2
        assert history[0]["content_hash"] == "h3"  # most recent first

    def test_no_snapshot(self, store):
        url_id, _ = store.add_url("https://example.com", "manual")
        assert store.get_latest_snapshot(url_id) is None

    def test_get_latest_good_snapshot_skips_errors(self, store):
        url_id, _ = store.add_url("https://example.com", "manual")
        store.add_snapshot(url_id, "good_hash", "Good content")
        store.add_snapshot(url_id, "", None, error="Timeout")

        latest = store.get_latest_snapshot(url_id)
        assert latest["error"] == "Timeout"  # most recent is error

        good = store.get_latest_good_snapshot(url_id)
        assert good["content_hash"] == "good_hash"  # skips error, returns last good

    def test_error_snapshot(self, store):
        url_id, _ = store.add_url("https://example.com", "manual")
        store.add_snapshot(url_id, "", None, error="Timeout")
        latest = store.get_latest_snapshot(url_id)
        assert latest["error"] == "Timeout"


class TestAlerts:
    def test_add_and_get_alert(self, store):
        url_id, _ = store.add_url("https://example.com", "manual")
        snap1 = store.add_snapshot(url_id, "h1", "old")
        snap2 = store.add_snapshot(url_id, "h2", "new")

        alert_id = store.add_alert(url_id, snap1, snap2, "diff text", ["new_script_tag"], "critical")
        assert alert_id > 0

        alert = store.get_alert(alert_id)
        assert alert["severity"] == "critical"
        assert alert["flags"] == ["new_script_tag"]
        assert alert["reviewed"] == 0

    def test_mark_reviewed(self, store):
        url_id, _ = store.add_url("https://example.com", "manual")
        snap1 = store.add_snapshot(url_id, "h1", "old")
        snap2 = store.add_snapshot(url_id, "h2", "new")
        alert_id = store.add_alert(url_id, snap1, snap2, "diff", [], "info")

        assert store.mark_alert_reviewed(alert_id)
        alert = store.get_alert(alert_id)
        assert alert["reviewed"] == 1

    def test_unreviewed_filter(self, store):
        url_id, _ = store.add_url("https://example.com", "manual")
        snap1 = store.add_snapshot(url_id, "h1", "old")
        snap2 = store.add_snapshot(url_id, "h2", "new")

        a1 = store.add_alert(url_id, snap1, snap2, "diff1", [], "info")
        a2 = store.add_alert(url_id, snap1, snap2, "diff2", [], "warning")
        store.mark_alert_reviewed(a1)

        unreviewed = store.get_alerts(unreviewed_only=True)
        assert len(unreviewed) == 1
        assert unreviewed[0]["id"] == a2

    def test_get_alerts_filtered_by_url_id(self, store):
        """get_alerts(url_id=X) returns only that URL's alerts."""
        id_a, _ = store.add_url("https://a.com", "manual")
        id_b, _ = store.add_url("https://b.com", "manual")
        sa1 = store.add_snapshot(id_a, "a1", "old")
        sa2 = store.add_snapshot(id_a, "a2", "new")
        sb1 = store.add_snapshot(id_b, "b1", "old")
        sb2 = store.add_snapshot(id_b, "b2", "new")
        alert_a = store.add_alert(id_a, sa1, sa2, "diff-a", ["new_domains"], "warning")
        store.add_alert(id_b, sb1, sb2, "diff-b", [], "info")

        a_only = store.get_alerts(url_id=id_a)
        assert len(a_only) == 1
        assert a_only[0]["id"] == alert_a
        assert a_only[0]["url"] == "https://a.com"
        # Without the filter, both alerts are returned
        assert len(store.get_alerts()) == 2

    def test_remove_url_cascades(self, store):
        url_id, _ = store.add_url("https://example.com", "manual")
        snap1 = store.add_snapshot(url_id, "h1", "old")
        snap2 = store.add_snapshot(url_id, "h2", "new")
        store.add_alert(url_id, snap1, snap2, "diff", [], "info")

        store.remove_url("https://example.com")
        assert store.url_count() == 0
        assert store.get_alerts() == []


class TestStatusMethods:
    def test_last_scan_time_empty(self, store):
        """last_scan_time returns None when no snapshots exist."""
        assert store.last_scan_time() is None

    def test_last_scan_time_after_snapshot(self, store):
        """last_scan_time returns a timestamp string after a snapshot is added."""
        url_id, _ = store.add_url("https://example.com", "manual")
        store.add_snapshot(url_id, "abc", "content")
        ts = store.last_scan_time()
        assert ts is not None
        assert "20" in ts  # starts with year 20xx

    def test_pending_alert_count_zero(self, store):
        """pending_alert_count is 0 with no alerts."""
        assert store.pending_alert_count() == 0

    def test_pending_alert_count(self, store):
        """pending_alert_count counts unreviewed alerts only."""
        url_id, _ = store.add_url("https://example.com", "manual")
        s1 = store.add_snapshot(url_id, "h1", "old")
        s2 = store.add_snapshot(url_id, "h2", "new")
        a1 = store.add_alert(url_id, s1, s2, "diff", [], "info")
        store.add_alert(url_id, s1, s2, "diff2", [], "warning")

        assert store.pending_alert_count() == 2
        store.mark_alert_reviewed(a1)
        assert store.pending_alert_count() == 1


class TestContextManager:
    def test_store_as_context_manager(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            with Store(db_path=db_path) as s:
                s.add_url("https://example.com", "manual")
                assert s.url_count() == 1
            # Connection is closed — accessing it should fail or be safe


class TestSources:
    def test_record_and_get_source(self, store):
        store.record_source("/path/SKILL.md", "hash1", ["https://a.com", "https://b.com"])
        sources = store.get_sources()
        assert len(sources) == 1
        assert sources[0]["path"] == "/path/SKILL.md"
        assert sources[0]["content_hash"] == "hash1"
        assert sources[0]["urls"] == ["https://a.com", "https://b.com"]

    def test_record_source_upserts_not_duplicates(self, store):
        store.record_source("/path/SKILL.md", "hash1", ["https://a.com"])
        store.record_source("/path/SKILL.md", "hash2", ["https://a.com", "https://c.com"])
        sources = store.get_sources()
        assert len(sources) == 1  # updated in place, not duplicated
        assert sources[0]["content_hash"] == "hash2"
        assert sources[0]["urls"] == ["https://a.com", "https://c.com"]

    def test_get_sources_empty(self, store):
        assert store.get_sources() == []
