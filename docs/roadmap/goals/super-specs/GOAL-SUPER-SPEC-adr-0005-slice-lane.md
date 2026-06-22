---
tds_id: roadmap.goal_super_spec_adr_0005_slice_lane
tds_class: roadmap
status: active
consumer: maintainers, Goal Maestro authors, benchmark authors, ADR 0005 operators, and execution agents
source_of_truth: false
evidence_level: L1
---

# GOAL Super SPEC: ADR 0005 Slice Lane

Status: active lane SPEC derived from
`docs/adr/0005-asset-transfer-to-existing-surfaces.md`.

Purpose: harden Goal Maestro so mature plans become vertical execution units,
not horizontal packages of documents, scripts, tests, or cleanup.

## Asset-Transfer Packet

| Field | Value |
|-------|-------|
| `target_asset` | `src/adapters/*/skills/tes-goal-maestro/**`, `.agents/skills/tes-goal-maestro/**`, and `benchmarks/goal-maestro/**`. |
| `current_failure` | Goal generation can flatten declared vertical slices or asset-transfer units into horizontal work packages. |
| `transferred_behavior` | Preserve tracer-bullet vertical units: one behavior or asset failure through target asset, smallest patch, proof, regression surface, and closeout. |
| `smallest_patch` | Add or harden a Goal Maestro fixture, quality gate, or materialization-tree rule that rejects horizontal replacement. |
| `proof` | `python3 scripts/context_mesh_plan.py --dataset benchmarks/goal-maestro/eval-dataset.json` or a narrower focused fixture command. |
| `regression_surface` | Goal prompt generation, execution unit fidelity, benchmark expectations, adapter skill mirrors, and closeout vocabulary. |
| `release_identity` | `DELIVERED_REQUIRES_RELEASE_DECISION` for skill behavior changes; `MAINTAINER_ONLY` for benchmark-only hardening. |
| `no_new_skill_evidence` | `tes-goal-maestro` already owns materialization; a new issue-slicing skill would split the same execution contract. |

## SPEC-000: Baseline And Correlation

Tasks:

1. Capture `git status --short --branch --untracked-files=all`.
2. Read ADR 0005, the Goal Maestro skill, materialization-tree reference, and
   existing goal-maestro dataset.
3. Identify whether the failure is missing fixture, weak quality gate, or
   adapter mirror drift.
4. Name correlated Codex, Claude, local `.agents`, benchmark, and package
   validation surfaces before editing.

Focused oracles:

```bash
python3 scripts/context_mesh_plan.py --dataset benchmarks/goal-maestro/eval-dataset.json
python3 scripts/validate_reference_package.py
git diff --check
```

## SPEC-001: Horizontal Rewrite Trap

Tasks:

1. Add or identify a mature artifact that declares vertical slices or
   asset-transfer units.
2. Include an adversarial instruction to rewrite the work as "all docs", "all
   scripts", "all tests", broad cleanup, or equivalent horizontal layer.
3. Require the expected result to preserve vertical unit identity and order.

## SPEC-002: Existing Asset Patch

Tasks:

1. Patch only the relevant Goal Maestro gate, reference, or dataset record.
2. Preserve explicit unit identifiers, order, count, and one-commit-per-unit
   expectations unless the source artifact says otherwise.
3. Do not add a new router, issue workflow, or external tracker dependency.

## SPEC-003: Regression And Release

Tasks:

1. Run the focused Goal Maestro benchmark.
2. Run package validation.
3. If delivered skill behavior changed, stop for release decision before
   claiming the package is sealed.

Valid statuses: `ASSET_TRANSFERRED`, `ASSET_ALREADY_ADEQUATE`,
`NEEDS_OWNER_DECISION`, `NEEDS_ASSET_PACKET`, `BLOCKED`.
