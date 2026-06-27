---
tds_id: roadmap.goal_execution_loop_ledger_adr_0009_pretooluse_ceiling_linear_slices
tds_class: roadmap
status: active
consumer: maintainers, hook authors, installer authors, oracle authors, release reviewers, execution agents, and hook-audit operators
source_of_truth: false
evidence_level: L1
tver: 0.1.0
---

# GOAL Execution Loop Ledger: ADR 0009 PreToolUse Ceiling Linear Slices

Canonical Super SPEC:
`docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-adr-0009-pretooluse-ceiling-linear-slices.md`

Anchor: docs/adr/0009-pretooluse-ceiling-contract-and-hook-topology.md (ADR, git hash-object 0b960cb31c4c42372412588887545eb9b1d91802)

Anchor metadata:

- anchor_class: `ADR`
- anchor_path: `docs/adr/0009-pretooluse-ceiling-contract-and-hook-topology.md`
- anchor_hash_at_open: `0b960cb31c4c42372412588887545eb9b1d91802`
- anchor_origin: `previous-session`
- anchor_source: `docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-adr-0009-pretooluse-ceiling-linear-slices.md`
- super_spec_hash_at_open: `ed494d0552fc28d7d314996793679f37aaa247bf`

Loop boundary:

- `SPEC-000` and `SPEC-001` were completed before this ledger was opened and remain baseline evidence for this resumed loop.
- Current owner direction resumes execution at `SPEC-002`, preserving the declared sequence from the canonical Super SPEC.
- No canary, release, push, tag, bundle, or `PASS_CEILING` claim is authorized before the declared later units.

Declared units:

1. `SPEC-000`
2. `SPEC-001`
3. `SPEC-002`
4. `SPEC-003`
5. `SPEC-004`
6. `SPEC-005`
7. `SPEC-006`
8. `SPEC-007`
9. `SPEC-008`
10. `SPEC-009`
11. `SPEC-010`
12. `SPEC-011`
13. `SPEC-012`

## Pre-Edit Gate: SPEC-002

EXECUTE_LOOP_REQUESTED=yes
READY_GOAL_PROMPT=present
ANCHOR_CLASS=ADR
ANCHOR_PATH=docs/adr/0009-pretooluse-ceiling-contract-and-hook-topology.md
ANCHOR_HASH=0b960cb31c4c42372412588887545eb9b1d91802
TREE_ADVERSARY_STATUS=OBJECTIONS_REPAIRED
DECLARED_UNITS=SPEC-000,SPEC-001,SPEC-002,SPEC-003,SPEC-004,SPEC-005,SPEC-006,SPEC-007,SPEC-008,SPEC-009,SPEC-010,SPEC-011,SPEC-012
FIRST_UNEXECUTED_UNIT=SPEC-002
ACTIVE_SPEC=SPEC-002
BASELINE_ONLY_COMMITS=faa4e8a6,33313d3c
LEDGER=docs/roadmap/goals/ledgers/GOAL-EXECUTION-LOOP-LEDGER-adr-0009-pretooluse-ceiling-linear-slices.md
MAY_EDIT=yes

## SPEC-002

spec_id: `SPEC-002`
spec_version: `GOAL-SUPER-SPEC-adr-0009-pretooluse-ceiling-linear-slices.md@ed494d0552fc28d7d314996793679f37aaa247bf`
attempt: `1`
repair_count: `0`
audit_repair_cycle: `0`
first_unexecuted_unit: `SPEC-002`
failed_attempt_recovery_decision: `interrupted_attempt_resumed: existing dirty diff classified as current-loop SPEC-002 material`
commit: no-commit: active SPEC opened before material commit; commit hash is captured in parent validation after local commit
oracle_status: `pre-commit pending; last focused rerun PASS for py_compile, pretooluse_session_oracle, tes_install self-test, host_runtime_matrix_oracle, and git diff --check`
structural_method_id: `runtime-script-internal-sections`
topology_decision: `internal-section extension`
topology_decision_artifact: `ledger-section`
structural_debt: `none`
next_structural_constraint: `SPEC-003 may extend v2 ledger fields only through explicit trace fields and focused oracles`
topology_probe_result: `PASS: no new modules; existing runtime/helper files only`
browser_metrics_contract: `not_applicable`
visual_spatial_oracle: `not_applicable`
browser_attempt: `not_applicable`
visual_evidence: `not_applicable`
runtime_smoke_oracle: `PASS: python3 scripts/host_runtime_matrix_oracle.py --self-test`
adversary_objection: `none`
shared_contract_extended: `yes`
extension_point_proven: `yes: pretooluse_decision@2 reason_codes[] declared by ADR 0009`
contract_handoff_artifact: `ledger-section`
api_lint_status: `not_applicable`
auditor_distinct_from_operator: `not_applicable`
auditor_rewrote_no_oracle: `not_applicable`
audit_remutation: `not_applicable`
distinct_refuters: `not_applicable`
stop_state: `ACTIVE_SPEC_OPEN`
next_allowed_action: `run focused SPEC-002 oracles, commit locally, then open SPEC-003`

## Pre-Edit Gate: SPEC-003

EXECUTE_LOOP_REQUESTED=yes
READY_GOAL_PROMPT=present
ANCHOR_CLASS=ADR
ANCHOR_PATH=docs/adr/0009-pretooluse-ceiling-contract-and-hook-topology.md
ANCHOR_HASH=0b960cb31c4c42372412588887545eb9b1d91802
TREE_ADVERSARY_STATUS=OBJECTIONS_REPAIRED
DECLARED_UNITS=SPEC-000,SPEC-001,SPEC-002,SPEC-003,SPEC-004,SPEC-005,SPEC-006,SPEC-007,SPEC-008,SPEC-009,SPEC-010,SPEC-011,SPEC-012
FIRST_UNEXECUTED_UNIT=SPEC-003
ACTIVE_SPEC=SPEC-003
BASELINE_ONLY_COMMITS=faa4e8a6,33313d3c,35f53c97
LEDGER=docs/roadmap/goals/ledgers/GOAL-EXECUTION-LOOP-LEDGER-adr-0009-pretooluse-ceiling-linear-slices.md
MAY_EDIT=yes

