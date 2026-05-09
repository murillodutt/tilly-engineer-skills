---
tds_id: mesh.tes_align_skill_source_of_truth
tds_class: mesh
status: active
consumer: maintainers and `/tes-align` skill authors
source_of_truth: true
evidence_level: L1
tver: 0.2.1
sources_verified_on: 2026-05-09
source_refresh_interval_days: 15
source_refresh_policy: >-
  If this document is accessed after a cycle of 15 days or more since
  sources_verified_on, verify the listed sources first, update this document if
  the sources changed, and only then use it as construction truth.
sources:
  - "docs/install/COMMAND-TRIGGERS.md"
  - "docs/mesh/CONTEXT-MESH-METHOD.md"
  - "docs/mesh/CONTEXT-MESH-CONVERGENCE.md"
  - "https://github.com/obsidianmd/obsidian-help"
  - "https://obsidian.md/help/bases"
  - "https://obsidian.md/help/properties"
  - "https://obsidian.md/help/links"
  - "https://obsidian.md/help/plugins/graph"
  - "https://obsidian.md/help/plugins/canvas"
  - "https://obsidian.md/help/cli"
---

# TES Align Skill Source Of Truth

This document is the source of truth for the `/tes-align` skill.

It defines what the skill must preserve, which failure modes it must prevent,
and how the project operating mesh should remain usable in Obsidian without
making Obsidian the source of truth.

## Thesis

`/tes-init` makes a project visible to TES. `/tes-align` must make the project
operationally legible.

The skill exists to perform semantic project alignment after initial context
creation:

```text
initial context -> semantic alignment -> operating mesh -> execution line
```

The outcome is not prettier documentation. The outcome is that a future agent
can enter the project, understand what already exists, what is in motion, what
must not be rebuilt, which gates prove quality, and which line of work should
advance next.

## Role Boundary

| Surface | Role |
|---------|------|
| `/tes-init` | Install, update, create the initial `docs/agents/PROJECT-CONTEXT.md` project map, and create a first-pass operating mesh when missing. |
| `/tes-align` | Refine the first-pass mesh into a deeper project operating system with roadmap, state, execution line, constraints, terms, decisions, and quality gates. |
| `/tes-doctor` | Health-check and certify installed TES surfaces and project gates. |
| `/tes-cortex` | Recall, curate, learn, and reflect from the continuity layer. |
| `/tes-field-reports` | Capture sanitized operational feedback outside project truth. |
| Build-Test-Fail-Fix loops | Prove product behavior with real failures, fixes, retests, and portable learning. |

`/tes-align` must not become a second installer, release gate, or generic
maestro. It is a specialist that turns observed project evidence into a deeper
actionable operating mesh. The first `/tes-init` execution may create the
minimum Obsidian-compatible mesh to reduce friction; `/tes-align` owns semantic
refinement, existing-doc reconciliation, and roadmap/execution-line maturity.

## Operating Mesh Contract

The target project should end with a coherent `docs/agents/**` layer. The
exact files depend on what the project already owns.

Default generated or updated surfaces:

| Surface | Purpose |
|---------|---------|
| `docs/agents/PROJECT-CONTEXT.md` | Refined project identity, architecture, territories, anchors, scripts, gaps, and next-work guidance. |
| `docs/agents/PROJECT-STATE.md` | Current state: done, active, blocked, deferred, and uncertain. |
| `docs/agents/PROJECT-ROADMAP.md` | Evidence-based roadmap that emphasizes what remains to build, not what already exists. |
| `docs/agents/EXECUTION-LINE.md` | The agreed work lane: sequence, gates, handoff rules, and restart protocol. |
| `docs/agents/QUALITY-GATES.md` | Project-specific commands, acceptance gates, risk gates, and certification semantics. |
| `docs/agents/BOUNDARIES-AND-CONSTRAINTS.md` | Safety, ownership, no-go surfaces, protected files, and mutation limits. |
| `docs/agents/KNOWLEDGE-LIFECYCLE.md` | How context is created, validated, refreshed, retired, and contradicted. |
| `docs/agents/GLOSSARY.md` | Ubiquitous language, domain terms, aliases, and overloaded terms. |
| `docs/agents/DECISIONS/` | ADR-style decision records or links to the project's existing decision system. |
| `docs/agents/evidence/<timestamp>-project-alignment.md` | Retained alignment packet with anchors read, changes made, gaps, and certification. |

