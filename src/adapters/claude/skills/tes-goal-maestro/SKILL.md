---
name: tes-goal-maestro
description: Use when the user explicitly invokes tes-goal-maestro, /tes-goal-maestro, /tes:goal-maestro, $tes-goal-maestro, or directly asks to generate a maestral /goal prompt (gerar um /goal maestral) for incremental, auditable materialization from a mature SPEC, Super SPEC, PRD, relational project plan, or accepted execution tree.
license: MIT
---

# TES Goal Maestro

Operational contract: `tes.goal_maestro@0.3.2`.

## Invocation Contract

Use after explicit invocation or a direct request to generate a maestral
`/goal` prompt from a mature SPEC, Super SPEC, PRD, relational project plan or
accepted execution tree. Do not activate from generic planning, ordinary goal
language, or early design discussion.

`tes-goal-maestro` does not execute implementation. It materializes an
execution-grade materialization tree and, when the tree passes the skill's
internal gates, emits a ready `/goal` prompt from a mature input artifact in
the same response.

When the workflow needs to create or carry a Super SPEC, do not paste the full
Super SPEC into the context window. Materialize it as a Markdown artifact named
`GOAL-SUPER-SPEC-<slug-or-timestamp>.md`, then reference only its path and a
short summary in chat. This Super SPEC artifact is the only default file write
allowed by this skill; prompt and tree files still require an explicit save
request.

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
- `NEEDS_TREE_REPAIR`: the generated tree exists but fails the fixed schema,
  ownership, oracle, fidelity or stop-state checks.
- `NEEDS_TREE_ACCEPTANCE`: use only when the user explicitly requested a
  two-step review workflow or when changing the declared execution contract
  requires owner acceptance.
- `READY_GOAL_PROMPT`: the input artifact is mature and the generated tree
  passes the internal tree gates.

If the input artifact is missing structural material, stop with
`NEEDS_SPEC_MATURITY` and list only the smallest set of missing pieces.

If the input artifact is mature but the tree is absent, generate the tree,
validate it internally, and continue to `READY_GOAL_PROMPT` in the same answer
when the tree passes.

Generate `/goal` when the input artifact is mature and the materialization tree
is explicit, faithful and internally accepted by the skill gates. Do not ask
for a separate permission merely to move from tree to prompt after explicit
skill invocation.

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
   - Run the Vertical Slice Fidelity Gate: when the artifact declares vertical
     slices or asset-transfer units, preserve units that carry one behavior or
     asset failure through target asset, smallest patch, focused proof,
     regression surface and closeout. Reject agent-invented horizontal layer
     packages such as "all docs", "all scripts", "all tests", or "cleanup" when
     they replace declared vertical units.
   - If fidelity cannot be preserved, stop with
     `NEEDS_EXECUTION_UNIT_FIDELITY`.
4. Run the Material Continuation Gate:
   - Distinguish contextual continuity from material execution.
   - Prior commits, closeouts or existing implementations may be used as
     baseline and context, but they do not satisfy a new materialization run by
     default.
   - When a new `/goal` asks for execution, require an additive material trail:
     non-empty commits per material unit, no rewrite, no rebase, no squash and
     no historical masking with empty certification commits.
   - If the input artifact explicitly marks a unit as no-material-change or
     no-commit, preserve and report that rationale.
   - If an earlier closeout records `NEEDS_EXECUTION_UNIT_FIDELITY`, preserve
     it as historical evidence and require new material commits to repair it
     unless the owner explicitly changes the execution contract.
5. Run the Negative Grep Semantics Gate:
   - Separate allowed vocabulary from forbidden behavior.
   - Do not make a prompt fail merely because a contract names a blocked state,
     reason code or safety enum.
   - Negative checks must target executable or behavioral violations when a
     term is also valid as policy vocabulary. For example, a blocked bypass
     enum can be allowed while CAPTCHA solving, proxy bypass, fake credentials
     or bypass-attempt flags remain forbidden.
6. Run the Sequential Ownership Gate:
   - When a queue requires commit-per-unit sequencing, prefer centralized
     material edits and use subagents mainly for read-only review, oracle
     tracking or bounded disjoint write scopes.
   - Do not imply parallel write execution when commits must be certified in a
     strict order unless the write scopes are genuinely independent and the
     prompt names how integration will be serialized.
7. Load the relevant references:
   - `references/materialization-tree.md` for tree construction.
   - `references/maestral-goal-prompt.md` for final prompt construction.
   - `references/subagents-and-oracles.md` when roles or verification are weak.
   - `references/quality-gates.md` when maturity, prompt strength or closeout
     needs hardening.
8. Produce the fixed `Materialization Tree` schema.
9. Validate the tree against maturity, execution-unit fidelity, material
   continuation, ownership, oracle, negative-grep semantics, material-diff,
   sync-commit and stop-state gates.
10. If a Super SPEC must be produced or expanded, write it to
   `GOAL-SUPER-SPEC-<slug-or-timestamp>.md` in the current target workspace or
   in the explicitly requested output directory. Use a filesystem-safe slug
   from the artifact title when available; otherwise use a timestamp. Do not
   display the full Super SPEC body in chat.
11. Produce the `Ready /goal Prompt` in the same response when the tree passes.
   Stop only for maturity gaps, execution-unit fidelity failure, tree repair,
   owner decisions, or an explicitly requested two-step review workflow.
12. Keep output chat-first except for the required Super SPEC artifact. Save
   prompt or tree files only when the user explicitly asks.

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
7. semantic commit message;
8. completion evidence requirements.

