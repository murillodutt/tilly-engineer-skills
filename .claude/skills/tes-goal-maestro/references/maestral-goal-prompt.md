# Maestral Goal Prompt

Use this reference only after:

1. the SPEC passes the Maturity Gate;
2. the materialization tree has been produced;
3. the tree passes the skill's internal fidelity and quality gates.

Do not ask the user for an extra acceptance step before producing `/goal`
unless the user explicitly requested staged review or the tree would change the
declared execution contract.

## Core Rule

```text
A maestral /goal prompt is an execution contract, not a long request.
```

It must let a future agent execute without inventing artifact, scope,
boundaries, owners, tests, commit rhythm or stop states.

If the source flow created a Super SPEC, the prompt must name the
`GOAL-SUPER-SPEC-<slug-or-timestamp>.md` artifact path as the canonical Super
SPEC reference. Do not embed the full Super SPEC body inside the `/goal`
prompt unless the user explicitly requests a self-contained prompt and accepts
the larger context footprint.

If the source artifact declares a materialization queue, the prompt must
preserve that queue. The prompt is not allowed to compress declared execution
units into fewer execution commits.

A commit message is not execution evidence. The prompt must require material
diff proof, focused oracles, reviewer result, post-commit status and sync
status for every material unit.

## Required Output Shape

The final prompt must include:

1. `/goal` opening line.
2. Mission.
3. Main SPEC path.
4. Super SPEC artifact path when one was created.
5. Certified context.
6. Phase boundary.
7. Central rule.
8. Non-objectives and forbidden moves.
9. Specialized subagents with ownership.
10. Work mode.
11. First mandatory act.
12. `SPEC-000 Preflight And Baseline`.
13. Narrow execution units.
14. Full oracle.
15. Negative grep.
16. Stop criteria.
17. Final delivery contract.
18. Execution unit fidelity statement when the input artifact declares units.
19. Per-unit material-diff and sync-commit evidence requirements.
20. Material continuation rule when prior commits, closeouts or partial
    implementations may exist.
21. Semantic negative-grep rules when blocked-state vocabulary is valid inside
    the contract.
22. Engineering Method Profile when the run changes code, UI or generated app
    artifacts.
23. Optional Next Prompt Handoff clause only when explicitly requested by
    `next_prompt_handoff=true`, `--next-prompt-handoff`, or an equivalent
    direct trigger.
24. Optional Execution Loop boundary only when explicitly requested by
    `--execute-loop`.

## Prompt Template

