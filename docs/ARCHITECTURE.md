# Architecture — SkillWatch

**Type:** Python CLI tool, runs locally via cron
**No server, no web UI, no auth, no payments**

---

## Pipeline

```
Input (SKILL.md / MCP config / URL list)
  → URL Extraction (parser.py)
  → Fetch + Text Extraction (fetcher.py, trafilatura)
  → Hash + Store (store.py, SQLite)
  → Compare to Previous Hash (differ.py)
  → If Changed: Pattern Detection (detector.py)
  → Output (formatter.py, terminal)
```

## Components

| Module | Responsibility | Dependencies |
|---|---|---|
| `cli.py` | argparse entry point: add, scan, list, history | all modules |
| `parser.py` | Extract URLs from SKILL.md, MCP configs, URL lists | re, json, yaml |
| `fetcher.py` | Fetch URL content, extract text via trafilatura | requests, trafilatura |
| `store.py` | SQLite read/write: URLs, snapshots, alerts | sqlite3 (stdlib) |
| `differ.py` | Hash comparison + unified diff generation | hashlib, difflib (stdlib) |
| `detector.py` | Rule-based suspicious pattern detection on diffs/HTML | bs4 |
| `formatter.py` | Terminal output with colours and summary tables | (stdlib) |

## Key Decisions

| Decision | Choice | Reasoning |
|---|---|---|
| Text extraction | trafilatura | Strips boilerplate, nav, ads, scripts. Solves 90% of dynamic content false positives. Well-maintained. |
| Hash target | Extracted text, NOT raw HTML | Raw HTML changes constantly (CSRF tokens, session IDs). Text content is stable for docs pages. |
| Storage | SQLite (local file) | Zero infrastructure. Built into Python. Sufficient for 100-1000 URLs. |
| CLI framework | argparse | Zero external dependencies. The tool should have minimal deps. |
| Config format | YAML | Human-readable, familiar to developers. Single optional dependency (PyYAML). |
| No LLM in v1 | Rule-based detection only | Keeps the tool free, offline-capable, and dependency-light. LLM classification is a v2 `--classify` flag. |
| No daemon | Cron-based scheduling | Simpler to build, test, and debug. Users know cron. |

## SQLite Schema

```sql
CREATE TABLE IF NOT EXISTS urls (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT UNIQUE NOT NULL,
    source_type TEXT NOT NULL,  -- 'skill_md', 'mcp_config', 'manual'
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
    flags TEXT,  -- JSON array: ["new_script_tag", "download_command", ...]
    severity TEXT NOT NULL DEFAULT 'info',  -- 'info', 'warning', 'critical'
    reviewed INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_snapshots_url ON snapshots(url_id, fetched_at DESC);
CREATE INDEX IF NOT EXISTS idx_alerts_url ON alerts(url_id, detected_at DESC);
```

## CLI Interface

```bash
# Add URLs from a SKILL.md file
skillwatch add skill.md

# Add URLs from an MCP config
skillwatch add mcp.json

# Add a single URL manually
skillwatch add-url https://example.com/docs

# Run a scan of all monitored URLs
skillwatch scan

# List all monitored URLs and their status
skillwatch list

# Show change history for a specific URL
skillwatch history https://example.com/docs

# Show details of an alert
skillwatch alert <alert-id>
```

## Config File (optional)

```yaml
# skillwatch.yaml
settings:
  delay_seconds: 2
  timeout_seconds: 10
  max_redirects: 3
  user_agent: "SkillWatch/0.1 (+https://github.com/kuzivaai/skillwatch)"
  db_path: ~/.skillwatch/skillwatch.db

ignore_patterns:
  - '\d{4}-\d{2}-\d{2}T\d{2}:\d{2}'  # ISO timestamps
  - 'v\d+\.\d+\.\d+'                   # Version strings
```
