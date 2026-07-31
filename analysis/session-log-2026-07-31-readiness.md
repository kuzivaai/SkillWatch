# SkillWatch readiness-consistency evidence — 2026-07-31

Append-only record for the readiness-truth and design-partner-pilot unit.

## Environment and initial state

```text
UTC: Fri Jul 31 21:31:15 UTC 2026
repository: /home/mkuziva/skillwatch
sandbox: workspace-write
approval: managed escalation
writes: repository and /tmp; outside paths require approval
network: restricted by default; approved fetch and GitHub reads succeeded
start_head: de2a998498293ad17f6b1990e19dc8868c614293
origin/main: 6c6ab215742b8d4913b9193a8df49e645f5cd060
upstream: de2a998498293ad17f6b1990e19dc8868c614293
branch: feat/archive-durability-and-strict-audit
local-only commits: none
remote-only commits: none
skillwatch_diff_exit=0
initial_diff_check_exit=0
```

PR #34 was reproduced via GitHub: OPEN, non-draft, MERGEABLE/CLEAN, head
`de2a998498293ad17f6b1990e19dc8868c614293`, base `main`, 12 commits, 17 changed
files, +4525/-1090. All nine CI checks passed. Its title and body still described
the earliest archive/strict-audit unit and claimed 595 tests.

## Pre-edit claim classification

1. **Demonstrated:** PR #34 is open at the GitHub-reported revision.
2. **Demonstrated:** the feature branch is fully pushed; upstream equals HEAD and
   both local-only and remote-only commit lists are empty.
3. **Demonstrated:** no `skillwatch/` production code differs from `origin/main`
   (`git diff --quiet ...`, exit 0).
4. **Demonstrated:** the dependency-complete `.venv` reproduces the harness and
   the prior 633-test collection; the unqualified system `python3` commands are
   **Contradicted** as reproducible commands because they fail importing
   `confusable_homoglyphs`. Settling command: `.venv/bin/python -m pytest
   --collect-only -q` and the escalated full coverage command.
5. **Contradicted:** ship-readiness condition 2 does not pass. The current
   harness gives benign FP 6/37 with Wilson upper bound 31.1%, above the ≤30%
   threshold.
6. **Contradicted:** conditions 1–4 do not all pass because condition 2 is not
   demonstrated.
7. **Contradicted:** zero users is not literally the only unresolved gate;
   condition 2 and the organic-delta evidence remain unresolved. It is the
   binding commercial constraint.
8. **Contradicted:** `SHIP-READINESS.md` contains stale current corpus totals,
   a retracted “same five” claim, and the pre-rewrite inline-only
   `hidden_content` description.
9. **Contradicted:** `## Open` contains rows explicitly marked CLOSED, including
   items 35 and 36.
10. **Contradicted:** PR #34 title/body do not represent its current 12-commit,
    17-file scope or current 633-test baseline.

## Reproduced contradictions

```text
OPEN-ITEMS.md:30: Item 9 ... is the only thing gating ... Conditions 1–4
SHIP-READINESS.md:38: condition 2 STILL NOT DEMONSTRATED
SHIP-READINESS.md:44: Conditions 1–4 pass
SHIP-READINESS.md:51: expanded from 10 items to 25
SHIP-READINESS.md:61: the same five are caught
SHIP-READINESS.md:77: 25 evasive items
SHIP-READINESS.md:96: only inspects an element's inline style
OPEN-ITEMS.md:58: item 35 status CLOSED under ## Open
OPEN-ITEMS.md:59: item 36 status CLOSED under ## Open
```

The system interpreter failed the requested harness commands with
`ModuleNotFoundError: confusable_homoglyphs`; this is an environment-command
failure, not a harness result. The repository `.venv` reproduced:

