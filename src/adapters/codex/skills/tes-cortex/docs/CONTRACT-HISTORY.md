# TES Cortex Contract History

## Purpose

`/tes-cortex` governs Cortex memory: recall, read, verify, audit, rebuild,
curate, learn, reflect, apply, remember, forget, and consolidation.

## Why This Skill Exists

Memory boundaries are easy to violate (SQLite as truth, writing sources after
import, ungoverned remember). This skill maps intents to safe operations.

## Contracts Preserved

- `docs/agents/cortex/sources/**`, cells, MAP, TRAIL, LINKS, CONTRACT are memory.
- SQLite recall/semantic DBs are rebuildable caches.
- Governed remember: plan then explicit approval.
- Apply/remember/forget require evidence and approval lanes.
- Read-only MCP preferred for recall/curate when available.

## Known Failure Modes Prevented

- Treating SQLite as source of truth.
- Writing `sources/**` after import.
- Ungoverned durable memory promotion.
- Skipping consolidation gate for forget.

## Relationship To Other Skills

`tes-init` scaffolds cortex tree. `tes-mcp` exposes Cortex tools. `tes-align`
may suggest Cortex promotion after Tier 1/2 review.

## Changelog

| Date | Change | Evidence | Confidence |
|------|--------|----------|------------|
| 2026-05-09 | Created cortex intent map skill. | Cortex MCP and `cortex.py` contract. | high |
| 2026-06-08 | Added contract history per Tilly skill standard. | Documentation authority tiers program. | high |

## Do Not Lose

Markdown artifacts are truth; SQLite is derived recall.
