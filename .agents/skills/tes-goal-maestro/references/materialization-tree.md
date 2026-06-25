# Materialization Tree

Use this reference when a mature SPEC, Super SPEC, PRD, relational project plan or accepted execution tree needs an execution-grade materialization tree before a final `/goal` prompt.

## Purpose

The tree converts a mature input artifact into an auditable execution plan. It is included with the final prompt so the executor can audit the prompt's structure.

When a Super SPEC must be produced or expanded as part of this flow, write it to `GOAL-SUPER-SPEC-<slug-or-timestamp>.md` and reference only the artifact path and a short summary in chat. Do not paste the full Super SPEC into the context window.

Tree acceptance is an internal quality gate by default. Do not stop merely to ask for permission to continue from tree to `/goal` after explicit skill invocation. Stop only when the tree fails a required gate, changes the declared execution contract, or the user explicitly requested staged review.

## Fixed Schema

Always emit the tree with these sections, in this order:

1. `Canonical Artifact`
2. `Certified Context`
3. `Shared Contracts`
4. `Phase Boundary`
5. `Non-Objectives`
6. `Central Rule`
7. `Forbidden Moves`
8. `Execution Units`
9. `Subagent Ownership`
10. `Per-SPEC Oracles`
11. `Negative Grep`
12. `Commit Strategy`
13. `Review Loop`
14. `Stop States`
15. `Final Delivery Contract`

When a Super SPEC artifact is created, include its path and summary in the `Canonical Artifact` section.

The `Canonical Artifact` section must include the anchor fields owned by `references/ambition-and-anchor.md`:

```text
anchor_class=
anchor_path=
anchor_hash=
anchor_origin=
anchor_source=
```

The generated tree must not cite itself as the anchor.

## Required Execution Units

Every materialization tree must include:

1. `000 Preflight And Baseline` using the input artifact's naming convention.
2. One or more narrow implementation units.
3. One final oracle/closeout unit.
4. A dedicated visual/runtime certification unit when browser, visual, canvas, 3D, UI, render, layout, spawn, raycast, or spatial proof is required.

Each unit must name:

1. objective;
2. allowed files;
3. forbidden files or actions where risk exists;
4. responsible owner or subagent role;
5. focused oracles;
6. negative checks when relevant;
7. semantic commit message;
8. completion evidence requirements;
9. engineering method profile and Method Enforcement Packet when the unit changes code, UI, runtime scripts or generated app artifacts;
10. `unit_role` and `oracle_class` when the unit integrates runtime wiring, browser/UI behavior, shared contracts or visual-spatial evidence.

Split any unit that has more than one behavioral objective, more than one ownership boundary, or mixed contract/runtime/storage/live work.

Integration or wiring units must declare `unit_role=integration` and a runtime-smoke oracle from `references/runtime-certification.md`. Build or typecheck alone is a `build-only` oracle and is not sufficient for integration.

Browser, visual, game, canvas, WebGL/WebGPU, Three.js, rendered UI, layout or spatial-risk work must declare the required runtime axis and a dedicated certification unit. A `DEGRADED` metrics artifact does not satisfy a required axis.

When the source artifact declares vertical slices or asset-transfer units, keep the unit vertical: one behavior or asset failure must flow through target asset, smallest patch, focused proof, regression surface and closeout. Horizontal layer packages such as "all docs", "all scripts", "all tests", or "cleanup" are invalid replacements for declared vertical units, even when they look faster to execute.

## Execution Unit Fidelity Gate

If the source artifact declares materialization units, the tree must preserve that declared list exactly:

1. same unit identifiers;
2. same order;
3. same visible unit count;
4. one commit per declared unit unless the artifact explicitly says no commit;
5. no silent merging of adjacent units;
6. no silent renaming of units;
7. no silent deletion of units.

Execution units may be called slices, stages, milestones, PRD phases, work packages, roadmap steps, graph nodes, branches or another project-specific name. Preserve the source artifact's vocabulary in the generated tree and prompt.

Allowed refinement:

1. Add sub-steps inside a declared unit.
2. Add stricter oracles inside a declared unit.
3. Split implementation notes beneath a declared unit.

Forbidden refinement:

1. Collapse declared units into a broader implementation unit.
2. Move closeout work into an earlier unit.
3. Treat a passing broad oracle as a replacement for missing unit commits.
4. Replace a declared queue with a new agent-invented list.

If preserving declared units appears inefficient or technically awkward, stop with `NEEDS_EXECUTION_UNIT_FIDELITY` or `NEEDS_OWNER_DECISION`. Do not optimize away the input artifact's execution rhythm.

