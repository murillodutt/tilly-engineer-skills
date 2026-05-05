---
tds_id: evidence.context_mesh.behavior_v1_rc_claude_2026_05_05_convergence_02
tds_class: evidence
status: active
consumer: benchmark reviewers
source_of_truth: false
evidence_level: L4
---

# Context Mesh Benchmark Report

Run ID: `behavior-v1-rc-claude-2026-05-05-convergence-02`

| Field | Value |
|-------|-------|
| Runner | `0.1.0` |
| Certification profile | `v1-rc` |
| Certification class | `behavior-v1-rc` |
| Certification status | `NO-GO` |
| Backend | `claude-cli` |
| Model | `sonnet` |
| Grader | `deterministic-substring@0.1.2` |
| Grader SHA | `49bfcf6d41f42cfaef30180d34e910fb9129f70baee260d2d9c5f89916fa3a08` |
| Dataset SHA | `edb7a0e8312d5f5da1dace6e065d55a05c6311d24d4784a6fe378a34b966f5fa` |
| Git HEAD | `8c1834670eaa4dad9eac603da55dc1cf003e0640` |
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
| trigger_pass_rate_full    | 0.25           |
| trigger_pass_rate_none    | 0.5            |
| behavioral_lift           | -0.25          |
| distractor_fail_rate      | 0.0            |
| distractor_leak_rate      | 0.5            |
| all_failures_have_excerpt | True           |
| dataset_sha_present       | True           |
| git_head_present          | True           |
| backend_declared          | True           |
| backend_error_count       | 0              |
| grader_version_declared   | True           |
| grader_sha_present        | True           |
| evidence_limits_declared  | True           |

## NO-GO

- full condition did not outperform none
- distractor leak confirmed

## By Condition

| Condition                  | Passed | Total | Pass Rate |
| -------------------------- | ------ | ----- | --------- |
| distractor                 | 2      | 2     | 100.00%   |
| drop:Goal-Driven Execution | 0      | 4     | 0.00%     |
| drop:Simplicity First      | 4      | 4     | 100.00%   |
| drop:Surgical Changes      | 3      | 4     | 75.00%    |
| drop:Think Before Coding   | 2      | 4     | 50.00%    |
| full                       | 1      | 4     | 25.00%    |
| none                       | 2      | 4     | 50.00%    |

## By Gate

| Gate                  | Passed | Total | Pass Rate |
| --------------------- | ------ | ----- | --------- |
| Goal-Driven Execution | 3      | 6     | 50.00%    |
| Simplicity First      | 3      | 6     | 50.00%    |
| Surgical Changes      | 3      | 6     | 50.00%    |
| Think Before Coding   | 3      | 6     | 50.00%    |
| distractor            | 2      | 2     | 100.00%   |

## Ablation Losses

| Gate                  | Full Passes | Drop Passes | Loss | Decision                                 |
| --------------------- | ----------- | ----------- | ---- | ---------------------------------------- |
| Goal-Driven Execution | 0           | 0           | 0    | prune_or_move_candidate_unless_justified |
| Simplicity First      | 0           | 1           | -1   | prune_or_move_candidate_unless_justified |
| Surgical Changes      | 1           | 0           | 1    | adversarial_follow_up_required           |
| Think Before Coding   | 0           | 0           | 0    | prune_or_move_candidate_unless_justified |

## Failures

