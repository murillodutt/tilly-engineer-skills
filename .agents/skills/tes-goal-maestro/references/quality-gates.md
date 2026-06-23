# Quality Gates

Use this reference when the SPEC, materialization tree or `/goal` prompt might
be too weak to execute safely.

## Readiness Score

Assign the lowest applicable status.

### NEEDS_SPEC_MATURITY

Use when the SPEC lacks any required foundation:

1. canonical artifact;
2. capability or purpose;
3. certified context or dependencies;
4. phase boundary;
5. non-objectives;
6. central rule;
7. forbidden moves;
8. acceptance criteria or oracle candidates;
9. stop states or owner-decision points;
10. final delivery contract.

Return only the smallest missing set.

### READY_GOAL_PROMPT

Use when:

1. SPEC is mature;
2. tree is explicit and passes internal gates;
3. file ownership is clear;
4. oracles are falsifiable;
5. stop states are explicit;
6. coding, UI, runtime-script or generated-app units include an Engineering
   Method Profile, `STRUCTURAL_METHOD=<profile-id>`, topology budget,
   structural source probes, structural negative checks, structural oracles and
   structural handoff requirements.

Explicit skill invocation is enough to produce both the tree and the final
`/goal` prompt in one response when these conditions are true.

When a Super SPEC is generated in the flow, readiness also requires that the
full Super SPEC is written to `GOAL-SUPER-SPEC-<slug-or-timestamp>.md` and that
chat output contains only the artifact path and a short summary.

### NEEDS_EXECUTION_UNIT_FIDELITY

Use when the source artifact declares materialization units and the proposed
tree or prompt would omit, merge, rename, reorder or otherwise compress them.
Also use it when the prompt would treat empty commits, compacted broad commits,
prior commits, old closeouts or broad-only oracles as proof that individual
material units executed in a new materialization run.

Also use it when a mature artifact declares vertical slices or asset-transfer
units and the proposed tree rewrites them into horizontal layer packages such
as "all docs", "all scripts", "all tests", or broad cleanup.

Return the declared unit list and the proposed correction. Do not produce
`READY_GOAL_PROMPT` until the tree preserves the declared list or the user
explicitly accepts a changed execution contract.

`NEEDS_SLICE_FIDELITY` is a backward-compatible alias for older prompts, but
new skill output should prefer `NEEDS_EXECUTION_UNIT_FIDELITY`.

### NEEDS_TREE_REPAIR

Use when the generated tree fails fixed schema, ownership, oracle,
execution-unit fidelity, material-continuation, structural-method,
negative-grep semantics, commit-rhythm or closeout checks.

### NEEDS_STRUCTURAL_METHOD

Use when code, UI, generated app artifacts or runtime scripts are in scope and
the tree or prompt lacks a safe Engineering Method Profile.

Also use it when the profile or evidence shows behavior can pass while the
implementation collapses into a god file, duplicates domain logic, mixes UI,
domain, storage, runtime or adapter layers without contract, bypasses framework
topology, or misuses a single-file exception as permission for unbounded file
growth.

Also use it when the prompt names a profile but does not enforce it through a
Method Enforcement Packet: `STRUCTURAL_METHOD=<profile-id>`, file topology
budget, allowed new modules/internal sections, structural debt budget,
structural source probes, `bug_vs_architecture` recovery classification and
structural handoff constraints.

Also use it when browser, UI, game or rendered-canvas work requires
certification but the prompt or closeout lacks a stable browser metrics
contract or visual-spatial oracle for risks such as render, layout, spawn,
raycast, camera framing or spatial alignment.

### DRAFT_MATERIALIZATION_TREE

Use only when the user explicitly asks for staged review before `/goal`.

### NEEDS_TREE_ACCEPTANCE

Use only when changing the declared execution contract requires owner
acceptance, or when a user-requested staged review tree has not been accepted.

## Maturity Failure Examples

Stop if the SPEC says:

1. "implement the feature" without canonical artifact;
2. "use best effort" without stop criteria;
3. "run everything" without phase boundary;
4. "add tests" without oracle candidates;
5. "integrate with storage/live/API" while saying the phase is contract-only;
6. "generate report" when the artifact is actually a machine contract.
7. "execute these slices" but the prompt collapses them into fewer commits.
8. "commit per slice" but there is no material-diff or sync evidence gate.
9. "continue from history" without saying whether prior commits are
   baseline-only or execution credit.
10. "execute these vertical slices" but the prompt rewrites them as all docs,
    all scripts, all tests or broad cleanup.
11. "build this app" without stating the intended code topology, structural
    boundaries or structure-sensitive oracles.
12. "certify this browser app/game/UI" without a machine-readable metrics
    artifact and visual-spatial evidence when visual or spatial failure is a
    realistic risk.

## Weak Prompt Rejection

Reject a prompt if it lacks:

