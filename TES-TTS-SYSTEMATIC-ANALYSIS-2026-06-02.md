# Auditoria sistemática do subsistema `tes-tts`

> **Para revisão sênior.** Diagnóstico verificado — nenhum arquivo de produto ou
> de trabalho foi alterado. Os achados estão classificados pelas **duas camadas
> do TES** (produto entregue vs trabalho agêntico) e ordenados por risco ao
> adotante, não pela ordem de descoberta.
>
> | | |
> |---|---|
> | Data | 2026-06-02 |
> | Versão do bundle | `0.3.157` (`tes_tts_runtime_types.py:22`) |
> | Escopo | subsistema `tes-tts` apenas (ver §6 Limites) |
> | Método | exploração estática + execução ao vivo (oracles, runtime, OmniVoice) + varredura de 31 agentes com verificação adversarial; achados HIGH re-verificados manualmente |
> | Plataforma de verificação | macOS / Apple Silicon (MPS); CUDA não testado |

---

## 0. As duas camadas (eixo de classificação)

Todo achado abaixo é rotulado por camada, porque a camada determina **o que uma
correção custa**:

- **🟦 Produto TES** — fonte do pacote entregue/instalado/validado: `src/**`,
  `docs/**`, `package.json`/manifests/bundles, e `scripts/**` *quando o adotante
  recebe, executa ou depende do script*. Mudança aqui pode alterar o TES como
  produto → exige escopo cirúrgico, oráculo, correlação e, se for *delivered
  behavior*, **decisão de versão/bundle**.
- **🟨 Trabalho agêntico** — orienta o agente enquanto desenvolve: `.agents/**`,
  `.claude/**`, `.cursor/**`, guards internos, gates de manutenção. Ajuda a
  trabalhar; **não** é produto e não se promove a `src/`/docs sem intenção.

Classificação dos arquivos tocados por esta auditoria (verificada em
`tes_bundle.py:94-101` = `HELPER_FILES` bundled para `.tes/bin/**`):

| Arquivo | Camada | Por quê |
|---------|--------|---------|
| `scripts/tes_tts_runtime_classifier.py` | 🟦 Produto | bundled, instalado em `.tes/bin/`; adotante depende |
| `scripts/tes_tts_runtime_verbalizer.py` | 🟦 Produto | bundled |
| `scripts/tes_tts_omnivoice_provider.py` | 🟦 Produto | bundled |
| `scripts/tes_tts_omnivoice_runtime_support.py` | 🟦 Produto | bundled |
| `scripts/tes_tts_audio_audit.py` | 🟨 Trabalho | **não** bundled; diagnóstico de maintainer |
| `scripts/tes_tts_*_oracle.py` (18) | 🟨 Trabalho | gates de maintainer; nenhum em `HELPER_FILES` nem em superfície de adotante |
| `.claude/CLAUDE.md`, `.agents/skills/**` | 🟨 Trabalho | bootloader/skills locais (composto/materializado) |

**Consequência de prioridade:** os defeitos que atingem o adotante vivem na
camada de produto (`classifier`, `provider`). A regressão de oracles, por mais
vermelha que esteja, é camada de trabalho — protege o desenvolvimento, não é
recebida pelo adotante. O report está ordenado segundo esse eixo.

---

## 1. Veredito executivo

O `tes-tts` é **arquiteturalmente sólido e operacionalmente funcional**: pipeline
limpo `classify → verbalize → adapt → provider`, núcleo dependency-free, e
síntese OmniVoice real verificada ao vivo (WAV válido, voz clonada, RTF 1.77).
Os problemas são localizados, não estruturais.

**Dois itens exigem ação; um deles é de produto e deve liderar:**

1. **🟦🔴 Vazamento de segredos na redação (P-1).** A fronteira de redação —
   promessa de segurança central do `tes-tts`, e código **entregue ao adotante**
   — deixa passar em claro os nomes canônicos de credencial (`access_token=`,
   `client_secret=`, `db_password=`, `TOKEN=`, `Token=`), além de `sk-`/`ghp_`/
   `AKIA`/PEM soltos, e **trunca** valores com caracteres especiais vazando o
   sufixo. Defeito objetivo de segurança em superfície de produto.
