---
tds_id: roadmap.goal_super_spec_adr_0005_language_lane
tds_class: roadmap
status: active
consumer: maintainers, Mine authors, Cortex authors, oracle authors, ADR 0005 operators, and execution agents
source_of_truth: false
evidence_level: L1
---

# GOAL Super SPEC: ADR 0005 Language Lane

Status: active lane SPEC derived from `docs/adr/0005-asset-transfer-to-existing-surfaces.md`.

Purpose: transfer shared-language discipline into existing mining, project context, glossary, Cortex, and private-vocabulary assets without turning language capture into memory hoarding.

## Asset-Transfer Packet

| Field | Value |
|-------|-------|
| `target_asset` | `tes-mine/**`, `project_alignment_oracle.py`, `private_vocabulary_oracle.py`, Cortex proposal gates, glossary/context references, and adapter mirrors. |
| `current_failure` | Domain language can remain verbose, contradictory, stale, or over-retained in Cortex instead of becoming precise project vocabulary. |
| `transferred_behavior` | Challenge fuzzy terms, cross-reference code, record only resolved vocabulary or ADR-worthy decisions, and keep implementation detail out of glossary surfaces. |
| `smallest_patch` | Add a negative fixture, oracle assertion, or narrow skill contract line that blocks unresolved or implementation-heavy language capture. |
| `proof` | `project_alignment_oracle.py` self-test, private vocabulary oracle, focused skill parity check, or benchmark fixture for concise language. |
| `regression_surface` | Target-project glossary semantics, Cortex write boundary, private vocabulary safety, adapter mirrors, and installed context expectations. |
| `release_identity` | `DELIVERED_REQUIRES_RELEASE_DECISION` if installed skill or oracle behavior changes; `MAINTAINER_ONLY` for analysis-only fixtures. |
| `no_new_skill_evidence` | `tes-mine`, alignment oracles, and Cortex gates already own language discipline; a new domain-modeling skill would duplicate the lane. |

## SPEC-000: Baseline And Correlation

Tasks:

1. Capture `git status --short --branch --untracked-files=all`.
2. Read ADR 0005, `tes-mine`, glossary/reference formats, and relevant Cortex write-boundary docs.
3. Classify the selected failure as ambiguity, contradiction, stale vocabulary, private vocabulary leakage, or over-retention.
4. Name correlated oracle and adapter surfaces before editing.

Focused oracles:

```bash
python3 scripts/project_alignment_oracle.py --self-test
python3 scripts/private_vocabulary_oracle.py
python3 scripts/validate_reference_package.py
git diff --check
```

## SPEC-001: Language Failure Selection

Tasks:

1. Choose one reproducible language failure.
2. Prove whether the failure belongs in `tes-mine`, a glossary/context oracle, Cortex gating, or the private-vocabulary oracle.
3. Reject any repair that stores unresolved speculation as durable memory.

## SPEC-002: Proof First

Tasks:

1. Add or identify the cheapest assertion that fails when unresolved language is accepted as context.
2. Prefer deterministic oracle fixtures for mechanical language rules.
3. Use benchmark samples only when the behavior depends on judgment or conversational restraint.

## SPEC-003: Existing Asset Patch

Tasks:

1. Patch the selected existing asset and required mirrors only.
2. Keep glossary surfaces free of implementation details.
3. Keep Cortex writes governed and proposal-based unless an existing contract explicitly authorizes durable write.

## SPEC-004: Regression And Release

Tasks:

1. Run the focused proof.
2. Run the smallest package oracle covering the changed surface.
3. If skill, oracle, or installed behavior changed, stop for release identity classification.

Valid statuses: `ASSET_TRANSFERRED`, `ASSET_ALREADY_ADEQUATE`, `NEEDS_OWNER_DECISION`, `NEEDS_ASSET_PACKET`, `BLOCKED`.
