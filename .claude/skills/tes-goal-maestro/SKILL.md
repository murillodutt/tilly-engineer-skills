---
name: tes-goal-maestro
description: Use when the user explicitly invokes tes-goal-maestro, /tes-goal-maestro, /tes:goal-maestro, $tes-goal-maestro, or directly asks to generate a maestral /goal prompt (gerar um /goal maestral) for incremental, auditable materialization from a mature SPEC, Super SPEC, PRD, relational project plan, or accepted execution tree.
license: MIT
---

# TES Goal Maestro

Operational contract: `tes.goal_maestro@0.3.6`.

## Invocation Contract

Use after explicit invocation or a direct request to generate a maestral
`/goal` prompt from a mature SPEC, Super SPEC, PRD, relational project plan or
accepted execution tree. Do not activate from generic planning, ordinary goal
language, or early design discussion.

`tes-goal-maestro` does not execute implementation by default. It materializes
an execution-grade materialization tree and, when the tree passes the skill's
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

Next Prompt Handoff is opt-in only. Activate it only when the user explicitly
requests the parameter or trigger, for example `next_prompt_handoff=true`,
`--next-prompt-handoff`, or a direct instruction to generate the next `/goal`
prompt in the chat/context window after certification. Do not infer it from a
multi-unit tree, a roadmap, or a desire to continue.

Execution Loop is opt-in only. Activate it only when the user explicitly
requests `--execute-loop`. This runs a parent-controlled execution loop after
`READY_GOAL_PROMPT`: the parent creates an `Execution Cost Draft`, opens one
`ACTIVE_SPEC` at a time in a fresh worker subagent with the full prompt plus a
hard active-SPEC envelope, validates local commit evidence, generates the next
prompt, and runs an Executive Stop Audit before final closure.

Reference implementations, prior manual builds, browser smoke results,
screenshots, run records and post-facto audits are baseline-only comparison
evidence. They never satisfy `--execute-loop` execution credit. A loop needs
strict sequential replay: each declared SPEC must open as `ACTIVE_SPEC`, execute
after the loop starts, produce fresh local evidence and pass parent validation
before the next SPEC opens.

Parent-side execution fallback requires the exact `--execute-loop-parent-fallback` flag; otherwise worker capacity stops with `NEEDS_OWNER_DECISION`.

Structural Method Gate is active for coding or app-building execution units.
It requires an `Engineering Method Profile` plus a compact `Method Enforcement
Packet`: `STRUCTURAL_METHOD=<profile-id>`, topology budget, allowed modules or
internal sections, structural debt budget, structural source probes,
`bug_vs_architecture` classification and structural handoff. The gate is method,
not governance: behavior-green work still fails if it becomes a god file, mixes
layers without contract, duplicates domain logic, bypasses framework topology
or abuses a single-file exception instead of proving internal structure.

If both Next Prompt Handoff and Execution Loop are requested, `--execute-loop`
owns sequential next-prompt generation and execution inside the parent runner.
The ordinary chat-only handoff clause is suspended until the loop stops or
completes, so the generated contract must not contain contradictory
"do not execute the next prompt automatically" language for parent-runner loop
continuation. Workers still cannot generate the authoritative next prompt or
execute later SPECs.

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
12. engineering method profile and Method Enforcement Packet when the run
    changes code, UI, runtime scripts or generated app artifacts;
13. final delivery contract.

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
- `NEEDS_EXECUTION_LOOP_DRAFT`: `--execute-loop` was requested but material
  sources are insufficient to draft the expected loop cost.
- `NEEDS_STRUCTURAL_METHOD`: the run changes code, UI or generated app
  artifacts but lacks enough stack or topology evidence to derive a safe
  Engineering Method Profile.
- `SPEC_BLOCKED`: the active SPEC cannot converge after allowed attempts,
  predictive analysis, knowledge-source escalation and sanitized cloud query.
- `SPEC_CONTRACT_UNSTABLE`: the active SPEC needs more LLM repairs than the
  allowed repair budget after escalation.
