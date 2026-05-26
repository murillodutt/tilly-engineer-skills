---
name: tes-cortex
description: Use when the user says /tes-cortex, /tes:cortex, /tes-curate, /tes:recall, /tes:learn, /tes:reflect, /tes:curate, or asks to inspect, audit, rebuild, query, read, learn from, reflect into, semantically curate, consolidate, or apply TES Cortex memory.
license: MIT
---

# TES Cortex

`/tes-cortex` is the preferred shared TES trigger for Cortex memory operations.
`/tes:cortex` is a compatible TES intent alias if the host reports it as an
invalid slash. The agent remains the executor; scripts and MCP tools are
oracles.

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
| operator health | run read-only `cortex_health` MCP or `cortex.py health` |
| operator peek | run read-only `cortex_peek` MCP or `cortex.py peek` |
| operator review | run read-only `cortex_review` MCP or `cortex.py review --backend lexical` |
| checkpoint progress | run `cortex.py checkpoint --yes`; writes only `.tes/checkpoints/**` |
| remember durable memory | run `cortex.py remember --yes` only with explicit approval and evidence |
| consolidate memory | run `consolidation_gate.py lock --yes`, then read-only `consolidation_gate.py certify` with observed write, review, rollback, and evidence |
| forget durable memory | run `cortex.py forget`; expect `BLOCKED` until consolidation gate exists |

## Rules

- Treat `sources/**`, `cells/**`, `MAP.md`, `TRAIL.md`, `LINKS.md`, and
  `CONTRACT.md` as the memory.
- Treat `.tes/cortex/recall.sqlite` as rebuildable cache.
- Treat `.tes/cortex/semantic.sqlite` as rebuildable curation cache.
- Prefer MCP for read-only recall/read/curate/reflect when available.
- Prefer MCP for read-only `health`, `peek`, and `review` when available.
- Never write `sources/**` after import.
- Never promote loose summaries; cells need `## Claim` and `## Evidence`.
- When `reflect.curation_due=true`, run `curate-plan` before proposing memory
  compaction, split, merge, or rejection.
- Never run `apply --yes` without explicit user authorization.
- Never run `remember --yes` without explicit user authorization and evidence.
- Never call consolidation `CERTIFIED` without a valid lock, approved review,
  rollback reference, allowed evidence, and observed Cortex cell write result.
- Do not treat `forget` as available destructive deletion; it is blocked until
  the consolidation gate owns observed-write and rollback evidence.
