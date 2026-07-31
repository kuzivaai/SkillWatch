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
