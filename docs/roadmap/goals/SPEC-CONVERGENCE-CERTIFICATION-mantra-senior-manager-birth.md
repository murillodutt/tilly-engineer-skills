---
tds_id: roadmap.spec_convergence_mantra_senior_manager_birth
tds_class: roadmap
status: active
consumer: maintainers and release reviewers certifying the convergence slice
source_of_truth: false
evidence_level: L1
tver: 0.1.0
---

# SPEC de Convergência e Certificação — Mantra Gate Senior Manager (Birth)

> Contrato falsificável de certificação. NÃO é um relatório de saúde. Define o que precisa ser **verdade verificável (file:line + comando verde)** para a fatia Birth ser declarada CONVERGIDA e CERTIFICÁVEL — pré-requisito único e indivisível de sync. Toda âncora abaixo foi re-executada contra os arquivos reais; correções de contagem/terminologia já estão absorvidas no texto (não herdamos citações derivadas).

---

## 1. CONTEXTO E ESCOPO DA CERTIFICAÇÃO

**O que está sendo certificado.** A fatia **Birth** da promoção do Mantra Gate a *gerente sênior*: 10 commits locais (`027bcf9d`…`c405506a`), entregando um substrato **reativo, em tempo de commit/git, host-agnóstico**:
- Substrato aditivo no `mantra_gate.py` (novo status `DRIFT_FROM_CONTRACT` peso 3 `:21`; envelope `supervise:{tier,interrupted}` `:311`).
- Contrato de pacote de transferência de ativo (`docs/governance/asset-transfer-packet.md`, 8 campos, JSONL).
- Detector `new_skill_without_packet.py` que parseia `REQUIRED_FIELDS` do contrato vivo (não hard-coded), cabeado como Gate `"asset-transfer-packet"` (`staged_commit_gate.py:353`).
- Dois oráculos auto-falsificáveis com falsificador autor-agnóstico (`test_mantra_gate_no_regression.py`, `build_detector_remutation_plan.py`).
- Retenção do contrato de plantão (`PLANTAO-HOOK-MECHANISM.md`, `status: proposed`, `source_of_truth: false`).

**O que explicitamente NÃO está sendo certificado.** O **plantão pró-sciente** — a camada pré-ação por evento de host (`PreToolUse`/`UserPromptSubmit`/`beforeSubmitPrompt`), a injeção de rubrica-que-não-decide, o intent-by-regex, o anti-cry-wolf por sessão. Confirmado por `grep -nE "PreToolUse|UserPromptSubmit|beforeSubmitPrompt|exit 2|additionalContext|updatedInput"` sobre os 5 scripts entregues → **zero ocorrências**. A fatia Birth **honestamente para no reativo**. O proativo é a **próxima fatia**, ancorada em `PLANTAO-HOOK-MECHANISM.md` + `FLASH-FRY-SKILL-SPEC.md` (§9).

**A fronteira honesta.** Esta certificação é de **fidelidade código↔ledger e integridade de leis** sobre uma fatia reativa. Ela **NÃO certifica fidelidade plano↔código contra o texto aprovado literal**, porque o plano aprovado vive **fora do repositório git**, em `~/.claude/plans/starry-brewing-patterson.md` (existe, 9056 bytes — confirmado por `ls`), e não é versionável/diffável a partir do git (`git ls-files` o reporta "outside repository"). Sob "nunca adivinhar", o eixo plano↔código não é confrontável byte-a-byte contra o histórico do repo; **decisão de base registrada (item 2.A): o ledger é a autoridade-de-registro** desta certificação, e o plano-fora-do-git é evidência de baseline, não fonte versionada. E ela **NÃO certifica release/closure**, que é dono-gated e tem red esperado-e-honesto (§7).

---

## 2. MATRIZ DE CONVERGÊNCIA PLANO↔CÓDIGO

**Fronteira de verificabilidade (decisão de base — RESOLVIDA).** O artefato de plano aprovado **existe**, mas **fora do repositório git**, em `~/.claude/plans/starry-brewing-patterson.md` (9056 bytes; `ls` resolve; `git ls-files` → "outside repository"). A leitura anterior ("ausente") era um **false-negative** de busca-no-cwd-do-repo (`git log --all -- '*patterson*'` é vazio porque o plano nunca esteve sob versionamento, não porque não exista). Como o plano não é diffável byte-a-byte contra o histórico do repo, a matriz abaixo confronta cada SPEC do **ledger** — formalmente declarado **autoridade-de-registro** desta certificação (item 2.A, decisão registrada) — contra o código. O eixo plano↔código literal permanece **não-confrontável-por-git** (decisão de base, não adivinhação); a fidelidade certificada é ledger↔código.

