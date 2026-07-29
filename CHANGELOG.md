# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.4.1] - 2026-07-29

**This release exists to publish corrections that were made in the repository and
reached no user.** Version 0.4.0 shipped on 2026-07-29; later the same day three
claims on its page were found to be wrong or incomplete and were corrected here.
Nothing in the published artefact changed until this release, because the PyPI
long description is only regenerated when a version is published.

There are no code changes to the detector. Efficacy figures are unchanged and
remain reproducible with `python3 analysis/measure_efficacy.py`.

### Fixed — claims on the published page

- **Trail of Bits scope and quantifier.** The 0.4.0 page states that every public
  skill scanner tested "was bypassed in under an hour". The source
  ([Judson and Hess, 3 June 2026](https://blog.trailofbits.com/2026/06/03/the-sorry-state-of-skill-distribution/))
  writes: *"it took us less than an hour to conceive and implement three of the
  four malicious skills … The fourth malicious skill took a few hours."* The hour
  belongs to **building three of four attacks**, not to bypassing scanners, and
  not to all four. The scope is the five scanners they tested, not every scanner
  in existence. OWASP's incident timeline carries the compressed form and this
  project repeated it.
- **OWASP AST05 mitigations, with OWASP's own wording restored.** The 0.4.0 page
  says the mitigations listed against AST05 are "source inventory, content
  pinning, repeated rescanning" and that they "describe what this tool does". The
  [AST05 page](https://owasp.org/www-project-agentic-skills-top-10/ast05.html)
  lists **six**: *Pin and verify referenced content; Prefer inlining over
  fetching; Allowlist permitted reference domains; Audit references transitively;
  Maintain fleet-wide visibility of referenced sources; Rescan continuously.* The
  three-item phrasing came from the compressed summary row on the project index,
  and it altered OWASP's **"continuous"** to "repeated" to fit this project's
  periodic-only constraint. SkillWatch covers one of the six and part of two more.
- **`hidden_content` coverage disclosed.** The check reads an element's inline
  `style` attribute for a lower-case `display:none` or `visibility:hidden` and
  nothing else. It does not fire on upper- or mixed-case declarations, `<style>`
  blocks, external stylesheets, the HTML `hidden` attribute, `aria-hidden`,
  off-screen positioning, `opacity:0`, `font-size:0`, `height:0`, `clip-path` or
  `text-indent`. Stylesheet-based hiding is the largest of these in practice.
  **Absence of the flag is not evidence that nothing is hidden.** The code gap is
  unchanged and remains open; only the disclosure is new.

### Added — machinery so this cannot recur silently

- **`scripts/claim_rules.py`** — the claim rules as a shared module with one
  entry point, `find_violations(text, source=...)`, so the same rules can run
  against repository files, a built artefact, and the live page.
- **`scripts/check_release_claims.py`** — a **blocking pre-release gate** over
  `README.md` and a freshly built sdist's `PKG-INFO`. Offline and deterministic.
- **`scripts/check_published_claims.py`** — a **non-gating report** over the live
  PyPI long description, which also reports claim-bearing drift between the
  published text and `README.md` at HEAD. It exits non-zero when it cannot reach
  PyPI, because a check that could not inspect its subject has not passed. It is
  deliberately not a release gate: only a release can make the live page correct,
  so gating on it would deadlock.
- **`tests/test_claim_rules.py`** — tests for the rules engine itself, including
  a positive fixture per negative rule.

### Fixed — a rule that could never fire

One of the negative claim rules shipped vacuous. Its span was `[^.\n]{0,60}`
where the text it was written to catch had 94 characters and a newline in that
position, so it never matched and passed against the very README it was meant to
flag. Widened to `[^.]{0,160}` and now proven to fire. **A rule that has never
fired has not been tested**; every negative rule now has a positive fixture.

### Changed

- **Ship condition 2 re-specified from "precision ≥75%" to "benign false-positive
  rate ≤30%".** Precision is `TP/(TP+FP)`, so it depends on the benign:malicious
  ratio of the corpus it was measured on (~38:47 here). A real change stream is
  overwhelmingly benign, so a corpus precision figure does not transfer to
  deployment and should never have been published as though it did. The
  false-positive rate is measured on benign items only and is ratio-independent.
  Condition 2 now PASSES at 4/32 (12.5%, CI [5.0%, 28.1%]).

  The remedy previously recorded against this condition — "more benign items are
  needed" — was arithmetically backwards: benign items can only add false
  positives, taking precision to 21/29 (72.4%, lower bound 54.3%). Reasoning in
  `SHIP-READINESS.md`.
- **Base-rate warning added to every surface publishing precision** (README,
  `docs/llms.txt`, `docs/index.html`). The claim "about 1 in 6 alerts is a false
  positive" was a deployment claim the measurement could not support and has been
  removed.

### Added

- **Why the published figures moved between 0.3.0 and 0.4.0**, decomposed in the
  README. Overall recall 15/20 (75.0%) → 21/35 (60.0%) is entirely a corpus-mix
  effect: `skillwatch/detector.py` is byte-identical across the two releases, and
  the malicious corpus went from 50% evasive to 71% evasive. Fifteen evasive items
  were added and six are caught. Nothing regressed. See the retraction below for
  what in that comparison is checkable and what is inference.
- **HTML corpus results published** (6/6 precision and recall, both 95% CI
  [61.0%, 100.0%]), and holdout results kept alongside the original corpus. All
  three corpora now appear in the README.
- **Which flags produce the false positives.** All five across both benign corpora
  (38 items) come from three delta checks: `new_exec_command` (2/38),
  `new_domains` (2/38), `new_base64` (1/38). The content checks
  (`prompt_injection`, `credential_reference`, `unicode_homoglyph`) produced 0/38,
  95% CI [0.0%, 9.2%]. Deleting the three delta checks would zero the corpus
  false positives and drop overall recall to 16/35 (45.7%); the trade is not worth
  taking.
- **OWASP AST05 positioning.** SkillWatch addresses AST05 "Untrusted External
  Instructions" in the OWASP Agentic Skills Top 10 (v1.0, 2026 Edition). That
  project is **early-stage, not a flagship standard** (its own pages disagree on
  the tier), and that qualifier is mandatory in every claim. The scanner-bypass
  finding cited there is Trail of Bits', not OWASP's. AST07 "Update Drift" is a
  partial fit only.
- **`OPEN-ITEMS.md`** — a tracked continuity ledger with first-raised dates,
  replacing per-session handover tables that lost items between sessions.
- **`tests/test_efficacy_harness.py`** (14 tests). The harness producing every
  published efficacy figure previously had no tests at all.

### Fixed

- **`specifier_allows` failed open in the dependency-floor auditor.** An
  unparseable requires_python clause — a transposed operator like `=>3.10`, a
  non-numeric bound — was silently reported as satisfied, in the check that gates
  the release. Replaced with a three-valued `SpecifierVerdict`
  (ALLOWED/EXCLUDED/UNEVALUABLE) in which only ALLOWED is truthy, so a caller
  writing `if verdict:` fails closed. Unevaluable metadata is now an audit
  failure reported distinctly from incompatible metadata. `_parse_version_strict`
  backs the correctness path, kept separate from `_version_key`'s ordering path.
- **The HTML corpus report published bare percentages.** It printed
  `Precision: 100.0%` with no interval while the other two reports carried Wilson
  bounds — the exact failure the project corrected elsewhere. 6/6 is 100% with a
  lower bound of 61.0%.
- **`analysis/` was outside the CI lint and type gate** despite
  `measure_efficacy.py` being tracked as evidence for published figures. Added to
  both. This surfaced a real omission: `fp_rate_standard` was computed and then
  dropped from the returned results while its four siblings were kept; it is now
  returned.
- **Removed a citation that did not support its claim.** The README cited
  arXiv 2508.12538 as independent corroboration of the bait-and-switch technique.
  That paper is MCPXKIT, an offensive MCP toolkit, and its abstract does not
  document URL content swapping. Replaced with arXiv 2605.05274 (SIGIL), which
  addresses the audit-runtime gap directly.
- **Retracted an inference presented as a check.** The README stated that on the
  original ten evasive items "the same five are caught". The 0.3.0-era corpus was
  never committed — `benign/`, `adversarial_a/` and `adversarial_b/` all entered
  version control in a single commit at the time of the expansion — so there is no
  earlier tracked state to diff against and the claim could not have been
  verified. The README now states what is checkable (`detector.py` is
  byte-identical across the two releases) and marks the rest as consistent-with
  rather than proven.
- **Stale documentation corrected.** `CLAUDE.md` said ten modules (there are 13)
  and v0.2.0 (PyPI serves 0.3.0, `main` is 0.4.0). It also gained the precision
  and OWASP AST05 rules so future sessions inherit them.
  `docs/skillwatch-overview.js` (v0.3.0, 323 tests, 12 modules) was edited too,
  but that file is gitignored and untracked, so the edit is **not** part of this
  release and does not persist outside one working copy. Tracked as open item 31.

## [0.4.0] - 2026-07-29

Minor, not patch: this adds two subcommands. The 0.3.1 entry below is retained as
a separate record because the security fix was developed and merged on its own,
without features attached; both ship in this release.

### Security

- **Raised `wheel` from unbounded to `>=0.46.2`.** Releases 0.40.0 through 0.46.1
  are affected by **CVE-2026-24049** ([GHSA-8rrh-rw8j-w5fx](https://github.com/advisories/GHSA-8rrh-rw8j-w5fx), CWE-22, rated HIGH) — arbitrary
  file permission modification via path traversal in `wheel unpack`. `wheel` is a
  build requirement and previously declared no lower bound at all, so every
  published release was permitted.

  **Version exposure and practical exposure are not the same thing, and both are
  stated here.** The *version* exposure was real and continuous: an unbounded
  requirement permitted every affected release for the project's entire life.
  The *practical* exposure was nil: the vulnerable code is
  `wheel.cli.unpack.unpack`, reached by running `wheel unpack` against an
  attacker-supplied wheel, which this project never does — it uses `wheel` only
  as a build backend. The advisory is `CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:H`:
  a local vector requiring user interaction. The floor is raised regardless,
  because a declared floor is a contract about what a resolver may install, not
  a judgement about how likely we are to trip over it.
- **Every remaining unbounded dependency now declares a floor**: `pytest-cov>=7.1.0`,
  `types-PyYAML>=6.0.12.20260518`, `types-requests>=2.33.0.20260518`,
  `types-beautifulsoup4>=4.12.0.20250516`. Each was checked to still support
  Python 3.10.
- **`scripts/audit_dependency_floors.py` now fails on any requirement with no
  lower bound**, and the allowlist that previously exempted them is gone. Auditing
  only *declared* floors was blind to the maximum-exposure case: a dependency with
  no bound permits every release ever published. This was not theoretical —
  `pytest-cov` had no floor and the `lowest-direct` CI leg resolved it to **0.6**, a
  2010 release, while the audit reported success. The `wheel` CVE above was found
  the moment that blind spot was closed.

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
