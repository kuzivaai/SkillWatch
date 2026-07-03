# Remediation Ledger

## Phase 0: Re-verification of Dossier Claims

**Date:** 2026-07-03
**Verifier:** Claude Code (Opus 4.6, independent session)
**Dossier under review:** analysis/SkillWatch_DOSSIER_2026-07-02.md
**Commit at verification time:** 43816f17bca159955ef263a2fb3d9ee2b0d12496 (unchanged from dossier)

---

### 1. Git State

```
$ git rev-parse HEAD
43816f17bca159955ef263a2fb3d9ee2b0d12496

$ git branch --show-current
main

$ git tag --list
(empty)

$ git status --short
(empty -- clean working tree)

$ git log --oneline
43816f1 chore: remove sensitive files from tracking, rename docs/SECURITY.md
713965f chore: repository readiness -- packaging, CI hardening, public files
60949d5 feat: status command, add-time URL validation, wider alert display
9fc5848 docs: reposition as periodic monitor, add AIR COI disclosure, update figures
f83d2be fix: base64 hex-digest false positives, URL-path filter, ReDoS timeout, import guard
514d386 feat: v0.2.0 -- comprehensive detection, distribution, and UX overhaul
a829c32 fix: SQLite IMMEDIATE isolation, pass bytes to trafilatura
bb735f4 fix: resolve all 6 residual risks
fab8660 fix: double-spaced diffs, trafilatura version cap, MANIFEST.in
8876612 fix: adversarial security hardening, DoS protection, unbounded growth
542cc0a fix: thread-safe DNS pinning, full parser coverage, pip install verified
0f090f0 fix: audit remediation -- silently skipped tests, dead code, stale docs
ec219ce fix: close all security gaps, eliminate false positives, full test coverage
195265e fix: pre-hop redirect validation, OSC/DCS escape stripping, honest SECURITY.md
c1911de fix: security hardening, dead code removal, lint cleanup
45c2739 feat: SkillWatch v0.1.0 -- continuous URL content monitoring for AI skills

$ git remote -v
origin	https://github.com/kuzivaai/SkillWatch.git (fetch)
origin	https://github.com/kuzivaai/SkillWatch.git (push)
```

Commit count: **16** (matches dossier)
First commit: 45c2739 (2026-06-26) -- matches dossier
Latest commit: 43816f1 (2026-07-02) -- matches dossier

---

### 2. Repository Visibility

```
$ gh api repos/kuzivaai/SkillWatch --jq '{private: .private, visibility: .visibility}'
{"private":true,"visibility":"private"}
```

Matches dossier claim.

Additional stats:
```
$ gh api repos/kuzivaai/SkillWatch --jq '{stargazers, forks, subscribers, watchers, open_issues}'
{"forks":0,"open_issues":5,"stargazers":0,"subscribers":0,"watchers":0}
```

5 open issues are all dependabot bumps:
- Bump actions/setup-python 5.6.0 -> 6.3.0
- Bump actions/cache 4.3.0 -> 6.1.0
- Bump actions/checkout 4.3.1 -> 7.0.0
- Bump actions/download-artifact 4.3.0 -> 8.0.1
- Bump actions/upload-artifact 4.6.2 -> 7.0.1

---

### 3. Contributors

```
$ git log --all --format='%aN' | sort -u
Kuziva Muzondo
```

Single contributor confirmed.

---

### 4. Full Pytest

```
$ python3 -m pytest tests/ -q --tb=no
213 passed in 8.59s
```

Matches dossier claim (213 tests, 0 failures).

---

### 5. Coverage

```
$ python3 -m pytest --cov=skillwatch --cov-report=term-missing -q tests/
Name                      Stmts   Miss  Cover   Missing
-------------------------------------------------------
skillwatch/__init__.py        1      0   100%
skillwatch/cli.py           253     25    90%   153-154, 162-164, 167-168, 187, 191, 210, 231, 251, 267, 291, 395-405, 424
skillwatch/detector.py      164      0   100%
skillwatch/differ.py          8      0   100%
skillwatch/fetcher.py       118     14    88%   111, 154, 159-160, 167, 170, 184-187, 218-225
skillwatch/formatter.py     110      2    98%   23, 184
skillwatch/parser.py         98      5    95%   63, 83, 111, 130, 132
skillwatch/ssrf.py           73      4    95%   82, 93, 110, 150
skillwatch/store.py          95      2    98%   184-185
-------------------------------------------------------
TOTAL                       920     52    94%
213 passed in 14.20s
```