```text
/goal
Materialize <CanonicalArtifact> as <capability/purpose>, in incremental,
auditable, fixture-first execution with commit per SPEC.

Do not restart from zero. Use the real worktree and Git state as the source of
truth.

Main SPEC:
<path/to/spec.md>

Certified context:
- <certified dependency or prior closeout>
- <existing contract/module that must be reused>
- <phase boundary already decided>
- <known deferred work>

Mission:
<short mission explaining the artifact, capability and value>

Phase boundary:
<what this phase may do>
<what later phases must do instead>

Central rule:
<single rule that prevents semantic drift>

Do not allow:
- <forbidden move 1>
- <forbidden move 2>
- <forbidden move 3>
- <forbidden move N>

Engineering Method Profile:
- Stack or language family: <HTML/CSS/JS, TypeScript, Vue, React, Python, CLI,
  docs generator, adapter, or no-code rationale>
- Intended topology: <files/modules/components/composables/stores/services/
  adapters/scripts/internal sections>
- Structural boundaries: <UI/domain/storage/runtime/docs/adapter boundaries>
- Topology exceptions: <none or source-mandated single-file deliverable with
  internal modularity, named sections, narrow APIs and no duplicated logic>
- Structural negative checks: <god file, duplicated logic, layer mixing,
  framework-topology bypass, broad inline CSS/JS when separation is expected,
  unchecked file-size growth>
- Structural oracles: <size thresholds, module/component inventory,
  import/dependency checks, lint/typecheck/build, rendered UI smoke or source
  probes>

Subagents:

1. <Role Senior>
Ownership:
- <allowed path or responsibility>
Mission:
- <bounded mission>

2. Tests Senior
Ownership:
- <test paths>
Mission:
- Build focused, adversarial and regression tests for this phase.

3. Reviewer Senior
Read-only per SPEC.
Mission:
- Review scope inflation, boundary drift, forbidden moves, missing oracles and
  false closure.

4. Evidence/Oracle Senior
Ownership:
- <reports/checklists if any>
Mission:
- Track commands, outputs, gaps, closeout and final status.

Work mode:
- Execute small SPECs.
- Do not accumulate multiple SPECs without commit.
- If prior commits, closeouts or partial implementations exist, treat them as
  baseline context by default, not execution credit for this run.
- Produce a new additive material trail with non-empty commits per material
  unit unless the source artifact explicitly marks a unit no-material-change or
  no-commit.
- Do not rewrite, rebase, squash, delete or mask historical evidence.
- Preserve every materialization unit declared by the input artifact.
- Do not merge declared units unless the user explicitly changes the
  execution contract before implementation.
- A declared no-commit preflight must still be reported as executed.
- Before editing code, UI or generated app artifacts, apply the Engineering
  Method Profile and do not accept behavior-only green if structure regresses.
- Stage only files for the current SPEC.
- Commit and certify the current SPEC before starting the next SPEC.
- Do not revert user changes.
- Preserve unrelated worktree changes.
- Run focused oracle before broader oracle.
- Fix until green or stop honestly.
- No force push, destructive git, hidden live execution or public-surface drift.

Next Prompt Handoff:
- Disabled unless `next_prompt_handoff=true`, `--next-prompt-handoff`, or an
  equivalent direct trigger was explicitly requested.
- When enabled, after this run reaches `GO` and certification is complete,
  emit the next `/goal` prompt for the next declared execution unit in this
  same chat/context window.
- Do not write the next prompt to disk unless the user explicitly asks.
- Do not execute the next prompt automatically.
- If this run stops, certification is incomplete, or no next declared unit
  exists, report the stop/final state instead of generating a next prompt.
- If `--execute-loop` is also enabled, suspend this ordinary handoff clause for
  internal continuation; the parent runner owns next-prompt generation and may
  execute the next active-SPEC prompt only after parent validation.

Execution Loop:
- Disabled unless `--execute-loop` was explicitly requested.
- When enabled, the parent runner must create an `Execution Cost Draft` before
  spawning any worker.
- The parent runner opens one `ACTIVE_SPEC` at a time with the full prompt plus
  a hard active-SPEC envelope.
- Workers may execute only `ACTIVE_SPEC`; they may propose next-prompt material
  but the parent generates the next prompt.
- Local commit per green SPEC is allowed; remote sync or push remains
  forbidden without separate user authorization.
- Reference implementations, prior manual builds, browser smoke results,
  screenshots, run records and post-facto audits are baseline-only comparison
  evidence. They never count as execution credit for this loop.
- Strict sequential replay is required: a SPEC is complete only from evidence
  produced after its `ACTIVE_SPEC` was opened and parent-validated before the
  next SPEC starts.
- The parent must classify the baseline worktree before the first worker,
  carry the active Engineering Method Profile when code structure is in scope,
  maintain a loop-state block for every attempt, repair only canonical SPEC
  artifacts, resolve failed-attempt residue before the next attempt, and use
  cloud escalation only after owner-approved redaction.
- Parent-side execution fallback is disabled unless the exact
  `--execute-loop-parent-fallback` flag was requested.
- Create `GOAL-EXECUTION-LOOP-LEDGER-<slug-or-timestamp>.md` when the loop is
  long, repaired, audit-expanded, explicitly requested, or resumes after
  context compaction without exact loop-state proof.
- Audit-added `SPEC-AUDIT-*` units are bounded; repeated audit expansion without
  new material evidence stops for owner decision or contract instability.
- Final stop requires Executive Stop Audit.

Negative grep semantics:
- Separate valid blocked-state or policy vocabulary from forbidden executable
  behavior.
- Allow enums, reason codes and fields that record a technical block when they
  are part of the contract.
- Forbid behavior such as solving CAPTCHA, proxy evasion, fake credentials,
  leaked secret use, hidden network calls, unauthorized storage or runtime
  boundary violations.

First mandatory act:
1. Run `git status --short --branch --untracked-files=all`.
2. Run `git log --oneline -12` when lineage matters.
3. Identify unrelated pending changes.
4. Read the main SPEC and existing dependencies.
5. Run read-only baseline oracles.
6. Derive the Engineering Method Profile before editing code, UI or generated
   app artifacts.
7. Declare the file matrix before editing.

SPEC-000 Preflight And Baseline
Objective:
<baseline objective>
Allowed files:
- <paths>
Forbidden:
- <paths/actions>
Oracles:
- <commands>
Commit:
<none or semantic commit when baseline docs are in scope>

Execution unit fidelity:
- Preserve the source-declared queue exactly.
- Execute each declared unit in order.
- Commit after each declared unit unless the unit is explicitly no-commit.
- Empty commits do not satisfy material execution units.
- Prior commits or closeouts do not satisfy this run's material units by
  default; they are baseline-only unless explicitly accepted by the source
  artifact or owner.
- Earlier failed or partial closeouts must be preserved as historical evidence
  and repaired through additive material commits, not overwritten as if they
  never happened.
- A SPEC is complete only after focused oracle, reviewer diff check, semantic
  commit, captured commit hash, `git show --stat`, post-commit status and sync
  status.
- Default sync is local commit certification. Remote sync or push requires
  explicit user authorization.
- Stop with `NEEDS_EXECUTION_UNIT_FIDELITY` if the prompt cannot preserve this
  queue.

SPEC-001 <Small Slice>
Objective:
<one narrow goal>
Allowed files:
- <paths>
Forbidden:
- <paths/actions>
Owner:
<role>
Oracles:
- <focused commands>
Negative checks:
- <rg commands or assertions>
Commit:
<semantic commit>
Completion evidence:
- Changed files:
- `git show --stat --oneline <commit>`:
- Oracles:
- Negative checks:
- Structural method result:
- Reviewer result:
- Post-commit status:
- Sync status:
  - `LOCAL_COMMITTED`
  - `REMOTE_SYNCED`
  - `REMOTE_SYNC_NOT_REQUESTED`
  - `SYNC_BLOCKED`

SPEC-002 <Small Slice>
Objective:
<one narrow goal>
Allowed files:
- <paths>
Forbidden:
- <paths/actions>
Owner:
<role>
Oracles:
- <focused commands>
Commit:
<semantic commit>
Completion evidence:
- Changed files:
- `git show --stat --oneline <commit>`:
- Oracles:
- Negative checks:
- Structural method result:
- Reviewer result:
- Post-commit status:
- Sync status:

Full Oracle And Closeout
Run:
- <focused test suite>
- <regression suite>
- <lint/typecheck/contract/doc checks>
- <structural method checks when applicable>
- `git diff --check`
Negative grep:
- <forbidden runtime or provider pattern>
- <unsafe export pattern>
- <phase leakage pattern>
Closeout artifact:
- <report path, if any>
Commit:
<semantic certification commit>

Stop criteria:
- `GO`: <green condition>
- `NEEDS_OWNER_DECISION`: <decision condition>
- `BLOCKED`: <critical external blocker>
- `SAFETY_BLOCKED`: <unsafe condition>

Final delivery:
- SPECs executed;
- subagents used;
- commits;
- per-SPEC material-diff evidence;
- sync status per SPEC;
- files changed;
- oracles run;
- structural method result when applicable;
- boundaries preserved;
- blockers or decisions pending;
- next prompt handoff status when explicitly requested;
- execution loop status when `--execute-loop` was requested;
- final status.
```

