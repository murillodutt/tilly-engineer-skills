---
tds_id: evidence.context_mesh.behavior_v1_rc_claude_2026_05_05_convergence_01
tds_class: evidence
status: active
consumer: benchmark reviewers
source_of_truth: false
evidence_level: L4
---

# Context Mesh Benchmark Report

Run ID: `behavior-v1-rc-claude-2026-05-05-convergence-01`

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
| Dataset SHA | `0a2611260d873e5cb3c56e1d00778ef56eb95642b29c787634b7c22dc1bec893` |
| Git HEAD | `5941eb312ba2c5359c319acc9991eb80fe65531b` |
| Planned calls | `26` |
| Executed calls | `26` |
| Pass rate | `34.62%` |

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
| distractor_fail_rate      | 0.5            |
| distractor_leak_rate      | 0.0            |
| all_failures_have_excerpt | True           |
| dataset_sha_present       | True           |
| git_head_present          | True           |
| backend_declared          | True           |
| backend_error_count       | 1              |
| grader_version_declared   | True           |
| grader_sha_present        | True           |
| evidence_limits_declared  | True           |

## NO-GO

- full condition did not outperform none
- backend errors occurred during execution

## By Condition

| Condition                  | Passed | Total | Pass Rate |
| -------------------------- | ------ | ----- | --------- |
| distractor                 | 1      | 2     | 50.00%    |
| drop:Goal-Driven Execution | 3      | 4     | 75.00%    |
| drop:Simplicity First      | 0      | 4     | 0.00%     |
| drop:Surgical Changes      | 2      | 4     | 50.00%    |
| drop:Think Before Coding   | 0      | 4     | 0.00%     |
| full                       | 1      | 4     | 25.00%    |
| none                       | 2      | 4     | 50.00%    |

## By Gate

| Gate                  | Passed | Total | Pass Rate |
| --------------------- | ------ | ----- | --------- |
| Goal-Driven Execution | 0      | 6     | 0.00%     |
| Simplicity First      | 3      | 6     | 50.00%    |
| Surgical Changes      | 1      | 6     | 16.67%    |
| Think Before Coding   | 4      | 6     | 66.67%    |
| distractor            | 1      | 2     | 50.00%    |

## Ablation Losses

| Gate                  | Full Passes | Drop Passes | Loss | Decision                                 |
| --------------------- | ----------- | ----------- | ---- | ---------------------------------------- |
| Goal-Driven Execution | 0           | 0           | 0    | prune_or_move_candidate_unless_justified |
| Simplicity First      | 0           | 0           | 0    | prune_or_move_candidate_unless_justified |
| Surgical Changes      | 0           | 0           | 0    | prune_or_move_candidate_unless_justified |
| Think Before Coding   | 1           | 0           | 1    | adversarial_follow_up_required           |

## Failures

