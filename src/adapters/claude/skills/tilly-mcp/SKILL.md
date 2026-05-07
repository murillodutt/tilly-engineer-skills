---
name: tilly-mcp
description: Use when the user says /tilly:mcp or asks to activate, verify, repair, audit, or explain the read-only Tilly Cortex MCP server for Codex, Claude, Cursor, or all runtimes.
license: MIT
---

# Tilly MCP

`/tilly:mcp` is the shortcut for project-scoped Cortex MCP activation and
health checks.

## Workflow

1. Identify the selected runtime route: `current`, `codex`, `claude`,
   `cursor`, or `all`.
2. Confirm the target project path.
3. Use `install_mcp.py --dry-run` when reviewing changes.
4. Use `install_mcp.py --target <project> --adapter <route> --yes` only when
   activation is authorized.
5. Run `install_mcp.py --self-test`, `cortex_mcp.py --self-test`, or
   `install_smoke.py --route mcp` as the local oracle.
6. Report created or merged project-scoped config paths.

The read-only surface includes `cortex_verify`, `cortex_audit`,
`cortex_recall`, `cortex_read_cell`, `cortex_absorb_plan`,
`cortex_curate_plan`, and `cortex_reflect`.

## Locks

- Do not edit global MCP config.
- Do not create write-capable MCP tools.
- Do not touch secrets, env files, hooks, remotes, or cloud settings.
- Do not call MCP, SQLite, or LLM output "memory"; MCP is access only.
- Treat `.tilly/bin/cortex_embed.mjs` as a local helper for optional neural
  curation, not as a memory source.