- `NEEDS_MORE_LOOPS`: Executive Stop Audit found missing corrective execution
  units and the parent has not yet appended or completed `SPEC-AUDIT-*`.
- `NEEDS_OWNER_DECISION`: safe progress needs owner authority, including
  remote sync, cloud query approval, unstable contract direction or unresolved
  dirty-baseline ownership.
- `SAFETY_BLOCKED`: the loop would require unsafe access, secrets, private
  data, destructive actions, policy bypass or unauthorized external execution.
- `EXECUTION_LOOP_COMPLETE`: all declared SPECs passed and Executive Stop Audit
  confirms final stop.
- `EXECUTION_LOOP_COMPLETE_WITH_AUDIT_REPAIRS`: audit-added `SPEC-AUDIT-*`
  units were needed and then converged.

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
6. Run the Structural Method Gate when execution units touch code, UI or
   generated app artifacts:
   - Derive the profile from material sources: stack, topology, boundaries,
     topology exceptions, negative checks and structural oracles.
   - Carry `STRUCTURAL_METHOD=<profile-id>` through tree, prompt, active-SPEC
     envelope, ledger and closeout.
   - Declare topology budget, allowed files/modules/internal sections,
     forbidden layer moves, structural debt budget and structural source probes.
   - Classify failed coding attempts with `bug_vs_architecture` before retry or
     escalation, including `structural_repair` when architecture collapsed.
   - Require structural handoff when another unit may build on the same code:
     changed topology, preserved boundaries, accepted debt and constraints.
   - If behavior passes but structure regresses, stop with
     `NEEDS_STRUCTURAL_METHOD` or append bounded `SPEC-AUDIT-STRUCTURE-*`
     repair units during `--execute-loop`.
7. Run the Sequential Ownership Gate:
   - When a queue requires commit-per-unit sequencing, prefer centralized
     material edits and use subagents mainly for read-only review, oracle
     tracking or bounded disjoint write scopes.
   - Do not imply parallel write execution when commits must be certified in a
     strict order unless the write scopes are genuinely independent and the
     prompt names how integration will be serialized.
8. Load the relevant references:
   - `references/materialization-tree.md` for tree construction.
   - `references/maestral-goal-prompt.md` for final prompt construction.
   - `references/subagents-and-oracles.md` when roles or verification are weak.
   - `references/quality-gates.md` when maturity, prompt strength or closeout
     needs hardening.
   - `references/execution-loop-runner.md` only when `--execute-loop` was
     explicitly requested.
9. Produce the fixed `Materialization Tree` schema.
10. Validate the tree against maturity, execution-unit fidelity, material
   continuation, ownership, oracle, structural method, negative-grep semantics,
   material-diff, sync-commit and stop-state gates.
11. If a Super SPEC must be produced or expanded, write it to
   `GOAL-SUPER-SPEC-<slug-or-timestamp>.md` in the current target workspace or
   in the explicitly requested output directory. Use a filesystem-safe slug
   from the artifact title when available; otherwise use a timestamp. Do not
   display the full Super SPEC body in chat.
12. Produce the `Ready /goal Prompt` in the same response when the tree passes.
   Stop only for maturity gaps, execution-unit fidelity failure, tree repair,
   owner decisions, or an explicitly requested two-step review workflow.
13. If Next Prompt Handoff was explicitly requested, include a chat-only
    handoff clause in the tree's `Final Delivery Contract` and in the generated
    `/goal` prompt. The clause must require the executor to emit the next
    `/goal` prompt in the same chat/context window only after the current run
    reaches `GO` with certification complete, must forbid writing the next
    prompt to disk, and must forbid executing the next prompt automatically.
    If the current run stops or no next declared unit exists, the executor must
    report the stop/final state instead of generating a next prompt.
    When code, UI, runtime scripts or generated app artifacts were touched, the
    next prompt must also carry a structural handoff summary from material
    evidence: active `STRUCTURAL_METHOD`, files/modules/internal sections
    created or changed, boundaries preserved, accepted structural debt and
    next-unit constraints.
    When `--execute-loop` is also requested, do not emit the ordinary handoff
    clause for internal loop continuation; use Execution Loop next-prompt
    authority instead and report the final prompt/status only after the loop
    stops or completes.
