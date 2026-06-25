---
name: tes-cortex
description: Use when the user says /tes-cortex, /tes:cortex, /tes-curate, /tes:recall, /tes:learn, /tes:reflect, /tes:curate, or asks to inspect, audit, rebuild, query, read, learn from, reflect into, semantically curate, consolidate, or apply TES Cortex memory.
---

# TES Cortex

`/tes-cortex` and `/tes:cortex` are user-facing shortcuts for Cortex memory operations. The agent remains the executor; scripts and MCP tools are oracles.

## Module Map

| Surface | Load when |
|---------|-----------|
| `docs/CONTRACT-HISTORY.md` | Memory boundaries or governed-write lanes |

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
| event inspection | use read-only `cortex_list_events` or `cortex_get_event_status` MCP |
| checkpoint progress | run `cortex.py checkpoint --yes`; writes only `.tes/checkpoints/**` |
| remember durable memory | run `cortex.py remember --yes` only with explicit approval and evidence |
| governed MCP remember | use `cortex_remember_plan`, obtain explicit approval for its phrase, then call `cortex_remember` |
| consolidate memory | run `consolidation_gate.py lock --yes`, then read-only `consolidation_gate.py certify` with observed write, review, rollback, and evidence |
| forget durable memory | run `cortex.py forget`; expect `BLOCKED` until consolidation gate exists |

## Rules

- Treat `sources/**`, `cells/**`, `MAP.md`, `TRAIL.md`, `LINKS.md`, and `CONTRACT.md` as the memory.
- Treat `.tes/cortex/recall.sqlite` as rebuildable cache.
- Treat `.tes/cortex/semantic.sqlite` as rebuildable curation cache.
- Prefer MCP for read-only recall/read/curate/reflect when available.
- Prefer MCP for read-only `health`, `peek`, and `review` when available.
- Prefer MCP event tools only for read-only lifecycle evidence inspection.
- Never write `sources/**` after import.
- Never promote loose summaries; cells need `## Claim` and `## Evidence`.
- When `reflect.curation_due=true`, run `curate-plan` before proposing memory compaction, split, merge, or rejection.
- Never run `apply --yes` without explicit user authorization.
- Never run `remember --yes` without explicit user authorization and evidence.
- Never call `cortex_remember` unless the user approved the exact plan phrase; read-only MCP mode intentionally hides the tool.
- Never call consolidation `CERTIFIED` without a valid lock, approved review, rollback reference, allowed evidence, and observed Cortex cell write result.
- Do not treat `forget` as available destructive deletion; it is blocked until the consolidation gate owns observed-write and rollback evidence.
