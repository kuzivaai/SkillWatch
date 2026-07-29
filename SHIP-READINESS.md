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
| 1 | Evasive recall ≥50% **or** documentation makes unmissable that the triage is decorative | **PASS via the documentation route** | Recall route fails: 11/25 (44.0%, CI [26.7%, 62.9%]). The README states plainly that the triage is decorative against *semantic* evasion (3/13) and structural evasion (0/3), while noting it catches mechanical obfuscation 7/7 and non-English 1/2. Families sum to 11/25. |
| 2 | Benign false-positive rate ≤30% | **NO LONGER DEMONSTRATED (2026-07-29)** | Was 4/32 (12.5%, CI [5.0%, 28.1%]) — upper bound cleared. Now **7/37 (18.9%, CI [9.5%, 34.2%])** — **upper bound 34.2% exceeds the gate.** The rise is the priced cost of the `hidden_content` rewrite; see below. Not a regression in behaviour, and not a reason to move the gate. |
| 3 | Named maintenance owner and pattern update cadence | **PASS, with an overdue review** | `MAINTENANCE.md` names the owner and a quarterly cadence. The July 2026 review was outstanding and is recorded in `PATTERNS.md`. |
| 4 | ≥1 independent, non-conflicted evidence source for the premise | **PASS** | arXiv 2605.05274 (SIGIL), abstract checked against the primary source and quoted below. A preprint, not peer-reviewed. The previously cited arXiv 2508.12538 is an offensive toolkit and is retired. |
| 5 | Evidence of minimal user demand | **FAIL** | 0 stars, 0 forks, 0 watchers, no external users. |

**Verdict: HOLD.** Conditions 1–4 pass. Condition 5 — user demand — is unmet and
is the only remaining constraint. No engineering change moves it; it is moved by
distribution, or not at all. Condition 4 was restored and condition 2 was
re-specified on 2026-07-29.

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
*semantic* evasion.

The qualifier matters and is not softening. A blanket "decorative against any
evasion" would be wrong in the opposite direction: mechanical obfuscation is
caught 7 of 7. The honest statement is that an attacker who encodes their payload
is caught and an attacker who simply writes plain English is not.

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
(`skillwatch/detector.py:602`) only inspects an element's **inline `style`
attribute** for a lower-case `display:\s*none` or `visibility:\s*hidden`.

Measured on 2026-07-29, the check does **not** fire on: upper- or mixed-case
declarations (the regex carries no `re.IGNORECASE`), rules in a `<style>` block,
external stylesheets, the HTML `hidden` attribute, `aria-hidden`, off-screen
positioning, `opacity:0`, `font-size:0`, `height:0;overflow:hidden`,
`clip-path:inset(100%)` or `text-indent:-9999px`. Stylesheet-based hiding is the
largest of these in practice — real pages hide content with a CSS class far more
often than with an inline style.

That is a narrow implementation gap rather than a semantic evasion. **The
documentation half was closed on 2026-07-29**: every surface now describes what
the code does rather than what it was assumed to do. **The code gap remains
open**, recorded here and in `PATTERNS.md` rather than fixed in the same change
that measures it, because `MAINTENANCE.md` requires an efficacy re-run on any
detector change and mixing the two would make the measurement circular.

## Condition 2 — false-positive rate (was: precision)

**Status: PASS.** 4/32 (12.5%, CI [5.0%, 28.1%]) on the original benign corpus,
1/6 (16.7%, CI [3.0%, 56.4%]) on the holdout. The gate is an upper bound: the
false-positive rate must not exceed 30%. The original corpus demonstrates that;
the holdout at n=6 does not, and cannot at that size.

### Why this condition was re-specified on 2026-07-29

The condition was previously "precision ≥75%", assessed NOT DEMONSTRATED at
21/25 (84.0%, CI [65.3%, 93.6%]). Two problems, in increasing order of
seriousness.

**The remedy recorded against it was arithmetically backwards.** The note read
"more benign items are needed to demonstrate this, not a lower gate." Precision
is `TP/(TP+FP)`. Adding benign items can only add false positives; it cannot add
true positives. At the observed 12.5% false-positive rate, adding 32 more benign
items yields 21/29 (72.4%) with a lower bound of 54.3% — worse than the 65.3%
it started from. The prescribed fix moved the gate further out of reach.

**Precision is not a property of the detector.** It is a property of the
detector *and the benign:malicious ratio of the corpus it was measured on* —
here roughly 38:47. Deployment runs at nothing like that ratio; almost every
change on a monitored URL is a legitimate edit. A precision figure measured near
1:1 does not transfer to a stream running at 1000:1, and publishing it as a ship
gate implied a deployment property the measurement cannot support. The project's
own honesty rule against applying a statistic from one population to another
applies to its own scoreboard.

The false-positive rate is ratio-independent: it is measured on benign items
only, so it says the same thing whatever the mix. It is the number that
transfers, so it is the number that gates.

This is a re-specification, not a relaxation. The old gate was never met and the
new one is met — but on a different and better-posed question. The precision
figures are still reported in the README, with the base-rate warning attached.

### 2026-07-29 — the gate stopped passing, and why that is reported rather than fixed

