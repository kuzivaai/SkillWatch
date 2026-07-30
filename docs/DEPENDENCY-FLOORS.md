# Dependency floors

SkillWatch is a security tool, so it must not permit a resolution to a
known-vulnerable dependency. That is a stronger requirement than "our CI is
green", and it needs two separate checks plus one CI leg.

## Why `pip-audit` alone is not enough

`pip-audit` audits the versions **actually installed**. In CI those are the newest
versions a resolver will pick, so `pip-audit` says nothing about what your
declared ranges *permit*.

That gap shipped once. `rfc3161-client>=1.0` permitted every release affected by
CVE-2026-33753 — an authorisation bypass whose worked example impersonates
freeTSA, this project's default anchoring backend — while CI stayed green for
months, because CI always installed a fixed version.

A downstream user resolving against an older index, a lockfile, or a constrained
environment does not get the newest version. They get whatever the floor allows.

## The three checks

| Check | Question it answers | Where |
|---|---|---|
| `pip-audit --strict -r <resolved set>` | Do the versions we installed have advisories? | `security` job |
| `scripts/audit_dependency_floors.py` | Do the versions we *permit* have advisories? | `security` job |
| `uv run --resolution lowest-direct` | Do the versions we permit actually work? | `lowest-direct` job |

## `pip-audit --strict`: settled 2026-07-30

For five sessions the ledger carried this as open, with two claims: that `--strict`
cannot pass **in the invocation shape CI used**, and — untested — that it can
**never** pass. The untested claim was tested on 2026-07-30. **It is false.**

The shape that works exports a resolved requirements file that excludes the project
itself, and audits that file:

```bash
pip install -e ".[dev]"
pip freeze --exclude-editable > requirements-audit.txt   # drops the editable project
python -m venv /tmp/auditenv && /tmp/auditenv/bin/pip install pip-audit
/tmp/auditenv/bin/pip-audit --strict --desc -r requirements-audit.txt
```

Measured, on pip-audit 2.10.1, 47 packages:

| Shape | Project version | Result |
|---|---|---|
| env scan, `pip-audit --strict` | 0.4.1 (published) | **exit 0** |
| env scan, `pip-audit --strict` | 0.9.9 (unreleased) | **exit 1** — `skillwatch: Dependency not found on PyPI and could not be audited: skillwatch (0.9.9)` |
| `--strict -r <resolved>` | 0.4.1 | **exit 0** |
| `--strict -r <resolved>` | 0.9.9 | **exit 0** |

So the original reasoning was **right about the mechanism and wrong about today**.
The env-scan shape passes at the moment only because `main`'s version happens to
equal what PyPI serves; it would fail at the next pre-release version bump, exactly
as the old comment predicted. The `-r` shape is robust because the project is
excluded from the audited set outright, so whether its version is published stops
mattering.

**Adopted.** `--skip-editable` is gone — it was the skip that `--strict` rejects.

Why pip-audit is installed in a **separate** virtualenv: if it were installed
alongside the project, `pip freeze` would also capture *its* dependency tree
(cyclonedx, CacheControl, boolean.py, license-expression, …) and an advisory in the
auditing tool would fail this project's CI for something this project does not ship.

### The `security` job was observed refusing something, 2026-07-30

The shape above was adopted on the strength of measurement, but until 2026-07-30 it
had only ever been observed **green**. That is not evidence a gate works; it is
evidence it did not object. The same commit that closed the identical complaint for
`lowest-direct` (ledger item 16) created it here (item 59).

