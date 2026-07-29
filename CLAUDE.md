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

# Type check
mypy skillwatch/

# Build (no publish)
python3 -m build

# Efficacy measurement
python3 analysis/measure_efficacy.py
```

## Architecture

Thirteen Python modules under `skillwatch/`:

| Module | Purpose |
|---|---|
| cli.py | Argparse CLI, subcommand dispatch (15 subcommands) |
| parser.py | Extract URLs from SKILL.md, MCP configs, URL lists |
| fetcher.py | HTTP fetch with SSRF protection, DNS pinning, text extraction |
| detector.py | 13 heuristic flag codes, 32 prompt injection patterns, canonicalisation (HTML comments, reversed text, ROT13), plain-language flag explanations |
| differ.py | Unified diff generation, content comparison |
| store.py | SQLite storage (7 tables: urls, snapshots, alerts, sources, ledger, anchors, flag_feedback) |
| formatter.py | Terminal output formatting, ANSI colours |
| ssrf.py | SSRF validation, DNS pinning adapter |
| sarif.py | SARIF 2.1.0 output for CI / GitHub Code Scanning |
| ledger.py | Append-only tamper-evident content ledger |
| anchoring.py | RFC 3161 timestamp anchoring (optional `anchor` extra) |
| cloak.py | Cloaking detection across fetch strategies |
| __init__.py | Version declaration |

Two tracked scripts under `scripts/`: `audit_dependency_floors.py`,
`refresh_confusables.py`. The efficacy harness is `analysis/measure_efficacy.py`
(tracked; the rest of `analysis/` except `corpus/` is gitignored).

## Settled constraints

These are closed findings from the five-prompt forensic audit. Do not re-litigate.

- **The regex triage is evadable by design.** Recall is 60.0% overall (21/35, CI [43.6%, 74.4%]) and 44.0% against evasive adversaries (11/25, CI [26.7%, 62.9%]). Semantic evasions (indirect instruction, polite framing, narrative framing) bypass detection by design. This is documented honestly and is not a bug to fix. The tool is a URL change monitor with best-effort triage, not a detection tool. The older 75%/50% figures were measured on a smaller corpus and are superseded.
- **"Periodic, not continuous."** The tool runs via cron or CI. It has no daemon mode, no schedule trigger, no unattended monitoring. All user-facing text uses "periodic" or "periodically." Do not introduce "continuous" or "continuously."
- **No ML or LLM detection.** The detector is regex/keyword/DOM-based. Proposals to add semantic detection are out of scope.
- **Published; demand condition still unmet.** PyPI serves 0.3.0 (2026-07-11); `main` is 0.4.0. GitHub Pages is live. Of the five readiness conditions, only user demand (condition 5) is unmet — and no engineering change moves it. Current scoreboard: SHIP-READINESS.md (DECISION.md is the superseded pre-remediation record). Open work is tracked in OPEN-ITEMS.md, which is the continuity ledger across sessions.
- **Precision is not a ship gate and must not be published as a deployment property.** It depends on the corpus benign:malicious ratio, which deployment does not share. The transferable figure is the benign false-positive rate. See SHIP-READINESS.md condition 2 for the arithmetic.
- **Positioning is OWASP AST05.** SkillWatch maps to AST05 "Untrusted External Instructions" in the OWASP Agentic Skills Top 10 (v1.0, 2026 Edition). That project is **early-stage, not a flagship standard**, and its own pages describe its status inconsistently (incubator vs new project proposal) — check the current status before repeating any maturity claim, and never imply endorsement. AST07 "Update Drift" is adjacent (version pinning) and may be cited only as a partial fit. The scanner-bypass finding in that document is **Trail of Bits'**, cited by OWASP, not OWASP's own — attribute it correctly.

## Conventions

- British English in all user-facing text
- Every code change ships with a test
- Do not overstate detection capability in any documentation change
- `severity_rank()` lives in `detector.py` and is the single source of truth for severity ordering
- `FLAG_EXPLANATIONS` / `explain()` in `detector.py` are the single source of truth for user-facing alert wording; a test asserts every emitted flag code has a plain-language entry. The reader-facing guide is `docs/UNDERSTANDING-ALERTS.md`.
