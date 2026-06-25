---
tds_id: evidence.context_mesh.cortex_mcp_activation_2026_05_06
tds_class: evidence
status: active
consumer: installer authors, MCP adapter authors, and certification reviewers
source_of_truth: false
evidence_level: L3
---

# Cortex MCP Activation Report

This report records the first project-scoped Cortex MCP activation cut on May 6, 2026.

Correction note, May 26, 2026: current helper installation uses `.tes/bin/**`. Older `.tilly/bin/**` references were stale path vocabulary, not the active runtime contract.

## Claim

The assisted installer can activate the read-only Cortex MCP server for target projects without relying on manual post-install configuration.

## Scope

| Surface | Status |
|---------|--------|
| Local server helpers | `.tes/bin/cortex.py`, `.tes/bin/cortex_mcp.py` |
| Codex project config | `.codex/config.toml` |
| Claude Code project config | `.mcp.json` |
| Cursor project config | `.cursor/mcp.json` |

## Evidence

| Oracle | Result |
|--------|--------|
| `python3 scripts/install_mcp.py --self-test` | PASS |
| `python3 scripts/install_mcp.py --target /tmp --adapter all --dry-run` | PASS |
| `python3 scripts/validate_reference_package.py` | PASS |
| `python3 scripts/validate_tds.py` | PASS |
| HTML parse of `docs/install/USER-MANUAL.html` | PASS |

## External Runtime Basis

| Runtime | Project-scoped basis |
|---------|----------------------|
| Codex | Official Codex MCP docs describe project-scoped `.codex/config.toml` for trusted projects |
| Claude Code | Official Claude Code MCP docs describe project-scoped `.mcp.json` |
| Cursor | Official Cursor MCP docs describe project `.cursor/mcp.json` |

## Non-Claims

- This does not add write-capable MCP tools.
- This does not edit global runtime configuration.
- This does not certify third-party MCP servers.
- This does not make SQLite, MCP, Obsidian, or LLM output the Cortex memory.

## Rollback

Use Git to revert this cut, or remove the project-scoped activation files from the target project:

```bash
git revert <install-commit>
rm -f .tes/bin/cortex.py .tes/bin/cortex_mcp.py
```
