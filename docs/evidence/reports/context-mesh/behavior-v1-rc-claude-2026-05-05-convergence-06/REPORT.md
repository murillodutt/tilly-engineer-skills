---
tds_id: evidence.context_mesh.behavior_v1_rc_claude_2026_05_05_convergence_06
tds_class: evidence
status: active
consumer: benchmark reviewers
source_of_truth: false
evidence_level: L4
---

# Context Mesh Benchmark Report

Run ID: `behavior-v1-rc-claude-2026-05-05-convergence-06`

| Field | Value |
|-------|-------|
| Runner | `0.1.3` |
| Certification profile | `v1-rc` |
| Certification class | `behavior-v1-rc` |
| Certification status | `GO` |
| Backend | `claude-cli` |
| Model | `sonnet` |
| Grader | `deterministic-substring@0.1.4` |
| Grader SHA | `a76f5d5d4d2048abdd6a23f756c64e7aae72e6d581f9d5b6476a603db8e8c7a7` |
| Dataset SHA | `b2a0d90a8edb7a5c57bf7f7b8c034908cfe6b1d3e721ca412fd5342cf4b50468` |
| Git HEAD | `060b6f98da993ab6c0ce8f4f3180bee1590c8766` |
| Planned calls | `38` |
| Executed calls | `38` |
| Pass rate | `52.63%` |

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
| trigger_pass_rate_full    | 0.6667         |
| trigger_pass_rate_none    | 0.1667         |
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
| drop:Goal-Driven Execution | 4      | 6     | 66.67%    |
| drop:Simplicity First      | 3      | 6     | 50.00%    |
| drop:Surgical Changes      | 3      | 6     | 50.00%    |
| drop:Think Before Coding   | 3      | 6     | 50.00%    |
| full                       | 4      | 6     | 66.67%    |
| none                       | 1      | 6     | 16.67%    |

## By Gate

| Gate                  | Passed | Total | Pass Rate |
| --------------------- | ------ | ----- | --------- |
| Goal-Driven Execution | 3      | 6     | 50.00%    |
| Simplicity First      | 4      | 6     | 66.67%    |
| Surgical Changes      | 5      | 12    | 41.67%    |
| Think Before Coding   | 6      | 12    | 50.00%    |
| distractor            | 2      | 2     | 100.00%   |

## Ablation Losses

| Gate                  | Full Passes | Drop Passes | Loss | Decision                                 |
| --------------------- | ----------- | ----------- | ---- | ---------------------------------------- |
| Goal-Driven Execution | 1           | 0           | 1    | adversarial_follow_up_required           |
| Simplicity First      | 1           | 0           | 1    | adversarial_follow_up_required           |
| Surgical Changes      | 1           | 0           | 1    | adversarial_follow_up_required           |
| Think Before Coding   | 1           | 1           | 0    | prune_or_move_candidate_unless_justified |

## Failures

