# Sync Plan — docs/governance/SYNC-AUDIT-CHECKLIST.md (rollback section) + docs/INDEX.md (new entry)

## TL;DR

**Escopo correto: source-only sync (no version bump, no public bundle, no tag).**

Os dois arquivos tocados são **maintainer-only / governance**, não são behavior
adopter-visível. Não há mudança em `src/adapters/**`, em `bin/tes.js`, em
scripts com `VERSION = …`, em `docs/install/**`, em i18n público, em
`docs/dist/**`, nem em plugin manifests. Por isso, e porque
`tes_bump.py --governance-check` já retornou `PASS`, a decisão de identidade
de release é: **não bumpar versão, não regenerar bundle, não criar tag**.

O que se quer aqui é apenas: rodar a porteira (`npm run commit:check`), commitar
com mensagem precisa e fazer `git push origin main`.

---

## 1. Por que é source-only e não source + bundle

Critério aplicado vem de dois lugares concordantes no repo:

- `AGENTS.md` bloco `<release_identity>`: bump só é requerido quando muda
  "adopter-visible skills, triggers, installer behavior, helper/runtime
  scripts, plugin metadata, public docs, MCP, Field Reports, Cortex behavior,
  or adapter materialization". Editar `SYNC-AUDIT-CHECKLIST.md` (que é
  governance maintainer-only) e adicionar uma linha em `docs/INDEX.md` não
  cai em nenhuma dessas classes.
- `docs/governance/SYNC-AUDIT-CHECKLIST.md` seção *Version governance
  decision*: quando `tes_bump.py --governance-check` retorna `PASS`, a
  instrução literal é "no bump needed; continue to **Commit**". A seção
  *Identity bump 0.3.X → 0.3.Y* e *Public bundle* só se aplicam se a decisão
  for **source + public refs + bundle**, que não é o caso.

Conclusão: nada em `package.json`, `bin/tes.js`, README badge,
`docs/tds/DOCS-INDEX.yml` header version, `docs/adapters/CODEX.md`,
`docs/roadmap/**` baseline, scripts `VERSION = …`, i18n público,
`structure.yml` `bundle_sha256`, ou `docs/dist/<new>/**` precisa se mover.

---

## 2. Plano de execução (read-only — só descrito)

### 2.1 Pré-flight

1. `git status -sb` — confirmar que o diff é exatamente:
   - `M docs/governance/SYNC-AUDIT-CHECKLIST.md`
   - `M docs/INDEX.md`
   Nenhum arquivo extra em `.tes/`, `docs/dist/`, `node_modules/`, `docs/i18n/`,
   `src/adapters/**` ou `scripts/**`. Se aparecer algo, parar e investigar
   antes de seguir — o pré-flight do checklist é explícito sobre isso.
2. Resumir em uma frase qual é a mudança entregue:
   "Adicionado bloco de rollback ao SYNC-AUDIT-CHECKLIST e registrada a nova
   entrada correspondente em `docs/INDEX.md`." Se a frase não fechar, o commit
   é prematuro.
3. Confirmar que a nova seção do `SYNC-AUDIT-CHECKLIST.md` faz sentido junto
   das seções existentes (Pre-flight, Source change, Oracle/self-test,
   Indexing, Doc size, Version governance decision, Identity bump, Public
   bundle, Final gate, Commit, Push, Tag, Closeout, Locks). Rollback
   provavelmente entra como seção nova entre *Push* e *Tag* ou junto de
   *Locks*; importante é que o `docs/INDEX.md` aponte para o doc certo, não
   para uma âncora que ainda não existe.

### 2.2 Correlation rule — indexing

Mesmo num source-only sync, o checklist exige verificar a regra de correlação
para qualquer doc tocado:

1. `docs/governance/SYNC-AUDIT-CHECKLIST.md` já existe — não precisa ser
   adicionado em `docs/tds/DOCS-INDEX.yml` de novo. Só conferir se a entrada
   atual ainda descreve o conteúdo agora que tem rollback. Se a descrição
   ficou estreita demais, atualizar a entrada (continua sendo source-only).
