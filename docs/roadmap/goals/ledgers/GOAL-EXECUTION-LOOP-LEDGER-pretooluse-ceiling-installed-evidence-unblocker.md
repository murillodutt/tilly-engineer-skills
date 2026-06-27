---
tds_id: roadmap.goal_execution_loop_ledger_pretooluse_ceiling_installed_evidence_unblocker
tds_class: roadmap
status: active
consumer: maintainers, hook authors, installer authors, oracle authors, release reviewers, and execution agents
source_of_truth: false
evidence_level: L1
tver: 0.1.0
---

# GOAL Execution Loop Ledger: PreToolUse Ceiling Installed Evidence Unblocker

Canonical Super SPEC:
`docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-pretooluse-ceiling-installed-evidence-unblocker.md`

Anchor metadata:

Anchor: docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-pretooluse-ceiling-installed-evidence-unblocker.md (Super-SPEC, git hash-object 03df2c6a936dc64fafbf0029ad65144f48ee4277)

- anchor_class: `Super-SPEC`
- anchor_path:
  `docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-pretooluse-ceiling-installed-evidence-unblocker.md`
- anchor_hash_at_open: `03df2c6a936dc64fafbf0029ad65144f48ee4277`
- anchor_origin: `provided`
- protected_release: `0.3.220`
- protected_baseline: `installed closure NEEDS_EVIDENCE; no installed PASS_CEILING`

Declared units:

1. `SPEC-000`
2. `SPEC-001`
3. `SPEC-002`
4. `SPEC-003`
5. `SPEC-004`
6. `SPEC-005`
7. `SPEC-006`

## Repaired Materialization Tree

tree_adversary_status: `OBJECTIONS_REPAIRED`
adversary_objections:

- `topology_budget_decorative`
- `runtime_smoke_missing_for_installed_hook_health`
- `shared_contracts_loose`
- `parent_memory_handoff`

Shared contracts:

```text
pretooluse_decision_v2:
declared_in: docs/architecture/PRETOOLUSE-CONTRACT.md; scripts/tes_install.py
frozen_surface: schema_version=pretooluse_decision@2 ledger rows with host, event, decision, trace, redaction, reason-code, payload-source, and renderer fields
extension_points: host-scoped ceiling_evidence_scope only; no legacy-row backfill
extenders: SPEC-001, SPEC-002, SPEC-005
optionality_rule: current v2 host evidence requires complete per-host fields; legacy rows are historical context only
declaring_oracles: python3 scripts/tes_install.py --self-test; python3 scripts/host_runtime_matrix_oracle.py --self-test
extension_oracles: red fixture for legacy v2 scoping; red fixture for cross-host no-fill; pass-ceiling packet oracle in SPEC-005

hook_health_json_v2:
declared_in: scripts/tes_install.py; docs/install/HOOK-AUDIT-PROMPT.md
frozen_surface: schema=tes-hook-health@2; status remains legacy functional status; floor_status and ceiling_status are separate
extension_points: helper_contract_status, discoverability_status, ceiling_evidence_scope, dedupe_contract
extenders: SPEC-001, SPEC-002, SPEC-004, SPEC-005
optionality_rule: installed hook-health must emit explicit PASS, NEEDS_EVIDENCE, MISSING, or not_available values; no silent omission
declaring_oracles: python3 scripts/tes_install.py --self-test; python3 scripts/host_runtime_matrix_oracle.py --self-test
extension_oracles: python3 scripts/hook_audit_prompt_oracle.py --self-test; installed hook-health smoke in temporary target

pretooluse_contract_lock:
declared_in: docs/architecture/PRETOOLUSE-CONTRACT.md; scripts/tes_install.py
frozen_surface: .tes/tes-install-lock.json schema=tes-install-lock@1
extension_points: pretooluse_contract object with package_path, installed_path, sha256, version
extenders: SPEC-003, SPEC-006
optionality_rule: installed contract reference is required after install; stale or mismatched hash is explicit evidence, not ignored
declaring_oracles: python3 scripts/tes_install.py --self-test
extension_oracles: python3 scripts/installed_certification_oracle.py --self-test; python3 scripts/validate_reference_package.py

hook_dedupe_policy:
declared_in: scripts/tes_install.py; docs/install/HOOK-AUDIT-PROMPT.md
frozen_surface: dedupe_contract schema=tes-hook-dedupe@1 and HOOK_RECORD_DEDUPE_FIELDS
extension_points: historical-noise severity rules only
extenders: SPEC-004, SPEC-005
optionality_rule: exact duplicate findings may warn; replay history and Cursor batched distinct rows must not block ceiling unless a current v2 contradiction exists
declaring_oracles: python3 scripts/tes_install.py --self-test
extension_oracles: python3 scripts/hook_audit_prompt_oracle.py --self-test
```

