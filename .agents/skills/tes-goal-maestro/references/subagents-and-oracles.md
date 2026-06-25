# Subagents And Oracles

Use this reference when a materialization tree or `/goal` prompt needs specialized ownership, review loops or stronger verification.

## Subagent Rules

Only include subagents when the user asks for delegation, the work is complex, or parallel independent ownership materially improves execution.

When included:

1. give each subagent a concrete ownership scope;
2. keep write scopes disjoint;
3. tell workers they are not alone in the codebase;
4. keep reviewer read-only;
5. keep evidence/oracle tracking separate from implementation;
6. avoid assigning the immediate blocking task to a subagent;
7. for strict commit-per-unit queues, prefer centralized material edits and read-only reviewer/oracle subagents unless write scopes are genuinely disjoint;
8. when write subagents are used in a strict sequence, name the serialized integration point and require the parent executor to certify one unit before the next starts;
9. close subagents after their bounded task is complete.

For `--execute-loop`, use one fresh worker subagent per `ACTIVE_SPEC`. The parent sends the full prompt plus a hard active-SPEC envelope, validates commit and oracle evidence, then closes the worker. Workers may propose next-prompt material but cannot generate the authoritative next prompt or execute the next SPEC. If worker capacity is unavailable after closing completed or degraded workers, the parent must either execute under the same `ACTIVE_SPEC` envelope only when the current request explicitly authorized parent-side loop execution with the exact `--execute-loop-parent-fallback` flag, or stop with `NEEDS_OWNER_DECISION`.

When a worker touches code, UI, runtime scripts or generated app artifacts, the hard envelope must include `STRUCTURAL_METHOD=<profile-id>`, file topology budget, allowed new modules/internal sections, structural debt budget, structural source probes and structural handoff requirements. The worker must classify failed attempts with `bug_vs_architecture` before another attempt can start.

Reference implementations, prior manual builds, browser smoke results, run records and post-facto audits are reviewer inputs only. They are baseline-only comparison evidence and never replace a fresh worker, strict sequential replay or per-`ACTIVE_SPEC` commit evidence.

## Reusable Roles

### Contracts Senior

Owns schemas, types, fixtures and contract tests.

Use when the slice creates or changes canonical artifacts, DTOs, validation rules or fixture matrices.

### Runtime Senior

Owns runtime modules and integration boundaries.

Use when the slice implements behavior after contracts are established.

### Visual-Runtime Senior

Owns browser automation, rendered evidence, browser metrics, runtime-smoke artifacts and visual-spatial certification.

Use when the slice touches UI, game, canvas, WebGL/WebGPU, Three.js, render, layout, spawn, raycast, camera framing, browser runtime or integration wiring.

### Tests Senior

Owns focused tests, adversarial cases, fixtures and regression selection.

Use when behavior must be certified before broader gates.

### Reviewer Senior

Read-only on the audited run: never edits the operator's code, oracles, or artifacts. Re-execution and re-mutation for `Executive Stop Audit` happen in a clean throwaway worktree, which is not the audited tree — mutating a disposable copy to falsify an oracle is auditing, not editing the work.

Reviews:

1. scope inflation;
2. forbidden moves;
3. missing oracles;
4. public surface drift;
5. storage or runtime entering the wrong phase;
6. hidden external access;
7. uncommitted multi-slice accumulation;
8. empty commits used as material execution evidence;
9. broad commits that hide multiple declared units;
10. missing per-unit sync status;
11. prior commits or closeouts being treated as execution credit without explicit authorization;
12. lexical negative greps that confuse valid blocked-state vocabulary with forbidden executable behavior;
13. `--execute-loop` workers touching files outside `ACTIVE_SPEC`, skipping local commit evidence, pushing remotely, bypassing loop-state evidence, starting another attempt with unresolved failed-attempt residue, missing a required persistent ledger, using parent-side execution fallback without explicit authorization, using cloud escalation without owner-approved redaction, crediting a reference implementation or post-facto audit as loop execution, skipping `STRUCTURAL_METHOD=<profile-id>` envelope fields, missing structural source probes, omitting structural handoff, retrying a coding SPEC without `bug_vs_architecture`, expanding audit repairs without new material evidence, missing required browser metrics or visual-spatial evidence for app/UI/game work, bypassing Executive Stop Audit, or closing with any required-axis oracle that was not re-executed and re-mutated by an auditor distinct from its operator (`audit_remutation≠ran` or `AUDITOR_DISTINCT_FROM_OPERATOR=no` → `NEEDS_INDEPENDENT_AUDIT`).

