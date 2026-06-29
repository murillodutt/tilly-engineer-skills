# TES Update Contract History

## Purpose

`/tes-update` refreshes an installed TES mesh via `tes_update.py` without default full re-initialization.

## Why This Skill Exists

Installed targets drift in helpers, adapters, and root-context blocks. Update needs a read-only plan first, bounded write scopes, and a recorded final probe.

## Contracts Preserved

- Engine is `tes_update.py`; skill does not reimplement planning.
- Default route is not `/tes-init`.
- Helper parity before adapter/MCP refresh.
- `root-context` scope preserves project overlay.
- Final probe must show `update_available=False` before PASS.

## Known Failure Modes Prevented

- Whole-file bootloader overwrite on root-context route.
- Rerunning Project-Start for helper-only drift.
- Reporting PASS without recorded final probe.
- Leaving `PENDING_APPROVAL` plans without resumable evidence.

## Relationship To Other Skills

`tes-update` refreshes TES runtime. `tes-init` recertifies project-start. `tes-doctor` validates health. `tes-adapter` materializes adapter trees.

## Changelog

`Version` records a skill operational contract version only when the skill declares one, followed by the containing TES package version when known. If no operational contract stamp exists, the TES package version is the shipped identity. `tver: 0.1.0` in roadmap, Super SPEC, ledger, or TDS frontmatter is document-template metadata, not a skill runtime or harness version. Patch-level changes can remain inside the same skill contract boundary; in that case the TES package version carries release identity until a future change alters the skill contract boundary itself.

| Date | Change | Evidence | Confidence |
|------|--------|----------|------------|
| 2026-06-29 | Documented universal Contract History version semantics so skill contract versions, TES package versions, and `tver` metadata are not conflated. | `docs/dist/0.3.229/tilly-engineer-skills-0.3.229.zip`; `scripts/public_bundle_oracle.py` | high |
| 2026-05-21 | Created visible update entrypoint skill. | `tes_update.py` planner contract. | high |
| 2026-06-08 | Added contract history per Tilly skill standard. | Documentation authority tiers program. | high |

## Do Not Lose

Plan read-only first. Write only the scope the planner names. Prove closure with the recorded probe.
