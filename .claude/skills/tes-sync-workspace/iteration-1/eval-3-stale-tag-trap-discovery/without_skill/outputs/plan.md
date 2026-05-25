# Procedimento para criar `v0.3.127` sem sobrescrever artefatos públicos

Contexto recebido:
- Bump `0.3.126 -> 0.3.127` já foi commitado.
- `npm run commit:check` passou (verde).
- Push para `main` já foi feito.
- Falta criar a tag `v0.3.127`.
- Pergunta crítica: como garantir que a tag não vai sobrescrever silenciosamente algum artefato público, inclusive no cenário onde a tag já existe apontando para um commit órfão.

A premissa que ancora todo o procedimento: **uma tag de release é um contrato imutável**. Se a tag `v0.3.127` já existe (local ou remota), assumir que pode reescrevê-la é o vetor principal de "sobrescrita silenciosa". Tudo abaixo é projetado para detectar, diagnosticar e só então decidir.

---

## Fase 0 — Confirmar estado de partida (read-only)

Antes de tocar em qualquer ref, fotografar o que existe. Nada disso muta o repositório.

1. **Confirmar HEAD e branch atual**

   ```bash
   git rev-parse --abbrev-ref HEAD          # esperado: main
   git rev-parse HEAD                       # SHA do commit do bump 0.3.127
   git log -1 --pretty='%h %s'              # última msg deve mencionar 0.3.127
   ```

2. **Confirmar que o working tree está limpo**

   ```bash
   git status --porcelain                   # esperado: vazio
   ```

   Se houver qualquer modificação pendente, **parar**. Tags assinadas devem refletir exatamente o que foi auditado pelo `commit:check`.

3. **Confirmar que `origin/main` está sincronizado com `HEAD`**

   ```bash
   git fetch origin
   git rev-parse HEAD
   git rev-parse origin/main
   # os dois SHAs devem ser idênticos
   ```

   Se diferirem, alguém empurrou algo no intervalo. **Parar** e reconciliar antes de taguear.

4. **Confirmar que `package.json` no commit alvo realmente diz `0.3.127`**

   ```bash
   git show HEAD:package.json | grep '"version"'
   ```

   Tag e versão precisam casar.

---

## Fase 1 — Detectar colisão de tag (o cenário do "commit órfão")

Esse é o coração da pergunta. Existem quatro estados possíveis para `v0.3.127`:

| Estado | Local? | Remoto? | Aponta para HEAD? | Ação |
|---|---|---|---|---|
| A | não | não | n/a | Caminho feliz, criar normalmente |
| B | sim | não | sim | Tag local já correta, faltava só `push` |
| C | sim | não | **não** (aponta p/ órfão) | **Não sobrescrever** — diagnosticar |
| D | sim ou não | **sim** | n/a | **Tag pública já existe** — abortar e reabrir incidente |

Sequência de verificação:

1. **Tag local existe?**

   ```bash
   git tag --list v0.3.127
   git rev-parse --verify --quiet refs/tags/v0.3.127 || echo "no local tag"
   ```

2. **Tag remota existe? (não confie só no cache local — `fetch` primeiro)**

   ```bash
   git fetch --tags --prune --prune-tags origin
   git ls-remote --tags origin v0.3.127
   git ls-remote --tags origin 'v0.3.127^{}'   # peeled, caso seja tag anotada
   ```

   - Saída vazia => não existe no remoto.
   - Saída com SHA => **tag pública já existe**. Estado D. Ver Fase 3.

3. **Se a tag local existe, ela aponta para o commit certo?**

   ```bash
   git rev-parse refs/tags/v0.3.127
   git rev-parse refs/tags/v0.3.127^{commit}   # peeled para o commit alvo
   git rev-parse HEAD
   ```

   Se o commit apontado pela tag **não** é HEAD, investigar:

   ```bash
   git cat-file -t v0.3.127                                  # blob/commit/tag?
   git log --oneline -1 v0.3.127^{commit}
   git branch --contains v0.3.127^{commit}                   # alguma branch?
   git for-each-ref --contains v0.3.127^{commit} refs/heads refs/remotes
   ```

   Se nenhuma branch contém esse commit, **é um commit órfão** — só sobrevive porque a tag o referencia. Estado C.

