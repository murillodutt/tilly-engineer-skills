---
tds_id: roadmap.goal_super_spec.goal_maestro_execution_thermometer.implementation_plan
tds_class: roadmap
status: active
consumer: maintainers, Goal Maestro authors, adapter authors, oracle authors, and execution agents
source_of_truth: true
evidence_level: L2
tver: 0.1.0
---

# Goal Maestro Execution Thermometer: Implementation Plan

This implementation is `Platform` work because it touches delivered Goal Maestro
behavior, report artifacts, helper scripts, adapters, oracles, and release
identity. The runtime path must be added around the existing loop, not inside it
as a second execution engine.

## Boundaries

Preserve:

- explicit Goal Maestro invocation;
- accepted-artifact input gate;
- ordered SPEC execution;
- active-SPEC isolation;
- ledger append behavior;
- pre-edit and post-edit gates;
- material diff and sync discipline;
- final audit;
- existing stop states;
- adapter parity.

Do not introduce:

- telemetry;
- dashboard server;
- database;
- hidden network access;
- alternate ledger format;
- automatic GitHub upload;
- remote write without owner approval.

## Proposed Source Surfaces

Exact paths are implementation decisions, but the expected shape is:

```text
src/**/goal-maestro/
  execution-thermometer/
    schema.*
    extract.*
    render-markdown.*
    render-html.*
    package.*
    gold-gate.*
    sanitize.*
    share-github.*
```

Expected oracles:

```text
scripts/**/validate-execution-thermometer.*
scripts/**/fixtures/execution-thermometer/**
```

Expected delivered behavior:

- schema validation;
- local package generation;
- Markdown renderer;
- HTML renderer;
- Gold Analysis Gate;
- sanitizer;
- GitHub dry-run and draft PR export path if approved.

Every changed `scripts/**` path must be classified before closure:

- maintainer-only validator;
- delivered helper;
- installed-target canary helper;
- release/package helper.

## SPEC-000: Preflight And Baseline

Objective: capture the protected Goal Maestro baseline before any runtime edit.

Inputs:

- current Goal Maestro skill and references;
- adapter materialization status;
- existing execute-loop fixtures/oracles;
- current package identity.

Deliverables:

- baseline note in execution ledger;
- list of protected invariants;
- smallest red-capable oracle selected.

Gate:

- current focused Goal Maestro validation passes before edits.

Stop state:

- `NEEDS_BASELINE_ORACLE`.

## SPEC-001: Data Contract And Schema

Objective: implement schema validation for `exec_identity.yaml` and
`exec_metrics.json`.

Deliverables:

- schema definitions;
- valid fixture;
- invalid fixtures for missing evidence, bad status, bad share state, and
  unreferenced metric.

Gate:

- valid fixture passes;
- invalid fixtures fail with actionable diagnostics.

Stop state:

- `NEEDS_THERMOMETER_SCHEMA`.

## SPEC-002: Ledger Extractor

Objective: normalize existing Goal Maestro loop evidence into the schema without
changing ledger semantics.

Deliverables:

- extractor;
- evidence reference mapping;
- `UNPROVEN` handling for missing fields;
- fixture from a small synthetic loop.

Gate:

- missing metric fixture renders `UNPROVEN`;
- existing loop semantics remain unchanged.

Stop state:

- `NEEDS_LEDGER_EVIDENCE`.

## SPEC-003: Markdown Context Receipt Renderer

Objective: produce the chat context receipt from schema data.

Deliverables:

- Markdown renderer;
- receipt fixture;
- line-width and Markdown-only checks.

Gate:

- receipt includes five signals, objective feedback, next actions, and source
  file references;
- no inline HTML is required.

Stop state:

- `NEEDS_CONTEXT_RECEIPT_RENDERER`.

## SPEC-004: Static HTML Report Renderer

Objective: produce an offline render-only HTML report with accumulated loop
selection.

Deliverables:

- HTML renderer;
- multi-loop fixture;
- selected-loop anchor behavior;
- print-friendly all-loop evidence behavior.

Gate:

- `file://` open works;
- clicking `#loop-L4` loads Loop L4 detail;
- report works without network access.

Stop state:

- `NEEDS_HTML_LOOP_SELECTION`.

## SPEC-005: Gold Analysis Gate

Objective: classify reports as ordinary, useful, or gold.

Deliverables:

- classifier;
- ordinary/useful/gold fixtures;
- reason-code validation;
- evidence requirement.

Gate:

- gold cannot pass without reason code, evidence ref, sanitizer pass, and package
  checksum.

Stop state:

- `NEEDS_GOLD_GATE_EVIDENCE`.

## SPEC-006: Sanitized Package Builder

Objective: build local report packages that are safe to inspect and optionally
share.

Deliverables:

- package builder;
- checksums;
- private vocabulary scan;
- secret/path fixtures.

Gate:

- unsafe fixture is blocked;
- safe fixture produces README, Markdown, YAML, JSON, HTML, and checksums.

Stop state:

- `BLOCKED_BY_SANITIZATION`.

## SPEC-007: Share Gate Prompt And Owner Consent

Objective: ask the owner only when a gold report is sanitized and shareable.

Deliverables:

- consent summary;
- dry-run mode;
- explicit approval boundary;
- decline path.

Gate:

- ordinary report never prompts;
- gold but unsafe report never prompts for remote sharing;
- decline leaves local package intact.

Stop state:

- `NEEDS_OWNER_SHARE_DECISION`.

## SPEC-008: GitHub Draft PR Export

Objective: create a private-review GitHub sharing lane without automatic remote
write.

Deliverables:

- destination config lookup;
- branch/package layout;
- draft PR body summary;
- dry-run evidence.

Gate:

- dry-run shows exact files and destination;
- remote action is blocked without explicit per-run approval.

Stop state:

- `BLOCKED_BY_GITHUB_AUTH` or `NEEDS_GITHUB_DESTINATION`.

## SPEC-009: Goal Maestro Integration

Objective: wire report generation after loop completion or honest stop without
changing execution order.

Deliverables:

- integration hook;
- config flag/default behavior;
- ledger reference;
- backwards compatibility fixture.

Gate:

- existing execute-loop fixture still passes;
- report generation failure does not falsely mark product execution failed unless
  reporting was explicitly required.

Stop state:

- `NEEDS_GOAL_MAESTRO_INTEGRATION`.

## SPEC-010: User Documentation And Manual Boundary

Objective: document the report as a report, not a dashboard or telemetry product.

Deliverables:

- user-facing explanation;
- package field reference;
- sharing consent warning;
- example receipt.

Gate:

- docs describe local-first, opt-in sharing, and `UNPROVEN` semantics.

Stop state:

- `NEEDS_USER_DOCS`.

## SPEC-011: Installed-Target Canary

Objective: prove the package path in a real installed target fixture.

Deliverables:

- canary run;
- generated local package;
- HTML open evidence;
- Markdown receipt evidence.

Gate:

- installed-target canary passes without repository-root assumptions.

Stop state:

- `NEEDS_INSTALLED_CANARY`.

## SPEC-012: Release Identity Decision

Objective: decide and apply package identity changes for delivered behavior.

Deliverables:

- version/bundle decision;
- correlated release surfaces if bumped;
- final focused release gate.

Gate:

- release identity is explicit before closure.

Stop state:

- `NEEDS_RELEASE_IDENTITY_DECISION`.
