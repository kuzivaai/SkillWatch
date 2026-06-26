"""SQLite storage for URLs, snapshots, and alerts."""

import json
import sqlite3
from pathlib import Path

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

CREATE INDEX IF NOT EXISTS idx_snapshots_url ON snapshots(url_id, fetched_at DESC);
CREATE INDEX IF NOT EXISTS idx_alerts_url ON alerts(url_id, detected_at DESC);
"""


class Store:
    def __init__(self, db_path: str | Path | None = None):
        self.db_path = Path(db_path) if db_path else _DEFAULT_DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(self.db_path))
        self._conn.row_factory = sqlite3.Row
        self._conn.executescript(_SCHEMA)

    def __enter__(self) -> "Store":
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def close(self) -> None:
        self._conn.close()

    # --- URLs ---

    def add_url(self, url: str, source_type: str, source_path: str = "") -> int:
        """Add a URL to monitor. Returns the url id. Ignores duplicates."""
        cur = self._conn.execute(
            "INSERT OR IGNORE INTO urls (url, source_type, source_path) VALUES (?, ?, ?)",
            (url, source_type, source_path),
        )
        self._conn.commit()
        if cur.lastrowid and cur.rowcount > 0:
            return cur.lastrowid
        # Already exists
        row = self._conn.execute("SELECT id FROM urls WHERE url = ?", (url,)).fetchone()
        return row["id"]

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
        """Remove a URL and its snapshots/alerts."""
        row = self._conn.execute("SELECT id FROM urls WHERE url = ?", (url,)).fetchone()
        if not row:
            return False
        url_id = row["id"]
        self._conn.execute("DELETE FROM alerts WHERE url_id = ?", (url_id,))
        self._conn.execute("DELETE FROM snapshots WHERE url_id = ?", (url_id,))
        self._conn.execute("DELETE FROM urls WHERE id = ?", (url_id,))
        self._conn.commit()
        return True

    def url_count(self) -> int:
        row = self._conn.execute("SELECT COUNT(*) as c FROM urls").fetchone()
        return row["c"]

    # --- Snapshots ---

    def add_snapshot(
        self, url_id: int, content_hash: str, content_text: str | None,
        raw_html_hash: str | None = None, status_code: int | None = None,
        error: str | None = None,
    ) -> int:
        cur = self._conn.execute(
            "INSERT INTO snapshots (url_id, content_hash, content_text, raw_html_hash, status_code, error) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (url_id, content_hash, content_text, raw_html_hash, status_code, error),
        )
        self._conn.commit()
        return cur.lastrowid

    def get_latest_snapshot(self, url_id: int) -> dict | None:
        row = self._conn.execute(
            "SELECT * FROM snapshots WHERE url_id = ? ORDER BY id DESC LIMIT 1",
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
