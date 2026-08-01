# Competitive benchmark — 2026-08-01

Use case: a security-conscious team approved an agent skill or MCP configuration
referencing mutable external instructions. It must learn what changed, affected
contexts, observed evidence, evidentiary limits, and whether a human accepted the
new state.

Labels: **D** demonstrated; **P** partially demonstrated; **C** claimed; **NF**
not found after the named official surfaces; **NA** not applicable. NF is not a
claim of absence.

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

Dimensions: RD reference discovery; TA transitive awareness; TO temporal
observation; LP local privacy; CI content integrity; PI publisher identity; SS
semantic safety; AM affected mapping; EP evidence portability; RS review state;
Dev developer/CI integration; Setup; Review; FC failure clarity; Scale; Burden.

| Product | RD | TA | TO | LP | CI | PI | SS | AM | EP | RS | Dev | Setup | Review | FC | Scale | Burden |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| SkillWatch | D | D | D | D | D | NF | P | D | D | D | D | P | P | D | P | D |
| Microsoft APM | P | D | P | D | D | P | P | P | D | P | D | P | P | D | D | P |
| changedetection.io | NF | NF | D | P | D | NF | NF | NF | P | NF | P | D | P | D | D | P |
| Distill | NF | NF | D | P | P | NF | NF | NF | P | NF | NF | D | P | P | D | P |
| Visualping | NF | NF | D | NF | P | NF | P | NF | D | P | D | D | P | D | D | P |
| Snyk Agent Scan | D | P | NF | NF | P | NF | D | P | P | P | P | P | P | D | D | P |
| Cisco Skill Scanner | P | NF | NF | D | P | NF | D | NF | D | P | D | P | P | D | P | P |
| NVIDIA SkillSpector | P | NF | NF | P | P | NF | D | NF | D | NF | D | P | P | P | NF | P |
| SchemaPin | NF | NF | P | D | D | D | NF | NF | D | P | D | P | D | D | P | P |
| Contract-drift preprint | C | C | C | C | C | NF | C | C | C | C | C | C | C | C | C | C |

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
