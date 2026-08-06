# SkillWatch readiness-consistency handover — 2026-07-31

> **SUPERSEDED:** `HANDOVER-PILOT-READINESS-2026-08-01.md` is designated by
> `docs/current-handover.txt` as the current handover.
> Current readiness values remain derived from `docs/readiness-status.json`, not
> from narrative prose in this handover.

Audience: an adversarial reviewer without access to the session. The permanent
raw record is `analysis/session-log-2026-07-31-readiness.md`. This document uses
**Demonstrated**, **Unverified** and **Contradicted** with the meanings required
by the session brief.

## What the session set out to do, and what it did

The narrow objective was to make current readiness internally true,
mechanically enforceable and suitable for an honest design-partner pilot,
without changing detection or adding a product feature. It reproduced ten
readiness claims, found six contradicted current claims, introduced a structured
current status and fail-closed validator, archived historical readiness prose,
corrected public surfaces, defined a falsifiable pilot from a bounded five-source
review, passed two context-restricted adversarial reviews, and closed ledger item
73. No remote write occurred.

## Environment and access

- UTC date: 2026-07-31.
- Repository: `/home/mkuziva/skillwatch`.
- Sandbox: workspace-write; managed approval; writes allowed in the repository
  and `/tmp`; network restricted by default.
- Approved unrestricted runs were needed for GitHub reads, network-dependent
  tests, live PyPI claims, isolated package builds, localhost binding and browser
  rendering.
- The system `python3` lacked `confusable_homoglyphs`; repository commands were
  therefore run with `.venv/bin/python`. Exact settling command: `.venv/bin/python
  -m pytest --cov=skillwatch --cov-report=term-missing --cov-fail-under=90 -q`.
- A sandboxed full suite failed DNS resolution; this was not called a pass. The
  unrestricted post-review run passed.

## Repository and PR state reproduced before editing

- Branch: `feat/archive-durability-and-strict-audit`.
- Start HEAD/upstream: `de2a998498293ad17f6b1990e19dc8868c614293`.
- `origin/main`: `6c6ab215742b8d4913b9193a8df49e645f5cd060`.
- Initial local-only commits: none; remote-only commits: none; tree clean.
- `git diff --quiet origin/main..HEAD -- skillwatch/` exited 0.
- PR #34: OPEN, non-draft, MERGEABLE/CLEAN, head `de2a998`, base `main`,
  12 commits, 17 files, +4525/-1090, nine checks passing. Its title/body were
  stale and described the earliest scope plus 595 tests.

## Initial material-claim classification

Demonstrated: PR #34 was open at its reported head; the branch was fully pushed;
production code did not differ from `origin/main`; the dependency-complete
virtual environment reproduced the harness and test baseline.

Contradicted: condition 2 passed; conditions 1–4 all passed; zero users was the
only unresolved gate; SHIP-READINESS described the current corpus/detector; the
Open ledger section contained only open rows; PR #34 represented the complete
branch. The system-interpreter reproduction commands were also contradicted in
this environment because a dependency was absent.

Unverified before correction: live external user state beyond the GitHub facts
read in this session. The offline readiness gate now states only that no demand
evidence is recorded in the repository. A fresh `gh repo view` plus product-user
observation would settle current external state.

## Fail-before and root defect class

The pre-fix targeted suite produced:

```text
$ .venv/bin/python -m pytest -q tests/test_readiness_consistency.py
FFFFF
5 failed in 0.06s
```

The five failures were the contradictory verdict, non-directional bound rule,
retracted “same five” claim, stale corpus total/families and CLOSED rows under
Open. Root class: current status, historical narrative, generated measurements
and summary verdicts could disagree while every existing gate remained green.

Chosen design: `docs/readiness-status.json` is the freshness-bounded current
source. `scripts/readiness_consistency.py` validates unique IDs, controlled
bases/vocabulary, cross-field semantics, condition-specific evidence,
directional Wilson bounds, the exact generated SHIP block and ledger section
status. Other surfaces point to it rather than copying current values.

Rejected design: prose-only corrections plus searches. It would still leave
multiple hand-maintained truth copies and phrase-specific tests. Known blind
spot: the validator proves repository evidence and controlled consistency, not
unobserved external demand or real-world efficacy.

## Material changes and commits

### `f22a312` — Make readiness status mechanically consistent

Added the structured source, validator and targeted suite; replaced SHIP with a
concise current scoreboard; archived the old narrative; reconciled README,
CLAUDE, AGENTS and launch facts; moved closed ledger rows; opened item 73. The
initial direction mutation unexpectedly passed, exposing that metric direction
was trusted from the mutable JSON. An independent metric registry fixed that
hole before commit.

### `c5024e7` — Define a falsifiable design-partner pilot

Added a five-source research matrix and pilot. The matrix labels all access as
partial and does not claim demand. The pilot distinguishes user/buyer, uses a
35-day baseline-plus-five-week design with a consented maximum of 56 days,
manual/exported measurement only, three qualified participants, explicit burden
and repeat-use thresholds, route precedence and standalone/integration/
assurance/pause falsifiers.

### `6fc38af` — Close adversarial readiness-truth gaps

Fixed every reproduced review finding: synthetic “safe pages” overclaim,
hard-coded verdict clauses, duplicate IDs, stale-able top-level metadata,
condition evidence, duplicated current prose, pilot ambiguity and two fail-open
section selectors. Closed item 73 only after focused re-reviews found no HIGH or
MEDIUM residue. Preserved raw results in the permanent log.

## Negative controls

Predicted and observed failures, each reverted cleanly:

1. “Only condition 5 remains” failed generated-block equality.
2. Lower-is-better FP metric changed to higher-is-better initially passed,
   exposing a real gap; after the independent registry it failed direction
   validation.
