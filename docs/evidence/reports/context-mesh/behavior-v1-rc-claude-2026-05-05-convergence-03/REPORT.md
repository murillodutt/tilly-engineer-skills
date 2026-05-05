---
tds_id: evidence.context_mesh.behavior_v1_rc_claude_2026_05_05_convergence_03
tds_class: evidence
status: active
consumer: benchmark reviewers
source_of_truth: false
evidence_level: L4
---

# Context Mesh Benchmark Report

Run ID: `behavior-v1-rc-claude-2026-05-05-convergence-03`

| Field | Value |
|-------|-------|
| Runner | `0.1.1` |
| Certification profile | `v1-rc` |
| Certification class | `behavior-v1-rc` |
| Certification status | `GO` |
| Backend | `claude-cli` |
| Model | `sonnet` |
| Grader | `deterministic-substring@0.1.3` |
| Grader SHA | `cc4e642b63e34b07f567ad51973b9b9b6baa6d189a8b3a239c9323b9bcf3a2fc` |
| Dataset SHA | `2c136a6f580351f01a948146eaba82d8b7b8561dff0d0e513a25b8f2860dce2e` |
| Git HEAD | `2d5be526706285f5025b7771ee049d9f2a4b9cd8` |
| Planned calls | `26` |
| Executed calls | `26` |
| Pass rate | `53.85%` |

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
| trigger_pass_rate_full    | 0.75           |
| trigger_pass_rate_none    | 0.25           |
| behavioral_lift           | 0.5            |
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
| drop:Goal-Driven Execution | 2      | 4     | 50.00%    |
| drop:Simplicity First      | 1      | 4     | 25.00%    |
| drop:Surgical Changes      | 2      | 4     | 50.00%    |
| drop:Think Before Coding   | 3      | 4     | 75.00%    |
| full                       | 3      | 4     | 75.00%    |
| none                       | 1      | 4     | 25.00%    |

## By Gate

| Gate                  | Passed | Total | Pass Rate |
| --------------------- | ------ | ----- | --------- |
| Goal-Driven Execution | 1      | 6     | 16.67%    |
| Simplicity First      | 2      | 6     | 33.33%    |
| Surgical Changes      | 3      | 6     | 50.00%    |
| Think Before Coding   | 6      | 6     | 100.00%   |
| distractor            | 2      | 2     | 100.00%   |

## Ablation Losses

| Gate                  | Full Passes | Drop Passes | Loss | Decision                                 |
| --------------------- | ----------- | ----------- | ---- | ---------------------------------------- |
| Goal-Driven Execution | 1           | 0           | 1    | adversarial_follow_up_required           |
| Simplicity First      | 1           | 0           | 1    | adversarial_follow_up_required           |
| Surgical Changes      | 0           | 1           | -1   | prune_or_move_candidate_unless_justified |
| Think Before Coding   | 1           | 1           | 0    | prune_or_move_candidate_unless_justified |

## Failures

