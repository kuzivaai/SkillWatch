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

**Original corpus** — 32 benign, 10 pattern-matching malicious, 25 evasive malicious:

| Metric | Value |
|---|---|
| Overall recall | 21/35 (60.0%, CI [43.6%, 74.4%]) |
| Evasive recall | 11/25 (44.0%, CI [26.7%, 62.9%]) |
| Benign false-positive rate | 4/32 (12.5%, CI [5.0%, 28.1%]) |
| Corpus precision | 21/25 (84.0%, CI [65.3%, 93.6%]) — **see §2 before quoting this** |

**Evasive recall by attack family** (sums to 11/25):

| Family | Caught |
|---|---|
| Mechanical obfuscation (ROT13, reversal, base64, zero-width, homoglyphs, spacing) | 7/7 |
| Semantic framing | 3/13 |
| Structural (hidden in markup) | 0/3 |
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
it was measured on — roughly 38:47 here. A real change stream is overwhelmingly
benign: most changes to a monitored URL are legitimate edits. A precision figure
measured near 1:1 does not transfer to a stream running at 1000:1.

**At a realistic base rate, most flags a user sees will be false positives.**

The transferable number is the benign false-positive rate: 4/32 (12.5%) on the
original corpus, 1/6 on the holdout. Lead with that. Never publish precision as
though it described what a user will experience.

**Which checks produce the false positives.** All five across both benign corpora
(38 items) came from three delta checks:

| Flag | FPs |
|---|---|
| `new_exec_command` | 2/38 |
| `new_domains` | 2/38 |
| `new_base64` | 1/38 |
| `prompt_injection` | 0/38 |
| `credential_reference` | 0/38 |
| `unicode_homoglyph` | 0/38 |

Content checks produced 0/38 (CI [0.0%, 9.2%]). Deleting the three delta checks
would zero the corpus false positives and drop recall to 16/35 (45.7%).

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
