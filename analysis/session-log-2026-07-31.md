# SkillWatch session evidence log — 2026-07-31

Append-only evidence record for the session requested by the maintainer. Command
output is recorded when observed, not reconstructed at handover time.

## Environment status

Requested command:

```text
$ /status
/bin/bash: line 1: /status: No such file or directory
```

Effective environment reported by the session runtime:

```text
workspace root: /home/mkuziva/skillwatch
filesystem mode: managed/restricted; repository and /tmp writable
git metadata: read-only without escalation
network: restricted by default
approval policy: approval required for writes outside the repository, Git metadata
writes, network/socket-dependent checks, and other escalated operations
```

The unavailable `/status` command is recorded as an attempted check, not silently
treated as success.

## Repository instructions read

```text
Read completely before edits: AGENTS.md, CLAUDE.md, OPEN-ITEMS.md
GitHub workflow read completely: github skill SKILL.md
```

## Early log commit attempt

```text
$ git add analysis/session-log-2026-07-31.md && git commit ...
The following paths are ignored by one of your .gitignore files:
analysis/session-log-2026-07-31.md
hint: Use -f if you really want to add them.
hint: Turn this message off by running
hint: "git config advice.addIgnoredFile false"
```

Result: failed before staging or committing. No force-add was used. The durable
class fix is to re-include `analysis/session-log-*.md` in `.gitignore`.

## Initial repository state

```text
$ git status --short --branch
## feat/archive-durability-and-strict-audit...origin/feat/archive-durability-and-strict-audit [ahead 3]

$ git status --short
[no output]

$ git log --oneline origin/main..HEAD
ed3ee71 Make session evidence durable
39cc419 Add tracked Codex transition handover
f6b75c8 Close adversarial assurance findings
4b366c5 Observe the build gate red; settle --strict as load-bearing
fd4f4a9 Make the gate table see behaviour, not just names
fe66903 Prove the security gate can fail; audit every gate; correct the version claim
17ab8f1 docs(ledger): close items 16, 22, 55-58; correct the global-floor record
852fd72 Make the capture's absence detectable; adopt pip-audit --strict

$ git rev-list --count origin/feat/archive-durability-and-strict-audit..HEAD
3

$ git log --oneline origin/feat/archive-durability-and-strict-audit..HEAD
ed3ee71 Make session evidence durable
39cc419 Add tracked Codex transition handover
f6b75c8 Close adversarial assurance findings

$ git diff main..HEAD --stat -- skillwatch/
[no output]

$ git diff main..HEAD -- skillwatch/
[no output]

$ git diff --quiet main..HEAD -- skillwatch/; echo skillwatch_diff_exit=$?
skillwatch_diff_exit=0
```

Detection implementation is byte-identical to `main`; this is measured, not
inferred from commit subjects.

## Test collection and per-file counts

```text
$ pytest --collect-only -q
628 tests collected in 1.16s

$ pytest --collect-only -q | <per-file counter>
tests/test_anchoring.py 21
tests/test_ci_scope.py 11
tests/test_claim_rules.py 11
tests/test_claude_md_currency.py 7
tests/test_cli.py 38
tests/test_cloak.py 8
tests/test_concealment_unevaluable.py 25
tests/test_delta_pass.py 11
tests/test_delta_rehearsal.py 34
tests/test_dependency_floors.py 32
tests/test_detector.py 88
tests/test_differ.py 8
tests/test_e2e.py 3
tests/test_efficacy_harness.py 14
tests/test_fetcher.py 29
tests/test_figure_rules.py 39
tests/test_formatter.py 23
tests/test_fp_adaptation.py 12
tests/test_gate_table.py 22
tests/test_hidden_content.py 18
tests/test_hiding_taxonomy.py 22
tests/test_ledger.py 40
tests/test_parser.py 22
tests/test_published_claims.py 8
tests/test_sarif.py 2
tests/test_ssrf.py 28
tests/test_store.py 26
tests/test_threading.py 2
tests/test_verify_capture.py 24
```

## GitHub authentication, PR #34, and remote movement

