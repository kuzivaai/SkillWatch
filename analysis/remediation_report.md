# SkillWatch Remediation Report -- Phase 4

**Date:** 2026-07-03
**Branch:** remediation/2026-07
**Baseline commit:** 43816f1 (main, pre-remediation)
**HEAD at report time:** f8f7ebc
**Author:** Kuziva Muzondo
**Generator:** Claude Code (Opus 4.6, 1M context)

---

## 1. Before/After Metrics

All figures are from `analysis/measure_efficacy.py` run against the respective corpora. Labels: VERIFIED = re-run in Phase 3 adversarial verification session; READ = taken from ledger/dossier without independent re-run.

### 1a. Core Metrics (Original Corpus)

| Metric | BEFORE (43816f1) | AFTER (remediation/2026-07) | Delta |
|--------|-------------------|-----------------------------|-------|
| Tests | 213 | 236 | +23 [VERIFIED] |
| Line coverage | 94% (920/52) | 95% (994/54) | +1pp [VERIFIED] |
| Precision | 72.2% (13TP / 5FP) | 78.9% (15TP / 4FP) | +6.7pp [VERIFIED] |
| Recall (overall) | 65.0% (13/20) | 75.0% (15/20) | +10.0pp [VERIFIED] |
| Evasive recall | 30.0% (3/10) | 50.0% (5/10) | +20.0pp [VERIFIED] |
| FP rate (overall) | 15.6% (5/32) | 12.5% (4/32) | -3.1pp [VERIFIED] |
| FP rate (hash subset) | 25.0% (2/8) | 12.5% (1/8) | -12.5pp [VERIFIED] |

### 1b. Holdout v2 Corpus (18 items, committed before detector changes)

| Metric | Value | Label |
|--------|-------|-------|
| Precision | 90.0% (9TP / 1FP) | VERIFIED |
| Recall | 75.0% | VERIFIED |
| Evasive recall | 75.0% (9/12) | VERIFIED |
| FP | 1/6 | VERIFIED |

Holdout evasive recall (75%) exceeds original corpus evasive recall (50%). This is the expected signature of generalisation, not overfitting. The 3 holdout FNs (HE-01, HE-02, HE-10) are all semantic evasions that fall outside the regex detector's design scope. [VERIFIED: Phase 3, Check 3]

### 1c. HTML Corpus (12 items)

| Metric | Value | Label |
|--------|-------|-------|
| Precision | 100% (6TP / 0FP) | VERIFIED |
| Recall | 100% (6/6) | VERIFIED |
| FP | 0/6 | VERIFIED |

All 5 HTML flag codes (suspicious_script, iframe_detected, hidden_content, meta_refresh_redirect, data_uri_embed) are now exercised. A bug was found and fixed: HTML checks were short-circuited by an early return guard when the text diff was empty. [VERIFIED: Phase 3, Check 2]

---

## 2. Disposition Table

### Gap Analysis (G-01 to G-12)

