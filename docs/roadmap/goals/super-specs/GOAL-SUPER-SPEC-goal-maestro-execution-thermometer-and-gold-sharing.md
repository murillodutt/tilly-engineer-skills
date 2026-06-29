---
tds_id: roadmap.goal_super_spec.goal_maestro_execution_thermometer_gold_sharing
tds_class: roadmap
status: active
consumer: maintainers, Goal Maestro authors, report renderer authors, oracle authors, GitHub workflow reviewers, and execution agents
source_of_truth: true
evidence_level: L2
tver: 0.1.0
---

# GOAL-SUPER-SPEC: Goal Maestro Execution Thermometer And Gold Sharing

Status: active pre-implementation project SPEC.

Purpose: add an opt-in post-execution reporting layer to
`tes-goal-maestro --execute-loop` without changing the loop semantics that make
Goal Maestro valuable. The project turns loop evidence into a concise Markdown
context receipt, a static offline HTML report, and a sanitized YAML plus JSON
evidence package that can be shared through an explicit GitHub draft PR only
after a local gold gate and owner approval.

This is not a prompt-vs-prompt benchmark. It is an execution thermometer: it
shows whether the harness executed well, where proof was strong or weak, what
the lenses changed, what Flash-Fry prevented, what cache/context reuse saved,
and which SPECs carried risk, rework, or missing evidence.

## Anchor And Origin

```text
anchor_class=owner-directed-product-project
anchor_path=docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-goal-maestro-execution-thermometer-and-gold-sharing.md
anchor_hash=<git hash-object captured by the execution loop before implementation>
anchor_origin=materialized-from-owner-direction
anchor_source=current owner direction, 2026-06-29
```

Production users reported the same gap: the product outcome is visible, but the
quality of the harness execution is not. The user sees the delivered backend or
frontend, but not whether the execution line was efficient, evidence-backed,
protected, and worth sharing back to improve TES.

## Central Rule

```text
The thermometer reports execution evidence; it does not manufacture confidence.
Every metric is either backed by a cited artifact or marked UNPROVEN.
```

## Project Pack

This Super SPEC is intentionally thin. The complete project contract is split
across governed references so implementation can advance SPEC by SPEC without a
large roadmap document becoming the operational surface.

| Surface | Authority |
|---------|-----------|
| `goal-maestro-execution-thermometer/EXPERIENCE-AND-DATA-CONTRACT.md` | Markdown receipt, static HTML behavior, package layout, YAML identity, JSON metrics schema |
| `goal-maestro-execution-thermometer/METRICS-GATES-AND-SHARING.md` | Five signals, lens/Flash-Fry/cache/SPEC metrics, Gold Analysis Gate, Share Gate, GitHub sharing policy |
| `goal-maestro-execution-thermometer/IMPLEMENTATION-PLAN.md` | Platform boundaries, source surfaces, execution units, script classification, integration sequence |
| `goal-maestro-execution-thermometer/VALIDATION-AND-CLOSEOUT.md` | Stop states, privacy gates, validation plan, acceptance criteria, final closeout contract |

## Product Shape

The project delivers two user-facing reports and one optional evidence package:

1. `context-receipt.md` appears in the chat context window and shows only the
   five most important execution signals.
2. `execution-thermometer.html` is a static render-only report. It opens offline,
   reads normalized data generated from YAML plus JSON, and lets the user click a
   loop row such as `#loop-L4` to load that loop's detail area.
3. `execution-thermometer-<run-id>/` packages the Markdown, HTML, YAML, JSON,
   README, and checksums for local review or opt-in sharing.

The HTML report is not a dashboard. There is no server, database, background
collector, telemetry stream, or live analytics surface. The report is an
artifact, not an application.

## Five User Signals

The chat receipt must stay simple and objective:

| Signal | Question answered |
|--------|-------------------|
| Delivery | Did the loop deliver the intended outcome on time? |
| Fidelity | Did execution follow the accepted SPEC order without silent skip or scope drift? |
| Proof | Were the required oracles, evidence, runtime checks, and citations present? |
| Efficiency | Was the loop economical in attempts, rework, tokens, cache, and time where proven? |
| Protection | Did Flash-Fry, lenses, sanitization, and gates prevent unsafe or weak execution? |

The HTML report may expose the full 20-point execution X-ray, but the chat
receipt stays intentionally compact: five signals, objective feedback, run
context, next actions, and source package references.

## Non-Objectives

- Do not compare Goal Maestro against prompt-by-prompt execution.
- Do not create a dashboard, hosted collector, SaaS integration, or telemetry
  pathway.
