# Launch facts

**Purpose.** The factual inputs for launch assets, in one place, each with its
source. This file deliberately contains **no drafted copy and nothing written in
the first person**. Anything posted under a real identity — Show HN, a newsletter
submission, a social post — has to be the maintainer's own words. Hacker News
bans AI-written posts outright.

Use this as the fact-check sheet you write *against*. If a sentence in a draft
asserts something that is not on this page with a source, it does not go out.

**Compiled:** 2026-07-29, against `main` and v0.4.0 on PyPI.

---

## 1. Current figures

Every figure carries a 95% Wilson confidence interval, because at these sample
sizes the point estimate alone is close to uninformative. Reproduce all of them
with `python3 analysis/measure_efficacy.py`.

**Original corpus** — 37 benign, 10 pattern-matching malicious, 32 evasive malicious:

| Metric | Value |
|---|---|
| Overall recall | 27/42 (64.3%, CI [49.2%, 77.0%]) |
| Evasive recall | 17/32 (53.1%, CI [36.4%, 69.1%]) |
| Benign false-positive rate | 6/37 (16.2%, CI [7.7%, 31.1%]) |
| Corpus precision | 27/33 (81.8%, CI [65.6%, 91.4%]) — **see §2 before quoting this** |

**Evasive recall by attack family** (sums to 17/32):

| Family | Caught |
|---|---|
| Mechanical obfuscation (ROT13, reversal, base64, zero-width, homoglyphs, spacing) | 7/7 |
| Structural (hidden in markup) | 6/10 |
| Semantic framing | 3/13 |
| Non-English instruction | 1/2 |

**Holdout corpus** — 18 items, 12 malicious (all evasive), 6 benign:

| Metric | Value |
|---|---|
| Overall recall | 9/12 (75.0%, CI [46.8%, 91.1%]) |
| Benign false-positive rate | 1/6 (16.7%, CI [3.0%, 56.4%]) |
| Corpus precision | 9/10 (90.0%, CI [59.6%, 98.2%]) |

**HTML corpus** — 12 items, DOM-level checks:

| Metric | Value |
|---|---|
| Precision | 6/6 (100.0%, CI [61.0%, 100.0%]) |
| Recall | 6/6 (100.0%, CI [61.0%, 100.0%]) |

Quote the interval, not the 100%. Six of six is consistent with a true rate as
low as 61%.

**These are synthetic corpora written by this project.** They are not real-world
data and were not reviewed by anyone outside it. That sentence belongs in any
asset that quotes the figures.

## 2. The base-rate warning — mandatory alongside any precision figure

Precision is `TP/(TP+FP)`. It depends on the benign:malicious ratio of the corpus
it was measured on — roughly 37:42 here. A real change stream is overwhelmingly
benign: most changes to a monitored URL are legitimate edits. A precision figure
measured near 1:1 does not transfer to a stream running at 1000:1.

**At a realistic base rate, most flags a user sees will be false positives.**

The transferable number is the benign false-positive rate: 6/37 (16.2%) on the
original corpus, 1/6 on the holdout. Lead with that. Never publish precision as
though it described what a user will experience.

**Which checks produce the false positives.** All seven across both benign corpora
(43 items) come from four checks that fire on the appearance of something:

| Flag | FPs |
|---|---|
| `new_exec_command` | 2/43 |
| `new_domains` | 2/43 |
| `hidden_content` | 2/43 |
| `new_base64` | 1/43 |
| `prompt_injection` | 0/43 |
| `credential_reference` | 0/43 |
| `unicode_homoglyph` | 0/43 |

Content checks produced 0/43 (CI [0.0%, 8.2%]). Deleting all four would zero the
corpus false positives and drop recall from 27/42 (64.3%) to 16/42 (38.1%).

## 2a. The real-page base rate — the first figure here that is not self-authored

201 pages, each referenced by a real `SKILL.md` sampled from 157 distinct public
repositories. None was written by this project and none carries a payload, so
every occurrence is a legitimate use. `python3 analysis/measure_base_rate.py`.

| Technique | Real pages carrying it | Flagged? |
|---|---|---|
| `aria-hidden` | 141/201 (70.1%) | no |
| HTML `hidden` attribute | 111/201 (55.2%) | **no — removed 0.4.1** |
| `display:none` | 103/201 (51.2%) | yes |
| `visibility:hidden` | 73/201 (36.3%) | yes |
| `opacity:0` | 11/201 (5.5%) | yes |
| `clip-path` sr-only | 10/201 (5.0%) | no |
| `font-size:0` | 3/201 (1.5%) | yes |
| zero box, clipped | 2/201 (1.0%) | yes |
| off-screen positioning | 1/201 (0.5%) | **no — removed 0.4.1** |
| `text-indent:-9999px` | 0/201 (0.0%) | no |

**This is a base rate, not a false-positive rate, and an asset must not present it
as one.** The concealment check is a delta check; a first fetch is a baseline that
runs no detection. The real-page false-positive rate is **not measured**: only 3 of
199 paired snapshots produced a text diff and none flagged, and `0/3` has a 95%
interval of [0.0%, 56.1%]. Snapshots were minutes apart; drift needs days. If an
asset needs a real-world false-positive number, there isn't one yet.

## 3. Claim inventory — every external claim, with its source

Nothing below may appear in an asset without the source beside it. Where a claim
is contested or conflicted, the caveat travels with it.

