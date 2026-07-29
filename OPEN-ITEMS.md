# Open items

The continuity ledger. Every item that is open, when it was first raised, its
current status, and what would close it.

**This file is the baseline for every session.** A session that finds something
adds it here; a session that closes something marks it closed here and says how.
Reproduce this file verbatim in any session handover. Nothing drops off a list
because it stopped being mentioned.

Dates are the date the item was first recorded, taken from git history or from
the handover that raised it. Where an item predates its first written record the
date is marked *(at latest)*.

**Last reviewed:** 2026-07-29

---

## The binding constraint

**Item 9 — zero users — is the only thing gating this project.** Conditions 1–4
of `SHIP-READINESS.md` pass. No engineering change moves condition 5. It moves by
distribution or not at all. Items 3 and 11 are the only ones that touch it, and
item 3 is now waiting on third parties, which leaves **item 11 as the only lever
still in our hands.** It has been out of scope four cycles running.

Read that before picking up anything else on this list. Most items below are
engineering, and engineering is not the constraint.

---

## Open

| # | Item | First raised | Status | Closes when |
|---|---|---|---|---|
| 3 | Distribution PRs [#31](https://github.com/LLMSecurity/awesome-agent-skills-security/pull/31) and [#239](https://github.com/Puliczek/awesome-mcp-security/pull/239) unmerged. Both opened 2026-07-11, no maintainer activity in 18 days. | 2026-07-11 | **Open.** Descriptions refreshed with 0.4.0 figures and AST05 framing, and both nudged, 2026-07-29. Third-party repos; not in our control. Nothing further to do but wait. | Merged, or closed and a different channel chosen. |
| 4 | Adopt ATR upstream through v3.5.11 (100+ commits since the 2026-06-26 derivation, incl. `#342` cutting false positives on 7 rules), then re-measure. | 2026-07-29 *(at latest)* | **Open, deferred three times.** Deliberately excluded from the 0.4.0 pre-release cycle: it changes detection, which forces a re-measure, and the release exists to correct published claims against a frozen detector. | Patterns refreshed in one commit, efficacy re-run in a separate commit, both figures published. |
| 5 | `PATTERNS.md` does not record which ATR version the 32 patterns were derived from. Drift is observable but not measurable. | 2026-07-29 *(at latest)* | **Open.** Blocks item 4's before/after comparison — without a baseline version there is nothing to diff against. | `PATTERNS.md` records the source version and commit for each pattern set. |
| 6 | 27 ruff 0.16 findings, held off by `ruff>=0.15.21,<0.16`. Counted, never individually assessed. | 2026-07-29 *(at latest)* | **Open.** Not release-blocking. The upper bound carries its justification in `pyproject.toml`. | Findings assessed and fixed, ceiling raised. |
| 7 | `hidden_content` is narrower than documented. `_extract_hidden_texts()` matches only `display:none` and `visibility:hidden`. Corpus item E-24 (`position:absolute;left:-9999px`) is missed; `clip-path`, `opacity:0`, `font-size:0`, `height:0` are unhandled. Code and documentation disagree. | 2026-07-29 *(at latest)* | **Open.** Excluded from the 0.4.0 cycle for the same reason as item 4. A real defect, not the semantic ceiling. | All CSS off-screen/invisible techniques handled, docs matched to code, efficacy re-run as a separate commit. |
| 9 | **No users.** 0 stars, 0 forks, 0 watchers, no external users, one month after going public. | 2026-07-11 | **Open — binding.** Untouched by three sessions of engineering. | Any external user. |
| 10 | CSA / advisory-feed step of the quarterly review not done end-to-end. | 2026-07-29 *(at latest)* | **Partly closed 2026-07-29.** SIGIL (arXiv 2605.05274), CVE-2026-33753, CVE-2026-24049 and the OWASP AST taxonomy were traced to primary sources. The CSA note and the advisory feed sweep remain. | A full pass recorded in `PATTERNS.md` with each source traced. |
| 11 | Phase 1.1–1.7: OWASP repositioning, purge uniqueness claims from `COMPETITORS.md`, LICENSE/NOASSERTION fix, stale-doc reconciliation, launch assets, credibility signals. | 2026-07-11 | **Partly closed 2026-07-29.** OWASP repositioning done (AST05, item 13). Stale docs done (item 12). **Launch assets and credibility signals remain and are the half that touches item 9.** Out of scope four cycles running. | Launch assets executed; `COMPETITORS.md` uniqueness claims removed; LICENSE metadata fixed. |
| 14 | AIR incident and its ~26,000-agent figure never independently verified. Company-reported, by a party that simultaneously launched a competing skill marketplace. | 2026-07-11 | **Open, correctly handled.** The README cites it *with* the disclosure and does not rely on the figure. Nothing depends on it. | Independent corroboration, or the citation is dropped. |
| 15 | SIGIL author affiliations not verified. | 2026-07-29 | **Open — attempted and failed 2026-07-29.** Affiliations are not in the arXiv abstract page. Needs the PDF front matter. | Affiliations read from the PDF and recorded in `SHIP-READINESS.md`. |
| 16 | The `lowest-direct` CI matrix has never been *observed* failing. The fix landed in the same commit as the check, so CI has only ever seen it green. A test that would pass if the fix were reverted. | 2026-07-29 | **Open.** Proven locally, never in CI. | A scratch branch lowers a floor, CI goes red, the run URL is recorded here, branch deleted. |
| 22 | `pip-audit --strict` cannot pass in the current invocation shape (editable install → "distribution marked as editable"; non-editable → "not found on PyPI"). The claim that it can *never* pass is untested — auditing a resolved requirements file that excludes the project itself (`uv export --no-emit-project`) may work. | 2026-07-29 | **Open, untested.** Reasoned, not evidenced: the assumption is that the editable project is the only skipped distribution. | The alternative shape is run. If it passes, adopt it. If not, record why and keep the current shape. **Do not add a skip to force it.** |
| 24 | `analysis/build_corpus.py` is untracked and has 3 mypy errors. It generates corpus items — the evidence behind published figures — from outside version control. | 2026-07-29 | **Open, new.** Surfaced when `analysis/` was brought into the lint gate. | Either tracked and linted like `measure_efficacy.py`, or explicitly documented as a throwaway. |
| 30 | **The corpus behind 0.3.0's published figures was never committed.** `benign/`, `adversarial_a/` and `adversarial_b/` entered version control in a single commit (`309d359`) at the time of the expansion; at tag `v0.3.0` only `holdout_v2/` and `html_v1/` were tracked. The figures 0.3.0 published (15/20, 5/10, 15/19) therefore cannot be reproduced at that tag, and claims comparing "the original ten" against the current set are inferences, not checks. | 2026-07-29 | **Open, new.** Surfaced when verifying an inherited README claim. Corrected in the README rather than repeated. Going forward the corpus is tracked, so this cannot recur — but the 0.3.0 comparison stays unverifiable. | Nothing closes it retrospectively. Mark closed once one release-to-release comparison has been made against two tracked corpus states. |
| 25 | The 11 July material (code review, distribution research with arXiv base rates, launch checklist incl. Show HN draft, SWOT) exists only in `/mnt/c/Users/mkuzi/Downloads/SkillWatch-HANDOVER-2026-07-29.md`. The `.docx` originals were deleted. Untracked, outside the repo, one deletion from gone. | 2026-07-29 | **Open.** Risk named in the previous handover; not acted on. Item 11's launch assets depend on it. | Content carried into the repository. |

---

## Closed

| # | Item | First raised | Closed | How |
|---|---|---|---|---|
| 1 | Cut the v0.4.0 release. | 2026-07-29 | 2026-07-29 | Released and published. PyPI serves 0.4.0; `publish.yml` run 30461711497, both jobs success. Verified on the live index that `rfc3161-client>=1.0.6` now ships — 0.3.0 declared `>=1.0`, which did not exclude the CVE-2026-33753-vulnerable versions. |
| 2 | Live PyPI page publishes superseded figures (78.9% precision, 75.0% recall, 50.0% evasive, no intervals). | 2026-07-29 | 2026-07-29 | Closed by the 0.4.0 release. PyPI now serves the corrected README with intervals on all three corpora and the base-rate warning. |
| 8 | Ship condition 2 (precision ≥75%) NOT DEMONSTRATED, with "needs more benign corpus items" recorded as the remedy. | 2026-07-29 | 2026-07-29 | **The recorded remedy was arithmetically backwards** — adding benign items can only add false positives, taking precision to 21/29 (72.4%, lower bound 54.3%). Condition re-specified as a benign false-positive-rate gate, which is ratio-independent. Reasoning in `SHIP-READINESS.md`. |
| 12 | Stale `CLAUDE.md` (10 modules, v0.2.0, "Pages disabled") and `docs/skillwatch-overview.js` (v0.3.0, 323 tests, 12 modules). | 2026-07-29 | 2026-07-29 | Both corrected. `CLAUDE.md` also gained the precision and AST05 rules so future sessions inherit them. |
| 13 | OWASP AST05/AST07 wording never verified against source; positioning blocked. | 2026-07-29 | 2026-07-29 | Verified against the OWASP project page. AST05 "Untrusted External Instructions" (High) is a direct fit; AST07 "Update Drift" (Medium) is partial. **Early-stage qualifier is mandatory** — v1.0 2026 Edition; OWASP's own pages disagree on the maturity tier, so state "early-stage, not flagship" rather than naming one. Scanner-bypass finding attributed to Trail of Bits, not OWASP. |
| 17 | `specifier_allows` failed open — an unparseable specifier passed silently in the auditor that gates the release. Recorded as "open by design". | 2026-07-29 | 2026-07-29 | Not a design decision, debt. Replaced with a three-valued `SpecifierVerdict` (ALLOWED/EXCLUDED/UNEVALUABLE) where only ALLOWED is truthy, so `if verdict:` fails closed. `_parse_version_strict` added for the correctness path, separate from `_version_key`'s ordering path. Unevaluable metadata is now an audit failure. 16 tests, fail-before/pass-after shown. |
| 18 | Holdout and html_v1 corpus results measured but unpublished. | 2026-07-29 | 2026-07-29 | Both now in the README with intervals. The harness already reported them; the summary tables did not. |
| 19 | Recall decomposition undisclosed — 75.0% → 60.0% reads as a regression. | 2026-07-29 | 2026-07-29 | Published in the README with the subset table. `detector.py` is byte-identical between v0.3.0 and v0.4.0; the corpus went from 50% evasive to 71% evasive. Nothing regressed. |
| 20 | Family classification audited once (E-09) and not generalised. | 2026-07-29 | 2026-07-29 | Family counts verified directly against the corpus files: semantic 13, mechanical 7, structural 3, language 2, summing to 25. Harness output matches. |
| 21 | Efficacy harness had no tests at all, while producing every published figure. | 2026-07-29 | 2026-07-29 | `tests/test_efficacy_harness.py`: 14 tests covering Wilson arithmetic against every published interval, gate-on-lower-bound behaviour, and the requirement that every corpus report carries an interval. |
| 23 | Ledger had no first-raised dates; items indistinguishable by age. | 2026-07-29 | 2026-07-29 | This file. |
| 26 | The html_v1 report published bare `100.0%` with no interval, breaching the project's own lower-bound convention. | 2026-07-29 | 2026-07-29 | Fixed. 6/6 is 100% with a 95% CI of [61.0%, 100.0%]. Test fails before, passes after. |
| 27 | `analysis/` was outside the CI lint and type gate, though `measure_efficacy.py` produces every published figure. | 2026-07-29 | 2026-07-29 | Added to both. Surfaced a real omission — `fp_rate_standard` was computed then dropped from the returned results while its four siblings were kept. Restored rather than deleted. |
| 28 | README cited arXiv 2508.12538 as corroboration for the bait-and-switch technique. | 2026-07-29 | 2026-07-29 | **The citation did not support the claim.** 2508.12538 is MCPXKIT, an offensive MCP toolkit, and its abstract does not document URL content swapping. Replaced with SIGIL (arXiv 2605.05274), which addresses the audit-runtime gap directly. |
| 29 | Precision published as a deployment property across README, `docs/llms.txt`, `docs/index.html` and `SHIP-READINESS.md` ("about 1 in 6 alerts is a false positive"). | 2026-07-29 | 2026-07-29 | Precision depends on the corpus benign:malicious ratio (~38:47) and does not transfer to a change stream that is overwhelmingly benign. All four surfaces now carry the base-rate warning and lead with the false-positive rate. |

---

## Standing decisions

Recorded so they are not silently redone. Fuller reasoning in
`docs/DEPENDENCY-FLOORS.md` and `SHIP-READINESS.md`.

- **Hard boundaries.** Local-only, no telemetry. No ML or LLM detection. Periodic,
  never continuous. No user→server data channel. The regex triage is evadable by
  design and documented as such.
- **Floors** are held at the lowest release that is free of known advisories *and*
  installable across the whole 3.10–3.13 matrix. Not the lowest that works on one
  Python. Never lower a floor to make `lowest-direct` pass.
- **Gates** are evaluated on the Wilson interval lower bound, never the point
  estimate.
- **Precision is not a gate** and must not be published as a deployment property.
- **"Decorative"** is scoped to *semantic* evasion, never blanket. Mechanical
  obfuscation is caught 7/7. Any surface using the word carries both figures.
- **arXiv 2508.12538 is not premise evidence.** It is MCPXKIT, an offensive
  toolkit, and its abstract does not cover URL content swapping. The premise
  citation is arXiv 2605.05274 (SIGIL), recorded as a preprint proposing a
  *competing* cooperation model.
- **OWASP AST is early-stage, not flagship.** Its own pages disagree on the tier
  (incubator vs new project proposal), so do not assert one without rechecking. An
  OWASP category describes a risk; it is not an endorsement of any tool. The
  scanner-bypass finding quoted from that document is Trail of Bits', cited by
  OWASP — attribute it to Trail of Bits.
- **Pattern refresh and efficacy measurement are separate commits.** Refresh
  first, measure second. Doing both at once makes the comparison circular.
- **The floor auditor has no allowlist.** A requirement with no lower bound is the
  maximum-exposure case, not an exempt one.
