# Maestral Goal Prompt

Use this reference only after:

1. the SPEC passes the Maturity Gate;
2. the materialization tree has been produced;
3. the user has accepted that tree.

## Core Rule

```text
A maestral /goal prompt is an execution contract, not a long request.
```

It must let a future agent execute without inventing artifact, scope,
boundaries, owners, tests, commit rhythm or stop states.

## Required Output Shape

The final prompt must include:

1. `/goal` opening line.
2. Mission.
3. Main SPEC path.
4. Certified context.
5. Phase boundary.
6. Central rule.
7. Non-objectives and forbidden moves.
8. Specialized subagents with ownership.
9. Work mode.
10. First mandatory act.
11. `SPEC-000 Preflight And Baseline`.
12. Narrow SPEC slices.
13. Full oracle.
14. Negative grep.
15. Stop criteria.
16. Final delivery contract.

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
- Stage only files for the current SPEC.
- Do not revert user changes.
- Preserve unrelated worktree changes.
- Run focused oracle before broader oracle.
- Fix until green or stop honestly.
- No force push, destructive git, hidden live execution or public-surface drift.

First mandatory act:
1. Run `git status --short --branch --untracked-files=all`.
2. Run `git log --oneline -12` when lineage matters.
3. Identify unrelated pending changes.
4. Read the main SPEC and existing dependencies.
5. Run read-only baseline oracles.
6. Declare the file matrix before editing.

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

Full Oracle And Closeout
Run:
- <focused test suite>
- <regression suite>
- <lint/typecheck/contract/doc checks>
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
- files changed;
- oracles run;
- boundaries preserved;
- blockers or decisions pending;
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
9. preserves unrelated worktree changes;
10. includes reviewer and evidence/oracle roles when complexity warrants them;
11. defines stop criteria;
12. defines final delivery.

## Stop If Missing

Stop with `NEEDS_SPEC_MATURITY` or `NEEDS_TREE_ACCEPTANCE` when:

1. the canonical artifact is unclear;
2. the execution phase is unclear;
3. forbidden moves are missing;
4. oracles are missing;
5. the materialization tree is not accepted;
6. the prompt would need to invent file ownership or stop states.

## Anti-Patterns

Reject prompts that:

1. say "implement everything" without slices;
2. allow broad best effort;
3. mix contract, runtime, storage and live execution accidentally;
4. omit `git status` preflight;
5. omit per-SPEC commit;
6. omit negative grep;
7. treat reviewer as optional for high-risk work;
8. end with prose instead of evidence;
9. hide owner decisions;
10. authorize actions not present in the SPEC.
