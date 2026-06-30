---
tds_id: evidence.canary_gap_repair_admission_alignment.source_changes_20260630
tds_class: evidence
status: active
consumer: maintainers, oracle authors, release authors
source_of_truth: false
evidence_level: L2
---

# SOURCE-CHANGES — Package Source And Oracle Patches

Every changed package-source file, the gap it repairs, and its falsifiable
proof. Installed canary mirrors were NOT patched (cleanroom rule).

## SPEC-004 — Bundle and bytecode hygiene (Gap 2)

### `scripts/tes_bundle.py`
- Added `BUILD_ARTIFACT_DIR_NAMES` / `BUILD_ARTIFACT_SUFFIXES` constants and
  `is_build_artifact()` + `is_delivery_contaminant()` helpers — a contamination
  class distinct from OS residue, covering `__pycache__/` dirs and `*.pyc/*.pyo`.
- `purge_os_residue()` now purges build artifacts too (before staging/ZIP).
- `iter_files()` excludes build artifacts from adapter collection.
- `validate_manifest()` rejects any bytecode entry (falsifiable manifest guard).
- `build_bundle()` and `zip_extracted_public_bundle()` refuse to ZIP a bytecode
  member.
- `self_test()`: red-capable bytecode fixture — plants a `__pycache__/*.pyc`
  under a delivered adapter skill and asserts (a) purge before packaging,
  (b) absence from staged manifest, (c) `validate_manifest` rejects an explicit
  bytecode entry. Verified red-capable: neutralizing `is_build_artifact` flips
  the self-test to FAIL naming the purge + manifest-rejection failures.

### `scripts/public_bundle_oracle.py`
- ZIP-member scan now rejects Python bytecode members in addition to OS residue
  (`tes_bundle.is_build_artifact`). Falsifiable: the existing helper-drift guard
  correctly turned this oracle RED after the helper edits (see release identity).

### `scripts/installed_certification_oracle.py`
- Imports `tes_bundle`; reuses `is_build_artifact` (single source of truth, no
  new duplicated literal list).
- `artifact_hygiene()` flags delivered Python bytecode as contamination: any
  bytecode manifest entry, plus filesystem bytecode under delivered-skill /
  staged-setup roots (`BYTECODE_GUARDED_ROOTS` = `.agents/skills`,
  `.claude/skills`, `.cursor`, `.tes/setup`). `.tes/bin` is intentionally
  excluded — it legitimately carries a runtime bytecode cache
  (INSTALLATION-FRAMEWORK.md:64).
- New `negative_checks.delivered_bytecode_absent`.
- `self_test()`: red-capable fixture — plants `__pycache__/*.pyc` under a
  delivered skill and asserts artifact_hygiene FAIL, named contamination, a
  certification finding, and `delivered_bytecode_absent=False`. Verified
  red-capable: neutralizing the detector flips to FAIL on all four assertions.

### Proof (focused self-tests, PYTHONDONTWRITEBYTECODE=1)
- `tes_bundle.py --self-test`: PASS (green); red-capable confirmed.
- `installed_certification_oracle.py --self-test`: PASS (green); red-capable
  confirmed.
- `public_bundle_oracle.py`: RED on helper-drift guard (EXPECTED) — delivered
  helpers changed, so the bundle must be regenerated after a version decision.
  This is the release-identity gate firing correctly, not a regression.

### Release identity (Gap 2)
Delivered behavior changed (HELPER_FILES `tes_bundle.py` +
`installed_certification_oracle.py`, plus `public_bundle_oracle.py`). The public
bundle must be regenerated. Version decision deferred to SPEC-007/008 closeout
after all source fixes land.

## SPEC-005 — Postinstall advisory truthfulness (Gap 3)

### `scripts/tes_install.py`
- `collect_advisories()` gains `derived_at` keyword; every advisory is stamped
  with the producing run's timestamp so a historical scaffold-era advisory can
  never be read as current-state evidence.
- `postinstall()` computes `advisory_stamp` once, passes it to
  `collect_advisories`, and writes `advisories_derived_at` into the sentinel on
  every PASS run. An empty advisory list + fresh `advisories_derived_at` is now
  POSITIVE proof that mesh.scaffold_only was re-evaluated against the aligned
  mesh and cleared — not merely absent. (Mechanism already re-derives advisories
  from THIS run's alignment oracle and replaces the sentinel list, so a forced/
  recovery postinstall after /tes-align drops mesh.scaffold_only.)
