# Materialization Tree

Use this reference when a mature SPEC, Super SPEC, PRD, relational project plan
or accepted execution tree needs an execution-grade materialization tree before
a final `/goal` prompt.

## Purpose

The tree converts a mature input artifact into an auditable execution plan. It
is included with the final prompt so the executor can audit the prompt's
structure.

Tree acceptance is an internal quality gate by default. Do not stop merely to
ask for permission to continue from tree to `/goal` after explicit skill
invocation. Stop only when the tree fails a required gate, changes the declared
execution contract, or the user explicitly requested staged review.

## Fixed Schema

Always emit the tree with these sections, in this order:

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

## Required Execution Units

Every materialization tree must include:

1. `000 Preflight And Baseline` using the input artifact's naming convention.
2. One or more narrow implementation units.
3. One final oracle/closeout unit.

Each unit must name:

1. objective;
2. allowed files;
3. forbidden files or actions where risk exists;
4. responsible owner or subagent role;
5. focused oracles;
6. negative checks when relevant;
7. semantic commit message;
8. completion evidence requirements.

Split any unit that has more than one behavioral objective, more than one
ownership boundary, or mixed contract/runtime/storage/live work.

## Execution Unit Fidelity Gate

If the source artifact declares materialization units, the tree must preserve
that declared list exactly:

1. same unit identifiers;
2. same order;
3. same visible unit count;
4. one commit per declared unit unless the artifact explicitly says no commit;
5. no silent merging of adjacent units;
6. no silent renaming of units;
7. no silent deletion of units.

Execution units may be called slices, stages, milestones, PRD phases, work
packages, roadmap steps, graph nodes, branches or another project-specific
name. Preserve the source artifact's vocabulary in the generated tree and
prompt.

Allowed refinement:

1. Add sub-steps inside a declared unit.
2. Add stricter oracles inside a declared unit.
3. Split implementation notes beneath a declared unit.

Forbidden refinement:

1. Collapse declared units into a broader implementation unit.
2. Move closeout work into an earlier unit.
3. Treat a passing broad oracle as a replacement for missing unit commits.
4. Replace a declared queue with a new agent-invented list.

If preserving declared units appears inefficient or technically awkward, stop
with `NEEDS_EXECUTION_UNIT_FIDELITY` or `NEEDS_OWNER_DECISION`. Do not optimize
away the input artifact's execution rhythm.

## Material Diff Gate

Commit rhythm is not enough. Each material unit must prove execution with
material evidence:

1. `git show --stat --oneline <unit-commit>` shows changed files;
2. changed files are inside the unit's allowed file matrix;
3. focused oracles for that unit passed after the diff;
4. reviewer inspected the unit diff;
5. the commit maps to exactly one declared unit.

Empty commits are forbidden for implementation, contract, fixture, runtime,
test, export, migration, storage, live-lane and documentation units unless the
source artifact explicitly marks that unit as no-commit or no-material-change.

If a compacted implementation already exists, do not create empty commits to
simulate the declared execution rhythm. Record the mismatch and stop with
`NEEDS_EXECUTION_UNIT_FIDELITY`, unless the owner explicitly accepts history
normalization or compacted execution.

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

Remote push or remote state changes must not be required by a generated prompt
unless the user explicitly requests remote sync.

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

## Subagent Ownership

Subagents are optional unless the user or task asks for them. When present,
each role must have clear ownership.

Rules:

1. Prefer one owner per write scope.
2. Keep reviewer read-only.
3. Keep evidence/oracle ownership separate from implementation ownership.
4. Do not assign urgent blocking work to a subagent if the main executor needs
   the result immediately.

## Per-SPEC Oracles

Each slice must have falsifiable oracles. Examples:

1. focused unit or contract tests;
2. lint or typecheck on changed files;
3. markdownlint for docs;
4. schema validation;
5. fixture parse;
6. `git diff --check`;
7. negative grep for forbidden behavior.

Avoid broad-only validation. Run the smallest meaningful oracle first.

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

## Commit Strategy

The tree must require commit per slice.

Each commit message should be semantic and scoped:

```text
feat(scope): add contract
test(scope): certify fixture matrix
chore(scope): expose internal boundary
docs(scope): define baseline
```

Never accumulate multiple units before commit unless the user explicitly
changes the execution contract.

When an input artifact declares N units, the final prompt must make N unit
entries visible and must require N corresponding commits, except units
explicitly marked as no-commit preflight by the artifact.

Every material unit must also require a unit evidence block:

```text
Unit:
Commit:
Changed files:
git show --stat:
Oracles:
Negative checks:
Reviewer result:
Post-commit status:
Sync status:
```

## Review Loop

The tree must include a review loop:

1. inspect diff for the current unit;
2. verify no unrelated files were touched;
3. verify forbidden moves are absent;
4. run focused oracles;
5. fix until green;
6. stage only unit files;
7. commit;
8. capture unit evidence block;
9. inspect post-commit status;
10. continue to the next slice only after sync status is certified.

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
10. stop states;
11. final delivery contract.

Also stop and revise the tree if it compresses, skips or renames a unit
declared by the source artifact.

## Stop States

Use the SPEC's stop states when available. Otherwise include:

1. `GO`: all slices committed, oracles green, final delivery complete.
2. `NEEDS_OWNER_DECISION`: a product, public-surface, data, legal, storage,
   live-execution or architectural decision is needed.
3. `BLOCKED`: a critical oracle fails for a reason outside the slice.
4. `SAFETY_BLOCKED`: the work would require unsafe access, secrets,
   destructive actions, policy bypass or unauthorized data.

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
9. final status.
