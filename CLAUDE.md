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

# Type check  (same scope as CI — the analysis/ list is DERIVED, not typed out,
# so a newly tracked module cannot escape the gate. tests/test_ci_scope.py
# asserts CI keeps deriving it.)
mypy skillwatch/ scripts/ $(git ls-files 'analysis/*.py')

# Published figures must match the harness (CI step + pre-release gate)
python3 scripts/figure_rules.py

# Dependency floor audit (security gate — must exit 0)
python3 scripts/audit_dependency_floors.py

# Verify the irreplaceable 2026-07-29 capture BEFORE anything relies on it.
# exit 0 all copies verified / 2 a copy is missing / 3 a copy is present but
# corrupt / 4 the manifest is unusable.
python3 analysis/verify_capture.py

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

Six tracked scripts under `scripts/`: `audit_dependency_floors.py`,
`check_published_claims.py`, `check_release_claims.py`, `claim_rules.py`,
`figure_rules.py`, `refresh_confusables.py`. This said "Two" until 2026-07-30,
which was stale from the moment the claims and figure checks landed. Regenerate it
with `git ls-files 'scripts/*.py'` rather than counting by hand; which of them are
gates is recorded in the gate table below, and `tests/test_gate_table.py` fails if
a new one is added without being classified.

Six tracked modules under `analysis/`: `build_realpage_corpus.py`,
`make_baseline.py`, `measure_base_rate.py`, `measure_efficacy.py`,
`run_delta_pass.py`, `verify_capture.py`. The efficacy harness is
`analysis/measure_efficacy.py`; the rest of `analysis/` except `corpus/` and these
tracked modules is gitignored.

## Settled constraints

These are closed findings from the five-prompt forensic audit. Do not re-litigate.

- **The regex triage is evadable by design.** Recall is 60.0% overall (21/35, CI [43.6%, 74.4%]) and 44.0% against evasive adversaries (11/25, CI [26.7%, 62.9%]). Semantic evasions (indirect instruction, polite framing, narrative framing) bypass detection by design. This is documented honestly and is not a bug to fix. The tool is a URL change monitor with best-effort triage, not a detection tool. The older 75%/50% figures were measured on a smaller corpus and are superseded.
- **"Periodic, not continuous."** The tool runs via cron or CI. It has no daemon mode, no schedule trigger, no unattended monitoring. All user-facing text uses "periodic" or "periodically." Do not introduce "continuous" or "continuously."
- **No ML or LLM detection.** The detector is regex/keyword/DOM-based. Proposals to add semantic detection are out of scope.
- **Published; demand condition still unmet.** PyPI serves 0.4.1 (2026-07-29); this repository declares 0.4.1 in `pyproject.toml`. GitHub Pages is live. Of the five readiness conditions, only user demand (condition 5) is unmet — and no engineering change moves it. Current scoreboard: SHIP-READINESS.md (DECISION.md is the superseded pre-remediation record). Open work is tracked in OPEN-ITEMS.md, which is the continuity ledger across sessions.
  <!-- Both version numbers above are checked, not trusted. The declared one is checked
  offline by tests/test_claude_md_currency.py against pyproject.toml; the published one
  is checked against the live index by scripts/check_published_claims.py. By hand:
      grep '^version' pyproject.toml
      python3 -c "import json,urllib.request; print(json.load(urllib.request.urlopen('https://pypi.org/pypi/skillwatch/json'))['info']['version'])"
  This sentence previously read "PyPI serves 0.3.0 (2026-07-11); main is 0.4.0" and
  BOTH halves were false as of 2026-07-30: PyPI had served 0.4.1 since 2026-07-29
  and main was 0.4.1. It briefed every session with a wrong fact for a day.
  The comment sat mid-bullet when first written, which broke the list item in two;
  moved to the end 2026-07-30. -->

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

### The 2026-07-29 real-page capture lives outside the repository

`analysis/corpus/realpage/DELTA-BASELINE.json` was derived from 56.2 MB of raw HTML
captured on 2026-07-29 (the containing `fetched_pages.json` is 60.0 MB / 59,968,045
bytes — the 56.2 MB is the sum of the page HTML itself). That HTML is **not committed**
and is **not in /tmp**.

**Run the verifier before anything relies on it:**

