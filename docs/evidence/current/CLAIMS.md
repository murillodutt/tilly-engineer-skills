---
tds_id: evidence.current.claims
tds_class: evidence
status: active
consumer: agents, maintainers, and certification reviewers
source_of_truth: true
evidence_level: L2
tver: 0.1.0
---

# Current Evidence Claims

## Retention Policy Claim

TES evidence is governed by three layers: `current`, temporal `reports`, and
`archive`.

Proof: `docs/evidence/INDEX.md`.

Boundary: this claim governs evidence organization. It does not certify any
adapter behavior by itself.

Retention status: `current`.

## Writer Path Claim

New context mesh runs default to
`docs/evidence/reports/YYYY/MM/DD/context-mesh/<run-id>/` when no explicit
`--out-root` is provided.

Proof: `scripts/context_mesh_run.py` and `docs/evals/EVALS.md`.

Boundary: callers may still provide a custom output root, including the legacy
`docs/evidence/reports/context-mesh` layout.

Retention status: `current`.

## Legacy Compatibility Claim

Historical context mesh evidence under
`docs/evidence/reports/context-mesh/<run-id>/` remains readable and retained.

Proof: `scripts/context_mesh_convergence.py`,
`scripts/retention_metadata.py`, and existing TDS index entries.

Boundary: legacy evidence is retained proof. It is not a current operational
claim unless linked from this directory or another active claim document.

Retention status: `current`.
