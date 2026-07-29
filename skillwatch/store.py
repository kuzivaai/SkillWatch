"""SQLite storage for URLs, snapshots, and alerts."""

import json
import sqlite3
from pathlib import Path

from . import ledger

_DEFAULT_DB_DIR = Path.home() / ".skillwatch"
_DEFAULT_DB_PATH = _DEFAULT_DB_DIR / "skillwatch.db"

_SCHEMA = """
CREATE TABLE IF NOT EXISTS urls (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT UNIQUE NOT NULL,
    source_type TEXT NOT NULL,
    source_path TEXT,
    added_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url_id INTEGER NOT NULL REFERENCES urls(id),
    fetched_at TEXT NOT NULL DEFAULT (datetime('now')),
    content_hash TEXT NOT NULL,
    content_text TEXT,
    raw_html TEXT,
    raw_html_hash TEXT,
    status_code INTEGER,
    error TEXT
);

CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url_id INTEGER NOT NULL REFERENCES urls(id),
    detected_at TEXT NOT NULL DEFAULT (datetime('now')),
    prev_snapshot_id INTEGER REFERENCES snapshots(id),
    new_snapshot_id INTEGER REFERENCES snapshots(id),
    diff_text TEXT,
    flags TEXT,
    severity TEXT NOT NULL DEFAULT 'info',
    reviewed INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    path TEXT UNIQUE NOT NULL,
    content_hash TEXT NOT NULL,
    urls TEXT NOT NULL,
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Append-only, never-pruned hash-chained record of what each URL served and
-- when. Unlike `snapshots` (capped at 50 per URL for disk), the ledger keeps
-- every observation as a tiny hash entry, so the tamper-evident history is
-- permanent even after full content is pruned. See skillwatch/ledger.py.
CREATE TABLE IF NOT EXISTS ledger (
    seq INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT NOT NULL,
    fetched_at TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    status_code INTEGER,
    prev_hash TEXT NOT NULL,
    chain_hash TEXT NOT NULL
);

-- External anchors of the ledger head. Each row records that a given head
-- (which commits to all history up to seq_covered) was externally attested by
-- `method` (e.g. an RFC 3161 timestamp token in `proof`). `verify` checks every
-- anchor's head is still in the chain, making a rewrite of anchored history
-- detectable. See skillwatch/anchoring.py.
CREATE TABLE IF NOT EXISTS anchors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    seq_covered INTEGER NOT NULL,
    head TEXT NOT NULL,
    method TEXT NOT NULL,
    external_ref TEXT,
    proof BLOB,
    anchored_time TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_snapshots_url ON snapshots(url_id, fetched_at DESC);
CREATE INDEX IF NOT EXISTS idx_alerts_url ON alerts(url_id, detected_at DESC);

-- Per-machine false-positive adaptation. Records the user's dismiss/confirm
-- decisions on alert flags so a flag repeatedly dismissed for a URL can be shown
-- as "previously dismissed" on future alerts. Local only; never leaves the
-- machine; the alert itself is never deleted, only its display priority lowered.
CREATE TABLE IF NOT EXISTS flag_feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url_id INTEGER NOT NULL REFERENCES urls(id),
    flag_code TEXT NOT NULL,
    content_fp TEXT NOT NULL DEFAULT '',
    decision TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_feedback_url ON flag_feedback(url_id, flag_code);
"""


