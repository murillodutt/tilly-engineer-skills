---
tds_id: mesh.cortex_mcp
tds_class: mesh
status: active
consumer: MCP adapter authors, installer authors, and agents
source_of_truth: true
evidence_level: L2
tver: 0.5.0
---

# TES Cortex MCP

The Cortex MCP surface is a project-scoped access layer over the filesystem Cortex contract. It exposes governed remember by default and can be started read-only with `--read-only` when an operator wants inspection only.

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

The MCP server may read these files and may call deterministic Cortex helper functions. Read-only mode must not write cells, sources, maps, links, trail entries, runtime bootloaders, `.obsidian/**`, `.tes/cortex/recall.sqlite`, or `.tes/cortex/semantic.sqlite`. The governed write lane may write one new cell and the correlated Cortex index files only through the `remember` gate.

## Tools

The server is `scripts/cortex_mcp.py`. It uses stdio JSON-RPC by default and also supports opt-in localhost HTTP framing. It does not require third-party Python packages. Target projects activate it through project-scoped runtime config, never through global config mutation. The server target is fixed at process startup with `--target`; individual MCP tool calls do not accept a `target` argument.

| Tool | Behavior |
|------|----------|
| `cortex_verify` | Validate required Cortex files, directories, and contract terms |
| `cortex_health` | Inspect Cortex health and operator mutability classes without writing |
| `cortex_peek` | Read one Cortex cell or recall query results without writing |
| `cortex_review` | Run no-write Cortex audit, curation, and reflection review |
| `cortex_audit` | Detect broken links, missing evidence, unlisted cells, and orphans |
| `cortex_recall` | Search through SQLite FTS5 and fall back to `rg` |
| `cortex_read_cell` | Read one file under `docs/agents/cortex/cells/**` |
| `cortex_cell_history` | Structure existing `TRAIL.md` entries for one cell without writing |
| `cortex_absorb_plan` | Generate a no-write plan for a source under `sources/**` |
| `cortex_curate_plan` | Classify semantic curation risks without writing memory or derived indexes |
| `cortex_reflect` | Generate a no-write closure and curation proposal |
| `cortex_list_events` | List sanitized lifecycle ledger events without writing |
| `cortex_get_event_status` | Return one lifecycle event status by id without writing |
| `cortex_remember_plan` | Validate a no-write durable-memory proposal and return an exact approval phrase |
| `cortex_remember` | Write one new Cortex cell only after exact approval phrase match |

## Native MCP Capabilities

`initialize` advertises tools, resources, and prompts. Native resources expose cell Markdown only:

```text
tes-cortex://cells/<cell-ref>
```

`resources/list` enumerates files under `docs/agents/cortex/cells/**`, and `resources/read` returns on-disk Markdown bytes. It does not expose `MAP.md`, `LINKS.md`, `TRAIL.md`, `sources/**`, subscriptions, or writable resources.

Server-side prompts are inert templates surfaced through `prompts/list` and `prompts/get`:

```text
cortex/closure-reflection
cortex/curation-review
cortex/remember-checklist
```

Prompts never invoke tools, embed credentials, include target-specific paths, or mutate state. They are operator guidance only.

Long-running tools may emit advisory `notifications/progress` messages when a client supplies a progress token. Progress is best-effort and callback failure does not fail the tool result. The verify path uses an in-process mtime cache for hot reads; failures to compute the cache key fall back to uncached verify.

## Local Command

```bash
python3 scripts/cortex_mcp.py --target /path/to/project
python3 scripts/cortex_mcp.py --target /path/to/project --read-only
python3 scripts/cortex_mcp.py --target /path/to/project --transport http --port 8765
```

