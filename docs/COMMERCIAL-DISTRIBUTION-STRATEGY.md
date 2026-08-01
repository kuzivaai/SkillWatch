# Commercial distribution strategy

## Decision

**Primary route: integration layer for existing agent package, scanner, registry,
CI and approval workflows.** Use the current standalone CLI only as reversible
pilot apparatus. **Secondary use: portable provenance and audit evidence.**
**Rejected route: generic standalone web-change monitor.**

This is a hypothesis, not demand and not authority to build an integration.
Current investment posture is HOLD until qualified participant behavior supports
it. If the pilot fails, pause standalone development.

## Route test

| Route | User / buyer / trigger | Distinct value and adoption | Strongest failure / cheapest falsifier |
|---|---|---|---|
| Generic monitor | Web operator / operations buyer / page change | Mature substitutes already win rendering, filtering and hosted operations. | No agent-specific advantage; reject from official comparison. |
| Skill scanner | Security engineer / AppSec / intake | Existing scanners have distribution and broader analysis. | SkillWatch triage misses semantic evasion; do not position here. |
| Standalone temporal CLI | AI-platform operator / platform owner / approved mutable reference | Local privacy and coherent end-to-end evidence. | Another install/schedule/review burden; retain only if two independent users prefer it and return unprompted. |
| Integration layer | Same user/buyer / approval or detected change | Adds temporal reference/impact evidence inside an existing workflow. | No integration request or affected mapping changes no decision. Pilot before building. |
| Provenance component | Assurance reviewer / assurance owner / disputed state | Portable observed-content, diff, ledger and optional anchoring evidence. | Diff alone suffices or evidence never changes a decision. |
| Assurance services | Consultant/reviewer / assurance buyer / adaptation need | Assurance, adaptation and assistance around open core. | Labor exceeds value or no commercial follow-through. |
| Pause | Maintainer / NA / failed pilot | Preserves capacity. | Overturned by repeated independent decision-changing use. |

## Sensitivity

- Adoption-first: integration wins because it removes a separate workflow.
- Defensibility-first: integration plus a used reference/impact graph wins
  conditionally; generic features are copyable.
- Enterprise-trust-first: portable evidence wins, but publisher identity and
  governed approval remain gaps.
- Maintainer-capacity-first: pause wins; a narrow integration experiment is the
  only lower-cost alternative.

No weighting makes generic monitoring or scanner positioning credible. A score
does not prove the decision.

## Participant and distribution system

At most three profiles:

1. User: security/AI-platform operator approving skills or MCP configurations.
   Buyer: AppSec or AI-platform lead. Qualifies only with mutable references and
   a real approval workflow; disqualify curiosity-only use or no authority to act.
2. User: OSS/project maintainer consuming agent assets. Buyer: project/platform
   owner. Qualifies with repeated reference review; disqualify one-off scanning.
3. User: assurance consultant/reviewer. Buyer: consultancy principal or client
   assurance owner. Qualifies only if evidence enters client decisions.

Channel hierarchy:

1. Maintainer-authorized qualified design partners already using registry,
   scanner, CI, ticket or approval workflows.
2. Technical proof assets: SARIF example, affected-context report, portable ledger
   verification, exact limitations.
3. Consent-based case study showing a decision changed.
4. Sustained issue/community participation.
5. Public launch channels only as attention acquisition.

Funnel: `qualified → clean install → useful baseline → repeated run → genuine
event → reviewed decision → unprompted continued use → integration request →
commercial follow-through`.

Activation is the first useful baseline on a real approved asset. Retention is a
third scheduled run plus an unprompted final run. Referral is a participant-
approved technical case study or introduction to the workflow owner. Stars,
downloads and social attention are not demand. The first ten qualified attempts
calibrate volume assumptions; no conversion rate is invented.

Commercial-offer hypothesis: paid assurance/adaptation/assistance or a private
workflow adapter around the Apache-2.0 core, only after a concrete procurement
step. Sponsorship may support contributors but is not the sales model.

## Stop and overturn criteria

Pause if qualified participants will not install, require excessive intervention,
see too few meaningful changes within the pilot cap, do not return unprompted,
find generic monitors sufficient, derive no decision value from affected mapping
or provenance, or make no commercial follow-through. The strongest overturning
observation is two independent qualified users meeting the pilot thresholds while
explicitly preferring the standalone local CLI.
