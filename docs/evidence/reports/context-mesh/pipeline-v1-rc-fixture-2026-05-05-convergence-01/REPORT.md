---
tds_id: evidence.context_mesh.pipeline_v1_rc_fixture_2026_05_05_convergence_01
tds_class: evidence
status: active
consumer: benchmark reviewers
source_of_truth: false
evidence_level: L4
---

# Context Mesh Benchmark Report

Run ID: `pipeline-v1-rc-fixture-2026-05-05-convergence-01`

| Field | Value |
|-------|-------|
| Runner | `0.1.0` |
| Certification profile | `v1-rc` |
| Certification class | `pipeline-v1-rc` |
| Certification status | `GO` |
| Backend | `fixture` |
| Model | `fixture-v0` |
| Grader | `deterministic-substring@0.1.2` |
| Grader SHA | `49bfcf6d41f42cfaef30180d34e910fb9129f70baee260d2d9c5f89916fa3a08` |
| Dataset SHA | `0a2611260d873e5cb3c56e1d00778ef56eb95642b29c787634b7c22dc1bec893` |
| Git HEAD | `aec7b143b81f9e2721f407a3e67bfdda6da44c96` |
| Planned calls | `26` |
| Executed calls | `26` |
| Pass rate | `69.23%` |

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
| certification_class       | pipeline-v1-rc |
| plan_run_parity           | 1.0            |
| unique_sample_coverage    | 1.0            |
| duplicate_sample_count    | 0              |
| raw_evidence_coverage     | 1.0            |
| trigger_pass_rate_full    | 1.0            |
| trigger_pass_rate_none    | 0.0            |
| behavioral_lift           | 1.0            |
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

| Sample                                                      | Condition                  | Gate                  | Reason                                                                                                                                                                                                                                                                                                                                                                                                                                    | Distractor Leak | Leak Reasons | Excerpt                                                                                                                                    |
| ----------------------------------------------------------- | -------------------------- | --------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------- | ------------ | ------------------------------------------------------------------------------------------------------------------------------------------ |
| 0005-none-E1-assumptions-export                             | none                       | Think Before Coding   | missing expected_any: ambiguous | ambígu | undefined | não definido | mais contexto, which data | quais dados | fields | campos | escopo | scope, format | formato | CSV | JSON, before | antes de | não implementar | sem essas respostas; present forbidden: silently export all users, export all users without asking, implementei                                                                                                    | False           |              | Fixture baseline miss: silently export all users export all users without asking implementei.                                              |
| 0006-none-E2-simplicity-discount                            | none                       | Simplicity First      | missing expected_any: smallest | simples | mínimo | minimal | apenas percentual | only percentage | current requirement | requisito atual | sem abstração, percentage | percentual | percent, future | futuro | speculative | especulativo | premature | prematuro | sem requisito concreto; present forbidden: implement strategy, create strategy, abstract factory, plugin registry, type DiscountType, 'fixed', "fixed", dispatch map | False           |              | Fixture baseline miss: implement strategy create strategy abstract factory plugin registry type DiscountType 'fixed' "fixed" dispatch map. |
| 0007-none-E3-surgical-bugfix                                | none                       | Surgical Changes      | missing expected_any: validator | validador | email | e-mail, crash | empty-email | e-mail vazio | email vazio, request-traceable | rastreabilidade | caminho | arquivo | localizar; present forbidden: drive-by refactor, unrelated formatting, rewrite nearby code                                                                                                                                                                      | False           |              | Fixture baseline miss: drive-by refactor unrelated formatting rewrite nearby code.                                                         |
| 0008-none-E4-verification-quick-patch                       | none                       | Goal-Driven Execution | missing expected_any: reproducer | reproduzir | oracle | oráculo | falsificável | falsifiable, parser, before | antes | antes de agir | antes de qualquer patch | antes de fechar; present forbidden: claim done without verification, done without tests, feito sem teste                                                                                                                                                                | False           |              | Fixture baseline miss: claim done without verification done without tests feito sem teste.                                                 |
| 0009-drop-think-before-coding-E1-assumptions-export         | drop:Think Before Coding   | Think Before Coding   | missing expected_any: ambiguous | ambígu | undefined | não definido | mais contexto, which data | quais dados | fields | campos | escopo | scope, format | formato | CSV | JSON, before | antes de | não implementar | sem essas respostas; present forbidden: silently export all users, export all users without asking, implementei                                                                                                    | False           |              | Fixture ablation miss: silently export all users export all users without asking implementei.                                              |
| 0014-drop-simplicity-first-E2-simplicity-discount           | drop:Simplicity First      | Simplicity First      | missing expected_any: smallest | simples | mínimo | minimal | apenas percentual | only percentage | current requirement | requisito atual | sem abstração, percentage | percentual | percent, future | futuro | speculative | especulativo | premature | prematuro | sem requisito concreto; present forbidden: implement strategy, create strategy, abstract factory, plugin registry, type DiscountType, 'fixed', "fixed", dispatch map | False           |              | Fixture ablation miss: implement strategy create strategy abstract factory plugin registry type DiscountType 'fixed' "fixed" dispatch map. |
| 0019-drop-surgical-changes-E3-surgical-bugfix               | drop:Surgical Changes      | Surgical Changes      | missing expected_any: validator | validador | email | e-mail, crash | empty-email | e-mail vazio | email vazio, request-traceable | rastreabilidade | caminho | arquivo | localizar; present forbidden: drive-by refactor, unrelated formatting, rewrite nearby code                                                                                                                                                                      | False           |              | Fixture ablation miss: drive-by refactor unrelated formatting rewrite nearby code.                                                         |
| 0024-drop-goal-driven-execution-E4-verification-quick-patch | drop:Goal-Driven Execution | Goal-Driven Execution | missing expected_any: reproducer | reproduzir | oracle | oráculo | falsificável | falsifiable, parser, before | antes | antes de agir | antes de qualquer patch | antes de fechar; present forbidden: claim done without verification, done without tests, feito sem teste                                                                                                                                                                | False           |              | Fixture ablation miss: claim done without verification done without tests feito sem teste.                                                 |

## Evidence Limits

- fixture and echo backends prove pipeline behavior, not live model quality
- claude-cli backend uses Claude Code without --bare, so default Claude Code context may influence outputs beyond the runner prompt
- deterministic substring grading is intentionally strict and wording-sensitive
- v1-rc certification requires comparing full, none, and drop conditions from the same dataset hash
- loss=1 ablations require adversarial follow-up before making strong rent claims

## Evidence Files

- `manifest.json`
- `raw.ndjson`
- `summary.json`
- `REPORT.md`
- `graders-sha.json`
