# SkillWatch

Continuous URL content monitoring for AI agent skills and MCP tools. Detects bait-and-switch attacks where skill-referenced URLs change from legitimate documentation to malicious instructions.

[![CI](https://github.com/kuzivaai/SkillWatch/actions/workflows/ci.yml/badge.svg)](https://github.com/kuzivaai/SkillWatch/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/skillwatch)](https://pypi.org/project/skillwatch/)
[![Python](https://img.shields.io/pypi/pyversions/skillwatch)](https://pypi.org/project/skillwatch/)
[![License](https://img.shields.io/github/license/kuzivaai/SkillWatch)](LICENSE)

## Why this exists

Static scanners check AI agent skills once, at install time. But the external URLs those skills reference can change afterwards. In June 2026, [security researchers demonstrated](https://www.air.security/blog-posts/the-story-of-skills) that a fake skill could bypass Cisco, NVIDIA, and skills.sh scanners by keeping its code clean while pointing to an external URL. After distribution, the URL content was swapped from legitimate documentation to malicious instructions.

The [ClawHavoc campaign](https://orca.security/resources/blog/ai-agent-skill-supply-chain-security/) compromised 1,184 skills using similar techniques. The [Cloud Security Alliance](https://labs.cloudsecurityalliance.org/research/csa-research-note-skill-md-agent-context-poisoning-20260506/) published a dedicated research note on SKILL.md context poisoning.

Existing tools like [Snyk Agent Scan](https://github.com/snyk/agent-scan) monitor tool descriptions and metadata. SkillWatch monitors what those tools **point to** — the actual content at external URLs. They are complementary.

## Install

```bash
pip install skillwatch
```

Or from source:

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
5. **Detect** — Analyses changes against 13 suspicious pattern detectors:

| Pattern | Severity | What it catches |
|---|---|---|
| Exec commands | Critical | `curl`, `pip install`, `eval()`, `subprocess`, `powershell` |
| Prompt injection | Critical | 32 ATR-derived patterns covering 7 languages + obfuscation (base64, zero-width, spaced letters) |
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

All HTML-level checks are **diff-based** — only newly introduced elements trigger alerts, avoiding false positives from pre-existing scripts or iframes.

Unicode homoglyph detection uses the [Unicode Consortium's official confusables database](https://github.com/vhf/confusable_homoglyphs) covering thousands of lookalike characters across all scripts.

## Automate with cron

```bash
# Check every 4 hours
0 */4 * * * /path/to/skillwatch scan --quiet >> /var/log/skillwatch.log 2>&1
```

SkillWatch exits with code 1 when alerts are created, making it easy to chain with notification tools.

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

- **False positives**: Legitimate docs updates that add `pip install` will trigger alerts. Review manually.
- **Dynamic pages**: SPAs and JS-rendered content may cause false changes. Use `--ignore-pattern`.
- **Evasion**: Uses a standard browser User-Agent by default (configurable via `--user-agent`). IP-based cloaking, TLS fingerprinting, and JS-only rendering can still evade detection.
- **Prompt injection**: Keyword-based detection catches common phrasing but not novel formulations or obfuscated injections (ROT13, emoji encoding).

## What SkillWatch does NOT do

- Replace Snyk Agent Scan or other static scanners (use both)
- Monitor tool descriptions or metadata (Snyk Agent Scan does this)
- Guarantee detection of all attacks (sophisticated evasion exists)
- Provide real-time protection (it is periodic, not a proxy)

## Development

```bash
git clone https://github.com/kuzivaai/SkillWatch.git
cd SkillWatch
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

185 tests, 94% code coverage.

## Licence

Apache 2.0