- `self_test()`: red-capable scaffold -> aligned transition fixture. Asserts the
  scaffold-era run emits mesh.scaffold_only stamped with its derived_at, and the
  aligned run does NOT carry mesh.scaffold_only forward. Verified red-capable:
  forcing the scaffold advisory to emit while aligned flips the self-test to FAIL
  naming the transition assertion.

### Proof
- `tes_install.py --self-test`: PASS (20s); red-capable confirmed.

### Replay-session requirement (documented in CANARY-REPLAY-HANDOFF.md)
If the replay uses postinstall as admission evidence, it MUST run a post-align
postinstall refresh (`--force` / recovery) so the sentinel re-derives advisories
against the aligned mesh and stamps a fresh advisories_derived_at.

### Release identity (Gap 3)
Delivered behavior changed (HELPER_FILE `tes_install.py`). Folds into the same
version decision as Gap 2.

## SPEC-003 + SPEC-006 — Git admission contract + per-host hook truthfulness (Gap 1 + Gap 4)

### `scripts/canary_admission_oracle.py` (NEW — maintainer/canary gate, NOT delivered)
A focused canary-admission oracle. No prior surface materially proved Git
admission or refused cross-host native hook claims.
- Git admission HARD GATE: BLOCKS when target is not a Git work tree; on a
  Git-backed target BLOCKS when the Field Reports pre-push gate is absent
  (reuses `field_reports.resolve_pre_push_hook` + `has_gate_pre_git_push`) or
  strict pre-commit proof is absent; reports `git_clean`/`prepush_installed`/
  `precommit_enforced` ONLY on material evidence (false, never silence).
- Per-host hook admission: consumes `tes_install.hook_health_payload(target,
  current_host=host)` per host; a host with its own OBSERVED runtime records is
  NATIVE_PASS, configured-but-unobserved is CONFIGURED_NOT_OBSERVED (never native
  PASS), and one host's records never fill another's claim. Overall status is
  NEEDS_EVIDENCE while any host is CONFIGURED_NOT_OBSERVED.
- `self_test()`: four sub-fixtures — (1) no-Git target claiming readiness ->
  BLOCKED with no false Git claims [SPEC-003 literal requirement]; (2) Git
  without gates -> BLOCKED naming both missing pre-push and pre-commit;
  (3) fully-gated clean Git -> git_admission PASS with real claims; (4) only
  Claude has its own runtime records -> Claude NATIVE_PASS, Codex+Cursor
  CONFIGURED_NOT_OBSERVED, overall NEEDS_EVIDENCE [SPEC-006 cross-host filling].
- Verified red-capable twice: neutralizing the Git gate flips (1) to FAIL
  ("no-Git target must BLOCK admission"); neutralizing per-host isolation
  (cross-host filling) flips (4) to FAIL ("no cross-host evidence filling").

### `docs/architecture/INSTALLATION-FRAMEWORK.md`
- Added `canary_admission_oracle.py` to the load-bearing oracle list with its
  contract; stated strict pre-commit is canary admission infrastructure, not TES
  default adopter behavior; a canary may only claim READY_FOR_GOAL_MAESTRO_CANARY
  after this oracle passes.

### `docs/install/AGENT-ORACLE-INVENTORY.md`
- New "Canary Admission And Installed Certification" section listing
  `installed_certification_oracle.py`, `public_bundle_oracle.py`, and
  `canary_admission_oracle.py`, with the per-host truthfulness note.

### Classification (scripts consumer)
`canary_admission_oracle.py` is a MAINTAINER gate (canary admission self-test +
replay gate). It is NOT a HELPER_FILE, NOT in the delivered bundle, NOT a
target-project adopter behavior — so it does not by itself change adopter-visible
delivered behavior or the public bundle identity.

### Proof
- `canary_admission_oracle.py --self-test`: PASS; red-capable confirmed (x2).
- `installed_certification_oracle.py --self-test`: PASS (NEEDS_EVIDENCE stays
  visible under aggregate PASS — Gap 4 truthfulness already guarded).
- `validate_doc_size.py`: exit 0 (no doc over threshold).
- `validate_reference_package.py`: 0 real failures (only this run's
  not-yet-TDS-indexed evidence files remain, indexed at closeout).
