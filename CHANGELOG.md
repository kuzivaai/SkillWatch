# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.4.0] - unreleased

Minor, not patch: this adds two subcommands. The 0.3.1 security fix shipped
separately so that users who wanted only the dependency fix were not required to
take new features with it.

### Added

- `skillwatch cloak <url>` — fetches a URL under three User-Agent personas
  (browser, agent, bot) through the existing SSRF-protected fetcher and reports
  whether the server returns different content to different clients. Exit 0
  clean, 1 varies, 2 insufficient data. **Honestly scoped:** User-Agent only. It
  uses no proxies, so it cannot see geo- or IP-conditional cloaking, and it adds
  no new trust cost — it contacts only the URL you pass it. One-shot, in keeping
  with periodic-not-continuous.
- Local false-positive adaptation. `skillwatch alert <id> --dismiss` / `--confirm`
  records one decision per flag in a new `flag_feedback` table. A flag is demoted
  for a URL once dismissed twice with no confirmation, aggregated by
  `(url_id, flag_code)`. Demoted flags are annotated "(previously dismissed)" —
  **shown, not hidden**; the alert is never suppressed or deleted. `skillwatch
  feedback` lists the decisions, `--reset` clears them, and removing a URL clears
  its feedback. Counts only: no model, no network, nothing leaves the machine.
- `docs/adr/0001-two-plane-architecture.md` and the Plane-1 / Plane-2 specs.
  Plane-1 §A (the signed pattern feed) and all of Plane 2 are specification only
  and are not implemented.

## [0.3.1] - 2026-07-29

### Security

- **Raised the `rfc3161-client` floor from `>=1.0` to `>=1.0.6`** in both the `[anchor]` and `[dev]` extras. Every release below 1.0.6 is affected by **CVE-2026-33753** ([GHSA-3xxc-pwj6-jgrj](https://github.com/trailofbits/rfc3161-client/security/advisories/GHSA-3xxc-pwj6-jgrj), CWE-295, published 8 April 2026), an authorisation bypass in timestamp-response verification: because the library picked the leaf certificate out of the unordered PKCS#7 bag by a naive heuristic rather than the RFC 3161 `ESSCertID` binding, an attacker holding any genuine timestamp from a trusted authority could append a forged certificate and defeat the client's authority pinning. The advisory's worked example impersonates **freeTSA — SkillWatch's default anchoring backend** — so this bore directly on the guarantee `skillwatch anchor` and `skillwatch verify` are meant to provide. Anchors already recorded are unaffected in themselves; re-verify them once upgraded.

  The same range also covers **CVE-2025-52556** ([GHSA-6qhv-4h7r-2g9m](https://github.com/trailofbits/rfc3161-client/security/advisories/GHSA-6qhv-4h7r-2g9m), CWE-347, rated Critical), an insufficient signature check fixed in 1.0.3. In practice that one was not reachable here: every affected release (1.0.0–1.0.2) is yanked from PyPI, so a resolver would not have selected it for `>=1.0`. The reachable exposure was 1.0.3–1.0.5, via CVE-2026-33753.

- **Raised every other dependency floor that permitted a published advisory**, which is the same defect rather than a separate one: `requests>=2.32.4` → `>=2.33.0`, `cryptography>=42` → `>=48.0.1`, `pytest>=8.0` → `>=9.0.3`, and the build requirement `setuptools>=68.0` → `>=83.0.0`. Floors are now held at the lowest release free of known advisories, not the lowest release that happens to work. The full test suite passes against an environment pinned to exactly these floors, so they are a tested configuration rather than an assumed one.

### Added

- `scripts/audit_dependency_floors.py` and a blocking `security` job in CI, so this class of defect cannot recur silently. The job runs two checks that catch different failures: `pip-audit` inspects the versions actually installed, while the floor audit inspects the versions `pyproject.toml` *permits* — which is what a downstream user resolving against an older index or a lockfile may get. A vulnerable floor is invisible to `pip-audit` alone, which is precisely how `rfc3161-client>=1.0` stayed green in CI while permitting a known-vulnerable resolution.
- A `lowest-direct` CI job (`uv run --python 3.10 --resolution lowest-direct`) that runs the suite against the lowest version each declared floor permits, so the floors are a configuration that has actually been executed rather than numbers nobody has run. `uv run` rather than `uv sync`, because with a lockfile present `uv sync --resolution lowest-direct` resolves above the declared minimums and would test nothing.
- `docs/DEPENDENCY-FLOORS.md`, documenting the three checks and their caveats — including that `lowest-direct` exercises the *build* path at the `setuptools` floor, and that a requirement left without a floor (currently `pytest-cov`) can resolve to a decade-old release on that leg.

### Changed

- Bounded `ruff` (`>=0.15.21,<0.16`) and `mypy` (`>=2.2,<2.3`) instead of leaving them floating. Their default rule sets change between minor releases, so an unpinned tool makes CI go red on an upstream release rather than on a code change — ruff 0.16.0 did exactly that, reporting 27 findings on unchanged, previously green code. Bumping these bounds is now a deliberate, reviewed change rather than something an unrelated push absorbs.

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
