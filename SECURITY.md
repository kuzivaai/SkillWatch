# Security Policy

## What SkillWatch does

SkillWatch fetches arbitrary URLs to monitor content changes. It includes SSRF protection, DNS pinning, escape sequence stripping, and per-hop redirect validation. All data is stored locally in SQLite. Nothing is sent externally.

## Reporting a vulnerability

If you find a security issue in SkillWatch, please report it by opening a GitHub issue. This is a personal open-source project, not infrastructure software, so public disclosure is appropriate.

For issues involving the SSRF protection, DNS pinning, or escape sequence stripping specifically, please email mkuziva@gmail.com first so the fix can be prepared before disclosure.

**Expected response time:** Best-effort acknowledgement within 7 days. This is a solo-maintained project; response times may vary.

## Supported versions

Only the latest release is supported with security fixes.

| Version | Supported |
|---------|-----------|
| 0.2.x   | Yes       |
| < 0.2   | No        |

---

## Security Evidence Register

Last updated: 2026-07-02. Commit: 9f79b1e (code fixes applied same date).

### SEC-001: User-Supplied Regex ReDoS (FIXED)

**Severity:** Medium (requires intentional crafted input via --ignore-pattern CLI flag)
**Affected files:** skillwatch/fetcher.py
**Status:** Fixed. User-supplied regex substitutions now run in a worker thread with a 2-second timeout. If the pattern causes catastrophic backtracking, the substitution is skipped and a warning is printed to stderr.

### SEC-002: ConnectionError Sanitisation (Mitigated)

**Severity:** Low (mitigated)
**Affected files:** skillwatch/fetcher.py:154-157
**Description:** `str(ConnectionError)` from requests could expose internal proxy hostnames. Sanitised to generic message: "Connection failed (DNS, network, or proxy error)".

### SEC-003: Dependency Audit (Time-Varying)

**Severity:** Medium (transitive, not direct)
**Note:** This entry is time-varying. It depends on the vulnerability advisory database at the time of the audit. Re-run `pip-audit` in a clean virtualenv to get current results.

**Audit date:** 2026-07-02
**SkillWatch direct dependencies (5 packages):** zero known vulnerabilities.
**Transitive vulnerabilities found (in polluted dev venv):**

| Package | Version | CVEs | Notes |
|---|---|---|---|
| pip | 24.0 | 5 | Build tool, not a runtime dependency |
| cryptography | 44.0.3 | 4 | Transitive (via urllib3/requests chain) |
| nltk | 3.9.4 | 1 | Transitive (via trafilatura) |

Packages transformers, llm-guard, and torch are present in the dev venv from evaluation work and are NOT SkillWatch dependencies.

### SEC-004: Secret Scan (Clean)

**Severity:** None (no findings)
**Method:** Pattern-based grep for sk-, api_key=, token=, password=, secret=, AKIA, ghp_ across all Python source. Also scanned for .env references and base64 constants.
**Result:** No credential patterns found. The sole .env reference is in detector.py (a detection regex searching monitored content for .env strings, intentional).

### SEC-005: SSRF Protection Coverage

**Severity:** Low (comprehensive)
**Description:** 20 SSRF test methods in test_ssrf.py covering 16 blocking categories, plus 6 SSRF-related tests in test_fetcher.py and 1 in test_cli.py (27 SSRF-related tests total). Coverage: private IPs (10.x, 172.16.x, 192.168.x), loopback, link-local, localhost, file/ftp schemes, IPv4-mapped IPv6, credentials in URL, IPv6 multicast, 6to4, NAT64, decimal IP, hex IP, zero IP. Cloud metadata (169.254.169.254) blocked by link-local range. DNS pinning thread-safe (2 tests).

### SEC-006: SQLite Transaction Isolation

**Severity:** Low (single-threaded CLI, safe)
**Affected files:** skillwatch/store.py:113-126
**Description:** Uses isolation_level="IMMEDIATE" and wraps add_snapshot INSERT + prune DELETE in a single `with self._conn:` block. Correct for single-threaded CLI. Multi-threaded use would raise ProgrammingError (no check_same_thread=False).