**Run <https://github.com/kuzivaai/SkillWatch/actions/runs/30526422428>**, PR
[#38](https://github.com/kuzivaai/SkillWatch/pull/38) titled "DO NOT MERGE", closed
unmerged (`mergedAt: null`), branch `throwaway/security-negative-control` deleted
locally and on the remote. `security` conclusion **failure**; all eight `test` and
`lowest-direct` legs **success**. Step conclusions:

```
success   Install dependencies
success   Export the resolved dependency set, excluding the project itself
success   Install pip-audit in an isolated environment
failure   Audit resolved dependencies (--strict, no skip flags)
skipped   Audit declared dependency floors
```

```
Found 4 known vulnerabilities in 1 package
jinja2 2.11.3  PYSEC-2026-1473  3.1.3
jinja2 2.11.3  PYSEC-2026-1471  3.1.6
jinja2 2.11.3  PYSEC-2026-1474  3.1.4
jinja2 2.11.3  PYSEC-2026-1475  3.1.5
##[error]Process completed with exit code 1.
```

**Route A was chosen over Route B, and the reasoning matters more than the result.**

The audited set is not a committed file. It is generated at CI time by `pip freeze`
into a gitignored `requirements-audit.txt`, so there is no requirements file in the
repository to add a vulnerable pin to. That left two routes:

| | What it does | What it exercises | What it misses |
|---|---|---|---|
| **A (chosen)** | vulnerable pin in `pyproject.toml` | the whole rewritten path: declaration, `pip install -e ".[dev]"`, `pip freeze --exclude-editable`, the `-r` shape, `--strict` | needs a `pyproject.toml` revert, proven by an empty `git diff main` |
| B | append a vulnerable line to `requirements-audit.txt` inside the workflow | the audit command only | never proves the *generation* path works, which is the part that was rewritten |

The class being closed is "a gate is changed and relied upon without anyone ever
observing it refuse anything". What was changed here was the generation path, so
only Route A observes the failure path of the thing that actually changed. Route B
would have produced a red run that says nothing about whether `pip freeze
--exclude-editable` captures what it is supposed to.

**The control was confounded, and counting it as clean would overstate it.**
`jinja2==2.11.3` is also rejected by `scripts/audit_dependency_floors.py`
(`exit=1`, *"minimum safe floor: 3.1.6"*), so the stimulus was not pip-audit
specific. Step ordering rescues the attribution rather than the choice of stimulus:
pip-audit runs first, so the floor step reported `skipped` and never executed. The
red is therefore attributable to the pip-audit step alone. This is weaker than an
unconfounded stimulus and stronger than the `lowest-direct` control, where both
guards actually ran. An unconfounded stimulus would need a dependency that
pip-audit flags on the *resolved* version while its declared floor stays clean,
which no straightforward pin provides.

**Nothing was left behind.** `git diff main -- pyproject.toml` is empty, `jinja2`
appears nowhere in the tree, and `main` is untouched at `6c6ab21`.

### The `build` job was observed refusing something, 2026-07-30

`publish.yml`'s `build` job had never been red across all four runs it had ever
had, and it guards the most public surface this project has.

**Run <https://github.com/kuzivaai/SkillWatch/actions/runs/30530850014>**, branch
`throwaway/build-negative-control` (deleted), head `1722028`. Stimulus: three lines
of invalid TOML in `pyproject.toml`.

```
build    failure
  success   Install build tools
  failure   Build package
  skipped   Run actions/upload-artifact@043fb46d...
publish  skipped        <- never started; no steps were even listed for it
```

```
* Creating isolated environment: venv+pip...
ERROR Failed to parse /home/runner/work/SkillWatch/SkillWatch/pyproject.toml:
      Expected '=' after a key in a key/value pair (at line 17, column 6)
##[error]Process completed with exit code 1.
```

`publish` was **skipped and never started**. That is `needs: build` with no `if:`,
the same ordering argument that isolated the pip-audit step from the floor step in
the `security` control. Nothing was published: PyPI still serves exactly four
releases, newest 0.4.1 from 2026-07-29.

**How the workflow was made to run, and a prediction that was wrong.**
`publish.yml` triggers only on `release: types: [published]`, so the job cannot be
exercised from a branch at all. Two temporary triggers were added on the throwaway
branch and removed with it: `workflow_dispatch:` and a `push:` trigger scoped to
that branch name.

The `push:` trigger was added as a fallback because `gh workflow run --ref` was
**predicted to fail**, on the understanding that GitHub requires a
`workflow_dispatch` trigger on the *default* branch. **That prediction was wrong.**
`gh workflow run publish.yml --ref throwaway/build-negative-control` exited 0 and
produced run 30530850014 with `event: workflow_dispatch`. The likely mechanism,
**reasoned and not verified against GitHub's documentation**: the workflow *file*
exists on the default branch, which is enough to resolve the workflow ID, and the
dispatch then runs the version at the given ref, which declares the trigger. The
observation that would settle it is dispatching a workflow whose file does not
exist on the default branch at all.

**Consequence: the `push:` trigger was unnecessary apparatus.** A later session
controlling `publish.yml` needs only `workflow_dispatch:` on the throwaway branch.

**A testability gap this exposed, logged in the ledger rather than fixed here.**
A workflow reachable only by publishing a real release cannot be exercised at all
without editing it, so every control against it changes the thing being controlled.
That is a weaker form of evidence than the `ci.yml` controls, where the trigger was
untouched, and it is stated rather than glossed.

### `--strict` is load-bearing: demonstrated 2026-07-30

For five sessions `--strict` was carried as a rule that had never been seen to fire,
and this document said so: *"no case was constructed in which `--strict` changed the
outcome of the `-r` shape"*. **That was true of the cases tried and false in
general.** A case exists, and it was found by reading pip-audit's source rather than
by guessing at inputs.

`--strict` turns any `SkippedDependency` into a fatal (`_cli.py:557`). The skip that
is reachable on *every* dependency source is `_service/pypi.py:85`: a package that
resolves but whose `(name, version)` **404s on PyPI**, so it cannot be audited at
all. Measured, pip-audit 2.10.1, against a locally built package deliberately absent
from PyPI (`pypi.org/pypi/skillwatch-strict-probe-does-not-exist/json` returns 404):

| Invocation | Exit | Output |
|---|---|---|
| `pip-audit --desc -r <file>` | **0** | `No known vulnerabilities found`, then a *Skip Reason* table naming the package. **It passes.** |
| `pip-audit --strict --desc -r <file>` | **1** | `ERROR: skillwatch-strict-probe-does-not-exist: Dependency not found on PyPI and could not be audited` |

**Without `--strict` this gate reports green over a dependency it never examined.**
That is the same fail-open shape as an unparseable specifier treated as satisfied
(ledger item 17) and a guard blind to the published artefact (item 35). The flag
stays, and it is now a demonstrated catch rather than a stated intent.

**Reachable in this project's real shape**, not only in a laboratory: `pip freeze`
names whatever is installed, so a dependency from a private index, a VCS URL, or a
release later removed from PyPI would produce exactly this skip.

Cases that do **not** distinguish the flag, recorded so they are not retried:

| Case | Without | With |
|---|---|---|
| resolvable package with advisories (`jinja2==2.11.3`) | 1 | 1 |
| package with no advisories (`skillwatch==0.4.1`) | 0 | 0 |
| nonexistent package name | 1 | 1 |
| yanked release (`urllib3==2.0.3`) | 1 | 1 |
| local sdist of a **published** version | 0 | 0 |
| editable `-e .` in the requirements file | 0 | 0 |

The editable and URL skips in `_collect_preresolved_deps` (`requirement.py:312-346`)
are **unreachable in CI's shape**: that code path runs only under `--no-deps`, which
this project does not pass.

**Stated limit on this control.** It was run locally against pip-audit **2.10.1**,
not in CI. CI installs whatever `pip install pip-audit` resolves at run time, so a
future version could change the behaviour. The mechanism is a property of pip-audit
and the requirements file rather than of the runner, which is why a local control was
judged sufficient; the observation that would overturn that is a CI run where a
skipped dependency does not fail the step.

**One honest limit remains.**

1. This audits the versions CI **installed**, which are the newest a resolver picks.
   It still says nothing about what the declared ranges *permit* — that remains the
   floor audit's job, and the reason the two checks are separate has not changed.

The floor audit queries OSV for every `>=` floor declared in any table of
`pyproject.toml` — runtime dependencies, every optional-dependency group, and
`build-system.requires` — and reports the lowest published version that clears
all known advisories. It exits non-zero if any floor is vulnerable.

Floors are therefore held at **the lowest release free of known advisories**, not
the lowest release that happens to work.

## Why `uv run`, not `uv sync`

Use:

```bash
uv run --python 3.10 --resolution lowest-direct --isolated --extra dev pytest -q
```

Not `uv sync --resolution lowest-direct`. With a lockfile present, `uv sync`
resolves from the lock and lands **above** the declared minimums, so the leg
passes while testing nothing. `uv run --isolated` resolves fresh.

## Caveat: `lowest-direct` can resolve some dependencies very low

`lowest-direct` applies the lowest version satisfying each **direct** declaration.
Any requirement with no floor is therefore free to resolve to its oldest release
on the index, which can be a decade old and nothing like what a real user installs.

Two live examples in this repo:

- **`setuptools`** now carries a declared floor (`>=83.0.0`), and it is a
  *build* dependency — so `lowest-direct` exercises the project's build path at
  that floor, not merely its runtime. A build backend old enough to mis-handle
  modern metadata will fail here rather than in a user's install.
- **`pytest-cov`** has no floor and resolves to **0.6** on this leg. That is
  harmless today only because the leg runs `pytest -q` without coverage. If the
  command ever gains `--cov`, give `pytest-cov` a floor first, or the leg will
  fail for reasons that have nothing to do with SkillWatch.

The deliberately floor-free requirements are listed in `NO_FLOOR_EXPECTED` in
`scripts/audit_dependency_floors.py`. A test asserts nothing else is floor-free,
so adding a requirement without a floor fails the suite rather than silently
opting out of the audit.

## The floor contract holds across the whole matrix, not just the oldest Python

A floor can be advisory-free, bounded, and still uninstallable on one supported
interpreter. `pyyaml>=6.0` was all three: 6.0 publishes no cp312 or cp313 wheel
and fails to build on both, yet the `lowest-direct` leg ran on 3.10 only and
stayed green. The project declares support for 3.10–3.13, so the contract has to
be exercised on all four. `lowest-direct` is now a matrix over 3.10, 3.11, 3.12
and 3.13.

**The resolver is the oracle, not package metadata.** Reading wheel filenames or
`requires_python` produces false positives — abi3 wheels (`cp39-abi3-*`) and
platform-tagged pure-Python wheels carry no `cp313` marker yet install fine on
3.13. Every floor raise here is evidenced by an actual resolve-and-run.

### Why `pyyaml>=6.0.2` and not `>=6.0.1`

Resolver evidence, `uv pip install --no-cache` on Python 3.13:

| Version | Result |
|---|---|
| `6.0` | fails — `AttributeError: 'build_ext' object has no attribute 'cython_sources'` |
| `6.0.1` | **`Built pyyaml==6.0.1`** — installs, but by compiling from sdist (2.04s) |
| `6.0.2` | `Prepared in 50ms` — installs from a wheel, no compilation |

6.0.1 is not broken; PyPI publishes no cp313 wheel for it, so it builds from
source. That works only where a C toolchain and a compatible Cython are present.
A floor whose installability depends on the user's build environment is a weak
contract, so the floor is 6.0.2 — the first release shipping wheels across the
whole matrix.

### Environment markers were considered and rejected

`pyyaml>=6.0; python_version<"3.12"` paired with a higher floor above would also
work. Rejected: it creates a permanent per-Python maintenance surface in exchange
for tolerating a transient packaging gap. PyYAML 6.0.2 is from August 2024;
requiring it harms nobody, and a single floor is one fact to keep true instead of
two. **Reasoned, not evidenced** — no source was found measuring how often
consumers are pinned below a two-year-old minor release. Assumption: no user of
this project is constrained to pyyaml <6.0.2. Observation that would overturn it:
a real user reporting they cannot upgrade. The change is cheap to reverse — one
line in `pyproject.toml`.

## What the auditor can and cannot prove

The auditor's networked check confirms, for every declared floor, that the exact
floor version exists on PyPI and that its `requires_python` admits every Python
in the project's own `Programming Language :: Python :: X.Y` classifiers. Those
classifiers are the single source, so the check follows declared support rather
than drifting from it.

**This does not prove installability**, and must not be described as if it does.
A release can satisfy `requires_python` and still have no wheel for a given
interpreter, then either build from sdist or fail. `pyyaml` 6.0 satisfies
`requires_python` on 3.13 and does not install. Only the `lowest-direct` matrix
proves a floor resolves and runs.

## Bumping the linter and type checker

`ruff` and `mypy` are bounded (`>=x,<y`), not floating. Their *default rule sets*
change between minor releases, so an unpinned tool turns CI into a check that
goes red on an upstream release rather than on a code change — which is exactly
what happened when ruff 0.16.0 landed and reported 27 findings on code that had
been green. Bumping those bounds is a deliberate, reviewed change; Dependabot
proposes it, and the rule-set delta gets read before it is accepted.
