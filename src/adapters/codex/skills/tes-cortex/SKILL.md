---
name: tes-cortex
description: Use when the user says /tes-cortex, /tes:cortex, /tes:recall, /tes:learn, /tes:reflect, /tes:curate, or asks to inspect, audit, rebuild, query, read, learn from, reflect into, semantically curate, or apply TES Cortex memory.
---

# TES Cortex

`/tes-cortex` and `/tes:cortex` are user-facing shortcuts for Cortex memory operations. The
agent remains the executor; scripts and MCP tools are oracles.

## Intent Map

| User intent | Preferred action |
|-------------|------------------|
| recall/query/search memory | use read-only `cortex_recall` MCP or `cortex.py recall` |
| read a cell | use read-only `cortex_read_cell` MCP or `cortex.py read-cell` |
| check memory health | run `cortex.py verify` and `cortex.py audit` |
| rebuild recall | run `cortex.py rebuild`; SQLite remains derived |
| curate memory quality | run read-only `cortex_curate_plan` MCP or `cortex.py curate-plan --backend lexical` |
| learn from a source | run `cortex.py learn` or `absorb-plan`; propose only |
| close a work cycle | run `cortex.py reflect`; propose only |
| promote a durable claim | run `cortex.py apply` only with explicit approval and evidence |

## Rules

- Treat `sources/**`, `cells/**`, `MAP.md`, `TRAIL.md`, `LINKS.md`, and
  `CONTRACT.md` as the memory.
- Treat `.tes/cortex/recall.sqlite` as rebuildable cache.
- Treat `.tes/cortex/semantic.sqlite` as rebuildable curation cache.
- Prefer MCP for read-only recall/read/curate/reflect when available.
- Never write `sources/**` after import.
- Never promote loose summaries; cells need `## Claim` and `## Evidence`.
- When `reflect.curation_due=true`, run `curate-plan` before proposing memory
  compaction, split, merge, or rejection.
- Never run `apply --yes` without explicit user authorization.
