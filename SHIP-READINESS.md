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
| 3 | **PASS** | An owner and quarterly cadence are documented; the current review is overdue. |
| 4 | **PASS** | SIGIL supports the premise; it is a preprint, not peer-reviewed. |
| 5 | **FAIL** | No external user or demand evidence has been observed. |

**Verdict: HOLD.** Condition 2 is not demonstrated; condition 5 fails.
Condition 2 evidence: 6/37 (16.2%), 95% Wilson interval [7.7%, 31.1%]. This lower-is-better gate uses the upper bound.
Zero users is the binding commercial constraint, distinct from the unresolved condition 2 evidence gate.
Organic delta evidence: pending. Private pilot: permissible_evidence_gathering. General commercial readiness: not_demonstrated.
<!-- readiness:end -->

## Current evidence

Run `python3 analysis/measure_efficacy.py` in an environment with the project
dependencies installed. The repository virtual environment currently emits:

- original corpus: 37 benign, 10 pattern-matching malicious, 32 evasive;
- benign false positives: 6/37, Wilson interval [7.7%, 31.1%];
- overall recall: 27/42; evasive recall: 17/32;
- evasive families: semantic 3/13, structural 6/10, mechanical 7/7,
  non-English 1/2.

These are synthetic, project-authored corpora. They do not establish real-world
alert burden. The days-apart organic delta measurement remains pending and must
not be substituted with the minutes-apart `0/3` rehearsal result.

## Condition notes

### Condition 1 — documentation route passes

The recall route does not pass its interval threshold. The documentation route
passes because the README makes the detector ceiling explicit: semantic evasion
is usually missed, and the dependable mechanism is change monitoring plus human
review. The unreproducible historical statement that the original ten retained
the “same five” detections is not a current fact; its retraction remains in the
historical archive.

### Condition 2 — not demonstrated

The benign false-positive threshold is ≤30%. Because lower is better, the upper
Wilson bound controls. The current upper bound is 31.1%, so this condition does
not pass. No threshold, corpus or detector behavior was changed to alter that
result. The scheduled organic delta pass is the next relevant evidence.

### Conditions 3 and 4 — pass with qualifications

Condition 3 has a named owner and cadence, but its review is overdue. Condition
4 rests on SIGIL as independent premise evidence; SIGIL is a preprint and a
competing approach, not peer-reviewed validation of SkillWatch.

### Condition 5 — failed and commercially binding

No external user or demand evidence has been observed. This is the binding
commercial constraint. It is not the only unresolved readiness question because
condition 2 and the organic delta evidence remain unresolved.

## Current `hidden_content` boundary

The detector and taxonomy agree: flagged techniques are `display:none`,
`visibility:hidden|collapse`, `opacity:0`, `font-size:0`, and a zero-sized box
with clipped overflow, whether inline or in a same-document `<style>` rule.
HTML `hidden`, off-screen positioning, `clip-path`/`text-indent` screen-reader
idioms and `aria-hidden` are deliberately not flagged. External stylesheets are
outside the product's user-specified-URL network boundary. Nested CSS at-rules
remain unevaluable. The full rationale is in
`docs/HIDING-TECHNIQUE-TAXONOMY.md`.

## Permissible next evidence

A private design-partner pilot is permissible as evidence gathering. It is not a
claim of production or general commercial readiness. Its purpose is to measure
whether change monitoring and provenance alter real decisions at tolerable
review cost. The pre-registered organic delta pass is separately eligible only
on or after 2026-08-05 and is not run in this consistency session.
