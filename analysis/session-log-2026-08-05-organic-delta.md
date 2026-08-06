# Session log, 2026-08-05: the organic delta pass ran

Branch `feat/archive-durability-and-strict-audit`, starting from `99decb0`.

## What this unit did

Ran the scheduled real-page delta pass on the first date its own guard permits,
recorded the result through the repository's own machinery, and fixed two gates that
were red on arrival.

## Starting state, measured rather than assumed

`pytest` reported 647 passed and **1 failed**, and two gates were red:

| Gate | Exit | Finding |
|---|---:|---|
| `scripts/readiness_consistency.py` | 1 | `HANDOVER-BUSINESS-OPERATIONS-2026-08-01.md`, added by the immediately preceding commit `99decb0`, carried no supersession marker. The commit that added it broke the gate that governs it. |
| `scripts/audit_dependency_floors.py` | 1 | `cryptography>=48.0.1` permits GHSA-g6cj-pr64-35w5, GHSA-jwv3-5hgf-82ww, GHSA-m2h6-j472-rp4c and PYSEC-2026-3552/3553/3554. Derived minimum safe floor 50.0.0. |

The dependency red was **new since 2026-08-01 without any repository change**: the
floor had not moved since `9e7b2a3`, so the advisories were published underneath a
static declaration. That is the failure mode the floor auditor exists to catch, and
it caught it.

`analysis/verify_capture.py` exited 0 with 3 of 3 recorded copies verified, which is
the precondition the delta pass depends on.

## The measurement

`python3 analysis/run_delta_pass.py`, 2026-08-05, seven days after the 2026-07-29
baseline. `EARLIEST` is 2026-08-05, so this is the earliest permitted run.

```
re-fetched OK          197/201
extracted text changed 38/197 (19.3%, 95% CI [14.4%, 25.4%])
DELTA FALSE-POSITIVE RATE  18/38 (47.4%, 95% CI [32.5%, 62.7%])
  suspicious_script  11/38   credential_reference 3/38   new_exec_command 3/38
  hidden_content      3/38   new_domains          2/38   new_base64       2/38
  major_deletion      1/38
```

**The whole 95% interval sits above the 30% gate.** Its lower bound, 32.5%, already
exceeds the threshold. So ship-readiness condition 2's failure is **structural, not a
small-sample artefact**, which is precisely the question item 38 posed and could not
answer from anything in the repository. A larger sample cannot rescue it.

The synthetic corpus estimated 16.2%. The real-page rate is roughly **three times**
that. The synthetic figure was the optimistic one, and it was the one being published.

`suspicious_script` alone, at 11/38 (28.9%), nearly exhausts the 30% budget by itself.

## What was built to record it, and why not by hand

Writing 18/38 onto a documentation surface by hand would have reproduced the exact
defect `scripts/figure_rules.py` exists to prevent. Instead:

- **`analysis/report_delta_pass.py`** (new, tracked): an offline reporter over the
  committed `DELTA-PASS.json`, registered as a third harness command. Not
  `run_delta_pass.py` itself, which re-fetches 201 live URLs and would make CI
  non-deterministic. Every published copy of the organic figure is now checked for
  currency, arithmetic and label correspondence on each run. Fails closed on a
  missing or malformed artefact.
- **A new metric family**, `false-positive-rate-organic`. Without it the organic and
  synthetic rates both classify as `false-positive-rate` and are therefore
  interchangeable to the correspondence check, so the flattering 16.2% could be
  published under a real-page label with every rule passing. Same shape as the
  existing evasive/overall recall split.
- **`readiness_consistency.organic_errors`**: derives the organic status from the
  artefact and the Wilson arithmetic rather than trusting the declaration.

### The `fail` status that condition 2 cannot express

Condition 2 is bound by construction to the synthetic efficacy harness, and its
validator returns only `pass` or `not_demonstrated`. It has no way to say "decided,
and against us". The organic validator therefore has three outcomes: `pass` (upper
bound meets the gate), `fail` (lower bound exceeds it, so refuted) and
`not_demonstrated` (the interval straddles it). `organic_delta_result` is `fail`.

Condition 2 itself still reads `not_demonstrated`, because it reports the synthetic
corpus and that is what it is wired to. Both figures are now on the scoreboard, side
by side, which is the second half of item 37's closing condition.

## Negative control on the new gate

Stimulus named in advance: the synthetic pair `6/37` published under an organic label.

```
[figure-mislabelled] SHIP-READINESS.md:45: 6/37 is published as
false-positive-rate-organic but the harness prints it as false-positive-rate.
The value is real and current; the label is wrong.
1 figure violation(s).                                              exit=1
```

Mutation reverted, `git diff` clean. RED OBSERVED.

## Ledger

- **Item 37 closed** on measurement. External validity is established. What closes is
  the validity of the figure, not the figure, which is bad.
- **Item 38 stays open, decided against.** None of its three closing routes occurred:
  the rate did not land below 30%, no larger benign corpus narrowed the synthetic
  bound, and the gate was not re-specified.
- **Item 43 stays open and cannot be settled from this artefact.** Its pre-registered
  rule asks whether `display:none` contributes at least 10% of the delta rate.
  `DELTA-PASS.json` records only `{url, flags}`, so no per-technique attribution
  exists. The reading is also ambiguous on the item's own terms: 3/18 is 16.7% and
  clears 10%, 3/38 is 7.9% and does not, and the item never fixed the denominator.
  Recorded rather than resolved by choosing the convenient one.
- **Item 82 opened** for both instrumentation gaps: no per-technique attribution, and
  4 of 201 URLs failed to re-fetch with no record of which or why. The first live run
  is exactly where those network outcomes carried information, and it was discarded.

## Three tests that were pinned to moving values

`test_healthy_overlapping_output_is_not_rejected` listed harness commands by index,
so it omitted the new third one and failed inside the fail-closed branch rather than
testing the floor. `test_current_metadata_fields_reject_arbitrary_or_stale_values`
pinned `organic_delta = "complete"` as the wrong spelling; the delta pass made it the
right one, so the assertion silently stopped testing anything.
`test_ledger_review_date_cannot_predate_item_history` pinned the latest item date.
All three now derive their expectations.

## Verification

```
pytest                              669 passed        (was 647 passed, 1 failed)
ruff check skillwatch/ tests/ scripts/ analysis/      exit 0
mypy skillwatch/ scripts/ $(git ls-files 'analysis/*.py')  exit 0
readiness_consistency.py / figure_rules.py            exit 0
audit_dependency_floors.py / check_release_claims.py  exit 0
verify_capture.py / report_delta_pass.py              exit 0
```

## Not done, deliberately

Nothing was committed, pushed, released or published. No detector change was made:
the organic rate is now a baseline that a detection change would have to be measured
against, and changing detection in the same unit that established it would confound
both.

**The commercial reading is the maintainer's to make.** The transferable
false-positive rate is 47.4% with a lower bound of 32.5%. Roughly one in two flagged
real pages is a false alarm, on benign pages, measured over seven days of ordinary
editorial drift. That is the number a design-partner pilot would expose a
participant to.
