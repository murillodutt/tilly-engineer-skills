---
name: tes-goal-maestro
description: Use when the user explicitly invokes tes-goal-maestro, /tes-goal-maestro, /tes:goal-maestro, $tes-goal-maestro, or directly asks to generate a maestral /goal prompt for incremental, auditable materialization from a mature SPEC, Super SPEC, PRD, relational project plan, or accepted execution tree.
license: MIT
---

# TES Goal Maestro

Operational contract: `tes.goal_maestro@0.2.0`.

## Invocation Contract

Use after explicit invocation or a direct request to generate a maestral
`/goal` prompt from a mature SPEC, Super SPEC, PRD, relational project plan or
accepted execution tree. Do not activate from generic planning, ordinary goal
language, or early design discussion.

`tes-goal-maestro` does not execute implementation. It materializes an
execution-grade materialization tree and, after acceptance, a ready `/goal`
prompt from a mature input artifact.

The skill optimizes for certifiable execution, not enthusiasm. A generated
prompt must be harder to break than an ad hoc manual prompt.

## Maturity Gate

Before generating `/goal`, verify that the input artifact contains, explicitly
or by clear derivation:

1. canonical artifact;
2. capability or purpose;
3. certified context and existing dependencies;
4. current phase and boundary between meaning and mechanics;
5. non-objectives;
6. central rule;
7. forbidden moves;
8. acceptance criteria or oracle candidates;
9. negative-grep candidates;
10. stop states or owner-decision points;
11. commit strategy;
12. final delivery contract.

Assign a readiness score:

- `READY`: all maturity criteria are explicit or clearly derivable.
- `NEEDS_SPEC_MATURITY`: the input artifact is missing structural material.
- `NEEDS_EXECUTION_UNIT_FIDELITY`: the input artifact names required execution
  units but the tree or prompt omits, renames, reorders or merges them without
  explicit acceptance. `NEEDS_SLICE_FIDELITY` is a backward-compatible alias.
- `NEEDS_TREE_ACCEPTANCE`: the input artifact is mature, but the execution tree
  is not explicit and accepted.
- `READY_GOAL_PROMPT`: the input artifact is mature and the accepted tree can
  produce a final prompt.

If the input artifact is missing structural material, stop with
`NEEDS_SPEC_MATURITY` and list only the smallest set of missing pieces.

If the input artifact is mature but the tree is absent, produce
`DRAFT_MATERIALIZATION_TREE` and ask for acceptance before generating `/goal`.

Generate `/goal` only when the input artifact is mature and the materialization
tree is explicit and accepted. If the user accepts a draft tree, continue with
`READY_GOAL_PROMPT`.

## What To Do

1. Read the input artifact and any user-provided tree.
2. Run the Maturity Gate and readiness score.
3. Run the Execution Unit Fidelity Gate:
   - If the input artifact declares a queue of execution units, preserve every
     unit identifier and order.
   - Execution units may be named slices, stages, milestones, PRD phases, work
     packages, roadmap steps, graph nodes or project branches.
   - Do not merge, skip, rename or reorder declared units unless the user
     explicitly accepts that change.
   - Require one commit or explicit no-commit decision per declared unit.
   - If fidelity cannot be preserved, stop with
     `NEEDS_EXECUTION_UNIT_FIDELITY`.
4. Load the relevant references:
   - `references/materialization-tree.md` for tree construction.
   - `references/maestral-goal-prompt.md` for final prompt construction.
   - `references/subagents-and-oracles.md` when roles or verification are weak.
   - `references/quality-gates.md` when maturity, prompt strength or closeout
     needs hardening.
5. Produce the fixed `Materialization Tree` schema.
6. Produce the `Ready /goal Prompt` only after tree acceptance.
7. Keep output chat-first. Save to files only when the user explicitly asks.

The fixed tree schema is:

1. `Canonical Artifact`
2. `Certified Context`
3. `Phase Boundary`
4. `Non-Objectives`
5. `Central Rule`
6. `Forbidden Moves`
7. `Execution Units`
8. `Subagent Ownership`
9. `Per-SPEC Oracles`
10. `Negative Grep`
11. `Commit Strategy`
12. `Review Loop`
13. `Stop States`
14. `Final Delivery Contract`

Always include a `000 Preflight And Baseline` unit in the `/goal` prompt. Use
the input artifact's naming convention when one exists.

Every execution unit in the tree must define:

1. objective;
2. allowed files;
3. forbidden files or actions where risk exists;
4. subagent or owner;
5. focused oracles;
6. negative checks where relevant;
7. semantic commit message.

If the source artifact already names materialization units, the tree and
prompt must preserve that list exactly. Expanding a unit into smaller sub-steps
is allowed only when the original unit remains visible and receives its own
commit or explicit no-commit rationale. Collapsing multiple declared units into
one implementation unit is forbidden without explicit owner acceptance.

Reject weak trees that omit per-SPEC files, oracles, review loop, stop states,
or commit rhythm.

## Output Contract

Use these statuses:

- `NEEDS_SPEC_MATURITY`: a mature input artifact is not available.
- `NEEDS_EXECUTION_UNIT_FIDELITY`: declared execution units were not preserved
  exactly.
- `NEEDS_SLICE_FIDELITY`: backward-compatible alias for
  `NEEDS_EXECUTION_UNIT_FIDELITY`.
- `DRAFT_MATERIALIZATION_TREE`: SPEC is mature enough, but the tree needs
  acceptance.
- `NEEDS_TREE_ACCEPTANCE`: a draft tree exists but has not been accepted.
- `READY_GOAL_PROMPT`: SPEC and tree are accepted; `/goal` is ready.
- `SAVE_REQUESTED`: user explicitly asked to write the prompt or tree to disk.

Default output:

1. `Maturity/Stop Status`
2. `Materialization Tree`
3. `Readiness Score`
4. `Ready /goal Prompt` when allowed

## Locks

- Do not mention project-specific origin stories, project names, paths, or
  domain examples.
- Do not generate `/goal` from an immature input artifact.
- Do not treat an implicit tree as accepted.
- Do not execute the implementation unless the user explicitly asks in a
  separate instruction.
- Do not write files unless the user asks to save the output.
- Do not hide forbidden moves, missing oracles, or owner-decision points inside
  prose.
- Do not emit a prompt that lacks `SPEC-000`, commit-per-SPEC discipline,
  negative grep, review loop, stop states, or final delivery contract.
- Do not compress declared execution units into fewer implementation units.
- Do not let the generated prompt authorize live execution, persistence,
  public-surface changes, destructive operations, or external access unless the
  SPEC explicitly authorizes them and names the boundary.
- Do not embed project-specific domain examples in the skill. Domain specifics
  must come from the input SPEC.

## Done

`tes-goal-maestro` is complete when it either stops with
`NEEDS_SPEC_MATURITY`, `NEEDS_EXECUTION_UNIT_FIDELITY`, produces an accepted
materialization tree, or delivers a ready `/goal` prompt whose artifact,
boundaries, execution units, ownership, oracles, negative grep, commit rhythm,
review loop, and stop states are explicit and faithful to any execution queue
declared by the input artifact.