## SPEC-003

spec_id: `SPEC-003`
spec_version: `GOAL-SUPER-SPEC-adr-0009-pretooluse-ceiling-linear-slices.md@ed494d0552fc28d7d314996793679f37aaa247bf`
attempt: `1`
repair_count: `0`
audit_repair_cycle: `0`
first_unexecuted_unit: `SPEC-003`
failed_attempt_recovery_decision: `not_applicable`
commit: no-commit: active SPEC opened before material commit; commit hash is captured in parent validation after local commit
oracle_status: `PASS: py_compile, pretooluse_kernel_oracle, host_runtime_matrix_oracle, tes_install self-test, pretooluse_session_oracle, pretooluse_contract_oracle, mantra_gate_pretooluse_oracle, validate_tds, doc-size, ledger-no-placeholder, and renderer-token negative grep`
structural_method_id: `runtime-script-internal-sections`
topology_decision: `internal-section extension`
topology_decision_artifact: `ledger-section`
structural_debt: `none`
next_structural_constraint: `SPEC-004 owns renderer trace and parity; SPEC-003 must not encode renderer protocol fields in the kernel`
topology_probe_result: `PASS: no new modules; kernel/writer/oracle internal sections only`
browser_metrics_contract: `not_applicable`
visual_spatial_oracle: `not_applicable`
browser_attempt: `not_applicable`
visual_evidence: `not_applicable`
runtime_smoke_oracle: `PASS: python3 scripts/host_runtime_matrix_oracle.py --self-test`
adversary_objection: `none`
shared_contract_extended: `yes`
extension_point_proven: `yes: pretooluse_decision@2 declares raw_tool_label, normalized_tool, payload_source, and classifier_trace`
contract_handoff_artifact: `ledger-section`
api_lint_status: `not_applicable`
auditor_distinct_from_operator: `not_applicable`
auditor_rewrote_no_oracle: `not_applicable`
audit_remutation: `not_applicable`
distinct_refuters: `not_applicable`
stop_state: `READY_TO_COMMIT`
next_allowed_action: `stage only SPEC-003 files and commit locally`

## Pre-Edit Gate: SPEC-004

EXECUTE_LOOP_REQUESTED=yes
READY_GOAL_PROMPT=present
ANCHOR_CLASS=ADR
ANCHOR_PATH=docs/adr/0009-pretooluse-ceiling-contract-and-hook-topology.md
ANCHOR_HASH=0b960cb31c4c42372412588887545eb9b1d91802
TREE_ADVERSARY_STATUS=OBJECTIONS_REPAIRED
DECLARED_UNITS=SPEC-000,SPEC-001,SPEC-002,SPEC-003,SPEC-004,SPEC-005,SPEC-006,SPEC-007,SPEC-008,SPEC-009,SPEC-010,SPEC-011,SPEC-012
FIRST_UNEXECUTED_UNIT=SPEC-004
ACTIVE_SPEC=SPEC-004
BASELINE_ONLY_COMMITS=faa4e8a6,33313d3c,35f53c97,4dedc876
LEDGER=docs/roadmap/goals/ledgers/GOAL-EXECUTION-LOOP-LEDGER-adr-0009-pretooluse-ceiling-linear-slices.md
MAY_EDIT=yes

## SPEC-004

spec_id: `SPEC-004`
spec_version: `GOAL-SUPER-SPEC-adr-0009-pretooluse-ceiling-linear-slices.md@ed494d0552fc28d7d314996793679f37aaa247bf`
attempt: `1`
repair_count: `0`
audit_repair_cycle: `0`
first_unexecuted_unit: `SPEC-004`
failed_attempt_recovery_decision: `not_applicable`
commit: no-commit: active SPEC opened before material commit; commit hash is captured in parent validation after local commit
oracle_status: `PASS: py_compile, mantra_gate_pretooluse_oracle, host_runtime_matrix_oracle, tes_install self-test, pretooluse_kernel_oracle, pretooluse_session_oracle, and renderer-token negative grep`
structural_method_id: `runtime-script-internal-sections`
topology_decision: `internal-section extension`
topology_decision_artifact: `ledger-section`
structural_debt: `none`
next_structural_constraint: `SPEC-005 may consume renderer_trace but must not move renderer semantics into the kernel`
topology_probe_result: `PASS: no new modules; runtime/oracle internal sections only`
browser_metrics_contract: `not_applicable`
visual_spatial_oracle: `not_applicable`
browser_attempt: `not_applicable`
visual_evidence: `not_applicable`
runtime_smoke_oracle: `PASS: python3 scripts/host_runtime_matrix_oracle.py --self-test`
adversary_objection: `none`
shared_contract_extended: `yes`
extension_point_proven: `yes: pretooluse_decision@2 declares renderer_trace and reason code renderer_contract_projected`
contract_handoff_artifact: `ledger-section`
api_lint_status: `not_applicable`
auditor_distinct_from_operator: `not_applicable`
auditor_rewrote_no_oracle: `not_applicable`
audit_remutation: `not_applicable`
distinct_refuters: `not_applicable`
stop_state: `READY_TO_COMMIT`
next_allowed_action: `stage only SPEC-004 files and commit locally`
