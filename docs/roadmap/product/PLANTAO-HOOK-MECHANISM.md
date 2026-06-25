---
tds_id: roadmap.plantao_hook_mechanism
tds_class: roadmap
status: proposed
consumer: maintainers, installer authors, and adapter-materialization reviewers
source_of_truth: false
evidence_level: L2
tver: 0.1.0
---

# Mecanismo de Plantão — Hook Pré-Ação e Gatilho por Intenção

> Contrato de roadmap (maintainer). Mapeia a forma portátil provada em produção no estudo o projeto-referência para a próxima fatia de plantão pré-sciente do Mantra-Gate. Não é fonte de verdade de comportamento entregue; é o desenho que será absorvido em `scripts/tes_install.py` e `scripts/materialize_adapter.py` quando uma fatia for autorizada. Toda transferência aqui é **forma, não conteúdo** (ADR 0005 asset-transfer) e cada hook proposto carrega sua própria falsificação (ADR 0006, linha 27: *"Affirmation is never credit, not even self-affirmation"*).

## 1. O que TES já tem vs. o GAP

**Estado atual (Birth, ~6/8 SPECs).** O detector senior-manager do Mantra-Gate existe e está fiado **só no tempo de commit** — reativo. A instalação de hooks é mínima e passiva:

- `tes_install.py:467` — Claude recebe **apenas** `SessionStart` (`ensure_hook_group(data, "SessionStart", CLAUDE_SESSIONSTART_MATCHER, entry)`).
- `tes_install.py:205-208` — Codex recebe **apenas** `[[hooks.SessionStart]]` via reescrita de TOML.
- `tes_install.py:481` — Cursor recebe `sessionStart` e `beforeSubmitPrompt`, mas `beforeSubmitPrompt` hoje só anexa o mesmo `hook_entry("cursor")` de aviso/setup; **não é um gate de intenção** — é o aviso de sessão duplicado num segundo evento.
- A lógica inversa de remoção (`remove_tes_claude_sessionstart_hooks` em `:465`, `:326`, `:344`; Codex em `:371-408`) sabe casar/limpar **somente** blocos `SessionStart`/`hooks.SessionStart`.

**O gap.** Não existe nenhuma camada **pré-ação** nem **por intenção**:

1. **Pré-ação (`PreToolUse`)** — nenhum hook intercepta `Write|Edit|MultiEdit` ou `Bash` antes da execução para bloquear/reescrever/injetar contexto. O detector senior-manager só fala depois, no commit gate. O gerente sênior chega tarde demais para impedir o atalho; ele só audita o estrago.
2. **Por intenção (`UserPromptSubmit` / `beforeSubmitPrompt` real)** — nenhum hook lê a mensagem do usuário para detectar sinais de risco/dúvida (erro, workaround, resume) e plantar uma rubrica de decisão. O `beforeSubmitPrompt` instalado hoje é facade de plantão: não detecta intenção, não decide nada.

O plantão pré-sciente — o gerente sênior que já está de prontidão antes do ato, não o auditor que aparece no commit — **não existe**. O o projeto-referência já roda esse plantão em produção; este contrato transfere a **forma** dele.

## 2. Os 4 mecanismos portáveis (forma, provados no o projeto-referência)

A regra de leitura: cada item abaixo é uma **forma** (exit code, schema JSON, regex-de-shape, ordem de fluxo). O conteúdo do o projeto-referência (nomes de tool MCP, scripts, env vars, schema de memória) **não atravessa** — ver §6.

### Mecanismo A — O contrato de hook (exit-2 bloqueia / `updatedInput` reescreve / `additionalContext` injeta / matcher economiza)

Forma única, três efeitos, todos no evento `PreToolUse`:

- **`exit 2` bloqueia, stderr vira feedback ao agente.** O contrato de hook pré-ação: exit 0 = allow the tool call; exit 2 = block the tool call (o stderr é mostrado ao agente como feedback). Entrada por stdin JSON (`tool_name`, `tool_input`); o guarda decide o bloqueio por pattern-match no path.
- **`updatedInput` reescreve os parâmetros mid-flight.** Um hook pré-ação emite `{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"allow","updatedInput":$updated}}` — a chamada do agente continua, mas com os parâmetros substituídos pelo hook.
- **`additionalContext` injeta contexto.** O mesmo contrato de saída declara o campo `additionalContext`, disponível para injetar ADR/SPEC/constraint antes da execução do tool.
- **Matcher economiza.** O campo `matcher` é o plano de controle: regex OU pipe de nomes de tool (`Write|Edit|MultiEdit`, `Read`, `Bash`). O matcher é **vocabulário transferível** (nome de tool do host); o comando ligado a ele é **host-privado**.

**Mapeamento ao gerente sênior.** O gerente vê o ato antes de ele acontecer: `exit 2` = *"esse atalho não passa"* (bloqueia Write/Edit em artefato governado, devolve o motivo legível por stderr); `updatedInput` = *"deixo passar, mas com o default de identidade/metadata corrigido"*; `additionalContext` = *"antes de você editar, leia este SPEC/ADR"*. O matcher é a escala de plantão: o gerente só é chamado para as tools que importam, não para todo `Read`.

### Mecanismo B — Rubrica de decisão (não decide pelo agente)

- A forma do hook de intenção: em vez de pré-executar a ação pelo agente, ele **injeta uma rubrica de decisão** que diz ao agente quando e como agir por conta própria. O princípio é explícito — o agente tem mais contexto que o script; deixe o agente decidir.
- O hook detecta sinais e **emite as detecções como contexto**; **nunca dispara a ação ele mesmo**. A rubrica é uma frase única por sessão.

**Mapeamento ao gerente sênior.** O plantonista não executa o trabalho; ele coloca uma régua na mesa: *"quando aparecer X, considere Y."* O agente, que tem mais contexto que o regex, decide. Isso impede o gate de virar um robô que rejeita por palavra solta — preserva o julgamento, planta a régua.

### Mecanismo C — Intenção por regex (sem API) + dedup anti-cry-wolf

- **Intenção por regex** — detecção de intenção no prompt do usuário por classes de sinal, sem API e sem DB: sinal-de-erro (stack traces como `Traceback`/`panic:`/`fatal:`, ou 2+ keywords de erro), file-paths por extensão, sinal-de-retomada e sinal-de-lembrança. Cada classe é uma flag booleana derivada por regex sobre o texto.
- **Anti-cry-wolf por camadas** — gate de comprimento (sai silencioso se o prompt < 20 chars); flag de dedup por cache de sessão (lida no início, escrita ao fim — a rubrica completa dispara **uma vez por sessão**); nudge periódico por contagem de mensagem (a cada N-ésima) e captura sobreposta em outro intervalo.

**Mapeamento ao gerente sênior.** As palavras de risco (`workaround`, `shim`, verbo-de-criação) e de dúvida (`error`, `panic`, `fatal`) detectadas por regex são o que dispara o plantão de intenção. O dedup é o que separa um gerente sênior de um alarme histérico: ele fala **uma vez por sessão**, não a cada mensagem. Sem essa camada, o gate cria *cry-wolf* e o agente aprende a ignorá-lo — falha de produto, não de detecção.

### Mecanismo D — Instalador idempotente multi-host (marcador de propriedade strip-then-merge)

- O instalador idempotente usa um **marcador de propriedade estável** (um nome de diretório, **não** um nome de produto) para fazer strip-then-merge: identifica as entradas próprias por esse marcador, remove-as, depois mescla o template fresco — re-run (upgrade) não duplica.
- Gate por feature-flag (a entrada de hooks só é escrita quando o host habilita a flag, ex. `codex_hooks=true` em `~/.codex/config.toml`); guarda Windows para scripts `.sh`.
- O manifesto por host declara o path do arquivo de hooks; o instalador reescreve esse JSON e o grava no config-dir do agente.

**Mapeamento ao gerente sênior.** É a folha de plantão idempotente: o gerente entra na escala uma vez por host (Claude `.claude/settings.json`, Cursor `.cursor/hooks.json` camelCase, Codex `.codex/config.toml` array-of-tables), e reinstalar não cria gerentes duplicados. TES já tem seu próprio marcador (`.tes/bin/tes_install.py` usado em `tes_install.py:319`, `:350` para detecção) e já tem `ensure_hook_group` (`:467`) — o instalador vira um **materializador burro**: lê manifesto, reescreve paths, mescla, verifica flag. O Mantra-Gate **possui** a definição de evento/matcher; o instalador não.