```text
$ gh auth status
github.com
  ✓ Logged in to github.com account kuzivaai (/home/mkuziva/.config/gh/hosts.yml)
  - Active account: true
  - Git operations protocol: https
  - Token: gho_************************************
  - Token scopes: 'gist', 'read:org', 'repo', 'workflow'

$ gh pr view 34 --repo kuzivaai/SkillWatch --json ...
{"baseRefName":"main","headRefName":"feat/archive-durability-and-strict-audit","headRefOid":"4b366c501b5cbfc4c856eddaa3d1d48a469fff7b","isDraft":false,"mergeStateStatus":"CLEAN","mergeable":"MERGEABLE","number":34,"state":"OPEN","title":"Close the archive single-point-of-failure class; settle pip-audit --strict","updatedAt":"2026-07-30T09:51:56Z","url":"https://github.com/kuzivaai/SkillWatch/pull/34"}

Recorded check rollup: all nine CI checks SUCCESS on run 30532398379:
test (3.10), test (3.11), test (3.12), test (3.13), security,
lowest-direct (3.10), lowest-direct (3.11), lowest-direct (3.12),
lowest-direct (3.13).

$ git rev-parse origin/main origin/feat/archive-durability-and-strict-audit
6c6ab215742b8d4913b9193a8df49e645f5cd060
4b366c501b5cbfc4c856eddaa3d1d48a469fff7b

$ git fetch origin --prune
[no output]

$ git rev-parse origin/main origin/feat/archive-durability-and-strict-audit
6c6ab215742b8d4913b9193a8df49e645f5cd060
4b366c501b5cbfc4c856eddaa3d1d48a469fff7b
```

Remote references were byte-identical before and after fetch. No force-push is
needed. PR #34 is OPEN, non-draft, mergeable/CLEAN, but its head is still the
remote branch at `4b366c5`; it does not yet include the three local commits.

## Full test suite with coverage

```text
$ PYTHONDONTWRITEBYTECODE=1 pytest --cov=skillwatch --cov-report=term-missing --cov-fail-under=90 -q
........................................................................ [ 11%]
........................................................................ [ 22%]
........................................................................ [ 34%]
........................................................................ [ 45%]
........................................................................ [ 57%]
........................................................................ [ 68%]
........................................................................ [ 80%]
........................................................................ [ 91%]
....................................................                     [100%]
TOTAL                      1627     70    96%
Required test coverage of 90% reached. Total coverage: 95.70%
628 passed in 20.11s
```

## Named local gates and scheduled refusal

```text
$ ruff check skillwatch/ tests/ scripts/ analysis/
All checks passed!
ruff_exit=0

$ mypy skillwatch/ scripts/ $(git ls-files 'analysis/*.py')
Success: no issues found in 25 source files
mypy_exit=0

$ python scripts/audit_dependency_floors.py
Audited 20 declared dependency floors.
Declared Python support: 3.10, 3.11, 3.12, 3.13
All declared floors are clear of known advisories.
Every declared requirement has a lower bound.
Every floor version exists and permits every supported Python.
(Installability is proven by the lowest-direct CI matrix, not here.)
floors_exit=0

$ python scripts/check_release_claims.py
Checked README.md
Checked sdist PKG-INFO (38895 chars) from skillwatch-0.4.1.tar.gz

No claim violations.

Harness currently produces 34 distinct proportions.
correspondence coverage: 27 of 50 non-exempt proportions carry a recognisable metric label.
the remaining 23 are NOT correspondence-checked — they are still checked for currency and arithmetic. See ledger item 42.
No figure violations: every published proportion is one the harness currently produces, under a label consistent with the harness's own.
release_claims_exit=0

$ python scripts/figure_rules.py
Harness currently produces 34 distinct proportions.
  measure_base_rate.py      17 parsed, minimum 10
  measure_efficacy.py       22 parsed, minimum 18
correspondence coverage: 27 of 50 non-exempt proportions carry a recognisable metric label.
the remaining 23 are NOT correspondence-checked — they are still checked for currency and arithmetic. See ledger item 42.
No figure violations: every published proportion is one the harness currently produces, under a label consistent with the harness's own.
figures_exit=0

$ python analysis/verify_capture.py
manifest      /home/mkuziva/skillwatch/analysis/corpus/realpage/CAPTURE-INTEGRITY.json
expected      sha256 861027d158b67c517074e3a17348777e4405a644c13a33c7fbc85f25aa417dfe  (59968045 bytes)
per-page      8 of 201 recorded hashes checked (deterministic sample)
host          DESKTOP-71IU9IC (recorded holder)
VERIFIED  /home/mkuziva/.skillwatch-archive/realpage-2026-07-29/fetched_pages.json
VERIFIED  /mnt/d/skillwatch-archive/realpage-2026-07-29/fetched_pages.json
VERIFIED  /mnt/c/Users/mkuzi/skillwatch-archive/realpage-2026-07-29/fetched_pages.json
3 verified, 0 missing, 0 corrupt, of 3 recorded copies.
All recorded copies verified against the manifest.
capture_exit=0

$ python analysis/run_delta_pass.py
REFUSING: today is 2026-07-31; this pass is scheduled for 2026-08-05 or later.
The first snapshots were 2026-07-29. A second pass sooner than seven days measures per-request churn, not editorial drift — which is exactly what made the first attempt return 0/3.
delta_exit=3
```

