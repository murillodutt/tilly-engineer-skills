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
commit: 35f53c9790783b4bf852ecb2a2403d4edd763848
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
stop_state: `COMMITTED`
next_allowed_action: `open SPEC-003`

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
commit: 4dedc876b4bc7d249f432977f9f8d2b269cab28f
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
stop_state: `COMMITTED`
next_allowed_action: `open SPEC-004`

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
commit: 595c3911ef50a5787aaa935170b27de1a89050c9
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
stop_state: `COMMITTED`
next_allowed_action: `open SPEC-005`

## Pre-Edit Gate: SPEC-005

EXECUTE_LOOP_REQUESTED=yes
READY_GOAL_PROMPT=present
ANCHOR_CLASS=ADR
ANCHOR_PATH=docs/adr/0009-pretooluse-ceiling-contract-and-hook-topology.md
ANCHOR_HASH=0b960cb31c4c42372412588887545eb9b1d91802
TREE_ADVERSARY_STATUS=OBJECTIONS_REPAIRED
DECLARED_UNITS=SPEC-000,SPEC-001,SPEC-002,SPEC-003,SPEC-004,SPEC-005,SPEC-006,SPEC-007,SPEC-008,SPEC-009,SPEC-010,SPEC-011,SPEC-012
FIRST_UNEXECUTED_UNIT=SPEC-005
ACTIVE_SPEC=SPEC-005
BASELINE_ONLY_COMMITS=faa4e8a6,33313d3c,35f53c97,4dedc876,595c3911
LEDGER=docs/roadmap/goals/ledgers/GOAL-EXECUTION-LOOP-LEDGER-adr-0009-pretooluse-ceiling-linear-slices.md
MAY_EDIT=yes

## SPEC-005

spec_id: `SPEC-005`
spec_version: `GOAL-SUPER-SPEC-adr-0009-pretooluse-ceiling-linear-slices.md@ed494d0552fc28d7d314996793679f37aaa247bf`
attempt: `1`
repair_count: `0`
audit_repair_cycle: `0`
first_unexecuted_unit: `SPEC-005`
failed_attempt_recovery_decision: `not_applicable`
commit: 3271ac4dc004fa4f9ac07a822a26d76435ab291f
oracle_status: `PASS: red failure reproduced in pretooluse_kernel_oracle and host_runtime_matrix_oracle, then PASS for pretooluse_kernel_oracle, host_runtime_matrix_oracle, and hook_audit_prompt_oracle`
structural_method_id: `runtime-script-internal-sections`
topology_decision: `internal-section extension plus audit prompt contract update`
topology_decision_artifact: `ledger-section`
structural_debt: `none`
next_structural_constraint: `SPEC-006 owns dedup semantics; SPEC-005 must not broaden the mutating tool allowlist`
topology_probe_result: `PASS: no new modules; kernel, matrix oracle, audit prompt oracle, and audit prompt only`
browser_metrics_contract: `not_applicable`
visual_spatial_oracle: `not_applicable`
browser_attempt: `not_applicable`
visual_evidence: `not_applicable`
runtime_smoke_oracle: `PASS: python3 scripts/host_runtime_matrix_oracle.py --self-test reports discoverability_status=NEEDS_DISCOVERABILITY`
adversary_objection: `none`
shared_contract_extended: `yes`
extension_point_proven: `yes: runtime output surfaces outcome=needs_discoverability and risk=needs-discoverability; ledger row carries outcome, risk, reason_codes, classifier_trace, and renderer_trace`
contract_handoff_artifact: `ledger-section`
api_lint_status: `not_applicable`
auditor_distinct_from_operator: `not_applicable`
auditor_rewrote_no_oracle: `not_applicable`
audit_remutation: `PASS: hook_audit_prompt_oracle red-capability mutants cover discoverability runtime output, matrix status, classifier trace, renderer trace, and redacted payload evidence`
distinct_refuters: `not_applicable`
stop_state: `COMMITTED`
next_allowed_action: `open SPEC-006`

## Pre-Edit Gate: SPEC-006

EXECUTE_LOOP_REQUESTED=yes
READY_GOAL_PROMPT=present
ANCHOR_CLASS=ADR
ANCHOR_PATH=docs/adr/0009-pretooluse-ceiling-contract-and-hook-topology.md
ANCHOR_HASH=0b960cb31c4c42372412588887545eb9b1d91802
TREE_ADVERSARY_STATUS=OBJECTIONS_REPAIRED
DECLARED_UNITS=SPEC-000,SPEC-001,SPEC-002,SPEC-003,SPEC-004,SPEC-005,SPEC-006,SPEC-007,SPEC-008,SPEC-009,SPEC-010,SPEC-011,SPEC-012
FIRST_UNEXECUTED_UNIT=SPEC-006
ACTIVE_SPEC=SPEC-006
BASELINE_ONLY_COMMITS=faa4e8a6,33313d3c,35f53c97,4dedc876,595c3911,3271ac4d
LEDGER=docs/roadmap/goals/ledgers/GOAL-EXECUTION-LOOP-LEDGER-adr-0009-pretooluse-ceiling-linear-slices.md
MAY_EDIT=yes

