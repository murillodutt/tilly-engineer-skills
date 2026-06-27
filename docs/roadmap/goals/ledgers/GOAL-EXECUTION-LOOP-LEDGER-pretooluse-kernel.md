---
tds_id: roadmap.goal_execution_loop_ledger_pretooluse_kernel
tds_class: roadmap
status: active
consumer: maintainers, hook authors, installer authors, oracle authors, release reviewers, and hook-audit operators
source_of_truth: false
evidence_level: L1
tver: 0.1.0
---

# PreToolUse Kernel Execution Ledger

Anchor: docs/install/HOOK-AUDIT-PROMPT.md (SPEC, git hash-object 39648f51893df783ade299eaa5afd57f008fcad2)
- anchor_class=SPEC
- anchor_path=docs/install/HOOK-AUDIT-PROMPT.md
- anchor_hash=0173bc105422e57a6354b6057cf25931438a91444969e075e5b1e100e02d1a9b
- anchor_origin=provided

Tree adversary:
- tree_adversary_status=ADVERSARY_CLEARED
- adversary_objections=scope must not change host output contracts; oracle must prove parity
- adversary_repair_evidence=bounded units preserve host renderers and add source parity oracle

## SPEC-000

spec_id: SPEC-000
spec_version: baseline
attempt: 1
repair_count: 0
audit_repair_cycle: 0
first_unexecuted_unit: SPEC-001
failed_attempt_recovery_decision: none
commit: no-commit (preflight baseline capture only; final sha is the commit that includes this ledger)
oracle_status: PASS
structural_method_id: python-runtime-script-module-split
topology_decision: module-split
topology_decision_artifact: this ledger
structural_debt: none
next_structural_constraint: preserve host-specific output rendering in scripts/tes_install.py
topology_probe_result: PASS
browser_metrics_contract: not_applicable
visual_spatial_oracle: not_applicable
browser_attempt: not_applicable
visual_evidence: not_applicable
runtime_smoke_oracle: scripts/mantra_gate_pretooluse_oracle.py --self-test
adversary_objection: repaired
shared_contract_extended: yes
extension_point_proven: yes
contract_handoff_artifact: docs/install/HOOK-AUDIT-PROMPT.md
api_lint_status: not_applicable
auditor_distinct_from_operator: not_applicable
auditor_rewrote_no_oracle: not_applicable
audit_remutation: not_applicable
distinct_refuters: not_applicable
stop_state: GO
next_allowed_action: SPEC-001

## SPEC-001

spec_id: SPEC-001
spec_version: kernel-extraction
attempt: 1
repair_count: 1
audit_repair_cycle: 1
first_unexecuted_unit: SPEC-002
failed_attempt_recovery_decision: `host-runtime-matrix first failed because installed target lacked pretooluse_kernel.py; repaired by adding the helper to every delivered helper list`
commit: no-commit (included in final 0.3.217 kernel commit)
oracle_status: PASS
structural_method_id: python-runtime-script-module-split
topology_decision: internal-subsystem
topology_decision_artifact: `scripts/pretooluse_kernel.py`
structural_debt: none
next_structural_constraint: `host-specific renderers and runtime ledger writes remain in scripts/tes_install.py`
topology_probe_result: `python3 scripts/pretooluse_kernel_oracle.py PASS; python3 scripts/host_runtime_matrix_oracle.py --self-test PASS`
browser_metrics_contract: not_applicable
visual_spatial_oracle: not_applicable
browser_attempt: not_applicable
visual_evidence: not_applicable
runtime_smoke_oracle: `python3 scripts/tes_install.py --self-test PASS`
adversary_objection: `kernel extraction can break installed helper imports`
shared_contract_extended: yes
extension_point_proven: yes
contract_handoff_artifact: `scripts/pretooluse_kernel_oracle.py`
api_lint_status: not_applicable
auditor_distinct_from_operator: not_applicable
auditor_rewrote_no_oracle: false
audit_remutation: not_applicable
distinct_refuters: not_applicable
stop_state: GO
next_allowed_action: SPEC-002

## SPEC-002

