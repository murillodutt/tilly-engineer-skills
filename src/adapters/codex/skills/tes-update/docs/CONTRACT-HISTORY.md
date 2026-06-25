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

| Date | Change | Evidence | Confidence |
|------|--------|----------|------------|
| 2026-05-21 | Created visible update entrypoint skill. | `tes_update.py` planner contract. | high |
| 2026-06-08 | Added contract history per Tilly skill standard. | Documentation authority tiers program. | high |

## Do Not Lose

Plan read-only first. Write only the scope the planner names. Prove closure with the recorded probe.