## Prompt Hardening Checklist

Before returning `READY_GOAL_PROMPT`, verify the prompt:

1. starts from a real SPEC;
2. includes `SPEC-000`;
3. names allowed files per slice;
4. names forbidden moves;
5. assigns ownership;
6. includes per-slice oracles;
7. includes negative grep;
8. requires commit per SPEC;
9. preserves every declared execution unit without silent merge;
10. forbids empty commits as proof of material execution;
11. requires `git show --stat` evidence per material unit;
12. states how prior commits or closeouts are treated when they exist;
13. distinguishes allowed policy vocabulary from forbidden behavior in negative
    grep;
14. requires sync status per unit;
15. preserves unrelated worktree changes;
16. includes reviewer and evidence/oracle roles when complexity warrants them;
17. includes an Engineering Method Profile and structural oracles when code,
    UI or generated app artifacts are in scope;
18. defines stop criteria;
19. defines final delivery;
20. includes a Next Prompt Handoff clause only when explicitly requested, and
    that clause is chat-only, post-certification, non-executing, and does not
    write prompt/tree files without an explicit save request;
21. includes an Execution Loop boundary only when `--execute-loop` is
    explicitly requested, and that boundary preserves parent authority,
    `ACTIVE_SPEC` isolation, baseline classification, loop-state evidence,
    failed-attempt recovery, persistent ledger triggers, local-only commit sync,
    baseline-only comparison for reference implementations, strict sequential
    replay, bounded repair/audit behavior, explicit parent-fallback
    authorization, and Executive Stop Audit.

