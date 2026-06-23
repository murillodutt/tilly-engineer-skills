# Materialization Tree

Use this reference when a mature SPEC, Super SPEC, PRD, relational project plan
or accepted execution tree needs an execution-grade materialization tree before
a final `/goal` prompt.

## Purpose

The tree converts a mature input artifact into an auditable execution plan. It
is included with the final prompt so the executor can audit the prompt's
structure.

When a Super SPEC must be produced or expanded as part of this flow, write it
to `GOAL-SUPER-SPEC-<slug-or-timestamp>.md` and reference only the artifact path
and a short summary in chat. Do not paste the full Super SPEC into the context
window.

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

When a Super SPEC artifact is created, include its path and summary in the
`Canonical Artifact` section.

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
8. completion evidence requirements;
9. engineering method profile and Method Enforcement Packet when the unit
   changes code, UI, runtime scripts or generated app artifacts.

Split any unit that has more than one behavioral objective, more than one
ownership boundary, or mixed contract/runtime/storage/live work.

When the source artifact declares vertical slices or asset-transfer units, keep
the unit vertical: one behavior or asset failure must flow through target
asset, smallest patch, focused proof, regression surface and closeout.
Horizontal layer packages such as "all docs", "all scripts", "all tests", or
"cleanup" are invalid replacements for declared vertical units, even when they
look faster to execute.

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

## Material Continuation Gate

When the worktree or history already contains prior implementation, closeout
reports or partial execution, the tree must distinguish baseline context from
new material execution.

Default rule:

1. Prior commits and closeouts are context, not execution credit.
2. A new materialization run must produce a new additive material trail.
3. Material units require non-empty commits unless the source artifact
   explicitly marks the unit as no-material-change or no-commit.
4. Do not rewrite, rebase, squash, delete or mask historical evidence.
5. Do not create empty certification commits to simulate per-unit execution.
6. If an earlier closeout records `NEEDS_EXECUTION_UNIT_FIDELITY`, preserve it
   as historical evidence and repair with new material commits unless the owner
   explicitly changes the execution contract.

Generated prompts should include a short explicit rule when prior work may
exist:

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

## Structural Method Gate

When a unit changes code, UI, generated app artifacts or runtime scripts, the
tree must include an `Engineering Method Profile` inside the relevant execution
unit or oracle contract.

The profile must state:

1. stack or language family;
2. intended topology, such as files, modules, components, composables, stores,
   services, adapters, scripts or internal sections;
3. structural boundaries between UI, domain, storage, runtime, docs generation
   and adapter layers;
4. explicit topology exceptions;
5. structural negative checks;
6. structural oracles;
7. `STRUCTURAL_METHOD=<profile-id>`, topology budget, allowed new
   files/modules/internal sections, structural debt budget and structural
   handoff requirements for the next unit.

A source-mandated single-file deliverable is a valid topology exception only
when the tree requires internal modularity, named sections, narrow APIs, no
duplicated logic and a structural audit note. The exception must not become
permission for an unbounded god file.

Structural negative checks should target:

1. god files or unchecked file-size growth;
2. duplicated domain or conversion logic;
3. accidental mixing of UI, domain, storage, runtime or adapter layers;
4. framework-topology bypass;
5. broad inline CSS/JS when file separation is expected;
6. glue or workaround code without a declared consumer.

Structural oracles should match the stack: size or line thresholds,
component/module inventory, import/dependency checks, lint, typecheck, build,
rendered UI smoke or source probes that can fail on structural collapse.

The tree must include a compact structural decision record for each applicable
unit:

```text
STRUCTURAL_METHOD=<profile-id>
topology_decision=<split, module, component, composable, service, adapter, script, internal-section, or single-file-exception>
file_topology_budget=<max files, max line growth, max section growth or source-proven exception>
allowed_new_modules=<paths, module names, internal sections or none>
structural_debt_budget=<none, explicit accepted debt, or owner-decision needed>
structural_source_probes=<commands or source inspections that can fail>
structural_handoff=<next-unit constraints, or none>
```

Use deterministic probes when source exists: line counts, module inventory,
import boundaries, duplicate symbols, inline CSS/JS scans, framework directory
probes or single-file section anchors. LLM review may supplement these probes,
but must not replace practical runnable or source-readable checks.

If a unit passes behavior or UI smoke but fails structural probes, the tree must
route to `NEEDS_STRUCTURAL_METHOD` or a bounded
`SPEC-AUDIT-STRUCTURE-*` repair unit. Do not treat this as ordinary bug fixing
unless the failure is classified as `bug_vs_architecture=behavior_bug`.

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

Negative grep must be semantic rather than purely lexical when a term can be
valid vocabulary. A blocked-state enum, safety reason code or policy field is
allowed when it records a prohibition; the forbidden target is the executable
behavior or unsafe configuration.

