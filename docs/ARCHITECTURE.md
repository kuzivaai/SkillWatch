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
| `ssrf.py` | SSRF validation, DNS pinning, PinnedDNSAdapter | ipaddress, socket, requests |
| `parser.py` | Extract URLs from SKILL.md, MCP configs, URL lists | re, json, yaml |
| `fetcher.py` | Fetch URL content, extract text via trafilatura | requests, trafilatura |
| `store.py` | SQLite read/write: URLs, snapshots, alerts | sqlite3 (stdlib) |
| `differ.py` | Hash comparison + unified diff generation | hashlib, difflib (stdlib) |
| `detector.py` | Rule-based detection on diffs/HTML + plain-language flag explanations | bs4 |
| `sarif.py` | SARIF 2.1.0 output for GitHub Code Scanning | (stdlib) |
| `formatter.py` | Terminal output with colours and summary tables | (stdlib) |
| `ledger.py` | Append-only hash-chained record, chain verification | hashlib (stdlib) |
| `anchoring.py` | RFC 3161 external timestamping of the ledger head | rfc3161-client, cryptography (optional `anchor` extra) |
| `cloak.py` | Cloaking detection across fetch strategies | requests |
| `__init__.py` | Version declaration | (none) |

Thirteen modules, which is the count `git ls-files 'skillwatch/*.py'` returns.
`tests/test_public_document_currency.py` derives it the same way and fails if this
table stops matching. The table listed nine until 2026-08-06, omitting `ledger.py`,
`anchoring.py`, `cloak.py` and `__init__.py`, because nothing checked it.

## Key Decisions

| Decision | Choice | Reasoning |
|---|---|---|
| Text extraction | trafilatura | Strips boilerplate, nav, ads, scripts. Solves 90% of dynamic content false positives. Well-maintained. |
| Hash target | Extracted text, NOT raw HTML | Raw HTML changes constantly (CSRF tokens, session IDs). Text content is stable for docs pages. |
| Storage | SQLite (local file) | Zero infrastructure. Built into Python. Sufficient for 100-1000 URLs. |
| CLI framework | argparse | Standard library; adds no additional dependency. |
| Config format | YAML | Human-readable, familiar to developers. Single optional dependency (PyYAML). |
| No LLM in v1 | Rule-based detection only | Keeps the tool free, offline-capable, and dependency-light. LLM classification is a v2 `--classify` flag. |
| No daemon | Cron-based scheduling | Simpler to build, test, and debug. Users know cron. |

## SQLite Schema

Seven tables, which is the count of `CREATE TABLE IF NOT EXISTS` statements under
`skillwatch/`. The full DDL is not reproduced here. It used to be, for three of the
seven, and the copy went stale: a schema pasted into prose is a second copy of a
fact, free to drift from the first, and this one did. The source of truth is the
`SCHEMA` constant in `skillwatch/store.py`.

| Table | Holds | Defined in |
|---|---|---|
| `urls` | Each monitored URL, its source type and source path | `store.py` |
| `snapshots` | Fetched text and raw HTML per observation, capped at 50 per URL for disk | `store.py` |
| `alerts` | A detected change, its diff, flag codes, severity and reviewed state | `store.py` |
| `sources` | Each skill file or config, its content hash and extracted URLs, so drift in the definition itself is visible | `store.py` |
| `ledger` | Append-only hash-chained record of what each URL served and when. Never pruned, so the tamper-evident history outlives pruned snapshots | `store.py`, verified by `ledger.py` |
| `anchors` | External attestations of a ledger head, including an RFC 3161 token in `proof` | `store.py`, written by `anchoring.py` |
| `flag_feedback` | Local accept or reject decisions per flag code and content fingerprint | `store.py` |

`tests/test_public_document_currency.py` derives the table count from the source and
fails if this table stops matching. This section documented three tables until
2026-08-06, omitting `sources`, `ledger`, `anchors` and `flag_feedback`.

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

## Configuration

All settings are controlled via CLI flags (`--db`, `--delay`, `--timeout`, `--quiet`).
There is no config file. This sentence read "no config file in v0.1" until 2026-08-06,
which had been carried unchanged through 0.2.0, 0.3.0, 0.4.0 and 0.4.1. Version
literals are not repeated in this document for that reason; `pyproject.toml` declares
the version and `tests/test_claude_md_currency.py` checks it.

The `## CLI Interface` section above is illustrative, not exhaustive. There are 15
subcommands; it shows the common ones. `skillwatch --help` is authoritative.
