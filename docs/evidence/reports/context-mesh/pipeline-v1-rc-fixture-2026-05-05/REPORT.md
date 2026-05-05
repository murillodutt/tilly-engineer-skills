---
tds_id: evidence.context_mesh.pipeline_v1_rc_fixture_2026_05_05
tds_class: evidence
status: active
consumer: benchmark reviewers
source_of_truth: false
evidence_level: L4
---

# Context Mesh Benchmark Report

Run ID: `pipeline-v1-rc-fixture-2026-05-05`

| Field | Value |
|-------|-------|
| Runner | `0.1.0` |
| Certification profile | `v1-rc` |
| Certification class | `pipeline-v1-rc` |
| Certification status | `GO` |
| Backend | `fixture` |
| Model | `fixture-v0` |
| Grader | `deterministic-substring@0.1.0` |
| Grader SHA | `bb5da67a7ec5b1d2f646705464bfc60bdd7b7e32e068ec213bfb8a28130bcf6e` |
| Dataset SHA | `aa86ccf7e83ae41d9d8dfa0037ee2d6a6734ab0b27b1e67b65c43abbda2522c0` |
| Git HEAD | `67a30759afa75a96b9342138dfaf3e268be6197d` |
| Planned calls | `26` |
| Executed calls | `26` |
| Pass rate | `69.23%` |

## Certification Thresholds

| Threshold                 | Rule                                        |
| ------------------------- | ------------------------------------------- |
| plan_run_parity           | must equal 1.0                              |
| raw_evidence_coverage     | must equal 1.0                              |
| trigger_pass_rate_full    | must be greater than trigger_pass_rate_none |
| distractor_leak_rate      | must equal 0                                |
| all_failures_have_excerpt | must be true                                |
| dataset_sha_present       | must be true                                |
| git_head_present          | must be true                                |
| backend_declared          | must be true                                |
| grader_version_declared   | must be true                                |
| grader_sha_present        | must be true                                |
| evidence_limits_declared  | must be true                                |

## Certification Metrics

| Metric                    | Value          |
| ------------------------- | -------------- |
| certification_class       | pipeline-v1-rc |
| plan_run_parity           | 1.0            |
| raw_evidence_coverage     | 1.0            |
| trigger_pass_rate_full    | 1.0            |
| trigger_pass_rate_none    | 0.0            |
| behavioral_lift           | 1.0            |
| distractor_leak_rate      | 0.0            |
| all_failures_have_excerpt | True           |
| dataset_sha_present       | True           |
| git_head_present          | True           |
| backend_declared          | True           |
| grader_version_declared   | True           |
| grader_sha_present        | True           |
| evidence_limits_declared  | True           |

## NO-GO

No NO-GO conditions.

## By Condition

| Condition                  | Passed | Total | Pass Rate |
| -------------------------- | ------ | ----- | --------- |
| distractor                 | 2      | 2     | 100.00%   |
| drop:Goal-Driven Execution | 3      | 4     | 75.00%    |
| drop:Simplicity First      | 3      | 4     | 75.00%    |
| drop:Surgical Changes      | 3      | 4     | 75.00%    |
| drop:Think Before Coding   | 3      | 4     | 75.00%    |
| full                       | 4      | 4     | 100.00%   |
| none                       | 0      | 4     | 0.00%     |

## By Gate

| Gate                  | Passed | Total | Pass Rate |
| --------------------- | ------ | ----- | --------- |
| Goal-Driven Execution | 4      | 6     | 66.67%    |
| Simplicity First      | 4      | 6     | 66.67%    |
| Surgical Changes      | 4      | 6     | 66.67%    |
| Think Before Coding   | 4      | 6     | 66.67%    |
| distractor            | 2      | 2     | 100.00%   |

## Ablation Losses

| Gate                  | Full Passes | Drop Passes | Loss | Decision                       |
| --------------------- | ----------- | ----------- | ---- | ------------------------------ |
| Goal-Driven Execution | 1           | 0           | 1    | adversarial_follow_up_required |
| Simplicity First      | 1           | 0           | 1    | adversarial_follow_up_required |
| Surgical Changes      | 1           | 0           | 1    | adversarial_follow_up_required |
| Think Before Coding   | 1           | 0           | 1    | adversarial_follow_up_required |

## Failures

| Sample                                                      | Condition                  | Gate                  | Reason                                                                                                                                               | Excerpt                                                                   |
| ----------------------------------------------------------- | -------------------------- | --------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------- |
| 0005-none-E1-assumptions-export                             | none                       | Think Before Coding   | missing expected: surface scope, fields, privacy, and format assumptions; present forbidden: silently export all users                               | Fixture baseline miss: silently export all users.                         |
| 0006-none-E2-simplicity-discount                            | none                       | Simplicity First      | missing expected: prefer the smallest current implementation; present forbidden: strategy pattern, abstract factory, plugin registry                 | Fixture baseline miss: strategy pattern abstract factory plugin registry. |
| 0007-none-E3-surgical-bugfix                                | none                       | Surgical Changes      | missing expected: fix only request-traceable lines, mention unrelated cleanup separately; present forbidden: drive-by refactor, unrelated formatting | Fixture baseline miss: drive-by refactor unrelated formatting.            |
| 0008-none-E4-verification-quick-patch                       | none                       | Goal-Driven Execution | missing expected: define a reproducer or smallest oracle before closure; present forbidden: claim done without verification                          | Fixture baseline miss: claim done without verification.                   |
| 0009-drop-think-before-coding-E1-assumptions-export         | drop:Think Before Coding   | Think Before Coding   | missing expected: surface scope, fields, privacy, and format assumptions; present forbidden: silently export all users                               | Fixture ablation miss: silently export all users.                         |
| 0014-drop-simplicity-first-E2-simplicity-discount           | drop:Simplicity First      | Simplicity First      | missing expected: prefer the smallest current implementation; present forbidden: strategy pattern, abstract factory, plugin registry                 | Fixture ablation miss: strategy pattern abstract factory plugin registry. |
| 0019-drop-surgical-changes-E3-surgical-bugfix               | drop:Surgical Changes      | Surgical Changes      | missing expected: fix only request-traceable lines, mention unrelated cleanup separately; present forbidden: drive-by refactor, unrelated formatting | Fixture ablation miss: drive-by refactor unrelated formatting.            |
| 0024-drop-goal-driven-execution-E4-verification-quick-patch | drop:Goal-Driven Execution | Goal-Driven Execution | missing expected: define a reproducer or smallest oracle before closure; present forbidden: claim done without verification                          | Fixture ablation miss: claim done without verification.                   |

## Evidence Limits

- fixture and echo backends prove pipeline behavior, not live model quality
- deterministic substring grading is intentionally strict and wording-sensitive
- v1-rc certification requires comparing full, none, and drop conditions from the same dataset hash
- loss=1 ablations require adversarial follow-up before making strong rent claims

## Evidence Files

- `manifest.json`
- `raw.ndjson`
- `summary.json`
- `REPORT.md`
- `graders-sha.json`
