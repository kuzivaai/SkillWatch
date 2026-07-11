# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
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