2. A "entrada nova" em `docs/INDEX.md` é o ponto sensível: ela precisa apontar
   para um arquivo que existe. Se a entrada nova aponta para um doc novo que
   não está no diff, esse arquivo está faltando — parar e adicioná-lo, ou
   remover a entrada. Se a entrada nova aponta para uma seção dentro de
   `SYNC-AUDIT-CHECKLIST.md` (a seção de rollback), o link/âncora precisa
   bater com o heading exato adicionado.
3. `scripts/validate_reference_package.py` `REQUIRED_PATHS` — só precisa
   mexer se um *novo arquivo obrigatório* foi adicionado. Como nesse caso a
   mudança é só dentro de docs já existentes, não tocar.

### 2.3 Doc size

`python3 scripts/validate_doc_size.py` precisa passar. `SYNC-AUDIT-CHECKLIST.md`
já é grande (~270 linhas) — adicionar uma seção de rollback pode encostar no
budget. Se estourar 500 linhas, o checklist é categórico: **não levantar o
budget**, extrair a seção de rollback para `docs/governance/SYNC-ROLLBACK.md`
(ou equivalente), linkar do checklist principal, indexar o novo arquivo no
`DOCS-INDEX.yml` e em `docs/INDEX.md`. Isso ainda mantém o sync source-only.

### 2.4 Governance gate

`python3 scripts/tes_bump.py --governance-check` já retornou `PASS` — confirma
que nenhum surface de versão divergiu. Rodar de novo depois das últimas
edições defensivas só pra ter o PASS imediatamente antes do commit.

### 2.5 Final gate — `npm run commit:check`

Esse é o gate intransponível antes do push (lock explícito do checklist:
"Do not push without `npm run commit:check` PASS").

A lista de 33 tags esperada está no checklist. Para um source-only sync
desse tipo, os tags relevantes que precisam continuar verdes são
especialmente:

- `tes-reference` (nenhum arquivo novo untracked),
- `tds` e `tds-surface` (índice de docs e bundle sha consistente — sha não
  muda pois bundle não é regerado),
- `doc-size` (se passou perto, modularizar),
- `context-mesh-plan`, `root-context`, `project-context` (governance docs
  são parte do mesh),
- `command-triggers`, `platform-surface`, `retention-metadata`,
  `reference-graph`, `materialize`, `adapter-parity-readiness` (não devem
  regredir).

Se qualquer tag virar `FAIL` ou `BLOCKER`, **não** commitar. As armadilhas
documentadas que se aplicam aqui:

- `tes-reference FAIL: untracked package path` → algum arquivo novo (ex.: o
  doc extraído por doc-size) não foi `git add`. Adicionar e re-rodar.
- `tds FAIL: missing index entry` → a entrada nova em `INDEX.md` deve ter
  par em `DOCS-INDEX.yml` se ela aponta para um arquivo que não estava
  indexado lá.
- `doc-size FAIL` → modularizar (não levantar budget).

Tags como `public-bundle-oracle`, `tes-install:self-test`, `tes-npx:self-test`,
`install-mcp`, `install-smoke` devem continuar verdes simplesmente porque
nada foi tocado nesses surfaces.

### 2.6 Stage + commit

1. `git add docs/governance/SYNC-AUDIT-CHECKLIST.md docs/INDEX.md` — staging
   explícito. Evitar `git add -A` aqui porque nada mais deveria estar mudando;
   se estiver, é sinal de que o pré-flight não pegou algo.
2. `git diff --cached --stat | tail -3` — confirmar 2 arquivos e magnitude
   de inserções esperada (poucas dezenas de linhas).
