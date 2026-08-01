# SkillWatch distribution evidence sprint — raw session log

Permanent append-only evidence record. Command output is recorded as executed;
claims in narrative documents are not substitutes for this record.

## Codex operating-context retrieval

The official Codex manual helper initially failed inside the restricted network
with `curl: (6) Could not resolve host: developers.openai.com`. The required
escalated retry succeeded and reported:

```text
Manual path: /tmp/openai-docs-cache/codex-manual.md
Outline path: /tmp/openai-docs-cache/codex-manual.outline.md
Manual status: local manual was already current.
```


=== DATE AND ENVIRONMENT ===
Sat Aug  1 01:05:33 UTC 2026
/home/mkuziva/skillwatch
Python 3.12.3
git version 2.43.0
/usr/bin/gh

=== SANDBOX DECLARATION ===
sandbox_mode=workspace-write
approval_policy=managed escalation
writable_paths=/home/mkuziva/skillwatch,/tmp
network=restricted; approved read-only escalation available

=== GIT STATE ===
## feat/archive-durability-and-strict-audit...origin/feat/archive-durability-and-strict-audit [ahead 6]
?? analysis/session-log-2026-08-01-distribution.md
origin	https://github.com/kuzivaai/SkillWatch.git (fetch)
origin	https://github.com/kuzivaai/SkillWatch.git (push)
git_fetch_exit=0
start_head=0d8cc1736a0a5f5f03c02c7bf47917b6559efa12
origin_main=6c6ab215742b8d4913b9193a8df49e645f5cd060
branch=feat/archive-durability-and-strict-audit
upstream=de2a998498293ad17f6b1990e19dc8868c614293

=== LOCAL ONLY ===
0d8cc17 Record exact committed-tree assurance count
675a261 Make handover authority movable and fail-closed
aaa6a28 Consolidate the readiness session for review
6fc38af Close adversarial readiness-truth gaps
c5024e7 Define a falsifiable design-partner pilot
f22a312 Make readiness status mechanically consistent

=== REMOTE ONLY ===

=== MAIN TO HEAD ===
0d8cc17 (HEAD -> feat/archive-durability-and-strict-audit) Record exact committed-tree assurance count
675a261 Make handover authority movable and fail-closed
aaa6a28 Consolidate the readiness session for review
6fc38af Close adversarial readiness-truth gaps
c5024e7 Define a falsifiable design-partner pilot
f22a312 Make readiness status mechanically consistent
de2a998 (origin/feat/archive-durability-and-strict-audit) Seal push-readiness handover
55c067d Close adversarial continuity gaps
86f77ff Make continuity claims self-consistent
fa748d4 Record repository and PR baseline
ed3ee71 Make session evidence durable
39cc419 Add tracked Codex transition handover
f6b75c8 Close adversarial assurance findings
4b366c5 Observe the build gate red; settle --strict as load-bearing
fd4f4a9 Make the gate table see behaviour, not just names
fe66903 Prove the security gate can fail; audit every gate; correct the version claim
17ab8f1 docs(ledger): close items 16, 22, 55-58; correct the global-floor record
852fd72 Make the capture's absence detectable; adopt pip-audit --strict
 .github/workflows/ci.yml                          |   81 +-
 .gitignore                                        |   14 +
 AGENTS.md                                         |   74 +
 CLAUDE.md                                         |  353 +++-
 OPEN-ITEMS.md                                     |   93 +-
 README.md                                         |   21 +-
 SHIP-READINESS.md                                 |  382 +---
 analysis/corpus/realpage/CAPTURE-INTEGRITY.json   | 2092 +++++++++++----------
 analysis/run_delta_pass.py                        |   78 +-
 analysis/session-log-2026-07-31-readiness.md      | 1673 ++++++++++++++++
 analysis/session-log-2026-07-31.md                |  437 +++++
 analysis/verify_capture.py                        |  354 ++++
 docs/DEPENDENCY-FLOORS.md                         |  213 ++-
 docs/DESIGN-PARTNER-PILOT.md                      |  173 ++
 docs/HANDOVER-2026-07-31.md                       |  368 ++++
 docs/HANDOVER-READINESS-2026-07-31.md             |  244 +++
 docs/LAUNCH-FACTS.md                              |    7 +-
 docs/archive/SHIP-READINESS-HISTORY-2026-07-31.md |  347 ++++
 docs/current-handover.txt                         |    1 +
 docs/readiness-status.json                        |   47 +
 docs/research/COMMERCIAL-VALIDATION-2026-07-31.md |  113 ++
 scripts/check_published_claims.py                 |   56 +-
 scripts/readiness_consistency.py                  |  314 ++++
 tests/test_ci_scope.py                            |  167 ++
 tests/test_claude_md_currency.py                  |  158 ++
 tests/test_continuity.py                          |   72 +
 tests/test_gate_table.py                          |  657 +++++++
 tests/test_readiness_consistency.py               |  175 ++
 tests/test_verify_capture.py                      |  397 ++++
 29 files changed, 7705 insertions(+), 1456 deletions(-)

=== PRODUCTION CODE DIFFERENCE ===

=== AUTHORITATIVE HANDOVER POINTER ===
HANDOVER-READINESS-2026-07-31.md
handover_test_exit=1
cat: HANDOVER-READINESS-2026-07-31.md: No such file or directory
handover_cat_exit=1

=== CURRENT READINESS SOURCE ===
{
  "schema_version": 1,
  "evaluated_at": "2026-07-31",
  "verdict": "HOLD",
  "commercial_constraint": "zero_users",
  "readiness_gate": "condition_2",
  "organic_delta": "pending",
  "pilot_status": "permissible_evidence_gathering",
  "general_commercial_readiness": "not_demonstrated",
  "conditions": [
    {
      "id": 1,
      "status": "pass",
      "basis": "documentation_route",
      "summary": "Regex triage is explicitly decorative against semantic evasion."
    },
    {
      "id": 2,
      "status": "not_demonstrated",
      "basis": "wilson_bound",
      "metric": "benign_false_positive_rate",
      "direction": "lower_is_better",
      "successes": 6,
      "trials": 37,
      "threshold": 0.30,
      "summary": "The 95% Wilson upper bound is 31.1%, above the 30% gate."
    },
    {
      "id": 3,
      "status": "pass",
      "basis": "named_owner_and_cadence",
      "summary": "The condition requires a named owner and cadence, both documented; the separate current review is overdue."
    },
    {
      "id": 4,
      "status": "pass",
      "basis": "independent_premise_source",
      "summary": "[SIGIL](https://arxiv.org/abs/2605.05274) supports the premise; it is a preprint, not peer-reviewed."
    },
    {
      "id": 5,
      "status": "fail",
      "basis": "zero_users",
      "summary": "No external user or demand evidence is recorded in the repository; current external state is not proven by this offline gate."
    }
  ]
}
# Ship readiness

This is the concise current scoreboard. Its machine-readable source is
`docs/readiness-status.json`; `scripts/readiness_consistency.py` derives and
validates the block below against the current efficacy harness. Historical
measurements and superseded decisions are preserved in
`docs/archive/SHIP-READINESS-HISTORY-2026-07-31.md` and are not inputs to the
current verdict.

## Evaluation rule

Wilson bounds are directional. For a higher-is-better metric, the 95% Wilson
**lower bound** must meet the threshold. For a lower-is-better metric, the 95%
Wilson **upper bound** must meet the threshold. A point estimate alone never
passes a gate.

## Current scoreboard

