---
tds_id: roadmap.audit.agent_hook_functional
tds_class: roadmap
status: active
consumer: maintainers, hook authors, oracle authors, and canary operators
source_of_truth: false
evidence_level: L2
---

# Agent Hook — Auditoria Funcional (working doc)

> **STATUS: WORKING DOC — NÃO É DOCUMENTAÇÃO DE PROJETO.**
> Esteira de desenvolvimento / auditoria / fix. Este arquivo descreve o estado
> *atual e verificado* da superfície de agent hooks do TES, incluindo bugs, gaps
> e tech-debt em aberto. **Não promover para documentação canônica** (`docs/architecture/`,
> `docs/agents/`, user manual) enquanto houver qualquer item em `## Findings acionáveis`.
> Quando a seção de findings zerar, esta matriz pode ser destilada em doc de projeto.

## 0. Sumário executivo

**36/36 afirmações auditadas** contra a fonte atual (34 ✅ · 2 imprecisas/incorretas que escondiam bug). **16 findings** sobreviveram à refutação adversarial; 11 refutados.

| Sev | Findings | Tema |
|---|---|---|
| **HIGH** | H-01, H-02 | **Perda de config do usuário** na superfície instalada (uninstall Codex engole bloco adjacente; `read_json` clobbera settings malformado). |
| **HIGH** | H-03 | **Bypass de governança via shell**: `echo/tee/sed/rm/cat` em superfície governada → `allow` silencioso (reproduzido). |
| **HIGH** | H-04 | **Evidência host-real forjável**: `provenance="host-real"` incondicional; qualquer chamador satisfaz ceiling. |
| MEDIUM | BUG-01…07, PREC-01 | fail-open de import, perda silenciosa de ledger, vazamento de segredo em reason/path, ramos de supervisão mortos p/ shell, corrupção de TOML alheio. |
| LOW | BUG-08, PREC-02/03, DEBT-01 | `SKILL.md` raiz não-governado, dedupe de janela, sentinel fail-open parcial, helper órfão. |

**Causa-raiz dominante:** o kernel supervisiona bem o caminho **estruturado** (`Edit`/`apply_patch` com `file_path`), mas é cego a **comando shell** (path nunca extraído) e o instalador confia demais em config do usuário bem-formado. Um único fix (extração de path shell) fecha H-03 + BUG-04/05/08.

**Caminho de fix (§7):** cada finding mapeia numa das 6 classes de solução madura, triangulada por mem0 + graphify + pesquisa web (6/6 classes `grounded`). Tese única: *mova a confiança da fronteira para o núcleo — parse defensivo · prove-don't-trust · degrade-loud · reconcile por manifesto.*