Example:

1. Allowed vocabulary: `BLOCKED_BYPASS_REQUIRED`, `requiresBypass`,
   `bypassRequired`.
2. Forbidden behavior: CAPTCHA solving, bypass attempts, fake credentials,
   proxy evasion, hidden network access or leaked secret usage.

If the same word is both valid policy vocabulary and forbidden behavior, write
the prompt with separate allow/deny patterns instead of a broad lexical grep.

## Sequential Ownership Gate

When the materialization queue requires strict commit-per-unit execution,
prefer centralized material edits with reviewer/oracle subagents unless write
scopes are genuinely disjoint.

The tree should not imply parallel implementation if:

1. the next unit depends on the current unit's committed contract;
2. staging must include only one unit's files;
3. each unit must be reviewed and committed before the next starts;
4. write scopes would overlap.

Use write subagents only when the tree names disjoint files and a serialized
integration point. Otherwise, keep subagents read-only or evidence-focused.

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
Structural method result:
Reviewer result:
Post-commit status:
Sync status:
```

## Review Loop

The tree must include a review loop:

1. inspect diff for the current unit;
2. verify no unrelated files were touched;
3. verify forbidden moves are absent;
4. verify structural method requirements when applicable;
5. run focused oracles;
6. fix until green;
7. stage only unit files;
8. commit;
9. capture unit evidence block;
10. inspect post-commit status;
11. continue to the next slice only after sync status is certified.

## Next Prompt Handoff

Next Prompt Handoff is optional and disabled by default. Include it only when
the user explicitly requests `next_prompt_handoff=true`,
`--next-prompt-handoff`, or an equivalent direct trigger.

When enabled, the tree must place the handoff in `Final Delivery Contract` and
require:

1. current run reaches `GO`;
2. certification is complete;
3. next declared execution unit exists;
4. next `/goal` prompt is emitted in the same chat/context window;
5. next prompt is not written to disk unless explicitly requested;
6. next prompt is not executed automatically.

If code, UI, runtime scripts or generated app artifacts were touched, handoff
also requires active `STRUCTURAL_METHOD=<profile-id>`, changed files/modules or
internal sections, preserved boundaries, accepted debt and next-unit
constraints that prevent architecture regression.

If the current run stops or no next declared unit exists, the executor reports
the stop/final state instead of generating a next prompt.

## Execution Loop Boundary

Execution Loop is optional and disabled by default. Include it only when the
user explicitly requests `--execute-loop`.

When enabled, the tree's `Final Delivery Contract` must require:

1. `Execution Cost Draft` before any worker subagent is spawned;
2. one active execution unit at a time through `ACTIVE_SPEC=SPEC-00N`;
3. full prompt plus hard active-SPEC envelope for each worker;
4. classified baseline worktree state before the first worker;
5. active Engineering Method Profile when the active unit changes code, UI or
   generated app artifacts;
6. active `STRUCTURAL_METHOD=<profile-id>`, file topology budget, allowed new
   modules/internal sections and structural debt budget in the hard envelope;
7. loop-state block for every attempt;
8. failed-attempt recovery before another attempt starts, including
   `bug_vs_architecture` and a `structural_repair` decision when architecture
   collapsed;
9. parent validation before opening the next unit;
10. local commit per green SPEC and no remote push without separate
   authorization;
11. reference implementations, prior manual builds, browser smoke results, run
   records and post-facto audits classified as baseline-only comparison
   evidence, never execution credit;
12. strict sequential replay with evidence produced after each `ACTIVE_SPEC`
    opens and before the next SPEC starts;
13. `SPEC_REPAIR_BY_LLM` as a separate commit against a canonical SPEC artifact
   when the active SPEC itself is repaired;
14. structural decision ledger fields inside
    `GOAL-EXECUTION-LOOP-LEDGER-<slug-or-timestamp>.md` when code structure is
    in scope;
15. `GOAL-EXECUTION-LOOP-LEDGER-<slug-or-timestamp>.md` when the loop is long,
    repaired, audit-expanded, explicitly ledgered, or resumes without exact
    loop-state proof;
16. parent-side execution fallback only after the exact
    `--execute-loop-parent-fallback` flag;
17. owner-approved redaction before any cloud escalation;
18. Executive Stop Audit before final loop closure;
19. `SPEC-AUDIT-*` appended units, not original-tree rewrites, when audit
    returns `NEEDS_MORE_LOOPS`;
20. bounded audit-repair cycles that stop on repeated audit expansion without
    new material evidence.

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
11. stop states;
12. final delivery contract.

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
9. structural method result when applicable;
10. structural handoff when applicable;
11. next prompt handoff status when explicitly requested;
12. execution loop status when `--execute-loop` was requested;
13. final status.