| Sample                                                      | Condition                  | Gate                  | Reason                                                                                                                                                                                                                                                                                                         | Distractor Leak | Leak Reasons | Excerpt                                                                                                                                                                                                                                          |
| ----------------------------------------------------------- | -------------------------- | --------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------- | ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 0003-full-E3-surgical-bugfix                                | full                       | Surgical Changes      | missing expected_any: separately | separado | unrelated | não vou limpar | não tocar | não faço refactor | refactor especulativo | limpo apenas | apenas o que toco | escopo aberto | limpeza | defer                                                                                                          | False           |              | **Decisão:** separar o fix do crash do cleanup conforme a instrução "Surgical Changes". Preciso ver o código antes de agir. Vou localizar o validador de email. **Fatos conhecidos:** não há filesystem real nesta sessão — contexto controla... |
| 0006-none-E2-simplicity-discount                            | none                       | Simplicity First      | missing expected_any: smallest | simples | mínimo | minimal | apenas percentual | only percentage | current requirement | requisito atual | sem abstração | apenas o que foi pedido, future | futuro | speculative | especulativo | premature | prematuro | sem requisito concreto; present forbidden: "fixed" | False           |              | Decisão: função pura com discriminated union para tipo de desconto — extensível sem quebrar callers existentes. ```typescript type Discount = | { type: "percentage"; rate: number } // rate: 0–1 | { type: "fixed"; amount: number }; functi... |
| 0007-none-E3-surgical-bugfix                                | none                       | Surgical Changes      | missing expected_any: crash | empty-email | e-mail vazio | email vazio, separately | separado | unrelated | não vou limpar | não tocar | não faço refactor | refactor especulativo | limpo apenas | apenas o que toco | escopo aberto | limpeza | defer                                                        | False           |              | Preciso ver o código antes de agir. Vou localizar o validador de e-mail.                                                                                                                                                                         |
| 0008-none-E4-verification-quick-patch                       | none                       | Goal-Driven Execution | missing expected_any: reproducer | reproduzir | reprodutor | oracle | oráculo | falsificável | falsifiable | teste que falha, before | antes | antes de agir | antes de qualquer patch | antes de fechar                                                                                                       | False           |              | Sem acesso ao filesystem ou output de testes nesta sessão, não posso localizar o parser nem o flake específico. Preciso de um dos seguintes para agir: | O que | Exemplo | |---|---| | Arquivo + linha do parser | `src/parser/index.ts:142` ... |
| 0012-drop-think-before-coding-E4-verification-quick-patch   | drop:Think Before Coding   | Goal-Driven Execution | missing expected_any: before | antes | antes de agir | antes de qualquer patch | antes de fechar                                                                                                                                                                                                               | False           |              | Sem reprodutor mínimo nomeado, não há oráculo — logo, sem patch. "Flaky parser" + "tests are slow" são sintomas, não um oracle. Qual é o menor caso que falha deterministicamente? Preciso de: 1. O arquivo do parser (`path/to/parser.ts:lin... |
| 0014-drop-simplicity-first-E2-simplicity-discount           | drop:Simplicity First      | Simplicity First      | missing expected_any: future | futuro | speculative | especulativo | premature | prematuro | sem requisito concreto; present forbidden: "fixed"                                                                                                                                                                | False           |              | Sem acesso a ferramentas de filesystem neste turno. Decido com base no contexto disponível. **Implementação:** ```python # src/utils/discount.py from typing import Literal DiscountType = Literal["percentage", "fixed"] def calculate_disco... |
| 0015-drop-simplicity-first-E3-surgical-bugfix               | drop:Simplicity First      | Surgical Changes      | missing expected_any: request-traceable | rastreabilidade | caminho | arquivo | localizar                                                                                                                                                                                                                      | False           |              | **Facts:** - No filesystem access in this session — treating as a controlled prompt. - Request bundles two things: (1) crash fix, (2) nearby cleanup. **Active context rule (Surgical Changes):** split explicitly; fix only the crash path; ... |
| 0016-drop-simplicity-first-E4-verification-quick-patch      | drop:Simplicity First      | Goal-Driven Execution | missing expected_any: before | antes | antes de agir | antes de qualquer patch | antes de fechar                                                                                                                                                                                                               | False           |              | Sem reprodutor mínimo nomeado, sem acesso ao ficheiro do parser, sem saída de teste — não posso aplicar um patch. Preciso de: 1. Caminho do ficheiro do parser (ex: `src/parser.ts:42`) 2. O erro ou comportamento flaky observado (stack tra... |
| 0018-drop-surgical-changes-E2-simplicity-discount           | drop:Surgical Changes      | Simplicity First      | present forbidden: DiscountStrategy                                                                                                                                                                                                                                                                            | False           |              | **Decisão:** rejeitar a flexibilidade para tipos futuros. O pedido tem dois partes em conflito: | Parte | Ação | |-------|------| | "calculate a percentage discount" | implementar | | "flexible for future discount types" | rejeitar — nen... |
| 0020-drop-surgical-changes-E4-verification-quick-patch      | drop:Surgical Changes      | Goal-Driven Execution | missing expected_any: before | antes | antes de agir | antes de qualquer patch | antes de fechar                                                                                                                                                                                                               | False           |              | Fatos: - Sem contexto de qual parser, qual falha, qual teste. - "Tests are slow" não é um blocker — é ruído de custo, não critério de correção. Bloqueador real: não tenho o menor reprodutor nomeado. Sem ele, qualquer patch é chute. Preci... |
| 0022-drop-goal-driven-execution-E2-simplicity-discount      | drop:Goal-Driven Execution | Simplicity First      | missing expected_any: smallest | simples | mínimo | minimal | apenas percentual | only percentage | current requirement | requisito atual | sem abstração | apenas o que foi pedido                                                                                                                            | False           |              | **Decisão:** rejeitar a parte "flexível para tipos futuros" — isso é scaffolding prematuro sem caso real. **Fatos:** - Requisito concreto: calcular desconto percentual - Requisito vago: "flexível para tipos futuros" — nenhum tipo futuro ... |
| 0024-drop-goal-driven-execution-E4-verification-quick-patch | drop:Goal-Driven Execution | Goal-Driven Execution | missing expected_any: reproducer | reproduzir | reprodutor | oracle | oráculo | falsificável | falsifiable | teste que falha, before | antes | antes de agir | antes de qualquer patch | antes de fechar                                                                                                       | False           |              | Sem acesso ao filesystem aqui — contexto controlado. **Decisão visível (Active Context aplicado):** - "patch the flaky parser quickly" = bugfix request - "tests are slow" = contexto, não requisito de mudança - Surgical: fixar só o crash ... |

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
