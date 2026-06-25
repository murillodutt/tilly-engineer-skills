# Plano de sync — docs/governance/SYNC-AUDIT-CHECKLIST.md + docs/INDEX.md

> Read-only. Nenhum comando de escrita rodado. Tudo abaixo é o roteiro que **você** vai executar (ou autorizar) depois.

## Scope

**No bump.** Justificativa em uma frase: `tes_bump.py --governance-check` retorna `PASS` e o diff toca apenas `docs/governance/**` (uma seção de rollback) e `docs/INDEX.md` (uma entrada nova) — nenhuma dessas superfícies move comportamento entregue (skill body, oracle, installer refs, i18n, bundle, plugin manifests), portanto a tabela de scopes do `SKILL.md` e o heurístico de `references/bump-scope.md` resolvem direto para No bump.

Por que **não** é source-only nem bundle:

- Source-only exigiria `NEEDS_VERSION_DECISION` no governance-check (não é o caso aqui — está `PASS`).
- Bundle exigiria mudança observável por adopter via instalador, skill ou oracle (não é o caso — governança + índice de docs são internos e não materializados).
- A regra de bolso do `bump-scope.md`: "Yes (skill body, oracle exit code, installer copy, command surface) → bundle scope. No (test fixtures, internal docs, governance) → no bump." Cai exatamente no ramo "No".

## Plan (fases que rodam vs. fases que pulam)

Mapeando contra os 12 passos do `SKILL.md`:

| # | Fase | Ação |
|---|------|------|
| 1 | Pre-flight | **Rodar** |
| 2 | Scope decision | **Anunciar** "No bump" antes de qualquer write |
| 3 | Source identity bump | **Pular** (sem bump) — declarar skip explicitamente |
| 4 | Public refs + i18n | **Pular** — declarar skip |
| 5 | Publish bundle | **Pular** — declarar skip |
| 6 | Regenerate public HTML | **Pular** — declarar skip |
| 7 | Final validation | **Rodar** (commit:check + governance-check) |
| 8 | Commit | **Rodar** |
| 9 | Push | **Rodar** (`git push origin main`) |
| 10 | Tag | **Pular** — tags só no bundle scope; declarar skip |
| 11 | Release certification (`release:check`) | **Pular** — só no bundle scope |
| 12 | Closeout | **Rodar** (relatório curto) |

A Output Shape do skill manda declarar cada skip explicitamente para auditoria — isso é importante porque o reviewer humano (ou um agente futuro relendo o log) precisa ver que pular não foi esquecimento.

## Active phase (o que rodar agora — quando você liberar)

### Phase 1 — Pre-flight

```bash
git status -sb
python3 scripts/tes_bump.py --governance-check
```

Pós-condição esperada:

- `git status -sb` mostra exatamente dois arquivos modificados (`docs/governance/SYNC-AUDIT-CHECKLIST.md` e `docs/INDEX.md`), nenhum arquivo surpresa em `.tes/`, `docs/dist/`, ou diffs largos em `scripts/`, `src/`, `docs/i18n/`.
- `governance-check` reconfirma `PASS: version bump surfaces are synchronized` (já confirmado pelo usuário, mas reexecutar elimina drift de estado entre a última checagem e o commit).

Se o status mostrar algo além dos dois arquivos, **parar** e abrir a decisão de novo — provavelmente é outra mudança não declarada.

### Phase 7 — Final validation

```bash
git add docs/governance/SYNC-AUDIT-CHECKLIST.md docs/INDEX.md
npm run commit:check
python3 scripts/tes_bump.py --governance-check
```

Notas:

- Stage explícito por path (não `git add -A`) para garantir que arquivos não-relacionados não entrem por acidente. O lock do skill diz "Diff scope is intentional".
- `npm run commit:check` é **não-opcional**, mesmo no scope No bump. Está nos Locks: "Do not push ... without `npm run commit:check` PASS." A suíte de 33 gates pega `docs/INDEX.md` desalinhado com `DOCS-INDEX.yml`, link quebrado, doc size estourado, etc. — exatamente os modos de falha plausíveis para esse diff.
- Governance-check final é o terceiro PASS da cadeia (você → pre-flight → final).

