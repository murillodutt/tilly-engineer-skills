---
tds_id: evidence.current.claims
tds_class: evidence
status: active
consumer: agents, maintainers, and certification reviewers
source_of_truth: true
evidence_level: L2
tver: 0.1.1
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

## TES Align Semantic Residue Claim

`/tes-align` runs a portable Semantic Residue Gate and freshness
reconciliation before reporting PASS. TES owns the mechanism; the target
project owns the vocabulary via
`docs/agents/contracts/SEMANTIC-RESIDUE.yml`. Malformed contract files
surface as a structured `residue.malformed_contract` finding inside
`semantic_residue.findings`, not only as a prose `failures[]` line.
Freshness reconciliation filters generic ADR section headings through an
internal stopword list to avoid noise on documentary scaffolding.

Proof: `docs/mesh/TES-ALIGN-SEMANTIC-RESIDUE.md`,
`scripts/project_alignment_oracle.py` self-test fixtures (13 total), the
initial certification report at
`docs/evidence/reports/2026/05/25/tes-align/semantic-drift-hardening/REPORT.md`,
and the external-review follow-up packet at
`docs/evidence/reports/2026/05/25/tes-align/external-review-followup/REPORT.md`.

Boundary: certified at the package-source contract level. The originating
target-project canary still owes a real-project rerun against the hardened
oracle.

Retention status: `current`.

## Single-Current-Dist Claim

The TES repository keeps exactly one `docs/dist/<version>/` directory at
any time. `scripts/tes_bundle.py::publish_public_bundle` runs
`prune_historical_dist` after each publish to enforce the policy.
Historical bundles remain reachable via Git tags
(`git checkout v<X> -- docs/dist/<X>`) and via previously published
GitHub Pages release URLs.

Proof: `scripts/tes_bundle.py` (`prune_historical_dist` plus self-test
fixture), `docs/governance/SYNC-AUDIT-CHECKLIST.md` retention step and
matching lock, and the external-review follow-up packet.

Boundary: the policy is enforced on publish. Hand-created
`docs/dist/<other>/` outside the publish flow is pruned on the next
publish; the checklist lock blocks the inverse path.

Retention status: `current`.

## TES Memory Lifecycle ADR Claim

ADR 0001 is implemented at the local package-source contract level through
Wave 7. The implemented lifecycle preserves Markdown as durable truth, events
as evidence, checkpoints as TTL resumability, Field Reports as transport, MCP
as read-only, and subagents as parent-return evidence only.

Proof: `docs/adr/0001-tes-memory-lifecycle.md`,
`docs/roadmap/GOAL-SUPER-SPEC-tes-memory-lifecycle.md`,
`docs/evidence/reports/2026/05/26/memory-lifecycle/wave7-release-canary/REPORT.md`,
and the Wave 1-6 commits named in that report.

Boundary: this is local package-source closure for version `0.3.133`. Remote
release certification, package publish, marketplace action, write-capable MCP,
and commercial-use certification remain outside the claim.

Retention status: `current`.
