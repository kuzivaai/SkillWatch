# SkillWatch

SkillWatch watches the web pages that AI tools rely on, and tells you when something changes. It exists because those pages can be swapped to contain harmful instructions after the AI tool has already been reviewed and approved.

[![CI](https://github.com/kuzivaai/SkillWatch/actions/workflows/ci.yml/badge.svg)](https://github.com/kuzivaai/SkillWatch/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/skillwatch)](https://pypi.org/project/skillwatch/)
[![Python 3.10+](https://img.shields.io/pypi/pyversions/skillwatch)](https://pypi.org/project/skillwatch/)
[![License](https://img.shields.io/github/license/kuzivaai/SkillWatch)](LICENSE)

## Why this exists

AI tools pull in instructions from the internet. Security scanners check those tools when they are installed, but the external pages the tools point to can be changed afterwards. The scanners do not re-check.

In June 2026, [security researchers demonstrated](https://www.air.security/blog-posts/the-story-of-skills) that a fake AI skill could pass every major scanner by keeping its code clean while pointing to an external URL. After distribution, the URL content was swapped from legitimate documentation to malicious instructions. (Disclosure: AIR, which published this research, simultaneously launched a managed skill marketplace. Their headline claim of 26,000 AI agents indexed is self-reported and unaudited. The bait-and-switch technique is independently corroborated by the [CSA research note](https://labs.cloudsecurityalliance.org/research/csa-research-note-skill-md-agent-context-poisoning-20260506/) and by [arXiv 2605.05274](https://arxiv.org/abs/2605.05274) (SIGIL, "Sealing the Audit-Runtime Gap for LLM Skills"), a preprint. An earlier version of this README also cited arXiv 2508.12538; that paper is MCPXKIT, an offensive MCP toolkit whose abstract does not document URL content swapping, so it did not support the claim and has been removed.)

The [ClawHavoc campaign](https://orca.security/resources/blog/ai-agent-skill-supply-chain-security/) compromised 1,184 skills using similar techniques. The [Cloud Security Alliance](https://labs.cloudsecurityalliance.org/research/csa-research-note-skill-md-agent-context-poisoning-20260506/) published a dedicated research note on SKILL.md context poisoning.

Tools like [Snyk Agent Scan](https://github.com/snyk/agent-scan) check tool descriptions and metadata. SkillWatch checks what those tools **point to**: the actual content at external URLs. They cover different layers and work well together.

### Where this sits in the OWASP taxonomy

SkillWatch addresses part of **AST05 — Untrusted External Instructions** in the
[OWASP Agentic Skills Top 10](https://owasp.org/www-project-agentic-skills-top-10/)
(v1.0, 2026 Edition), the category covering skills that retrieve instructions
from external sources.

The [AST05 page](https://owasp.org/www-project-agentic-skills-top-10/ast05.html)
lists six preventive mitigations. SkillWatch addresses one of them and part of two
more; it does not address the other three. Their headings, quoted verbatim:

| OWASP AST05 mitigation | SkillWatch |
|---|---|
| 1. "Pin and verify referenced content" | **Partial.** Records a content hash and alerts on drift, but does not refuse drifted content — it is a monitor, not an enforcement point. |
| 2. "Prefer inlining over fetching" | **No.** A publishing-side control; nothing to do with this tool. |
| 3. "Allowlist permitted reference domains" | **No.** |
| 4. "Audit references transitively" | **No.** SkillWatch watches the URLs you give it and does not follow reference chains. |
| 5. "Maintain fleet-wide visibility of referenced sources" | **Yes.** This is what the URL inventory and `skillwatch sources` do. |
| 6. "Rescan continuously" | **Partial, and deliberately not as worded.** SkillWatch runs periodically via cron or CI. It has no daemon and no continuous mode, by design. |

Mitigation 6 is worth stating plainly rather than glossing: OWASP's word is
*continuously*, and this tool is *periodic*. An earlier version of this README
listed the mitigations as "source inventory, content pinning, repeated
rescanning" — that phrasing came from the compressed summary row on the project
index, not from the AST05 page, and it silently changed OWASP's "continuous" to
"repeated" to fit this project's own constraint. Both are corrected here.

**Read that with the right weight.** The Agentic Skills Top 10 is an
early-stage OWASP project in active development, not a flagship standard. At the
time of writing its own pages describe its status inconsistently (one as an
incubator initiative, one as a new project proposal), so check the current status
before repeating any maturity claim. An OWASP category describes a risk; it is
not an endorsement. Nothing here is OWASP-certified, OWASP-recommended, or
OWASP-reviewed.

**Trail of Bits on scanner bypass, stated as the source states it.** In
[The sorry state of skill distribution](https://blog.trailofbits.com/2026/06/03/the-sorry-state-of-skill-distribution/)
(Samuel Judson and Tjaden Hess, 3 June 2026), Trail of Bits report bypassing
ClawHub's malicious skill detector, Cisco's agent skill scanner, and all three
scanners integrated into skills.sh. Their words:

> "These were not advanced attacks: it took us less than an hour to conceive and
> implement three of the four malicious skills in
> trailofbits/overtly-malicious-skills, using standard tricks and rapid
> inspection of the scanner source code. The fourth malicious skill took a few
> hours, but only because the prompt injection required some trial and error."

Two things that get garbled when this is repeated, including by us. The **scope**
is the five scanners they tested, not every scanner that exists. The **hour**
is how long it took to build three of the four attacks — not how long it took to
bypass the scanners, and not all four attacks. OWASP's own incident timeline
compresses this to "every public skill scanner tested … is bypassed in under an
hour", and an earlier version of this README repeated that compression. It is
corrected above against the primary source.

This project has not reproduced Trail of Bits' work. It is cited because it
describes the category SkillWatch operates in, and it is why this README does not
claim the triage catches determined attackers — see [measured detection
rates](#measured-detection-rates). The dependable mechanism is change detection
and the tamper-evident ledger, neither of which depends on recognising the
payload.

**AST07 — Update Drift** is adjacent: it concerns version-pinning failure, where
SkillWatch watches content changing at a stable URL. Related, not the same
thing, and only claimed here as a partial fit.

## Who this is for

SkillWatch is a command-line tool for people who build, deploy, or review AI agent skills and MCP tools: developers, security engineers, and maintainers who are comfortable at a terminal. Using it means installing a Python package, running commands in a terminal, scheduling scans with cron or CI, and reading a diff to judge whether a change is malicious.

**It is not yet usable by a non-technical person.** There is no app or website. It runs in a terminal, and reading an alert takes some security judgement — on a real change stream, where nearly every change is a legitimate edit, expect most flags to be false alarms (see [the base-rate note](#precision-does-not-transfer-to-your-change-stream)). The plain-language explanations and the [Understanding your alerts](docs/UNDERSTANDING-ALERTS.md) guide help with that, but you still need a terminal and some manual review.

## Why trust SkillWatch

SkillWatch is built to be the boring, honest option in a crowded field.

- **It runs on your machine and sends nothing.** Everything lives in a local SQLite file, and the only network requests it makes are to the URLs you ask it to watch. It never uploads your skills, configs, or results. Platform scanners often upload your skill code to their servers to analyse it, which is a reasonable trade-off for their features but a different trust model.
- **It tells you what it misses.** It publishes its own measured detection *and* evasion rates and names the attacks that defeat it. A clean scan means "none of 13 checks matched", not "you're safe".
- **It's independent and open.** Apache 2.0, no paid tier, no telemetry, no platform to upsell. It complements scanners like Snyk Agent Scan, Cisco skill-scanner, Socket, and MCP-Scan rather than competing for your budget.

## Install

```bash
pip install skillwatch
```

Or install from source:

```bash
git clone https://github.com/kuzivaai/SkillWatch.git
cd SkillWatch
pip install .
```

Requires Python 3.10+. Five dependencies, all Apache/MIT/BSD licensed. Optional cryptographic anchoring (`pip install 'skillwatch[anchor]'`) adds `cryptography` (Apache-2.0/BSD) and `rfc3161-client` (Apache-2.0); the core install and all monitoring work without them.

## Quick start

```bash
# Add URLs from a SKILL.md file
skillwatch add path/to/SKILL.md

# Or add a single URL
skillwatch add-url https://docs.example.com/setup

# Run a scan
skillwatch scan

# Check results
skillwatch alerts
skillwatch alert 1
```

## How it works

1. **Extract URLs** from SKILL.md files, MCP configs (.json/.yaml), or plain URL lists.
2. **Fetch each page** with built-in protections against server-side request forgery (SSRF) and DNS rebinding. Text is extracted using [trafilatura](https://github.com/adbar/trafilatura).
3. **Take a fingerprint** (SHA-256 hash) of the extracted text and store it locally in a SQLite database.
4. **On the next scan, compare fingerprints.** If the hash has changed, the content has changed.
5. **Run 13 pattern checks** on the changed content to flag anything suspicious. Before checking, the tool decodes common obfuscation tricks (HTML comments containing hidden text, reversed text, ROT13 encoding) so that disguised payloads are checked in their readable form. See [Measured detection rates](#measured-detection-rates) for what it catches and what it misses.
6. **Record the observation** in an append-only, hash-chained ledger, so you keep a permanent, verifiable history of what each URL served and when. Verify it any time with `skillwatch verify`. See [Verifiable content ledger](#verifiable-content-ledger).

SkillWatch checks for 13 suspicious patterns across three severity levels. Each check only looks at content that was added since the last scan, so pre-existing scripts or iframes on a page will not trigger false alerts.

| Pattern | Severity | What it catches |
|---|---|---|
| Exec commands | Critical | `curl`, `pip install`, `eval()`, `subprocess`, `powershell` |
| Prompt injection | Critical | 32 patterns from the [Agent Threat Rules](https://github.com/Agent-Threat-Rule/agent-threat-rules) project, covering 7 languages plus obfuscation. Before checking, the tool decodes HTML comments, reversed text, and ROT13 encoding. |
| Suspicious scripts | Critical | New `<script>` tags with eval/fetch/cookie access |
| Data URI embeds | Critical | `<iframe src="data:text/html;base64,...">` |
| Base64 strings | Warning | Obfuscated payloads (40+ character base64 blocks) |
| Credential keywords | Warning | New references to `api_key`, `token`, `password`, `.env` |
| New domains | Warning | URLs pointing to domains not in the original content |
| Unicode lookalikes | Warning | Cyrillic/Greek characters that mimic Latin letters, detected via the [Unicode Consortium's confusables database](https://github.com/vhf/confusable_homoglyphs) |
| Data URI payloads | Warning | `data:text/html` and `data:application/javascript` in text |
| Meta refresh | Warning | New `<meta http-equiv="refresh">` redirects |
| Major deletion | Warning | More than 50% of original content removed |
| Iframes | Warning | New `<iframe>` elements |
| Hidden content | Info | New elements with an **inline** `style` attribute containing lower-case `display:none` or `visibility:hidden`. Narrow by design of the current implementation — see [what this check does not catch](#what-hidden_content-does-not-catch) |

### What `hidden_content` does not catch

This check is narrower than its name suggests, and the gap is worth stating
because **absence of the flag is not evidence that nothing is hidden**.

`_extract_hidden_texts()` inspects an element's own inline `style` attribute for
a lower-case `display:none` or `visibility:hidden`. Measured on 2026-07-29:

| Hiding technique | Flagged |
|---|---|
| `style="display:none"` / `display: none` | yes |
| `style="visibility:hidden"` | yes |
| `style="DISPLAY:NONE"` or `Display:None` | **no** — the pattern is case-sensitive |
| A rule in a `<style>` block, e.g. `.x{display:none}` | **no** |
| An external stylesheet | **no** |
| `hidden` attribute, `aria-hidden` | **no** |
| `position:absolute;left:-9999px` | **no** |
| `opacity:0`, `font-size:0`, `height:0;overflow:hidden` | **no** |
| `clip-path:inset(100%)`, `text-indent:-9999px` | **no** |

Stylesheet-based hiding is the largest of these in practice: real pages hide
content with a CSS class far more often than with an inline style.

This is an implementation gap, not the semantic ceiling described above, and it
is fixable. It is not fixed yet because widening the check changes detection and
forces a full efficacy re-measure, which has to be a separate change from any
measurement work to keep the comparison honest. Tracked in `PATTERNS.md` and
`OPEN-ITEMS.md`.

### Measured detection rates

**Treat the triage as decorative against semantic evasion.** An attacker who writes
their instruction as ordinary English — a polite request, a story, a changelog
entry — gets past it: 3 of 13 such payloads are caught. Mechanical obfuscation is
a different story and is caught reliably: 7 of 7 (ROT13, reversal, base64,
zero-width characters, homoglyphs, letter spacing). So the flags are worth
reading, but never treat their absence as safety. The tool's dependable value is
the change alert and the tamper-evident ledger; if a page you watch changes,
review the diff yourself.

That is a plain reading of the measurement, not modesty. Against evasive
payloads the tool catches **11 of 25**. Every proportion below is given as
`k/n (point estimate, 95% confidence interval)`, because at these sample sizes
the point estimate alone is close to uninformative — an earlier version of this
README reported "50.0%" from 5/10, a result equally consistent with a true rate
of a quarter or of three quarters.

These are synthetic corpora, not real-world data. They are in
`analysis/corpus/`; reproduce every figure with `python3 analysis/measure_efficacy.py`.

**Original corpus (67 items: 32 benign, 10 pattern-matching, 25 evasive):**

| Metric | Value |
|---|---|
| Precision | 21/25 (84.0%, 95% CI [65.3%, 93.6%]) |
| Overall recall | 21/35 (60.0%, 95% CI [43.6%, 74.4%]) |
| Recall against evasive attacks | 11/25 (44.0%, 95% CI [26.7%, 62.9%]) |
| Benign false positives | 4/32 (12.5%, 95% CI [5.0%, 28.1%]) |

**Holdout corpus (18 items, committed before any detector changes):**

| Metric | Value |
|---|---|
| Precision | 9/10 (90.0%, 95% CI [59.6%, 98.2%]) |
| Overall recall | 9/12 (75.0%, 95% CI [46.8%, 91.1%]) |
| Benign false positives | 1/6 (16.7%, 95% CI [3.0%, 56.4%]) |

The holdout corpus does not report a separate "evasive recall". All 12 of its
malicious items are evasive, so that figure would be the same 9/12 as overall
recall — one measurement printed twice, not two independent results. Earlier
versions of this README listed both.

**HTML corpus (12 items, DOM-level checks):**

| Metric | Value |
|---|---|
| Precision | 6/6 (100.0%, 95% CI [61.0%, 100.0%]) |
| Recall | 6/6 (100.0%, 95% CI [61.0%, 100.0%]) |
| Benign false positives | 0/6 (0.0%, 95% CI [0.0%, 39.0%]) |

Read that interval, not the 100%. Six of six is consistent with a true rate as low
as 61%. The DOM checks look strong and the corpus is too small to show it.

**Why the published figures moved between 0.3.0 and 0.4.0.** Version 0.3.0
reported overall recall 15/20 (75.0%) and evasive recall 5/10 (50.0%). This
release reports 21/35 (60.0%) and 11/25 (44.0%). Nothing regressed — the corpus
changed and the detector did not. `skillwatch/detector.py` is byte-identical
between the two releases (`git diff v0.3.0..HEAD -- skillwatch/detector.py` is
empty). Decomposed:

| Subset | 0.3.0 | 0.4.0 |
|---|---|---|
| Non-evasive malicious | 10/10 | 10/10 |
| Evasive malicious | 5/10 | 11/25 |
| Overall recall | 15/20 (75.0%) | 21/35 (60.0%) |
| Benign false positives | 4/32 | 4/32 |

Fifteen evasive items were added and six of them are caught. The headline recall
fell because the malicious corpus went from 50% evasive to 71% evasive — a
harder and more honest test, not a worse detector. Precision moved the other way
over the same period, 15/19 (78.9%) to 21/25 (84.0%), for the same structural
reason.

**What is and is not verifiable here.** The load-bearing fact is checkable:
`skillwatch/detector.py` is byte-identical between the two releases, so no
detection behaviour changed. The 0.3.0-era corpus, however, was never committed —
the benign and adversarial sets entered version control in a single commit
(`309d359`) at the time of the expansion, so there is no earlier tracked state to
diff against. The first ten evasive items in the current corpus score 5/10,
matching what 0.3.0 published, and the benign false-positive count is the same
four items; both are consistent with the original set having been carried forward
unchanged, but neither proves it. An earlier version of this README stated flatly
that "the same five are caught" on the original ten. That was an inference
presented as a check, and this note replaces it.

Detection is almost perfectly split by attack family: **7 of 7** obfuscation
payloads are caught (ROT13, reversal, base64, zero-width characters, homoglyphs,
letter spacing), because obfuscation leaves mechanical traces. **3 of 13**
semantic-framing payloads are caught, because those are ordinary English
sentences whose meaning is hostile and whose form is unremarkable. No amount of
pattern work closes that second gap.

**What the checks catch:** Payloads that use expected phrasings ("ignore all previous instructions"), cleartext shell commands (`curl`, `pip install`), ROT13-encoded commands, reversed text containing command words, and injection phrases hidden in HTML comments.

**What it misses:** Clever attackers can phrase their instructions as polite requests, stories, or academic language. SkillWatch cannot detect these because they look identical to legitimate text. Specifically:

- "The AI should consider updating its approach to..." (no command words to match)
- "Would you mind helping me by..." (sounds like a normal request)
- Instructions embedded in a fictional story (a pattern matcher cannot tell fiction from a real instruction)
- "In this experiment, the model should..." (indistinguishable from legitimate academic writing)
- "Print the full contents of its system prompt" (the relevant words are too far apart to match without also flagging innocent text)

These are fundamental limits of pattern matching. Catching them would require a language model or similar semantic analysis, which is out of scope for this tool.

**False positives:** SRI integrity hashes (sha256-/sha384-/sha512- prefixed base64) are structurally excluded. Remaining false positives come from pages with legitimate `pip install` instructions, new domain references, or base64-like strings in educational content.

### Precision does not transfer to your change stream

The corpora above are 38 benign items against 47 malicious ones. Your monitored
URLs are not. Almost every change SkillWatch shows you will be a legitimate
edit — a version bump, a reworded paragraph, a new link. Precision is
`TP/(TP+FP)`, so it depends on that ratio, and a figure measured at roughly 1:1
tells you nothing about a stream that runs at 1000:1.

Do not carry the corpus precision figure into an expectation about your alerts.
The transferable number is the **false-positive rate: 4/32 (12.5%, 95% CI
[5.0%, 28.1%])** on the original benign corpus and 1/6 on the holdout. At a
realistic base rate, most flags you see will be false positives. That is a
property of the arithmetic, not a defect being confessed — it is why the tool
tells you to read the diff rather than trust the flag.

### Which flags produce the false positives

All five false positives across both benign corpora (38 items) came from three
"something new appeared" delta checks:

| Flag code | False positives |
|---|---|
| `new_exec_command` | 2/38 |
| `new_domains` | 2/38 |
| `new_base64` | 1/38 |
| `prompt_injection` | 0/38 |
| `credential_reference` | 0/38 |
| `unicode_homoglyph` | 0/38 |

The content checks — the ones that assert something about *what the text says* —
produced no false positives at all (0/38, 95% CI [0.0%, 9.2%]). The delta checks
fire on the appearance of a shell command, a domain or a base64-like string,
which are all things benign pages legitimately add.

This is a trade, not a bug to be fixed. Those same three checks are the *only*
thing catching five evasive payloads in the corpus (E-04, E-05, E-09, E-10 via
`new_exec_command`/`new_domains`; E-19 via `new_base64`). Deleting all three
would take the corpus false-positive count to zero and precision to 16/16, and
drop overall recall from 21/35 (60.0%) to 16/35 (45.7%). They earn their place;
weight them accordingly when triaging.

## Automate with cron

```bash
# Check every 4 hours
0 */4 * * * /path/to/skillwatch scan --quiet >> /var/log/skillwatch.log 2>&1
```

SkillWatch exits with code 1 when alerts are created, making it easy to chain with notification tools.

### Scheduled monitoring with GitHub Actions

A ready-to-use GitHub Actions workflow is provided at [`examples/scheduled-monitoring.yml`](examples/scheduled-monitoring.yml). Copy it into your repository at `.github/workflows/skillwatch.yml` and adjust the cron expression and file paths. The workflow:

1. Runs on a configurable schedule (default: every 6 hours)
2. Installs SkillWatch and adds URLs from your SKILL.md or MCP config
3. Caches the SQLite database between runs so only changes trigger alerts
4. Creates a GitHub issue if suspicious content changes are detected

The workflow can also be triggered manually from the Actions tab.

## Commands

| Command | Description |
|---|---|
| `skillwatch add <file>` | Extract and monitor URLs from SKILL.md, .json, .yaml, or .txt |
| `skillwatch add-url <url>` | Monitor a single URL |
| `skillwatch remove <url>` | Stop monitoring a URL |
| `skillwatch scan` | Scan all URLs for content changes |
| `skillwatch list` | Show all monitored URLs and their status |
| `skillwatch sources` | Re-check tracked skill/config files for changes (definition drift) |
| `skillwatch history <url>` | Show change history for a URL |
| `skillwatch alerts` | Show unreviewed alerts |
| `skillwatch alert <id>` | Show alert details with diff |
| `skillwatch alert <id> --review` | Mark an alert as reviewed |
| `skillwatch verify` | Check the tamper-evident content ledger is intact; auto-check anchors |
| `skillwatch ledger` | Show or `--export` the verifiable record of what URLs served |
| `skillwatch anchor` | RFC 3161 timestamp the ledger head (optional `[anchor]` extra) |

### Scan options

| Flag | Description |
|---|---|
| `--delay N` | Seconds between requests (default: 1.0) |
| `--timeout N` | Request timeout in seconds (default: 10) |
| `--quiet` | Only show changes and errors |
| `--output text\|json\|sarif` | Output format: text (default), JSON for webhooks, or SARIF for GitHub Code Scanning |
| `--preset docs` | Built-in ignore patterns for timestamps, UUIDs, build hashes |
| `--user-agent STRING` | Custom User-Agent for HTTP requests |
| `--ignore-pattern REGEX` | Strip matching text before hashing (repeatable) |
| `--db PATH` | Path to SQLite database |

`--db` works before or after the subcommand: `skillwatch --db /path scan` and `skillwatch scan --db /path` are equivalent.

## Detecting skill-file changes (definition drift)

`skillwatch scan` watches the *content* at the URLs a skill points to. `skillwatch sources` watches the *skill files themselves*. When you `add` a SKILL.md or MCP config, its content hash and the set of URLs it references are recorded. Running `skillwatch sources` re-reads each tracked file and flags:

- the file was edited since it was added,
- a new URL reference appeared (a new external target to watch),
- a reference was removed.

New references are added to monitoring automatically, and the command exits `1` if anything changed, so it fits cron and CI. This is a local, offline check inspired by MCP-Scan's tool pinning, but aimed at the SKILL.md threat model rather than MCP tool descriptions.

## SARIF output for CI

`skillwatch scan --output sarif` emits SARIF 2.1.0, which GitHub Code Scanning ingests. SkillWatch's findings then appear in the Security tab alongside static scanners like Cisco skill-scanner and SkillTotal that also emit SARIF: different layers, one dashboard.

## Verifiable content ledger

Every scan records what each URL served as an append-only, hash-chained entry in a local ledger. Unlike the snapshot cache (which keeps the last 50 versions per URL to save disk), the ledger keeps a tiny hash entry for **every** observation, permanently. So you keep a complete, tamper-evident history of what a page served and when, even after the full content is pruned.

```bash
skillwatch verify                        # recompute the chain; print the head; auto-check anchors
skillwatch verify --against <head>       # confirm history up to a head you published earlier
skillwatch anchor                        # RFC 3161 timestamp the head (optional [anchor] extra)
skillwatch anchor --method git --repo .  # or commit the head to a git repo (no TSA, no extra)
skillwatch ledger                        # show recent entries
skillwatch ledger --export ledger.json   # portable record anyone can re-verify
```

`skillwatch verify` recomputes the whole chain. If any past entry was edited, reordered, or deleted, the recorded hashes no longer line up; `verify` names the first broken entry and exits `1`. An exported ledger re-verifies with the same public function (`skillwatch.ledger.verify_chain`) with no database access, so a third party can independently confirm a record you produce.

**What this does and does not give you (honest scope):**

- It **does** give you integrity and independent re-verification. Accidental corruption or a naive edit to the history is detected, and anyone can re-check an exported ledger without trusting your machine.
- On its own, a purely local chain is **not** tamper-*proof*: an attacker with write access to your database could rewrite an earlier entry and recompute the whole chain so that plain `verify` still passes. Nothing inside the chain pins its history.
- To close that gap, `verify` prints the chain **head** (which commits to the entire history). Two ways to anchor it: **(a) by hand, zero-dependency** — publish the head somewhere you do not control (a git commit, a public note) and re-check with `skillwatch verify --against <head>`; or **(b) automatically** — `pip install 'skillwatch[anchor]'` and run `skillwatch anchor`, which gets a signed [RFC 3161](https://www.rfc-editor.org/rfc/rfc3161) timestamp for the head from a public authority (freeTSA.org by default). `skillwatch verify` then auto-checks every recorded anchor, catching any rewrite of anchored history even after a full-chain recompute. Only a hash ever leaves your machine; the anchoring crypto is an optional extra, so the core stays offline. See [docs/LEDGER.md](docs/LEDGER.md).

See [docs/LEDGER.md](docs/LEDGER.md) for the exact hash construction, the anchoring workflow, and how to re-verify an export yourself.

## Security

SkillWatch fetches arbitrary URLs, so it includes several layers of protection:

- **SSRF protection**: Blocks requests to private IPs, loopback addresses, link-local ranges, and cloud metadata endpoints
- **DNS pinning**: Resolves DNS once and pins the IP for the connection, preventing DNS rebinding attacks
- **Redirect validation**: Each redirect target is checked before following
- **Escape stripping**: ANSI/VT escape sequences are removed when content is fetched and when it is displayed
- **Size limits**: 5 MB response limit, 5-hop redirect limit
- **Local storage only**: All data lives in `~/.skillwatch/skillwatch.db`. Nothing is sent externally.

## Reducing false positives

```bash
# Strip ISO timestamps before hashing
skillwatch scan --ignore-pattern '\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}'

# Strip version strings
skillwatch scan --ignore-pattern 'v\d+\.\d+\.\d+'
```

## Limitations

- **False positives**: About 1 in 8 safe pages (12.5% in testing) will trigger an alert. Common causes are pages with legitimate `pip install` instructions, new domain references, or base64-like strings in educational content. Review all alerts manually.
- **Evasion**: The checks include decoding for ROT13, reversed text, and HTML comments, but they are fundamentally pattern-based. Attacks phrased as polite requests, stories, or academic language will not be caught. Against deliberately evasive payloads the tool catches 11/25 (44.0%, 95% CI [26.7%, 62.9%]). That figure splits by attack family, and the families sum to the total: mechanical obfuscation 7/7, semantic framing 3/13, structural (hidden in markup) 0/3, non-English instruction 1/2. Treat the triage as decorative against semantic and structural evasion, and rely on the change alert there.
- **Dynamic pages**: Single-page applications and JavaScript-rendered content may cause false changes. Use `--ignore-pattern` to filter out dynamic elements.
- **Fetch limitations**: SkillWatch uses a standard browser User-Agent by default (configurable via `--user-agent`). Pages that cloak content by IP address, TLS fingerprint, or require JavaScript rendering can evade fetching entirely.

## What this tool is not

- A replacement for Snyk Agent Scan or other static scanners (use both)
- A scanner for tool descriptions or metadata (Snyk Agent Scan does this)
- A guarantee of catching all attacks (overall recall is 21/35, 60.0%; against evasive payloads 11/25, 44.0% — attacks phrased as polite requests or stories bypass detection by design)
- Real-time protection (it runs periodically, not as a proxy)
- A replacement for human review of alerts (see the base-rate warning below — on a
  real change stream, most flags you see will be false positives)

## Using SkillWatch alongside a static scanner

SkillWatch and static scanners like [Snyk Agent Scan](https://github.com/snyk/agent-scan) cover different attack surfaces. Use both for defence in depth.

```
┌─────────────────────┐     ┌──────────────────────┐
│  Static Scanner     │     │  SkillWatch           │
│  (e.g. Snyk)        │     │  (periodic monitor)   │
│                     │     │                       │
│  Checks at install: │     │  Checks over time:    │
│  - Tool code        │     │  - External URLs      │
│  - Metadata         │     │  - Referenced content  │
│  - Permissions      │     │  - Content changes     │
└─────────────────────┘     └──────────────────────┘
```

A typical CI workflow runs both:

```yaml
# .github/workflows/skill-security.yml
name: Skill Security
on:
  schedule:
    - cron: "0 */6 * * *"  # Every 6 hours
jobs:
  static-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npx @anthropic-ai/agent-scan .  # or your static scanner

  content-monitor:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: kuzivaai/SkillWatch@main
        with:
          files: SKILL.md
```

The static scanner catches malicious tool descriptions and code at install time. SkillWatch catches bait-and-switch attacks where URL content changes after the static scan passes.

## FAQ

**What is SkillWatch?**
A free, open-source Python CLI that watches the web pages your AI agent skills and MCP tools point to, and tells you when the content changes. It runs 13 pattern checks on what changed to flag anything suspicious, and stores everything locally in SQLite.

**How is it different from Snyk Agent Scan, Cisco skill-scanner, or MCP-Scan?**
Those check the code and descriptions inside AI tools at install time. SkillWatch checks the external web pages those tools point to, over time. Different layers. Use them together.

**What does it catch, and what does it miss?**
It catches cleartext shell commands, known prompt-injection phrasings (32 patterns across 7 languages), suspicious HTML, Unicode look-alike characters, and more, including some ROT13, reversed-text, and HTML-comment obfuscation. It misses attacks phrased as polite requests, stories, or academic language, because those look like normal text. Overall recall is 21/35 (60.0%), falling to 11/25 (44.0%) against deliberately evasive payloads; the benign false-positive rate is 4/32 (12.5%). Corpus precision is 21/25 (84.0%), but that figure depends on the corpus benign:malicious ratio and does not transfer to a real change stream, which is overwhelmingly benign — expect most flags you see to be false positives. That evasive figure splits by attack family: mechanical obfuscation 7/7, semantic framing 3/13, structural 0/3, non-English 1/2 — so treat the triage as decorative against semantic and structural evasion. Review every alert manually.

**Can non-technical people use it?**
Not yet. It is a terminal tool, and reading an alert takes some security judgement. The [Understanding your alerts](docs/UNDERSTANDING-ALERTS.md) guide helps, but a terminal and manual review are still required.

**Does it send my data anywhere?**
No. Everything runs on your machine and stores locally. It only fetches the URLs you ask it to watch.

**Is it on PyPI? Is it free?**
Yes to both. `pip install skillwatch`, Apache 2.0.

## Documentation

- [Understanding your alerts](docs/UNDERSTANDING-ALERTS.md): what each flag means and what to do, in plain language
- [Verifiable content ledger](docs/LEDGER.md): the hash-chain spec, `verify`, and how to re-verify an export yourself
- [Architecture](docs/ARCHITECTURE.md): how the pipeline fits together
- [Threat model](docs/THREAT-MODEL.md): SSRF, DoS, terminal injection, and privacy
- [Changelog](CHANGELOG.md): release history

## Development

```bash
git clone https://github.com/kuzivaai/SkillWatch.git
cd SkillWatch
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

326 tests, 95% code coverage.

## Licence

Apache 2.0. See [LICENSE](LICENSE) for the full text. Copyright 2026 Kuziva Muzondo.
