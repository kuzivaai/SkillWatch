# Preserved material, 11 July 2026 (v0.3.0 era)

**Why this file exists.** This content was produced on 11 July 2026 as `.docx`
files whose generators were subsequently lost. From then until 29 July 2026 the
only copy lived in a handover file in a Windows Downloads folder, outside version
control — one deletion from gone. It is carried into the repository here so that
it survives. This closes item 25 of `OPEN-ITEMS.md`.

**Staleness warning.** Everything below dates from v0.3.0. Its efficacy figures
(75% recall, 50% evasive, 78.9% precision, "323 tests", "12 modules") are
**superseded**. Current figures are in `README.md` and reproduce via
`python3 analysis/measure_efficacy.py`. Several claims here breach the project's
own honesty rules and are flagged inline — they are preserved as a record of what
was written, not as statements the project now stands behind.

Content is reproduced faithfully. Editorial notes added during preservation are
marked **[2026-07-29]**.

---

## Code review (11 July 2026, v0.3.0)

Scope: all 12 modules then existing, the test suite, plus an empirical ReDoS
measurement. Verdict at the time: **no findings above LOW severity.**

**Strengths verified by reading the code:**

- SSRF denylist covers IPv4/IPv6 private, loopback, link-local (incl.
  169.254.169.254 cloud metadata), CGNAT, 6to4, NAT64; rejects
  credentials-in-URL and non-standard numeric hosts; unwraps IPv4-mapped IPv6.
- **DNS pinning done correctly** — DNS resolved once in `validate_url`; the
  resolved IP pinned for the TCP connection while Host header and TLS SNI keep
  the original hostname, closing DNS rebinding (TOCTOU) without breaking TLS.
- Redirects followed manually, each hop re-validated and re-pinned
  (`allow_redirects=False`).
- Does not trust server-declared encoding; streams with a 5 MB cap and 5-hop
  redirect cap; strips ANSI/VT escapes at fetch and display.
- User `--ignore-pattern` regexes run in a worker thread with a 2 s ReDoS timeout.
- Ledger: append-only, never pruned, JSON-canonicalised hashing, independent
  re-verification, offline anchoring.

| ID | Sev | Finding | Resolution |
|---|---|---|---|
| CR-1 | LOW | Built-in detection regexes ran on attacker-controlled text *without* the 2 s timeout user patterns get. **Measured:** no catastrophic backtracking — worst case ~0.8 s at 580 KB, ~linear (~1.3 ms/KB); a 5 MB page adds ~6–7 s. A slowdown, not a hang. | Fixed — 256 KB deterministic cap before all regex/library detection. |
| CR-2 | LOW | SSRF denylist omitted 240.0.0.0/4 (Class E) and 192.0.0.0/24 (IETF assignments). | Fixed — blocks on stdlib classification plus expanded explicit list. |
| CR-3 | LOW | Ledger grows unbounded by design; `verify`/`export` loaded all rows into memory. | Fixed — both stream from an ordered cursor (O(1) memory); atomic export. **Do NOT add naive pruning — it breaks the chain.** |
| CR-4 | INFO | Offline anchoring depended on the user publishing the head by hand. | Built beyond the fix — pluggable anchoring, `skillwatch anchor`, RFC 3161 extra, `anchors` table, `verify` auto-checks. Proven live: full-chain rewrite caught (DIVERGED, exit 1). |
| CR-5 | LOW | `docs/skillwatch-overview.js` stale. | Fixed at the time. **[2026-07-29] Went stale again and was corrected in v0.4.0 — ledger item 12, now closed.** |
| CR-6 | INFO | Inline `import sys` in `fetcher.py` warning branches. | Fixed — imports hoisted. |

**What that reviewer did NOT verify:** no fuzzer, no live DNS-rebinding harness
(SSRF review by reading and reasoning, not exploitation); denylist checked
against main risk ranges, not the full IANA registry; ReDoS measured on a handful
of inputs, no formal static backtracking analysis over all 32 patterns.

---

## Distribution research (11 July 2026)

**Base rates — arXiv:2511.04453**, "Launch-Day Diffusion", 138 HN→GitHub AI-tool
launches 2024–25 (42% Show HN):

- Front-page mean star gain: **+121 (24h) · +189 (48h) · +289 (7d)**
- **Median runs much lower** — a few virals inflate the average
- **"Show HN" tag: no statistically significant advantage** (β = −119, p = 0.39)
- Best window **12:00–17:00 UTC**; good timing worth ~200 stars
- Pre-launch signals explain ~half the variance (R² = 0.48)

> A later pass found a larger corpus — Daniel King, 188,085 Show HN posts, median
> **2 points**, 50 points = top 6%, ~1.4 stars/upvote, 92% of impact within 48h.
> **Plan for the median.** Sources disagree on timing (King: Monday 00:00 UTC;
> Kraishan: 12–17 UTC; older handover: Tue–Thu 1–4pm UK). Unresolved — a human
> should choose.

