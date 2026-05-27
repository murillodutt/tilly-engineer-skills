---
tds_id: mesh.cortex_mcp
tds_class: mesh
status: active
consumer: MCP adapter authors, installer authors, and agents
source_of_truth: true
evidence_level: L2
tver: 0.4.0
---

# TES Cortex MCP

The Cortex MCP surface is a project-scoped access layer over the filesystem
Cortex contract. It is read-only by default and exposes an optional governed
write lane only when the server starts with `--enable-writes`.

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

The MCP server may read these files and may call deterministic Cortex helper
functions. Default activation must not write cells, sources, maps, links, trail
entries, runtime bootloaders, `.obsidian/**`, `.tes/cortex/recall.sqlite`, or
`.tes/cortex/semantic.sqlite`. The opt-in governed write lane may write one new
cell and the correlated Cortex index files only through the `remember` gate.

## Tools

The server is `scripts/cortex_mcp.py`. It uses stdio JSON-RPC and does not
require third-party Python packages. Target projects activate it through
project-scoped runtime config, never through global config mutation. The server
target is fixed at process startup with `--target`; individual MCP tool calls
do not accept a `target` argument.

| Tool | Behavior |
|------|----------|
| `cortex_verify` | Validate required Cortex files, directories, and contract terms |
| `cortex_audit` | Detect broken links, missing evidence, unlisted cells, and orphans |
| `cortex_recall` | Search through SQLite FTS5 and fall back to `rg` |
| `cortex_read_cell` | Read one file under `docs/agents/cortex/cells/**` |
| `cortex_absorb_plan` | Generate a no-write plan for a source under `sources/**` |
| `cortex_curate_plan` | Classify semantic curation risks without writing memory or derived indexes |
| `cortex_reflect` | Generate a no-write closure and curation proposal |
| `cortex_list_events` | List sanitized lifecycle ledger events without writing |
| `cortex_get_event_status` | Return one lifecycle event status by id without writing |
| `cortex_remember_plan` | With `--enable-writes`, validate a no-write durable-memory proposal and return an exact approval phrase |
| `cortex_remember` | With `--enable-writes`, write one new Cortex cell only after exact approval phrase match |

## Local Command

```bash
python3 scripts/cortex_mcp.py --target /path/to/project
python3 scripts/cortex_mcp.py --target /path/to/project --enable-writes
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
python3 scripts/install_mcp.py --target /path/to/project --adapter all --enable-writes --yes
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
.tes/bin/scope_contract.py
.tes/bin/event_ledger.py
.tes/bin/checkpoint.py
.tes/bin/field_reports.py
.tes/bin/mantra_gate.py
.tes/bin/mantra_gate_adoption_oracle.py
.tes/bin/tes_install.py
.tes/bin/tes_update.py
.tes/bin/tes_legacy_retirement.py
.tes/bin/root_context.py
.tes/bin/tes_init.py
.tes/bin/project_context_oracle.py
.tes/bin/project_alignment_oracle.py
.tes/bin/tes_map.py
.tes/bin/tes_map_oracle.py
.tes/bin/tes_open_obsidian.py
.tes/bin/command_trigger_oracle.py
.tes/bin/tes_bundle.py
.tes/bin/materialize_adapter.py
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
    - .tes/bin/scope_contract.py
    - .tes/bin/event_ledger.py
    - .tes/bin/checkpoint.py
    - .tes/bin/field_reports.py
    - .tes/bin/mantra_gate.py
    - .tes/bin/mantra_gate_adoption_oracle.py
    - .tes/bin/tes_install.py
    - .tes/bin/tes_update.py
    - .tes/bin/tes_legacy_retirement.py
    - .tes/bin/root_context.py
    - .tes/bin/tes_init.py
    - .tes/bin/project_context_oracle.py
    - .tes/bin/project_alignment_oracle.py
    - .tes/bin/tes_map.py
    - .tes/bin/tes_map_oracle.py
    - .tes/bin/tes_open_obsidian.py
    - .tes/bin/command_trigger_oracle.py
    - .tes/bin/tes_bundle.py
    - .tes/bin/materialize_adapter.py
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

The cut above describes activation. Runtime `cortex_remember` writes are a
separate ADR 0002 lane: one new `cells/**` file plus correlated `MAP.md`,
`LINKS.md`, `TRAIL.md`, and derived recall index writes after exact approval.
It does not grant permission to write `sources/**`, overwrite cells, delete
memory, or mutate checkpoint/event state.

## Boundary

MCP activation is local and project-scoped. It installs read-only config by
default. `--enable-writes` is an explicit opt-in that adds only the governed
remember lane; it must not edit global Codex, Claude, or Cursor configuration,
secrets, hooks, remotes, package lockfiles, `.obsidian/**`, or Cortex source
material.
Project scope is enforced at the MCP tool boundary: a server initialized for
one project rejects caller-provided `target` overrides instead of resolving
another project path.

MCP audit and recall preserve the same evidence boundary as the CLI. Valid
Cortex cell evidence is limited to repository-relative refs under `sources/**`,
`docs/agents/cortex/sources/**`, `docs/agents/evidence/**`, or an
`Assumption:` line. Absolute paths, traversal refs, derived caches, checkpoints,
run scratch, benchmark outputs, recall indexes, and semantic indexes are
reported as evidence failures or non-memory artifacts; the MCP server must not
repair them by writing memory.

Write-capable MCP is limited to the ADR 0002 governed lane. `learn` and
`apply` stay CLI-governed. `cortex_remember_plan` is no-write; `cortex_remember`
requires `--enable-writes`, a new cell, explicit evidence, and the exact
approval phrase tied to the planned payload. The read-only operator tools
`cortex_health`, `cortex_peek`, `cortex_review`, `cortex_list_events`, and
`cortex_get_event_status` are allowed. `checkpoint`, `forget`, update, delete,
bulk delete, entity delete, direct `apply`, and automatic writes remain outside
MCP.
The MCP self-test includes negative calls for unknown write-like tools, invalid
argument shapes, path traversal, target overrides, invalid curation backends,
and empty required arguments. It also verifies that tool schemas do not expose a
`target` property and that a second project cannot be read through caller input.
`cortex_curate_plan` is required to report no writes and no derived
semantic-index writes over MCP.
