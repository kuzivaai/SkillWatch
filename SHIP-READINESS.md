# Ship Readiness Checklist

Items removed or deferred during remediation. Restore these before publishing to PyPI.

## Removed (must restore before PyPI publish)

| Item | Location | Original Content | Reason Removed |
|------|----------|------------------|----------------|
| PyPI version badge | README.md line 6 | `[![PyPI](https://img.shields.io/pypi/v/skillwatch)](https://pypi.org/project/skillwatch/)` | Links to unpublished package; badge renders as "not found" |
| PyPI Python versions badge | README.md line 7 | `[![Python](https://img.shields.io/pypi/pyversions/skillwatch)](https://pypi.org/project/skillwatch/)` | Links to unpublished package; badge renders as "not found" |
| `pip install skillwatch` instruction | README.md Install section | `pip install skillwatch` as primary install method | Package not on PyPI; command would fail |
| `pip install skillwatch` in action.yml | action.yml line 32 | `run: pip install skillwatch` | Changed to `pip install git+https://...` until PyPI publish |

## Deferred (not yet ready)

| Item | Blocker | Notes |
|------|---------|-------|
| PyPI publish | DECISION.md HOLD -- conditions 3 and 5 fail | publish.yml workflow exists but requires manual dispatch |
| GitHub Marketplace listing | Repository is private | action.yml is functional but not listed |
| GitHub Pages deployment | DECISION.md HOLD | docs/index.html exists but Pages not enabled |
