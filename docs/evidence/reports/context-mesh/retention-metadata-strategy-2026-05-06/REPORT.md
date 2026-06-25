---
tds_id: evidence.context_mesh.retention_metadata_strategy_2026_05_06
tds_class: evidence
status: active
consumer: certification reviewers, benchmark maintainers, and evidence auditors
source_of_truth: false
evidence_level: L3
---

# Retention Metadata Strategy - 2026-05-06

## Decision

Historical generated manifests that contain `retention_head=pending` are valid only when they are retained by Git history and explained by a governed evidence report. The manifest is the run artifact; Git is the retention ledger.

New certification reports must either:

- write a final retaining commit/hash when generated after the commit exists;
- or declare the pending retention field and point to the report that resolves it after commit.

## Oracle

```bash
python3 scripts/retention_metadata.py --check
```

The oracle scans `docs/evidence/reports/context-mesh/**/manifest.json`, requires every pending manifest to expose `run_id`, `run_head`, and `gate_head`, and requires the v1 final certification report to explicitly explain the historical `retention_head=pending` state.

## Scope

This closes the metadata-strategy debt from the v1 final certification without rewriting historical generated evidence. Rewriting old manifests would make the evidence look cleaner while weakening lineage.

## No-Claim

This report does not certify new behavior parity. It certifies the retention policy and local checker for already-retained evidence.
