---
tds_id: evidence.canary_gap_repair_admission_alignment.journal_20260630
tds_class: evidence
status: active
consumer: maintainers, Claude Opus execution agents, installer authors, oracle authors, canary operators
source_of_truth: false
evidence_level: L2
---

# Canary Gap Repair And Admission Alignment Journal

- SPEC: GOAL-SUPER-SPEC-tes-canary-gap-repair-and-admission-alignment
- Journal reference read: docs/evidence/reports/2026/06/30/canary-pre-goal-maestro-cleanroom-fix-20260630T132334Z-tes-canary-pre-goal-maestro-cleanroom-fix/JOURNAL.md @ 2026-06-30T15:25:53Z
- Executor host: Claude Code
- Executor model: Claude Opus 4.8 Max (claude-opus-4-8[1m])
- Started UTC: 2026-06-30T15:25:53Z
- Package source: /Users/murillo/Dev/tilly-engineer-skills
- Canary root: /Users/murillo/Dev/tes-canaries/tmp-replay-0.3.231-20260630092532
- Cleanroom assertion: no canary writes, no slash-skill execution, no Goal
  Maestro execution, no MCP memory writes, no remote actions.

## Reference Journal Reuse And Drift Avoidance

- Reference path: docs/evidence/reports/2026/06/30/canary-pre-goal-maestro-cleanroom-fix-20260630T132334Z-tes-canary-pre-goal-maestro-cleanroom-fix/JOURNAL.md
- UTC read: 2026-06-30T15:25:53Z
- Audit practices reused: per-action UTC entries with intent/precondition/exact
  command/exit code/proof-before/proof-after; explicit stop states; final audit
  handoff; recording of failed/skipped gates (e.g. prior run recorded
  tes_init --self-test FAIL openly).
- How this SPEC avoids prior drift:
  - Stale HEADs: this SPEC is package-source only; no canary Git HEAD claims are
    made. Any commit hash recorded is captured live with git rev-parse at write
    time, never copied forward.
  - Thin command logs: every material action logs the exact command and exit code.
  - Omitted failed attempts: failed self-tests/gates are recorded as failures,
    never silently dropped or relabeled PASS.
  - Report-only proof: each gap fix requires a red-capable fixture/self-test, not
    prose. Oracle exit codes are captured.
  - Skipped gates hidden as PASS: npm run commit:check is required and its real
    result recorded; if a gate is skipped the reason is stated.

## 2026-06-30T15:25:53Z - SPEC-000/001 Reference gate + read-only reconfirmation

- Phase: SPEC-000 | SPEC-001
- Actor/host: Claude Code (Opus 4.8 Max)
- Working directory: /Users/murillo/Dev/tilly-engineer-skills
- Intent: Confirm journal reference, establish evidence packet, reconfirm the
  four confirmed gaps read-only against canary root and prove the local bundle.
- Precondition: paths explicit; reference JOURNAL.md present.
- Command(s):
  ```bash
  test -f <reference JOURNAL.md>   # exit 0
  git -C <canary>/{cursor,claude,codex} rev-parse --is-inside-work-tree
  find <canary> for hooks + __pycache__/*.pyc
  jq postinstall.json / manifest.json
  shasum -a 256 <BUNDLE_PATH>; cat <BUNDLE_PATH>.sha256
  unzip -p <BUNDLE_PATH> tes-bundle-manifest.json | jq summary
  ```
