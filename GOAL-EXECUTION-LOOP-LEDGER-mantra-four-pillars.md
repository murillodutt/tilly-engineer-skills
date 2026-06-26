# GOAL-EXECUTION-LOOP-LEDGER — Mantra Gate Senior Manager (Four Pillars)

Anchor: docs/adr/0006-decision-lens-evolution-and-routable-gate-closure.md (ADR, git hash-object 58a53a48323213922b0e0ccd459d60c5fdcfce8d)
Anchor (secundária): docs/adr/0005-asset-transfer-to-existing-surfaces.md (ADR, git hash-object f0c70274a1ed8a33d62720d3223bf43b6c5aca4f). Ambition: "furar o teto — os quatro pilares atendidos em ordem de gravidade".
Tree Adversary: OBJECTIONS_REPAIRED (band-oracle facade → re-mutação obrigatória; mirror drift → re-materializa do source). Sync: local-commit only (remote não autorizado).

Escopo: os QUATRO PILARES de execução (bootloader, skill, hook, agent) num loop, ordem de gravidade.
Decisões do owner (este loop):
- Release: construo tudo verde, PARO antes de bump/bundle. public_bundle_oracle red-esperado honesto. Release = autorização posterior do owner.
- /flash-fry: NÃO criar skill invocável (AUTO-ATIVO-only, gap declarado, ADR 0005).
Análise de base: workflow exaustivo 100% leitura-direta (5 leitores + 2 re-leituras), confrontado contra arquivos. Estado dos 4 pilares provado por file:line.

---

spec_id: SPEC-P-000
spec_version: 1
attempt: 1
first_unexecuted_unit: SPEC-P-001
commit: no-commit (preflight read-only, no material change)
oracle_status: PASS (5 substrings-piso presentes; AGENTS.md:40 ≡ .claude/CLAUDE.md:40; adoption_oracle/materialize/mantra_gate self-test exit 0)
evidence: as 4+ superfícies carregam as substrings; baseline protegida verde antes de tocar qualquer pilar.
sync: LOCAL_COMMITTED (preflight)

---

spec_id: SPEC-P-001
spec_version: 1
attempt: 1
failed_attempt_recovery_decision: bug_vs_architecture=bug_no_corpus (band-oracle confundia tier-de-classificação com ação-de-bloqueio; alinhado à semântica de dois-registros do bootloader, NÃO mexeu no runtime classify_risk)
pillar: 0 BOOTLOADER (camada-mãe)
commit: no-commit (sha registrado no corpo do commit que inclui este ledger)
files: AGENTS.md, .claude/CLAUDE.md (<mantra_gate> aditivo, byte-idênticos), scripts/mantra_gate_band_oracle.py (novo), package.json (wire)
oracle_status: PASS — band-oracle discrimina (risco→hard-gate high-risk/forbidden; benigno→supervisão routine/material); self-test pega sleeping+crywolf mutants (4/0); zero-regressão: adoption_oracle/materialize/no-regression/runtime exit 0
zero_regression: 5 substrings-piso byte-intactas; 2 espelhos byte-idênticos preservados; mantra_gate.py runtime untouched
release_identity: NENHUM bump — maintainer governance body (band-oracle não é HELPER_FILE; bootloaders raiz não em HELPER_FILES). Confirmado PLANTAO:146 Slice 1 "sem bump".
sync: LOCAL_COMMITTED (remote não autorizado)

---

spec_id: SPEC-P-002
spec_version: 1
attempt: 1
pillar: 1 SKILL (camada produto/source DELIVERED + camada desenvolvimento/dev-mirror)
commit: no-commit (sha no corpo do commit que inclui este ledger)
files: src/adapters/{claude,codex}/skills/tes-engineering-discipline/SKILL.md (SOURCE delivered), .claude/ + .agents/skills/tes-engineering-discipline/SKILL.md (DEV mirror, byte-idênticos entre si)
layer_separation: editei o SOURCE delivered (adopter recebe via materialização) E o DEV mirror (camada desenvolvimento, governa este agente) — NÃO confundi com a camada maintainer do Pilar 0 (bootloaders raiz). Cada camada tocada na sua superfície correta.
oracle_status: PASS — gerente sênior projetado nas 4 superfícies; substrings-piso byte-intactas; materialize --check/adoption(R4)/band-oracle/validate_reference_package exit 0; local-skill-parity preservada (.claude ≡ .agents)
flash_fry_decision: NÃO criado /flash-fry invocável (AUTO-ATIVO-only, gap declarado, ADR 0005) — decisão do owner
zero_regression: 5 substrings-piso intactas em todas as 4 superfícies; 2 dev mirrors byte-idênticos preservados
release_identity: DISPARA (SKILL.md é delivered — está no bundle 0.3.195 publicado). Drift delivered source↔bundle igual ao C8. Por decisão do owner: PARO antes do bump; red-esperado honesto; release = autorização posterior.
sync: LOCAL_COMMITTED (remote não autorizado)

---