```bash
python3 analysis/verify_capture.py            # sample of per-page hashes
python3 analysis/verify_capture.py --all-pages # all 201
```

Exit codes are the contract, because the two failures need opposite responses:
`0` all recorded copies verified · `2` **MISSING** — a copy is absent, restore it *from*
a verified copy · `3` **CORRUPT** — a copy is present and wrong, do **not** restore the
others *from* it · `4` the manifest is unusable. `3` outranks `2` when both occur,
because reporting only the absence would invite restoring from the corrupt copy.

**Where every copy lives.** All three are recorded in
`analysis/corpus/realpage/CAPTURE-INTEGRITY.json` under `copies`, which is the single
registry — `run_delta_pass.py` derives its search path from it rather than keeping a
second list.

| Path | Medium | Survives | Dies with |
|---|---|---|---|
| `/home/mkuziva/.skillwatch-archive/realpage-2026-07-29/fetched_pages.json` | WSL2 ext4 (`/dev/sdd`), inside the VHDX on C: | — (primary) | `wsl --unregister`, distro reset, ext4/VHDX corruption, C: loss, Disk 0 failure |
| `/mnt/d/skillwatch-archive/realpage-2026-07-29/fetched_pages.json` | NTFS on D: (Disk 0 partition 5), outside the VHDX | VHDX loss, distro reset, **a C: reimage** | Disk 0 failure, an OEM recovery reformat of D:, machine loss |
| `/mnt/c/Users/mkuzi/skillwatch-archive/realpage-2026-07-29/fetched_pages.json` | NTFS on C: (Disk 0 partition 3), outside the VHDX | VHDX loss, distro reset, **a D: reformat** | C: loss, Disk 0 failure, machine loss |

**The independence is PARTIAL, and saying otherwise would be false.** Windows reports
exactly one physical disk on this machine — Disk 0, `RS1D0TSSD510`, NVMe, 1,024,209,543,168
bytes. C: is partition 3 and D: is partition 5 **of that same disk**, and the WSL2 ext4
filesystem is a VHDX file on C:. So all three copies share one physical device. What the
second and third copies do close is the largest real-world class for a WSL user:
anything destroying the ext4 filesystem or the VHDX leaves both NTFS copies untouched,
and a C: reimage leaves the D: copy untouched.

**Residual risk, unmitigated:** failure of Disk 0, and loss/theft/destruction of the
machine. Both take all three copies. Closing them needs an off-machine destination,
which is outside this project's local-only boundary (no user→server data channel; the
only outbound traffic is fetching user-specified URLs) and is therefore the user's
decision, not a session's. An OneDrive folder exists at `/mnt/c/Users/mkuzi/OneDrive`
and would close it, at the cost of pushing 56.2 MB of third-party HTML into a personal
cloud account. **Not done — flagged for the user.**

`analysis/run_delta_pass.py --rehearse --source capture` and
`analysis/make_baseline.py --source <path>` both depend on the capture, and both now
verify before loading: `--source capture` refuses a corrupt copy, and an explicit path
is verified if it is a recorded copy or else announced as `UNVERIFIED`. A verifier
nobody runs is the defect one level up from the one the copies fix.

**What the verifier cannot see.** It verifies the copies the manifest *records*. A copy
made and never recorded is invisible to it, and it cannot check the manifest against
itself — the manifest is the reference. Recording a new copy is therefore a committed,
reviewable manifest edit rather than a disk scan.

**Why it matters that this survives.** Two things become impossible without it:
re-verifying the baseline's derivation, and rehearsing against a source that
exercises the **text** checks. The committed `html_v1` corpus runs only the five HTML
checks, which is exactly why a corpus-only rehearsal could not see the
`old_text=None` defect that disabled `new_domains` and `major_deletion`.

**An empty locating result is a FAILED command, not an absence.** If a command meant
to find this file returns nothing, do not conclude it is gone. Widen the search —
different glob depths, different roots, search by filename — and report every attempt.
Concluding absence from a single unmatched pattern is how an irreplaceable artefact
gets written off while still sitting on disk.

If you are hunting for it in a scratchpad, the path is **four** levels deep:

```
/tmp/claude-<uid>/<project>/<session>/scratchpad/fetched_pages.json
/tmp/claude-1000/-home-mkuziva-skillwatch/*/scratchpad/fetched_pages.json
```

