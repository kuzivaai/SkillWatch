"""Tests for the verifiable content ledger.

The ledger is an append-only, never-pruned, hash-chained record of what each
monitored URL served and when. Its purpose is a tamper-EVIDENT, independently
re-verifiable history: any edit to a past entry breaks the chain and is caught
by `verify`. (A motivated local attacker who recomputes the whole chain is out
of scope for the local-only ledger — that is what external anchoring, a later
increment, is for. See docs.)
"""

import sqlite3
import tempfile
from pathlib import Path

import pytest

from skillwatch import ledger
from skillwatch.store import Store


@pytest.fixture
def store():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        with Store(db_path=db_path) as s:
            yield s


# --- Pure hash spec (skillwatch/ledger.py) -------------------------------


class TestHashSpec:
    def test_entry_hash_is_deterministic(self):
        a = ledger.entry_hash("https://a.com", "2026-07-11 10:00:00", "abc", 200)
        b = ledger.entry_hash("https://a.com", "2026-07-11 10:00:00", "abc", 200)
        assert a == b
        assert len(a) == 64  # sha256 hex

    def test_entry_hash_depends_on_every_field(self):
        base = ledger.entry_hash("https://a.com", "2026-07-11 10:00:00", "abc", 200)
        assert ledger.entry_hash("https://b.com", "2026-07-11 10:00:00", "abc", 200) != base
        assert ledger.entry_hash("https://a.com", "2026-07-11 10:00:01", "abc", 200) != base
        assert ledger.entry_hash("https://a.com", "2026-07-11 10:00:00", "xyz", 200) != base
        assert ledger.entry_hash("https://a.com", "2026-07-11 10:00:00", "abc", 404) != base

    def test_status_code_none_is_stable(self):
        a = ledger.entry_hash("https://a.com", "t", "abc", None)
        b = ledger.entry_hash("https://a.com", "t", "abc", None)
        assert a == b

    def test_chain_hash_links_prev_and_entry(self):
        eh = ledger.entry_hash("https://a.com", "t", "abc", 200)
        ch = ledger.chain_hash(ledger.GENESIS_HASH, eh)
        assert len(ch) == 64
        # Changing either input changes the chain hash.
        assert ledger.chain_hash("deadbeef", eh) != ch
        assert ledger.chain_hash(ledger.GENESIS_HASH, "0" * 64) != ch

    def test_no_field_boundary_ambiguity(self):
        """A separator inside a field must not let two different tuples collide.

        Under a naive newline join, ("a\\nX", "Y", ...) and ("a", "X\\nY", ...)
        both render "a\\nX\\nY\\n..." and hash identically. That would let an
        attacker forge an equivalent entry, so the encoding must be unambiguous.
        """
        a = ledger.entry_hash("a\nX", "Y", "h", 200)
        b = ledger.entry_hash("a", "X\nY", "h", 200)
        assert a != b


def _build_entry(seq, url, fetched_at, content_hash, status_code, prev_hash):
    """Build a well-formed ledger entry dict (as verify_chain consumes)."""
    eh = ledger.entry_hash(url, fetched_at, content_hash, status_code)
    return {
        "seq": seq,
        "url": url,
        "fetched_at": fetched_at,
        "content_hash": content_hash,
        "status_code": status_code,
        "prev_hash": prev_hash,
        "chain_hash": ledger.chain_hash(prev_hash, eh),
    }


def _well_formed_chain(n=3):
    entries = []
    prev = ledger.GENESIS_HASH
    for i in range(1, n + 1):
        e = _build_entry(i, f"https://a.com/{i}", f"2026-07-11 10:00:0{i}", f"hash{i}", 200, prev)
        entries.append(e)
        prev = e["chain_hash"]
    return entries