| Claim | Source | Caveat that must travel with it |
|---|---|---|
| Skills that fetch external content can be swapped after review | [OWASP AST05](https://owasp.org/www-project-agentic-skills-top-10/ast05.html) | OWASP project is early-stage, not a flagship standard; not an endorsement |
| Scanner bypass: ClawHub's detector, Cisco's `skill-scanner`, all three skills.sh scanners | [Trail of Bits, 3 Jun 2026](https://blog.trailofbits.com/2026/06/03/the-sorry-state-of-skill-distribution/) | Scope is **the scanners they tested**. "Less than an hour" is the time to conceive and implement **three of the four** attacks; the fourth took a few hours. Not reproduced by this project. |
| The audit-runtime gap as a research premise | [arXiv 2605.05274, SIGIL](https://arxiv.org/abs/2605.05274) | Preprint, not peer-reviewed. Proposes a *competing* cooperation model. Author affiliations unverified. |
| SKILL.md context poisoning | [CSA research note](https://labs.cloudsecurityalliance.org/research/csa-research-note-skill-md-agent-context-poisoning-20260506/) | Not independently traced by this project |
| ClawHavoc compromised 1,184 skills | [Orca](https://orca.security/resources/blog/ai-agent-skill-supply-chain-security/) | Vendor-reported |
| A malicious skill reached 26,000+ agents | [Air Security](https://www.air.security/blog-posts/the-story-of-skills) | **Self-reported and unaudited**, by a party that simultaneously launched a competing skill marketplace. Never state without that disclosure. |
| 17,822 of 142,836 live skills (12.4%, 6.7M installs) reference ≥1 external instruction source | Air Security, *The Circus of Skills*, cited in [OWASP AST05](https://owasp.org/www-project-agentic-skills-top-10/ast05.html) | Same conflict as above. A better-scoped number than the 26,000 figure, same provenance problem. |
| changedetection.io is a free general substitute for the core mechanic | [GitHub](https://github.com/dgtlmoon/changedetection.io) | ~32,500 stars, Apache-2.0, verified 2026-07-29. Far more mature than SkillWatch. |

**Retired citations — do not reuse.** arXiv 2508.12538 is MCPXKIT, an offensive
MCP toolkit; its abstract does not document URL content swapping and it never
supported the bait-and-switch claim it was attached to.

## 4. Positioning, as corrected

**OWASP AST05 — partial coverage, stated as partial.** The AST05 page lists six
preventive mitigations. SkillWatch covers one, part of two more, and none of the
other three:

| AST05 mitigation | SkillWatch |
|---|---|
| Pin and verify referenced content | partial — alerts on drift, does not refuse it |
| Prefer inlining over fetching | no |
| Allowlist permitted reference domains | no |
| Audit references transitively | no |
| Maintain fleet-wide visibility of referenced sources | yes |
| Rescan continuously | partial — this tool is **periodic**, not continuous, by design |

Never write that the AST05 mitigations "describe what this tool does."

**Against SIGIL.** SIGIL and on-chain registry proposals are *cooperation
models*: they require the ecosystem to adopt signing, registries, or verification
loaders. SkillWatch requires nobody's cooperation and assumes the ecosystem will
not provide any. That is a difference in approach, not a claim of superiority,
and SIGIL's approach would make this tool unnecessary if adopted.

**What the tool is.** A periodic URL change monitor with a tamper-evident ledger
and best-effort regex triage. The triage is evadable by design and documented as
such. The dependable mechanisms are change detection and the ledger, neither of
which depends on recognising a payload.

**What it is not.** Not real-time. Not a detector. Not a replacement for static
scanners. Not a guarantee.

## 5. Competitor position

See [docs/COMPETITORS.md](COMPETITORS.md), rewritten 2026-07-29.

The one thing that must not be forgotten: **this project makes no uniqueness
claim.** Not "the only tool", not "nobody else does this", not "first". Earlier
internal notes made all three and they were wrong — changedetection.io covers the
core mechanic and has roughly 32,500 stars.

## 6. Project facts

| Fact | Value |
|---|---|
| Version | v0.4.0, live on PyPI |
| Licence | Apache-2.0 |
| Python | 3.10–3.13, all four in CI |
| Install | `pip install skillwatch` |
| Tests | 404 passing, 96% line coverage |
| Telemetry | none; local-only, nothing transmitted except fetching the URLs you specify |
| Users | **none known as of 2026-07-29** — 0 stars, 0 forks, 0 external users |

## 7. Channels and expectations

Channel analysis and launch-day base rates are in
[docs/archive/2026-07-11-preserved-material.md](archive/2026-07-11-preserved-material.md).
The headline from that research, which should shape expectations rather than be
published: **plan for the median, not the mean.** Front-page outcomes are a
minority result and a few viral launches inflate every average. Sources disagree
on optimal timing and that disagreement is unresolved.

Two directory PRs are open and unmerged since 2026-07-11:
[#31](https://github.com/LLMSecurity/awesome-agent-skills-security/pull/31),
[#239](https://github.com/Puliczek/awesome-mcp-security/pull/239).

## 8. What is deliberately absent

No Show HN post. No newsletter blurb. No social copy. No first-person prose of
any kind.

Those are posted under a real name and must be written by the person whose name
is on them. The raw material — the technique, the honest limits, the ledger
question worth asking for feedback on — is in
`docs/archive/2026-07-11-preserved-material.md`, marked as raw material and
carrying a staleness warning on its figures. Rewrite, do not paste.