A **three**-level glob (`/tmp/claude-*/*/scratchpad`) matches nothing and makes a
present file look permanently lost. That near-miss actually happened on 2026-07-29 —
the brief's own locating glob was one level too shallow — and is ledger item 51.
`tests/test_verify_capture.py::test_the_four_level_scratchpad_glob_is_preserved`
asserts the depth stays at four.

### Figures are claims too

`scripts/claim_rules.py` checks **citations**. `scripts/figure_rules.py` checks
**figures**: every `k/n (p%)` on a published surface must be a proportion the
harness currently produces, and its percentage must match its own fraction.

The allowed set is **the harness's own stdout**, parsed — not a table of expected
values maintained beside it. A second copy of the figures is free to drift from
the first, which is the defect one level up. If the harness output format changes,
the parsed set collapses and the check fails closed rather than passing vacuously.

**Correspondence, not membership.** A published figure must match the metric it is
LABELLED with, not merely appear somewhere in the harness output. Set membership
cannot see a substitution: `evasive recall 27/42 (64.3%)` is a real, current,
arithmetically correct proportion — it is *overall* recall — so a membership check
passes it while the surface tells the reader something false. Both sides are
classified into metric families by the same keyword function and the families must
agree. Text *before* a figure wins over text after it, because a label almost always
precedes its number.

A figure naming no metric cannot be correspondence-checked. `scripts/figure_rules.py`
counts those and prints the coverage, so what the rule does not cover is stated
rather than implied.

**The fail-closed floor is per-command, and there is deliberately NO global floor.**
`MIN_PROPORTIONS_PER_COMMAND` gives each harness command its own minimum, and each
command's *own parse* is compared against its *own* minimum. Their sum is never
compared against anything.

This sentence previously said "the floor is their sum." That was wrong as of commit
`6c6ab21` and is corrected here on 2026-07-30. Two reasons the sum cannot be a
threshold. It double-counts: five proportions are produced by both commands, so the
sum (28) is not commensurable with the deduplicated distinct count (34). And it would
reject healthy output: efficacy 18 and base_rate 10 with eight overlapping meets both
minimums while the distinct set is 20, below 28 — and a gate that fails on healthy
output is a gate someone removes.

The history, since three documents disagreed about it:

- At `8d35321` a genuine global comparison did gate — `if len(allowed.pairs) < 20`, a
  hand-picked constant against an actual count of 34. Ledger item 47.
- At `fa49fc5` enforcement became per-command. `derived_floor()` still existed but its
  value was only ever **printed**, never compared. The misleading part from here on
  was the printed juxtaposition of "floor 28" beside "34 distinct".
- At `6c6ab21` `derived_floor()` was deleted and the print replaced with an explicit
  statement that the two numbers are not comparable.

So "a global floor check was removed" is true of `8d35321`→`fa49fc5`, and "no global
comparison ever gated" is true only from `fa49fc5` onwards. Both statements were in
the repository, unqualified, describing different eras as if they described the same
one.

The only global assertion left is that the reference set is non-empty, which cannot be
mistaken for a threshold. A count floor of any shape still cannot detect a parse
returning the WRONG proportions — scraping confidence-interval bounds as fractions
would keep every count high. Detecting that needs the parsed values compared against
an independently computed expectation.

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

### Every gate, and whether it has ever been seen to refuse anything

<!-- gate-table:rule -->
**A gate that is added or materially changed requires a negative control before it
is relied on.** Green is not evidence that a check works. Green is evidence that it
did not object today, and a check that has never objected is indistinguishable from
a check that cannot. Make it red on purpose, on a throwaway branch, against a
stimulus you named in advance; then record the result in the table below.

The rule exists because the shape keeps recurring. It has been logged six times
(items 17, 35, 36, 42/45, 16, 59), and the sixth was *created by the fix for the
fifth*: the commit that closed `lowest-direct` by running a negative control also
rewrote the `security` job, which then inherited the identical problem. Closing
instances one at a time is how a class survives. The table is what makes the class
checkable, and `tests/test_gate_table.py` fails if a job or script is added without
an entry.

Status is one of exactly three values. **RED OBSERVED** with a run URL or a pasted
exit code, **never observed red**, or **unknown**. If a gate's history cannot be
established from CI or from the repository, write `unknown`. Do not infer.
<!-- gate-table:rule-end -->