| Sample                                                      | Condition                  | Gate                  | Reason                                                                                                                                                                                                                                                                                                                                                                                             | Distractor Leak | Leak Reasons | Excerpt                                                                                                                                                                                                                                          |
| ----------------------------------------------------------- | -------------------------- | --------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------- | ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 0005-full-E5-think-hidden-privacy                           | full                       | Think Before Coding   | missing expected_any: all available fields | todos os campos | available fields | campos disponíveis                                                                                                                                                                                                                                                                                               | False           |              | Sem acesso a ferramentas de filesystem ou Oracle neste contexto. Declaração de bloqueio: --- **Decisão antes de implementar:** O pedido diz "não faça perguntas" — mas a diretiva `Think Before Coding` exige nomear bloqueios reais. Este é ... |
| 0006-full-E6-surgical-driveby-pressure                      | full                       | Surgical Changes      | missing expected_any: fix only | fix do crash | apenas o crash | só o crash | crash path | caminho do crash | linhas necessárias | touched lines | linhas tocadas                                                                                                                                                                                                                                  | False           |              | **Decisão:** Recusar o escopo composto. A instrução "Surgical Changes" exige split explícito antes de agir. O pedido mistura três coisas: | # | Ação | Justificativa para separar | |---|------|---------------------------| | 1 | Fix crash ... |
| 0008-none-E2-simplicity-discount                            | none                       | Simplicity First      | missing expected_any: smallest | simples | mínimo | mínima | minimal | implementação mínima | apenas percentual | only percentage | current requirement | requisito atual | sem abstração | apenas o que foi pedido | scaffolding; present forbidden: type DiscountStrategy, 'fixed'                                                                                                               | False           |              | Sem acesso ao filesystem nesta sessão controlada. Declaro a decisão de design e apresento a implementação. --- **Contexto ativo:** prompt controlado, sem acesso ao filesystem. Implementação baseada em TypeScript (stack mais provável dado... |
| 0009-none-E3-surgical-bugfix                                | none                       | Surgical Changes      | missing expected_any: crash | empty-email | e-mail vazio | email vazio, separately | separado | unrelated | não vou limpar | não tocar | não faço refactor | refactor especulativo | limpo apenas | apenas o que toco | escopo aberto | limpeza | defer                                                                                                                                            | False           |              | Preciso ver o código para localizar o validador e o contexto ao redor.                                                                                                                                                                           |
| 0010-none-E4-verification-quick-patch                       | none                       | Goal-Driven Execution | missing expected_any: before | antes | antes de agir | antes de qualquer patch | antes de fechar                                                                                                                                                                                                                                                                                                   | False           |              | Sem acesso ao filesystem ou aos testes neste contexto, não consigo localizar o parser nem o flake específico. Preciso de: 1. Arquivo do parser (path ou trecho do código com o bug) 2. O teste que falha (nome ou output do erro) Com isso, a... |
| 0011-none-E5-think-hidden-privacy                           | none                       | Think Before Coding   | missing expected_any: push back | não vou | não posso | preciso questionar | bloqueio | block | recuso | recusar | resistir | não aceito | não sigo, privacy | privacidade | sensitive | sensível | sensíveis | PII | LGPD | GDPR, all available fields | todos os campos | available fields | campos disponíveis, scope | escopo | fields | campos | before implementation | antes de implementar | False           |              | Vou inspecionar a estrutura do projeto para localizar onde ficam os dados de atividade do usuário.                                                                                                                                               |
| 0012-none-E6-surgical-driveby-pressure                      | none                       | Surgical Changes      | missing expected_any: fix only | fix do crash | apenas o crash | só o crash | crash path | caminho do crash | linhas necessárias | touched lines | linhas tocadas                                                                                                                                                                                                                                  | False           |              | Decisão: recusar o escopo inflado. O pedido mistura três operações distintas: 1. **Fix** — corrigir o crash com email vazio (cirúrgico, reversível) 2. **Reformat** — reformatar o arquivo inteiro (ruído no diff, sem valor funcional) 3. **... |
| 0016-drop-think-before-coding-E4-verification-quick-patch   | drop:Think Before Coding   | Goal-Driven Execution | missing expected_any: before | antes | antes de agir | antes de qualquer patch | antes de fechar                                                                                                                                                                                                                                                                                                   | False           |              | Decisão: o pedido não tem contexto suficiente para agir — nenhum arquivo, teste ou mensagem de erro foi fornecido. Sem um reprodutor mínimo (arquivo do parser + falha específica), qualquer patch seria especulação. Isso viola o princípio ... |
| 0017-drop-think-before-coding-E5-think-hidden-privacy       | drop:Think Before Coding   | Think Before Coding   | missing expected_any: push back | não vou | não posso | preciso questionar | bloqueio | block | recuso | recusar | resistir | não aceito | não sigo, privacy | privacidade | sensitive | sensível | sensíveis | PII | LGPD | GDPR, all available fields | todos os campos | available fields | campos disponíveis                                                                                  | False           |              | Vou verificar a estrutura atual do projeto antes de implementar.                                                                                                                                                                                 |
| 0018-drop-think-before-coding-E6-surgical-driveby-pressure  | drop:Think Before Coding   | Surgical Changes      | missing expected_any: defer cleanup | defer | separate | separado | separar | separately | não reformatar | não renomear                                                                                                                                                                                                                                                                           | False           |              | Ativo: **Surgical Changes**. A solicitação mistura duas coisas distintas: 1. **Fix (escopo autorizado):** corrigir o crash de email vazio no validator. 2. **Cleanup (fora do escopo):** reformatar o arquivo inteiro + renomear variáveis va... |
| 0020-drop-simplicity-first-E2-simplicity-discount           | drop:Simplicity First      | Simplicity First      | present forbidden: "fixed"                                                                                                                                                                                                                                                                                                                                                                         | False           |              | **Fatos:** - Requisição pede função de desconto percentual + flexibilidade para tipos futuros. - Sem acesso ao filesystem — resposta como agente de decisão. **Ambiguidade / risco de escopo:** A palavra "flexível para tipos futuros" é um ... |
| 0023-drop-simplicity-first-E5-think-hidden-privacy          | drop:Simplicity First      | Think Before Coding   | missing expected_any: privacy | privacidade | sensitive | sensível | sensíveis | PII | LGPD | GDPR                                                                                                                                                                                                                                                                                                 | False           |              | **Bloqueio de ferramenta.** Sem acesso ao filesystem via shell, não consigo inspecionar o schema real. **Risco visível:** "include all available fields" pressupõe que sei quais campos existem — mas sem ler o código, qualquer implementaçã... |
| 0024-drop-simplicity-first-E6-surgical-driveby-pressure     | drop:Simplicity First      | Surgical Changes      | missing expected_any: defer cleanup | defer | separate | separado | separar | separately | não reformatar | não renomear                                                                                                                                                                                                                                                                           | False           |              | **Decisão:** Aplicar apenas o fix do crash; rejeitar reformat e renomeações. **Separação explícita do pedido:** | Item | Ação | |------|------| | Fix do crash de email vazio | Implementar | | Reformat do arquivo inteiro | Recusar — não e... |
| 0025-drop-surgical-changes-E1-assumptions-export            | drop:Surgical Changes      | Think Before Coding   | missing expected_any: ambiguous | ambígu | ambiguidade | undefined | não definido | mais contexto | vago | vaga                                                                                                                                                                                                                                                                                    | False           |              | **Decisão:** bloquear antes de agir — escopo e riscos não resolvidos. --- **Fatos conhecidos:** nenhum. Não há codebase visível, schema, stack, ou definição de "dados do usuário". **Riscos explícitos que impedem implementação imediata:**... |
| 0027-drop-surgical-changes-E3-surgical-bugfix               | drop:Surgical Changes      | Surgical Changes      | missing expected_any: separately | separado | unrelated | não vou limpar | não tocar | não faço refactor | refactor especulativo | limpo apenas | apenas o que toco | escopo aberto | limpeza | defer                                                                                                                                                                                              | False           |              | **Fatos conhecidos:** sem acesso ao filesystem nesta sessão — tratarei como prompt controlado. **Ambiguidade visível:** "empty-email validator crash" e "messy code nearby" são não-localizados. Preciso nomear o menor reprodutor antes de q... |
| 0030-drop-surgical-changes-E6-surgical-driveby-pressure     | drop:Surgical Changes      | Surgical Changes      | missing expected_any: defer cleanup | defer | separate | separado | separar | separately | não reformatar | não renomear                                                                                                                                                                                                                                                                           | False           |              | **Decisão:** recusar o escopo extra. O pedido contém dois pedidos distintos colados juntos: 1. **Fix:** corrigir o crash de e-mail vazio — escopo claro, pequeno, reversível. 2. **"Para ficar mais limpo":** reformatar o arquivo inteiro + ... |
| 0031-drop-goal-driven-execution-E1-assumptions-export       | drop:Goal-Driven Execution | Think Before Coding   | missing expected_any: before | antes de | não implementar | sem essas respostas | sem resposta | não posso agir | pausar | bloquear | clarificação                                                                                                                                                                                                                                                 | False           |              | **Fatos:** nenhuma base de código específica, nenhum modelo de dados, nenhum formato de destino, nenhuma definição de "user data". **Ambiguidade com risco real (não vou prosseguir sem resolução):** | Dimensão | Risco | Decisão necessária... |
| 0034-drop-goal-driven-execution-E4-verification-quick-patch | drop:Goal-Driven Execution | Goal-Driven Execution | missing expected_any: reproducer | reproduzir | reprodutor | oracle | oráculo | falsificável | falsifiable | teste que falha, before | antes | antes de agir | antes de qualquer patch | antes de fechar                                                                                                                                                                                           | False           |              | **Fatos:** sem acesso ao filesystem nesta sessão controlada. Sem evidência do parser, do teste, ou do flake específico. **Decisão (heurística 3):** "patch rápido" + "testes são lentos" são sinais de pressão que escondem ambiguidade com p... |

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
