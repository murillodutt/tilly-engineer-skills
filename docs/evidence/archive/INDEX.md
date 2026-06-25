---
tds_id: evidence.archive.index
tds_class: evidence
status: active
consumer: maintainers and evidence auditors
source_of_truth: true
evidence_level: L2
tver: 0.1.0
---

# Evidence Archive

The archive is for cold proof that still has audit value but should not govern current agent behavior.

Monthly indexes should use:

```text
docs/evidence/archive/YYYY-MM.index.json
docs/evidence/archive/YYYY-MM.sha256
```

Each `YYYY-MM.index.json` should use schema `tes-evidence-archive-index@1` and include entries with:

- path
- domain
- run id or report id
- related claim id
- evidence level
- retention status
- version or Git head
- hash

The `.sha256` sidecar hashes the monthly JSON index. It does not replace hashes inside individual manifests, raw traces, reports, or bundle artifacts.