If the source artifact already names materialization units, the tree and
prompt must preserve that list exactly. Expanding a unit into smaller sub-steps
is allowed only when the original unit remains visible and receives its own
commit or explicit no-commit rationale. Collapsing multiple declared units into
one implementation unit is forbidden without explicit owner acceptance.

Completion evidence is mandatory. A unit is not executed because it has a
commit message. A unit is executed only when its allowed files changed, its
focused oracle passed, its diff was reviewed, and its commit evidence maps to
exactly one declared unit. Empty commits are forbidden for implementation,
contract, fixture, runtime, test and export units unless the source artifact
explicitly marks the unit as no-material-change or no-commit.

When a previous implementation or closeout already exists, continuity is
contextual by default, not execution credit. Generated prompts must say whether
prior commits are baseline-only or explicitly satisfy a unit. For a new
materialization run, prior commits do not satisfy material units unless the
source artifact or owner explicitly says so. The generated prompt must require
a new additive material trail with non-empty commits per material unit, without
rewrite, rebase, squash or deletion of historical evidence.

Each generated `/goal` prompt must require a per-unit evidence block:

1. declared unit id;
2. changed files;
3. `git show --stat --oneline <commit>`;
4. focused oracles run;
5. negative checks run;
6. reviewer result;
7. post-commit `git status --short --branch --untracked-files=all`;
8. sync status: `LOCAL_COMMITTED`, `REMOTE_SYNCED`,
   `REMOTE_SYNC_NOT_REQUESTED` or `SYNC_BLOCKED`.

Default sync means local Git commit certification. Remote sync or push is
forbidden unless the user explicitly authorizes remote actions.

Reject weak trees that omit per-SPEC files, oracles, review loop, stop states,
material-diff evidence, sync status or commit rhythm.

## Output Contract

Use these statuses:

- `NEEDS_SPEC_MATURITY`: a mature input artifact is not available.
- `NEEDS_EXECUTION_UNIT_FIDELITY`: declared execution units were not preserved
  exactly.
- `NEEDS_SLICE_FIDELITY`: backward-compatible alias for
  `NEEDS_EXECUTION_UNIT_FIDELITY`.
- `NEEDS_TREE_REPAIR`: generated tree failed a required tree gate.
- `DRAFT_MATERIALIZATION_TREE`: use only when the user explicitly requested
  staged review before `/goal`.
- `NEEDS_TREE_ACCEPTANCE`: use only when owner acceptance is required to change
  the declared execution contract.
- `READY_GOAL_PROMPT`: input artifact is mature, tree passes gates, and `/goal`
  is ready.
- `SUPER_SPEC_MATERIALIZED`: a Super SPEC was written to
  `GOAL-SUPER-SPEC-<slug-or-timestamp>.md` and summarized instead of pasted in
  chat.
- `SAVE_REQUESTED`: user explicitly asked to write the prompt or tree to disk.

Default output:

1. `Maturity/Stop Status`
2. `Super SPEC Artifact` path and summary when one was created
3. `Materialization Tree`
4. `Readiness Score`
5. `Ready /goal Prompt` when gates pass

## Locks

- Do not mention project-specific origin stories, project names, paths, or
  domain examples.
- Do not generate `/goal` from an immature input artifact.
- Do not ask for a separate permission between tree and `/goal` when the user
  explicitly invoked the skill and the tree passes all gates.
- Do not treat an implicit or weak tree as passing internal gates.
- Do not execute the implementation unless the user explicitly asks in a
  separate instruction.
- Do not write files unless the user asks to save the output, except for the
  required `GOAL-SUPER-SPEC-<slug-or-timestamp>.md` artifact when a Super SPEC
  must be produced or expanded.
- Do not paste the full Super SPEC into the context window.
- Do not hide forbidden moves, missing oracles, or owner-decision points inside
  prose.
- Do not emit a prompt that lacks `SPEC-000`, commit-per-SPEC discipline,
  material-diff proof, sync status, negative grep, review loop, stop states, or
  final delivery contract.
- Do not compress declared execution units into fewer implementation units.
- Do not allow empty commits to satisfy material execution units.
- Do not allow `GO` when declared units were implemented in compacted commits
  and later masked with empty certification commits.
- Do not let prior commits or closeouts satisfy a new materialization run by
  default; require explicit baseline-only versus execution-credit treatment.
- Do not overwrite an earlier failed or partial closeout as if it never
  happened; preserve it as historical evidence and repair with additive
  material commits unless the owner explicitly authorizes a different contract.
- Do not write lexical negative greps that reject valid blocked-state,
  reason-code or safety vocabulary when the actual forbidden issue is runtime
  behavior.
- Do not imply parallel write subagents for a strict commit-per-unit queue
  unless the prompt defines disjoint write scopes and serialized integration.
- Do not require or imply remote sync unless the user explicitly authorized
  remote actions.
- Do not let the generated prompt authorize live execution, persistence,
  public-surface changes, destructive operations, or external access unless the
  SPEC explicitly authorizes them and names the boundary.
- Do not embed project-specific domain examples in the skill. Domain specifics
  must come from the input SPEC.

## Done

`tes-goal-maestro` is complete when it either stops with
`NEEDS_SPEC_MATURITY`, `NEEDS_EXECUTION_UNIT_FIDELITY`, `NEEDS_TREE_REPAIR`,
or delivers a ready `/goal` prompt whose artifact, boundaries, execution
units, ownership, oracles, negative grep, commit rhythm, review loop, and stop
states are explicit and faithful to any execution queue declared by the input
artifact.
