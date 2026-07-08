# SkillWatch

Periodic URL content monitoring for AI agent skills and MCP tools, with best-effort content triage. Alerts when skill-referenced URLs change, and applies heuristic checks to flag suspicious patterns in the changed content. The triage is evadable and does not replace human review.

[![CI](https://github.com/kuzivaai/SkillWatch/actions/workflows/ci.yml/badge.svg)](https://github.com/kuzivaai/SkillWatch/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/github/license/kuzivaai/SkillWatch)](LICENSE)

## Why this exists

Static scanners check AI agent skills once, at install time. But the external URLs those skills reference can change afterwards. In June 2026, [security researchers demonstrated](https://www.air.security/blog-posts/the-story-of-skills) that a fake skill could bypass Cisco, NVIDIA, and skills.sh scanners by keeping its code clean while pointing to an external URL. After distribution, the URL content was swapped from legitimate documentation to malicious instructions. (Disclosure: AIR, which published this research, simultaneously launched a managed skill marketplace. Their headline claim of 26,000 AI agents indexed is self-reported and unaudited. The bait-and-switch technique is independently corroborated by the [CSA research note](https://labs.cloudsecurityalliance.org/research/csa-research-note-skill-md-agent-context-poisoning-20260506/) and [arxiv 2508.12538](https://arxiv.org/abs/2508.12538).)

The [ClawHavoc campaign](https://orca.security/resources/blog/ai-agent-skill-supply-chain-security/) compromised 1,184 skills using similar techniques. The [Cloud Security Alliance](https://labs.cloudsecurityalliance.org/research/csa-research-note-skill-md-agent-context-poisoning-20260506/) published a dedicated research note on SKILL.md context poisoning.

Existing tools like [Snyk Agent Scan](https://github.com/snyk/agent-scan) monitor tool descriptions and metadata. SkillWatch monitors what those tools **point to** — the actual content at external URLs. They are complementary.

## Install

```bash
git clone https://github.com/kuzivaai/SkillWatch.git
cd SkillWatch
pip install .
```

Requires Python 3.10+. Five dependencies, all Apache/MIT/BSD licensed.

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

1. **Parse** — Extracts URLs from SKILL.md files, MCP configs (.json/.yaml), or plain URL lists
2. **Fetch** — Downloads each URL with SSRF protection and DNS pinning, extracts text via [trafilatura](https://github.com/adbar/trafilatura)
3. **Hash** — Computes SHA-256 of the extracted text, stores locally in SQLite
4. **Compare** — On subsequent scans, detects content changes via hash comparison
5. **Triage** — Applies 13 heuristic pattern checks to changed content, with a pre-detection canonicalisation layer that decodes HTML comments, reversed text, and ROT13-encoded payloads before scanning. See [Measured detection rates](#measured-detection-rates) below for what it catches and what it misses.

| Pattern | Severity | What it catches |
|---|---|---|
| Exec commands | Critical | `curl`, `pip install`, `eval()`, `subprocess`, `powershell` |
| Prompt injection | Critical | 32 [ATR](https://github.com/Agent-Threat-Rule/agent-threat-rules)-derived patterns covering 7 languages + obfuscation, with pre-detection canonicalisation for HTML comments, reversed text, and ROT13 |
| Suspicious scripts | Critical | New `<script>` tags with eval/fetch/cookie access |
| Data URI embeds | Critical | `<iframe src="data:text/html;base64,...">` |
| Base64 strings | Warning | Obfuscated payloads (40+ character base64 blocks) |
| Credential keywords | Warning | New references to `api_key`, `token`, `password`, `.env` |
| New domains | Warning | URLs pointing to domains not in the original content |
| Unicode homoglyphs | Warning | Cyrillic/Greek characters via Unicode Consortium confusables database |
| Data URI payloads | Warning | `data:text/html` and `data:application/javascript` in text |
| Meta refresh | Warning | New `<meta http-equiv="refresh">` redirects |
| Major deletion | Warning | >50% of original content removed |
| Iframes | Warning | New `<iframe>` elements |
| Hidden content | Info | New elements with `display:none` or `visibility:hidden` |

All HTML-level checks are **diff-based** -- only newly introduced elements trigger alerts, avoiding false positives from pre-existing scripts or iframes.

Unicode homoglyph detection uses the [Unicode Consortium's official confusables database](https://github.com/vhf/confusable_homoglyphs) covering thousands of lookalike characters across all scripts.

### Measured detection rates

Measured against a 52-item synthetic corpus (32 benign, 10 pattern-matching adversarial, 10 deliberately evasive adversarial) and a separate 18-item holdout corpus (6 benign, 12 evasive adversarial) committed before detector changes.

**Original corpus (52 items):**

| Metric | Value |
|---|---|
| Precision | 78.9% (15/19) |
| Overall recall | 75.0% (15/20 malicious items detected) |
| Recall against evasive adversaries | 50.0% (5/10) |
| Benign false positives | 4/32 (12.5%) |

**Holdout corpus (18 items, committed before detector changes):**

| Metric | Value |
|---|---|
| Precision | 90.0% (9/10) |
| Overall recall | 75.0% (9/12 malicious items detected) |
| Recall against evasive adversaries | 75.0% (9/12) |
| Benign false positives | 1/6 (16.7%) |

**What the triage catches:** Payloads that use expected phrasings ("ignore all previous instructions"), cleartext shell commands (`curl`, `pip install`), ROT13-encoded commands, reversed text containing command words, and injection phrases hidden in HTML comments.

**What it misses (honest ceiling statement):** The regex engine cannot catch semantic evasions by design. The following evasion classes will consistently bypass detection regardless of pattern additions:

- **Indirect instruction:** "The AI should consider updating its approach to..." -- no imperative verb, no trigger word
- **Polite request framing:** "Would you mind helping me by..." -- no injection vocabulary
- **Narrative/story framing:** Instructions embedded in fictional stories -- regex cannot distinguish fiction from instruction
- **Academic/scientific framing:** "In this experiment, the model should..." -- indistinguishable from legitimate academic text
- **Multi-word gap evasion:** "Print the full contents of its system prompt" -- too many words between "print" and "system prompt" for a regex to span without unacceptable false positives

These are fundamental limitations of pattern matching. Detecting them would require semantic analysis (LLM-based or embedding-based), which is out of scope for this tool.

**False positives:** SRI integrity hashes (sha256-/sha384-/sha512- prefixed base64) are now structurally excluded. Remaining false positives come from pages with legitimate `pip install` instructions, new domain references, or base64-like strings in educational content.

These rates are from synthetic test data. Real-world rates may differ.

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
| `skillwatch history <url>` | Show change history for a URL |
| `skillwatch alerts` | Show unreviewed alerts |
| `skillwatch alert <id>` | Show alert details with diff |
| `skillwatch alert <id> --review` | Mark an alert as reviewed |

### Scan options

| Flag | Description |
|---|---|
| `--delay N` | Seconds between requests (default: 1.0) |
| `--timeout N` | Request timeout in seconds (default: 10) |
| `--quiet` | Only show changes and errors |
| `--output text\|json` | Output format: text (default) or JSON for piping to webhooks |
| `--preset docs` | Built-in ignore patterns for timestamps, UUIDs, build hashes |
| `--user-agent STRING` | Custom User-Agent for HTTP requests |
| `--ignore-pattern REGEX` | Strip matching text before hashing (repeatable) |
| `--db PATH` | Path to SQLite database |

`--db` works before or after the subcommand: `skillwatch --db /path scan` and `skillwatch scan --db /path` are equivalent.

## Security

SkillWatch fetches arbitrary URLs, so it includes defence-in-depth:

- **SSRF protection**: Blocks private IPs, loopback, link-local, cloud metadata endpoints
- **DNS pinning**: Resolves DNS once, pins the IP for the connection (prevents rebinding)
- **Per-hop redirect validation**: Each redirect target is SSRF-checked before following
- **Escape stripping**: ANSI/VT escape sequences removed at fetch and display time
- **Size limits**: 5 MB response limit, 5-hop redirect limit
- **Local storage only**: All data in `~/.skillwatch/skillwatch.db`, nothing sent externally

## Reducing false positives

```bash
# Strip ISO timestamps before hashing
skillwatch scan --ignore-pattern '\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}'

# Strip version strings
skillwatch scan --ignore-pattern 'v\d+\.\d+\.\d+'
```

## Limitations

- **False positives**: SRI integrity hashes and pure hex digests are now structurally excluded. Remaining false positives (12.5% in testing) come from pages with legitimate `pip install` instructions, new domain references, or base64-like strings in educational content. Review all alerts manually.
- **Evasion**: The content triage includes canonicalisation for ROT13, reversed text, and HTML comments, but is fundamentally regex-based. It misses semantic evasions: indirect instruction, polite request framing, narrative framing, and academic framing. Against deliberately evasive payloads, recall is 50% on the original corpus and 75% on a separate holdout set.
- **Dynamic pages**: SPAs and JS-rendered content may cause false changes. Use `--ignore-pattern`.
- **User-Agent**: Uses a standard browser User-Agent by default (configurable via `--user-agent`). IP-based cloaking, TLS fingerprinting, and JS-only rendering can still evade fetching entirely.

## What SkillWatch does NOT do

- Replace Snyk Agent Scan or other static scanners (use both)
- Monitor tool descriptions or metadata (Snyk Agent Scan does this)
- Guarantee detection of all attacks (overall recall is 75%; semantic evasions like indirect instruction and polite framing bypass detection by design)
- Provide real-time protection (it is periodic, not a proxy)
- Replace human review of alerts (precision is 78.9%; about 1 in 5 alerts is a false positive)

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

## Development

```bash
git clone https://github.com/kuzivaai/SkillWatch.git
cd SkillWatch
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

236 tests, 95% code coverage.

## Licence

Apache 2.0. See [LICENSE](LICENSE) for the full text. Copyright 2026 Kuziva Muzondo.
