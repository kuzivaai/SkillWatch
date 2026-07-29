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
| `pip-audit --skip-editable` | Do the versions we installed have advisories? | `security` job |
| `scripts/audit_dependency_floors.py` | Do the versions we *permit* have advisories? | `security` job |
| `uv run --resolution lowest-direct` | Do the versions we permit actually work? | `lowest-direct` job |

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
