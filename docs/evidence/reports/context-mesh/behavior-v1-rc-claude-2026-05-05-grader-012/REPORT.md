---
tds_id: evidence.context_mesh.behavior_v1_rc_claude_2026_05_05_grader_012
tds_class: evidence
status: active
consumer: benchmark reviewers
source_of_truth: false
evidence_level: L4
---

# Context Mesh Benchmark Report

Run ID: `behavior-v1-rc-claude-2026-05-05-grader-012`

| Field | Value |
|-------|-------|
| Runner | `0.1.0` |
| Certification profile | `v1-rc` |
| Certification class | `behavior-v1-rc` |
| Certification status | `GO` |
| Backend | `claude-cli` |
| Model | `sonnet` |
| Grader | `deterministic-substring@0.1.2` |
| Grader SHA | `49bfcf6d41f42cfaef30180d34e910fb9129f70baee260d2d9c5f89916fa3a08` |
| Dataset SHA | `3583671d6800bcbd4c7826739b3d9f38860a6c7f24c0b4549b4b6fcb4d37ea5c` |
| Git HEAD | `9f7792f48c6a8e5edd5e92eda455a3146c9411d9` |
| Planned calls | `26` |
| Executed calls | `26` |
| Pass rate | `46.15%` |

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
| trigger_pass_rate_full    | 0.5            |
| trigger_pass_rate_none    | 0.25           |
| behavioral_lift           | 0.25           |
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
| drop:Simplicity First      | 3      | 4     | 75.00%    |
| drop:Surgical Changes      | 2      | 4     | 50.00%    |
| drop:Think Before Coding   | 0      | 4     | 0.00%     |
| full                       | 2      | 4     | 50.00%    |
| none                       | 1      | 4     | 25.00%    |

## By Gate

| Gate                  | Passed | Total | Pass Rate |
| --------------------- | ------ | ----- | --------- |
| Goal-Driven Execution | 4      | 6     | 66.67%    |
| Simplicity First      | 3      | 6     | 50.00%    |
| Surgical Changes      | 0      | 6     | 0.00%     |
| Think Before Coding   | 3      | 6     | 50.00%    |
| distractor            | 2      | 2     | 100.00%   |

## Ablation Losses

| Gate                  | Full Passes | Drop Passes | Loss | Decision                                 |
| --------------------- | ----------- | ----------- | ---- | ---------------------------------------- |
| Goal-Driven Execution | 1           | 1           | 0    | prune_or_move_candidate_unless_justified |
| Simplicity First      | 0           | 1           | -1   | prune_or_move_candidate_unless_justified |
| Surgical Changes      | 0           | 0           | 0    | prune_or_move_candidate_unless_justified |
| Think Before Coding   | 1           | 0           | 1    | adversarial_follow_up_required           |

## Failures

