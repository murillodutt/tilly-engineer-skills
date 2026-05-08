---
tds_id: mesh.cortex_mcp
tds_class: mesh
status: active
consumer: MCP adapter authors, installer authors, and agents
source_of_truth: true
evidence_level: L2
tver: 0.3.3
---

# TES Cortex MCP

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
bootloaders, `.obsidian/**`, `.tes/cortex/recall.sqlite`, or
`.tes/cortex/semantic.sqlite` except through explicit local CLI commands, not
by the v1 MCP tools.

## Tools

The read-only server is `scripts/cortex_mcp.py`. It uses stdio JSON-RPC and
does not require third-party Python packages. Target projects activate it
through project-scoped runtime config, never through global config mutation.

| Tool | Behavior |
|------|----------|
| `cortex_verify` | Validate required Cortex files, directories, and contract terms |
| `cortex_audit` | Detect broken links, missing evidence, unlisted cells, and orphans |
| `cortex_recall` | Search through SQLite FTS5 and fall back to `rg` |
| `cortex_read_cell` | Read one file under `docs/agents/cortex/cells/**` |
| `cortex_absorb_plan` | Generate a no-write plan for a source under `sources/**` |
| `cortex_curate_plan` | Classify semantic curation risks without writing memory or derived indexes |
| `cortex_reflect` | Generate a no-write closure and curation proposal |

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

Project-scoped activation:

```bash
python3 scripts/install_mcp.py --target /path/to/project --adapter codex --yes
python3 scripts/install_mcp.py --target /path/to/project --adapter all --yes
python3 scripts/install_mcp.py --self-test
```

The assisted-installer `current` route is resolved to the detected runtime
before calling the script. The script accepts `codex`, `claude`, `cursor`, or
`all`.

## Runtime Config

The activation path installs local MCP helpers into the target project:

```text
.tes/bin/cortex.py
.tes/bin/cortex_mcp.py
.tes/bin/cortex_embed.mjs
.tes/bin/field_reports.py
.tes/bin/tes_update.py
.tes/bin/tes_legacy_retirement.py
.tes/bin/root_context.py
```

It then writes only project-scoped config for the selected runtime:

| Runtime | Project config |
|---------|----------------|
| Codex | `.codex/config.toml` |
| Claude Code | `.mcp.json` |
| Cursor | `.cursor/mcp.json` |

Existing config is merged when the `tes-cortex` server name is absent. If a
different `tes-cortex` entry already exists, activation stops unless the user
explicitly passes `--overwrite`; backups are created by default.

## MCP Cut

```yaml
cortex_cut:
  consumer: MCP-capable agents
  camada: mcp
  escreve_em:
    - .tes/bin/cortex.py
    - .tes/bin/cortex_mcp.py
    - .tes/bin/cortex_embed.mjs
    - .tes/bin/field_reports.py
    - .tes/bin/tes_update.py
    - .tes/bin/tes_legacy_retirement.py
    - .tes/bin/root_context.py
    - .codex/config.toml
    - .mcp.json
    - .cursor/mcp.json
  nao_toca:
    - docs/agents/cortex/sources/**
    - docs/agents/cortex/cells/**
    - docs/agents/cortex/MAP.md
    - docs/agents/cortex/TRAIL.md
    - docs/agents/cortex/LINKS.md
    - .tes/cortex/semantic.sqlite
    - .obsidian/**
  oracle: python3 scripts/install_mcp.py --self-test
  rollback: git revert <commit>
```

## Boundary

MCP activation is local, read-only, and project-scoped. It must not edit global
Codex, Claude, or Cursor configuration, secrets, hooks, remotes, package
lockfiles, `.obsidian/**`, or Cortex source material.

Write-capable MCP tools remain outside v1. `learn` and `apply` stay CLI-governed
because promotion into Cortex requires explicit evidence and authorization.
The MCP self-test includes negative calls for unknown write-like tools, invalid
argument shapes, path traversal, invalid targets, invalid curation backends, and
empty required arguments. `cortex_curate_plan` is required to report no writes
and no derived semantic-index writes over MCP.
