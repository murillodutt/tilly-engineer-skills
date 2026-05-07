---
tds_id: docs.index
tds_class: index
status: active
consumer: maintainers and agents
source_of_truth: true
evidence_level: L2
tver: 0.4.0
---

# Tilly Engineer Skills Docs

This documentation layer explains the method behind the source package without
turning the repository root into an inventory.

## Map

| Need | Document |
|------|----------|
| Repository shape and ownership | `architecture/PROJECT-STRUCTURE.md` |
| User manual PT/EN/ES | `install/USER-MANUAL.html` |
| Adapter installation | `install/INSTALL.md` |
| Assisted context installer mini prompt | `install/MINI-PROMPT.md` |
| Assisted context installer raw spec | `install/ASSISTED-CONTEXT-INSTALLER.prompt.md` |
| Command trigger matrix | `install/COMMAND-TRIGGERS.md` |
| Assisted installer navigation library | `install/navigation/NAVIGATION-LIBRARY.md` |
| Tool-neutral engineering principles | `mesh/PRINCIPLES.md` |
| Neutral behavioral contract manifest | `mesh/CONTRACT-MANIFEST.yml` |
| Context mesh method | `mesh/CONTEXT-MESH-METHOD.md` |
| Tilly Cortex | `mesh/CORTEX.md` |
| Tilly Cortex MCP | `mesh/CORTEX-MCP.md` |
| Tilly Field Reports | `mesh/FIELD-REPORTS.md` |
| Adoption and convergence scorecard | `mesh/SCORECARD.md` |
| Eval and ablation design | `evals/EVALS.md` |
| Detailed examples | `evals/EXAMPLES.md` |
| Cross-adapter parity gate | `evals/PARITY-GATE.md` |
| Cross-tool agentic governance | `governance/AGENTIC-ALIGNMENT-GOVERNANCE.md` |
| Adapter capability matrix | `adapters/ADAPTER-CAPABILITY-MATRIX.md` |
| Codex adapter guide | `adapters/CODEX.md` |
| Claude adapter guide | `adapters/CLAUDE.md` |
| Cursor adapter guide | `adapters/CURSOR.md` |
| Adapter materialization | `adapters/MATERIALIZATION.md` |
| Codex adapter pipeline | `adapters/pipelines/CODEX-PIPELINE.md` |
| Claude adapter pipeline | `adapters/pipelines/CLAUDE-PIPELINE.md` |
| Cursor adapter pipeline | `adapters/pipelines/CURSOR-PIPELINE.md` |
| Next-session continuity | `roadmap/NEXT-STEPS-LETTER-2026-05-05.md` |
| TDS specification | `tds/TDS-SPEC.md` |
| TDS document index | `tds/DOCS-INDEX.yml` |

## Source Boundary

`docs/**` explains and audits behavior. It is not the installable source.

Copyable adapter material lives in `src/adapters/**`:

| Adapter | Source |
|---------|--------|
| Codex | `../src/adapters/codex/**` |
| Claude | `../src/adapters/claude/**` |
| Cursor | `../src/adapters/cursor/**` |