CI history below is **exhaustive, not sampled**: all 81 `ci.yml` runs and all 4
`publish.yml` runs that exist as of 2026-07-30 were inspected. `ci.yml` has 4
failures; `publish.yml` has none.

**The `Executable hash` column is what stops this table certifying a gate it has
not examined.** A name and a status record a gate's *identity*. They cannot notice
that a job was rewritten under the same name and silently kept its old verdict,
which is precisely what happened to `security` on 2026-07-30. Each job's row
therefore carries a digest of what that job actually executes, and
`tests/test_gate_table.py` fails when a job's current digest stops matching, with
the message that the gate changed materially and needs a fresh negative control.
The status must then be read as `unknown`, and a second test enforces that it
cannot say anything else while the hash is drifted.

**Do not update a drifted hash on its own.** That records that the change happened
and asserts nothing about whether the gate still refuses anything. Run the control,
then update the status, the evidence and the hash together.

**What the hash covers, and why it is not "`run:` lines only".** Hashing the whole
workflow *file* was considered earlier and rejected, correctly: it fires on comment
edits and gets switched off within a week. The obvious narrowing is to hash only
executable `run:` lines, mirroring `pip_audit_run_lines()` in
`tests/test_ci_scope.py`. **That narrowing is wrong here, and measurably so.** The
`publish` job has **zero** `run:` lines, so a run-lines-only digest for it is
`sha256("[]")` regardless of what the job does. It would be blind to:

- `needs: build` — the ordering that keeps a failed build from ever reaching PyPI,
  and the entire safety argument for the 2026-07-30 `build` control;
- `environment: pypi` and `permissions: id-token: write`;
- the pinned SHA of `pypa/gh-action-pypi-publish`.

A digest blind to all of that is the defect being closed, not a fix for it. So the
hash is over the **parsed job specification** with cosmetic keys removed. Parsing as
YAML drops comments, blank lines and trailing whitespace *inherently*, which is a
stronger normalisation than stripping them by regex, and it keeps step order
significant — correct, because step ordering is what isolated the pip-audit step
from the floor step in the `security` control.

**The hash also covers the workflow's `on:` block, and that was found by doing, not
by reasoning.** An earlier draft hashed the job specification alone. The build
negative control then added `workflow_dispatch:` to `publish.yml` to make an
otherwise unreachable workflow reachable, and the hash did not move, because `on:`
sits outside `jobs:`. A job's behaviour is not only what it runs but **when** it
runs: changing `ci.yml`'s `on:` from `[push, pull_request]` to `[push]` would stop
every pull request being gated at all while every job line stayed byte-identical.
A gate that no longer runs is not a gate. Both directions are asserted in
`tests/test_gate_table.py::test_the_trigger_block_is_part_of_every_job_hash`.

One trap worth knowing if you touch that code: under YAML 1.1 the bare key `on`
parses to the **boolean True**, not the string `"on"`. `data["on"]` returns nothing
on every workflow here, and a digest built on it would silently omit the trigger
from every hash. Both spellings are read.

`name:` on a job or a step deliberately does **not** move the hash: a rename changes
nothing that executes. The cost is real and is stated rather than hidden: the
evidence cells below quote step names, so a rename can leave the prose stale while
the hash stays green. That is a documentation problem, not a gate-behaviour one.

**Reasoned, not evidenced,** and recorded as such: no source was searched for or
found on how workflow-gate drift is detected elsewhere, because this is a
repository-specific accounting problem rather than a general one. The design rests
on one assumption — that behaviour is fully determined by the parsed job spec minus
display names. The observation that would overturn it is a job changing behaviour
with an unchanged spec, which composite actions and `${{ }}` expressions over
repository variables could both produce. It is cheap to reverse: delete one column
and three tests.

**Repository-side gates are NOT hashed**, and that hole is left open deliberately
rather than papered over. `scripts/*.py` can be rewritten under the same name and
keep their status, exactly as `security` did. A hash of the source text would fire
on comment edits, which is the rejected shape; the right instrument is a digest over
the parsed AST with docstrings stripped. Not built. See the ledger.

