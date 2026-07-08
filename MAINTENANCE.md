# Maintenance

## Owner

**Kuziva Muzondo** — sole contributor and maintainer.

## RATIFIED cadence

Ratified by Kuziva Muzondo on 2026-07-08.

### Quarterly pattern review

Every calendar quarter (January, April, July, October), review the 32
prompt injection patterns and any patterns added since the last review:

1. Check ATR (Agent Threat Rules) repository for new patterns
2. Check CSA, arxiv, and security advisory feeds for new MCP/skill attack techniques
3. Run `python3 analysis/measure_efficacy.py` against all corpora
4. Record any pattern additions, removals, or modifications in PATTERNS.md

### Mandatory efficacy re-run on detector changes

Any commit that modifies `skillwatch/detector.py` must:

1. Run the full efficacy harness before merging
2. Record before/after metrics in the commit message or PR description
3. Not regress precision below 75% or overall recall below 70%

### Dependency updates

- **Dependabot:** configured for weekly checks (already active)
- **confusable_homoglyphs data:** run `scripts/refresh_confusables.py`
  quarterly to check for Unicode confusables updates
- **pip-audit:** run before any release consideration

### Intake path for reported bypasses

If an external party reports a pattern bypass or false negative:

1. Open a GitHub issue tagged `bypass-report`
2. Add the bypass payload to the appropriate corpus (adversarial or holdout)
3. Assess whether a pattern fix is feasible without unacceptable FP increase
4. If fixed, re-run the efficacy harness and update PATTERNS.md
5. If not fixable (semantic evasion), document in the honest ceiling statement

### Deprecation and archival

If the project receives no external usage after 12 months from first
public release, consider archiving the repository with a notice in README.
