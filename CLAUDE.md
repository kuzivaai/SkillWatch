# SkillWatch

Periodic URL content monitoring for AI agent skills and MCP tools.

## Quick commands

```bash
# Setup
python3 -m venv .venv && source .venv/bin/activate && pip install -e ".[dev]"

# Test
pytest --cov=skillwatch --cov-report=term-missing -q

# Lint
ruff check skillwatch/ tests/

# Build (no publish)
python3 -m build

# Efficacy measurement
python3 analysis/measure_efficacy.py
```

## Architecture

Nine Python modules under `skillwatch/`:

| Module | Purpose |
|---|---|
| cli.py | Argparse CLI, subcommand dispatch |
| parser.py | Extract URLs from SKILL.md, MCP configs, URL lists |
| fetcher.py | HTTP fetch with SSRF protection, DNS pinning, text extraction |
| detector.py | 13 heuristic flag codes, 32 prompt injection patterns |
| differ.py | Unified diff generation, content comparison |
| store.py | SQLite storage (urls, snapshots, alerts) |
| formatter.py | Terminal output formatting, ANSI colours |
| ssrf.py | SSRF validation, DNS pinning adapter |
| __init__.py | Version declaration |

## Settled constraints

These are closed findings from the five-prompt forensic audit. Do not re-litigate.

- **The regex triage is evadable by design.** Recall is 65% overall, 30% against evasive adversaries. This is documented honestly and is not a bug to fix. The tool is a URL change monitor with best-effort triage, not a detection tool.
- **"Periodic, not continuous."** The tool runs via cron or CI. It has no daemon mode, no schedule trigger, no unattended monitoring. All user-facing text uses "periodic" or "periodically." Do not introduce "continuous" or "continuously."
- **No ML or LLM detection.** The detector is regex/keyword/DOM-based. Proposals to add semantic detection are out of scope.
- **HOLD decision in force.** Not published to PyPI, no release tagged, no GitHub Pages enabled. See DECISION.md for the readiness bar.

## Conventions

- British English in all user-facing text
- Every code change ships with a test
- Do not overstate detection capability in any documentation change
- `severity_rank()` lives in `detector.py` and is the single source of truth for severity ordering
