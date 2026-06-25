---
tds_id: evidence.current.risks
tds_class: evidence
status: active
consumer: agents, maintainers, and evidence auditors
source_of_truth: true
evidence_level: L2
tver: 0.1.1
---

# Current Evidence Risks

## Legacy Status Ambiguity

Many historical reports still carry TDS `status: active` because TDS currently uses a small status vocabulary. Treat those reports as retained proof when `source_of_truth: false` is present and no current claim links them as present truth.

Mitigation: use the semantic retention statuses in `docs/evidence/INDEX.md`.

## Incremental Adoption

The repository intentionally does not move all historical evidence into the temporal layout in one patch.

Mitigation: future writers use temporal paths, while readers continue accepting legacy paths.

## Archive Materialization

The archive contract exists before monthly archive indexes are generated.

Mitigation: create `YYYY-MM.index.json` and `YYYY-MM.sha256` only when evidence is actually archived, then keep the index addressable by date, domain, hash, related claim, and retention status.

## Remote Release Certification Deferred

The memory lifecycle implementation is closed at local package-source level, but no tag, push, package publish, marketplace action, or fixed public release ref was authorized for this loop.

Mitigation: do not run or claim `npm run release:check` until the matching remote release action is explicitly authorized. Until then, treat `0.3.133` as locally bundled and source-certified, not remotely release-certified.

## Canary Scope Limit

Wave 7 used one disposable real-project canary with neutral tracked evidence. That supports local closure and drift screening, but it is not enough for a commercial-use or broad cross-project claim.

Mitigation: require two additional real-project canary replays before making any commercial-use claim from this ADR implementation.
