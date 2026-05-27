---
tds_id: evidence.cortex_mcp_vscode_config_parity_20260527
tds_class: evidence
status: active
consumer: maintainers, installer authors, MCP operators, and release reviewers
source_of_truth: false
evidence_level: L2
tver: 0.1.0
---

# Cortex MCP VS Code Config Parity

## Summary

A private canary project exposed a TES installer false green: MCP activation
could pass while a project-scoped VS Code MCP file remained unregistered for
`tes-cortex`. The portable finding is not project-specific. It is an installer
contract gap: activation must validate the final MCP registration surface, not
only helper presence or adapter route completion.

## Mantra Gate

| Field | Record |
|-------|--------|
| `VERIFY` | Reproduced with a neutral temporary project containing an existing non-TES `.vscode/mcp.json` server. |
| `SCOPE` | `scripts/install_mcp.py`, install smoke/oracle coverage, MCP docs, release identity, and evidence. |
| `BEST_PATH` | Add VS Code as an MCP config route, preserve existing `servers`, and validate final `tes-cortex` registration after write. |
| `DOCUMENT` | This report plus correlated MCP/install docs. |
| `ORACLE` | `python3 scripts/install_mcp.py --self-test`, focused repro fixture, and package gates. |
| `RESOLVE` | Delivered behavior requires patch release identity. |
| `STATUS` | `PASS` after focused oracle. |

## Evidence

Before the fix, a neutral fixture with `.vscode/mcp.json` containing an
unrelated HTTP MCP server returned install success but left only the existing
server in `servers`.

After the fix, the same fixture returns install success and the file contains
both the existing server and `tes-cortex`.

The installer now validates registered config after write:

- Codex: `.codex/config.toml` with `mcp_servers.tes-cortex`.
- Claude Code: `.mcp.json` with `mcpServers.tes-cortex`.
- Cursor: `.cursor/mcp.json` with `mcpServers.tes-cortex`.
- VS Code: `.vscode/mcp.json` with `servers.tes-cortex`.

## Boundary

VS Code support is MCP-consumer support only. It does not add a fourth TES
adapter, VS Code skills, VS Code hooks, VS Code bootloaders, marketplace
publishing, remote action, cloud action, global MCP mutation, or any write lane
beyond ADR 0002 governed remember.

## Closure

Release identity: patch bump required because adopter-visible MCP installer
behavior changed.

Focused oracles:

```bash
python3 scripts/install_mcp.py --self-test
python3 scripts/install_smoke.py --self-test
python3 scripts/platform_surface_oracle.py --self-test
```

Status: `PASS`.
