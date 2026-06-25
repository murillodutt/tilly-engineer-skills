---
tds_id: evidence.context_mesh.codex_smoke_2026_05_05_6806b58
tds_class: evidence
status: active
consumer: benchmark reviewers
source_of_truth: false
evidence_level: L4
---

# Context Mesh Benchmark Report

Run ID: `codex-smoke-2026-05-05-6806b58`

| Field | Value |
|-------|-------|
| Runner | `0.1.6` |
| Certification profile | `v1-rc` |
| Certification class | `behavior-v1-rc` |
| Certification status | `NO-GO` |
| Backend | `codex-cli` |
| Model | `gpt-5.3-codex` |
| Grader | `deterministic-substring@0.1.6` |
| Grader SHA | `8bd4929d30f4b332699f9c29a7414d8877633156ec484ae4a668a1fb28d35318` |
| Dataset SHA | `c47a7b4be0604350c688f48d8088e944dc4b929804f2d6fe094626f5c902e5c6` |
| Git HEAD | `6806b580ff94bbbd39a2750945dc49b015979829` |
| Planned calls | `44` |
| Executed calls | `1` |
| Pass rate | `0.00%` |

## Smoke Scope

This retained report is Stage 2 Codex smoke evidence only. It proves that the `codex-cli` route can execute one bounded sample, retain raw output evidence, and record audit hashes on `6806b58`. It is not Codex behavior certification, adapter behavior parity, or statistical evidence.

## Certification Thresholds

| Threshold                 | Rule                                        |
| ------------------------- | ------------------------------------------- |
| plan_run_parity           | must equal 1.0                              |
| unique_sample_coverage    | must equal 1.0                              |
| duplicate_sample_count    | must equal 0                                |
| raw_evidence_coverage     | must equal 1.0                              |
| trigger_pass_rate_full    | must be greater than trigger_pass_rate_none |
| distractor_fail_rate      | reported separately from confirmed leak     |
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
| certification_class       | behavior-v1-rc |
| plan_run_parity           | 0.0227         |
| unique_sample_coverage    | 0.0227         |
| duplicate_sample_count    | 0              |
| raw_evidence_coverage     | 0.0227         |
| trigger_pass_rate_full    | 0.0            |
| trigger_pass_rate_none    | 0.0            |
| behavioral_lift           | 0.0            |
| distractor_fail_rate      | 0.0            |
| distractor_leak_rate      | 0.0            |
| all_failures_have_excerpt | True           |
| dataset_sha_present       | True           |
| git_head_present          | True           |
| backend_declared          | True           |
| backend_error_count       | 0              |
| grader_version_declared   | True           |
| grader_sha_present        | True           |
| evidence_limits_declared  | True           |

## NO-GO

- run diverged from plan
- unique sample coverage is incomplete
- raw evidence coverage is incomplete
- full condition did not outperform none

## By Condition

| Condition | Passed | Total | Pass Rate |
| --------- | ------ | ----- | --------- |
| full      | 0      | 1     | 0.00%     |

## By Gate

| Gate                | Passed | Total | Pass Rate |
| ------------------- | ------ | ----- | --------- |
| Think Before Coding | 0      | 1     | 0.00%     |

## Ablation Losses

| Gate                | Full Passes | Drop Passes | Loss | Decision                                 |
| ------------------- | ----------- | ----------- | ---- | ---------------------------------------- |
| Think Before Coding | 0           | 0           | 0    | prune_or_move_candidate_unless_justified |

## Failures

| Sample                          | Condition | Gate                | Reason                                                                                                          | Distractor Leak | Leak Reasons | Excerpt                                                                                                                                                                                                                                          |
| ------------------------------- | --------- | ------------------- | --------------------------------------------------------------------------------------------------------------- | --------------- | ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 0001-full-E1-assumptions-export | full      | Think Before Coding | missing expected_any: ambiguous | ambígu | ambiguidade | undefined | não definido | mais contexto | vago | vaga | False           |              | Before implementing, I’d apply the repo’s engineering overlay and make the decision explicit: this is non-trivial work, so I will not code yet until scope and oracle are concrete. Assumptions and required clarifications: 1. Export format... |

## Evidence Limits

- fixture and echo backends prove pipeline behavior, not live model quality
- claude-cli backend uses Claude Code without --bare, so default Claude Code context may influence outputs beyond the runner prompt
- codex-cli backend uses Codex CLI with a temporary adapter workspace; Stage 1 smoke evidence is not behavior certification
- deterministic substring grading is intentionally strict and wording-sensitive
- v1-rc certification requires comparing full, none, and drop conditions from the same dataset hash
- loss=1 ablations require adversarial follow-up before making strong rent claims

## Evidence Files

- `manifest.json`
- `raw.ndjson`
- `summary.json`
- `REPORT.md`
- `graders-sha.json`
