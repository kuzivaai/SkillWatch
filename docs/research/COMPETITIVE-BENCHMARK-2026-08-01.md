# Competitive benchmark — 2026-08-01

Use case: a security-conscious team approved an agent skill or MCP configuration
referencing mutable external instructions. It must learn what changed, affected
contexts, observed evidence, evidentiary limits, and whether a human accepted the
new state.

Labels record capability evidence only: **D** demonstrated; **P** partially
demonstrated; **C** claimed; **NF** not found after the named official surfaces;
**NA** not applicable. They are not quality scores. NF is not a claim of absence.

## Official sources and target jobs

- [Microsoft APM](https://github.com/microsoft/apm): agent dependency graph,
  transitive resolution, content-hashed lockfile, workspace audit, policy, CI and
  SARIF. It does not document periodic arbitrary-URL observation or accepted
  external snapshots. Closest distribution/integration neighbour.
- [changedetection.io](https://github.com/dgtlmoon/changedetection.io): mature
  arbitrary-page monitoring, diffs/history, filters, schedules, Playwright and
  APIs; no agent reference/impact graph found. Strongest generic substitute.
- [Distill](https://help.distill.com/): browser/cloud page monitoring; official
  retrieval was incomplete, so most detailed capabilities remain NF.
- [Visualping](https://visualping.io/): hosted visual/text monitoring with browser
  actions, history, teams, API/webhooks and MCP; no local mode or agent graph found.
- [Snyk Agent Scan](https://github.com/snyk/agent-scan): agent/MCP/skill discovery
  and security scanning, with server-backed verification and documented metadata
  egress; no post-install URL temporal model found.
- [Cisco Skill Scanner](https://github.com/cisco-ai-defense/skill-scanner): local
  static scanning plus optional cloud/LLM engines, JSON/SARIF/CI; no temporal
  history or acceptance workflow found.
- [NVIDIA SkillSpector](https://github.com/NVIDIA/skillspector): broad static and
  optional LLM skill scanning; early repository maturity; no temporal model found.
- [SchemaPin](https://schemapin.org/): P-256 signatures, domain discovery, TOFU
  pins, version binding, expiry/revocation and CI. Complementary publisher/content
  integrity, not arbitrary-reference discovery. Do not build another protocol.
- Fan et al., [“Skill Drift Is Contract Violation”](https://arxiv.org/abs/2605.10990),
  2026: abstract-only preprint describing environment-contract extraction and
  validation. Product capabilities are C, not demonstrated.
- [Skilldex](https://arxiv.org/abs/2604.16911): abstract-only preprint/registry
  neighbour; detailed capabilities remain Unverified.

## Normalized benchmark

Capability dimensions: RD reference discovery; TA transitive awareness; TO
temporal observation; LP local privacy; CI content integrity; PI publisher
identity; SS semantic safety; AM affected mapping; EP evidence portability; RS
review state; Dev developer/CI integration.

| Product | RD | TA | TO | LP | CI | PI | SS | AM | EP | RS | Dev |
|---|---|---|---|---|---|---|---|---|---|---|---|
| SkillWatch | D | D | D | D | D | NF | P | D | D | D | D |
| Microsoft APM | P | D | P | D | D | P | P | P | D | P | D |
| changedetection.io | NF | NF | D | P | D | NF | NF | NF | P | NF | P |
| Distill | NF | NF | D | P | P | NF | NF | NF | P | NF | NF |
| Visualping | NF | NF | D | NF | P | NF | P | NF | D | P | D |
| Snyk Agent Scan | D | P | NF | NF | P | NF | D | P | P | P | P |
| Cisco Skill Scanner | P | NF | NF | D | P | NF | D | NF | D | P | D |
| NVIDIA SkillSpector | P | NF | NF | P | P | NF | D | NF | D | NF | D |
| SchemaPin | NF | NF | P | D | D | D | NF | NF | D | P | D |
| Contract-drift preprint | C | C | C | C | C | NF | C | C | C | C | C |

Each row is supported by the corresponding official-source paragraph above; a
cell is no more specific than that paragraph. This remains a documentation
benchmark, not a clean-room performance test.

## Operational assessment — separate from evidence status

Directional rubric: setup/review burden is **lower**, **mixed**, or **higher**
relative to this use case; scaling/failure clarity is **strong**, **mixed**, or
**weak**. **Unknown** means the official material and issue sample do not support
a direction. These are reasoned assessments with the observation that would
settle them, not D/P capability grades.

| Product/class | Setup and review burden | Scaling and failure clarity | Evidence note / settling observation |
|---|---|---|---|
| SkillWatch | Higher: separate local install, schedule and review. | Mixed: deterministic exits/SARIF, but no fleet service. | Repository behavior; settle burden in clean pilot installs. |
| Microsoft APM | Lower when already adopted; otherwise unknown. | Strong organizational targets/CI; issue sample shows integrity/install edge cases. | Official quickstart/action plus fixed-window issue sample; clean install remains unrun. |
| changedetection.io / Visualping / Distill | Lower for generic watch setup, mixed for security review. | Strong hosted/browser operations for the first two; Distill detail unknown. | Official monitor docs; settle with account/container onboarding and identical-page task. |
| Snyk / Cisco / NVIDIA scanners | Lower inside an existing scan workflow; higher if added solely for temporal evidence. | Mixed: broad integrations, but issue samples report provider/output/failure-clarity risks. | Official READMEs plus sampled issues; defects not independently reproduced. |
| SchemaPin | Lower for signed-object verification, not applicable to arbitrary discovery. | Strong deterministic identity/integrity path; operational adoption unknown. | Official specification; settle with signed-skill workflow test. |
| Contract-drift research | Unknown. | Unknown. | Abstract-only preprint; requires full implementation and independent run. |

SkillWatch does not win every slice. APM owns packaging/governance; mature web
monitors own acquisition/rendering/noise operations; scanners own broad semantic
inspection; SchemaPin owns publisher identity; contract-drift research challenges
raw-diff actionability. The falsifiable differentiation is local URL-to-installed-
context mapping plus portable fetch/diff evidence and explicit human acceptance.
It is falsified if adjacent platforms add that workflow or partners find their
lockfile/monitor/scanner evidence sufficient.

No clean-room installs were run: meaningful Visualping/Distill tests require an
account; changedetection requires image/dependency retrieval; Snyk warns that MCP
scanning may execute configured commands. Official quickstarts were inspected,
but untrusted MCP configurations were not executed.
