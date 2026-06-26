---
tds_id: docs.index
tds_class: index
status: active
consumer: maintainers and agents
source_of_truth: true
evidence_level: L2
tver: 0.4.18
---

# Tilly Engineer Skills Docs

This documentation layer explains the method behind the source package without turning the repository root into an inventory.

## Map

| Need | Document |
|------|----------|
| Repository shape and ownership | `architecture/PROJECT-STRUCTURE.md` |
| TES namespace migration catalog | `architecture/TES-NAMING-MIGRATION-CATALOG.md` |
| Archived TES Memory Lifecycle ADR | `adr/0001-tes-memory-lifecycle.md` |
| Archived Cortex governed MCP write lane ADR | `adr/0002-cortex-governed-mcp-write-lane.md` |
| Active Cortex MCP capability expansion ADR | `adr/0003-cortex-mcp-capability-expansion.md` |
| Active installed certification and Field Reports intake ADR | `adr/0003-1-installed-certification-and-field-reports-feedback-intake.md` |
| Active TES capsule isolation and reversible installation ADR | `adr/0004-tes-capsule-isolation-and-reversible-installation.md` |
| Active asset transfer to existing TES surfaces ADR | `adr/0005-asset-transfer-to-existing-surfaces.md` |
| Active Goal Maestro decision-lens evolution and self-falsifying ceiling ADR | `adr/0006-decision-lens-evolution-and-routable-gate-closure.md` |
| Active Cortex runtime-first memory and mesh drift ADR | `adr/0007-cortex-proactive-memory-and-mesh-drift.md` |
| User manual PT/EN/ES | `install/USER-MANUAL.html` |
| Agent manual | `install/AGENT-MANUAL.md` |
| Agent oracle inventory | `install/AGENT-ORACLE-INVENTORY.md` |
| GitHub Pages landing | `index.html` |
| Public page i18n source | `i18n/tes-public.content.json` and `i18n/tes-public.structure.yml` |
| Live GitHub Pages landing | `https://murillodutt.github.io/tilly-engineer-skills/` |
| Optional public LLM navigation map | `../llms.txt` and `llms.txt` |
| Public installer bundle | `dist/0.3.202/tilly-engineer-skills-0.3.202.zip` |
| GitHub package-spec installation | `install/INSTALL.md` |
| Install reversibility (detach/uninstall/attach-health) | `install/REVERSIBILITY.md` |
| Command trigger matrix | `install/COMMAND-TRIGGERS.md` |
| Runtime navigation library | `install/navigation/NAVIGATION-LIBRARY.md` |
| Tool-neutral engineering principles | `mesh/PRINCIPLES.md` |
| Maturity Layer Gate evidence | `mesh/MATURITY-LAYER-GATE-EVIDENCE.md` |
| Neutral behavioral contract manifest | `mesh/CONTRACT-MANIFEST.yml` |
| Context mesh method | `mesh/CONTEXT-MESH-METHOD.md` |
| TES Align skill source of truth | `mesh/TES-ALIGN-SKILL-SOURCE-OF-TRUTH.md` |
| TES Align semantic residue gate | `mesh/TES-ALIGN-SEMANTIC-RESIDUE.md` |
| TES Mantra Gate | `mesh/MANTRA-GATE.md` |
| TES Scope Contract | `mesh/SCOPE-CONTRACT.md` |
| TES Event Ledger | `mesh/EVENT-LEDGER.md` |
| TES Checkpoints | `mesh/CHECKPOINTS.md` |
| TES Cortex | `mesh/CORTEX.md` |
| TES Cortex MCP | `mesh/CORTEX-MCP.md` |
| TES Field Reports | `mesh/FIELD-REPORTS.md` |
| Tilly Git safety | `mesh/GIT-SAFETY.md` |
| Local quality recipe | `mesh/LOCAL-QUALITY-RECIPE.md` |
| Adoption and convergence scorecard | `mesh/SCORECARD.md` |
| Eval and ablation design | `evals/EVALS.md` |
| Cortex memory benchmarks | `evals/CORTEX-MEMORY-BENCHMARKS.md` |
| Detailed examples | `evals/EXAMPLES.md` |
| Cross-adapter parity gate | `evals/PARITY-GATE.md` |
| Evidence retention policy | `evidence/INDEX.md` |
| Current evidence claims | `evidence/current/CLAIMS.md` |
| Cross-tool agentic governance | `governance/AGENTIC-ALIGNMENT-GOVERNANCE.md` |
| Maintainer correlation rule | `governance/MAINTAINER-CORRELATION-RULE.md` |
| Sync audit checklist | `governance/SYNC-AUDIT-CHECKLIST.md` |
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
| Cortex MCP Capability Expansion Goal Super SPEC | `roadmap/goals/super-specs/GOAL-SUPER-SPEC-cortex-mcp-capability-expansion.md` |
| Cortex MCP Host Segmentation Goal Super SPEC | `roadmap/goals/super-specs/GOAL-SUPER-SPEC-cortex-mcp-host-segmentation.md` |
| TES Memory Lifecycle Goal Super SPEC | `roadmap/goals/super-specs/GOAL-SUPER-SPEC-tes-memory-lifecycle.md` |
| Cortex Memory Benchmark Harness Goal Super SPEC | `roadmap/goals/super-specs/GOAL-SUPER-SPEC-cortex-memory-benchmark-harness.md` |
| TES Anti-Contamination Hardening Goal Super SPEC | `roadmap/goals/super-specs/GOAL-SUPER-SPEC-tes-anti-contamination-hardening.md` |
| TES Capsule Install And Uninstall Goal Super SPEC | `roadmap/goals/super-specs/GOAL-SUPER-SPEC-tes-capsule-install-and-uninstall.md` |
| TES Attach/Detach And Attach-Health Goal Super SPEC | `roadmap/goals/super-specs/GOAL-SUPER-SPEC-tes-attach-detach-and-attach-health.md` |
| TES Runtime-Surface Attach/Detach Goal Super SPEC | `roadmap/goals/super-specs/GOAL-SUPER-SPEC-tes-runtime-surface-attach-detach.md` |
| TES GPS Capsule Mode Goal Super SPEC | `roadmap/goals/super-specs/GOAL-SUPER-SPEC-tes-gps-capsule-mode.md` |
| TES Bootloader-To-Skill Migration Goal Super SPEC | `roadmap/goals/super-specs/GOAL-SUPER-SPEC-tes-bootloader-skill-migration.md` |
| TES Postinstall And Cortex Curation Hardening Goal Super SPEC | `roadmap/goals/super-specs/GOAL-SUPER-SPEC-tes-postinstall-cortex-hardening.md` |
| TES Postinstall Recovery Contract Symmetry Goal Super SPEC | `roadmap/goals/super-specs/GOAL-SUPER-SPEC-tes-postinstall-recovery-contract-symmetry.md` |
| TES NPX MCP Convergence Goal Super SPEC | `roadmap/goals/super-specs/GOAL-SUPER-SPEC-tes-npx-mcp-convergence.md` |
| TES Installed Certification And Field Reports Hardening Goal Super SPEC | `roadmap/goals/super-specs/GOAL-SUPER-SPEC-tes-installed-certification-and-field-reports-hardening.md` |
| TES Root Context Composition Goal Super SPEC | `roadmap/goals/super-specs/GOAL-SUPER-SPEC-tes-root-context-composition.md` |
| TES Inherited Context Canonical Source Goal Super SPEC | `roadmap/goals/super-specs/GOAL-SUPER-SPEC-tes-inherited-context-canonical-source.md` |
| ADR 0005 asset transfer realignment Goal Super SPEC | `roadmap/goals/super-specs/GOAL-SUPER-SPEC-adr-0005-asset-transfer-realignment.md` |
| Goal Maestro Progressive Disclosure Goal Super SPEC | `roadmap/goals/super-specs/GOAL-SUPER-SPEC-goal-maestro-progressive-disclosure.md` |
| Inherited Context line dashboard | `roadmap/inherited-context/DASHBOARD.md` |
| RC1 readiness roadmap | `roadmap/product/RC1-READINESS-ROADMAP.md` |
| TES Align semantic drift hardening prompt | `roadmap/product/TES-ALIGN-SEMANTIC-DRIFT-HARDENING-SUPER-PROMPT.md` |
| TES skill benchmark convergence roadmap | `roadmap/product/TES-SKILL-BENCHMARK-CONVERGENCE-ROADMAP.md` |
| Flash-Fry skill gap spec | `roadmap/product/FLASH-FRY-SKILL-SPEC.md` |
| Historical next-session continuity | `roadmap/archive/notes/NEXT-STEPS-LETTER-2026-05-05.md` |
| TDS specification | `tds/TDS-SPEC.md` |
| TDS document index | `tds/DOCS-INDEX.yml` |

