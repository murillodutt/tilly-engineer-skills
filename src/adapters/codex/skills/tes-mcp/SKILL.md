---
name: tes-mcp
description: Use when the user says /tes-mcp, /tes:mcp, or asks to activate, verify, repair, audit, or explain the TES Cortex MCP server for Codex, Claude, Cursor, VS Code, or all runtimes.
---

# TES MCP

`/tes-mcp` and `/tes:mcp` are explicit shortcuts for project-scoped Cortex MCP
activation, repair, host-recognition checks, and VS Code MCP registration.
Normal first registration for Codex, Claude Code, and Cursor comes from the
`npx`/`bunx` installer; this skill is the focused MCP route after install or
when the user asks for MCP directly.

## Module Map

| Surface | Load when |
|---------|-----------|
| `docs/CONTRACT-HISTORY.md` | Host recognition states or MCP failure modes |

## Workflow

1. Identify the selected runtime route: `current`, `codex`, `claude`,
   `cursor`, `vscode`, or `all`.
2. Confirm the target project path.
3. Use `install_mcp.py --dry-run` when reviewing changes.
4. Use `install_mcp.py --target <project> --adapter <route> --yes` only when
   activation is authorized.
5. Add `--read-only` only when the user explicitly requests inspection-only
   MCP; default activation exposes governed Cortex remember.
6. Run `install_mcp.py --self-test`, `cortex_mcp.py --self-test`, or
   `install_smoke.py --route mcp` as the local oracle.
7. Report created or merged project-scoped config paths and classify host
   recognition separately.
8. If the user asks for full installed TES certification, hand off to
   `/tes-doctor` or run `installed_certification_oracle.py`; `/tes-mcp` may
   repair MCP drift, but MCP success alone is not a clean install `PASS`.

## Host Recognition

Do not call MCP functional from config file presence alone. Report these states
when evidence is available:

- `config_present`: project-scoped MCP file contains `tes-cortex`.
- `server_self_test_pass`: `cortex_mcp.py --self-test` passes.
- `protocol_handshake_pass`: direct MCP initialize/tools-list returns tools.
- `host_listed`: the host lists `tes-cortex`.
- `host_connected`: the host exposes the TES Cortex tools.
- `session_restart_required`: config is valid, but the active host session was
  started outside the target workspace or has not reloaded project MCP config.

For Codex, run `codex mcp list` from the target project when available. Codex
supports user-level `~/.codex/config.toml` and project-scoped
`.codex/config.toml` in trusted projects; TES defaults to project-scoped config.
Do not edit global Codex MCP config unless the user explicitly requests that
scope.

For Cursor and VS Code, a valid project MCP file may still require the host to
reload, approve, enable, or reconnect the project server before tools appear.

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
