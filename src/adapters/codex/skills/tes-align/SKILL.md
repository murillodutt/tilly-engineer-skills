---
name: tes-align
description: Use when the user says /tes-align, /tes:align, tes align, align TES, align this project, alinhar TES, alinhar projeto, or asks TES to semantically align a project after /tes-init by creating or updating the project operating mesh, System X-Ray, Convergence Line, execution line, quality gates, boundaries, glossary, decisions, and retained alignment evidence.
license: MIT
---

# TES Align

`/tes-align` is the preferred shared TES trigger for semantic project alignment after `/tes-init`. `/tes:align` is a compatible TES intent alias if the host reports it as invalid slash text.

Use this skill when initial project context exists but the project still needs an operating mesh that tells the next agent what is done, what is active, what must not be rebuilt, which gates prove quality, and which execution line should advance next.

## Module Map

| Surface | Load when |
|---------|-----------|
| `references/alignment-procedure.md` | Running alignment workflow details |
| `docs/CONTRACT-HISTORY.md` | Reviewing why the skill exists, changelog, or failure modes |

## Source Of Truth

When working inside the TES source package, read the TES Align source-of-truth document before changing this skill. When running in an installed target, use this skill body as the embedded contract. Any material skill change must append `docs/CONTRACT-HISTORY.md` before claiming done. If the package source-of-truth document is 15 days or more past `sources_verified_on`, verify its listed sources, update it if needed, and only then use it as construction truth.

## Mission

Turn initial context into an evidenced project operating mesh:

```text
DOCUMENTATION-AUTHORITY (when present)
-> Tier 1 anchors (README, roadmap, decisions)
-> PROJECT-STATE -> PROJECT-ROADMAP x-ray/convergence -> EXECUTION-LINE
-> Tier 3 contracts mirror + PROJECT-CONTEXT inventory demotion
```

The goal is operational legibility, not prettier documentation. When `docs/agents/DOCUMENTATION-AUTHORITY.md` exists, Tier 2 leads cold start; `PROJECT-CONTEXT` is init inventory after `/tes-align`, not position authority. `PROJECT-ROADMAP.md` should present Eraser-first Atlas links plus Mermaid fallback System X-Ray and Convergence Line views first, so the project organism and future path are visible before the audit lanes. `tes-align` owns the map. `/tes-map` updates the Atlas projection and current GPS position inside the managed `TES-MAP` block after this roadmap exists.

## Workflow

1. Confirm TES is installed or run `/tes-init` first.
2. Inspect existing project docs and classify each expected surface as `present`, `linked_existing`, `created`, `needs_update`, `contradictory`, `deferred`, or `not_applicable`.
3. Read strong anchors before claiming depth: identity, structure, build and gates, architecture, governance, history, and risk.
4. Before claiming alignment, read the latest accepted ADRs under `docs/agents/DECISIONS/**` (or the linked decision system) and the most recent retained alignment evidence packet under `docs/agents/evidence/**`. Treat contradictions between newer decisions and the active mesh as first-class evidence and record them in the retained packet. Do not erase older claims without a successor decision.
5. Before the first `docs/agents/**` mesh write, create or refresh `.tes/runtime/tes-align.active` with text containing `tes-align active`, keep it fresh during long alignment passes, and remove it before closeout. This tells Cortex runtime hooks that mesh edits are inside the explicit `/tes-align` reconciler instead of ordinary drift.
6. Create or update the project operating mesh under `docs/agents/**`: `DOCUMENTATION-AUTHORITY.md` (tier ladder when missing), `PROJECT-STATE.md`, `PROJECT-ROADMAP.md`, `EXECUTION-LINE.md`, `QUALITY-GATES.md`, `BOUNDARIES-AND-CONSTRAINTS.md`, `KNOWLEDGE-LIFECYCLE.md`, `GLOSSARY.md`, `DECISIONS/**` or a link to an existing decision system, `evidence/<timestamp>-project-alignment.md`, then mirror Tier 1+2 into `contracts/**` and demote `PROJECT-CONTEXT.md` to Tier 3 inventory.
7. In `PROJECT-ROADMAP.md`, make the first human scan path Eraser-first with local `.tes/gps/*.eraserdiagram` Atlas sidecars and Mermaid fallback graphs:
   - System X-Ray: Git state, delivered behavior, validation mesh, and release boundary.
   - Convergence Line: done/current/next/later/deferred/blocked/unknown/final states. Easy-first is the Atlas birth surface, not the evolution ceiling: the initial output must be useful and certified, and deeper project-specific relationships should evolve through profilers, `--deep`, fixtures, and oracles. Keep Done, Active, Next, Later, Deferred, Blocked, and Unknown as compact audit lanes.
8. Keep the mesh Obsidian-native and Git-portable: use Markdown, YAML frontmatter, and useful wikilinks; never write `.obsidian/**`; do not make `.base` or `.canvas` the only source of truth.
9. Keep target-project alignment evidence under `docs/agents/evidence/**`. Package benchmark evidence uses `docs/evidence/current/**`, `docs/evidence/reports/YYYY/MM/DD/**`, and `docs/evidence/archive/**`; do not mix those source-package retention layers into target projects.
10. Run the Semantic Residue Gate before PASS. If the project declares `docs/agents/contracts/SEMANTIC-RESIDUE.yml`, the oracle scans active documentation for retired terms and stale claim patterns. Report exact stale terms and paths when the gate fails. Refuse to call scaffold output deep alignment, and do not report PASS when retired vocabulary remains in active docs. TES owns the mechanism; the target project owns the vocabulary.
11. Certify with:

```bash
python3 .tes/bin/project_alignment_oracle.py --target .
```

Use `python3 scripts/project_alignment_oracle.py --target <target>` when running from the TES source package. Pass `--strict` to make `NEEDS_REVIEW` exit non-zero in CI.

## Done

Close only when the oracle passes or the report honestly says `NEEDS_REVIEW`, `BLOCKED`, or `DEFERRED` with evidence.

Remove `.tes/runtime/tes-align.active` before closeout, even when alignment ends as `NEEDS_REVIEW`, `BLOCKED`, or `DEFERRED`.

The certification sentence is:

```text
Project alignment: PASS, with explicit limits.
```

## Locks

- Do not run installer/update writes unless TES is missing or stale.
- Do not overwrite active governance before `.tes/bk/<timestamp>/manifest.json` exists.
- Do not recreate docs that already exist under stronger project-owned paths.
- Do not invent architecture, roadmap items, or decisions.
- Do not replace the Atlas/System X-Ray/Convergence Line with only a textual roadmap.
- Do not call scaffold output deep alignment.
- Do not write `.obsidian/**`.
- Do not claim PASS without retained evidence and a passing oracle.
- Do not leave `.tes/runtime/tes-align.active` behind after the alignment attempt.
- Do not hard-code project-specific vocabulary into TES skill body. The Semantic Residue Gate carries the mechanism; the project carries the terms via `docs/agents/contracts/SEMANTIC-RESIDUE.yml`.
- Do not report PASS when newer accepted ADRs introduce successor terms absent from the active mesh. Re-read the ADR and reconcile first.
