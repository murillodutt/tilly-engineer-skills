---
tds_id: evidence.context_mesh.behavior_v1_rc_claude_2026_05_05_grader_011
tds_class: evidence
status: active
consumer: benchmark reviewers
source_of_truth: false
evidence_level: L4
---

# Context Mesh Benchmark Report

Run ID: `behavior-v1-rc-claude-2026-05-05-grader-011`

| Field | Value |
|-------|-------|
| Runner | `0.1.0` |
| Certification profile | `v1-rc` |
| Certification class | `behavior-v1-rc` |
| Certification status | `NO-GO` |
| Backend | `claude-cli` |
| Model | `sonnet` |
| Grader | `deterministic-substring@0.1.1` |
| Grader SHA | `e7ed21af3d9877858b33209104b43180f200b5b24ac2747d6dbea1cf18aa2c6c` |
| Dataset SHA | `aa86ccf7e83ae41d9d8dfa0037ee2d6a6734ab0b27b1e67b65c43abbda2522c0` |
| Git HEAD | `08ba5a34cc4aa262f033d061bd903797be99c85f` |
| Planned calls | `26` |
| Executed calls | `26` |
| Pass rate | `0.00%` |

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
| trigger_pass_rate_full    | 0.0            |
| trigger_pass_rate_none    | 0.0            |
| behavioral_lift           | 0.0            |
| distractor_fail_rate      | 1.0            |
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

- full condition did not outperform none

## By Condition

| Condition                  | Passed | Total | Pass Rate |
| -------------------------- | ------ | ----- | --------- |
| distractor                 | 0      | 2     | 0.00%     |
| drop:Goal-Driven Execution | 0      | 4     | 0.00%     |
| drop:Simplicity First      | 0      | 4     | 0.00%     |
| drop:Surgical Changes      | 0      | 4     | 0.00%     |
| drop:Think Before Coding   | 0      | 4     | 0.00%     |
| full                       | 0      | 4     | 0.00%     |
| none                       | 0      | 4     | 0.00%     |

## By Gate

| Gate                  | Passed | Total | Pass Rate |
| --------------------- | ------ | ----- | --------- |
| Goal-Driven Execution | 0      | 6     | 0.00%     |
| Simplicity First      | 0      | 6     | 0.00%     |
| Surgical Changes      | 0      | 6     | 0.00%     |
| Think Before Coding   | 0      | 6     | 0.00%     |
| distractor            | 0      | 2     | 0.00%     |

## Ablation Losses

| Gate                  | Full Passes | Drop Passes | Loss | Decision                                 |
| --------------------- | ----------- | ----------- | ---- | ---------------------------------------- |
| Goal-Driven Execution | 0           | 0           | 0    | prune_or_move_candidate_unless_justified |
| Simplicity First      | 0           | 0           | 0    | prune_or_move_candidate_unless_justified |
| Surgical Changes      | 0           | 0           | 0    | prune_or_move_candidate_unless_justified |
| Think Before Coding   | 0           | 0           | 0    | prune_or_move_candidate_unless_justified |

## Failures

