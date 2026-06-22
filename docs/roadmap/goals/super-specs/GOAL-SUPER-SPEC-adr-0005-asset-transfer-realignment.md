---
tds_id: roadmap.goal_super_spec_adr_0005_asset_transfer_realignment
tds_class: roadmap
status: active
consumer: maintainers, skill authors, oracle authors, benchmark authors, ADR 0005 operators, and execution agents
source_of_truth: false
evidence_level: L1
tver: 0.2.0
---

# GOAL Super SPEC: ADR 0005 Asset Transfer Realignment

Status: active execution contract derived from
`docs/adr/0005-asset-transfer-to-existing-surfaces.md`.

Purpose: transfer the useful operating behavior from the inspected
`mattpocock/skills` pattern into existing TES assets: skills, references,
scripts, hooks, agents, benchmarks, routes, and adapter source. This Super SPEC
does not authorize creating new TES skills by default.

## Central Rule

No governance-only pass. Each implementation unit must either change or prove an
existing TES asset, or delete/condense a document that was standing in for an
asset.

## Non-Objectives

- Do not copy upstream skill text, packaging, issue-tracker workflow, command
  names, or private assumptions.
- Do not add a new `/tes-*` command.
- Do not create a new skill unless a deletion test proves no existing asset can
  carry the behavior.
- Do not run private canaries or write private target details into TES source.
- Do not change public docs, adapters, package version, bundle, tag, push, or
  release unless the selected asset patch is classified as delivered behavior
  and the owner authorizes the correlated release path.

## Asset-Transfer Packet

Every material unit must close with:

| Field | Requirement |
|-------|-------------|
| `target_asset` | Existing file or file family changed or certified. |
| `current_failure` | Falsifiable weakness being repaired. |
| `transferred_behavior` | Generic behavior absorbed from the external pattern. |
| `smallest_patch` | Minimal asset edit or proof addition. |
| `proof` | Focused command, fixture, benchmark, or self-test. |
| `regression_surface` | Source, installed, generated, adapter, hook, or public surface at risk. |
| `release_identity` | `MAINTAINER_ONLY`, `DELIVERED_NO_VERSION`, `DELIVERED_REQUIRES_RELEASE_DECISION`, or `NEEDS_OWNER_DECISION`. |
| `no_new_skill_evidence` | Why the existing asset can carry the behavior. |

If a unit cannot fill the packet, stop as `NEEDS_ASSET_PACKET`.

## Candidate Asset Lanes

Select the smallest lane that matches the observed failure. Do not execute all
lanes in one run unless the owner explicitly asks for a full sweep.

| Lane | Primary assets | Intended repair |
|------|----------------|-----------------|
| Pressure | `src/adapters/*/skills/tes-prospect/**`, `tes-mine/**` | One-branch questioning, codebase-before-question, cognitive brake proof. |
| Language | `tes-mine/**`, Cortex gates, private-vocabulary oracle | Concise glossary/ADR discipline without Cortex over-retention. |
| Slice | `tes-goal-maestro/**`, `benchmarks/goal-maestro/**` | Reject horizontal units; preserve vertical proof and execution-unit fidelity. |
| Proof | `tes-engineering-discipline/**`, `discipline_oracle.py`, local quality recipe | Require red-capable proof before implementation closeout. |
| Sanitization | regression guard, reference package checks, route/oracle fixtures | Apply deletion test and condense pass-through surfaces. |
| Routing | `COMMAND-TRIGGERS.md`, `command_trigger_oracle.py`, adapter route surfaces | Show next flow without exposing inventory or auto-firing explicit skills. |

## Implementation Units

Run units sequentially for the selected lane.

### SPEC-000: Baseline And Correlation

Tasks:

1. Capture `git status --short --branch --untracked-files=all`.
2. Read ADR 0005 and this Super SPEC.
3. Identify the selected asset lane and classify whether it is maintainer-only
   or delivered behavior.
4. Name correlated files before editing.

Focused oracles:

```bash
python3 scripts/validate_tds.py
python3 scripts/validate_reference_package.py
git diff --check
```

### SPEC-001: Asset Failure Selection

Tasks:

1. Choose one current TES failure from the selected lane.
2. Prove why the failure belongs in an existing asset.
3. Fill `target_asset`, `current_failure`, `transferred_behavior`,
   `smallest_patch`, and `no_new_skill_evidence` before editing.

Stop if the first useful action would be a new skill, new command, or new
governance file.

### SPEC-002: Proof First

Tasks:

1. Add or identify the cheapest proof that can fail for the selected failure.
2. Prefer deterministic scripts and fixture checks for mechanical contracts.
3. Use benchmarks only when the behavior depends on judgment, routing,
   language, restraint, or sequencing.

Acceptable outputs: focused self-test, dataset fixture, benchmark sample,
oracle assertion, hook check, or documented `NO_CHANGE` with evidence.

### SPEC-003: Existing Asset Patch

Tasks:

1. Patch only the selected existing asset and required correlated surfaces.
2. Keep explicit-invocation skills explicit.
3. Move detail on demand before adding root or route prose.
4. If architecture bloat is found, apply the deletion test and choose one
   result: `NO_CHANGE`, `CONDENSED`, `MOVED_ON_DEMAND`, `DEEPENED`, `DELETED`,
   `ROUTED_TO_UNIT`, or `NEEDS_OWNER_DECISION`.

Forbidden: broad refactor, drive-by cleanup, copied upstream prose, public docs
or adapter changes without release classification.

### SPEC-004: Regression And Release Classification

Tasks:

1. Run the focused proof from SPEC-002.
2. Run the smallest package-level oracle that covers the regression surface.
3. Classify release identity.
4. If delivered behavior changed, stop for release decision unless the owner
   already authorized the correlated release path.

Recommended oracle set by surface:

```bash
python3 scripts/validate_reference_package.py
python3 scripts/command_trigger_oracle.py --self-test
python3 scripts/platform_surface_oracle.py --self-test
python3 scripts/private_vocabulary_oracle.py
git diff --check
```

### SPEC-005: Closeout

Tasks:

1. Produce the asset-transfer packet.
2. Name changed files and proof run.
3. State whether a new skill was avoided and why.
4. State next unit only if another concrete asset failure remains.

Valid final statuses:

| Status | Meaning |
|--------|---------|
| `ASSET_TRANSFERRED` | Existing asset changed, focused proof passed, release classification complete. |
| `ASSET_ALREADY_ADEQUATE` | Existing asset passed deletion/proof review; no edit needed. |
| `ROUTED_TO_UNIT` | A larger repair needs a separate vertical unit. |
| `NEEDS_OWNER_DECISION` | Release identity, public behavior, or explicit invocation would move. |
| `NEEDS_ASSET_PACKET` | Required packet fields are missing. |
| `BLOCKED` | Required proof or source inspection failed outside this run. |

## Closure Rule

The closeout must not say ADR 0005 is implemented because these documents
exist. ADR 0005 is implemented only when an existing TES asset is improved or
proven adequate with the packet above.