---

## Fase 2 — Caminho feliz (estado A)

Tag não existe em lugar nenhum. Procedimento canônico:

1. **Criar tag anotada (nunca leve) apontando para HEAD**

   ```bash
   git tag -a v0.3.127 -m "Release 0.3.127"
   # ou assinada, se o repo exige:
   # git tag -s v0.3.127 -m "Release 0.3.127"
   ```

   - Anotada (`-a`) carrega autor, data e mensagem; é o que GitHub Releases consome.
   - Lightweight (`git tag v0.3.127` sem `-a`) é um ref nu — frágil, não recomendado para release.

2. **Re-verificar antes de publicar**

   ```bash
   git rev-parse v0.3.127^{commit}     # deve bater com HEAD
   git tag --verify v0.3.127 2>/dev/null || git cat-file -p v0.3.127 | head
   ```

3. **Publicar a tag explicitamente, sem `--force`**

   ```bash
   git push origin refs/tags/v0.3.127
   ```

   Usar o refspec completo (`refs/tags/...`) evita que algum push.followTags ou alias dispare side effects. **Nunca** usar `git push --tags --force` aqui.

4. **Confirmar que o remoto aceitou**

   ```bash
   git ls-remote --tags origin v0.3.127
   ```

5. **Confirmar a release no GitHub (se houver automação)**

   - Se há workflow disparando em `push` de tag (npm publish, GitHub Release, build de bundle público), abrir Actions e acompanhar.
   - Antes de declarar pronto: confirmar que o `dist/` publicado, o `npm view tilly-engineer-skills@0.3.127` (se aplicável) e o GitHub Release casam com o SHA da tag.

---

## Fase 3 — Tag pública já existe (estado D)

**Regra de ouro: tag publicada não se reescreve.** Sobrescrever altera artefatos que consumidores já podem ter cacheado (npm, CDN, GitHub Release assets, mirrors). Esse é exatamente o tipo de "sobrescrita silenciosa" que a pergunta quer evitar.

1. **Comparar a tag remota com o commit do bump**

   ```bash
   git fetch --tags origin
   REMOTE=$(git rev-parse refs/tags/v0.3.127^{commit})
   LOCAL=$(git rev-parse HEAD)
   echo "remote=$REMOTE local=$LOCAL"
   ```

2. **Se REMOTE == LOCAL**: a tag já está correta, alguém só não comunicou. Verificar consistência da release no GitHub/npm. Não republicar.

3. **Se REMOTE != LOCAL**: incidente. Decisões válidas:
   - **Preferida**: abandonar `0.3.127`, bumpar para `0.3.128` e seguir. Custo: um número de versão. Benefício: zero risco de quebrar consumidores.
   - **Excepcional** (somente se ninguém consumiu ainda — checar npm downloads, GitHub Release downloads, mirrors):
     1. Documentar a decisão (commit em `docs/`, abrir issue, anotar no CHANGELOG/CONTRACT-HISTORY).
     2. Deletar a tag remota: `git push origin :refs/tags/v0.3.127`.
     3. Deletar a release GitHub associada (UI ou `gh release delete v0.3.127`).
     4. Re-rodar Fase 2.
   - Nunca usar `git push --force refs/tags/v0.3.127` cegamente.

---

## Fase 4 — Tag local existe e aponta para commit órfão (estado C)

Esse é o caso espinhoso citado na pergunta. Sintoma: `git tag` mostra `v0.3.127`, mas `git rev-parse v0.3.127^{commit}` retorna um SHA que **nenhuma branch contém**.

Origens prováveis:
- Tentativa anterior de release foi abortada com `git reset --hard` ou rebase que descartou o commit, mas a tag sobreviveu e ancorou o commit no reflog/objeto.
- Stash ou cherry-pick experimental marcado por engano.
- Resíduo de outra máquina sincronizado via `git fetch`.

