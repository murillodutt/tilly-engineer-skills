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

`Version` records a skill operational contract version only when the skill declares one, followed by the containing TES package version when known. If no operational contract stamp exists, the TES package version is the shipped identity. `tver: 0.1.0` in roadmap, Super SPEC, ledger, or TDS frontmatter is document-template metadata, not a skill runtime or harness version. Patch-level changes can remain inside the same skill contract boundary; in that case the TES package version carries release identity until a future change alters the skill contract boundary itself.

| Date | Change | Evidence | Confidence |
|------|--------|----------|------------|
| 2026-06-29 | Documented universal Contract History version semantics so skill contract versions, TES package versions, and `tver` metadata are not conflated. | `docs/dist/0.3.229/tilly-engineer-skills-0.3.229.zip`; `scripts/public_bundle_oracle.py` | high |
| 2026-05-15 | Created MCP-focused skill. | `install_mcp.py` contract. | high |
| 2026-06-08 | Added contract history per Tilly skill standard. | Documentation authority tiers program. | high |

## Do Not Lose

Report host recognition states separately from config writes.
