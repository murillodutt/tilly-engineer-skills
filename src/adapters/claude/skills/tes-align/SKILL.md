---
name: tes-align
description: Use when the user says /tes-align, /tes:align, tes align, align TES, align this project, alinhar TES, alinhar projeto, or asks TES to semantically align a project after /tes-init by creating or updating the project operating mesh, roadmap, execution line, quality gates, boundaries, glossary, decisions, and retained alignment evidence.
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
PROJECT-CONTEXT -> PROJECT-STATE -> PROJECT-ROADMAP -> EXECUTION-LINE
```

The goal is operational legibility, not prettier documentation.

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
5. Keep the mesh Obsidian-native and Git-portable: use Markdown, YAML
   frontmatter, and useful wikilinks; never write `.obsidian/**`; do not make
   `.base` or `.canvas` the only source of truth.
6. Certify with:

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
- Do not overwrite project-owned governance.
- Do not recreate docs that already exist under stronger project-owned paths.
- Do not invent architecture, roadmap items, or decisions.
- Do not call scaffold output deep alignment.
- Do not write `.obsidian/**`.
- Do not claim PASS without retained evidence and a passing oracle.