The delta result is the required pre-date refusal, not a failed push gate. The
dated commitment remains intact and was not bypassed.

## Continuity regression tests — initial failure

```text
$ pytest -q tests/test_continuity.py
.FF                                                                      [100%]
FAILED tests/test_continuity.py::test_item_22_names_the_later_strict_demonstration
AssertionError: item 22 retains its earlier 'no case was found' conclusion without pointing to item 60, which later demonstrated --strict changing the outcome
FAILED tests/test_continuity.py::test_item_60_links_back_to_the_superseded_record
AssertionError: assert 'item 22' in <item 60 row>
2 failed, 1 passed in 0.02s
```

The durability test already passes because the `.gitignore` class fix preceded
the test. Its required fail-before demonstration follows with that rule removed
temporarily and restored immediately afterward.

```text
$ [temporarily remove !analysis/session-log-*.md]
$ pytest -q tests/test_continuity.py::test_dated_session_logs_are_not_ignored
F                                                                        [100%]
FAILED tests/test_continuity.py::test_dated_session_logs_are_not_ignored
AssertionError: analysis/session-log-2099-12-31.md is ignored; a session cutoff would strand its evidence on one machine. Re-include dated session logs in .gitignore.
1 failed in 0.02s
$ [restore !analysis/session-log-*.md]

$ pytest -q tests/test_continuity.py
...                                                                      [100%]
3 passed in 0.01s
```

The durability test failed for the intended reason with the rule reverted. The
ledger tests failed on the measured contradiction and pass after item 22 names
item 60 as its superseding evidence and item 60 links back to item 22.

## Continuity unit verification

```text
$ pytest -q tests/test_continuity.py
...                                                                      [100%]
3 passed in 0.01s

$ ruff check tests/test_continuity.py
All checks passed!

$ mypy tests/test_continuity.py
Success: no issues found in 1 source file

$ pytest --cov=skillwatch --cov-report=term-missing --cov-fail-under=90 -q
........................................................................ [ 11%]
........................................................................ [ 22%]
........................................................................ [ 34%]
........................................................................ [ 45%]
........................................................................ [ 57%]
........................................................................ [ 68%]
........................................................................ [ 79%]
........................................................................ [ 91%]
.......................................................                  [100%]
TOTAL                      1627     70    96%
Required test coverage of 90% reached. Total coverage: 95.70%
631 passed in 18.83s
```

## Continuity commit and preliminary debt enumeration

```text
$ git commit -m "Make continuity claims self-consistent" ...
[feat/archive-durability-and-strict-audit 86f77ff] Make continuity claims self-consistent
 3 files changed, 193 insertions(+), 3 deletions(-)
 create mode 100644 tests/test_continuity.py

$ git status --short

$ git log --oneline -5
86f77ff Make continuity claims self-consistent
fa748d4 Record repository and PR baseline
ed3ee71 Make session evidence durable
39cc419 Add tracked Codex transition handover
f6b75c8 Close adversarial assurance findings

$ git diff -U0 39cc419..HEAD -- . ':!analysis/session-log-2026-07-31.md' | rg -ni 'skip|xfail|ignore|disable|noqa|type: ignore|TODO|FIXME|(^|[^A-Za-z])(pin|pinned|pins|version pin)' || true
Matches occurred only in the `.gitignore` filename and the ledger/test prose
about closing the ignored-log defect and preserving historical `pip-audit`
skip evidence. There are no new suppressions, pins, skips, exclusions, stubs,
hardcoded values, TODOs, FIXMEs, `noqa`, or `type: ignore` directives.

$ git diff --check 39cc419..HEAD

$ git diff --quiet main..HEAD -- skillwatch/; echo detection_diff_exit=$?
detection_diff_exit=0
```