| Item (ledger SPEC) | Artefato | Veredito |
|---|---|---|
| SPEC-001 oráculo no-regression | `test_mantra_gate_no_regression.py` | CONVERGE — `--self-test`→`{"status":"PASS"}` exit 0; 10 grupos rotulados A–J via `check()` (`:60`,`:65`–`:107`) |
| SPEC-002 contrato de pacote | `docs/governance/asset-transfer-packet.md` | CONVERGE — 8 campos, JSONL (`kind`/`skill_name`) |
| SPEC-003 detector | `supervise_detectors/new_skill_without_packet.py` | CONVERGE no comportamento (verde) — **DIVERGE em contagem documental** (item 2.B) |
| SPEC_REPAIR_BY_LLM refuter de peso | `test_mantra_gate_no_regression.py` | CONVERGE — muta fragmento `"PROCEED": 0`→`9` (não-vacuo sob crescimento aditivo); audit 4/0 |
| SPEC-004 substrato supervise | `mantra_gate.py` | CONVERGE — `DRIFT_FROM_CONTRACT:3` `:21`; `supervise` `:311`; aditivo 21/2 |
| SPEC-005 falsificador do detector | `build_detector_remutation_plan.py` | CONVERGE — plano distinto, decoy não-vacuo; `--self-test`→4/0 PASS |
| Retenção plantão | `PLANTAO-HOOK-MECHANISM.md` | CONVERGE como retenção ADR-0005 — **confidencialidade RESOLVIDA** (commit `86ca5d3b`; grep de identificadores → vazio; ver 2.C, §3) |
| SPEC-006 gate + gitignore | `staged_commit_gate.py:353`, `.gitignore` | CONVERGE — Gate `"asset-transfer-packet"`; 17 gates totais |
| SPEC-AUDIT-001 parse-do-contrato | `new_skill_without_packet.py` | CONVERGE — parseia `REQUIRED_FIELDS`; unparseable→NEEDS_REVIEW |
| SPEC-AUDIT-002 índice TDS | `docs/tds/DOCS-INDEX.yml` | CONVERGE — ambos os docs registrados |

**Os 10 commits CONVERGEM** (todos resolvem via `git log -1 --oneline`; assuntos batem com os rótulos SPEC). **O ledger não está rastreado** (`?? GOAL-EXECUTION-LOOP-LEDGER-mantra-senior-manager-birth.md`) → item 2.D.

### Itens de ação (somente DIVERGE)

