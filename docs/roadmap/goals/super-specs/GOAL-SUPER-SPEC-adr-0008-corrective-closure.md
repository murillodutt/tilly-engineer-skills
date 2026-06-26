---
tds_id: roadmap.goal_super_spec_adr_0008_corrective_closure
tds_class: roadmap
status: active
consumer: maintainers, Goal Maestro authors, release reviewers, execution agents, and audit agents
source_of_truth: false
evidence_level: L1
tver: 0.1.0
---

# GOAL Super SPEC: ADR 0008 Corrective Closure

Status: active corrective closure plan. This document closes ADR 0008 honestly. It does not deliver runtime behavior, change hooks, re-execute prior commits, certify retroactive worker lifecycle, or change release identity.

## Objective

Separate the product result from the execution-harness result:

- `host_aware_runtime_product=PASS`: local product evidence for ADR 0008 is strong and already committed.
- `tes_goal_maestro_execute_loop=DEGRADED`: the material commits do not prove one fresh worker/subagent lifecycle per `ACTIVE_SPEC`.

Both facts must stay visible. A strong product result must not erase a degraded execution trail.

## Closure Rule

Runtime evidence may pass while harness evidence remains degraded. Do not merge those claims. Do not backfill worker lifecycle for commits that were already created by the parent executor. Do not reexecute ADR 0008 only to manufacture redundant commits.

## Boundary

Allowed files: this document, `docs/INDEX.md`, `docs/tds/DOCS-INDEX.yml`, and narrow evidence docs if a later owner request requires them.

Forbidden moves: runtime edits, installer edits, hook edits, adapter edits, package bump, public bundle, release, push, tag, publish, secrets, destructive Git, and any claim that prior commits were worker-executed without explicit owner acceptance.

## Units

1. **SPEC-000 Baseline**
   - Verify Git status, ADR 0008 anchor, recent commits, loop ledger, and `ledger-no-placeholder`.
   - Expected result: product commits exist; ledger placeholder oracle passes; execute-loop lifecycle remains degraded.

2. **SPEC-001 Closure Record**
   - Record the final split verdict: `product/runtime=PASS`, `execute-loop-evidence=DEGRADED`.
   - If the owner explicitly accepts the prior commits as material credit, record `ACCEPTED_WITH_PROCESS_EXCEPTION`.
   - Otherwise keep `NEEDS_OWNER_DECISION`.

3. **SPEC-002 Sentinel Handoff**
   - Preserve `tes-loop-sentinel` as the next product target for preventing ledger debt, subagent collapse, false green, and long-loop degradation.
   - Do not implement Sentinel in this closure unit.

4. **SPEC-003 Local Validation**
   - Run `python3 scripts/validate_tds.py`, `python3 scripts/validate_reference_package.py`, focused doc-size/private-vocabulary checks, `git diff --check`, and `npm run commit:check`.
   - Commit message: `docs/spec: add adr 0008 corrective closure`.

## Done

This closure is complete when ADR 0008 is reported as locally product-certified, the execute-loop limitation is explicitly preserved, `tes-loop-sentinel` remains the next implementation target, all docs oracles pass, and no runtime/release behavior is changed.
