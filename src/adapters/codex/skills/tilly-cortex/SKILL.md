---
name: tilly-cortex
description: Use when the user says /tilly:cortex, /tilly:recall, /tilly:learn, /tilly:reflect, or asks to inspect, audit, rebuild, query, read, learn from, reflect into, or apply Tilly Cortex memory.
---

# Tilly Cortex

`/tilly:cortex` is the user-facing shortcut for Cortex memory operations. The
agent remains the executor; scripts and MCP tools are oracles.

## Intent Map

| User intent | Preferred action |
|-------------|------------------|
| recall/query/search memory | use read-only `cortex_recall` MCP or `cortex.py recall` |
| read a cell | use read-only `cortex_read_cell` MCP or `cortex.py read-cell` |
| check memory health | run `cortex.py verify` and `cortex.py audit` |
| rebuild recall | run `cortex.py rebuild`; SQLite remains derived |
| learn from a source | run `cortex.py learn` or `absorb-plan`; propose only |
| close a work cycle | run `cortex.py reflect`; propose only |
| promote a durable claim | run `cortex.py apply` only with explicit approval and evidence |

## Rules

- Treat `sources/**`, `cells/**`, `MAP.md`, `TRAIL.md`, `LINKS.md`, and
  `CONTRACT.md` as the memory.
- Treat `.tilly/cortex/recall.sqlite` as rebuildable cache.
- Prefer MCP for read-only recall/read/reflect when available.
- Never write `sources/**` after import.
- Never promote loose summaries; cells need `## Claim` and `## Evidence`.
- Never run `apply --yes` without explicit user authorization.
