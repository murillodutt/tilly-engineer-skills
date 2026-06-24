# Subagents And Oracles

Use this reference when a materialization tree or `/goal` prompt needs
specialized ownership, review loops or stronger verification.

## Subagent Rules

Only include subagents when the user asks for delegation, the work is complex,
or parallel independent ownership materially improves execution.

When included:

1. give each subagent a concrete ownership scope;
2. keep write scopes disjoint;
3. tell workers they are not alone in the codebase;
4. keep reviewer read-only;
5. keep evidence/oracle tracking separate from implementation;
6. avoid assigning the immediate blocking task to a subagent;
7. for strict commit-per-unit queues, prefer centralized material edits and
   read-only reviewer/oracle subagents unless write scopes are genuinely
   disjoint;
8. when write subagents are used in a strict sequence, name the serialized
   integration point and require the parent executor to certify one unit before
   the next starts;
9. close subagents after their bounded task is complete.

For `--execute-loop`, use one fresh worker subagent per `ACTIVE_SPEC`. The
parent sends the full prompt plus a hard active-SPEC envelope, validates commit
and oracle evidence, then closes the worker. Workers may propose next-prompt
material but cannot generate the authoritative next prompt or execute the next
SPEC. If worker capacity is unavailable after closing completed or degraded
workers, the parent must either execute under the same `ACTIVE_SPEC` envelope
only when the current request explicitly authorized parent-side loop execution
with the exact `--execute-loop-parent-fallback` flag, or stop with
`NEEDS_OWNER_DECISION`.

When a worker touches code, UI, runtime scripts or generated app artifacts, the
hard envelope must include `STRUCTURAL_METHOD=<profile-id>`, file topology
budget, allowed new modules/internal sections, structural debt budget,
structural source probes and structural handoff requirements. The worker must
classify failed attempts with `bug_vs_architecture` before another attempt can
start.

Reference implementations, prior manual builds, browser smoke results, run
records and post-facto audits are reviewer inputs only. They are baseline-only
comparison evidence and never replace a fresh worker, strict sequential replay
or per-`ACTIVE_SPEC` commit evidence.

## Reusable Roles

### Contracts Senior

Owns schemas, types, fixtures and contract tests.

Use when the slice creates or changes canonical artifacts, DTOs, validation
rules or fixture matrices.

### Runtime Senior

Owns runtime modules and integration boundaries.

Use when the slice implements behavior after contracts are established.

### Visual-Runtime Senior

Owns browser automation, rendered evidence, browser metrics, runtime-smoke
artifacts and visual-spatial certification.

Use when the slice touches UI, game, canvas, WebGL/WebGPU, Three.js, render,
layout, spawn, raycast, camera framing, browser runtime or integration wiring.

### Tests Senior

Owns focused tests, adversarial cases, fixtures and regression selection.

Use when behavior must be certified before broader gates.

### Reviewer Senior

Read-only.

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
11. prior commits or closeouts being treated as execution credit without
    explicit authorization;
12. lexical negative greps that confuse valid blocked-state vocabulary with
    forbidden executable behavior;
13. `--execute-loop` workers touching files outside `ACTIVE_SPEC`, skipping
    local commit evidence, pushing remotely, bypassing loop-state evidence,
    starting another attempt with unresolved failed-attempt residue, missing a
    required persistent ledger, using parent-side execution fallback without
    explicit authorization, using cloud escalation without owner-approved
    redaction, crediting a reference implementation or post-facto audit as loop
    execution, skipping `STRUCTURAL_METHOD=<profile-id>` envelope fields,
    missing structural source probes, omitting structural handoff, retrying a
    coding SPEC without `bug_vs_architecture`, expanding audit repairs without
    new material evidence, missing required browser metrics or visual-spatial
    evidence for app/UI/game work, or bypassing Executive Stop Audit.

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

Owns authorization boundaries, sensitive data handling, secrets avoidance,
unsafe access checks and negative grep for safety leakage.

Use when the task touches external access, secrets, auth, privacy, production,
destructive commands or public surfaces.

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
15. visual-spatial screenshot or pixel/legibility audit when layout, render,
    spawn, raycast, canvas, 3D placement or visual state can fail despite green
    logic;
16. source-derived contract handoff and API lint when workers reuse existing
    APIs;
17. final status report.

## Integration Runtime-Smoke Oracle

When a unit connects modules into an executable runtime path, build and
typecheck are not enough. Use `references/runtime-certification.md` as the
owner of this contract.

The oracle must instantiate the real wiring module, stub only external
browser/GPU/network/clock boundaries, run deterministic ticks or calls, and
assert state movement, no fatal runtime failure, and at least one cross-module
effect.

## Browser Metrics Contract

For browser-certified apps, UI tools, games or generated app artifacts, do not
rely only on `window` globals or prose. Produce a stable machine-readable
artifact when browser certification is part of the closeout.

`references/runtime-certification.md` owns required-axis completion. This
section records the artifact shape for prompt writers.

Default artifact:

```text
browser-metrics.json
```

Minimum fields:

```json
{
  "status": "PASS|DEGRADED|BLOCKED",
  "consoleErrors": [],
  "runtime": {},
  "visual": {},
  "domainMetrics": {},
  "failures": []
}
```

Use domain-specific fields under `domainMetrics`; do not force every canary or
app to share the same game-specific keys. Parent reviewers must parse the
artifact by contract before trusting a worker closeout.

## Visual-Spatial Oracle

When a failure can be visual or spatial, logic checks are necessary but not
sufficient. Require screenshot, pixel, canvas, bounding-box, accessibility tree
or equivalent rendered evidence when the active SPEC touches:

- canvas, WebGL, Three.js, maps or 3D scenes;
- spawn position, raycast, collision, block/grid alignment or camera framing;
- responsive layout, text fit, modal position or critical UI visibility;
- generated images, visual assets or rendered public docs.

If visual-spatial evidence is impossible in the environment, record the exact
browser/render attempt and command output. For required axes, a blocked or
degraded visual result routes to `VISUAL_CERT_BLOCKED` or `AXIS_UNPROVEN`; it
does not satisfy `EXECUTION_LOOP_COMPLETE`.

## Negative Grep Patterns

Use task-specific forbidden words and APIs. Common categories:

1. hidden network execution;
2. unauthorized storage writes;
3. public-surface exports;
4. forbidden providers;
5. secrets or tokens;
6. raw payload export;
7. final interpretation leakage;
8. bypass or destructive operations.

Example shape:

```text
rg -n "fetch|getFetcher|service\\.run" <scope>
rg -n "rawPayloadExported: true|finalInterpretationExported: true" <scope>
rg -n "password|token|secret|privateKey" <scope>
```

When a term is valid as a blocked-state enum, reason code or policy field, do
not use a broad lexical grep that treats the vocabulary itself as a violation.
Write checks that separate allowed vocabulary from forbidden behavior.

Example:

```text
# Allowed as policy vocabulary:
# BLOCKED_BYPASS_REQUIRED, requiresBypass, bypassRequired

# Forbidden as behavior:
rg -n "solveCaptcha|captchaSolver|bypassAttempted: true|residentialProxy|fakeCredential" <scope>
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
6. the execution contract requires one material commit at a time and the
   subagent would need to edit overlapping files in parallel.
