---
name: tes-goal-maestro
description: Use when the user explicitly invokes tes-goal-maestro, /tes-goal-maestro, /tes:goal-maestro, $tes-goal-maestro, or directly asks to generate a maestral /goal prompt for incremental, auditable materialization from a mature SPEC.
license: MIT
---

# TES Goal Maestro

Operational contract: `tes.goal_maestro@0.1.0`.

## Invocation Contract

Use after explicit invocation or a direct request to generate a maestral
`/goal` prompt. Do not activate from generic planning, ordinary goal language,
or early design discussion.

`tes-goal-maestro` does not execute implementation by default. It materializes
a ready `/goal` prompt from a mature SPEC and an explicit materialization tree.

## Maturity Gate

Before generating `/goal`, verify that the SPEC contains, explicitly or by
clear derivation:

1. canonical artifact;
2. capability or purpose;
3. certified context and existing dependencies;
4. current phase and boundary between meaning and mechanics;
5. non-objectives;
6. central rule;
7. forbidden moves;
8. acceptance criteria or oracle candidates;
9. stop states or owner-decision points.

If the SPEC is missing structural material, stop with `NEEDS_SPEC_MATURITY` and
list only the smallest set of missing pieces.

If the SPEC is mature but the tree is absent, produce
`DRAFT_MATERIALIZATION_TREE` and ask for acceptance before generating `/goal`.

Generate `/goal` only when the SPEC is mature and the materialization tree is
explicit and accepted.

## What To Do

1. Read the SPEC and any user-provided tree.
2. Run the Maturity Gate.
3. Load `references/maestral-goal-prompt.md` when producing the tree or final
   prompt.
4. Produce the fixed `Materialization Tree` schema.
5. Produce the `Ready /goal Prompt` only after tree acceptance.
6. Keep output chat-first. Save to files only when the user explicitly asks.

The fixed tree schema is:

1. `Canonical Artifact`
2. `Certified Context`
3. `Phase Boundary`
4. `Non-Objectives`
5. `Central Rule`
6. `Forbidden Moves`
7. `SPEC Slices`
8. `Subagent Ownership`
9. `Per-SPEC Oracles`
10. `Negative Grep`
11. `Commit Strategy`
12. `Review Loop`
13. `Stop States`
14. `Final Delivery Contract`

Always include `SPEC-000 Preflight And Baseline` in the `/goal` prompt.

## Output Contract

Use these statuses:

- `NEEDS_SPEC_MATURITY`: a mature SPEC is not available.
- `DRAFT_MATERIALIZATION_TREE`: SPEC is mature enough, but the tree needs
  acceptance.
- `READY_GOAL_PROMPT`: SPEC and tree are accepted; `/goal` is ready.
- `SAVE_REQUESTED`: user explicitly asked to write the prompt or tree to disk.

Default output:

1. `Maturity/Stop Status`
2. `Materialization Tree`
3. `Ready /goal Prompt` when allowed

## Locks

- Do not mention project-specific origin stories, project names, paths, or
  domain examples.
- Do not generate `/goal` from an immature SPEC.
- Do not treat an implicit tree as accepted.
- Do not execute the implementation unless the user explicitly asks in a
  separate instruction.
- Do not write files unless the user asks to save the output.
- Do not hide forbidden moves, missing oracles, or owner-decision points inside
  prose.

## Done

`tes-goal-maestro` is complete when it either stops with
`NEEDS_SPEC_MATURITY`, produces an accepted materialization tree, or delivers a
ready `/goal` prompt whose artifact, boundaries, SPEC slices, ownership,
oracles, negative grep, commit rhythm, review loop, and stop states are
explicit.