<!-- gate-table:start -->
| Gate | Kind | Executable hash | Ever observed red | Evidence |
|---|---|---|---|---|
| `test` | CI job (matrix 3.10-3.13) | `b96b822b258e` | RED OBSERVED | <https://github.com/kuzivaai/SkillWatch/actions/runs/30442289082> `test (3.13)`, 2026-07-29; also 30503588045 `test (3.11)` on a Dependabot ruff bump |
| `security` | CI job | `576042ed1d31` | RED OBSERVED | <https://github.com/kuzivaai/SkillWatch/actions/runs/30526422428>, 2026-07-30, PR #38 closed unmerged. Failed at step *Audit resolved dependencies (--strict, no skip flags)* on `jinja2 2.11.3`, reporting PYSEC-2026-1471/1473/1474/1475; the later floor step was `skipped` |
| `lowest-direct` | CI job (matrix 3.10-3.13) | `2496d1c17fbe` | RED OBSERVED | <https://github.com/kuzivaai/SkillWatch/actions/runs/30500657407>, 2026-07-29, all four legs. **Confounded**: see the note below |
| `build` | CI job (`publish.yml`) | `49bfdcbce0cf` | RED OBSERVED | <https://github.com/kuzivaai/SkillWatch/actions/runs/30530850014>, 2026-07-30, branch `throwaway/build-negative-control` (deleted). Failed at step *Build package*: `ERROR Failed to parse .../pyproject.toml: Expected '=' after a key in a key/value pair (at line 17, column 6)`, exit 1. `publish` reported `skipped` and never started |
| `publish` | CI job (`publish.yml`) | `a541d9bfaf8b` | never observed red | **Deliberately not controlled, and this is a maintainer decision, not an oversight.** A deliberate failure here risks an artefact reaching the real index. The 2026-07-30 build control confirmed the ordering that protects it (`needs: build`, no `if:`, so `publish` was `skipped` when `build` failed), but that observes the *guard*, not the job. The cheap next step is a dry run against **TestPyPI**, which needs no change to the real publish path. Ledger item 63 |
| `scripts/audit_dependency_floors.py` | repository gate | n/a (not a workflow job) | RED OBSERVED | 2026-07-30, `exit=1` on a temporary `jinja2>=2.11.3` floor: *"permits versions with: GHSA-cpwx-vrp4-4pq7, ... minimum safe floor: 3.1.6"*. Mutation reverted |
| `scripts/check_release_claims.py` | repository gate (pre-release) | n/a (not a workflow job) | RED OBSERVED | 2026-07-30, `exit=1` on both paths. Claims: *"Do not release. Correct the claims first."*, 4 violations, caught in README **and** in the freshly built sdist PKG-INFO. Figures: *"Do not release. Published figures disagree with the harness."* Mutations reverted |
| `scripts/check_published_claims.py` | repository report (never a gate) | n/a (not a workflow job) | RED OBSERVED | 2026-07-30, `exit=2` with PyPI unreachable: *"This check has NOT passed. A check that cannot inspect its subject has not verified anything."* It also exited non-zero on live content on 2026-07-29 (item 2), which is not re-observable now that 0.4.1 is correct |
| `scripts/figure_rules.py` | repository gate (also a CI step of `test`) | n/a (not a workflow job) | RED OBSERVED | 2026-07-30, `exit=1` on a relabelled README figure: *"[figure-mislabelled] README.md:235: 9/12 is published as false-positive-rate but the harness prints it as recall-overall."* Mutation reverted |
| `analysis/verify_capture.py` | repository gate | n/a (not a workflow job) | RED OBSERVED | 2026-07-30, `exit=2` MISSING on an absent path and `exit=3` CORRUPT on a wrong file; with both present, 3 outranked 2 as specified. Demonstrated via `--copy`, so no recorded copy was touched |<!-- gate-table:end -->

**The `lowest-direct` red is confounded, and counting it as clean evidence would
overstate it.** The floor chosen for that control (`pyyaml>=6.0`) tripped two
independent guards, so "all four legs red" is not four legs of matrix-specific
evidence. The 3.10 and 3.11 legs went red on
`tests/test_dependency_floors.py::test_load_bearing_floors_are_at_or_above_their_known_good_minimum`,
which any leg would have caught. Only **3.12 and 3.13** failed on the thing the
matrix uniquely exists to catch: `Failed to build pyyaml==6.0` /
`AttributeError: 'build_ext' object has no attribute 'cython_sources'`. Isolating
it fully needs a floor that is unbuildable but absent from the known-good-minimum
table.

