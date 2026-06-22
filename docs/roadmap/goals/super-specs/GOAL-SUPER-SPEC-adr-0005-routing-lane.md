---
tds_id: roadmap.goal_super_spec_adr_0005_routing_lane
tds_class: roadmap
status: active
consumer: maintainers, route authors, installer authors, adapter authors, ADR 0005 operators, and execution agents
source_of_truth: false
evidence_level: L1
---

# GOAL Super SPEC: ADR 0005 Routing Lane

Status: active lane SPEC derived from
`docs/adr/0005-asset-transfer-to-existing-surfaces.md`.

Purpose: make TES routing lighter and clearer through existing command trigger,
doctor, map, installer, and adapter surfaces without adding a router skill.

## Asset-Transfer Packet

| Field | Value |
|-------|-------|
| `target_asset` | `docs/install/COMMAND-TRIGGERS.md`, `command_trigger_oracle.py`, installed adapter routing, doctor/map surfaces, and platform-surface checks. |
| `current_failure` | Routing can expose inventory instead of next action, auto-fire explicit skills, or hide platform-specific surface risk. |
| `transferred_behavior` | Route to the smallest existing flow, keep explicit skills explicit, and show the next useful action without broad inventory. |
| `smallest_patch` | Add a route oracle fixture, clarify one trigger row, or repair one adapter routing rule. |
| `proof` | `command_trigger_oracle.py --self-test`, `platform_surface_oracle.py --self-test`, install smoke, or adapter materialization check. |
| `regression_surface` | Command trigger docs, installed bootloaders, adapter source/materialized parity, installer behavior, and platform routing. |
| `release_identity` | `DELIVERED_REQUIRES_RELEASE_DECISION` for any installed route or adapter behavior change. |
| `no_new_skill_evidence` | Current trigger, doctor, map, and platform surfaces must fail a deletion test before a new router exists. |

## SPEC-000: Baseline And Correlation

Tasks:

1. Capture `git status --short --branch --untracked-files=all`.
2. Read ADR 0005, command triggers, relevant adapter route source, and platform
   surface rules.
3. Classify the failure as over-routing, under-routing, explicit-invocation
   breach, platform mismatch, or stale trigger copy.
4. Name correlated install, adapter, generated, and public surfaces before
   editing.

Focused oracles:

```bash
python3 scripts/command_trigger_oracle.py --self-test
python3 scripts/platform_surface_oracle.py --self-test
python3 scripts/validate_reference_package.py
git diff --check
```

## SPEC-001: Route Failure Fixture

Tasks:

1. Add or identify a route case where the correct answer is one next flow, not
   a command inventory.
2. Include an explicit-invocation trap when relevant.
3. Require the expected result to preserve platform boundaries.

## SPEC-002: Existing Asset Patch

Tasks:

1. Patch the smallest trigger row, oracle assertion, adapter route, or platform
   check needed to make the route behavior correct.
2. Do not add a router skill, command alias, or setup workflow.
3. Preserve explicit-invocation contracts unless the owner accepts a contract
   change.

## SPEC-003: Regression And Release

Tasks:

1. Run route and platform focused oracles.
2. Run package validation.
3. If installed adapter or trigger behavior changed, stop for release identity
   decision.

Valid statuses: `ASSET_TRANSFERRED`, `ASSET_ALREADY_ADEQUATE`,
`NEEDS_OWNER_DECISION`, `NEEDS_ASSET_PACKET`, `BLOCKED`.
