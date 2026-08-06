# Competitor voice — 2026-08-01

## Sampling protocol

Fixed creation window: 2025-08-01 through 2026-08-01. For each GitHub repository
and state:

```bash
gh api -X GET search/issues \
  -f q="repo:OWNER/REPO is:issue created:2025-08-01..2026-08-01 state:STATE" \
  -f sort=created -f order=desc -f per_page=50
```

Pull requests were excluded. Samples are newest-created, up to 50 per state.
Microsoft APM required `per_page=100`, then the first 50 relevant issues after
deterministic exclusions, because automated performance/CLI consistency reports
crowded out relevant reports. Excluded: automated reports, marketplace/listing
solicitations, reserved-account notices and unrelated pitches.

Mutually exclusive type taxonomy from title and labels: bug, enhancement, support
question, documentation, other. Overlapping themes use titles. Search responses
contained body/labels but not complete discussions, so operator error and closure
correctness are Unverified. Settle them by retrieving every comment/timeline and
independently coding maintainer closure reasons.

The complete 410-record selection/coding audit trail is
[`data/competitor-issues-2026-08-01.tsv`](data/competitor-issues-2026-08-01.tsv),
SHA-256 `9f90aa7c08c7e5712272016de8c6b08ff2cd1aa30dae0c2f057c6070a41400f9`.
It records every issue ID, date, URL/title, retained/excluded decision, exclusion
reason, one type and overlapping theme codes. Walk API order, apply the recorded
exclusion/type/theme rules and stop at 50 retained items or EOF. This makes the
selection reproducible; keyword coding validity still requires independent
double-coding or adjudication.

Failed attempt: `gh api search/issues -f ...` implicitly used POST and returned
HTTP 404. Adding `-X GET` succeeded. The 404 is a tooling-method failure, not an
empty corpus.

## Samples and themes

| Repository | Population and retained sample | Type counts | Positive evidence | Negative/recurrent themes |
|---|---|---|---|---|
| Microsoft APM | Open 106, 50 relevant from 100; closed 900, 50 relevant. Closed median 1.84 days, max 13.59. | Open: 7 bug, 30 enhancement, 4 docs, 9 other. Closed: 46 bug, 2 enhancement, 2 other. | Active closure and many target/integration requests. | In 100 raw titles: target/portability 33; lock/audit/integrity 12; install/update/remove 24. #2392 re-sync-before-audit risk, #2379 narrowed integrity scope, #2297 lock churn. Automation/development intensity confounds the stream. |
| changedetection.io | Open 84 / newest 50; closed 242 / newest 50. Closed median 0.85 days. | Open: 12 bug, 26 enhancement, 1 support, 11 other. Closed: 13 bug, 11 enhancement, 3 support, 23 other. | Fast sampled closure; requests extend advanced browser/history/notification flows. | Themes: LLM 22; browser/fetch 19; notifications 13; UI/history 21. Operational browser, scheduling, delivery, history and LLM edge cases recur. |
| Snyk Agent Scan | Open 3/all; closed 30/all, 25 retained after five pitches. Closed median across all 30: 29.07 days. | Open: 1 bug, 2 other. Closed retained: 13 bug, 2 enhancement, 1 support, 1 docs, 8 other. | Coverage and CI-ignore requests show workflow relevance. | Raw themes: service/auth/egress 7; input/coverage 17; FP/ignore 3. Hosted availability/auth, opt-out/local-only clarity, input gaps and false positives recur. |
| Cisco Skill Scanner | Open 10/9 retained; closed 35/34 retained. Median 5.32 days. | Open: 4 bug, 3 enhancement, 1 support, 1 other. Closed: 23 bug, 7 enhancement, 1 support, 3 other. | Active fixes; SARIF/report/CI/provider requests support integration demand. | Themes: LLM reliability 16; FP/non-determinism 5; gaps 3; CI/output 9. Truncation, provider failure, non-determinism and output correctness recur. |
| NVIDIA SkillSpector | Open 50/49 retained; closed 90/newest 50. Median 2.46 days. | Open: 16 bug, 9 enhancement, 24 other. Closed: 29 bug, 5 enhancement, 1 docs, 15 other. | Rapid sampled closure; broad output/provider/integration work. | Themes: FP/scoring 7; silent/incomplete 9; gaps/evasions 19; LLM/provider 29; output/integration 18; dependency-version 5. Issues allege safe-on-provider-failure, dropped batches and lossy output; not independently reproduced. |
| SchemaPin (`ThirdKeyAi/schemapin`) | Open 0, closed 0. | Empty corpus. | None inferable. | Zero issues is not proof of quality, adoption or no complaints. |

## Review-platform result

No defensible recent Distill or Visualping store/review sample was obtained.
Dynamic/account/rate-limited surfaces and search snippets do not form an ordered
sample. Status: **Blocked / Unverified**. To settle: name one store, preserve the
newest N reviews in order with dates and solicitation/incentive disclosure, then
code all N with the published rubric.

## Interpretation limits

GitHub reporters self-select; populations mix users, maintainers, automation and
security researchers. Newest-created samples overweight current release work.
Closed does not mean fixed. Theme counts overlap and describe sampled titles, not
all users or installations. Positive and negative evidence are retained equally.

The evidence supports testing integration into APM/scanner/CI review paths and
competing on deterministic local evidence, impact mapping and acceptance. It
does not establish competitor prevalence, SkillWatch demand, or scanner
superiority.

Adversarial audit correction: the first hand-counted aggregates reported APM
closed as 47/1/2 and NVIDIA open as 14/9/26. Regeneration through one classifier
produced 46/2/2 and 16/9/24 respectively. The manifest values are authoritative;
the discrepancy is retained because it demonstrates why the audit trail matters.
