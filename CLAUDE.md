# SkillWatch

Periodic URL content monitoring for AI agent skills and MCP tools.

## Quick commands

```bash
# Setup
python3 -m venv .venv && source .venv/bin/activate && pip install -e ".[dev]"

# Export this for the session. See "Bytecode caching" below — it is not optional
# when you are about to trust a before/after result.
export PYTHONDONTWRITEBYTECODE=1

# Test
pytest --cov=skillwatch --cov-report=term-missing -q

# Lint  (same scope as CI — analysis/ is evidence for published figures)
ruff check skillwatch/ tests/ scripts/ analysis/

# Type check  (same scope as CI)
mypy skillwatch/ scripts/ analysis/measure_efficacy.py \
     analysis/measure_base_rate.py analysis/build_realpage_corpus.py \
     analysis/run_delta_pass.py

# Published figures must match the harness (CI step + pre-release gate)
python3 scripts/figure_rules.py

# Dependency floor audit (security gate — must exit 0)
python3 scripts/audit_dependency_floors.py

# Build (no publish)
python3 -m build

# Efficacy measurement
python3 analysis/measure_efficacy.py
```

### Bytecode caching

**Set `PYTHONDONTWRITEBYTECODE=1` before any run whose result you intend to
believe.** CI sets it at workflow level in `.github/workflows/ci.yml`; locally it
is on you.

CPython decides a cached `.pyc` is still valid by comparing the source file's
**mtime and size** against the header stored in the cache. mtime has whole-second
granularity. So two edits within the same second that leave the file the same
size — changing `3` to `4`, flipping a comparison operator — are indistinguishable
from no edit, and Python silently runs the old bytecode.

This has produced a false result in this repository: a test was edited, re-run
inside the same second, and reported passing from pre-change bytecode. The
conclusion drawn — that the change was unnecessary — was wrong.

`find . -name __pycache__ -type d -exec rm -rf {} +` also works but protects only
the machine and the moment where someone remembers to run it. The environment
variable removes the failure mode rather than sweeping up after it.

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
- **Positioning is OWASP AST05, partially.** SkillWatch addresses AST05 "Untrusted External Instructions" in the OWASP Agentic Skills Top 10 (v1.0, 2026 Edition). Of the six preventive mitigations the AST05 page lists, SkillWatch covers one ("Maintain fleet-wide visibility of referenced sources") and part of two ("Pin and verify referenced content" — alerts on drift, does not refuse it; "Rescan continuously" — this tool is periodic by design and does **not** satisfy that mitigation as OWASP words it). It does not address the other three. Never write that the AST05 mitigations "describe what this tool does." That project is **early-stage, not a flagship standard**, and its own pages describe its status inconsistently (incubator vs new project proposal) — check the current status before repeating any maturity claim, and never imply endorsement. AST07 "Update Drift" is adjacent (version pinning) and may be cited only as a partial fit.

### Citing external findings on a public surface

An external finding quoted on any public surface — README, `docs/`, PyPI, a
pull-request body, launch copy — must carry **the source's own scope and
quantifier**. Not a downstream paraphrase of them, including OWASP's paraphrase
of someone else's work.

- Go to the primary source. If you found the claim in a secondary source that is
  itself citing a third party, fetch the third party. Secondary sources compress,
  and compression is where scope and quantifiers get lost.
- **Paste the source sentence verbatim into the commit message** so a later
  session can compare the surface text against the source without refetching.
- Attribute to whoever did the work, not to whoever you read it in.
- Never silently alter a quoted word to fit this project's constraints. If OWASP
  says "continuously" and this tool is periodic, say both.

Worked example of the failure this rule exists to prevent. Trail of Bits wrote
that it "took us less than an hour to conceive and implement three of the four
malicious skills". OWASP's incident timeline compressed that to "every public
skill scanner tested … is bypassed in under an hour" — moving the hour from
*building three of four attacks* to *bypassing scanners*, and dropping the fourth
attack that took a few hours. This README repeated OWASP's compression. Two hops,
two distortions, one public surface.

`tests/test_published_claims.py` enforces the mechanical half of this: a cited
finding on a public surface must be accompanied by a source URL.

### Figures are claims too

