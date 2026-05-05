---
tds_id: tds.spec
tds_class: tds
status: active
consumer: maintainers and agents
source_of_truth: true
evidence_level: L2
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

## Versioning And Changelog

Git is the versioning and changelog system for this project.

`package.json` declares the current package baseline. Commits declare semantic
history. TDS documents declare current contracts, evidence, proposals, and
governed indexes. They must not recreate a parallel changelog, diary, or
historical drawer.

Do not add `CHANGELOG.md`. If a release summary is needed later, create a
retained evidence report with a clear consumer and point back to the exact Git
commit range.

## Index Contract

`docs/tds/DOCS-INDEX.yml` is the governed document registry. It must list every
Markdown file under `docs/**`, including this spec and roadmap documents.

The index stores document path, id, class, status, consumer, source-of-truth
flag, and evidence level. The validator checks that the index and frontmatter
agree.

## Validation

Run:

```bash
npm run tds:validate
```

`npm run commit:check` also runs the TDS validator. A documentation change is
not ready if a document is missing frontmatter, missing from the index, indexed
twice, or has a mismatched class/status/source-of-truth flag.
