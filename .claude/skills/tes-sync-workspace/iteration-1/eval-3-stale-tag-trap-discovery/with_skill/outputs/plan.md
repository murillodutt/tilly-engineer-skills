# Procedimento de Tagging Seguro — v0.3.127

Contexto: bump `0.3.126 -> 0.3.127` já commitado, `npm run commit:check` verde, push para `main` feito. Falta criar `v0.3.127` sem sobrescrever silenciosamente nenhum artefato público.

A skill `tes-sync` (fase 10 — *Tag*) e o reference `references/tag-conflict-resolution.md` definem a rotina abaixo. Tags são artefatos públicos: nunca mover sem autorização explícita do usuário.

---

## Mantra

> Tags são artefatos públicos. Inspecionar antes de tocar, nunca sobrescrever em silêncio, sempre citar o conflito ao usuário.

A pressa de "só dar `git tag -f`" é exatamente o que criou o trap do 0.3.124: um `v0.3.124` apontando para `9877682` (commit órfão, bump abandonado) sobreviveu no remoto. Quem rodasse `npx ... #v0.3.124` recebia o source abandonado — não o release real em `main`.

---

## Fase 0 — Pré-condições (já satisfeitas, registrar)

Confirmar antes de qualquer escrita:

```bash
git status -sb                         # deve mostrar "## main...origin/main" limpo
git rev-parse HEAD                     # capturar HEAD_HASH
python3 scripts/tes_bump.py --governance-check
# esperado: PASS: version bump surfaces are synchronized
```

Se `commit:check` ou `--governance-check` regrediram desde o push, **pare**: a tag não pode subir antes da identidade estar sincronizada.

---

## Fase 1 — Diagnóstico da tag (ordem obrigatória)

Executar os seis passos do reference `tag-conflict-resolution.md` e registrar cada saída. Não pular nenhum — o trap mora exatamente em quando o local e o remoto discordam.

```bash
# 1. A tag existe localmente?
git tag -l v0.3.127

# 2. A tag existe no remoto?
git ls-remote --tags origin v0.3.127

# 3. Para onde a tag aponta localmente?
git rev-list -n 1 v0.3.127 2>/dev/null || echo "(no local tag)"

# 4. Para onde a tag aponta no remoto (dereferenciada)?
git ls-remote --tags origin 'v0.3.127^{}'

# 5. Onde está HEAD?
git rev-parse HEAD

# 6. (3), (4) e (5) coincidem?
```

Capturar `HEAD_HASH`, `LOCAL_TAG_HASH`, `REMOTE_TAG_HASH` antes de decidir. Comparar manualmente — não confiar em uma única linha de saída.

---

## Fase 2 — Decisão por caso

Mapear o resultado dos seis passos a um dos casos abaixo. Anunciar qual caso aplica antes de qualquer comando destrutivo.

### Caso A — tag não existe em lugar nenhum

Cenário esperado para um bump normal. Seguro criar e publicar:

```bash
git tag -a v0.3.127 -m "Release 0.3.127 — <rationale curto + caminho da evidência>"
git rev-list -n 1 v0.3.127            # deve igualar HEAD_HASH
git push origin v0.3.127
git ls-remote --tags origin 'v0.3.127^{}'   # confirma no remoto
```

Ir para Fase 3.

### Caso B — tag local existe e aponta para HEAD, remoto não tem

Tag local válida, só falta publicar:

```bash
git rev-list -n 1 v0.3.127            # deve igualar HEAD_HASH; se não, ir ao Caso D
git push origin v0.3.127
git ls-remote --tags origin 'v0.3.127^{}'
```

Ir para Fase 3.

### Caso C — local e remoto apontam para HEAD

Tag já está publicada e correta. Nada a fazer. Pular direto para `npm run release:check` (Fase 3) para certificar.

### Caso D — tag aponta para um commit antigo, local ou remotamente (TRAP)

**Parar imediatamente.** Este é o cenário do enunciado ("tag já existe apontando para commit órfão") e o que mordeu 0.3.124. Não executar `git tag -f`, não executar `git push --force`, não deletar nada.

Citar o conflito ao usuário, literalmente, e esperar autorização explícita:

```
Tag v0.3.127 já existe, apontando para <LOCAL_TAG_HASH ou REMOTE_TAG_HASH>.
HEAD está em <HEAD_HASH>.

O commit <hash-antigo> aparenta ser <órfão / branch abandonada / bump
revertido — descrever o que git log mostra sobre ele, sem suposição>.

Para mover a tag para HEAD, preciso deletar a tag local, deletar a tag
remota e recriar. Isso reescreve a identidade pública do release
v0.3.127. Posso prosseguir?
```

