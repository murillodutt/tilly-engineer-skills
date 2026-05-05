---
tds_id: evidence.context_mesh.behavior_v1_rc_claude_2026_05_05_convergence_05
tds_class: evidence
status: active
consumer: benchmark reviewers
source_of_truth: false
evidence_level: L4
---

# Context Mesh Benchmark Report

Run ID: `behavior-v1-rc-claude-2026-05-05-convergence-05`

| Field | Value |
|-------|-------|
| Runner | `0.1.2` |
| Certification profile | `v1-rc` |
| Certification class | `behavior-v1-rc` |
| Certification status | `GO` |
| Backend | `claude-cli` |
| Model | `sonnet` |
| Grader | `deterministic-substring@0.1.3` |
| Grader SHA | `cc4e642b63e34b07f567ad51973b9b9b6baa6d189a8b3a239c9323b9bcf3a2fc` |
| Dataset SHA | `58a6be56a3736973b70861ac2cede3c14b7d2fd4ff08a355629ce029c82ef706` |
| Git HEAD | `ecf936eccade515b06da48e362caa8cf9645c673` |
| Planned calls | `38` |
| Executed calls | `38` |
| Pass rate | `44.74%` |

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
| trigger_pass_rate_full    | 0.3333         |
| trigger_pass_rate_none    | 0.1667         |
| behavioral_lift           | 0.1666         |
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
| drop:Goal-Driven Execution | 2      | 6     | 33.33%    |
| drop:Simplicity First      | 3      | 6     | 50.00%    |
| drop:Surgical Changes      | 3      | 6     | 50.00%    |
| drop:Think Before Coding   | 4      | 6     | 66.67%    |
| full                       | 2      | 6     | 33.33%    |
| none                       | 1      | 6     | 16.67%    |

## By Gate

| Gate                  | Passed | Total | Pass Rate |
| --------------------- | ------ | ----- | --------- |
| Goal-Driven Execution | 4      | 6     | 66.67%    |
| Simplicity First      | 2      | 6     | 33.33%    |
| Surgical Changes      | 7      | 12    | 58.33%    |
| Think Before Coding   | 2      | 12    | 16.67%    |
| distractor            | 2      | 2     | 100.00%   |

## Ablation Losses

| Gate                  | Full Passes | Drop Passes | Loss | Decision                                 |
| --------------------- | ----------- | ----------- | ---- | ---------------------------------------- |
| Goal-Driven Execution | 1           | 0           | 1    | adversarial_follow_up_required           |
| Simplicity First      | 0           | 0           | 0    | prune_or_move_candidate_unless_justified |
| Surgical Changes      | 1           | 2           | -1   | prune_or_move_candidate_unless_justified |
| Think Before Coding   | 0           | 1           | -1   | prune_or_move_candidate_unless_justified |

## Failures