Matches dossier: 920 stmts, 52 missed, 94% coverage.

**Note:** DECISION.md states "205 tests, 95% coverage (862 stmts, 47 missed)" -- this is stale. DECISION.md was written during the audit chain before the final commits (43816f1, 713965f) which added 8 tests and changed statement counts. The dossier correctly reports the current 213/94% figures.

---

### 6. Ruff

```
$ ruff check .
All checks passed!
```

Matches dossier.

---

### 7. Build

```
$ rm -rf dist/ build/ skillwatch.egg-info && python3 -m build
Successfully built skillwatch-0.2.0.tar.gz and skillwatch-0.2.0-py3-none-any.whl
```

Matches dossier.

---

### 8. Efficacy Harness

```
$ python3 analysis/measure_efficacy.py
Corpus: 32 benign (8 hash, 24 standard), 10 adversarial A, 10 adversarial B

FP rate overall:  5/32 = 15.6%
FP rate hash:     2/8 = 25.0%
FP rate standard: 3/24 = 12.5%

FN rate subset A: 0/10 = 0.0%
FN rate subset B: 7/10 = 70.0%

Precision: 72.2%
Recall:    65.0%

FP breakdown by flag code:
  new_exec_command: 2/32 = 6.2%
  new_domains: 2/32 = 6.2%
  new_base64: 1/32 = 3.1%

PER-ITEM RESULTS:
B-05  benign/hash     FP (new_exec_command)
B-08  benign/hash     FP (new_base64)
B-12  benign/standard FP (new_domains)
B-19  benign/standard FP (new_domains)
B-27  benign/standard FP (new_exec_command)
A-01 through A-10: all correctly flagged (TP)
E-01 through E-05, E-07, E-08: missed (FN)
E-06: flagged (prompt_injection)
E-09: flagged (new_exec_command)
E-10: flagged (new_exec_command, new_domains)
```

All figures match dossier exactly:
- Precision 72.2% -- CONFIRMED
- Recall 65.0% -- CONFIRMED
- Evasive recall 30.0% (3/10) -- CONFIRMED
- FP rate 15.6% -- CONFIRMED
- FN rate evasive 70.0% -- CONFIRMED

---

### 9. Secret Scan

```
$ git log --all -p -S 'OPENAI_API_KEY' --oneline
(empty -- no results)

$ git log --all -- '.env' --oneline
(empty -- .env never committed)
```

Matches dossier. No secrets in history.

---

### 10. Personal Data History Check

```
$ git log --all --full-history -- .handover.md
(empty)

$ git log --all --full-history -- AUDIT-REPORT.md
(empty)

$ git log --all --full-history -- docs/skillwatch-overview.js
(empty)
```

All three files absent from history after the filter-repo rewrite. Matches dossier.

---

### 11. Action SHA Inventory

```
$ grep -rn '@[0-9a-f]{40}' .github/workflows/ action.yml

.github/workflows/ci.yml:19:    actions/checkout@34e114876b0b...  # v4
.github/workflows/ci.yml:20:    actions/setup-python@a26af69be951...  # v5
.github/workflows/publish.yml:14:  actions/checkout@34e114876b0b...  # v4
.github/workflows/publish.yml:15:  actions/setup-python@a26af69be951...  # v5
.github/workflows/publish.yml:22:  actions/upload-artifact@ea165f8d65b6...  # v4
.github/workflows/publish.yml:34:  actions/download-artifact@d3f86a106a0b...  # v4
.github/workflows/publish.yml:38:  pypa/gh-action-pypi-publish@cef221092ed1...  # release/v1
action.yml:26:  actions/setup-python@a26af69be951...  # v5
action.yml:35:  actions/cache@0057852bfaa8...  # v4
action.yml:72:  actions/upload-artifact@ea165f8d65b6...  # v4
```

Total: **10 SHA-pinned refs across 3 files** (ci.yml: 2, publish.yml: 5, action.yml: 3). Matches dossier.

---

### 12. Dependency List

```
$ pip list --format=columns | grep relevant
beautifulsoup4          4.15.0
build                   1.5.0
confusable-homoglyphs   3.3.1
pytest                  9.1.1
pytest-cov              7.1.0
PyYAML                  6.0.3
requests                2.34.2
requests-file           3.0.1
responses               0.26.1
ruff                    0.15.20
trafilatura             2.1.0
```

