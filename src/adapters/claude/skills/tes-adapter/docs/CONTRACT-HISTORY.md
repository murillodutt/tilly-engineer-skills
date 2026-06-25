# TES Adapter Contract History

## Purpose

`/tes-adapter` materializes, dry-runs, retrofits, validates, and certifies TES adapters for Codex, Claude, Cursor, or all routes.

## Why This Skill Exists

Adapter installs conflict with project-owned instructions. Materialization and retrofit need explicit dry-run and conflict review.

## Contracts Preserved

- `materialize_adapter.py --check` before package writes.
- `install_adapter.py --dry-run` on targets.
- Retrofit plan when conflicts exist.
- Writes only with explicit `--yes`.
- `dist/**` is not canonical source.
- No legacy `.cursorrules` reintroduction.

## Known Failure Modes Prevented

- Blind overwrite of project instructions.
- Treating generated dist as source of truth.
- Publishing marketplace packages from this shortcut.

## Relationship To Other Skills

`tes-init` applies adapters during install. `tes-adapter` is focused materialization/certification. `tes-update` may refresh adapter config.

## Changelog

| Date | Change | Evidence | Confidence |
|------|--------|----------|------------|
| 2026-05-09 | Created adapter skill. | `install_adapter.py`, smoke oracles. | high |
| 2026-06-08 | Added contract history per Tilly skill standard. | Documentation authority tiers program. | high |

## Do Not Lose

Dry-run and conflict review before any adapter write.