spec_id: SPEC-P-002b (reparo — bootloaders de adapter, furo apontado pelo owner)
spec_version: 1
attempt: 1
pillar: 0/1 fronteira — BOOTLOADERS DE ADAPTER (camada produto/source DELIVERED)
commit: no-commit (sha no corpo do commit que inclui este ledger)
files: src/adapters/codex/AGENTS.md, src/adapters/claude/CLAUDE.md, src/adapters/cursor/rules/tes-engineering-discipline.mdc
gap_caught: o owner apontou que os bootloaders de src/adapters/** não foram tocados. Confirmado por git: nenhum commit anterior os tocou. Eu havia raciocinado errado ("roteiam para a skill, regra proíbe duplicar") e pulei a LINHA DE ROTEAMENTO, que ainda descrevia o gate em framing-piso — drift bootloader↔skill na própria camada delivered (inversão de gravidade em miniatura).
fix: linha de roteamento dos 3 bootloaders de adapter projeta o registro gerente-sênior ADITIVAMENTE, sem introduzir o protocolo dos 7 campos (regra BOOTLOADER_DUPLICATED_MANTRA_GATE_FRAGMENTS respeitada). CURSOR.md não toca o gate (roteia para .mdc) — correto, não editado.
oracle_status: PASS — materialize --check (duplicação+paridade) exit 0; substrings-piso intactas; fragmento proibido ausente; adoption/package exit 0
surfaces_promoted_total: 9 (2 maintainer raiz + 3 adapter bootloader + 4 skill source/dev) — nenhuma superfície de bootloader/skill ficou no piso
release_identity: DISPARA (bootloaders de adapter são delivered — no bundle 0.3.195). Drift delivered. PARO antes do bump (decisão do owner).
sync: LOCAL_COMMITTED (remote não autorizado)

---

spec_id: SPEC-P-003a (Pilar Hook — LÓGICA de decisão, wiring de instalação a seguir)
spec_version: 1
attempt: 1
failed_attempt_recovery_decision: bug_vs_architecture=architecture. Design inicial passava o comando shell cru a classify_risk (que keya em vocabulário de intenção, não shell) → 'rm -rf docs/adr' classificava routine (provado por execução). Reescrito para ancorar no sinal estrutural confiável: tool mutante + artefato governado, com classify_risk reforçando forbidden. Validado por execução antes do commit.
pillar: 2 HOOK (camada produto/source DELIVERED — handler em tes_install.py HELPER_FILE)
commit: no-commit (sha no corpo do commit que inclui este ledger)
files: scripts/tes_install.py (hook_pretooluse + _pretooluse_decision + dispatch PreToolUse, aditivo), scripts/mantra_gate_pretooluse_oracle.py (novo, maintainer-gate), package.json (wire)
oracle_status: PASS — handler discrimina por execução real nos 3 hosts: forbidden→Claude/Codex exit2+stderr / Cursor JSON permission:deny; governado+mutante→supervisiona (additionalContext, allow); benigno→silencioso (anti-cry-wolf por session dedup). Oráculo FALSIFICÁVEL provado: mutar Cursor-block→exit2 deixa oráculo RED (exit 1); restore→verde.
contract_divergence: HONRADA — Cursor JSON-permission ≠ exit-2 (Claude/Codex). Oráculo trava o colapso (Cursor não pode usar exit 2).
zero_regression: tes_install --self-test exit 0 (SessionStart intacto); dispatch PreToolUse aditivo antes do fluxo existente; validate_reference_package exit 0
remaining_in_pillar: wiring de instalação (install_*_pretooluse + remove_* ownership-strip + --self-test idempotência) — próximo passo separado (decisão do owner: commitar lógica primeiro, menor blast radius)
release_identity: DISPARA (tes_install.py é HELPER_FILE delivered). Drift delivered. PARO antes do bump (decisão do owner).
sync: LOCAL_COMMITTED (remote não autorizado)

---

spec_id: SPEC-P-003b (Pilar Hook — WIRING de instalação, completa o pilar)
spec_version: 1
attempt: 1
pillar: 2 HOOK (camada produto/source DELIVERED — tes_install.py HELPER_FILE)
commit: no-commit (sha no corpo do commit que inclui este ledger)
files: scripts/tes_install.py (CLAUDE_PRETOOLUSE_MATCHER, pretooluse_hook_entry, remove_tes_claude_event_hooks genérico, install_claude/cursor_pretooluse_hook, codex_pretooluse_snippet + install_codex_hook estendido, install_hooks orquestra, --self-test asserção PreToolUse)
oracle_status: PASS — install provado por execução nos 3 hosts: Claude grupo PreToolUse matcher Write|Edit|MultiEdit idempotente; Cursor preToolUse camelCase preserva foreign idempotente; Codex TOML [[hooks.PreToolUse]] idempotente SessionStart intacto. --self-test estende asserção PreToolUse e é FALSIFICÁVEL (desabilitar install → self-test RED exit 1; restore → verde).
contract_divergence: HONRADA — Claude PreToolUse / Cursor preToolUse (camelCase) / Codex TOML. Cada host seu evento e formato.
zero_regression: tes_install --self-test exit 0 (SessionStart intacto); foreign hooks preservados nos 3 hosts (echo keep/echo foreign); remove genérico só remove TES por ownership-marker
pillar_2_complete: lógica (c31fddac) + wiring (este) + 2 oráculos falsificáveis (handler + install)
release_identity: DISPARA (tes_install.py HELPER_FILE delivered). Drift delivered. PARO antes do bump (decisão do owner).
sync: LOCAL_COMMITTED (remote não autorizado)