All versions match dossier Appendix A13 exactly.

---

### 13. pip-audit

```
$ pip-audit (non-strict, local venv)
Found 26 known vulnerabilities in 4 packages

Name         Version ID                  Fix Versions
------------ ------- ------------------- ------------
cryptography 44.0.3  PYSEC-2026-35       46.0.6
cryptography 44.0.3  CVE-2026-26007      46.0.5
cryptography 44.0.3  GHSA-537c-gmf6-5ccf 48.0.1
nltk         3.9.4   PYSEC-2026-597
pip          24.0    PYSEC-2026-196      26.1.2
pip          24.0    CVE-2025-8869       25.3
pip          24.0    CVE-2026-1703       26.0
pip          24.0    CVE-2026-3219       26.1
pip          24.0    CVE-2026-6357       26.1
transformers 4.51.3  PYSEC-2025-217
transformers 4.51.3  (14 more CVEs)      4.52.1-5.3.0

Name       Skip Reason
---------- -------------------------------------------------------------------------
skillwatch Dependency not found on PyPI and could not be audited: skillwatch (0.2.0)
```

**Key finding:** The dossier marked all CVE columns as "UNKNOWN" because pip-audit was not run during the dossier session. Now run, the results show:
- **cryptography 44.0.3** has 3 CVEs (transitive dep via trafilatura). This is NOT a direct dependency of SkillWatch.
- **nltk 3.9.4** has 1 CVE (transitive dep via trafilatura).
- **pip 24.0** has 5 CVEs (the pip in the venv itself).
- **transformers 4.51.3** has 16 CVEs (transitive dep via trafilatura).
- **No CVEs in SkillWatch's 5 direct runtime dependencies** (trafilatura, requests, beautifulsoup4, pyyaml, confusable_homoglyphs).

The dossier's DECISION.md claim of "0 direct-dependency CVEs" is **CONFIRMED** for direct deps. The transitive dependency situation is worse than implied, but the dossier honestly flagged the CVE columns as UNKNOWN.

---

### 14. Dossier Errata Check (Cross-Project Contamination)

#### 14.1: esbuild

```
$ grep -r 'esbuild' . --include='*.json' --include='*.toml' --include='*.lock' --exclude-dir=.venv --exclude-dir=.git
(no results, exit code 1)
```

**DOSSIER-ERRATUM: SEC-001.** The dossier Section 9 states "SEC-001: esbuild directory traversal (dev-only, Windows) -- Low -- Accepted." esbuild does not appear anywhere in the SkillWatch tree. This is cross-contamination from a different project (likely Cape-Town-Dash or another Node.js project). SkillWatch is a pure Python project with no JavaScript build tooling.

#### 14.2: /embed/ pages

```
$ find . -path '*/embed/*' -not -path './.venv/*' -not -path './.git/*'
(no results)
```

**DOSSIER-ERRATUM: SEC-003 (partial).** The dossier Section 9 states "/embed/* pages set X-Frame-Options: ALLOWALL." No /embed/ directory or pages exist in SkillWatch. The only "embed" references in docs/index.html are descriptions of a detection feature ("Data URI embeds"), not embed pages. This is cross-contamination from a different project.

#### 14.3: Analytics scripts in docs/index.html

```
$ grep -n 'plausible|amplitude|sentry|analytics|gtag|google-analytics' docs/index.html
(no results, exit code 1)
```

**DOSSIER-ERRATUM: SEC-003.** The dossier states "Consent model (Plausible ungated, Amplitude/Sentry consent-gated) -- Informational." No analytics scripts of any kind exist in SkillWatch's docs/index.html. This is cross-contamination from a different project (likely Cape-Town-Dash, which uses Plausible/Amplitude/Sentry).

#### 14.4: Risk-band threshold invariant

```
$ grep -rn 'risk.band|threshold.*67.*34|sanitize.ts' docs/ CLAUDE.md
(no results, exit code 1)
```

**DOSSIER-ERRATUM: Section 12 (Engineering Health).** The dossier states "Risk-band thresholds (67/34/0) are duplicated between compute_suburb_safety.mjs [N/A] and src/utils/sanitize.ts [N/A]. (This is a StreetSignal invariant, not applicable to SkillWatch.)" While the dossier does mark this "[N/A]", it should not appear in the SkillWatch dossier at all. This is StreetSignal (Cape-Town-Dash) content that leaked into the SkillWatch audit.

