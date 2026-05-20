# Maestral Goal Prompt

Use this reference only after `tes-goal-maestro` passes the Maturity Gate or
needs to draft the explicit materialization tree.

## Core Rule

```text
A maestral /goal prompt is an execution contract, not a long request.
```

It names the artifact, protects boundaries, decomposes work, assigns ownership,
defines oracles, preserves review, requires commit discipline, and declares
honest stop states before implementation begins.

## Materialization Tree Schema

Always produce this schema before the final prompt:

```text
Canonical Artifact:
Certified Context:
Phase Boundary:
Non-Objectives:
Central Rule:
Forbidden Moves:
SPEC Slices:
Subagent Ownership:
Per-SPEC Oracles:
Negative Grep:
Commit Strategy:
Review Loop:
Stop States:
Final Delivery Contract:
```

If the tree is inferred from the SPEC rather than supplied by the user, label it
`DRAFT_MATERIALIZATION_TREE` and ask for acceptance.

## Readiness Checklist

The final `/goal` prompt is ready only when a future agent can execute it
without inventing:

1. artifact;
2. scope;
3. boundaries;
4. sequencing;
5. subagent ownership;
6. tests and oracles;
7. commit rhythm;
8. stop states.

## Prompt Skeleton

```text
/goal
Materialize <CanonicalArtifact> as <capability>, in incremental, auditable,
fixture-first execution with commit per SPEC.

Do not restart from zero. Use the real worktree and Git state as source of
truth.

Main SPEC:
<path/to/spec.md>

Mandatory context:
- <already certified dependency>
- <boundary to preserve>
- <phase separation>
- <known deferred work>

Mission:
<one or two paragraphs describing the artifact and why it matters>

Central rule:
<single spine rule>

Do not allow:
- <forbidden move 1>
- <forbidden move 2>
- <forbidden move 3>

Specialized subagents:

1. <Role>
Ownership:
- <paths>
Mission:
- <bounded responsibility>

2. Reviewer Senior
Read-only per SPEC.
Mission:
- Review scope, boundary, oracles and false closure.

3. Evidence/Oracle Senior
Ownership:
- reports/checklists
Mission:
- Record commands, results, gaps and closeout.

Work mode:
- Execute small SPECs.
- Commit per SPEC.
- Do not stage unrelated files.
- Do not revert user changes.
- Stop only for real owner decisions, critical blockers or safety blockers.

First mandatory act:
1. git status --short --branch --untracked-files=all
2. git log --oneline -12
3. Identify pending changes.
4. Run read-only oracles.
5. Commit baseline docs if green.

SPEC-000 Preflight And Baseline
Objective:
<baseline objective>
Allowed files:
- <paths>
Oracles:
- <commands>
Commit:
<semantic commit>

SPEC-001 <Small Slice>
Objective:
<one narrow goal>
Allowed files:
- <paths>
Forbidden:
- <paths/actions>
Oracles:
- <commands>
Commit:
<semantic commit>

Full Oracle:
- <focused tests>
- <regression tests>
- git diff --check
- negative rg checks

Stop criteria:
- GO
- NEEDS_OWNER_DECISION
- BLOCKED
- SAFETY_BLOCKED

Final delivery:
- SPECs executed
- subagents used
- commits
- files changed
- oracles run
- boundaries preserved
- pending decisions
- final status
```

## Slice Rules

Each SPEC slice should remove one ambiguity or certify one layer. Split any
slice that cannot be explained in one short objective.

Every slice needs:

1. objective;
2. allowed files;
3. forbidden files or actions when risk exists;
4. falsifiable oracles;
5. semantic commit message.

## Negative Grep

Add negative grep for phase violations, hidden runtime execution, forbidden
fallbacks, unsafe exports, or boundary drift.

Examples:

```text
rg -n "fetch|getFetcher|service.run" <contract-files>
rg -n "rawPayloadExported: true|finalInterpretationExported: true" <scope>
rg -n "ForbiddenProvider|legacyFallback" <scope>
```

## Anti-Patterns

Avoid:

1. starting implementation before naming the canonical artifact;
2. mixing semantic contract and physical storage in one phase;
3. asking for broad best effort;
4. assigning subagents without file ownership;
5. letting runtime code enter a contract-only phase;
6. treating projections, reports, or generated hypotheses as source of truth;
7. running broad regressions without focused oracles;
8. ending with prose instead of evidence;
9. accumulating multiple SPECs before commit;
10. treating review as optional.
