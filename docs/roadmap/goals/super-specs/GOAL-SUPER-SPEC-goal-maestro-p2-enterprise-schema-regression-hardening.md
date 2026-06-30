---
tds_id: roadmap.goal_super_spec.goal_maestro_p2_enterprise_schema_regression_hardening
tds_class: roadmap
status: active
consumer: maintainers, Goal Maestro authors, adapter authors, schema authors, oracle authors, release reviewers, and installed-canary operators
source_of_truth: true
evidence_level: L2
tver: 0.1.0
---

# GOAL-SUPER-SPEC: Goal Maestro P2 Enterprise Schema And Regression Hardening

Status: active corrective Super SPEC.

Purpose: after P0 blocks false closure and P1 standardizes cross-host feedback,
promote the repaired Goal Maestro feedback line into durable enterprise-grade
schemas, fixtures, stop states, and anti-contamination boundaries.

This is the third of three linked corrective Super SPECs. It carries exactly
four slices: SPEC-031 through SPEC-034.

## Dependency

P2 must not start before P0 and P1 have converged. If either is open, stop with
`NEEDS_P0_P1_FEEDBACK_CONVERGENCE`.

## Central Rule

```text
Real validation evidence teaches the TES harness through generic fixtures and
schemas; it must not become product-specific harness behavior.
```

## Stop States

- `NEEDS_FORMAL_ARTIFACT_SCHEMAS`
- `NEEDS_REAL_REGRESSION_FIXTURES`
- `NEEDS_STOP_STATE_COVERAGE`
- `NEEDS_ANTI_CONTAMINATION_BOUNDARY`
- `PASS_P2_ENTERPRISE_SCHEMA_REGRESSION_HARDENING`

## Execution Slices

### SPEC-031 - Formal Artifact Schemas

Goal: make new P0/P1 artifacts stable and machine-checkable.

Required behavior:

- Add formal schemas for:
  - `pre_edit_gate`;
  - `prompt_enrichment_packet`;
  - `document_analysis_packet`;
  - `visual_evidence_packet`;
  - `browser_metrics`;
  - `install_chronology`;
  - `commit_enforcement`;
  - `lens_ledger`;
  - `cloud_search_classification`;
  - `thermometer_execution_metrics`.
- Schemas must distinguish `missing`, `not_required`, `blocked`, `unproven`,
  and `pass`.
- Schema validation must run in source and installed-target contexts.

Acceptance:

- Missing required P0/P1 fields fail schema validation.
- Unknown fields that could hide false confidence fail unless explicitly allowed
  as extension metadata.
- Stop state: `NEEDS_FORMAL_ARTIFACT_SCHEMAS`.

### SPEC-032 - Real Regression Fixtures

Goal: preserve every observed canary failure as a failing fixture.

Required behavior:

- Add fixtures for:
  - missing material SPEC replaced by audit row;
  - `SPEC-UNKNOWN`;
  - initial-state-only visual evidence falsely marked as active-state proof;
  - install after material commits;
  - manual commits reported as hook-enforced;
  - missing Flash-Fry status hidden by protection score;
  - missing cloud-search classification;
  - absent heartbeat sidecar with heartbeat option present;
  - scheduled wakeup or host job without authorization.
- Fixtures must fail before the corresponding repair and pass after repair.

Acceptance:

- Fixture suite is red-capable and wired into the focused Goal Maestro gate.
- No fixture contains project-specific product nouns as required harness
  vocabulary.
- Stop state: `NEEDS_REAL_REGRESSION_FIXTURES`.

### SPEC-033 - Stop State Coverage

Goal: make every known failure close with a specific state.

Required behavior:

- Add and document stop states introduced by P0/P1.
- Ensure Goal Maestro chooses the most specific state before generic
  `SPEC_BLOCKED` or `SAFETY_BLOCKED`.
- Thermometer report states remain separate from Goal Maestro execution states.
- Heartbeat report states remain separate from both.

Acceptance:

- Fixture failures map to the intended stop state.
- A generic stop state for a specific known failure fails.
- Stop state: `NEEDS_STOP_STATE_COVERAGE`.

### SPEC-034 - Anti-Contamination Boundary

Goal: prevent any validation prompt from becoming the harness contract.

Required behavior:

- All repaired contracts use generic artifact classes: rendered surface, UI,
  runtime, report, installed target, evidence packet, and execution unit.
- Validation-target-specific product names stay only in evidence fixtures or
  retained validation reports.
- Public docs and adapter contracts describe generic behavior.
- The next validation run may repeat the same external prompt unchanged, but the
  harness must not contain that prompt as a special case.

Acceptance:

- Private or validation-target-specific product vocabulary in delivered harness
  contracts fails.
- Generic fixtures derived from validation evidence pass without embedding
  validation-target nouns in runtime behavior.
- Stop state: `NEEDS_ANTI_CONTAMINATION_BOUNDARY`.

## Required P2 Oracles

- Schema validation suite for all new artifact contracts.
- Regression fixture suite using real failure classes.
- Stop-state routing oracle.
- Anti-contamination vocabulary oracle.
- Adapter materialization and installed-target canary proof after source repair.

## Done Means

P2 is complete only when P0/P1 behavior is protected by formal schemas, real
regression fixtures, specific stop states, anti-contamination checks, adapter
materialization proof, and a repeated unchanged canary run that cannot pass by
harness-external output quality alone.
