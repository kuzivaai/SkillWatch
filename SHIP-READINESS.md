# Ship Readiness

Scoreboard for the five conditions in `DECISION.md` (which is the superseded
pre-remediation record; this file is current).

**Last evaluated:** 2026-07-29, against the corpora in `analysis/corpus/`.

## How gates are evaluated (changed 2026-07-29)

Gates are evaluated on the **lower bound of the 95% Wilson score interval**, not
on the point estimate.

The reason is that these corpora are small, and a point estimate from a small
sample carries almost no information about the underlying rate. The clearest
example is the one this project shipped for months: evasive recall of 5/10 was
recorded as "50.0%, gate met", when its 95% interval runs from 23.7% to 76.3%.
That result is consistent with a true rate of one in four and with a true rate of
three in four. It does not demonstrate anything.

So the question a gate now asks is not *"did the measured value clear the
threshold?"* but *"does the evidence demonstrate the threshold is met?"* Wilson
is used rather than the normal approximation because it stays well-behaved at
small n and near 0 or 1; Clopper–Pearson is needlessly conservative here.

Intervals are computed by `wilson_interval()` in `analysis/measure_efficacy.py`
and printed by the harness, so every figure below is reproducible with:

```bash
python3 analysis/measure_efficacy.py
```

## Condition map

| # | Condition | Status | Basis |
|---|-----------|--------|-------|
| 1 | Evasive recall ≥50% **or** documentation makes unmissable that the triage is decorative | **PASS via the documentation route** | Recall route fails: 11/25 (44.0%, CI [26.7%, 62.9%]). The README now states plainly that the triage is decorative against a competent adversary. |
| 2 | Precision ≥75% | **NOT DEMONSTRATED** | 21/25 (84.0%, CI [65.3%, 93.6%]). Point clears 75%; lower bound does not. |
| 3 | Named maintenance owner and pattern update cadence | **PASS, with an overdue review** | `MAINTENANCE.md` names the owner and a quarterly cadence. The July 2026 review was outstanding and is recorded in `PATTERNS.md`. |
| 4 | ≥1 independent, non-conflicted evidence source for the premise | **UNDER REVIEW** | One of the two cited sources does not support the claim made of it — see below. Not re-established in this pass. |
| 5 | Evidence of minimal user demand | **FAIL** | 0 stars, 0 forks, 0 watchers, no external users. |

**Verdict: HOLD.** Conditions 2, 4 and 5 are unmet or unverified.

## Condition 1 — the honest outcome

The evasive corpus was expanded from 10 items to 25 on 2026-07-29, because at
n=10 the interval was too wide to support any claim. The result:

| | Before (n=10) | After (n=25) |
|---|---|---|
| Evasive recall | 5/10 (50.0%, CI [23.7%, 76.3%]) | 11/25 (44.0%, CI [26.7%, 62.9%]) |

**The detector did not get worse.** Its behaviour on the original ten items is
unchanged — the same five are caught. The measured rate fell because the sample
grew, which is what a wider sample of the same population does to an optimistic
small-sample estimate.

The point estimate is now **below** the 50% threshold, not merely its lower
bound. The threshold has not been moved to accommodate this. Condition 1 offers
two routes, and the recall route has failed on the evidence, so the condition is
met by the second route: the README states that the triage is decorative against
an adversary who is trying to evade it.

Corpus composition, since a recall figure is a property of the corpus as much as
of the detector — 25 evasive items, expanded while preserving the family
proportions of the original ten so that sample size changed and the population
definition did not:

| Family | n | Caught |
|---|---|---|
| Semantic / framing (no obfuscation, no trigger words) | 13 | 2 |
| Encoding / obfuscation (ROT13, reversal, base64, zero-width, homoglyph, spacing) | 7 | 7 |
| Structural (HTML comment, hidden element) | 3 | 1 |
| Non-English instruction | 2 | 1 |

The pattern is not noise. Every obfuscation-family item is caught, because
obfuscation leaves mechanical traces the canonicalisation layer is built to find.
Almost no semantic-framing item is caught, because those contain nothing to match
— they are ordinary English sentences whose meaning is hostile. That is the
documented ceiling, and it is a property of regex triage, not a defect to fix.

One miss is **not** the ceiling and is worth separating out: `E-24` hides text
with `position:absolute;left:-9999px`, and `_extract_hidden_texts()`
(`skillwatch/detector.py:605`) matches only `display:none` and
`visibility:hidden`. That is a narrow implementation gap rather than a semantic
evasion. It is recorded here and in `PATTERNS.md` rather than fixed in the same
change that measures it, because `MAINTENANCE.md` requires an efficacy re-run on
any detector change and mixing the two would make the measurement circular.

## Condition 2 — precision

21/25 (84.0%, CI [65.3%, 93.6%]) on the original corpus; 9/10 (90.0%, CI
[59.6%, 98.2%]) on the holdout. Both point estimates clear 75%; neither lower
bound does. More benign items are needed to demonstrate this, not a lower gate.

## Condition 3 — maintenance

Owner and quarterly cadence are ratified in `MAINTENANCE.md`. The July 2026
review was overdue at the start of this pass; see `PATTERNS.md` for what was
done and what remains.

## Condition 4 — premise evidence

Previously recorded as PASS on two sources. One of them, **arXiv 2508.12538**, is
*MCPXkit: The Unified Toolkit for Analyzing Model Context Protocol Security* — an
offensive toolkit cataloguing attack methods. It is not independent evidence that
the bait-and-switch premise occurs; citing it as such overstates what it says.
The second source (a CSA AI Safety Initiative note) has not been re-verified in
this pass.

The premise may well be supportable — stronger sources appear to exist — but this
condition is marked UNDER REVIEW rather than PASS until a citation has actually
been checked against its primary source. Re-establishing it is separate work.

## Condition 5 — demand

0 stars, 0 forks, 0 watchers, 0 external users. This remains the binding
constraint, and no amount of engineering moves it.

Note for anyone reading an older copy of this file: it previously recorded this
condition's basis as "Repository is private", and listed the PyPI publish, Pages
deployment and Marketplace listing as blocked. Those statements were stale. The
repository is public, `0.2.0` and `0.3.0` are on PyPI, and Pages is serving. The
condition genuinely fails, but for the plain reason that nobody is using the
tool.

## Reproducing these figures

```bash
python3 analysis/measure_efficacy.py
```

The corpora are in `analysis/corpus/`. Until 2026-07-29 only `holdout_v2` and
`html_v1` were tracked in git; the 67 items behind the headline figures were
covered by a `.gitignore` rule, so the published numbers could not be checked
from a clean clone. That is fixed — the corpora and the harness are now tracked.
