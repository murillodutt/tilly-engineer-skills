# TES Doctor Contract History

## Purpose

`/tes-doctor` health-checks installed targets and the TES source package with the smallest oracle that proves the claim.

## Why This Skill Exists

Agents conflate contexts (installed target vs package source) and invent gates. Doctor classifies workspace first, then selects oracles.

## Contracts Preserved

- Installed target: `.tes/bin/**` oracles, project context/alignment, mantra adoption, optional project `gate:*` scripts.
- Package source: `npm run validate`, docs size, TDS, cortex/MCP self-tests.
- Smallest gate that proves the claim.
- Report `NOT_AVAILABLE` instead of inventing project gates.

## Known Failure Modes Prevented

- Running package-source scripts on installed targets without checking.
- Claiming clean install from MCP-only success.
- Skipping workspace classification.

## Relationship To Other Skills

`tes-init` installs. `tes-doctor` certifies. `tes-mcp` repairs MCP drift. `tes-align` oracle is separate from doctor but may be invoked by doctor table.

## Changelog

| Date | Change | Evidence | Confidence |
|------|--------|----------|------------|
| 2026-05-09 | Created doctor skill with context gate table. | Installed certification oracle. | high |
| 2026-06-08 | Added contract history per Tilly skill standard. | Documentation authority tiers program. | high |

## Do Not Lose

Classify workspace before choosing commands.