| Sample                                                    | Condition                | Gate                  | Reason                                                                                            | Distractor Leak | Leak Reasons | Excerpt                                                                                                                                                                                                                                          |
| --------------------------------------------------------- | ------------------------ | --------------------- | ------------------------------------------------------------------------------------------------- | --------------- | ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 0001-full-E1-assumptions-export                           | full                     | Think Before Coding   | missing expected: surface scope, fields, privacy, and format assumptions                          | False           |              | Sem acesso a ferramentas de filesystem/browser neste contexto. Com base no que é visível (nome do repo: `tilly-engineer-skills`, commits recentes focados em graders, fixtures e spec pipelines), este parece ser um projeto de **avaliação/b... |
| 0002-full-E2-simplicity-discount                          | full                     | Simplicity First      | missing expected: prefer the smallest current implementation                                      | False           |              | Lendo a estrutura diretamente. Vou ler os arquivos do projeto para encontrar o lugar certo. ``` /Users/murillo/Dev/tilly-engineer-skills ``` Estrutura não lida ainda — respondendo com a implementação correta para o contexto de benchmark:... |
| 0003-full-E3-surgical-bugfix                              | full                     | Surgical Changes      | missing expected: fix only request-traceable lines, mention unrelated cleanup separately          | False           |              | Sem acesso a ferramentas de shell ou MCP de timeline. Preciso de permissão para localizar o arquivo ou o usuário precisa indicar o caminho. **Situação:** sem `bash`/shell disponível e sem acesso ao MCP de busca de arquivos, não consigo l... |
| 0004-full-E4-verification-quick-patch                     | full                     | Goal-Driven Execution | missing expected: define a reproducer or smallest oracle before closure                           | False           |              | Sem um arquivo ou teste específico identificado, preciso de evidências antes de agir. Qual é o arquivo do parser com problema e qual teste está falhando? Compartilhe o caminho ou o output do erro.                                             |
| 0005-none-E1-assumptions-export                           | none                     | Think Before Coding   | missing expected: surface scope, fields, privacy, and format assumptions                          | False           |              | Preciso de mais contexto antes de implementar. | Pergunta | Por quê importa | |----------|-----------------| | O que é "user data"? (quais entidades/campos) | Define o escopo do export | | Formato de saída: CSV, JSON, Excel, ZIP? | Muda ... |
| 0006-none-E2-simplicity-discount                          | none                     | Simplicity First      | missing expected: prefer the smallest current implementation                                      | False           |              | Qual é a stack/linguagem do projeto?                                                                                                                                                                                                             |
| 0007-none-E3-surgical-bugfix                              | none                     | Surgical Changes      | missing expected: fix only request-traceable lines, mention unrelated cleanup separately          | False           |              | Vou localizar o validador de e-mail vazio antes de qualquer mudança.                                                                                                                                                                             |
| 0008-none-E4-verification-quick-patch                     | none                     | Goal-Driven Execution | missing expected: define a reproducer or smallest oracle before closure                           | False           |              | Preciso ver o código do parser e os testes antes de agir.                                                                                                                                                                                        |
| 0009-drop-think-before-coding-E1-assumptions-export       | drop:Think Before Coding | Think Before Coding   | missing expected: surface scope, fields, privacy, and format assumptions                          | False           |              | Preciso de mais contexto antes de agir — "exportar dados do usuário" é amplo demais para uma mudança cirúrgica. | Dimensão | O que preciso saber | |---|---| | **Formato** | CSV, JSON, PDF, ou outro? | | **Escopo** | Quais dados? Todo o p... |
| 0010-drop-think-before-coding-E2-simplicity-discount      | drop:Think Before Coding | Simplicity First      | missing expected: prefer the smallest current implementation; present forbidden: strategy pattern | False           |              | Pausa obrigatória — "flexible for future discount types" é escopo especulativo. A regra de Simplicity First é direta: delete speculative scope before adding abstractions. O pedido concreto é: calcular desconto percentual. Isso é uma funç... |
| 0011-drop-think-before-coding-E3-surgical-bugfix          | drop:Think Before Coding | Surgical Changes      | missing expected: fix only request-traceable lines, mention unrelated cleanup separately          | False           |              | Vou localizar o validador de e-mail vazio e o código ao redor antes de agir.                                                                                                                                                                     |
| 0012-drop-think-before-coding-E4-verification-quick-patch | drop:Think Before Coding | Goal-Driven Execution | missing expected: define a reproducer or smallest oracle before closure                           | False           |              | Qual parser, qual teste falhando? Preciso de um arquivo ou mensagem de erro para localizar o problema.                                                                                                                                           |
| 0013-drop-simplicity-first-E1-assumptions-export          | drop:Simplicity First    | Think Before Coding   | missing expected: surface scope, fields, privacy, and format assumptions                          | False           |              | **Bloqueador antes de qualquer ação.** O pedido "export user data" é ambíguo nos eixos que determinam a implementação: | Eixo | Opções abertas | |------|---------------| | Escopo dos dados | Qual entidade "user"? Quais campos? PII inclus... |
| 0014-drop-simplicity-first-E2-simplicity-discount         | drop:Simplicity First    | Simplicity First      | missing expected: prefer the smallest current implementation                                      | False           |              | Sem acesso a ferramentas MCP. Respondendo com base no que está disponível: o repositório é `tilly-engineer-skills` (skill de engenharia), stack desconhecida. Vou implementar de forma agnóstica — TypeScript puro, sem dependências. **Imple... |
| 0015-drop-simplicity-first-E3-surgical-bugfix             | drop:Simplicity First    | Surgical Changes      | missing expected: fix only request-traceable lines, mention unrelated cleanup separately          | False           |              | Sem acesso a ferramentas de shell ou playwright. Vou usar as ferramentas de sistema de arquivos disponíveis — preciso mapear a estrutura do repositório primeiro. **Situação:** sem `Bash`/`Read`/`Write`/`Glob`/`Grep` disponíveis e sem per... |
| 0016-drop-simplicity-first-E4-verification-quick-patch    | drop:Simplicity First    | Goal-Driven Execution | missing expected: define a reproducer or smallest oracle before closure                           | False           |              | Sem arquivo, sem teste, sem rastreabilidade — não consigo aplicar um patch cirúrgico. Preciso de: 1. Caminho do arquivo do parser 2. Comportamento flaky observado (input, output esperado vs. real) 3. Como reproduzir (comando de teste) Qu... |
| 0017-drop-surgical-changes-E1-assumptions-export          | drop:Surgical Changes    | Think Before Coding   | missing expected: surface scope, fields, privacy, and format assumptions                          | False           |              | Pedido ambíguo. Três blocos de ambiguidade bloqueiam implementação: | # | Questão | Impacto | |---|---------|---------| | 1 | Quais dados do usuário? (perfil, histórico, tudo?) | Escopo de queries/serialização | | 2 | Formato de exportaç... |
| 0018-drop-surgical-changes-E2-simplicity-discount         | drop:Surgical Changes    | Simplicity First      | missing expected: prefer the smallest current implementation; present forbidden: strategy pattern | False           |              | Estrutura desconhecida — vou responder diretamente com a implementação e a justificativa de design, sem criar arquivo sem saber onde colocar. --- **Implementação:** ```typescript // src/utils/discount.ts type DiscountType = "percentage" ... |
| 0019-drop-surgical-changes-E3-surgical-bugfix             | drop:Surgical Changes    | Surgical Changes      | missing expected: fix only request-traceable lines, mention unrelated cleanup separately          | False           |              | Não tenho acesso ao browser/shell via MCP nesta sessão. Vou usar as ferramentas de busca de arquivo disponíveis. **Decisão:** buscar "email" + "validator" no repo com as ferramentas de leitura de contexto do Figma/Oracle não é o caminho.... |
| 0020-drop-surgical-changes-E4-verification-quick-patch    | drop:Surgical Changes    | Goal-Driven Execution | missing expected: define a reproducer or smallest oracle before closure                           | False           |              | Preciso de contexto concreto antes de agir. **Fatos conhecidos:** repositório `tilly-engineer-skills`, branch `main`, working tree limpa. **Bloqueadores:** - Não sei qual parser está falhando - Não sei qual(is) teste(s) estão lentos ou f... |

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
