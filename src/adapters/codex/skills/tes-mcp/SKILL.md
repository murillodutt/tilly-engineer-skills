---
name: tes-mcp
description: Use when the user says /tes-mcp, /tes:mcp, or asks to activate, verify, repair, audit, or explain the TES Cortex MCP server for Codex, Claude, Cursor, or all runtimes.
---

# TES MCP

`/tes-mcp` and `/tes:mcp` are shortcuts for project-scoped Cortex MCP
activation and health checks.

## Workflow

1. Identify the selected runtime route: `current`, `codex`, `claude`,
   `cursor`, or `all`.
2. Confirm the target project path.
3. Use `install_mcp.py --dry-run` when reviewing changes.
4. Use `install_mcp.py --target <project> --adapter <route> --yes` only when
   activation is authorized.
5. Add `--read-only` only when the user explicitly requests inspection-only
   MCP; default activation exposes governed Cortex remember.
6. Run `install_mcp.py --self-test`, `cortex_mcp.py --self-test`, or
   `install_smoke.py --route mcp` as the local oracle.
7. Report created or merged project-scoped config paths.

The always-safe inspection surface includes `cortex_verify`, `cortex_audit`,
`cortex_recall`, `cortex_read_cell`, `cortex_absorb_plan`,
`cortex_curate_plan`, `cortex_reflect`, `cortex_list_events`, and
`cortex_get_event_status`.

The governed write surface includes only `cortex_remember_plan` and
`cortex_remember`; it requires exact approval phrase match, claim, evidence,
and a new cell.

## Locks

- Do not edit global MCP config.
- Do not expose write-capable MCP tools outside the ADR 0002 governed remember
  lane.
- Do not touch secrets, env files, hooks, remotes, or cloud settings.
- Do not call MCP, SQLite, event ledger, or LLM output "memory"; Cortex
  Markdown remains the source of truth.
- Do not expose update, delete, bulk delete, entity delete, checkpoint write,
  direct apply, or automatic writes through MCP.
- Treat `.tes/bin/cortex_embed.mjs` as a local helper for optional neural
  curation, not as a memory source.