| ID | Description | Status | Evidence / Notes |
|----|-------------|--------|------------------|
| G-01 | Zero users, zero demand signal | DECISION-REQUIRED | `analysis/demand_validation_memo.md` written with 3 options (make public and wait; write technical post; post in community). No recommendation made -- owner decision. Zero stars/forks/external users confirmed. [VERIFIED] |
| G-02 | Evasive recall is 30% | FIXED | Canonicalisation layer added (HTML comments, reversed text, ROT13). Evasive recall 30% -> 50% on original corpus, 75% on holdout. Precision 72.2% -> 78.9%. SRI hash exclusion reduced hash FP from 25% to 12.5%. [VERIFIED] |
| G-03 | No maintenance owner or pattern-update cadence | PREPARED | `MAINTENANCE.md` drafted naming Kuziva Muzondo as owner with quarterly pattern review cadence. Status: PROPOSED, pending owner ratification. Becomes FIXED when ratified. [READ] |
| G-04 | Premise source COI (AIR conflict of interest) | ASSESSED | `analysis/source_independence_memo.md` assesses CSA and arxiv sources as LIKELY INDEPENDENT of AIR. arxiv authors at Tsinghua/CAS/Swinburne. CSA note attributed to CSA's own research initiative. Not VERIFIED (full affiliation check infeasible). The COI disclosure remains in README regardless. [READ] |
| G-05 | No scheduled monitoring capability | FIXED | `examples/scheduled-monitoring.yml` added with copy-paste GitHub Actions cron workflow. README section added pointing to it. [VERIFIED] |
| G-06 | confusable_homoglyphs frozen at Unicode 12.0 | FIXED | `scripts/refresh_confusables.py` added. `skillwatch/data/PROVENANCE.md` documents data currency. Assessed as low practical impact: Unicode 13-16 confusables are rare in real attacks. [READ] |
| G-07 | No type checker | FIXED | mypy added with pragmatic-strict config in `pyproject.toml`. 0 violations. CI step added to `.github/workflows/ci.yml`. [VERIFIED] |
| G-08 | HTML-level efficacy unmeasured | FIXED | 12-item HTML corpus (`analysis/corpus/html_v1/`) covering all 5 HTML flag codes. Bug found and fixed: HTML checks short-circuited on empty text diff. [VERIFIED] |
| G-09 | No end-to-end integration test | FIXED | Hermetic E2E test (`tests/test_e2e.py`) with ephemeral HTTP server. Tests full pipeline: add URL -> scan -> detect change -> generate alert. No external network dependency. [VERIFIED] |
| G-10 | Landing page exists but not deployed | PREPARED | `SHIP-READINESS.md` has publish-day checklist including GitHub Pages enablement steps. Cannot deploy until repository is public and HOLD is lifted. [READ] |
| G-11 | PyPI badges link to unpublished package | FIXED | Badges removed from README. `pip install skillwatch` changed to install-from-source (`pip install git+https://...`). Removed items logged in `SHIP-READINESS.md` for restoration on publish day. [VERIFIED] |
| G-12 | Precision below 75% threshold | FIXED | Precision 78.9% on original corpus, 90.0% on holdout. Exceeds 75% target on both corpora. [VERIFIED] |

### Risk Register (R-01 to R-05)

| ID | Description | Status | Evidence / Notes |
|----|-------------|--------|------------------|
| R-01 | Publishing to zero demand damages consulting credibility | OPEN (mitigated) | HOLD remains in force. `demand_validation_memo.md` provides 3 low-effort options for generating a demand signal. Risk cannot be closed until demand evidence exists or the owner decides to archive. [READ] |
| R-02 | Pattern set becomes stale without maintenance | PREPARED (pending ratification) | `MAINTENANCE.md` proposes quarterly review cadence, mandatory efficacy re-run on detector changes, and bypass intake path. Pending owner ratification. The risk remains open until the cadence is ratified and the first review is completed. [READ] |
| R-03 | Evasive recall misunderstood as detection capability | MITIGATED | README updated with honest ceiling statement. Evasive recall improved from 30% to 50%, reducing the misinterpretation gap. Ceiling statement explains what the detector cannot catch (semantic evasions). [READ] |
| R-04 | confusable_homoglyphs abandoned, breaks on future Python | MITIGATED | Refresh script (`scripts/refresh_confusables.py`) enables data update without depending on library releases. Practical impact assessed as low. [READ] |
| R-05 | Prior clones (58 unique) retain sensitive personal data | ACCEPTED | Cannot be undone. 0 forks, 0 external page views. Personal data was removed from current history via git-filter-repo. Risk is residual and unmitigable. [VERIFIED] |

### Opportunities (O-01 to O-03)

| ID | Description | Status | Evidence / Notes |
|----|-------------|--------|------------------|
| O-01 | Publish as change-monitor (not detector) | DONE (pre-existing) | Repositioning completed in prior audit chain. README opening line: "Periodic URL content monitoring." No changes made in this remediation. [VERIFIED] |
| O-02 | Integrate with existing scanners | DOCUMENTED | `SHIP-READINESS.md` documents complementary positioning. No integration code written (out of scope for HOLD). [INFERRED from SHIP-READINESS.md] |
| O-03 | GitHub Marketplace Action | PREPARED | `action.yml` is functional. Marketplace metadata (icon: shield, color: blue) configured. Listing blocked until repository is public. Procedure documented in `SHIP-READINESS.md`. [READ] |

