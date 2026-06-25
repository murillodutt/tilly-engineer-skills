---
tds_id: tds.spec
tds_class: tds
status: active
consumer: maintainers and agents
source_of_truth: true
evidence_level: L2
tver: 0.2.2
---

# TDS Specification

This project uses a small TDS layer to keep documentation traceable, indexable, and tied to evidence.

TDS in this repository is not a broad knowledge base. It is a control layer for documents that affect agent behavior, package structure, adapter distribution, evaluation, and retained evidence.

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
consumer: user or agent consumer
source_of_truth: true|false
evidence_level: L0|L1|L2|L3|L4
---
```

Use one specific H1 after the frontmatter. Do not create decorative documents. Active source-of-truth documents must also include:

```yaml
tver: 0.1.0
```

`tver` is optional for roadmaps, retained evidence, and other documents that do not define active package behavior or authority.

## Evidence Levels

| Level | Meaning |
|-------|---------|
| `L0` | Conversation or proposal only |
| `L1` | Static source inspection |
| `L2` | Local script, validator, materializer, or package gate |
| `L3` | Cross-tool/runtime validation |
| `L4` | Retained benchmark artifact with reproducible raw evidence |

## Source Of Truth Rules

- `source_of_truth: true` is reserved for documents that define active package behavior or governance.
- Roadmap and proposal documents must use `source_of_truth: false`.
- A document with `status: archived` must remain indexed.
- A new documentation class requires a TDS spec update in the same patch.

## Evidence Retention Semantics

TDS status is intentionally small: `active`, `proposed`, or `archived`. Evidence needs a separate retention meaning so historical proof does not become current truth merely because it is indexed.

The governed policy lives in `docs/evidence/INDEX.md`.

Rules:

- Raw evidence reports and generated traces should use `source_of_truth: false`.
- Current evidence interpretation lives in `docs/evidence/current/**`.
- New generated evidence should default to `docs/evidence/reports/YYYY/MM/DD/<domain>/<run-id>/`.
- Legacy paths such as `docs/evidence/reports/context-mesh/<run-id>/` remain readable retained proof.
- Retention status may be `current`, `retained`, `superseded`, `archived`, or `expired`; map it onto TDS `status` without widening the TDS frontmatter enum.

## Versioning And TVer

Git is the versioning and changelog system for this project.

`package.json` declares the current package baseline. Commits declare semantic history. TDS documents declare current contracts, evidence, proposals, and governed indexes. They must not recreate a parallel changelog, diary, or historical drawer.

Do not add `CHANGELOG.md`. If a release summary is needed later, create a retained evidence report with a clear consumer and point back to the exact Git commit range.

TVer is the lightweight contract version for governed documents. It does not replace Git. It declares which version of a living contract is active.

Rules:

- Active documents with `source_of_truth: true` must carry `tver: x.y.z`.
- Existing active contracts start at `tver: 0.1.0`.
- A material contract change bumps that document's `tver`.
- Roadmaps and retained evidence do not need `tver` unless they become active source-of-truth contracts.
- Evidence documents that support a certification must retain a date, version, hash, run id, Git head, or equivalent reproducibility marker.
- No package, adapter, Cortex, or benchmark certification claim closes without an oracle and a semantic Git commit.

## Index Contract

`docs/tds/DOCS-INDEX.yml` is the governed document registry. It must list every Markdown file under `docs/**`, including this spec and roadmap documents.

The index stores document path, id, class, status, consumer, source-of-truth flag, and evidence level. The validator checks that the index and frontmatter agree.

## Generated Public Surfaces

TDS also governs how public documentation surfaces are projected, even when the rendered output is HTML or another non-Markdown artifact.

```text
The source is the contract.
The rendered document is evidence.
The module graph is the memory.
The generated surface must never become the hidden source.
```

Rules:

- Structured sources own public copy, payloads, links, claims, and i18n text.
- The module graph must name generated outputs and source files.
- The renderer must be deterministic and support a check mode before closure.
- Generated HTML is evidence and review surface, not the edit source.
- Copy-ready payloads must remain canonical source files and be rendered into public surfaces without payload drift.
- Local preview must preserve the hosting base path and expose TDS health, manifest, and check routes when source/render/output alignment is under review.

For TES public docs, the governed projection is:

| Layer | Path |
|-------|------|
| Source | `docs/i18n/tes-public.content.json`, `docs/install/MINI-PROMPT.md` |
| Module graph | `docs/i18n/tes-public.structure.yml` |
| Renderer | `scripts/build_public_docs.py` |
| Generated output | `docs/index.html`, `docs/install/USER-MANUAL.html` |
| Drift oracle | `scripts/tds_surface_oracle.py` |
| Runtime server | `scripts/tds_runtime_server.py` |

## Size And Modularity

Documentation must stay modular enough for people and agents to use without context bloat.

Default rule:

- Markdown and rule documents have a 500-line review limit.
- Crossing the limit requires modularization, not silent growth.
- Runtime prompt specs and generated user manuals may carry explicit local limits when a single-file distribution contract requires it.
- Curation removes or compacts only with visible diff, retained rationale, and authorization. It must not erase evidence lineage.

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

`npm run commit:check` also runs the TDS validator and document-size gate. A documentation change is not ready if a document is missing frontmatter, missing from the index, indexed twice, has a mismatched class/status/source-of-truth flag, or exceeds its size budget without modularization.