- Exit code(s): all read probes 0
- Files read: reference JOURNAL.md; canary postinstall.json/manifest.json; bundle manifest
- Files written: PREFLIGHT.md, JOURNAL.md (this file)
- Proof before: gaps asserted by prior audit
- Proof after (live, this run):
  - Canary root tmp-replay-0.3.231-20260630092532: all 3 targets are Git work
    trees; only .git/hooks/pre-push present (no pre-commit); no
    .pre-commit-config.yaml / lefthook.yml.
  - postinstall.json: state=complete, last_status=PASS, BUT advisory
    mesh.scaffold_only STILL ACTIVE (Gap 3 reproduced).
  - manifest.json: 379 entries, source_commit d05b050a (Gap 2: differs from
    bundle 378 / 7a664a93).
  - bytecode __pycache__/*.pyc present under delivered skill
    tes-engineering-discipline/scripts AND .tes/bin (Gap 4 reproduced).
  - Bundle: SHA 565ccb30 matches sidecar; manifest version 0.3.231,
    source_commit 7a664a93, entry_count 378, pycache 0 (bundle itself clean).
- Evidence written: PREFLIGHT.md
- Result: All four gap symptoms reconfirmed read-only; bundle ZIP clean; canary
  staging/runtime carries bytecode the ZIP does not.
- Decision: proceed to gap classification (SPEC-002). No canary writes performed.
- Stop state after this entry: NEEDS_GAP_CLASSIFICATION
- Next action: Read authority sources; write GAP-CLASSIFICATION.md.

## 2026-06-30T15:36:04Z - SPEC-002 Gap classification

- Phase: SPEC-002
- Actor/host: Claude Code (Opus 4.8 Max)
- Working directory: /Users/murillo/Dev/tilly-engineer-skills
- Intent: Read authority sources + harness hook docs, classify all four gaps,
  decide package-fix architecture before any patch.
- Precondition: read-only reconfirmation complete (PREFLIGHT.md); baseline
  self-tests green.
- Command(s):
  ```bash
  # parallel recon workflow (12 agents, Opus only) over authority docs + oracles
  # claude-code-guide agent over official Claude/Codex/Cursor hook docs
  # baseline self-tests for every changed surface
  PYTHONDONTWRITEBYTECODE=1 $PY scripts/<surface>.py --self-test   # all exit 0
  ```
- Exit code(s): baseline self-tests all 0; validate_reference_package exit 1
  ONLY from (a) empty spurious root .cursor dir [removed] and (b) this run's
  not-yet-indexed evidence files [will be TDS-indexed at closeout].
- Files read: INSTALL.md, COMMAND-TRIGGERS.md, INSTALLATION-FRAMEWORK.md,
  installed_certification_oracle.py, public_bundle_oracle.py, tes_bundle.py
  (residue/iter_files), tes_install.py (collect_advisories, postinstall,
  hook_health_payload), project_alignment_oracle.py (freshness),
  field_reports.py (pre-push), project_context_oracle.py (git).
- Files written: GAP-CLASSIFICATION.md
- Proof before: gaps asserted by prior audit
- Proof after: each gap classified with source/contract/oracle/canary-state
  decomposition; fix architecture decided.
- Evidence written: GAP-CLASSIFICATION.md
- Result: Architecture: (Gap1+Gap4 admission) NEW canary_admission_oracle.py;
  (Gap2) bytecode hygiene across tes_bundle/public_bundle_oracle/
  installed_certification_oracle; (Gap3) run-scoped advisories +
  post-align refresh in tes_install.py.
- Decision: proceed to SPEC-004 bytecode hygiene first (smallest, source-proven),
  then SPEC-005 advisory, then SPEC-003+006 admission oracle.
- Stop state after this entry: NEEDS_SOURCE_FIX
- Next action: SPEC-004 bytecode hygiene patch + red fixtures.

## 2026-06-30T16:06:36Z - SPEC-004/005/003/006 source + oracle fixes

- Phase: SPEC-004 | SPEC-005 | SPEC-003 | SPEC-006
- Actor/host: Claude Code (Opus 4.8 Max)
- Working directory: /Users/murillo/Dev/tilly-engineer-skills
- Intent: Patch package source/oracles for the four gaps; each with a
  red-capable fixture.
- Precondition: baseline self-tests green; GAP-CLASSIFICATION written.
- Command(s):
  ```bash
  PYTHONDONTWRITEBYTECODE=1 $PY scripts/tes_bundle.py --self-test
  PYTHONDONTWRITEBYTECODE=1 $PY scripts/installed_certification_oracle.py --self-test
  PYTHONDONTWRITEBYTECODE=1 $PY scripts/tes_install.py --self-test
  PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=scripts $PY scripts/canary_admission_oracle.py --self-test
  # red-capability proofs by neutralizing each detector (see ORACLE-RESULTS.md)
  ```
- Exit code(s): all self-tests 0; every red-capability neutralization produced
  the expected FAIL, then restored to PASS.
- Files written (source): scripts/tes_bundle.py, scripts/public_bundle_oracle.py,
  scripts/installed_certification_oracle.py, scripts/tes_install.py,
  scripts/canary_admission_oracle.py (NEW).
- Files written (docs): docs/architecture/INSTALLATION-FRAMEWORK.md,
  docs/install/AGENT-ORACLE-INVENTORY.md.
- Proof before: gaps reproduced read-only.
- Proof after: all four gaps closed with falsifiable fixtures; see
  SOURCE-CHANGES.md + ORACLE-RESULTS.md.
- Result: Gap2 bytecode hygiene; Gap3 run-scoped advisories + cleared scaffold;
  Gap1 Git admission gate; Gap4 per-host hook truthfulness + no cross-host fill.
- Decision: delivered behavior changed -> release-identity decision required.
- Stop state after this entry: NEEDS_RELEASE_IDENTITY_DECISION
- Next action: owner release-identity decision; bundle refresh.

## 2026-06-30T16:06:36Z - SPEC-007/008 release identity, bump, bundle refresh, validation

- Phase: SPEC-007 | SPEC-008
- Actor/host: Claude Code (Opus 4.8 Max)
- Intent: Owner-confirmed patch bump + local bundle refresh; run full validation.
- Precondition: all source self-tests green.
- Command(s):
  ```bash
  $PY scripts/tes_bump.py patch --yes              # 0.3.231 -> 0.3.232 (70 surfaces)
  $PY scripts/build_public_docs.py                 # regen index.html + USER-MANUAL.html
  PYTHONDONTWRITEBYTECODE=1 $PY scripts/tes_bundle.py publish --adapter all
  PYTHONDONTWRITEBYTECODE=1 $PY scripts/public_bundle_oracle.py
  PYTHONDONTWRITEBYTECODE=1 $PY scripts/install_smoke.py --self-test
  PYTHONDONTWRITEBYTECODE=1 $PY scripts/validate_tds.py
  PYTHONDONTWRITEBYTECODE=1 $PY scripts/validate_doc_size.py
  git add -A && PYTHONDONTWRITEBYTECODE=1 $PY scripts/staged_commit_gate.py   # npm run commit:check
  ```
- Exit code(s): bump 70 updated; build_public_docs PASS; publish BUILT;
  public_bundle_oracle PASS; install_smoke PASS; validate_tds PASS;
  validate_doc_size 0; commit:check PASS (staged_files 81).
- Owner decision: bump 0.3.231 -> 0.3.232, local refresh, NO push/tag/publish.
- Files written: 70-surface version bump + new bundle docs/dist/0.3.232/** ;
  pruned docs/dist/0.3.231/**; canary_admission_oracle VERSION -> 0.3.232;
  TDS index +8 evidence entries.
- Proof after: bundle 0.3.232 sha b77c3183..., 378 entries, pycache 0;
  validate_reference_package PASS (254 files); validate_tds PASS (264 docs).
- Result: package-ready, not release-sealed.
- Stop state after this entry: NEEDS_CANARY_REPLAY_HANDOFF -> resolved
- Next action: write handoff + final admission.

## Final Audit Handoff

- Final status: PACKAGE_READY_FOR_CANARY_REPLAY
- Remaining stop state: none (package readiness). NOT release-sealed (no
  commit:closure, no tag, no release:check, no push).
- Confirmed gaps: all four classified (GAP-CLASSIFICATION.md) and fixed.
- Source files changed: scripts/tes_bundle.py, scripts/public_bundle_oracle.py,
  scripts/installed_certification_oracle.py, scripts/tes_install.py,
  scripts/canary_admission_oracle.py (NEW), + 70-surface version bump.
- Docs/evidence files changed: docs/architecture/INSTALLATION-FRAMEWORK.md,
  docs/install/AGENT-ORACLE-INVENTORY.md, docs/tds/DOCS-INDEX.yml, regenerated
  public HTMLs, and this evidence packet (8 files).
- Bundle status: refreshed to 0.3.232
  (sha b0f8eee3ad7b3ba115efcd2c3576042029ac2ef8b8573724758952826a88c987),
  378 entries, pycache 0; 0.3.231 pruned.
- Oracles passed: tes_bundle, installed_certification_oracle,
  canary_admission_oracle, public_bundle_oracle, tes_install, install_smoke,
  validate_tds, validate_doc_size, validate_reference_package, commit:check.
- Oracles failed or skipped: none failed. commit:closure NOT run (not a
  release/seal window); canary install/replay NOT run (out of scope by SPEC).
- Release identity decision: patch bump 0.3.231 -> 0.3.232 + local bundle
  refresh; no push/tag/publish; package-ready, not sealed.
- Canary replay requirements: see CANARY-REPLAY-HANDOFF.md (Git init first,
  install 0.3.232 bundle, setup/align/map, post-align postinstall refresh,
  pre-push, strict pre-commit, baseline commit, admission oracle PASS).
- Claims forbidden until replay: precommit_enforced, prepush_installed,
  git_clean, native Codex/Cursor hook PASS, no stale mesh.scaffold_only
  post-align, READY_FOR_GOAL_MAESTRO_CANARY.
- Exact next SPEC/session recommended: dedicated canary replay session per
  CANARY-REPLAY-HANDOFF.md against a freshly Git-initialized canary.
