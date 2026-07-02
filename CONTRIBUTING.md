# Contributing to SkillWatch

Thank you for your interest in contributing.

## Getting started

```bash
git clone https://github.com/kuzivaai/SkillWatch.git
cd SkillWatch
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

## Running checks

```bash
# Tests
pytest --cov=skillwatch --cov-report=term-missing -q

# Lint
ruff check skillwatch/ tests/

# Efficacy measurement (optional, requires corpus in analysis/)
python3 analysis/measure_efficacy.py
```

## What to work on

- Bug reports and fixes are welcome.
- If you want to add a new detection pattern, please include a corpus item (benign and adversarial) and re-run the efficacy measurement to confirm no regression.
- The content triage is heuristic and evadable by design. Proposals to add ML or LLM-based detection are out of scope for this project.

## Pull request guidelines

1. Fork the repository and create a branch from `main`.
2. Add tests for any new behaviour.
3. Run `pytest` and `ruff check` before submitting.
4. Keep pull requests focused on a single change.

## Code of conduct

This project follows the [Contributor Covenant](CODE_OF_CONDUCT.md). Please be respectful and constructive.

## Reporting security issues

See [SECURITY.md](SECURITY.md) for vulnerability reporting instructions.