## SPEC-006

spec_id: `SPEC-006`
spec_version: `GOAL-SUPER-SPEC-adr-0009-pretooluse-ceiling-linear-slices.md@ed494d0552fc28d7d314996793679f37aaa247bf`
attempt: `1`
repair_count: `0`
audit_repair_cycle: `0`
first_unexecuted_unit: `SPEC-006`
failed_attempt_recovery_decision: `not_applicable`
commit: 63ce1301931fd860174eaf7450de5c9eb8361108
oracle_status: `PASS: red failure reproduced in tes_install self-test and host_runtime_matrix_oracle, then PASS for py_compile, tes_install self-test, host_runtime_matrix_oracle, hook_audit_prompt_oracle, pretooluse_kernel_oracle, pretooluse_session_oracle, pretooluse_contract_oracle, and mantra_gate_pretooluse_oracle`
structural_method_id: `runtime-script-internal-sections`
topology_decision: `internal-section extension`
topology_decision_artifact: `ledger-section`
structural_debt: `none`
next_structural_constraint: `SPEC-007 owns installed helper packaging; SPEC-006 must not change helper packaging or release identity`
topology_probe_result: `PASS: no new modules; hook-health analytics helpers, runtime fixtures, matrix oracle, audit prompt oracle, and audit prompt only`
browser_metrics_contract: `not_applicable`
visual_spatial_oracle: `not_applicable`
browser_attempt: `not_applicable`
visual_evidence: `not_applicable`
runtime_smoke_oracle: `PASS: python3 scripts/tes_install.py --self-test and python3 scripts/host_runtime_matrix_oracle.py --self-test`
adversary_objection: `none`
shared_contract_extended: `yes`
extension_point_proven: `yes: hook-health exposes dedupe_contract, duplicate findings include dedupe_fields and record identity, replay remains history, and Cursor batch rows with different tool/path/risk/marker fields do not collapse`
contract_handoff_artifact: `ledger-section`
api_lint_status: `not_applicable`
auditor_distinct_from_operator: `not_applicable`
auditor_rewrote_no_oracle: `not_applicable`
audit_remutation: `PASS: hook_audit_prompt_oracle red-capability mutants cover dedupe_contract, dedupe fields, replay rule, and Cursor batch rule`
distinct_refuters: `not_applicable`
stop_state: `COMMITTED`
next_allowed_action: `open SPEC-007`

## Pre-Edit Gate: SPEC-007

EXECUTE_LOOP_REQUESTED=yes
READY_GOAL_PROMPT=present
ANCHOR_CLASS=ADR
ANCHOR_PATH=docs/adr/0009-pretooluse-ceiling-contract-and-hook-topology.md
ANCHOR_HASH=0b960cb31c4c42372412588887545eb9b1d91802
TREE_ADVERSARY_STATUS=OBJECTIONS_REPAIRED
DECLARED_UNITS=SPEC-000,SPEC-001,SPEC-002,SPEC-003,SPEC-004,SPEC-005,SPEC-006,SPEC-007,SPEC-008,SPEC-009,SPEC-010,SPEC-011,SPEC-012
FIRST_UNEXECUTED_UNIT=SPEC-007
ACTIVE_SPEC=SPEC-007
BASELINE_ONLY_COMMITS=faa4e8a6,33313d3c,35f53c97,4dedc876,595c3911,3271ac4d,63ce1301
LEDGER=docs/roadmap/goals/ledgers/GOAL-EXECUTION-LOOP-LEDGER-adr-0009-pretooluse-ceiling-linear-slices.md
MAY_EDIT=yes

## SPEC-007