spec_id: SPEC-002
spec_version: documentation-and-oracle
attempt: 1
repair_count: 0
audit_repair_cycle: 0
first_unexecuted_unit: SPEC-003
failed_attempt_recovery_decision: none
commit: no-commit (included in final 0.3.217 kernel commit)
oracle_status: PASS
structural_method_id: associated-documentation
topology_decision: documented-internal-contract
topology_decision_artifact: `docs/architecture/INSTALLATION-FRAMEWORK.md; docs/architecture/PROJECT-STRUCTURE.md; docs/install/AGENT-ORACLE-INVENTORY.md; docs/tds/DOCS-INDEX.yml`
structural_debt: none
next_structural_constraint: `new code must keep direct module docs or indexed Markdown contract docs`
topology_probe_result: `python3 scripts/validate_tds.py PASS; python3 scripts/build_public_docs.py --check PASS`
browser_metrics_contract: not_applicable
visual_spatial_oracle: not_applicable
browser_attempt: not_applicable
visual_evidence: not_applicable
runtime_smoke_oracle: `python3 scripts/runtime_topology_oracle.py --self-test PASS`
adversary_objection: cleared
shared_contract_extended: yes
extension_point_proven: yes
contract_handoff_artifact: `scripts/pretooluse_kernel_oracle.py`
api_lint_status: not_applicable
auditor_distinct_from_operator: not_applicable
auditor_rewrote_no_oracle: false
audit_remutation: not_applicable
distinct_refuters: not_applicable
stop_state: GO
next_allowed_action: SPEC-003

## SPEC-003

spec_id: SPEC-003
spec_version: release-identity-and-installed-proof
attempt: 1
repair_count: 1
audit_repair_cycle: 1
first_unexecuted_unit: SPEC-004
failed_attempt_recovery_decision: `tes-npx self-test failed because bin/tes.js lacked executable permission in the filesystem; chmod restored executable local package execution and the bundle was republished`
commit: no-commit (included in final 0.3.217 kernel commit)
oracle_status: PASS
structural_method_id: bundle-scope-release-identity
topology_decision: package-version-advanced
topology_decision_artifact: `package.json 0.3.217; docs/dist/0.3.217`
structural_debt: none
next_structural_constraint: `do not claim remote release before push/tag/release gates are explicitly authorized`
topology_probe_result: `python3 scripts/tes_bump.py --governance-check --json PASS; python3 scripts/public_bundle_oracle.py PASS`
browser_metrics_contract: not_applicable
visual_spatial_oracle: not_applicable
browser_attempt: not_applicable
visual_evidence: not_applicable
runtime_smoke_oracle: `npx --yes --package <local-package> -- tilly-engineer-skills add --agent all --yes PASS on target-project`
adversary_objection: `local npx package can fail before Python installer starts if bin shim is not executable`
shared_contract_extended: yes
extension_point_proven: yes
contract_handoff_artifact: `scripts/tes_npx_oracle.py`
api_lint_status: not_applicable
auditor_distinct_from_operator: not_applicable
auditor_rewrote_no_oracle: false
audit_remutation: not_applicable
distinct_refuters: not_applicable
stop_state: GO
next_allowed_action: SPEC-004

## SPEC-004

spec_id: SPEC-004
spec_version: final-gates
attempt: 1
repair_count: 0
audit_repair_cycle: 0
first_unexecuted_unit: none
failed_attempt_recovery_decision: none
commit: no-commit (sha is the local commit that includes this ledger)
oracle_status: PASS
structural_method_id: local-commit-closure
topology_decision: local-commit-ready
topology_decision_artifact: `staged 0.3.217 source package and target-project install proof`
structural_debt: none
next_structural_constraint: `npm run commit:check must pass before local commit`
topology_probe_result: `npm run commit:check PASS`
browser_metrics_contract: not_applicable
visual_spatial_oracle: not_applicable
browser_attempt: not_applicable
visual_evidence: not_applicable
runtime_smoke_oracle: `local npx target-project install PASS; installed hook-health PASS; installed certification PASS`
adversary_objection: `commit gate caught ledger placeholders and EOF whitespace; repaired before commit`
shared_contract_extended: yes
extension_point_proven: yes
contract_handoff_artifact: this ledger
api_lint_status: not_applicable
auditor_distinct_from_operator: not_applicable
auditor_rewrote_no_oracle: false
audit_remutation: not_applicable
distinct_refuters: not_applicable
stop_state: GO
next_allowed_action: `commit locally after npm run commit:check PASS; no push/tag/release without owner authorization`
