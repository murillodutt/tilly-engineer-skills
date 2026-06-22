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
5. stop states are explicit.

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
execution-unit fidelity, material-continuation, negative-grep semantics,
commit-rhythm or closeout checks.

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

## Boundary Leakage Checks

Ask whether the prompt accidentally permits:

1. runtime execution in a contract-only phase;
2. storage or migration in a semantic phase;
3. public API or UI changes in an internal phase;
4. network/live access in a fixture-first phase;
5. destructive git or filesystem operations;
6. secrets, credentials or private data;
7. raw payload export;
8. final interpretation, verdict or score.

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
8. remote sync is reported only when explicitly authorized.

If any check fails, use `NEEDS_EXECUTION_UNIT_FIDELITY`.

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

## Stop-State Mapping

Use:

- `GO` when all required slices are committed, oracles are green and no
  boundary is violated.
- `NEEDS_OWNER_DECISION` when the next safe step needs product, architecture,
  public-surface, data, legal, live-execution or ownership decision.
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
If Next Prompt Handoff appears, was it explicitly requested, and does it wait
for GO plus certification before emitting only the next prompt in chat without
writing or executing it?
```

If the answer is no, return `NEEDS_TREE_REPAIR`.
