# SkillWatch readiness-consistency evidence — 2026-07-31

Append-only record for the readiness-truth and design-partner-pilot unit.

## Environment and initial state

```text
UTC: Fri Jul 31 21:31:15 UTC 2026
repository: /home/mkuziva/skillwatch
sandbox: workspace-write
approval: managed escalation
writes: repository and /tmp; outside paths require approval
network: restricted by default; approved fetch and GitHub reads succeeded
start_head: de2a998498293ad17f6b1990e19dc8868c614293
origin/main: 6c6ab215742b8d4913b9193a8df49e645f5cd060
upstream: de2a998498293ad17f6b1990e19dc8868c614293
branch: feat/archive-durability-and-strict-audit
local-only commits: none
remote-only commits: none
skillwatch_diff_exit=0
initial_diff_check_exit=0
```

PR #34 was reproduced via GitHub: OPEN, non-draft, MERGEABLE/CLEAN, head
`de2a998498293ad17f6b1990e19dc8868c614293`, base `main`, 12 commits, 17 changed
files, +4525/-1090. All nine CI checks passed. Its title and body still described
the earliest archive/strict-audit unit and claimed 595 tests.

## Pre-edit claim classification

1. **Demonstrated:** PR #34 is open at the GitHub-reported revision.
2. **Demonstrated:** the feature branch is fully pushed; upstream equals HEAD and
   both local-only and remote-only commit lists are empty.
3. **Demonstrated:** no `skillwatch/` production code differs from `origin/main`
   (`git diff --quiet ...`, exit 0).
4. **Demonstrated:** the dependency-complete `.venv` reproduces the harness and
   the prior 633-test collection; the unqualified system `python3` commands are
   **Contradicted** as reproducible commands because they fail importing
   `confusable_homoglyphs`. Settling command: `.venv/bin/python -m pytest
   --collect-only -q` and the escalated full coverage command.
5. **Contradicted:** ship-readiness condition 2 does not pass. The current
   harness gives benign FP 6/37 with Wilson upper bound 31.1%, above the ≤30%
   threshold.
6. **Contradicted:** conditions 1–4 do not all pass because condition 2 is not
   demonstrated.
7. **Contradicted:** zero users is not literally the only unresolved gate;
   condition 2 and the organic-delta evidence remain unresolved. It is the
   binding commercial constraint.
8. **Contradicted:** `SHIP-READINESS.md` contains stale current corpus totals,
   a retracted “same five” claim, and the pre-rewrite inline-only
   `hidden_content` description.
9. **Contradicted:** `## Open` contains rows explicitly marked CLOSED, including
   items 35 and 36.
10. **Contradicted:** PR #34 title/body do not represent its current 12-commit,
    17-file scope or current 633-test baseline.

## Reproduced contradictions

```text
OPEN-ITEMS.md:30: Item 9 ... is the only thing gating ... Conditions 1–4
SHIP-READINESS.md:38: condition 2 STILL NOT DEMONSTRATED
SHIP-READINESS.md:44: Conditions 1–4 pass
SHIP-READINESS.md:51: expanded from 10 items to 25
SHIP-READINESS.md:61: the same five are caught
SHIP-READINESS.md:77: 25 evasive items
SHIP-READINESS.md:96: only inspects an element's inline style
OPEN-ITEMS.md:58: item 35 status CLOSED under ## Open
OPEN-ITEMS.md:59: item 36 status CLOSED under ## Open
```

The system interpreter failed the requested harness commands with
`ModuleNotFoundError: confusable_homoglyphs`; this is an environment-command
failure, not a harness result. The repository `.venv` reproduced:

```text
original corpus: 37 benign, 10 adversarial A, 32 adversarial B
benign FP: 6/37 (16.2%, 95% CI [7.7%, 31.1%])
overall recall: 27/42 (64.3%, 95% CI [49.2%, 77.0%])
evasive recall: 17/32 (53.1%, 95% CI [36.4%, 69.1%])
families: semantic 3/13; structural 6/10; mechanical 7/7; language 1/2
base rate: 201 pages, 166 SKILL.md files, 157 repositories
figure rules: 34 distinct proportions; exit 0 under `.venv`
```

## Readiness fail-before

Prediction: the targeted suite should fail once for each reproduced class:
contradictory verdict, non-directional bound rule, retracted claim, stale corpus
totals, and closed rows under Open.

```text
$ .venv/bin/python -m pytest -q tests/test_readiness_consistency.py
FFFFF
5 failed in 0.06s

Failures:
- condition 2 row contains NOT DEMONSTRATED while current verdict says 1–4 pass;
- no directional lower/higher and upper/lower rule exists;
- current condition 1 prose says “same five are caught”;
- current condition 1 prose says 25 evasive items while the corpus contains 32;
- CLOSED rows occur under ## Open.
```

## Design choice

Chosen: `docs/readiness-status.json` is the small structured source for condition
status, metric direction, verdict and the distinction between commercial and
readiness constraints. `scripts/readiness_consistency.py` validates it against
the live efficacy harness and requires `SHIP-READINESS.md`'s marked current block
to equal the generated rendering. It also validates ledger sections.

Rejected: correcting prose and adding only semantic searches. That would catch
today's phrases but leave five independently maintained status copies. The
structured source closes status/verdict drift and derives metric bounds; prose
searches remain narrow regressions for retracted historical claims and detector
description. Blind spot: arbitrary prose outside the generated block can still
make novel semantic claims; bounded regression searches and review remain needed.
A future condition is added once to the JSON schema and renderer, while its
metric is named from harness output rather than copied into prose.

## Negative-control predictions

1. Change the generated verdict to “only condition 5 remains”: the generated
   scoreboard equality test must fail.
2. Change condition 2 direction to `higher_is_better`: status validation must
   fail because the lower bound would pass while status remains not demonstrated.
3. Reinsert “same five are caught” in the current condition 1 section: the
   retracted-claim test must fail.
4. Move closed item 35 under Open: the ledger-section test and repository gate
   must fail.

Each mutation will be reverted and checked with a path-scoped empty diff against
its saved pre-mutation copy.

## Negative-control observations

```text
Control 1 — scoreboard says “Only condition 5 remains”
FAILED test_structured_status_matches_harness_and_current_scoreboard
Diff: expected “Condition 2 is not demonstrated; condition 5 fails”, observed
“Only condition 5 remains”. 1 failed. Reverted.

Control 2 — false-positive metric changed to higher_is_better
First run unexpectedly PASSED. Confound/root gap: direction was supplied by the
same mutable JSON as the metric, so the validator had no independent semantic
knowledge. Added METRIC_DIRECTIONS as the metric-definition registry.
Second run:
FAILED test_structured_status_matches_harness_and_current_scoreboard
condition 2 direction higher_is_better conflicts with
benign_false_positive_rate direction lower_is_better. 1 failed. Reverted.

Control 3 — reinsert “same five are caught” in current condition 1
FAILED test_retracted_original_ten_claim_is_not_current. 1 failed. Reverted.

Control 4 — duplicate CLOSED item 35 under ## Open
FAILED test_ledger_sections_agree_with_row_statuses and repository gate reported:
FAIL: non-open status under Open: | 35 | ... . Reverted.

Post-revert checks:
git diff --check: exit 0
forbidden mutation phrases in current files: no output
item 35 authoritative row count: 1
tests/test_readiness_consistency.py: 6 passed
scripts/readiness_consistency.py: exit 0
```

The first direction mutation found and closed a real duplicated-truth hole. No
expected value was changed to absorb it; the independent metric-direction
registry now makes the control load-bearing.

## Assurance correction and passing full suite

The first final full-suite run reproduced a public-claim failure: the generated
condition-4 summary attributed a finding to SIGIL without linking its arXiv
primary source. Result: `1 failed, 638 passed`; coverage remained 95.70%. The
structured summary and both current SHIP-READINESS references now link
`https://arxiv.org/abs/2605.05274`.

The post-fix full-suite result was:

```text
TOTAL                      1627     70    96%
Required test coverage of 90% reached. Total coverage: 95.70%
639 passed in 60.89s (0:01:00)
```

## Independent adversarial review — verbatim findings and disposition

Reviewer A initial findings (verbatim):

```text
HIGH — README.md:515 says “About 1 in 6 safe pages … will trigger an alert,” contradicting docs/LAUNCH-FACTS.md:59-61,113-118 and SHIP-READINESS.md:45-47, which say the corpus is synthetic and the real-page false-positive rate is unmeasured.

MEDIUM — scripts/readiness_consistency.py:70-113 evidence-validates only Wilson-bound conditions. Conditions 1, 3, 4 and 5 can drift without failure. Currently condition 3 is marked PASS while its review is overdue.

MEDIUM — scripts/readiness_consistency.py:77-84,116-140 accepts arbitrary non-GO verdicts and hard-codes the condition-2/condition-5 prose instead of deriving those clauses from condition statuses.

MEDIUM — docs/DESIGN-PARTNER-PILOT.md:90-139 does not operationalize “limited intervention,” “tolerable review cost,” “repeatedly,” burden exceeding value, or minimum enrollment.

LOW — docs/DESIGN-PARTNER-PILOT.md:58-60 calls repeated weekly observations “independent”; independence is not established.

LOW — docs/research/COMMERCIAL-VALIDATION-2026-07-31.md:15-16,32-33,50-51,69-70,87-88,111-112 acknowledges partial source review but claims no additional source would change the pilot decisions.
```

Reviewer B initial findings (verbatim):

```text
MEDIUM: readiness consistency remains an instance fix; duplicated current truth outside the generated block is not validated, despite the session log acknowledging this blind spot.

MEDIUM: duplicate condition IDs are silently collapsed before uniqueness validation, so the “exactly once” schema guarantee can pass malformed data.

No HIGH findings or hard-scope violations found.
```

All findings were reproduced. Fixes: the README now names synthetic corpus
items; the renderer derives non-passing clauses and evidence; all bases and
top-level values are controlled and cross-validated; freshness is bounded;
condition-specific evidence is checked; duplicate IDs fail closed; current
status copies outside the generated block were removed; pilot enrollment,
burden, use and routing thresholds are operational; and both cheap LOW wording
issues were corrected.

Reviewer B final focused result (verbatim):

```text
Fixed. No residual duplicated-truth finding remains within the focused scope. Current readiness values now live only in the structured source and generated/validated SHIP block; other surfaces point there without repeating them.
```

Reviewer A's last focused pass found the condition-1 section selector used a
fail-open `split(...)[-1]` when its heading was absent. That LOW finding was
reproduced and fixed by requiring exactly one heading, with absent/duplicate
mutation coverage. Its cross-field result (verbatim) was:

```text
Cross-field invariants: fixed, no residual.
```

No HIGH or MEDIUM finding remains. No finding was disputed or silently dropped.

## Render and visual inspection

Pandoc rendered `SHIP-READINESS.md`, the pilot and the research matrix to local
standalone HTML. The first Playwright attempt failed because it blocks `file:`
URLs. A headless Chromium snap fallback then failed to place two files because
of snap confinement. A temporary localhost-only server on 127.0.0.1:8876 gave
Playwright supported URLs. All three pages returned HTTP 200; the only console
errors were expected `/favicon.ico` 404s. Full-page screenshots and accessibility
snapshots showed complete headings, lists and tables with no truncation,
overlap, malformed table or missing section. The server was stopped after
inspection. Temporary artifacts remain only under `/tmp`.
=== FINAL TARGETED TESTS ===
........................................................................ [ 91%]
.......                                                                  [100%]
79 passed in 2.06s
targeted_exit=0
=== FINAL FULL SUITE ===
........................................................................ [ 11%]
........................................................................ [ 22%]
........................................................................ [ 33%]
........................................................................ [ 45%]
........................................................................ [ 56%]
........................................................................ [ 67%]
........................................................................ [ 78%]
..........................................F............................. [ 90%]
...............................................................          [100%]
=================================== FAILURES ===================================
_ TestEveryPublicSurfaceIsClean.test_surface_has_no_violations[SHIP-READINESS.md] _

self = <tests.test_published_claims.TestEveryPublicSurfaceIsClean object at 0x74e1c0b4c5f0>
rel = 'SHIP-READINESS.md'

    @pytest.mark.parametrize("rel", PUBLIC_SURFACES)
    def test_surface_has_no_violations(self, rel: str) -> None:
        found = rules.find_violations(_read(rel), source=rel)