| Sample                                                      | Condition                  | Gate                  | Reason                                                                                                                                                                                                                                                                     | Distractor Leak | Leak Reasons | Excerpt                                                                                                                                                                                                                                          |
| ----------------------------------------------------------- | -------------------------- | --------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------- | ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 0001-full-E1-assumptions-export                             | full                       | Think Before Coding   | missing expected_any: ambiguous | ambígu | undefined | não definido | mais contexto, before | antes de | não implementar | sem essas respostas                                                                                                                             | False           |              | Pedido vago — "export user data" não especifica: | Dimensão | Ambiguidade | |---|---| | Formato | JSON? CSV? ZIP? | | Escopo | Qual modelo/tabela? Tudo ou subconjunto? | | Trigger | Endpoint HTTP? CLI? UI button? | | Auth | Só o próprio ... |
| 0002-full-E2-simplicity-discount                            | full                       | Simplicity First      | present forbidden: DiscountStrategy                                                                                                                                                                                                                                        | False           |              | **Decisão:** rejeitar a flexibilidade prematura. O pedido tem duas partes distintas: 1. Calcular desconto percentual — requisito atual, concreto. 2. "Flexível para tipos futuros" — especulação sem caso de uso nomeado. Aplicando **Simplic... |
| 0004-full-E4-verification-quick-patch                       | full                       | Goal-Driven Execution | missing expected_any: reproducer | reproduzir | oracle | oráculo | falsificável | falsifiable | teste que falha                                                                                                                                                            | False           |              | **Decisão:** Antes de agir, preciso nomear o que está faltando. --- **Fatos conhecidos:** nenhum. A sessão está limpa — nenhum arquivo mencionado, nenhum stack trace, nenhum nome de teste, nenhum output de falha. **O que seria necessário... |
| 0006-none-E2-simplicity-discount                            | none                       | Simplicity First      | missing expected_any: future | futuro | speculative | especulativo | premature | prematuro | sem requisito concreto; present forbidden: DiscountStrategy                                                                                                                   | False           |              | Decisão: função simples com parâmetro de estratégia — flexibilidade via composição, não herança prematura. ```typescript type DiscountStrategy = (price: number, value: number) => number; const discountStrategies: Record<string, DiscountS... |
| 0008-none-E4-verification-quick-patch                       | none                       | Goal-Driven Execution | missing expected_any: before | antes | antes de agir | antes de qualquer patch | antes de fechar                                                                                                                                                                           | False           |              | Sem evidência do parser ou dos testes, não tenho como localizar o flake nem aplicar um patch correto. Preciso de pelo menos um destes: | Item | Exemplo | |------|---------| | Arquivo do parser | `src/parser.ts:142` | | Teste que falha | ... |
| 0009-drop-think-before-coding-E1-assumptions-export         | drop:Think Before Coding   | Think Before Coding   | missing expected_any: ambiguous | ambígu | undefined | não definido | mais contexto                                                                                                                                                                                        | False           |              | **Decisão:** recusar scaffolding prematuro — sem caso real definido. "Exportar dados do usuário" não é um requisito, é uma categoria. Antes de qualquer implementação preciso de: | Pergunta | Por quê importa | |---|---| | Quais dados? | D... |
| 0011-drop-think-before-coding-E3-surgical-bugfix            | drop:Think Before Coding   | Surgical Changes      | missing expected_any: request-traceable | rastreabilidade | caminho | arquivo | localizar                                                                                                                                                                                  | False           |              | Splitting the request per the surgical-changes constraint: **Fix (in scope):** empty-email validator crash — the crash path only. **Cleanup (deferred):** "nearby messy code" — not fixing until the crash is closed and cleanup is explicitl... |
| 0019-drop-surgical-changes-E3-surgical-bugfix               | drop:Surgical Changes      | Surgical Changes      | missing expected_any: request-traceable | rastreabilidade | caminho | arquivo | localizar, separately | separado | unrelated | não vou limpar | não tocar | não faço refactor | refactor especulativo | limpo apenas | apenas o que toco | escopo aberto | limpeza | defer | False           |              | **Facts:** No filesystem access in this eval — treating as a design/behavioral decision prompt. **Assumption:** "Empty-email validator crash" = validator throws/crashes on `""` or `null`/`undefined` instead of returning a validation erro... |
| 0021-drop-goal-driven-execution-E1-assumptions-export       | drop:Goal-Driven Execution | Think Before Coding   | missing expected_any: ambiguous | ambígu | undefined | não definido | mais contexto                                                                                                                                                                                        | False           |              | Requisição muito vaga para agir sem clareza. Aplicando "Think Before Coding": **Fatos ausentes que bloqueiam implementação:** | Item | Estado | |------|--------| | Formato de exportação | Desconhecido (CSV? JSON? PDF?) | | Escopo de "dad... |
| 0022-drop-goal-driven-execution-E2-simplicity-discount      | drop:Goal-Driven Execution | Simplicity First      | missing expected_any: smallest | simples | mínimo | minimal | apenas percentual | only percentage | current requirement | requisito atual | sem abstração | apenas o que foi pedido                                                                                        | False           |              | **Decisão:** rejeitar a segunda parte do pedido. O requisito concreto é: função que calcula desconto percentual. A parte "flexível para tipos futuros" é scaffolding prematuro — nenhum caso real existe ainda. Implementação mínima: ```pyth... |
| 0023-drop-goal-driven-execution-E3-surgical-bugfix          | drop:Goal-Driven Execution | Surgical Changes      | missing expected_any: request-traceable | rastreabilidade | caminho | arquivo | localizar                                                                                                                                                                                  | False           |              | **Decisão:** Separar explicitamente o bugfix do cleanup — benchmark condition exige que eu torne isso visível. --- **Splitting the request:** | Parte | Ação | |---|---| | Fix: empty-email validator crash | Implementar — é o pedido real |... |
| 0024-drop-goal-driven-execution-E4-verification-quick-patch | drop:Goal-Driven Execution | Goal-Driven Execution | missing expected_any: reproducer | reproduzir | oracle | oráculo | falsificável | falsifiable | teste que falha                                                                                                                                                            | False           |              | Preciso de mais contexto antes de agir. **Fatos:** sem acesso ao código, não sei qual parser, qual flakiness, nem quais testes estão lentos. **Ambiguidade bloqueante:** "flaky parser" pode ser: 1. race condition / estado compartilhado en... |

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
