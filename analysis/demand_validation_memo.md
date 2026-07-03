# Demand Validation Memo

**Date:** 2026-07-03
**Context:** DECISION.md condition 5 requires "evidence of at least minimal user demand" before publication. Current state: zero stars, zero forks, zero external users. Repository is private.

## Options

### Option 1: Make the repository public and wait

**Effort:** 5 minutes (change visibility setting).
**Signal quality:** LOW. A public repository with zero organic discovery generates no signal. GitHub search rankings favour repositories with existing stars and activity.
**Downside:** Publishing to zero demand is the exact credibility risk DECISION.md warns against (R-01). If the repository sits public with zero stars for months, it becomes evidence against the project rather than for it.

### Option 2: Write a short technical post on the bait-and-switch attack vector, linking to SkillWatch

**Effort:** 2-4 hours (write, edit, publish on personal blog or TIL newsletter).
**Signal quality:** MEDIUM. If the post generates any traffic to the repository (stars, issues, clones beyond the author), that is a genuine demand signal. If it generates nothing, that is also a genuine signal -- indicating the attack vector does not concern the target audience enough to adopt tooling.
**Downside:** Requires making the repository public first. The post must be honest about SkillWatch's limitations (30-50% evasive recall, regex-only) to avoid credibility damage. Time investment is low enough that a null result is acceptable.

### Option 3: Post a "looking for feedback" thread in a relevant community

**Effort:** 30 minutes (write post, link to repository).
**Signal quality:** MEDIUM-HIGH. Direct feedback from practitioners (AI agent developers, MCP users) is the strongest signal available at zero budget. Relevant venues: Hacker News (Show HN), AI security Slack/Discord communities, MCP-related GitHub discussions.
**Downside:** Requires making the repository public. Reddit is not available (user is banned). Show HN has unpredictable timing -- a well-written post can get zero traction. Risk of harsh feedback if the tool is perceived as overpromising, but the honest documentation reduces this risk.

## Recommendation

No recommendation is made. This is a decision for the owner. All three options are low-effort and low-risk. The key constraint is that the repository must be made public before any demand signal can be obtained, which requires resolving Q-03 (public/private decision) first.

If the owner decides the project is not worth pursuing further, archiving with a clear README notice is a valid outcome. The code quality is high (233 tests, 94% coverage) and the honest documentation positions it well for revival if demand emerges later.
