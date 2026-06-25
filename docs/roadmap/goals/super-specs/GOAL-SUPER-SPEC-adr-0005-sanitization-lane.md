---
tds_id: roadmap.goal_super_spec_adr_0005_sanitization_lane
tds_class: roadmap
status: active
consumer: maintainers, regression-guard authors, oracle authors, route authors, ADR 0005 operators, and execution agents
source_of_truth: false
evidence_level: L1
---

# GOAL Super SPEC: ADR 0005 Sanitization Lane

Status: active lane SPEC derived from `docs/adr/0005-asset-transfer-to-existing-surfaces.md`.

Purpose: transfer architecture-cleanup behavior into existing TES regression, route, oracle, and surface-review assets using deletion tests rather than new governance.

## Asset-Transfer Packet

| Field | Value |
|-------|-------|
| `target_asset` | Regression guard, reference package checks, route/oracle fixtures, duplicated pass-through docs, and adapter materialization checks. |
| `current_failure` | TES can accumulate shallow pass-through documents, route aliases, fixtures, or helper surfaces that add inventory without leverage. |
| `transferred_behavior` | Apply a deletion test: if removing a surface deletes complexity, condense or delete it; if complexity spreads to callers, deepen the owning asset. |
| `smallest_patch` | Add a deletion-test fixture, condense one pass-through surface, or deepen one existing owner asset with proof. |
| `proof` | `validate_reference_package.py`, focused route/oracle self-test, materialization check, or explicit `NO_CHANGE` evidence. |
| `regression_surface` | Installed adapters, generated outputs, route maps, reference package paths, oracles, and public docs when touched. |
| `release_identity` | `DELIVERED_REQUIRES_RELEASE_DECISION` for installed/public/adapter changes; `MAINTAINER_ONLY` for local guard or fixture-only changes. |
| `no_new_skill_evidence` | Regression guard and existing validators already own cleanup pressure; a new architecture skill is invalid until deletion tests prove no owner asset can carry it. |

## SPEC-000: Baseline And Correlation

Tasks:

1. Capture `git status --short --branch --untracked-files=all`.
2. Read ADR 0005, regression guard, relevant route/oracle docs, and the target surface under review.
3. Select exactly one suspected shallow surface.
4. Name every correlated installed, generated, adapter, route, and public surface before editing.

Focused oracles:

```bash
python3 scripts/validate_reference_package.py
python3 scripts/command_trigger_oracle.py --self-test
python3 scripts/platform_surface_oracle.py --self-test
git diff --check
```

## SPEC-001: Deletion Test

Tasks:

1. Simulate or inspect what happens if the suspected surface disappears.
2. Classify the result as `NO_CHANGE`, `CONDENSED`, `MOVED_ON_DEMAND`, `DEEPENED`, `DELETED`, `ROUTED_TO_UNIT`, or `NEEDS_OWNER_DECISION`.
3. Stop if the surface touches release, installer, public, or adapter behavior and no release identity can be named.

## SPEC-002: Existing Asset Patch

Tasks:

1. Apply the smallest change matching the deletion-test result.
2. Prefer moving detail on demand, condensing duplicated prose, or deepening the real owner over adding a new governance document.
3. Do not delete compatibility or release paths without retirement evidence.

## SPEC-003: Regression And Release

Tasks:

1. Run the focused proof matching the changed surface.
2. Run package validation and any materialization or public-doc oracle affected by the patch.
3. If delivered behavior changed, stop for release decision.

Valid statuses: `ASSET_TRANSFERRED`, `ASSET_ALREADY_ADEQUATE`, `ROUTED_TO_UNIT`, `NEEDS_OWNER_DECISION`, `NEEDS_ASSET_PACKET`, `BLOCKED`.
