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

### DRAFT_MATERIALIZATION_TREE

Use when the SPEC is mature, but the execution tree has not been accepted.

Produce the fixed tree and ask for acceptance. Do not produce `/goal`.

### NEEDS_TREE_ACCEPTANCE

Use when a tree already exists but user acceptance is missing or ambiguous.

### READY_GOAL_PROMPT

Use only when:

1. SPEC is mature;
2. tree is explicit and accepted;
3. file ownership is clear;
4. oracles are falsifiable;
5. stop states are explicit.

## Maturity Failure Examples

Stop if the SPEC says:

1. "implement the feature" without canonical artifact;
2. "use best effort" without stop criteria;
3. "run everything" without phase boundary;
4. "add tests" without oracle candidates;
5. "integrate with storage/live/API" while saying the phase is contract-only;
6. "generate report" when the artifact is actually a machine contract.

## Weak Prompt Rejection

Reject a prompt if it lacks:

1. `SPEC-000 Preflight And Baseline`;
2. allowed files per slice;
3. forbidden files or actions;
4. commit per SPEC;
5. focused oracles;
6. negative grep;
7. reviewer loop;
8. stop states;
9. final closeout.

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

## Commit Rhythm Checks

A valid prompt must require:

1. no accumulated multi-slice commits;
2. stage only current-slice files;
3. semantic commit messages;
4. no unrelated revert;
5. no force push;
6. worktree status inspection before final closeout.

## Closeout Checks

Final delivery must report:

1. status: `GO`, `NEEDS_OWNER_DECISION`, `BLOCKED` or `SAFETY_BLOCKED`;
2. slices executed;
3. commits;
4. files changed;
5. tests and oracles run;
6. failures fixed;
7. boundaries preserved;
8. pending owner decisions.

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
