# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.3.0] - 2026-07-11

### Added
- Verifiable content ledger: every scan now records what each URL served as an append-only, hash-chained entry in a new `ledger` table. Unlike the snapshot cache (capped at 50 per URL), the ledger keeps every observation permanently as a tiny hash entry, so the tamper-evident history survives snapshot pruning. New `skillwatch/ledger.py` defines the versioned hash spec (fields JSON-encoded before hashing, so a separator inside a field cannot cause a collision) and a pure `verify_chain`.
- `skillwatch verify`: recomputes the ledger hash chain, reports the first entry that was edited, reordered, or deleted (exits 1 on a broken chain, 0 when intact), and prints the chain **head** — a hash committing to the whole history.
- External anchoring with pluggable backends, so you are not tied to one authority. (1) Publish the head by hand and re-check with `skillwatch verify --against <head>` (zero dependencies). (2) `skillwatch anchor` gets a signed RFC 3161 timestamp from a public authority (freeTSA.org by default) under the optional `[anchor]` extra. (3) `skillwatch anchor --method git --repo <path>` commits the head to a git repo you push — an independent, timestamped record that needs no timestamp authority and no extra dependency. Anchors are stored in a new `anchors` table, and `skillwatch verify` now automatically checks every recorded anchor — confirming the anchored head is still in the chain and cryptographically verifying RFC 3161 tokens — so a full-chain rewrite that plain `verify` would accept is caught. Only a hash ever leaves the machine; the core stays offline (freeTSA's CA cert is bundled for offline verification).

### Changed / Security
- SSRF: IP validation now blocks on the stdlib classification (`is_private`/`is_reserved`/…) as a future-proof baseline, plus an expanded explicit list (240.0.0.0/4, 192.0.0.0/24, 198.18.0.0/15, TEST-NETs, IPv6 documentation), closing gaps for reserved/benchmark ranges.
- Detection input is capped at 256 KB before regex/library work, giving a deterministic bound on scan cost against an adversarially large page (measured ~linear).
- Ledger verification and export now stream rows from an ordered cursor instead of loading the whole ledger into memory, so they scale to very large ledgers; export writes atomically via a temp file.
- `skillwatch ledger` / `skillwatch ledger --export PATH`: show recent entries, or write the full ledger as portable JSON that re-verifies with `skillwatch.ledger.verify_chain` — no database access required, so a third party can independently confirm a record you produce.
- `docs/LEDGER.md`: the exact hash construction, what `verify` checks, the anchoring workflow, the honest scope (a local chain is tamper-evident and independently verifiable; publishing the head makes history up to it tamper-proof), and how to re-verify an export yourself.
- `skillwatch sources`: detects when a tracked SKILL.md or MCP config is edited or gains/loses URL references (a local rug-pull check inspired by MCP-Scan's tool pinning). New references are added to monitoring automatically; exits 1 on drift.
- `scan --output sarif`: SARIF 2.1.0 output for GitHub Code Scanning, so findings appear in the Security tab alongside static scanners like Cisco skill-scanner and SkillTotal.
- Plain-language alert output: each of the 13 flag codes now shows an ordinary-English explanation plus a universal "what to do", with the raw code kept in parentheses for power users. JSON output is unchanged.
- `docs/UNDERSTANDING-ALERTS.md`: a plain-language guide to every flag and how to triage it (about 1 in 5 alerts is a false alarm).
- Examples-first `--help` with a copy-paste first-run quickstart.
- `[i/total]` progress counter during scans (non-quiet, non-JSON output).
- "Who this is for / not for" section in the README (honest audience scope).
- `docs/llms.txt` and a README FAQ for discoverability.
- CI coverage floor (`--cov-fail-under=90`).

### Changed
- Error messages now state the fix (missing file, blocked URL).
- User-facing copy run through a plain-language pass.

### Fixed
- README no longer claimed "Not on PyPI" (the package is published).
- Corrected a stale "38 patterns" code comment (there are 32) and stale test-count figures.

## [0.2.0] - 2026-07-01

### Added
- 32 ATR-derived prompt injection patterns covering 7 languages (EN, DE, ES, FR, AR, RU, SR/HR) plus obfuscation variants (base64, zero-width, spaced letters, URL-encoded, ALL-CAPS, markdown)
- Unicode homoglyph detection via the `confusable_homoglyphs` library (Unicode Consortium official data)
- Data URI payload detection in text content
- Meta refresh redirect detection (new `<meta http-equiv="refresh">` elements)
- Data URI embed detection in iframes, embeds, and objects
- Diff-based HTML comparison (only newly introduced elements trigger alerts)
- `--output json` flag for machine-readable scan output
- `--preset docs` with 6 built-in ignore patterns (timestamps, UUIDs, build hashes, version params, nonces)
- `--user-agent` flag for custom User-Agent string
- `--db` flag works both before and after the subcommand
- GitHub Action (`action.yml`) for CI/CD integration
- CI workflow testing Python 3.10 through 3.13
- PyPI trusted publishing workflow (OIDC, zero secrets)
- SSRF protection with DNS pinning and per-hop redirect validation
- First-run guidance when database is empty

### Changed
- Detection patterns expanded from 2 English-only regexes to 32 ATR-derived patterns
- Homoglyph detection upgraded from 30-entry hand-built map to Unicode Consortium confusables database
- Default User-Agent changed from identifiable "SkillWatch/0.1" to standard browser UA
- ConnectionError messages sanitised to prevent proxy hostname leakage

### Fixed
- Base64 false positives on hex digests: pure hexadecimal strings (SHA-1, SHA-256, etc.) no longer trigger `new_base64`
- URL path fragments no longer match the base64 character class
- Import fragility: malformed prompt injection patterns now raise a descriptive `ValueError` instead of a bare `re.error`
- ReDoS on user-supplied `--ignore-pattern`: regex substitutions bounded by 2-second timeout
- Variable shadowing in homoglyph detection

## [0.1.0] - 2026-06-26

### Added
- Initial release
- URL extraction from SKILL.md, MCP config (.json/.yaml), and plain URL lists
- SHA-256 content hashing and change detection
- SQLite local storage
- Basic suspicious pattern detection (exec commands, base64 strings, credential keywords, new domains, major deletion)
- SSRF protection (private IP, loopback, link-local, cloud metadata blocking)
- Escape sequence stripping at fetch and display time
- CLI commands: add, add-url, remove, scan, list, history, alerts, alert
