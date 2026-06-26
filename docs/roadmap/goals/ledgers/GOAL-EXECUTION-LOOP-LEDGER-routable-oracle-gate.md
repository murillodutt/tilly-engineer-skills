---
tds_id: roadmap.goal_ledger_routable_oracle_gate
tds_class: roadmap
status: active
consumer: maintainers and execution agents reviewing the goal-execution loop record
source_of_truth: false
evidence_level: L1
tver: 0.1.0
---

# GOAL-EXECUTION-LOOP-LEDGER — routable-oracle-gate

Anchor: docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-goal-maestro-routable-oracle-gate.md (Super-SPEC, git hash-object b70acfa7ea95a74f54a14e19bfac54b945efed99)

## Execution Cost Draft (from material sources)

- Source artifacts: the anchor Super-SPEC (11 units SPEC-000→010); the harness 4 surfaces; `staged_commit_gate.py`; `package.json` (commit:check/closure); `validate_reference_package.py`; `tes_init.py`.
- Declared SPEC order: SPEC-000 (preflight) → 001 (A1 check23 two-layer) → 002 (A2b des-hardcode) → 003 (A2 re-mutation wiring) → 004 (A3 SKILL claim) → 005 (I1 router Gate) → 006 (I2 closure) → 007 (A4 src↔src parity) → 008 (B1/B2 installer detect+propose) → 009 (B3 regression_target write) → 010 (closeout+bump).
- Dependency edges: 001→002→003 (check23 concept before its mjs impl); 005→006 (router Gate before closure entry); 002/003 inform 008/009 (installer must register what the harness reads). 010 last (bump).
- Risk: 4-surface fidelity drift; validate-walls regression (invariant 27/27); cross-stack hardcode removal must not break this repo's GitHub-less reality.
- Expected oracles: `validate-walls.mjs` (every SPEC, exit 0); `commit:check`/`:plan`; `validate_reference_package.py` empirical parity test; `tes_init.py --self-test`; `anchor-rehash.mjs`.
- Expected commits: one local per SPEC, no push.
- Likely repair points: 003 (re-mutation logic is the hardest mjs change); 008/009 (installer detection across stacks).
- Final stop: EXECUTION_LOOP_COMPLETE after Executive Stop Audit (distinct auditor, re-mutation).
- Baseline worktree classification: clean; only the anchor untracked (current-loop material); ahead 3 (prior session commits, baseline-only).
- Canonical SPEC repair target: the anchor Super-SPEC (SPEC_REPAIR_BY_LLM target).
- Audit budget: 1 batch SPEC-AUDIT-* if NEEDS_MORE_LOOPS.
- Structural method: coding SPECs 003/005/007/008/009 carry Engineering Method Profile; topology probe via line-count where mjs/py grow.
- Runtime/visual/integration: not_applicable (no browser/UI/game axis; the "integration" here is gate-routing, proven by re-mutation not browser smoke).
- Shared contracts: `regression_target` field (context-completeness.mjs:13) is the cross-unit contract; extension-only.
- Source-derived handoff: workers reuse `lib/harness.mjs`, `audit-remutation.mjs` pattern, `staged_commit_gate.py` Gate dataclass, `validate_reference_package.py` parity molde — source snippets handed in envelope.
- Tree Adversary: see status below.
- Ledger path: GOAL-EXECUTION-LOOP-LEDGER-routable-oracle-gate.md (this file).

## Tree Adversary (pre-execution)

tree_adversary_status=OBJECTIONS_REPAIRED
adversary_objections=B3 originally "discover by execution without pointer" (facade risk: naive gate exit-0 is subdetermined); A2 originally ".includes mention".
adversary_repair_evidence=B3 reformed to declared-pointer (regression_target, existing) + gate re-mutation proof (SPEC-003); A2 reformed to audit-remutation pattern; A2b added to des-hardcode cross-stack. Stress-tested by 3 independent lenses before anchor materialization (descobribilidade BROKE the naive version → repaired; custo/coerência SURVIVES_WITH_CAVEAT → caveats folded into SPEC-003).

## Ledger Entries