## 3. As 4 camadas de plantão e o bootloader como camada-mãe

O plantão é uma pilha, mais barata embaixo, mais cara em cima:

1. **Camada 0 — Regra no bootloader (`<mantra_gate>`).** É a gravidade. A regra correta de quando o gerente sênior é acionado mora no `.claude/CLAUDE.md`/`AGENTS.md`. Custo zero de runtime, sempre presente.
2. **Camada 1 — Gatilhos de palavra-chave (rubrica por intenção).** Mecanismos B+C: regex de risco/dúvida no `UserPromptSubmit`, com dedup. Planta a régua, não decide.
3. **Camada 2 — Hook pré-ação (`PreToolUse`).** Mecanismo A: `exit 2` bloqueia o atalho governado, `updatedInput` corrige default, `additionalContext` injeta o SPEC/ADR. É o ponto onde o gerente impede o ato, não o audita.
4. **Camada 3 — Preset de agente multi-host.** Mecanismo D: a escala idempotente que materializa as camadas 1-2 em Claude/Cursor/Codex sem duplicar.

**Por que o bootloader é a camada-mãe.** Quando a regra de acionamento no `<mantra_gate>` está correta — *"use um Mantra Gate leve só para mudanças destrutivas, remotas, de release, sync, secret-bearing ou de alto impacto"* — os gatilhos de palavra-chave **caem por gravidade** das camadas superiores: o regex de risco da Camada 1 e o matcher de tool da Camada 2 são apenas a projeção executável da regra do bootloader nos eventos do host. Se a regra-mãe estiver larga demais, o gate vira cry-wolf (viola Mecanismo C); se estiver estreita, o ato escapa. A Camada 0 é o oráculo de calibração das Camadas 1-3: elas não inventam o que é risco, elas materializam o que o bootloader já declarou risco. Logo a **primeira fatia** mexe na Camada 0, e só então as demais herdam o critério — não o contrário.

## 4. Como entra sem violar ADR 0005 (asset-transfer, no-new-skill)

ADR 0005 invariante 1 (linha 94): *"No new skill by default."* O detector senior-manager **já existe** (Birth). Portanto a regra de entrada é **absorver em superfície existente**, nunca criar skill de plantão:

- **Estender, não criar.** `tes_install.py` já tem `ensure_hook_group` (`:467`), os instaladores por agente (`install_claude_hook:462`, `install_cursor_hook:472`, `install_codex_hook:216`) e a lógica inversa de remoção (`:322-459`). A extensão é: generalizar `ensure_hook_group` para eventos além de `SessionStart` (`PreToolUse`, `UserPromptSubmit`), e generalizar o strip/merge para casar qualquer evento TES pelo marcador de propriedade do TES, não só `SessionStart`. `materialize_adapter.py` materializa os scripts de hook por host.
- **O detector é o `transferred_behavior`; o hook é o `smallest_patch`.** Nada de skill nova: o comportamento (detecção senior-manager) é o mesmo; só muda **quando** ele é chamado — de commit-time para pre-action/intent-time.

**Asset-transfer packet sketch** (ADR 0005, tabela `:39-50`):

