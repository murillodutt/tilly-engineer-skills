---
tds_id: roadmap.goal_prompt_adr_0005_asset_transfer_realignment
tds_class: roadmap
status: active
consumer: maintainers, ADR 0005 operators, and execution agents
source_of_truth: false
evidence_level: L1
tver: 0.2.0
---

# GOAL Prompt: ADR 0005 Asset Transfer Realignment

Generated for
`docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-adr-0005-asset-transfer-realignment.md`.
Paste the prompt below as a `/goal` when executing an ADR 0005 asset-transfer
run.

/goal Execute ADR 0005 Asset Transfer Realignment as a senior, sequential
package-maintainer run.

Primary ADR:
docs/adr/0005-asset-transfer-to-existing-surfaces.md

Main Super SPEC:
docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-adr-0005-asset-transfer-realignment.md

Objective:
Transfer one concrete behavior from the inspected mattpocock/skills operating
pattern into existing TES assets. Do not create new skills, routes, canaries, or
governance documents by default. The run succeeds only when an existing asset is
changed or proven adequate with a focused proof.

Central rule:
No governance-only pass. Every material unit must change or prove an existing
TES asset, or delete/condense a document that was standing in for an asset.

Select exactly one lane unless Murillo explicitly asks for a full sweep:
- Pressure: tes-prospect / tes-mine
- Language: tes-mine / Cortex gates / private-vocabulary oracle
- Slice: tes-goal-maestro / benchmarks/goal-maestro
- Proof: tes-engineering-discipline / discipline_oracle / local quality recipe
- Sanitization: regression guard / reference package checks / route-oracle fixtures
- Routing: COMMAND-TRIGGERS / command_trigger_oracle / adapter routing

Before editing:
1. Run `git status --short --branch --untracked-files=all`.
2. Read AGENTS.md.
3. Read the ADR and Super SPEC above.
4. Declare the selected lane, target asset, current failure, smallest patch,
   proof, regression surface, and release-identity classification.
5. If you cannot name those fields, stop with NEEDS_ASSET_PACKET.

Execution units:

SPEC-000 Baseline And Correlation
- Capture status and correlated files.
- Run:
  - `python3 scripts/validate_tds.py`
  - `python3 scripts/validate_reference_package.py`
  - `git diff --check`

SPEC-001 Asset Failure Selection
- Choose one falsifiable TES failure in the selected lane.
- Prove an existing asset can carry the repair.
- Stop if the first useful move would be a new skill, new command, or new
  governance file.

SPEC-002 Proof First
- Add or identify the cheapest proof that can fail for the selected behavior.
- Prefer deterministic scripts or fixtures for mechanical contracts.
- Use benchmark samples only for judgment, routing, language, restraint, or
  sequencing behavior.

SPEC-003 Existing Asset Patch
- Patch only the selected asset and required correlated surfaces.
- Preserve explicit-invocation contracts unless the owner accepts a contract
  change.
- Do not copy upstream prose or packaging.
- Do not touch public docs, adapters, package version, bundles, tags, pushes, or
  release surfaces without release decision.

SPEC-004 Regression And Release Classification
- Run the focused proof.
- Run the smallest package-level oracle matching the regression surface.
- Use these when relevant:
  - `python3 scripts/validate_reference_package.py`
  - `python3 scripts/command_trigger_oracle.py --self-test`
  - `python3 scripts/platform_surface_oracle.py --self-test`
  - `python3 scripts/private_vocabulary_oracle.py`
  - `git diff --check`
- If delivered behavior changed, stop for release identity unless Murillo
  already authorized the correlated release path.

SPEC-005 Closeout
Return an asset-transfer packet:
- target_asset:
- current_failure:
- transferred_behavior:
- smallest_patch:
- proof:
- regression_surface:
- release_identity:
- no_new_skill_evidence:
- changed_files:
- status:

Valid statuses:
- ASSET_TRANSFERRED
- ASSET_ALREADY_ADEQUATE
- ROUTED_TO_UNIT
- NEEDS_OWNER_DECISION
- NEEDS_ASSET_PACKET
- BLOCKED

Commit strategy:
Commit locally per material unit only after focused proof passes, unless
Murillo says no commit. Never push, tag, publish, or release without explicit
authorization.

Final answer:
State the selected asset, the behavior transferred, the proof run, release
classification, and why no new skill was created.
