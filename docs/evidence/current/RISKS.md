---
tds_id: evidence.current.risks
tds_class: evidence
status: active
consumer: agents, maintainers, and evidence auditors
source_of_truth: true
evidence_level: L2
tver: 0.1.0
---

# Current Evidence Risks

## Legacy Status Ambiguity

Many historical reports still carry TDS `status: active` because TDS currently
uses a small status vocabulary. Treat those reports as retained proof when
`source_of_truth: false` is present and no current claim links them as present
truth.

Mitigation: use the semantic retention statuses in `docs/evidence/INDEX.md`.

## Incremental Adoption

The repository intentionally does not move all historical evidence into the
temporal layout in one patch.

Mitigation: future writers use temporal paths, while readers continue accepting
legacy paths.

## Archive Materialization

The archive contract exists before monthly archive indexes are generated.

Mitigation: create `YYYY-MM.index.json` and `YYYY-MM.sha256` only when evidence
is actually archived, then keep the index addressable by date, domain, hash,
related claim, and retention status.
