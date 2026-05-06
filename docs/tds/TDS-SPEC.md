---
tds_id: tds.spec
tds_class: tds
status: active
consumer: maintainers and agents
source_of_truth: true
evidence_level: L2
tver: 0.2.0
---

# TDS Specification

This project uses a small TDS layer to keep documentation traceable,
indexable, and tied to evidence.

TDS in this repository is not a broad knowledge base. It is a control layer for
documents that affect agent behavior, package structure, adapter distribution,
evaluation, and retained evidence.

## Document Classes

| Class | Purpose |
|-------|---------|
| `index` | Navigation and governed document registry |
| `architecture` | Repository shape, source ownership, and structural locks |
| `adapter` | Tool-specific source, runtime, and materialization guidance |
| `governance` | Cross-tool authority, alignment gates, and no-go rules |
| `mesh` | Engineering discipline and context-mesh method |
| `eval` | Benchmark design, examples, and measurement rules |
| `evidence` | Retained proof, reports, and reproducible artifacts |
| `roadmap` | Proposed next work, not active contract |
| `tds` | Documentation contract and index rules |

## Required Frontmatter

Every Markdown file under `docs/**` must start with:

```yaml
---
tds_id: stable.identifier
tds_class: index|architecture|adapter|governance|mesh|eval|evidence|roadmap|tds
status: active|proposed|archived
consumer: human or agent consumer
source_of_truth: true|false
evidence_level: L0|L1|L2|L3|L4
---
```

Use one specific H1 after the frontmatter. Do not create decorative documents.
Active source-of-truth documents must also include:

```yaml
tver: 0.1.0
```

`tver` is optional for roadmaps, retained evidence, and other documents that do
not define active package behavior or authority.

## Evidence Levels

| Level | Meaning |
|-------|---------|
| `L0` | Conversation or proposal only |
| `L1` | Static source inspection |
| `L2` | Local script, validator, materializer, or package gate |
| `L3` | Cross-tool/runtime validation |
| `L4` | Retained benchmark artifact with reproducible raw evidence |

## Source Of Truth Rules

- `source_of_truth: true` is reserved for documents that define active package
  behavior or governance.
- Roadmap and proposal documents must use `source_of_truth: false`.
- A document with `status: archived` must remain indexed.
- A new documentation class requires a TDS spec update in the same patch.

## Versioning And TVer

Git is the versioning and changelog system for this project.

`package.json` declares the current package baseline. Commits declare semantic
history. TDS documents declare current contracts, evidence, proposals, and
governed indexes. They must not recreate a parallel changelog, diary, or
historical drawer.

Do not add `CHANGELOG.md`. If a release summary is needed later, create a
retained evidence report with a clear consumer and point back to the exact Git
commit range.

TVer is the lightweight contract version for governed documents. It does not
replace Git. It declares which version of a living contract is active.

Rules:

- Active documents with `source_of_truth: true` must carry `tver: x.y.z`.
- Existing active contracts start at `tver: 0.1.0`.
- A material contract change bumps that document's `tver`.
- Roadmaps and retained evidence do not need `tver` unless they become active
  source-of-truth contracts.
- Evidence documents that support a certification must retain a date, version,
  hash, run id, Git head, or equivalent reproducibility marker.
- No package, adapter, Cortex, or benchmark certification claim closes without
  an oracle and a semantic Git commit.

## Index Contract

`docs/tds/DOCS-INDEX.yml` is the governed document registry. It must list every
Markdown file under `docs/**`, including this spec and roadmap documents.

The index stores document path, id, class, status, consumer, source-of-truth
flag, and evidence level. The validator checks that the index and frontmatter
agree.

## Size And Modularity

Documentation must stay modular enough for humans and agents to use without
context bloat.

Default rule:

- Markdown and rule documents have a 500-line review limit.
- Crossing the limit requires modularization, not silent growth.
- Runtime prompt specs and generated user manuals may carry explicit local
  limits when a single-file distribution contract requires it.
- Curation removes or compacts only with visible diff, retained rationale, and
  authorization. It must not erase evidence lineage.

The local gate is:

```bash
python3 scripts/validate_doc_size.py
```

## Validation

Run:

```bash
npm run tds:validate
npm run docs:size
```

`npm run commit:check` also runs the TDS validator and document-size gate. A
documentation change is not ready if a document is missing frontmatter, missing
from the index, indexed twice, has a mismatched class/status/source-of-truth
flag, or exceeds its size budget without modularization.