### Open Questions (Q-01 to Q-05)

| ID | Question | Status | Evidence / Notes |
|----|----------|--------|------------------|
| Q-01 | Is there any user demand? | STILL NO | Zero stars, zero forks, zero external users. `demand_validation_memo.md` written. [VERIFIED] |
| Q-02 | Are CSA and arxiv sources independent of AIR? | ASSESSED (LIKELY INDEPENDENT) | `analysis/source_independence_memo.md` concluded LIKELY INDEPENDENT based on author affiliations and source attribution. Not fully VERIFIED (individual contributor affiliations cannot be exhaustively checked). [READ] |
| Q-03 | Should the repository be made public? | DECISION-REQUIRED | Blocked on Q-01. Cannot generate demand signal while private. Circular dependency documented in `demand_validation_memo.md`. [INFERRED] |
| Q-04 | What is the pip-audit result? | ANSWERED | 0 direct-dependency CVEs. 26 transitive-dep CVEs across cryptography (3), nltk (1), pip (5), transformers (16). Measured in Phase 0. [VERIFIED] |
| Q-05 | Does the GitHub Action work end-to-end? | DOCUMENTED | Dry-run procedure written in `SHIP-READINESS.md`. Cannot be tested from within the repository (requires a consuming repository with GitHub Actions runner). [READ] |

---

## 3. Updated HOLD Scoreboard

DECISION.md defines 5 conditions that must all pass before publication (PyPI, GitHub Pages, release tag, or TIL article). Current status mapped to evidence from this remediation:

| # | Condition | Before | After | Evidence |
|---|-----------|--------|-------|----------|
| 1 | Evasive recall >= 50% OR unmissable documentation | PASS (docs route) | **PASS** | Evasive recall is now 50% on original corpus (was 30%), satisfying the 50% threshold directly. Documentation also updated with honest ceiling statement. Both routes now pass. [VERIFIED] |
| 2 | Periodic framing at every claim | PASS | **PASS** | Unchanged. README and landing page use "periodic" throughout. No "continuous" introduced. [VERIFIED] |
| 3 | Named maintenance owner and update cadence | FAIL | **PREPARED** | MAINTENANCE.md names Kuziva Muzondo as owner with quarterly review cadence. Status: PROPOSED, pending ratification. Becomes PASS only when the owner ratifies. [READ] |
| 4 | Independent, non-conflicted premise evidence | FAIL | **LIKELY** | CSA and arxiv sources assessed as LIKELY INDEPENDENT (see analysis/source_independence_memo.md). Not VERIFIED: full affiliation check infeasible. Becomes PASS when at least one source is confirmed independent via a primary-source check. [READ] |
| 5 | Evidence of minimal user demand | FAIL | **FAIL** | Zero stars, zero forks, zero external users. Repository remains private. demand_validation_memo.md provides options but no demand signal has been generated. [VERIFIED] |

**Verdict: 2 firm PASS, 1 PREPARED, 1 LIKELY, 1 FAIL.**

Conditions 1 and 2 are firmly met by measured data. Condition 3 is drafted but requires the owner to ratify the maintenance cadence. Condition 4 is assessed as likely met but the independence of corroborating sources has not been exhaustively verified. Condition 5 remains unmet: zero users, zero demand.

The HOLD cannot be lifted until at minimum: the owner ratifies MAINTENANCE.md (condition 3), and at least one external demand signal is obtained (condition 5). Condition 4 may also warrant a primary-source check of author affiliations before claiming PASS.

---

## 4. Dossier Errata

Four cross-project contamination errors were found in the original dossier (`analysis/SkillWatch_DOSSIER_2026-07-02.md`) during Phase 0 verification. All originate from the dossier generator carrying forward findings from a different project audit (likely Cape-Town-Dash / StreetSignal) into the SkillWatch dossier.

