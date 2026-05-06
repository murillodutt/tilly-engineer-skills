---
tds_id: mesh.cortex_mcp
tds_class: mesh
status: active
consumer: MCP adapter authors, installer authors, and agents
source_of_truth: true
evidence_level: L2
tver: 0.1.0
---

# Tilly Cortex MCP

The Cortex MCP surface is a read-only access layer over the filesystem Cortex
contract. It exposes recall and inspection tools to MCP-capable runtimes without
turning the MCP server into memory.

## Contract

Source of truth remains:

```text
docs/agents/cortex/CONTRACT.md
docs/agents/cortex/MAP.md
docs/agents/cortex/TRAIL.md
docs/agents/cortex/LINKS.md
docs/agents/cortex/sources/**
docs/agents/cortex/cells/**
```

The MCP server may read these files and may call the deterministic Cortex CLI
functions. It must not write cells, sources, maps, links, trail entries, runtime
bootloaders, `.obsidian/**`, or `.tilly/cortex/recall.sqlite` except through an
explicit local rebuild command exposed by the CLI, not by the v1 MCP tools.

## Tools

The read-only v1 server is `scripts/cortex_mcp.py`. It uses stdio JSON-RPC and
does not require third-party Python packages.

| Tool | Behavior |
|------|----------|
| `cortex_verify` | Validate required Cortex files, directories, and contract terms |
| `cortex_audit` | Detect broken links, missing evidence, unlisted cells, and orphans |
| `cortex_recall` | Search through SQLite FTS5 and fall back to `rg` |
| `cortex_read_cell` | Read one file under `docs/agents/cortex/cells/**` |
| `cortex_absorb_plan` | Generate a no-write plan for a source under `sources/**` |

## Local Command

```bash
python3 scripts/cortex_mcp.py --target /path/to/project
```

Self-test:

```bash
python3 scripts/cortex_mcp.py --self-test
```

Package script:

```bash
npm run cortex:mcp:self-test
```

## MCP Cut

```yaml
cortex_cut:
  consumer: MCP-capable agents
  camada: mcp
  escreve_em: []
  nao_toca:
    - docs/agents/cortex/sources/**
    - docs/agents/cortex/cells/**
    - docs/agents/cortex/MAP.md
    - docs/agents/cortex/TRAIL.md
    - docs/agents/cortex/LINKS.md
    - .obsidian/**
  oracle: python3 scripts/cortex_mcp.py --self-test
  rollback: git revert <commit>
```

## Boundary

This cut does not add MCP configuration files for Codex, Claude, or Cursor. Each
target project should opt in explicitly after the local CLI and MCP smoke pass.
Write-capable MCP tools remain outside v1.
