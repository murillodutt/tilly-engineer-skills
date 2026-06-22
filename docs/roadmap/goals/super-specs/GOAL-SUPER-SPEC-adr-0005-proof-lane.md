---
tds_id: roadmap.goal_super_spec_adr_0005_proof_lane
tds_class: roadmap
status: active
consumer: maintainers, engineering-discipline authors, oracle authors, benchmark authors, ADR 0005 operators, and execution agents
source_of_truth: false
evidence_level: L1
---

# GOAL Super SPEC: ADR 0005 Proof Lane

Status: active lane SPEC derived from
`docs/adr/0005-asset-transfer-to-existing-surfaces.md`.

Purpose: harden TES proof discipline so green gates must be red-capable for the
specific behavior being changed.

## Asset-Transfer Packet

| Field | Value |
|-------|-------|
| `target_asset` | `tes-engineering-discipline/**`, `discipline_oracle.py`, `docs/mesh/LOCAL-QUALITY-RECIPE.md`, focused fixtures, and adapter mirrors. |
| `current_failure` | A closure can cite a passing gate that is not able to catch the exact behavior regression being claimed. |
| `transferred_behavior` | One red-capable proof per material slice, through public or declared interfaces, before implementation closeout. |
| `smallest_patch` | Add a discipline rule, oracle plan check, or quality recipe assertion that distinguishes "runs green" from "could fail on this behavior." |
| `proof` | `discipline_oracle.py --self-test`, a focused plan-check fixture, local quality recipe validation, or benchmark sample for proof quality. |
| `regression_surface` | Engineering discipline skill, oracle grammar, quality recipe, adapter mirrors, and maintainer closeout behavior. |
| `release_identity` | `DELIVERED_REQUIRES_RELEASE_DECISION` if adopter-visible discipline changes; `MAINTAINER_ONLY` for source-only fixture exploration. |
| `no_new_skill_evidence` | `tes-engineering-discipline` already owns proof and closeout; a separate TDD skill would duplicate the proof contract. |

## SPEC-000: Baseline And Correlation

Tasks:

1. Capture `git status --short --branch --untracked-files=all`.
2. Read ADR 0005, `tes-engineering-discipline`, its oracle, and the local
   quality recipe.
3. Identify whether the failure is proof semantics, oracle grammar, quality
   routing, or closeout wording.
4. Name correlated Codex, Claude, local `.agents`, oracle, docs, and package
   validation surfaces before editing.

Focused oracles:

```bash
python3 src/adapters/codex/skills/tes-engineering-discipline/scripts/discipline_oracle.py --self-test
python3 scripts/validate_reference_package.py
python3 scripts/validate_tds.py
git diff --check
```

## SPEC-001: Red-Capable Fixture

Tasks:

1. Add or identify a plan/check fixture where the proposed oracle is broad but
   cannot catch the named behavior regression.
2. Require the expected result to stop as insufficient proof or bind to a
   behavior-specific oracle.
3. Ensure the fixture permits legitimate broad gates only after a focused proof
   exists.

## SPEC-002: Existing Asset Patch

Tasks:

1. Patch the smallest discipline text, oracle check, or recipe line needed to
   enforce red-capable proof.
2. Keep tests and checks behavior-facing; do not require implementation-detail
   mocks or private-method checks as the default.
3. Avoid adding a generic test framework, strategy interface, or new command.

## SPEC-003: Regression And Release

Tasks:

1. Run the discipline focused proof.
2. Run TDS validation if documentation changed and package validation if skill
   or oracle behavior changed.
3. If adopter-visible discipline changed, stop for release identity
   classification.

Valid statuses: `ASSET_TRANSFERRED`, `ASSET_ALREADY_ADEQUATE`,
`NEEDS_OWNER_DECISION`, `NEEDS_ASSET_PACKET`, `BLOCKED`.
