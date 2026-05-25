---
tds_id: docs.index
tds_class: index
status: active
consumer: maintainers and agents
source_of_truth: true
evidence_level: L2
tver: 0.4.11
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
| Agent oracle inventory | `install/AGENT-ORACLE-INVENTORY.md` |
| GitHub Pages landing | `index.html` |
| Public page i18n source | `i18n/tes-public.content.json` and `i18n/tes-public.structure.yml` |
| Live GitHub Pages landing | `https://murillodutt.github.io/tilly-engineer-skills/` |
| Optional public LLM navigation map | `../llms.txt` and `llms.txt` |
| Public installer bundle | `dist/0.3.124/tilly-engineer-skills-0.3.124.zip` |
| GitHub-only npx installation | `install/INSTALL.md` |
| Command trigger matrix | `install/COMMAND-TRIGGERS.md` |
| Runtime navigation library | `install/navigation/NAVIGATION-LIBRARY.md` |
| Tool-neutral engineering principles | `mesh/PRINCIPLES.md` |
| Neutral behavioral contract manifest | `mesh/CONTRACT-MANIFEST.yml` |
| Context mesh method | `mesh/CONTEXT-MESH-METHOD.md` |
| TES Align skill source of truth | `mesh/TES-ALIGN-SKILL-SOURCE-OF-TRUTH.md` |
| TES Align semantic residue gate | `mesh/TES-ALIGN-SEMANTIC-RESIDUE.md` |
| TES Mantra Gate | `mesh/MANTRA-GATE.md` |
| TES Cortex | `mesh/CORTEX.md` |
| TES Cortex MCP | `mesh/CORTEX-MCP.md` |
| TES Field Reports | `mesh/FIELD-REPORTS.md` |
| Tilly Git safety | `mesh/GIT-SAFETY.md` |
| Local quality recipe | `mesh/LOCAL-QUALITY-RECIPE.md` |
| Adoption and convergence scorecard | `mesh/SCORECARD.md` |
| Eval and ablation design | `evals/EVALS.md` |
| Detailed examples | `evals/EXAMPLES.md` |
| Cross-adapter parity gate | `evals/PARITY-GATE.md` |
| Evidence retention policy | `evidence/INDEX.md` |
| Current evidence claims | `evidence/current/CLAIMS.md` |
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
| TES Align semantic drift hardening prompt | `roadmap/TES-ALIGN-SEMANTIC-DRIFT-HARDENING-SUPER-PROMPT.md` |
| Flash-Fry skill gap spec | `roadmap/FLASH-FRY-SKILL-SPEC.md` |
| Historical next-session continuity | `roadmap/NEXT-STEPS-LETTER-2026-05-05.md` |
| TDS specification | `tds/TDS-SPEC.md` |
| TDS document index | `tds/DOCS-INDEX.yml` |

## Source Boundary

`docs/**` explains and audits behavior. It is not the installable source.

`docs/tds/DOCS-INDEX.yml` governs Markdown files under `docs/**`. Rendered
HTML and text surfaces such as `docs/index.html`,
`docs/install/USER-MANUAL.html`, and `docs/llms.txt` remain public
documentation entrypoints referenced here and in `README.md`, but they are not
listed as TDS documents because they do not carry Markdown frontmatter.

`docs/index.html` and `docs/install/USER-MANUAL.html` are rendered public
surfaces. Their commercial, documentation, and user-facing text is sourced from
`docs/i18n/tes-public.content.json` and structured by
`docs/i18n/tes-public.structure.yml`. Use
`python3 scripts/build_public_docs.py` to regenerate them and
`python3 scripts/build_public_docs.py --check` before closure.

Public surface review follows a source/render/output contract:

```text
The source is the contract.
The rendered document is evidence.
The module graph is the memory.
The generated surface must never become the hidden source.
```

Use `python3 scripts/tds_surface_oracle.py` to check rendered public docs
against their structured sources, copy-ready payloads, generated markers, TDS
labels, and public source map. Use `python3 scripts/tds_runtime_server.py` for
a local GitHub Pages-like runtime with `/_tds/health`, `/_tds/manifest`, and
`/_tds/check` endpoints.

Copyable adapter material lives in `src/adapters/**`:

| Adapter | Source |
|---------|--------|
| Codex | `../src/adapters/codex/**` |
| Claude | `../src/adapters/claude/**` |
| Cursor | `../src/adapters/cursor/**` |