| Classe | Findings | Padrão maduro | Adotar (mira laser) |
|---|---|---|---|
| C1 command-intent | H-03, BUG-04/05/08 | parse-then-evaluate, fail-closed no ambíguo | parsear Bash espelhando o Claude Code; extrair path de redirect/flag; ambíguo→supervise |
| C2 config-preserve | H-01, H-02, BUG-07, PREC-01 | owned-region + refuse-on-unparseable | `read_json` para de coagir a `{}`; END-marker explícito; backup já existe |
| C3 provenance | H-04, LEDGER-02 | trust-boundary (SLSA "forge provenance") | relocar carimbo `host-real` p/ entrypoint do host + hash-chain |
| C4 fail-observable | BUG-01/02, PREC-03 | risk-typed + degrade-loud (dead-man's-switch) | breadcrumb `SUPERVISION_DEGRADED`; evidência não some silenciosa |
| C5 redaction | BUG-03, BUG-06 | redact-at-boundary, sink fail-closed | scrub simétrico command+path+reason numa função única |
| C6 reconcile | DEBT-01, F1 | inventory-anchored, nunca scan-and-guess | `.tes/materialized.json` (path+sha256); prune por set-difference |

---

- **Escopo:** agent hooks (`codex` / `claude` / `cursor`). Git hooks são outra camada, fora deste escopo.
- **Método:** cada afirmação confrontada linha-a-linha contra a fonte real. Fonte de verdade = `scripts/**` (NÃO `src/**` — `src/adapters/**` só tem markdown/plugin; não há código Python de hooks lá). `.tes/bin/**` é o mirror materializado no target instalado, não a fonte.
- **Data da varredura:** 2026-07-01.
- **Classificação:** `Platform` (toca hooks, instalador, materialização, MCP/Cortex runtime, contratos de host). Rigor de runtime obrigatório; ver `docs/architecture/PRETOOLUSE-CONTRACT.md`.
- **Elevação (2026-07-01):** relido em paralelo por lentes convergentes (re-verificação das 36 afirmações contra o código atual) e divergentes (8 lentes adversariais: cobertura-do-kernel, integridade-do-ledger, uninstall/idempotência, fail-open/closed, segurança/redação, cross-host, dry-run/materialização, completude-do-matcher). Cada finding novo passou por **refutação adversarial** (default = refutado; só sobrevive quem reproduz o cenário no código). Resultado: **16 findings sobreviveram**, 11 foram refutados. Os 4 HIGH e os 2 candidatos originais (F-03/F-06) foram **reproduzidos por execução** contra o `mantra_gate`/kernel/instalador reais (probes em `scratchpad/`, não versionados).

---

## 1. Mapa de fontes (fonte de verdade)

| Componente | Arquivo | Âncoras |
|---|---|---|
| Instalador de hooks + `hook` / `hook-health` | `scripts/tes_install.py` | `hook()` L3902; `hook_pretooluse` dispatch L3908; `hook_health()` L3974 |
| Kernel host-neutral (decisão) | `scripts/pretooluse_kernel.py` | `decide_pretooluse()` L194-287 |
| Sentinel anti-cry-wolf (sessão) | `scripts/pretooluse_session.py` | `coordinate_pretooluse_context()` L39 |
| Renderers por host | `scripts/tes_install.py` | `hook_pretooluse` L3789-3899; `pretooluse_renderer_trace` L2600-2618 |
| Cortex runtime (advisory) | `scripts/cortex_runtime.py` | `evaluate_runtime_event()` L384 |
| Ledger | `scripts/tes_install.py` | `record_hook_execution` L2752-2830 |
| Oráculos | `scripts/*.py` | ver §5 |

**Helpers entregues em `.tes/bin/`:** `HOOK_RUNTIME_HELPERS = ("cortex_runtime.py", "pretooluse_kernel.py", "pretooluse_session.py")` (`tes_install.py:52`); materializados por `install_hook_runtime_helpers` L838-855.

---

## 2. Matriz de auditoria — afirmação × fonte × veredito

Legenda veredito: ✅ CONFIRMADO · ⚠️ IMPRECISO (verdadeiro no núcleo, texto/termo errado) · ❌ INCORRETO · 🧩 CORROMPIDO NO INPUT (paste quebrado, conceito real)

Legenda consumidor (quem age sobre o output da funcionalidade — primário, com secundário entre `()`):
- **harness** = host (Claude/Codex/Cursor) ou instalador consome mecanicamente (matcher, exit codes, JSON de permissão, config, async rewake).
- **LLM** = o agente é o alvo do efeito (contexto injetado, supervisão, marker, Cortex advisory).
- **humano** = maintainer/operador lê ou decide (status de health, auditoria, release).
- **harness-oráculo** = um maintainer-gate/oráculo consome a prova programaticamente (ledger, provenance, ceiling) e o humano decide sobre a saída dele.

O sufixo `(H-0X)`/`(BUG-0X)`/`(PREC-0X)` na coluna Capacidade aponta o limite conhecido → finding em §3.

| # | Afirmação auditada | Fonte (`scripts/`) | Veredito | Capacidade técnica (— limite) | Consumidor |
|---|---|---|---|---|---|
| 1 | Hosts: `codex`, `claude`, `cursor` | `tes_install.py:5327` | ✅ | Enumera os 3 hosts adaptáveis | harness |
| 2 | Configs: `.codex/config.toml` / `.claude/settings.json` / `.cursor/hooks.json` | `tes_install.py:352,734,744` | ✅ | Escreve config de host — clobbera config malformada (H-02); uninstall engole bloco adjacente (H-01/BUG-07) | harness |
| 3 | Entrypoint comum `.tes/bin/tes_install.py hook --agent <host> --target ...` | `tes_install.py:382,408,428` | ✅ | Comando único que o host invoca por evento | harness |
| 4 | Helpers entregues: `cortex_runtime.py`, `pretooluse_kernel.py`, `pretooluse_session.py` | `tes_install.py:52` | ✅ | Materializa runtime em `.tes/bin` — sem poda de órfão (DEBT-01); import não-guardado (BUG-01); fora do drift manifest (F1, §4) | harness (→LLM em runtime) |
| 5 | Eventos Codex: `SessionStart`, `PreToolUse` | `HOOK_HEALTH_CONTRACTS` L2693; snippets L325/339 | ✅ | Registra 2 gatilhos no host Codex | harness |
| 6 | Eventos Claude: `SessionStart`, `PreToolUse` | `tes_install.py:734,799` | ✅ | Registra 2 gatilhos no host Claude | harness |
| 7 | Eventos Cursor: `sessionStart`, `beforeSubmitPrompt`, `preToolUse` | `tes_install.py:5327,2703-2704,3008` | ✅ | Registra 3 gatilhos no host Cursor | harness |
| 8 | SessionStart Claude: fase síncrona `--announce-start` + async `--rewake-on-complete` | `tes_install.py:383,394,396` | ✅ | Setup em 2 fases via async rewake do host | harness (→humano vê statusMessage) |
| 9 | SessionStart faz setup 1ª sessão via `.tes/postinstall.json` | `POSTINSTALL_PATH` L36 | ✅ | Sentinela de setup de primeira sessão | harness (→humano se needs_review) |
| 10 | PreToolUse projeta o Mantra Gate antes da execução | `pretooluse_contract_oracle.py:27` | ✅ | Projeta obrigação de gate pré-tool | LLM (→humano audita ledger) |
| 11 | **Matcher PreToolUse** = `Write\|Edit\|MultiEdit\|NotebookEditell\|shell\|apply_patch` | Real: `Write\|Edit\|MultiEdit\|NotebookEdit\|Bash\|Shell\|shell\|apply_patch` (`tes_install.py:46`) | ❌ ver DOC-01 | Gatilho que decide se o hook dispara — só nomes estruturados (base de H-03) | harness |
| 12 | **Pipeline** host cfg → adapter → kernel → `pretooluse_session.py` → renderer → ledger | `session.py` NÃO renderiza (`pretooluse_session.py:7-9`); renderer em `tes_install.py:3789` | ⚠️ ver DOC-02 | Cadeia decisão→sentinel→render→prova | harness+LLM+harness-oráculo (cadeia) |
| 13 | Kernel normaliza tool/payload/path/command, extrai paths de patch, classifica risco, detecta superfície governada, decisão host-neutral | `pretooluse_kernel.py:194-287,74` | ✅ | Decide host-neutral (risco+superfície) — cego a comando shell (H-03) | LLM (→harness renderiza) |
| 14 | Superfícies governadas: `AGENTS.md`, `CLAUDE.md`, `docs/adr/`, `docs/governance/`, `SKILL.md`, `.cursor/rules/` | `GOVERNED_ARTIFACT_HINTS` L18-25 — é `/SKILL.md` (com barra) | ⚠️→❌ ver BUG-08 | Define o alvo protegido — `SKILL.md` raiz escapa (BUG-08) | LLM (contrato) / harness-oráculo |
| 15 | Decisões: `allow`, `supervise`, `block`, `needs_discoverability` | `pretooluse_kernel.py:248,261,275,287` | ✅ | Vocabulário de 4 desfechos host-neutral | LLM (→harness projeta) |
| 16 | Rotina silenciosa: leitura/diagnóstico não-governado não emite ruído | `pretooluse_kernel.py:287` (`routine_non_governed`) | ✅ | Suprime ruído em ação não-governada | LLM |
| 17 | Supervisão: mutação em superfície governada executa mas injeta contexto/oráculo | `pretooluse_kernel.py:270-282` | ✅ | Injeta obrigação sem bloquear — ramo morto p/ shell (BUG-05) | LLM (→humano audita) |
| 18 | Bloqueio: ação proibida bloqueia antes da ferramenta | `pretooluse_kernel.py:243-255` | ✅ | Barra ação forbidden antes da tool | harness (executa deny) / LLM |
| 19 | Discoverability: tool nova / payload ambíguo com cara de mutação → `NEEDS_DISCOVERABILITY` | `pretooluse_kernel.py:256-269` | ✅ | Marca mutação ambígua p/ evidência — não dispara em shell governado (BUG-04) | LLM (→humano decide fixture) |
| 20 | Anti-cry-wolf: contexto aparece 1× por sessão/contexto; repetição suprime marcador | `pretooluse_session.py:58-65` (`anti_crywolf_repeated_context`) | ✅ 🧩 | Deduplica contexto por sessão — fail-open parcial + flag morta (PREC-03) | LLM |
| 21 | Render Claude: `hookSpecificOutput` / `permissionDecision=allow` / `additionalContext`; block exit 2 + stderr | `tes_install.py:3878-3892,3827`; contract `json_hookSpecificOutput_allow` L2613 | ✅ | Projeta decisão no protocolo Claude — reason de block vaza segredo (BUG-03) | harness (→LLM lê contexto) |
| 22 | Render Codex: contexto em stderr; block exit 2; allow silencioso | `tes_install.py:3893-3894,3827`; `stderr_context`/`silent_allow` L2615-2617 | ✅ | Projeta decisão no protocolo Codex — reason de block vaza segredo (BUG-03) | harness (→LLM/humano vê stderr) |
| 23 | Render Cursor: JSON `permission`/`continue`/`user_message`/`agent_message`; block `permission=deny` | `tes_install.py:3824-3826,3870-3877,3897`; contracts L2603-2617 | ✅ | Projeta decisão no protocolo Cursor — reason de block vaza segredo (BUG-03) | harness (→LLM lê agent_message) |
| 24 | Ledger: `.tes/runtime/hooks/executed.jsonl`; legado `.tes/hooks/executed.jsonl` | `tes_install.py:2689-2690` | ✅ | Persiste prova de execução — write fail-open silencioso (BUG-02); sem lock (LEDGER-02, §4) | harness-oráculo (→humano) |
| 25 | Ledger gitignored: `.tes/runtime/` + legado no exclude | `.gitignore:15`; `HOOK_RUNTIME_EXCLUDE_PATTERNS` L2692 | ✅ | Mantém prova fora do versionamento | harness |
| 26 | Proveniência `provenance=host-real` | `tes_install.py:2785` | ✅ | Tag que autoriza claim nativo — carimbada incondicionalmente, forjável (H-04) | harness-oráculo (→humano decide release) |
| 27 | Campos PreToolUse (agent, event, session, tool, path, cmd category, decision, risk, outcome, reason codes, classifier trace, renderer trace, marker/context state) | `record_hook_execution` L2752-2830; `classifier_trace` L225-235 | ✅ | Esquema de auditoria por linha — `path` gravado bruto (BUG-06) | harness-oráculo (→humano) |
| 28 | Sem vazamento bruto: comando classificado/redigido; auditoria por categorias/hashes | `redaction-safe command class` L2568 | ✅ | Redige o comando no ledger — só o comando; `path` e reason ficam de fora (BUG-06/BUG-03) | harness-oráculo (→humano) |
| 29 | Dedup: não colapsa batch Cursor legítimo; replay histórico não bloqueia ceiling salvo contradição v2 | `cursor_batch_rule`/`ceiling_noise_rule` L2912-2913 | ✅ | Tolera ruído sem falso-bloquear ceiling — janela de 50 linhas (PREC-02) | harness-oráculo |
| 30 | Health schema `health@2` | Real: `HOOK_HEALTH_SCHEMA_VERSION = "tes-hook-health@2"` L65 (legacy `@1` L66) | ⚠️ ver DOC-03 🧩 | Versiona o payload de health | harness-oráculo (→humano) |
| 31 | Estados por evento: `OBSERVED`, `CONFIGURED`, `NOT_CONFIGURED`, `STALE/UNEXPECTED` | `tes_install.py:3493,3495,3515,3505` | ✅ | Classifica observação por evento/host | harness-oráculo (→humano) |
| 32 | Status hook-health: `NOT_APPLIED`, `NEEDS_EVIDENCE`, `DEGRADED`, `PASS_WITH_FINDINGS`, `PASS` | `tes_install.py:3591-3602` | ✅ | Agrega estados num status de saúde | humano (→harness-gate exit code) |
| 33 | Floor vs ceiling: `PASS_BASIC` ≠ `PASS_CEILING`; ceiling exige evidência host-real por host | `hook_floor_status` L3160; `hook_ceiling_status` L3350; `pretooluse_ceiling_evidence` L3295 | ✅ | Separa piso de teto por evidência host-real | humano (→gate de certificação) |
| 34 | Sem cross-fill; host configurado sem ledger é `CONFIGURED_NOT_OBSERVED` | Termo em `canary_admission_oracle.py:64`; em `tes_install.py` = `configured_without_runtime_observation` L3499 / estado `CONFIGURED` | ⚠️ ver DOC-04 | Impede prova de um host valer p/ outro | harness-oráculo (→humano) |
| 35 | Cortex advisory: sugere contexto/alinhamento; sem escrita durável automática | `_evaluate_cortex_runtime` L3689; `cortex_runtime.evaluate_runtime_event` L384 | ✅ | Injeta recall de memória no contexto do hook | LLM |
| 36 | Oráculos: `hook-health`, `installed_certification_oracle`, `canary_admission_oracle`, `pretooluse_contract_oracle`, `hook_audit_prompt_oracle` | ver §6 | ✅ | Certificam a superfície (source e installed) | humano (→CI/harness-gate) |

### Fatos adicionais confirmados (não estavam na lista de entrada)

- **Dois schemas versionados distintos:** ledger row = `pretooluse_decision@2` (`tes_install.py:60`); health = `tes-hook-health@2` (L65). Não confundir.
- **Cobertura do kernel > matcher registrado:** `MUTATING_TOOLS` inclui `StrReplace` (`pretooluse_kernel.py:28`), mas `StrReplace` **não** está no matcher de host (`CLAUDE_PRETOOLUSE_MATCHER` L46). Fato estrutural real, mas **latente** (nenhum host atual emite `StrReplace`); o forbidden-block por texto de comando cobre o caso destrutivo. Não é bug ativo — anotar como decisão consciente (kernel mais amplo que matcher por design defensivo). Correlato de MATCHER-03 (§4).
- **Matchers SessionStart:** Claude `startup|resume|clear|compact` (L44); Codex `startup|resume` (L329).
- **Extração de patch body:** `PATCH_FILE_HEADER_RE = ^\*\*\* (?:Add|Update|Delete) File: (.+)$` (`pretooluse_kernel.py:17`); reason `patch_body_path_extracted` L219.
- **Superfície "operating mesh" separada:** `OPERATING_MESH_PRETOOLUSE_HINTS` (`tes_install.py:53-59`: `PROJECT-STATE.md`, `PROJECT-ROADMAP.md`, `EXECUTION-LINE.md`, `QUALITY-GATES.md`, `DECISIONS/`) é distinta das superfícies governadas do kernel.

---

## 3. Findings acionáveis (bugs / gaps / tech-debt)

> Esta seção precisa **zerar** antes de qualquer promoção a doc de projeto.
> Cada item: tipo · severidade · evidência (file:line) · cenário de falha · ação · status de verificação.
> `[REPRO]` = reproduzido por execução real neste ciclo. `[ADV✓]` = sobreviveu à refutação adversarial. Nenhum fix aplicado ainda — diagnóstico.

Placar de verificação: **16 findings sobreviveram** à refutação adversarial (4 HIGH · 8 MEDIUM · 4 LOW), 11 foram refutados (ver §4).

### Prioridade 0 — HIGH (perda de dado do usuário / bypass de governança / evidência forjada)

#### H-01 — [BUG · REPRO] Uninstall/refresh Codex deleta bloco `[[hooks.SessionStart]]` adjacente do próprio usuário
- **Arquivo:** `scripts/tes_install.py:561-583` (`_remove_codex_marked_block`).
- **Evidência:** a varredura de fim-de-bloco (L578-580) só trata um header como fronteira se ele **não** começar com `section_prefix`. Um `[[hooks.SessionStart]]` do usuário logo abaixo do bloco TES começa com o mesmo prefixo → é engolido.
- **Cenário (reproduzido):** config com bloco TES + bloco `[[hooks.SessionStart]]` do usuário adjacente → `_remove_codex_marked_block` retornou **lista vazia**: o hook do usuário foi silenciosamente deletado.
- **Ação:** delimitar o bloco TES ao **primeiro** header array-of-tables que não seja o filho `.hooks` imediato da tabela TES recém-aberta, em vez de consumir todo header sob o mesmo `section_prefix`. `[ADV✓]` HIGH.

#### H-02 — [BUG · REPRO] `read_json` engole config malformado e o install clobbera todo o `settings.json`/`hooks.json` do usuário
- **Arquivo:** `scripts/tes_install.py:129-136` (`read_json`), consumido por `install_claude_hook`/`install_claude_pretooluse_hook`/`install_cursor_hook`.
- **Evidência:** `read_json` captura `JSONDecodeError` e retorna `{}` (L134-135), indistinguível de "arquivo ausente". O install então escreve `json.dumps(data)` por cima.
- **Cenário (reproduzido):** `.claude/settings.json` com trailing-comma (`{"permissions":...,"env":...,}`) → `read_json` retorna `{}` → install escreve arquivo **só com o hook TES**; `permissions` e `env` do usuário **perdidos** no caminho vivo.
- **Ação:** não coagir config ilegível a `{}`. Em `JSONDecodeError`, abortar a escrita daquela superfície com erro claro (distinguir "ausente" de "presente mas inválido"). `[ADV✓]` HIGH.

#### H-03 — [BUG · REPRO] Escrita shell em superfície governada não extrai path → governança nunca engaja (allow silencioso)
- **Arquivo:** `scripts/pretooluse_kernel.py:148-161, 208, 214-216`.
- **Evidência dupla (mesmo ponto cego):** (1) `hook_tool_path` só lê `file_path`/`path`/`filePath` ou body `apply_patch` (`PATCH_FILE_HEADER_RE`, L17) → shell puro não expõe path → `paths=[]` → `governed=False`. (2) `_classify_pretooluse_risk` → `mantra_gate.classify_risk` casa **vocabulário de intenção** (`write/edit/delete`), não verbos shell (`echo/tee/sed/rm/cat`) nem nomes de superfície → `routine`. O docstring de `_classify_pretooluse_risk` (`tes_install.py:3648-3653`) admite combinar os dois "porque nenhum é confiável sozinho" — mas ambos são cegos a shell.
- **Cenário (reproduzido com `mantra_gate` real):** todos → `outcome=allow`:
  `echo x >> CLAUDE.md` · `sed -i AGENTS.md` · `rm docs/governance/RULE.md` · `cat > .cursor/rules/x.mdc`. A **mesma** edição via `Edit`/`apply_patch` dá `supervise`. Governança bypassada pelo vetor de mutação mais comum.
- **Ação:** extrair paths-alvo das formas shell comuns (`>`/`>>`, `tee [-a]`, `sed -i`, `cp`/`mv`) em `hook_tool_path*`, ou casar `GOVERNED_ARTIFACT_HINTS` contra o texto bruto do comando quando não houver path estruturado. Root fix compartilhado com H-04, BUG-04, BUG-05. `[ADV✓]` HIGH.

#### H-04 — [BUG · REPRO] `provenance="host-real"` é carimbado incondicionalmente → qualquer chamador forja evidência nativa
- **Arquivo:** `scripts/tes_install.py:2785` (`record_hook_execution`).
- **Evidência:** `record["provenance"] = "host-real"` em toda escrita, sem parâmetro para origem sintética. O oráculo de ceiling (L3287-3308) trata como fixture **apenas** rows com `provenance=="fixture"`; row sem tag lê como host-real.
- **Cenário:** uma invocação manual/scriptada (`echo '{...}' | python3 .tes/bin/tes_install.py hook --agent claude --target /real`) grava um row `pretooluse_decision@2` com `provenance="host-real"`. O ceiling passa a contar isso como execução nativa — o gate `PASS_CEILING` pode ser satisfeito sem host real.
- **Ação:** exigir argumento `provenance` explícito em `record_hook_execution`; passar `"host-real"` **só** dos entrypoints de host real (após `parse_hook_input` do stdin); self-test/sintético passa `"fixture"`. `[ADV✓]` HIGH (estrutural; não reproduzido por execução mas confirmado por leitura + rastreio do oráculo).

### Prioridade 1 — MEDIUM

#### BUG-01 — [BUG] Import top-level não-guardado de `pretooluse_kernel`/`pretooluse_session` derruba o hook inteiro se o helper faltar
- **Arquivo:** `scripts/tes_install.py:20-29`. `mantra_gate`/`cortex_runtime` têm import defensivo; estes dois **não**.
- **Cenário:** `.tes/bin/pretooluse_kernel.py` deletado/truncado por update falho → subprocess do hook sai com `ImportError` (exit 1, não 2). No Claude, exit≠2 é não-bloqueante → tool prossegue **sem** supervisão, sem sinal.
- **Ação:** envolver os dois imports no mesmo padrão defensivo e degradar `hook_pretooluse` para postura documentada em vez de crashar. `[ADV✓]`

#### BUG-02 — [BUG] Falha de escrita do ledger é engolida fail-open (`except OSError: pass`) → evidência host-real perdida sem sinal
- **Arquivo:** `scripts/tes_install.py:2829`.
- **Cenário:** `.tes/` read-only momentâneo / volume cheio / `mkdir` falha → decisão renderiza certo, mas nenhum row é gravado; o ceiling lê "sem evidência" como "hook nunca rodou".
- **Ação:** manter não-fatal, mas tornar a perda observável — breadcrumb em stderr e/ou contador durável `ledger_write_errors` que o oráculo lê. `[ADV✓]`

#### BUG-03 — [BUG] Reason de bloqueio forbidden ecoa o comando bruto (com segredo) para stderr do host / `agent_message` do Cursor
- **Arquivo:** `scripts/pretooluse_kernel.py:250-254` (interpola `{action}`).
- **Cenário:** `git push --force https://x-access-token:ghp_REAL@github.com/org/repo` casa forbidden e bloqueia; o `reason` reflete o comando **com o token** de volta pro host/stderr.
- **Ação:** não interpolar `action`/`command` bruto no `reason`; usar a saída redacted (`hook_command_category(command)` + `tool_name`), simétrico ao ledger. `[ADV✓]`

#### BUG-04 — [BUG] `needs_discoverability` para tool desconhecida-mutante nunca dispara em escrita shell governada
- **Arquivo:** `scripts/pretooluse_kernel.py:256, 217`. Ramo exige `governed=True`, que é falso para shell (H-03).
- **Cenário:** tool futura/host-específica (nome com `append/write/create`) muta `CLAUDE.md` via payload shell → `unknown_mutating=True` mas `governed=False` → `allow` em vez de `needs_discoverability`.
- **Ação:** mesmo root fix de H-03 (extrair path do shell); o ramo de discoverability passa a cobrir. `[ADV✓]`

#### BUG-05 — [BUG] Escalonamento `routine→material` e `supervise` estão mortos para escrita shell governada
- **Arquivo:** `scripts/pretooluse_kernel.py:223, 270`. Ambos exigem `governed=True`.
- **Cenário:** `cat payload > CLAUDE.md` → `classify_risk` vê "edit" e retorna `material`, mas `governed=False` (path não extraído do `>`), então o ramo `supervise` (L270) é pulado; mutação material do bootloader passa.
- **Ação:** root cause é H-03. Corrigir extração de path e L223/L270 engajam. `[ADV✓]`

#### BUG-06 — [GAP · REPRO] Path unredacted no ledger: segredo embutido em file_path é gravado em `executed.jsonl`
- **Arquivo:** `scripts/tes_install.py:2798-2799`. O `command` é redacted, mas `path` é gravado bruto.
- **Cenário:** `Write` para `/tmp/deploy/aws_AKIA…_creds.json` ou patch tocando `secrets/ghp_REAL.txt` → o path com segredo é persistido no ledger gitignored (mas legível em disco).
- **Ação:** política de redação em `path` simétrica ao `command` — categoria/basename-hash/flag de superfície governada, ou scrub de segredo. `[ADV✓]`

#### BUG-07 — [BUG · REPRO] Uninstall Codex remove qualquer linha `hooks = true` / `codex_hooks = true` independente da tabela
- **Arquivo:** `scripts/tes_install.py:661-664`. Remoção sem contexto de tabela (o install é table-scoped; o uninstall não).
- **Cenário:** usuário tem `hooks = true` sob outra tabela TOML não-relacionada → uninstall deleta a linha, mudando a semântica da tabela alheia.
- **Ação:** escopar a remoção do flag à tabela `[features]` (rastrear header ativo ao varrer), espelhando `replace_or_insert_toml_feature`. `[ADV✓]`

#### PREC-01 — [PRECISION] `replace_or_insert_toml_feature` pode inserir `[features]` no meio do arquivo, capturando keys de raiz
- **Arquivo:** `scripts/tes_install.py:270-284`.
- **Cenário:** `.codex/config.toml` começa com keys de raiz (`model = "x"`) antes de qualquer tabela → TES prepend `[features]` no topo → as keys de raiz passam a ser parseadas sob `[features]`, mudando o significado.
- **Ação:** inserir `[features]` no fim do arquivo (ou após o último run de keys de raiz). `[ADV✓]`

### Prioridade 2 — LOW

#### BUG-08 — [BUG · REPRO] `/SKILL.md` usa substring com barra inicial → `SKILL.md` na raiz não é governado (era F-03)
- **Arquivo:** `scripts/pretooluse_kernel.py:23, 214`.
- **Cenário (reproduzido):** `Edit` de `SKILL.md` na raiz (host passa filename nu, sem `./`) → `governed=False` → allow sem supervisão. `docs/x/SKILL.md`/`./SKILL.md`/`/abs/SKILL.md` casam; `MYSKILL.md`/`SKILLS.md` corretamente não.
- **Ação:** casar `SKILL.md` por segmento/basename: `path=='SKILL.md' or path.endswith('/SKILL.md') or path.split('/')[-1]=='SKILL.md'`. `[ADV✓]`

#### PREC-02 — [PRECISION] Dedupe só varre as últimas 50 linhas → decisão idêntica reemitida além da janela grava row duplicado
- **Arquivo:** `scripts/tes_install.py:2940`.
- **Cenário:** sessão longa com 60+ tool-calls; um Read idêntico recorre após a primeira ocorrência sair da cauda de 50 → dedupe erra e grava segundo row. (Não bloqueia ceiling — é ruído tolerado, mas polui contagens.)
- **Ação:** documentar a janela de 50 como recência-limitada intencional (e escopar oráculo/self-test a ela), ou indexar as dedupe-keys vistas por sessão. `[ADV✓]`

#### PREC-03 — [PRECISION] Sentinel anti-cry-wolf é fail-open em `OSError` mas **não** em não-`OSError`; flag `context_suppressed` é morta
- **Arquivo:** `scripts/pretooluse_session.py:69`.
- **Cenário:** sentinel com bytes não-UTF-8 (corrupção/writer concorrente) → `read_text(encoding='utf-8')` levanta `UnicodeDecodeError` (`ValueError`, não `OSError`) → escapa o guard e propaga por `hook_pretooluse`. Além disso, o ramo "já visto" nunca retorna `context_suppressed=True` — a supressão anunciada não acontece.
- **Ação:** decidir o contrato: se supressão-no-repeat é intencional, retornar `context_suppressed=True` (e zerar contexto) no ramo "já visto"; capturar `Exception` (não só `OSError`) na leitura. `[ADV✓]`

#### DEBT-01 — [TECH_DEBT] Sem limpeza de helper órfão quando `HOOK_RUNTIME_HELPERS` encolhe → helper aposentado fica vivo em `.tes/bin`
- **Arquivo:** `scripts/tes_install.py:838` (`install_hook_runtime_helpers` só copia, nunca poda).
- **Cenário:** pacote aposenta `pretooluse_session.py` (funde no kernel) → update copia o kernel novo mas o `.tes/bin/pretooluse_session.py` velho persiste; um `import pretooluse_session` remanescente ou a health probe (L3382) pode ler o helper morto.
- **Ação:** reconciliar `.tes/bin` contra `HOOK_RUNTIME_HELPERS` no install/update — remover helpers de hook (e `__pycache__`) fora do tuple atual, com guarda. `[ADV✓]`

### Correções de descrição (input corrompido, código correto — herdadas do 1º ciclo)

| ID | Item | Real | Ação |
|---|---|---|---|
| DOC-01 | Matcher `...NotebookEditell|shell|apply_patch` | `Write\|Edit\|MultiEdit\|NotebookEdit\|Bash\|Shell\|shell\|apply_patch` (`tes_install.py:46`) | corrigir material derivado; sem mudança de código |
| DOC-02 | `pretooluse_session.py` como renderer | session = só sentinel (`L7-9`); renderer em `hook_pretooluse` (`tes_install.py:3789-3899`) | gravar pipeline correto na destilação; comentário-âncora opcional |
| DOC-03 | "Health schemaalth@2" | `tes-hook-health@2` (`L65`) | corrigir material derivado |
| DOC-04 | `CONFIGURED_NOT_OBSERVED` no health do instalador | termo é do `canary_admission_oracle.py:64`; no instalador = finding `configured_without_runtime_observation` (`L3499`) / estado `CONFIGURED` | separar camadas na destilação; alinhamento de nome = decisão de owner |

---

## 4. Refutados (não são bugs de runtime — registro honesto)

11 candidatos foram derrubados na refutação adversarial. Três carregam **fato estrutural verdadeiro** que vale como hardening-gap/nota, mesmo sem cenário reproduzível:

- **F1 — `HELPER_FILES` (update) omite os helpers de hook.** Confirmado: `tes_update.py:42-77` lista `cortex_runtime.py`/`mantra_gate.py`/… mas **não** `pretooluse_kernel.py`/`pretooluse_session.py` — eles nunca entram na comparação sha256 de drift. Refutado como HIGH porque um adopter *atrás de versão* é mandado atualizar (o install re-materializa os helpers). **Blind-spot residual real:** content-drift **na mesma versão** (edição sem bump) não é detectado — mas `release_identity` proíbe mudar delivered behavior sem bump. Registrar como nota de robustez, não bug.
- **LEDGER-02 — append ao ledger sem lock.** A ausência de `flock` é real; mas duplicata concorrente vira `duplicate_runtime_hook_records` severidade *warning* → `PASS_WITH_FINDINGS` (não-bloqueante, por design: `ceiling_noise_rule`), e o torn-line não reproduz em ext4/xfs/APFS (append single-`write()` atômico). Hardening-gap latente, não bug.
- **MATCHER-03 — `bash` minúsculo escaparia o matcher.** `git push --force` é pego pelo classifier de **texto** (`FORBIDDEN_PATTERNS`) independente do nome da tool; nenhum host atual emite `bash` minúsculo. Latente/hipotético.

Refutados sem fato residual relevante: **FO-2** (exceção não-`OSError` no block path — premissa correta mas sem input reproduzível), **LEDGER-05** (nada não-serializável chega ao `json.dumps`), **PTU-01/02/03/04/05** (contratos de renderer por host estão corretos: Cursor snake_case bate a doc real; `continue:true`, exit-2, stderr-Codex conferem).

---

## 5. Itens que passaram limpos (sem finding)

Núcleo conceitual da superfície **correto e verificado** (matriz §2, linhas ✅): hosts, configs, eventos por host, quatro decisões do kernel no caminho estruturado (`Edit`/`apply_patch`), contratos de renderer por host, ledger + proveniência, gitignore, estados/status de health, floor-vs-ceiling, anti-cry-wolf, dedup de batch Cursor, Cortex advisory sem escrita durável, idempotência do install Cursor, materialização a partir da fonte de verdade (`source_helper_path`), forbidden-block por texto de comando. Os buracos estão nos **vetores não-estruturados** (shell) e nas **superfícies de config do usuário** (uninstall/read_json), não no caminho feliz.

---

## 6. Oráculos de verificação (para o loop de fix)

Rodar o oráculo correspondente ao surface após cada fix. Nenhum é build-only.

| Oráculo | Arquivo | Cobre |
|---|---|---|
| `tes_install.py hook-health` | `scripts/tes_install.py:3974` | estados por evento, status floor/ceiling, schema `@2` |
| `installed_certification_oracle.py` | L1103; `hook_runtime_health` L295-339 | ledger runtime + legado em target real |
| `canary_admission_oracle.py` | L455 | `CONFIGURED_NOT_OBSERVED`, `NATIVE_PASS`, classe por host |
| `pretooluse_contract_oracle.py` | L141 | contrato host-neutral (`docs/architecture/PRETOOLUSE-CONTRACT.md`) |
| `hook_audit_prompt_oracle.py` | L525 | prompt de auditoria, packaging `.tes/bin/*`, `tes-hook-health@2` |
| `attach_health_oracle.py` | L440 | superfície de saúde + detecção de duplicados |
| `install_smoke.py` | L745+ | install/uninstall + resíduo de ledger em target |

**Mapa finding → oráculo/red-capable** (cada fix precisa de um teste que fica vermelho ANTES):

| Finding | Red-capable a escrever | Oráculo de regressão |
|---|---|---|
| H-01, H-03, BUG-04, BUG-05, BUG-08 | fixture no kernel: shell/`SKILL.md`-raiz/bloco-adjacente → asserção de `outcome`/preservação | `pretooluse_contract_oracle.py` + probe do kernel |
| H-02, BUG-07, PREC-01 | fixture de config do usuário malformado/adjacente → asserção de preservação | `install_smoke.py` |
| H-04 | row sintético vs host-real → asserção de que ceiling não conta sintético | `installed_certification_oracle.py`, `attach_health_oracle.py` |
| BUG-01, BUG-02, PREC-03 | helper ausente / `.tes` read-only / sentinel não-UTF-8 → asserção de degradação sinalizada | `hook-health`, `install_smoke.py` |
| BUG-03, BUG-06 | comando/path com segredo → asserção de que ledger/reason não vazam | `pretooluse_contract_oracle.py` |
| DEBT-01, F1(nota) | helper aposentado / drift same-version → asserção de poda/detecção | `install_smoke.py`, `tes_update.py` manifest |

**Regra de camada:** oráculos de source/package rodam neste repo; oráculos de installed-target rodam contra fixture de target real (não a raiz deste repo). Ver `<layer_boundary>` no bootloader.

---

## 7. Caminho de fix maduro (como projetos que já resolveram isto resolvem)

> Esta seção é o **GPS**: para cada uma das 6 classes de finding, o padrão maduro
> nomeado, como projetos de referência o implementam, o que adotar no TES, e o
> aterrissamento cirúrgico no nosso código. Triangulado por 3 fontes independentes
> — **mem0** e **graphify** (lidos localmente em `tmp/`), e **pesquisa web** de
> specs/projetos de referência (6/6 classes verificadas como `grounded`, confiança
> HIGH, por um verificador cético que corrigiu overstatements). Onde as 3 fontes
> convergem, o princípio é robusto; onde divergem, registro o trade-off.

### Princípio unificador (a tese)

Os 16 findings são o mesmo meta-problema: **o hook confia em fronteiras que não controla** — o payload shell, o config do usuário, o próprio chamador do ledger, a disponibilidade do helper. A cura, que as 3 fontes ensinam de formas diferentes, é a mesma: **mova a confiança da fronteira para o núcleo** — *parse defensivo · prove-don't-trust · degrade-loud · reconcile por manifesto*. As 3 fontes convergem: o Claude Code (nosso próprio host) faz parse conservador de Bash e recusa arg-matching frágil; graphify valida proveniência por schema e recusa sobrescrita de perda não-explicada; mem0 torna a autoria imutável e o timestamp server-side.

---

### C1 — Extração de intenção de comando não-estruturado → `H-03, BUG-04, BUG-05, BUG-08`

**Padrão maduro:** *parse-then-evaluate, nunca substring; fail-closed no ambíguo, com backstop de efeito.* Trata a string shell como um programa não-confiável: parseia em AST (split em `&&`/`||`/`;`/`|`/`&`/newline, strip de `VAR=val` e wrappers `timeout/nice/nohup/stdbuf/xargs`, desce em `$()`/backticks), extrai o path de cada comando simples dos **operandos de argumento E de redirecionamento**, e roda política deny-first sobre isso.

**Quem faz e como:**
- **Claude Code (o próprio host)** — documenta *exatamente* o nosso H-03: Bash chega como string crua sem pré-extração de path; o matcher deles faz o parse acima e **recusa** `Bash(command:rm *)` como bypassável, emitindo warning. Confirma nossa causa-raiz e dá a semântica de decomposição a espelhar.
- **graphify** — `extract_markdown` (`extract.py:11813`) é o análogo direto: parse line-by-line com regex, `errors="replace"`, pula fenced blocks, e o *indirect-dispatch guard* (`extract.py:3088-3097`) "não manufatura edge de token ambíguo" — prefere não emitir a emitir errado.
- **OPA/Conftest** (política sobre argv parseado, não string) · **Falco** (backstop no syscall) · **bashlex / tree-sitter-bash** (o parser).

**Adotar no TES:** quando `tool_name==Bash`, parsear `command` (espelhando a decomposição do Claude Code para casar o host); extrair paths de operandos de arg **e** de redirect (`>>`/`>`, `sed -i`, `cp`/`mv` dest, positional de `rm`); casar contra `GOVERNED_ARTIFACT_HINTS`; **fail-closed** — comando ingovernável/ambíguo que plausivelmente toca superfície governada vira `supervise`/`needs_discoverability`, nunca `allow` silencioso (é o defeito exato de H-03/BUG-04). Não hardcodar lista literal de comandos (`<regression_guard>` — seed de regressão); dirigir o match pelo set de paths governados + AST.
- **Aterrissagem:** `pretooluse_kernel.py:hook_tool_path_source` (L164) + novo extrator shell; fixture red-capable com as 3 formas + variantes ofuscadas (`FOO=bar sed -i`, `$(echo AGENTS.md)`, `>>` vs `>`).
- **Trade-off honesto:** parser não resolve indireção runtime (`$VAR`, `eval`, interpretador que abre arquivo). Por isso o padrão é defense-in-depth: o hook cobre o comum e o host permission-layer/sandbox é o backstop. Documentar o limite, não fingir cobertura total.

---

### C2 — Preservação de config do usuário → `H-01, H-02, BUG-07, PREC-01`

**Padrão maduro:** *owned-region editing + fail-closed load.* Nunca load-then-overwrite do arquivo inteiro: (a) parser round-trip que preserva keys/comentários desconhecidos; (b) escrita confinada a um bloco delimitado por marcadores `BEGIN/END` idempotentes; (c) **refuse-on-unparseable** (aborta com diagnóstico em vez de coagir a `{}`); (d) commit atômico (temp+rename) após backup timestamped.

**Quem faz e como:** **Ansible `blockinfile`** (edita só entre `# BEGIN/END ANSIBLE MANAGED BLOCK`) · **tomlkit** (round-trip + `ParseError` fail-closed) · **ruamel.yaml** · **.npmrc/ini** (merge de key, não overwrite).

**Adotar no TES:**
- **H-01/H-02/BUG-07:** `read_json` (`tes_install.py:129-136`) deve **parar de coagir** — `raise`/abortar no parse-error, nunca `{}`. Em arquivo válido, deep-merge só das keys TES, preservando `permissions`/`env`/hooks do usuário; nunca emitir documento TES-only.
- **UNINST-1 (Codex):** adotar o contrato de managed-block do Ansible — **END-marker explícito** (`# TES END …`), não a heurística de `section_prefix` que engole o bloco adjacente do usuário (`_remove_codex_marked_block:578-580`).
- **graphify converge:** o *shrink-guard* (`watch.py:351-406`) recusa sobrescrever quando o novo estado tem menos dados sem deleção declarada — mesmo invariante: *não clobber sem explicação, recuse*.
- **Aterrissagem barata:** o **backup já existe** (`write_text_if_changed:296` faz `.bak-{stamp}`) e falta só o **guard de parse** + o **END-marker**. Não precisamos de `tomlkit` (dep externa que o TES evita) se refusamos escrever no unparseable — não há formato a preservar quando recusamos.
- **Trade-off:** refuse-on-unparseable bloqueia o install até o usuário corrigir; backup-then-write prossegue mas empurra o recovery para um `.bak` que o usuário pode nunca achar. Maduro faz **os dois**: recusa *coagir*, mas sempre deixa `.bak`.

---

### C3 — Proveniência / anti-forja de evidência → `H-04, LEDGER-02`

**Padrão maduro:** *trust-boundary provenance — o escritor não pode auto-assinar sua própria origem.* SLSA chama o nosso bug pelo nome: *"Forge values of the provenance"*. O carimbo de origem é gerado por um plano de controle que o escritor do payload não alcança (isolamento de chave e/ou identidade ambiente OIDC/SPIFFE). "Provenance que o escritor carimba em si mesmo é, por definição, inútil."

**Quem faz e como:**
- **SLSA v1.0 / in-toto** — nomeia e ataca exatamente esta ameaça.
- **Sigstore (Fulcio+Rekor), Trillian/transparency.dev, `nono`** — logs tamper-evident por **hash-chain** (`chain[i]=H(chain[i-1] ‖ entry[i])`).
- **graphify RESOLVE o que mem0 não resolve** — proveniência é campo **obrigatório validado por schema** (`REQUIRED_NODE_FIELDS`, `validate.py:6`; `assert_valid` levanta `ValueError`), com origem binária `_origin:"ast"` (real) vs LLM (inferido) e a regra **"AST always wins; não-AST colidindo é ghost, removido"** (`build.py:433,486`).
- **mem0** — `actor_id` **imutável pós-criação** (`main.py:1909-1911`) e timestamp **server-side** (`main.py:1823`). Mas mem0 *não* distingue real vs sintético e seu MD5 é só dedup — nem mem0 fecha nosso H-04 sozinho.

**Adotar no TES (3 camadas, da barata à forte):**
1. **Relocar o carimbo** (barato, fecha 80%): remover o literal incondicional `provenance="host-real"` (`tes_install.py:2785`); só o entrypoint que o host spawna escreve `host-real`; todo outro caminho escreve `unattested`/`self-reported`. O gate `PASS_CEILING` exige `host-real` **+ prova**, não a string nua. Aterrissar em `record_hook_execution` recebendo `provenance` explícito, derivado da presença de sinais que o chamador manual não tem (`tool_use_id`/`transcript_path`/`CLAUDE_PROJECT_DIR`).
2. **Hash-chain do ledger** (médio): encadear entries (`nono`/Trillian) — a infra já existe (`event_ledger.sha256_text`). Torna reescrita histórica detectável, fechando o resíduo de LEDGER-02.
3. **Assinar com chave isolada** (forte, se houver fronteira de processo real): honestidade do trade-off — no contexto local, host e chamador rodam como o **mesmo usuário**; sem uma fronteira de privilégio genuína, a chave não é inalcançável. Por isso a camada 1+2 é o teto realista local; a camada 3 fica documentada como aspiração, não promessa.

---

### C4 — Fail-open vs fail-closed observável → `BUG-01, BUG-02, PREC-03`

**Padrão maduro:** *risk-typed failure com degradação obrigatoriamente observável ("fail loud, not silent").* Não há política global única: controle de segurança falha **fechado**; controle de disponibilidade/telemetria falha **aberto** — mas **todo** caminho degradado emite um breadcrumb detectável por máquina, para que *"o gate não rodou"* nunca seja indistinguível de *"o gate rodou e passou"* (dead-man's-switch).

**Quem faz e como:**
- **K8s ValidatingAdmissionWebhook** (`failurePolicy: Fail` fail-closed com timeout) · **OPA/Gatekeeper** (`Ignore` fail-open, com o **audit subsystem como backstop compensatório** documentado — a lição do deadlock: um webhook fail-closed cujos pods morrem trava o cluster).
- **mem0** — a **assimetria consciente**: vector store degrada fail-open por item (`main.py:963-975`); a trilha SQLite é transacional + lock + rollback + **raise** (`storage.py`). *Dado reconstruível degrada; evidência de auditoria não.*
- **graphify** — degrada com `error` **estruturado** (`{nodes:[],edges:[],error:causa}`, `extract.py:3058-3078`), nunca `except: pass` mudo; marca o único ponto silencioso deles (`watch.py:686`) como débito.

**Adotar no TES:** nosso hook é controle de supervisão, mas o contrato do host (Claude trata não-2 como não-bloqueante) o força a ser estruturalmente fail-open — então, pela lição do Gatekeeper, **não** hard-fail o host; **torne cada degradação observável**:
- **BUG-01:** envolver o import top-level (`tes_install.py:20-29`) no mesmo try/except defensivo de `mantra_gate`/`cortex_runtime`; na falha, exit fail-open MAS emitir breadcrumb `SUPERVISION_DEGRADED: <reason>` em stderr — "hook crashou" distinguível de "hook passou".
- **BUG-02:** o `except OSError: pass` do ledger (`L2829`) — seguindo a assimetria do mem0, evidência não pode sumir silenciosa: breadcrumb em stderr + contador durável `ledger_write_errors` que o oráculo lê.
- **PREC-03:** o sentinel captura só `OSError` (`session.py:69`); capturar `Exception` (o `UnicodeDecodeError` de sentinel corrompido escapa) e resolver o `context_suppressed` morto.
- **PREC-02** (fora das 6 classes — ajuste local): a janela de dedupe de 50 linhas (`tes_install.py:2940`) não é problema de fronteira, é uma escolha de recência não-declarada. Alinha-se ao princípio "observável": ou **documentar** a janela como recência-limitada intencional (e escopar o oráculo a ela), ou indexar as dedupe-keys vistas por sessão. Decisão consciente, não fix estrutural.

---

### C5 — Redação de segredo em telemetria → `BUG-03, BUG-06`

**Padrão maduro:** *redact-at-the-boundary — sink allowlist-first (fail-closed) + substituição categoria+hash-não-reversível.* Nunca emite/persiste valor bruto; o próprio sink (não cada call-site) aplica duas fases: (1) key-phase (só campos permitidos sobrevivem); (2) value-phase (regex de segredo + entropia de Shannon + strip de userinfo de URL), substituindo por `categoria + prefixo de hash`.

**Quem faz e como:** **OpenTelemetry Collector redaction processor** (allowlist-first fail-closed, `hash_function` HMAC recomendado, `redaction.masked.count`) · **Databricks** `REDACTED_CREDENTIALS(hash_prefix)` · **Go `net/url` `URL.Redacted()`** · **Datadog SDS** · **gitleaks/TruffleHog/detect-secrets** (as regexes) · **mem0** (denylist em camadas `_is_sensitive_field`, `main.py:220-233` — mas só na telemetria/config, não no payload).

**Adotar no TES:**
- **BUG-03:** o `reason` de block (`pretooluse_kernel.py:250-254`) não pode interpolar `action`/`command` bruto — usar `hook_command_category` + a regra que disparou. Aplicar o scrub **em ambos** os renderers (stderr Claude/Codex E `agent_message` Cursor), no renderer host-específico (o `PRETOOLUSE-CONTRACT` proíbe flatten).
- **BUG-06:** o ledger é sink **fail-closed** — `path`/args não vão brutos; scrub simétrico ao do `command`, substituindo segmento de alta entropia por `categoria + hash-prefix`, com campo tipo `redaction.masked.count`.
- Centralizar em **uma** função de redação de write (como o processor único do OTel), não scrub por call-site. Oráculo red-capable: planta token conhecido no comando **e** no path, assere que não aparece em stderr/`agent_message`/`executed.jsonl`, mas a categoria da tool sim.
- **Correção do verificador (registrar):** `URL.Redacted()` sozinho só tira userinfo de URL, **não** token em segmento de path — é o cenário exato de BUG-06; o scrub por entropia+regex é o que fecha. E hash de segmento de baixa entropia é brute-forçável → usar HMAC-com-chave ou **dropar** (não hashear) segmentos de baixa entropia.

---

### C6 — Reconciliação de estado materializado → `DEBT-01, F1`

**Padrão maduro:** *inventory-anchored declarative reconciliation.* A cada apply, renderiza o set desejado da fonte, grava um **inventário autoritativo** do que materializou (identidade + digest sha256 por membro), e reconcilia: (a) **PRUNE** = `materializado − desejado` (mata órfão); (b) **DRIFT** = digest gravado vs digest em disco (pega content-drift de mesma identidade). **Regra dura, aprendida por todos:** *nunca* descobrir o set gerenciado por scan/glob heurístico — isso vaza órfão e super-deleta.

**Quem faz e como:** **Flux CD** (`.status.inventory`, prune = inventário anterior − novo; delete gated por `prune:` não-vazio) · **kubectl ApplySet/KEP-3659** (abandonou `--prune-allowlist` por scan justamente porque vazava/super-deletava) · **Terraform** (state = inventário; in-state-not-in-config = destroy; attribute mismatch = drift) · **dpkg** (manifesto `.list` por pacote, set-difference no upgrade) · **graphify** (replace-per-source `build.py:788`, prune de órfão por `source_file` sumido `watch.py:608-627`, edge ownership evita phantom).

**Adotar no TES:** **um manifesto content-addressed fecha os dois findings.**
- **DEBT-01:** o installer/updater persiste `.tes/materialized.json` (path + sha256 por helper). No update: PRUNE = `manifesto − desejado`, deletando o helper aposentado de `.tes/bin`. **Não** scanear `.tes/bin` e adivinhar por nome (o modo de falha do ApplySet). Gate do delete atrás de manifesto presente e não-vazio (espelha Flux `allowEmpty:false` / ArgoCD prune-off), pra um bug de render não esvaziar o bin.
- **F1:** o mesmo manifesto guarda sha256 de **todo** helper — incluindo os dois de PreToolUse que hoje estão fora do drift manifest (`tes_update.py:HELPER_FILES`); o oráculo de drift compara digest gravado vs em disco, pegando content-drift de mesma versão. `sha256_file` já existe (`tes_install.py:125`).
- **Trade-off:** inventário é artefato persistido que precisa ser escrito transacionalmente com a materialização e pode driftar — por isso o prune fica atrás de opt-in/gate, com o manifesto não-vazio como trava.

---

## 8. Critério de fechamento (quando promover a doc de projeto)

1. **HIGH primeiro** (H-01…H-04): red-capable vermelho antes, fix, oráculo verde. H-01/H-02 são perda de config do usuário na superfície instalada — `Platform`, exigem bump de identidade (delivered behavior) e correlação (`MAINTAINER-CORRELATION-RULE.md`).
2. MEDIUM (BUG-01…07, PREC-01): idem, red-capable + fix + oráculo. BUG-03/03/04/05/08 compartilham o root fix de extração de path shell — um fix, vários findings fecham.
3. LOW (PREC-02/03, DEBT-01) e as notas de refutados (F1, LEDGER-02, StrReplace): decisão consciente registrada — corrigir ou aceitar-e-anotar; não deixar implícito.
4. DOC-01…04 corrigidos em qualquer material derivado (erros de input/nomenclatura, não de código).
5. `pretooluse_contract_oracle.py` + `hook-health` + `install_smoke.py` verdes.
6. Decisão de release-identity registrada para todo fix que toque delivered behavior (kernel, instalador, renderer, ledger são todos delivered).

Só então: destilar a matriz §2 em `docs/architecture/` (ou surface canônica adequada) e **remover** este working doc ou movê-lo para `docs/roadmap/archive/`.

---

## 9. Fontes de pesquisa (rastreabilidade do §7)

O caminho de fix foi triangulado por 3 fontes independentes; cada padrão do §7 é `grounded` (verificado por um agente cético que corrigiu overstatements — ex.: `URL.Redacted()` insuficiente sozinho; dpkg não auto-remove conffiles).

**Locais (lidos em `tmp/`, não versionados):**
- **mem0** (`tmp/project-mem0/mem0/`) — `actor_id` imutável (`main.py:1909-1911`), timestamp server-side, trilha append-only+soft-delete (`storage.py`), denylist scrubber (`main.py:220-233`), assimetria fail-open (`main.py:963-975` vs `storage.py`).
- **graphify** (`tmp/graphify/`) — proveniência obrigatória por schema (`validate.py:6`), `_origin` real vs inferido + "AST always wins" (`build.py:433,486`), `extract_markdown` parse defensivo (`extract.py:11813`), replace-per-source + prune (`build.py:788`, `watch.py:608-627`), shrink-guard (`watch.py:351-406`), `error` estruturado nunca `except:pass` (`extract.py:3058-3078`).

**Web (specs/projetos de referência, verificados contra fonte primária):**
- C1: Claude Code hooks/permissions docs · OPA/Conftest · Falco · bashlex/tree-sitter-bash.
- C2: Ansible `blockinfile` · tomlkit · ruamel.yaml · npm ini.
- C3: SLSA v1.0 threats ("Forge values of the provenance") · Sigstore (Fulcio/Rekor) · Trillian/transparency.dev · `nono`.
- C4: K8s ValidatingAdmissionWebhook `failurePolicy` · OPA/Gatekeeper audit-backstop · AuthZed · dead-man's-switch.
- C5: OpenTelemetry redaction processor · Databricks credential redaction · Go `net/url` `URL.Redacted()` · Datadog SDS · gitleaks/TruffleHog/detect-secrets.
- C6: Flux CD `.status.inventory` · kubectl ApplySet/KEP-3659 · Terraform state drift · dpkg `.list`.

> Nota de método: onde as 3 fontes **convergem** (ex.: C1 parse conservador; C2 refuse-clobber; C4 degrade-loud), o princípio é robusto e o fix é seguro de priorizar. Onde uma fonte madura **não resolve** (mem0 não distingue real vs sintético em C3; nenhuma resolve indireção runtime em C1), o limite está registrado — não prometemos mais do que o padrão entrega.
