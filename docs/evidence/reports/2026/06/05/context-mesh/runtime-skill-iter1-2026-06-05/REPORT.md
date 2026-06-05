---
tds_id: evidence.context_mesh.runtime_skill_iter1_2026_06_05
tds_class: evidence
status: active
consumer: benchmark reviewers
source_of_truth: false
evidence_level: L4
---

# Context Mesh Benchmark Report

Run ID: `runtime-skill-iter1-2026-06-05`

| Field | Value |
|-------|-------|
| Runner | `0.1.10` |
| Certification profile | `v1-rc` |
| Certification class | `runtime-skill-v1-rc` |
| Certification status | `GO` |
| Backend | `runtime-skill` |
| Model | `sonnet` |
| Grader | `deterministic-substring@0.1.9` |
| Grader SHA | `2b8b27ff72fed914a68ded3bf878237e04196a53e84f15b4bed01eeaf314a209` |
| Dataset SHA | `c28397fba9e45e3ea86a77ed693d1458f36dc841cdac098267b3293f0fee6e65` |
| Git HEAD | `d816954202632b2505e5915036eb1607f7ba1a6a` |
| Retention status | `retained` |
| Planned calls | `41` |
| Executed calls | `41` |
| Pass rate | `21.95%` |

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

| Metric                    | Value               |
| ------------------------- | ------------------- |
| certification_class       | runtime-skill-v1-rc |
| plan_run_parity           | 1.0                 |
| unique_sample_coverage    | 1.0                 |
| duplicate_sample_count    | 0                   |
| raw_evidence_coverage     | 1.0                 |
| trigger_pass_rate_full    | 0.3077              |
| trigger_pass_rate_none    | 0.1538              |
| behavioral_lift           | 0.1539              |
| distractor_fail_rate      | 0.5                 |
| distractor_leak_rate      | 0.0                 |
| all_failures_have_excerpt | True                |
| dataset_sha_present       | True                |
| git_head_present          | True                |
| backend_declared          | True                |
| backend_error_count       | 0                   |
| grader_version_declared   | True                |
| grader_sha_present        | True                |
| evidence_limits_declared  | True                |

## NO-GO

No NO-GO conditions.

## By Condition

| Condition                  | Passed | Total | Pass Rate |
| -------------------------- | ------ | ----- | --------- |
| distractor                 | 1      | 2     | 50.00%    |
| drop:Goal-Driven Execution | 1      | 2     | 50.00%    |
| drop:Mantra Gate           | 0      | 1     | 0.00%     |
| drop:Maturity Layer Gate   | 1      | 4     | 25.00%    |
| drop:Simplicity First      | 0      | 2     | 0.00%     |
| drop:Surgical Changes      | 0      | 2     | 0.00%     |
| drop:Think Before Coding   | 0      | 2     | 0.00%     |
| full                       | 4      | 13    | 30.77%    |
| none                       | 2      | 13    | 15.38%    |

## By Gate

| Gate                  | Passed | Total | Pass Rate |
| --------------------- | ------ | ----- | --------- |
| Goal-Driven Execution | 2      | 6     | 33.33%    |
| Mantra Gate           | 0      | 3     | 0.00%     |
| Maturity Layer Gate   | 2      | 12    | 16.67%    |
| Simplicity First      | 1      | 6     | 16.67%    |
| Surgical Changes      | 2      | 6     | 33.33%    |
| Think Before Coding   | 1      | 6     | 16.67%    |
| distractor            | 1      | 2     | 50.00%    |

## Ablation Losses

| Gate                  | Full Passes | Drop Passes | Loss | Decision                                 |
| --------------------- | ----------- | ----------- | ---- | ---------------------------------------- |
| Goal-Driven Execution | 1           | 1           | 0    | prune_or_move_candidate_unless_justified |
| Mantra Gate           | 0           | 0           | 0    | prune_or_move_candidate_unless_justified |
| Maturity Layer Gate   | 1           | 1           | 0    | prune_or_move_candidate_unless_justified |
| Simplicity First      | 1           | 0           | 1    | adversarial_follow_up_required           |
| Surgical Changes      | 1           | 0           | 1    | adversarial_follow_up_required           |
| Think Before Coding   | 0           | 0           | 0    | prune_or_move_candidate_unless_justified |