Pós-condição: `commit:check` termina sem `FAIL`/`BLOCKER`; governance reimprime `PASS`.

### Phase 8 — Commit

Mensagem deve seguir o template do skill. Sugestão concreta para esse diff:

```bash
git commit -m "$(cat <<'EOF'
docs(governance): document rollback path in sync audit checklist

Closes the gap reviewers hit when a partial sync needs to be reverted
mid-flight: the rollback procedure now lives next to the checklist
that fails the audit. INDEX entry added so the new section is
discoverable from the docs root.

No bump: governance + docs/INDEX only; tes_bump.py --governance-check
returns PASS. Identity surfaces, i18n, bundle, public HTML, and tag
phases intentionally skipped per tes-sync No-bump scope.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

Pontos da mensagem que o skill exige/recomenda:

- Tipo + escopo na primeira linha (`docs(governance):`).
- Parágrafo de "por que" (failure pattern fechado).
- **Declaração explícita do scope ("No bump") com motivo** — equivale ao "bump scope statement" que o skill usa nos bumps; aqui registra a decisão de não bumpar.
- Linha de skips explicita, para auditoria.
- Trailer Co-Authored-By.

Pós-commit:

```bash
git status
git log -1 --stat
```

Verificar que só os dois arquivos esperados aparecem no `--stat`.

### Phase 9 — Push

```bash
git push origin main
git status -sb
```

Pós-condição: `## main...origin/main` sem `[ahead]` nem `[behind]`.

### Phase 12 — Closeout

Relatar em um bloco:

- **Claim final:** PASS (No bump scope, dois arquivos sincronizados, commit:check verde, governance PASS pré e pós).
- **Commit hash:** preencher após o push.
- **Tag / bundle sha:** N/A (scope No bump — sem tag, sem bundle).
- **Evidence packet:** se a sessão tem packet ativo, anexar o caminho; caso contrário declarar "no certification packet (scope No bump)".
- **Limits / follow-ups:** confirmar que `SYNC-AUDIT-CHECKLIST.md` e `DOCS-INDEX.yml` continuam consistentes (o entry novo no INDEX precisa estar refletido no `DOCS-INDEX.yml` se a política exigir — `commit:check` confirma isso, mas vale citar).

## Trap watch (dado este diff específico)

Mesmo no scope mais leve, três armadilhas plausíveis aqui:

1. **`docs/INDEX.md` x `docs/tds/DOCS-INDEX.yml` drift.** Adicionar entry no INDEX sem refletir no YAML (ou vice-versa) é o modo de falha mais provável. O `commit:check` tem gate de parity entre os dois — se falhar, ajustar o YAML, **não** baixar o gate.
2. **Doc size budget no `SYNC-AUDIT-CHECKLIST.md`.** Adicionar uma seção pode estourar o budget de `validate_doc_size.py`. Lock do skill: "Do not raise `validate_doc_size.py` budgets to make a doc fit. Modularize and link from the parent." Se estourar, mover a seção de rollback para `docs/governance/rollback/` (ou `references/`) e linkar a partir do checklist.
3. **Tentação de "já que estou aqui, bumpar."** Não. Governance retornou `PASS`. Bumpar sem `NEEDS_VERSION_DECISION` cria uma release vazia que polui tag/bundle history. Manter No bump.

Não-aplicáveis (mas vale registrar para auditoria do skill em si):

- `bundle_sha256` mismatch — N/A (sem publish).
- Tag stale em `origin` — N/A (sem tag novo).
- `validate_reference_package.py` zip filename trap — N/A (sem bundle).

## Resumo executivo

Scope: **No bump**. Rodar fases 1, 2, 7, 8, 9, 12. Pular 3, 4, 5, 6, 10, 11 (declarando cada skip no commit message e no closeout). Commit nominal por path, `npm run commit:check` obrigatório antes do push, governance-check final como terceira confirmação, push para `origin/main`, sem tag, sem `release:check`. Trap principal a vigiar: parity entre `docs/INDEX.md` e `docs/tds/DOCS-INDEX.yml` — o `commit:check` decide.