spec_id: `SPEC-007`
spec_version: `GOAL-SUPER-SPEC-adr-0009-pretooluse-ceiling-linear-slices.md@ed494d0552fc28d7d314996793679f37aaa247bf`
attempt: `1`
repair_count: `0`
audit_repair_cycle: `0`
first_unexecuted_unit: `SPEC-007`
failed_attempt_recovery_decision: `not_applicable`
commit: eeecb2af370ba1130e34ba9d8a1cea3f55695a05
oracle_status: `PASS: py_compile, host_runtime_matrix_oracle, hook_audit_prompt_oracle, tes_install self-test, pretooluse_kernel_oracle, pretooluse_session_oracle, and pretooluse_contract_oracle`
structural_method_id: `runtime-script-internal-sections`
topology_decision: `matrix helper-contract extension`
topology_decision_artifact: `ledger-section`
structural_debt: `none`
next_structural_constraint: `SPEC-008 owns hook-health floor/ceiling split; SPEC-007 must not rename hook-health schema or claim PASS_CEILING`
topology_probe_result: `PASS: no new modules; installed helper import/parity probe added to host_runtime_matrix_oracle only, with audit prompt/oracle update`
browser_metrics_contract: `not_applicable`
visual_spatial_oracle: `not_applicable`
browser_attempt: `not_applicable`
visual_evidence: `not_applicable`
runtime_smoke_oracle: `PASS: python3 scripts/host_runtime_matrix_oracle.py --self-test reports helper_contract_status=PASS`
adversary_objection: `none`
shared_contract_extended: `yes`
extension_point_proven: `yes: installed .tes/bin/pretooluse_kernel.py and pretooluse_session.py are byte-matched, imported from .tes/bin, and simulated for discoverability/session contract`
contract_handoff_artifact: `ledger-section`
api_lint_status: `not_applicable`
auditor_distinct_from_operator: `not_applicable`
auditor_rewrote_no_oracle: `not_applicable`
audit_remutation: `PASS: hook_audit_prompt_oracle red-capability mutants cover helper paths, import contract, and helper_contract_status`
distinct_refuters: `not_applicable`
stop_state: `COMMITTED`
next_allowed_action: `open SPEC-008`

## Pre-Edit Gate: SPEC-008

EXECUTE_LOOP_REQUESTED=yes
READY_GOAL_PROMPT=present
ANCHOR_CLASS=ADR
ANCHOR_PATH=docs/adr/0009-pretooluse-ceiling-contract-and-hook-topology.md
ANCHOR_HASH=0b960cb31c4c42372412588887545eb9b1d91802
TREE_ADVERSARY_STATUS=OBJECTIONS_REPAIRED
DECLARED_UNITS=SPEC-000,SPEC-001,SPEC-002,SPEC-003,SPEC-004,SPEC-005,SPEC-006,SPEC-007,SPEC-008,SPEC-009,SPEC-010,SPEC-011,SPEC-012
FIRST_UNEXECUTED_UNIT=SPEC-008
ACTIVE_SPEC=SPEC-008
BASELINE_ONLY_COMMITS=faa4e8a6,33313d3c,35f53c97,4dedc876,595c3911,3271ac4d,63ce1301,eeecb2af
LEDGER=docs/roadmap/goals/ledgers/GOAL-EXECUTION-LOOP-LEDGER-adr-0009-pretooluse-ceiling-linear-slices.md
MAY_EDIT=yes

## SPEC-008

spec_id: `SPEC-008`
spec_version: `GOAL-SUPER-SPEC-adr-0009-pretooluse-ceiling-linear-slices.md@ed494d0552fc28d7d314996793679f37aaa247bf`
attempt: `1`
repair_count: `0`
audit_repair_cycle: `0`
first_unexecuted_unit: `SPEC-008`
failed_attempt_recovery_decision: `not_applicable`
commit: no-commit: active SPEC opened before material commit; commit hash is captured in parent validation after local commit
oracle_status: `PASS: py_compile, tes_install self-test, host_runtime_matrix_oracle, hook_audit_prompt_oracle, pretooluse_kernel_oracle, pretooluse_session_oracle, pretooluse_contract_oracle, and mantra_gate_pretooluse_oracle`
structural_method_id: `runtime-script-internal-sections`
topology_decision: `hook-health additive contract extension`
topology_decision_artifact: `ledger-section`
structural_debt: `none`
next_structural_constraint: `SPEC-009 owns final audit prompt projection; SPEC-008 must not claim PASS_CEILING without installed ceiling evidence`
topology_probe_result: `PASS: no new modules; additive hook-health payload extension plus docs/oracle update`
browser_metrics_contract: `not_applicable`
visual_spatial_oracle: `not_applicable`
browser_attempt: `not_applicable`
visual_evidence: `not_applicable`
runtime_smoke_oracle: `PASS: host runtime matrix reports hook_health_floor_status=NEEDS_EVIDENCE and hook_health_ceiling_status=NEEDS_FLOOR without PASS_CEILING collapse`
adversary_objection: `none`
shared_contract_extended: `yes`
extension_point_proven: `yes: hook-health emits schema tes-hook-health@2, legacy_schema tes-hook-health@1, status, floor_status, ceiling_status, and ceiling_gaps`
contract_handoff_artifact: `ledger-section`
api_lint_status: `not_applicable`
auditor_distinct_from_operator: `not_applicable`
auditor_rewrote_no_oracle: `not_applicable`
audit_remutation: `PASS: hook_audit_prompt_oracle red-capability mutants cover hook-health v2 split, floor/ceiling fields, PASS_BASIC not PASS_CEILING, and ceiling gap rule`
distinct_refuters: `not_applicable`
stop_state: `READY_TO_COMMIT`
next_allowed_action: `stage only SPEC-008 files and commit locally`