1. `SPEC-000 Preflight And Baseline`;
2. allowed files per slice;
3. forbidden files or actions;
4. commit per SPEC;
5. material-diff proof per material SPEC;
6. focused oracles;
7. negative grep;
8. reviewer loop;
9. sync status per SPEC;
10. stop states;
11. final closeout.
12. exact preservation of any slice list declared by the SPEC.
13. treatment of prior commits or closeouts when they may exist.
14. semantic negative-grep separation for valid blocked-state vocabulary.
15. rejection of horizontal layer packages when the SPEC declares vertical
    slices or asset-transfer units.
16. Next Prompt Handoff only when explicitly requested, with post-`GO`
    certification, chat-only emission and no automatic execution.
17. Execution Loop only when `--execute-loop` is explicitly requested, with an
    Execution Cost Draft, `ACTIVE_SPEC` isolation, parent validation, local-only
    commit sync and Executive Stop Audit.
18. Engineering Method Profile for coding, UI or generated-app work, including
    topology, exceptions, structural negative checks and structural oracles.
19. `STRUCTURAL_METHOD=<profile-id>`, topology budget, structural source
    probes, structural debt budget and structural handoff requirements for
    coding, UI, runtime-script or generated-app work.

## Boundary Leakage Checks

Ask whether the prompt accidentally permits:

1. runtime execution in a contract-only phase;
2. storage or migration in a semantic phase;
3. public API or UI changes in an internal phase;
4. network/live access in a fixture-first phase;
5. destructive git or filesystem operations;
6. secrets, credentials or private data;
7. raw payload export;
8. final interpretation, verdict or score;
9. god-file growth, framework-topology bypass or accidental UI/domain/storage
   mixing in coding or app-building work.
10. next-unit architecture regression because no structural handoff carried the
    active method, changed topology, accepted debt and constraints.

If yes, revise before returning the prompt.

## Interaction Checks

A valid skill response must not stop to ask permission between a valid tree and
the `/goal` prompt after explicit invocation. The tree gate is technical:
generate, validate, then emit `READY_GOAL_PROMPT`.

A valid response must not paste a generated Super SPEC into the context window.
Use the `GOAL-SUPER-SPEC-<slug-or-timestamp>.md` artifact instead, then continue
to the tree and `/goal` prompt when the remaining gates pass.

Next Prompt Handoff is valid only when explicitly requested by
`next_prompt_handoff=true`, `--next-prompt-handoff`, or an equivalent direct
trigger. When requested, the generated prompt must require chat-only next
prompt emission after `GO` and certification, must not write the next prompt to
disk without an explicit save request, and must not execute it automatically.
When not requested, the prompt must not include a next-prompt handoff clause.

Execution Loop is valid only when explicitly requested by `--execute-loop`.
When requested, the generated response must require an `Execution Cost Draft`
from material sources before spawning, one fresh worker per `ACTIVE_SPEC`,
full prompt plus hard active-SPEC envelope, parent validation before advancing,
local automatic commit per green SPEC, no remote push, bounded
`SPEC_REPAIR_BY_LLM`, a loop-state block for every attempt, classified
baseline state before the first worker, owner-approved cloud escalation only,
failed-attempt recovery before the next attempt, persistent ledger when the loop
is long or repaired, exact parent-fallback flag authorization, bounded audit
repairs, strict sequential replay, baseline-only comparison for reference
implementations or manual builds, active Engineering Method Profile when code
structure is in scope, `STRUCTURAL_METHOD=<profile-id>` envelope fields,
structural decision ledger fields, `bug_vs_architecture` recovery
classification, and Executive Stop Audit before final stop.
When not requested, the prompt must not include execution-loop behavior.

If Next Prompt Handoff and Execution Loop are both explicitly requested,
Execution Loop owns internal continuation. Reject prompts that also include the
ordinary handoff constraint in a way that forbids parent-runner execution of
the next validated active-SPEC prompt.

## Commit Rhythm Checks

A valid prompt must require:

1. no accumulated multi-slice commits;
2. stage only current-unit files;
3. semantic commit messages;
4. no empty commits for material units;
5. `git show --stat --oneline <commit>` evidence for each material unit;
6. changed files inside the unit's allowed file matrix;
7. no unrelated revert;
8. no force push;
9. worktree status inspection after each commit and before final closeout;
10. one visible commit per declared unit unless explicitly no-commit;
11. sync status per unit;
12. prior commits are baseline-only by default unless explicitly accepted as
    execution credit;
13. no rewrite, rebase, squash or deletion of historical evidence to repair
    materialization fidelity.

## Material Execution Checks

Before `GO`, verify:

1. declared unit count matches executed unit count;
2. each material unit has a non-empty diff or explicit no-material-change
   rationale accepted by the source artifact;
3. each material unit has focused oracle evidence;
4. broad regression did not replace missing per-unit oracles;
5. compacted implementation commits were not masked by later empty commits;
6. prior commits or closeouts were not counted as new material execution by
   default;
7. earlier failed or partial closeouts were preserved as historical evidence
   and repaired through additive material commits when applicable;
8. reference implementations, prior manual builds, browser smoke results, run
   records and post-facto audits were baseline-only comparison evidence, not
   execution credit;