| Campo | Conteúdo |
|-------|----------|
| `target_asset` | `scripts/tes_install.py` (instaladores de hook por agente + lógica inversa) e `scripts/materialize_adapter.py` (materialização dos scripts de hook por host). |
| `current_failure` | Detector senior-manager fiado só no commit gate (reativo); `beforeSubmitPrompt` instalado é facade de plantão (`tes_install.py:481` só duplica o aviso de sessão); nenhuma interceptação `PreToolUse`. |
| `transferred_behavior` | Forma host-agnóstica `evento → matcher-gated tool regex → comando host-privado (exit-2 bloqueia / `updatedInput` reescreve / `additionalContext` injeta)` + rubrica-que-não-decide + dedup anti-cry-wolf + instalador idempotente por marker. |
| `smallest_patch` | Generalizar `ensure_hook_group` para `PreToolUse`/`UserPromptSubmit`; generalizar strip/merge para casar qualquer evento TES pelo marcador de propriedade do TES; materializar 2 scripts de hook (pré-ação, intenção) com vocabulário de matcher TES-namespace. |
| `proof` | Fixture que prova `exit 2` bloqueando um Write em artefato governado; band-oracle de `interrupt_rate` no intervalo honesto; oráculo de idempotência (re-run não duplica entradas marcadas). |
| `regression_surface` | Superfície entregue (instalador, configs `.claude`/`.cursor`/`.codex` do target), materialização do adapter, contagem de hooks por host. Risco de release-identity: bump de patch + bundle. |
| `release_identity` | **Delivered** — muda comportamento do instalador e dos scripts de hook que o adopter recebe. Bump de patch + superfícies correlatas (`<release_identity>`); decisão do owner antes do fechamento. |
| `no_new_skill_evidence` | O detector já existe; o asset que carrega o novo timing é o instalador/materializador existente. Skill nova só se invocação autônoma não puder ser carregada por essas superfícies — não é o caso. |

## 4.1 Paridade multi-host (obrigatória) — os pilares hooks/agents NÃO são uniformes

Os hooks **não têm a mesma forma** entre Claude Code, Codex e Cursor — divergem em **nome** e **camada** do gancho, e — o ponto que a certificação obriga a não colapsar — no **contrato de saída**. Tratar "hooks" como camada única é facade de portabilidade: materializar só o evento Claude deixaria o pilar morto em dois dos três hosts. Matriz por host (forma, não conteúdo do projeto-referência):

| Dimensão | Claude Code | Codex | Cursor |
|----------|-------------|-------|--------|
| **(a) Pré-ação** | `PreToolUse` (PascalCase) | `PreToolUse` | `preToolUse` (camelCase) |
| **(b) Intenção** | `UserPromptSubmit` | `UserPromptSubmit` | `beforeSubmitPrompt` (nome E camada divergentes) |
| **(c) Exclusivos** | — | `statusMessage` por evento; `PreCompact` | `preCompact` |
| **(d) Ponto de instalação** | `.claude/settings.json` | `.codex/config.toml` (array-of-tables) + feature-flag `codex_hooks=true` + guarda Windows `.sh` | `.cursor/hooks.json` (`version:1`) |
| **(e) Contrato de saída** | `exit 2` bloqueia + stderr→agente; `hookSpecificOutput.updatedInput` reescreve; `additionalContext` injeta | **idêntico a Claude** (`exit 2` + `updatedInput`) | **NÃO usa `exit 2`** — bloqueio é JSON-permission (`{"permission":"deny","agent_message":"…"}`); a intenção emite `{"continue":true,"user_message":"…"}` |

**Três divergências não-colapsáveis:** (1) o nome do evento de intenção (`UserPromptSubmit` vs `beforeSubmitPrompt`); (2) `statusMessage` é só-Codex; (3) **o contrato de saída do Cursor é JSON-permission, não exit-code** — um materializador que assume `exit 2` em todo host quebra silenciosamente no Cursor. A fatia de hooks (§7 Slices 3-5) só é certificável-coerente quando esta matriz de cinco dimensões estiver honrada por host — não como "hooks" genérico.

## 5. Como cada hook se auto-falsifica (ADR 0006)

ADR 0006 linha 27: *"A generated oracle/fixture/anchor that does not fire under mutation of its own named property is a facade — even if the harness wrote it. Affirmation is never credit, not even self-affirmation."* Aplicado a hooks de plantão:

- **Um hook que nunca bloqueia/injeta é facade.** O `beforeSubmitPrompt` atual (`tes_install.py:481`) é exatamente isso: instalado, mas sem efeito de plantão. Instalar não é prova; prova é o hook **disparando** sob a mutação da propriedade que ele nomeia. Um hook pré-ação que nunca emite `exit 2` em nenhuma fixture é teatro — o equivalente ao `LENS_THEATER`/`CEILING_NOT_REACHED` da ADR 0006 (linhas 134, 136).
- **Fixture obrigatória do `exit 2`.** O hook pré-ação só é admitido se existir uma fixture adversarial que **prova `exit 2` bloqueando**: dado um Write/Edit em artefato governado (a propriedade nomeada = "edição governada sem evidência"), o hook retorna 2 e o stderr legível; e dado um Write benigno, retorna 0. Sem o caso vermelho observado, não há crédito (diamond build-test-fail-fix do bootloader: contrato final → fixture adversarial → falha observada → reparo menor → gate verde).
- **Band-oracle `interrupt_rate` (anti-cry-wolf falsificável).** A propriedade nomeada da camada de intenção é *"interrompe quando há risco, cala quando não há."* O oráculo é uma **banda**: interrupt_rate abaixo do piso = facade (gerente dormindo, nunca dispara); acima do teto = cry-wolf (gerente histérico, viola Mecanismo C). A fixture roda um corpus de prompts com/sem sinal de risco e exige a taxa dentro da banda. Um hook que dispara 100% ou 0% **falha o próprio oráculo** — afirmação de "está vigilante" não é crédito; o disparo medido sob mutação é.
- **Dedup é falsificável pela repetição.** Mecanismo C exige rubrica uma vez por sessão: a fixture injeta dois prompts de risco na mesma sessão e exige **uma** injeção; injeta em sessões distintas e exige duas. Se o hook repete dentro da sessão, falha — a flag de dedup por cache de sessão é a propriedade nomeada, a repetição é a mutação.

Cada hook nasce com seu falsificador; o instalador não credita um hook que não tenha fixture de disparo verde.

## 6. Confidencialidade — só a forma atravessa

ADR 0005 invariante 3 (`:96`) + `<confidentiality>` do bootloader. **Atravessa (forma):** o triplo `evento → matcher → timeout`; o schema de saída (`exit 0/2`, `hookSpecificOutput.updatedInput`, `additionalContext`); a rubrica-que-não-decide; os regex-shapes de intenção (erro/file-path/resume/save); o dedup por cache de sessão; o marcador-de-propriedade strip-then-merge; o gate por feature-flag e a guarda Windows `.sh`. `statusMessage` é feature opcional só-Codex (schema público do host) — atravessa como conhecimento de capacidade, não como string.

**NÃO atravessa (domínio/identidade do projeto-referência) — descrito por classe, nunca enumerado:**

A regra de confidencialidade proíbe enumerar os identificadores do projeto-referência aqui (enumerá-los É vazá-los — o erro que este parágrafo existe para evitar). Atravessa só a *forma*; ficam de fora, por classe:

1. **Regex de tool MCP do projeto-referência** — os nomes de ferramenta MCP e o namespace de plugin dele. Os matchers de TES usam o TES-namespace, nunca esses.
2. **Nomes de hook do projeto-referência** — os rótulos de hook branded dele.
3. **Paths de comando e variáveis de ambiente do projeto-referência** — os prefixos de root de plugin por host, as env vars com o prefixo dele, e os nomes de arquivo dos scripts de hook dele.
4. **Schema de identidade/memória do projeto-referência** — as chaves de partição (usuário/app/sessão), os campos de metadata de memória, os filtros de tipo, e os conceitos de domínio (memória, personalização, busca semântica).
5. **Metadata de plugin do projeto-referência** — nome/versão/autor/keywords dos manifestos de plugin e o bloco de configuração de chave de API.

Regra de fronteira: se uma string carrega o nome do projeto-referência, seu prefixo de env var, um nome de tool MCP dele, um nome de arquivo de script dele, ou um conceito de domínio dele (memória/usuário/personalização), **fica fora** do conteúdo TES rastreado — e não deve sequer ser citada como exemplo aqui. Só o *shape* (códigos de saída, schema JSON, nomes de evento de host, ordem de fluxo) cruza. Esta classe deve ser coberta por um gate de confidencialidade falsificável (ver `SPEC-CONVERGENCE` item de teto), não apenas por limpeza pontual.

## 7. Fatias ordenadas (cada uma com oracle falsificável)

A ordem segue a gravidade da §3: a camada-mãe primeiro, depois cada projeção. Default = `Birth`. As fatias que **alargam superfície entregue** são `owner_deferred` (decisão de release-identity antes de abrir).