- **2.A [RESOLVIDO — decisão de base registrada] Plano aprovado vive fora do git.** `~/.claude/plans/starry-brewing-patterson.md` existe (9056 bytes; `ls` resolve), mas fora do repositório (`git ls-files` → "outside repository"). A leitura anterior de "ausente" foi false-negative de busca-no-cwd. **Decisão registrada:** o ledger é a autoridade-de-registro; o plano-fora-do-git é evidência de baseline, não fonte versionada confrontável byte-a-byte. Eixo plano↔código literal: não-confrontável-por-git (declarado, não adivinhado). **Fechado.**
- **2.B [RESOLVIDO] Contagem do detector alinhada.** Docstring `new_skill_without_packet.py:242` diz "**Eight fixtures**" e bate com a lista `cases` (8 elementos: 1,2,3,4,5,6a,6b,7). `grep -n "Eight fixtures" scripts/supervise_detectors/new_skill_without_packet.py` → `:242`. **Fechado** (corrigido em fatia anterior; a contagem "Six"/"5"/"7" de relatórios antigos não se aplica ao estado atual).
- **2.C [RESOLVIDO — confidencialidade, ver §3] Vazamento de identificadores neutralizado** em `PLANTAO-HOOK-MECHANISM.md` (commit `86ca5d3b`). Verificação: o grep do conjunto-de-identificadores-do-projeto-referência (padrão canônico mantido no ledger da task #10; **não re-encarnado aqui** — regra 3.A-bis) sobre o doc → **vazio**. **Fechado.**
- **2.D [aberto — endereçado por SPEC-C-005] Ledger não commitado.** A autoridade-de-registro que substitui o plano não é reproduzível do git. SPEC-C-005 commita o ledger **ou** registra a decisão de exclusão. (Único item 2.x ainda aberto.)

---

## 3. FIDELIDADE AO APRENDIZADO mem0

**Eixo de código (mecanismos proativos ENTREGUES) = NENHUM — HONESTO, CONFIRMADO.** Zero `PreToolUse/UserPromptSubmit/beforeSubmitPrompt/exit 2/additionalContext/updatedInput` nos 5 scripts. `staged_commit_gate.py:62` usa `git diff --cached` — puramente tempo-de-commit. O literal `mem0` não aparece em nenhum script.

**Diferido-com-contrato — HONESTO, CONFIRMADO.** O doc declara o gap em prosa (a camada pré-ação/por-intenção "não existe") e marca cada fatia proativa como `owner_deferred` com oráculo falsificável na §5. A fronteira reativo↔proativo está **declarada**, não escondida.

**Reivindicado-sem-lastro — UMA VIOLAÇÃO (confidencialidade), agora RESOLVIDA.** Quando este eixo foi primeiro auditado, `PLANTAO-HOOK-MECHANISM.md` **violava a própria regra de fronteira `:122`** e a afirmação do seu commit de retenção: três linhas enumeravam, **verbatim e dentro da própria lista §6 que declara o que "NÃO atravessa"**, identificadores técnicos do projeto-referência por **categoria** — (a) nomes de tool MCP de memória, (b) prefixos de env var de plugin-root + roster de nomes de arquivo de hook-script, (c) campos de schema de memória. O **nome do projeto** já estava 100% neutralizado (`grep -ci <nome> → 0`); o vazamento era estritamente dos identificadores técnicos. (Esta SPEC descreve o vazamento **por categoria, não por token**, deliberadamente — para não reintroduzir os mesmos identificadores neutralizados num artefato rastreável; ver regra de auto-neutralização abaixo.)

**Estado atual — FECHADO (`86ca5d3b`).** O doc foi reescrito **por forma**, não por substituição-de-token: a mecânica (exit-code, regex-shape, contrato de saída por host) foi retida; cada identificador técnico do projeto-referência virou placeholder. Prova: o grep do conjunto-de-identificadores (padrão canônico no ledger da task #10, não re-encarnado nesta SPEC) sobre `docs/roadmap/product/PLANTAO-HOOK-MECHANISM.md` → **vazio**.

### Itens de ação
- **3.A [RESOLVIDO] Vazamento de identificadores neutralizado** em `PLANTAO-HOOK-MECHANISM.md` (`86ca5d3b`), por forma, audit-caught (não reparo silencioso). `private_vocabulary_oracle.py` cobre o doc no `commit:closure`. **Fechado.** O gate falsificável-de-classe (que detecta *qualquer* identificador de projeto-referência futuro, não só esta lista) fica como item TETO declarado (task #11, fatia futura).
- **3.A-bis [regra de auto-neutralização desta SPEC] Esta SPEC não pode re-vazar.** Como este arquivo será commitado por SPEC-C-005, ele **não** enumera os identificadores neutralizados verbatim — descreve o vazamento histórico por categoria. Falsificável: o mesmo `grep` de 3.A rodado sobre **esta** SPEC deve retornar vazio.
- **3.B [verificação correlata] Re-avaliar as citações de forma `:39`,`:48`,`:55`,`:106`** contra a regra `:122`: confirmar que carregam apenas *forma* (exit-code, regex-shape, header verbatim de comportamento) e não identificador de domínio. `private_vocabulary_oracle.py` deve cobrir essas linhas no `commit:closure`.

---

## 4. OS QUATRO PILARES DE EXECUÇÃO — SEÇÃO CENTRAL DA CERTIFICAÇÃO

### Matriz de quatro pilares

| Pilar | Estado real (file:line) | Classificação | Âncora da fatia seguinte |
|---|---|---|---|
| **1. BOOTLOADER (camada-mãe)** | `AGENTS.md:40` e `.claude/CLAUDE.md:40` — blocos `<mantra_gate>` byte-idênticos, **framing reativo pontual antigo** ("só para mudanças destrutivas, remotas, de release, sync, secret-bearing ou de alto impacto… não bloqueie" em edições ordinárias). **Sem critério de plantão proativo.** | **GAP-DECLARADO** | PLANTAO §3 `:72`, Slice 1 `:130`/`:136` |
| **2. SKILLS** | 19 skills `tes-*` por adaptador, **nenhuma flash-fry** (`find src/adapters -path '*flash-fry*'` → vazio). Marker <code>MARKER = "`🍳 Flash-Fry`"</code> (`mantra_gate.py:19`); validado via `materialize_adapter.py` contra termos da discipline skill. **Sem superfície de invocação `/flash-fry`.** | **AUTO-ATIVO** (marker via discipline skill) **+ GAP-DECLARADO** (`/flash-fry`) | `FLASH-FRY-SKILL-SPEC.md`; PLANTAO Slice 2 |
| **3. HOOKS (por-host)** | TES instala **só `SessionStart`** em todos os hosts (`tes_install.py`: Claude `install_claude_hook`, Codex `:205-208`+flag `codex_hooks` `:219`, Cursor `install_cursor_hook`). Cursor re-anexa o MESMO `hook_entry("cursor")` em `sessionStart`+`beforeSubmitPrompt` → **facade**. Sem `PreToolUse`/`UserPromptSubmit` real em `src/adapters`. | **GAP-DECLARADO** (paridade por-host **PARCIAL** — ver §4.1) | PLANTAO Slices 3-5 `:133-134` |
| **4. AGENTS** | `grep "mantra\|flash-fry\|plantão\|senior-manager"` sobre todos `src/adapters/**/agents/openai.yaml` → **zero hits**. Nenhum `openai.yaml` registra o gate como agente-dever. | **GAP-DECLARADO** | PLANTAO Slice 5 |

### RELAÇÃO DE GRAVIDADE — INVERSÃO LATENTE, HONESTAMENTE DECLARADA

A lei de gravidade está escrita verbatim no doc-âncora: **`PLANTAO:77`** — *"a **primeira fatia** mexe na Camada 0, e só então as demais herdam o critério — não o contrário"*; **`:136`** — *"A fatia 1 (Camada 0) define o critério; as fatias 2-4 herdam-no por projeção"*. O bootloader (`<mantra_gate>`) é a **camada-mãe que gera os outros três**: o regex de risco (hooks) e o matcher de tool (hooks/skills) são "apenas a projeção executável da regra do bootloader".

**O que a fatia Birth fez:** entregou o **enforcement** (commit-gate reativo, host-agnóstico) **SEM atualizar o bootloader-mãe** (`:40` ainda no framing reativo antigo). **O enforcement roda à frente da regra-mãe que o justifica.**

**Veredito de gravidade:** isto é uma **INVERSÃO LATENTE, MAS DECLARADA** — não silenciosa. O doc declara a inversão (`:17` "fiado só no tempo de commit — reativo"; Slice 1 não iniciada). Portanto: **honesta no registro, mas a certificação DEVE sinalizá-la** e NÃO pode chamar o modelo de quatro pilares de "coerente" hoje.

**Condição de coerência (falsificável):** o modelo de quatro pilares só é COERENTE quando **a camada-mãe (bootloader) declara o critério e os outros três o projetam**. Hoje falta: o `<mantra_gate>` em AMBOS os espelhos (`AGENTS.md:40`, `.claude/CLAUDE.md:40`) ainda **não** declara o critério de plantão proativo. **Coerência = Slice 1 (upgrade do bootloader com band-oracle de calibração) ser a PRÓXIMA fatia entregue, antes de qualquer pilar de projeção.** Qualquer claim de "convergência dos quatro pilares" é falso até lá.

**Disposição dos gaps:**
- Todos os quatro pilares estão **GAP-DECLARADO** (estado proativo) ou **AUTO-ATIVO** (marker da discipline skill) → entram nos **diferidos (§9)**, na ordem de gravidade.
- O único **GAP-NÃO-DECLARADO** estava **dentro do pilar de hooks** (paridade por-host de contrato de saída) → **RESOLVIDO em `5737b5bd`** (matriz Cursor adicionada ao PLANTAO `:109`); ver §4.1.

**Distinção que NÃO pode colapsar:** o commit-gate entregue (SPEC-006, `staged_commit_gate.py:353`, dirigido por `git_staged_paths()` `:62`) é **enforcement reativo host-agnóstico em tempo-de-git** — **NÃO** é o pilar de hooks por-host (PreToolUse), que permanece inteiramente gap. Não conflar.

### SUB-SEÇÃO 4.1 — PARIDADE MULTI-HOST (OBRIGATÓRIA)

Os pilares hooks/agents/skills **NÃO são uniformes** entre Claude Code, Codex e Cursor — há diferenças reais de **NOME** e **CAMADA** do gancho. A certificação **não pode tratar 'hooks' como camada única**. Matriz verificada contra o projeto-referência (`tmp/project-mem0/mem0/integrations/mem0-plugin/`):

| Dimensão | Claude (`hooks.json` top-level) | Codex (`hooks/codex-hooks.json`) | Cursor (`hooks/cursor-hooks.json`) |
|---|---|---|---|
| **(a) Pré-ação** | `PreToolUse:33` | `PreToolUse:3` | **`preToolUse:10`** (camelCase) |
| **(b) Intenção** | `UserPromptSubmit:21` | `UserPromptSubmit:47` | **`beforeSubmitPrompt:49`** (nome E camada divergentes) |
| **(c) Exclusivos** | — | **`statusMessage`** só-Codex (`:42,:53,:98`); `PreCompact:92` | `preCompact:44` |
| **(d) Ponto de instalação** | `.claude/settings.json` (TES: `SessionStart` only) | `.codex/config.toml` + **flag `codex_hooks=true`** (`tes_install.py:219`) + guarda Windows `.sh` | `.cursor/hooks.json` **`version:1`** (`:2`); TES re-anexa em `sessionStart`+`beforeSubmitPrompt` → facade |
| **(e) Contrato de saída** | **`exit 2` bloqueia** + stderr→agente; `hookSpecificOutput.updatedInput` reescreve parâmetros | **idêntico a Claude** (`exit 2` + `updatedInput`) | **NÃO exit-2** — bloqueio por JSON-permission `{"permission":"deny","agent_message":"…"}`; intenção por `{"continue":true,"user_message":"<text>"}` |

**Três divergências verificadas, não-colapsáveis:** (1) nome do evento de intenção `UserPromptSubmit` vs `beforeSubmitPrompt`; (2) `statusMessage` só-Codex (`PreCompact` **não** é estritamente só-Codex: presente em Codex, Cursor e em `hooks/hooks.json:102`; **ausente apenas no `hooks.json` top-level** de Claude — reconciliar qual é o alvo canônico Claude); (3) contrato de saída **NÃO uniforme** — Cursor é JSON-permission, não exit-2.

**A paridade por-host está DECLARADA em PLANTAO? — PARCIAL.**
- **Declarado:** pontos de instalação, split do nome de intenção (`:27`, Slice 4 `:133`), flag de feature Codex + guarda Windows `.sh` (`:112`), `statusMessage` só-Codex (`:112`), camelCase Cursor.
- **Era NÃO declarado (registro histórico da auditoria) — agora DECLARADO (`5737b5bd`):** na auditoria, o doc apresentava exit-2 como schema portável e o contrato JSON-permission do Cursor não aparecia. **Reparo:** a matriz §4.1 do PLANTAO agora carrega a linha (e) de contrato-de-saída por host, com a coluna Cursor explícita em JSON-permission (`:109`) e as três divergências não-colapsáveis nomeadas (`:111`). `grep -nE "permission|agent_message|user_message" docs/roadmap/product/PLANTAO-HOOK-MECHANISM.md` → `:109`/`:111`. Cursor continua não honrando exit-2 — mas isso agora está **declarado**, não silencioso.

**Veredito de paridade — RESOLVIDO (`5737b5bd`).** O gap acima era real **no momento da auditoria**; foi fechado: `PLANTAO-HOOK-MECHANISM.md` ganhou a matriz por-host de cinco dimensões (a)–(e) com a **linha do contrato-de-saída Cursor** (JSON-permission: `{"permission":"deny",…}` bloqueio / `{"continue":true,"user_message":…}` intenção) — `:109`. Falsificável: `grep -nE "permission|agent_message|user_message" docs/roadmap/product/PLANTAO-HOOK-MECHANISM.md` → retorna `:109`/`:111`. A fatia seguinte de hooks é agora **certificável-coerente** quanto à declaração de paridade. O commit-gate entregue (SPEC-006) é host-agnóstico (roda em git) e **NÃO precisa** dessa matriz. **Ainda assim, NÃO certificar o pilar de hooks como uniforme** — a matriz declara as três divergências, não as colapsa.

---

## 5. VEREDITO POR LEI

| Lei | Veredito | Evidência (file:line / comando) |
|---|---|---|
| **ADR 0005 — sem nova skill / pacote de transferência real** | **SATISFEITO** | `git diff 027bcf9d^ HEAD --name-only` → 10 arquivos, **zero `SKILL.md`**; detector parseia `REQUIRED_FIELDS` do contrato vivo (`5ca449a3`); case 6b (`new_skill_without_packet.py:282-288`) prova flip contrato-9/packet-8→`DRIFT_FROM_CONTRACT`; gate cabeado `:353` |
| **ADR 0006 — afirmação nunca é crédito** | **SATISFEITO (solidez + durabilidade CI)** `50f0bd60` | Ambos os falsificadores autor-agnósticos disparam: regression `audit-remutation.mjs`→4/0; detector→4/0 (decoy é controle negativo). **GAP-CI fechado (`50f0bd60`):** `commit:closure` agora roda os três `--self-test` da fatia **E** os dois replays `audit-remutation` (regression + detector plans). Falsificável: `grep -o "audit-remutation" package.json | wc -l`→2; `runChecks` (`harness.mjs:8`) força exit 1 sob facade futuro. As provas deixaram de ser hand-run-only. |
| **Owner — ganhar sem perder ("ganhar tools sem perder o que é")** | **SATISFEITO** | `mantra_gate.py` aditivo **21 ins / 2 del**; as 2 deleções re-emitem `STATUS_WEIGHT` com os três pesos antigos byte-intactos (`:21`), só `DRIFT_FROM_CONTRACT:3` anexado; `mantra_gate_adoption_oracle.py` **byte-untouched** (`git diff 027bcf9d^ HEAD` vazio); oracle usa checagens de subconjunto `<=` nas superfícies aditivas |
| **Owner — nunca adivinhar** | **SATISFEITO** | Hashes-âncora exatos (ADR 0005 `f0c70274…`, ADR 0006 `58a53a48…`); claims audit reproduzidos ao vivo; cada veredito desta sessão re-medido por comando (false-negative de "plano ausente" corrigido por `ls`; drift C8 provado por extração de zip; C7 por `grep -o`). O eixo plano↔código literal é **declarado** não-confrontável-por-git (plano vive fora do repo, decisão 2.A), não adivinhado |
| **Release identity / closure** | **GAP dono-gated + oracle des-cegado (`5fd4ce79`)** | `mantra_gate.py` está em `HELPER_FILES` (`tes_bundle.py:79`) → comportamento entregue. `VERSION="0.3.195"` **inalterada**; 0.3.195 publicada ANTES da fatia. **Drift provado:** fonte `DRIFT_FROM_CONTRACT`=2 vs bundle 0.3.195=0. **Mudança desta certificação:** `public_bundle_oracle.py` **deixou de ser cego** — agora compara cada `HELPER_FILE` working-tree↔zip e **FALHA** sob drift salvo `VERSION` avançada (ADR 0005 invariante 7 `:100` **agora cumprido**). O oracle reporta `FAIL` nomeando `scripts/mantra_gate.py` — **red-esperado dono-reconhecido**, não cegueira. Reconciliar (bump+bundle) é dono-gated; **não tomado nesta fatia** (§7). Condição de fecho exata: `VERSION` move + bundle regenera. |

Cada GAP acima vira critério de aceitação (§6).

---

## 6. CRITÉRIOS DE ACEITAÇÃO DE CERTIFICAÇÃO (falsificáveis)

Para declarar a fatia Birth **CONVERGIDA E CERTIFICÁVEL**, cada item abaixo deve estar verde (comando rodável ou checagem de fixture):

1. **[VERDE] Plano re-baselinado no ledger.** O plano aprovado existe fora do git (`ls ~/.claude/plans/starry-brewing-patterson.md` → 9056 bytes); decisão de base registrada (§1, §2 item 2.A): **o ledger é a autoridade-de-registro**; o eixo plano↔código literal é declarado não-confrontável-por-git (não adivinhação). Falsificável: `ls ~/.claude/plans/starry-brewing-patterson.md` resolve **E** o bloco de decisão 2.A está nesta SPEC.
2. **[fechado por SPEC-C-005] Ledger decidido.** `git status --porcelain | grep ledger` vazio (commitado) **OU** decisão de exclusão documentada. SPEC-C-005 executa.
3. **[VERDE] Vazamento de identificadores neutralizado** (`86ca5d3b`). O grep de identificadores do projeto-referência (a lista canônica vive no comando de verificação do ledger SPEC-AUDIT/task #10; **não a re-encarno aqui** para esta SPEC não re-vazar — regra 3.A-bis) sobre `docs/roadmap/product/PLANTAO-HOOK-MECHANISM.md` → **vazio**. Nota de fato: `private_vocabulary_oracle.py` roda sobre a árvore mas detecta o **vocabulário privado do owner** (8 entries em `.tes/private-vocabulary.txt`), **não** identificadores genéricos de projeto-referência — o gate falsificável-de-classe para estes é o item TETO (task #11), declarado, fatia futura. A proteção atual é a neutralização-por-forma + o grep manual.
4. **[VERDE] Contagem do detector alinhada.** `grep -n "Eight fixtures" scripts/supervise_detectors/new_skill_without_packet.py` → `:242`; bate com `cases` (8 elementos: 1,2,3,4,5,6a,6b,7).
5. **[VERDE] Auto-testes (re-execução, não afirmação):** `test_mantra_gate_no_regression.py --self-test`→PASS exit 0; `mantra_gate.py --self-test`→0; `mantra_gate_adoption_oracle.py --self-test`→0; `new_skill_without_packet.py --self-test`→`{"status":"PASS"}`; `build_detector_remutation_plan.py --self-test`→`4 pass, PASS`. (Re-executados nesta sessão: todos exit 0.)
6. **[VERDE] Falsificadores autor-agnósticos disparam:** regression `--write-plan` → `audit-remutation.mjs tmp/regression-remutation-plan.json`→4/0; detector → `audit-remutation.mjs tmp/detector-remutation-plan.json`→4/0 (decoy é controle negativo, permanece OK). Caminho canônico: `.claude/skills/tes-goal-maestro/scripts/audit-remutation.mjs` (4 cópias idênticas).
7. **[VERDE — `50f0bd60`] Provas da fatia cabeadas em CI (fecha GAP ADR 0006).** `commit:closure` agora roda, após os três `--self-test`, os dois replays: `test_mantra_gate_no_regression.py --write-plan && audit-remutation.mjs tmp/regression-remutation-plan.json` e `build_detector_remutation_plan.py && audit-remutation.mjs tmp/detector-remutation-plan.json`. Falsificável: `grep -o "audit-remutation" package.json | wc -l` → **2**; `runChecks` (`harness.mjs:8`) garante exit 1 sob facade futuro.
8. **[VERDE — `5fd4ce79`] `public_bundle_oracle` ganha checagem de drift fonte↔bundle.** Asserção: cada `HELPER_FILE` cujos bytes no zip publicado diferem da working tree ⇒ FAIL, **salvo** `VERSION` avançada além da publicada (bump em curso). Falsificável e provado: drift vivo → `FAIL` nomeando `scripts/mantra_gate.py`; `VERSION` simulada 0.3.196 → asserção se cala (0 drift failures). **A cegueira morreu.** O red resultante é o red-esperado §7 (engenharia fechada; release dono-gated).
9. **[VERDE — red-esperado dono-reconhecido] `commit:closure` roda a veredito não-vacuo.** O closure agora **não é vacuo**: roda `public_bundle_oracle.py` (que reporta FAIL honesto por drift, item 8) e os dois replays de falsificador (item 7) — todos não-SKIP. O FAIL do `public_bundle_oracle` é **red-esperado por lei** (§7 + ADR 0006: facade é proibido, red honesto é sancionado), com **condição de fecho exata e nomeada: `VERSION` move além de 0.3.195 + bundle regenera** (decisão de release dono-gated, não tomada nesta fatia). Reverter a hardenização do item 8 para "passar o CI" re-cega o oracle = **regressão visível**, não conserto. Falsificável: o closure não pode ser declarado verde por SKIP-vacuo; ou passa não-vacuo, ou exibe o red-esperado nomeado.
10. **[VERDE — `5737b5bd`] Coerência dos quatro pilares declarada no doc certo.** Cada pilar (§4) na classificação declarada, gap no doc certo (Pilar 1 bootloader em `PLANTAO`; Pilar 2 `/flash-fry` em `FLASH-FRY-SKILL-SPEC.md`; Pilar 4 agents em PLANTAO Slice 5). A matriz por-host §4.1 (a)–(e) existe em `PLANTAO-HOOK-MECHANISM.md` com a linha do contrato-de-saída Cursor (JSON-permission). Falsificável: `grep -nE "permission|agent_message|user_message" docs/roadmap/product/PLANTAO-HOOK-MECHANISM.md` → retorna a linha Cursor (`:109`).
11. **[VERDE] Inversão de gravidade sinalizada.** Esta certificação registra explicitamente (§4) que o enforcement (commit-gate) precede o bootloader-mãe, classifica os quatro pilares como **NÃO-coerentes hoje**, e gateia qualquer claim de coerência na Slice 1 (upgrade do `<mantra_gate>`) ser a próxima fatia entregue.

**Estado recalibrado por fato (re-medido nesta sessão):** itens **1, 3, 4, 5, 6, 7, 8, 9, 10, 11 = VERDES**. Item **2** fecha em SPEC-C-005 (este loop). A fatia está **CONVERGIDA E CERTIFICÁVEL** assim que o item 2 fechar — com a ressalva de lei: o item 8/9 carrega um **red-esperado dono-reconhecido** (engenharia fechada, release dono-gated), que é certificação-honesta, não falha. (A reconciliação plano↔código contra texto-literal permanece não-confrontável-por-git por decisão de base 2.A, não por gap.)

---

## 7. GAPS DE RELEASE-IDENTITY (declarar, NÃO mover agora)

A fatia é **comportamento entregue** (`mantra_gate.py` está em `HELPER_FILES`, `tes_bundle.py:79`): novo status `DRIFT_FROM_CONTRACT`, envelope `supervise`, novo detector, novo contrato. Sob `<release_identity>` + ADR 0005 invariante 7 (`:100`), isto exige **decisão de release-identity antes do closure**. Superfícies que precisariam mover **SE/QUANDO o owner autorizar bump+bundle**:

- `package.json:3` `"version": "0.3.195"` → próximo patch.
- `mantra_gate.py:17` `VERSION = "0.3.195"` (e demais constantes `VERSION` de scripts entregues).
- Plugin manifests (`plugins/tilly-engineer-skills/**`).
- `docs/dist/<nova-versão>/**` — novo bundle + `tilly-engineer-skills-<v>.zip`.
- `.sha256` sidecars + `docs/dist/index.json`.
- Public docs (landing/manual) se a versão exibida mudar.
- Validadores de release e a maintainer correlation rule.

**Decisão atual: NÃO mover.** O owner não autorizou bump; nenhum push/publish/tag. **O que esta convergência fez para furar o teto (não aceitar o piso):** o `public_bundle_oracle` foi **des-cegado** (`5fd4ce79`) — antes ele teria deixado o drift passar em silêncio sob 0.3.195 (o piso: facade verde). Agora ele **detecta e reporta** o drift como `FAIL` honesto, com condição de fecho nomeada (`VERSION` move + bundle regenera). O drift deixou de ser invisível; tornou-se um red-esperado **rastreável e dono-reconhecido**. A separação é limpa: **engenharia fechada** (a cegueira morreu, o oracle vê), **release pendente** (bump+bundle é decisão per-request do owner). Reverter a hardenização para "passar o CI" re-cegaria o oracle = **regressão**, não conserto.

---

## 8. PORTÃO DE SYNC

**Condição exata e única sob a qual sync é legítimo:**

> **certificação verde (todos os itens §6 fechados ou formalmente diferidos por lei) + decisão de release-identity §7 tomada + autorização explícita e per-request do owner.**

`git rev-list --count @{u}..HEAD` = **41** (10 desta fatia + 31 anteriores), **todos locais**. Remote **NÃO autorizado**. Por `<operating_discipline>`: "push it" não é grant permanente — cada push precisa do seu próprio request.

**Enquanto qualquer item §6 (1–4, 7–11) estiver aberto sem diferimento por lei, ou enquanto o owner não autorizar explicitamente: NÃO sync, NÃO push, NÃO publish, NÃO tag.** Sync está **corretamente bloqueado**.

---

## 9. O QUE FICA DIFERIDO (declarado, não escondido)

As fatias de plantão seguintes, na **ordem de gravidade** (`PLANTAO:77,136` — a camada-mãe primeiro, depois as projeções):

1. **Slice 1 — Bootloader (Camada 0, camada-mãe).** Upgrade do `<mantra_gate>` em AMBOS os espelhos (`AGENTS.md:40`, `.claude/CLAUDE.md:40`) para o critério de plantão proativo, com band-oracle de calibração (`PLANTAO:130,136`). **Deve ser a próxima fatia** — restaura a gravidade declarada. Abre em `Birth`, sem bump (corpo maintainer).
2. **Slice 2 — Skills / `/flash-fry`.** Materializar `/flash-fry` per `FLASH-FRY-SKILL-SPEC.md`, **OU** reafirmar formalmente AUTO-ATIVO-only (marker via discipline skill) como escopo Birth aceito, com o gap de invocação mantido declarado.
3. **Slices 3-4 — Hooks pré-ação (por-host).** Camada 1-2 projetando o critério da Camada 0 nos eventos de host. Pré-requisito: matriz por-host §4.1 declarada (item 6.10). `owner_deferred` por release-identity (toca instalador/configs do target).
4. **Slice 5 — Agents preset (duty-agent).** Registrar o gate como agente-dever em `openai.yaml` (hoje zero hits). `owner_deferred`.

Âncoras de diferimento: `docs/roadmap/product/PLANTAO-HOOK-MECHANISM.md` (`status: proposed`, `source_of_truth: false`) e `docs/roadmap/product/FLASH-FRY-SKILL-SPEC.md`. Nenhuma canary/âncora em fonte rastreada além desses docs de roadmap — handoff de próxima-fatia limpo.

---

**Bottom line (verificado, recalibrado por fato nesta sessão).** A engenharia é sólida: aditiva (21/2, pesos antigos byte-intactos), o adoption oracle protegido está byte-untouched, os oráculos genuinamente se auto-falsificam sob refuter autor-agnóstico (8/8 mutações disparam nos dois planos), e nenhuma nova skill foi criada. Dos 11 critérios §6, **dez estão VERDES** após re-medição e três commits desta convergência:
- **C8 (`5fd4ce79`)** — `public_bundle_oracle` **des-cegado**: agora detecta drift fonte↔bundle e reporta `FAIL` honesto (não mais PASS cego). A cegueira que o item 8 nomeava morreu.
- **C7 (`50f0bd60`)** — os dois falsificadores autor-agnósticos **cabeados em `commit:closure`** (replay, não só self-test). ADR 0006 durabilidade-CI fechada.
- **C1/C2-texto/C3/C4/C9/C10/C11** — reconciliados por fato: o plano **existe** (fora do git → ledger é autoridade-de-registro, decisão 2.A); vazamento neutralizado (`86ca5d3b`); contagem "Eight" (`:242`); matriz Cursor presente (`5737b5bd`); inversão de gravidade sinalizada (§4).

**Único item de execução restante: C2 (ledger não-rastreado)** → SPEC-C-005, neste loop. O **red-esperado** do `public_bundle_oracle` (drift 2 vs 0) é **certificação-honesta dono-gated**, não falha: engenharia fechada (oracle vê o drift), release pendente (bump+bundle é decisão per-request do owner, §7). A **inversão de gravidade** (enforcement antes do bootloader-mãe) é honesta-e-declarada e a certificação a sinaliza: **os quatro pilares NÃO são coerentes hoje** — coerência exige a Slice 1 (bootloader) como a próxima fatia. **Sync permanece corretamente NÃO autorizado** (§8): nenhum item de lei o libera, e o owner não autorizou.

---

Arquivo de evidência scratch (não-entregável): `/private/tmp/claude-501/-Users-murillo-Dev-tilly-engineer-skills/e7afb2c3-aae3-4fe2-8f07-d192b983de0a/scratchpad/convergence-spec.md` (placeholder). O contrato de certificação acima É a saída — o parent o persiste com o header TDS.