9. structural method evidence exists for coding, UI or generated-app units;
10. structural source probes ran or were explicitly impossible with rationale;
11. structural handoff exists when another unit can build on the same code;
12. browser metrics artifact exists when browser app, UI, game or rendered
    canvas certification is in scope;
13. visual-spatial oracle evidence exists or is explicitly impossible with
    rationale when visual or spatial failure is in scope;
14. remote sync is reported only when explicitly authorized.

If any check fails, use `NEEDS_EXECUTION_UNIT_FIDELITY`.
If structural method evidence is missing or failing, use
`NEEDS_STRUCTURAL_METHOD`.

## Closeout Checks

Final delivery must report:

1. status: `GO`, `NEEDS_OWNER_DECISION`, `BLOCKED` or `SAFETY_BLOCKED`;
2. execution units executed;
3. commits;
4. files changed;
5. tests and oracles run;
6. failures fixed;
7. boundaries preserved;
8. pending owner decisions.
9. declared unit count versus executed unit count.
10. material units with non-empty diff versus empty/no-diff units.
11. sync status for each unit.
12. whether prior commits/closeouts were baseline-only or explicitly credited.
13. whether negative grep allowed valid blocked-state vocabulary while
    forbidding unsafe behavior.
14. structural method result for coding, UI or generated-app units.
15. structural handoff for coding, UI or generated-app units when applicable.
16. browser metrics artifact and visual-spatial oracle result when applicable.

## Stop-State Mapping

Use:

- `GO` when all required slices are committed, oracles are green and no
  boundary is violated.
- `NEEDS_OWNER_DECISION` when the next safe step needs product, architecture,
  public-surface, data, legal, live-execution or ownership decision.
- `NEEDS_STRUCTURAL_METHOD` when code, UI or generated-app work lacks a safe
  Engineering Method Profile or fails structure-sensitive checks.
- `BLOCKED` when a critical oracle fails outside the slice's control.
- `SAFETY_BLOCKED` when the task would require unsafe access, fake authority,
  secrets, destructive operations, bypass, private data, or hidden production
  changes.

## Final Prompt Strength Test

Before returning `READY_GOAL_PROMPT`, ask:

```text
Could a capable agent execute this prompt without asking what to build, which
files to touch, how to verify, when to commit, or when to stop?
```

If the answer is no, the prompt is not ready.

Then ask:

```text
If the SPEC declared N slices, does this prompt preserve N visible slices and
N matching commit decisions?
```

If the answer is no, return `NEEDS_EXECUTION_UNIT_FIDELITY`.

Then ask:

```text
Does every material unit have changed files, focused oracle evidence,
reviewer result, git show --stat output, post-commit status and sync status?
```

If the answer is no, return `NEEDS_EXECUTION_UNIT_FIDELITY`.

Then ask:

```text
If prior commits or closeouts exist, does the prompt explicitly say whether
they are baseline-only or execution credit, and does new execution require an
additive material trail?
```

If the answer is no, return `NEEDS_TREE_REPAIR`.

Then ask:

```text
Do negative greps target forbidden behavior without rejecting valid policy
vocabulary such as blocked-state enums or reason codes?
```

If the answer is no, return `NEEDS_TREE_REPAIR`.

Then ask:

```text
If code, UI or generated app artifacts are in scope, does the prompt state an
Engineering Method Profile with topology, exceptions, structural negative
checks, structural oracles and per-unit structural evidence?
```

If the answer is no, return `NEEDS_STRUCTURAL_METHOD`.

Then ask:

```text
If code, UI or generated app artifacts are in scope, does the prompt carry
`STRUCTURAL_METHOD=<profile-id>`, topology budget, structural source probes,
structural debt budget, `bug_vs_architecture` recovery classification and
structural handoff constraints?
```

If the answer is no, return `NEEDS_STRUCTURAL_METHOD`.

Then ask:

```text
If browser, UI, game or rendered-canvas work is in scope, does the prompt carry
a stable browser metrics contract and visual-spatial oracle requirement when
visual or spatial failure can occur?
```

If the answer is no, return `NEEDS_STRUCTURAL_METHOD`.

Then ask:

```text
If Next Prompt Handoff appears, was it explicitly requested, and does it wait
for GO plus certification before emitting only the next prompt in chat without
writing or executing it?
```

If the answer is no, return `NEEDS_TREE_REPAIR`.

Then ask:

```text
If Execution Loop appears, was `--execute-loop` explicitly requested, and does
it require Execution Cost Draft, ACTIVE_SPEC isolation, parent validation,
local-only commit sync, baseline classification, loop-state blocks, canonical
SPEC_REPAIR_BY_LLM, failed-attempt recovery, persistent ledger triggers, the
exact `--execute-loop-parent-fallback` flag for parent fallback, owner-approved
cloud escalation, strict sequential replay, reference implementations as
baseline-only comparison, bounded audit repairs, structural decision ledger
fields, `bug_vs_architecture` recovery classification and Executive Stop Audit?
```

If the answer is no, return `NEEDS_TREE_REPAIR`.
