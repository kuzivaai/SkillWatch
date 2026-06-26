# SkillWatch

Continuous URL content monitoring for AI skills and MCP tools.

Static scanners check skills once — at install time. But the URLs those skills reference can change afterwards. A skill that pointed to legitimate documentation yesterday can point to malicious instructions today.

SkillWatch monitors the **content at external URLs** referenced by your installed skills. It detects when that content changes and flags suspicious patterns like new download commands, script injection, or credential harvesting.

## The problem

In June 2026, security researchers demonstrated that a fake AI skill could bypass every major scanner (Cisco, NVIDIA, skills.sh) by keeping its own code clean while pointing to an external URL. After distribution, the URL's content was swapped from legitimate documentation to malicious instructions. Static scanners never re-checked.

Existing tools like [MCP-Scan](https://github.com/invariantlabs-ai/mcp-scan) monitor tool **descriptions** (metadata). SkillWatch monitors what those tools **point to** (URL content). They're complementary.

## Install

```bash
pip install git+https://github.com/kuzivaai/SkillWatch.git
```

Or from source:

```bash
git clone https://github.com/kuzivaai/SkillWatch.git
cd SkillWatch
pip install .
```

Requires Python 3.10+.

## Quick start

```bash
# Add URLs from a SKILL.md file
skillwatch add path/to/SKILL.md

# Or add a single URL
skillwatch add-url https://docs.example.com/setup

# Run a scan
skillwatch scan

# Check results
skillwatch list
skillwatch alerts
skillwatch alert 1
```

## How it works

1. **Parse** — Extracts URLs from SKILL.md files, MCP configs (.json/.yaml), or plain URL lists
2. **Fetch** — Downloads each URL and extracts the main text content (using [trafilatura](https://github.com/adbar/trafilatura))
3. **Hash** — Computes SHA-256 of the extracted text and stores it locally (SQLite)
4. **Compare** — On subsequent scans, detects content changes via hash comparison
5. **Detect** — Flags suspicious patterns in changed content:
   - New download/execution commands (`curl`, `pip install`, `eval()`, etc.)
   - New base64-encoded strings (potential obfuscated payloads)
   - New external domains referenced
   - Credential/secret keyword references
   - Major content deletions (>50%)
   - Suspicious HTML (`<script>` with eval/fetch, `<iframe>`)

## Automate with cron

Check every 4 hours:

```bash
crontab -e
# Add:
0 */4 * * * /path/to/skillwatch scan --quiet >> /var/log/skillwatch.log 2>&1
```

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

## Security

SkillWatch fetches arbitrary URLs, so it includes SSRF protection:

- Blocks private IPs (`10.x`, `172.16.x`, `192.168.x`), loopback, link-local, and cloud metadata endpoints
- Only allows `http://` and `https://` schemes
- Validates redirect targets at each hop
- Limits response size to 5 MB
- Strips ANSI escape sequences from fetched content
- All data stored locally in `~/.skillwatch/skillwatch.db` — nothing is sent externally

## What SkillWatch does NOT do

- Replace MCP-Scan or other static scanners (use both)
- Monitor tool descriptions or metadata (MCP-Scan does this)
- Guarantee detection of all attacks (sophisticated evasion exists)
- Provide real-time protection (it's periodic, not a proxy)

## Limitations

- **False positives**: A legitimate documentation update that adds a code example with `pip install` will trigger an alert. Review alerts manually.
- **Dynamic pages**: SPAs and heavily personalised pages may show false changes. trafilatura handles most documentation pages well but is not perfect.
- **Evasion**: An attacker who serves different content based on User-Agent can evade detection. This is a fundamental limitation of any HTTP-based monitoring approach.

## Development

```bash
git clone https://github.com/kuzivaai/SkillWatch.git
cd SkillWatch
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

## Licence

Apache 2.0
