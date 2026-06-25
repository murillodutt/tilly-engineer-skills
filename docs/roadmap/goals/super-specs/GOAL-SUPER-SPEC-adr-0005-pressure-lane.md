---
tds_id: roadmap.goal_super_spec_adr_0005_pressure_lane
tds_class: roadmap
status: active
consumer: maintainers, Prospect/Mine authors, benchmark authors, ADR 0005 operators, and execution agents
source_of_truth: false
evidence_level: L1
---

# GOAL Super SPEC: ADR 0005 Pressure Lane

Status: active lane SPEC derived from `docs/adr/0005-asset-transfer-to-existing-surfaces.md`.

Purpose: transfer the external relentless-interview behavior into existing TES pressure assets without creating a new skill or command.

## Asset-Transfer Packet

| Field | Value |
|-------|-------|
| `target_asset` | `src/adapters/*/skills/tes-prospect/**`, `src/adapters/*/skills/tes-mine/**`, matching `.agents/skills/**` mirrors, and pressure fixtures or benchmarks. |
| `current_failure` | Pressure can degrade into broad planning, multiple questions, or user questions that repository evidence could answer. |
| `transferred_behavior` | One decision branch at a time, one question at a time, with a recommended answer and codebase-before-question discipline. |
| `smallest_patch` | Harden the existing skill contract or focused fixture that catches pressure drift. |
| `proof` | Focused skill text oracle, benchmark fixture, or self-test that fails on multi-question, passive, or evidence-ignoring output. |
| `regression_surface` | Skill trigger semantics, explicit invocation, cognitive brake, adapter mirrors, and benchmark expectations. |
| `release_identity` | `DELIVERED_REQUIRES_RELEASE_DECISION` if adapter skill behavior changes; otherwise `MAINTAINER_ONLY` for benchmarks only. |
| `no_new_skill_evidence` | `tes-prospect` and `tes-mine` already own pressure and mining; a new grill-style skill would duplicate invocation surface. |

## SPEC-000: Baseline And Correlation

Tasks:

1. Capture `git status --short --branch --untracked-files=all`.
2. Read ADR 0005, the parent ADR 0005 Super SPEC, `tes-prospect`, and `tes-mine`.
3. Name whether the selected patch is skill behavior, benchmark behavior, or mirror parity only.
4. List correlated Codex, Claude, local `.agents`, benchmark, and package validation surfaces before editing.

Focused oracles:

```bash
python3 scripts/validate_reference_package.py
python3 scripts/command_trigger_oracle.py --self-test
git diff --check
```

## SPEC-001: Pressure Drift Fixture

Tasks:

1. Add or identify one fixture where the prompt tempts the agent to ask several questions, skip the recommended answer, or ask what the repo can answer.
2. Require the expected behavior to answer with exactly one next pressure question and one recommended answer.
3. Preserve the cognitive brake as a stop condition.

Stop if the fixture would require a new user-invoked skill.

## SPEC-002: Existing Asset Patch

Tasks:

1. Patch only the smallest pressure contract text, reference, or benchmark expectation needed to make the fixture pass.
2. Keep `tes-prospect` and `tes-mine` explicit-invocation only.
3. Do not copy external skill names, command names, setup workflow, or issue tracker assumptions.

## SPEC-003: Regression And Release

Tasks:

1. Run the focused fixture or benchmark.
2. Run package validation and command-trigger validation.
3. If any adapter skill text changed, stop with release identity classified as `DELIVERED_REQUIRES_RELEASE_DECISION`.

Valid statuses: `ASSET_TRANSFERRED`, `ASSET_ALREADY_ADEQUATE`, `NEEDS_OWNER_DECISION`, `NEEDS_ASSET_PACKET`, `BLOCKED`.
