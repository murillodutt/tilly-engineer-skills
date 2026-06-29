# TES Context Distill Contract History

## Purpose

`/tes-context-distill` runs Phase 2 judgment condense on inherited root context archived to `.bak-<stamp>`, with non-loss coverage against the archive.

## Why This Skill Exists

Installer Phase 1 is deterministic and headless; condense requires judgment and user confirmation. Isolating Phase 2 keeps `/tes-setup` thin and testable.

## Contracts Preserved

- Phase 1 is installer code only — not this skill.
- `.bak-<stamp>` is non-loss oracle; never edit it.
- Phase 2 rewords only with explicit user confirmation.
- Drops require closed-set discard reasons.
- `PROJECT-CONTEXT` after distill remains Tier 3 inventory unless `/tes-align` refreshes Tier 2.

## Known Failure Modes Prevented

- Distilling without Phase 1 archive.
- Silent deletion without recorded discard reason.
- Treating condensed inventory as operational position without align.

## Relationship To Other Skills

`tes-init` runs Phase 1 archive/extract. `tes-context-distill` runs Phase 2. `tes-align` owns Tier 2 after inventory exists.

## Changelog

`Version` records a skill operational contract version only when the skill declares one, followed by the containing TES package version when known. If no operational contract stamp exists, the TES package version is the shipped identity. `tver: 0.1.0` in roadmap, Super SPEC, ledger, or TDS frontmatter is document-template metadata, not a skill runtime or harness version. Patch-level changes can remain inside the same skill contract boundary; in that case the TES package version carries release identity until a future change alters the skill contract boundary itself.

| Date | Change | Evidence | Confidence |
|------|--------|----------|------------|
| 2026-06-29 | Documented universal Contract History version semantics so skill contract versions, TES package versions, and `tver` metadata are not conflated. | `docs/dist/0.3.229/tilly-engineer-skills-0.3.229.zip`; `scripts/public_bundle_oracle.py` | high |
| 2026-05-20 | Created distill skill for inherited context Phase 2. | GOAL-SUPER-SPEC inherited context. | high |
| 2026-06-08 | Clarified Tier 3 inventory role post-distill. | Consumer pilot documentation authority tiers. | high |

## Do Not Lose

Archive is truth for non-loss. Distill organizes inventory; align positions the project.
