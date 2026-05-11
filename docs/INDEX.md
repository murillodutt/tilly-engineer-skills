---
tds_id: docs.index
tds_class: index
status: active
consumer: maintainers and agents
source_of_truth: true
evidence_level: L2
tver: 0.4.5
---

# Tilly Engineer Skills Docs

This documentation layer explains the method behind the source package without
turning the repository root into an inventory.

## Map

| Need | Document |
|------|----------|
| Repository shape and ownership | `architecture/PROJECT-STRUCTURE.md` |
| TES namespace migration catalog | `architecture/TES-NAMING-MIGRATION-CATALOG.md` |
| User manual PT/EN/ES | `install/USER-MANUAL.html` |
| Agent manual | `install/AGENT-MANUAL.md` |
| GitHub Pages landing | `index.html` |
| Live GitHub Pages landing | `https://murillodutt.github.io/tilly-engineer-skills/` |
| Public installer bundle | `dist/0.3.82/tilly-engineer-skills-0.3.82.zip` |
| Adapter installation | `install/INSTALL.md` |
| Assisted context installer mini prompt | `install/MINI-PROMPT.md` |
| Assisted context installer raw spec | `install/ASSISTED-CONTEXT-INSTALLER.prompt.md` |
| Command trigger matrix | `install/COMMAND-TRIGGERS.md` |
| Assisted installer navigation library | `install/navigation/NAVIGATION-LIBRARY.md` |
| Tool-neutral engineering principles | `mesh/PRINCIPLES.md` |
| Neutral behavioral contract manifest | `mesh/CONTRACT-MANIFEST.yml` |
| Context mesh method | `mesh/CONTEXT-MESH-METHOD.md` |
| TES Align skill source of truth | `mesh/TES-ALIGN-SKILL-SOURCE-OF-TRUTH.md` |
| TES Cortex | `mesh/CORTEX.md` |
| TES Cortex MCP | `mesh/CORTEX-MCP.md` |
| TES Field Reports | `mesh/FIELD-REPORTS.md` |
| Tilly Git safety | `mesh/GIT-SAFETY.md` |
| Local quality recipe | `mesh/LOCAL-QUALITY-RECIPE.md` |
| Adoption and convergence scorecard | `mesh/SCORECARD.md` |
| Eval and ablation design | `evals/EVALS.md` |
| Detailed examples | `evals/EXAMPLES.md` |
| Cross-adapter parity gate | `evals/PARITY-GATE.md` |
| Cross-tool agentic governance | `governance/AGENTIC-ALIGNMENT-GOVERNANCE.md` |
| Maintainer correlation rule | `governance/MAINTAINER-CORRELATION-RULE.md` |
| Adapter capability matrix | `adapters/ADAPTER-CAPABILITY-MATRIX.md` |
| Platform differences reference | `adapters/PLATFORM-DIFFERENCES.md` |
| Codex adapter guide | `adapters/CODEX.md` |
| Claude adapter guide | `adapters/CLAUDE.md` |
| Cursor adapter guide | `adapters/CURSOR.md` |
| Adapter materialization | `adapters/MATERIALIZATION.md` |
| Codex adapter pipeline | `adapters/pipelines/CODEX-PIPELINE.md` |
| Claude adapter pipeline | `adapters/pipelines/CLAUDE-PIPELINE.md` |
| Cursor adapter pipeline | `adapters/pipelines/CURSOR-PIPELINE.md` |
| Current roadmap index | `roadmap/README.md` |
| RC1 readiness roadmap | `roadmap/RC1-READINESS-ROADMAP.md` |
| Historical next-session continuity | `roadmap/NEXT-STEPS-LETTER-2026-05-05.md` |
| TDS specification | `tds/TDS-SPEC.md` |
| TDS document index | `tds/DOCS-INDEX.yml` |

## Source Boundary

`docs/**` explains and audits behavior. It is not the installable source.

`docs/tds/DOCS-INDEX.yml` governs Markdown files under `docs/**`. Rendered
HTML surfaces such as `docs/index.html` and `docs/install/USER-MANUAL.html`
remain public documentation entrypoints referenced here and in `README.md`, but
they are not listed as TDS documents because they do not carry Markdown
frontmatter.

Copyable adapter material lives in `src/adapters/**`:

| Adapter | Source |
|---------|--------|
| Codex | `../src/adapters/codex/**` |
| Claude | `../src/adapters/claude/**` |
| Cursor | `../src/adapters/cursor/**` |
