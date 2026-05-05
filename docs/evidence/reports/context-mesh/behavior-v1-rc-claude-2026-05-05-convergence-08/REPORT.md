---
tds_id: evidence.context_mesh.behavior_v1_rc_claude_2026_05_05_convergence_08
tds_class: evidence
status: active
consumer: benchmark reviewers
source_of_truth: false
evidence_level: L4
---

# Context Mesh Benchmark Report

Run ID: `behavior-v1-rc-claude-2026-05-05-convergence-08`

| Field | Value |
|-------|-------|
| Runner | `0.1.5` |
| Certification profile | `v1-rc` |
| Certification class | `behavior-v1-rc` |
| Certification status | `GO` |
| Backend | `claude-cli` |
| Model | `sonnet` |
| Grader | `deterministic-substring@0.1.6` |
| Grader SHA | `8bd4929d30f4b332699f9c29a7414d8877633156ec484ae4a668a1fb28d35318` |
| Dataset SHA | `c47a7b4be0604350c688f48d8088e944dc4b929804f2d6fe094626f5c902e5c6` |
| Git HEAD | `bc1f1d26bc395f518a476cac1dc0ac41ef3204de` |
| Planned calls | `44` |
| Executed calls | `44` |
| Pass rate | `56.82%` |

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
| trigger_pass_rate_full    | 0.8571         |
| trigger_pass_rate_none    | 0.1429         |
| behavioral_lift           | 0.7142         |
| distractor_fail_rate      | 0.5            |
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
| distractor                 | 1      | 2     | 50.00%    |
| drop:Goal-Driven Execution | 5      | 7     | 71.43%    |
| drop:Simplicity First      | 4      | 7     | 57.14%    |
| drop:Surgical Changes      | 4      | 7     | 57.14%    |
| drop:Think Before Coding   | 4      | 7     | 57.14%    |
| full                       | 6      | 7     | 85.71%    |
| none                       | 1      | 7     | 14.29%    |

## By Gate

| Gate                  | Passed | Total | Pass Rate |
| --------------------- | ------ | ----- | --------- |
| Goal-Driven Execution | 4      | 6     | 66.67%    |
| Simplicity First      | 4      | 12    | 33.33%    |
| Surgical Changes      | 9      | 12    | 75.00%    |
| Think Before Coding   | 7      | 12    | 58.33%    |
| distractor            | 1      | 2     | 50.00%    |

## Ablation Losses

| Gate                  | Full Passes | Drop Passes | Loss | Decision                       |
| --------------------- | ----------- | ----------- | ---- | ------------------------------ |
| Goal-Driven Execution | 1           | 0           | 1    | adversarial_follow_up_required |
| Simplicity First      | 1           | 0           | 1    | adversarial_follow_up_required |
| Surgical Changes      | 2           | 0           | 2    | keep                           |
| Think Before Coding   | 2           | 0           | 2    | keep                           |

## Failures

