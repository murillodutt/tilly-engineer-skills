---
tds_id: roadmap.goal_super_spec_adr_0005_retention_lane
tds_class: roadmap
status: active
consumer: maintainers, TDS authors, Cortex authors, evidence authors, ADR 0005 operators, and execution agents
source_of_truth: false
evidence_level: L1
---

# GOAL Super SPEC: ADR 0005 Retention Lane

Status: active lane SPEC derived from `docs/adr/0005-asset-transfer-to-existing-surfaces.md`.

Purpose: retain ADR 0005 learning only where it affects existing contracts, evidence, Cortex boundaries, TDS indexes, or contract histories.

## Asset-Transfer Packet

| Field | Value |
|-------|-------|
| `target_asset` | ADRs, TDS index, evidence reports, Cortex apply boundary, contract histories, and retained benchmark artifacts. |
| `current_failure` | TES can retain too much prose, duplicate history, or let retained notes supersede active contracts without evidence. |
| `transferred_behavior` | Keep only decision-grade, proof-backed, or contract-changing learning; use ADRs sparingly and keep Cortex writes governed. |
| `smallest_patch` | Update one index, evidence note, contract history, or Cortex boundary check tied to a material asset change. |
| `proof` | `validate_tds.py`, evidence/index validator, Cortex oracle, private vocabulary oracle, or focused retained-artifact restore check. |
| `regression_surface` | TDS index, evidence interpretation, Cortex write/apply boundary, contract histories, private vocabulary, and release claims. |
| `release_identity` | `MAINTAINER_ONLY` for retained planning/evidence unless public, adapter, or installed behavior changes. |
| `no_new_skill_evidence` | ADRs, TDS, evidence, Cortex, and contract histories already own retention; new retention skills would duplicate governance. |

## SPEC-000: Baseline And Correlation

Tasks:

1. Capture `git status --short --branch --untracked-files=all`.
2. Read ADR 0005, TDS spec, relevant evidence index, Cortex boundary, or contract history.
3. Identify the exact retained learning and the existing surface that owns it.
4. Name whether the change is index-only, evidence-only, contract-history, or behavior-correlated.

Focused oracles:

```bash
python3 scripts/validate_tds.py
python3 scripts/private_vocabulary_oracle.py
python3 scripts/validate_reference_package.py
git diff --check
```

## SPEC-001: Retention Need Test

Tasks:

1. Prove that the learning changes a contract, explains a hard-to-reverse decision, supports evidence, or prevents a repeated failure.
2. If it is only interesting context, keep it out of tracked TES docs.
3. If it belongs to a contract history, update the owning history instead of creating a new document.

## SPEC-002: Existing Asset Patch

Tasks:

1. Patch the smallest retained surface that owns the learning.
2. Keep TDS entries synchronized with frontmatter.
3. Do not let evidence wording override a newer accepted ADR or source of truth.

## SPEC-003: Regression And Release

Tasks:

1. Run TDS validation and private vocabulary checks.
2. Run any Cortex or evidence oracle matching the changed surface.
3. If public, adapter, installed, or release behavior changed, stop for release identity decision.

Valid statuses: `ASSET_TRANSFERRED`, `ASSET_ALREADY_ADEQUATE`, `NEEDS_OWNER_DECISION`, `NEEDS_ASSET_PACKET`, `BLOCKED`.