The `hidden_content` rewrite (ledger item 7) took evasive recall from 11/32 (34.4%)
to 19/32 (59.4%) and the structural family from 0/10 to 8/10. It also took the
benign false-positive rate from 5/37 (13.5%) to **7/37 (18.9%, CI [9.5%, 34.2%])**.

**On the interval, 34.2% exceeds the ≤30% gate. Condition 2 no longer passes.**

That is a trade, and it is reported as one. The three false positives are B-33
(collapsed accordion), B-35 (hidden form field) and B-37 (a `<style>`-collapsed
changelog). All three genuinely do hide content; the flag is `info` and says
"content is hidden here", which is true. They were added to the corpus in the same
session, deliberately, so the cost of the rule would be counted rather than hidden.

**What was NOT done, and why.** The gate was not moved, the corpus was not padded
with benign items to dilute the rate, and no technique was dropped to buy the
number back. Each would have made the figure pass without changing anything real.
Moving a gate because your change broke it is how a gate stops meaning anything.

**Options, none taken this session:**

1. Accept a higher FP rate for `info`-severity flags specifically, on the grounds
   that a flag meaning "look at this diff" costs a reader seconds. This needs the
   gate re-specified per severity, which is a bigger change than it looks.
2. Suppress `hidden_content` when the concealed text carries no other signal.
   Cheap, but it re-introduces the coupling the flag-class decomposition was
   meant to remove.
3. Accept that n=37 is too small to demonstrate a 30% bound at all — the interval
   is 25 points wide. More benign items narrow it honestly, unlike padding.

**REASONED, not evidenced:** option 3 is most likely right, because the point
estimate (18.9%) is well inside the gate and it is the interval width doing the
work. What would confirm: a benign corpus large enough that the upper bound falls
below 30% at a similar point estimate. Not attempted here — corpus and detector
changes are not measured together, and this session already changed both once.

### What would actually reduce the false-positive rate

All five false positives across both benign corpora came from three delta
checks: `new_exec_command` (2/38), `new_domains` (2/38), `new_base64` (1/38).
The content checks — `prompt_injection`, `credential_reference`,
`unicode_homoglyph` — produced 0/38 (CI [0.0%, 9.2%]).

Deleting the three delta checks would take the corpus false-positive count to
zero. It would also cost five true positives (E-04, E-05, E-09, E-10, E-19),
dropping overall recall from 21/35 (60.0%) to 16/35 (45.7%). That trade is not
worth taking. The honest position is that the false-positive floor is set by the
delta checks and is the price of the recall they contribute.

## Condition 3 — maintenance

Owner and quarterly cadence are ratified in `MAINTENANCE.md`. The July 2026
review was overdue at the start of this pass; see `PATTERNS.md` for what was
done and what remains.

## Condition 4 — premise evidence

**Status: PASS**, on a citation checked against its primary source.

### The source

**[arXiv 2605.05274](https://arxiv.org/abs/2605.05274) — "Sealing the Audit-Runtime Gap for LLM Skills"** (SIGIL).
Tingda Shen, Yebo Feng, Konglin Zhu, Xiaojun Jia, Yang Liu, Lin Zhang. Submitted
6 May 2026. Abstract retrieved from the arXiv API on 2026-07-29.

The premise sentence, quoted verbatim from the abstract:

> "Once in the LLM's context, skill content cannot be reliably separated from
> trusted instructions, and a skill's executable side can invoke privileged
> actions, exposing the skill supply chain to injection, tampering, and rug-pull
> attacks."

And on why install-time review is not enough, also verbatim:

> "Existing defenses are stage-bound: centralized signing, audit reports unbound
> from the runtime artifact, or policy engines that cannot attest to what was
> approved."

That is an independent academic treatment of the exact gap SkillWatch exists to
watch: a skill approved once, whose content is not bound to what runs later.

### Qualifications, stated rather than buried

- **This is a preprint. It is not peer-reviewed.** It is cited as evidence that
  the gap is recognised and characterised in the literature, not as a settled
  result.
- **The paper proposes a competing approach**, and this cuts both ways. SIGIL's
  answer is a cooperation model — an on-chain registry plus a mandatory Skill
  Verification Loader embedded in the platform. SkillWatch's answer is the
  opposite: an independent observer that assumes no cooperation. The paper is
  therefore strong evidence *for the premise* and simultaneously evidence that
  better-resourced approaches to the same problem exist. Both are true and both
  should be said.
- **I did not verify the authors' institutional affiliations**; they are not in
  the abstract. The claim of independence rests on there being no connection to
  this project, which is straightforward, not on any assessment of the authors.

### The citation that must never be reused

**arXiv 2508.12538 is *MCPXkit: The Unified Toolkit for Analyzing Model Context
Protocol Security*** — an offensive toolkit cataloguing attack methods. It was
previously cited here as independent premise evidence. It is not, and it must
never be cited as such again. It may be cited, if at all, as a taxonomy of attack
techniques.

The second source previously claimed (a CSA AI Safety Initiative note) still has
not been re-verified against its primary source and is **not** relied on here.
This condition passes on arXiv 2605.05274 alone.

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
