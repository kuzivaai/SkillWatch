# SkillWatch design-partner pilot

Purpose: determine whether periodic change monitoring and provenance create
enough operational value to justify continued investment. This is evidence
gathering, not launch copy, a pricing plan or proof of demand.

## Participant hypotheses

### Profile A — agent-security reviewer

- User role: security engineer reviewing deployed skills or MCP configurations.
- Potential buyer: application-security or AI-platform lead; the user and buyer
  may be different people.
- Workflow: reviews terminal-based agent assets and can identify referenced URLs.
- Required problem: owns at least one deployed asset whose external references
  can change after approval and has a real review decision attached to drift.
- Disqualifiers: no deployed references, no authority to review changes, or no
  willingness to run a local CLI.
- Present substitute: manual revisit, repository diff, or generic web monitor.
- Evidence value: can judge whether discovery, diff and provenance alter a
  security decision.

### Profile B — skill or MCP maintainer

- User role: technical maintainer responsible for externally referenced content.
- Potential buyer: maintainer, project sponsor or platform owner.
- Workflow: publishes a SKILL.md/MCP config and periodically validates its links.
- Required problem: concern about upstream documentation drift, removed content
  or a stable URL serving materially different instructions.
- Disqualifiers: references are immutable/pinned, changes have no operational
  consequence, or a generic monitor already fully satisfies the need.
- Present substitute: release checklist, cron plus hashes, changedetection.io.
- Evidence value: can show whether automated discovery and a verifiable history
  reduce an existing manual control.

### Profile C — assurance consultant

- User role: consultant performing periodic client evidence or supply-chain
  reviews.
- Potential buyer: consultancy principal or client assurance owner.
- Workflow: collects change evidence across engagements and must explain what was
  reviewed and when.
- Required problem: repeated need to evidence the history of external references.
- Disqualifiers: one-off assessment, inability to retain a local database, or no
  client decision depends on provenance.
- Present substitute: screenshots, spreadsheets, ticket history, generic monitor.
- Evidence value: tests whether SkillWatch is stronger as an assurance asset than
  as a standalone product.

## Workflow and support boundary

1. Install into a clean Python 3.10–3.13 virtual environment from the specified
   artefact; record success, elapsed time, commands and intervention.
2. Run discovery on an agreed real SKILL.md, MCP config or URL list. Record total
   references, relevant references and anything missed or wrongly included.
3. Establish the initial local baseline. Record time to the first baseline that
   the participant considers useful.
4. Run once every seven days and after any known upstream change. Weekly cadence
   is periodic, limits burden, and creates five independent review opportunities
   after baseline during the 35-day observation window.
5. For every genuine change, the participant reviews the diff first, then the
   provenance/ledger evidence, recording separate usefulness judgements and the
   resulting decision.
6. Maintainer support covers installation clarification and defect capture, not
   operating the participant’s monitoring, classifying alerts for them, or
   changing their security decision.
7. At exit, export only what the participant explicitly agrees to share, remove
   the virtual environment/database if requested, and record whether they choose
   to continue unprompted.

### Duration basis

The observation window is 35 days: baseline plus five seven-day intervals. The
repository’s minutes-apart sample produced only 3 text changes across 199 pairs,
so a short demo cannot establish value. Five weekly opportunities bound burden
while allowing editorial change to occur. If no genuine change occurs, extend
only by explicit agreement until either one genuine event is reviewed or 56 days
total is reached; zero events at that point is itself evidence against the
standalone monitoring value for that participant.

## Data handling

SkillWatch remains local-only and has no telemetry. The only product traffic is
fetching participant-specified URLs. Measurements are recorded manually by
agreement in a participant-owned or mutually agreed worksheet, or explicitly
exported by the participant. No database, skill file, URL inventory, alert or
ledger is uploaded automatically. Participants may redact URLs and content while
retaining timings and decisions.

## Measurements and decisions

| Measure | Recording method | Decision it informs |
|---|---|---|
| Installation completion | yes/no, elapsed time, commands, intervention | Whether self-service use is viable |
| Time to first useful baseline | timer plus participant judgement | Whether setup cost is tolerable |
| Commands/manual decisions | count and notes | Workflow burden and integration need |
| References discovered | total, relevant, missed | Incremental value over manual inventory |
| Genuine changes observed | event log | Whether event frequency can sustain value |
| Alerts reviewed | event log | Denominator for burden/actionability |
| Operationally actionable | participant classification with reason | Whether alerts affect work |
| Review time per event | timer | Whether burden exceeds value |
| Benign-trigger burden | count and reason, separate from detector error | Whether tuning/context is adequate |
| Evidence changed a decision | before/after decision and evidence used | Core operational-value test |
| Repeated use | scan dates | Whether use survives first setup |
| Continued unprompted use | participant-initiated run after support pause | Adoption rather than compliance |
| Change detection vs provenance | separate 5-point preference plus reason | Which value proposition survives |
| Stated willingness to pay | range/context, labelled stated preference | Interview signal only, never purchase evidence |

## Falsification and routing decisions

### Continue a standalone product

Supported only if qualified participants install with limited intervention,
return without prompting, review genuine changes, and at least two independent
participants report a decision changed at tolerable review cost. A stated price
does not satisfy this without behavior.

### Integrate into another tool

Prefer integration when discovery/provenance is useful but participants reject a
separate CLI, want findings in an existing scanner/ticket workflow, or generic
monitoring supplies the change event while SkillWatch-specific evidence remains
useful.

### Consulting or assurance asset

Prefer this route when consultants repeatedly use exports/ledger evidence in
client decisions but end users do not operate the tool independently.

### Pause or stop

Pause or stop if qualified participants will not install; installation requires
the maintainer to operate it; genuine changes are too rare by the 56-day cap;
participants do not return after setup; generic monitors satisfy the workflow;
provenance never changes a decision; or review burden exceeds perceived value.

The strongest standalone falsifier is a qualified participant completing the
workflow and preferring changedetection.io or an existing generic monitor because
reference discovery and provenance add no decision value.

## Claims boundary

- Demonstrated repository facts: local-only operation, no telemetry, periodic
  execution, URL discovery, local baseline/diff, ledger and measured synthetic
  harness results.
- Externally supported threat facts: indirect prompt injection and security-alert
  review burden exist in the cited scopes; neither proves SkillWatch demand.
- Pilot hypotheses: partners value automatic reference discovery, diffs or
  provenance enough to repeat use or change decisions.
- Prohibited claims: production/commercial readiness, real-world detection rate,
  demand, purchase intent, prevention, comprehensive coverage, or superiority to
  generic monitors.