Engineering Method Profile:

- STRUCTURAL_METHOD: `platform-python-installer-internal-sections`
- stack: `Python CLI installer/runtime helpers; Markdown prompt contract`
- runtime_target: `node-not_applicable; python-runtime`
- topology_decision: `internal-section patch inside existing delivered scripts and prompt oracles`
- topology_decision_artifact: `this ledger`
- topology_budget: `no new runtime module for SPEC-001 through SPEC-004 unless an active SPEC records NEEDS_STRUCTURAL_METHOD; no new external dependency; no host abstraction or strategy interface`
- topology_probe: `versioned failing probes are the touched script self-tests; any new topology must add or update a self-test assertion before commit`
- allowed_modules_or_internal_sections: `scripts/tes_install.py hook-health helpers; scripts/host_runtime_matrix_oracle.py contract assertions; scripts/hook_audit_prompt_oracle.py terms/mutants; scripts/pretooluse_evidence_oracle.py packet validation; docs/install/HOOK-AUDIT-PROMPT.md`
- forbidden_layer_moves: `no source-matrix synthesis of installed-only status; no installed mirror patch without package source; no host-contract flattening`
- structural_debt_budget: `none`
- structural_source_probes: `rg -n pretooluse_ceiling_gaps scripts/tes_install.py; python3 scripts/tes_install.py --self-test; python3 scripts/host_runtime_matrix_oracle.py --self-test; python3 scripts/hook_audit_prompt_oracle.py --self-test; git diff --check`
- structural_negative_checks: `no cross-host field pooling; no raw command persistence; no PASS_CEILING from simulated-only evidence; no legacy row current v2 gaps`
- runtime_smoke_oracle: `python3 scripts/tes_install.py --self-test plus explicit temporary installed hook-health --json-only fixture in active SPEC`

Source-derived handoff:

```text
contract_handoff_artifact=this ledger
runtime_target=python-runtime
symbol_index_source=manual-source-read
symbols=pretooluse_ceiling_gaps(records); hook_ceiling_status(floor_status, ceiling_gaps); hook_health_payload(target); duplicate_hook_records(records); hook_dedupe_contract(); write_install_lock(...)
reused_source_files=scripts/tes_install.py; scripts/host_runtime_matrix_oracle.py; docs/install/HOOK-AUDIT-PROMPT.md; scripts/hook_audit_prompt_oracle.py
oracle_runner_contract=python3 scripts/tes_install.py --self-test; python3 scripts/host_runtime_matrix_oracle.py --self-test; python3 scripts/hook_audit_prompt_oracle.py --self-test; python3 scripts/installed_certification_oracle.py --self-test; python3 scripts/pretooluse_evidence_oracle.py --packet <packet>
environment_notes=Python 3.11+; local-only commits; no push/tag/release
api_lint_status=PASS by source read and baseline self-tests in SPEC-000
```

## SPEC-000

