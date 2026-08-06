# Commercial-validation research for a design-partner pilot

Search date: 2026-07-31. Research question: what should SkillWatch measure to
decide whether change monitoring and provenance create enough operational value
to justify continued investment? This is a bounded five-source review, not a
market survey. No source demonstrates demand for SkillWatch.

## Source matrix

### 1. True Attacks, Attack Attempts, or Benign Triggers?

- Authors: Limin Yang et al.
- Date and venue: 2024, 33rd USENIX Security Symposium.
- Peer review: yes, conference proceedings.
- Access: conference page and abstract/summary; the open-access paper was
  available but was not read end to end in this session.
- Narrow finding: a four-year operational dataset contained 115 million alerts;
  the study distinguishes true attacks, attack attempts and benign triggers.
- Limitation: enterprise network SOC alerts are not URL-change alerts and the
  volume is radically different.
- Transferability: classification quality and review burden matter more than a
  raw “false positive” label.
- Pilot decision changed: record genuine change, benign trigger, actionable
  outcome and review time separately; never collapse them to one precision rate.
- Source: <https://www.usenix.org/conference/usenixsecurity24/presentation/yang-limin>

### 2. 99% False Positives: A Qualitative Study of SOC Analysts’ Perspectives on Security Alarms

- Authors: Bushra A. Alahmadi, Louise Axon, Ivan Martinovic.
- Date and venue: August 2022, 31st USENIX Security Symposium.
- Peer review: yes, conference proceedings.
- Access: conference page and abstract/summary; the open-access PDF was
  available but was not read end to end in this session.
- Narrow finding: survey participants (n=20) and qualitative participants
  (n=21) reported high manual validation burden; the paper identifies reliable,
  explainable, analytical, contextual and transferable alarm properties.
- Limitation: small qualitative samples in SOC settings; it does not establish a
  tolerable threshold for SkillWatch.
- Transferability: provenance and diff context have value only if they shorten or
  improve a real decision.
- Pilot decision changed: measure review time, context sufficiency, evidence used
  in a decision and benign-trigger burden—not alert count alone.
- Source: <https://www.usenix.org/conference/usenixsecurity22/presentation/alahmadi>

### 3. Adaptive Attacks Break Defenses Against Indirect Prompt Injection Attacks on LLM Agents

- Authors: Qiusi Zhan, Richard Fang, Henil Shalin Panchal, Daniel Kang.
- Date and venue: April 2025, Findings of NAACL 2025, pages 7116–7132.
- Peer review: yes, ACL Findings conference publication.
- Access: ACL Anthology metadata and abstract; the full text was available but
  was not read end to end in this session.
- Narrow finding: adaptive attacks bypassed all eight evaluated defenses with
  attack success above 50%; static evaluation can overstate robustness.
- Limitation: evaluates agent defenses, not periodic content-change monitoring;
  its attack success rates do not transfer to SkillWatch.
- Transferability: the pilot must not treat regex triage as the value unit or a
  green scan as safety; evaluate whether noticing a change alters review/action.
- Pilot decision changed: ask participants to compare change detection and
  provenance evidence separately, and prohibit claims that the pilot validates
  payload detection.
- Source: <https://aclanthology.org/2025.findings-naacl.395/>

### 4. changedetection.io API 0.1.7

- Issuing body: changedetection.io project.
- Publication/revision date: current documentation retrieved 2026-07-31; page
  does not expose a reliable publication date.
- Peer review: no; official competitor documentation.
- Access: partial documentation-page review of the API overview and named
  capabilities; not an end-to-end review of every endpoint.
- Narrow finding: the API manages watches, groups and notifications and supports
  text/JSON diff processors, notification formats and browser steps.
- Limitation: capability documentation does not show customer outcomes.
- Transferability: a mature general monitor can satisfy basic watch/diff/notify
  workflows, so SkillWatch must demonstrate incremental value from reference
  discovery or provenance rather than generic change detection.
- Pilot decision changed: explicitly ask whether changedetection.io or another
  generic monitor would satisfy the workflow; this is a standalone-product
  falsifier.
- Source: <https://changedetection.io/docs/api_v1/>

### 5. SLSA Provenance v1.2

- Issuing body: Supply-chain Levels for Software Artifacts (SLSA) project.
- Publication/revision date: v1.2 current specification, retrieved 2026-07-31.
- Peer review: no academic peer review; official ecosystem specification.
- Access: partial specification-page review of the provenance purpose and
  verification model; not an end-to-end review of the complete specification.
- Narrow finding: provenance is verifiable information for tracing an artefact
  through a supply chain to its origin; verification binds claims to an artefact
  and a root of trust.
- Limitation: build provenance is not web-content history; SkillWatch’s local
  hash chain is weaker unless its head is independently anchored.
- Transferability: provenance is valuable only if a reviewer uses it to establish
  origin/history or make a decision they could not make from a diff alone.
- Pilot decision changed: record whether ledger/anchor evidence changed a
  decision, and whether participants prefer it to the change diff.
- Source: <https://slsa.dev/spec/v1.2/provenance>

## Bounded conclusion

Demonstrated by the sources: alert review has a human cost; benign triggers and
true attacks are not the only useful classes; adaptive threats make payload
detection an unsuitable value claim; generic monitors already cover watch/diff
and notification; provenance is meaningful when verified and used.

Unverified: that SkillWatch reduces review time, discovers references a partner
would otherwise miss, changes a decision, earns repeat use, or commands payment.
The pilot in `docs/DESIGN-PARTNER-PILOT.md` measures those propositions directly.

No additional source was used because the five-source cap was sufficient to
define the bounded pilot questions. Because every source was reviewed only in
part, whether deeper reading would change a pilot decision remains unverified.