## Stop If Missing

Stop with `NEEDS_SPEC_MATURITY`, `NEEDS_TREE_REPAIR`,
`NEEDS_EXECUTION_UNIT_FIDELITY`, `NEEDS_STRUCTURAL_METHOD` or
`NEEDS_TREE_ACCEPTANCE` when:

1. the canonical artifact is unclear;
2. the execution phase is unclear;
3. forbidden moves are missing;
4. oracles are missing;
5. the materialization tree fails internal gates;
6. the prompt would need to invent file ownership or stop states;
7. the prompt would need to merge or drop declared execution units;
8. code, UI or generated app artifacts are in scope but the prompt lacks an
   Engineering Method Profile, structural negative checks or structural
   oracles.

Use `NEEDS_TREE_ACCEPTANCE` only when changing the declared execution contract
requires owner acceptance or the user explicitly asked for staged review.

## Anti-Patterns

Reject prompts that:

1. say "implement everything" without slices;
2. allow broad best effort;
3. mix contract, runtime, storage and live execution accidentally;
4. omit `git status` preflight;
5. omit per-SPEC commit;
6. allow empty commits to satisfy material execution;
7. omit `git show --stat` material-diff proof;
8. omit sync status;
9. omit negative grep;
10. treat reviewer as optional for high-risk work;
11. end with prose instead of evidence;
12. hide owner decisions;
13. authorize actions not present in the SPEC;
14. compress a declared multi-SPEC queue into fewer commits;
15. let prior commits satisfy a new materialization run by default;
16. use broad lexical greps that fail valid blocked-state vocabulary instead of
    targeting forbidden behavior;
17. include Next Prompt Handoff without an explicit parameter/trigger or allow
    it to execute the next prompt automatically;
18. include Execution Loop without explicit `--execute-loop` or let a worker
    execute outside `ACTIVE_SPEC`, push remotely, or bypass Executive Stop
    Audit.
19. let a reference implementation, prior manual build, browser smoke result,
    run record or post-facto audit satisfy `--execute-loop` without strict
    sequential replay.
20. accept a behavior-green implementation that collapsed into a god file,
    duplicated domain logic, bypassed framework topology or misused a
    single-file exception to mix unrelated layers.
