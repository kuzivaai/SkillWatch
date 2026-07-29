# Competitor comparison

**Status:** tracked and public as of 2026-07-29. Supersedes an untracked
`COMPETITORS.md` (dated 2026-06-26) which is deleted — see "What changed and why"
at the foot of this file.

**How to read this.** The tool-by-tool table below was compiled on 2026-06-26 by
reading vendor documentation. It has **not** been re-verified since, and no cell
in it was confirmed by running the tool. Treat it as a starting point for your
own evaluation, not as a tested comparison. Where a column says "NO", that means
*not documented as doing this on the date checked*.

---

## What SkillWatch does

SkillWatch re-fetches the external URLs an AI skill or MCP tool config points at,
hashes the content, alerts when it changes, and keeps a hash-chained ledger of
what it saw. Its threat model is the post-review content swap: the skill passes
review, the skill never changes, and the *page it points at* changes afterwards.

## What it does not claim

This project does not claim to be the only tool that does this, the first, or to
occupy a gap nobody else fills. Those claims require exhaustively checking every
tool that exists, which has not been done and realistically cannot be. Earlier
versions of this document made all three; they are removed.

**A free, general-purpose substitute for the core mechanic exists and is far more
widely used.** [changedetection.io](https://github.com/dgtlmoon/changedetection.io)
(Apache-2.0, ~32,500 GitHub stars, verified 2026-07-29) monitors arbitrary web
pages for content changes and notifies on them, with CSS/XPath/JSONPath
filtering. Anyone weighing SkillWatch should look at it first.

The honest differences, stated as differences rather than as advantages:

| | changedetection.io | SkillWatch |
|---|---|---|
| Monitors arbitrary URLs for change | yes | yes |
| Input format | URLs you enter | parses `SKILL.md`, MCP configs, URL lists |
| Triage of *what* changed | generic diff | 13 heuristic flags aimed at prompt injection, evadable by design |
| Tamper-evident ledger | no | hash-chained, externally anchorable (RFC 3161 or git) |
| Output for CI | notifications | SARIF, exit codes |
| Maturity | large user base, years of use | v0.4.0, no external users as of 2026-07-29 |

If you want general change monitoring, changedetection.io is the more mature
choice. SkillWatch is narrower: skill-file parsing, injection-oriented triage,
and a verifiable record.

---

## Tool-by-tool table (compiled 2026-06-26, not re-verified)

| Tool | Type | Free? | Monitors metadata? | Monitors URL content? | Runs unattended? |
|---|---|---|---|---|---|
| changedetection.io | Self-hosted monitor | Yes (Apache-2.0) | No | **Yes** | Yes |
| MCP-Scan / Snyk Agent Scan | CLI scanner + proxy | Yes (Apache-2.0) | Yes (tool pinning) | Not documented | Proxy mode only |
| Bitdefender AI Skills Checker | Browser tool | Yes | Yes (patterns) | Not documented | No |
| ESET AI Skills Checker | Browser tool | Yes | Yes (behavioural) | Not documented | Registry-side only |
| Repello AI SkillCheck | Browser tool | Yes | Yes | Not documented | No |
| Mondoo AI Skills Check | CLI | Free tier | Yes (SHA-256) | Not documented | Manual re-run |
| MCPSafe | Browser tool | Yes | Yes (multi-model) | Not documented | No |
| SkillScan.dev | API | Yes | Yes (patterns) | Not documented | No |
| NVIDIA SkillSpector | Static analyser | Yes (OSS) | Yes | Not documented | No |
| Cisco skill-scanner | Static analyser | Yes (OSS) | Yes (YARA + LLM) | Not documented | No |
| Enkrypt AI | Scanner + gateway | OSS gateway | Yes | Runtime traffic | Gateway only |
| Snyk Evo | Platform | Enterprise | Yes | Enterprise | Enterprise |
| Nightfall AI | Platform | Enterprise | Yes | Yes (enterprise) | Yes (enterprise) |
| Cisco DefenseClaw | Platform | Enterprise | Yes | Yes (enterprise) | Yes (enterprise) |
| Repello ARGUS | Platform | Enterprise | Yes | Yes (enterprise) | Yes (enterprise) |

Note on the last column: it was originally headed "Continuous?". SkillWatch is
**periodic** — cron or CI, no daemon — and the column is renamed so the table
does not imply otherwise about this tool by proximity.

## Nearest adjacent tool: MCP-Scan / Snyk Agent Scan

Complementary rather than competing, on the documentation available. MCP-Scan
checks tool descriptions and metadata; SkillWatch checks the content at the URLs
those tools reference. Running both covers both layers.

Snyk has the resources to add URL-content monitoring, and this project has no
means of preventing that. Any estimate of when is speculation and none is offered
here.

---

## What changed and why (2026-07-29)

The previous `COMPETITORS.md` was **untracked and gitignored**, which meant the
input to public launch copy sat outside version control with no review, no
history and no test coverage. That is the same failure mode as citing a source
without checking it: an unverified claim with a clear path to a public surface.

It also carried claims that breach this project's own honesty rules:

| Removed claim | Why |
|---|---|
| "14 tools investigated. None fills SkillWatch's specific gap." | An exhaustive negative over a market nobody enumerated. |
| "What SkillWatch does that nothing else does" | Same, as a section heading. |
| "none fetches and hashes the actual web page a skill points agents to" | False as written — changedetection.io does exactly this, and it was already known to this project by 11 July. |
| "VERIFIED — no existing free tool covers it" | The strongest breach of the three: an exhaustive negative tagged as verified. Nothing was verified; 14 tools were read about. |
| "it needs to be the FIRST tool" | Unfalsifiable priority claim, and irrelevant to a user. |

**Decision: track it, purged.** The alternative — delete it and keep the analysis
only in a private note — was rejected because the claims would then still exist,
still be uncheckable, and still feed launch copy, with the only change being that
nobody could see them. Tracking makes the document reviewable and puts it under
`tests/test_published_claims.py`.

The strategic framing that was in the old file (market sizing, "portfolio piece",
window estimates) is **not** carried over. It is opinion rather than evidence,
it is partly contradicted by the changedetection.io finding, and a version of it
is already preserved with honesty flags in
`docs/archive/2026-07-11-preserved-material.md`.

## Sources

- [changedetection.io](https://github.com/dgtlmoon/changedetection.io) — checked 2026-07-29
- [MCP-Scan](https://github.com/invariantlabs-ai/mcp-scan)
- [Stytch MCP-Scan deep-dive](https://stytch.com/blog/mcp-scan/)
- [NVIDIA SkillSpector](https://github.com/nvidia/skillspector)
- [Cisco skill-scanner](https://github.com/cisco-ai-defense/skill-scanner)
- [Akto — MCP security tools](https://www.akto.io/blog/mcp-security-tools)
- [Practical DevSecOps — MCP security tools](https://www.practical-devsecops.com/top-mcp-security-tools/)
