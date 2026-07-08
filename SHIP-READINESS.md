# Ship Readiness Checklist

Items removed or deferred during remediation. Restore these before publishing to PyPI.

## DECISION.md Condition Map

All 5 conditions must PASS before the HOLD can be lifted.

| # | Condition | Status | Evidence |
|---|-----------|--------|----------|
| 1 | Evasive recall >= 50% OR documentation makes unmissable that triage is decorative | **PASS** | Evasive recall is 50% on original corpus, 75% on holdout. README states figures in multiple places with honest ceiling statement. |
| 2 | Precision >= 75% | **PASS** | 78.9% on original corpus, 90.0% on holdout. SRI hash FP fixed. |
| 3 | Named maintenance owner and pattern update cadence | **PASS** | MAINTENANCE.md names sole contributor as owner. Quarterly review cadence ratified 2026-07-08. |
| 4 | Minimum one independent, non-conflicted evidence source for premise | **LIKELY** | CSA and arxiv sources assessed as LIKELY INDEPENDENT of AIR (see analysis/source_independence_memo.md). arxiv authors at Tsinghua/CAS/Swinburne. CSA note attributed to CSA's own initiative. Full affiliation verification not possible. |
| 5 | Evidence of at least minimal user demand | **FAIL** | Zero stars, zero forks, zero external users. Repository is private. |

**Current verdict: HOLD.**

Honest condition tally: 3 firm PASS (conditions 1, 2, and 3), 1 LIKELY but not fully verified (condition 4), 1 FAIL (condition 5). The HOLD cannot be lifted until conditions 4 and 5 are resolved.

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
| PyPI publish | DECISION.md HOLD -- conditions 4 and 5 fail | publish.yml workflow exists but requires manual dispatch |
| GitHub Marketplace listing | Repository is private | action.yml is functional but not listed |
| GitHub Pages deployment | DECISION.md HOLD | docs/index.html exists but Pages not enabled |

## Marketplace — post-HOLD (O-03)

The action.yml already has marketplace branding configured:
- `icon: shield`
- `color: blue`

Once the HOLD is lifted and the repository is made public:
1. Go to https://github.com/marketplace
2. Select the SkillWatch repository
3. Choose "Create a new listing" for GitHub Actions
4. Fill in the listing description from the README "Why this exists" section
5. Set pricing to "Free"
6. Submit for review

Do NOT list until: repository is public, HOLD is lifted, and all 5
DECISION.md conditions are met.

## Publish-day checklist

Exact commands to run on the day the HOLD is lifted. Execute in order.

```bash
# 1. Verify all tests pass
source .venv/bin/activate
python3 -m pytest --cov=skillwatch --cov-report=term-missing -q

# 2. Verify lint is clean
ruff check skillwatch/ tests/

# 3. Verify build is clean
rm -rf dist/ build/ skillwatch.egg-info
python3 -m build

# 4. Run efficacy harness and confirm no regressions
python3 analysis/measure_efficacy.py

# 5. Verify mypy passes
mypy skillwatch/

# 6. Run pip-audit on the venv
pip-audit

# 7. Restore PyPI badges to README.md
# (see "Removed" table above for exact badge markdown)

# 8. Restore pip install instruction to README.md
# Change Install section from "git clone" to "pip install skillwatch"

# 9. Restore pip install in action.yml
# Change line 32 from "pip install git+https://..." to "pip install skillwatch"

# 10. Bump version in pyproject.toml if needed
# Update skillwatch/__init__.py version to match

# 11. Tag the release
git tag -a v0.X.0 -m "Release v0.X.0"
git push origin main --tags

# 12. Publish to PyPI (manual dispatch)
# Go to Actions > publish.yml > Run workflow

# 13. Verify PyPI listing
pip install skillwatch  # from a clean venv

# 14. Enable GitHub Pages if desired
# Settings > Pages > Source: Deploy from branch > main > /docs

# 15. List on GitHub Marketplace (see section above)
```

## Action dry-run procedure (Q-05)

The GitHub Action cannot be tested end-to-end from within this repository.
To verify it works in a consuming repository:

```bash
# 1. Create a test repository
mkdir skillwatch-action-test && cd skillwatch-action-test
git init && git remote add origin https://github.com/<user>/skillwatch-action-test.git

# 2. Create a test SKILL.md with a known URL
cat > SKILL.md <<'SKILL_EOF'
# Test Skill

Documentation: https://example.com
Setup: https://httpbin.org/html
SKILL_EOF

# 3. Create a GitHub Actions workflow using the SkillWatch action
mkdir -p .github/workflows
cat > .github/workflows/test-skillwatch.yml <<'WF_EOF'
name: Test SkillWatch Action
on: [push]
jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: kuzivaai/SkillWatch@main
        with:
          files: SKILL.md
WF_EOF

# 4. Push and check the workflow run
git add -A && git commit -m "test: verify SkillWatch action"
git push -u origin main

# 5. Go to Actions tab and verify:
#    - Python is installed
#    - SkillWatch is installed from git
#    - URLs are added from SKILL.md
#    - Scan runs without error
#    - Results artifact is uploaded

# 6. On second push (with SKILL.md unchanged), verify:
#    - Database is restored from cache
#    - Scan reports "unchanged" for previously seen URLs
```

This procedure cannot be automated from within SkillWatch itself because
the Action is a composite step that requires a GitHub Actions runner
environment with access to `actions/setup-python`, `actions/cache`, etc.