2. **🟨🟠 Suíte de oracles vermelha, sem gate e auto-mascarante (W-1).** 11/18
   oracles falham por version drift; nenhum está no `commit:check`; e o
   version-gate faz uma regressão real ficar indistinguível do drift. É grave
   para a **confiabilidade do desenvolvimento**, mas é camada de trabalho: os
   oracles não estão em `HELPER_FILES`/`.tes/bin` nem são runtime instalado, então
   não falam áudio nem alteram o runtime do adotante. (Nuance de empacotamento:
   `package.json` não declara `files`, então a fronteira do pacote-fonte é mais
   frouxa que o bundle; isso não muda a prioridade — W-1 segue gate/dev.)

A inversão a corrigir versus a primeira passada deste report: a regressão de
oracles fora rotulada "CRÍTICO nº 1". Pela classificação por camada, **o
vazamento de segredos (produto) tem prioridade sobre a regressão de oracles
(trabalho)**.

**Fio condutor de todos os achados sérios:** os oracles validam fixtures
mockadas, não a saída do runtime real nem formatos adversariais — e o
version-gate ainda mascara o que sobraria. Por isso drift, divergência de
boundary e gaps de redação passam todos sem alarme.

---

## 2. Achados de camada de PRODUTO 🟦 (atingem o adotante)

### P-1 🔴 HIGH — Vazamento de segredos: cobertura por lista literal e truncamento

| | |
|---|---|
| Arquivo | `scripts/tes_tts_runtime_classifier.py:30-34` (`SECRET_PATTERN`, `BEARER_SECRET_PATTERN`) |
| Camada | 🟦 Produto — bundled, `delivered behavior` |
| Baseline | commit `adebd5d` ("Improve TES TTS protected matcher runtime"), VERSION `0.3.157` |
| Invariante violado | `## Safety` do SKILL.md: *"Do not read API keys, tokens, passwords, private keys… aloud. Redaction overrides exact, literal, raw, verbatim."* |
| Doutrina relevante | `regression_guard`: *"narrow literal lists in runtime code… are regression seeds"* — o defeito **confirma empiricamente** essa doutrina |

**Repro (executado ao vivo, `redact_secret_like_values`):**

```
access_token=ghp_AbC123Def456  →  (intacto)     client_secret=swordfish → (intacto)
db_password=Pa55word           →  (intacto)     TOKEN=abc / SECRET=abc  → (intacto)
PASSWORD=topsecret             →  (intacto)     Token=hunter2 / Api_Key=x → (intacto)
password=p@ssw0rd!             →  password=[REDACTED_SECRET]@ssw0rd!   (sufixo vaza)
sk-proj-ABC… / ghp_… / AKIA… / -----BEGIN PRIVATE KEY-----  →  (intactos)
# Controles que redigem: api_key=, MY_PASSWORD=, APIKEY=, Bearer <token>
```

**Mecanismo (4 causas no regex):**
1. `_` é caractere de palavra → não há `\b` antes de `token`/`secret`/`password`
   em nomes compostos (`access_token=`, `client_secret=`).
2. ramo maiúsculo `[A-Z][A-Z0-9_]*(?:KEY|TOKEN|…)` exige ≥1 char antes do sufixo
   → `PASSWORD=` puro não casa (mas `MY_PASSWORD=` casa).
3. ramo minúsculo é case-exato → `Token=`/`Api_Key=` escapam.
4. truncamento: grupo de captura `([A-Za-z0-9_./:+-]+)` para no 1º caractere
   especial, redigindo o prefixo e **vazando o sufixo**.

**Blast radius:** todo adotante com `.tes/bin/` instalado. O `redacted_text`
flui para a síntese de voz (`classifier.py:519,532,576`), então o segredo é
falado / persiste no texto preparado.

**Correção (delivered behavior — exige ciclo de release):** reescrever
`SECRET_PATTERN` como dado governado, não lista literal — case-insensitive
(`(?i)`), nomes compostos (`[\w-]*(?:key|token|secret|password)=`), grupo de
captura ganancioso até whitespace, e prefixos conhecidos (`sk-`,`ghp_`,`AKIA`,
PEM). Disciplina `diamond build-test-fail-fix`: fixture adversarial → observar
vazamento → reparo mínimo → gate verde. Propagação:
`scripts/` → `tes_bundle` → `.tes/bin/**` → bump de versão + bundle público +
`commit:check`.

### P-2 🟠 MEDIUM — Idioma misto pt/en classifica prosa inglesa como `pt`

| | |
|---|---|
| Arquivo | `scripts/tes_tts_omnivoice_runtime_support.py:581-662` (`infer_long_read_chunk_language`) |
| Camada | 🟦 Produto — bundled |
| Severidade | MEDIUM (verificador rebaixou de high: caminho `auto` é opt-in, `--language` default `pt`; impacto é qualidade de fala, não quebra) |