`scripts/claim_rules.py` checks **citations**. `scripts/figure_rules.py` checks
**figures**: every `k/n (p%)` on a published surface must be a proportion the
harness currently produces, and its percentage must match its own fraction.

The allowed set is **the harness's own stdout**, parsed — not a table of expected
values maintained beside it. A second copy of the figures is free to drift from
the first, which is the defect one level up. If the harness output format changes,
the parsed set collapses and the check fails closed rather than passing vacuously.

Historical and hypothetical figures are legitimate — release-to-release tables,
counterfactuals, dated review records. They are marked explicitly:

```
<!-- figures:exempt reason="0.3.0 to 0.4.1 release comparison" -->
| Overall recall | 15/20 (75.0%) | 21/35 (60.0%) | 27/42 (64.3%) |
<!-- figures:end -->
```

A `reason=` is required so a reviewer can audit the exemption; an unclosed region
is a violation rather than a silent exemption of the rest of the file. Find every
one with `git log -S "figures:exempt"`.

**Why this exists.** On 2026-07-29 the detector was rewritten and re-measured, and
six surfaces went on publishing the pre-rewrite numbers — a benign false-positive
rate of 4/32 (12.5%) where the harness produced 7/37 (18.9%). `SHIP-READINESS.md`
contradicted itself inside one file. **This is the fourth recurrence of one shape:
a check that reports green because what it should examine is out of its scope** —
after an unparseable specifier treated as satisfied, a guard that could not see the
published artefact, and a regex that could never match. When you add a check, ask
what it cannot see.

### The claims checks: one gate, one report, and why they cannot be merged

The rules live in **`scripts/claim_rules.py`** — one entry point,
`find_violations(text, source=...)`, taking arbitrary text. Three callers run the
same rules against three different subjects:

| Check | Subject | Role | Blocking? |
|---|---|---|---|
| `tests/test_published_claims.py` | repository files | CI | yes, in CI |
| **`scripts/check_release_claims.py`** | `README.md` + a freshly built sdist's `PKG-INFO` | **THE GATE** | **yes — run before every release** |
| `scripts/check_published_claims.py` | the live PyPI long description | **THE REPORT** | **no — never gate on it** |

**Why they cannot be the same check.** The gate asks *"is what we are about to
publish correct?"* — answerable, and true, before a release. The report asks *"is
what is currently published correct?"* — which nothing but a release can make
true. Gating a release on the report would deadlock: the live page stays stale
until you release, and you could not release until the live page stopped being
stale. Run the report on a schedule or after a release, never as a precondition
for one.

The report **exits non-zero when it cannot reach PyPI**, and says so. A check that
could not inspect its subject has not passed.

**Release procedure — the gate is a required step:**

```bash
python3 scripts/check_release_claims.py     # must exit 0. Do not release otherwise.
gh release create vX.Y.Z --title "vX.Y.Z" --notes-file <notes>
python3 scripts/check_published_claims.py   # after the release; expect exit 0 once PyPI updates
```

**Why this exists.** On 2026-07-29 the repository corrected two misquoted external
claims and `tests/test_published_claims.py` went green — while the live PyPI page
carried both distortions for the rest of the day. The guard read four repository
paths and its own docstring said it "does not fetch anything", so the most public
surface this project has was outside its scope. Same fail-open shape as the
dependency auditor treating an unparseable specifier as satisfied: **a check that
passes because what it should examine is out of scope.**

**A rule that has never fired has not been tested.** One of the original negative
rules shipped vacuous — its span was `[^.\n]{0,60}` where the text it was written
to catch had 94 characters and a newline in that position, so it could never
match and passed against the very README it was meant to flag. Every negative
rule now has a positive fixture in `tests/test_claim_rules.py` proving it fires.
Add one for any rule you add.

## Conventions

- British English in all user-facing text
- Every code change ships with a test
- Do not overstate detection capability in any documentation change
- `severity_rank()` lives in `detector.py` and is the single source of truth for severity ordering
- `FLAG_EXPLANATIONS` / `explain()` in `detector.py` are the single source of truth for user-facing alert wording; a test asserts every emitted flag code has a plain-language entry. The reader-facing guide is `docs/UNDERSTANDING-ALERTS.md`.
