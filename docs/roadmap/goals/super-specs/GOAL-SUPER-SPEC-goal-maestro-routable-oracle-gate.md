---
tds_id: roadmap.goal_super_spec.goal_maestro_routable_oracle_gate
tds_class: roadmap
status: active
consumer: maintainers, Goal Maestro authors, installer authors, oracle authors, release reviewers, and execution agents
source_of_truth: true
evidence_level: L2
tver: 0.1.0
---

# Goal Maestro Routable-Oracle Gate Super SPEC

Status: active pre-implementation SPEC. Anchor artifact for an explicitly requested `--execute-loop`.

Purpose: remove the **leaked-environment dependency** from the `tes-goal-maestro` harness — it was built in an isolated environment with a husky pre-commit gate and absorbed that environment as structural property (`.husky/pre-commit` as a hardcoded default-example, `(also wired in CI)` claimed in `SKILL.md:67`, and `.github/workflows/`+`certify` hardcoded in the check-23 contract). This repo now uses **Lefthook** with an inverted commit contract (`commit:check` = staged-scoped router, `commit:closure` = opt-in full closure). Elevate the harness from *"grep textual of a gate it recognizes"* to a **routable-oracle contract**: the harness emits an axis oracle that ANY persistent gate routes by staged path, and proves "wired" by **re-mutation of the gate**, never by mention. The installer chooses the tool; the harness never knows which.

## Reverse Analysis

Reverse failure path if not done:
1. The harness stays stack-locked to JS/GitHub — `GO` is unreachable on Python/Go targets (no `.github/workflows/`, no `certify`), so the product fails its "runs on hundreds of stacks" mandate.
2. `oracle-wiring-check.mjs` keeps proving *mention* (`.includes(oracle)`), a facade one level above the oracles it exists to police — the harness commits the facade it teaches others to detect.
3. The `(also wired in CI)` claim stays false against this repo's actual gate (Lefthook/`commit:check`), violating the harness's own check 23.
4. The executable walls can silently diverge between adapters (src/claude ↔ src/codex), since no closure gate compares them.

Correct move:

```text
The installer chooses the tool (Lefthook/husky/...). The harness never names it.
The harness reads one declared pointer (regression_target, already in the Worker Packet).
"Wired" is proven by re-mutation of the gate, not by mention or naive exit-0.
```

## Anchor & Source

- This Super SPEC is the persisted non-self anchor for the loop. `anchor-rehash.mjs` recomputes its `git hash-object` at the Pre-Edit Gate.
- Stress-tested: the B3 seam survived a 3-lens adversarial pass (descobribilidade BREAKS → reformulated; custo SURVIVES_WITH_CAVEAT → `--plan` proves routing not PASS; coerência SURVIVES_WITH_CAVEAT → gate-level re-mutation required).
- Prior state verified: Lefthook installed and tested (2 local commits); `staged_commit_gate.py` already routes `tes-goal-maestro` parity for the `.agents`↔`.claude` mirror pair (`local_skill_parity_failures()` l.100-128) — so A4 is scoped to the **src↔src** source pair only.

## Central Rule

```text
Affirmation is never credit. The harness names no tool; it reads one declared
pointer (regression_target) and proves the gate routes the oracle by re-mutation.
```

## Phase Boundary

In scope: harness contract surfaces (`tes-goal-maestro` 4 mirrors), the repo's gate router (`staged_commit_gate.py`, `package.json`), the source-parity gate (`validate_reference_package.py`), and the installer (`tes_init.py`/`tes-setup`). Out of scope: rewriting wall logic (the 27 walls converge and stay frozen), remote sync/push, any new state-channel artifact.

## Non-Objectives

- No `.tes/runtime-config.json` or any new state channel (reuse `regression_target`).
- No tool list in the harness (no husky/lefthook enumeration in harness code).
- No change to the 27 walls' logic or to `lib/harness.mjs` 3-state contract.

## Forbidden Moves

- Do not let the harness read "which tool" the gate is.
- Do not prove wiring by `.includes()` (mention) nor by naive gate exit-0 (a gate that never invokes the oracle also exits 0).
- Do not hardcode `.github/workflows/`/`certify` (stack-lock).
- Do not diverge the 4 surfaces; do not diverge src/claude ↔ src/codex `.mjs`.
- Do not auto-install husky/Lefthook without owner approval (necessary-for-quality, not mandatory-for-use).

## Execution Units (ordered queue)

### SPEC-000 Preflight And Baseline
`git status --short --branch --untracked-files=all`; recent `git log`; confirm Lefthook gate present; run `node .../validate-walls.mjs` (must be 27/27, exit 0) as read-only baseline. No-commit unless baseline docs in scope.

