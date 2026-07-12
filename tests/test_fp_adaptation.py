"""Tests for local false-positive adaptation (dismiss/confirm -> demotion).

All offline: SQLite temp DB + the CLI's own --db flag. No network.
"""
import pytest

from skillwatch.cli import main
from skillwatch.detector import Flag
from skillwatch.formatter import format_alert_detail, format_scan_result
from skillwatch.store import Store


def _store(tmp_path):
    return Store(db_path=tmp_path / "t.db")


def _seed_alert(db):
    """Create one URL + one alert (id 1) with two flags. Returns url_id."""
    s = Store(db_path=db)
    url_id, _ = s.add_url("https://x.test", "manual")
    snap = s.add_snapshot(url_id, "h1", "content")
    s.add_alert(
        url_id, prev_snapshot_id=snap, new_snapshot_id=snap,
        diff_text="- old\n+ new curl evil", severity="critical",
        flags=["new_exec_command", "new_domains"],
    )
    s.close()
    return url_id


# --- store layer --------------------------------------------------------------

def test_demoted_after_two_dismissals(tmp_path):
    s = _store(tmp_path)
    uid, _ = s.add_url("https://x.test", "manual")
    s.record_flag_feedback(uid, "new_exec_command", "dismissed")
    assert s.demoted_flags(uid) == set()  # one dismissal is below threshold
    s.record_flag_feedback(uid, "new_exec_command", "dismissed")
    assert s.demoted_flags(uid) == {"new_exec_command"}
    s.close()


def test_confirm_cancels_demotion(tmp_path):
    s = _store(tmp_path)
    uid, _ = s.add_url("https://x.test", "manual")
    s.record_flag_feedback(uid, "new_domains", "dismissed")
    s.record_flag_feedback(uid, "new_domains", "dismissed")
    s.record_flag_feedback(uid, "new_domains", "confirmed")
    assert s.demoted_flags(uid) == set()
    s.close()


def test_reset_clears_feedback(tmp_path):
    s = _store(tmp_path)
    uid, _ = s.add_url("https://x.test", "manual")
    s.record_flag_feedback(uid, "new_domains", "dismissed")
    s.record_flag_feedback(uid, "new_domains", "dismissed")
    assert s.demoted_flags(uid) == {"new_domains"}
    assert s.reset_flag_feedback() == 2
    assert s.demoted_flags(uid) == set()
    s.close()


def test_list_feedback_groups(tmp_path):
    s = _store(tmp_path)
    uid, _ = s.add_url("https://x.test", "manual")
    s.record_flag_feedback(uid, "new_domains", "dismissed")
    s.record_flag_feedback(uid, "new_domains", "dismissed")
    rows = s.list_flag_feedback()
    assert len(rows) == 1
    assert rows[0]["flag_code"] == "new_domains"
    assert rows[0]["decision"] == "dismissed"
    assert rows[0]["n"] == 2
    s.close()


def test_remove_url_clears_feedback(tmp_path):
    s = _store(tmp_path)
    uid, _ = s.add_url("https://x.test", "manual")
    s.record_flag_feedback(uid, "new_domains", "dismissed")
    s.remove_url("https://x.test")
    assert s.list_flag_feedback() == []
    s.close()


def test_record_rejects_bad_decision(tmp_path):
    s = _store(tmp_path)
    uid, _ = s.add_url("https://x.test", "manual")
    with pytest.raises(ValueError):
        s.record_flag_feedback(uid, "new_domains", "bogus")
    s.close()


# --- formatter layer ----------------------------------------------------------

def test_format_alert_detail_annotates_only_demoted():
    alert = {
        "id": 1, "url": "https://x.test", "detected_at": "t", "severity": "critical",
        "reviewed": 0, "flags": ["new_exec_command", "new_domains"], "diff_text": "",
    }
    out = format_alert_detail(alert, demoted_flags={"new_exec_command"})
    assert out.count("previously dismissed") == 1


def test_format_scan_result_annotates_demoted():
    flags = [Flag("new_exec_command", "critical", "x"), Flag("new_domains", "warning", "y")]
    out = format_scan_result("https://x.test", True, flags, demoted_flags={"new_domains"})
    assert out.count("previously dismissed") == 1
    assert "previously dismissed" not in format_scan_result("https://x.test", True, flags)


# --- CLI layer (production dispatch) ------------------------------------------

def test_cli_dismiss_records_feedback(tmp_path, capsys):
    db = tmp_path / "t.db"
    _seed_alert(db)
    assert main(["--db", str(db), "alert", "1", "--dismiss"]) == 0
    assert "dismissed" in capsys.readouterr().out.lower()
    s = Store(db_path=db)
    assert {r["flag_code"] for r in s.list_flag_feedback()} == {"new_exec_command", "new_domains"}
    s.close()


def test_cli_alert_shows_demotion_after_threshold(tmp_path, capsys):
    db = tmp_path / "t.db"
    uid = _seed_alert(db)
    s = Store(db_path=db)
    s.record_flag_feedback(uid, "new_exec_command", "dismissed")
    s.record_flag_feedback(uid, "new_exec_command", "dismissed")
    s.close()
    assert main(["--db", str(db), "alert", "1"]) == 0
    assert "previously dismissed" in capsys.readouterr().out


def test_cli_confirm_cancels_demotion(tmp_path, capsys):
    db = tmp_path / "t.db"
    uid = _seed_alert(db)
    s = Store(db_path=db)
    s.record_flag_feedback(uid, "new_exec_command", "dismissed")
    s.record_flag_feedback(uid, "new_exec_command", "dismissed")
    s.close()
    assert main(["--db", str(db), "alert", "1", "--confirm"]) == 0
    capsys.readouterr()
    assert main(["--db", str(db), "alert", "1"]) == 0
    assert "previously dismissed" not in capsys.readouterr().out


def test_cli_feedback_list_and_reset(tmp_path, capsys):
    db = tmp_path / "t.db"
    uid = _seed_alert(db)
    s = Store(db_path=db)
    s.record_flag_feedback(uid, "new_domains", "dismissed")
    s.close()
    assert main(["--db", str(db), "feedback"]) == 0
    assert "new_domains" in capsys.readouterr().out
    assert main(["--db", str(db), "feedback", "--reset"]) == 0
    assert "Cleared" in capsys.readouterr().out
    main(["--db", str(db), "feedback"])
    assert "No feedback" in capsys.readouterr().out
