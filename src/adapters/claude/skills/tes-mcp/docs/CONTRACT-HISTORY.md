# TES MCP Contract History

## Purpose

`/tes-mcp` activates, verifies, repairs, and explains project-scoped TES Cortex MCP for Codex, Claude, Cursor, VS Code, or all routes.

## Why This Skill Exists

MCP registration is easy to confuse with host recognition. This skill separates config presence, self-test, handshake, and session restart requirements.

## Contracts Preserved

- Default activation exposes governed remember (not inspection-only unless asked).
- Project-scoped config is default for Codex.
- MCP success alone is not full installed certification (`tes-doctor` owns that).
- Use `install_mcp.py` dry-run before writes.

## Known Failure Modes Prevented

- Claiming MCP functional from file presence alone.
- Skipping `cortex_mcp.py --self-test`.
- Treating host listing as connected tools without session reload.

## Relationship To Other Skills

`tes-init` may activate MCP during install. `tes-mcp` is the focused repair route. `tes-cortex` operates memory; `tes-doctor` certifies install health.

## Changelog

| Date | Change | Evidence | Confidence |
|------|--------|----------|------------|
| 2026-05-15 | Created MCP-focused skill. | `install_mcp.py` contract. | high |
| 2026-06-08 | Added contract history per Tilly skill standard. | Documentation authority tiers program. | high |

## Do Not Lose

Report host recognition states separately from config writes.
