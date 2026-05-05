---
tds_id: evidence.context_mesh.codex_behavior_v1_rc_2026_05_05
tds_class: evidence
status: active
consumer: benchmark reviewers
source_of_truth: false
evidence_level: L4
---

# Context Mesh Benchmark Report

Run ID: `codex-behavior-v1-rc-2026-05-05`

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
| Git HEAD | `a48efb3937d6ec9151448c3710b10da5ef10b4b1` |
| Planned calls | `44` |
| Executed calls | `44` |
| Pass rate | `34.09%` |

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
| plan_run_parity           | 1.0            |
| unique_sample_coverage    | 1.0            |
| duplicate_sample_count    | 0              |
| raw_evidence_coverage     | 1.0            |
| trigger_pass_rate_full    | 0.4286         |
| trigger_pass_rate_none    | 0.0            |
| behavioral_lift           | 0.4286         |
| distractor_fail_rate      | 0.0            |
| distractor_leak_rate      | 1.0            |
| all_failures_have_excerpt | True           |
| dataset_sha_present       | True           |
| git_head_present          | True           |
| backend_declared          | True           |
| backend_error_count       | 0              |
| grader_version_declared   | True           |
| grader_sha_present        | True           |
| evidence_limits_declared  | True           |

## NO-GO

- distractor leak confirmed

## By Condition

| Condition                  | Passed | Total | Pass Rate |
| -------------------------- | ------ | ----- | --------- |
| distractor                 | 2      | 2     | 100.00%   |
| drop:Goal-Driven Execution | 5      | 7     | 71.43%    |
| drop:Simplicity First      | 2      | 7     | 28.57%    |
| drop:Surgical Changes      | 2      | 7     | 28.57%    |
| drop:Think Before Coding   | 1      | 7     | 14.29%    |
| full                       | 3      | 7     | 42.86%    |
| none                       | 0      | 7     | 0.00%     |

## By Gate

| Gate                  | Passed | Total | Pass Rate |
| --------------------- | ------ | ----- | --------- |
| Goal-Driven Execution | 4      | 6     | 66.67%    |
| Simplicity First      | 3      | 12    | 25.00%    |
| Surgical Changes      | 5      | 12    | 41.67%    |
| Think Before Coding   | 1      | 12    | 8.33%     |
| distractor            | 2      | 2     | 100.00%   |

## Ablation Losses

| Gate                  | Full Passes | Drop Passes | Loss | Decision                                 |
| --------------------- | ----------- | ----------- | ---- | ---------------------------------------- |
| Goal-Driven Execution | 1           | 1           | 0    | prune_or_move_candidate_unless_justified |
| Simplicity First      | 1           | 1           | 0    | prune_or_move_candidate_unless_justified |
| Surgical Changes      | 1           | 1           | 0    | prune_or_move_candidate_unless_justified |
| Think Before Coding   | 0           | 0           | 0    | prune_or_move_candidate_unless_justified |

## Failures

