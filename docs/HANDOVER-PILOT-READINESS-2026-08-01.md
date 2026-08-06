# SkillWatch pilot-readiness handover — 2026-08-01

> **AUTHORITATIVE HANDOVER:** `docs/current-handover.txt` designates this file.

## Intended and actual scope

The unit reproduced local, remote, PR, public-package and assurance state; ran
published and candidate clean-room workflows; delegated a context-restricted
first-time-operator rehearsal; corrected one reproduced P1; added the minimum
participant operations package; and prepared local-only public reconciliation.
No integration was built and no remote write occurred.

## Environment and access

- UTC date: 2026-08-01.
- Repository: `/home/mkuziva/skillwatch`.
- Sandbox: workspace-write; repository and `/tmp` writable, `.git` and Windows
  Downloads required explicit approval. Network and local sockets were restricted
  until individually approved for read-only verification.
- Interpreter: `.venv/bin/python`, Python 3.12.3.
- Raw evidence: `analysis/session-log-2026-08-01-pilot-readiness.md`.

## Initial repository and public state

- Start `39e85a654435908a38898332dccfbc314b7ad16f`; branch
  `feat/archive-durability-and-strict-audit`; upstream `de2a998498293ad17f6b1990e19dc8868c614293`;
  `origin/main` `6c6ab215742b8d4913b9193a8df49e645f5cd060`.
- Initial tree clean and 11 commits ahead. PR #34 OPEN, CLEAN and MERGEABLE but
  at the older upstream revision. All nine reported PR checks passed.
- PyPI served 0.4.1. Public main README differed from the candidate README and
  retained stale public documentation.
- Condition 2 not demonstrated; condition 5 failed; organic delta pending.
- No recorded behavioural demand evidence. Literal absence of all external use
  remains Unverified.

## Material classifications

Demonstrated: repository/PR revisions; stale PR; public/local README divergence;
646 passing tests after the change; 95.71% coverage; readiness states; published
0.4.1; mechanical install and command behavior; no detector/corpus/baseline/
dependency/threshold/integration change.

Unverified: human self-service, trust, demand, retention, payment, separate-CLI
acceptability, provenance changing a decision, public suitability after this
unpublished fix, and organic drift. These require qualified participant behavior,
before/after decisions, commercial follow-through, a public-state reconciliation,
or the separately registered organic pass.

Contradicted: the inherited 645-test and 95.70% figures after adding the regression
test; the final reproduced values are 646 and 95.71%. The claim that the existing
pilot package was executable without maintainer knowledge was contradicted by the
restricted rehearsal.

## Clean-room evidence

Published and pre-fix candidate 0.4.1 installed in isolated environments. The
maintainer-run path established a baseline, repeated an unchanged scan, listed
alerts, verified/exported the ledger, exercised unreachable and malformed inputs,
and removed state. Published and candidate behavior was materially identical.

The restricted operator installed the candidate wheel but `example.com` resolved
to a reserved address. `add` printed `Added 0 URL(s)`, exited 0 and told the
operator to scan; scans exited 0 with no URLs. It produced a database and tracked
source only—no fetched snapshot, observation, ledger head or baseline. This is an
agent mechanical rehearsal, not user or demand evidence.

## Changes and evidence

- `skillwatch/cli.py`: all-rejected file add exits 1, gives corrective guidance
  and omits the scan instruction. Detector semantics are unchanged.
- `tests/test_cli.py`: one regression test; add validation made DNS-independent.
  Fail-before: `E assert 0 == 1`. Pass-after: `2 passed`. Mutation back to exit 0:
  the named test failed at the predicted assertion.
- `docs/pilot/`: participant runbook, maintainer checklist and manual CSV.
- `docs/DESIGN-PARTNER-PILOT.md`: executability matrix and links; thresholds remain
  solely canonical there.
- `docs/UNDERSTANDING-ALERTS.md`: removed an invalid live false-alarm extrapolation.
- `OPEN-ITEMS.md`: items 77–78 open; 79–80 closed with evidence.

Commits: `44fa051 Record pilot-readiness baseline`; `c0bbe8e Make pilot baseline
failures actionable`.

## Assurance

The first sandbox run recorded 5 failures caused by denied local sockets/DNS and
network-dependent floor/release/build checks as blocked. With explicitly approved
read-only network/socket access:

```text
646 passed in 26.71s
Required test coverage of 90% reached. Total coverage: 95.71%
full_suite_escalated_exit=0
Audited 20 declared dependency floors.
floors_escalated_exit=0
No claim violations.
release_claims_escalated_exit=0
No claim-marker drift between HEAD and the live page.
published_claims_escalated_exit=0
Successfully built skillwatch-0.4.1.tar.gz and skillwatch-0.4.1-py3-none-any.whl
build_escalated_exit=0
```

Readiness consistency, ruff, mypy, figure rules and capture verification each
exited 0. Collection: 646. Test-count change: `tests/test_cli.py` +1. Protected
diff for detector, corpora, delta runner and `pyproject.toml`: empty.

## Public reconciliation and next action

`/tmp/skillwatch-pr34-proposed.md` contains the complete proposed PR title/body;
`/tmp/skillwatch-maintainer-actions.md` contains normal-push, CI and review
commands. Final branch head before this handover commit was `c0bbe8e`, 25 commits
and 43 changed files versus origin/main, and 13 commits ahead of upstream.

Recommendation: after reviewing this handover, the maintainer should fetch,
verify upstream has not moved, normally push (never force), wait for CI, update
PR #34, and only then recruit qualified design partners. The organic pass remains
a separate unit on or after 2026-08-05.

## Continuity ledger

The complete canonical ledger is `OPEN-ITEMS.md` and is reproduced verbatim in
the Downloads consolidation generated from this handover and the ledger. No item
was removed. Items 37, 38, 43 and 52 remain open pending the organic pass; item 9
remains open because an agent rehearsal is not a user.

## Final bounded verification update

Final verification commit: `60dbd8f Record final pilot workflow verification`.
The candidate wheel was built from `e74b89a5de2e0ccd684886d211accf43361fd3a8`
and has SHA-256 `2719b78bea0f68ce1a49f431fad078f2257ca2ed1af6d0d311fceb2a3322e231`.
The project-owned README URL returned HTTP 200 and was accepted without an SSRF
bypass. With approved read-only network access, the fresh isolated run installed
all dependencies, added one URL, completed the first scan and a second unchanged
scan, verified two ledger entries, exported the ledger, removed the URL, and
rejected the localhost-only input with exit 1 and corrective guidance. The
restricted subagent attempt was blocked at dependency installation by DNS; its
`--no-deps` workaround was invalid and did not test product behavior. No new P0
or P1 was reproduced. Mechanical decision: READY. Human usability, trust,
demand, retention, payment and provenance decision value remain Unverified.

The final full suite was `647 passed in 53.20s`, with 95.71% coverage. The latest
working tree is clean, 15 commits ahead of upstream, and no remote write occurred.
