# Audit Report — SkillWatch v0.1.0

**Date:** 26 June 2026
**Auditor:** Independent sceptical review (no stake in passing)
**Commit:** 1f2814c
**Method:** Full source read of all 26 tracked files, lint, 118 tests, E2E against live HTTPS, edge case exercise, claim-by-claim verification, coverage analysis

---

## Summary

The tool works. The core pipeline — add URLs, scan, detect changes, show alerts — functions correctly end-to-end against real HTTPS targets. Security mitigations (SSRF, DNS pinning, escape stripping, per-hop redirect validation) are implemented and functional.

However, the test suite has a serious structural defect: 10 HTTP mock tests are silently skipped due to incorrect use of `@responses.activate` on a class, and the three most important CLI commands (`scan`, `history`, `alert`) have zero test coverage. Documentation has not kept pace with code changes.

---

## Findings

### F1 — CRITICAL: 10 fetcher HTTP tests silently skipped

**Severity:** Critical
**Verdict:** Broken
**Evidence:** `python -m pytest tests/test_fetcher.py -v` collects 18 tests, not 28. The `TestFetchUrlHTTP` class (11 methods) is decorated with `@responses.activate` at class level, which does not work with pytest — the decorator only works per-method or as a context manager. These tests are never collected, never run, and never counted in the "118 passing" total. The fetcher's happy path (lines 82-165: DNS-pinned fetch, redirect loop, content extraction, hashing) has **zero test coverage**.

**Impact:** The core function that fetches URLs and extracts content is untested. Any regression in the fetch pipeline would go undetected.

### F2 — HIGH: `scan`, `history`, `alert` CLI commands untested

**Severity:** High
**Verdict:** Partial (commands work in E2E but have no automated tests)
**Evidence:** `grep -c "scan\|history\|alert" tests/test_cli.py` shows no test exercises the scan, history, or individual alert commands. Coverage report confirms `cli.py` at 53% with lines 152-297 (all three commands) uncovered.

**Impact:** The entire detection pipeline (scan → compare → detect → alert) has no automated test. Regressions would only be caught by manual E2E testing.

### F3 — MEDIUM: ARCHITECTURE.md schema is stale

**Severity:** Medium
**Verdict:** False claim
**Evidence:** ARCHITECTURE.md's snapshot schema does not include the `raw_html` column that was added to `store.py`. The actual schema has 8 columns; the doc shows 7.

### F4 — MEDIUM: Config file documented but not implemented

**Severity:** Medium
**Verdict:** False claim
**Evidence:** ARCHITECTURE.md documents a `skillwatch.yaml` config file format with `ignore_patterns`, `delay_seconds`, `user_agent`, `db_path`, and `max_redirects` settings. No code in the project reads a config file. The CLI uses only command-line arguments. The `--config` flag does not exist.

### F5 — LOW: ARCHITECTURE.md says max_redirects: 3, code uses 5

**Severity:** Low
**Verdict:** False claim
**Evidence:** `docs/ARCHITECTURE.md` line 114: `max_redirects: 3`. `skillwatch/fetcher.py` line 14: `_MAX_REDIRECTS = 5`. The doc is stale from an earlier iteration.

### F6 — LOW: Dead code — `diff_stats` and `Flag.to_dict()`

**Severity:** Low
**Verdict:** Partial work
**Evidence:** `differ.py::diff_stats()` is defined and tested but never imported or called by any module. `detector.py::Flag.to_dict()` is defined but never called. Both are vestigial from planned features that were never wired up.

### F7 — INFO: Overall test coverage is 74%

**Severity:** Informational
**Verdict:** Confirmed
**Evidence:** `pytest --cov=skillwatch --cov-report=term-missing` reports 74% overall. Key gaps: `fetcher.py` at 41% (happy path untested), `cli.py` at 53% (scan/history/alert untested), `ssrf.py` at 71% (PinnedDNSAdapter untested by unit tests, only by E2E), `parser.py` at 78% (YAML/fallback paths untested).

---

## What was verified as genuinely working

| Feature | Evidence |
|---|---|
| URL extraction from .md, .json, .txt | 12 parser tests + E2E with sample_skill.md |
| SSRF blocking (private IPs, loopback, link-local, IPv4-mapped IPv6, schemes) | 13 SSRF tests + 5 fetcher SSRF tests + E2E |
| DNS pinning via PinnedDNSAdapter | E2E test against docs.python.org (HTTPS, SNI working) |
| Per-hop redirect validation | Programmatic test with `responses` library (verified manually) |
| Redirect limit enforcement (5 hops) | Programmatic test with `responses` library (verified manually) |
| Content hashing (SHA-256 of trafilatura-extracted text) | E2E: two scans of same URL produce identical hashes |
| Change detection (hash comparison) | E2E: two scans show "unchanged" |
| Suspicious pattern detection (6 rules) | 10 detector tests covering all rule types |
| HTML old-vs-new comparison (no false positives from pre-existing elements) | 7 HTML comparison tests |
| Escape sequence stripping (CSI, OSC, DCS, Fe, C1) | 9 escape stripping tests |
| Escape stripping at display time (defence in depth) | 1 formatter test with malicious diff content |
| SQLite storage (URLs, snapshots, alerts, context manager) | 18 store tests |
| CLI error handling (missing files, unknown URLs, nonexistent alerts) | E2E exercise of all error paths |
| Deduplication reporting ("already monitored") | E2E + 1 store test |
| Ruff lint clean | `ruff check skillwatch/ tests/` — 0 errors |

---

## What needs fixing

1. **F1:** Fix `@responses.activate` on TestFetchUrlHTTP — apply per-method or use `responses.mock` as context manager
2. **F2:** Add tests for `scan`, `history`, `alert` CLI commands (requires mock HTTP or test fixtures)
3. **F3:** Update ARCHITECTURE.md snapshot schema to include `raw_html` column
4. **F4:** Remove the config file section from ARCHITECTURE.md (it's not implemented and isn't needed for v0.1)
5. **F5:** Change ARCHITECTURE.md `max_redirects: 3` to `5` or remove the stale config section entirely (fix in F4 covers this)
6. **F6:** Remove `diff_stats` and `Flag.to_dict()` dead code