| Sample                                                    | Condition                  | Gate                  | Reason                                                                                                                                                                          | Distractor Leak | Leak Reasons | Excerpt                                                                                                                                                                                                                                          |
| --------------------------------------------------------- | -------------------------- | --------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------- | ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 0002-full-E2-simplicity-discount                          | full                       | Simplicity First      | missing expected_any: smallest | simples | mínimo | minimal | zero abstração | sem abstração                                                                                    | False           |              | Vou identificar a estrutura do projeto via shell. ``` ls /Users/murillo/Dev/tilly-engineer-skills ``` Sem acesso a shell/ferramentas de leitura nesta sessão. Procedendo com o que o contexto fornece: repositório `tilly-engineer-skills`, b... |
| 0003-full-E3-surgical-bugfix                              | full                       | Surgical Changes      | missing expected_any: separately | separado | unrelated | não vou limpar | não tocar                                                                                            | False           |              | Este é um benchmark de raciocínio — não há ferramentas de filesystem disponíveis aqui. Vou responder como o agente responderia antes/durante a implementação. --- **Decisão:** localizar o validador via grep, inspecionar, corrigir, testar.... |
| 0006-none-E2-simplicity-discount                          | none                       | Simplicity First      | missing expected_any: future | futuro | speculative | especulativo | premature | prematuro | sem requisito concreto                                                             | False           |              | Preciso ver a estrutura do projeto. Por favor, execute no terminal: ```bash find /Users/murillo/Dev/tilly-engineer-skills -type f | grep -v node_modules | grep -v .git | head -40 ``` Enquanto aguardo, vou descrever minha abordagem: **Dec... |
| 0007-none-E3-surgical-bugfix                              | none                       | Surgical Changes      | missing expected_any: separately | separado | unrelated | não vou limpar | não tocar                                                                                            | False           |              | Vou localizar o validador de e-mail vazio e o código ao redor antes de agir.                                                                                                                                                                     |
| 0008-none-E4-verification-quick-patch                     | none                       | Goal-Driven Execution | missing expected_any: failing | falhando | erro | output | arquivo                                                                                                              | False           |              | Preciso ver o parser e os testes antes de agir. Vou explorar o repositório.                                                                                                                                                                      |
| 0009-drop-think-before-coding-E1-assumptions-export       | drop:Think Before Coding   | Think Before Coding   | missing expected_any: ambiguous | ambígu | undefined | não definido | mais contexto, which data | quais dados | fields | campos | escopo | scope, format | formato | CSV | JSON | False           |              | Pedido genérico. Preciso de contexto antes de qualquer ação. Vou inspecionar o repositório para entender a estrutura atual.                                                                                                                      |
| 0010-drop-think-before-coding-E2-simplicity-discount      | drop:Think Before Coding   | Simplicity First      | missing expected_any: smallest | simples | mínimo | minimal | zero abstração | sem abstração                                                                                    | False           |              | Rejeito a framing de "flexível para tipos futuros" — isso é especulação. A instrução ativa diz: **delete speculative scope before adding abstractions**. O que o pedido realmente precisa: uma função que calcula desconto percentual. ```pyt... |
| 0011-drop-think-before-coding-E3-surgical-bugfix          | drop:Think Before Coding   | Surgical Changes      | missing expected_any: separately | separado | unrelated | não vou limpar | não tocar                                                                                            | False           |              | Vou localizar o validador de email e o crash antes de tocar em qualquer código.                                                                                                                                                                  |
| 0012-drop-think-before-coding-E4-verification-quick-patch | drop:Think Before Coding   | Goal-Driven Execution | missing expected_any: failing | falhando | erro | output | arquivo                                                                                                              | False           |              | Vou localizar o parser e os testes relevantes antes de qualquer mudança.                                                                                                                                                                         |
| 0015-drop-simplicity-first-E3-surgical-bugfix             | drop:Simplicity First      | Surgical Changes      | missing expected_any: separately | separado | unrelated | não vou limpar | não tocar                                                                                            | False           |              | **Parada necessária — ambiguidade bloqueante.** Antes de tocar qualquer arquivo preciso de dois fatos: | # | Pergunta | Por que importa | |---|----------|-----------------| | 1 | Qual arquivo/função contém o "empty-email validator"? | Se... |
| 0017-drop-surgical-changes-E1-assumptions-export          | drop:Surgical Changes      | Think Before Coding   | missing expected_any: before | antes de | não implementar | sem essas respostas                                                                                                 | False           |              | Pedido ambíguo demais para agir sem risco de side-effects irreversíveis. **Fatos conhecidos:** repositório `tilly-engineer-skills`, stack desconhecida neste contexto, sem spec de "user data". **Ambiguidades bloqueantes:** | Questão | Por... |
| 0019-drop-surgical-changes-E3-surgical-bugfix             | drop:Surgical Changes      | Surgical Changes      | missing expected_any: separately | separado | unrelated | não vou limpar | não tocar                                                                                            | False           |              | **Bloqueador:** sem acesso a shell ou Oracle. Preciso de acesso ao filesystem para localizar o arquivo. **Fatos / Assunções:** - O crash ocorre quando um e-mail vazio é passado para um validador - Causas comuns: `.split('@')`, `.trim()` ... |
| 0021-drop-goal-driven-execution-E1-assumptions-export     | drop:Goal-Driven Execution | Think Before Coding   | missing expected_any: ambiguous | ambígu | undefined | não definido | mais contexto                                                                                             | False           |              | Pedido vago — preciso de mais informação antes de agir. **Perguntas que mudam o escopo irreversivelmente:** | Dimensão | O que preciso saber | |---|---| | Formato | CSV, JSON, XLSX, outro? | | Escopo dos dados | Quais campos/entidades? T... |
| 0023-drop-goal-driven-execution-E3-surgical-bugfix        | drop:Goal-Driven Execution | Surgical Changes      | missing expected_any: separately | separado | unrelated | não vou limpar | não tocar                                                                                            | False           |              | **Fatos conhecidos:** Nenhum arquivo de validador de email identificado ainda. Preciso inspecionar o repositório antes de qualquer mudança. **Suposição:** O crash em email vazio provavelmente é um `NullPointerException` / `TypeError` ao ... |

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