### SPEC-001 (fused A1+A2b)
spec_id: SPEC-001
spec_version: 2 (post SPEC_REPAIR_BY_LLM fuse)
attempt: 1
repair_count: 1
audit_repair_cycle: 0
first_unexecuted_unit: SPEC-003
failed_attempt_recovery_decision: not_applicable
commit: 012d9588
oracle_status: PASS (4-surface parity OK; validate-walls 27/27; doc-size PASS; hardcode GitHub removed)
structural_method_id: doc-surface-edit
topology_decision: not_applicable
topology_decision_artifact: not_applicable
structural_debt: none
next_structural_constraint: check 23 now references regression_target; SPEC-003 oracle-wiring-check.mjs must read that pointer
topology_probe_result: not_applicable
browser_metrics_contract: not_applicable
visual_spatial_oracle: not_applicable
browser_attempt: not_applicable
visual_evidence: not_applicable
runtime_smoke_oracle: not_applicable
adversary_objection: repaired
shared_contract_extended: yes (regression_target named as gate pointer)
extension_point_proven: yes (field pre-exists in context-completeness.mjs:13)
contract_handoff_artifact: ledger-section
api_lint_status: not_applicable
auditor_distinct_from_operator: not_applicable
auditor_rewrote_no_oracle: not_applicable
audit_remutation: not_applicable
stop_state: active_spec_committed
next_allowed_action: worker_attempt (SPEC-003)

### SPEC-003 (A2: oracle-wiring-check by gate re-mutation)
spec_id: SPEC-003
spec_version: 1
attempt: 1
repair_count: 0
audit_repair_cycle: 0
first_unexecuted_unit: SPEC-005
failed_attempt_recovery_decision: not_applicable
commit: b8a0ab04
oracle_status: PASS (suite 27/27 in all 4 surfaces; D3 facade→exit1, wired→exit0, oracle-as-gate barred; 3-lens design stress: residual trust-boundary documented in-code)
structural_method_id: mjs-harness-edit
topology_decision: single-file harness rewrite (oracle-wiring-check.mjs), mirrors audit-remutation.mjs structure
topology_decision_artifact: ledger-section
structural_debt: residual — cannot prove (node-pure) that declared gate_command IS the persistent gate at regression_target; documented in-code; full closure needs installed-target canary (out of unit scope)
next_structural_constraint: SPEC-009 installer must write a gate_command/regression_target the harness can re-mutate
topology_probe_result: not_applicable (line count well within budget; mirrors existing harness)
browser_metrics_contract: not_applicable
visual_spatial_oracle: not_applicable
browser_attempt: not_applicable
visual_evidence: not_applicable
runtime_smoke_oracle: not_applicable
adversary_objection: repaired (naive exit-0 → gate re-mutation + mandatory decoy negative control + anti-oracle-as-gate)
shared_contract_extended: yes (oracle-wiring-check input schema: requiredOracles/wiredText → oracles[]{gate_command,oracle_command,mutate,decoy_mutate,regression_target})
extension_point_proven: yes (D3 fixture rewritten to new schema, suite green)
contract_handoff_artifact: ledger-section
api_lint_status: not_applicable
auditor_distinct_from_operator: not_applicable
auditor_rewrote_no_oracle: not_applicable
audit_remutation: not_applicable
stop_state: active_spec_committed
next_allowed_action: worker_attempt (SPEC-005)

### SPEC-004 (A3: SKILL.md:67 agnostic claim)
spec_id: SPEC-004 | spec_version: 1 | attempt: 1 | repair_count: 0 | audit_repair_cycle: 0
first_unexecuted_unit: SPEC-005 | failed_attempt_recovery_decision: not_applicable
commit: fa100f4f
oracle_status: PASS ((also wired in CI) removed from 4 surfaces; validate-walls 27/27; doc-size PASS)
structural_method_id: doc-surface-edit | topology_*: not_applicable | structural_debt: none
next_structural_constraint: none
runtime/visual/browser fields: not_applicable
adversary_objection: not_applicable | shared_contract_extended: no
contract_handoff_artifact: not_applicable | api_lint_status: not_applicable
audit_* fields: not_applicable
stop_state: active_spec_committed | next_allowed_action: worker_attempt (SPEC-005)