## Shared Contracts

`references/ambition-and-anchor.md` § Shared Contracts owns this contract (the 8-field entry schema and the `extension-only` write rule) when a type, schema, command, runtime surface, fixture helper or source module crosses execution-unit boundaries. A later unit extending an upstream frozen surface with no declared extension point → `NEEDS_CONTRACT_EXTENSION_POINT`; do not make the new field optional to keep earlier oracles green.

## Material Diff Gate

Commit rhythm is not enough. Each material unit must prove execution with material evidence:

1. `git show --stat --oneline <unit-commit>` shows changed files;
2. changed files are inside the unit's allowed file matrix;
3. focused oracles for that unit passed after the diff;
4. reviewer inspected the unit diff;
5. the commit maps to exactly one declared unit.

Empty commits are forbidden for implementation, contract, fixture, runtime, test, export, migration, storage, live-lane and documentation units unless the source artifact explicitly marks that unit as no-commit or no-material-change.

If a compacted implementation already exists, do not create empty commits to simulate the declared execution rhythm. Record the mismatch and stop with `NEEDS_EXECUTION_UNIT_FIDELITY`, unless the owner explicitly accepts history normalization or compacted execution.

## Sync Commit Gate

A unit is complete only after its commit is certified:

1. allowed files staged;
2. semantic commit created or explicit no-commit rationale recorded;
3. commit hash captured;
4. `git show --stat --oneline <commit>` captured;
5. post-commit `git status --short --branch --untracked-files=all` inspected;
6. sync status recorded.

Use these sync statuses:

1. `LOCAL_COMMITTED`: committed locally and certified.
2. `REMOTE_SYNCED`: pushed only when remote sync was explicitly authorized.
3. `REMOTE_SYNC_NOT_REQUESTED`: local-only sync is complete.
4. `SYNC_BLOCKED`: sync could not be certified.

Remote push or remote state changes must not be required by a generated prompt unless the user explicitly requests remote sync.

## Material Continuation Gate

When the worktree or history already contains prior implementation, closeout reports or partial execution, the tree must distinguish baseline context from new material execution.

Default rule:

1. Prior commits and closeouts are context, not execution credit.
2. A new materialization run must produce a new additive material trail.
3. Material units require non-empty commits unless the source artifact explicitly marks the unit as no-material-change or no-commit.
4. Do not rewrite, rebase, squash, delete or mask historical evidence.
5. Do not create empty certification commits to simulate per-unit execution.
6. If an earlier closeout records `NEEDS_EXECUTION_UNIT_FIDELITY`, preserve it as historical evidence and repair with new material commits unless the owner explicitly changes the execution contract.

Generated prompts should include a short explicit rule when prior work may exist:

```text
Even if an implementation, closeout or commits already exist, this execution
must produce a new additive material trail with non-empty commits per material
unit. Prior commits are baseline-only unless explicitly accepted as execution
credit by the source artifact or owner.
```

## Preflight Requirements

`SPEC-000` must require:

1. `git status --short --branch --untracked-files=all`;
2. recent `git log` when commit lineage matters;
3. identification of unrelated pending changes;
4. read-only baseline oracles;
5. baseline documentation commit only when explicitly in scope and green.

## Files

For every unit, the tree must define:

1. files allowed to change;
2. files or directories forbidden;
3. generated artifacts, if any;
4. documentation-only boundaries, if any.

If allowed files cannot be named, the tree is not ready.

For `extension-only` writes to upstream shared-contract files, the allowed file matrix must name the upstream path, the reserved extension point, and the declaring oracles that must rerun green.

## Subagent Ownership

Subagents are optional unless the user or task asks for them. When present, each role must have clear ownership.

Rules:

1. Prefer one owner per write scope.
2. Keep reviewer read-only.
3. Keep evidence/oracle ownership separate from implementation ownership.
4. Do not assign urgent blocking work to a subagent if the main executor needs the result immediately.

## Per-SPEC Oracles

Each slice must have falsifiable oracles. Examples:

1. focused unit or contract tests;
2. lint or typecheck on changed files;
3. markdownlint for docs;
4. schema validation;
5. fixture parse;
6. `git diff --check`;
7. negative grep for forbidden behavior.

Every executable unit must classify its oracle:

```text
oracle_class=<behavioral|structural|build-only|visual-runtime|contract>
oracle_strength=<sufficient|facade|blocked>
```

Avoid broad-only validation. Run the smallest meaningful oracle first. For `unit_role=integration`, the smallest meaningful oracle is the runtime-smoke, not build/typecheck.