Procedimento:

1. **Inspecionar o commit órfão antes de descartar**

   ```bash
   ORPHAN=$(git rev-parse v0.3.127^{commit})
   git show --stat $ORPHAN
   git show $ORPHAN:package.json | grep version
   git diff HEAD $ORPHAN -- package.json scripts dist docs
   ```

   - Confirmar que o conteúdo do órfão é equivalente ou inferior ao HEAD atual.
   - Se o órfão tiver algo que o HEAD não tem (ex: um patch que ficou de fora do bump), **parar** e reconciliar via cherry-pick **antes** de tocar na tag.

2. **Confirmar que a tag órfã nunca foi pública**

   ```bash
   git ls-remote --tags origin v0.3.127     # tem que ser vazio; senão, vai para Fase 3
   ```

3. **Deletar somente a tag local**

   ```bash
   git tag -d v0.3.127
   ```

   Isso não muta nada remoto. O commit órfão fica acessível via reflog por ~90 dias, então é reversível.

4. **Recriar a tag em cima do HEAD correto** (Fase 2 a partir do passo 1).

5. **Antes de fazer push, repetir Fase 1 inteira** — paranoia justificada: confirmar que entre a deleção local e o `tag -a` ninguém empurrou `v0.3.127` no remoto.

---

## Fase 5 — Tag local correta mas não publicada (estado B)

Caso comum quando alguém já fez `git tag -a` antes e esqueceu o push.

1. Confirmar que `v0.3.127^{commit}` == `HEAD` (Fase 1, passo 3).
2. Confirmar que `git ls-remote --tags origin v0.3.127` está vazio.
3. Publicar como na Fase 2, passos 3 e 4.

---

## Checklist final (independente do estado)

Antes de declarar a release como pronta:

- [ ] `package.json` na tag diz `0.3.127`.
- [ ] `git rev-parse v0.3.127^{commit}` == SHA do commit de bump em `main`.
- [ ] `git ls-remote --tags origin v0.3.127` retorna o mesmo SHA peeled.
- [ ] Nenhum commit órfão foi referenciado pela tag final.
- [ ] CHANGELOG / CONTRACT-HISTORY / release notes mencionam `0.3.127`.
- [ ] Workflow de release (se existir) terminou verde.
- [ ] Artefatos públicos (npm, bundle, dist) batem com o SHA da tag.
- [ ] Nenhum `--force` foi usado no caminho.

---

## Anti-padrões a evitar explicitamente

- `git push --tags` em massa: arrasta tags antigas/experimentais sem querer.
- `git push --force` ou `git push -f refs/tags/...`: reescreve tag pública.
- `git tag -f v0.3.127`: substitui silenciosamente uma tag local sem alertar.
- Criar tag **antes** de confirmar `origin/main == HEAD`: a tag pode ficar apontando para um commit que ninguém mais tem.
- Criar release no GitHub via UI antes de a tag estar publicada via git: gera tag lightweight desalinhada com o que o `commit:check` validou.
- Confiar em `git tag` local sem `git fetch --tags --prune-tags`: tags deletadas no remoto continuam fantasmas localmente.

---

## Resumo executivo

1. Snapshot read-only do estado (HEAD, branch, working tree, sync com origin, versão no package.json).
2. `git fetch --tags --prune-tags` e classificar o estado de `v0.3.127` em A/B/C/D.
3. Estado A (não existe): `git tag -a` em HEAD, `git push origin refs/tags/v0.3.127`, verificar.
4. Estado B (local OK, falta push): só publicar.
5. Estado C (local aponta para órfão, remoto vazio): inspecionar órfão, `git tag -d` local, recriar em HEAD, publicar.
6. Estado D (tag remota existe): **não sobrescrever**; comparar SHAs; se divergente, preferir bumpar para `0.3.128`.
7. Checklist final antes de fechar.