3. Mensagem de commit (modelo seguindo a convenção do checklist):

   ```
   docs(governance): add rollback section to SYNC-AUDIT-CHECKLIST and index entry

   Documents the rollback path that was missing from the audit checklist
   so maintainers have an explicit recovery procedure if a sync step fails
   mid-flight. INDEX.md gains the corresponding entry so the new section
   is discoverable from the docs map.

   Source-only sync: no behavior change, no version bump, no bundle
   regenerated. tes_bump.py --governance-check PASS confirms release
   identity surfaces are aligned.

   Co-Authored-By: …
   ```

   Pontos que a mensagem precisa carregar (pelo checklist):
   - subject 1-line do que mudou;
   - body com o "por quê";
   - declaração explícita do escopo (`Source-only sync`) — substitui o
     `Release identity X -> Y` que só aparece quando houve bump;
   - footer `Co-Authored-By` padrão.

4. `git status` deve ficar limpo, `git log -1 --stat` deve refletir só os
   dois arquivos esperados.

### 2.7 Push

1. `git status -sb` → deve mostrar `## main...origin/main [ahead 1]`.
2. `git push origin main`.
3. `git status -sb` → deve mostrar `## main...origin/main` sem `[ahead]`.

### 2.8 Tag — **não fazer**

Source-only sync sem bump não cria tag nova. A seção *Tag* do checklist é
literal: "only when the bump publishes a new public ref". Como não há novo
ref público (sem `package.json` bump, sem `docs/dist/<new>/`, sem
`bin/tes.js` `TES_VERSION` novo), não criar `v0.3.<next>`. Não rodar
`npm run release:check` (esse é parte do fluxo de tag).

### 2.9 Closeout

Registrar para fechar a sessão:

- Claim final: `PASS — source-only sync of governance docs`.
- Commit hash do push.
- Pacote de evidência: este próprio plano + saída do `commit:check`.
- Sem tag, sem bundle regenerado, sem versão movida.
- Sem exceção de bump deferido (não há mudança de behavior que justificasse
  bump em primeiro lugar — não é um "deferred bump", é um "no bump needed").

---

## 3. O que NÃO fazer (locks aplicáveis)

- Não tocar `package.json`, `bin/tes.js`, README shield, `DOCS-INDEX.yml`
  header version, `docs/adapters/CODEX.md` Project version, roadmap baseline,
  scripts `VERSION`, i18n público, `docs/dist/**`, plugin manifests. Nenhum
  desses arquivos faz parte dessa mudança.
- Não rodar `scripts/tes_bundle.py publish`. O bundle só é regerado em
  scope source + public refs + bundle.
- Não rodar `scripts/build_public_docs.py`. Mesma razão.
- Não criar tag nova `v0.3.<next>`.
- Não usar `--no-verify` para passar por cima do `commit:check`. O lock
  do checklist é claro.
- Não fazer `git push --force` em nenhuma circunstância aqui — é fast-forward
  de um único commit, push normal basta.
- Não levantar `validate_doc_size.py` budget se o doc estourar 500 linhas —
  modularizar.

---

## 4. Resumo executável (mas read-only neste momento)

| Etapa | Comando | Status esperado |
|-------|---------|-----------------|
| Pré-flight | `git status -sb` | só 2 arquivos M |
| Doc size | `python3 scripts/validate_doc_size.py` | PASS |
| Governance | `python3 scripts/tes_bump.py --governance-check` | PASS (já confirmado) |
| Final gate | `npm run commit:check` | 33 tags PASS |
| Stage | `git add docs/governance/SYNC-AUDIT-CHECKLIST.md docs/INDEX.md` | — |
| Commit | `git commit -m …` (mensagem acima) | clean tree depois |
| Push | `git push origin main` | `origin/main` em paridade |
| Tag | **não fazer** | — |
| Bundle | **não fazer** | — |
| Release check | **não fazer** | — |

Esse é o escopo source-only. Se em algum ponto o `commit:check` revelar
que um surface oculto se moveu (ex.: alguém regenerou bundle paralelamente
e o sha não bate), aí sim re-avaliar o escopo — mas com base no diff
descrito, isso não deve acontecer.