## Source Boundary

`docs/**` explains and audits behavior. It is not the installable source.

`docs/tds/DOCS-INDEX.yml` governs Markdown files under `docs/**`. Rendered HTML and text surfaces such as `docs/index.html`, `docs/install/USER-MANUAL.html`, and `docs/llms.txt` remain public documentation entrypoints referenced here and in `README.md`, but they are not listed as TDS documents because they do not carry Markdown frontmatter.

`docs/index.html` and `docs/install/USER-MANUAL.html` are rendered public surfaces. Their commercial, documentation, and user-facing text is sourced from `docs/i18n/tes-public.content.json` and structured by `docs/i18n/tes-public.structure.yml`. Use `python3 scripts/build_public_docs.py` to regenerate them and `python3 scripts/build_public_docs.py --check` before closure.

Public surface review follows a source/render/output contract:

```text
The source is the contract.
The rendered document is evidence.
The module graph is the memory.
The generated surface must never become the hidden source.
```

Use `python3 scripts/tds_surface_oracle.py` to check rendered public docs against their structured sources, copy-ready payloads, generated markers, TDS labels, and public source map. Use `python3 scripts/tds_runtime_server.py` for a local GitHub Pages-like runtime with `/_tds/health`, `/_tds/manifest`, and `/_tds/check` endpoints.

Copyable adapter material lives in `src/adapters/**`:

| Adapter | Source |
|---------|--------|
| Codex | `../src/adapters/codex/**` |
| Claude | `../src/adapters/claude/**` |
| Cursor | `../src/adapters/cursor/**` |