| Channel | Fit | Honest expected value |
|---|---|---|
| awesome-agent-skills-security | Best | Low traffic (~39★) but exact-topic + credibility. Do first. |
| Hacker News (Show HN) | High | Highest ceiling and variance. Front page is a minority outcome. |
| tl;dr sec | High | Clint Gibler, 90k+ readers, curated, no public submit form. |
| Security awesome-lists | High | Durable, evergreen. |
| PyCoder's Weekly | Medium | Broad Python reach, not security-targeted. |
| X / Twitter | Medium | One reshare can outperform HN. |
| LinkedIn | Medium | Credibility even at low volume. |
| Lobsters | Low now | Invite-only; self-promo <¼ of activity. |
| MCP server registries | **Poor — skip** | SkillWatch is **not** an MCP server. Off-category spam. |

| Horizon | Upper | Base case | Downside |
|---|---|---|---|
| Launch week | Front page + 100–300 stars | 20–60 stars | <10 stars — common, not a failure signal |
| Month 1 | 300–800 with a newsletter feature | 50–150 stars | Flat |
| Month 3 | ~1,000 with sustained promotion | 150–400 stars | Small but real user base |

**What to track:** stars are a vanity proxy. Weight PyPI installs, issues opened
by strangers, and unsolicited mentions above them.

---

## Launch checklist — human-only

**PyCoder's Weekly** (~2 min). <https://pycoders.com/submissions> → "Submit Your
Link" (Google form, sign-in required). URL:
`https://github.com/kuzivaai/SkillWatch`. Description:

> SkillWatch — a Python CLI that periodically re-checks the external URLs AI
> agent skills reference and flags suspicious changes, with a verifiable,
> externally-anchored content ledger. Apache-2.0, on PyPI.

**Show HN** (~10 min). Timing contested. <https://news.ycombinator.com/submit>.
Title:

> Show HN: SkillWatch – periodic monitor for what AI-skill URLs actually serve

Leave text empty; add a first comment **in your own words** — HN bans AI-written
posts. Draft as raw material only:

> I built this after seeing the "bait-and-switch" attacks on AI skills: a skill
> passes a security scan, then the URL it fetches its instructions from gets
> swapped for something malicious. Scanners check the skill once at install;
> nothing re-checks what those URLs serve afterwards.
>
> SkillWatch is a small CLI that periodically re-fetches those URLs and flags
> suspicious changes. Honest limits up front: the triage is regex-based —
> ~~about 75% recall (50% against attacks built to evade it), ~79% precision~~
> **[STALE. Current at v0.4.0: overall recall 21/35 (60.0%, 95% CI [43.6%,
> 74.4%]), evasive 11/25 (44.0%, [26.7%, 62.9%]), benign false-positive rate
> 4/32 (12.5%). The evasive figure splits by family: mechanical obfuscation 7/7,
> semantic framing 3/13, structural 0/3, non-English 1/2. Do not quote corpus
> precision as a deployment property — see the base-rate note in the README.]**
> It's a change monitor with best-effort triage, not a detector, and it
> complements scanners like Socket and Snyk rather than replacing them.
>
> The bit I'd most like feedback on is the verifiable ledger: every observation
> is hash-chained, and you can anchor the chain head externally (an RFC 3161
> timestamp or a git commit) so a later rewrite of the history is detectable. Is
> that independent-observer approach the right call versus the cooperation-model
> ideas (on-chain registries, signed manifests)?

**Do NOT ask anyone to upvote** — HN detects and penalises this.