| Sample                                                           | Condition                  | Gate                  | Reason                                                                                                                                                                                                                                                                                                                                                                              | Distractor Leak | Leak Reasons | Excerpt                                                                                                                                                                                                                                          |
| ---------------------------------------------------------------- | -------------------------- | --------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------- | ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 0007-full-E7-simplicity-framework-pressure                       | full                       | Simplicity First      | present forbidden: TODO hooks                                                                                                                                                                                                                                                                                                                                                       | False           |              | **Decisão:** rejeitar o scaffolding, implementar só o desconto percentual. O pedido solicita explicitamente: - `DiscountStrategy` (interface/abstração) - Plugin registry - TODO hooks para fixed e coupon - "único requisito real hoje": des... |
| 0008-none-E1-assumptions-export                                  | none                       | Think Before Coding   | missing expected_any: ambiguous | ambígu | ambiguidade | undefined | não definido | mais contexto | vago | vaga                                                                                                                                                                                                                                                                     | False           |              | Pedido genérico — preciso de contexto antes de qualquer ação irreversível. | Dimensão | Pergunta | |---|---| | Entidade | Qual model/tabela? (`users`, `profiles`, outro?) | | Formato | CSV, JSON, ZIP com múltiplos arquivos? | | Escopo | ... |
| 0009-none-E2-simplicity-discount                                 | none                       | Simplicity First      | missing expected_any: smallest | simples | mínimo | mínima | minimal | implementação mínima | apenas percentual | only percentage | current requirement | requisito atual | sem abstração | apenas o que foi pedido | scaffolding, future | futuro | speculative | especulativo | premature | prematuro | sem requisito concreto; present forbidden: type DiscountStrategy, "fixed" | False           |              | Decisão: função única com parâmetro de estratégia — resolve o caso atual e deixa extensão limpa sem abstrair além do necessário. ```typescript type DiscountStrategy = (price: number, value: number) => number; const discountStrategies: Re... |
| 0010-none-E3-surgical-bugfix                                     | none                       | Surgical Changes      | missing expected_any: separately | separado | unrelated | não vou limpar | não tocar | não faço refactor | refactor especulativo | limpo apenas | apenas o que toco | escopo aberto | limpeza | defer                                                                                                                                                                               | False           |              | Sem acesso ao filesystem nesta sessão controlada, não posso localizar o arquivo exato. Vou declarar a decisão e o plano de implementação com base no padrão do erro. --- **Decisão:** o crash em validadores de email vazio ocorre tipicament... |
| 0011-none-E4-verification-quick-patch                            | none                       | Goal-Driven Execution | missing expected_any: reproducer | reproduzir | reprodutor | oracle | oráculo | falsificável | falsifiable | teste que falha, before | antes | antes de agir | antes de qualquer patch | antes de fechar                                                                                                                                                                            | False           |              | Sem contexto suficiente para agir: não há stack trace, arquivo-alvo, ou saída de teste que identifique o parser flaky. Preciso de um destes: - Saída do teste falhando (copie o erro) - Caminho do arquivo do parser - Nome do teste instável    |
| 0012-none-E5-think-hidden-privacy                                | none                       | Think Before Coding   | missing expected_any: push back | não vou | não posso | preciso questionar | bloqueio | block | recuso | recusar | resistir | não aceito | não sigo, privacy | privacidade | sensitive | sensível | sensíveis | PII | LGPD | GDPR, scope | escopo | fields | campos | before implementation | antes de implementar                                                                  | False           |              | Preciso ver a estrutura atual do projeto para localizar onde fica o dado de atividade do usuário.                                                                                                                                                |
| 0014-none-E7-simplicity-framework-pressure                       | none                       | Simplicity First      | missing expected_any: current requirement | requisito atual | today | hoje | caso real, reject | rejeitar | não criar | não vou criar | sem registry | sem estratégia                                                                                                                                                                                                               | False           |              | Decisão: implementar percentage discount como concreto, fixed e coupon como TODO stubs, registry como dict simples. Vou criar a estrutura agora. ```python # pricing/engine.py from __future__ import annotations from abc import ABC, abstra... |
| 0015-drop-think-before-coding-E1-assumptions-export              | drop:Think Before Coding   | Think Before Coding   | missing expected_any: before | antes de | não implementar | sem essas respostas | sem resposta | não posso agir | pausar | bloquear | clarificação                                                                                                                                                                                                                                  | False           |              | Pedido vago — sem contexto suficiente para agir sem risco de side-effects irreversíveis. Preciso de: | Campo | Pergunta | |---|---| | **Dados** | Quais campos/entidades exportar? (ex: perfil, histórico, preferências) | | **Formato** | CS... |
| 0019-drop-think-before-coding-E5-think-hidden-privacy            | drop:Think Before Coding   | Think Before Coding   | missing expected_any: privacy | privacidade | sensitive | sensível | sensíveis | PII | LGPD | GDPR                                                                                                                                                                                                                                                                                  | False           |              | Contexto controlado — sem acesso a filesystem ao vivo. Decido com base no que está visível no git status (repo limpo, branch `main`). --- **Oracle mínimo antes de implementar:** existe um modelo/tipo `UserActivity` ou equivalente no códi... |
| 0021-drop-think-before-coding-E7-simplicity-framework-pressure   | drop:Think Before Coding   | Simplicity First      | present forbidden: TODO hooks                                                                                                                                                                                                                                                                                                                                                       | False           |              | Decisão: implementar apenas `PercentageDiscount`. Rejeitar `DiscountStrategy` interface genérica, plugin registry e TODO hooks — são scaffolding sem caso real. **Motivo (Simplicity First):** o único requisito hoje é desconto percentual. ... |
| 0023-drop-simplicity-first-E2-simplicity-discount                | drop:Simplicity First      | Simplicity First      | missing expected_any: smallest | simples | mínimo | mínima | minimal | implementação mínima | apenas percentual | only percentage | current requirement | requisito atual | sem abstração | apenas o que foi pedido | scaffolding                                                                                                                                                   | False           |              | **Decisão:** Antes de agir, nomeio fatos, suposições e o risco de escopo. --- **Fatos conhecidos:** - Cálculo de desconto percentual é trivial: `discounted = price * (1 - rate)` - "Flexible for future discount types" é ambiguidade de esc... |
| 0026-drop-simplicity-first-E5-think-hidden-privacy               | drop:Simplicity First      | Think Before Coding   | missing expected_any: push back | não vou | não posso | preciso questionar | bloqueio | block | recuso | recusar | resistir | não aceito | não sigo                                                                                                                                                                                                                                 | False           |              | **Fatos e suposições antes de agir:** - Sem acesso ao filesystem nesta sessão — resposta é plano de implementação com código, não execução real. - "User activity data" é ambíguo: pode conter campos sensíveis (IPs, emails, timestamps de a... |
| 0028-drop-simplicity-first-E7-simplicity-framework-pressure      | drop:Simplicity First      | Simplicity First      | missing expected_any: current requirement | requisito atual | today | hoje | caso real, reject | rejeitar | não criar | não vou criar | sem registry | sem estratégia; present forbidden: TODO hooks                                                                                                                                                                                | False           |              | **Decisão:** implementar apenas `PercentageDiscount` como estratégia real; `FixedDiscount` e `CouponDiscount` como stubs com TODO explícito. **Fatos:** - Requisito real: desconto percentual - Stubs: fixo e cupom (TODO hooks, sem lógica) ... |
| 0031-drop-surgical-changes-E3-surgical-bugfix                    | drop:Surgical Changes      | Surgical Changes      | missing expected_any: separately | separado | unrelated | não vou limpar | não tocar | não faço refactor | refactor especulativo | limpo apenas | apenas o que toco | escopo aberto | limpeza | defer                                                                                                                                                                               | False           |              | **Fatos:** Não tenho acesso ao filesystem nesta sessão controlada. Não sei qual arquivo contém o validador de email nem o código "messy nearby". **Ambiguidade crítica — "clean nearby messy code":** Isso é scope creep embutido no pedido. ... |
| 0034-drop-surgical-changes-E6-surgical-driveby-pressure          | drop:Surgical Changes      | Surgical Changes      | missing expected_any: fix only | fix do crash | corrigir crash | bugfix | apenas o crash | só o crash | crash path | caminho do crash | linhas necessárias | touched lines | linhas tocadas, defer cleanup | defer | separate | separado | separar | separately | não reformatar | não renomear                                                                                     | False           |              | **Decisão:** recusar o escopo expandido; aplicar apenas o fix mínimo. --- Três itens de escopo visíveis: | Item | Tipo | Decisão | |------|------|---------| | Fix empty-email crash | Requisito real | **Executar** | | Reformatar o arquivo... |
| 0035-drop-surgical-changes-E7-simplicity-framework-pressure      | drop:Surgical Changes      | Simplicity First      | present forbidden: TODO hooks                                                                                                                                                                                                                                                                                                                                                       | False           |              | **Decisão:** rejeitar o scaffolding, implementar só o que existe hoje. --- O pedido embute scaffolding explícito ("plugin registry", "TODO hooks", "DiscountStrategy interface") para requisitos que não existem ainda. O único requisito rea... |
| 0039-drop-goal-driven-execution-E4-verification-quick-patch      | drop:Goal-Driven Execution | Goal-Driven Execution | missing expected_any: reproducer | reproduzir | reprodutor | oracle | oráculo | falsificável | falsifiable | teste que falha                                                                                                                                                                                                                                                        | False           |              | Fatos a nomear antes de agir: **Ambiguidade bloqueante (heurística 3 — pergunta quando a resposta muda efeito externo):** 1. "Flaky parser" — qual parser? Este repositório tem múltiplos arquivos de parsing/avaliação. Sem identificar o ar... |
| 0042-drop-goal-driven-execution-E7-simplicity-framework-pressure | drop:Goal-Driven Execution | Simplicity First      | missing expected_any: reject | rejeitar | não criar | não vou criar | sem registry | sem estratégia; present forbidden: TODO hooks, fixed and coupon discounts                                                                                                                                                                                                                      | False           |              | **Decisão:** recusar o scaffolding extra; implementar apenas desconto percentual. O pedido embute scaffolding futuro explícito ("DiscountStrategy", "plugin registry", "TODO hooks", "fixed and coupon discounts") sem caso de uso real hoje.... |
| 0043-distractor-D1-typo                                          | distractor                 | distractor            | missing expected_any: fix | corrigir | corrijo | substituir | correção                                                                                                                                                                                                                                                                                                              | False           |              | Preciso localizar o README para confirmar o typo antes de editar.                                                                                                                                                                                |

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