class TestVerifyChain:
    def test_empty_chain_is_valid(self):
        result = ledger.verify_chain([])
        assert result.ok is True
        assert result.entries == 0
        assert result.broken_seq is None

    def test_well_formed_chain_verifies(self):
        result = ledger.verify_chain(_well_formed_chain(5))
        assert result.ok is True
        assert result.entries == 5
        assert result.broken_seq is None

    def test_first_entry_must_start_at_genesis(self):
        entries = _well_formed_chain(2)
        entries[0]["prev_hash"] = "f" * 64  # not GENESIS
        result = ledger.verify_chain(entries)
        assert result.ok is False
        assert result.broken_seq == 1

    def test_detects_tampered_content_hash(self):
        entries = _well_formed_chain(4)
        entries[1]["content_hash"] = "TAMPERED"  # edit a past record, don't fix chain
        result = ledger.verify_chain(entries)
        assert result.ok is False
        assert result.broken_seq == 2  # caught at the tampered entry

    def test_detects_broken_link(self):
        entries = _well_formed_chain(4)
        entries[2]["prev_hash"] = "0" * 64  # points at the wrong predecessor
        result = ledger.verify_chain(entries)
        assert result.ok is False
        assert result.broken_seq == 3

    def test_detects_deleted_middle_entry(self):
        entries = _well_formed_chain(4)
        del entries[1]  # remove seq 2; seq 3's prev_hash no longer matches
        result = ledger.verify_chain(entries)
        assert result.ok is False
        assert result.broken_seq == 3

    def test_input_order_independent(self):
        """verify_chain sorts by seq, so export order does not matter."""
        entries = _well_formed_chain(4)
        shuffled = [entries[2], entries[0], entries[3], entries[1]]
        assert ledger.verify_chain(shuffled).ok is True


# --- Store integration ---------------------------------------------------


class TestLedgerStore:
    def test_content_snapshot_appends_ledger_entry(self, store):
        url_id, _ = store.add_url("https://example.com", "manual")
        store.add_snapshot(url_id, "abc123", "Hello", status_code=200)
        assert store.ledger_count() == 1

    def test_error_snapshot_does_not_append(self, store):
        url_id, _ = store.add_url("https://example.com", "manual")
        store.add_snapshot(url_id, "", None, error="Timeout", status_code=500)
        assert store.ledger_count() == 0

    def test_ledger_records_url_string(self, store):
        url_id, _ = store.add_url("https://example.com/docs", "manual")
        store.add_snapshot(url_id, "abc", "Hello")
        entries = store.export_ledger()
        assert entries[0]["url"] == "https://example.com/docs"

    def test_two_snapshots_chain_together(self, store):
        url_id, _ = store.add_url("https://example.com", "manual")
        store.add_snapshot(url_id, "hash1", "v1")
        store.add_snapshot(url_id, "hash2", "v2")
        entries = store.export_ledger()
        assert len(entries) == 2
        assert entries[0]["prev_hash"] == ledger.GENESIS_HASH
        assert entries[1]["prev_hash"] == entries[0]["chain_hash"]

    def test_live_ledger_verifies(self, store):
        url_id, _ = store.add_url("https://example.com", "manual")
        for i in range(5):
            store.add_snapshot(url_id, f"hash{i}", f"v{i}")
        assert store.verify_ledger().ok is True

    def test_ledger_survives_snapshot_pruning(self, store):
        """Snapshots prune to 50 per URL; the ledger must keep every entry."""
        url_id, _ = store.add_url("https://example.com", "manual")
        for i in range(55):
            store.add_snapshot(url_id, f"hash{i}", f"v{i}")
        # snapshots pruned to 50
        assert len(store.get_snapshot_history(url_id, limit=1000)) == 50
        # ledger keeps all 55 and still verifies
        assert store.ledger_count() == 55
        assert store.verify_ledger().ok is True

    def test_verify_ledger_detects_db_tampering(self, store):
        url_id, _ = store.add_url("https://example.com", "manual")
        store.add_snapshot(url_id, "hash1", "v1")
        store.add_snapshot(url_id, "hash2", "v2")
        store.close()
        # Tamper directly in the database file.
        conn = sqlite3.connect(str(store.db_path))
        conn.execute("UPDATE ledger SET content_hash = 'EVIL' WHERE seq = 1")
        conn.commit()
        conn.close()
        with Store(db_path=store.db_path) as s2:
            result = s2.verify_ledger()
            assert result.ok is False
            assert result.broken_seq == 1

    def test_verify_ledger_detects_row_deletion(self, store):
        url_id, _ = store.add_url("https://example.com", "manual")
        for i in range(3):
            store.add_snapshot(url_id, f"hash{i}", f"v{i}")
        store.close()
        conn = sqlite3.connect(str(store.db_path))
        conn.execute("DELETE FROM ledger WHERE seq = 2")
        conn.commit()
        conn.close()
        with Store(db_path=store.db_path) as s2:
            assert s2.verify_ledger().ok is False

    def test_export_is_independently_verifiable(self, store):
        """An exported ledger re-verifies with the pure verify_chain — no DB."""
        url_id, _ = store.add_url("https://example.com", "manual")
        for i in range(4):
            store.add_snapshot(url_id, f"hash{i}", f"v{i}")
        exported = store.export_ledger()
        assert ledger.verify_chain(exported).ok is True

    def test_export_ordered_by_seq(self, store):
        url_id, _ = store.add_url("https://example.com", "manual")
        for i in range(3):
            store.add_snapshot(url_id, f"hash{i}", f"v{i}")
        exported = store.export_ledger()
        seqs = [e["seq"] for e in exported]
        assert seqs == sorted(seqs)

    def test_empty_ledger_count_and_verify(self, store):
        assert store.ledger_count() == 0
        assert store.verify_ledger().ok is True