**The two directory PRs.**
[#31](https://github.com/LLMSecurity/awesome-agent-skills-security/pull/31),
[#239](https://github.com/Puliczek/awesome-mcp-security/pull/239).
**[2026-07-29] Both still open, 18 days with no maintainer activity. Descriptions
refreshed with v0.4.0 figures and AST05 framing, and both nudged, on 2026-07-29.**

---

## Technical writeup draft (needs rewriting in the maintainer's voice)

Title: *The audit-runtime gap in AI agent skills — and keeping a record you can
verify*

**The gap.** A skill is reviewed once at install. Scanners check shipped code and
descriptions. But a skill often tells the agent to fetch instructions from a URL
at runtime, and that page can change after review.

**Evidence cited** (all REPORTED-UNVERIFIED): AIR's June 2026 demonstration
<https://www.air.security/blog-posts/the-story-of-skills> — with the disclosure
that AIR published while launching a managed skill marketplace and its "26,000
agents" figure is self-reported and unaudited; CSA research note
<https://labs.cloudsecurityalliance.org/research/csa-research-note-skill-md-agent-context-poisoning-20260506/>;
ClawHavoc, 1,184 skills
<https://orca.security/resources/blog/ai-agent-skill-supply-chain-security/>;
SIGIL <https://arxiv.org/abs/2605.05274>; Socket re-scanning 60,000+ skills
<https://socket.dev/blog/socket-brings-supply-chain-security-to-skills>.

> **Do not reuse the arXiv 2508.12538 citation** — it is *MCPXkit*, an offensive
> toolkit.
>
> **[2026-07-29]** This warning was correct and was *not* being followed: the
> README cited 2508.12538 as corroboration for the bait-and-switch technique
> until v0.4.0. Checking the source found something stronger than "offensive
> toolkit" — its abstract does not document URL content swapping at all, so the
> citation did not support the claim it was attached to. Removed.

**The stance.** SIGIL and on-chain registries are *cooperation models*.
SkillWatch is the opposite: an independent outside observer that needs nobody's
permission and assumes the ecosystem will *not* cooperate.

**The ledger.** `chain_hash = sha256(prev_hash || entry_hash)`. Editing,
reordering or deleting any past entry breaks the chain from that point.
`skillwatch ledger --export` writes portable JSON that re-verifies with no
database access. The Wayback Machine records content over time but applies no
cryptographic seal.

**The honest limit.** A purely local chain does not stop an attacker with
database write access from recomputing the *whole* chain. So `verify` prints the
chain **head**, you publish it somewhere you do not control, and
`verify --against <head>` checks it is still in the chain. A full-chain rewrite
reports `DIVERGED`.

---

## Positioning and SWOT (11 July — with honesty flags)

**The agreed honest line:** the edge is *the combination* — an independent,
zero-cooperation observer of what referenced URLs actually serve, **plus** a
verifiable content ledger. Say **"a combination I haven't seen elsewhere"**,
never "the only tool".

**Competitive context.** Socket re-scans 60k+ skills on skills.sh; SkillFortify
and ClawSec (30k+ audited) do formal/pipeline scanning; **changedetection.io
(32k★) is a free generic substitute** for the core mechanic. Snyk could close the
gap in 3–6 months, Anthropic at platform level in 6–12.

**Market framing (all ESTIMATE, no published data):** TAM ~50–100k; SAM ~5–15k;
SOM 30–500 users in 3 months. Comparables: TheAuditor 547★/9 months, AgentArmor
90★, Agentsec 7★.

**Revenue: zero, by design.** Value is indirect. **This pipeline is explicitly
unverified** — no documented cases exist of a solo developer converting a free
security tool into consulting leads.

> **Claims in the original SWOT that breach the honesty rules (ledger item 11):**
>
> - "an independent, tamper-evident record **no competitor offers**"
> - "**No competitor found** covering this exact niche as of July 2026"
> - "**One of very few** free tools focused on URL content changes"
>
> These live in `COMPETITORS.md`, which is **not in the repository** (gitignored).
> A repo-wide grep confirms zero uniqueness claims on any published surface.
>
> **[2026-07-29]** Still true and still open. `COMPETITORS.md` remains gitignored
> and still carries these claims. It is the input to launch copy, so purging them
> must happen *before* launch assets are drafted, not after.

---

## Link appendix

- Base-rate study — <https://arxiv.org/abs/2511.04453>
- Show HN rules — <https://news.ycombinator.com/showhn.html>
- awesome-agent-skills-security — <https://github.com/LLMSecurity/awesome-agent-skills-security>
- awesome-mcp-security — <https://github.com/Puliczek/awesome-mcp-security>
- PyCoder's submit — <https://pycoders.com/submissions>
- tl;dr sec — <https://tldrsec.com>
- SIGIL (premise citation) — <https://arxiv.org/abs/2605.05274>
- CSA SKILL.md context poisoning — <https://labs.cloudsecurityalliance.org/research/csa-research-note-skill-md-agent-context-poisoning-20260506/>
- Orca ClawHavoc — <https://orca.security/resources/blog/ai-agent-skill-supply-chain-security/>
- RFC 3161 — <https://www.rfc-editor.org/rfc/rfc3161>
- CVE-2026-33753 (rfc3161-client) — <https://github.com/trailofbits/rfc3161-client/security/advisories/GHSA-3xxc-pwj6-jgrj>
- CVE-2025-52556 (rfc3161-client) — <https://github.com/trailofbits/rfc3161-client/security/advisories/GHSA-6qhv-4h7r-2g9m>
- CVE-2026-24049 (wheel) — <https://github.com/advisories/GHSA-8rrh-rw8j-w5fx>
- ATR upstream — <https://github.com/Agent-Threat-Rule/agent-threat-rules>
- OWASP Agentic Skills Top 10 — <https://owasp.org/www-project-agentic-skills-top-10/>