14. If `--execute-loop` was explicitly requested, run the Execution Loop only
    after `READY_GOAL_PROMPT`. Produce the `Execution Cost Draft` first; if it
    cannot be produced from material sources, stop with
    `NEEDS_EXECUTION_LOOP_DRAFT`. Execute one `ACTIVE_SPEC` at a time through a
    fresh worker subagent, require local commit evidence per green SPEC, allow
    `SPEC_REPAIR_BY_LLM` only for the active SPEC with a separate commit, and
    run Executive Stop Audit before any final stop. The loop must record a
    loop-state block for every attempt, classify the worktree baseline before
    the first worker, repair only canonical SPEC artifacts, require explicit
    owner approval before any sanitized cloud query, require `Failed Attempt
    Recovery` with `bug_vs_architecture` before another attempt starts, carry
    `STRUCTURAL_METHOD=<profile-id>` and topology budget in every coding
    active-SPEC envelope, create a persistent structural decision ledger inside
    the loop ledger, create a persistent
    `GOAL-EXECUTION-LOOP-LEDGER-<slug-or-timestamp>.md` for long or repaired
    loops, reject reference implementations and post-facto audits as execution
    credit, and bound audit-repair cycles so repeated `NEEDS_MORE_LOOPS`
    becomes `NEEDS_OWNER_DECISION` or `SPEC_CONTRACT_UNSTABLE`.
15. Keep output chat-first except for the required Super SPEC artifact and any
   required execution-loop ledger. Save prompt or tree files only when the user
   explicitly asks.

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
8. completion evidence requirements;
9. structural method requirements, `STRUCTURAL_METHOD=<profile-id>`, topology
   budget, structural oracles and structural handoff requirements when the unit
   changes code, UI, runtime scripts or generated app artifacts.

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
6. structural method result when applicable;
7. structural handoff when applicable;
8. reviewer result;
9. post-commit `git status --short --branch --untracked-files=all`;
10. sync status: `LOCAL_COMMITTED`, `REMOTE_SYNCED`,
   `REMOTE_SYNC_NOT_REQUESTED` or `SYNC_BLOCKED`.

Default sync means local Git commit certification. Remote sync or push is
forbidden unless the user explicitly authorizes remote actions.

Next Prompt Handoff does not change sync. It is a chat-only closeout behavior
for the generated `/goal` prompt and is disabled unless explicitly requested by
parameter or trigger.

Execution Loop does not change remote sync. It may create local commits per
SPEC when `--execute-loop` is explicitly requested, but remote sync or push
remains forbidden unless separately authorized by the user.

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
- `NEEDS_EXECUTION_LOOP_DRAFT`: `--execute-loop` lacks material sources for
  loop-cost drafting.
- `NEEDS_STRUCTURAL_METHOD`: coding or app-building execution lacks a safe
  Engineering Method Profile, or the profile reveals structural regression that
  must be repaired before the next unit.
- `SPEC_BLOCKED`: active SPEC failed the allowed convergence ladder.
- `SPEC_CONTRACT_UNSTABLE`: active SPEC exceeded repair budget after
  escalation.
- `NEEDS_MORE_LOOPS`: Executive Stop Audit requires appended `SPEC-AUDIT-*`
  units before closure.
- `NEEDS_OWNER_DECISION`: safe progress needs owner authority or an explicit
  product/contract decision.
- `SAFETY_BLOCKED`: unsafe access, secrets, destructive actions or
  unauthorized external execution would be required.