### SPEC-001 — A1+A2b FUSED (SPEC_REPAIR_BY_LLM): check-23 two-layer + cross-stack (4 surfaces)
> SPEC_REPAIR_BY_LLM (proposed and executed by the LLM, not a human): execution proved A1 (two-layer "wired") and A2b (des-hardcode cross-stack) touch the SAME indivisible block (check 23 + line 265). Splitting them would create an incoherent intermediate commit ("two layers but still GitHub-locked") — the simulated rhythm the harness forbids. Lens applied: do not saw an atomic block into artificial commits. The queue is now 10 units; attempt counter reset for this contract change.
`references/quality-gates.md:263-265`: distinguish **staged-wired** (dev `GO`) from **closure-wired** (seal/release); tool-agnostic "persistent gate"; proof is execution not text presence; AND replace literal `.github/workflows/`+`certify` with the per-axis `regression_target` (`context-completeness.mjs:13`) so the gate is cross-stack (Lefthook/pre-commit/CI-per-workspace/Makefile). No-gate → `DEGRADED`/`AXIS_UNPROVEN`, never `GO`. One commit, 4 surfaces.

### SPEC-003 — A2: oracle-wiring-check by gate re-mutation (4 surfaces)
`oracle-wiring-check.mjs`: replace `.includes(oracle)` (l.61) with the `audit-remutation.mjs:73-79` pattern at the gate level — (1) run gate clean → must pass; (2) re-mutate the named axis property → gate must exit≠0; (3) revert. Remove `.husky/pre-commit` hardcoded default (l.12) → agnostic examples incl. Lefthook. Reuse `lib/harness.mjs`.
Oracle: `node validate-walls.mjs` D3 fixture still converges; new re-mutation path fires on a gate that does not route the oracle.

### SPEC-004 — A3: SKILL.md:67 agnostic claim (4 surfaces)
`(also wired in CI)` → routable-oracle description; this repo routes via `staged_commit_gate.py` (staged) and `commit:closure` (seal). Lefthook as one example among many.

### SPEC-005 — I1: validate-walls as a declarative Gate in the router
Add a `Gate(matcher, file_filter)` in `staged_commit_gate.py` `gate_plan()` (l.210) matching `*/skills/tes-goal-maestro/scripts/*.mjs` → `node .../validate-walls.mjs`. Staged-scoped regression net.
Oracle: `commit:check:plan` shows the wall gate `RUN` when a `.mjs` is staged, `SKIP` otherwise.

### SPEC-006 — I2: validate-walls in commit:closure
Add `node src/adapters/claude/skills/tes-goal-maestro/scripts/validate-walls.mjs` to `commit:closure` (`package.json:125`). The seal layer re-runs the full wall suite. I1+I2 make check 23 true in this repo by construction.

### SPEC-007 — A4: src↔src wall parity in closure
Add `goal_maestro_scripts_parity_failures()` to `validate_reference_package.py` (reuse `local_development_skill_parity_failures()` molde, `.rglob`+`.read_bytes`, l.807-838), comparing `src/adapters/claude/.../scripts` ↔ `src/adapters/codex/.../scripts`. Plug in `main()` ~l.1097.
Oracle (empirical): inject divergence in one adapter `.mjs` → fails; revert → passes. (The `.agents`↔`.claude` mirror pair is already covered by the staged gate — do not duplicate it.)

### SPEC-008 — B1/B2: installer detects + proposes gate (delivered)
`tes_init.py`: `detect_persistent_gates()` (reuse `stack_signals()` l.752); detect target gate (Lefthook/husky/pre-commit/CI/git-hooks) + file types. `/tes-setup`: respect existing gate; if none, **propose** the best-fit model (Lefthook default; husky when target is husky-centric), inform necessary-for-quality, install only on approval, hooks per file type. Reuse `install_<agent>_hook()` + `write_text_if_changed()`.

### SPEC-009 — B3: write/confirm regression_target (delivered)
`/tes-setup` writes/confirms the per-axis `regression_target` (the existing Worker Packet pointer) for the target — the act that materializes the seam. No new state channel.

### SPEC-010 — Closeout & version
Bump 0.3.194 → 0.3.195 (A+B are delivered); update `staged_commit_gate.py:21` VERSION; correlated surfaces per `MAINTAINER-CORRELATION-RULE.md`. Executive Stop Audit (distinct auditor, re-mutation).

## Per-SPEC Oracles, Commit Strategy, Stop States

- One local commit per SPEC; material-diff (`git show --stat`); focused oracle run with literal exit-code; sync `LOCAL_COMMITTED`. No push.
- Coding-surface SPECs (003, 005, 007, 008, 009) carry an Engineering Method Profile.
- Stop states: `NEEDS_CONTEXT` (missing `regression_target`), `NEEDS_TREE_REPAIR`, `NEEDS_STRUCTURAL_METHOD`, `AXIS_UNPROVEN`, `NEEDS_OWNER_DECISION`, `NEEDS_INDEPENDENT_AUDIT`, `EXECUTION_LOOP_COMPLETE`.

## Final Delivery Contract

Units executed; commits + `git show --stat` per SPEC; oracles run (incl. `validate-walls` 27/27, src↔src parity empirical test, `tes_init --self-test`); 4-surface parity preserved; check 23 cross-stack and re-mutation-proven; bump + correlated surfaces; Executive Stop Audit with `audit_remutation=ran`; anchor hash validated; final status.
