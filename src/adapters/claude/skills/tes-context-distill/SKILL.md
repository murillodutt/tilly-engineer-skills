---
name: tes-context-distill
description: Use when the user says /tes-context-distill, tes context distill, distill project context, optimize the inherited CLAUDE.md/AGENTS.md context, or when tes-init/tes-setup reports an inherited context overlay that needs the optional condense pass. Runs the judgment phase of inherited-context distillation with a non-loss coverage gate.
license: MIT
---

# TES Context Distill

`/tes-context-distill`, `tes context distill`, `distill project context`,
`optimize inherited context`, `condensar contexto`, `destilar contexto do
projeto` are the triggers for the judgment phase of inherited-context
distillation.

This skill is the Phase 2 of `GOAL-SUPER-SPEC-tes-inherited-context-canonical-source`:
the agent-driven condense/optimize pass. It is deliberately isolated from the
installer so the heavy, judgment-bearing work is testable on its own and the
`/tes-setup` alias stays thin.

## Phase Boundary

Distillation has two phases. Know which one you are in.

- **Phase 1 — deterministic (NOT this skill).** Archive the pre-existing root
  as `<root>.bak-<stamp>`, extract context units verbatim into the canonical
  source `docs/agents/PROJECT-CONTEXT.md`, render the thin root. This runs as
  code inside the installer (`scripts/install_adapter.py` →
  `route_inherited_context_roots`) because it must run headless during a
  non-interactive `install --yes`. Do not re-implement it here.
- **Phase 2 — judgment (THIS skill).** Condense, organize, and sanitize the
  extracted units into clean canonical sections. Only this phase may reword. It
  runs only under explicit user confirmation.

## Workflow

1. Confirm Phase 1 already ran: `docs/agents/PROJECT-CONTEXT.md` exists and a
   `<root>.bak-<stamp>` archive is present. If not, route the user to
   `/tes-init` first — do not distill without the archive (it is the non-loss
   oracle).
2. Read the archived original `<root>.bak-<stamp>` and the current canonical
   source. The `.bak` is the source of truth for non-loss; never edit it.
3. Propose a condensed/optimized canonical source: merge duplicate units, drop
   redundant or obsolete ones, and place each unit under its governed section.
   Every drop must be a recorded discard with a reason from the closed set:
   `redundant-with-tes-core`, `obsolete`, `duplicate`, or `superseded-by-<unit>`.
4. Get explicit user confirmation before writing. Phase 2 rewords human content;
   it is opt-in.
5. Verify with the coverage gate before closing:
   `python3 .tes/bin/context_distill_coverage_oracle.py --bak <root>.bak-<stamp> --source docs/agents/PROJECT-CONTEXT.md [--discards <discards.json>]`
   Required result: `OVERLAY_COVERED`. Anything else means a unit was lost
   without a reason — stop and repair.
6. Confirm the canonical source still satisfies the overlay oracle:
   `python3 .tes/bin/project_context_oracle.py --target .` (must stay PASS).

## Locks

- Do not run Phase 2 without explicit user confirmation. It rewords human text.
- Do not write a condensed source that fails `OVERLAY_COVERED`; a lost unit with
  no recorded reason is a hard stop.
- Do not delete or edit the `<root>.bak-<stamp>` archive — it is the non-loss
  oracle and the uninstall restore source.
- Do not re-implement Phase 1 (archive/extract/render) here; that is installer
  code that must run headless.
- Do not push, publish, tag, or edit remotes from this skill.
- Keep the final response short: report the coverage verdict, units condensed,
  units discarded-with-reason, and limits.