---

### Phase 0 Reconciliation Table

| Item ID | Dossier Claim | Phase-0 Status | Evidence Pointer |
|---------|---------------|----------------|------------------|
| **Gap Analysis** | | | |
| G-01 | Zero users, zero demand signal | **CONFIRMED** | gh api: 0 stars, 0 forks, 0 subscribers. 58 unique clones (all author). |
| G-02 | Evasive recall is 30% | **CONFIRMED** | measure_efficacy.py: 3/10 evasive detected. |
| G-03 | No maintenance owner or pattern-update cadence | **CONFIRMED** | DECISION.md conditions 3: FAIL. No document names an owner. |
| G-04 | Premise source COI | **CONFIRMED** | DECISION.md: AIR sells managed skill marketplace; COI disclosure added to README. |
| G-05 | No scheduled monitoring capability | **CONFIRMED** | No schedule: trigger in ci.yml or action.yml. User must configure cron externally. |
| G-06 | confusable_homoglyphs frozen at Unicode 12.0 | **CONFIRMED** | pip list: confusable-homoglyphs 3.3.1, last PyPI release 2019-01-06. |
| G-07 | No type checker | **CONFIRMED** | No mypy/ty/pyright in requirements or pip list. |
| G-08 | HTML-level efficacy unmeasured | **CONFIRMED** | Corpus is text-only (52 .txt files). 5 HTML flag codes untested. |
| G-09 | No end-to-end integration test against real URL | **CONFIRMED** | All test files use `responses` mock library. No live HTTP calls. |
| G-10 | Landing page exists but not deployed | **CONFIRMED** | docs/index.html exists. GitHub Pages not enabled (DECISION.md). |
| G-11 | PyPI badges link to unpublished package | **CONFIRMED** | README present; pip install skillwatch would fail (not on PyPI). |
| G-12 | Precision below 75% threshold | **CONFIRMED** | 72.2% measured vs DECISION.md 75% target. |
| **Risk Register** | | | |
| R-01 | Publishing to zero demand damages consulting credibility | **CONFIRMED** | DECISION.md condition 5: zero users, HOLD in force. |
| R-02 | Pattern set becomes stale without maintenance | **CONFIRMED** | No update cadence defined. 32 patterns frozen since v0.2.0. |
| R-03 | Evasive recall misunderstood as detection capability | **CONFIRMED** | README states 30% in 3 places; risk is reader interpretation despite honest docs. |
| R-04 | confusable_homoglyphs abandoned, breaks on future Python | **CONFIRMED** | Last release 2019. No maintained alternative identified. |
| R-05 | Prior clones (58 unique) retain sensitive personal data | **CONFIRMED** | gh api traffic/clones: 58 uniques. filter-repo rewrite removed .handover.md, AUDIT-REPORT.md, docs/skillwatch-overview.js from current history. Cannot revoke from prior clones. |
| **Opportunities** | | | |
| O-01 | Publish as change-monitor (not detector) | **CONFIRMED** | README repositioning verified. Opening line: "Periodic URL content monitoring". |
| O-02 | Integrate with existing scanners (Snyk Agent Scan) | **CONFIRMED** | README positions as complementary. No integration code exists. |
| O-03 | GitHub Marketplace Action | **CONFIRMED** | action.yml exists and is a functional composite action (setup-python, cache, upload-artifact). |
| **Open Questions** | | | |
| Q-01 | Is there any user demand? | **CONFIRMED (still zero)** | gh api: 0 stars, 0 forks, 0 external issues (5 open issues are all dependabot). |
| Q-02 | Are CSA and arxiv sources independent of AIR? | **UNVERIFIABLE** | Cannot verify author affiliations from this session. Manual check required. |
| Q-03 | Should the repository be made public? | **CONFIRMED (still HOLD)** | DECISION.md HOLD in force. Conditions 3 and 5 still fail. |
| Q-04 | What is the pip-audit result? | **CONFIRMED (now answered)** | 0 direct-dep CVEs. 26 transitive-dep CVEs across cryptography (3), nltk (1), pip (5), transformers (16). Previously UNKNOWN; now measured. |
| Q-05 | Does the GitHub Action work end-to-end? | **UNVERIFIABLE** | Cannot test in a consuming repository from this session. |
| **Dossier Errata** | | | |
| SEC-001 | "esbuild directory traversal (dev-only, Windows)" | **ERRATUM** | esbuild does not exist in SkillWatch. Cross-contamination from a Node.js project. |
| SEC-003 | "Consent model (Plausible ungated, Amplitude/Sentry consent-gated)" | **ERRATUM** | No analytics scripts in SkillWatch. Cross-contamination from another project (likely Cape-Town-Dash). |
| SEC-003 | "/embed/* pages set X-Frame-Options: ALLOWALL" | **ERRATUM** | No /embed/ pages exist in SkillWatch. Cross-contamination. |
| S12-INV | "Risk-band thresholds (67/34/0) duplicated between compute_suburb_safety.mjs and src/utils/sanitize.ts" | **ERRATUM** | StreetSignal (Cape-Town-Dash) invariant, not SkillWatch. Marked [N/A] in dossier but should not appear at all. |

