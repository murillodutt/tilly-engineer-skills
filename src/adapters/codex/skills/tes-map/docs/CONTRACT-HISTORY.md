# TES Map Contract History

## Purpose

`/tes-map` updates the Project GPS managed block and Eraser Atlas projections inside `PROJECT-ROADMAP.md` after alignment exists.

## Why This Skill Exists

Agents need a visual current-position answer without rewriting the whole roadmap. `tes-align` owns the map; `tes-map` refreshes GPS projection.

## Contracts Preserved

- Writable region is only `<!-- TES-MAP:START -->` … `<!-- TES-MAP:END -->`.
- `PROJECT-ROADMAP.md` remains Markdown source of truth.
- `.tes/gps/*.eraserdiagram` are projections, not parallel roadmaps.
- Missing roadmap → `NEEDS_ALIGN`; missing context → `NEEDS_CONTEXT`.

## Known Failure Modes Prevented

- Writing outside the managed GPS block.
- Treating Atlas sidecars as authority over Tier 2 mesh.
- Running map before `/tes-align`.

## Relationship To Other Skills

`tes-align` creates/updates roadmap and Convergence Line. `tes-map` refreshes GPS position and Atlas links.

## Changelog

`Version` records a skill operational contract version only when the skill declares one, followed by the containing TES package version when known. If no operational contract stamp exists, the TES package version is the shipped identity. `tver: 0.1.0` in roadmap, Super SPEC, ledger, or TDS frontmatter is document-template metadata, not a skill runtime or harness version. Patch-level changes can remain inside the same skill contract boundary; in that case the TES package version carries release identity until a future change alters the skill contract boundary itself.

| Date | Change | Evidence | Confidence |
|------|--------|----------|------------|
| 2026-06-29 | Documented universal Contract History version semantics so skill contract versions, TES package versions, and `tver` metadata are not conflated. | `docs/dist/0.3.229/tilly-engineer-skills-0.3.229.zip`; `scripts/public_bundle_oracle.py` | high |
| 2026-05-11 | Created map/GPS skill with managed block contract. | `tes_map.py` helper. | high |
| 2026-06-08 | Added contract history per Tilly skill standard. | Documentation authority tiers program. | high |

## Do Not Lose

Map updates position; align updates meaning.
