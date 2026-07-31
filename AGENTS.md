# Codex onboarding handover

This is the tracked entry point for Codex sessions in SkillWatch. Read this file,
`CLAUDE.md`, and `OPEN-ITEMS.md` before editing. `OPEN-ITEMS.md` is the canonical
continuity ledger; update it in the same commit as any item opened or closed. Do
not use ignored local handovers as an authority source.

## Current transition

The branch `feat/archive-durability-and-strict-audit` contains five reconciled
commits above `origin/main`:

1. `852fd72` — capture absence/corruption verification, durable copy registry,
   derived mypy scope, and strict resolved-dependency auditing.
2. `17ab8f1` — continuity-ledger closures and corrected dependency-floor history.
3. `fe66903` — observed-red security control, complete gate accounting, and
   mechanically checked onboarding facts.
4. `fd4f4a9` — workflow behavior/trigger digests and drift enforcement.
5. `4b366c5` — observed-red build control and demonstrated load-bearing
   `pip-audit --strict` behavior.

An independent adversarial review on 2026-07-31 received only the five-commit
diff, the committed verification record, and `OPEN-ITEMS.md`. Its two MEDIUM
findings were independently reproduced and fixed:

- malformed nonempty capture copy registries now produce the documented
  `UNUSABLE` result and exit 4 instead of an uncaught exception;
- gate canonicalisation ignores `name` only for job/step display labels and
  retains behavior-bearing nested inputs such as `with.name`.

No HIGH findings were reported. Ledger items 68 and 69 contain the reproductions
and resolutions. The remaining risks are ledger items 3, 9, 11, 31, 63, and 66;
in particular, the real `publish` job has never been observed red and must not be
tested against production PyPI without explicit maintainer authority.

## Final local verification (2026-07-31)

- `git diff --check origin/main..HEAD` — pass.
- Offline citation check, `pytest -q tests/test_published_claims.py` — 8 passed.
- Citation self-test, `pytest -q tests/test_claim_rules.py` — 11 passed.
- `ruff check skillwatch/ tests/ scripts/ analysis/` — pass.
- `mypy skillwatch/ scripts/ $(git ls-files 'analysis/*.py')` — 25 files clean.
- Full suite with coverage — 628 passed, 95.70% coverage.
- `python scripts/figure_rules.py` — pass, 34 distinct proportions.
- `python scripts/audit_dependency_floors.py` — 20 floors audited, pass.
- `python analysis/verify_capture.py` — all 3 copies verified.
- `python -m build` — sdist and wheel built successfully.
- `npm run lint` — not applicable: this Python repository has no `package.json`.
- Markdown render path — `CLAUDE.md`, `OPEN-ITEMS.md`, and this handover rendered
  with Pandoc and were visually inspected.

Set `PYTHONDONTWRITEBYTECODE=1` for verification runs. The canonical commands and
the reasons behind them are maintained in `CLAUDE.md`.