>       assert found == [], "\n" + rules.format_violations(found)
E       AssertionError:
E         1 claim violation(s):
E           [unsourced-attribution] SHIP-READINESS.md: attributes a finding to 'SIGIL' but links nowhere on arxiv.org. A reader cannot check it and neither can we.
E               excerpt: 'SIGIL'
E       assert [Violation(ru...EADINESS.md')] == []
E
E         Left contains one more item: Violation(rule='unsourced-attribution', message="attributes a finding to 'SIGIL' but links nowhere on arxiv.org. A reader cannot check it and neither can we.", excerpt='SIGIL', source='SHIP-READINESS.md')
E         Use -v to get more diff

tests/test_published_claims.py:74: AssertionError
================================ tests coverage ================================
_______________ coverage: platform linux, python 3.12.3-final-0 ________________

Name                      Stmts   Miss  Cover   Missing
-------------------------------------------------------
skillwatch/__init__.py        1      0   100%
skillwatch/anchoring.py     101     12    88%   58-59, 109-110, 144, 155-156, 189-190, 197-198, 200
skillwatch/cli.py           491     30    94%   271-272, 307-308, 327, 335-336, 340, 360, 381, 385, 405, 422, 446, 556-558, 573-575, 579, 581, 718-721, 752-754, 781-782, 811
skillwatch/cloak.py          49      0   100%
skillwatch/detector.py      313      5    98%   266, 320, 732, 815-816
skillwatch/differ.py          8      0   100%
skillwatch/fetcher.py       117     12    90%   112, 155, 160-161, 168, 171, 185-187, 218-224
skillwatch/formatter.py     131      2    98%   23, 220
skillwatch/ledger.py         35      0   100%
skillwatch/parser.py        103      5    95%   75, 95, 123, 142, 144
skillwatch/sarif.py          17      0   100%
skillwatch/ssrf.py           81      4    95%   112, 130, 148, 190
skillwatch/store.py         180      0   100%
-------------------------------------------------------
TOTAL                      1627     70    96%
Required test coverage of 90% reached. Total coverage: 95.70%
=========================== short test summary info ============================
FAILED tests/test_published_claims.py::TestEveryPublicSurfaceIsClean::test_surface_has_no_violations[SHIP-READINESS.md]
1 failed, 638 passed in 41.37s
pytest_exit=1
=== FINAL COLLECTION ===
tests/test_anchoring.py::TestRfc3161Crypto::test_available
tests/test_anchoring.py::TestRfc3161Crypto::test_verifies_real_token_for_correct_head
tests/test_anchoring.py::TestRfc3161Crypto::test_rejects_wrong_head
tests/test_anchoring.py::TestRfc3161Crypto::test_rejects_empty_proof
tests/test_anchoring.py::TestRfc3161Crypto::test_bundled_cacert_verifies
tests/test_anchoring.py::TestRfc3161Crypto::test_anchor_head_posts_and_parses
tests/test_anchoring.py::TestRfc3161Crypto::test_unknown_method_raises
tests/test_anchoring.py::TestRfc3161Crypto::test_verify_unknown_method_raises
tests/test_anchoring.py::TestRfc3161Crypto::test_refuses_private_tsa
tests/test_anchoring.py::TestRfc3161Crypto::test_network_error_is_actionable
tests/test_anchoring.py::TestAnchorStore::test_record_get_latest
tests/test_anchoring.py::TestAnchorCommand::test_records_and_writes_proof
tests/test_anchoring.py::TestAnchorCommand::test_empty_ledger_cannot_anchor
tests/test_anchoring.py::TestAnchorCommand::test_unavailable_extra_is_actionable
tests/test_anchoring.py::TestVerifyAutoChecksAnchors::test_present_anchor_head_in_chain
tests/test_anchoring.py::TestVerifyAutoChecksAnchors::test_diverged_anchor_detected
tests/test_anchoring.py::TestVerifyAutoChecksAnchors::test_crypto_anchor_verified_through_cli
tests/test_anchoring.py::TestGitAnchor::test_module_commits_and_returns_sha
tests/test_anchoring.py::TestGitAnchor::test_cli_git_anchor_records
tests/test_anchoring.py::TestGitAnchor::test_requires_a_git_repo
tests/test_anchoring.py::TestGitAnchor::test_verify_shows_git_anchor
tests/test_ci_scope.py::test_there_is_at_least_one_tracked_analysis_module
tests/test_ci_scope.py::test_ci_type_checks_every_tracked_analysis_module
tests/test_ci_scope.py::test_the_mypy_scope_is_derived_rather_than_typed_out
tests/test_ci_scope.py::test_ci_lints_the_same_directories_the_docs_promise
tests/test_ci_scope.py::test_claude_md_documents_the_same_mypy_scope_as_ci
tests/test_ci_scope.py::test_pip_audit_runs_strict
tests/test_ci_scope.py::test_the_strict_guard_reads_the_command_not_the_comments
tests/test_ci_scope.py::test_pip_audit_does_not_skip_editable
tests/test_ci_scope.py::test_the_audited_set_excludes_the_project_itself
tests/test_ci_scope.py::test_pip_audit_is_installed_apart_from_the_project
tests/test_ci_scope.py::test_pythondontwritebytecode_is_set_at_workflow_level
tests/test_claim_rules.py::TestEntryPointExists::test_find_violations_is_callable
tests/test_claim_rules.py::TestEntryPointExists::test_returns_a_list
tests/test_claim_rules.py::TestCatchesTheShippedDistortions::test_flags_the_compressed_trail_of_bits_claim
tests/test_claim_rules.py::TestCatchesTheShippedDistortions::test_flags_the_reworded_owasp_mitigation
tests/test_claim_rules.py::TestCatchesTheShippedDistortions::test_flags_the_mitigations_overclaim
tests/test_claim_rules.py::TestCatchesTheShippedDistortions::test_flags_an_unsourced_attribution
tests/test_claim_rules.py::TestCatchesTheShippedDistortions::test_flags_trail_of_bits_cited_without_the_quantifier
tests/test_claim_rules.py::TestCurrentReadmeIsClean::test_readme_has_no_violations
tests/test_claim_rules.py::TestUseVersusMention::test_retraction_is_not_a_violation
tests/test_claim_rules.py::TestUseVersusMention::test_blockquoted_source_text_is_not_a_violation
tests/test_claim_rules.py::TestViolationShape::test_violation_carries_rule_message_and_excerpt
tests/test_claude_md_currency.py::test_the_pyproject_version_is_readable
tests/test_claude_md_currency.py::test_the_number_word_map_covers_the_counts_in_use
tests/test_claude_md_currency.py::test_claude_md_states_the_version_this_repository_declares
tests/test_claude_md_currency.py::test_claude_md_does_not_claim_a_pypi_version_without_a_date
tests/test_claude_md_currency.py::test_claude_md_counts_the_skillwatch_modules_correctly
tests/test_claude_md_currency.py::test_claude_md_counts_and_names_the_tracked_scripts_correctly
tests/test_claude_md_currency.py::test_claude_md_counts_and_names_the_tracked_analysis_modules_correctly
tests/test_cli.py::TestCLI::test_version
tests/test_cli.py::TestCLI::test_list_empty
tests/test_cli.py::TestCLI::test_add_url_and_list
tests/test_cli.py::TestCLI::test_add_from_file
tests/test_cli.py::TestCLI::test_add_ssrf_blocked
tests/test_cli.py::TestCLI::test_add_url_ssrf_error_is_actionable
tests/test_cli.py::TestCLI::test_add_missing_file_gives_actionable_error
tests/test_cli.py::TestCLI::test_remove_url
tests/test_cli.py::TestCLI::test_remove_nonexistent
tests/test_cli.py::TestCLI::test_alerts_empty
tests/test_cli.py::TestCLI::test_alerts_lists_open_alerts
tests/test_cli.py::TestCLI::test_alerts_all_includes_reviewed
tests/test_cli.py::TestCLI::test_no_command_shows_help
tests/test_cli.py::TestCLI::test_help_leads_with_examples
tests/test_cli.py::TestCLI::test_scan_shows_progress_counter
tests/test_cli.py::TestCLI::test_scan_initial_baseline
tests/test_cli.py::TestCLI::test_scan_unchanged_content
tests/test_cli.py::TestCLI::test_scan_detects_change_and_creates_alert
tests/test_cli.py::TestCLI::test_scan_error_handling
tests/test_cli.py::TestCLI::test_history_shows_snapshots
tests/test_cli.py::TestCLI::test_history_unknown_url
tests/test_cli.py::TestCLI::test_alert_detail_and_review
tests/test_cli.py::TestCLI::test_alert_nonexistent
tests/test_cli.py::TestCLI::test_db_after_subcommand
tests/test_cli.py::TestCLI::test_db_before_subcommand
tests/test_cli.py::TestCLI::test_db_shows_in_subcommand_help
tests/test_cli.py::TestCLI::test_user_agent_flag
tests/test_cli.py::TestCLI::test_json_output_baseline
tests/test_cli.py::TestCLI::test_json_output_with_alert
tests/test_cli.py::TestCLI::test_json_output_empty
tests/test_cli.py::TestCLI::test_scan_output_sarif
tests/test_cli.py::TestCLI::test_preset_docs
tests/test_cli.py::TestCLI::test_preset_docs_strips_timestamps
tests/test_cli.py::TestCLI::test_status_empty
tests/test_cli.py::TestCLI::test_status_after_scan
tests/test_cli.py::TestCLI::test_add_file_blocks_localhost
tests/test_cli.py::TestCLI::test_sources_empty
tests/test_cli.py::TestCLI::test_sources_detects_drift_and_adds_new_url
tests/test_cloak.py::test_compare_flags_variation
tests/test_cloak.py::test_compare_clean_when_identical
tests/test_cloak.py::test_compare_insufficient_fetches
tests/test_cloak.py::test_check_url_detects_cloaking_offline
tests/test_cloak.py::test_check_url_clean_offline
tests/test_cloak.py::test_cli_cloak_clean
tests/test_cloak.py::test_cli_cloak_detects_variation
tests/test_cloak.py::test_cli_cloak_insufficient
tests/test_concealment_unevaluable.py::TestConcealmentIsThreeValuedAndFailsClosed::test_concealed_is_truthy
tests/test_concealment_unevaluable.py::TestConcealmentIsThreeValuedAndFailsClosed::test_visible_is_falsey
tests/test_concealment_unevaluable.py::TestConcealmentIsThreeValuedAndFailsClosed::test_unevaluable_is_falsey
tests/test_concealment_unevaluable.py::TestConcealmentIsThreeValuedAndFailsClosed::test_unevaluable_is_not_visible
tests/test_concealment_unevaluable.py::TestMalformedDeclarationBlock::test_unparseable_segment_is_reported[bare-word]
tests/test_concealment_unevaluable.py::TestMalformedDeclarationBlock::test_unparseable_segment_is_reported[property-only]
tests/test_concealment_unevaluable.py::TestMalformedDeclarationBlock::test_unparseable_segment_is_reported[trailing-garbage]
tests/test_concealment_unevaluable.py::TestMalformedDeclarationBlock::test_unparseable_segment_is_reported[braces]
tests/test_concealment_unevaluable.py::TestMalformedDeclarationBlock::test_unparseable_segment_is_reported[number]
tests/test_concealment_unevaluable.py::TestMalformedDeclarationBlock::test_unparseable_block_assesses_as_unevaluable
tests/test_concealment_unevaluable.py::TestMalformedDeclarationBlock::test_a_parseable_block_is_visible_not_unevaluable
tests/test_concealment_unevaluable.py::TestMalformedDeclarationBlock::test_zero_height_without_clipping_does_not_conceal
tests/test_concealment_unevaluable.py::TestMalformedDeclarationBlock::test_zero_height_with_clipping_does_conceal
tests/test_concealment_unevaluable.py::TestMalformedDeclarationBlock::test_concealment_still_wins_over_unparseable_siblings
tests/test_concealment_unevaluable.py::TestUnparseableStyleBlock::test_chunk_with_no_brace_is_reported
tests/test_concealment_unevaluable.py::TestUnparseableStyleBlock::test_at_rule_is_reported_as_unparsed
tests/test_concealment_unevaluable.py::TestUnparseableStyleBlock::test_empty_selector_is_reported_as_unparsed
tests/test_concealment_unevaluable.py::TestUnparseableStyleBlock::test_a_clean_style_block_parses_fully
tests/test_concealment_unevaluable.py::TestUnparseableStyleBlock::test_at_rule_hidden_content_is_a_known_blind_spot
tests/test_concealment_unevaluable.py::TestSelectorEngineRejection::test_rejected_selector_does_not_crash_and_extracts_nothing[bad-nth]
tests/test_concealment_unevaluable.py::TestSelectorEngineRejection::test_rejected_selector_does_not_crash_and_extracts_nothing[empty-pseudo]
tests/test_concealment_unevaluable.py::TestSelectorEngineRejection::test_rejected_selector_does_not_crash_and_extracts_nothing[bare-combinator]
tests/test_concealment_unevaluable.py::TestSelectorEngineRejection::test_rejected_selector_does_not_crash_and_extracts_nothing[unclosed-has]
tests/test_concealment_unevaluable.py::TestSelectorEngineRejection::test_rejected_selector_does_not_crash_and_extracts_nothing[unknown-pseudo]
tests/test_concealment_unevaluable.py::TestSelectorEngineRejection::test_a_rejected_selector_does_not_suppress_a_valid_one
tests/test_continuity.py::test_dated_session_logs_are_not_ignored
tests/test_continuity.py::test_existing_session_logs_are_tracked
tests/test_continuity.py::test_item_22_names_the_later_strict_demonstration
tests/test_continuity.py::test_item_60_links_back_to_the_superseded_record
tests/test_continuity.py::test_supersession_index_records_item_22_to_60
tests/test_delta_pass.py::TestTheBaselineIsSufficient::test_baseline_exists_and_covers_the_manifest
tests/test_delta_pass.py::TestTheBaselineIsSufficient::test_every_page_carries_every_set_the_detector_diffs
tests/test_delta_pass.py::TestTheBaselineIsSufficient::test_the_stored_text_is_not_hashes
tests/test_delta_pass.py::TestTheBaselineIsSufficient::test_reconstruction_was_verified_against_the_stored_hashes
tests/test_delta_pass.py::TestTheBaselineIsSufficient::test_the_evidence_limitation_is_recorded
tests/test_delta_pass.py::TestTheHtmlChecksMirrorTheDetector::test_every_html_check_maps_to_a_real_flag_code
tests/test_delta_pass.py::TestTheHtmlChecksMirrorTheDetector::test_every_set_name_is_produced_by_extract_sets
tests/test_delta_pass.py::TestTheHtmlChecksMirrorTheDetector::test_a_newly_hidden_element_is_detected_against_an_empty_baseline
tests/test_delta_pass.py::TestTheHtmlChecksMirrorTheDetector::test_an_unchanged_hidden_element_produces_no_delta
tests/test_delta_pass.py::TestTheScheduleGuardIsReal::test_the_earliest_date_is_at_least_seven_days_after_the_snapshots
tests/test_delta_pass.py::TestTheScheduleGuardIsReal::test_running_before_the_earliest_date_is_refused
tests/test_delta_rehearsal.py::TestRehearsalModeExists::test_the_module_exposes_a_rehearse_entry_point
tests/test_delta_rehearsal.py::TestRehearsalModeExists::test_rehearsal_is_reachable_from_the_cli
tests/test_delta_rehearsal.py::TestRehearsalCompletes::test_report_has_every_expected_field
tests/test_delta_rehearsal.py::TestRehearsalCompletes::test_no_expected_field_is_none
tests/test_delta_rehearsal.py::TestRehearsalCompletes::test_pages_were_actually_loaded
tests/test_delta_rehearsal.py::TestRehearsalCompletes::test_every_pipeline_stage_is_reported
tests/test_delta_rehearsal.py::TestRehearsalCompletes::test_every_pipeline_stage_executed
tests/test_delta_rehearsal.py::TestRehearsalCompletes::test_the_result_is_labelled_not_a_measurement
tests/test_delta_rehearsal.py::TestRehearsalCompletes::test_a_zero_change_delta_produces_no_flags
tests/test_delta_rehearsal.py::TestRehearsalCompletes::test_the_gate_is_closed_for_identical_snapshots
tests/test_delta_rehearsal.py::TestTheGuardedChecksAreReachable::test_reachability_is_reported_for_both_guarded_checks
tests/test_delta_rehearsal.py::TestTheGuardedChecksAreReachable::test_the_guarded_check_is_reachable[new_domains]
tests/test_delta_rehearsal.py::TestTheGuardedChecksAreReachable::test_the_guarded_check_is_reachable[major_deletion]
tests/test_delta_rehearsal.py::TestTheGuardedChecksAreReachable::test_the_baseline_stores_text_not_only_line_hashes
tests/test_delta_rehearsal.py::TestTheGuardedChecksAreReachable::test_baseline_reconstruction_was_verified
tests/test_delta_rehearsal.py::TestEveryEmittableCodeIsProvenReachable::test_the_probe_covers_every_emittable_code
tests/test_delta_rehearsal.py::TestEveryEmittableCodeIsProvenReachable::test_the_probe_checks_nothing_that_cannot_be_emitted
tests/test_delta_rehearsal.py::TestEveryEmittableCodeIsProvenReachable::test_the_counts_are_asserted_equal_inside_the_probe
tests/test_delta_rehearsal.py::TestEveryEmittableCodeIsProvenReachable::test_every_code_is_reachable[credential_reference]
tests/test_delta_rehearsal.py::TestEveryEmittableCodeIsProvenReachable::test_every_code_is_reachable[data_uri_embed]
tests/test_delta_rehearsal.py::TestEveryEmittableCodeIsProvenReachable::test_every_code_is_reachable[data_uri_payload]
tests/test_delta_rehearsal.py::TestEveryEmittableCodeIsProvenReachable::test_every_code_is_reachable[hidden_content]
tests/test_delta_rehearsal.py::TestEveryEmittableCodeIsProvenReachable::test_every_code_is_reachable[iframe_detected]
tests/test_delta_rehearsal.py::TestEveryEmittableCodeIsProvenReachable::test_every_code_is_reachable[major_deletion]
tests/test_delta_rehearsal.py::TestEveryEmittableCodeIsProvenReachable::test_every_code_is_reachable[meta_refresh_redirect]
tests/test_delta_rehearsal.py::TestEveryEmittableCodeIsProvenReachable::test_every_code_is_reachable[new_base64]
tests/test_delta_rehearsal.py::TestEveryEmittableCodeIsProvenReachable::test_every_code_is_reachable[new_domains]
tests/test_delta_rehearsal.py::TestEveryEmittableCodeIsProvenReachable::test_every_code_is_reachable[new_exec_command]
tests/test_delta_rehearsal.py::TestEveryEmittableCodeIsProvenReachable::test_every_code_is_reachable[prompt_injection]
tests/test_delta_rehearsal.py::TestEveryEmittableCodeIsProvenReachable::test_every_code_is_reachable[suspicious_script]
tests/test_delta_rehearsal.py::TestEveryEmittableCodeIsProvenReachable::test_every_code_is_reachable[unicode_homoglyph]
tests/test_delta_rehearsal.py::TestRehearsalMakesNoNetworkRequest::test_fetch_url_is_never_called
tests/test_delta_rehearsal.py::TestRehearsalOutputIsConfined::test_documentation_surfaces_are_not_writable_targets
tests/test_delta_rehearsal.py::TestRehearsalOutputIsConfined::test_a_missing_source_is_reported_not_fetched
tests/test_dependency_floors.py::TestParseRequirement::test_extracts_name_and_floor[requests>=2.33.0-requests-2.33.0]
tests/test_dependency_floors.py::TestParseRequirement::test_extracts_name_and_floor[trafilatura>=2.0,<3-trafilatura-2.0]
tests/test_dependency_floors.py::TestParseRequirement::test_extracts_name_and_floor[confusable_homoglyphs>=3.3-confusable-homoglyphs-3.3]
tests/test_dependency_floors.py::TestParseRequirement::test_extracts_name_and_floor[requests[socks]>=2.33.0-requests-2.33.0]
tests/test_dependency_floors.py::TestParseRequirement::test_extracts_name_and_floor[tomli>=2.0; python_version < "3.11"-tomli-2.0]
tests/test_dependency_floors.py::TestParseRequirement::test_extracts_name_and_floor[pytest-cov-pytest-cov-None]
tests/test_dependency_floors.py::TestParseRequirement::test_extracts_name_and_floor[somepkg<3-somepkg-None]
tests/test_dependency_floors.py::TestVersionOrdering::test_orders_numerically_not_lexically
tests/test_dependency_floors.py::TestPythonSupportTargets::test_reads_minor_versions_from_classifiers
tests/test_dependency_floors.py::TestPythonSupportTargets::test_real_pyproject_declares_the_full_matrix
tests/test_dependency_floors.py::TestPythonSupportTargets::test_absent_classifiers_yield_no_targets
tests/test_dependency_floors.py::TestEvaluateSpecifier::test_evaluates_requires_python[>=3.9-version0-allowed]
tests/test_dependency_floors.py::TestEvaluateSpecifier::test_evaluates_requires_python[>=3.11-version1-excluded]
tests/test_dependency_floors.py::TestEvaluateSpecifier::test_evaluates_requires_python[!=3.9.0,!=3.9.1,>=3.9-version2-allowed]
tests/test_dependency_floors.py::TestEvaluateSpecifier::test_evaluates_requires_python[>=3.9,<3.13-version3-excluded]
tests/test_dependency_floors.py::TestEvaluateSpecifier::test_evaluates_requires_python[>=3.9,<3.13-version4-allowed]
tests/test_dependency_floors.py::TestEvaluateSpecifier::test_evaluates_requires_python[None-version5-allowed]
tests/test_dependency_floors.py::TestEvaluateSpecifier::test_evaluates_requires_python[-version6-allowed]
tests/test_dependency_floors.py::TestSpecifierFailsClosed::test_unparseable_clause_is_unevaluable_not_allowed[=>3.10]
tests/test_dependency_floors.py::TestSpecifierFailsClosed::test_unparseable_clause_is_unevaluable_not_allowed[garbage]
tests/test_dependency_floors.py::TestSpecifierFailsClosed::test_unparseable_clause_is_unevaluable_not_allowed[>=abc]
tests/test_dependency_floors.py::TestSpecifierFailsClosed::test_unparseable_clause_is_unevaluable_not_allowed[>= 3.10, ~~4.0]
tests/test_dependency_floors.py::TestSpecifierFailsClosed::test_unparseable_clause_is_unevaluable_not_allowed[\u22653.10]
tests/test_dependency_floors.py::TestSpecifierFailsClosed::test_unparseable_clause_is_unevaluable_not_allowed[3.10]
tests/test_dependency_floors.py::TestSpecifierFailsClosed::test_unevaluable_is_not_truthy_by_accident
tests/test_dependency_floors.py::TestSpecifierFailsClosed::test_floor_compatibility_reports_unevaluable_metadata
tests/test_dependency_floors.py::TestSpecifierFailsClosed::test_strict_version_parse_rejects_non_numeric
tests/test_dependency_floors.py::TestCollectRequirements::test_collects_from_every_table
tests/test_dependency_floors.py::TestDeclaredFloors::test_rfc3161_client_floor_excludes_cve_2026_33753
tests/test_dependency_floors.py::TestDeclaredFloors::test_every_runtime_dependency_declares_a_floor
tests/test_dependency_floors.py::TestDeclaredFloors::test_load_bearing_floors_are_at_or_above_their_known_good_minimum
tests/test_dependency_floors.py::TestDeclaredFloors::test_no_requirement_is_left_without_a_lower_bound
tests/test_detector.py::TestDetectionInputBound::test_input_beyond_cap_is_truncated
tests/test_detector.py::TestDetectionInputBound::test_payload_within_cap_still_flags
tests/test_detector.py::TestDetectionInputBound::test_large_adversarial_input_is_bounded_in_time
tests/test_detector.py::TestTextPatterns::test_detects_curl_command
tests/test_detector.py::TestTextPatterns::test_detects_pip_install
tests/test_detector.py::TestTextPatterns::test_detects_npm_install
tests/test_detector.py::TestTextPatterns::test_detects_eval
tests/test_detector.py::TestTextPatterns::test_detects_base64_strings
tests/test_detector.py::TestTextPatterns::test_detects_credential_references
tests/test_detector.py::TestTextPatterns::test_detects_new_domains
tests/test_detector.py::TestTextPatterns::test_detects_major_deletion
tests/test_detector.py::TestTextPatterns::test_no_flags_on_benign_change
tests/test_detector.py::TestTextPatterns::test_no_flags_on_empty_diff
tests/test_detector.py::TestHTMLComparison::test_new_suspicious_script_flagged
tests/test_detector.py::TestHTMLComparison::test_preexisting_script_NOT_flagged
tests/test_detector.py::TestHTMLComparison::test_new_iframe_flagged
tests/test_detector.py::TestHTMLComparison::test_preexisting_iframe_NOT_flagged
tests/test_detector.py::TestHTMLComparison::test_new_hidden_content_flagged
tests/test_detector.py::TestHTMLComparison::test_preexisting_hidden_content_NOT_flagged
tests/test_detector.py::TestHTMLComparison::test_first_scan_no_old_html
tests/test_detector.py::TestPromptInjection::test_detects_ignore_previous_instructions
tests/test_detector.py::TestPromptInjection::test_detects_disregard_system_prompt
tests/test_detector.py::TestPromptInjection::test_detects_forget_prior_rules
tests/test_detector.py::TestPromptInjection::test_detects_override_original_instructions
tests/test_detector.py::TestPromptInjection::test_detects_role_hijack_you_are_now
tests/test_detector.py::TestPromptInjection::test_detects_role_hijack_act_as
tests/test_detector.py::TestPromptInjection::test_detects_role_hijack_pretend
tests/test_detector.py::TestPromptInjection::test_detects_new_role_assignment
tests/test_detector.py::TestPromptInjection::test_no_false_positive_on_normal_docs
tests/test_detector.py::TestPromptInjection::test_no_false_positive_on_security_article
tests/test_detector.py::TestPromptInjection::test_severity_is_critical
tests/test_detector.py::TestPromptInjection::test_detects_german_injection
tests/test_detector.py::TestPromptInjection::test_detects_spanish_injection
tests/test_detector.py::TestPromptInjection::test_detects_french_injection
tests/test_detector.py::TestPromptInjection::test_detects_russian_injection
tests/test_detector.py::TestPromptInjection::test_detects_base64_encoded_injection
tests/test_detector.py::TestPromptInjection::test_detects_spaced_out_letters
tests/test_detector.py::TestPromptInjection::test_detects_all_caps_commands
tests/test_detector.py::TestPromptInjection::test_detects_fake_system_delimiters
tests/test_detector.py::TestPromptInjection::test_detects_temporal_override
tests/test_detector.py::TestPromptInjection::test_detects_restriction_removal
tests/test_detector.py::TestUnicodeHomoglyphs::test_detects_cyrillic_a
tests/test_detector.py::TestUnicodeHomoglyphs::test_detects_cyrillic_o
tests/test_detector.py::TestUnicodeHomoglyphs::test_detects_cyrillic_c
tests/test_detector.py::TestUnicodeHomoglyphs::test_detects_greek_omicron
tests/test_detector.py::TestUnicodeHomoglyphs::test_no_false_positive_on_pure_ascii
tests/test_detector.py::TestUnicodeHomoglyphs::test_no_false_positive_on_legitimate_unicode
tests/test_detector.py::TestUnicodeHomoglyphs::test_evidence_includes_codepoint
tests/test_detector.py::TestUnicodeHomoglyphs::test_detects_osage_confusable_unicode_10
tests/test_detector.py::TestUnicodeHomoglyphs::test_detects_cherokee_confusable
tests/test_detector.py::TestDataURIDetection::test_detects_data_uri_text_html
tests/test_detector.py::TestDataURIDetection::test_detects_data_uri_javascript
tests/test_detector.py::TestDataURIDetection::test_no_false_positive_on_data_uri_image
tests/test_detector.py::TestDataURIDetection::test_no_false_positive_on_word_data
tests/test_detector.py::TestMetaRefreshHTML::test_detects_new_meta_refresh
tests/test_detector.py::TestMetaRefreshHTML::test_preexisting_meta_refresh_NOT_flagged
tests/test_detector.py::TestMetaRefreshHTML::test_detects_meta_refresh_case_insensitive
tests/test_detector.py::TestDataURIEmbedHTML::test_detects_new_data_uri_iframe
tests/test_detector.py::TestDataURIEmbedHTML::test_preexisting_data_uri_iframe_NOT_flagged
tests/test_detector.py::TestDataURIEmbedHTML::test_detects_data_uri_embed_tag
tests/test_detector.py::TestDataURIEmbedHTML::test_data_uri_embed_severity_critical
tests/test_detector.py::TestPatternCompilationSafety::test_malformed_pattern_raises_descriptive_error
tests/test_detector.py::TestBase64HexFiltering::test_sha256_hex_digest_does_not_flag
tests/test_detector.py::TestBase64HexFiltering::test_url_path_does_not_flag_as_base64
tests/test_detector.py::TestBase64HexFiltering::test_genuine_base64_instruction_still_flags
tests/test_detector.py::TestCanonicalisation::test_html_comment_injection_detected
tests/test_detector.py::TestCanonicalisation::test_html_comment_benign_not_flagged
tests/test_detector.py::TestCanonicalisation::test_html_comment_with_command
tests/test_detector.py::TestCanonicalisation::test_reversed_text_with_command_detected
tests/test_detector.py::TestCanonicalisation::test_reversed_normal_text_not_flagged
tests/test_detector.py::TestCanonicalisation::test_reversed_text_very_long_span_capped
tests/test_detector.py::TestCanonicalisation::test_rot13_command_detected
tests/test_detector.py::TestCanonicalisation::test_rot13_injection_detected
tests/test_detector.py::TestCanonicalisation::test_rot13_normal_text_not_flagged
tests/test_detector.py::TestCanonicalisation::test_rot13_very_long_span_capped
tests/test_detector.py::TestCanonicalisation::test_deeply_nested_html_comments
tests/test_detector.py::TestCanonicalisation::test_total_decoded_cap_respected
tests/test_detector.py::TestSRIHashExclusion::test_sha512_sri_hash_not_flagged
tests/test_detector.py::TestSRIHashExclusion::test_sha384_sri_hash_not_flagged
tests/test_detector.py::TestSRIHashExclusion::test_sha256_sri_prefix_not_flagged
tests/test_detector.py::TestSRIHashExclusion::test_genuine_base64_without_sri_still_flagged
tests/test_detector.py::TestSRIHashExclusion::test_is_sri_hash_direct
tests/test_detector.py::TestSRIHashExclusion::test_b08_sri_hash_now_clean
tests/test_detector.py::TestSeverity::test_severity_ranking
tests/test_detector.py::TestSeverity::test_severity_empty
tests/test_detector.py::TestFlagExplanations::test_every_emitted_code_has_plain_language_entry
tests/test_detector.py::TestFlagExplanations::test_explanations_are_plain_text_not_the_raw_code
tests/test_detector.py::TestFlagExplanations::test_explain_falls_back_to_code_when_unknown
tests/test_differ.py::TestContentChanged::test_same_hashes
tests/test_differ.py::TestContentChanged::test_different_hashes
tests/test_differ.py::TestContentChanged::test_empty_hashes
tests/test_differ.py::TestGenerateDiff::test_shows_added_lines
tests/test_differ.py::TestGenerateDiff::test_shows_removed_lines
tests/test_differ.py::TestGenerateDiff::test_shows_url_in_header
tests/test_differ.py::TestGenerateDiff::test_identical_content_empty_diff
tests/test_differ.py::TestGenerateDiff::test_empty_to_content
tests/test_e2e.py::TestEndToEnd::test_full_pipeline_detects_change_and_creates_alert
tests/test_e2e.py::TestEndToEnd::test_unchanged_content_no_alert
tests/test_e2e.py::TestEndToEnd::test_json_output_structure
tests/test_efficacy_harness.py::TestWilsonInterval::test_matches_published_intervals[21-25-0.653-0.936]
tests/test_efficacy_harness.py::TestWilsonInterval::test_matches_published_intervals[21-35-0.436-0.744]
tests/test_efficacy_harness.py::TestWilsonInterval::test_matches_published_intervals[11-25-0.267-0.629]
tests/test_efficacy_harness.py::TestWilsonInterval::test_matches_published_intervals[9-10-0.596-0.982]
tests/test_efficacy_harness.py::TestWilsonInterval::test_matches_published_intervals[9-12-0.468-0.911]
tests/test_efficacy_harness.py::TestWilsonInterval::test_matches_published_intervals[6-6-0.61-1.0]
tests/test_efficacy_harness.py::TestWilsonInterval::test_matches_published_intervals[0-38-0.0-0.092]
tests/test_efficacy_harness.py::TestWilsonInterval::test_no_data_is_not_certainty
tests/test_efficacy_harness.py::TestWilsonInterval::test_interval_stays_inside_unit_range
tests/test_efficacy_harness.py::TestGateVerdict::test_point_clears_but_lower_bound_does_not
tests/test_efficacy_harness.py::TestGateVerdict::test_demonstrated_requires_lower_bound
tests/test_efficacy_harness.py::TestGateVerdict::test_no_data_is_not_demonstrated
tests/test_efficacy_harness.py::TestEveryCorpusReportCarriesIntervals::test_html_report_prints_confidence_intervals
tests/test_efficacy_harness.py::TestEveryCorpusReportCarriesIntervals::test_html_report_returns_intervals_for_downstream_use
tests/test_fetcher.py::TestStripEscapeSequences::test_strips_csi
tests/test_fetcher.py::TestStripEscapeSequences::test_strips_osc_bel_terminated
tests/test_fetcher.py::TestStripEscapeSequences::test_strips_osc_st_terminated
tests/test_fetcher.py::TestStripEscapeSequences::test_strips_dcs
tests/test_fetcher.py::TestStripEscapeSequences::test_strips_c1_csi
tests/test_fetcher.py::TestStripEscapeSequences::test_strips_c1_osc
tests/test_fetcher.py::TestStripEscapeSequences::test_strips_fe_sequences
tests/test_fetcher.py::TestStripEscapeSequences::test_preserves_normal_text
tests/test_fetcher.py::TestStripEscapeSequences::test_empty_string
tests/test_fetcher.py::TestNormaliseWhitespace::test_collapses_spaces
tests/test_fetcher.py::TestNormaliseWhitespace::test_strips_blank_lines
tests/test_fetcher.py::TestNormaliseWhitespace::test_strips_trailing_whitespace
tests/test_fetcher.py::TestNormaliseWhitespace::test_empty_string
tests/test_fetcher.py::TestFetchUrlSSRF::test_blocks_private_ip
tests/test_fetcher.py::TestFetchUrlSSRF::test_blocks_loopback
tests/test_fetcher.py::TestFetchUrlSSRF::test_blocks_metadata_endpoint
tests/test_fetcher.py::TestFetchUrlSSRF::test_blocks_file_scheme
tests/test_fetcher.py::TestFetchUrlSSRF::test_blocks_ipv4_mapped_ipv6
tests/test_fetcher.py::TestFetchUrlHTTP::test_fetches_html_page
tests/test_fetcher.py::TestFetchUrlHTTP::test_handles_http_404
tests/test_fetcher.py::TestFetchUrlHTTP::test_handles_http_500
tests/test_fetcher.py::TestFetchUrlHTTP::test_handles_connection_error
tests/test_fetcher.py::TestFetchUrlHTTP::test_enforces_size_limit
tests/test_fetcher.py::TestFetchUrlHTTP::test_follows_redirects_safely
tests/test_fetcher.py::TestFetchUrlHTTP::test_blocks_redirect_to_private_ip
tests/test_fetcher.py::TestFetchUrlHTTP::test_limits_redirect_count
tests/test_fetcher.py::TestFetchUrlHTTP::test_content_hash_is_deterministic
tests/test_fetcher.py::TestFetchUrlHTTP::test_strips_escape_sequences_from_content
tests/test_fetcher.py::TestReDoSProtection::test_catastrophic_backtracking_bounded
tests/test_figure_rules.py::TestTheHarnessIsActuallyReachable::test_harness_yields_proportions
tests/test_figure_rules.py::TestTheHarnessIsActuallyReachable::test_harness_includes_the_headline_figures
tests/test_figure_rules.py::TestTheHarnessIsActuallyReachable::test_harness_includes_base_rate_figures
tests/test_figure_rules.py::TestTheHarnessIsActuallyReachable::test_a_stale_pair_is_not_in_the_allowed_set
tests/test_figure_rules.py::TestExtraction::test_extracts_k_n_and_percentage
tests/test_figure_rules.py::TestExtraction::test_extracts_several_from_one_line
tests/test_figure_rules.py::TestExtraction::test_ignores_bare_fractions_without_a_percentage
tests/test_figure_rules.py::TestExtraction::test_records_the_line_number
tests/test_figure_rules.py::TestArithmetic::test_percentage_inconsistent_with_the_fraction_is_flagged
tests/test_figure_rules.py::TestArithmetic::test_consistent_percentage_passes_arithmetic
tests/test_figure_rules.py::TestArithmetic::test_rounding_at_one_decimal_is_tolerated
tests/test_figure_rules.py::TestCurrency::test_the_real_drift_is_caught
tests/test_figure_rules.py::TestCurrency::test_a_current_figure_passes
tests/test_figure_rules.py::TestCurrency::test_several_stale_figures_are_each_reported
tests/test_figure_rules.py::TestCorrespondenceNotMembership::test_a_current_figure_under_the_wrong_label_is_caught
tests/test_figure_rules.py::TestCorrespondenceNotMembership::test_the_same_figure_under_its_right_label_passes
tests/test_figure_rules.py::TestCorrespondenceNotMembership::test_precision_published_as_recall_is_caught
tests/test_figure_rules.py::TestCorrespondenceNotMembership::test_evasive_recall_under_its_own_label_passes
tests/test_figure_rules.py::TestCorrespondenceNotMembership::test_a_figure_with_two_valid_labels_passes_under_either
tests/test_figure_rules.py::TestCorrespondenceNotMembership::test_prose_naming_no_metric_is_not_flagged
tests/test_figure_rules.py::TestCorrespondenceNotMembership::test_unlabelled_figures_are_counted_so_coverage_is_honest
tests/test_figure_rules.py::TestPercentageMatchesItsOwnFraction::test_a_wrong_percentage_is_caught
tests/test_figure_rules.py::TestPercentageMatchesItsOwnFraction::test_the_right_percentage_passes
tests/test_figure_rules.py::TestTheFloorIsDerivedNotPicked::test_there_is_no_global_floor_against_the_deduplicated_set
tests/test_figure_rules.py::TestTheFloorIsDerivedNotPicked::test_healthy_overlapping_output_is_not_rejected
tests/test_figure_rules.py::TestTheFloorIsDerivedNotPicked::test_every_harness_command_has_an_expectation
tests/test_figure_rules.py::TestTheFloorIsDerivedNotPicked::test_a_partial_parse_of_one_command_fails_rather_than_passing
tests/test_figure_rules.py::TestHistoricalExemption::test_figures_inside_an_exempt_region_are_allowed
tests/test_figure_rules.py::TestHistoricalExemption::test_figures_after_the_region_closes_are_checked_again
tests/test_figure_rules.py::TestHistoricalExemption::test_an_exempt_region_without_a_reason_is_a_violation
tests/test_figure_rules.py::TestHistoricalExemption::test_an_unclosed_exempt_region_is_a_violation
tests/test_figure_rules.py::TestHistoricalExemption::test_an_unclosed_region_does_not_swallow_later_drift
tests/test_figure_rules.py::TestHistoricalExemption::test_a_stray_end_marker_is_a_violation
tests/test_figure_rules.py::TestTheRealSurfaces::test_surface_carries_no_drifted_figure[README.md]
tests/test_figure_rules.py::TestTheRealSurfaces::test_surface_carries_no_drifted_figure[docs/llms.txt]
tests/test_figure_rules.py::TestTheRealSurfaces::test_surface_carries_no_drifted_figure[docs/LAUNCH-FACTS.md]
tests/test_figure_rules.py::TestTheRealSurfaces::test_surface_carries_no_drifted_figure[PATTERNS.md]
tests/test_figure_rules.py::TestTheRealSurfaces::test_surface_carries_no_drifted_figure[SHIP-READINESS.md]
tests/test_figure_rules.py::TestTheRealSurfaces::test_surface_carries_no_drifted_figure[CHANGELOG.md]
tests/test_formatter.py::TestURLTable::test_empty_table
tests/test_formatter.py::TestURLTable::test_table_with_urls
tests/test_formatter.py::TestURLTable::test_truncates_long_urls
tests/test_formatter.py::TestScanResult::test_unchanged
tests/test_formatter.py::TestScanResult::test_error
tests/test_formatter.py::TestScanResult::test_changed_with_flags
tests/test_formatter.py::TestScanResult::test_changed_no_flags
tests/test_formatter.py::TestScanResult::test_changed_flags_show_plain_language_and_next_step
tests/test_formatter.py::TestScanResult::test_progress_prefix_shown
tests/test_formatter.py::TestScanSummary::test_all_unchanged
tests/test_formatter.py::TestScanSummary::test_with_alerts_and_errors
tests/test_formatter.py::TestAlertDetail::test_renders_string_flags
tests/test_formatter.py::TestAlertDetail::test_alert_detail_shows_plain_language_and_next_step
tests/test_formatter.py::TestAlertDetail::test_renders_without_diff
tests/test_formatter.py::TestAlertDetail::test_escapes_malicious_diff_content
tests/test_formatter.py::TestAlertDetail::test_truncates_long_diff
tests/test_formatter.py::TestHistory::test_empty_history
tests/test_formatter.py::TestHistory::test_history_with_entries
tests/test_formatter.py::TestHistory::test_history_with_error
tests/test_formatter.py::TestSeverityRankConsistency::test_formatter_uses_detector_severity_rank
tests/test_formatter.py::TestStatusIcon::test_no_alerts
tests/test_formatter.py::TestStatusIcon::test_with_alerts
tests/test_formatter.py::TestStatusIcon::test_never_checked
tests/test_fp_adaptation.py::test_demoted_after_two_dismissals
tests/test_fp_adaptation.py::test_confirm_cancels_demotion
tests/test_fp_adaptation.py::test_reset_clears_feedback
tests/test_fp_adaptation.py::test_list_feedback_groups
tests/test_fp_adaptation.py::test_remove_url_clears_feedback
tests/test_fp_adaptation.py::test_record_rejects_bad_decision
tests/test_fp_adaptation.py::test_format_alert_detail_annotates_only_demoted
tests/test_fp_adaptation.py::test_format_scan_result_annotates_demoted
tests/test_fp_adaptation.py::test_cli_dismiss_records_feedback
tests/test_fp_adaptation.py::test_cli_alert_shows_demotion_after_threshold
tests/test_fp_adaptation.py::test_cli_confirm_cancels_demotion
tests/test_fp_adaptation.py::test_cli_feedback_list_and_reset
tests/test_gate_table.py::test_the_workflow_parser_finds_the_workflows_that_exist
tests/test_gate_table.py::test_the_ci_job_parser_finds_the_jobs_that_exist
tests/test_gate_table.py::test_the_job_parser_does_not_mistake_on_or_permissions_keys_for_jobs
tests/test_gate_table.py::test_the_script_parser_finds_the_scripts_that_exist
tests/test_gate_table.py::test_the_table_has_rows
tests/test_gate_table.py::test_an_unclosed_table_region_is_a_failure_not_a_silent_exemption
tests/test_gate_table.py::test_every_ci_job_appears_in_the_gate_table
tests/test_gate_table.py::test_every_tracked_script_is_either_a_gate_or_declared_not_one
tests/test_gate_table.py::test_every_declared_non_gate_carries_a_reason
tests/test_gate_table.py::test_the_table_has_the_columns_the_checks_read
tests/test_gate_table.py::test_every_gate_row_is_complete
tests/test_gate_table.py::test_every_gate_status_uses_the_controlled_vocabulary
tests/test_gate_table.py::test_the_hash_parser_finds_a_hash_for_every_job
tests/test_gate_table.py::test_no_job_has_changed_since_its_negative_control
tests/test_gate_table.py::test_a_job_whose_hash_drifted_may_not_claim_red_observed
tests/test_gate_table.py::test_a_comment_edit_does_not_move_a_job_hash
tests/test_gate_table.py::test_the_trigger_block_is_part_of_every_job_hash
tests/test_gate_table.py::test_an_executable_change_does_move_a_job_hash
tests/test_gate_table.py::test_a_step_rename_does_not_move_a_job_hash
tests/test_gate_table.py::test_an_action_input_named_name_does_move_a_job_hash
tests/test_gate_table.py::test_a_red_observed_claim_carries_checkable_evidence
tests/test_gate_table.py::test_the_negative_control_rule_is_stated_beside_the_table
tests/test_hidden_content.py::test_technique_detection_matches_its_bucket[inline display:none]
tests/test_hidden_content.py::test_technique_detection_matches_its_bucket[inline display: none]
tests/test_hidden_content.py::test_technique_detection_matches_its_bucket[inline visibility:hidden]
tests/test_hidden_content.py::test_technique_detection_matches_its_bucket[UPPERCASE DISPLAY:NONE]
tests/test_hidden_content.py::test_technique_detection_matches_its_bucket[mixed-case Display:None]
tests/test_hidden_content.py::test_technique_detection_matches_its_bucket[off-screen position]
tests/test_hidden_content.py::test_technique_detection_matches_its_bucket[opacity:0]
tests/test_hidden_content.py::test_technique_detection_matches_its_bucket[font-size:0]
tests/test_hidden_content.py::test_technique_detection_matches_its_bucket[height:0;overflow:hidden]
tests/test_hidden_content.py::test_technique_detection_matches_its_bucket[HTML hidden attribute]
tests/test_hidden_content.py::test_technique_detection_matches_its_bucket[<style> block rule]
tests/test_hidden_content.py::test_technique_detection_matches_its_bucket[clip-path inset(50%)]
tests/test_hidden_content.py::test_technique_detection_matches_its_bucket[text-indent:-9999px]
tests/test_hidden_content.py::test_technique_detection_matches_its_bucket[aria-hidden]
tests/test_hidden_content.py::test_technique_detection_matches_its_bucket[external stylesheet]
tests/test_hidden_content.py::TestBoundaryIsDocumentedNotAccidental::test_external_stylesheet_boundary_is_in_the_docstring
tests/test_hidden_content.py::TestHiddenTextIsActuallyReturned::test_returns_the_concealed_text
tests/test_hidden_content.py::TestHiddenTextIsActuallyReturned::test_empty_hidden_element_yields_nothing
tests/test_hiding_taxonomy.py::TestDocumentAndCodeAgree::test_the_document_actually_has_a_bucket_table
tests/test_hiding_taxonomy.py::TestDocumentAndCodeAgree::test_every_documented_technique_exists_in_the_code_table
tests/test_hiding_taxonomy.py::TestDocumentAndCodeAgree::test_every_code_technique_is_documented
tests/test_hiding_taxonomy.py::TestDocumentAndCodeAgree::test_bucket_matches_the_document[aria-hidden]
tests/test_hiding_taxonomy.py::TestDocumentAndCodeAgree::test_bucket_matches_the_document[clip-path-inset]
tests/test_hiding_taxonomy.py::TestDocumentAndCodeAgree::test_bucket_matches_the_document[display:none]
tests/test_hiding_taxonomy.py::TestDocumentAndCodeAgree::test_bucket_matches_the_document[font-size:0]
tests/test_hiding_taxonomy.py::TestDocumentAndCodeAgree::test_bucket_matches_the_document[html-hidden-attr]
tests/test_hiding_taxonomy.py::TestDocumentAndCodeAgree::test_bucket_matches_the_document[offscreen-position]
tests/test_hiding_taxonomy.py::TestDocumentAndCodeAgree::test_bucket_matches_the_document[opacity:0]
tests/test_hiding_taxonomy.py::TestDocumentAndCodeAgree::test_bucket_matches_the_document[text-indent-negative]
tests/test_hiding_taxonomy.py::TestDocumentAndCodeAgree::test_bucket_matches_the_document[visibility:hidden]
tests/test_hiding_taxonomy.py::TestDocumentAndCodeAgree::test_bucket_matches_the_document[zero-box-clipped]
tests/test_hiding_taxonomy.py::TestDocumentAndCodeAgree::test_buckets_are_valid_letters
tests/test_hiding_taxonomy.py::TestTheAssignmentsTheBaseRateChanged::test_html_hidden_attribute_is_not_flagged
tests/test_hiding_taxonomy.py::TestTheAssignmentsTheBaseRateChanged::test_offscreen_positioning_is_not_flagged
tests/test_hiding_taxonomy.py::TestTheAssignmentsTheBaseRateChanged::test_offscreen_and_text_indent_share_a_bucket
tests/test_hiding_taxonomy.py::TestTheAssignmentsTheBaseRateChanged::test_display_none_is_still_flagged
tests/test_hiding_taxonomy.py::TestBehaviourFollowsTheTable::test_hidden_attribute_content_is_not_extracted
tests/test_hiding_taxonomy.py::TestBehaviourFollowsTheTable::test_offscreen_content_is_not_extracted
tests/test_hiding_taxonomy.py::TestBehaviourFollowsTheTable::test_display_none_content_is_still_extracted
tests/test_hiding_taxonomy.py::TestBehaviourFollowsTheTable::test_canonical_sr_only_ruleset_is_not_extracted
tests/test_ledger.py::TestHashSpec::test_entry_hash_is_deterministic
tests/test_ledger.py::TestHashSpec::test_entry_hash_depends_on_every_field
tests/test_ledger.py::TestHashSpec::test_status_code_none_is_stable
tests/test_ledger.py::TestHashSpec::test_chain_hash_links_prev_and_entry
tests/test_ledger.py::TestHashSpec::test_no_field_boundary_ambiguity
tests/test_ledger.py::TestVerifyChain::test_empty_chain_is_valid
tests/test_ledger.py::TestVerifyChain::test_well_formed_chain_verifies
tests/test_ledger.py::TestVerifyChain::test_first_entry_must_start_at_genesis
tests/test_ledger.py::TestVerifyChain::test_detects_tampered_content_hash
tests/test_ledger.py::TestVerifyChain::test_detects_broken_link
tests/test_ledger.py::TestVerifyChain::test_detects_deleted_middle_entry
tests/test_ledger.py::TestVerifyChain::test_input_order_independent
tests/test_ledger.py::TestLedgerStore::test_content_snapshot_appends_ledger_entry
tests/test_ledger.py::TestLedgerStore::test_error_snapshot_does_not_append
tests/test_ledger.py::TestLedgerStore::test_ledger_records_url_string
tests/test_ledger.py::TestLedgerStore::test_two_snapshots_chain_together
tests/test_ledger.py::TestLedgerStore::test_live_ledger_verifies
tests/test_ledger.py::TestLedgerStore::test_ledger_survives_snapshot_pruning
tests/test_ledger.py::TestLedgerStore::test_verify_ledger_detects_db_tampering
tests/test_ledger.py::TestLedgerStore::test_verify_ledger_detects_row_deletion
tests/test_ledger.py::TestLedgerStore::test_export_is_independently_verifiable
tests/test_ledger.py::TestLedgerStore::test_export_ordered_by_seq
tests/test_ledger.py::TestLedgerStore::test_empty_ledger_count_and_verify
tests/test_ledger.py::TestAnchoring::test_verify_reports_head
tests/test_ledger.py::TestAnchoring::test_empty_ledger_head_is_none
tests/test_ledger.py::TestAnchoring::test_earlier_head_still_present_after_more_entries
tests/test_ledger.py::TestStreaming::test_verify_stream_accepts_a_generator
tests/test_ledger.py::TestStreaming::test_verify_stream_detects_tamper_in_order
tests/test_ledger.py::TestStreaming::test_verify_ledger_streams_and_stays_correct
tests/test_ledger.py::TestStreaming::test_export_to_file_streams_and_reverifies
tests/test_ledger.py::TestVerifyCommand::test_verify_empty_db_is_ok
tests/test_ledger.py::TestVerifyCommand::test_verify_clean_ledger
tests/test_ledger.py::TestVerifyCommand::test_verify_tampered_ledger_exits_nonzero
tests/test_ledger.py::TestLedgerCommand::test_ledger_empty
tests/test_ledger.py::TestLedgerCommand::test_ledger_lists_entries
tests/test_ledger.py::TestLedgerCommand::test_ledger_export_writes_verifiable_json
tests/test_ledger.py::TestLedgerCommand::test_ledger_export_to_unwritable_path_errors
tests/test_ledger.py::TestVerifyAgainstAnchor::test_verify_shows_head
tests/test_ledger.py::TestVerifyAgainstAnchor::test_verify_against_matching_head_ok
tests/test_ledger.py::TestVerifyAgainstAnchor::test_verify_against_divergent_head_fails
tests/test_parser.py::test_extract_markdown_links
tests/test_parser.py::test_extract_raw_urls
tests/test_parser.py::test_extract_multiple_urls
tests/test_parser.py::test_deduplicates_urls
tests/test_parser.py::test_rejects_private_ips
tests/test_parser.py::test_rejects_non_http_schemes
tests/test_parser.py::test_strips_trailing_punctuation
tests/test_parser.py::test_extract_from_skill_md_file
tests/test_parser.py::test_extract_from_json_config
tests/test_parser.py::test_extract_from_url_list
tests/test_parser.py::test_extract_from_yaml_config
tests/test_parser.py::test_extract_from_yml_extension
tests/test_parser.py::test_extract_yaml_with_list_values
tests/test_parser.py::test_extract_yaml_with_invalid_yaml
tests/test_parser.py::test_extract_json_with_invalid_json
tests/test_parser.py::test_extract_json_with_nested_lists
tests/test_parser.py::test_fallback_to_markdown_for_unknown_extension
tests/test_parser.py::test_extract_url_with_balanced_parens
tests/test_parser.py::test_extract_url_with_nested_parens
tests/test_parser.py::test_file_not_found
tests/test_parser.py::test_empty_file
tests/test_parser.py::test_source_fingerprint_detects_change
tests/test_published_claims.py::TestEveryPublicSurfaceIsClean::test_surface_has_no_violations[README.md]
tests/test_published_claims.py::TestEveryPublicSurfaceIsClean::test_surface_has_no_violations[docs/llms.txt]
tests/test_published_claims.py::TestEveryPublicSurfaceIsClean::test_surface_has_no_violations[docs/index.html]
tests/test_published_claims.py::TestEveryPublicSurfaceIsClean::test_surface_has_no_violations[SHIP-READINESS.md]
tests/test_published_claims.py::TestTheRulesCanActuallyFire::test_compressed_quantifier_rule_fires
tests/test_published_claims.py::TestTheRulesCanActuallyFire::test_mitigation_overclaim_rule_fires
tests/test_published_claims.py::TestTheRulesCanActuallyFire::test_reworded_continuous_rule_fires
tests/test_published_claims.py::TestTheRulesCanActuallyFire::test_unsourced_attribution_rule_fires
tests/test_readiness_consistency.py::test_nonpassing_condition_cannot_coexist_with_all_one_to_four_pass
tests/test_readiness_consistency.py::test_confidence_bound_rule_is_directional
tests/test_readiness_consistency.py::test_retracted_original_ten_claim_is_not_current
tests/test_readiness_consistency.py::test_current_evasive_corpus_total_and_families_are_authoritative
tests/test_readiness_consistency.py::test_ledger_sections_agree_with_row_statuses
tests/test_readiness_consistency.py::test_structured_status_matches_harness_and_current_scoreboard
tests/test_sarif.py::test_empty_sarif_is_well_formed
tests/test_sarif.py::test_sarif_maps_flags_to_results_and_levels
tests/test_ssrf.py::TestSSRFValidation::test_allows_public_https
tests/test_ssrf.py::TestSSRFValidation::test_allows_public_http
tests/test_ssrf.py::TestSSRFValidation::test_blocks_private_10
tests/test_ssrf.py::TestSSRFValidation::test_blocks_private_172
tests/test_ssrf.py::TestSSRFValidation::test_blocks_private_192
tests/test_ssrf.py::TestSSRFValidation::test_blocks_loopback
tests/test_ssrf.py::TestSSRFValidation::test_blocks_link_local
tests/test_ssrf.py::TestSSRFValidation::test_blocks_localhost
tests/test_ssrf.py::TestSSRFValidation::test_blocks_file_scheme
tests/test_ssrf.py::TestSSRFValidation::test_blocks_ftp_scheme
tests/test_ssrf.py::TestSSRFValidation::test_blocks_no_hostname
tests/test_ssrf.py::TestSSRFValidation::test_blocks_zero_ip
tests/test_ssrf.py::TestSSRFValidation::test_blocks_ipv4_mapped_ipv6_loopback
tests/test_ssrf.py::TestSSRFValidation::test_blocks_credentials_in_url
tests/test_ssrf.py::TestSSRFValidation::test_blocks_ipv6_multicast
tests/test_ssrf.py::TestSSRFValidation::test_blocks_6to4
tests/test_ssrf.py::TestSSRFValidation::test_blocks_nat64
tests/test_ssrf.py::TestSSRFValidation::test_blocks_decimal_ip
tests/test_ssrf.py::TestSSRFValidation::test_blocks_hex_ip
tests/test_ssrf.py::TestSSRFValidation::test_handles_unicode_hostname_error
tests/test_ssrf.py::TestSSRFReservedRanges::test_blocks_additional_reserved[http://240.0.0.1/]
tests/test_ssrf.py::TestSSRFReservedRanges::test_blocks_additional_reserved[http://255.255.255.255/]
tests/test_ssrf.py::TestSSRFReservedRanges::test_blocks_additional_reserved[http://192.0.0.1/]
tests/test_ssrf.py::TestSSRFReservedRanges::test_blocks_additional_reserved[http://198.18.0.1/]
tests/test_ssrf.py::TestSSRFReservedRanges::test_blocks_additional_reserved[http://192.0.2.5/]
tests/test_ssrf.py::TestSSRFReservedRanges::test_blocks_additional_reserved[http://203.0.113.9/]
tests/test_ssrf.py::TestSSRFReservedRanges::test_blocks_additional_reserved[http://[2001:db8::1]/]
tests/test_ssrf.py::TestSSRFReservedRanges::test_allows_global_ip_literal
tests/test_store.py::TestURLStorage::test_add_url
tests/test_store.py::TestURLStorage::test_add_duplicate_url
tests/test_store.py::TestURLStorage::test_get_urls
tests/test_store.py::TestURLStorage::test_remove_url
tests/test_store.py::TestURLStorage::test_remove_nonexistent
tests/test_store.py::TestURLStorage::test_url_count
tests/test_store.py::TestSnapshots::test_add_and_get_snapshot
tests/test_store.py::TestSnapshots::test_stores_raw_html
tests/test_store.py::TestSnapshots::test_latest_snapshot_is_most_recent
tests/test_store.py::TestSnapshots::test_snapshot_history
tests/test_store.py::TestSnapshots::test_no_snapshot
tests/test_store.py::TestSnapshots::test_get_latest_good_snapshot_skips_errors
tests/test_store.py::TestSnapshots::test_error_snapshot
tests/test_store.py::TestAlerts::test_add_and_get_alert
tests/test_store.py::TestAlerts::test_mark_reviewed
tests/test_store.py::TestAlerts::test_unreviewed_filter
tests/test_store.py::TestAlerts::test_get_alerts_filtered_by_url_id
tests/test_store.py::TestAlerts::test_remove_url_cascades
tests/test_store.py::TestStatusMethods::test_last_scan_time_empty
tests/test_store.py::TestStatusMethods::test_last_scan_time_after_snapshot
tests/test_store.py::TestStatusMethods::test_pending_alert_count_zero
tests/test_store.py::TestStatusMethods::test_pending_alert_count
tests/test_store.py::TestContextManager::test_store_as_context_manager
tests/test_store.py::TestSources::test_record_and_get_source
tests/test_store.py::TestSources::test_record_source_upserts_not_duplicates
tests/test_store.py::TestSources::test_get_sources_empty
tests/test_threading.py::TestThreadSafety::test_getaddrinfo_not_patched_after_fetch
tests/test_threading.py::TestThreadSafety::test_adapter_uses_url_rewriting_not_global_patch
tests/test_verify_capture.py::test_clean_copy_exits_zero
tests/test_verify_capture.py::test_absent_copy_exits_nonzero_and_says_it_cannot_find_it
tests/test_verify_capture.py::test_corrupt_copy_exits_nonzero_with_a_different_message
tests/test_verify_capture.py::test_absent_and_corrupt_do_not_share_an_exit_code
tests/test_verify_capture.py::test_corruption_is_localised_to_the_offending_url
tests/test_verify_capture.py::test_corrupt_wins_over_missing_when_both_occur
tests/test_verify_capture.py::test_every_recorded_copy_is_checked_not_just_the_first
tests/test_verify_capture.py::test_an_unusable_manifest_is_not_a_pass
tests/test_verify_capture.py::test_a_missing_manifest_is_not_a_pass
tests/test_verify_capture.py::test_a_manifest_recording_no_copies_is_not_a_pass
tests/test_verify_capture.py::test_a_manifest_with_malformed_copies_is_unusable[copies0]
tests/test_verify_capture.py::test_a_manifest_with_malformed_copies_is_unusable[copies1]
tests/test_verify_capture.py::test_a_manifest_with_malformed_copies_is_unusable[copies2]
tests/test_verify_capture.py::test_a_manifest_with_malformed_copies_is_unusable[copies3]
tests/test_verify_capture.py::test_page_sample_is_deterministic
tests/test_verify_capture.py::test_the_real_manifest_records_where_every_copy_lives
tests/test_verify_capture.py::test_the_real_capture_verifies_on_a_machine_that_holds_it
tests/test_verify_capture.py::test_the_real_manifest_copies_are_not_all_on_one_medium
tests/test_verify_capture.py::test_capture_source_refuses_a_corrupt_copy
tests/test_verify_capture.py::test_capture_source_says_cannot_find_it_when_no_copy_exists
tests/test_verify_capture.py::test_capture_candidates_are_driven_by_the_manifest
tests/test_verify_capture.py::test_an_explicit_path_that_is_a_recorded_copy_is_verified
tests/test_verify_capture.py::test_an_unrecorded_explicit_path_loads_but_is_flagged_unverified
tests/test_verify_capture.py::test_the_four_level_scratchpad_glob_is_preserved

639 tests collected in 2.28s
collection_exit=0
=== FINAL RUFF ===
All checks passed!
ruff_exit=0
=== FINAL MYPY ===
Success: no issues found in 26 source files
mypy_exit=0
=== FINAL FLOORS ===
Audited 20 declared dependency floors.
Declared Python support: 3.10, 3.11, 3.12, 3.13
All declared floors are clear of known advisories.
Every declared requirement has a lower bound.
Every floor version exists and permits every supported Python.
(Installability is proven by the lowest-direct CI matrix, not here.)
floors_exit=0
=== FINAL RELEASE CLAIMS ===
Checked README.md
Checked sdist PKG-INFO (39129 chars) from skillwatch-0.4.1.tar.gz

No claim violations.

Harness currently produces 34 distinct proportions.
Per-command parses are checked against per-command minimums. There is no global floor: the minimums sum without deduplication and the distinct count deduplicates, so the two are not comparable.
  measure_base_rate.py      17 parsed, minimum 10
  measure_efficacy.py       22 parsed, minimum 18

  README.md                 15 label-checked,  11 name no metric
  docs/llms.txt              1 label-checked,   0 name no metric
  docs/LAUNCH-FACTS.md      10 label-checked,  10 name no metric
  PATTERNS.md                0 label-checked,   0 name no metric
  SHIP-READINESS.md          0 label-checked,   1 name no metric
  CHANGELOG.md               0 label-checked,   0 name no metric

correspondence coverage: 26 of 48 non-exempt proportions carry a recognisable metric label.
the remaining 22 are NOT correspondence-checked — they are still checked for currency and arithmetic. See ledger item 42.

No figure violations: every published proportion is one the harness currently produces, under a label consistent with the harness's own.
release_claims_exit=0
=== FINAL PUBLISHED CLAIMS ===
Live on PyPI: skillwatch 0.4.1 (38623 chars)

No claim violations.

No claim-marker drift between HEAD and the live page.

CLAUDE.md's published-version claim matches the live index (0.4.1).
published_claims_exit=0
=== FINAL FIGURES ===
Harness currently produces 34 distinct proportions.
Per-command parses are checked against per-command minimums. There is no global floor: the minimums sum without deduplication and the distinct count deduplicates, so the two are not comparable.
  measure_base_rate.py      17 parsed, minimum 10
  measure_efficacy.py       22 parsed, minimum 18

  README.md                 15 label-checked,  11 name no metric
  docs/llms.txt              1 label-checked,   0 name no metric
  docs/LAUNCH-FACTS.md      10 label-checked,  10 name no metric
  PATTERNS.md                0 label-checked,   0 name no metric
  SHIP-READINESS.md          0 label-checked,   1 name no metric
  CHANGELOG.md               0 label-checked,   0 name no metric

correspondence coverage: 26 of 48 non-exempt proportions carry a recognisable metric label.
the remaining 22 are NOT correspondence-checked — they are still checked for currency and arithmetic. See ledger item 42.

No figure violations: every published proportion is one the harness currently produces, under a label consistent with the harness's own.
figures_exit=0
=== FINAL CAPTURE ===
manifest      /home/mkuziva/skillwatch/analysis/corpus/realpage/CAPTURE-INTEGRITY.json
expected      sha256 861027d158b67c517074e3a17348777e4405a644c13a33c7fbc85f25aa417dfe  (59968045 bytes)
per-page      8 of 201 recorded hashes checked (deterministic sample)
host          DESKTOP-71IU9IC (recorded holder)

VERIFIED  /home/mkuziva/.skillwatch-archive/realpage-2026-07-29/fetched_pages.json
          sha256 matches; 8 per-page hashes match.
VERIFIED  /mnt/d/skillwatch-archive/realpage-2026-07-29/fetched_pages.json
          sha256 matches; 8 per-page hashes match.
VERIFIED  /mnt/c/Users/mkuzi/skillwatch-archive/realpage-2026-07-29/fetched_pages.json
          sha256 matches; 8 per-page hashes match.

3 verified, 0 missing, 0 corrupt, of 3 recorded copies.
All recorded copies verified against the manifest.
capture_exit=0
=== FINAL DELTA GUARD ===
REFUSING: today is 2026-07-31; this pass is scheduled for 2026-08-05 or later.
The first snapshots were 2026-07-29. A second pass sooner than seven days measures per-request churn, not editorial drift — which is exactly what made the first attempt return 0/3.
delta_guard_exit=3
........................................................................ [ 11%]
........................................................................ [ 22%]
........................................................................ [ 33%]
........................................................................ [ 45%]
........................................................................ [ 56%]
........................................................................ [ 67%]
........................................................................ [ 78%]
........................................................................ [ 90%]
...............................................................          [100%]
================================ tests coverage ================================
_______________ coverage: platform linux, python 3.12.3-final-0 ________________

Name                      Stmts   Miss  Cover   Missing
-------------------------------------------------------
skillwatch/__init__.py        1      0   100%
skillwatch/anchoring.py     101     12    88%   58-59, 109-110, 144, 155-156, 189-190, 197-198, 200
skillwatch/cli.py           491     30    94%   271-272, 307-308, 327, 335-336, 340, 360, 381, 385, 405, 422, 446, 556-558, 573-575, 579, 581, 718-721, 752-754, 781-782, 811
skillwatch/cloak.py          49      0   100%
skillwatch/detector.py      313      5    98%   266, 320, 732, 815-816
skillwatch/differ.py          8      0   100%
skillwatch/fetcher.py       117     12    90%   112, 155, 160-161, 168, 171, 185-187, 218-224
skillwatch/formatter.py     131      2    98%   23, 220
skillwatch/ledger.py         35      0   100%
skillwatch/parser.py        103      5    95%   75, 95, 123, 142, 144
skillwatch/sarif.py          17      0   100%
skillwatch/ssrf.py           81      4    95%   112, 130, 148, 190
skillwatch/store.py         180      0   100%
-------------------------------------------------------
TOTAL                      1627     70    96%
Required test coverage of 90% reached. Total coverage: 95.70%
639 passed in 80.28s (0:01:20)
* Creating isolated environment: venv+pip...
* Installing packages in isolated environment:
  - setuptools>=83.0.0
  - wheel>=0.46.2
* Getting build dependencies for sdist...
running egg_info
writing skillwatch.egg-info/PKG-INFO
writing dependency_links to skillwatch.egg-info/dependency_links.txt
writing entry points to skillwatch.egg-info/entry_points.txt
writing requirements to skillwatch.egg-info/requires.txt
writing top-level names to skillwatch.egg-info/top_level.txt
reading manifest file 'skillwatch.egg-info/SOURCES.txt'
reading manifest template 'MANIFEST.in'
adding license file 'LICENSE'
writing manifest file 'skillwatch.egg-info/SOURCES.txt'
* Installed build dependency versions:
  - setuptools==83.0.0
  - wheel==0.47.0
* Building sdist...
running sdist
running egg_info
writing skillwatch.egg-info/PKG-INFO
writing dependency_links to skillwatch.egg-info/dependency_links.txt
writing entry points to skillwatch.egg-info/entry_points.txt
writing requirements to skillwatch.egg-info/requires.txt
writing top-level names to skillwatch.egg-info/top_level.txt
reading manifest file 'skillwatch.egg-info/SOURCES.txt'
reading manifest template 'MANIFEST.in'
adding license file 'LICENSE'
writing manifest file 'skillwatch.egg-info/SOURCES.txt'
running check
creating skillwatch-0.4.1
creating skillwatch-0.4.1/skillwatch
creating skillwatch-0.4.1/skillwatch.egg-info
creating skillwatch-0.4.1/skillwatch/data
creating skillwatch-0.4.1/tests
creating skillwatch-0.4.1/tests/fixtures
copying files to skillwatch-0.4.1...
copying CHANGELOG.md -> skillwatch-0.4.1
copying LICENSE -> skillwatch-0.4.1
copying MANIFEST.in -> skillwatch-0.4.1
copying README.md -> skillwatch-0.4.1
copying pyproject.toml -> skillwatch-0.4.1
copying skillwatch/__init__.py -> skillwatch-0.4.1/skillwatch
copying skillwatch/anchoring.py -> skillwatch-0.4.1/skillwatch
copying skillwatch/cli.py -> skillwatch-0.4.1/skillwatch
copying skillwatch/cloak.py -> skillwatch-0.4.1/skillwatch
copying skillwatch/detector.py -> skillwatch-0.4.1/skillwatch
copying skillwatch/differ.py -> skillwatch-0.4.1/skillwatch
copying skillwatch/fetcher.py -> skillwatch-0.4.1/skillwatch
copying skillwatch/formatter.py -> skillwatch-0.4.1/skillwatch
copying skillwatch/ledger.py -> skillwatch-0.4.1/skillwatch
copying skillwatch/parser.py -> skillwatch-0.4.1/skillwatch
copying skillwatch/sarif.py -> skillwatch-0.4.1/skillwatch
copying skillwatch/ssrf.py -> skillwatch-0.4.1/skillwatch
copying skillwatch/store.py -> skillwatch-0.4.1/skillwatch
copying skillwatch.egg-info/PKG-INFO -> skillwatch-0.4.1/skillwatch.egg-info
copying skillwatch.egg-info/SOURCES.txt -> skillwatch-0.4.1/skillwatch.egg-info
copying skillwatch.egg-info/dependency_links.txt -> skillwatch-0.4.1/skillwatch.egg-info
copying skillwatch.egg-info/entry_points.txt -> skillwatch-0.4.1/skillwatch.egg-info
copying skillwatch.egg-info/requires.txt -> skillwatch-0.4.1/skillwatch.egg-info
copying skillwatch.egg-info/top_level.txt -> skillwatch-0.4.1/skillwatch.egg-info
copying skillwatch/data/freetsa_cacert.pem -> skillwatch-0.4.1/skillwatch/data
copying tests/__init__.py -> skillwatch-0.4.1/tests
copying tests/conftest.py -> skillwatch-0.4.1/tests
copying tests/test_anchoring.py -> skillwatch-0.4.1/tests
copying tests/test_ci_scope.py -> skillwatch-0.4.1/tests
copying tests/test_claim_rules.py -> skillwatch-0.4.1/tests
copying tests/test_claude_md_currency.py -> skillwatch-0.4.1/tests
copying tests/test_cli.py -> skillwatch-0.4.1/tests
copying tests/test_cloak.py -> skillwatch-0.4.1/tests
copying tests/test_concealment_unevaluable.py -> skillwatch-0.4.1/tests
copying tests/test_continuity.py -> skillwatch-0.4.1/tests
copying tests/test_delta_pass.py -> skillwatch-0.4.1/tests
copying tests/test_delta_rehearsal.py -> skillwatch-0.4.1/tests
copying tests/test_dependency_floors.py -> skillwatch-0.4.1/tests
copying tests/test_detector.py -> skillwatch-0.4.1/tests
copying tests/test_differ.py -> skillwatch-0.4.1/tests
copying tests/test_e2e.py -> skillwatch-0.4.1/tests
copying tests/test_efficacy_harness.py -> skillwatch-0.4.1/tests
copying tests/test_fetcher.py -> skillwatch-0.4.1/tests
copying tests/test_figure_rules.py -> skillwatch-0.4.1/tests
copying tests/test_formatter.py -> skillwatch-0.4.1/tests
copying tests/test_fp_adaptation.py -> skillwatch-0.4.1/tests
copying tests/test_gate_table.py -> skillwatch-0.4.1/tests
copying tests/test_hidden_content.py -> skillwatch-0.4.1/tests
copying tests/test_hiding_taxonomy.py -> skillwatch-0.4.1/tests
copying tests/test_ledger.py -> skillwatch-0.4.1/tests
copying tests/test_parser.py -> skillwatch-0.4.1/tests
copying tests/test_published_claims.py -> skillwatch-0.4.1/tests
copying tests/test_readiness_consistency.py -> skillwatch-0.4.1/tests
copying tests/test_sarif.py -> skillwatch-0.4.1/tests
copying tests/test_ssrf.py -> skillwatch-0.4.1/tests
copying tests/test_store.py -> skillwatch-0.4.1/tests
copying tests/test_threading.py -> skillwatch-0.4.1/tests
copying tests/test_verify_capture.py -> skillwatch-0.4.1/tests
copying tests/fixtures/sample_skill.md -> skillwatch-0.4.1/tests/fixtures
copying skillwatch.egg-info/SOURCES.txt -> skillwatch-0.4.1/skillwatch.egg-info
Writing skillwatch-0.4.1/setup.cfg
Creating tar archive
removing 'skillwatch-0.4.1' (and everything under it)
* Building wheel from sdist
* Creating isolated environment: venv+pip...
* Installing packages in isolated environment:
  - setuptools>=83.0.0
  - wheel>=0.46.2
* Getting build dependencies for wheel...
running egg_info
writing skillwatch.egg-info/PKG-INFO
writing dependency_links to skillwatch.egg-info/dependency_links.txt
writing entry points to skillwatch.egg-info/entry_points.txt
writing requirements to skillwatch.egg-info/requires.txt
writing top-level names to skillwatch.egg-info/top_level.txt
reading manifest file 'skillwatch.egg-info/SOURCES.txt'
reading manifest template 'MANIFEST.in'
adding license file 'LICENSE'
writing manifest file 'skillwatch.egg-info/SOURCES.txt'
* Installed build dependency versions:
  - setuptools==83.0.0
  - wheel==0.47.0
* Building wheel...
running bdist_wheel
running build
running build_py
creating build/lib/skillwatch
copying skillwatch/ledger.py -> build/lib/skillwatch
copying skillwatch/ssrf.py -> build/lib/skillwatch
copying skillwatch/store.py -> build/lib/skillwatch
copying skillwatch/fetcher.py -> build/lib/skillwatch
copying skillwatch/__init__.py -> build/lib/skillwatch
copying skillwatch/cloak.py -> build/lib/skillwatch
copying skillwatch/differ.py -> build/lib/skillwatch
copying skillwatch/detector.py -> build/lib/skillwatch
copying skillwatch/parser.py -> build/lib/skillwatch
copying skillwatch/anchoring.py -> build/lib/skillwatch
copying skillwatch/formatter.py -> build/lib/skillwatch
copying skillwatch/sarif.py -> build/lib/skillwatch
copying skillwatch/cli.py -> build/lib/skillwatch
running egg_info
writing skillwatch.egg-info/PKG-INFO
writing dependency_links to skillwatch.egg-info/dependency_links.txt
writing entry points to skillwatch.egg-info/entry_points.txt
writing requirements to skillwatch.egg-info/requires.txt
writing top-level names to skillwatch.egg-info/top_level.txt
reading manifest file 'skillwatch.egg-info/SOURCES.txt'
reading manifest template 'MANIFEST.in'
adding license file 'LICENSE'
writing manifest file 'skillwatch.egg-info/SOURCES.txt'
creating build/lib/skillwatch/data
copying skillwatch/data/freetsa_cacert.pem -> build/lib/skillwatch/data
warning: build_py: byte-compiling is disabled, skipping.

installing to build/bdist.linux-x86_64/wheel
running install
running install_lib
creating build/bdist.linux-x86_64/wheel
creating build/bdist.linux-x86_64/wheel/skillwatch
copying build/lib/skillwatch/ledger.py -> build/bdist.linux-x86_64/wheel/./skillwatch
copying build/lib/skillwatch/ssrf.py -> build/bdist.linux-x86_64/wheel/./skillwatch
copying build/lib/skillwatch/store.py -> build/bdist.linux-x86_64/wheel/./skillwatch
copying build/lib/skillwatch/fetcher.py -> build/bdist.linux-x86_64/wheel/./skillwatch
copying build/lib/skillwatch/__init__.py -> build/bdist.linux-x86_64/wheel/./skillwatch
copying build/lib/skillwatch/cloak.py -> build/bdist.linux-x86_64/wheel/./skillwatch
copying build/lib/skillwatch/differ.py -> build/bdist.linux-x86_64/wheel/./skillwatch
copying build/lib/skillwatch/detector.py -> build/bdist.linux-x86_64/wheel/./skillwatch
copying build/lib/skillwatch/parser.py -> build/bdist.linux-x86_64/wheel/./skillwatch
copying build/lib/skillwatch/anchoring.py -> build/bdist.linux-x86_64/wheel/./skillwatch
copying build/lib/skillwatch/formatter.py -> build/bdist.linux-x86_64/wheel/./skillwatch
copying build/lib/skillwatch/sarif.py -> build/bdist.linux-x86_64/wheel/./skillwatch
copying build/lib/skillwatch/cli.py -> build/bdist.linux-x86_64/wheel/./skillwatch
creating build/bdist.linux-x86_64/wheel/skillwatch/data
copying build/lib/skillwatch/data/freetsa_cacert.pem -> build/bdist.linux-x86_64/wheel/./skillwatch/data
warning: install_lib: byte-compiling is disabled, skipping.

running install_egg_info
Copying skillwatch.egg-info to build/bdist.linux-x86_64/wheel/./skillwatch-0.4.1-py3.12.egg-info
running install_scripts
creating build/bdist.linux-x86_64/wheel/skillwatch-0.4.1.dist-info/WHEEL
creating '/home/mkuziva/skillwatch/dist/.tmp-ak6dw526/skillwatch-0.4.1-py3-none-any.whl' and adding 'build/bdist.linux-x86_64/wheel' to it
adding 'skillwatch/__init__.py'
adding 'skillwatch/anchoring.py'
adding 'skillwatch/cli.py'
adding 'skillwatch/cloak.py'
adding 'skillwatch/detector.py'
adding 'skillwatch/differ.py'
adding 'skillwatch/fetcher.py'
adding 'skillwatch/formatter.py'
adding 'skillwatch/ledger.py'
adding 'skillwatch/parser.py'
adding 'skillwatch/sarif.py'
adding 'skillwatch/ssrf.py'
adding 'skillwatch/store.py'
adding 'skillwatch/data/freetsa_cacert.pem'
adding 'skillwatch-0.4.1.dist-info/licenses/LICENSE'
adding 'skillwatch-0.4.1.dist-info/METADATA'
adding 'skillwatch-0.4.1.dist-info/WHEEL'
adding 'skillwatch-0.4.1.dist-info/entry_points.txt'
adding 'skillwatch-0.4.1.dist-info/top_level.txt'
adding 'skillwatch-0.4.1.dist-info/RECORD'
removing build/bdist.linux-x86_64/wheel
Successfully built skillwatch-0.4.1.tar.gz and skillwatch-0.4.1-py3-none-any.whl
=== POST-REVIEW TARGETED ===
........................................................................ [ 86%]
...........                                                              [100%]
83 passed in 1.48s
targeted_exit=0
=== POST-REVIEW FULL ===
........................................................................ [ 11%]
........................................................................ [ 22%]
........................................................................ [ 33%]
........................................................................ [ 44%]
........................................................................ [ 55%]
........................................................................ [ 67%]
........................................................................ [ 78%]
........................................................................ [ 89%]
...................................................................      [100%]
================================ tests coverage ================================
_______________ coverage: platform linux, python 3.12.3-final-0 ________________

Name                      Stmts   Miss  Cover   Missing
-------------------------------------------------------
skillwatch/__init__.py        1      0   100%
skillwatch/anchoring.py     101     12    88%   58-59, 109-110, 144, 155-156, 189-190, 197-198, 200
skillwatch/cli.py           491     30    94%   271-272, 307-308, 327, 335-336, 340, 360, 381, 385, 405, 422, 446, 556-558, 573-575, 579, 581, 718-721, 752-754, 781-782, 811
skillwatch/cloak.py          49      0   100%
skillwatch/detector.py      313      5    98%   266, 320, 732, 815-816
skillwatch/differ.py          8      0   100%
skillwatch/fetcher.py       117     12    90%   112, 155, 160-161, 168, 171, 185-187, 218-224
skillwatch/formatter.py     131      2    98%   23, 220
skillwatch/ledger.py         35      0   100%
skillwatch/parser.py        103      5    95%   75, 95, 123, 142, 144
skillwatch/sarif.py          17      0   100%
skillwatch/ssrf.py           81      4    95%   112, 130, 148, 190
skillwatch/store.py         180      0   100%
-------------------------------------------------------
TOTAL                      1627     70    96%
Required test coverage of 90% reached. Total coverage: 95.70%
643 passed in 40.64s
pytest_exit=0
=== POST-REVIEW RUFF ===
All checks passed!
ruff_exit=0
=== POST-REVIEW MYPY ===
Success: no issues found in 26 source files
mypy_exit=0
=== POST-REVIEW FLOORS ===
Audited 20 declared dependency floors.
Declared Python support: 3.10, 3.11, 3.12, 3.13
All declared floors are clear of known advisories.
Every declared requirement has a lower bound.
Every floor version exists and permits every supported Python.
(Installability is proven by the lowest-direct CI matrix, not here.)
floors_exit=0
=== POST-REVIEW RELEASE CLAIMS ===
Checked README.md
Checked sdist PKG-INFO (39235 chars) from skillwatch-0.4.1.tar.gz

No claim violations.

Harness currently produces 34 distinct proportions.
Per-command parses are checked against per-command minimums. There is no global floor: the minimums sum without deduplication and the distinct count deduplicates, so the two are not comparable.
  measure_base_rate.py      17 parsed, minimum 10
  measure_efficacy.py       22 parsed, minimum 18

  README.md                 15 label-checked,  11 name no metric
  docs/llms.txt              1 label-checked,   0 name no metric
  docs/LAUNCH-FACTS.md      10 label-checked,  10 name no metric
  PATTERNS.md                0 label-checked,   0 name no metric
  SHIP-READINESS.md          0 label-checked,   1 name no metric
  CHANGELOG.md               0 label-checked,   0 name no metric

correspondence coverage: 26 of 48 non-exempt proportions carry a recognisable metric label.
the remaining 22 are NOT correspondence-checked — they are still checked for currency and arithmetic. See ledger item 42.

No figure violations: every published proportion is one the harness currently produces, under a label consistent with the harness's own.
release_claims_exit=0
=== POST-REVIEW PUBLISHED CLAIMS ===
Live on PyPI: skillwatch 0.4.1 (38623 chars)

No claim violations.

No claim-marker drift between HEAD and the live page.

CLAUDE.md's published-version claim matches the live index (0.4.1).
published_claims_exit=0
=== POST-REVIEW FIGURES ===
Harness currently produces 34 distinct proportions.
Per-command parses are checked against per-command minimums. There is no global floor: the minimums sum without deduplication and the distinct count deduplicates, so the two are not comparable.
  measure_base_rate.py      17 parsed, minimum 10
  measure_efficacy.py       22 parsed, minimum 18

  README.md                 15 label-checked,  11 name no metric
  docs/llms.txt              1 label-checked,   0 name no metric
  docs/LAUNCH-FACTS.md      10 label-checked,  10 name no metric
  PATTERNS.md                0 label-checked,   0 name no metric
  SHIP-READINESS.md          0 label-checked,   1 name no metric
  CHANGELOG.md               0 label-checked,   0 name no metric

correspondence coverage: 26 of 48 non-exempt proportions carry a recognisable metric label.
the remaining 22 are NOT correspondence-checked — they are still checked for currency and arithmetic. See ledger item 42.

No figure violations: every published proportion is one the harness currently produces, under a label consistent with the harness's own.
figures_exit=0
=== POST-REVIEW CAPTURE ===
manifest      /home/mkuziva/skillwatch/analysis/corpus/realpage/CAPTURE-INTEGRITY.json
expected      sha256 861027d158b67c517074e3a17348777e4405a644c13a33c7fbc85f25aa417dfe  (59968045 bytes)
per-page      8 of 201 recorded hashes checked (deterministic sample)
host          DESKTOP-71IU9IC (recorded holder)

VERIFIED  /home/mkuziva/.skillwatch-archive/realpage-2026-07-29/fetched_pages.json
          sha256 matches; 8 per-page hashes match.
VERIFIED  /mnt/d/skillwatch-archive/realpage-2026-07-29/fetched_pages.json
          sha256 matches; 8 per-page hashes match.
VERIFIED  /mnt/c/Users/mkuzi/skillwatch-archive/realpage-2026-07-29/fetched_pages.json
          sha256 matches; 8 per-page hashes match.

3 verified, 0 missing, 0 corrupt, of 3 recorded copies.
All recorded copies verified against the manifest.
capture_exit=0
=== POST-REVIEW READINESS ===
Readiness status, generated scoreboard, harness metrics, and ledger sections agree.
readiness_exit=0
* Creating isolated environment: venv+pip...
* Installing packages in isolated environment:
  - setuptools>=83.0.0
  - wheel>=0.46.2
* Getting build dependencies for sdist...
running egg_info
writing skillwatch.egg-info/PKG-INFO
writing dependency_links to skillwatch.egg-info/dependency_links.txt
writing entry points to skillwatch.egg-info/entry_points.txt
writing requirements to skillwatch.egg-info/requires.txt
writing top-level names to skillwatch.egg-info/top_level.txt
reading manifest file 'skillwatch.egg-info/SOURCES.txt'
reading manifest template 'MANIFEST.in'
adding license file 'LICENSE'
writing manifest file 'skillwatch.egg-info/SOURCES.txt'
* Installed build dependency versions:
  - setuptools==83.0.0
  - wheel==0.47.0
* Building sdist...
running sdist
running egg_info
writing skillwatch.egg-info/PKG-INFO
writing dependency_links to skillwatch.egg-info/dependency_links.txt
writing entry points to skillwatch.egg-info/entry_points.txt
writing requirements to skillwatch.egg-info/requires.txt
writing top-level names to skillwatch.egg-info/top_level.txt
reading manifest file 'skillwatch.egg-info/SOURCES.txt'
reading manifest template 'MANIFEST.in'
adding license file 'LICENSE'
writing manifest file 'skillwatch.egg-info/SOURCES.txt'
running check
creating skillwatch-0.4.1
creating skillwatch-0.4.1/skillwatch
creating skillwatch-0.4.1/skillwatch.egg-info
creating skillwatch-0.4.1/skillwatch/data
creating skillwatch-0.4.1/tests
creating skillwatch-0.4.1/tests/fixtures
copying files to skillwatch-0.4.1...
copying CHANGELOG.md -> skillwatch-0.4.1
copying LICENSE -> skillwatch-0.4.1
copying MANIFEST.in -> skillwatch-0.4.1
copying README.md -> skillwatch-0.4.1
copying pyproject.toml -> skillwatch-0.4.1
copying skillwatch/__init__.py -> skillwatch-0.4.1/skillwatch
copying skillwatch/anchoring.py -> skillwatch-0.4.1/skillwatch
copying skillwatch/cli.py -> skillwatch-0.4.1/skillwatch
copying skillwatch/cloak.py -> skillwatch-0.4.1/skillwatch
copying skillwatch/detector.py -> skillwatch-0.4.1/skillwatch
copying skillwatch/differ.py -> skillwatch-0.4.1/skillwatch
copying skillwatch/fetcher.py -> skillwatch-0.4.1/skillwatch
copying skillwatch/formatter.py -> skillwatch-0.4.1/skillwatch
copying skillwatch/ledger.py -> skillwatch-0.4.1/skillwatch
copying skillwatch/parser.py -> skillwatch-0.4.1/skillwatch
copying skillwatch/sarif.py -> skillwatch-0.4.1/skillwatch
copying skillwatch/ssrf.py -> skillwatch-0.4.1/skillwatch
copying skillwatch/store.py -> skillwatch-0.4.1/skillwatch
copying skillwatch.egg-info/PKG-INFO -> skillwatch-0.4.1/skillwatch.egg-info
copying skillwatch.egg-info/SOURCES.txt -> skillwatch-0.4.1/skillwatch.egg-info
copying skillwatch.egg-info/dependency_links.txt -> skillwatch-0.4.1/skillwatch.egg-info
copying skillwatch.egg-info/entry_points.txt -> skillwatch-0.4.1/skillwatch.egg-info
copying skillwatch.egg-info/requires.txt -> skillwatch-0.4.1/skillwatch.egg-info
copying skillwatch.egg-info/top_level.txt -> skillwatch-0.4.1/skillwatch.egg-info
copying skillwatch/data/freetsa_cacert.pem -> skillwatch-0.4.1/skillwatch/data
copying tests/__init__.py -> skillwatch-0.4.1/tests
copying tests/conftest.py -> skillwatch-0.4.1/tests
copying tests/test_anchoring.py -> skillwatch-0.4.1/tests
copying tests/test_ci_scope.py -> skillwatch-0.4.1/tests
copying tests/test_claim_rules.py -> skillwatch-0.4.1/tests
copying tests/test_claude_md_currency.py -> skillwatch-0.4.1/tests
copying tests/test_cli.py -> skillwatch-0.4.1/tests
copying tests/test_cloak.py -> skillwatch-0.4.1/tests
copying tests/test_concealment_unevaluable.py -> skillwatch-0.4.1/tests
copying tests/test_continuity.py -> skillwatch-0.4.1/tests
copying tests/test_delta_pass.py -> skillwatch-0.4.1/tests
copying tests/test_delta_rehearsal.py -> skillwatch-0.4.1/tests
copying tests/test_dependency_floors.py -> skillwatch-0.4.1/tests
copying tests/test_detector.py -> skillwatch-0.4.1/tests
copying tests/test_differ.py -> skillwatch-0.4.1/tests
copying tests/test_e2e.py -> skillwatch-0.4.1/tests
copying tests/test_efficacy_harness.py -> skillwatch-0.4.1/tests
copying tests/test_fetcher.py -> skillwatch-0.4.1/tests
copying tests/test_figure_rules.py -> skillwatch-0.4.1/tests
copying tests/test_formatter.py -> skillwatch-0.4.1/tests
copying tests/test_fp_adaptation.py -> skillwatch-0.4.1/tests
copying tests/test_gate_table.py -> skillwatch-0.4.1/tests
copying tests/test_hidden_content.py -> skillwatch-0.4.1/tests
copying tests/test_hiding_taxonomy.py -> skillwatch-0.4.1/tests
copying tests/test_ledger.py -> skillwatch-0.4.1/tests
copying tests/test_parser.py -> skillwatch-0.4.1/tests
copying tests/test_published_claims.py -> skillwatch-0.4.1/tests
copying tests/test_readiness_consistency.py -> skillwatch-0.4.1/tests
copying tests/test_sarif.py -> skillwatch-0.4.1/tests
copying tests/test_ssrf.py -> skillwatch-0.4.1/tests
copying tests/test_store.py -> skillwatch-0.4.1/tests
copying tests/test_threading.py -> skillwatch-0.4.1/tests
copying tests/test_verify_capture.py -> skillwatch-0.4.1/tests
copying tests/fixtures/sample_skill.md -> skillwatch-0.4.1/tests/fixtures
copying skillwatch.egg-info/SOURCES.txt -> skillwatch-0.4.1/skillwatch.egg-info
Writing skillwatch-0.4.1/setup.cfg
Creating tar archive
removing 'skillwatch-0.4.1' (and everything under it)
* Building wheel from sdist
* Creating isolated environment: venv+pip...
* Installing packages in isolated environment:
  - setuptools>=83.0.0
  - wheel>=0.46.2
* Getting build dependencies for wheel...
running egg_info
writing skillwatch.egg-info/PKG-INFO
writing dependency_links to skillwatch.egg-info/dependency_links.txt
writing entry points to skillwatch.egg-info/entry_points.txt
writing requirements to skillwatch.egg-info/requires.txt
writing top-level names to skillwatch.egg-info/top_level.txt
reading manifest file 'skillwatch.egg-info/SOURCES.txt'
reading manifest template 'MANIFEST.in'
adding license file 'LICENSE'
writing manifest file 'skillwatch.egg-info/SOURCES.txt'
* Installed build dependency versions:
  - setuptools==83.0.0
  - wheel==0.47.0
* Building wheel...
running bdist_wheel
running build
running build_py
creating build/lib/skillwatch
copying skillwatch/ledger.py -> build/lib/skillwatch
copying skillwatch/ssrf.py -> build/lib/skillwatch
copying skillwatch/store.py -> build/lib/skillwatch
copying skillwatch/fetcher.py -> build/lib/skillwatch
copying skillwatch/__init__.py -> build/lib/skillwatch
copying skillwatch/cloak.py -> build/lib/skillwatch
copying skillwatch/differ.py -> build/lib/skillwatch
copying skillwatch/detector.py -> build/lib/skillwatch
copying skillwatch/parser.py -> build/lib/skillwatch
copying skillwatch/anchoring.py -> build/lib/skillwatch
copying skillwatch/formatter.py -> build/lib/skillwatch
copying skillwatch/sarif.py -> build/lib/skillwatch
copying skillwatch/cli.py -> build/lib/skillwatch
running egg_info
writing skillwatch.egg-info/PKG-INFO
writing dependency_links to skillwatch.egg-info/dependency_links.txt
writing entry points to skillwatch.egg-info/entry_points.txt
writing requirements to skillwatch.egg-info/requires.txt
writing top-level names to skillwatch.egg-info/top_level.txt
reading manifest file 'skillwatch.egg-info/SOURCES.txt'
reading manifest template 'MANIFEST.in'
adding license file 'LICENSE'
writing manifest file 'skillwatch.egg-info/SOURCES.txt'
creating build/lib/skillwatch/data
copying skillwatch/data/freetsa_cacert.pem -> build/lib/skillwatch/data
warning: build_py: byte-compiling is disabled, skipping.

installing to build/bdist.linux-x86_64/wheel
running install
running install_lib
creating build/bdist.linux-x86_64/wheel
creating build/bdist.linux-x86_64/wheel/skillwatch
copying build/lib/skillwatch/ledger.py -> build/bdist.linux-x86_64/wheel/./skillwatch
copying build/lib/skillwatch/ssrf.py -> build/bdist.linux-x86_64/wheel/./skillwatch
copying build/lib/skillwatch/store.py -> build/bdist.linux-x86_64/wheel/./skillwatch
copying build/lib/skillwatch/fetcher.py -> build/bdist.linux-x86_64/wheel/./skillwatch
copying build/lib/skillwatch/__init__.py -> build/bdist.linux-x86_64/wheel/./skillwatch
copying build/lib/skillwatch/cloak.py -> build/bdist.linux-x86_64/wheel/./skillwatch
copying build/lib/skillwatch/differ.py -> build/bdist.linux-x86_64/wheel/./skillwatch
copying build/lib/skillwatch/detector.py -> build/bdist.linux-x86_64/wheel/./skillwatch
copying build/lib/skillwatch/parser.py -> build/bdist.linux-x86_64/wheel/./skillwatch
copying build/lib/skillwatch/anchoring.py -> build/bdist.linux-x86_64/wheel/./skillwatch
copying build/lib/skillwatch/formatter.py -> build/bdist.linux-x86_64/wheel/./skillwatch
copying build/lib/skillwatch/sarif.py -> build/bdist.linux-x86_64/wheel/./skillwatch
copying build/lib/skillwatch/cli.py -> build/bdist.linux-x86_64/wheel/./skillwatch
creating build/bdist.linux-x86_64/wheel/skillwatch/data
copying build/lib/skillwatch/data/freetsa_cacert.pem -> build/bdist.linux-x86_64/wheel/./skillwatch/data
warning: install_lib: byte-compiling is disabled, skipping.

running install_egg_info
Copying skillwatch.egg-info to build/bdist.linux-x86_64/wheel/./skillwatch-0.4.1-py3.12.egg-info
running install_scripts
creating build/bdist.linux-x86_64/wheel/skillwatch-0.4.1.dist-info/WHEEL
creating '/home/mkuziva/skillwatch/dist/.tmp-4j4ct4u2/skillwatch-0.4.1-py3-none-any.whl' and adding 'build/bdist.linux-x86_64/wheel' to it
adding 'skillwatch/__init__.py'
adding 'skillwatch/anchoring.py'
adding 'skillwatch/cli.py'
adding 'skillwatch/cloak.py'
adding 'skillwatch/detector.py'
adding 'skillwatch/differ.py'
adding 'skillwatch/fetcher.py'
adding 'skillwatch/formatter.py'
adding 'skillwatch/ledger.py'
adding 'skillwatch/parser.py'
adding 'skillwatch/sarif.py'
adding 'skillwatch/ssrf.py'
adding 'skillwatch/store.py'
adding 'skillwatch/data/freetsa_cacert.pem'
adding 'skillwatch-0.4.1.dist-info/licenses/LICENSE'
adding 'skillwatch-0.4.1.dist-info/METADATA'
adding 'skillwatch-0.4.1.dist-info/WHEEL'
adding 'skillwatch-0.4.1.dist-info/entry_points.txt'
adding 'skillwatch-0.4.1.dist-info/top_level.txt'
adding 'skillwatch-0.4.1.dist-info/RECORD'
removing build/bdist.linux-x86_64/wheel
Successfully built skillwatch-0.4.1.tar.gz and skillwatch-0.4.1-py3-none-any.whl