- Do not send data automatically.
- Do not include raw prompts, raw diffs, secrets, private paths, private project
  names, or unreviewed logs in a shareable package.
- Do not paste the package into GitHub issue bodies, comments, or public Gists.
- Do not make HTML the source of truth. YAML plus JSON are the data contract;
  Markdown and HTML are renderers.
- Do not alter `tes-goal-maestro --execute-loop` sequencing, commit rhythm,
  active-SPEC isolation, or stop-state semantics.

## Protected Baseline

The implementation protects the current Goal Maestro harness:

- explicit invocation only;
- mature SPEC input gate;
- one active SPEC at a time;
- append-only execution ledger behavior;
- pre-edit and post-edit gates;
- Flash-Fry early analysis;
- decision lens and structural-method enforcement;
- material diff and sync discipline;
- honest stop states;
- adapter parity across delivered hosts;
- no remote action without explicit owner approval.

Any runtime implementation of this project is `Platform` from the first changed
line because it touches delivered Goal Maestro behavior, reports, helpers,
oracles, package identity, and possibly GitHub export flow.

## Report Lifecycle

```text
Goal Maestro loop evidence
  -> extractor
  -> exec_identity.yaml + exec_metrics.json
  -> Markdown context receipt
  -> static HTML report
  -> checksummed local package
  -> Gold Analysis Gate
  -> sanitizer
  -> explicit owner prompt
  -> optional GitHub draft PR
```

If any required evidence is missing, the report still renders, but the affected
metric is marked `UNPROVEN`. Missing evidence is not hidden and does not silently
become a zero, pass, or inferred estimate.

## GitHub Sharing Decision

GitHub is the preferred sharing lane because it preserves review, branch,
history, and owner control. The remote action is never automatic.

The share flow is allowed only when all are true:

1. local Gold Analysis Gate returns `gold`;
2. sanitizer passes;
3. the owner sees the package summary and destination;
4. the owner explicitly approves the remote action for that run;
5. the export opens a draft PR, not a direct merge.

The default shared payload is sanitized `exec_identity.yaml`,
`exec_metrics.json`, and `checksums.sha256`. Markdown and HTML are local package
artifacts unless the owner explicitly allows them for the configured repository.

## Implementation Rule

Build this as a narrow extension around the existing loop evidence path. The
right implementation reads ledger/evidence already produced by Goal Maestro,
normalizes it, renders reports, and packages outputs. It must not introduce a
parallel execution engine, a second ledger format, or a broad analytics runtime.

## High-Level SPEC Partition

| SPEC | Scope | Gate |
|------|-------|------|
| SPEC-000 | Baseline and host contract capture | Current Goal Maestro checks pass before edits |
| SPEC-001 | YAML/JSON schema and fixtures | Schema fixtures validate, bad fixtures fail |
| SPEC-002 | Ledger extractor | Missing evidence becomes `UNPROVEN` |
| SPEC-003 | Markdown receipt renderer | Five-signal receipt renders in Markdown only |
| SPEC-004 | Static HTML renderer | Offline report and loop links work |
| SPEC-005 | Gold Analysis Gate | Ordinary/useful/gold fixtures classify correctly |
| SPEC-006 | Sanitized package builder | Secrets/private vocabulary fixtures are blocked |
| SPEC-007 | Share Gate consent prompt | No prompt unless gold and sanitized |
| SPEC-008 | GitHub draft PR export | Dry-run first; remote only after explicit approval |
| SPEC-009 | Goal Maestro integration | Loop semantics unchanged |
| SPEC-010 | User docs | Report behavior documented without dashboard drift |
| SPEC-011 | Installed-target canary | Real target package path proven |
| SPEC-012 | Release identity | Version/bundle decision made before closure |

## Owner Decisions Before Runtime Implementation

1. Default local package directory under installed target projects.
2. Whether Markdown and HTML may ever be included in a GitHub share payload.
3. Default private GitHub repository or project-level destination config.
4. Whether repeated gold reports should prompt every time or be rate-limited.
5. Whether cost fields are required in v1 or allowed as `UNPROVEN`.
6. Whether this ships inside `tes-goal-maestro` or as a helper invoked by it.

## Done Means

The project is complete only when a Goal Maestro loop can generate the Markdown
receipt, the static HTML report, a checksummed local package, gold classification,
sanitization evidence, and an explicit opt-in GitHub draft PR path while proving
that existing Goal Maestro execution behavior did not regress.

## Do Not Lose

The Execution Thermometer exists to make Goal Maestro observable without
weakening Goal Maestro. A beautiful report that hides unproven metrics is a
regression. A GitHub upload without explicit approval is a safety failure. A
score that rewards lower cost while proof weakens is false confidence.