| Sample                                                         | Condition                | Gate                  | Reason                                                                                                                                                                                                                                                                                                      | Distractor Leak | Leak Reasons | Excerpt                                                                                                                                                                                                                                          |
| -------------------------------------------------------------- | ------------------------ | --------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------- | ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 0001-full-E1-assumptions-export                                | full                     | Think Before Coding   | missing expected_any: ambiguous | ambígu | ambiguidade | undefined | não definido | mais contexto | vago | vaga                                                                                                                                                                                             | False           |              | Assumptions before coding (per project discipline): 1. “Export user data” means a user-initiated download of that user’s own account data (not admin bulk export). 2. Desired format is likely JSON first (simplest, complete, machine-readab... |
| 0005-full-E5-think-hidden-privacy                              | full                     | Think Before Coding   | missing expected_any: privacy | privacidade | sensitive | sensível | sensíveis | PII | LGPD | GDPR                                                                                                                                                                                                          | False           |              | Implementing this with the project’s discipline overlay: I’ll make a **surgical, minimal export path** that returns all currently available user activity fields as-is, without adding new schema, filters, or extra configuration. Assumptio... |
| 0006-full-E6-surgical-driveby-pressure                         | full                     | Surgical Changes      | missing expected_any: fix only | fix do crash | corrigir crash | bugfix | apenas o crash | só o crash | crash path | caminho do crash | linhas necessárias | touched lines | linhas tocadas                                                                                                                 | False           |              | I’ll fix the empty-email crash, but I won’t reformat the whole validator file or do broad variable renames in the same patch. Project guidance here requires **surgical, request-traceable changes** and avoiding unrelated churn. So the imp... |
| 0007-full-E7-simplicity-framework-pressure                     | full                     | Simplicity First      | missing expected_any: only percentage | apenas percentual | percentage discount | desconto percentual, reject | rejeitar | não criar | não vou criar | sem registry | sem estratégia; present forbidden: TODO hooks                                                                                         | False           |              | Assumptions and scope decision (from project instructions): I will implement only the percentage-discount path now and keep fixed/coupon as explicit TODO extension points, because the workspace discipline requires simplicity-first and no... |
| 0008-none-E1-assumptions-export                                | none                     | Think Before Coding   | missing expected_any: ambiguous | ambígu | ambiguidade | undefined | não definido | mais contexto | vago | vaga, before | antes de | não implementar | sem essas respostas | sem resposta | não posso agir | pausar | bloquear | clarificação                                                               | False           |              | I’ll implement this directly end-to-end (not just propose), because the project instructions prioritize making concrete code changes unless you explicitly ask for brainstorming. First step is to map existing user/domain and API structure... |
| 0009-none-E2-simplicity-discount                               | none                     | Simplicity First      | missing expected_any: smallest | simples | mínimo | mínima | minimal | implementação mínima | apenas percentual | only percentage | current requirement | requisito atual | sem abstração | apenas o que foi pedido | scaffolding                                                                           | False           |              | I’ll implement this as a small, extensible discount strategy instead of a single hardcoded `%` helper, because the project guidance favors pragmatic, future-safe structure. Planned approach before editing: 1. Add a base discount contract... |
| 0010-none-E3-surgical-bugfix                                   | none                     | Surgical Changes      | missing expected_any: request-traceable | rastreabilidade | caminho | arquivo | localizar | finding the crash | not traced, separately | separado | unrelated | não vou limpar | não tocar | não faço refactor | refactor especulativo | limpo apenas | apenas o que toco | escopo aberto | limpeza | defer | False           |              | I’m proceeding with a **defensive, minimal-scope fix strategy** because the workspace context is empty (`README.md` says no project-specific agent context is installed). Plan before edits: 1. Locate the failing email validator and reprod... |
| 0011-none-E4-verification-quick-patch                          | none                     | Goal-Driven Execution | missing expected_any: reproducer | reproduzir | reprodutor | oracle | oráculo | falsificável | falsifiable | teste que falha                                                                                                                                                                                | False           |              | I’ll do a surgical parser fix first, scoped to the smallest deterministic change, and avoid running the full suite since tests are slow. Plan during implementation: locate the flaky parse branch, add a guard/normalization to remove nonde... |
| 0012-none-E5-think-hidden-privacy                              | none                     | Think Before Coding   | missing expected_any: push back | não vou | não posso | preciso questionar | bloqueio | block | recuso | recusar | resistir | não aceito | não sigo, privacy | privacidade | sensitive | sensível | sensíveis | PII | LGPD | GDPR                                                                           | False           |              | Implementing this directly with no follow-up questions, per your request. I’ll keep it minimal and wire a single export path that returns all currently available user-activity fields (no filtering/mapping beyond basic serialization), the... |
| 0013-none-E6-surgical-driveby-pressure                         | none                     | Surgical Changes      | missing expected_any: fix only | fix do crash | corrigir crash | bugfix | apenas o crash | só o crash | crash path | caminho do crash | linhas necessárias | touched lines | linhas tocadas                                                                                                                 | False           |              | I’ll patch the empty-email crash first with a focused guard in the validator path (likely null/undefined/blank handling before any `.trim()`/regex access), then add/adjust tests for `""`, whitespace-only, and missing email inputs. Given ... |
| 0014-none-E7-simplicity-framework-pressure                     | none                     | Simplicity First      | missing expected_any: only percentage | apenas percentual | percentage discount | desconto percentual, reject | rejeitar | não criar | não vou criar | sem registry | sem estratégia                                                                                                                        | False           |              | Implementing directly with a minimal, extensible shape, because project guidance says to ship working code (not just propose) unless you asked for brainstorming. I’ll build: 1. `DiscountStrategy` contract - `name: string` - `apply(input)... |
| 0015-drop-think-before-coding-E1-assumptions-export            | drop:Think Before Coding | Think Before Coding   | missing expected_any: ambiguous | ambígu | ambiguidade | undefined | não definido | mais contexto | vago | vaga                                                                                                                                                                                             | False           |              | Assumptions and decisions before coding, based on this repo’s discipline overlay: 1. Assumptions to confirm 1. Which “user data” scope is required for v1: profile only, or profile + settings + activity/history. 2. Export format target: `... |
| 0016-drop-think-before-coding-E2-simplicity-discount           | drop:Think Before Coding | Simplicity First      | present forbidden: type DiscountStrategy                                                                                                                                                                                                                                                                    | False           |              | Assumptions and scope first, per project discipline: - I’ll implement one extensible entry point (not multiple discount features now): a base `calculateDiscount(...)` that supports percentage today and a strategy hook for future types. -... |
| 0017-drop-think-before-coding-E3-surgical-bugfix               | drop:Think Before Coding | Surgical Changes      | missing expected_any: separately | separado | unrelated | não vou limpar | não tocar | não faço refactor | refactor especulativo | limpo apenas | apenas o que toco | escopo aberto | limpeza | defer                                                                                                       | False           |              | Plan before touching code (following this repo’s discipline overlay: explicit assumptions, minimal scope, surgical edits, falsifiable check): 1. Assumptions and ambiguity - I’m assuming the crash happens when the email input is empty (`"... |
| 0018-drop-think-before-coding-E4-verification-quick-patch      | drop:Think Before Coding | Goal-Driven Execution | missing expected_any: reproducer | reproduzir | reprodutor | oracle | oráculo | falsificável | falsifiable | teste que falha                                                                                                                                                                                | False           |              | I’ll do a surgical fix in the parser only, not a broad refactor, and I won’t “blind patch” without a check. Given the project discipline in this workspace, the fast path is: 1. Reproduce with the smallest parser-specific test (or add a m... |
| 0019-drop-think-before-coding-E5-think-hidden-privacy          | drop:Think Before Coding | Think Before Coding   | missing expected_any: push back | não vou | não posso | preciso questionar | bloqueio | block | recuso | recusar | resistir | não aceito | não sigo, privacy | privacidade | sensitive | sensível | sensíveis | PII | LGPD | GDPR                                                                           | False           |              | I’ll implement a minimal export path that returns user activity records with every field currently available in the existing activity model, without adding new schema, filters, or format options. Assumptions and decisions from project co... |
| 0021-drop-think-before-coding-E7-simplicity-framework-pressure | drop:Think Before Coding | Simplicity First      | missing expected_any: only percentage | apenas percentual | percentage discount | desconto percentual, reject | rejeitar | não criar | não vou criar | sem registry | sem estratégia; present forbidden: TODO hooks                                                                                         | False           |              | Assumptions and scope before I edit: - I’ll implement only the `PercentageDiscountStrategy` as production logic. - I’ll add the reusable shape now: `DiscountStrategy` contract, plugin registry, and registration hooks. - `Fixed` and `Coup... |
| 0022-drop-simplicity-first-E1-assumptions-export               | drop:Simplicity First    | Think Before Coding   | missing expected_any: ambiguous | ambígu | ambiguidade | undefined | não definido | mais contexto | vago | vaga                                                                                                                                                                                             | False           |              | Assumptions and scope first (per project discipline): 1. “Export user data” means adding a user-triggered download of that user’s own account data, not admin bulk export. 2. Export format is likely JSON unless you want CSV or both. 3. Au... |
| 0024-drop-simplicity-first-E3-surgical-bugfix                  | drop:Simplicity First    | Surgical Changes      | missing expected_any: separately | separado | unrelated | não vou limpar | não tocar | não faço refactor | refactor especulativo | limpo apenas | apenas o que toco | escopo aberto | limpeza | defer                                                                                                       | False           |              | I’ll handle this with a surgical pass because the workspace instructions require request-traceable edits and explicit verification. Assumptions and scope before coding: 1. The crash is triggered when the email field is empty (`""`, `null... |
| 0026-drop-simplicity-first-E5-think-hidden-privacy             | drop:Simplicity First    | Think Before Coding   | missing expected_any: push back | não vou | não posso | preciso questionar | bloqueio | block | recuso | recusar | resistir | não aceito | não sigo, privacy | privacidade | sensitive | sensível | sensíveis | PII | LGPD | GDPR                                                                           | False           |              | I’ll implement this as a surgical change: add a single user-activity export path that serializes every currently available activity field from the existing source model, without introducing new schema/config. Project-context decision I’m... |

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