| # | Fatia | Camada | Asset | Oracle falsificável | Release |
|---|-------|--------|-------|--------------------|---------|
| 1 | **Bootloader-rule** — afinar `<mantra_gate>` para o critério exato de acionamento do plantão (quando o gerente sênior é chamado). | 0 | `.claude/CLAUDE.md` / `AGENTS.md` (corpo governança espelhado) | Oráculo de calibração: corpus de cenários risco/não-risco; a regra classifica dentro da banda (sem cry-wolf, sem dormir). Falha se a regra não discrimina. | Maintainer (corpo de governança); sem bump. |
| 2 | **Keyword-triggers** — rubrica por intenção: regex de risco/dúvida + dedup por flag de cache de sessão, emitindo contexto sem decidir (Mecanismos B+C). | 1 | `materialize_adapter.py` (script de intenção materializado) | Band-oracle `interrupt_rate` dentro do intervalo honesto; dedup prova 1 injeção/sessão e 2 em sessões distintas; gate de comprimento < 20 chars sai silencioso. | **Delivered** → `owner_deferred` (bump de patch). |
| 3 | **PreToolUse hook** — interceptação pré-ação: `exit 2` bloqueia edição governada, `updatedInput` corrige default, `additionalContext` injeta SPEC/ADR (Mecanismo A). | 2 | `materialize_adapter.py` (script pré-ação) + `tes_install.py` (generalizar `ensure_hook_group` para `PreToolUse`) | Fixture adversarial: Write em artefato governado → `exit 2` + stderr legível; Write benigno → `exit 0`; `updatedInput` reescreve param verificado por diff. | **Delivered** → `owner_deferred` (bump de patch). |
| 4 | **UserPromptSubmit rubric** — fiar a rubrica da fatia 2 ao evento real por host (`UserPromptSubmit`/`beforeSubmitPrompt`), substituindo o facade atual (`tes_install.py:481`). | 1→2 | `tes_install.py` (evento real + matcher TES-namespace), inverso de remoção generalizado | A rubrica dispara no evento certo do host; o facade antigo é removido (strip pelo marcador de propriedade do TES); re-run idempotente não duplica. | **Delivered** → `owner_deferred` (bump de patch). |
| 5 | **Agents preset multi-host** — strip-then-merge pelo marcador de propriedade do TES generalizado para todos os eventos TES nos 3 hosts (Claude `.claude/settings.json`, Cursor `.cursor/hooks.json`, Codex `.codex/config.toml`), feature-flag gate Codex + guarda Windows `.sh` (Mecanismo D). | 3 | `tes_install.py` (strip/merge por evento, não só `SessionStart`; `:322-459` generalizado) | Oráculo de idempotência por host: instalar→reinstalar não duplica entradas marcadas; desinstalar remove só as TES e preserva hooks alheios (já testado para `SessionStart` em `:2118`, estender a todos os eventos). | **Delivered** → `owner_deferred` (bump de patch + bundle). |

**Sequência e gravidade.** A fatia 1 (Camada 0) define o critério; as fatias 2-4 (Camadas 1-2) herdam-no por projeção; a fatia 5 (Camada 3) materializa tudo idempotentemente. Nenhuma fatia 2-5 fecha sem o oráculo de disparo verde da §5 — instalar não é prova (ADR 0006). Cada fatia que toca o instalador ou os configs do target é `owner_deferred` por release-identity: a decisão de bump/bundle precede a abertura. A fatia 1, sendo só corpo de governança maintainer, abre em `Birth` sem bump.

Arquivo-alvo deste contrato: `/Users/murillo/Dev/tilly-engineer-skills/docs/roadmap/product/PLANTAO-HOOK-MECHANISM.md` (status: proposed, source_of_truth: false). Assets de absorção: `/Users/murillo/Dev/tilly-engineer-skills/scripts/tes_install.py`, `/Users/murillo/Dev/tilly-engineer-skills/scripts/materialize_adapter.py`. Leis governantes: `/Users/murillo/Dev/tilly-engineer-skills/docs/adr/0005-asset-transfer-to-existing-surfaces.md` (no-new-skill, packet `:39-50`), `/Users/murillo/Dev/tilly-engineer-skills/docs/adr/0006-decision-lens-evolution-and-routable-gate-closure.md` (affirmation-is-never-credit, `:27`).