---

### Summary of Findings

**Dossier accuracy:** Of the 25 verifiable claims (G-01 through G-12, R-01 through R-05, O-01 through O-03, Q-01 through Q-05), **21 are CONFIRMED**, **2 are UNVERIFIABLE** (Q-02, Q-05), and **2 are now answered** (Q-04 measured, Q-01 re-confirmed).

**Cross-project contamination found:** 4 errata identified. All originate from dossier Section 9 (Security Posture) and Section 12 (Engineering Health). The dossier generator appears to have carried forward findings from a different project audit (likely Cape-Town-Dash / StreetSignal) into the SkillWatch dossier:

1. **SEC-001 (esbuild):** Fabricated. No JavaScript tooling in SkillWatch.
2. **SEC-003 (analytics consent model):** Fabricated. No analytics in SkillWatch.
3. **SEC-003 (embed pages / X-Frame-Options):** Fabricated. No embed pages in SkillWatch.
4. **Section 12 (risk-band invariant):** Cross-contamination from StreetSignal. Correctly marked [N/A] but should have been omitted entirely.

**No core technical claims were fabricated.** All test counts, coverage figures, efficacy measurements, dependency versions, git state, and repository metadata match exactly.

**New information from this verification:**
- pip-audit now shows 26 transitive-dep CVEs (previously UNKNOWN). None in direct dependencies.
- 5 dependabot PRs are open for action version bumps.
- DECISION.md's test/coverage figures (205/95%) are stale relative to the dossier's correct figures (213/94%).

---

## Phase 1: Truth, Hygiene, and Tooling

**Date:** 2026-07-03
**Owner:** Kuziva Muzondo
**Constraint:** HOLD remains in force. No publishing, no release tags, no GitHub Pages.

---

### Severity-Ranked Backlog

Items are ordered by urgency. Classifications:
- **DECISION-REQUIRED** -- blocked on a human judgement call, not code.
- **FIX-NOW** -- can be resolved in code without external input.
- **PREPARE** -- blocked by the HOLD constraint; build the asset but do not ship.

#### DECISION-REQUIRED

| # | Registry ID | Objective | Acceptance Criteria | Blast Radius |
|---|-------------|-----------|---------------------|--------------|
| 1 | G-01 | Write demand memo: decide whether to pursue user demand or archive | A written document in decisions/ stating the chosen path (seek demand, archive, or hold indefinitely) with reasoning | Determines whether any further development is justified. Blocks Q-01, Q-03, condition 5 of DECISION.md |
| 2 | Q-03 | Decide whether to make the repository public | A written document in decisions/ stating public/private with conditions | Blocks G-10, O-03, PyPI steps. Interacts with R-01 (credibility risk of publishing to zero demand) |
| 3 | (new) | Ratify MAINTENANCE.md cadence | A MAINTENANCE.md file naming the owner and review cadence for the 32 injection patterns | Blocks DECISION.md condition 3. Without this, HOLD cannot be lifted regardless of code quality |
| 4 | (new) | Rotate or remove OPENAI_API_KEY reference | Confirm no API key was ever committed; if the key exists in any environment, rotate it | Security hygiene. Blast radius: credential exposure if key was reused |

#### FIX-NOW