### SPEC-005 (I1: validate-walls as declarative Gate in staged router)
spec_id: SPEC-005 | spec_version: 1 | attempt: 1 | repair_count: 0 | audit_repair_cycle: 0
first_unexecuted_unit: SPEC-006 | failed_attempt_recovery_decision: not_applicable
commit: 17919070
oracle_status: PASS (--plan: walls gate SKIP when no .mjs staged, RUN when a .mjs is staged; END-TO-END: broken wall staged → gate FAIL [commit-gate]; restored → 27/27. THIS is staged-wired proof per check 23.)
structural_method_id: py-router-gate-add | topology_decision: declarative Gate in gate_plan() (mirrors existing Gate entries) | structural_debt: none
next_structural_constraint: SPEC-006 adds same wall to closure (closure-wired layer)
runtime_smoke_oracle: pass (gate executed end-to-end, observed FAIL on broken wall) | adversary_objection: not_applicable
shared_contract_extended: no | contract_handoff_artifact: not_applicable | api_lint_status: not_applicable
audit_* fields: not_applicable
stop_state: active_spec_committed | next_allowed_action: worker_attempt (SPEC-006)

### SPEC-006 (I2: validate-walls in commit:closure)
spec_id: SPEC-006 | spec_version: 1 | attempt: 1 | repair_count: 0 | audit_repair_cycle: 0
first_unexecuted_unit: SPEC-007 | failed_attempt_recovery_decision: not_applicable
commit: d23a3ac0
oracle_status: PASS (package.json JSON valid; validate-walls.mjs in commit:closure chain; closure-wired confirmed by running ref-pkg + walls elos). check 23 now true in BOTH layers (staged SPEC-005 + closure SPEC-006).
structural_method_id: package-json-chain-edit | topology_decision: not_applicable | structural_debt: none
next_structural_constraint: SPEC-010 bump must update VERSION here too
runtime/visual/browser fields: not_applicable | adversary_objection: not_applicable
shared_contract_extended: no | contract_handoff_artifact: not_applicable | api_lint_status: not_applicable
audit_* fields: not_applicable
stop_state: active_spec_committed | next_allowed_action: worker_attempt (SPEC-007)

### SPEC-007 (A4: src↔src wall parity in closure)
spec_id: SPEC-007 | spec_version: 1 | attempt: 1 | repair_count: 0 | audit_repair_cycle: 0
first_unexecuted_unit: SPEC-008 | failed_attempt_recovery_decision: not_applicable
commit: f09d0b7a
oracle_status: PASS (goal_maestro_scripts_parity_failures added, reusing local_development_skill_parity_failures molde rglob+read_bytes; plugged in main() after line 1138. EMPIRICAL: baseline PASS; divergence in claude token-budget.mjs → FAIL 'claude/codex source drift'; reverted → PASS. The silent-divergence hole is now closed.)
structural_method_id: py-parity-fn-add | topology_decision: glob/walk fn (not REQUIRED_PATHS literal list) | structural_debt: none
next_structural_constraint: none
runtime/visual/browser fields: not_applicable | adversary_objection: not_applicable
shared_contract_extended: no | contract_handoff_artifact: not_applicable | api_lint_status: not_applicable
audit_* fields: not_applicable
stop_state: active_spec_committed | next_allowed_action: worker_attempt (SPEC-008)