The complete matching lines remain available in this commit's parent session
output; the decisive enumeration above distinguishes documentary mentions from
introduced debt.

## Independent adversarial review

The reviewer received only the session diff for `.gitignore` and
`tests/test_continuity.py`, committed verification output at log lines 163–299,
and `OPEN-ITEMS.md`. Its findings are reproduced verbatim:

```text
Independent constrained review — 2 material findings, no HIGH.

MEDIUM — `.gitignore` hunk `!analysis/session-log-*.md`; `tests/test_continuity.py:20-31` (`test_dated_session_logs_are_not_ignored`). The claimed class fix is durability/permanence (“dated session evidence logs are permanent handover inputs”; test docstring says an ignored log “disappears on the next clone or machine”), but the test proves only that a hypothetical pathname is *not ignored*. It does not prove any real dated session log is tracked, committed, present, or retained. A newly created `analysis/session-log-YYYY-MM-DD.md` passes immediately while still untracked and therefore still disappears on the next clone; deleting every tracked session log also leaves this test green. This is an instance/workaround that leaves the defect class open. Reproducible falsification: create any matching untracked log, run `pytest -q tests/test_continuity.py::test_dated_session_logs_are_not_ignored` (passes), then run `git ls-files --error-unmatch <that-log>` (fails). A class-level test needs to enumerate the required real log(s) and assert they are returned by `git ls-files` (and, if permanence means retention, assert the expected dated evidence file remains present).

MEDIUM — `tests/test_continuity.py:33-46`, especially exact phrase exclusion and substring cross-links. The module claims continuity evidence is “internally current,” and the session evidence says “the measured contradiction” is now regression-tested, but these tests enforce only today’s wording/links, not semantic consistency. Item 22 passes as long as it contains the literal `Superseded by item 60` and avoids exactly `no case was found in which `--strict` changed the outcome`; item 60 passes if the characters `item 22` appear anywhere. A synonymous contradiction (e.g. “we never identified an outcome altered by `--strict`”) plus those cross-links passes. Likewise `item 22` could occur in unrelated prose in item 60. The evidence accurately demonstrates this one historical wording failed, but overclaims a class closure. Reproducible check: on a throwaway edit, replace item 22’s final two sentences with `Superseded by item 60. We never identified an outcome altered by --strict.` and retain `item 22` in item 60; run the two ledger tests and observe green despite contradiction with item 60’s DEMONSTRATED/load-bearing claim. This should be described as an instance regression test unless assertions parse mutually exclusive status/facts rather than prose substrings.

Exact sources/commands used only:
1. `git diff 39cc419..86f77ff -- .gitignore tests/test_continuity.py`
2. `sed -n '163,299p' /home/mkuziva/skillwatch/analysis/session-log-2026-07-31.md` (covers exactly requested 163-242 and 243-299)
3. `sed -n '1,10000p' /home/mkuziva/skillwatch/OPEN-ITEMS.md`
4. `rg '^\\| (22|60|67) \\|' /home/mkuziva/skillwatch/OPEN-ITEMS.md` (targeted reread of the authorized ledger only)
No other files/history/network inspected; no edits.
```

Both MEDIUM findings were accepted. The first is closed by enumerating every
existing `analysis/session-log-*.md` and requiring `git ls-files
--error-unmatch` to prove it survives a fresh clone. The second is closed by a
structured supersession index (`22 -> 60`) and a regression test for that
machine-readable lineage; the literal prose checks remain instance regression
tests and are not represented as semantic interpretation of arbitrary prose.

The initial strengthened run also exposed that the new index row shadowed the
five-column ledger row in `_ledger_item`; the helper now selects exactly one
five-column ledger row. This was an unexpected fail, not suppressed.

```text
$ pytest -q tests/test_continuity.py  # strengthened tests before fixes
.F..F
FAILED test_existing_session_logs_are_tracked - NameError: name 'probe' is not defined
FAILED test_supersession_index_records_item_22_to_60 - AssertionError
2 failed, 3 passed in 0.03s

$ pytest -q tests/test_continuity.py  # after index, before row disambiguation
..F..
FAILED test_item_22_names_the_later_strict_demonstration
1 failed, 4 passed in 0.03s

$ pytest -q tests/test_continuity.py
.....                                                                    [100%]
5 passed in 0.02s
```