| # | Dossier Location | Erroneous Content | Actual State | Source Project |
|---|-----------------|-------------------|--------------|----------------|
| 1 | Section 9, SEC-001 | "esbuild directory traversal (dev-only, Windows) -- Low -- Accepted" | esbuild does not exist anywhere in the SkillWatch tree. SkillWatch is a pure Python project with no JavaScript build tooling. [VERIFIED] | Node.js project (likely Cape-Town-Dash) |
| 2 | Section 9, SEC-003 | "Consent model (Plausible ungated, Amplitude/Sentry consent-gated) -- Informational" | No analytics scripts of any kind exist in SkillWatch's docs/index.html. [VERIFIED] | Cape-Town-Dash (uses Plausible/Amplitude/Sentry) |
| 3 | Section 9, SEC-003 | "/embed/* pages set X-Frame-Options: ALLOWALL" | No /embed/ directory or pages exist in SkillWatch. [VERIFIED] | Unknown (likely Cape-Town-Dash) |
| 4 | Section 12 | "Risk-band thresholds (67/34/0) duplicated between compute_suburb_safety.mjs and src/utils/sanitize.ts" | StreetSignal invariant. Marked [N/A] in dossier but should not appear at all. [VERIFIED] | StreetSignal (Cape-Town-Dash) |

**No core technical claims were fabricated.** All test counts, coverage figures, efficacy measurements, dependency versions, git state, and repository metadata in the dossier matched exactly on re-verification. The contamination was limited to the security findings section and one engineering health invariant.

---

## 5. Residual-Risk Pre-Mortem

Five risks that survive this remediation, ranked by likelihood x impact:

### Risk 1: Demand never materialises (HIGH likelihood, HIGH impact)

The project has zero users after 7 days of development. The remediation improved code quality and detection efficacy, but quality does not create demand. If the repository is made public and still generates zero interest after 3 months, the entire effort becomes a sunk cost. The demand_validation_memo provides options but none guarantee a result.

**Mitigation:** Set a 90-day clock from the date the repository goes public. If zero external engagement at day 90, archive with a clear README notice. The code quality means it can be revived if demand emerges later.

### Risk 2: MAINTENANCE.md is never ratified (MEDIUM likelihood, MEDIUM impact)

The maintenance cadence is PROPOSED, not ratified. Without explicit owner commitment, the quarterly pattern review will not happen. The 32 injection patterns will degrade as adversarial techniques evolve. This is the same failure mode that existed before remediation, just with better documentation of the proposed process.

**Mitigation:** Owner ratifies MAINTENANCE.md in the next session. A single `git commit` with the word "Ratified" in the file header is sufficient.

### Risk 3: Semantic evasions remain undetectable (HIGH likelihood, LOW impact per-event)

The regex detector cannot catch indirect instruction ("please help me with..."), polite request framing ("it would be great if you could..."), or narrative/story framing ("once upon a time, a helpful assistant..."). Evasive recall is 50% on the original corpus and 75% on the holdout, but 100% of the remaining FNs across both corpora are semantic evasions. This is a fundamental design limitation, not a bug.

**Mitigation:** The honest ceiling statement in README and the "does NOT do" section make this limitation unmissable. The tool is positioned as a change monitor with best-effort triage, not a detection tool. No code change can fix this without adding ML/LLM detection, which is out of scope.

### Risk 4: confusable_homoglyphs library breaks on Python 3.14+ (LOW likelihood, LOW impact)

The library's last release was January 2019. It works on Python 3.10-3.13 today but has no CI testing against newer Python versions. The refresh script mitigates the data currency issue but not a potential import failure on future Python.

**Mitigation:** The refresh script can extract and vendor the confusables data file independent of the library. If the library breaks, vendor the data and replace the 3 call sites with direct lookups. Estimated effort: 2 hours.

### Risk 5: Accidental publication violates HOLD (LOW likelihood, HIGH impact)

A careless `git tag`, `gh release create`, PyPI upload, or GitHub Pages enablement would publish to zero demand. The publish.yml workflow requires manual dispatch and a release event, but human error is always possible.

**Mitigation:** No `schedule:` trigger in any workflow. publish.yml requires manual dispatch. SHIP-READINESS.md documents all 15 publish-day steps. Phase 3 verified no accidental publication side effects. [VERIFIED]

---

## 6. DECISIONS-REQUIRED