These are canonical names for TES-generated target-project meshes, not a blind
creation requirement. If equivalent project-owned docs already exist, the skill
must link and align them instead of duplicating them.

## Existing-Doc Classification

Before writing any project operating mesh file, `/tes-align` must classify
existing documentation and governance.

| Status | Meaning | Action |
|--------|---------|--------|
| `present` | The expected surface exists and is current enough to use. | Preserve and link. |
| `linked_existing` | The project has an equivalent under another path. | Reference it from `docs/agents/**`; do not duplicate. |
| `created` | No equivalent exists and the project needs the surface. | Create the minimal useful file. |
| `needs_update` | The surface exists but conflicts with current evidence. | Patch with citations and keep contradictions visible. |
| `contradictory` | Two sources disagree materially. | Record the tension and request or derive resolution from evidence. |
| `deferred` | Useful, but not required for the current alignment pass. | Record as future work. |
| `not_applicable` | The surface does not fit the project. | Record why; do not create filler. |

The skill must discover before it writes. It must not create a new roadmap,
ADR folder, safety policy, or glossary just because the template contains one.

## Discovery Anchors

For a non-trivial project, `/tes-align` must read strong anchors before
claiming semantic alignment.

Required anchor classes:

| Anchor class | Examples |
|--------------|----------|
| Identity | `README`, package metadata, app manifests, public docs, project description. |
| Structure | source tree, packages, apps, services, modules, examples, generated assets. |
| Build and gates | package scripts, CI, test configs, lint/typecheck/build commands, release scripts. |
| Architecture | existing architecture docs, design docs, ADRs, API contracts, schemas. |
| Governance | `AGENTS.md`, `CLAUDE.md`, Cursor rules, `.github/**`, security, contributing, CODEOWNERS. |
| History | recent Git commits, existing roadmap, issue/PR references when locally available. |
| Risk | secrets policy, destructive commands, external systems, deployment surfaces, data boundaries. |

If a project is sparse, `/tes-align` must say so plainly and avoid inventing
architecture. Sparse projects can still pass when the roadmap and state explain
what is unknown.

## Obsidian-Native Design

Obsidian is the preferred visualization layer for the project operating mesh.
Markdown and Git remain the source of truth.

Design rules:

1. Use portable Markdown files as the authority.
2. Use YAML frontmatter as Obsidian Properties, not hidden metadata.
3. Use wikilinks for project-local relationships when they improve navigation.
4. Keep hub documents small enough for humans and agents to scan.
5. Treat Graph view as a navigation signal for hubs, orphans, and relation
   density.
6. Treat Bases as an optional view layer over Markdown properties, not as the
   only record of project state.
7. Treat Canvas as an optional visual synthesis layer; important cards should
   resolve back to Markdown files.
8. Do not write `.obsidian/**`.
9. Do not require Obsidian plugins for the mesh to work.
10. Do not let `.canvas`, `.base`, or visual views become the only source of a
    claim, decision, risk, or roadmap item.

Suggested frontmatter for target-project mesh documents:

```yaml
---
tes_doc: project-state
status: active
owner: project
updated: YYYY-MM-DD
confidence: high|medium|low
evidence:
  - path: README.md
  - path: package.json
tags:
  - tes
  - project-state
related:
  - "[[PROJECT-CONTEXT]]"
---
```

The exact keys may evolve, but the intent must hold: make the mesh queryable,
linkable, and Git-readable without binding TES to an Obsidian runtime.

## Roadmap Semantics

`PROJECT-ROADMAP.md` must reduce confusion, not create ambition theater.

It must separate:

| Category | Meaning |
|----------|---------|
| `Done` | Already implemented and evidenced. |
| `Active` | Currently in motion or the next intended lane. |
| `Next` | Sequenced work with concrete gates. |
| `Later` | Real but not yet scheduled. |
| `Deferred` | Intentionally postponed, with reason. |
| `Blocked` | Cannot proceed until a named dependency resolves. |
| `Unknown` | Evidence is insufficient; do not invent. |

The roadmap must not ask agents to rebuild what already exists. If the project
has a previous roadmap, `/tes-align` must compare against it and mark stale,
done, superseded, or still-active items.

## Execution Line Semantics

`EXECUTION-LINE.md` is the project lane. It should tell the next agent how to
restart work without rediscovering the whole repository.

It must include:

1. Current mission or active lane.
2. Entry anchors to read first.
3. Expected Build-Test-Fail-Fix loop.
4. Quality gates before closure.
5. Commit, push, release, and external-mutation rules.
6. Reentry packet shape for the next session.
7. Stop conditions.

The execution line must be specific to the project, not a copied TES workflow.

## Quality And Safety

`QUALITY-GATES.md` and `BOUNDARIES-AND-CONSTRAINTS.md` must map real project
surfaces.

The skill should classify gates as:

| Gate class | Meaning |
|------------|---------|
| `required` | Must pass before claiming project closure. |
| `focused` | Run for a specific touched territory. |
| `advisory` | Useful signal but not closure-blocking. |
| `unavailable` | Expected in theory but absent in this project. |
| `unsafe` | Must not run without explicit authorization. |

Safety constraints must mention protected files, generated files, secrets,
external systems, destructive commands, and project-owned governance.

## Evidence And Contradictions

`/tes-align` must treat contradictions as signal.

Rules:

1. Do not erase old claims just because a newer file disagrees.
2. Record the conflict, sources, and current working interpretation.
3. Mark confidence on claims that affect roadmap or execution.
4. Prefer source inspection and local gates over memory.
5. Preserve raw project sources; do not edit sources to make docs cleaner.

The retained evidence packet should include:

```yaml
alignment_evidence:
  target:
  tes_version:
  anchors_read:
  existing_docs_classification:
  created_or_updated:
  contradictions:
  quality_gates_discovered:
  roadmap_changes:
  obsidian_native_checks:
  oracle_result:
  limits:
```

## Oracle Requirements

The implementation includes a deterministic `project_alignment_oracle.py`
package gate.

Minimum checks:

| Check | Failure it prevents |
|-------|---------------------|
| Required surface or linked equivalent exists | Empty alignment claims. |
| Anchors are listed with paths | Context written from memory. |
| Roadmap separates done, active, next, deferred, blocked, unknown | Rebuilding existing work or hiding uncertainty. |
| Execution line names gates and stop conditions | Agents restart without direction. |
| Quality gates are project-specific | Generic "run tests" filler. |
| Boundaries mention protected governance and external mutation | Unsafe autonomy. |
| Glossary or term map exists when domain terms are non-obvious | Semantic drift. |
| Obsidian frontmatter/wikilink hygiene passes | Graph and query views degrade. |
| No `.obsidian/**` writes | Runtime/editor state pollution. |
| Evidence packet exists | Alignment cannot be audited. |

The oracle must allow sparse projects to pass honestly when gaps are explicit.
It must fail generic documents that look complete but cannot guide work.

## Skill Construction Requirements

`/tes-align` follows Tilly skill structure:

| Surface | Requirement |
|---------|-------------|
| `SKILL.md` | Lean router: trigger, role, workflow, locks, outputs, validation. |
| `references/` | Detailed alignment procedure, Obsidian-native mesh guidance, templates, and canary strategy. |
| `scripts/` | Deterministic oracle and fixture helpers where useful. |
| `docs/CONTRACT-HISTORY.md` | Why the skill exists, origin evidence, failure modes, relationships, and do-not-lose points. |
| `agents/openai.yaml` | Runtime display and default prompt aligned to `/tes-align`. |

The skill body must be English. Target-project generated docs may follow the
project language when evidence supports it.

## Canaries

Before certification, `/tes-align` must be tested against real and synthetic
projects:

| Canary | Risk |
|--------|------|
| Sparse repository | Invented roadmap or architecture. |
| Docs-heavy repository | Duplicated docs instead of linking existing truth. |
| Large monorepo | Generic territory summaries and false confidence. |
| Project with stale roadmap | Failure to mark done/superseded work. |
| Project-owned governance | Overwriting or contradicting local rules. |
| Obsidian vault-like docs | `.obsidian/**` pollution or visual-only truth. |
| Multi-language/toolchain project | Incorrect gate and ownership mapping. |

Certification must include at least one false-green attempt where the first
alignment looks plausible but the oracle or reviewer proves it is not useful
enough.

## Source Ledger

This contract is based on:

| Source | Reference | Signal |
|--------|-----------|--------|
| TES Wave 1-6 canary convergence | `/Users/murillo/Dev/tes-canaries/RUN-INDEX.md` and retained run reports | Real Build-Test-Fail-Fix loops showed that context must be proven by canaries, not prose. |
| `/tes-init` project-start gate | `docs/install/COMMAND-TRIGGERS.md` | Initial context generation is necessary but not enough for deep alignment. |
| Context mesh method | `docs/mesh/CONTEXT-MESH-METHOD.md` and `docs/mesh/CONTEXT-MESH-CONVERGENCE.md` | Context becomes contract only when linked to execution, verification, evidence, and transfer. |
| User project-wiki thesis | Conversation directive captured before this source-of-truth document | Durable Markdown, immutable sources, schema, index, log, crosslinks, lint, Git, and Obsidian visualization are core principles. |
| Senior peer review supplied by Murillo | Conversation directive captured before this source-of-truth document | ADRs, boundaries, knowledge lifecycle, glossary, and evidence taxonomy are useful when discovered and not blindly imposed. |
| Obsidian official help repository | `https://github.com/obsidianmd/obsidian-help` | The English help vault is the upstream documentation source used for Obsidian behavior. |
| Obsidian Bases | `https://obsidian.md/help/bases` | Bases are optional database-like views over local Markdown files and their properties. |
| Obsidian Properties | `https://obsidian.md/help/properties` | Properties are the portable metadata layer that makes Markdown queryable. |
| Obsidian internal links | `https://obsidian.md/help/links` | Internal links and wikilinks are the durable relationship layer for navigable project knowledge. |
| Obsidian Graph view | `https://obsidian.md/help/plugins/graph` | Graph view informs hub, orphan, and relationship visualization. |
| Obsidian Canvas | `https://obsidian.md/help/plugins/canvas` | Canvas is a visual synthesis layer; it must not become the only source of truth. |
| Obsidian CLI | `https://obsidian.md/help/cli` | CLI support is relevant for future optional opening/navigation workflows, not a TES runtime dependency. |
| Context7 Obsidian documentation lookup | Context7 library `/websites/obsidian_md_help`, checked on 2026-05-09 | Confirms the same direction: Bases and Properties are local Markdown/property-oriented and suitable as optional views. |

## Locks

- Do not build `/tes-align` as another installer.
- Do not create a new command parameter for `/tes-init` to do this work.
- Do not create docs that duplicate stronger project-owned sources.
- Do not call alignment deep when only a scaffold was generated.
- Do not require Obsidian, Obsidian plugins, or `.obsidian/**`.
- Do not make `.base` or `.canvas` files the source of truth.
- Do not turn roadmap creation into speculative feature invention.
- Do not overwrite project-owned governance.
- Do not claim certification without a deterministic oracle and retained
  evidence.

## Done

`/tes-align` is ready only when a clean target project can run it after
`/tes-init` and receive:

1. A refined project context.
2. A current state document.
3. A roadmap that does not rebuild completed work.
4. An execution line that makes the next session obvious.
5. Project-specific quality gates and boundaries.
6. An Obsidian-native but Git-portable mesh.
7. A retained evidence packet.
8. A passing alignment oracle.

The certification sentence should be:

```text
Project alignment: PASS, with explicit limits.
```

If the project is too sparse, contradictory, or unsafe to align, the honest
closure is `NEEDS_REVIEW`, `BLOCKED`, or `DEFERRED`, not a polished false
green.