### Evidence/Oracle Senior

Owns checklists, commands run, results, gaps, closeout reports and final status.

Use for long or high-stakes goals.

### Storage Senior

Owns persistence, migrations, repositories, idempotency and replay.

Use only when storage is explicitly in phase.

### Docs Senior

Owns specs, reports, documentation lint, indexes and traceability.

Use for documentation-heavy or baseline phases.

### Security/Boundary Senior

Owns authorization boundaries, sensitive data handling, secrets avoidance, unsafe access checks and negative grep for safety leakage.

Use when the task touches external access, secrets, auth, privacy, production, destructive commands or public surfaces.

## Ownership Template

```text
<Role> Senior
Ownership:
- <path or responsibility>
Mission:
- <bounded task>
Forbidden:
- <paths/actions out of scope>
Oracles:
- <focused checks>
```

## Oracle Patterns

Prefer focused checks first, then broader checks.

Common oracles:

1. unit or contract tests for changed behavior;
2. fixture parse or schema validation;
3. lint on changed files;
4. typecheck when type surface changes;
5. markdownlint for docs;
6. contract verification when contracts change;
7. migration or DB harness only when storage is in phase;
8. `git diff --check`;
9. negative grep for forbidden patterns;
10. `git show --stat --oneline <commit>` for material-diff proof;
11. post-commit `git status --short --branch --untracked-files=all`;
12. structural source probes for coding work;
13. integration runtime-smoke oracle for wiring units;
14. browser metrics artifact for app, UI, game or rendered-canvas work;
15. visual-spatial screenshot or pixel/legibility audit when layout, render, spawn, raycast, canvas, 3D placement or visual state can fail despite green logic;
16. source-derived contract handoff and API lint when workers reuse existing APIs;
17. final status report.

## Integration Runtime-Smoke Oracle

When a unit connects modules into an executable runtime path, build and typecheck are not enough. `references/runtime-certification.md` § Integration Runtime-Smoke Oracle owns this contract (instantiate the real wiring module, stub only the narrow GPU/network/clock surface, assert state movement and cross-module effect).

## Browser Metrics Contract

`references/runtime-certification.md` § Browser And Visual Certification owns the `browser-metrics.json` artifact shape and required-axis completion. Parent reviewers parse the artifact by that contract before trusting a worker closeout; do not duplicate the field list here.

## Visual-Spatial Oracle

`references/runtime-certification.md` § Browser And Visual Certification owns visual-spatial evidence (screenshot/pixel/canvas/bounding-box/accessibility) and the `scene_nondegeneracy_oracle`. A blocked or degraded required visual axis routes to `VISUAL_CERT_BLOCKED` or `AXIS_UNPROVEN`, never `EXECUTION_LOOP_COMPLETE`.

## Negative Grep Patterns

`references/materialization-tree.md` § Negative Grep owns the contract (semantic, not purely lexical: a blocked-state enum or policy field is allowed when it records a prohibition; the forbidden target is the executable behavior). The command shape, retained here for prompt writers:

```text
rg -n "fetch|getFetcher|service\\.run" <scope>
rg -n "password|token|secret|privateKey" <scope>
# Allowed vocabulary (not a violation): BLOCKED_BYPASS_REQUIRED, requiresBypass
# Forbidden behavior:
rg -n "solveCaptcha|bypassAttempted: true|residentialProxy|fakeCredential" <scope>
```

## Closeout Requirements

For complex goals, require closeout with:

1. execution units executed;
2. subagents used;
3. commits;
4. material-diff evidence for each material unit;
5. sync status for each unit;
6. files changed;
7. oracles run;
8. failures found and fixed;
9. boundaries preserved;
10. pending owner decisions;
11. final status.

## When Not To Use Subagents

Avoid subagents when:

1. the task is a tiny single-file edit;
2. the next local step depends immediately on the delegated result;
3. the write scope cannot be separated;
4. the work is too ambiguous to delegate safely;
5. delegation would create more integration risk than value;
6. the execution contract requires one material commit at a time and the subagent would need to edit overlapping files in parallel.