Complete list of items awaiting the owner. Each includes a recommendation and the single action to execute.

### Decision 1: Ratify MAINTENANCE.md

**What:** The maintenance cadence (quarterly pattern review, mandatory efficacy re-run on detector changes, bypass intake path) is PROPOSED in `MAINTENANCE.md` but not ratified.

**Recommendation:** Ratify. The cadence is lightweight (4 reviews per year) and the efficacy re-run is already automated (`python3 analysis/measure_efficacy.py`).

**Action:**
```bash
# Change "PROPOSED cadence -- pending owner ratification" to "RATIFIED cadence"
# in MAINTENANCE.md, then commit:
git add MAINTENANCE.md && git commit -m "docs: ratify maintenance cadence"
```

### Decision 2: Make repository public

**What:** The repository is private. No demand signal can be generated while it remains private. This creates a circular dependency with DECISION.md condition 5.

**Recommendation:** Make public. The code quality is high (236 tests, 95% coverage, 78.9% precision), the documentation is honest, and no secrets or personal data remain in the history. The credibility risk of publishing to zero demand (R-01) is lower than the opportunity cost of keeping it private indefinitely.

**Action:**
```bash
gh repo edit kuzivaai/SkillWatch --visibility public
```

### Decision 3: Choose demand validation approach

**What:** `analysis/demand_validation_memo.md` presents 3 options for generating a demand signal. None has been chosen.

**Recommendation:** Option 2 (write a short technical post on the bait-and-switch attack vector, linking to SkillWatch). This is the best signal-to-effort ratio: 2-4 hours of writing generates a genuine demand signal (or a genuine null result). Option 3 (community post) is also viable but requires identifying the right venue.

**Action:** Choose an option and execute it. No git command -- this is a content creation task.

### Decision 4: Resolve dependabot PRs

**What:** 5 dependabot PRs are open for GitHub Actions version bumps (checkout v4->v7, setup-python v5->v6, cache v4->v6, upload-artifact v4->v7, download-artifact v4->v8).

**Recommendation:** Merge all 5. They are all major-version bumps for GitHub Actions with no breaking changes for this project's usage patterns. SHA pins will need updating.

**Action:**
```bash
# Review and merge each dependabot PR:
gh pr list --label dependencies --json number,title
# Then for each: gh pr merge <number> --merge
```

---

## Appendix: Commit Log (remediation/2026-07)

All commits from the remediation branch, in chronological order:

```
bd4a24c fix(G-11): remove PyPI badges and pip install for unpublished package
5f9b93b feat(G-07): add mypy with pragmatic-strict config
d4d6237 feat(G-05): add scheduled monitoring example workflow
8b2ea9e docs: add Phase 1 plan and pre-mortem to remediation ledger
22edc08 test(G-02): add holdout_v2 corpus (18 items, committed before detector changes)
7c079c6 feat(G-02): add canonicalisation layer and SRI hash exclusion
20aea32 fix(G-02): expand ROT13 candidate regex and update measurement harness
fec3c36 docs(G-02): update measured detection rates and add honest ceiling statement
565c92c fix: increase ReDoS test timeout margin for WSL/CI environments
fcb9275 feat(G-08): add HTML sub-corpus and fix HTML checks running on empty text diffs
46d6be0 feat(G-06): assess confusable_homoglyphs data currency, add refresh script
dd1d98e docs(G-03): add MAINTENANCE.md with proposed review cadence
5282cc8 docs: add PATTERNS.md with provenance table for all detection patterns
5360b17 docs(G-04): assess independence of CSA and arxiv premise sources from AIR
4dae11e docs(O-02): add complementary workflow example with static scanner
9a976e5 docs(G-01): add demand validation memo with 3 lowest-effort options
cc0853a test(G-09): add hermetic E2E test with ephemeral HTTP server
9861baf docs: update SHIP-READINESS.md with condition map, publish checklist, and Q-05 dry-run
f8f7ebc docs: update test count in README to 236
```

---

*Generated by Claude Code (Opus 4.6, 1M context). All VERIFIED labels confirmed in Phase 3 adversarial verification session. All READ labels sourced from repository files without independent re-execution.*
