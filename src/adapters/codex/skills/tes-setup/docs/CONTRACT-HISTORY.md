# TES Setup Contract History

## Purpose

`/tes-setup` is the Claude Code setup alias for `/tes-init`, optimized for
first-session postinstall sentinel handling.

## Why This Skill Exists

The first-session hook recommends `/tes-setup`. This skill routes to `tes-init`
without duplicating installer logic.

## Contracts Preserved

- Delegates to `tes-init` skill when present.
- Respects `.tes/postinstall.json` sentinel (`complete`, `running`, `needs_review`).
- Recovery uses `tes_install.py postinstall --recover-needs-review`.

## Known Failure Modes Prevented

- Duplicate Project-Start while postinstall is `running`.
- Ignoring `needs_review` without recovery closure.
- Reimplementing installer workflow in the alias skill.

## Relationship To Other Skills

Thin alias over `tes-init`. No separate installer authority.

## Changelog

| Date | Change | Evidence | Confidence |
|------|--------|----------|------------|
| 2026-05-09 | Created setup alias skill. | First-session hook contract. | high |
| 2026-06-08 | Added contract history per Tilly skill standard. | Documentation authority tiers program. | high |

## Do Not Lose

`/tes-setup` is routing and sentinel discipline, not a second installer.