spec_id: `SPEC-000`
spec_version: `0.1.0`
attempt: `1`
repair_count: `0`
audit_repair_cycle: `0`
first_unexecuted_unit: `SPEC-001`
failed_attempt_recovery_decision: `not_applicable`
commit: no-commit preflight
oracle_status: `PASS`
structural_method_id: `not_applicable`
topology_decision: `not_applicable`
topology_decision_artifact: `not_applicable`
structural_debt: `not_applicable`
next_structural_constraint: `open SPEC-001 only after tree repair and anchor rehash`
topology_probe_result: `not_applicable`
browser_metrics_contract: `not_applicable`
visual_spatial_oracle: `not_applicable`
browser_attempt: `not_applicable`
visual_evidence: `not_applicable`
runtime_smoke_oracle: `PASS: python3 scripts/host_runtime_matrix_oracle.py --self-test; python3 scripts/pretooluse_evidence_oracle.py --packet docs/evidence/reports/2026/06/27/hooks/pretooluse-ceiling-installed-evidence`
adversary_objection: `repaired before SPEC-001`
shared_contract_extended: `not_applicable`
extension_point_proven: `not_applicable`
contract_handoff_artifact: `this ledger`
api_lint_status: `PASS`
auditor_distinct_from_operator: `not_applicable`
auditor_rewrote_no_oracle: `not_applicable`
audit_remutation: `not_applicable`
distinct_refuters: `not_applicable`
stop_state: `SPEC-000_NO_COMMIT_PREFLIGHT_PASS`
next_allowed_action: `open SPEC-001`

SPEC-000 evidence:

- `git status --short --branch --untracked-files=all`: clean at open, `main...origin/main [ahead 32]`.
- Anchor sha256 values declared by the Super SPEC match tracked files.
- Super SPEC git hash-object at open: `03df2c6a936dc64fafbf0029ad65144f48ee4277`.
- `python3 scripts/host_runtime_matrix_oracle.py --self-test`: PASS; matrix remains NEEDS_EVIDENCE/NEEDS_FLOOR.
- `python3 scripts/pretooluse_evidence_oracle.py --packet docs/evidence/reports/2026/06/27/hooks/pretooluse-ceiling-installed-evidence`: PASS.
- Closure report final status: `NEEDS_EVIDENCE`.
- No tracked installed `PASS_CEILING` proof exists.

## Execution Cost Draft

source_artifacts: `GOAL-SUPER-SPEC-pretooluse-ceiling-installed-evidence-unblocker.md; docs/architecture/PRETOOLUSE-CONTRACT.md; scripts/tes_install.py; scripts/host_runtime_matrix_oracle.py; docs/install/HOOK-AUDIT-PROMPT.md`
declared_spec_order: `SPEC-000 -> SPEC-001 -> SPEC-002 -> SPEC-003 -> SPEC-004 -> SPEC-005 -> SPEC-006`
dependency_edges: `SPEC-001 before SPEC-002; SPEC-002 before SPEC-003; SPEC-003 before SPEC-004; SPEC-004 before SPEC-005; SPEC-006 last`
risk: `Platform; delivered installer/hook-health/runtime evidence`
expected_commits: `one local commit per material SPEC-001 through SPEC-006 unless a SPEC honestly closes no-op/blocked`
baseline_worktree_classification: `clean before ledger creation; ledger is current-loop required artifact`
canonical_spec_repair_target: `docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-pretooluse-ceiling-installed-evidence-unblocker.md if active SPEC contract is wrong`
runtime_plan: `installed hook-health smoke through self-tests and temporary installed target fixtures; SPEC-005 attempts native installed evidence only if authorized/available`
tree_adversary_result: `OBJECTIONS_REPAIRED`
ledger_path: `docs/roadmap/goals/ledgers/GOAL-EXECUTION-LOOP-LEDGER-pretooluse-ceiling-installed-evidence-unblocker.md`

## Pre-Edit Gate For SPEC-001

EXECUTE_LOOP_REQUESTED: `yes`
READY_GOAL_PROMPT: `present`
ANCHOR_CLASS: `Super-SPEC`
ANCHOR_PATH: `docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-pretooluse-ceiling-installed-evidence-unblocker.md`
ANCHOR_HASH: `03df2c6a936dc64fafbf0029ad65144f48ee4277`
TREE_ADVERSARY_STATUS: `OBJECTIONS_REPAIRED`
DECLARED_UNITS: `SPEC-000,SPEC-001,SPEC-002,SPEC-003,SPEC-004,SPEC-005,SPEC-006`
FIRST_UNEXECUTED_UNIT: `SPEC-001`
ACTIVE_SPEC: `SPEC-001`
BASELINE_ONLY_COMMITS: `89e6e000,ad028e99,b76a9d1e,ec40caaa,33b60f73,9a538daf,a270dc71`
LEDGER: `docs/roadmap/goals/ledgers/GOAL-EXECUTION-LOOP-LEDGER-pretooluse-ceiling-installed-evidence-unblocker.md`
MAY_EDIT: `yes`

