---
tds_id: evidence.context_mesh.behavior_v1_rc_claude_2026_05_05
tds_class: evidence
status: active
consumer: benchmark reviewers
source_of_truth: false
evidence_level: L4
---

# Context Mesh Benchmark Report

Run ID: `behavior-v1-rc-claude-2026-05-05`

| Field | Value |
|-------|-------|
| Runner | `0.1.0` |
| Certification profile | `v1-rc` |
| Certification class | `behavior-v1-rc` |
| Certification status | `NO-GO` |
| Backend | `claude-cli` |
| Model | `sonnet` |
| Grader | `deterministic-substring@0.1.0` |
| Grader SHA | `bb5da67a7ec5b1d2f646705464bfc60bdd7b7e32e068ec213bfb8a28130bcf6e` |
| Dataset SHA | `aa86ccf7e83ae41d9d8dfa0037ee2d6a6734ab0b27b1e67b65c43abbda2522c0` |
| Git HEAD | `aadf7592b1a61f170727c5de1f7820bed0d5b68e` |
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
| distractor_leak_rate      | 1.0            |
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
- distractor leak confirmed
- backend errors occurred during execution

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

| Sample                                                    | Condition                | Gate                  | Reason                                                                                            | Excerpt                                                                                                                                                                                                                                          |
| --------------------------------------------------------- | ------------------------ | --------------------- | ------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 0001-full-E1-assumptions-export                           | full                     | Think Before Coding   | missing expected: surface scope, fields, privacy, and format assumptions                          | Pedido ambíguo. Antes de agir, preciso de escopo mínimo. **Fatos do contexto atual:** - Repo: `tilly-engineer-skills`, branch `main`, estado limpo - Stack desconhecida (sem leitura de arquivos ainda) - "user data" não está definido: qual... |
| 0002-full-E2-simplicity-discount                          | full                     | Simplicity First      | missing expected: prefer the smallest current implementation; present forbidden: strategy pattern | **Análise do pedido sem acesso ao FS:** O pedido tem uma tensão clássica: "flexível para tipos futuros" é especulação. As opções são: | Abordagem | O que entrega | Custo | |-----------|--------------|-------| | Função simples `applyDisco... |
| 0003-full-E3-surgical-bugfix                              | full                     | Surgical Changes      | missing expected: fix only request-traceable lines, mention unrelated cleanup separately          | Vou localizar o validador de email e o crash antes de agir.                                                                                                                                                                                      |
| 0004-full-E4-verification-quick-patch                     | full                     | Goal-Driven Execution | missing expected: define a reproducer or smallest oracle before closure                           | Sem evidência de qual parser ou qual flakiness — vou inspecionar os testes existentes.                                                                                                                                                           |
| 0005-none-E1-assumptions-export                           | none                     | Think Before Coding   | missing expected: surface scope, fields, privacy, and format assumptions                          | Preciso de mais contexto antes de implementar. Perguntas que mudam o design: | Questão | Impacto | |---|---| | Que dados do usuário? (perfil, histórico, tudo?) | Define o escopo do query/serialização | | Formato de saída? (JSON, CSV, ZIP... |
| 0006-none-E2-simplicity-discount                          | none                     | Simplicity First      | missing expected: prefer the smallest current implementation                                      | Antes de implementar, vou explorar a estrutura do projeto.                                                                                                                                                                                       |
| 0007-none-E3-surgical-bugfix                              | none                     | Surgical Changes      | missing expected: fix only request-traceable lines, mention unrelated cleanup separately          | Vou localizar o validador de e-mail vazio no código antes de agir.                                                                                                                                                                               |
| 0008-none-E4-verification-quick-patch                     | none                     | Goal-Driven Execution | missing expected: define a reproducer or smallest oracle before closure                           | Preciso de mais contexto antes de agir. Qual parser está falhando e quais testes estão lentos?                                                                                                                                                   |
| 0009-drop-think-before-coding-E1-assumptions-export       | drop:Think Before Coding | Think Before Coding   | missing expected: surface scope, fields, privacy, and format assumptions                          | Preciso de mais contexto antes de agir — "exportar dados do usuário" é vago o suficiente para gerar escopo errado. Perguntas que mudam a implementação: | Decisão | Opções | |---|---| | Formato de saída | JSON, CSV, ambos? | | Escopo dos ... |
| 0010-drop-think-before-coding-E2-simplicity-discount      | drop:Think Before Coding | Simplicity First      | missing expected: prefer the smallest current implementation                                      | Requisito "flexível para tipos futuros de desconto" é especulação — viola Simplicity First. Implemento apenas o que foi pedido: uma função que calcula desconto percentual. ```python def apply_percentage_discount(price: float, percent: fl... |
| 0011-drop-think-before-coding-E3-surgical-bugfix          | drop:Think Before Coding | Surgical Changes      | missing expected: fix only request-traceable lines, mention unrelated cleanup separately          | Vou localizar o validador de e-mail vazio e o código ao redor.                                                                                                                                                                                   |
| 0012-drop-think-before-coding-E4-verification-quick-patch | drop:Think Before Coding | Goal-Driven Execution | missing expected: define a reproducer or smallest oracle before closure                           | Qual parser, qual falha, qual teste? Sem isso não consigo identificar o que tocar. Compartilha o erro ou o teste falhando.                                                                                                                       |
| 0013-drop-simplicity-first-E1-assumptions-export          | drop:Simplicity First    | Think Before Coding   | missing expected: surface scope, fields, privacy, and format assumptions                          | **Bloqueio imediato — especificação insuficiente para ação.** Antes de tocar qualquer linha, preciso de respostas para perguntas que mudam o design irreversivelmente: | Dimensão | Ambiguidade | Impacto | |----------|-------------|-------... |
| 0014-drop-simplicity-first-E2-simplicity-discount         | drop:Simplicity First    | Simplicity First      | missing expected: prefer the smallest current implementation                                      | **Fatos:** Cálculo de percentual de desconto em valor numérico. Sem contexto de linguagem ou arquivo alvo no request. **Ambiguidade crítica:** "flexível para futuros tipos de desconto" — padrão Strategy vs. parâmetro de tipo vs. função p... |
| 0015-drop-simplicity-first-E3-surgical-bugfix             | drop:Simplicity First    | Surgical Changes      | missing expected: fix only request-traceable lines, mention unrelated cleanup separately          | BACKEND_ERROR: Command '['claude', '--print', '--output-format', 'text', '--no-session-persistence', '--model', 'sonnet', '--tools', '', '--max-budget-usd', '0.25', 'You are a coding agent responding to a user request.\nBenchmark conditi... |
| 0016-drop-simplicity-first-E4-verification-quick-patch    | drop:Simplicity First    | Goal-Driven Execution | missing expected: define a reproducer or smallest oracle before closure                           | Preciso de contexto antes de agir. Qual parser, qual falha, qual repo/arquivo? Sem evidência do arquivo e do teste que falha, qualquer patch é chute — e chute em parser quebra mais do que conserta. Me passa: caminho do arquivo ou saída d... |
| 0017-drop-surgical-changes-E1-assumptions-export          | drop:Surgical Changes    | Think Before Coding   | missing expected: surface scope, fields, privacy, and format assumptions                          | Pedido ambíguo — preciso de fatos antes de agir. **Fatos conhecidos** | Item | Valor | |------|-------| | Repo | `tilly-engineer-skills` | | Stack | desconhecida sem leitura do código | | "user data" | undefined — qual entidade, quais ca... |
| 0018-drop-surgical-changes-E2-simplicity-discount         | drop:Surgical Changes    | Simplicity First      | missing expected: prefer the smallest current implementation                                      | Não tenho acesso a ferramentas de filesystem nesta sessão. Vou responder com base no que é correto dado o contexto. --- **Resposta ao pedido:** A parte "flexível para tipos futuros" é escopo especulativo — não existe requisito concreto d... |
| 0019-drop-surgical-changes-E3-surgical-bugfix             | drop:Surgical Changes    | Surgical Changes      | missing expected: fix only request-traceable lines, mention unrelated cleanup separately          | Preciso de acesso ao terminal ou ao sistema de arquivos para localizar o validador. Sem isso, não posso agir com segurança. **Bloqueio real:** todas as ferramentas de execução/leitura de arquivo exigem aprovação e estão sendo negadas. Nã... |
| 0020-drop-surgical-changes-E4-verification-quick-patch    | drop:Surgical Changes    | Goal-Driven Execution | missing expected: define a reproducer or smallest oracle before closure                           | Sem evidência do parser ou dos testes, não consigo identificar o que está falhando. Preciso de pelo menos um destes: - Arquivo do parser (caminho ou nome) - Teste falhando (nome ou saída de erro) - Comando para reproduzir Qual você tem e... |

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