Enquanto não houver autorização, oferecer alternativas não destrutivas:

1. **Bump para 0.3.128** — pula o conflito, deixa a tag órfã intocada mas não usada. Custo: queima um número de patch e exige refazer bump+commit+push.
2. **Investigar a origem do tag órfão** — `git log <hash-antigo>`, `git branch --contains <hash-antigo>`, `git reflog`. Necessário antes de qualquer cleanup permanente.
3. **Postergar cleanup** — documentar o conflito em `docs/governance/` e tratar em uma janela dedicada de manutenção.

Se autorização chegar, ir para Caso E. Se for negada, abortar o sync e deixar o estado anotado no closeout.

### Caso E — movimentação autorizada (somente após "sim" explícito)

Sequência exata do reference. Cada passo verifica a invariante antes de prosseguir:

```bash
# 1. Capturar o estado anterior para o registro do release
PREV_TAG_HASH=$(git rev-list -n 1 v0.3.127 2>/dev/null || \
                git ls-remote --tags origin 'v0.3.127^{}' | awk '{print $1}')
echo "Tag v0.3.127 movida de ${PREV_TAG_HASH} para $(git rev-parse HEAD)" \
  >> docs/evidence/<packet>/tag-move.log

# 2. Deletar local
git tag -d v0.3.127

# 3. Deletar remoto
git push origin :refs/tags/v0.3.127

# 4. Confirmar que sumiu dos dois lados antes de recriar
git tag -l v0.3.127                          # vazio
git ls-remote --tags origin v0.3.127         # vazio

# 5. Criar anotada em HEAD
git tag -a v0.3.127 -m "Release 0.3.127 — <rationale + evidência>; supersedes ${PREV_TAG_HASH}"

# 6. Verificar localmente
git rev-list -n 1 v0.3.127                   # === git rev-parse HEAD

# 7. Publicar
git push origin v0.3.127

# 8. Verificar no remoto
git ls-remote --tags origin 'v0.3.127^{}'    # === git rev-parse HEAD
```

Só seguir para Fase 3 se os passos 6 e 8 retornarem exatamente `HEAD_HASH`.

---

## Fase 3 — Certificação do release

Tag publicada não é tag certificada. Rodar:

```bash
npm run release:check
```

Resultado obrigatório:

- `status: PASS`
- `classification: certified_local`
- `resolved_commit` === `git rev-parse HEAD`

Qualquer outra saída significa que tag e source desviaram. **Parar e reconciliar** — não tentar consertar empurrando outra tag por cima.

---

## Fase 4 — Closeout

Reportar em bloco único:

- Caso aplicado (A / B / C / D-abortado / E-autorizado).
- `HEAD_HASH`, `v0.3.127 -> <hash>`, sha do bundle público.
- Caminho do evidence packet (`docs/evidence/<packet>/`).
- Se foi Caso E: link para `tag-move.log` registrando o `PREV_TAG_HASH` superseded.
- Limites e follow-ups (ex.: investigar a origem do órfão se ainda não feito).

---

## Locks aplicáveis (skill `tes-sync`)

- **Não mover tag pública sem autorização.** O Caso D existe para forçar a citação do conflito ao usuário.
- **Não pular `npm run commit:check`.** Tag sem o suite de 33 gates verde pode estar publicando um bundle com sha desalinhado.
- **Não pular `release:check`.** Tag empurrada sem certificação não conta como release fechado.
- **Não fazer `git push --force` em refs/tags.** A sequência correta é deletar-no-remoto + recriar, com autorização explícita.
- **Nunca usar `git tag -f` para "consertar rápido".** Reescreve a identidade local sem deixar rastro do hash antigo.

---

## Resumo executável (caminho feliz, Caso A)

```bash
# 0. Pré-flight
git status -sb
python3 scripts/tes_bump.py --governance-check

# 1. Diagnóstico (todos os seis passos)
git tag -l v0.3.127
git ls-remote --tags origin v0.3.127
git rev-list -n 1 v0.3.127 2>/dev/null || echo "(no local tag)"
git ls-remote --tags origin 'v0.3.127^{}'
git rev-parse HEAD

# 2. Caso A — criar e publicar
git tag -a v0.3.127 -m "Release 0.3.127 — <rationale>; evidence: <path>"
git rev-list -n 1 v0.3.127    # === HEAD
git push origin v0.3.127
git ls-remote --tags origin 'v0.3.127^{}'   # === HEAD

# 3. Certificar
npm run release:check         # PASS / certified_local / resolved_commit === HEAD
```

Para qualquer outro caso, voltar à Fase 1 e tratar conforme a árvore de decisão. **Em dúvida, parar e perguntar.**