## SPEC-001

spec_id: `SPEC-001`
spec_version: `0.1.0`
attempt: `1`
repair_count: `0`
audit_repair_cycle: `0`
first_unexecuted_unit: `SPEC-002`
failed_attempt_recovery_decision: `not_applicable`
commit: e1e51351
oracle_status: `PASS: python3 scripts/tes_install.py --self-test; python3 scripts/host_runtime_matrix_oracle.py --self-test; npm run commit:check`
structural_method_id: `platform-python-installer-internal-sections`
topology_decision: `internal-section patch in scripts/tes_install.py plus matrix assertions; no new runtime module`
topology_decision_artifact: `scripts/tes_install.py; scripts/host_runtime_matrix_oracle.py; this ledger`
structural_debt: `none`
next_structural_constraint: `SPEC-002 may extend hook-health JSON fields only through installed evidence, not source-matrix synthesis`
topology_probe_result: `PASS`
browser_metrics_contract: `not_applicable`
visual_spatial_oracle: `not_applicable`
browser_attempt: `not_applicable`
visual_evidence: `not_applicable`
runtime_smoke_oracle: `PASS: installed hook-health path exercised by tes_install self-test and host-runtime matrix`
adversary_objection: `repaired before SPEC-001 open`
shared_contract_extended: `yes`
extension_point_proven: `yes`
contract_handoff_artifact: `this ledger`
api_lint_status: `PASS`
auditor_distinct_from_operator: `not_applicable`
auditor_rewrote_no_oracle: `not_applicable`
audit_remutation: `not_applicable`
distinct_refuters: `not_applicable`
stop_state: `SPEC-001_LOCAL_COMMITTED`
next_allowed_action: `open SPEC-002`

SPEC-001 evidence:

- Commit: `e1e51351 feat(pretooluse): scope ceiling evidence per host`.
- `git show --stat --oneline e1e51351`: changed `scripts/tes_install.py`, `scripts/host_runtime_matrix_oracle.py`, this ledger, and `docs/tds/DOCS-INDEX.yml`.
- Red fixture before repair: legacy pre-v2 row produced current v2 gaps, and cross-host pooling returned no gaps.
- Parent validation after repair: same-host legacy rows are ignored for current v2 gaps, ignored legacy counts are reported, and cross-host split evidence produces gaps per host.
- Sync status: `REMOTE_SYNC_NOT_REQUESTED`.

## Pre-Edit Gate For SPEC-002

EXECUTE_LOOP_REQUESTED: `yes`
READY_GOAL_PROMPT: `present`
ANCHOR_CLASS: `Super-SPEC`
ANCHOR_PATH: `docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-pretooluse-ceiling-installed-evidence-unblocker.md`
ANCHOR_HASH: `03df2c6a936dc64fafbf0029ad65144f48ee4277`
TREE_ADVERSARY_STATUS: `OBJECTIONS_REPAIRED`
DECLARED_UNITS: `SPEC-000,SPEC-001,SPEC-002,SPEC-003,SPEC-004,SPEC-005,SPEC-006`
FIRST_UNEXECUTED_UNIT: `SPEC-002`
ACTIVE_SPEC: `SPEC-002`
BASELINE_ONLY_COMMITS: `e1e51351,89e6e000,ad028e99,b76a9d1e,ec40caaa,33b60f73,9a538daf,a270dc71`
LEDGER: `docs/roadmap/goals/ledgers/GOAL-EXECUTION-LOOP-LEDGER-pretooluse-ceiling-installed-evidence-unblocker.md`
MAY_EDIT: `yes`