Heurística de ~20 stopwords hardcoded; inglês natural sem marcadores técnicos
vira `pt`. Mesma classe do P-1 (lista literal estreita). Confirmado: *"This is a
simple sentence…"* → `pt`. Degrada idioma de chunks no `speak-long --language auto`.

### P-3 🟠 MEDIUM — `certifies_provider_support` live contradiz o oracle e o ADR

| | |
|---|---|
| Arquivos | provider `tes_tts_omnivoice_provider.py:219` vs oracle `tes_tts_provider_probe_oracle.py:293-294` |
| Camada | 🟦 Produto (provider) ↔ 🟨 Trabalho (oracle) |
| ADR | 0004:23 e OWNER-001:41 negam *"provider certification"* |

O probe **live** emite `certifies_provider_support: True` (quando OmniVoice
disponível — confirmei ao vivo). O oracle exige `False` (*"plan must not certify
provider support"*) e o ADR proíbe certificação. A mesma chave significa o
oposto no produto e no gate; o oracle nunca confronta a saída real, então a
divergência é invisível. Decisão de interpretação do owner: renomear a chave
(separar "ambiente usável" de "certificado p/ redistribuição") ou alinhar.

### Achados LOW de produto (qualidade/fragilidade — sem quebra ativa)

- **🟦 IPv4 vs versão** (`classifier.py:429-445`): `1.2.3.4` falado como "IP 1
  ponto 2…"; sem tipo SemVer, IPv4 sempre vence. `preserve_identity=False`, só
  afeta o spoken_alias.
- **🟦 PATH trunca acentos** (`classifier.py:38-41`): `/home/joão` → `/home/jo`.
  É aliasing de leitura, **não** fronteira de segurança (verificador rebaixou de
  medium). Input realista num subsistema PT-BR-nativo → vale corrigir a qualidade.
- **🟦 `verbalize_ir` assume IR ordenada** (`verbalizer.py:8-26`): contrato
  implícito frágil; corrompe se a IR não vier ordenada por `start` (hoje vem).
- **🟦 `combine_wav_files`** descarta chunk ausente em silêncio e reporta PASS
  (`runtime_support.py:74`); fila de playback pode tocar arquivo inexistente (`:242`).
- **🟦 Profile sobrescreve flags** (`provider.py:511-518`): `technical-live`
  sobrepõe `--chunk-chars`/`--language` do usuário no `speak-long` sem avisar.
- **🟦 `torch.load(weights_only=False)`** (`direct_kernel.py:143`): desserialização
  irrestrita no cache de prompt (mitigado: cache local protegido `0600`).
- **🟦 Wrappers mortos** (`provider.py:3039-3075`): 6 funções `return
  direct_kernel.X(...)` nunca chamadas localmente. *Não* é duplicação de
  implementação (correção a um exagero da 1ª passada) — é código morto, baixo.

---

## 3. Achados de camada de TRABALHO 🟨 (confiabilidade do desenvolvimento)

> Estes não atingem o adotante. Importam porque são o que **permitiria os
> defeitos de produto entrarem sem alarme** — a raiz comum do report.

### W-1 🔴 HIGH (dev) — Suíte de oracles vermelha + sem gate + auto-mascarante

Três achados que se compõem:

- **W-1a — 11/18 oracles FAIL por version drift.** Fixtures pinadas em `0.3.150`,
  runtime `0.3.157`; `VERSION` hardcoded em 17 oracles + assert de igualdade
  estrita. (chunked_preparation, compiled_lexical_index, fast_path, hot_path,
  live_session, pronunciation_catalog, ptbr_lexical ×2, request_local_memoization,
  runtime_ir, runtime_latency.)
- **W-1b — fora do gate.** `commit:check` roda só `roadmap_partition`; pre-commit
  roda +`audio_audit`/`omnivoice_provider` condicionais. Os 11 não rodam em
  lugar nenhum (verificado: ausentes de `validate_reference_package.py`, CI,
  pre-push). Por isso o release `0.3.157` saiu com a suíte vermelha.
- **W-1c — version-gate mascarante** (`runtime_ir_oracle.py:154`): `validate_fixtures`
  faz `return` no check de versão **antes** do loop de casos. Enquanto houver
  drift, nenhum caso de comportamento roda — **uma regressão real é
  indistinguível do drift**. Re-pinar sem corrigir a estrutura esconderia bugs.

**Correção:** (1) re-pinar 11 fixtures `0.3.150→0.3.157` (mecânico); (2)
importar `VERSION` de `tes_tts_runtime_types.py` (fonte única) em vez de
hardcode; (3) adicionar os oracles a um alvo no `commit:check`; (4) separar
"fixture version" de "comportamento" para o gate não mascarar. Itens 2-4 são
decisão de processo do owner.

### W-2 🟡 MEDIUM (dev) — Oracles testam mocks, não o runtime real

Cobertura inversa verificada:
- `omnivoice_provider_oracle` (2962L) nunca sintetiza áudio real — `FakeModel`,
  `b"fake-wave"`, probe monkeypatched, `--dry-run` em todo speak/bench. É oracle
  de **contrato/IR by-design** (ADR proíbe modelo pesado em CI); o caminho real
  é o `live-smoke` manual. Gap de cobertura automatizada, não defeito.
- `instruction_normalizer_oracle` (38KB) + `runtime_latency_oracle` medem
  funções que **só existem dentro do próprio oracle** (markdown clean,
  conversational, tabela) — cobertura/timing órfãos. (Correção do verificador:
  redação e siglas, citadas no achado original, **estão** no runtime via outros
  oracles — não inflar.)
- Nenhum oracle asserta o **valor** de `certifies_provider_support` (só shape),
  por isso o P-3 não é regredido por teste.

### W-3 🟡 MEDIUM (dev) — `audio_audit` (ferramenta de maintainer)

- **`audit-session` quebra com chunk ausente** (`audio_audit.py:463`):
  `FileNotFoundError` não tratado (combined.wav ausente é tratado; chunk não).
- **STT só resolve caminho legado** (`:26-32,644-645`): resolve python/modelo STT
  só em `ROOT/.tes`, sem fallback p/ runtime global `$HOME/.tes` nem env — mesma
  classe que o commit `2b3112a` corrigiu p/ o probe. (Verificador: fix correto
  precisa achar Whisper no cache HF, não sob o runtime omnivoice.)
- Fragilidades menores: `IndexError` com STT stdout vazio; bloat de JSON.

### Achados LOW de trabalho

- **Código morto em oracle** (`hot_path_span_matcher_oracle.py:136`):
  `literal_spans` reimplementado nunca chamado, com `normalizer` inexistente
  (`NameError` se rodasse).
- **Guard AST evadível** (`candidate_review_oracle.py:103-122`): `os.system` via
  atributo escapa — mas só escaneia o próprio fonte do oracle, **sem vetor de
  atacante** (verificador rebaixou a INFO).
- **Higiene documental:** 23 arquivos `*OWNER-DECISION*`, ~20 redundantes
  (>95% boilerplate). A decisão já foi parcialmente fechada em OWNER-001
  (2026-05-29). Débito de processo da camada de trabalho.

---

## 4. Verificação de runtime do OmniVoice (POSITIVO, ao vivo) 🟢

- Runtime global `~/.tes/runtime/tes-tts/omnivoice/` presente e válido; venv
  isolado; `omnivoice 0.1.5`, `torch 2.8.0`, `soundfile` importáveis; MPS sim,
  CUDA não.
- `probe → provider_available` (resolve venv global automaticamente);
  `status → ready`; voice-prompt cache **protegido** (`0700`, nenhum desprotegido).
- Profiles do SKILL.md (`technical-live`/`hd`/`streamer`/`quality`) batem com o
  código (`provider.py:80-119`): live `num_step 28`, hd `32`, chunk 420, 450ms.
- **Síntese real fim-a-fim FUNCIONA:** WAV válido (PCM 16-bit mono 24 kHz,
  2.96s), voz clonada, cache hit (1.07ms), 5.24s → RTF 1.77. Invariantes
  honrados: `source_text_immutable`, `command_execution: not_performed`,
  `summary_behavior: none`. WAV temporário removido.

Outros positivos confirmados (18 no total): imutabilidade do source no pipeline;
redação de `Bearer` e `chave=valor` lowercase funciona; materialização de
adapter governada e testada (`materialize_adapter all --check` PASS) — **não** é
drift, é pipeline governado; guard de range IPv4 descarta octetos > 255.

---

## 5. Plano de correção proposto (para decisão sênior)

Ordenado por camada e prioridade. **Nada executado.**

| # | Achado | Camada | Tipo | Custo de propagação |
|---|--------|--------|------|---------------------|
| P-1 | Vazamento de segredos | 🟦 Produto | defeito objetivo de segurança | fonte→bundle→`.tes/bin`→**bump+bundle+release** |
| P-2 | Idioma misto → pt | 🟦 Produto | qualidade | idem (delivered) |
| P-3 | `certifies` live vs ADR | 🟦/🟨 | decisão de owner | renomear chave / alinhar oracle |
| P-LOW | IPv4, PATH acento, verbalizer, combine_wav, profile, torch.load, wrappers mortos | 🟦 Produto | qualidade/limpeza | delivered se mudar comportamento |
| W-1 | Oracles vermelhos / sem gate / mascarante | 🟨 Trabalho | regressão de dev + processo | re-pin (mecânico) + gate/fonte-única (owner) |
| W-2 | Oracles mockados | 🟨 Trabalho | cobertura | adicionar testes que tocam runtime real |
| W-3 | `audio_audit` crash + STT legado | 🟨 Trabalho | bug de ferramenta | edição de fonte, não bundled |
| W-LOW | Código morto oracle, guard AST, bloat OWNER-DECISION | 🟨 Trabalho | limpeza | edição local |

**Sequência recomendada:** P-1 primeiro (segurança de produto, disciplina
diamond, fixtures de regressão), depois W-1c+W-1b (para que o gate **detecte** a
correção e impeça reincidência), depois o resto. Toda correção de produto passa
pela decisão de versão/bundle do `release_identity`. Itens 🟨 não precisam de
bump. A rota TES natural é `/tes-bump` + `/tes-sync`.

---

## 6. Limites desta auditoria

- **Escopo `tes-tts` apenas.** Resto do TES (Cortex, field-reports, instaladores,
  ~80 scripts) não auditado.
- **Síntese real só em caso curto.** `speak-long` com relatório grande real e
  qualidade de áudio (além de RTF/validade) não estressados.
- **Sem teste de carga/concorrência** (`serve`, fila de playback sob pressão).
- **Cobertura amostral, não formal** — sem métrica de linha/branch.
- **Sem fuzzing/property-testing** — os gaps de redação (P-1) vêm de casos
  escolhidos a dedo; um fuzzer acharia mais formatos.
- **macOS/MPS apenas** — Linux/CUDA não verificado.
- **Camada de trabalho não reescrita** — `.claude/CLAUDE.md` é composto por
  `root_context.py` (core+overlay, hash-verificado); editá-lo à mão quebraria
  hashes e violaria o `target_source_boundary`. Fora do escopo de produto.

---

## Apêndice — comandos de verificação reproduzíveis

```bash
# W-1a/W-1b: suíte de oracles (esperado 11 FAIL por version drift) e gate
for f in scripts/tes_tts_*_oracle.py; do
  python3 "$f" --self-test >/dev/null 2>&1 && echo "PASS  $(basename $f)" || echo "FAIL  $(basename $f)"
done
grep -l '"0.3.150"' benchmarks/tes-tts/*.json | wc -l          # 11 fixtures defasadas
grep -o 'tes_tts_[a-z_]*oracle\.py' package.json | sort -u     # só roadmap_partition gated

# P-1: gap de redação de segredos (formatos que VAZAM)
python3 -c "
import sys; sys.path.insert(0,'scripts')
from tes_tts_runtime_classifier import redact_secret_like_values as R
for t in ['access_token=ghp_AbC123','client_secret=x','db_password=Pa55word',
          'TOKEN=abc','Token=hunter2','password=p@ssw0rd!','sk-proj-ABC']:
    red,_=R(t); print(('REDIGE ' if '[REDACTED_SECRET]' in red else 'VAZA   ')+red)
"

# Classificação por camada: helpers bundled (produto) vs oracles (trabalho)
grep -nE '"tes_tts_(runtime|omnivoice)' scripts/tes_bundle.py     # 8 helpers = produto (.tes/bin)
grep -c 'oracle' scripts/tes_bundle.py | grep -q tes_tts || \
  ls scripts/tes_tts_*_oracle.py | wc -l                          # 18 oracles, nenhum bundled = trabalho

# Materialização governada (NÃO é drift) + runtime OmniVoice vivo
python3 scripts/materialize_adapter.py all --check && echo "materialize: governado"
python3 scripts/tes_tts_omnivoice_provider.py probe   # provider_available, ao vivo
```