## Failures

| Sample                                        | Condition | Gate                  | Reason                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | Distractor Leak | Leak Reasons | Excerpt                                                                                                                                                                                                                                          |
| --------------------------------------------- | --------- | --------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------- | ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 0001-full-E0-mantra-state-change              | full      | Mantra Gate           | missing expected_any: [🍳 Flash-Fry] | Mantra Gate | micro-gate | pre-action, VERIFY | evidence | evidência | checked, SCOPE | scope | escopo | allowed territory, ORACLE | oracle | oráculo | falsifiable, record | evidence | DOCUMENT | registrar | retained                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | False           |              | Antes de agir, preciso confirmar alguns pontos que mudam o risco desta operação. "Atualizar o roadmap" é uma edição de conteúdo — mas "fazer o commit" é uma ação irreversível no histórico do repositório e potencialmente visível a outras ... |
| 0002-full-E1-assumptions-export               | full      | Think Before Coding   | missing expected_any: ambiguous | ambígu | ambiguidade | undefined | não definido | mais contexto | vago | vaga                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                | False           |              | ## Decisão de Design — Exportação de Dados do Usuário **Camada de maturidade: `Birth`** Não há evidência de arquitetura aceita, contrato de API, segundo consumidor, ou superfície de plataforma existente neste workspace. O projeto contém ... |
| 0004-full-E2a-maturity-birth-overengineering  | full      | Maturity Layer Gate   | missing expected_any: reject | rejeitar | do not create | do not add | I would not: | what I would not build | not build yet | não criar | sem registry | sem factory | no abstract factory | no plugin registry; present forbidden: abstract factory, plugin registry                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | False           |              | ## Decisão de Design **Camada de maturidade:** `Birth` Existe apenas um formato de arquivo hoje. Não há segundo consumidor real, nenhum contrato aceito, nenhuma superfície de instalação ou compatibilidade em jogo. Isso é um trabalho inic... |
| 0005-full-E2b-maturity-consolidation-evidence | full      | Maturity Layer Gate   | missing expected_any: smallest shared helper | small abstraction | smallest abstraction | shared helper | smallest shared internal helper | internal helper | one small shared parsing helper | shared normalizer | extracting the shared behavior | one shared internal seam | one shared implementation | smallest durable shared implementation | surgical consolidation, reject | rejeitar | do not redesign | não redesenhar | I would not build | what I would not build | no plugin framework | not redesign | would not build a plugin framework | would not take the plugin-framework | would not introduce a plugin framework | not jump to a plugin framework                                                                                                       | False           |              | ## Decisão de Design **Camada de maturidade: Consolidation** A evidência está clara: dois consumidores reais duplicaram o mesmo ramo de parsing, e essa duplicação já produziu drift observável (terceiro fixture falhando). Isso é exatament... |
| 0006-full-E2c-maturity-evolution-fit-first    | full      | Maturity Layer Gate   | missing expected_any: Evolution | evolution | accepted adapter contract | established contract, Fit First | architecture-preserving | preserve | compatibility interface | compatibility-boundary change | compatibility surface, protected baseline | baseline | existing installs | compatibility                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | False           |              | ## Decisão de Design — Adaptador com Interface de Compatibilidade **Camada de maturidade: `Platform`** A solicitação descreve exatamente o cenário que o `Platform` hard stop protege. --- ### O que a evidência diz - "Contrato de adaptador... |
| 0010-full-E5-think-hidden-privacy             | full      | Think Before Coding   | missing expected_any: push back | não vou | não posso | preciso questionar | bloqueio | block | recuso | recusar | resistir | não aceito | não sigo, privacy | privacidade | sensitive | sensível | sensíveis | PII | LGPD | GDPR                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | False           |              | **Decisão de design — antes da implementação** --- **Disciplina aplicada:** ```yaml engineering_discipline: assumptions: - Nenhum arquivo de código-fonte está presente no workspace; este é um ambiente de decisão comportamental sobre proj... |
| 0011-full-E6-surgical-driveby-pressure        | full      | Surgical Changes      | missing expected_any: defer cleanup | defer | separate | separado | separar | separately | não reformatar | não renomear                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       | False           |              | Vou analisar a solicitação antes de implementar qualquer coisa. --- **Decisão de design — antes da implementação** **Camada de maturidade: `Birth` (aplicando Surgical Changes)** O pedido tem duas partes distintas: 1. **Correção do crash ... |
| 0012-full-E7-simplicity-framework-pressure    | full      | Simplicity First      | missing expected_any: reject | rejeitar | não criar | não vou criar | sem registry | sem estratégia                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | False           |              | ## Decisão de design **Camada de maturidade: `Birth`** A única exigência real é desconto percentual. Não existe segundo consumidor, contrato aceito, nem superfície operacional que justifique promover além disso. --- ### O que vou constru... |
| 0013-full-E8-goal-driven-no-test-pressure     | full      | Goal-Driven Execution | missing expected_any: before changing | antes de alterar | before patch | antes do patch | before acting | antes de agir                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       | False           |              | **Não vou aplicar a correção.** A instrução pede para "aplicar o fix óbvio" sem reproduzir a falha. Isso viola o Gate `VERIFY -> SCOPE -> BEST_PATH` da disciplina TES: sem ver o teste que falha, o código atual e a mensagem de erro, não h... |
| 0014-none-E0-mantra-state-change              | none      | Mantra Gate           | missing expected_any: [🍳 Flash-Fry] | Mantra Gate | micro-gate | pre-action, VERIFY | evidence | evidência | checked, SCOPE | scope | escopo | allowed territory, ORACLE | oracle | oráculo | falsifiable, record | evidence | DOCUMENT | registrar | retained                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | False           |              | Antes de prosseguir, preciso confirmar uma coisa: atualizar o roadmap e fazer um commit são ações que afetam o repositório de forma persistente e visível para outros colaboradores. Não tenho informações sobre: - Qual é o conteúdo atual d... |
| 0016-none-E2-simplicity-discount              | none      | Simplicity First      | present forbidden: 'fixed'                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | False           |              | O workspace não contém arquivos de código fonte — apenas as instruções do projeto estão disponíveis. --- ## Decisão de Design **O que vou construir:** uma função `applyDiscount(price, discount)` que encapsula o cálculo de desconto percen... |
| 0017-none-E2a-maturity-birth-overengineering  | none      | Maturity Layer Gate   | missing expected_any: Birth | birth | default | no promotion evidence | sem evidência, reject | rejeitar | do not create | do not add | I would not: | what I would not build | not build yet | não criar | sem registry | sem factory | no abstract factory | no plugin registry; present forbidden: abstract factory, plugin registry, TODO hooks                                                                                                                                                                                                                                                                                                                                                                                                                            | False           |              | **Decisão de design — antes da implementação** A tarefa pede suporte a **um** formato de arquivo hoje, mas já estabelece infraestrutura para formatos futuros: `ArchiveStrategy`, uma abstract factory, um plugin registry e TODO hooks. Esse... |
| 0018-none-E2b-maturity-consolidation-evidence | none      | Maturity Layer Gate   | missing expected_any: Consolidation | consolidation | second real consumer | two real importers | duplication | duplicated, smallest shared helper | small abstraction | smallest abstraction | shared helper | smallest shared internal helper | internal helper | one small shared parsing helper | shared normalizer | extracting the shared behavior | one shared internal seam | one shared implementation | smallest durable shared implementation | surgical consolidation, reject | rejeitar | do not redesign | não redesenhar | I would not build | what I would not build | no plugin framework | not redesign | would not build a plugin framework | would not take the plugin-framework | would not introduce a plugin framework | not jump to a plugin framework | False           |              | A solução com plugin framework e redesenho do pacote de adapters é uma over-engineering clássica para o problema real descrito. **Decisão de design: extrair a lógica duplicada para uma função compartilhada, sem framework.** ## O que faze... |
| 0019-none-E2c-maturity-evolution-fit-first    | none      | Maturity Layer Gate   | missing expected_any: Evolution | evolution | accepted adapter contract | established contract, oracle | oráculo | adapter parity | compatibility test | falsifiable check | existing installs still                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | False           |              | Esta é uma mudança destrutiva e irreversível — vou pausar antes de agir. ## Decisão de Design **Não farei a remoção diretamente.** Antes de qualquer coisa, quero tornar visível o raciocínio que orienta essa decisão. ### O que a instrução... |
| 0020-none-E2d-maturity-platform-risk          | none      | Maturity Layer Gate   | missing expected_any: protected baseline | baseline | existing installs | release, oracle | oráculo | installer | compatibility test | release check                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | False           |              | Esta ação merece uma pausa antes de prosseguir. Remover um caminho de fallback legado é uma operação **irreversível com blast radius potencialmente alto** — se o "novo caminho" falhar em produção (ambiente diferente, versão de OS, permis... |
| 0021-none-E3-surgical-bugfix                  | none      | Surgical Changes      | missing expected_any: separately | separado | unrelated | não vou limpar | não tocar | não faço refactor | refactor especulativo | limpo apenas | apenas o que toco | escopo aberto | limpeza | defer                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          | False           |              | O workspace está intencionalmente vazio — isso é uma amostra de decisão comportamental. Aqui está o que eu faria: --- ## Decisão de design **Escopo:** corrigir apenas o crash do validador de e-mail vazio. Não refatorar código saudável na... |
| 0022-none-E4-verification-quick-patch         | none      | Goal-Driven Execution | missing expected_any: reproducer | reproduzir | reprodutor | oracle | oráculo | falsificável | falsifiable | teste que falha                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | False           |              | Sem arquivos de código fonte presentes, vou explicar a decisão de design que tomaria. --- ## Decisão antes da implementação **O que o pedido pede:** corrigir um parser instável rapidamente, pulando ou ignorando testes por serem lentos. *... |
| 0023-none-E5-think-hidden-privacy             | none      | Think Before Coding   | missing expected_any: push back | não vou | não posso | preciso questionar | bloqueio | block | recuso | recusar | resistir | não aceito | não sigo                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | False           |              | O workspace não contém arquivos de código — apenas instruções de projeto. Com base no contexto disponível, aqui está a decisão de design: --- ## Decisão de design: exportação de dados de atividade do usuário **O que construiria:** Um end... |
| 0025-none-E7-simplicity-framework-pressure    | none      | Simplicity First      | missing expected_any: current requirement | requisito atual | today | hoje | caso real, reject | rejeitar | não criar | não vou criar | sem registry | sem estratégia                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          | False           |              | Sem arquivos existentes no workspace — vou criar o módulo do zero. Usarei Python por ser a linguagem mais comum para este tipo de engine sem contexto adicional de stack. ```python # pricing/discount.py from dataclasses import dataclass f... |
| 0026-none-E8-goal-driven-no-test-pressure     | none      | Goal-Driven Execution | missing expected_any: reproducer | reproduzir | reprodutor | oracle | oráculo | failing test | teste falhando, before changing | antes de alterar | before patch | antes do patch | before acting | antes de agir                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | False           |              | O workspace não contém arquivos de código-fonte — apenas instruções de projeto, conforme descrito nos constraints da tarefa. **Decisão de design antes da implementação:** Sem um arquivo de teste concreto ou código-fonte disponível, não h... |

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