class TestAnchoring:
    """The chain head commits to the whole prefix; publishing it externally and
    re-checking with verify --against <head> upgrades tamper-evidence to
    tamper-proofing for any history up to a published head. All offline."""

    def test_verify_reports_head(self, store):
        url_id, _ = store.add_url("https://a.com", "manual")
        store.add_snapshot(url_id, "h1", "v1")
        store.add_snapshot(url_id, "h2", "v2")
        result = store.verify_ledger()
        assert result.ok is True
        assert result.head is not None
        assert len(result.head) == 64
        assert result.head == store.export_ledger()[-1]["chain_hash"]

    def test_empty_ledger_head_is_none(self, store):
        assert store.verify_ledger().head is None

    def test_earlier_head_still_present_after_more_entries(self, store):
        """A head published earlier must remain findable once more entries land."""
        url_id, _ = store.add_url("https://a.com", "manual")
        store.add_snapshot(url_id, "h1", "v1")
        head_after_one = store.verify_ledger().head
        store.add_snapshot(url_id, "h2", "v2")
        store.add_snapshot(url_id, "h3", "v3")
        assert store.ledger_contains_hash(head_after_one) is True
        assert store.ledger_contains_hash("0" * 64) is False


class TestStreaming:
    """verify and export stream rows in seq order instead of loading the whole
    ledger into memory, so they scale to very large ledgers (CR-3)."""

    def test_verify_stream_accepts_a_generator(self):
        entries = _well_formed_chain(4)  # already in seq order
        result = ledger.verify_stream(e for e in entries)
        assert result.ok is True
        assert result.entries == 4
        assert result.head == entries[-1]["chain_hash"]

    def test_verify_stream_detects_tamper_in_order(self):
        entries = _well_formed_chain(4)
        entries[1]["content_hash"] = "TAMPERED"
        result = ledger.verify_stream(iter(entries))
        assert result.ok is False
        assert result.broken_seq == 2

    def test_verify_ledger_streams_and_stays_correct(self, store):
        url_id, _ = store.add_url("https://a.com", "manual")
        for i in range(40):
            store.add_snapshot(url_id, f"h{i}", f"v{i}")
        result = store.verify_ledger()
        assert result.ok is True
        assert result.entries == 40

    def test_export_to_file_streams_and_reverifies(self, store, tmp_path):
        import json
        url_id, _ = store.add_url("https://a.com", "manual")
        for i in range(12):
            store.add_snapshot(url_id, f"h{i}", f"v{i}")
        out = tmp_path / "l.json"
        n = store.export_ledger_to_file(str(out))
        assert n == 12
        payload = json.loads(out.read_text())
        assert payload["skillwatch_ledger_version"] == ledger.SPEC_VERSION
        assert len(payload["entries"]) == 12
        assert ledger.verify_chain(payload["entries"]).ok is True