**The `security` control was confounded too, and differently.** `jinja2==2.11.3`
is also rejected by `scripts/audit_dependency_floors.py`, so the stimulus was not
pip-audit-specific. Step ordering isolated it: pip-audit runs first, so the floor
step reported `skipped` and the red is attributable to the pip-audit step alone.
That is weaker than an unconfounded stimulus and stronger than the
`lowest-direct` case, where both guards actually ran.

<!-- gate-table:not-a-gate -->
Tracked scripts that are deliberately **not** gates. Listed rather than omitted, so
a new gate cannot arrive unclassified. Same shape as `NO_FLOOR_EXPECTED` in the
floor auditor: opting out is a written declaration with a reason.

- `scripts/claim_rules.py`: a rules module with no CLI entry point. It defines the
  rules; the three callers in the table above are what enforce them.
- `scripts/refresh_confusables.py`: a data-refresh utility, run by hand, with no
  pass/fail verdict over the repository.
- `analysis/measure_efficacy.py`: a measurement harness. Its stdout is the
  reference set `figure_rules.py` checks against, which makes it the subject of a
  gate rather than one.
- `analysis/measure_base_rate.py`: a measurement harness, as above.
- `analysis/build_realpage_corpus.py`: a corpus builder, run once to produce inputs.
- `analysis/make_baseline.py`: a baseline builder. It verifies its own output
  (201/201 content hashes) but issues no verdict over the repository.
- `analysis/run_delta_pass.py`: a measurement harness. Its date guard was observed
  refusing on 2026-07-30 (`exit=3`, *"REFUSING: today is 2026-07-30; this pass is
  scheduled for 2026-08-05 or later"*), but a scheduling guard is not a gate on the
  repository's correctness.
<!-- gate-table:not-a-gate-end -->

### The facts in this file are claims too

**Asked and answered on 2026-07-30: is there a cheap check for staleness in this
file, as `figure_rules.py` is for published proportions? Yes, and it is now in
place.** The question arose because the version sentence above was false in both
halves, and the same sentence had already gone stale once (ledger item 12).

It is cheap because it is the *same* fix as the figure check: stop keeping a second
copy of a fact, and derive the claim from the artefact it describes. It splits in
two along the line this repository already draws between a gate and a report.

| Claim | Derived from | Where checked | Blocking |
|---|---|---|---|
| "this repository declares X in `pyproject.toml`" | `pyproject.toml` | `tests/test_claude_md_currency.py` | yes, offline, in CI |
| "N Python modules under `skillwatch/`" | `git ls-files` | `tests/test_claude_md_currency.py` | yes |
| "N tracked scripts under `scripts/`", and each named | `git ls-files` | `tests/test_claude_md_currency.py` | yes |
| "N tracked modules under `analysis/`", and each named | `git ls-files` | `tests/test_claude_md_currency.py` | yes |
| "PyPI serves X (date)" | the live PyPI index | `scripts/check_published_claims.py` | **no, and must never be** |

The last row cannot be blocking, for the reason already recorded above: only a
release can make it true, so gating on it would deadlock exactly as gating on the
published-claims report would. It is a finding to act on.

Because those claims are now parsed, **their wording is load-bearing**. Write them
in the forms the checks expect (`this repository declares X.Y.Z in
\`pyproject.toml\``, `PyPI serves X.Y.Z (YYYY-MM-DD)`, `N tracked scripts under
\`scripts/\``) or the check fails closed rather than passing vacuously.

**What this does not cover, stated rather than implied.** Only mechanically
derivable facts. The prose claims here — that Pages is live, the AST05 positioning,
the base-rate reasoning, the boundary statements — are not checked by anything and
can go stale silently. That is a smaller version of the same hole and it stays open.

## Conventions

- British English in all user-facing text
- Every code change ships with a test
- Do not overstate detection capability in any documentation change
- `severity_rank()` lives in `detector.py` and is the single source of truth for severity ordering
- `FLAG_EXPLANATIONS` / `explain()` in `detector.py` are the single source of truth for user-facing alert wording; a test asserts every emitted flag code has a plain-language entry. The reader-facing guide is `docs/UNDERSTANDING-ALERTS.md`.