HTTP transport is opt-in. It binds to `127.0.0.1` by default, is stateless per request, uses the same JSON-RPC handler as stdio, honors `--read-only`, and requires an explicit `--allow-non-localhost` flag before binding outside localhost.

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
python3 scripts/install_mcp.py --target /path/to/project --adapter all --read-only --yes
python3 scripts/install_mcp.py --target /path/to/project --adapter all --transport http --port 8765 --yes
python3 scripts/install_mcp.py --target /path/to/project --adapter all --transport http --bearer-env TES_BEARER_TOKEN --yes
python3 scripts/install_mcp.py --self-test
```

Installed-target fallback repair, used by `/tes-doctor` when MCP health is the failing surface:

```bash
python3 .tes/bin/install_mcp.py --target . --adapter all --dry-run --overwrite --json-only
python3 .tes/bin/install_mcp.py --target . --adapter all --overwrite --yes
```

The assisted-installer `current` route is resolved to the detected runtime before calling the script. The script accepts `codex`, `claude`, `cursor`, `vscode`, or `all`. `all` prepares every certified project-scoped MCP config, including VS Code's workspace MCP file when no conflicting `tes-cortex` entry exists.

## Runtime Config

The activation path installs local MCP helpers into the target project:

```text
.tes/bin/install_mcp.py
.tes/bin/install_mcp_hosts/__init__.py
.tes/bin/install_mcp_hosts/base.py
.tes/bin/install_mcp_hosts/codex.py
.tes/bin/install_mcp_hosts/claude.py
.tes/bin/install_mcp_hosts/cursor.py
.tes/bin/install_mcp_hosts/vscode.py
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
| VS Code | `.vscode/mcp.json` |

Existing config is merged when the `tes-cortex` server name is absent. If a different `tes-cortex` entry already exists, activation stops unless the user explicitly passes `--overwrite`; backups are created by default. Generated server entries use the active Python executable as an absolute command, the installed `.tes/bin/cortex_mcp.py` helper as an absolute script argument, the target root as an absolute `--target` argument, and, for Codex, the target root as absolute `cwd`. This keeps project-scoped config portable across host process working directories without mutating global MCP config. For JSON-based runtimes, the installer validates the final registered server object after write: Claude Code and Cursor use `mcpServers.tes-cortex`; VS Code uses `servers.tes-cortex`, matching the VS Code workspace MCP schema.

Config registration is not the same as host recognition. A certification report must classify the highest observed state: `config_present`, `server_self_test_pass`, `protocol_handshake_pass`, `host_listed`, `host_connected`, or `session_restart_required`. Codex recognition is checked with `codex mcp list` from the target project when the CLI is available. Cursor and VS Code may require reload, approval, enable, or reconnect before a valid project config becomes visible in the host UI.

## Per-Host Installer Segmentation

The installer at `scripts/install_mcp.py` delegates to one adapter module per host under `scripts/install_mcp_hosts/`. Each adapter owns the host's exact schema for stdio, opt-in localhost HTTP, and bearer-env authenticated HTTP. The plan that introduced this segmentation lives at `docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-cortex-mcp-host-segmentation.md`.

Authoritative field matrix per host:

| Field | Codex `.codex/config.toml` | Claude `.mcp.json` | Cursor `.cursor/mcp.json` | VS Code `.vscode/mcp.json` |
|---|---|---|---|---|
| Root key | `[mcp_servers.<name>]` | `mcpServers.<name>` | `mcpServers.<name>` | `servers.<name>` |
| stdio discriminator | absence of `url` (untagged) | optional `type: "stdio"` | optional `type: "stdio"` | `type: "stdio"` |
| http discriminator | presence of `url` | `type: "http"` | `type: "http"` | `type: "http"` |
| `command` (stdio) | yes | yes | yes | yes |
| `args` (stdio) | yes | yes | yes | yes |
| `env` (stdio) | sub-table `[mcp_servers.<name>.env]` | object | object | object |
| `cwd` | yes | not supported | local only | yes |
| `url` (http) | yes | yes | yes | yes |
| HTTP headers | `http_headers` + `env_http_headers` | `headers` | `headers` | `headers` |
| Bearer auth | `bearer_token_env_var` | inline `headers.Authorization` | inline `headers.Authorization` | inline `headers.Authorization` with `${input:...}` |
| Timeouts | `startup_timeout_sec`, `tool_timeout_sec` | not exposed | not exposed | not exposed |
| Strict fields | `deny_unknown_fields` | tolerant | tolerant | tolerant |

Per-host forbidden-field guards, enforced before write:

| Host | stdio forbidden | http forbidden |
|------|-----------------|----------------|
| Codex | `url`, `bearer_token_env_var`, `http_headers`, `env_http_headers` | `command`, `args`, `env`, `cwd` |
| Claude | `url`, `headers`, `cwd` | `command`, `args`, `env`, `cwd` |
| Cursor | `url`, `headers`, `auth` | `command`, `args`, `env`, `cwd` |
| VS Code | `url`, `headers` | `command`, `args`, `env`, `cwd` |

HTTP transport contract:

- HTTP install is opt-in. Default remains stdio.
- Default URL is `http://127.0.0.1:8765/mcp`. Non-localhost URLs require `--allow-non-localhost`, mirroring the server-side guard.
- Codex HTTP installs use the `StreamableHttp` untagged variant of `McpServerTransportConfig`. Claude, Cursor, and VS Code use `{"type": "http", "url": "..."}` in their respective root keys.

Bearer-env authentication contract:

- `--bearer-env <NAME>` declares the environment variable that holds the bearer secret. The installer never reads, prints, or stores the secret value; only the variable name appears in generated config, the JSON report, and the event ledger.
- Codex emits `bearer_token_env_var = "<NAME>"`. The Rust runtime reads the variable at startup.
- Claude and Cursor emit `headers: {"Authorization": "Bearer ${env:<NAME>}"}` using each host's documented environment-interpolation form.
- VS Code emits `headers: {"Authorization": "Bearer ${input:<name>-token>}"}` following the VS Code workspace MCP `inputs` convention.

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
    - .tes/bin/install_mcp.py
    - .tes/bin/install_mcp_hosts/__init__.py
    - .tes/bin/install_mcp_hosts/base.py
    - .tes/bin/install_mcp_hosts/codex.py
    - .tes/bin/install_mcp_hosts/claude.py
    - .tes/bin/install_mcp_hosts/cursor.py
    - .tes/bin/install_mcp_hosts/vscode.py
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
    - .vscode/mcp.json
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

The cut above describes activation. Runtime `cortex_remember` writes are a separate ADR 0002 lane: one new `cells/**` file plus correlated `MAP.md`, `LINKS.md`, `TRAIL.md`, and derived recall index writes after exact approval. It does not grant permission to write `sources/**`, overwrite cells, delete memory, or mutate checkpoint/event state.

## Boundary

MCP activation is local and project-scoped. It installs governed remember by default and may install read-only config with `--read-only`; it must not edit global Codex, Claude, Cursor, or VS Code configuration, secrets, hooks, remotes, package lockfiles, `.obsidian/**`, or Cortex source material. Project scope is enforced at the MCP tool boundary: a server initialized for one project rejects caller-provided `target` overrides instead of resolving another project path.

MCP audit and recall preserve the same evidence boundary as the CLI. Valid Cortex cell evidence is limited to repository-relative refs under `sources/**`, `docs/agents/cortex/sources/**`, `docs/agents/evidence/**`, or an `Assumption:` line. Absolute paths, traversal refs, derived caches, checkpoints, run scratch, benchmark outputs, recall indexes, and semantic indexes are reported as evidence failures or non-memory artifacts; the MCP server must not repair them by writing memory.

Write-capable MCP is limited to the ADR 0002 governed lane. `learn` and `apply` stay CLI-governed. `cortex_remember_plan` is no-write; `cortex_remember` requires a new cell, explicit evidence, and the exact approval phrase tied to the planned payload. The read-only operator tools `cortex_health`, `cortex_peek`, `cortex_review`, `cortex_list_events`, and `cortex_get_event_status` are allowed. `checkpoint`, `forget`, update, delete, bulk delete, entity delete, direct `apply`, and automatic writes remain outside MCP. The MCP self-test includes negative calls for unknown write-like tools, invalid argument shapes, path traversal, target overrides, invalid curation backends, and empty required arguments. It also verifies that tool schemas do not expose a `target` property and that a second project cannot be read through caller input. `cortex_curate_plan` is required to report no writes and no derived semantic-index writes over MCP. Resources, prompts, progress notifications, verify cache, optional HTTP, and `cortex_cell_history` add no memory authority: they are read-only, inert, advisory, cached, or opt-in transport surfaces.