```text
original corpus: 37 benign, 10 adversarial A, 32 adversarial B
benign FP: 6/37 (16.2%, 95% CI [7.7%, 31.1%])
overall recall: 27/42 (64.3%, 95% CI [49.2%, 77.0%])
evasive recall: 17/32 (53.1%, 95% CI [36.4%, 69.1%])
families: semantic 3/13; structural 6/10; mechanical 7/7; language 1/2
base rate: 201 pages, 166 SKILL.md files, 157 repositories
figure rules: 34 distinct proportions; exit 0 under `.venv`
```

## Readiness fail-before

Prediction: the targeted suite should fail once for each reproduced class:
contradictory verdict, non-directional bound rule, retracted claim, stale corpus
totals, and closed rows under Open.

```text
$ .venv/bin/python -m pytest -q tests/test_readiness_consistency.py
FFFFF
5 failed in 0.06s

Failures:
- condition 2 row contains NOT DEMONSTRATED while current verdict says 1–4 pass;
- no directional lower/higher and upper/lower rule exists;
- current condition 1 prose says “same five are caught”;
- current condition 1 prose says 25 evasive items while the corpus contains 32;
- CLOSED rows occur under ## Open.
```

## Design choice

Chosen: `docs/readiness-status.json` is the small structured source for condition
status, metric direction, verdict and the distinction between commercial and
readiness constraints. `scripts/readiness_consistency.py` validates it against
the live efficacy harness and requires `SHIP-READINESS.md`'s marked current block
to equal the generated rendering. It also validates ledger sections.

Rejected: correcting prose and adding only semantic searches. That would catch
today's phrases but leave five independently maintained status copies. The
structured source closes status/verdict drift and derives metric bounds; prose
searches remain narrow regressions for retracted historical claims and detector
description. Blind spot: arbitrary prose outside the generated block can still
make novel semantic claims; bounded regression searches and review remain needed.
A future condition is added once to the JSON schema and renderer, while its
metric is named from harness output rather than copied into prose.

## Negative-control predictions

1. Change the generated verdict to “only condition 5 remains”: the generated
   scoreboard equality test must fail.
2. Change condition 2 direction to `higher_is_better`: status validation must
   fail because the lower bound would pass while status remains not demonstrated.
3. Reinsert “same five are caught” in the current condition 1 section: the
   retracted-claim test must fail.
4. Move closed item 35 under Open: the ledger-section test and repository gate
   must fail.

Each mutation will be reverted and checked with a path-scoped empty diff against
its saved pre-mutation copy.

## Negative-control observations

```text
Control 1 — scoreboard says “Only condition 5 remains”
FAILED test_structured_status_matches_harness_and_current_scoreboard
Diff: expected “Condition 2 is not demonstrated; condition 5 fails”, observed
“Only condition 5 remains”. 1 failed. Reverted.

Control 2 — false-positive metric changed to higher_is_better
First run unexpectedly PASSED. Confound/root gap: direction was supplied by the
same mutable JSON as the metric, so the validator had no independent semantic
knowledge. Added METRIC_DIRECTIONS as the metric-definition registry.
Second run:
FAILED test_structured_status_matches_harness_and_current_scoreboard
condition 2 direction higher_is_better conflicts with
benign_false_positive_rate direction lower_is_better. 1 failed. Reverted.

Control 3 — reinsert “same five are caught” in current condition 1
FAILED test_retracted_original_ten_claim_is_not_current. 1 failed. Reverted.

Control 4 — duplicate CLOSED item 35 under ## Open
FAILED test_ledger_sections_agree_with_row_statuses and repository gate reported:
FAIL: non-open status under Open: | 35 | ... . Reverted.

Post-revert checks:
git diff --check: exit 0
forbidden mutation phrases in current files: no output
item 35 authoritative row count: 1
tests/test_readiness_consistency.py: 6 passed
scripts/readiness_consistency.py: exit 0
```

The first direction mutation found and closed a real duplicated-truth hole. No
expected value was changed to absorb it; the independent metric-direction
registry now makes the control load-bearing.
