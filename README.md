# SkillWatch

SkillWatch watches the web pages that AI tools rely on, and tells you when something changes. It exists because those pages can be swapped to contain harmful instructions after the AI tool has already been reviewed and approved.

[![CI](https://github.com/kuzivaai/SkillWatch/actions/workflows/ci.yml/badge.svg)](https://github.com/kuzivaai/SkillWatch/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/skillwatch)](https://pypi.org/project/skillwatch/)
[![Python 3.10+](https://img.shields.io/pypi/pyversions/skillwatch)](https://pypi.org/project/skillwatch/)
[![License](https://img.shields.io/github/license/kuzivaai/SkillWatch)](LICENSE)

## Why this exists

AI tools pull in instructions from the internet. Security scanners check those tools when they are installed, but the external pages the tools point to can be changed afterwards. The scanners do not re-check.

In June 2026, [security researchers demonstrated](https://www.air.security/blog-posts/the-story-of-skills) that a fake AI skill could pass every major scanner by keeping its code clean while pointing to an external URL. After distribution, the URL content was swapped from legitimate documentation to malicious instructions. (Disclosure: AIR, which published this research, simultaneously launched a managed skill marketplace. Their headline claim of 26,000 AI agents indexed is self-reported and unaudited. The bait-and-switch technique is independently corroborated by the [CSA research note](https://labs.cloudsecurityalliance.org/research/csa-research-note-skill-md-agent-context-poisoning-20260506/) and [arxiv 2508.12538](https://arxiv.org/abs/2508.12538).)

The [ClawHavoc campaign](https://orca.security/resources/blog/ai-agent-skill-supply-chain-security/) compromised 1,184 skills using similar techniques. The [Cloud Security Alliance](https://labs.cloudsecurityalliance.org/research/csa-research-note-skill-md-agent-context-poisoning-20260506/) published a dedicated research note on SKILL.md context poisoning.

Tools like [Snyk Agent Scan](https://github.com/snyk/agent-scan) check tool descriptions and metadata. SkillWatch checks what those tools **point to**: the actual content at external URLs. They cover different layers and work well together.

## Who this is for

SkillWatch is a command-line tool for people who build, deploy, or review AI agent skills and MCP tools: developers, security engineers, and maintainers who are comfortable at a terminal. Using it means installing a Python package, running commands in a terminal, scheduling scans with cron or CI, and reading a diff to judge whether a change is malicious.

**It is not yet usable by a non-technical person.** There is no app or website. It runs in a terminal, and reading an alert takes some security judgement (about 1 in 5 alerts is a false alarm). The plain-language explanations and the [Understanding your alerts](docs/UNDERSTANDING-ALERTS.md) guide help with that, but you still need a terminal and some manual review.

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

1. **Extract URLs** from SKILL.md files, MCP configs (.json/.yaml), or plain URL lists.
2. **Fetch each page** with built-in protections against server-side request forgery (SSRF) and DNS rebinding. Text is extracted using [trafilatura](https://github.com/adbar/trafilatura).
3. **Take a fingerprint** (SHA-256 hash) of the extracted text and store it locally in a SQLite database.
4. **On the next scan, compare fingerprints.** If the hash has changed, the content has changed.
5. **Run 13 pattern checks** on the changed content to flag anything suspicious. Before checking, the tool decodes common obfuscation tricks (HTML comments containing hidden text, reversed text, ROT13 encoding) so that disguised payloads are checked in their readable form. See [Measured detection rates](#measured-detection-rates) for what it catches and what it misses.

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
| Hidden content | Info | New elements with `display:none` or `visibility:hidden` |

### Measured detection rates

In testing, SkillWatch caught 75% of attacks overall, and 50% of attacks designed to avoid detection. It incorrectly flagged about 1 in 8 safe pages.

These numbers come from a synthetic test corpus, not real-world data.

**Original corpus (52 items: 32 benign, 10 pattern-matching, 10 evasive):**

| Metric | Value |
|---|---|
| Precision | 78.9% (15/19) |
| Overall recall | 75.0% (15/20 malicious items detected) |
| Recall against evasive attacks | 50.0% (5/10) |
| Benign false positives | 4/32 (12.5%) |

**Holdout corpus (18 items, committed before any detector changes):**

| Metric | Value |
|---|---|
| Precision | 90.0% (9/10) |
| Overall recall | 75.0% (9/12 malicious items detected) |
| Recall against evasive attacks | 75.0% (9/12) |
| Benign false positives | 1/6 (16.7%) |

**What the checks catch:** Payloads that use expected phrasings ("ignore all previous instructions"), cleartext shell commands (`curl`, `pip install`), ROT13-encoded commands, reversed text containing command words, and injection phrases hidden in HTML comments.

**What it misses:** Clever attackers can phrase their instructions as polite requests, stories, or academic language. SkillWatch cannot detect these because they look identical to legitimate text. Specifically:

- "The AI should consider updating its approach to..." (no command words to match)
- "Would you mind helping me by..." (sounds like a normal request)
- Instructions embedded in a fictional story (a pattern matcher cannot tell fiction from a real instruction)
- "In this experiment, the model should..." (indistinguishable from legitimate academic writing)
- "Print the full contents of its system prompt" (the relevant words are too far apart to match without also flagging innocent text)

These are fundamental limits of pattern matching. Catching them would require a language model or similar semantic analysis, which is out of scope for this tool.

**False positives:** SRI integrity hashes (sha256-/sha384-/sha512- prefixed base64) are structurally excluded. Remaining false positives come from pages with legitimate `pip install` instructions, new domain references, or base64-like strings in educational content.

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
- **Evasion**: The checks include decoding for ROT13, reversed text, and HTML comments, but they are fundamentally pattern-based. Attacks phrased as polite requests, stories, or academic language will not be caught. Against deliberately evasive payloads, detection is 50% on the original corpus and 75% on a separate holdout set.
- **Dynamic pages**: Single-page applications and JavaScript-rendered content may cause false changes. Use `--ignore-pattern` to filter out dynamic elements.
- **Fetch limitations**: SkillWatch uses a standard browser User-Agent by default (configurable via `--user-agent`). Pages that cloak content by IP address, TLS fingerprint, or require JavaScript rendering can evade fetching entirely.

## What this tool is not

- A replacement for Snyk Agent Scan or other static scanners (use both)
- A scanner for tool descriptions or metadata (Snyk Agent Scan does this)
- A guarantee of catching all attacks (overall recall is 75%; attacks phrased as polite requests or stories bypass detection by design)
- Real-time protection (it runs periodically, not as a proxy)
- A replacement for human review of alerts (precision is 78.9%; about 1 in 5 alerts is a false positive)

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
It catches cleartext shell commands, known prompt-injection phrasings (32 patterns across 7 languages), suspicious HTML, Unicode look-alike characters, and more, including some ROT13, reversed-text, and HTML-comment obfuscation. It misses attacks phrased as polite requests, stories, or academic language, because those look like normal text. Overall recall is 75% (50% against deliberately evasive attacks); precision is 78.9%. Review every alert manually.

**Can non-technical people use it?**
Not yet. It is a terminal tool, and reading an alert takes some security judgement. The [Understanding your alerts](docs/UNDERSTANDING-ALERTS.md) guide helps, but a terminal and manual review are still required.

**Does it send my data anywhere?**
No. Everything runs on your machine and stores locally. It only fetches the URLs you ask it to watch.

**Is it on PyPI? Is it free?**
Yes to both. `pip install skillwatch`, Apache 2.0.

## Documentation

- [Understanding your alerts](docs/UNDERSTANDING-ALERTS.md): what each flag means and what to do, in plain language
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

249 tests, 96% code coverage.

## Licence

Apache 2.0. See [LICENSE](LICENSE) for the full text. Copyright 2026 Kuziva Muzondo.