3. Reinserting “same five are caught” failed the retraction test.
4. Moving a CLOSED row under Open failed both the test and repository gate.
5. Later mutations reject duplicate IDs, arbitrary verdict/top-level values,
   eight-day stale evaluation, commercial-ready with HOLD/failing conditions,
   pilot/result artefact disagreement, and absent/duplicate current README
   measurement headings.

No expected value, threshold, corpus or detector behavior was changed to absorb
an incorrect result.

## Complete assurance results

```text
POST-REVIEW TARGETED: 63 passed in 0.95s; exit 0
POST-REVIEW FULL: 645 passed in 23.91s
TOTAL 1627 statements, 70 missed, 95.70% coverage; required 90%; exit 0
ruff: All checks passed; exit 0
mypy: Success: no issues found in 26 source files; exit 0
dependency floors: 20 audited; all clear/bounded/existing/compatible; exit 0
release claims: no claim violations; exit 0
published claims: PyPI 0.4.1 live, no drift/violations; exit 0
figure rules: 34 distinct proportions, no violations; exit 0
capture: 3 verified, 0 missing, 0 corrupt; exit 0
readiness consistency: status, scoreboard, harness and ledger agree; exit 0
package build: skillwatch-0.4.1.tar.gz and wheel built successfully
delta guard: REFUSING on 2026-07-31 as designed; exit 3
```

Test-count accounting: prior collection 633; only
`tests/test_readiness_consistency.py` was added, with twelve collected tests;
final collection/full run 645. Production coverage remained 95.70%.

No-new-debt enumeration: no suppression, pin, skip, xfail, noqa, type-ignore,
exclusion, stub, hardcoded harness output or TODO was introduced. Generated build
warnings about disabled byte-compilation are not suppressions. The pilot's
“pinned references” phrase is a participant disqualifier, not a dependency pin.

## Visual inspection and failed attempts

Pandoc rendered SHIP, pilot and research. Playwright first failed because it
blocks `file:`; snap Chromium then failed to place two screenshots. These were
not treated as proof. A temporary localhost server produced HTTP 200 pages;
Playwright full-page snapshots/screenshots showed intact headings, lists and
tables with no overlap/truncation. Only `/favicon.ico` returned 404. The server
was stopped and its untracked browser directory removed.

## Independent adversarial review

Reviewer A saw only canonical truth surfaces, implementation, research and
pilot. Reviewer B saw only the final diff, raw gates, ledger and fail-before/
mutation record. Initial findings: one HIGH synthetic-page-rate overclaim;
MEDIUM evidence/status, hard-coded rendering, duplicate truth, duplicate IDs and
pilot-routing gaps; cheap LOW independence/research wording and heading
fail-open behavior. Every finding was reproduced and fixed. Reviewer B final:
“Fixed. No residual duplicated-truth finding remains within the focused scope.”
Reviewer A final cross-field result: “fixed, no residual”; its last LOW heading
selector was then fixed and mutation-tested. No finding was disputed.

## Research limitations and pilot status

Five primary sources were partially reviewed: two peer-reviewed USENIX papers,
one peer-reviewed ACL Findings paper, changedetection.io official API docs and
SLSA v1.2 provenance. None was read end to end; this is explicit. Deeper reading
changing a pilot decision is Unverified. The pilot is a permissible
evidence-gathering exercise, not evidence of demand or commercial readiness.

Recommended next action: after 2026-08-05, the maintainer runs the separately
pre-registered organic delta pass in its own measurement unit, then recruits the
minimum three qualified pilot participants only if willing to perform outreach.
Default: **PILOT**.

## Scope integrity

`git diff --name-status de2a998..HEAD -- skillwatch/`, `analysis/corpus/`,
`analysis/run_delta_pass.py` and `pyproject.toml` produced no changes. Detector,
corpora, baseline, dependencies, telemetry and production features are
unchanged. No push, PR edit, merge, tag, release, publish or third-party contact
occurred.

## Exact reproduction commands

```bash
cd /home/mkuziva/skillwatch
export PYTHONDONTWRITEBYTECODE=1
.venv/bin/python -m pytest -q tests/test_readiness_consistency.py tests/test_continuity.py tests/test_figure_rules.py tests/test_claude_md_currency.py tests/test_gate_table.py
.venv/bin/python -m pytest --cov=skillwatch --cov-report=term-missing --cov-fail-under=90 -q
.venv/bin/python -m pytest --collect-only -q
.venv/bin/ruff check skillwatch/ tests/ scripts/ analysis/
.venv/bin/mypy skillwatch/ scripts/ $(git ls-files 'analysis/*.py')
.venv/bin/python scripts/audit_dependency_floors.py
.venv/bin/python scripts/check_release_claims.py
.venv/bin/python scripts/check_published_claims.py
.venv/bin/python scripts/figure_rules.py
.venv/bin/python analysis/verify_capture.py
.venv/bin/python scripts/readiness_consistency.py
.venv/bin/python -m build
.venv/bin/python analysis/run_delta_pass.py  # must refuse before 2026-08-05
git diff --check
git diff --name-status de2a998498293ad17f6b1990e19dc8868c614293..HEAD -- skillwatch/ analysis/corpus/ analysis/run_delta_pass.py pyproject.toml
git status --short --branch
```

## Complete continuity ledger

The canonical ledger is [OPEN-ITEMS.md](../OPEN-ITEMS.md). It is intentionally
not duplicated into this committed handover because doing so would create the
same second current truth source this unit closes. Its exact blob at handover
creation is settled by:

```bash
git hash-object OPEN-ITEMS.md
cat OPEN-ITEMS.md
```

The Downloads consolidation must include the ledger verbatim for a reader
without repository access; the in-repository canonical ledger remains the
authority if the two ever differ.