### SPEC-008+009 (B1/B2 detect+propose; B3 declare-in-mesh) — post SPEC_REPAIR_BY_LLM
spec_id: SPEC-008+009 | spec_version: 2 (post B-reframe repair) | attempt: 1 | repair_count: 1 | audit_repair_cycle: 0
first_unexecuted_unit: SPEC-010 | failed_attempt_recovery_decision: not_applicable
commit: f75204b1
oracle_status: PASS-with-AXIS_UNPROVEN-handoff. detect_persistent_gates() agnostic closed signal (executable non-sample pre-commit, core.hooksPath-aware) — DOGFOODING caught a real false-negative: this repo uses core.hooksPath=.githooks; fixed case-insensitive hookspath parse; now detects active=lefthook. Proposal always written to QUALITY-GATES mesh (declare-in-mesh = honest install-time seam). self-test PASS. Install verb (--install-gate) deferred as handoff (highest-risk, deserves own canary). regression_target end-to-end derivation by a subsequent goal-maestro: AXIS_UNPROVEN (node-pure cannot prove; canary handoff).
structural_method_id: py-installer-detect | topology_decision: new fn detect_persistent_gates near stack_signals + 1 row in QUALITY-GATES writer | structural_debt: install verb + regression_target-read canary deferred (declared, not masked)
next_structural_constraint: SPEC-010 bump; canary must prove goal-maestro reads the declared gate
runtime_smoke_oracle: pass (detect_persistent_gates exercised on synthetic fixtures + this real repo) | adversary_objection: repaired (3-lens: closed signal kills tool-list; two verbs un-fused; registro reframed to mesh-declare)
shared_contract_extended: yes (QUALITY-GATES mesh now carries Persistent gate row) | extension_point_proven: yes (writer extended, self-test green)
contract_handoff_artifact: ledger-section + QUALITY-GATES mesh row | api_lint_status: not_applicable
audit_* fields: not_applicable
stop_state: active_spec_committed | next_allowed_action: worker_attempt (SPEC-010)

### SPEC-010 (closeout + bump 0.3.194→0.3.195)
spec_id: SPEC-010 | spec_version: 1 | attempt: 1 | repair_count: 0 | audit_repair_cycle: 0
first_unexecuted_unit: none (all units executed) | failed_attempt_recovery_decision: not_applicable
commit: 9baa3acf
oracle_status: PASS (tes_bump.py patch --yes: 67 targets in sync; staged_commit_gate.py added to bump.json; package-lock.json synced; validate-walls 27/27; tes_init self-test PASS). docs/dist/0.3.195 bundle is sync/release scope (not this loop, no push).
structural_method_id: version-bump | topology_decision: not_applicable | structural_debt: none
next_structural_constraint: none
runtime/visual/browser fields: not_applicable | adversary_objection: not_applicable
audit_* fields: not_applicable (written by Executive Stop Audit reviewer next)
stop_state: active_spec_committed → ready for Executive Stop Audit | next_allowed_action: audit

(one entry per SPEC, appended as the loop advances)

## SPEC-AUDIT-001 (Executive Stop Audit repair)
audit_repair_cycle: 1
finding_1: anchor hash in ledger was stale (declared 69245eb4 ≠ real). Anchor was edited mid-loop by two SPEC_REPAIR_BY_LLM (69245eb4→1004fb2c→b70acfa7). Repaired: ledger now declares the real, now-final anchor hash; anchor is immutable from here.
finding_2: ledger placeholders (<pending>) were committed at loop HEAD 9baa3acf; SHA backfill was uncommitted. Repaired: real SHAs committed in this audit-repair commit.
auditor_distinct_from_operator: yes
auditor_rewrote_no_oracle: yes
audit_remutation: ran (items 2,3,4,5 — no facades found; oracles sound)
stop_state: EXECUTION_LOOP_COMPLETE_WITH_AUDIT_REPAIRS (pending this repair commit)

## FINAL STATUS — EXECUTION_LOOP_COMPLETE_WITH_AUDIT_REPAIRS

Re-audit (independent, clean checkout of HEAD 49bcc56c) confirmed:
- Finding 1 (anchor hash stale) CLOSED: ledger declares b70acfa7 == git hash-object; anchor-rehash exit 0 (wrong hash exit 1).
- Finding 2 (ledger placeholders) CLOSED: ledger-no-placeholder exit 0; 8 real resolvable SHAs.
- Invariant: validate-walls 27/27 exit 0.
- Oracles sound (no facades): oracle-wiring facade→exit1, parity drift caught/clean.
- AUDITOR_DISTINCT_FROM_OPERATOR=yes | AUDITOR_REWROTE_NO_ORACLE=yes | audit_remutation=ran (1st pass items 2,3,4,5).

Release/sync handoff (NOT a loop blocker): docs/dist/0.3.195 bundle unbuilt; build+commit before any sync/release.
Canary handoff (SPEC-009 AXIS_UNPROVEN): prove a subsequent goal-maestro derives regression_target from the QUALITY-GATES mesh declaration on an installed target.
