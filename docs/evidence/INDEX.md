---
tds_id: evidence.index
tds_class: evidence
status: active
consumer: maintainers, evidence producers, and agents
source_of_truth: true
evidence_level: L2
tver: 0.1.0
---

# Evidence Retention Policy

Evidence is retained proof. It is not operational truth by itself.

Operational truth lives in small current claims with explicit limits and links to proof. Raw traces, reports, and historical audit material support those claims, but they do not govern the present merely because they still exist.

## Layers

| Layer | Path | Role |
|-------|------|------|
| Current | `docs/evidence/current/` | Small claim and risk panel for what is currently asserted. |
| Reports | `docs/evidence/reports/YYYY/MM/DD/<domain>/<run-id>/` | Default home for new generated evidence runs. |
| Archive | `docs/evidence/archive/` | Cold audit indexes for retained proof that should stay addressable but inactive. |

New evidence must be born under `docs/evidence/reports/YYYY/MM/DD/<domain>/<run-id>/` unless a caller provides an explicit external or legacy output root. The context mesh domain is `context-mesh`.

The legacy layout `docs/evidence/reports/context-mesh/<run-id>/` remains readable and indexable. Do not migrate historical evidence in bulk unless a separate migration plan proves the move is safe, reversible, and worth the review noise.

## Retention Status

TDS frontmatter currently supports `status: active|proposed|archived`. Evidence needs a second semantic layer so retained proof does not masquerade as current truth.

| Retention status | Meaning | TDS compatibility |
|------------------|---------|-------------------|
| `current` | Supports a claim in `docs/evidence/current/**`. | Usually `status: active`; claim panels may use `source_of_truth: true`. |
| `retained` | Preserved proof with audit value, but not a current claim. | May remain `status: active` for index compatibility; must use `source_of_truth: false`. |
| `superseded` | Preserved proof replaced by newer evidence or a narrower claim. | May remain `status: active` or move to `archived`; must use `source_of_truth: false`. |
| `archived` | Cold proof kept for audit, no longer part of current operating context. | Use `status: archived` when the Markdown report itself is archived. |
| `expired` | Proof no longer supports any claim and has no active audit role. | Use `status: archived` before any removal decision; raw evidence is not deleted by default. |

Generated evidence reports and raw traces should normally declare or be treated as `source_of_truth: false`. The current claim panel may be `source_of_truth: true` because it defines the present interpretation, not because it stores raw proof.

## Current Contract

`docs/evidence/current/INDEX.md` is the agent-readable entrypoint.

`docs/evidence/current/CLAIMS.md` lists current evidence-backed claims. Each claim must stay small and name its proof, boundary, and retention status.

`docs/evidence/current/RISKS.md` lists known limits, stale-evidence hazards, and migration risks. It is the place to explain why a retained report is not a current claim.

Do not place `raw.ndjson`, large report bodies, benchmark matrices, or audit logs under `current/**`.

## Report Contract

Generated run directories should use this shape:

```text
docs/evidence/reports/YYYY/MM/DD/<domain>/<run-id>/
  REPORT.md
  manifest.json
  raw.ndjson
  summary.json
  graders-sha.json
```

Reports under `docs/**` must remain TDS-indexed when they are Markdown. The generated `REPORT.md` must retain reproducibility fields such as run id, Git HEAD, dataset hash, grader hash, backend, model, and evidence limits when those fields apply.

## Archive Contract

Archive indexes are monthly, addressable, and hashable:

```text
docs/evidence/archive/
  INDEX.md
  YYYY-MM.index.json
  YYYY-MM.sha256
```

Each monthly index should identify entries by date, domain, version or Git head, related claim, hash, path, evidence level, and retention status. Archive indexes do not replace raw evidence; they make cold proof discoverable without promoting it back into current context.

## Compatibility

Legacy evidence under `docs/evidence/reports/context-mesh/<run-id>/` remains valid retained proof. Existing claims and reports must not be rewritten simply to fit the temporal layout.

Readers should accept both temporal and legacy paths. Writers should default to the temporal path unless a caller explicitly asks for another output root.