class Store:
    def __init__(self, db_path: str | Path | None = None):
        self.db_path = Path(db_path) if db_path else _DEFAULT_DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(self.db_path), timeout=30, isolation_level="IMMEDIATE")
        self._conn.row_factory = sqlite3.Row
        self._conn.executescript(_SCHEMA)

    def __enter__(self) -> "Store":
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def close(self) -> None:
        self._conn.close()

    # --- URLs ---

    def add_url(self, url: str, source_type: str, source_path: str = "") -> tuple[int, bool]:
        """Add a URL to monitor. Returns (url_id, is_new)."""
        cur = self._conn.execute(
            "INSERT OR IGNORE INTO urls (url, source_type, source_path) VALUES (?, ?, ?)",
            (url, source_type, source_path),
        )
        self._conn.commit()
        if cur.lastrowid and cur.rowcount > 0:
            return cur.lastrowid, True
        row = self._conn.execute("SELECT id FROM urls WHERE url = ?", (url,)).fetchone()
        return row["id"], False

    def get_urls(self) -> list[dict]:
        """Get all monitored URLs."""
        rows = self._conn.execute(
            "SELECT u.id, u.url, u.source_type, u.source_path, u.added_at, "
            "  (SELECT content_hash FROM snapshots WHERE url_id = u.id ORDER BY id DESC LIMIT 1) as last_hash, "
            "  (SELECT fetched_at FROM snapshots WHERE url_id = u.id ORDER BY id DESC LIMIT 1) as last_checked, "
            "  (SELECT COUNT(*) FROM alerts WHERE url_id = u.id AND reviewed = 0) as open_alerts "
            "FROM urls u ORDER BY u.id"
        ).fetchall()
        return [dict(r) for r in rows]

    def remove_url(self, url: str) -> bool:
        """Remove a URL and its snapshots/alerts atomically."""
        row = self._conn.execute("SELECT id FROM urls WHERE url = ?", (url,)).fetchone()
        if not row:
            return False
        url_id = row["id"]
        with self._conn:
            self._conn.execute("DELETE FROM flag_feedback WHERE url_id = ?", (url_id,))
            self._conn.execute("DELETE FROM alerts WHERE url_id = ?", (url_id,))
            self._conn.execute("DELETE FROM snapshots WHERE url_id = ?", (url_id,))
            self._conn.execute("DELETE FROM urls WHERE id = ?", (url_id,))
        return True

    def url_count(self) -> int:
        row = self._conn.execute("SELECT COUNT(*) as c FROM urls").fetchone()
        return int(row["c"])

    def last_scan_time(self) -> str | None:
        """Return the most recent fetched_at timestamp, or None if no scans."""
        row = self._conn.execute(
            "SELECT fetched_at FROM snapshots ORDER BY id DESC LIMIT 1"
        ).fetchone()
        return row["fetched_at"] if row else None

    def pending_alert_count(self) -> int:
        """Return the number of unreviewed alerts."""
        row = self._conn.execute(
            "SELECT COUNT(*) as c FROM alerts WHERE reviewed = 0"
        ).fetchone()
        return int(row["c"])

    # --- Snapshots ---

    def add_snapshot(
        self, url_id: int, content_hash: str, content_text: str | None,
        raw_html: str | None = None, raw_html_hash: str | None = None,
        status_code: int | None = None, error: str | None = None,
    ) -> int:
        # Single transaction: INSERT + prune + ledger append together, so the
        # snapshot cache and the append-only ledger can never diverge.
        with self._conn:
            cur = self._conn.execute(
                "INSERT INTO snapshots (url_id, content_hash, content_text, raw_html, raw_html_hash, status_code, error) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (url_id, content_hash, content_text, raw_html, raw_html_hash, status_code, error),
            )
            # Prune old snapshots to prevent unbounded disk growth (keep most recent 50)
            self._conn.execute(
                "DELETE FROM snapshots WHERE url_id = ? AND id NOT IN "
                "(SELECT id FROM snapshots WHERE url_id = ? ORDER BY id DESC LIMIT 50)",
                (url_id, url_id),
            )
            # Record a permanent, tamper-evident ledger entry for every real
            # observation. Errors (empty content_hash) served no content, so
            # they are not part of the "what did this URL serve" record.
            if content_hash:
                self._append_ledger_entry(url_id, content_hash, status_code)
        assert cur.lastrowid is not None  # INSERT always sets lastrowid
        return cur.lastrowid

    def _append_ledger_entry(self, url_id: int, content_hash: str, status_code: int | None) -> None:
        """Append one hash-chained ledger entry. Must run inside a transaction."""
        url_row = self._conn.execute("SELECT url FROM urls WHERE id = ?", (url_id,)).fetchone()
        url = url_row["url"] if url_row else ""
        head = self._conn.execute(
            "SELECT chain_hash FROM ledger ORDER BY seq DESC LIMIT 1"
        ).fetchone()
        prev_hash = head["chain_hash"] if head else ledger.GENESIS_HASH
        # Read back the snapshot's stored fetched_at so the ledger commits to the
        # exact recorded time (the snapshots default is datetime('now')).
        fetched_at_row = self._conn.execute(
            "SELECT fetched_at FROM snapshots WHERE url_id = ? ORDER BY id DESC LIMIT 1",
            (url_id,),
        ).fetchone()
        fetched_at = fetched_at_row["fetched_at"] if fetched_at_row else ""
        eh = ledger.entry_hash(url, fetched_at, content_hash, status_code)
        ch = ledger.chain_hash(prev_hash, eh)
        self._conn.execute(
            "INSERT INTO ledger (url, fetched_at, content_hash, status_code, prev_hash, chain_hash) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (url, fetched_at, content_hash, status_code, prev_hash, ch),
        )

    # --- Ledger (verifiable content record) ---

    def ledger_count(self) -> int:
        row = self._conn.execute("SELECT COUNT(*) as c FROM ledger").fetchone()
        return int(row["c"])

    _LEDGER_COLS = (
        "seq, url, fetched_at, content_hash, status_code, prev_hash, chain_hash"
    )

    def export_ledger(self) -> list[dict]:
        """Return every ledger entry, ordered by seq, as portable dicts.

        Materialises the whole ledger; fine for programmatic use and tests. For
        large ledgers or the CLI, prefer export_ledger_to_file (streaming).
        The result re-verifies with ledger.verify_chain with no database access.
        """
        rows = self._conn.execute(
            f"SELECT {self._LEDGER_COLS} FROM ledger ORDER BY seq"
        ).fetchall()
        return [dict(r) for r in rows]

    def export_ledger_to_file(self, path: str | Path) -> int:
        """Stream the full ledger to a portable JSON file without loading it all
        into memory, writing to a temp file and renaming so a failure never
        leaves a partial export. Returns the number of entries written.
        """
        p = Path(path)
        tmp = p.with_name(p.name + ".tmp")
        cur = self._conn.execute(f"SELECT {self._LEDGER_COLS} FROM ledger ORDER BY seq")
        n = 0
        with open(tmp, "w", encoding="utf-8") as f:
            f.write('{"skillwatch_ledger_version": ' + str(ledger.SPEC_VERSION) + ', "entries": [')
            for r in cur:
                f.write(("," if n else "") + "\n    " + json.dumps(dict(r)))
                n += 1
            f.write("\n]}\n")
        tmp.replace(p)
        return n

    def get_ledger(self, limit: int = 20) -> list[dict]:
        """Return the most recent ledger entries, newest first."""
        rows = self._conn.execute(
            "SELECT seq, url, fetched_at, content_hash, status_code, prev_hash, chain_hash "
            "FROM ledger ORDER BY seq DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [dict(r) for r in rows]

    def verify_ledger(self) -> ledger.LedgerVerification:
        """Recompute the whole chain and report the first break, if any.

        Streams rows from an ordered cursor rather than loading the ledger into
        memory, so verification scales to very large ledgers.
        """
        cur = self._conn.execute(f"SELECT {self._LEDGER_COLS} FROM ledger ORDER BY seq")
        return ledger.verify_stream(dict(r) for r in cur)

    def record_anchor(
        self, seq_covered: int, head: str, method: str,
        external_ref: str = "", proof: bytes = b"", anchored_time: str = "",
    ) -> int:
        """Persist an external anchor of the ledger head. Returns its row id."""
        cur = self._conn.execute(
            "INSERT INTO anchors (seq_covered, head, method, external_ref, proof, anchored_time) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (seq_covered, head, method, external_ref, proof, anchored_time),
        )
        self._conn.commit()
        assert cur.lastrowid is not None  # INSERT always sets lastrowid
        return cur.lastrowid

    def get_anchors(self) -> list[dict]:
        """Return all recorded anchors, oldest first."""
        rows = self._conn.execute(
            "SELECT id, seq_covered, head, method, external_ref, proof, anchored_time, created_at "
            "FROM anchors ORDER BY id"
        ).fetchall()
        return [dict(r) for r in rows]

    def latest_anchor(self) -> dict | None:
        """Return the most recently recorded anchor, or None."""
        row = self._conn.execute(
            "SELECT id, seq_covered, head, method, external_ref, proof, anchored_time, created_at "
            "FROM anchors ORDER BY id DESC LIMIT 1"
        ).fetchone()
        return dict(row) if row else None

    def anchor_count(self) -> int:
        row = self._conn.execute("SELECT COUNT(*) as c FROM anchors").fetchone()
        return int(row["c"])

    def ledger_contains_hash(self, chain_hash: str) -> bool:
        """True if any entry has this chain_hash.

        A head published earlier stays findable as history grows, so this is how
        `verify --against <head>` confirms an externally anchored head is still
        part of the current, verified chain.
        """
        row = self._conn.execute(
            "SELECT 1 FROM ledger WHERE chain_hash = ? LIMIT 1", (chain_hash,)
        ).fetchone()
        return row is not None

    def get_latest_snapshot(self, url_id: int) -> dict | None:
        row = self._conn.execute(
            "SELECT * FROM snapshots WHERE url_id = ? ORDER BY id DESC LIMIT 1",
            (url_id,),
        ).fetchone()
        return dict(row) if row else None

    def get_latest_good_snapshot(self, url_id: int) -> dict | None:
        """Get the most recent snapshot that was NOT an error."""
        row = self._conn.execute(
            "SELECT * FROM snapshots WHERE url_id = ? AND error IS NULL "
            "ORDER BY id DESC LIMIT 1",
            (url_id,),
        ).fetchone()
        return dict(row) if row else None

    def get_snapshot_history(self, url_id: int, limit: int = 20) -> list[dict]:
        rows = self._conn.execute(
            "SELECT * FROM snapshots WHERE url_id = ? ORDER BY id DESC LIMIT ?",
            (url_id, limit),
        ).fetchall()
        return [dict(r) for r in rows]

    # --- Alerts ---

    def add_alert(
        self, url_id: int, prev_snapshot_id: int, new_snapshot_id: int,
        diff_text: str, flags: list[str], severity: str = "info",
    ) -> int:
        cur = self._conn.execute(
            "INSERT INTO alerts (url_id, prev_snapshot_id, new_snapshot_id, diff_text, flags, severity) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (url_id, prev_snapshot_id, new_snapshot_id, diff_text, json.dumps(flags), severity),
        )
        self._conn.commit()
        assert cur.lastrowid is not None  # INSERT always sets lastrowid
        return cur.lastrowid

    def get_alerts(self, url_id: int | None = None, unreviewed_only: bool = False) -> list[dict]:
        query = "SELECT a.*, u.url FROM alerts a JOIN urls u ON a.url_id = u.id WHERE 1=1"
        params: list = []
        if url_id is not None:
            query += " AND a.url_id = ?"
            params.append(url_id)
        if unreviewed_only:
            query += " AND a.reviewed = 0"
        query += " ORDER BY a.detected_at DESC"
        rows = self._conn.execute(query, params).fetchall()
        result = []
        for r in rows:
            d = dict(r)
            if d.get("flags"):
                d["flags"] = json.loads(d["flags"])
            result.append(d)
        return result

    def mark_alert_reviewed(self, alert_id: int) -> bool:
        cur = self._conn.execute(
            "UPDATE alerts SET reviewed = 1 WHERE id = ?", (alert_id,),
        )
        self._conn.commit()
        return cur.rowcount > 0

    def get_alert(self, alert_id: int) -> dict | None:
        row = self._conn.execute(
            "SELECT a.*, u.url FROM alerts a JOIN urls u ON a.url_id = u.id WHERE a.id = ?",
            (alert_id,),
        ).fetchone()
        if not row:
            return None
        d = dict(row)
        if d.get("flags"):
            d["flags"] = json.loads(d["flags"])
        return d

    # --- Flag feedback (local false-positive adaptation) ---

    def record_flag_feedback(
        self, url_id: int, flag_code: str, decision: str, content_fp: str = ""
    ) -> None:
        """Record a 'dismissed' or 'confirmed' decision for a flag on a URL."""
        if decision not in ("dismissed", "confirmed"):
            raise ValueError(f"decision must be 'dismissed' or 'confirmed', got {decision!r}")
        self._conn.execute(
            "INSERT INTO flag_feedback (url_id, flag_code, content_fp, decision) "
            "VALUES (?, ?, ?, ?)",
            (url_id, flag_code, content_fp, decision),
        )
        self._conn.commit()

    def demoted_flags(self, url_id: int, threshold: int = 2) -> set[str]:
        """Flag codes for this URL dismissed >= threshold times and never confirmed.

        Aggregated per (url_id, flag_code): a confirm anywhere cancels demotion.
        content_fp is retained per row for audit but does not gate this decision,
        since a recurring benign change produces a different diff each time.
        """
        rows = self._conn.execute(
            "SELECT flag_code, "
            "SUM(CASE WHEN decision = 'dismissed' THEN 1 ELSE 0 END) AS dismissed, "
            "SUM(CASE WHEN decision = 'confirmed' THEN 1 ELSE 0 END) AS confirmed "
            "FROM flag_feedback WHERE url_id = ? GROUP BY flag_code",
            (url_id,),
        ).fetchall()
        return {
            str(r["flag_code"])
            for r in rows
            if int(r["dismissed"]) >= threshold and int(r["confirmed"]) == 0
        }

    def list_flag_feedback(self) -> list[dict]:
        """Summarise recorded feedback, grouped by URL, flag, and decision."""
        rows = self._conn.execute(
            "SELECT u.url AS url, f.flag_code AS flag_code, f.decision AS decision, "
            "COUNT(*) AS n, MAX(f.created_at) AS last_at "
            "FROM flag_feedback f JOIN urls u ON f.url_id = u.id "
            "GROUP BY f.url_id, f.flag_code, f.decision "
            "ORDER BY u.url, f.flag_code, f.decision"
        ).fetchall()
        return [dict(r) for r in rows]

    def reset_flag_feedback(self) -> int:
        """Delete all recorded feedback. Returns the number of rows removed."""
        with self._conn:
            cur = self._conn.execute("DELETE FROM flag_feedback")
        return cur.rowcount

    # --- Sources (definition drift) ---

    def record_source(self, path: str, content_hash: str, urls: list[str]) -> None:
        """Insert or update a monitored source file's fingerprint (hash + URL set)."""
        self._conn.execute(
            "INSERT INTO sources (path, content_hash, urls) VALUES (?, ?, ?) "
            "ON CONFLICT(path) DO UPDATE SET "
            "content_hash = excluded.content_hash, urls = excluded.urls, "
            "updated_at = datetime('now')",
            (path, content_hash, json.dumps(urls)),
        )
        self._conn.commit()

    def get_sources(self) -> list[dict]:
        """Return all tracked source files, each with its recorded URL set."""
        rows = self._conn.execute("SELECT * FROM sources ORDER BY id").fetchall()
        result = []
        for r in rows:
            d = dict(r)
            d["urls"] = json.loads(d["urls"]) if d.get("urls") else []
            result.append(d)
        return result
