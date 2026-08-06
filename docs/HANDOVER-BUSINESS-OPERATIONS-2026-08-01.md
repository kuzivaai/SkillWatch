# SkillWatch business and operations handover

> **SUPERSEDED:** This file is not the designated current handover.
> `docs/current-handover.txt` designates `HANDOVER-PILOT-READINESS-2026-08-01.md`,
> which is the authoritative continuation. What is preserved here is this file's
> own scope (the commercial and operations dossier) and not readiness authority:
> current readiness values are derived from `docs/readiness-status.json` and
> rendered in `SHIP-READINESS.md`, never from narrative prose here.

**Date:** 2026-08-01

**Audience:** a maintainer or reviewer with no session memory.

## Objective

Create an accurate, unbiased end-to-end business and operations dossier for
SkillWatch, explain technical terms in plain language, and preserve the actual
commercial and assurance boundaries.

## Actual result

Created and committed:

`docs/SKILLWATCH-BUSINESS-AND-OPERATIONS.md`

Commit:

`0218f33 Add objective SkillWatch business operations dossier`

The dossier covers product behavior, boundaries, evidence classifications,
users and buyers, pilot operations, commercial options, competitive position,
moat hypotheses, operating procedures, governance alignment, responsibilities,
decision rules, and a plain-language glossary.

It explicitly rejects unsupported claims of commercial readiness, autonomous
cross-user learning, comprehensive detection, prevention, superiority,
certification and a durable moat.

## Repository state at handover creation

Measured on 2026-08-01 19:23 UTC:

```text
branch: feat/archive-durability-and-strict-audit
HEAD: 0218f33613434a6cf8a2b5e02bcfafce4dc0bb9e
origin/main: 6c6ab215742b8d4913b9193a8df49e645f5cd060
upstream: 2d8c3321dee476dc34c237d3c6c93e81b97ac7b0
ahead/behind upstream: 0 1
working tree: clean
```

The business dossier commit is local and has not been pushed. No remote write,
PR edit, merge, release or publication was performed in this unit.

The branch is otherwise already pushed through `2d8c332`. The new documentation
commit is one local commit ahead of the remote tracking branch.

## Evidence classifications

### Demonstrated

- The repository contains the business and operations dossier.
- The dossier was committed as `0218f33`.
- The preceding candidate workflow passed its recorded clean-room verification:
  installation, valid URL acceptance, baseline scan, unchanged repeat, ledger
  verification/export, removal and rejected-input handling.
- The preceding assurance record reports 647 passing tests and 95.71% coverage.
- Ruff, mypy, readiness consistency, dependency floors, release claims, figure
  rules, capture verification and package build passed in the preceding unit.
- The dossier is byte-identical between the repository and Downloads copy.

### Unverified

- Human usability, trust, retention, demand and willingness to pay.
- A real participant changing a decision because of SkillWatch evidence.
- Superiority to generic monitors in a real workflow.
- A durable moat.
- Autonomous learning value; no such system exists in the current product.
- ISO/IEC 27001 certification, NIST conformity or OWASP SAMM maturity score.
- Current PR status after this local documentation commit.

The exact observations that would settle these claims are participant
installation and repeated-use records, before/after decisions, commercial
follow-through, an independent assurance assessment, or a fresh GitHub PR query.

### Contradicted or prohibited

- “Commercially ready” is not supported.
- “Learns from all users” is incompatible with the current no-telemetry,
  local-only product boundary.
- “Comprehensive detector” and “prevents prompt injection” are unsupported.
- Industry-framework alignment is not certification or compliance.

## Product and operating model

SkillWatch periodically fetches user-specified public URLs, stores a local
baseline, compares later observations, reports selected suspicious changes, and
maintains a hash-linked local ledger.

Its hard boundaries are local-only operation, no telemetry, no user-to-server
data channel, no ML/LLM detector, periodic rather than continuous operation,
and no requests beyond user-specified URLs.

The recommended posture is evidence-first HOLD: run a controlled design-partner
pilot, measure decision value, and do not build an integration until two
independent qualified participants request a concrete destination with a named
workflow owner.

The dossier defines three candidate profiles: agent-security reviewer,
skill/MCP maintainer, and assurance consultant. It distinguishes users from
buyers and defines qualification/disqualification criteria.

## Commercial decision

Primary hypothesis: temporal-assurance evidence inside an existing scanner, CI,
registry, ticket or approval workflow.

Secondary hypothesis: portable provenance and audit evidence.

Rejected primary route: generic standalone web monitoring, because mature
substitutes already provide hosted operations, rendering and filtering.

Potential compounding assets—organisation-specific context, accepted review
history, portable evidence, lawful real-drift corpus, workflow knowledge and
assurance reputation—remain hypotheses until actual use demonstrates them.

## Operations included

The dossier defines:

- release gates and protected-path review;
- defect severity and fail-before/mutation evidence;
- participant qualification and consent;
- support boundaries;
- data retention, withdrawal and deletion;
- pilot measurements and falsification criteria;
- responsibilities for maintainer, release, pilot, privacy and commercial work;
- plain-language definitions for baseline, provenance, ledger, SARIF, SSRF,
  Wilson bound, telemetry, SSDF, AI RMF, SAMM and ISO/IEC 27001.

## Standards references

The dossier records these as practice references, not certifications:

- NIST SP 800-218 SSDF 1.1: <https://csrc.nist.gov/pubs/sp/800/218/final>
- NIST AI Risk Management Framework: <https://www.nist.gov/itl/ai-risk-management-framework>
- OWASP SAMM: <https://owasp.org/www-project-samm/>
- ISO/IEC 27001:2022: <https://www.iso.org/standard/27001.html>

The sources support process recommendations. They do not establish demand,
effectiveness, superiority, certification or a moat.

## Verification of this unit

```text
git diff --check: pass
business dossier commit: 0218f33
working tree after commit: clean
```

The dossier is documentation-only; the preceding product assurance result was
not rerun solely because of this documentation commit. The last recorded full
suite remains 647 passed with 95.71% coverage.

## Downloads copy

Expected path:

`/mnt/c/Users/mkuzi/Downloads/SKILLWATCH-BUSINESS-AND-OPERATIONS.md`

The repository and Downloads copies were verified byte-identical with SHA-256:

`b0e5b39f72acac32a36c6c9b7532fc20887b957e9aff4cbe67e1439ef9cbb874`

This handover should be copied to the same Downloads folder after any later
change to the repository handover.

## Next action

The maintainer should decide whether to push the documentation commit, then run
the qualified pilot. No further product engineering is justified until pilot
behavior demonstrates a material unresolved problem or decision-changing value.

The organic-delta measurement remains a separate unit and must not be folded
into this business-documentation handover.
