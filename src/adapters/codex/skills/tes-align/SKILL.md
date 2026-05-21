---
name: tes-align
description: Use when the user says /tes-align, /tes:align, tes align, align TES, align this project, alinhar TES, alinhar projeto, or asks TES to semantically align a project after /tes-init by creating or updating the project operating mesh, System X-Ray, Convergence Line, execution line, quality gates, boundaries, glossary, decisions, and retained alignment evidence.
license: MIT
---

# TES Align

`/tes-align` is the preferred shared TES trigger for semantic project
alignment after `/tes-init`. `/tes:align` is a compatible TES intent alias if
the host reports it as invalid slash text.

Use this skill when initial project context exists but the project still needs
an operating mesh that tells the next agent what is done, what is active, what
must not be rebuilt, which gates prove quality, and which execution line should
advance next.

## Source Of Truth

When working inside the TES source package, read the TES Align source-of-truth
document before changing this skill. When running in an installed target, use
this skill body as the embedded contract. If the package source-of-truth
document is 15 days or more past `sources_verified_on`, verify its listed
sources, update it if needed, and only then use it as construction truth.

## Mission

Turn initial context into an evidenced project operating mesh:

```text
PROJECT-CONTEXT -> PROJECT-STATE -> PROJECT-ROADMAP x-ray/convergence -> EXECUTION-LINE
```

The goal is operational legibility, not prettier documentation.
`PROJECT-ROADMAP.md` should present a System X-Ray and Convergence Line first
so the project organism and future path are visible before the audit lanes.
`tes-align` owns the map. `/tes-map` only updates the current GPS position
inside the managed `TES-MAP` block after this roadmap exists.

## Workflow

1. Confirm TES is installed or run `/tes-init` first.
2. Inspect existing project docs and classify each expected surface as
   `present`, `linked_existing`, `created`, `needs_update`, `contradictory`,
   `deferred`, or `not_applicable`.
3. Read strong anchors before claiming depth: identity, structure, build and
   gates, architecture, governance, history, and risk.
4. Create or update the project operating mesh under `docs/agents/**`:
   `PROJECT-CONTEXT.md`, `PROJECT-STATE.md`, `PROJECT-ROADMAP.md`,
   `EXECUTION-LINE.md`, `QUALITY-GATES.md`,
   `BOUNDARIES-AND-CONSTRAINTS.md`, `KNOWLEDGE-LIFECYCLE.md`,
   `GLOSSARY.md`, `DECISIONS/**` or a link to an existing decision system,
   and `evidence/<timestamp>-project-alignment.md`.
5. In `PROJECT-ROADMAP.md`, make the first human scan path two Mermaid
   `flowchart TD` graphs:
   - System X-Ray: Git state, delivered behavior, validation mesh, and release
     boundary.
   - Convergence Line: done/current/next/later/deferred/blocked/unknown/final
     states.
   Keep Done, Active, Next, Later, Deferred, Blocked, and Unknown as compact
   audit lanes.
6. Keep the mesh Obsidian-native and Git-portable: use Markdown, YAML
   frontmatter, and useful wikilinks; never write `.obsidian/**`; do not make
   `.base` or `.canvas` the only source of truth.
7. Keep target-project alignment evidence under `docs/agents/evidence/**`.
   Package benchmark evidence uses `docs/evidence/current/**`,
   `docs/evidence/reports/YYYY/MM/DD/**`, and `docs/evidence/archive/**`;
   do not mix those source-package retention layers into target projects.
8. Certify with:

```bash
python3 .tes/bin/project_alignment_oracle.py --target .
```

Use `python3 scripts/project_alignment_oracle.py --target <target>` when
running from the TES source package.

## Done

Close only when the oracle passes or the report honestly says `NEEDS_REVIEW`,
`BLOCKED`, or `DEFERRED` with evidence.

The certification sentence is:

```text
Project alignment: PASS, with explicit limits.
```

## Locks

- Do not run installer/update writes unless TES is missing or stale.
- Do not overwrite active governance before `.tes/bk/<timestamp>/manifest.json` exists.
- Do not recreate docs that already exist under stronger project-owned paths.
- Do not invent architecture, roadmap items, or decisions.
- Do not replace the System X-Ray and Convergence Line with only a textual roadmap.
- Do not call scaffold output deep alignment.
- Do not write `.obsidian/**`.
- Do not claim PASS without retained evidence and a passing oracle.