- `EXECUTION_LOOP_COMPLETE`: loop and Executive Stop Audit are complete.
- `EXECUTION_LOOP_COMPLETE_WITH_AUDIT_REPAIRS`: audit-added loops converged.

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
- Do not include Next Prompt Handoff unless `next_prompt_handoff=true`,
  `--next-prompt-handoff`, or an equivalent direct trigger was explicitly
  requested.
- Do not generate a next prompt after a stopped or uncertified run, when no
  next declared unit exists, or by writing it to disk without an explicit save
  request.
- Do not run Execution Loop unless `--execute-loop` was explicitly requested.
- Do not combine ordinary Next Prompt Handoff wording with `--execute-loop` in
  a way that forbids parent-runner continuation after each validated SPEC.
- Do not run `--execute-loop` without an `Execution Cost Draft` from material
  sources.
- Do not run `--execute-loop` on an unclassified dirty baseline.
- Do not certify `--execute-loop` from a reference implementation, prior manual
  build, browser smoke result, screenshot, run record or post-facto audit. They
  are baseline-only comparison evidence and require strict sequential replay
  through fresh `ACTIVE_SPEC` execution.
- Do not let the parent execute a worker role because worker capacity is
  unavailable unless the exact `--execute-loop-parent-fallback` flag was
  explicitly requested.
- Do not let a worker subagent execute outside `ACTIVE_SPEC`, execute the next
  SPEC, push remotely, or become the authority for next-prompt generation.
- Do not let a worker ignore the active unit's Engineering Method Profile,
  collapse code into an unbounded god file, bypass the target framework's
  normal topology, or use a single-file delivery exception as permission to mix
  unrelated layers without internal structure.
- Do not let a coding active-SPEC run without `STRUCTURAL_METHOD=<profile-id>`,
  file topology budget, allowed new module/internal-section constraints,
  structural source probes and structural handoff requirements.
- Do not retry a failed coding active-SPEC before classifying
  `bug_vs_architecture` and deciding whether the next action is bug repair,
  `structural_repair`, SPEC repair, escalation or stop.
- Do not continue an `ACTIVE_SPEC` without a visible loop-state block carrying
  SPEC id, SPEC version, attempt number, repair count, audit-repair cycle,
  last commit and next allowed action.
- Do not start the next attempt while failed-attempt residue remains
  unclassified or unresolved; commit valid material, revert only isolated
  current-attempt changes after diff review, or stop for owner decision.
- Do not let a `SPEC_REPAIR_BY_LLM` be attributed to a human; it must be
  committed separately before implementation and marked as LLM action.
- Do not repair a SPEC only in memory; `SPEC_REPAIR_BY_LLM` must update a
  canonical material artifact such as the source SPEC or generated Super SPEC.
- Do not perform a cloud query from the escalation ladder without explicit
  owner approval of the exact sanitized payload and a redaction block proving
  no secrets, private paths, project names, sensitive architecture structure or
  raw internal payloads remain.
- Do not close an execution loop without Executive Stop Audit.
- Do not keep creating `SPEC-AUDIT-*` loops indefinitely; repeated audit
  requests without new material evidence must stop for owner decision or
  contract instability.
- Do not run long or repaired execution loops without a persistent ledger when
  the draft predicts more than three SPECs, the loop resumes after compaction,
  a SPEC repair occurs, or an audit repair is appended.
- Do not hide forbidden moves, missing oracles, or owner-decision points inside
  prose.
- Do not emit a prompt that lacks `SPEC-000`, commit-per-SPEC discipline,
  material-diff proof, sync status, negative grep, review loop, stop states, or
  final delivery contract.
- Do not emit a coding or app-building prompt without an Engineering Method
  Profile or an explicit no-code rationale.
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
delivers a ready `/goal` prompt whose artifact, boundaries, execution units,
ownership, oracles, negative grep, commit rhythm, review loop, optional Next
Prompt Handoff boundary, optional `--execute-loop` boundary, and stop states
are explicit and faithful to any execution queue declared by the input
artifact; or when `--execute-loop` was explicitly requested, completes with a
certified loop status after parent validation and Executive Stop Audit.