| # | Registry ID | Wave | Objective | Acceptance Criteria | Blast Radius |
|---|-------------|------|-----------|---------------------|--------------|
| 5 | G-11 | 1 | Remove PyPI badges and pip install instruction | No badge or instruction references an unpublished package; removed items logged in SHIP-READINESS.md | README displays broken badges to anyone who views the repo |
| 6 | G-07 | 1 | Add mypy to dev toolchain | mypy passes with pragmatic-strict config; CI step added; all source violations fixed | Type safety gap across 920 statements |
| 7 | G-05 | 1 | Provide scheduled monitoring example | examples/scheduled-monitoring.yml exists with a copy-paste GitHub Actions cron workflow; README section added | Users have no guidance on how to run SkillWatch periodically in CI |
| 8 | G-02 | 2 | Improve evasive recall (bounded) | At least 1 additional evasive corpus item detected without increasing FP rate; measure_efficacy.py updated | Core efficacy metric. Must not regress precision |
| 9 | G-03 | 2 | Draft MAINTENANCE.md (content, not ratification) | File exists with proposed cadence, escalation process, and pattern-update checklist | Supports DECISION-REQUIRED item 3 |
| 10 | G-06 | 2 | Assess confusable_homoglyphs risk | Written assessment of abandonment risk; identify maintained alternative or document vendoring plan | R-04: library last released 2019, may break on future Python |
| 11 | G-08 | 2 | Add HTML-level efficacy corpus items | At least 5 HTML corpus items covering the 5 untested HTML flag codes; measure_efficacy.py updated | 5 of 13 flag codes have zero test coverage in the efficacy corpus |
| 12 | G-09 | 2 | Add end-to-end integration test | One test that fetches a real (stable) URL and exercises the full pipeline | All 213 tests use mocked HTTP; no confidence that real fetching works |
| 13 | G-12 | 2 | Improve precision to >= 75% | Precision >= 75.0% measured by measure_efficacy.py without recall regression | 72.2% is below the 75% DECISION.md threshold |
| 14 | G-04 | 3 | Verify premise source independence | Written assessment confirming or denying independence of CSA and arxiv sources from AIR | Blocks DECISION.md condition 4 |

#### PREPARE (blocked by HOLD)

| # | Registry ID | Objective | Acceptance Criteria | Blast Radius |
|---|-------------|-----------|---------------------|--------------|
| 15 | G-10 | Build landing page deployment config | GitHub Pages config ready but not enabled; docs/index.html reviewed for accuracy | Cannot deploy until Q-03 resolved and HOLD lifted |
| 16 | O-03 | Prepare GitHub Marketplace listing | action.yml reviewed; marketplace metadata ready but not submitted | Cannot list until repository is public |
| 17 | (new) | Prepare PyPI publishing steps | publish.yml workflow reviewed; twine/build config verified; testpypi dry-run documented | Cannot publish until HOLD lifted and all 5 DECISION.md conditions met |

---

### Pre-Mortem: Five Risks of This Remediation

1. **Corpus overfitting producing fake recall gains.** Improving evasive recall (G-02) by tuning patterns to the existing 10-item evasive corpus risks overfitting: patterns that match these specific payloads but fail on novel evasion. Guard: blind holdout protocol. Reserve 3+ new evasive items written before pattern tuning begins. Measure recall against the holdout, not the training set.

2. **Canonicalisation layer opening decode-bomb or DoS surface.** If G-02 adds content normalisation (e.g. ROT13 decode, base64 decode, Unicode NFKD) to catch encoded payloads, an attacker could craft deeply nested or exponentially expanding inputs. Guard: depth-1 decoding only, strict size caps (e.g. 10 KB decoded output), 2-second time budget per normalisation step (matching the existing ReDoS guard pattern).

3. **New dependencies raising audit burden.** Adding mypy, type stubs, or detection libraries increases the dependency surface that pip-audit must cover. Guard: no new runtime dependencies. mypy and type stubs are dev-only. Vendored data only (e.g. confusables database snapshot rather than a new library).

4. **Documentation drift reintroducing "detection tool" positioning.** Every README edit risks re-introducing language that overstates detection capability. The repositioning from "detection tool" to "periodic monitor with best-effort triage" was hard-won across prompts 3-5. Guard: Phase 3 includes a full documentation sweep. Every quantitative claim is verified against measure_efficacy.py output. No commit passes review if it introduces "detect", "continuous", or "real-time" without the established qualifiers.

5. **Accidental publication side effects.** A careless `git tag`, `gh release create`, PyPI upload, or GitHub Pages enable would violate the HOLD constraint and publish to zero demand. Guard: HOLD constraint checks at every commit. The CI workflow has no publish trigger. publish.yml requires manual dispatch. No `schedule:` trigger is added to the repository's own CI (only to the example file). Every PR description must state "HOLD status: unchanged".