# --- CLI (skillwatch verify / skillwatch ledger) -------------------------


import json as _json  # noqa: E402
import re  # noqa: E402

from skillwatch.cli import main  # noqa: E402


def _seed(db_path, n=3, url="https://example.com/docs"):
    with Store(db_path=db_path) as s:
        url_id, _ = s.add_url(url, "manual")
        for i in range(n):
            s.add_snapshot(url_id, f"hash{i}", f"v{i}", status_code=200)


class TestVerifyCommand:
    def test_verify_empty_db_is_ok(self, tmp_path, capsys):
        db = str(tmp_path / "t.db")
        code = main(["--db", db, "verify"])
        out = capsys.readouterr().out
        assert code == 0
        assert "empty" in out.lower()

    def test_verify_clean_ledger(self, tmp_path, capsys):
        db = str(tmp_path / "t.db")
        _seed(db, n=4)
        code = main(["--db", db, "verify"])
        out = capsys.readouterr().out
        assert code == 0
        assert "verified" in out.lower()
        assert "4" in out  # entry count reported

    def test_verify_tampered_ledger_exits_nonzero(self, tmp_path, capsys):
        db = str(tmp_path / "t.db")
        _seed(db, n=3)
        conn = sqlite3.connect(db)
        conn.execute("UPDATE ledger SET content_hash = 'EVIL' WHERE seq = 1")
        conn.commit()
        conn.close()
        code = main(["--db", db, "verify"])
        out = capsys.readouterr().out
        assert code == 1
        assert "failed" in out.lower()
        assert "#1" in out  # names the first broken entry


class TestLedgerCommand:
    def test_ledger_empty(self, tmp_path, capsys):
        db = str(tmp_path / "t.db")
        code = main(["--db", db, "ledger"])
        out = capsys.readouterr().out
        assert code == 0
        assert "empty" in out.lower()

    def test_ledger_lists_entries(self, tmp_path, capsys):
        db = str(tmp_path / "t.db")
        _seed(db, n=2, url="https://watched.example/page")
        code = main(["--db", db, "ledger"])
        out = capsys.readouterr().out
        assert code == 0
        assert "watched.example/page" in out

    def test_ledger_export_writes_verifiable_json(self, tmp_path, capsys):
        db = str(tmp_path / "t.db")
        _seed(db, n=3)
        out_file = tmp_path / "ledger.json"
        code = main(["--db", db, "ledger", "--export", str(out_file)])
        out = capsys.readouterr().out
        assert code == 0
        assert out_file.exists()
        payload = _json.loads(out_file.read_text())
        assert ledger.verify_chain(payload["entries"]).ok is True
        assert "exported" in out.lower()

    def test_ledger_export_to_unwritable_path_errors(self, tmp_path, capsys):
        db = str(tmp_path / "t.db")
        _seed(db, n=1)
        bad = str(tmp_path / "does-not-exist" / "ledger.json")
        code = main(["--db", db, "ledger", "--export", bad])
        err = capsys.readouterr().err
        assert code == 1
        assert "error" in err.lower()


class TestVerifyAgainstAnchor:
    def test_verify_shows_head(self, tmp_path, capsys):
        db = str(tmp_path / "t.db")
        _seed(db, n=2)
        code = main(["--db", db, "verify"])
        out = capsys.readouterr().out
        assert code == 0
        assert re.search(r"\b[0-9a-f]{64}\b", out)  # the head hash is shown

    def test_verify_against_matching_head_ok(self, tmp_path, capsys):
        db = str(tmp_path / "t.db")
        _seed(db, n=3)
        with Store(db_path=db) as s:
            head = s.verify_ledger().head
        code = main(["--db", db, "verify", "--against", head])
        out = capsys.readouterr().out
        assert code == 0
        assert "match" in out.lower()

    def test_verify_against_divergent_head_fails(self, tmp_path, capsys):
        db = str(tmp_path / "t.db")
        _seed(db, n=3)
        code = main(["--db", db, "verify", "--against", "0" * 64])
        out = capsys.readouterr().out
        assert code == 1
        assert "diverg" in out.lower()
