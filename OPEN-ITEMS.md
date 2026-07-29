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

**Last reviewed:** 2026-07-30

---

## The binding constraint

**Item 9 — zero users — is the only thing gating this project.** Conditions 1–4
of `SHIP-READINESS.md` pass. No engineering change moves condition 5. It moves by
distribution or not at all. Items 3 and 11 are the only ones that touch it, and
item 3 is waiting on third parties who have not responded since 2026-07-11.

As of 2026-07-29 item 11's **blockers** are cleared: the uniqueness claims that
would have contaminated launch copy are purged (item 34), and the facts an asset
needs are assembled in `docs/LAUNCH-FACTS.md`. What remains is writing the copy
itself, which is first-person, posted under a real name, and deliberately not
written by an agent. **That is a maintainer task, not an engineering one.**

Read that before picking up anything else on this list. Most items below are
engineering, and engineering is not the constraint.

---

## Open

| # | Item | First raised | Status | Closes when |
|---|---|---|---|---|
| 3 | Distribution PRs [#31](https://github.com/LLMSecurity/awesome-agent-skills-security/pull/31) and [#239](https://github.com/Puliczek/awesome-mcp-security/pull/239) unmerged. Both opened 2026-07-11, no maintainer activity in 18 days. | 2026-07-11 | **Open.** Descriptions refreshed with 0.4.0 figures and AST05 framing, and both nudged, 2026-07-29. Third-party repos; not in our control. Nothing further to do but wait. | Merged, or closed and a different channel chosen. |
| 2 | **REOPENED as the class 2026-07-30.** The repository and the published artefact diverge, and nothing detects it. Originally closed as an instance — superseded efficacy figures fixed by the 0.4.0 release. They diverged again the same day with different content: 0.4.0 shipped, then two misquoted citations and the `hidden_content` disclosure were corrected in-repository, and the live page kept serving the old text. A corrected claim reaches users only on release, and until 2026-07-30 nothing checked the correspondence in either direction. | 2026-07-29 | **Open until 0.4.1 ships.** Now *enforced*: `scripts/check_release_claims.py` gates on README + built sdist PKG-INFO before a release; `scripts/check_published_claims.py` reports live drift after one. Both use `scripts/claim_rules.py`. Verified against live 0.4.0: 5 violations, 4 markers HEAD-only. | 0.4.1 is published and `check_published_claims.py` exits 0. |
| 33 | External findings reached public surfaces without the source's own scope and quantifier — the Trail of Bits scanner-bypass finding and the OWASP AST05 mitigation list. | 2026-07-29 | **DOWNGRADED to partly closed 2026-07-30.** The 2026-07-29 closure said "corrected on every surface carrying them". That was not true of the **published artefact**: the live PyPI 0.4.0 page still carries both, confirmed by scanning its long description. Corrected in-repository and on both distribution PR bodies; the class fix (CLAUDE.md rule + tests) holds. | 0.4.1 ships and the live page carries the corrected text. |
| 35 | The claims guard could not see the published artefact. `tests/test_published_claims.py` read four repository paths and its own docstring said it "does not fetch anything", so the PyPI long description — the most public surface this project has — was outside its scope. The guard reported green while the live page served two distortions the repository had already corrected. Same fail-open shape as the dependency auditor treating an unparseable specifier as satisfied. | 2026-07-30 | **CLOSED 2026-07-30 by this commit.** Rules extracted to `scripts/claim_rules.py` with one entry point over arbitrary text; three callers now run them against repository files, a built sdist's PKG-INFO, and the live page. Gate and report kept separate and documented in CLAUDE.md as to which is which and why they cannot be merged. | (closed) |
| 36 | A negative claim rule shipped **vacuous**. `MITIGATION_OVERCLAIM_RE` used `[^.\n]{0,60}` where the text it was written to catch had 94 characters and a newline in that position, so it could never match. It passed against the pre-correction README and was therefore *not* among the failures when that file was used as a fail-before fixture — the fail-before run looked convincing while one of its three negative rules was inert. | 2026-07-30 | **CLOSED 2026-07-30.** Widened to `[^.]{0,160}` and proven to fire: it now reports on the pre-correction README (4 violations -> 5) and on the live PyPI page. Structural fix: every negative rule has a positive fixture in `tests/test_claim_rules.py`, and CLAUDE.md records that a rule which has never fired has not been tested. | (closed) |
| 4 | Adopt ATR upstream through v3.5.11 (100+ commits since the 2026-06-26 derivation, incl. `#342` cutting false positives on 7 rules), then re-measure. | 2026-07-29 *(at latest)* | **Open, deferred three times.** Deliberately excluded from the 0.4.0 pre-release cycle: it changes detection, which forces a re-measure, and the release exists to correct published claims against a frozen detector. | Patterns refreshed in one commit, efficacy re-run in a separate commit, both figures published. |
| 5 | `PATTERNS.md` does not record which ATR version the 32 patterns were derived from. Drift is observable but not measurable. | 2026-07-29 *(at latest)* | **Open.** Blocks item 4's before/after comparison — without a baseline version there is nothing to diff against. | `PATTERNS.md` records the source version and commit for each pattern set. |
| 6 | 27 ruff 0.16 findings, held off by `ruff>=0.15.21,<0.16`. Counted, never individually assessed. | 2026-07-29 *(at latest)* | **Open.** Not release-blocking. The upper bound carries its justification in `pyproject.toml`. | Findings assessed and fixed, ceiling raised. |
| 7 | `hidden_content` coverage is narrower than the flag name suggests. **Documentation half CLOSED 2026-07-29; code gap STILL OPEN.** Measured behaviour: `_extract_hidden_texts()` (`detector.py:602`) inspects an element's **inline `style` attribute** for lower-case `display:\s*none` or `visibility:\s*hidden` and nothing else. It does not fire on upper/mixed-case declarations (no `re.IGNORECASE`), `<style>` blocks, external stylesheets, the HTML `hidden` attribute, `aria-hidden`, `position:absolute;left:-9999px` (corpus `E-24`), `opacity:0`, `font-size:0`, `height:0`, `clip-path`, or `text-indent`. Stylesheet-based hiding is the largest gap in practice and was not previously recorded at all. | 2026-07-29 *(at latest)* | **Open — code only.** Every surface (README, PATTERNS.md, SHIP-READINESS.md, UNDERSTANDING-ALERTS.md, UX-DESIGN, and the function docstring) now describes what the code actually does, evidenced by a 15-technique behavioural run. The disagreement is closed; the gap is not. | All CSS hiding techniques handled and the case-sensitivity removed, in one commit, with the efficacy re-run as a separate commit. |
| 9 | **No users.** 0 stars, 0 forks, 0 watchers, no external users, one month after going public. | 2026-07-11 | **Open — binding.** Untouched by three sessions of engineering. | Any external user. |
| 10 | CSA / advisory-feed step of the quarterly review not done end-to-end. | 2026-07-29 *(at latest)* | **Partly closed; external-source re-verification CLOSED 2026-07-30.** Both sources this project's claims rest on were re-fetched from their primary URLs and are **unchanged** from what the corrections were written against. AST05 `Preventive Mitigations`, headings verbatim: 1 *Pin and verify referenced content*; 2 *Prefer inlining over fetching*; 3 *Allowlist permitted reference domains*; 4 *Audit references transitively*; 5 *Maintain fleet-wide visibility of referenced sources*; 6 *Rescan continuously*. `index.md:203` — "Trail of Bits publishes 'The Sorry State of Skill Distribution' — every public skill scanner tested (ClawHub's VirusTotal + LLM guard model, Cisco's `skill-scanner`, the skills.sh scanners) is bypassed in under an hour…". `index.md:227` — "| [AST05](ast05.md) | Untrusted External Instructions | High | Source inventory, content pinning, continuous rescanning | …". changedetection.io re-verified via `gh api`: **32,540 stars, Apache-2.0** — the tracked "~32,500" is accurate. **Still open: the CSA research note and the advisory-feed sweep.** | A full pass recorded in `PATTERNS.md` with each source traced. |
| 11 | Phase 1.1–1.7: OWASP repositioning, purge uniqueness claims from `COMPETITORS.md`, LICENSE/NOASSERTION fix, stale-doc reconciliation, launch assets, credibility signals. | 2026-07-11 | **Mostly closed 2026-07-29.** OWASP repositioning done and then corrected (items 13, 33). Stale docs done (item 12). **`COMPETITORS.md` element CLOSED** — tracked, purged, and rewritten as `docs/COMPETITORS.md`; see item 34. Launch *facts* assembled in `docs/LAUNCH-FACTS.md`. **Still open: the launch assets themselves** (first-person copy, deliberately not written by an agent) and the LICENSE/NOASSERTION fix. | Launch assets written and posted by the maintainer; LICENSE metadata fixed. |
| 14 | AIR incident and its ~26,000-agent figure never independently verified. Company-reported, by a party that simultaneously launched a competing skill marketplace. | 2026-07-11 | **Open, correctly handled.** The README cites it *with* the disclosure and does not rely on the figure. Nothing depends on it. | Independent corroboration, or the citation is dropped. |
| 15 | SIGIL author affiliations not verified. | 2026-07-29 | **Open — attempted and failed 2026-07-29.** Affiliations are not in the arXiv abstract page. Needs the PDF front matter. | Affiliations read from the PDF and recorded in `SHIP-READINESS.md`. |
| 16 | The `lowest-direct` CI matrix has never been *observed* failing. The fix landed in the same commit as the check, so CI has only ever seen it green. A test that would pass if the fix were reverted. | 2026-07-29 | **Open.** Proven locally, never in CI. | A scratch branch lowers a floor, CI goes red, the run URL is recorded here, branch deleted. |
| 22 | `pip-audit --strict` cannot pass in the current invocation shape (editable install → "distribution marked as editable"; non-editable → "not found on PyPI"). The claim that it can *never* pass is untested — auditing a resolved requirements file that excludes the project itself (`uv export --no-emit-project`) may work. | 2026-07-29 | **Open, untested.** Reasoned, not evidenced: the assumption is that the editable project is the only skipped distribution. | The alternative shape is run. If it passes, adopt it. If not, record why and keep the current shape. **Do not add a skip to force it.** |
| 24 | `analysis/build_corpus.py` is untracked and has 3 mypy errors. It generates corpus items — the evidence behind published figures — from outside version control. | 2026-07-29 | **Open, new.** Surfaced when `analysis/` was brought into the lint gate. | Either tracked and linted like `measure_efficacy.py`, or explicitly documented as a throwaway. |
| 30 | **The corpus behind 0.3.0's published figures was never committed.** `benign/`, `adversarial_a/` and `adversarial_b/` entered version control in a single commit (`309d359`) at the time of the expansion; at tag `v0.3.0` only `holdout_v2/` and `html_v1/` were tracked. The figures 0.3.0 published (15/20, 5/10, 15/19) therefore cannot be reproduced at that tag, and claims comparing "the original ten" against the current set are inferences, not checks. | 2026-07-29 | **Open, new.** Surfaced when verifying an inherited README claim. Corrected in the README rather than repeated. Going forward the corpus is tracked, so this cannot recur — but the 0.3.0 comparison stays unverifiable. | Nothing closes it retrospectively. Mark closed once one release-to-release comparison has been made against two tracked corpus states. |
| 31 | `docs/skillwatch-overview.js` is gitignored and untracked, so its staleness cannot be fixed durably — any correction is local to one machine. It also writes a `.docx` into `/mnt/c/Users/mkuzi/Downloads/`, a side effect outside the repository. | 2026-07-29 | **Open, new.** Surfaced when checking whether the item-12 fix had actually been committed. It had not. | Either tracked and kept current, or deleted as a personal scratch artefact. Deciding not to track it is a valid close, but must be recorded rather than left ambiguous. |

---

## Closed

| # | Item | First raised | Closed | How |
|---|---|---|---|---|
| 32 | The stale-bytecode hazard was handled **procedurally** — "remember to delete `__pycache__`" — which protects one machine for as long as someone remembers, and protects CI not at all. It had already produced one false test result. | 2026-07-29 | 2026-07-29 | Made structural. `PYTHONDONTWRITEBYTECODE: "1"` set at **workflow level** in `.github/workflows/ci.yml`, so both pytest-running jobs (`test`, `lowest-direct`) inherit it and any future job does too. Reasoning — mtime is whole-second granular, so two same-second edits of equal size are indistinguishable from no edit — recorded in the workflow itself and in `CLAUDE.md`. `publish.yml` runs no pytest and was not changed. |
| 34 | `COMPETITORS.md` was untracked and gitignored while being the input to launch copy, and carried uniqueness claims breaching this project's honesty rules — including an exhaustive negative tagged "VERIFIED". | 2026-07-11 | 2026-07-29 | **Decision: track it, purged.** Rewritten as `docs/COMPETITORS.md`, `.gitignore` entry replaced with an explanatory comment, old file deleted. Four uniqueness claims removed and tabulated with why. The claim "none fetches and hashes the actual web page" was false as written — changedetection.io (Apache-2.0, ~32,500 stars, verified 2026-07-29) does exactly that and is now named in the comparison as the more mature choice for general change monitoring. Rejected alternative: delete and keep private, which would leave the claims uncheckable and still feeding launch copy. |
| 25 | The 11 July material (code review, distribution research with arXiv base rates, launch checklist incl. Show HN draft, SWOT) existed only in a Downloads folder outside version control; the `.docx` originals were deleted. | 2026-07-29 | 2026-07-29 | Carried into the repository at `docs/archive/2026-07-11-preserved-material.md`, with staleness warnings and 2026-07-29 editorial notes. The Downloads copy is now redundant. |
| 1 | Cut the v0.4.0 release. | 2026-07-29 | 2026-07-29 | Released and published. PyPI serves 0.4.0; `publish.yml` run 30461711497, both jobs success. Verified on the live index that `rfc3161-client>=1.0.6` now ships — 0.3.0 declared `>=1.0`, which did not exclude the CVE-2026-33753-vulnerable versions. |
| 8 | Ship condition 2 (precision ≥75%) NOT DEMONSTRATED, with "needs more benign corpus items" recorded as the remedy. | 2026-07-29 | 2026-07-29 | **The recorded remedy was arithmetically backwards** — adding benign items can only add false positives, taking precision to 21/29 (72.4%, lower bound 54.3%). Condition re-specified as a benign false-positive-rate gate, which is ratio-independent. Reasoning in `SHIP-READINESS.md`. |
| 12 | Stale `CLAUDE.md` (10 modules, v0.2.0, "Pages disabled") and `docs/skillwatch-overview.js` (v0.3.0, 323 tests, 12 modules). | 2026-07-29 | 2026-07-29 | **`CLAUDE.md` only.** Corrected and committed; it also gained the precision and AST05 rules so future sessions inherit them. `docs/skillwatch-overview.js` was edited locally but is **gitignored and untracked** (`.gitignore:40`), so that edit is not in the repository and does not persist for anyone else. See item 31. |
| 13 | OWASP AST05/AST07 wording never verified against source; positioning blocked. | 2026-07-29 | 2026-07-29 | Verified against the OWASP project page. AST05 "Untrusted External Instructions" (High) is a direct fit; AST07 "Update Drift" (Medium) is partial. **Early-stage qualifier is mandatory** — v1.0 2026 Edition; OWASP's own pages disagree on the maturity tier, so state "early-stage, not flagship" rather than naming one. Scanner-bypass finding attributed to Trail of Bits, not OWASP. |
| 17 | `specifier_allows` failed open — an unparseable specifier passed silently in the auditor that gates the release. Recorded as "open by design". | 2026-07-29 | 2026-07-29 | Not a design decision, debt. Replaced with a three-valued `SpecifierVerdict` (ALLOWED/EXCLUDED/UNEVALUABLE) where only ALLOWED is truthy, so `if verdict:` fails closed. `_parse_version_strict` added for the correctness path, separate from `_version_key`'s ordering path. Unevaluable metadata is now an audit failure. The fail-before run showed 16 failures; `tests/test_dependency_floors.py` went 23 -> 32 tests (+9). |
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