<!-- readiness:current -->
| # | Status | Current basis |
|---:|---|---|
| 1 | **PASS** | Regex triage is explicitly decorative against semantic evasion. |
| 2 | **NOT_DEMONSTRATED** | The 95% Wilson upper bound is 31.1%, above the 30% gate. |
| 3 | **PASS** | The condition requires a named owner and cadence, both documented; the separate current review is overdue. |
| 4 | **PASS** | [SIGIL](https://arxiv.org/abs/2605.05274) supports the premise; it is a preprint, not peer-reviewed. |
| 5 | **FAIL** | No external user or demand evidence is recorded in the repository; current external state is not proven by this offline gate. |

**Verdict: HOLD.** Condition 2 not demonstrated; Condition 5 fail.
Condition 2 evidence: 6/37 (16.2%), 95% Wilson interval [7.7%, 31.1%]. This lower-is-better gate uses the upper bound.
Zero users is the binding commercial constraint, distinct from the unresolved condition 2 evidence gate.
Organic delta evidence: pending. Private pilot: permissible_evidence_gathering. General commercial readiness: not_demonstrated.
<!-- readiness:end -->

## Current `hidden_content` boundary

The detector and taxonomy agree: flagged techniques are `display:none`,
`visibility:hidden|collapse`, `opacity:0`, `font-size:0`, and a zero-sized box
with clipped overflow, whether inline or in a same-document `<style>` rule.
HTML `hidden`, off-screen positioning, `clip-path`/`text-indent` screen-reader
idioms and `aria-hidden` are deliberately not flagged. External stylesheets are
outside the product's user-specified-URL network boundary. Nested CSS at-rules
remain unevaluable. The full rationale is in
`docs/HIDING-TECHNIQUE-TAXONOMY.md`.
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

**Last reviewed:** 2026-08-01 (readiness-continuity verification: remote and PR state re-established; legacy handover authority made movable and fail-closed; item chronology checked against this review stamp)

---

## Supersession index

This machine-readable lineage makes later evidence authoritative without
rewriting the historical record in the superseded row.

| Superseded item | Authoritative item | Reason |
|---:|---:|---|
| 22 | 60 | Item 60 demonstrated the `pip-audit --strict` outcome difference that item 22 had not yet found. |

## The binding constraint

The current binding constraint, readiness gate and evidence state are defined
once in `docs/readiness-status.json` and rendered in `SHIP-READINESS.md`; do not
copy their current values into this narrative. The individual ledger rows below
remain the authoritative history and acceptance criteria for their own items.

As of 2026-07-29 the published artefact is correct for the first time: 0.4.1 is
live, `scripts/check_published_claims.py` exits 0 against it, and items 2 and 33
are closed. **That removes the last reason to delay distribution.** Nothing on the
engineering list now blocks item 11.

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
| 63 | **`publish.yml`'s `publish` job has never been observed red, and it gates the most public surface this project has.** All 4 `publish.yml` runs that had ever executed (v0.2.0, v0.3.0, v0.4.0, v0.4.1) concluded success. Surfaced by building the gate table, which is the table's purpose. **Split 2026-07-30:** this item originally covered `build` and `publish` together, which conflated a safe control with an unsafe one. The `build` half is closed by item 65; this is the `publish` half. | 2026-07-30 | **Open, and deliberately not attempted. This is a maintainer decision, not an oversight.** A deliberate failure of `publish` risks an artefact reaching the real PyPI index, which is outward-facing and hard to reverse. The 2026-07-30 `build` control did confirm the *guard* around it: `publish` has `needs: build` and no `if:`, and it reported `skipped` and never started when `build` failed. That observes the ordering, **not the job**. Recorded in the `CLAUDE.md` gate table as `never observed red` rather than left implied by absence. | A dry run against **TestPyPI** observes `publish` refusing a bad artefact. That needs no change to the real publish path and is the cheapest first step. |
| 66 | **A workflow reachable only by publishing a release cannot be exercised without editing it, so every control against it changes the thing being controlled.** `publish.yml` triggers solely on `release: types: [published]`. Testing `build` on 2026-07-30 required adding a `workflow_dispatch:` trigger on a throwaway branch. That worked, but it means the evidence is weaker than the `ci.yml` controls, where the trigger was untouched and the job ran exactly as it does in production. | 2026-07-30 | **Open, newly logged, and not a defect in the workflow so much as a property of it.** Stated rather than glossed: run 30530850014 exercised `build` under a trigger that does not exist on `main`. The job body and `runs-on` were identical, and the failure was in `python -m build` reading `pyproject.toml`, which no trigger influences, so the result transfers. **Reasoned, not evidenced.** The observation that would overturn it is a `build` failure mode that depends on the triggering event. Related: `tests/test_gate_table.py` now includes the `on:` block in every job hash, so a permanent trigger change forces `unknown`. | Either a release-time observation of `build` failing, or a documented decision that the dispatch-trigger control is sufficient evidence and the gap is accepted. |
| 3 | Distribution PRs [#31](https://github.com/LLMSecurity/awesome-agent-skills-security/pull/31) and [#239](https://github.com/Puliczek/awesome-mcp-security/pull/239) unmerged. Both opened 2026-07-11, no maintainer activity in 18 days. | 2026-07-11 | **Open.** Descriptions refreshed with 0.4.0 figures and AST05 framing, and both nudged, 2026-07-29. Third-party repos; not in our control. Nothing further to do but wait. | Merged, or closed and a different channel chosen. |
| 4 | Adopt ATR upstream through v3.5.11 (100+ commits since the 2026-06-26 derivation, incl. `#342` cutting false positives on 7 rules), then re-measure. | 2026-07-29 *(at latest)* | **Open, deferred three times.** Deliberately excluded from the 0.4.0 pre-release cycle: it changes detection, which forces a re-measure, and the release exists to correct published claims against a frozen detector. | Patterns refreshed in one commit, efficacy re-run in a separate commit, both figures published. |
| 6 | 27 ruff 0.16 findings, held off by `ruff>=0.15.21,<0.16`. Counted, never individually assessed. | 2026-07-29 *(at latest)* | **Open.** Not release-blocking. The upper bound carries its justification in `pyproject.toml`. | Findings assessed and fixed, ceiling raised. |
| 7 | `hidden_content` coverage. **Documentation half closed 2026-07-29. Code half closed 2026-07-29. Bucket assignments re-derived on measured evidence later the same day.** | 2026-07-29 *(at latest)* | **Partly open by decision, and the decisions are now evidenced rather than assumed.** The check asks whether content is concealed from a human while remaining in the ingested text, inline or via same-document `<style>` rules, case-insensitively. **Flagged:** `display:none`, `visibility:hidden|collapse`, `opacity:0`, `font-size:0`, zero box with clipped overflow. **Not flagged, each with a measured or sourced reason:** the HTML `hidden` attribute (55.2% of real pages — UI-state primitive); off-screen absolute positioning (WebAIM calls it the *recommended* `.sr-only` implementation); `clip-path`/`text-indent` sr-only idioms; `aria-hidden` (inverse of the threat). **Out of reach by hard boundary:** external stylesheets. **Newly stated residual gap:** `@media` and other nested at-rules are reported unparsed and nothing surfaces that to the flag. Reasoning: `docs/HIDING-TECHNIQUE-TAXONOMY.md`. | Bucket (b) is revisited if a days-apart delta measurement shows a flagged technique churning, or evidence appears that `.sr-only` markup carries payloads in practice. |
| 37 | **Every published figure rests on a self-authored corpus.** | 2026-07-29 *(as an uncertainty since 2026-07-11)* | **Partial — base rate demonstrated; organic delta scheduled and rehearsed.** The base rate is measured and published (201 real pages, 157 repositories). The real-page false-positive rate is **still not measured**: earliest run date **2026-08-05**, command **`python3 analysis/run_delta_pass.py`** — unchanged. **New this session: the pipeline is proven to run.** `--rehearse` executes every stage over stored HTML with no network call; all eight stages EXECUTED against both the 12-item committed corpus and the 201-page 2026-07-29 capture. It found a live defect that would have corrupted the measurement — see item 49. Its zero-change result is NOT a measurement, is labelled as such, and its artefact is gitignored so it cannot be mistaken for one. **Still unproven: everything touching the network** — SSRF validation on live hosts, DNS pinning, redirects, timeouts, vanished hosts — and behaviour on any genuinely changed page. | The delta pass runs on or after 2026-08-05 and its false-positive rate is published beside the synthetic one. |
| 38 | **Ship-readiness condition 2 does not pass.** The benign false-positive rate's Wilson upper bound exceeds the ≤30% gate. | 2026-07-29 | **Open. 6/37 (16.2%, [7.7, 31.1]); the bound fell from 34.2% to 31.1% after the base-rate reclassification and still exceeds 30%.** Whether that failure is a small-sample artefact or structural is **not decidable from anything in this repository today**: the base rate says the flagged techniques are common on real pages (argues structural), but `hidden_content` is a delta check and a first fetch runs no detection, so prevalence is exposure rather than a rate (argues artefact). **The deciding measurement is scheduled: `python3 analysis/run_delta_pass.py` on or after 2026-08-05** (item 37). No gate moved, no corpus padded, no technique dropped. | Either the scheduled delta rate lands below 30% on the interval, or a larger benign corpus narrows the bound, or the gate is re-specified per severity with that reasoning recorded. |
| 42 | **A detector change and its published figures can diverge, and nothing detects it.** Six surfaces carried pre-rewrite figures after the 2026-07-29 concealment rewrite; `SHIP-READINESS.md` contradicted itself inside one file. `scripts/claim_rules.py` checks citations and is blind to figures. | 2026-07-29 | **Partial — class controls exist with one stated correspondence residue.** `scripts/figure_rules.py` now enforces three rules: **currency** (the proportion must be one the harness prints), **arithmetic** (the percentage must equal k/n, independent of the harness), and **correspondence** (it must match the metric it is *labelled* with — see item 45). Allowed figures come from the harness's own stdout, parsed, not a maintained table. Floor derived per command (item 47). Wired into CI as a named step and into `check_release_claims.py`. **Residue, stated plainly: 23 of 50 non-exempt published proportions are NOT checked for correspondence.** 27 carry a recognisable metric label; the other 23 name a technique rather than a metric and are checked only for currency and arithmetic. **The specific substitution this cannot see: base-rate technique rows sharing the denominator 201.** Transposing two of them — publishing `display:none` as 111/201 and `html-hidden-attr` as 103/201 — yields two current, arithmetically correct, in-set figures under the wrong subjects, and every rule passes. `scripts/figure_rules.py` prints that split on every run. Also uncovered: `docs/index.html`, which renders percentages in prose ("64% recall") rather than `k/n (p%)`, so the parser sees nothing there. | The 23 unlabelled proportions gain recognisable labels, or a rule reaches figures whose label sits outside the line; and index.html figures become parseable or gain a prose-percentage rule. |
| 43 | **The `display:none` / `html-hidden-attr` split rests on an unevidenced churn claim that the cited source argues against.** `html-hidden-attr` was moved out of the flagged bucket on its 55.2% base rate while `display:none` was retained at 51.2%. The two intervals — [48.3%, 61.9%] and [44.4%, 58.1%] — overlap across almost their whole width, so **base rate does not separate them**. WebAIM, the primary source this project cites elsewhere, says the `hidden` attribute "functions the same as CSS display:none", so **concealment behaviour does not separate them either**. The split rests entirely on a churn argument: that the `hidden` attribute is toggled at runtime while `display:none` is static, and only churning concealment costs a false positive on a delta check. Nothing measures that. | 2026-07-29 | **Open. The weakest decision in the taxonomy, and named as such in it.** Recorded in `docs/HIDING-TECHNIQUE-TAXONOMY.md` under *The split between `html-hidden-attr` and `display:none`*, with the assumption, the evidence against it, and — fixed in advance — what each outcome of the delta pass would mean. If `display:none` contributes ≥10% of the delta false-positive rate the churn argument fails and it should move to bucket (b) on the same reasoning that moved `html-hidden-attr`. | `python3 analysis/run_delta_pass.py` runs on or after 2026-08-05 and its per-flag decomposition either supports the churn argument or moves `display:none`. |
| 44 | **Two `detector.py` lines are unreachable by configuration, not untested, and will go live untested if either technique returns to the flagged bucket.** `detector.py:732` (the off-screen positioned-guard) and `detector.py:815-816` (the HTML hidden-attribute branch) are skipped by `_is_flagged` because both techniques sit in bucket (b). Coverage reports them as uncovered; that is accurate but misleading — they are not dead code, they are guarded-out code with no test behind them. | 2026-07-29 | **Open, newly logged.** Deliberately not fixed this session: exercising a branch that cannot execute would mean temporarily moving a technique back to bucket (a), which is a detection change, and this session must not make one — it would confound the baseline the scheduled delta pass is read against. | A test that exercises both branches with the bucket table patched, or the branches are exercised naturally because a technique returned to bucket (a) — in which case the coverage must land in the same commit as the move. |
| 48 | **The harness-output evidence did not account for five published proportions.** The 2026-07-29 handover reported "Harness currently produces 34 distinct proportions" and never enumerated them, so a reader could not check that the five figures the live PyPI page publishes from the holdout and html_v1 corpora — 9/10, 9/12, 1/6, 6/6, 0/6 — were covered rather than silently exempted. A count is not an accounting. | 2026-07-29 | **Open as a reporting standard, resolved for this instance.** Enumerated: all 34 members listed, and all five are present as `(9,10) (9,12) (1,6) (6,6) (0,6)`. None sits inside a `figures:exempt` region — README's regions are lines 292-312 and 392-400 and the figures are at 233-248 and 366; SHIP-READINESS's regions are 37-39, 54-58, 129-140, 167-175, 202-208, 249-255 and its figure is at 117. So they are live measurements correctly covered, and **no correction was needed** — the conditional in the brief did not fire. | Closed when a reference set used to audit anything is enumerated in the evidence rather than counted, as a standing habit. |
| 52 | **The changed-page path had never executed.** Every rehearsal input was identical on both sides, or diffed against an empty or synthetic baseline. The mode the pipeline exists for — a real page that changed between snapshots — had never run. | 2026-07-29 | **Partial — injected changed-page path demonstrated; organic drift pending.** A `changed_page_probe` now takes five real stored pages, mutates copies offline, and runs the pipeline with the real baseline on the old side. All six expected checks fired: `new_domains`, `credential_reference`, `new_exec_command`, `new_base64` on 5/5, `hidden_content` and `major_deletion` on 4/5. **Both 4/5 results diagnosed as correct behaviour, not defects:** one page (`api.chub.ai`) has no `</body>` tag so the injection had nothing to replace, and one (`bags.fm`) has 61 characters of text where `major_deletion` requires `old_len > 100`. **Still pending: a page that changed on its own**, which only the 2026-08-05 pass provides — every change here was injected by the probe. | The scheduled delta pass runs and the pipeline is exercised on genuine drift. |
| 9 | **No users.** 0 stars, 0 forks, 0 watchers, no external users, one month after going public. | 2026-07-11 | **Open — binding.** Untouched by three sessions of engineering. | Any external user. |
| 10 | CSA / advisory-feed step of the quarterly review not done end-to-end. | 2026-07-29 *(at latest)* | **Partial — external-source re-verification closed; CSA and advisory sweep open.** Both sources this project's claims rest on were re-fetched from their primary URLs and are **unchanged** from what the corrections were written against. AST05 `Preventive Mitigations`, headings verbatim: 1 *Pin and verify referenced content*; 2 *Prefer inlining over fetching*; 3 *Allowlist permitted reference domains*; 4 *Audit references transitively*; 5 *Maintain fleet-wide visibility of referenced sources*; 6 *Rescan continuously*. `index.md:203` — "Trail of Bits publishes 'The Sorry State of Skill Distribution' — every public skill scanner tested (ClawHub's VirusTotal + LLM guard model, Cisco's `skill-scanner`, the skills.sh scanners) is bypassed in under an hour…". `index.md:227` — "| [AST05](ast05.md) | Untrusted External Instructions | High | Source inventory, content pinning, continuous rescanning | …". **Star-count reconciliation, completed 2026-07-29 (second attempt).** The figure disagreed between the public surfaces (`~32,500`) and this ledger (an exact count from an earlier fetch). Reconciled to **one form: the approximation `~32,500`, Apache-2.0**, which is what every surface now carries. The exact count is deliberately NOT restated anywhere — it was observed moving twice within a single day, and a figure that goes stale between a commit and a release is a claim this project cannot keep. **The first attempt at this reconciliation did not land:** it declared the exact figure "replaced by the approximation" while leaving three exact counts in this very sentence, so the ledger asserted a correction it had not made. See item 54. **Still open: the CSA research note and the advisory-feed sweep.** | A full pass recorded in `PATTERNS.md` with each source traced. |
| 11 | Phase 1.1–1.7: OWASP repositioning, purge uniqueness claims from `COMPETITORS.md`, LICENSE/NOASSERTION fix, stale-doc reconciliation, launch assets, credibility signals. | 2026-07-11 | **Partial — engineering elements mostly closed; maintainer launch work open.** OWASP repositioning done and then corrected (items 13, 33). Stale docs done (item 12). **`COMPETITORS.md` element CLOSED** — tracked, purged, and rewritten as `docs/COMPETITORS.md`; see item 34. Launch *facts* assembled in `docs/LAUNCH-FACTS.md`. **Still open: the launch assets themselves** (first-person copy, deliberately not written by an agent) and the LICENSE/NOASSERTION fix. | Launch assets written and posted by the maintainer; LICENSE metadata fixed. |
| 14 | AIR incident and its ~26,000-agent figure never independently verified. Company-reported, by a party that simultaneously launched a competing skill marketplace. | 2026-07-11 | **Open, correctly handled.** The README cites it *with* the disclosure and does not rely on the figure. Nothing depends on it. | Independent corroboration, or the citation is dropped. |
| 15 | SIGIL author affiliations not verified. | 2026-07-29 | **Open — attempted and failed 2026-07-29.** Affiliations are not in the arXiv abstract page. Needs the PDF front matter. | Affiliations read from the PDF and recorded in `SHIP-READINESS.md`. |
| 24 | `analysis/build_corpus.py` is untracked and has 3 mypy errors. It generates corpus items — the evidence behind published figures — from outside version control. | 2026-07-29 | **Open, new.** Surfaced when `analysis/` was brought into the lint gate. | Either tracked and linted like `measure_efficacy.py`, or explicitly documented as a throwaway. |
| 30 | **The corpus behind 0.3.0's published figures was never committed.** `benign/`, `adversarial_a/` and `adversarial_b/` entered version control in a single commit (`309d359`) at the time of the expansion; at tag `v0.3.0` only `holdout_v2/` and `html_v1/` were tracked. The figures 0.3.0 published (15/20, 5/10, 15/19) therefore cannot be reproduced at that tag, and claims comparing "the original ten" against the current set are inferences, not checks. | 2026-07-29 | **Open, new.** Surfaced when verifying an inherited README claim. Corrected in the README rather than repeated. Going forward the corpus is tracked, so this cannot recur — but the 0.3.0 comparison stays unverifiable. | Nothing closes it retrospectively. Mark closed once one release-to-release comparison has been made against two tracked corpus states. |
| 31 | `docs/skillwatch-overview.js` is gitignored and untracked, so its staleness cannot be fixed durably — any correction is local to one machine. It also writes a `.docx` into `/mnt/c/Users/mkuzi/Downloads/`, a side effect outside the repository. | 2026-07-29 | **Open, new.** Surfaced when checking whether the item-12 fix had actually been committed. It had not. | Either tracked and kept current, or deleted as a personal scratch artefact. Deciding not to track it is a valid close, but must be recorded rather than left ambiguous. |

---

## Closed

| # | Item | First raised | Closed | How |
|---|---|---|---|---|
| 74 | **The legacy tracked handover still presented the superseded “only gate” conclusion as current after the readiness-truth class fix.** `docs/HANDOVER-2026-07-31.md` is a required onboarding surface and could silently substitute historical state for the structured current verdict. | 2026-08-01 | 2026-08-01 | Added a supersession notice before any legacy claim. `docs/current-handover.txt` is the single movable authority pointer; every other `docs/HANDOVER*.md` must open with the exact supersession marker and name the pointer target. The real legacy file failed before the notice. Adversarial review caught and closed two follow-on gaps: the first test froze the dated 31 July handover forever, and the ledger review date lagged this 1 August item. The gate now validates pointer syntax/existence, exact sibling opt-out, and ledger review-date chronology. |
| 73 | **Current readiness status, historical narrative, generated measurements and summary verdicts could contradict one another while all checks remained green.** Reproduced in `SHIP-READINESS.md`: condition 2 was NOT DEMONSTRATED while the verdict said conditions 1–4 pass; it also carried stale corpus prose, a retracted claim and the old `hidden_content` description. The ledger kept closed rows under `## Open`. | 2026-07-31 | 2026-07-31 | Closed structurally. `docs/readiness-status.json` is the freshness-bounded current source; `scripts/readiness_consistency.py` validates unique condition IDs, controlled and cross-field status semantics, directional Wilson evidence, condition-specific evidence, the generated SHIP scoreboard and ledger sections. Current status copies outside the generated block were removed. Historical SHIP prose is archived and excluded from the verdict. The real fail-before was 5/5; required mutations failed and reverted; an initially passing direction mutation exposed and closed a duplicated-truth hole. Two independent restricted reviews found one HIGH and multiple MEDIUM/LOW gaps; every reproduced finding was fixed, including the synthetic page-rate overclaim, derived verdict clauses, evidence/freshness checks, pilot decision thresholds and heading fail-closed behavior. Final focused re-reviews found no HIGH or MEDIUM residue. |
| 35 | The claims guard could not see the published artefact. `tests/test_published_claims.py` read four repository paths and its own docstring said it "does not fetch anything", so the PyPI long description — the most public surface this project has — was outside its scope. The guard reported green while the live page served two distortions the repository had already corrected. Same fail-open shape as the dependency auditor treating an unparseable specifier as satisfied. | 2026-07-29 | **CLOSED 2026-07-29 by this commit.** Rules extracted to `scripts/claim_rules.py` with one entry point over arbitrary text; three callers now run them against repository files, a built sdist's PKG-INFO, and the live page. Gate and report kept separate and documented in CLAUDE.md as to which is which and why they cannot be merged. | (closed) |
| 36 | A negative claim rule shipped **vacuous**. `MITIGATION_OVERCLAIM_RE` used `[^.\n]{0,60}` where the text it was written to catch had 94 characters and a newline in that position, so it could never match. It passed against the pre-correction README and was therefore *not* among the failures when that file was used as a fail-before fixture — the fail-before run looked convincing while one of its three negative rules was inert. | 2026-07-29 | **CLOSED 2026-07-29.** Widened to `[^.]{0,160}` and proven to fire: it now reports on the pre-correction README (4 violations -> 5) and on the live PyPI page. Structural fix: every negative rule has a positive fixture in `tests/test_claim_rules.py`, and CLAUDE.md records that a rule which has never fired has not been tested. | (closed) |
| 72 | **The independent adversarial review found two MEDIUM assurance gaps:** the session-log test proved only that future names were not ignored, not that existing logs were tracked; and the item 22/60 prose assertions were overclaimed as semantic consistency. | 2026-07-31 | 2026-07-31 | Both reproduced and closed. The durability suite now enumerates every existing dated log and requires Git to track it. The ledger now has a structured supersession index recording `22 -> 60`, while the prose assertions are correctly limited to instance regressions. The strengthened tests failed before the fixes and pass 5/5 after them; verbatim reviewer findings and outputs are in `analysis/session-log-2026-07-31.md`. |
| 71 | **Closed ledger items 22 and 60 contradicted one another about whether `pip-audit --strict` had ever changed an outcome.** Item 22 retained the earlier statement that no distinguishing case was found and the flag was merely explicit intent. Item 60 recorded the later demonstrated 0→1 exit-code difference, but neither row linked to the other. A reader could legitimately inherit either conclusion. | 2026-07-31 | 2026-07-31 | Item 22 now says its earlier limit is superseded by item 60 and preserves only the still-current installed-closure limit. Item 60 explicitly identifies item 22 as the historical record it supersedes, and the structured supersession index records `22 -> 60`. `tests/test_continuity.py` enforces that lineage and retains literal instance regressions without claiming to interpret arbitrary prose. |
| 70 | **The required permanent session evidence log was ignored by `analysis/*`, so its first commit attempt failed and a session cutoff would have stranded the only record on one machine.** Force-adding the instance would have left the next dated log exposed to the same failure. | 2026-07-31 | 2026-07-31 | `.gitignore` now re-includes `analysis/session-log-*.md`. `tests/test_continuity.py` both probes a future dated path with `git check-ignore --no-index` and enumerates all existing matching logs with `git ls-files --error-unmatch`, proving that present evidence survives a fresh clone. The failed `git add` and fail-before outputs remain in the committed session log. |
| 69 | **The gate-table digest claimed to hash every action `with` input but recursively removed every key named `name`.** A display `name` on a job or step is cosmetic; `with.name` is often behavior-bearing. Changing that input left the digest unchanged, so a materially changed gate could retain its earlier verdict. The existing test changed only a step display label and therefore proved the exception, not its boundary. | 2026-07-31 | 2026-07-31 | Independently reproduced with otherwise-identical upload-artifact specs whose `with.name` values differed but whose hashes were equal. `_canonicalise` is now schema-aware: it removes `name` only from job and step display objects and retains nested inputs. A regression test proves `with.name` moves the digest while the display-rename test remains green. The `build` and `publish` hashes changed solely because the corrected algorithm now sees their existing upload-artifact names; their workflow specs did not change, so their prior control statuses remain applicable and the table records this algorithm migration rather than claiming a new negative control. |
| 68 | **A syntactically valid manifest with a malformed nonempty `copies` registry escaped the capture verifier's documented exit-4 contract.** Values such as `copies: [null]`, a string entry, a missing `path`, or a non-string path raised an uncaught exception and exited 1. `recorded_copies()` had the same unchecked assumption. Tests covered invalid JSON and an empty list but not malformed nonempty entries. | 2026-07-31 | 2026-07-31 | Independently reproduced with `copies: [null]` (uncaught `TypeError`, exit 1). Copy-registry parsing is now centralized and validates the list, each object, and each nonempty string path. The CLI reports `UNUSABLE`, no traceback, and exits 4; the consumer API returns an empty tuple for an unusable registry. Four malformed shapes are regression-tested. |
| 64 | **The gate table recorded identity, not behaviour, and therefore certified gates it had not examined.** It forced a row and a status to exist for every job and script. It could not notice a job rewritten under the same name keeping its old verdict, which is not hypothetical: `security` was rewritten on 2026-07-30 (separate venv, `pip freeze --exclude-editable`, the `-r` shape, `--strict` for `--skip-editable`) and silently carried forward a never-observed-red status. The accounting built to close the class contained the class. | 2026-07-30 | 2026-07-30 | **Each job's row now carries a digest of what the job executes, and the suite fails when it drifts.** A drifted job's status must read `unknown`; a second test enforces that it cannot say anything else, kept separate so weakening one does not weaken the other. The failure message prints the current hashes so they are copy-pasteable, and says explicitly not to update a hash alone, because that records the change happened and asserts nothing about whether the gate still refuses anything. **Deliberate deviation from "hash the executable `run:` lines", with the reason measured rather than argued:** the `publish` job has **zero** `run:` lines, so a run-lines-only digest for it is `sha256("[]")`, a constant, blind to `needs: build` (the ordering that keeps a failed build off PyPI), `environment: pypi`, `permissions: id-token: write`, and the pinned SHA of `pypa/gh-action-pypi-publish`. The digest is over the parsed job spec instead: YAML parsing drops comments, blank lines and trailing whitespace *inherently*, which is stronger than regex stripping, and step order stays significant, which is correct because step ordering is what isolated the pip-audit step from the floor step in item 59. **The digest also covers the workflow's `on:` block, found by doing rather than by reasoning:** an earlier draft hashed the job alone, the build control then added `workflow_dispatch:` to `publish.yml`, and the hash did not move because `on:` sits outside `jobs:`. A gate that stops running is not a gate. Trap recorded: under YAML 1.1 the bare key `on` parses to boolean `True`, so a digest reading `data["on"]` would omit the trigger from every hash. Rows are now read by **column name**, not position, since a column was inserted and a checker that keeps passing while reading the wrong cell is this exact shape. Proven both ways on real workflow text, cache cleared between all four runs: baseline **21 passed**; a comment edit inside `security` **21 passed** with the hash unchanged at `576042ed1d31`; an executable change (dropping `--strict`) **2 failed** naming `security: recorded 576042ed1d31, now b8ea72554518`; reverted **21 passed**. Corroborated unstaged later the same session: a 19-line comment rewrite in that job left the hash at `576042ed1d31`. **Stated limits, in the module and beside the table:** it checks a status is *recorded*, not *true*; **repository-side gate scripts are NOT hashed** and can be rewritten under the same name exactly as `security` was (item 67); and a job calling a script whose contents changed keeps its hash. | (closed) |
| 65 | **`publish.yml`'s `build` job had never been observed red**, across all 4 runs it had ever had, while guarding the most public surface this project has. Split from item 63 on 2026-07-30, because bundling it with `publish` conflated a control that is safe with one that is not. | 2026-07-30 | 2026-07-30 | **OBSERVED RED.** Run **<https://github.com/kuzivaai/SkillWatch/actions/runs/30530850014>**, branch `throwaway/build-negative-control` (deleted), head `1722028e528d73a8c68709eb76fa5e2c2e6a6508`, event `workflow_dispatch`. Stimulus: three lines of invalid TOML in `pyproject.toml`. `build` **failure** at step *Build package*: `ERROR Failed to parse /home/runner/work/SkillWatch/SkillWatch/pyproject.toml: Expected '=' after a key in a key/value pair (at line 17, column 6)`, `Process completed with exit code 1`. The preceding *Install build tools* step **succeeded**, and the following *upload-artifact* step was `skipped`. **`publish` reported `skipped` and never started** — the GitHub API listed no steps for it at all. Every element matched the prediction recorded in the commit message before the run. **Nothing was published:** PyPI still serves exactly four releases, newest 0.4.1 from 2026-07-29. A second run, `30530833867`, fired from the `push:` trigger with identical conclusions. **A prediction that was WRONG, recorded rather than quietly dropped:** `gh workflow run --ref` was expected to be refused from a non-default branch, and a `push:` trigger was added as a fallback. It exited **0** and produced the dispatch run, so the `push:` trigger was unnecessary apparatus; a later session needs only `workflow_dispatch:`. Teardown proven: branch deleted locally and on the remote, `git branch -a` shows no `throwaway`, `git diff main` is **0 bytes** on both `pyproject.toml` and `.github/workflows/publish.yml`, `publish.yml`'s `on:` block is back to `release` only, and no PR was ever opened (`gh pr list --head ... --state all` returns `[]`). Testability caveat logged as item 66. | (closed) |
| 60 | **`pip-audit --strict` was a rule that had never been observed firing**, carried for five sessions and adopted for stated intent rather than demonstrated effect. The 2026-07-30 `security` control (item 59) did not close it: `jinja2==2.11.3` is a resolvable package with advisories, which plain `pip-audit` reports too, so that run exercised the *job* and not the *flag*. | 2026-07-30 | 2026-07-30 | **DEMONSTRATED. The flag is load-bearing and stays.** Found by reading pip-audit's source rather than guessing at inputs: `--strict` turns any `SkippedDependency` fatal (`_cli.py:557`), and the skip reachable on *every* dependency source is `_service/pypi.py:85`, a package that resolves but whose `(name, version)` **404s on PyPI** and therefore cannot be audited at all. Measured on pip-audit 2.10.1 against a locally built package deliberately absent from PyPI (its JSON endpoint returns HTTP 404): **without `--strict`, exit 0** — it prints `No known vulnerabilities found` and a *Skip Reason* table and **passes**; **with `--strict`, exit 1** — `ERROR: skillwatch-strict-probe-does-not-exist: Dependency not found on PyPI and could not be audited`. So without the flag this gate reports green over a dependency it never examined: the same fail-open shape as items 17 and 35. Reachable in the real shape, since `pip freeze` names whatever is installed, including anything from a private index, a VCS URL, or a release later removed from PyPI. **Supersedes item 22's earlier record that no distinguishing case had been found.** **Six cases that do NOT distinguish the flag are tabulated in `docs/DEPENDENCY-FLOORS.md` so they are not retried** (resolvable-with-advisories, no-advisories, nonexistent name, yanked release, local sdist of a published version, editable `-e .`), along with the finding that the editable and URL skips in `requirement.py:312-346` are **unreachable in CI's shape** because that path runs only under `--no-deps`, which this project does not pass. The false claim in `ci.yml`'s comment (*"no case was constructed where `--strict` changed the outcome"*) is corrected in place. **Stated limit: the control was local, against pip-audit 2.10.1**, while CI installs whatever `pip install pip-audit` resolves at run time. | (closed) |
| 67 | **Locating commands inherited from a brief have twice named things that did not exist in the branch being worked on, and both times an empty result would have been read as an absence.** 2026-07-29: the capture's locating glob was `/tmp/claude-*/*/scratchpad`, three levels where the real path has four, and it matched nothing while the file sat on disk (item 56). 2026-07-30: a brief instructed `grep -n -B2 -A20 "name: Audit installed dependencies" .github/workflows/ci.yml`, which returned nothing because the step had been renamed to *Audit resolved dependencies (--strict, no skip flags)* in the very rewrite under investigation. The literal came from `main`; the work was on a branch. | 2026-07-29 | 2026-07-30 | **Both caught by the same rule, which is why it is recorded as a rule rather than twice as an anecdote.** `CLAUDE.md` states that an empty result from a locating command is a **FAILED command, not an absence**: widen the search, vary the depth and the root, search by filename, and report every attempt before concluding anything. Applied on 2026-07-30, widening from the stale literal to `grep -rin "audit" .github/workflows/ci.yml` found the renamed step immediately. **The generalisation worth carrying forward: a literal name in an inherited instruction is a claim about repository state at the time it was written, and `main` and a feature branch are different repositories.** Treat the concept as the target, not the string. `tests/test_verify_capture.py::test_the_four_level_scratchpad_glob_is_preserved` pins the glob depth; nothing can pin a step name written in prose, so the rule is the control. | (closed) |
| 59 | **The rewritten `security` job was relied upon without its failure path ever being observed.** The 2026-07-30 rewrite (separate venv, `pip freeze --exclude-editable`, the `-r` shape, `--strict` in place of `--skip-editable`) had only ever run green. Green is not evidence a gate works; it is evidence it did not object. This is the **sixth** outing of the shape, and it was created by the fix for the fifth: the same commit that closed item 16 for `lowest-direct` by running a negative control rewrote `security` and left it unproven. | 2026-07-30 | 2026-07-30 | **OBSERVED RED.** Run **<https://github.com/kuzivaai/SkillWatch/actions/runs/30526422428>**, PR [#38](https://github.com/kuzivaai/SkillWatch/pull/38) "DO NOT MERGE", branch `throwaway/security-negative-control`, head `d82ba032b75f0ea2537114df91aded5dc098f158`. `security` conclusion **failure** at step *Audit resolved dependencies (--strict, no skip flags)*: `Found 4 known vulnerabilities in 1 package`, `jinja2 2.11.3`, PYSEC-2026-1471/1473/1474/1475, `Process completed with exit code 1`. The later *Audit declared dependency floors* step reported `skipped`. All eight `test` and `lowest-direct` legs **success**, matching the prediction recorded in the commit message *before* the run. **Route A of two, chosen because the audited set is generated at CI time into a gitignored path rather than committed:** the pin went into `pyproject.toml` so the whole rewritten path executed, where Route B (appending to the generated file inside the workflow) would have exercised the audit command alone and proven nothing about the generation path that was actually rewritten. Reasoning recorded in `docs/DEPENDENCY-FLOORS.md`. **Confound, stated rather than glossed:** `jinja2==2.11.3` is also rejected by `scripts/audit_dependency_floors.py`, so the stimulus was not pip-audit specific; step ordering rescues the attribution because pip-audit runs first and the floor step never executed. PR closed **unmerged** (`state: CLOSED, mergedAt: null`); branch deleted locally and on the remote, `git branch -a` confirms it gone; `git diff main -- pyproject.toml` empty; `jinja2` absent from the whole tree; `main` untouched at `6c6ab21`. | (closed) |
| 62 | **No record existed of which gates had ever been seen to refuse anything.** Item 16 closed that question for `lowest-direct` and item 59 for `security`, one at a time, while the underlying class stayed open: nothing recorded the answer for the other gates, so the next session would have had to rediscover it, and a newly added gate could be relied upon indefinitely without anyone noticing it had never been tested. Closing instances one at a time is how a class survives. | 2026-07-30 | 2026-07-30 | **A gate table and a rule, both enforced.** `CLAUDE.md` now carries a table of every gate with its negative-control status, and beside it the rule: **a gate that is added or materially changed requires a negative control before it is relied on.** Status is a controlled vocabulary of exactly three values (`RED OBSERVED` with a run URL or exit code, `never observed red`, `unknown`), so a guess cannot be written where a verdict belongs. **History is exhaustive, not sampled:** all 81 `ci.yml` runs and all 4 `publish.yml` runs that exist were inspected; 4 CI failures, 0 publish failures. Eight of ten gates are `RED OBSERVED`; the two that are not are `build` and `publish` (item 63). The five repository-side gates were demonstrated red **fresh this session** rather than inherited from the ledger: floor audit `exit=1`, release gate `exit=1` on both its claim and figure paths, published-claims report `exit=2` with PyPI unreachable, figure check `exit=1` on a relabelled figure, capture verifier `exit=2` and `exit=3` with 3 outranking 2. Every mutation reverted. `tests/test_gate_table.py` (13 tests) enforces it: job names are parsed as **YAML from every tracked workflow**, not grepped from `ci.yml` alone, because a table blind to `publish.yml` would reproduce the very out-of-scope defect being closed; and every tracked script under `scripts/` and `analysis/` must be either a table row or an explicit not-a-gate declaration with a reason, mirroring `NO_FLOOR_EXPECTED`. Proven non-vacuous three ways: 9 failed / 4 passed against `HEAD`'s table-less `CLAUDE.md`, then 13 passed; adding an unrecorded CI job failed naming it; adding an unclassified tracked script failed naming it. **Stated limit, in the module: it checks that a status is recorded, not that it is true.** A reviewer must still follow the URL. | (closed) |
| 61 | **`CLAUDE.md` briefed every session with a false version claim.** It read *"PyPI serves 0.3.0 (2026-07-11); `main` is 0.4.0"*. Both halves were false: PyPI had served 0.4.1 since 2026-07-29T18:17:39Z and `main` was 0.4.1. The same sentence had already gone stale once before (item 12: "10 modules, v0.2.0, Pages disabled"), so this is a recurrence, not a first offence. A second stale claim was found in the same file: *"Two tracked scripts under `scripts/`"* where `git ls-files 'scripts/*.py'` returns **six**. | 2026-07-30 | 2026-07-30 | **Corrected, and the class checked rather than the instance.** The sentence now reads *"PyPI serves 0.4.1 (2026-07-29); this repository declares 0.4.1 in `pyproject.toml`"*, with the verification commands beside it and the previous wrong text preserved in a comment. The scripts claim is corrected to six and names all six; a corresponding claim for the six tracked `analysis/` modules is added. **The staleness question was asked and answered in the file** (*"The facts in this file are claims too"*): yes, a cheap check exists, and it is the same fix as `figure_rules.py` (derive the claim from the artefact instead of keeping a second copy), split along the gate/report line this repository already draws. Offline and blocking, in `tests/test_claude_md_currency.py` (7 tests): the declared version against `pyproject.toml`, and three counts plus their filenames against `git ls-files`. Networked and **non-blocking**, in `scripts/check_published_claims.py`: `CLAUDE.md`'s *"PyPI serves X"* against the live index, deliberately not a gate because only a release can make it true and gating would deadlock exactly as gating on the report itself would. Both proven on the real defect: the offline test is 3 failed / 4 passed against `HEAD`'s stale file and 7 passed after; the report exits **1** against `HEAD` with *"CLAUDE.md says PyPI serves 0.3.0 (checked 2026-07-11); PyPI actually serves 0.4.1"* and **0** after. **Consequence recorded: the wording is now load-bearing** and must be written in the parsed forms or the checks fail closed. **Stated limit: only mechanically derivable facts are covered**; the prose claims in `CLAUDE.md` can still go stale silently. | (closed) |
| 55 | **The irreplaceable capture had a single point of failure and nothing detected its absence.** Item 51 moved the 2026-07-29 HTML capture out of an ephemeral scratchpad into `/home/mkuziva/.skillwatch-archive/`, which fixed the *instance*. The **class** stayed open: one directory, one filesystem, and no check anywhere that would fail if the file vanished or silently rotted. A copy nobody verifies is indistinguishable from no copy on the day it rots, and `--source capture` loaded whichever path existed first **without checking a single hash** — so a corrupted copy would have been fed through a rehearsal and reported as a result. | 2026-07-30 | 2026-07-30 | **Two copies added and a verifier that fails.** Copies at `/mnt/d/skillwatch-archive/…` and `/mnt/c/Users/mkuzi/skillwatch-archive/…`, both outside the WSL2 VHDX; all three `sha256 861027d158b67c517074e3a17348777e4405a644c13a33c7fbc85f25aa417dfe`, 59968045 bytes, matching `CAPTURE-INTEGRITY.json`. **Independence is PARTIAL and is documented as partial:** Windows reports exactly one physical disk (Disk 0, `RS1D0TSSD510`, NVMe, 1,024,209,543,168 bytes); C: is partition 3, D: is partition 5 of that same disk, and the ext4 filesystem is a VHDX file on C:. What the copies close is the largest real class for a WSL user — `wsl --unregister`, a distro reset, ext4/VHDX corruption, and a C: reimage (the D: copy survives that). **Residual and unmitigated: Disk 0 failure and loss of the machine.** Closing those needs an off-machine destination, which is outside this project's local-only boundary, so it is flagged for the user in `CLAUDE.md` and deliberately **not** done. `analysis/verify_capture.py` exits 0 verified / **2 MISSING** / **3 CORRUPT** / 4 manifest unusable, with distinct messages ("cannot find it" vs "found it and it is wrong"); **3 outranks 2** because reporting only the absence would invite restoring the missing copy *from* the corrupt one. Per-page hashes localise damage: a tampered `https://bags.fm` was reported as 1 of 201. Both consumers now verify **before** loading. `CAPTURE-INTEGRITY.json` gained `copies`/`holders` and is the single registry — `run_delta_pass.py` derives its search path from it rather than keeping a second list free to drift. 20 tests. **Stated limit, in the module: it verifies the copies the manifest RECORDS**, so an unrecorded copy is invisible to it, and it cannot check the manifest against itself. | (closed) |
| 56 | **An empty result from a locating command was treated as proof of absence.** On 2026-07-29 the locating glob for the capture was `/tmp/claude-*/*/scratchpad` — **three** levels where the real path has **four** (`/tmp/claude-<uid>/<project>/<session>/scratchpad`). It matched nothing. Nothing required a locating command for an irreplaceable artefact to return non-empty, so an unmatched pattern and a genuinely missing file were indistinguishable, and the near-miss was one step from declaring the permanent loss of a file that was sitting on disk. Recorded inside item 51 as an aside; promoted here because it is a rule, not an anecdote. | 2026-07-29 | 2026-07-30 | **An empty locating result is now a FAILED command, not an absence.** Written into `CLAUDE.md`: if a command meant to find the capture returns nothing, widen the search — different glob depths, different roots, search by filename — and report every attempt before concluding anything. The four-level path is spelled out there literally, alongside the three-level glob that fails, with the reason. `run_delta_pass.py`'s not-found message now says the same thing at the point of failure. `tests/test_verify_capture.py::test_the_four_level_scratchpad_glob_is_preserved` parses `_CAPTURE_CANDIDATES` and fails if any `/tmp/claude-` glob is shallower than four levels, so the depth cannot regress silently. | (closed) |
| 57 | **Three records disagreed about whether a global floor comparison existed in `figure_rules.py`, and two were wrong.** `CLAUDE.md` said "the floor is their sum, so a partial parse of either command fails". Item 47 said "with the floor as their sum, **28**". Item 53 said "Global floor removed" *and* "Enforcement was in fact already per-command", which cannot both describe one state without a date. A reader had no way to tell what the code did. | 2026-07-30 | 2026-07-30 | **Settled against the code and against git history, and the wrong documents corrected.** The code as it stands has **no global floor comparison**: `find_violations` compares each command's own parse against its own minimum (`figure_rules.py:438-450`), and the only global assertion is `len(allowed.pairs) < 1` — non-empty, which cannot be mistaken for a threshold. History, verified with `git show <rev>:scripts/figure_rules.py`: at **`8d35321`** a real global comparison gated (`if len(allowed.pairs) < 20`, a hand-picked constant); at **`fa49fc5`** enforcement became per-command and `derived_floor()` existed but its value was only ever **printed** (line 477), never compared; at **`6c6ab21`** `derived_floor()` was deleted and the print replaced with an explicit statement that the two numbers are not comparable. So "a global floor check was removed" is true of `8d35321`→`fa49fc5`, and "no global comparison ever gated" is true only from `fa49fc5` on. **Corrected: `CLAUDE.md`** (rewritten with the three-commit history and both reasons a sum cannot be a threshold — it double-counts five shared proportions, and it would reject healthy output) and **item 47** (the "floor as their sum, 28" clause removed). **Clarified: item 53** (era-stamped). `figure_rules.py` itself was already correct and needed no change. | (closed) |
| 58 | **The CI type-check scope was a hand-maintained list, so a newly tracked module was silently unchecked.** `mypy` named five `analysis/` files literally. Adding a sixth and forgetting to extend the list left it outside the gate while the gate reported green. This is the **fifth** outing of one shape — a check that reports green because what it should examine is out of its scope — after items 17, 35, 36 and 42/45. It fired immediately: `analysis/verify_capture.py` was created and mypy still reported "24 source files", because `analysis/*` in `.gitignore` excluded it and it was therefore invisible to both the ignore-aware tooling and the literal list. | 2026-07-30 | 2026-07-30 | **Scope derived, not typed out.** CI and `CLAUDE.md` both now run `mypy skillwatch/ scripts/ $(git ls-files 'analysis/*.py')`, so a newly *tracked* module is checked automatically and gitignored scratch is not (a bare `mypy analysis/` would try to check local throwaways). `.gitignore` re-includes `analysis/verify_capture.py` with the reason — an untracked verifier is no verifier, it would exist on one machine, which is the same single-point-of-failure shape as the capture it protects. mypy went **24 → 25 source files**. `tests/test_ci_scope.py` (6 tests) asserts the scope stays derived, that every tracked `analysis/*.py` is covered, that ruff still covers all four directories, and that `CLAUDE.md` and CI do not drift apart. Proven non-vacuous: run against `HEAD`'s pre-change `ci.yml`, 6 failed / 5 passed; against the new one, 11 passed. | (closed) |
| 16 | The `lowest-direct` CI matrix has never been *observed* failing. The fix landed in the same commit as the check, so CI has only ever seen it green. A test that would pass if the fix were reverted. | 2026-07-29 | 2026-07-30 | **OBSERVED RED. The matrix is not vacuous.** Run **<https://github.com/kuzivaai/SkillWatch/actions/runs/30500657407>**, throwaway branch `throwaway/floor-negative-control`, head `a4a7c068f1fd820cbd15e7002615f14eadc0e75f`, one line changed (`pyyaml>=6.0.2` → `>=6.0`). Conclusion **failure**. Per leg: `lowest-direct (3.12)` and `(3.13)` — **`Failed to build pyyaml==6.0` / `AttributeError: 'build_ext' object has no attribute 'cython_sources'`**, which is the failure only this matrix catches; `lowest-direct (3.10)` and `(3.11)` — pyyaml 6.0 installed from wheels and the red came from `tests/test_dependency_floors.py::test_load_bearing_floors_are_at_or_above_their_known_good_minimum` (1 failed, 563 passed); `test (3.11)` — same assertion; `test (3.10/3.12/3.13)` cancelled by fail-fast. **`security` PASSED** — the floor audit did *not* catch it, because pyyaml 6.0's `requires_python` admits 3.12/3.13 even though no wheel exists. That is the documented gap the matrix exists to close, and this run corroborates it. **Confound, stated rather than glossed:** the chosen floor trips *two* independent guards, so "all four legs red" overstates what the matrix alone caught — the clean matrix-specific evidence is 3.12 and 3.13. Isolating it fully would need a floor that is unbuildable but absent from the known-good-minimum table. PR [#33](https://github.com/kuzivaai/SkillWatch/pull/33) closed **unmerged** (`state: CLOSED, mergedAt: null`); branch deleted locally and on the remote and `git branch -a` confirms it gone; `main` untouched at `6c6ab21`; `git diff main -- pyproject.toml` empty. | (closed) |
| 22 | `pip-audit --strict` cannot pass in the current invocation shape (editable install → "distribution marked as editable"; non-editable → "not found on PyPI"). The claim that it can *never* pass is untested. | 2026-07-29 | 2026-07-30 | **Tested after five sessions open. The untested strong claim is FALSE, and adopted.** `pip-audit --strict --desc -r <resolved set excluding the project>` exits **0** (47 packages, pip-audit 2.10.1). Measured, all four cells: env scan at version 0.4.1 (published) → **0**; env scan at 0.9.9 (unreleased) → **1**, `skillwatch: Dependency not found on PyPI and could not be audited: skillwatch (0.9.9)`; `-r` shape at either version → **0**. So the original reasoning was **right about the mechanism and wrong about today** — the env-scan shape passes only because `main`'s version equals what PyPI serves, and would fail at the next pre-release bump. The `-r` shape is robust because the project is excluded outright. CI adopts it and **`--skip-editable` is gone** (it was the skip `--strict` rejects); pip-audit is installed in a separate venv so the freeze is SkillWatch's closure and not the auditor's. The 0.9.9 bump was reverted and proven byte-identical. **Superseded by item 60.** At this point no distinguishing case had yet been found; item 60 later demonstrated one and established that the flag is load-bearing. The remaining limit is that it still audits what CI *installed*, not what the ranges *permit*, which remains the floor audit's job. | (closed) |
| 2 | **The repository and the published artefact diverge, and nothing detects it.** Corrected claims reach users only on release; the live PyPI page served two distortions the repository had already fixed. | 2026-07-29 | 2026-07-29 | **CLOSED by the 0.4.1 release.** PyPI serves 0.4.1 (publish.yml run 30479211839, success). `scripts/check_published_claims.py` now exits **0** against the live page: *"No claim violations. No claim-marker drift between HEAD and the live page."* The enforcement built in the previous session held — the gate (`check_release_claims.py`) passed before the release and the report passed after it. Note the class this did NOT cover: figures, as opposed to citations. See item 42. |
| 33 | External findings reached public surfaces without the source's own scope and quantifier — the Trail of Bits scanner-bypass finding and the OWASP AST05 mitigation list. | 2026-07-29 | 2026-07-29 | **CLOSED by the 0.4.1 release.** Both were corrected in-repository on 2026-07-29 and on both distribution PR bodies, but the live page carried them until 0.4.1 shipped. It now carries the corrected text, verified by the live report exiting 0. The class fix (CLAUDE.md citation rule + `scripts/claim_rules.py` + tests) holds. |
| 50 | **Eleven of thirteen flag codes had no reachability assertion.** After `new_domains` and `major_deletion` were found unable to fire through the delta pipeline, a probe was added covering exactly those two — the two already known to be broken, the weakest possible sample. The other eleven went through the same `flags_for` plumbing with nothing asserting they could fire. | 2026-07-29 | 2026-07-29 | Probe extended to **all 13** codes `detector.py` can emit, each with the minimal synthetic input that should produce it. `reachability_complete` asserts the number probed equals the number emittable, read from `detector.py` source, so adding a flag without a probe entry fails the suite. **All 13 turned out already reachable** — no pipeline fix was needed beyond the earlier two. Proven to have teeth: disabling one `detector.py` guard made the probe fail naming `data_uri_payload` (exit=1) and the mutation was reverted, tree clean. **Incidental finding: the enumeration regex `code="[a-z_]*"` silently omits `new_base64` because it excludes digits** — a 13-code set reads as 12. The probe's own reader uses `[a-z0-9_]+`. | (closed) |
| 51 | **The 2026-07-29 HTML capture was held only in an ephemeral session scratchpad.** Its loss would have made two things permanently impossible: re-verifying `DELTA-BASELINE.json`'s derivation, and rehearsing against a source that exercises the TEXT checks — the committed `html_v1` corpus runs only the five HTML checks, which is exactly why a corpus-only rehearsal could not see the `old_text=None` defect. | 2026-07-29 | 2026-07-29 | **Preserved.** Copied to `/home/mkuziva/.skillwatch-archive/realpage-2026-07-29/` (58 MB, 1 file), SHA-256 byte-identical to the source. Integrity manifest committed at `analysis/corpus/realpage/CAPTURE-INTEGRITY.json` — per-page hashes for all 201 pages, so a later session can localise a corrupted copy rather than only detect it. `make_baseline.py` re-run against the preserved path verified **201/201** content hashes and regenerated a byte-identical `DELTA-BASELINE.json`. `--source capture` now searches the archive first. **Near-miss worth recording: the brief's own locating glob `/tmp/claude-*/*/scratchpad` is one directory level too shallow** — the real path has four levels — and returned nothing, which would have led to declaring a permanent loss of a file that was present. | (closed) |
| 53 | **The fail-closed floor compared a non-deduplicated sum against a deduplicated count.** `MIN_PROPORTIONS_PER_COMMAND` sums to 28; the per-command parses sum to 39; the deduplicated allowed set is 34, because five proportions are produced by both commands. The output printed "floor 28" beside "34 distinct", inviting the two to be compared. A global check would also reject healthy output: efficacy 18, base_rate 10, eight overlapping — both minimums met, distinct set 20, below 28. | 2026-07-29 | 2026-07-29 | **Global floor removed rather than reinterpreted.** Per-command minimums are compared against per-command parses and never against the deduplicated total; the only remaining global assertion is that the set is non-empty, which cannot be mistaken for a threshold. The overlap case above is a test. Enforcement was already per-command **as of `fa49fc5`** — the misleading part by then was the printed juxtaposition, which is now replaced by an explicit statement that the two numbers are not comparable. **Clarified 2026-07-30 (item 57):** "already per-command" is true only from `fa49fc5` onwards. At `8d35321` a genuine global comparison *did* gate — `if len(allowed.pairs) < 20`, item 47 — so "no global comparison ever existed" is false of that commit. Two eras, and this entry previously described them as one. Stated limit: **a count floor of any shape cannot detect a parse returning the WRONG proportions** — scraping CI bounds as fractions would keep every count high. | (closed) |
| 54 | **The ledger retained an exact star count after recording that it had been replaced.** Item 10 asserted the exact figure was "replaced by the approximation" while leaving three exact counts in the same sentence. The ledger claimed a correction it had not made — the same shape as a check reporting green over something out of its scope, applied to prose. | 2026-07-29 | 2026-07-29 | Item 10 rewritten to carry only `~32,500, Apache-2.0`. Verified: `grep -rn "32,540\|32541\|32542" OPEN-ITEMS.md docs/` returns nothing. The failed first attempt is recorded in item 10 rather than quietly overwritten. | (closed) |
| 45 | **The figure check tested set membership, not correspondence.** `figure_rules.py` asserted a published `k/n` was *a* proportion the harness produces. It could not detect a current figure under the wrong label: `evasive recall 27/42 (64.3%)` passes, because 27/42 is real, current and arithmetically correct — it is *overall* recall. The fifth recurrence of "a check that validates a value without validating what the value is claimed to be", after items 17, 35, 36 and 42. | 2026-07-29 | 2026-07-29 | The harness's printed metric label is now carried into the allowed set instead of discarded, and both sides — harness label and surface context — are classified into metric families by the same keyword function, which must agree. Text *before* a figure wins over text after it; preferring the trailing window misread two correct figures in one README sentence, which is why the window now stops at a clause boundary. Three alternatives rejected and recorded in the module: exact label matching (fires on correct prose — "Benign false positives" vs "False-positive rate (overall)"), a mandatory per-figure annotation (markup beside every number, and a hand-written annotation can be wrong in the way being guarded against), and positional table parsing (handles tables, not prose, and prose carries most figures). Shown failing on the fixture before the rule existed and passing after; then a negative control relabelled a real README figure, both the test and the gate caught it, and the revert was verified against HEAD as an empty diff. |
| 46 | **`make_baseline.py` was untracked while its output was committed evidence.** It generated `DELTA-BASELINE.json`, which the scheduled delta pass reads to decide items 37, 38 and 43, and existed only in an ephemeral session scratchpad — it would have vanished, leaving a committed artefact nobody could regenerate or audit. Third instance of that shape, after `COMPETITORS.md` (item 34) and `analysis/build_corpus.py` (item 24). | 2026-07-29 | 2026-07-29 | Tracked at `analysis/make_baseline.py`, re-included in `.gitignore` with the reason, and added to the ruff and mypy gates in CI and in CLAUDE.md. It verifies its own output: every reconstructed page's text must hash to the `content_hash` already in MANIFEST.json, and a mismatch fails the run. Re-verified 201/201 on regeneration. |
| 47 | **The fail-closed floor was a hand-picked constant.** `if len(allowed.pairs) < 20` against an actual count of 34. A single global threshold cannot notice one harness command returning nothing while the other's output alone clears it — `measure_efficacy` alone yields 22 proportions, so a total failure of `measure_base_rate` would have passed. | 2026-07-29 | 2026-07-29 | Replaced by `MIN_PROPORTIONS_PER_COMMAND` — a per-command minimum (measure_efficacy 18, measure_base_rate 10) — with each command checked against its own minimum. Current parse: 22 and 17. A test constructs a reference set where one command yielded 0 and asserts the check raises naming that command. **Stated limit, recorded in the module: a count floor cannot detect a parse returning the WRONG proportions** — scraping confidence-interval bounds as fractions would keep the count high. Detecting that needs the parsed values compared against an independently computed expectation. **CORRECTED 2026-07-30 (item 57):** this entry previously read "with the floor as their sum, **28**". There is no sum floor and there has not been one since `6c6ab21`; the sum was only ever *printed*, never compared. The wording is fixed here and the full history is in item 57. |
| 49 | **The delta pass silently disabled two checks, and only a rehearsal found it.** `run_delta_pass.py` called `detect_suspicious_changes(old_text=None, ...)` because the baseline stored only SHA-256 hashes of old text *lines*. `detector.py` guards `new_domains` (line 401) and `major_deletion` (line 414) behind `if old_text:`, so **neither could ever fire** — and `new_domains` is one of the four checks that produce false positives in the synthetic corpus. The scheduled pass would have under-reported the real-page false-positive rate by omitting a quarter of the checks that generate it, and neither the code, the tests nor two handovers said so. | 2026-07-29 | 2026-07-29 | Found by rehearsing, not by reading: the maximal pass emitted nine flag codes and `new_domains` was conspicuously absent. Fixed by storing the full extracted text (1.78 MB; baseline 0.54 MB -> 1.93 MB) instead of line hashes, so `detect_suspicious_changes` is called with a real `old_text` and the project's own `generate_diff`, exactly as `cli.py` calls them — nothing re-derived on the text side. A reachability probe now asserts both codes can be emitted through `flags_for` and fails the rehearsal if either cannot; a mutation restoring `old_text=None` showed both UNREACHABLE and was reverted. |
| 40 | **The taxonomy classified hiding techniques on concealment alone.** `docs/HIDING-TECHNIQUE-TAXONOMY.md` assigned every technique to a bucket on one criterion — does this conceal content from a human reader — which cannot distinguish a detection from a false-positive generator. A second criterion ("is this a canonical accessibility idiom?") was in fact being applied, but was never written down, so it was applied to two techniques and got both backwards. | 2026-07-29 | 2026-07-29 | **Criterion added and every assignment re-derived against it.** A technique is flagged only if it conceals **and** is rare enough on ordinary pages to be signal. The second half is now measured (item 37). Two techniques moved out of the flagged bucket: the HTML `hidden` attribute (55.2% of 201 real pages, 1534 occurrences — a UI-state primitive) and off-screen absolute positioning (WebAIM: *"the recommended styles for visually hiding content that will be read by a screen reader"*). The inconsistency the prompt identified — off-screen positioning flagged while `text-indent` was excluded, though both are forms of one legacy `.sr-only` idiom — is resolved on the primary source, which says off-screen is the recommended form and `text-indent` the one with "better techniques available". Also corrected: the document named `clip-path: inset(100%)`; the canonical ruleset uses `inset(50%)` and `clip: rect(1px,1px,1px,1px)`. The implementation was unaffected because the exclusion is an absence rather than a value match — luck, not design, and recorded as such. Class fix: `TECHNIQUE_BUCKETS` in `detector.py` is the single source of truth in code, and `tests/test_hiding_taxonomy.py` fails if it and the document disagree. Shown failing 7/22 before, passing 22/22 after. Cost, not netted off: corpus items E-24 and E-31 were caught and are now missed. |
| 41 | **The `UNEVALUABLE` branch shipped without a fixture proving it fires.** `_Concealment` is three-valued so unparseable CSS is never silently reported as "nothing is hidden" — the fail-open shape of item 17. But every line producing UNEVALUABLE was uncovered at `2a11dd0`, including `_Concealment.__bool__` (detector.py:622), which nothing had ever called. By this project's own rule — a rule which has never fired has not been tested — the guarantee was untested. | 2026-07-29 | 2026-07-29 | `tests/test_concealment_unevaluable.py`, 25 fixtures forcing a malformed declaration block, an unparseable `<style>` rule, an at-rule, an empty selector, and five selectors the selector engine rejects. Because the branch already worked, no honest fail-before exists; two mutations were run instead and reverted, neither committed: returning VISIBLE where UNEVALUABLE belongs (1 failed, 22 passed — reported as one rather than implied broad), and `__bool__` returning True (3 failed, 20 passed), which proves line 622 is load-bearing rather than merely executed. `detector.py` coverage 95% → 98%, uncovered 14 → 5. Of the 5 remaining, 732 and 815-816 are unreachable *by configuration* — both techniques moved to bucket (b) — not untested. |
| 39 | The taxonomy stated the two remaining structural misses were "E-23 and E-25". | 2026-07-29 | 2026-07-29 | **Wrong, and corrected.** `E-25` is recorded in the corpus as family `language` (a Vietnamese instruction outside the 7-language pattern set), not `structural`. The structural misses were E-07 and E-23, both comment injection. Found by listing every evasive item's recorded family against the harness's per-family totals: semantic 13, mechanical 7, structural 10, language 2, summing to 32, and the caught/missed split reconciling exactly with the reported 3/13, 7/7, 8/10, 1/2. No other item's recorded family conflicts with how it is counted or described anywhere in the repository. |
| 5 | `PATTERNS.md` did not record which upstream version the 32 patterns were derived from, so drift was observable but not measurable. This blocked item 4. | 2026-07-29 *(at latest)* | 2026-07-29 | Provenance section added to `PATTERNS.md`. Derivation date **2026-06-26** is evidenced (`git log --reverse` on `detector.py`). Version **v3.5.1** (`22463fc82033a427708e655f0549cf15aa8c75e6`) is **REASONED, not evidenced**: it was the only ATR release available on that date (published 2026-06-21; next release v3.5.3 not until 2026-06-30), but nobody recorded which version was actually consulted. A future session should treat v3.5.1 as a hypothesis to check. **This unblocks item 4** — the v3.5.1→v3.5.11 diff is now computable. |
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
- **Wilson gates are directional, never point-estimate gates:** use the lower
  bound when higher is better and the upper bound when lower is better.
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
- **A check must validate what a value is CLAIMED to be, not only the value.** Five
  defects here have been one shape: an unparseable specifier treated as satisfied
  (17), a guard blind to the published artefact (35), a regex that could never match
  (36), a guard blind to figures (42), and a figure check that tested set membership
  rather than correspondence (45). When you add a check, ask what it cannot see, and
  write that down where it is defined.
- **A count is not an accounting.** If a reference set audits anything, enumerate
  its members in the evidence. "34 proportions" did not let a reader verify that the
  five figures the live page publishes were covered (48).
- **Rehearse before the one-shot run.** Code whose first execution is the
  measurement it exists to take must be exercised offline first. Rehearsing the
  delta pipeline found two checks that could never fire (49).
- **Figures are claims, and are checked like claims.** Every `k/n (p%)` on a
  published surface must be a proportion the harness currently produces
  (`scripts/figure_rules.py`, in CI and in the pre-release gate). Historical and
  hypothetical figures carry an explicit `<!-- figures:exempt reason="..." -->`
  region; they are never inferred from prose. Find every exemption with
  `git log -S "figures:exempt"`.
- **When you add a check, ask what it cannot see.** Four defects in this
  repository have been the same shape — a check reporting green because its
  subject was out of scope: an unparseable specifier treated as satisfied (17), a
  guard that could not see the published artefact (35), a regex that could never
  match (36), and a claims guard blind to figures (42). Each new check states its
  own blind spots where it is defined.
- **A gate that is added or materially changed requires a negative control before
  it is relied on.** Green means it did not object today, not that it works. Make
  it red on purpose against a stimulus named in advance, on a throwaway branch,
  then record the result in the gate table in `CLAUDE.md`.
  `tests/test_gate_table.py` fails if a job or a tracked script is added without an
  entry. Closing this one instance at a time is what let it recur six times
  (17, 35, 36, 42/45, 16, 59), the sixth created by the fix for the fifth.
- **An accounting must validate behaviour, not identity.** A table saying a gate
  HAS a status certifies its name, not what it does; `security` was rewritten under
  its own name and kept a never-observed-red verdict (64). Every job row carries a
  digest of its executable surface **and its trigger block**, because a gate that
  stops running is not a gate. Do not update a drifted hash on its own: that records
  the change and asserts nothing about whether the gate still refuses anything.
- **A rule that has never fired has not been tested, and "no case was found" is not
  "no case exists".** `--strict` was carried for five sessions as undemonstrated
  debt on the strength of four failed attempts to make it fire (60). The case was
  found by reading the tool's source for where its fatal condition is raised, rather
  than by guessing at more inputs. When a rule resists demonstration, read the
  implementation before concluding it is decoration.
- **A negative control's stimulus is usually confounded, and the confound is part
  of the result.** `lowest-direct` (16): the chosen floor `pyyaml>=6.0` tripped two
  independent guards, so "all four legs red" overstates it. The 3.10 and 3.11 legs
  went red on `test_load_bearing_floors_are_at_or_above_their_known_good_minimum`,
  which any leg would have caught; **only 3.12 and 3.13 are matrix-specific
  evidence**, failing on `Failed to build pyyaml==6.0`. `security` (59):
  `jinja2==2.11.3` is also rejected by the floor auditor, but step ordering meant
  the floor step never ran, so the attribution holds. State the confound with the
  result; a control reported as clean when it was not is worse than no control.
- **Pattern refresh and efficacy measurement are separate commits.** Refresh
  first, measure second. Doing both at once makes the comparison circular.
- **The floor auditor has no allowlist.** A requirement with no lower bound is the
  maximum-exposure case, not an exempt one.
# Codex onboarding handover

This is the tracked entry point for Codex sessions in SkillWatch. Read this file,
`CLAUDE.md`, and `OPEN-ITEMS.md` before editing. `OPEN-ITEMS.md` is the canonical
continuity ledger; update it in the same commit as any item opened or closed. Do
not use ignored local handovers as an authority source.

## Current transition

The branch `feat/archive-durability-and-strict-audit` contains five reconciled
commits above `origin/main`:

1. `852fd72` — capture absence/corruption verification, durable copy registry,
   derived mypy scope, and strict resolved-dependency auditing.
2. `17ab8f1` — continuity-ledger closures and corrected dependency-floor history.
3. `fe66903` — observed-red security control, complete gate accounting, and
   mechanically checked onboarding facts.
4. `fd4f4a9` — workflow behavior/trigger digests and drift enforcement.
5. `4b366c5` — observed-red build control and demonstrated load-bearing
   `pip-audit --strict` behavior.

An independent adversarial review on 2026-07-31 received only the five-commit
diff, the committed verification record, and `OPEN-ITEMS.md`. Its two MEDIUM
findings were independently reproduced and fixed:

- malformed nonempty capture copy registries now produce the documented
  `UNUSABLE` result and exit 4 instead of an uncaught exception;
- gate canonicalisation ignores `name` only for job/step display labels and
  retains behavior-bearing nested inputs such as `with.name`.

No HIGH findings were reported. Ledger items 68 and 69 contain the reproductions
and resolutions. The remaining risks are ledger items 3, 9, 11, 31, 63, and 66;
in particular, the real `publish` job has never been observed red and must not be
tested against production PyPI without explicit maintainer authority.

The subsequent push-readiness pass added four focused local commits:

1. `ed3ee71` — make dated session evidence logs trackable.
2. `fa748d4` — persist the repository, PR #34, and remote baseline.
3. `86f77ff` — reconcile ledger items 22 and 60 and add continuity tests.
4. `55c067d` — close two further MEDIUM adversarial findings by proving existing
   logs are tracked and encoding the `22 -> 60` supersession structurally.

The second independent review received only the session diff, committed test
output, and the ledger. It reported no HIGH and two MEDIUM findings; both were
reproduced, fixed, regression-tested, and recorded as ledger item 72.

## Final local verification (2026-07-31)

- `git diff --check origin/main..HEAD` — pass.
- Offline citation check, `pytest -q tests/test_published_claims.py` — 8 passed.
- Citation self-test, `pytest -q tests/test_claim_rules.py` — 11 passed.
- `ruff check skillwatch/ tests/ scripts/ analysis/` — pass.
- `mypy skillwatch/ scripts/ $(git ls-files 'analysis/*.py')` — 25 files clean.
- Full suite with coverage — 633 passed, 95.70% coverage.
- `python scripts/figure_rules.py` — pass, 34 distinct proportions.
- `python scripts/audit_dependency_floors.py` — 20 floors audited, pass.
- `python analysis/verify_capture.py` — all 3 copies verified.
- `python -m build` — sdist and wheel built successfully.
- `npm run lint` — not applicable: this Python repository has no `package.json`.
- Markdown render path — `CLAUDE.md`, `OPEN-ITEMS.md`, and this handover rendered
  with Pandoc and were visually inspected.

Set `PYTHONDONTWRITEBYTECODE=1` for verification runs. The canonical commands and
the reasons behind them are maintained in `CLAUDE.md`.

## Current readiness truth

Do not infer readiness from historical prose or copy current values into this
file. `docs/readiness-status.json` is the structured current source;
`SHIP-READINESS.md` contains its generated/validated scoreboard, and
`scripts/readiness_consistency.py` checks it against the efficacy harness,
condition-specific evidence and ledger sections. Read that scoreboard before
making any readiness statement.
# SkillWatch

Periodic URL content monitoring for AI agent skills and MCP tools.

## Quick commands

```bash
# Setup
python3 -m venv .venv && source .venv/bin/activate && pip install -e ".[dev]"

# Export this for the session. See "Bytecode caching" below — it is not optional
# when you are about to trust a before/after result.
export PYTHONDONTWRITEBYTECODE=1

# Test
pytest --cov=skillwatch --cov-report=term-missing -q

# Lint  (same scope as CI — analysis/ is evidence for published figures)
ruff check skillwatch/ tests/ scripts/ analysis/

# Type check  (same scope as CI — the analysis/ list is DERIVED, not typed out,
# so a newly tracked module cannot escape the gate. tests/test_ci_scope.py
# asserts CI keeps deriving it.)
mypy skillwatch/ scripts/ $(git ls-files 'analysis/*.py')

# Published figures must match the harness (CI step + pre-release gate)
python3 scripts/figure_rules.py

# Structured current readiness, generated scoreboard, harness and ledger agree
python3 scripts/readiness_consistency.py

# Dependency floor audit (security gate — must exit 0)
python3 scripts/audit_dependency_floors.py

# Verify the irreplaceable 2026-07-29 capture BEFORE anything relies on it.
# exit 0 all copies verified / 2 a copy is missing / 3 a copy is present but
# corrupt / 4 the manifest is unusable.
python3 analysis/verify_capture.py

# Build (no publish)
python3 -m build

# Efficacy measurement
python3 analysis/measure_efficacy.py
```

### Bytecode caching

**Set `PYTHONDONTWRITEBYTECODE=1` before any run whose result you intend to
believe.** CI sets it at workflow level in `.github/workflows/ci.yml`; locally it
is on you.

CPython decides a cached `.pyc` is still valid by comparing the source file's
**mtime and size** against the header stored in the cache. mtime has whole-second
granularity. So two edits within the same second that leave the file the same
size — changing `3` to `4`, flipping a comparison operator — are indistinguishable
from no edit, and Python silently runs the old bytecode.

This has produced a false result in this repository: a test was edited, re-run
inside the same second, and reported passing from pre-change bytecode. The
conclusion drawn — that the change was unnecessary — was wrong.

`find . -name __pycache__ -type d -exec rm -rf {} +` also works but protects only
the machine and the moment where someone remembers to run it. The environment
variable removes the failure mode rather than sweeping up after it.

## Architecture

Thirteen Python modules under `skillwatch/`:

| Module | Purpose |
|---|---|
| cli.py | Argparse CLI, subcommand dispatch (15 subcommands) |
| parser.py | Extract URLs from SKILL.md, MCP configs, URL lists |
| fetcher.py | HTTP fetch with SSRF protection, DNS pinning, text extraction |
| detector.py | 13 heuristic flag codes, 32 prompt injection patterns, canonicalisation (HTML comments, reversed text, ROT13), plain-language flag explanations |
| differ.py | Unified diff generation, content comparison |
| store.py | SQLite storage (7 tables: urls, snapshots, alerts, sources, ledger, anchors, flag_feedback) |
| formatter.py | Terminal output formatting, ANSI colours |
| ssrf.py | SSRF validation, DNS pinning adapter |
| sarif.py | SARIF 2.1.0 output for CI / GitHub Code Scanning |
| ledger.py | Append-only tamper-evident content ledger |
| anchoring.py | RFC 3161 timestamp anchoring (optional `anchor` extra) |
| cloak.py | Cloaking detection across fetch strategies |
| __init__.py | Version declaration |

Seven tracked scripts under `scripts/`: `audit_dependency_floors.py`,
`check_published_claims.py`, `check_release_claims.py`, `claim_rules.py`,
`figure_rules.py`, `readiness_consistency.py`, `refresh_confusables.py`. This said "Two" until 2026-07-30,
which was stale from the moment the claims and figure checks landed. Regenerate it
with `git ls-files 'scripts/*.py'` rather than counting by hand; which of them are
gates is recorded in the gate table below, and `tests/test_gate_table.py` fails if
a new one is added without being classified.

Six tracked modules under `analysis/`: `build_realpage_corpus.py`,
`make_baseline.py`, `measure_base_rate.py`, `measure_efficacy.py`,
`run_delta_pass.py`, `verify_capture.py`. The efficacy harness is
`analysis/measure_efficacy.py`; the rest of `analysis/` except `corpus/` and these
tracked modules is gitignored.

## Settled constraints

These are closed findings from the five-prompt forensic audit. Do not re-litigate.

- **The regex triage is evadable by design.** Current harness output is 64.3% overall recall (27/42, CI [49.2%, 77.0%]) and 53.1% against evasive adversaries (17/32, CI [36.4%, 69.1%]). Semantic evasions (indirect instruction, polite framing, narrative framing) bypass detection by design. This is documented honestly and is not a bug to fix. The tool is a URL change monitor with best-effort triage, not a detection tool. Historical measurements are archived and are not current facts.
- **"Periodic, not continuous."** The tool runs via cron or CI. It has no daemon mode, no schedule trigger, no unattended monitoring. All user-facing text uses "periodic" or "periodically." Do not introduce "continuous" or "continuously."
- **No ML or LLM detection.** The detector is regex/keyword/DOM-based. Proposals to add semantic detection are out of scope.
- **Published; readiness and demand remain distinct.** PyPI serves 0.4.1 (2026-07-29); this repository declares 0.4.1 in `pyproject.toml`. GitHub Pages is live. Do not duplicate current readiness values here: read `docs/readiness-status.json` and its generated/validated `SHIP-READINESS.md` scoreboard. Open work is tracked in `OPEN-ITEMS.md`.
  <!-- Both version numbers above are checked, not trusted. The declared one is checked
  offline by tests/test_claude_md_currency.py against pyproject.toml; the published one
  is checked against the live index by scripts/check_published_claims.py. By hand:
      grep '^version' pyproject.toml
      python3 -c "import json,urllib.request; print(json.load(urllib.request.urlopen('https://pypi.org/pypi/skillwatch/json'))['info']['version'])"
  This sentence previously read "PyPI serves 0.3.0 (2026-07-11); main is 0.4.0" and
  BOTH halves were false as of 2026-07-30: PyPI had served 0.4.1 since 2026-07-29
  and main was 0.4.1. It briefed every session with a wrong fact for a day.
  The comment sat mid-bullet when first written, which broke the list item in two;
  moved to the end 2026-07-30. -->

- **Precision is not a ship gate and must not be published as a deployment property.** It depends on the corpus benign:malicious ratio, which deployment does not share. The transferable figure is the benign false-positive rate. See SHIP-READINESS.md condition 2 for the arithmetic.
- **Positioning is OWASP AST05, partially.** SkillWatch addresses AST05 "Untrusted External Instructions" in the OWASP Agentic Skills Top 10 (v1.0, 2026 Edition). Of the six preventive mitigations the AST05 page lists, SkillWatch covers one ("Maintain fleet-wide visibility of referenced sources") and part of two ("Pin and verify referenced content" — alerts on drift, does not refuse it; "Rescan continuously" — this tool is periodic by design and does **not** satisfy that mitigation as OWASP words it). It does not address the other three. Never write that the AST05 mitigations "describe what this tool does." That project is **early-stage, not a flagship standard**, and its own pages describe its status inconsistently (incubator vs new project proposal) — check the current status before repeating any maturity claim, and never imply endorsement. AST07 "Update Drift" is adjacent (version pinning) and may be cited only as a partial fit.

### Citing external findings on a public surface

An external finding quoted on any public surface — README, `docs/`, PyPI, a
pull-request body, launch copy — must carry **the source's own scope and
quantifier**. Not a downstream paraphrase of them, including OWASP's paraphrase
of someone else's work.

- Go to the primary source. If you found the claim in a secondary source that is
  itself citing a third party, fetch the third party. Secondary sources compress,
  and compression is where scope and quantifiers get lost.
- **Paste the source sentence verbatim into the commit message** so a later
  session can compare the surface text against the source without refetching.
- Attribute to whoever did the work, not to whoever you read it in.
- Never silently alter a quoted word to fit this project's constraints. If OWASP
  says "continuously" and this tool is periodic, say both.

Worked example of the failure this rule exists to prevent. Trail of Bits wrote
that it "took us less than an hour to conceive and implement three of the four
malicious skills". OWASP's incident timeline compressed that to "every public
skill scanner tested … is bypassed in under an hour" — moving the hour from
*building three of four attacks* to *bypassing scanners*, and dropping the fourth
attack that took a few hours. This README repeated OWASP's compression. Two hops,
two distortions, one public surface.

`tests/test_published_claims.py` enforces the mechanical half of this: a cited
finding on a public surface must be accompanied by a source URL.

### The 2026-07-29 real-page capture lives outside the repository

`analysis/corpus/realpage/DELTA-BASELINE.json` was derived from 56.2 MB of raw HTML
captured on 2026-07-29 (the containing `fetched_pages.json` is 60.0 MB / 59,968,045
bytes — the 56.2 MB is the sum of the page HTML itself). That HTML is **not committed**
and is **not in /tmp**.

**Run the verifier before anything relies on it:**

```bash
python3 analysis/verify_capture.py            # sample of per-page hashes
python3 analysis/verify_capture.py --all-pages # all 201
```

Exit codes are the contract, because the two failures need opposite responses:
`0` all recorded copies verified · `2` **MISSING** — a copy is absent, restore it *from*
a verified copy · `3` **CORRUPT** — a copy is present and wrong, do **not** restore the
others *from* it · `4` the manifest is unusable. `3` outranks `2` when both occur,
because reporting only the absence would invite restoring from the corrupt copy.

**Where every copy lives.** All three are recorded in
`analysis/corpus/realpage/CAPTURE-INTEGRITY.json` under `copies`, which is the single
registry — `run_delta_pass.py` derives its search path from it rather than keeping a
second list.

| Path | Medium | Survives | Dies with |
|---|---|---|---|
| `/home/mkuziva/.skillwatch-archive/realpage-2026-07-29/fetched_pages.json` | WSL2 ext4 (`/dev/sdd`), inside the VHDX on C: | — (primary) | `wsl --unregister`, distro reset, ext4/VHDX corruption, C: loss, Disk 0 failure |
| `/mnt/d/skillwatch-archive/realpage-2026-07-29/fetched_pages.json` | NTFS on D: (Disk 0 partition 5), outside the VHDX | VHDX loss, distro reset, **a C: reimage** | Disk 0 failure, an OEM recovery reformat of D:, machine loss |
| `/mnt/c/Users/mkuzi/skillwatch-archive/realpage-2026-07-29/fetched_pages.json` | NTFS on C: (Disk 0 partition 3), outside the VHDX | VHDX loss, distro reset, **a D: reformat** | C: loss, Disk 0 failure, machine loss |

**The independence is PARTIAL, and saying otherwise would be false.** Windows reports
exactly one physical disk on this machine — Disk 0, `RS1D0TSSD510`, NVMe, 1,024,209,543,168
bytes. C: is partition 3 and D: is partition 5 **of that same disk**, and the WSL2 ext4
filesystem is a VHDX file on C:. So all three copies share one physical device. What the
second and third copies do close is the largest real-world class for a WSL user:
anything destroying the ext4 filesystem or the VHDX leaves both NTFS copies untouched,
and a C: reimage leaves the D: copy untouched.

**Residual risk, unmitigated:** failure of Disk 0, and loss/theft/destruction of the
machine. Both take all three copies. Closing them needs an off-machine destination,
which is outside this project's local-only boundary (no user→server data channel; the
only outbound traffic is fetching user-specified URLs) and is therefore the user's
decision, not a session's. An OneDrive folder exists at `/mnt/c/Users/mkuzi/OneDrive`
and would close it, at the cost of pushing 56.2 MB of third-party HTML into a personal
cloud account. **Not done — flagged for the user.**

`analysis/run_delta_pass.py --rehearse --source capture` and
`analysis/make_baseline.py --source <path>` both depend on the capture, and both now
verify before loading: `--source capture` refuses a corrupt copy, and an explicit path
is verified if it is a recorded copy or else announced as `UNVERIFIED`. A verifier
nobody runs is the defect one level up from the one the copies fix.

**What the verifier cannot see.** It verifies the copies the manifest *records*. A copy
made and never recorded is invisible to it, and it cannot check the manifest against
itself — the manifest is the reference. Recording a new copy is therefore a committed,
reviewable manifest edit rather than a disk scan.

**Why it matters that this survives.** Two things become impossible without it:
re-verifying the baseline's derivation, and rehearsing against a source that
exercises the **text** checks. The committed `html_v1` corpus runs only the five HTML
checks, which is exactly why a corpus-only rehearsal could not see the
`old_text=None` defect that disabled `new_domains` and `major_deletion`.

**An empty locating result is a FAILED command, not an absence.** If a command meant
to find this file returns nothing, do not conclude it is gone. Widen the search —
different glob depths, different roots, search by filename — and report every attempt.
Concluding absence from a single unmatched pattern is how an irreplaceable artefact
gets written off while still sitting on disk.

If you are hunting for it in a scratchpad, the path is **four** levels deep:

```
/tmp/claude-<uid>/<project>/<session>/scratchpad/fetched_pages.json
/tmp/claude-1000/-home-mkuziva-skillwatch/*/scratchpad/fetched_pages.json
```

A **three**-level glob (`/tmp/claude-*/*/scratchpad`) matches nothing and makes a
present file look permanently lost. That near-miss actually happened on 2026-07-29 —
the brief's own locating glob was one level too shallow — and is ledger item 51.
`tests/test_verify_capture.py::test_the_four_level_scratchpad_glob_is_preserved`
asserts the depth stays at four.

### Figures are claims too

`scripts/claim_rules.py` checks **citations**. `scripts/figure_rules.py` checks
**figures**: every `k/n (p%)` on a published surface must be a proportion the
harness currently produces, and its percentage must match its own fraction.

The allowed set is **the harness's own stdout**, parsed — not a table of expected
values maintained beside it. A second copy of the figures is free to drift from
the first, which is the defect one level up. If the harness output format changes,
the parsed set collapses and the check fails closed rather than passing vacuously.

**Correspondence, not membership.** A published figure must match the metric it is
LABELLED with, not merely appear somewhere in the harness output. Set membership
cannot see a substitution: `evasive recall 27/42 (64.3%)` is a real, current,
arithmetically correct proportion — it is *overall* recall — so a membership check
passes it while the surface tells the reader something false. Both sides are
classified into metric families by the same keyword function and the families must
agree. Text *before* a figure wins over text after it, because a label almost always
precedes its number.

A figure naming no metric cannot be correspondence-checked. `scripts/figure_rules.py`
counts those and prints the coverage, so what the rule does not cover is stated
rather than implied.

**The fail-closed floor is per-command, and there is deliberately NO global floor.**
`MIN_PROPORTIONS_PER_COMMAND` gives each harness command its own minimum, and each
command's *own parse* is compared against its *own* minimum. Their sum is never
compared against anything.

This sentence previously said "the floor is their sum." That was wrong as of commit
`6c6ab21` and is corrected here on 2026-07-30. Two reasons the sum cannot be a
threshold. It double-counts: five proportions are produced by both commands, so the
sum (28) is not commensurable with the deduplicated distinct count (34). And it would
reject healthy output: efficacy 18 and base_rate 10 with eight overlapping meets both
minimums while the distinct set is 20, below 28 — and a gate that fails on healthy
output is a gate someone removes.

The history, since three documents disagreed about it:

- At `8d35321` a genuine global comparison did gate — `if len(allowed.pairs) < 20`, a
  hand-picked constant against an actual count of 34. Ledger item 47.
- At `fa49fc5` enforcement became per-command. `derived_floor()` still existed but its
  value was only ever **printed**, never compared. The misleading part from here on
  was the printed juxtaposition of "floor 28" beside "34 distinct".
- At `6c6ab21` `derived_floor()` was deleted and the print replaced with an explicit
  statement that the two numbers are not comparable.

So "a global floor check was removed" is true of `8d35321`→`fa49fc5`, and "no global
comparison ever gated" is true only from `fa49fc5` onwards. Both statements were in
the repository, unqualified, describing different eras as if they described the same
one.

The only global assertion left is that the reference set is non-empty, which cannot be
mistaken for a threshold. A count floor of any shape still cannot detect a parse
returning the WRONG proportions — scraping confidence-interval bounds as fractions
would keep every count high. Detecting that needs the parsed values compared against
an independently computed expectation.

Historical and hypothetical figures are legitimate — release-to-release tables,
counterfactuals, dated review records. They are marked explicitly:

```
<!-- figures:exempt reason="0.3.0 to 0.4.1 release comparison" -->
| Overall recall | 15/20 (75.0%) | 21/35 (60.0%) | 27/42 (64.3%) |
<!-- figures:end -->
```

A `reason=` is required so a reviewer can audit the exemption; an unclosed region
is a violation rather than a silent exemption of the rest of the file. Find every
one with `git log -S "figures:exempt"`.

**Why this exists.** On 2026-07-29 the detector was rewritten and re-measured, and
six surfaces went on publishing the pre-rewrite numbers — a benign false-positive
rate of 4/32 (12.5%) where the harness produced 7/37 (18.9%). `SHIP-READINESS.md`
contradicted itself inside one file. **This is the fourth recurrence of one shape:
a check that reports green because what it should examine is out of its scope** —
after an unparseable specifier treated as satisfied, a guard that could not see the
published artefact, and a regex that could never match. When you add a check, ask
what it cannot see.

### The claims checks: one gate, one report, and why they cannot be merged

The rules live in **`scripts/claim_rules.py`** — one entry point,
`find_violations(text, source=...)`, taking arbitrary text. Three callers run the
same rules against three different subjects:

| Check | Subject | Role | Blocking? |
|---|---|---|---|
| `tests/test_published_claims.py` | repository files | CI | yes, in CI |
| **`scripts/check_release_claims.py`** | `README.md` + a freshly built sdist's `PKG-INFO` | **THE GATE** | **yes — run before every release** |
| `scripts/check_published_claims.py` | the live PyPI long description | **THE REPORT** | **no — never gate on it** |

**Why they cannot be the same check.** The gate asks *"is what we are about to
publish correct?"* — answerable, and true, before a release. The report asks *"is
what is currently published correct?"* — which nothing but a release can make
true. Gating a release on the report would deadlock: the live page stays stale
until you release, and you could not release until the live page stopped being
stale. Run the report on a schedule or after a release, never as a precondition
for one.

The report **exits non-zero when it cannot reach PyPI**, and says so. A check that
could not inspect its subject has not passed.

**Release procedure — the gate is a required step:**

```bash
python3 scripts/check_release_claims.py     # must exit 0. Do not release otherwise.
gh release create vX.Y.Z --title "vX.Y.Z" --notes-file <notes>
python3 scripts/check_published_claims.py   # after the release; expect exit 0 once PyPI updates
```

**Why this exists.** On 2026-07-29 the repository corrected two misquoted external
claims and `tests/test_published_claims.py` went green — while the live PyPI page
carried both distortions for the rest of the day. The guard read four repository
paths and its own docstring said it "does not fetch anything", so the most public
surface this project has was outside its scope. Same fail-open shape as the
dependency auditor treating an unparseable specifier as satisfied: **a check that
passes because what it should examine is out of scope.**

**A rule that has never fired has not been tested.** One of the original negative
rules shipped vacuous — its span was `[^.\n]{0,60}` where the text it was written
to catch had 94 characters and a newline in that position, so it could never
match and passed against the very README it was meant to flag. Every negative
rule now has a positive fixture in `tests/test_claim_rules.py` proving it fires.
Add one for any rule you add.

### Every gate, and whether it has ever been seen to refuse anything

<!-- gate-table:rule -->
**A gate that is added or materially changed requires a negative control before it
is relied on.** Green is not evidence that a check works. Green is evidence that it
did not object today, and a check that has never objected is indistinguishable from
a check that cannot. Make it red on purpose, on a throwaway branch, against a
stimulus you named in advance; then record the result in the table below.

The rule exists because the shape keeps recurring. It has been logged six times
(items 17, 35, 36, 42/45, 16, 59), and the sixth was *created by the fix for the
fifth*: the commit that closed `lowest-direct` by running a negative control also
rewrote the `security` job, which then inherited the identical problem. Closing
instances one at a time is how a class survives. The table is what makes the class
checkable, and `tests/test_gate_table.py` fails if a job or script is added without
an entry.

Status is one of exactly three values. **RED OBSERVED** with a run URL or a pasted
exit code, **never observed red**, or **unknown**. If a gate's history cannot be
established from CI or from the repository, write `unknown`. Do not infer.
<!-- gate-table:rule-end -->

CI history below is **exhaustive, not sampled**: all 81 `ci.yml` runs and all 4
`publish.yml` runs that exist as of 2026-07-30 were inspected. `ci.yml` has 4
failures; `publish.yml` has none.

**The `Executable hash` column is what stops this table certifying a gate it has
not examined.** A name and a status record a gate's *identity*. They cannot notice
that a job was rewritten under the same name and silently kept its old verdict,
which is precisely what happened to `security` on 2026-07-30. Each job's row
therefore carries a digest of what that job actually executes, and
`tests/test_gate_table.py` fails when a job's current digest stops matching, with
the message that the gate changed materially and needs a fresh negative control.
The status must then be read as `unknown`, and a second test enforces that it
cannot say anything else while the hash is drifted.

**Do not update a drifted hash on its own.** That records that the change happened
and asserts nothing about whether the gate still refuses anything. Run the control,
then update the status, the evidence and the hash together.

**What the hash covers, and why it is not "`run:` lines only".** Hashing the whole
workflow *file* was considered earlier and rejected, correctly: it fires on comment
edits and gets switched off within a week. The obvious narrowing is to hash only
executable `run:` lines, mirroring `pip_audit_run_lines()` in
`tests/test_ci_scope.py`. **That narrowing is wrong here, and measurably so.** The
`publish` job has **zero** `run:` lines, so a run-lines-only digest for it is
`sha256("[]")` regardless of what the job does. It would be blind to:

- `needs: build` — the ordering that keeps a failed build from ever reaching PyPI,
  and the entire safety argument for the 2026-07-30 `build` control;
- `environment: pypi` and `permissions: id-token: write`;
- the pinned SHA of `pypa/gh-action-pypi-publish`.

A digest blind to all of that is the defect being closed, not a fix for it. So the
hash is over the **parsed job specification** with cosmetic keys removed. Parsing as
YAML drops comments, blank lines and trailing whitespace *inherently*, which is a
stronger normalisation than stripping them by regex, and it keeps step order
significant — correct, because step ordering is what isolated the pip-audit step
from the floor step in the `security` control.

**The hash also covers the workflow's `on:` block, and that was found by doing, not
by reasoning.** An earlier draft hashed the job specification alone. The build
negative control then added `workflow_dispatch:` to `publish.yml` to make an
otherwise unreachable workflow reachable, and the hash did not move, because `on:`
sits outside `jobs:`. A job's behaviour is not only what it runs but **when** it
runs: changing `ci.yml`'s `on:` from `[push, pull_request]` to `[push]` would stop
every pull request being gated at all while every job line stayed byte-identical.
A gate that no longer runs is not a gate. Both directions are asserted in
`tests/test_gate_table.py::test_the_trigger_block_is_part_of_every_job_hash`.

One trap worth knowing if you touch that code: under YAML 1.1 the bare key `on`
parses to the **boolean True**, not the string `"on"`. `data["on"]` returns nothing
on every workflow here, and a digest built on it would silently omit the trigger
from every hash. Both spellings are read.

`name:` on a job or a step deliberately does **not** move the hash: a rename changes
nothing that executes. This exception is schema-aware, not recursive. A nested
action input such as `with.name` remains behavior-bearing and does move the hash.
The original implementation removed every nested key named `name`, which made the
hash blind to artifact and package-name changes; ledger item 69 records the repair.
The cost of ignoring display labels is real and is stated rather than hidden: the
evidence cells below quote step names, so a rename can leave the prose stale while
the hash stays green. That is a documentation problem, not a gate-behaviour one.

**Reasoned, not evidenced,** and recorded as such: no source was searched for or
found on how workflow-gate drift is detected elsewhere, because this is a
repository-specific accounting problem rather than a general one. The design rests
on one assumption — that behaviour is fully determined by the parsed job spec minus
display names. The observation that would overturn it is a job changing behaviour
with an unchanged spec, which composite actions and `${{ }}` expressions over
repository variables could both produce. It is cheap to reverse: delete one column
and three tests.

**Repository-side gates are NOT hashed**, and that hole is left open deliberately
rather than papered over. `scripts/*.py` can be rewritten under the same name and
keep their status, exactly as `security` did. A hash of the source text would fire
on comment edits, which is the rejected shape; the right instrument is a digest over
the parsed AST with docstrings stripped. Not built. See the ledger.

<!-- gate-table:start -->
| Gate | Kind | Executable hash | Ever observed red | Evidence |
|---|---|---|---|---|
| `test` | CI job (matrix 3.10-3.13) | `b96b822b258e` | RED OBSERVED | <https://github.com/kuzivaai/SkillWatch/actions/runs/30442289082> `test (3.13)`, 2026-07-29; also 30503588045 `test (3.11)` on a Dependabot ruff bump |
| `security` | CI job | `576042ed1d31` | RED OBSERVED | <https://github.com/kuzivaai/SkillWatch/actions/runs/30526422428>, 2026-07-30, PR #38 closed unmerged. Failed at step *Audit resolved dependencies (--strict, no skip flags)* on `jinja2 2.11.3`, reporting PYSEC-2026-1471/1473/1474/1475; the later floor step was `skipped` |
| `lowest-direct` | CI job (matrix 3.10-3.13) | `2496d1c17fbe` | RED OBSERVED | <https://github.com/kuzivaai/SkillWatch/actions/runs/30500657407>, 2026-07-29, all four legs. **Confounded**: see the note below |
| `build` | CI job (`publish.yml`) | `055e7e4ff69e` | RED OBSERVED | <https://github.com/kuzivaai/SkillWatch/actions/runs/30530850014>, 2026-07-30, branch `throwaway/build-negative-control` (deleted). Failed at step *Build package*: `ERROR Failed to parse .../pyproject.toml: Expected '=' after a key in a key/value pair (at line 17, column 6)`, exit 1. `publish` reported `skipped` and never started. Hash migrated 2026-07-31 when the digest began retaining behavior-bearing `with.name`; the job spec itself did not change |
| `publish` | CI job (`publish.yml`) | `8652a0d0cb00` | never observed red | **Deliberately not controlled, and this is a maintainer decision, not an oversight.** A deliberate failure here risks an artefact reaching the real index. The 2026-07-30 build control confirmed the ordering that protects it (`needs: build`, no `if:`, so `publish` was `skipped` when `build` failed), but that observes the *guard*, not the job. The cheap next step is a dry run against **TestPyPI**, which needs no change to the real publish path. Hash migrated 2026-07-31 when the digest began retaining behavior-bearing `with.name`; the job spec itself did not change. Ledger items 63 and 69 |
| `scripts/audit_dependency_floors.py` | repository gate | n/a (not a workflow job) | RED OBSERVED | 2026-07-30, `exit=1` on a temporary `jinja2>=2.11.3` floor: *"permits versions with: GHSA-cpwx-vrp4-4pq7, ... minimum safe floor: 3.1.6"*. Mutation reverted |
| `scripts/check_release_claims.py` | repository gate (pre-release) | n/a (not a workflow job) | RED OBSERVED | 2026-07-30, `exit=1` on both paths. Claims: *"Do not release. Correct the claims first."*, 4 violations, caught in README **and** in the freshly built sdist PKG-INFO. Figures: *"Do not release. Published figures disagree with the harness."* Mutations reverted |
| `scripts/check_published_claims.py` | repository report (never a gate) | n/a (not a workflow job) | RED OBSERVED | 2026-07-30, `exit=2` with PyPI unreachable: *"This check has NOT passed. A check that cannot inspect its subject has not verified anything."* It also exited non-zero on live content on 2026-07-29 (item 2), which is not re-observable now that 0.4.1 is correct |
| `scripts/figure_rules.py` | repository gate (also a CI step of `test`) | n/a (not a workflow job) | RED OBSERVED | 2026-07-30, `exit=1` on a relabelled README figure: *"[figure-mislabelled] README.md:235: 9/12 is published as false-positive-rate but the harness prints it as recall-overall."* Mutation reverted |
| `scripts/readiness_consistency.py` | repository gate | n/a (not a workflow job) | RED OBSERVED | 2026-07-31, `exit=1` fail-before: condition 2 was non-passing while the verdict said conditions 1–4 pass; stale corpus/current detector prose and closed rows under Open were also observed. Four focused mutation controls are recorded in the readiness session log. |
| `analysis/verify_capture.py` | repository gate | n/a (not a workflow job) | RED OBSERVED | 2026-07-30, `exit=2` MISSING on an absent path and `exit=3` CORRUPT on a wrong file; with both present, 3 outranked 2 as specified. Demonstrated via `--copy`, so no recorded copy was touched |<!-- gate-table:end -->

**The `lowest-direct` red is confounded, and counting it as clean evidence would
overstate it.** The floor chosen for that control (`pyyaml>=6.0`) tripped two
independent guards, so "all four legs red" is not four legs of matrix-specific
evidence. The 3.10 and 3.11 legs went red on
`tests/test_dependency_floors.py::test_load_bearing_floors_are_at_or_above_their_known_good_minimum`,
which any leg would have caught. Only **3.12 and 3.13** failed on the thing the
matrix uniquely exists to catch: `Failed to build pyyaml==6.0` /
`AttributeError: 'build_ext' object has no attribute 'cython_sources'`. Isolating
it fully needs a floor that is unbuildable but absent from the known-good-minimum
table.

**The `security` control was confounded too, and differently.** `jinja2==2.11.3`
is also rejected by `scripts/audit_dependency_floors.py`, so the stimulus was not
pip-audit-specific. Step ordering isolated it: pip-audit runs first, so the floor
step reported `skipped` and the red is attributable to the pip-audit step alone.
That is weaker than an unconfounded stimulus and stronger than the
`lowest-direct` case, where both guards actually ran.

<!-- gate-table:not-a-gate -->
Tracked scripts that are deliberately **not** gates. Listed rather than omitted, so
a new gate cannot arrive unclassified. Same shape as `NO_FLOOR_EXPECTED` in the
floor auditor: opting out is a written declaration with a reason.

- `scripts/claim_rules.py`: a rules module with no CLI entry point. It defines the
  rules; the three callers in the table above are what enforce them.
- `scripts/refresh_confusables.py`: a data-refresh utility, run by hand, with no
  pass/fail verdict over the repository.
- `analysis/measure_efficacy.py`: a measurement harness. Its stdout is the
  reference set `figure_rules.py` checks against, which makes it the subject of a
  gate rather than one.
- `analysis/measure_base_rate.py`: a measurement harness, as above.
- `analysis/build_realpage_corpus.py`: a corpus builder, run once to produce inputs.
- `analysis/make_baseline.py`: a baseline builder. It verifies its own output
  (201/201 content hashes) but issues no verdict over the repository.
- `analysis/run_delta_pass.py`: a measurement harness. Its date guard was observed
  refusing on 2026-07-30 (`exit=3`, *"REFUSING: today is 2026-07-30; this pass is
  scheduled for 2026-08-05 or later"*), but a scheduling guard is not a gate on the
  repository's correctness.
<!-- gate-table:not-a-gate-end -->

### The facts in this file are claims too

**Asked and answered on 2026-07-30: is there a cheap check for staleness in this
file, as `figure_rules.py` is for published proportions? Yes, and it is now in
place.** The question arose because the version sentence above was false in both
halves, and the same sentence had already gone stale once (ledger item 12).

It is cheap because it is the *same* fix as the figure check: stop keeping a second
copy of a fact, and derive the claim from the artefact it describes. It splits in
two along the line this repository already draws between a gate and a report.

| Claim | Derived from | Where checked | Blocking |
|---|---|---|---|
| "this repository declares X in `pyproject.toml`" | `pyproject.toml` | `tests/test_claude_md_currency.py` | yes, offline, in CI |
| "N Python modules under `skillwatch/`" | `git ls-files` | `tests/test_claude_md_currency.py` | yes |
| "N tracked scripts under `scripts/`", and each named | `git ls-files` | `tests/test_claude_md_currency.py` | yes |
| "N tracked modules under `analysis/`", and each named | `git ls-files` | `tests/test_claude_md_currency.py` | yes |
| "PyPI serves X (date)" | the live PyPI index | `scripts/check_published_claims.py` | **no, and must never be** |

The last row cannot be blocking, for the reason already recorded above: only a
release can make it true, so gating on it would deadlock exactly as gating on the
published-claims report would. It is a finding to act on.

Because those claims are now parsed, **their wording is load-bearing**. Write them
in the forms the checks expect (`this repository declares X.Y.Z in
\`pyproject.toml\``, `PyPI serves X.Y.Z (YYYY-MM-DD)`, `N tracked scripts under
\`scripts/\``) or the check fails closed rather than passing vacuously.

**What this does not cover, stated rather than implied.** Only mechanically
derivable facts. The prose claims here — that Pages is live, the AST05 positioning,
the base-rate reasoning, the boundary statements — are not checked by anything and
can go stale silently. That is a smaller version of the same hole and it stays open.

## Conventions

- British English in all user-facing text
- Every code change ships with a test
- Do not overstate detection capability in any documentation change
- `severity_rank()` lives in `detector.py` and is the single source of truth for severity ordering
- `FLAG_EXPLANATIONS` / `explain()` in `detector.py` are the single source of truth for user-facing alert wording; a test asserts every emitted flag code has a plain-language entry. The reader-facing guide is `docs/UNDERSTANDING-ALERTS.md`.

=== PR 34 ===
github.com
  ✓ Logged in to github.com account kuzivaai (/home/mkuziva/.config/gh/hosts.yml)
  - Active account: true
  - Git operations protocol: https
  - Token: gho_************************************
  - Token scopes: 'gist', 'read:org', 'repo', 'workflow'
{"additions":4525,"baseRefName":"main","body":"Closes ledger items **55, 56, 57, 58, 16, 22**. Corrects items **47** and **53**.\n\n## 1. The archive class (item 55)\n\nItem 51 moved the irreplaceable 2026-07-29 capture out of an ephemeral scratchpad. That fixed the *instance*. The **class** stayed open: one directory, one filesystem, and nothing anywhere that would fail if the file vanished or silently rotted. `--source capture` loaded whichever path existed first **without checking a single hash**.\n\n- Two further copies outside the WSL2 VHDX (`/mnt/d`, `/mnt/c`). All three `sha256 861027d1…7dfe`, 59968045 bytes, matching `CAPTURE-INTEGRITY.json`.\n- **Independence is PARTIAL and documented as partial.** Windows reports exactly one physical disk — Disk 0, `RS1D0TSSD510`, NVMe. C: is partition 3 and D: is partition 5 of that same disk, and the ext4 filesystem is a VHDX file on C:. The copies close the largest real class for a WSL user (`wsl --unregister`, distro reset, ext4/VHDX corruption, a C: reimage). **Residual and unmitigated: Disk 0 failure and loss of the machine** — closing those needs an off-machine destination, outside this project's local-only boundary, so it is flagged for the maintainer and deliberately not done.\n- `analysis/verify_capture.py`: **0** verified / **2 MISSING** / **3 CORRUPT** / **4** manifest unusable. Distinct messages. **3 outranks 2**, because reporting only the absence would invite restoring the missing copy *from* the corrupt one.\n- Per-page hashes localise damage — a tampered `https://bags.fm` was reported as 1 of 201.\n- `CAPTURE-INTEGRITY.json` gains `copies`/`holders` and is the single registry; `run_delta_pass.py` derives its search path from it rather than keeping a second list free to drift.\n- Both consumers verify **before** loading.\n\nStated limit, in the module: it verifies the copies the manifest *records*, so an unrecorded copy is invisible to it, and it cannot check the manifest against itself.\n\n## 2. `pip-audit --strict` settled after five sessions open (item 22)\n\nThe untested claim that `--strict` can *never* pass is **false**. Measured, 47 packages, pip-audit 2.10.1:\n\n| Shape | Version | Result |\n|---|---|---|\n| env scan | 0.4.1 (published) | exit 0 |\n| env scan | 0.9.9 (unreleased) | **exit 1** — `Dependency not found on PyPI and could not be audited` |\n| `--strict -r <resolved>` | either | exit 0 |\n\nThe original reasoning was right about the mechanism and wrong about today: the env-scan shape passes only because `main`'s version equals what PyPI serves, and would fail at the next pre-release bump. Adopted the `-r` shape; **`--skip-editable` removed**. pip-audit installed in a separate venv so the freeze is SkillWatch's closure, not the auditor's.\n\n**Limit recorded, not hidden:** on the `-r` shape an unresolvable entry already fails *without* `--strict` (exit 1 either way) and no case was found where `--strict` changed the outcome. Kept as explicit intent, flagged as a rule not seen to fire.\n\n## 3. lowest-direct matrix observed RED (item 16)\n\nRun **<https://github.com/kuzivaai/SkillWatch/actions/runs/30500657407>** on a throwaway branch, since deleted. `lowest-direct (3.12)` and `(3.13)` failed with `Failed to build pyyaml==6.0` / `AttributeError: 'build_ext' object has no attribute 'cython_sources'`. **`security` passed** — the floor audit does not catch it, which is exactly the gap the matrix exists to close.\n\n**Confound stated:** the chosen floor trips two independent guards, so the clean matrix-specific evidence is 3.12/3.13, not all four legs.\n\n## 4. Two findings fixed in passing — same out-of-scope shape (item 58)\n\n- The CI mypy scope was a hand-written list of five files. A newly tracked module would be silently unchecked while the gate reported green. Now `$(git ls-files 'analysis/*.py')`. **Fifth outing** of this shape after items 17, 35, 36, 42/45.\n- `analysis/*` in `.gitignore` silently excluded `verify_capture.py` — mypy reported 24 files, not 25. An untracked verifier is no verifier.\n\n## Verification\n\n`595 passed` (564 → 595, **+31**: `test_verify_capture.py` 20, `test_ci_scope.py` 11). ruff, mypy (25 files), floor audit, release gate, published-claims report, figure check and the new capture verifier all exit 0.\n\n**Nothing fetched. Detection unchanged. The delta pass remains scheduled for 2026-08-05 and was not run.**\n\n🤖 Generated with [Claude Code](https://claude.com/claude-code)","changedFiles":17,"commits":[{"authoredDate":"2026-07-29T23:46:34Z","authors":[{"email":"mkuziv@gmail.com","id":"","login":"","name":"Kuziva Muzondo"},{"email":"noreply@anthropic.com","id":"MDQ6VXNlcjgxODQ3","login":"claude","name":"Claude Opus 5 (1M context)"}],"committedDate":"2026-07-29T23:46:34Z","messageBody":"The irreplaceable 2026-07-29 real-page capture sat in one directory on one disk\nwith nothing detecting its absence. A second copy alone does not close that: a\ncopy nobody checks is indistinguishable from no copy on the day it silently rots.\n\nArchive durability\n- Two further copies, outside the WSL2 VHDX: /mnt/d and /mnt/c. All three\n  sha256 861027d158b67c517074e3a17348777e4405a644c13a33c7fbc85f25aa417dfe,\n  59968045 bytes, matching CAPTURE-INTEGRITY.json.\n- Independence is PARTIAL and CLAUDE.md says so. Windows reports exactly ONE\n  physical disk: Disk 0, RS1D0TSSD510, NVMe. C: is partition 3 and D: is\n  partition 5 of that same disk, and the ext4 filesystem is a VHDX file on C:.\n  What the copies close is the largest real class for a WSL user - anything\n  destroying the ext4 filesystem or the VHDX, and a C: reimage. Residual and\n  unmitigated: Disk 0 failure and loss of the machine. Closing those needs an\n  off-machine destination, which is outside this project's local-only boundary,\n  so it is flagged for the user and NOT done.\n- analysis/verify_capture.py: exit 0 verified / 2 MISSING / 3 CORRUPT /\n  4 manifest unusable. 3 outranks 2, because reporting only the absence would\n  invite restoring the missing copy FROM the corrupt one.\n- CAPTURE-INTEGRITY.json gains `copies` and `holders` and is now the single\n  registry; run_delta_pass derives its search path from it rather than keeping a\n  second list free to drift.\n- Both consumers verify before loading. --source capture refuses a corrupt copy;\n  an explicit path is verified if recorded, else announced UNVERIFIED. A\n  verifier nobody runs is the defect one level up from the one it fixes.\n\npip-audit --strict, settled after five sessions open (item 22)\nThe untested claim that --strict can NEVER pass is FALSE. Measured, 47 packages,\npip-audit 2.10.1:\n\n  env scan,  version 0.4.1 (published)    --strict          -> exit 0\n  env scan,  version 0.9.9 (unreleased)   --strict          -> exit 1\n      \"skillwatch: Dependency not found on PyPI and could not be audited\"\n  -r resolved set, either version         --strict          -> exit 0\n\nSo the original reasoning was right about the mechanism and wrong about today:\nthe env-scan shape passes only because main's version equals what PyPI serves,\nand would fail at the next pre-release bump. The -r shape is robust because the\nproject is excluded outright. Adopted; --skip-editable removed. pip-audit is\ninstalled in a separate venv so the freeze is SkillWatch's closure and not the\nauditor's. Stated limit: on the -r shape an unresolvable entry already fails\nWITHOUT --strict (exit 1 either way) and no case was found where --strict\nchanged the outcome - it is kept as explicit intent, not as an observed catch.\n\nTwo findings fixed in passing, both the same out-of-scope shape\n- The CI mypy scope was a hand-written list of five analysis/ files. A newly\n  tracked module would be silently unchecked while the gate reported green. Now\n  derived from `git ls-files 'analysis/*.py'`; tests/test_ci_scope.py asserts it\n  stays derived. This is the fifth outing of \"a check that reports green because\n  what it should examine is out of its scope\".\n- analysis/* in .gitignore silently excluded verify_capture.py, so mypy checked\n  24 files, not 25. An untracked verifier is no verifier - it would exist on one\n  machine, the same single-point-of-failure shape as the capture it protects.\n\nTests: +26 (test_verify_capture.py 20, test_ci_scope.py 6), 564 -> 590.\nThe CI guards were proven non-vacuous by running them against HEAD's ci.yml:\n6 failed there, 11 pass here. test_pip_audit_runs_strict initially passed\nagainst the old file because its COMMENT said \"--strict\" - tightened to read\nexecutable run: lines only.\n\nNothing fetched. Detection unchanged. The delta pass remains scheduled for\n2026-08-05 and was not run.\n\nCo-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>","messageHeadline":"Make the capture's absence detectable; adopt pip-audit --strict","oid":"852fd723e6c5e5fcfde92e0304cc469482610316"},{"authoredDate":"2026-07-29T23:55:48Z","authors":[{"email":"mkuziv@gmail.com","id":"","login":"","name":"Kuziva Muzondo"},{"email":"noreply@anthropic.com","id":"MDQ6VXNlcjgxODQ3","login":"claude","name":"Claude Opus 5 (1M context)"}],"committedDate":"2026-07-29T23:55:48Z","messageBody":"Closed\n- 55 archive single point of failure with nothing detecting its absence.\n- 56 an empty locating result was treated as proof of absence. Promoted from an\n  aside inside item 51 to a rule: an empty locating result is a FAILED command.\n  The four-level scratchpad path is now literal in CLAUDE.md and asserted by a\n  test that fails if any /tmp/claude- glob is shallower than four levels.\n- 57 three records disagreed about the global floor in figure_rules.py; two were\n  wrong. Settled against the code and git history.\n- 58 the CI mypy scope was a hand-maintained list. Fifth outing of \"a check that\n  reports green because what it should examine is out of its scope\".\n- 16 lowest-direct matrix OBSERVED RED, run 30500657407. Confound stated: the\n  chosen floor trips two guards, so the clean matrix-specific evidence is the\n  3.12/3.13 build failure, not all four legs.\n- 22 pip-audit --strict settled. The untested \"can never pass\" claim is false.\n\nCorrected\n- item 47: \"with the floor as their sum, 28\" removed. No sum floor exists; the\n  sum was only ever printed, never compared.\n- item 53: era-stamped. \"Enforcement was already per-command\" holds from fa49fc5\n  onwards, not at 8d35321 where `if len(allowed.pairs) < 20` did gate.\n- CLAUDE.md carries the three-commit history rather than a single claim.\n\nfigure_rules.py itself was already correct and was not changed.\n\nThe scheduled delta pass is unchanged: 2026-08-05 or later,\n`python3 analysis/run_delta_pass.py`. Not run.\n\nCo-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>","messageHeadline":"docs(ledger): close items 16, 22, 55-58; correct the global-floor record","oid":"17ab8f19c240dac62f8dc11ee2ae3eab46797c83"},{"authoredDate":"2026-07-30T08:47:53Z","authors":[{"email":"mkuziv@gmail.com","id":"","login":"","name":"Kuziva Muzondo"},{"email":"noreply@anthropic.com","id":"MDQ6VXNlcjgxODQ3","login":"claude","name":"Claude Opus 5 (1M context)"}],"committedDate":"2026-07-30T08:47:53Z","messageBody":"…on claim\n\nThree closures, one class. The class: a gate is changed and relied upon without\nanyone ever observing it refuse anything. Sixth outing (17, 35, 36, 42/45, 16,\n59), and the sixth was created by the fix for the fifth: the commit that closed\nlowest-direct by running a negative control rewrote the security job and left it\nunproven in the same breath.\n\n1. security OBSERVED RED (item 59)\n   https://github.com/kuzivaai/SkillWatch/actions/runs/30526422428\n   PR #38 \"DO NOT MERGE\", closed unmerged, branch deleted local and remote.\n   Failed at \"Audit resolved dependencies (--strict, no skip flags)\":\n   jinja2 2.11.3, PYSEC-2026-1471/1473/1474/1475, exit 1. Floor step skipped.\n   All eight test and lowest-direct legs green, matching the prediction made\n   before the run. Route A chosen over B because the audited set is generated at\n   CI time into a gitignored path, so only a pyproject.toml pin exercises the\n   generation path that was actually rewritten. Confounded (the floor auditor\n   also rejects the pin); step ordering rescues the attribution. Reasoning in\n   docs/DEPENDENCY-FLOORS.md. git diff main -- pyproject.toml is empty.\n\n2. Every gate audited and the answer recorded (item 62)\n   CLAUDE.md gains a gate table plus the rule: a gate that is added or\n   materially changed requires a negative control before it is relied on.\n   History exhaustive, not sampled: all 81 ci.yml runs and all 4 publish.yml\n   runs. 8 of 10 gates RED OBSERVED; build and publish never observed red and\n   logged as item 63. The five repository-side gates were demonstrated red fresh\n   rather than inherited from the ledger, every mutation reverted.\n   tests/test_gate_table.py (13) parses jobs as YAML from EVERY tracked\n   workflow, not ci.yml alone, because a table blind to publish.yml would\n   reproduce the out-of-scope defect being closed; and every tracked script must\n   be a row or an explicit not-a-gate declaration with a reason.\n\n3. CLAUDE.md's false version claim corrected, and the class checked (item 61)\n   It read \"PyPI serves 0.3.0 (2026-07-11); main is 0.4.0\". Both halves false:\n   PyPI has served 0.4.1 since 2026-07-29, main is 0.4.1. Second stale claim\n   found in the same file: \"Two tracked scripts under scripts/\" where there are\n   six. The staleness question is asked and answered in the file. Offline and\n   blocking: tests/test_claude_md_currency.py (7) checks the declared version\n   against pyproject.toml and three counts against git ls-files. Networked and\n   deliberately NOT blocking: check_published_claims.py compares the published\n   claim against the live index, because only a release can make it true.\n\nAlso logged: item 60, pip-audit --strict is a rule not observed firing, kept for\nstated intent and placed in the debt column rather than counted as a widened\ngate until a case is found where it changes an outcome.\n\nTests 595 -> 615 (+20), both new files: test_gate_table.py +13,\ntest_claude_md_currency.py +7. No existing file's count changed.\nCoverage 95.70%. ruff, mypy, floors, figures, release gate, published report and\ncapture verifier all exit 0. Detection unchanged. Delta pass still refuses\n(exit 3, scheduled 2026-08-05).\n\nCo-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>","messageHeadline":"Prove the security gate can fail; audit every gate; correct the versi…","oid":"fe66903bd628f0da244e69a2a795fd89b14341c4"},{"authoredDate":"2026-07-30T09:27:07Z","authors":[{"email":"mkuziv@gmail.com","id":"","login":"","name":"Kuziva Muzondo"},{"email":"noreply@anthropic.com","id":"MDQ6VXNlcjgxODQ3","login":"claude","name":"Claude Opus 5 (1M context)"}],"committedDate":"2026-07-30T09:27:07Z","messageBody":"The table recorded that a gate HAS a row and a status. That validates identity,\nnot behaviour: a job rewritten under the same name keeps its old verdict. Not\nhypothetical, it is what happened. `security` was rewritten on 2026-07-30 and\nsilently carried forward a never-observed-red status under an unchanged name.\nAn accounting that certifies something it has not examined is the same shape as\nevery other defect in this repository's ledger under that heading.\n\nEach job's row now carries a digest of what the job executes. When a job's\ndigest stops matching, the suite fails saying the gate changed materially and\nneeds a fresh negative control, and a second test enforces that its status\ncannot say anything but `unknown` while drifted. Do not update a drifted hash\nalone: that records the change happened and asserts nothing about whether the\ngate still refuses anything.\n\nWHY NOT \"run: lines only\", which is what a literal reading would give. The\npublish job has ZERO run: lines, so a run-lines-only digest for it is\nsha256(\"[]\"), a constant. It would be blind to `needs: build` (the ordering that\nkeeps a failed build from reaching PyPI, and the whole safety argument for the\nbuild control), to `environment: pypi`, to `permissions: id-token: write`, and\nto the pinned SHA of pypa/gh-action-pypi-publish. That is the defect being\nclosed, not a fix for it. The digest is over the parsed job spec instead:\nparsing as YAML drops comments, blank lines and trailing whitespace inherently,\nwhich is stronger than stripping them by regex, and it keeps step order\nsignificant, which is correct because step ordering is what isolated the\npip-audit step from the floor step in the security control.\n\nThe digest ALSO covers the workflow's `on:` block, and that was found by doing\nrather than by reasoning. An earlier draft hashed the job alone; the build\ncontrol then added workflow_dispatch: to publish.yml and the hash did not move,\nbecause `on:` sits outside `jobs:`. A gate that stops running is not a gate:\nchanging ci.yml's on: from [push, pull_request] to [push] would ungate every\npull request with no job line changed. Trap recorded in the module: under YAML\n1.1 the bare key `on` parses to boolean True, not \"on\", so a digest reading\ndata[\"on\"] would silently omit the trigger from every hash.\n\nRows are now read by column name, not position. A column was inserted; a checker\nthat keeps passing while reading the wrong cell is the shape this file prevents.\n\nStated limits, in the module and beside the table:\n  - it checks a status is RECORDED, not that it is TRUE;\n  - repository-side gate scripts are NOT hashed and can be rewritten under the\n    same name, exactly as security was. A source-text hash fires on comments,\n    which is the rejected shape; an AST digest with docstrings stripped is the\n    right instrument and was not built. Logged in the ledger;\n  - a job calling a script whose contents changed keeps its hash.\n\nAlso fixed: a mid-bullet HTML comment added on 2026-07-30 split the version list\nitem in two. Moved to the end of the bullet.\n\nTests 615 -> 623 (+8), all in tests/test_gate_table.py (13 -> 21).\n\nCo-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>","messageHeadline":"Make the gate table see behaviour, not just names","oid":"fd4f4a92709698ee67386ca1e48acc41863b4750"},{"authoredDate":"2026-07-30T09:51:27Z","authors":[{"email":"mkuziv@gmail.com","id":"","login":"","name":"Kuziva Muzondo"},{"email":"noreply@anthropic.com","id":"MDQ6VXNlcjgxODQ3","login":"claude","name":"Claude Opus 5 (1M context)"}],"committedDate":"2026-07-30T09:51:27Z","messageBody":"STEP 3: build OBSERVED RED (item 65, split from 63)\n  https://github.com/kuzivaai/SkillWatch/actions/runs/30530850014\n  Branch throwaway/build-negative-control, deleted. Stimulus: three lines of\n  invalid TOML in pyproject.toml.\n    build    failure at \"Build package\":\n             ERROR Failed to parse .../pyproject.toml: Expected '=' after a key\n             in a key/value pair (at line 17, column 6). exit 1.\n             \"Install build tools\" succeeded; upload-artifact skipped.\n    publish  SKIPPED, never started, no steps listed at all.\n  Nothing published: PyPI still serves exactly four releases, newest 0.4.1 from\n  2026-07-29. Every element matched the prediction made before the run.\n\n  publish.yml triggers only on release publication, so the job cannot be\n  exercised from a branch. Two temporary triggers were added and removed with\n  the branch. A PREDICTION THAT WAS WRONG, recorded rather than dropped:\n  `gh workflow run --ref` was expected to be refused from a non-default branch\n  and a push: trigger was added as a fallback. It exited 0. The push: trigger\n  was unnecessary apparatus; a later session needs only workflow_dispatch.\n  Testability caveat logged as item 66: a workflow reachable only via release\n  cannot be controlled without editing it, so the control changes the thing\n  being controlled.\n\n  Teardown: branch gone locally and remotely, no PR was ever opened, git diff\n  main is 0 bytes on pyproject.toml AND on publish.yml, on: is back to release\n  only. publish was never deliberately failed.\n\nSTEP 4: --strict DEMONSTRATED, item 60 closed, flag kept\n  Carried five sessions as undemonstrated debt. Found by reading pip-audit's\n  source rather than guessing at inputs: --strict makes any SkippedDependency\n  fatal (_cli.py:557), and the skip reachable on every source is\n  _service/pypi.py:85, a package that resolves but 404s on PyPI.\n    pip-audit --desc -r <file>           -> exit 0, prints a Skip Reason table\n                                            and PASSES\n    pip-audit --strict --desc -r <file>  -> exit 1\n  Without the flag this gate reports green over a dependency it never examined:\n  the same fail-open shape as items 17 and 35. Reachable in the real shape\n  because pip freeze names whatever is installed, including packages from a\n  private index, a VCS URL, or a release later removed from PyPI.\n\n  Six non-distinguishing cases tabulated in docs/DEPENDENCY-FLOORS.md so they\n  are not retried, plus the finding that the editable/URL skips in\n  requirement.py:312-346 are unreachable in CI's shape because that path runs\n  only under --no-deps, which this project does not pass.\n\n  The false claim in ci.yml's comment is corrected in place. That 19-line\n  comment rewrite left the security job hash at 576042ed1d31 and the suite\n  green, which corroborates the Step 2 normalisation on an unstaged edit.\n\n  Stated limit: the control was local against pip-audit 2.10.1; CI installs\n  whatever it resolves at run time.\n\nLedger: 60 closed, 63 split to publish-only, 64/65/67 closed, 66 opened. Two\nstanding decisions added.\n\nNo test count change this commit (all 8 new tests landed in fd4f4a9).\n615 -> 623 across the session, all in tests/test_gate_table.py.\n\nCo-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>","messageHeadline":"Observe the build gate red; settle --strict as load-bearing","oid":"4b366c501b5cbfc4c856eddaa3d1d48a469fff7b"},{"authoredDate":"2026-07-31T14:18:23Z","authors":[{"email":"mkuziva@gmail.com","id":"U_kgDOC3YLqA","login":"kuzivaai","name":"Kuziva Muzondo"}],"committedDate":"2026-07-31T14:18:23Z","messageBody":"Fail malformed capture copy registries through the documented unusable-manifest path, and make workflow hashing retain behavior-bearing nested name inputs. Record both independently reproduced findings and the digest migration in the continuity ledger.","messageHeadline":"Close adversarial assurance findings","oid":"f6b75c8f288c9446fa8f9050e9dbae326a19bbd9"},{"authoredDate":"2026-07-31T14:30:11Z","authors":[{"email":"mkuziva@gmail.com","id":"U_kgDOC3YLqA","login":"kuzivaai","name":"Kuziva Muzondo"}],"committedDate":"2026-07-31T14:30:11Z","messageBody":"Record the five reconciled commits, independent assurance results, final local verification, and remaining continuity risks in the repository-native Codex onboarding file.","messageHeadline":"Add tracked Codex transition handover","oid":"39cc419bc34445455279b298fc4dba88d0ebc3f3"},{"authoredDate":"2026-07-31T16:34:29Z","authors":[{"email":"mkuziva@gmail.com","id":"U_kgDOC3YLqA","login":"kuzivaai","name":"Kuziva Muzondo"}],"committedDate":"2026-07-31T16:34:29Z","messageBody":"Re-include dated analysis session logs and commit the initial environment record so a cutoff cannot strand the only evidence in an ignored local file.","messageHeadline":"Make session evidence durable","oid":"ed3ee71c2dd8d2e0454f24205788cd5a104e0fe4"},{"authoredDate":"2026-07-31T16:47:10Z","authors":[{"email":"mkuziva@gmail.com","id":"U_kgDOC3YLqA","login":"kuzivaai","name":"Kuziva Muzondo"}],"committedDate":"2026-07-31T16:47:10Z","messageBody":"Persist local commit inventory, detection-diff proof, per-file test counts, PR #34 state, and unchanged remote refs before running gates.","messageHeadline":"Record repository and PR baseline","oid":"fa748d49464427d47e7b612869eb08663389e8e5"},{"authoredDate":"2026-07-31T19:07:47Z","authors":[{"email":"mkuziva@gmail.com","id":"U_kgDOC3YLqA","login":"kuzivaai","name":"Kuziva Muzondo"}],"committedDate":"2026-07-31T19:07:47Z","messageBody":"Cross-link the strict-audit supersession, reject the obsolete conclusion in item 22, and prove future session evidence paths remain trackable. Both controls fail against the prior state and pass now.","messageHeadline":"Make continuity claims self-consistent","oid":"86f77ff2463ec826d9aeb089cf4945a82f123d0f"},{"authoredDate":"2026-07-31T19:20:51Z","authors":[{"email":"mkuziva@gmail.com","id":"U_kgDOC3YLqA","login":"kuzivaai","name":"Kuziva Muzondo"}],"committedDate":"2026-07-31T19:20:51Z","messageBody":"Prove existing session logs are tracked, encode ledger supersession structurally, and preserve the independent review and fail-before evidence.","messageHeadline":"Close adversarial continuity gaps","oid":"55c067d27b84dccefc8d9114af95c5a6d4c793ab"},{"authoredDate":"2026-07-31T20:04:24Z","authors":[{"email":"mkuziva@gmail.com","id":"U_kgDOC3YLqA","login":"kuzivaai","name":"Kuziva Muzondo"}],"committedDate":"2026-07-31T20:04:24Z","messageBody":"Record final gates, adversarial closure, render inspection, full ledger, and the next dated action for a reviewer without session access.","messageHeadline":"Seal push-readiness handover","oid":"de2a998498293ad17f6b1990e19dc8868c614293"}],"deletions":1090,"headRefOid":"de2a998498293ad17f6b1990e19dc8868c614293","isDraft":false,"mergeStateStatus":"CLEAN","mergeable":"MERGEABLE","number":34,"state":"OPEN","title":"Close the archive single-point-of-failure class; settle pip-audit --strict","url":"https://github.com/kuzivaai/SkillWatch/pull/34"}
lowest-direct (3.10)	pass	26s	https://github.com/kuzivaai/SkillWatch/actions/runs/30665202423/job/91270474866
lowest-direct (3.11)	pass	26s	https://github.com/kuzivaai/SkillWatch/actions/runs/30665202423/job/91270474920
lowest-direct (3.12)	pass	28s	https://github.com/kuzivaai/SkillWatch/actions/runs/30665202423/job/91270474913
lowest-direct (3.13)	pass	26s	https://github.com/kuzivaai/SkillWatch/actions/runs/30665202423/job/91270474929
security	pass	41s	https://github.com/kuzivaai/SkillWatch/actions/runs/30665202423/job/91270474868
test (3.10)	pass	1m14s	https://github.com/kuzivaai/SkillWatch/actions/runs/30665202423/job/91270474905
test (3.11)	pass	40s	https://github.com/kuzivaai/SkillWatch/actions/runs/30665202423/job/91270474896
test (3.12)	pass	41s	https://github.com/kuzivaai/SkillWatch/actions/runs/30665202423/job/91270475078
test (3.13)	pass	40s	https://github.com/kuzivaai/SkillWatch/actions/runs/30665202423/job/91270474916

=== PUBLIC MAIN README ===
86:## Who this is for
116:## Quick start
139:5. **Run 13 pattern checks** on the changed content to flag anything suspicious. Before checking, the tool decodes common obfuscation tricks (HTML comments containing hidden text, reversed text, ROT13 encoding) so that disguised payloads are checked in their readable form. See [Measured detection rates](#measured-detection-rates) for what it catches and what it misses.
158:| Hidden content | Info | New elements concealed from a human but left in the ingested text — inline **or** same-document `<style>` block, case-insensitively: `display:none`, `visibility:hidden|collapse`, `opacity:0`, `font-size:0`, large negative `left`/`top` on a positioned element, zero `height`/`width` with clipped overflow, and the HTML `hidden` attribute. See [what this check does not catch](#what-hidden_content-does-not-catch) |
170:| `position:absolute;left:-9999px` | yes |
172:| HTML `hidden` attribute | yes |
196:### Measured detection rates
267:| HTML `hidden` attribute | 111/201 (55.2%) | **no — removed 0.4.1** |
314:The two techniques removed are the HTML `hidden` attribute and off-screen

=== LOCAL README ===
86:## Who this is for
116:## Quick start
139:5. **Run 13 pattern checks** on the changed content to flag anything suspicious. Before checking, the tool decodes common obfuscation tricks (HTML comments containing hidden text, reversed text, ROT13 encoding) so that disguised payloads are checked in their readable form. See [Measured detection rates](#measured-detection-rates) for what it catches and what it misses.
158:| Hidden content | Info | New elements concealed from a human but left in the ingested text — inline **or** same-document `<style>` block, case-insensitively: `display:none`, `visibility:hidden|collapse`, `opacity:0`, `font-size:0`, large negative `left`/`top` on a positioned element, zero `height`/`width` with clipped overflow, and the HTML `hidden` attribute. See [what this check does not catch](#what-hidden_content-does-not-catch) |
170:| `position:absolute;left:-9999px` | **no — deliberate accessibility boundary** |
172:| HTML `hidden` attribute | **no — deliberate base-rate decision** |
196:### Measured detection rates
267:| HTML `hidden` attribute | 111/201 (55.2%) | **no — removed 0.4.1** |
314:The two techniques removed are the HTML `hidden` attribute and off-screen

=== BASELINE CONSISTENCY ===
Readiness status, generated scoreboard, harness metrics, and ledger sections agree.
readiness_exit=0
.............F.......................................................... [ 84%]
.............                                                            [100%]
=================================== FAILURES ===================================
____________________ test_existing_session_logs_are_tracked ____________________

    def test_existing_session_logs_are_tracked() -> None:
        """Every existing permanent evidence log must survive a fresh clone."""
        logs = sorted((REPO / "analysis").glob("session-log-*.md"))
        assert logs, "no permanent session evidence logs exist"
        relative_logs = [str(path.relative_to(REPO)) for path in logs]
        result = subprocess.run(
            ["git", "ls-files", "--error-unmatch", *relative_logs],
            cwd=REPO,
            check=False,
            capture_output=True,
            text=True,
        )
>       assert result.returncode == 0, (
            "existing session logs are not tracked and will disappear on a fresh clone: "
            f"{result.stderr.strip()}"
        )
E       AssertionError: existing session logs are not tracked and will disappear on a fresh clone: error: pathspec 'analysis/session-log-2026-08-01-distribution.md' did not match any file(s) known to git
E         Did you forget to 'git add'?
E       assert 1 == 0
E        +  where 1 = CompletedProcess(args=['git', 'ls-files', '--error-unmatch', 'analysis/session-log-2026-07-31-readiness.md', 'analysis...alysis/session-log-2026-08-01-distribution.md' did not match any file(s) known to git\nDid you forget to 'git add'?\n").returncode

tests/test_continuity.py:47: AssertionError
=========================== short test summary info ============================
FAILED tests/test_continuity.py::test_existing_session_logs_are_tracked - Ass...
1 failed, 84 passed in 1.15s
targeted_exit=1
........................................................................ [ 11%]
..................................................F..................... [ 22%]
........................................................................ [ 33%]
........................................................................ [ 44%]
........................................................................ [ 55%]
........................................................................ [ 66%]
........................................................................ [ 78%]
........................................................................ [ 89%]
.....................................................................    [100%]
=================================== FAILURES ===================================
____________________ test_existing_session_logs_are_tracked ____________________

    def test_existing_session_logs_are_tracked() -> None:
        """Every existing permanent evidence log must survive a fresh clone."""
        logs = sorted((REPO / "analysis").glob("session-log-*.md"))
        assert logs, "no permanent session evidence logs exist"
        relative_logs = [str(path.relative_to(REPO)) for path in logs]
        result = subprocess.run(
            ["git", "ls-files", "--error-unmatch", *relative_logs],
            cwd=REPO,
            check=False,
            capture_output=True,
            text=True,
        )
>       assert result.returncode == 0, (
            "existing session logs are not tracked and will disappear on a fresh clone: "
            f"{result.stderr.strip()}"
        )
E       AssertionError: existing session logs are not tracked and will disappear on a fresh clone: error: pathspec 'analysis/session-log-2026-08-01-distribution.md' did not match any file(s) known to git
E         Did you forget to 'git add'?
E       assert 1 == 0
E        +  where 1 = CompletedProcess(args=['git', 'ls-files', '--error-unmatch', 'analysis/session-log-2026-07-31-readiness.md', 'analysis...alysis/session-log-2026-08-01-distribution.md' did not match any file(s) known to git\nDid you forget to 'git add'?\n").returncode

tests/test_continuity.py:47: AssertionError
================================ tests coverage ================================
_______________ coverage: platform linux, python 3.12.3-final-0 ________________

Name                      Stmts   Miss  Cover   Missing
-------------------------------------------------------
skillwatch/__init__.py        1      0   100%
skillwatch/anchoring.py     101     12    88%   58-59, 109-110, 144, 155-156, 189-190, 197-198, 200
skillwatch/cli.py           491     30    94%   271-272, 307-308, 327, 335-336, 340, 360, 381, 385, 405, 422, 446, 556-558, 573-575, 579, 581, 718-721, 752-754, 781-782, 811
skillwatch/cloak.py          49      0   100%
skillwatch/detector.py      313      5    98%   266, 320, 732, 815-816
skillwatch/differ.py          8      0   100%
skillwatch/fetcher.py       117     12    90%   112, 155, 160-161, 168, 171, 185-187, 218-224
skillwatch/formatter.py     131      2    98%   23, 220
skillwatch/ledger.py         35      0   100%
skillwatch/parser.py        103      5    95%   75, 95, 123, 142, 144
skillwatch/sarif.py          17      0   100%
skillwatch/ssrf.py           81      4    95%   112, 130, 148, 190
skillwatch/store.py         180      0   100%
-------------------------------------------------------
TOTAL                      1627     70    96%
Required test coverage of 90% reached. Total coverage: 95.70%
=========================== short test summary info ============================
FAILED tests/test_continuity.py::test_existing_session_logs_are_tracked - Ass...
1 failed, 644 passed in 21.94s
full_suite_exit=1

## Independent research workstreams

Three context-isolated Codex subagents received repository context but no lead
agent conclusions. Academic evidence returned ten peer-reviewed sources with
access-depth/limitations and independently favored an integration/provenance
test. The competitor analyst inspected official surfaces for the nine required
competitors plus Skilldex and independently reached the same route. The
commercial sceptic's strongest recommendation was to stop standalone investment
unless the pilot produces repeated, decision-changing, unprompted use.

The issue-sampling workstream used the fixed 2025-08-01..2026-08-01 window. Its
initial implicit-POST `gh api search/issues` call returned HTTP 404; retrying with
`-X GET` succeeded. Population/sample accounting:

```text
Microsoft APM: open 106 / 50 relevant; closed 900 / 50 relevant
changedetection.io: open 84 / 50; closed 242 / 50
Snyk Agent Scan: open 3 / 3; closed 30 / 30 (25 relevant)
Cisco Skill Scanner: open 10 / 10 (9 relevant); closed 35 / 35 (34 relevant)
NVIDIA SkillSpector: open 50 / 50 (49 relevant); closed 90 / newest 50
SchemaPin: open 0 / 0; closed 0 / 0 — empty corpus, not evidence of quality
```

Review-platform sampling was blocked: no account-free, chronological and
complete Distill/Visualping review sample was obtainable. Search snippets were
rejected as a sample. Exact queries, taxonomies, counts, positive/negative themes
and selection limits are preserved in
`docs/research/COMPETITOR-VOICE-2026-08-01.md`.

## Baseline interpretation

- Demonstrated: clean start HEAD `0d8cc17`; six local-only commits; PR #34 at
  upstream `de2a998`; no `skillwatch/` diff; condition 2 not demonstrated;
  condition 5 fail; organic delta pending; public main has stale detector prose.
- Contradicted: all work is remote; PR #34 represents the complete branch; public
  main describes the current detector; the prior five-source pilot review alone
  is sufficient for a distribution decision.
- Unverified: design-partner referral suitability, actual demand, integration
  preference, provenance decision value and payment. Settle through clean install
  and repeated-use observations, concrete integration requests, recorded
  before/after decisions and an actual procurement step.

The requested pointer shell treated `HANDOVER-READINESS-2026-07-31.md` as
repository-root-relative and failed. The pointer contract is relative to `docs/`;
`scripts/readiness_consistency.py` resolved it and exited 0. This is a prompt
command defect, not evidence that the tracked target is absent.