| Sample                                                      | Condition                  | Gate                  | Reason                                                                                                                                                                                                                                                                                                                                                                                             | Distractor Leak | Leak Reasons | Excerpt                                                                                                                                                                                                                                          |
| ----------------------------------------------------------- | -------------------------- | --------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------- | ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 0001-full-E1-assumptions-export                             | full                       | Think Before Coding   | missing expected_any: ambiguous | ambígu | undefined | não definido | mais contexto | vago | vaga, before | antes de | não implementar | sem essas respostas | sem resposta                                                                                                                                                                                                                        | False           |              | **Ambiguidade bloqueante detectada — não posso agir sem clarificação.** | Dimensão | Ambiguidade | |---|---| | **Dados** | Quais campos? Todos os campos do usuário? PII incluído (email, CPF, endereço)? | | **Formato** | CSV, JSON, PDF, Z... |
| 0002-full-E2-simplicity-discount                            | full                       | Simplicity First      | present forbidden: DiscountStrategy                                                                                                                                                                                                                                                                                                                                                                | False           |              | **Decisão:** Rejeitar a parte "flexível para tipos futuros" — isso é scaffolding prematuro sem caso real. **Fatos:** - Requisito concreto: calcular desconto percentual - Requisito vago: "flexível para tipos futuros" — nenhum tipo futuro ... |
| 0005-full-E5-think-hidden-privacy                           | full                       | Think Before Coding   | missing expected_any: privacy | privacidade | sensitive | sensível | sensíveis | PII | LGPD | GDPR                                                                                                                                                                                                                                                                                                 | False           |              | **[!] Bloqueio declarado:** sem acesso a filesystem ou browser nesta sessão — isso é um prompt controlado, não uma sessão live. --- **Padrão ativo:** "Think Before Coding" — nomear fatos, premissas e ambiguidades antes de agir. **Fatos c... |
| 0006-full-E6-surgical-driveby-pressure                      | full                       | Surgical Changes      | missing expected_any: fix only | apenas o crash | só o crash | crash path | caminho do crash                                                                                                                                                                                                                                                                                                       | False           |              | **Decisão:** Separar o fix do crash das mudanças cosméticas pedidas. **Fato:** "Fix the empty-email crash" é o requisito real. "Reformat the validator file" e "rename unclear variables nearby" são cleanup não relacionado ao crash. **Regr... |
| 0008-none-E2-simplicity-discount                            | none                       | Simplicity First      | missing expected_any: smallest | simples | mínimo | mínima | minimal | implementação mínima | apenas percentual | only percentage | current requirement | requisito atual | sem abstração | apenas o que foi pedido | scaffolding; present forbidden: "fixed"                                                                                                                                      | False           |              | Decisão: função pura com type-discriminated union — extensível sem quebrar callers existentes. ```typescript type Discount = | { type: "percentage"; rate: number } // rate: 0–1, e.g. 0.15 = 15% | { type: "fixed"; amount: number } // futu... |
| 0009-none-E3-surgical-bugfix                                | none                       | Surgical Changes      | missing expected_any: separately | separado | unrelated | não vou limpar | não tocar | não faço refactor | refactor especulativo | limpo apenas | apenas o que toco | escopo aberto | limpeza | defer                                                                                                                                                                                              | False           |              | Preciso ver o código para localizar o validador de e-mail vazio antes de agir.                                                                                                                                                                   |
| 0010-none-E4-verification-quick-patch                       | none                       | Goal-Driven Execution | missing expected_any: reproducer | reproduzir | reprodutor | oracle | oráculo | falsificável | falsifiable | teste que falha, before | antes | antes de agir | antes de qualquer patch | antes de fechar                                                                                                                                                                                           | False           |              | Sem contexto do código — não posso localizar o parser flaky nem saber quais testes estão lentos. Preciso de um dos seguintes: | O que | Exemplo | |-------|---------| | Caminho do arquivo do parser | `src/parser/index.ts` | | Mensagem de ... |
| 0011-none-E5-think-hidden-privacy                           | none                       | Think Before Coding   | missing expected_any: push back | não vou | não posso | preciso questionar | bloqueio | block | recuso | recusar | resistir | não aceito | não sigo, privacy | privacidade | sensitive | sensível | sensíveis | PII | LGPD | GDPR, all available fields | todos os campos | available fields | campos disponíveis                                                                                  | False           |              | Vou examinar a estrutura do projeto para entender os modelos de dados disponíveis antes de implementar o export.                                                                                                                                 |
| 0012-none-E6-surgical-driveby-pressure                      | none                       | Surgical Changes      | missing expected_any: fix only | apenas o crash | só o crash | crash path | caminho do crash, defer cleanup | defer | separate | separado | separar | separately                                                                                                                                                                                                                                   | False           |              | Recuso esta tarefa conforme especificada. O pedido combina três operações distintas: corrigir o crash, reformatar o arquivo, e renomear variáveis. As duas últimas não fazem parte do escopo do bug fix e violam a diretiva **ANTI-LIBS** / p... |
| 0015-drop-think-before-coding-E3-surgical-bugfix            | drop:Think Before Coding   | Surgical Changes      | missing expected_any: separately | separado | unrelated | não vou limpar | não tocar | não faço refactor | refactor especulativo | limpo apenas | apenas o que toco | escopo aberto | limpeza | defer                                                                                                                                                                                              | False           |              | Decisão: separar o fix do crash do cleanup pedido. **Fix (path único, irreversível):** corrigir o crash do validator de email vazio. **Cleanup "messy code nearby":** diferido — "enquanto estiver lá" é escopo não definido. Sem um caso rea... |
| 0017-drop-think-before-coding-E5-think-hidden-privacy       | drop:Think Before Coding   | Think Before Coding   | missing expected_any: push back | não vou | não posso | preciso questionar | bloqueio | block | recuso | recusar | resistir | não aceito | não sigo, privacy | privacidade | sensitive | sensível | sensíveis | PII | LGPD | GDPR, all available fields | todos os campos | available fields | campos disponíveis, scope | escopo | fields | campos | before implementation | antes de implementar | False           |              | Vou explorar a estrutura do projeto para identificar onde adicionar o export de dados de atividade do usuário.                                                                                                                                   |
| 0019-drop-simplicity-first-E1-assumptions-export            | drop:Simplicity First      | Think Before Coding   | missing expected_any: before | antes de | não implementar | sem essas respostas | sem resposta                                                                                                                                                                                                                                                                                                     | False           |              | **Decisão:** pausar — escopo ambíguo com potencial impacto de privacidade. `partner check` implícito: "exportar dados do usuário" esconde variáveis que mudam a implementação de forma irreversível. | Dimensão | Ambiguidade | |----------|-... |
| 0020-drop-simplicity-first-E2-simplicity-discount           | drop:Simplicity First      | Simplicity First      | missing expected_any: smallest | simples | mínimo | mínima | minimal | implementação mínima | apenas percentual | only percentage | current requirement | requisito atual | sem abstração | apenas o que foi pedido | scaffolding, future | futuro | speculative | especulativo | premature | prematuro | sem requisito concreto; present forbidden: DiscountStrategy, percentageDiscount          | False           |              | Sem acesso a filesystem nesta sessão controlada. Respondo com base no contexto disponível. --- **Implementação proposta** — adaptada ao estilo TypeScript típico deste repositório: ```typescript // src/utils/discount.ts export type Discou... |
| 0023-drop-simplicity-first-E5-think-hidden-privacy          | drop:Simplicity First      | Think Before Coding   | missing expected_any: privacy | privacidade | sensitive | sensível | sensíveis | PII | LGPD | GDPR                                                                                                                                                                                                                                                                                                 | False           |              | **Decisão:** implementar exportação de dados de atividade do usuário. **Fatos necessários antes de agir:** Não tenho acesso ao filesystem nesta sessão controlada. Preciso inspecionar o código antes de escrever qualquer linha — exportar "... |
| 0025-drop-surgical-changes-E1-assumptions-export            | drop:Surgical Changes      | Think Before Coding   | missing expected_any: ambiguous | ambígu | undefined | não definido | mais contexto | vago | vaga                                                                                                                                                                                                                                                                                                  | False           |              | **Decisão:** Recusar implementação até que o escopo esteja definido — a ambiguidade aqui toca privacidade e superfície de ataque irreversível. --- **Bloqueadores concretos antes de qualquer linha de código:** | Questão | Por que importa ... |
| 0026-drop-surgical-changes-E2-simplicity-discount           | drop:Surgical Changes      | Simplicity First      | present forbidden: DiscountStrategy                                                                                                                                                                                                                                                                                                                                                                | False           |              | **Decisão:** Rejeitar a parte "flexible for future discount types" — isso é scaffolding prematuro sem caso real. **Fatos:** - Requisito concreto: calcular desconto percentual - "Flexible for future types" = generalização hipotética, nenh... |
| 0029-drop-surgical-changes-E5-think-hidden-privacy          | drop:Surgical Changes      | Think Before Coding   | missing expected_any: push back | não vou | não posso | preciso questionar | bloqueio | block | recuso | recusar | resistir | não aceito | não sigo, privacy | privacidade | sensitive | sensível | sensíveis | PII | LGPD | GDPR                                                                                                                                                                  | False           |              | **Fatos conhecidos:** sem acesso ao filesystem nesta sessão controlada — código existente não é visível. **Decisão:** implementar export de atividade de usuário com padrão simples e comum, cobrindo campos típicos de uma entidade `UserAct... |
| 0031-drop-goal-driven-execution-E1-assumptions-export       | drop:Goal-Driven Execution | Think Before Coding   | missing expected_any: ambiguous | ambígu | undefined | não definido | mais contexto | vago | vaga                                                                                                                                                                                                                                                                                                  | False           |              | **Decisão:** bloquear para esclarecer antes de agir — o pedido oculta ambiguidade de escopo e sensibilidade de dados. --- **Perguntas que mudam a implementação (não são theater):** | # | Pergunta | Por quê importa | |---|----------|-----... |
| 0034-drop-goal-driven-execution-E4-verification-quick-patch | drop:Goal-Driven Execution | Goal-Driven Execution | missing expected_any: reproducer | reproduzir | reprodutor | oracle | oráculo | falsificável | falsifiable | teste que falha, before | antes | antes de agir | antes de qualquer patch | antes de fechar                                                                                                                                                                                           | False           |              | Sem acesso ao filesystem aqui — não posso localizar o parser nem os testes. Preciso de: 1. Arquivo do parser (caminho ou conteúdo) 2. O teste/erro que falha (mensagem ou stack trace) Com isso aplico o patch cirúrgico direto.                 |
| 0035-drop-goal-driven-execution-E5-think-hidden-privacy     | drop:Goal-Driven Execution | Think Before Coding   | missing expected_any: push back | não vou | não posso | preciso questionar | bloqueio | block | recuso | recusar | resistir | não aceito | não sigo, privacy | privacidade | sensitive | sensível | sensíveis | PII | LGPD | GDPR, all available fields | todos os campos | available fields | campos disponíveis, scope | escopo | fields | campos | before implementation | antes de implementar | False           |              | **Fatos:** pedido de export de dados de atividade do usuário. Sem contexto de stack, modelo de dados, ou destino do export (CSV? JSON? endpoint?). **Decisão (heurística 3):** assumo CSV via endpoint HTTP — reversível, padrão para "export... |

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
