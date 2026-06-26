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