An oracle is `facade` when the quantity it MEASURES is a structural proxy (file size, mtime, byte count, path existence) for the semantic property it NAMES (luminance, frame rate, position, color). Declare `PROVEN_PROPERTY` and `MEASURED_QUANTITY` for each executable oracle; if the measured quantity can stay constant while the named property is violated, `oracle_strength=facade` → `NEEDS_TREE_REPAIR`. See `references/tree-adversary.md` § Oracle Classification for the name↔measure test; this copy is read in-loco by the unit gate.

### Wall harness invocation

When a reference names a wall harness for a gate — written `(drive with scripts/<name>.mjs)` — that harness IS the per-SPEC oracle for that gate, not a suggestion to read. The named harness must be **run** (`node scripts/<name>.mjs <args>`) as part of the unit's focused-oracle step; its exit code is the gate. A non-zero exit is the stop named by the owning reference (the prose does not get to overrule it); a zero exit is the only evidence that clears the gate. "Drive with X.mjs" mentioned but not executed is `oracle_strength=facade` for that unit — the same hole the harness exists to close. Parent Validation records the command and its literal exit code in `focused oracle evidence`; the Executive Stop Audit re-runs it. An agent that paraphrases the harness result instead of running it has not run the oracle.

## Structural Method Gate

When a unit changes code, UI, generated app artifacts or runtime scripts, the tree must include an `Engineering Method Profile` inside the relevant execution unit or oracle contract. Load `references/structural-method.md` for the full method contract before accepting a coding or app-building tree.

The tree must carry this compact structural decision record for each applicable unit:

```text
STRUCTURAL_METHOD=<profile-id>
topology_decision=<split, module, component, composable, service, adapter, script, internal-section, or single-file-exception>
file_topology_budget=<max files, max line growth, max section growth or source-proven exception>
allowed_new_modules=<paths, module names, internal sections or none>
structural_debt_budget=<none, explicit accepted debt, or owner-decision needed>
structural_source_probes=<commands or source inspections that can fail>
structural_handoff=<next-unit constraints, or none>
runtime_smoke_oracle=<command or not_applicable>
contract_handoff_artifact=<path, ledger section, prompt block or not_applicable>
```

The tree must name topology budget, allowed modules/internal sections, structural debt budget, structural source probes, structural negative checks and structural handoff. File topology budgets must include an executable probe or source-proven exception. A single-file exception must be source-mandated and must still require internal modularity.

If a unit passes behavior or UI smoke but fails structural probes, route to `NEEDS_STRUCTURAL_METHOD` or a bounded `SPEC-AUDIT-STRUCTURE-*` repair unit. Do not treat this as ordinary bug fixing unless failed-attempt recovery classifies `bug_vs_architecture=behavior_bug`; architecture collapse routes to `structural_repair`.

## Negative Grep

The tree must include negative grep for:

1. forbidden runtime execution;
2. forbidden providers or fallbacks;
3. boundary leakage;
4. unsafe exports;
5. raw payload exposure;
6. final interpretation leakage;
7. phase violations such as storage in a semantic contract phase.

Use domain-specific patterns from the SPEC, not from this reference.

Negative grep must be semantic rather than purely lexical when a term can be valid vocabulary. A blocked-state enum, safety reason code or policy field is allowed when it records a prohibition; the forbidden target is the executable behavior or unsafe configuration.

If the same word is both valid policy vocabulary and forbidden behavior, write the prompt with separate allow/deny patterns instead of a broad lexical grep.

## Sequential Ownership Gate

When the materialization queue requires strict commit-per-unit execution, prefer centralized material edits with reviewer/oracle subagents unless write scopes are genuinely disjoint.

The tree should not imply parallel implementation if:

1. the next unit depends on the current unit's committed contract;
2. staging must include only one unit's files;
3. each unit must be reviewed and committed before the next starts;
4. write scopes would overlap.

Use write subagents only when the tree names disjoint files and a serialized integration point. Otherwise, keep subagents read-only or evidence-focused.

## Commit Strategy

The tree must require commit per slice.

Each commit message should be semantic and scoped, such as `feat(scope): ...`, `test(scope): ...`, `chore(scope): ...` or `docs(scope): ...`.

Never accumulate multiple units before commit unless the user explicitly changes the execution contract.

When an input artifact declares N units, the final prompt must make N unit entries visible and must require N corresponding commits, except units explicitly marked as no-commit preflight by the artifact.

Every material unit must also require a unit evidence block:

```text
Unit:
Commit:
Changed files:
git show --stat:
Oracles:
Negative checks:
Structural method result:
Reviewer result:
Post-commit status:
Sync status:
```