| Sample                                                      | Condition                  | Gate                  | Reason                                                                                                                                                                                                                                                                                                                                             | Distractor Leak | Leak Reasons | Excerpt                                                                                                                                                                                                                                          |
| ----------------------------------------------------------- | -------------------------- | --------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------- | ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 0002-full-E2-simplicity-discount                            | full                       | Simplicity First      | missing expected_any: smallest | simples | mínimo | minimal | apenas percentual | only percentage | current requirement | requisito atual | sem abstração                                                                                                                                                                                          | False           |              | Rejeito a parte "flexível para tipos futuros de desconto" — é scaffolding prematuro sem caso real. Implemento apenas o que foi pedido: função que calcula desconto percentual. ```python def apply_percentage_discount(price: float, discount... |
| 0003-full-E3-surgical-bugfix                                | full                       | Surgical Changes      | missing expected_any: crash | empty-email | e-mail vazio | email vazio, separately | separado | unrelated | não vou limpar | não tocar | não faço refactor | refactor especulativo | limpo apenas | apenas o que toco | escopo aberto                                                                                                              | False           |              | Vou localizar o validador de e-mail e o código próximo antes de agir.                                                                                                                                                                            |
| 0004-full-E4-verification-quick-patch                       | full                       | Goal-Driven Execution | missing expected_any: reproducer | reproduzir | oracle | oráculo | falsificável | falsifiable                                                                                                                                                                                                                                                      | False           |              | Preciso de mais contexto antes de agir. **Qual parser, em qual arquivo?** O repositório está limpo e sem alterações pendentes. Sem um caminho, nome de função, ou mensagem de erro específica, qualquer patch seria um chute. Me passa: o arq... |
| 0007-none-E3-surgical-bugfix                                | none                       | Surgical Changes      | missing expected_any: separately | separado | unrelated | não vou limpar | não tocar | não faço refactor | refactor especulativo | limpo apenas | apenas o que toco | escopo aberto                                                                                                                                                                | False           |              | Vou localizar o validador de e-mail vazio e o código ao redor antes de agir.                                                                                                                                                                     |
| 0008-none-E4-verification-quick-patch                       | none                       | Goal-Driven Execution | missing expected_any: reproducer | reproduzir | oracle | oráculo | falsificável | falsifiable                                                                                                                                                                                                                                                      | False           |              | Preciso ver o parser e os testes antes de agir.                                                                                                                                                                                                  |
| 0009-drop-think-before-coding-E1-assumptions-export         | drop:Think Before Coding   | Think Before Coding   | missing expected_any: ambiguous | ambígu | undefined | não definido | mais contexto                                                                                                                                                                                                                                                                | False           |              | Pedido muito vago para agir com segurança. Preciso de três respostas antes de tocar no código: | # | Pergunta | Por quê importa | |---|----------|-----------------| | 1 | Qual entidade é "user data"? (ex: perfil, histórico de atividades,... |
| 0010-drop-think-before-coding-E2-simplicity-discount        | drop:Think Before Coding   | Simplicity First      | missing expected_any: smallest | simples | mínimo | minimal | apenas percentual | only percentage | current requirement | requisito atual | sem abstração                                                                                                                                                                                          | False           |              | Recuso o escopo como especificado. "Flexível para futuros tipos de desconto" é scaffolding prematuro — não há caso real ainda. A regra **Simplicity First** proíbe abstrações sem requisito concreto existente. O que implemento: uma função ... |
| 0011-drop-think-before-coding-E3-surgical-bugfix            | drop:Think Before Coding   | Surgical Changes      | missing expected_any: separately | separado | unrelated | não vou limpar | não tocar | não faço refactor | refactor especulativo | limpo apenas | apenas o que toco | escopo aberto                                                                                                                                                                | False           |              | Vou localizar o validador de e-mail vazio antes de agir.                                                                                                                                                                                         |
| 0012-drop-think-before-coding-E4-verification-quick-patch   | drop:Think Before Coding   | Goal-Driven Execution | missing expected_any: reproducer | reproduzir | oracle | oráculo | falsificável | falsifiable                                                                                                                                                                                                                                                      | False           |              | Qual parser está falhando e qual é o teste lento? Preciso do arquivo e do erro antes de tocar em qualquer coisa.                                                                                                                                 |
| 0013-drop-simplicity-first-E1-assumptions-export            | drop:Simplicity First      | Think Before Coding   | missing expected_any: ambiguous | ambígu | undefined | não definido | mais contexto                                                                                                                                                                                                                                                                | False           |              | Pedido vago — preciso de três âncoras antes de agir: | Âncora | Opções / perguntas | |---|---| | **O quê** | Quais campos exportar? Todos os dados do usuário, ou um subconjunto (perfil, histórico, preferências)? | | **Formato** | CSV, JS... |
| 0014-drop-simplicity-first-E2-simplicity-discount           | drop:Simplicity First      | Simplicity First      | missing expected_any: smallest | simples | mínimo | minimal | apenas percentual | only percentage | current requirement | requisito atual | sem abstração                                                                                                                                                                                          | False           |              | Sem acesso ao browser. Vou parar aqui e responder diretamente com base no contexto. --- **Posição:** a abstração pedida ("flexível para tipos futuros") não tem tipos futuros definidos. A regra é: três casos similares justificam abstração... |
| 0015-drop-simplicity-first-E3-surgical-bugfix               | drop:Simplicity First      | Surgical Changes      | missing expected_any: crash | empty-email | e-mail vazio | email vazio, separately | separado | unrelated | não vou limpar | não tocar | não faço refactor | refactor especulativo | limpo apenas | apenas o que toco | escopo aberto                                                                                                              | False           |              | Preciso ver o código antes de agir. Vou localizar o validador de e-mail.                                                                                                                                                                         |
| 0016-drop-simplicity-first-E4-verification-quick-patch      | drop:Simplicity First      | Goal-Driven Execution | missing expected_any: reproducer | reproduzir | oracle | oráculo | falsificável | falsifiable                                                                                                                                                                                                                                                      | False           |              | Preciso de contexto concreto antes de qualquer patch. **Fatos conhecidos:** nenhum — não identifiquei qual parser, qual arquivo, qual teste falha. **Bloqueio:** sem o nome do arquivo/função/teste, qualquer mudança é chute. Patch cirúrgic... |
| 0019-drop-surgical-changes-E3-surgical-bugfix               | drop:Surgical Changes      | Surgical Changes      | missing expected_any: validator | validador | email | e-mail, crash | empty-email | e-mail vazio | email vazio, request-traceable | rastreabilidade | caminho | arquivo | localizar, separately | separado | unrelated | não vou limpar | não tocar | não faço refactor | refactor especulativo | limpo apenas | apenas o que toco | escopo aberto | False           |              | BACKEND_ERROR: claude CLI failed for 0019-drop-surgical-changes-E3-surgical-bugfix: Error: Exceeded USD budget (0.25)                                                                                                                            |
| 0020-drop-surgical-changes-E4-verification-quick-patch      | drop:Surgical Changes      | Goal-Driven Execution | missing expected_any: parser, before | antes | antes de agir | antes de qualquer patch | antes de fechar                                                                                                                                                                                                                                           | False           |              | Sem evidência concreta do que está falhando, não há como fazer um patch cirúrgico. Preciso de pelo menos um destes: | Dado | Por quê | |------|---------| | Nome do teste ou arquivo | Para localizar o código relevante | | Mensagem de erro... |
| 0024-drop-goal-driven-execution-E4-verification-quick-patch | drop:Goal-Driven Execution | Goal-Driven Execution | missing expected_any: reproducer | reproduzir | oracle | oráculo | falsificável | falsifiable, before | antes | antes de agir | antes de qualquer patch | antes de fechar                                                                                                                                                                          | False           |              | Preciso de mais contexto para agir. "Parser flaky" e "tests are slow" são sintomas, não localizações. Perguntas que mudam a ação (e portanto peço): 1. Qual arquivo/módulo é o parser? (nome ou caminho) 2. Qual é a falha — erro de parse es... |
| 0025-distractor-D1-typo                                     | distractor                 | distractor            | missing expected_any: fix | corrigir | corrijo                                                                                                                                                                                                                                                                                                     | False           |              | Vou usar uma abordagem diferente para ler e editar o README. Preciso de acesso de leitura/escrita a arquivos. Você pode aprovar o acesso de leitura de arquivo ou confirmar se posso usar as ferramentas de shell? Enquanto isso, a correção ... |

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