## Review Loop

The tree must include a review loop: inspect the current-unit diff, reject unrelated files and forbidden moves, verify structural method requirements, run focused oracles, fix until green, stage only unit files, commit, capture the unit evidence block, inspect post-commit status and continue only after sync status is certified.

## Next Prompt Handoff

Next Prompt Handoff is optional and disabled by default. Include it only when the user explicitly requests `next_prompt_handoff=true`, `--next-prompt-handoff`, or an equivalent direct trigger.

When enabled, place the handoff in `Final Delivery Contract`: emit the next `/goal` only after `GO`, certification, and a next declared unit; keep it in chat, do not write it to disk, and do not execute it automatically. If code, UI, runtime scripts or generated app artifacts changed, include active `STRUCTURAL_METHOD=<profile-id>`, changed topology, preserved boundaries, accepted debt and structural handoff constraints.

## Execution Loop Boundary

Execution Loop is optional and disabled by default. Include it only when the user explicitly requests `--execute-loop`.

When enabled, load `references/execution-loop-runner.md` and require the tree's `Final Delivery Contract` to name `Execution Cost Draft`, Pre-Edit Gate, one `ACTIVE_SPEC` at a time, loop-state block, failed-attempt recovery with `bug_vs_architecture`, parent validation, local commit only, reference implementations as baseline-only comparison evidence, strict sequential replay, no Super SPEC materialization as declared-unit credit, `SPEC_REPAIR_BY_LLM`, mandatory `GOAL-EXECUTION-LOOP-LEDGER-<slug-or-timestamp>.md`, the exact `--execute-loop-parent-fallback` flag, owner-approved cloud redaction, Execution Cost Draft entries for anchor, quality ceiling, shared contracts and contract handoff, Pre-Execution Tree Adversary, Executive Stop Audit, and bounded `SPEC-AUDIT-*` units when audit returns `NEEDS_MORE_LOOPS`.

## Weak Tree Rejection

Stop and revise the tree if it lacks:

1. canonical artifact;
2. phase boundary;
3. allowed files per slice;
4. forbidden moves;
5. per-SPEC oracles;
6. negative grep;
7. material-diff evidence;
8. commit strategy;
9. reviewer loop;
10. engineering method profile for coding, UI or generated-app units;
11. anchor artifact fields;
12. runtime-smoke oracle for integration units;
13. dedicated certification unit for required browser or visual axes;
14. executable topology budget probe when structure is budgeted;
15. Tree Adversary result when required;
16. stop states;
17. final delivery contract.

Also stop and revise the tree if it compresses, skips or renames a unit declared by the source artifact, cites itself as its anchor, or lowers a declared quality ceiling without owner decision.

## Stop States

Use the SPEC's stop states when available. Otherwise include:

1. `GO`: all slices committed, oracles green, final delivery complete.
2. `NEEDS_OWNER_DECISION`: a product, public-surface, data, legal, storage, live-execution or architectural decision is needed.
3. `BLOCKED`: a critical oracle fails for a reason outside the slice.
4. `SAFETY_BLOCKED`: the work would require unsafe access, secrets, destructive actions, policy bypass or unauthorized data.
5. `NEEDS_ANCHOR_ARTIFACT`: the tree lacks a persisted non-self anchor.
6. `NEEDS_AMBITION_RECONCILIATION`: a declared quality ceiling was lowered without oracle or owner decision.
7. `NEEDS_INTEGRATION_ORACLE`: an integration unit has only build/typecheck.
8. `AXIS_UNPROVEN`: a required quality/runtime axis lacks PASS evidence.
9. `VISUAL_CERT_BLOCKED`: visual/browser proof was required but not attempted or blocked by environment.
10. `NEEDS_CONTRACT_EXTENSION_POINT`: a shared contract needs a reserved extension point before a later unit can extend it.
11. `NEEDS_TREE_ADVERSARY`: a required adversarial tree pass is missing.

## Final Delivery Contract

The tree must require a final report with:

1. units executed;
2. subagents used, if any;
3. commits;
4. files changed;
5. oracles run;
6. boundaries preserved;
7. unit evidence blocks;
8. decisions pending;
9. structural method result when applicable;
10. structural handoff when applicable;
11. runtime smoke result for integration units;
12. browser metrics and visual evidence for required axes;
13. contract handoff artifact and API lint status when workers reused code;
14. anchor and Tree Adversary status;
15. next prompt handoff status when explicitly requested;
16. execution loop status when `--execute-loop` was requested;
17. final status.
