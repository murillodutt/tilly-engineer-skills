---
tds_id: roadmap.cortex_mcp_host_segmentation.execution_units
tds_class: roadmap
status: active
consumer: maintainers, Cortex MCP authors, installer authors, host integration authors, release reviewers, and execution agents
source_of_truth: false
evidence_level: L1
tver: 0.1.0
---

# Cortex MCP Host Segmentation Execution Units

This document is the execution-detail companion to `docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-cortex-mcp-host-segmentation.md`.

Read the canonical Super SPEC first. Use this file only for the current execution unit, so the installer can advance in small auditable waves without turning planning detail into runtime behavior.

## SPEC-000 Preflight And Boundary

Objective: prove that this segmentation is an ADR 0003 installer-surface implementation, not a new server authority.

Allowed files:

- `docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-cortex-mcp-host-segmentation.md`
- `docs/roadmap/cortex-mcp-host-segmentation/EXECUTION-UNITS.md`
- `docs/mesh/**`
- `docs/tds/DOCS-INDEX.yml`
- `docs/INDEX.md`
- `docs/roadmap/README.md`

Forbidden:

- Runtime implementation.
- `scripts/install_mcp.py` or `scripts/cortex_mcp.py` edits.
- Package version bump.
- Remote, publish, push, or bundle updates.

Focused oracles:

- `python3 scripts/validate_tds.py`
- `python3 scripts/validate_doc_size.py`
- `python3 scripts/validate_reference_graph.py`
- `git diff --check`

Done when the Super SPEC and this companion are indexed in `docs/INDEX.md`, `docs/roadmap/README.md`, and `docs/tds/DOCS-INDEX.yml`.

## SPEC-001 HostAdapter Base And Skeleton Modules

Objective: introduce the per-host module structure without moving behavior.

Owned files:

- `scripts/install_mcp_hosts/__init__.py`
- `scripts/install_mcp_hosts/base.py`
- `scripts/install_mcp_hosts/codex.py`
- `scripts/install_mcp_hosts/claude.py`
- `scripts/install_mcp_hosts/cursor.py`
- `scripts/install_mcp_hosts/vscode.py`

Contract:

- `base.py` exposes a `HostAdapter` class with `name`, `config_path`, `supports_cwd`, `supports_http`, `supports_sse`, `supports_timeouts`, `supports_auth_block`, plus method stubs `build_stdio`, `build_http`, `merge_into_existing`, `validate_registered`.
- `__init__.py` exposes a `HOSTS` registry keyed by adapter name.
- Adapter modules subclass `HostAdapter` and raise `NotImplementedError` for behavior that will be migrated in SPEC-002 to SPEC-004.

Forbidden:

- Editing `scripts/install_mcp.py` behavior. The orchestrator stays unchanged in SPEC-001.

Focused oracles:

- `python3 -c "from install_mcp_hosts import HOSTS; assert set(HOSTS) == {'codex','claude','cursor','vscode'}"` via `PYTHONPATH=scripts`.
- `python3 scripts/install_mcp.py --self-test`
- `python3 scripts/cortex_mcp.py --self-test`

Done when the new modules exist, the registry resolves, and the existing self-tests still pass.

## SPEC-002 Migrate Codex

Objective: move Codex TOML logic into `install_mcp_hosts/codex.py` with byte-identical output.

Owned files:

- `scripts/install_mcp_hosts/codex.py`
- `scripts/install_mcp.py` (delegation only)

Contract:

- `codex.py` owns `codex_snippet`, `merge_codex_config`, and the Codex branch of `validate_config_registration`.
- `install_mcp.py` calls into the registry instead of hard-coding the Codex branch in `install_configs` and `validate_config_registrations`.
- The generated TOML must be byte-identical to the pre-refactor output for default stdio installs.

Focused oracles:

- A new golden self-test asserts the exact string emitted by `CodexHost().build_stdio(...)` for a fixed target, including `[mcp_servers.tes-cortex]`, `command`, `args`, `cwd`, `startup_timeout_sec`, `tool_timeout_sec`, and `enabled`.
- `python3 scripts/install_mcp.py --self-test`
- `python3 scripts/cortex_mcp.py --self-test`

Done when the Codex branch is removed from `install_mcp.py` and the golden self-test passes.

## SPEC-003 Migrate Claude Code And Cursor

Objective: split the shared JSON builder into Claude and Cursor adapters with byte-identical stdio output.

Owned files:

- `scripts/install_mcp_hosts/claude.py`
- `scripts/install_mcp_hosts/cursor.py`
- `scripts/install_mcp.py` (delegation only)

Contract:

- `claude.py` owns `mcpServers.tes-cortex` for `.mcp.json` with `type: "stdio"`, `command`, `args`, `env: {}`. Never emits `cwd`.
- `cursor.py` owns `mcpServers.tes-cortex` for `.cursor/mcp.json` with `type: "stdio"`, `command`, `args`, `env: {}`. Keeps absolute paths and does not introduce `${workspaceFolder}` interpolation in stdio mode.
- Both delegate `merge_into_existing` to a shared JSON helper inside `base.py` that preserves existing servers.
- `install_mcp.py` resolves the adapter by name and calls `HostAdapter.merge_into_existing`.

Focused oracles:

- Golden self-tests assert the exact dict emitted by `ClaudeHost().build_stdio(...)` and `CursorHost().build_stdio(...)`.
- `python3 scripts/install_mcp.py --self-test`
- `python3 scripts/cortex_mcp.py --self-test`

Done when the shared JSON branch is removed from `install_mcp.py` for Claude and Cursor, golden self-tests pass, and stdio output is identical.

## SPEC-004 Migrate VS Code And Close Wave 1

Objective: migrate VS Code and finish Wave 1 with full per-host golden coverage.

Owned files:

- `scripts/install_mcp_hosts/vscode.py`
- `scripts/install_mcp.py` (delegation only)
- `tests` only if a separate test file is needed; otherwise self-test inside `install_mcp.py`.

Contract:

- `vscode.py` owns `servers.tes-cortex` for `.vscode/mcp.json` with `type: "stdio"`, `command`, `args`, `env: {}`. Uses the `servers` root key per the VS Code workspace MCP schema.
- The shared JSON helper in `base.py` accepts an `existing_servers_key` parameter so VS Code can reuse the merge logic without aliasing.
- `install_mcp.py` no longer hard-codes any host branch.
- A consolidated golden self-test asserts every adapter's stdio output for a fixed target path.

Focused oracles:

- `python3 scripts/install_mcp.py --self-test`
- `python3 scripts/cortex_mcp.py --self-test`
- `npm run commit:check`

Done when all four adapters live in their modules, the orchestrator is host-agnostic, and the consolidated golden self-test passes.

## SPEC-005 HTTP Transport

Objective: add `--transport http --port` to the installer and `build_http` to every adapter.

Owned files:

- `scripts/install_mcp.py`
- `scripts/install_mcp_hosts/codex.py`
- `scripts/install_mcp_hosts/claude.py`
- `scripts/install_mcp_hosts/cursor.py`
- `scripts/install_mcp_hosts/vscode.py`
- `docs/mesh/CORTEX-MCP.md`

Contract:

- `install_mcp.py` adds `--transport stdio|http`, `--port` (default 8765), `--host` (default `127.0.0.1`), and `--allow-non-localhost`. Non-localhost hosts are rejected without `--allow-non-localhost`, mirroring the server.
- `CodexHost.build_http` emits the `StreamableHttp` variant with `url` only. No `command`, `args`, or `cwd`.
- `ClaudeHost.build_http`, `CursorHost.build_http`, and `VSCodeHost.build_http` emit `{"type": "http", "url": "..."}`.
- The mesh doc adds an HTTP transport section per host and references this Super SPEC.

Focused oracles:

- The installer self-test now covers a `stdio × http × read-only` matrix per host.
- `python3 scripts/install_mcp.py --self-test`
- `python3 scripts/cortex_mcp.py --self-test`
- `npm run commit:check`

Done when HTTP installs work for all four hosts, registered server objects on disk match the host adapter contract, and the mesh doc reflects the new surface.

## SPEC-006 Strict Validation And Forbidden Fields

Objective: tighten per-host validation so silent drift is impossible.

Owned files:

- `scripts/install_mcp_hosts/codex.py`
- `scripts/install_mcp_hosts/claude.py`
- `scripts/install_mcp_hosts/cursor.py`
- `scripts/install_mcp_hosts/vscode.py`
- `docs/mesh/CORTEX-MCP.md`

Contract:

- Each adapter exposes `allowed_fields()` and `forbidden_fields()` for both stdio and http modes.
- Codex validates against the closed `StreamableHttp` field set before write and rejects unknown fields, mirroring `deny_unknown_fields`.
- Claude asserts `cwd` is never emitted in any mode.
- Cursor asserts `cwd` is never emitted in HTTP mode and stays absolute in stdio mode.
- VS Code asserts `servers` (not `mcpServers`) is the root key and that `inputs` stays opt-in.
- Mesh doc gains a forbidden-field row per host and a short rationale.

Focused oracles:

- Negative self-tests assert that injecting `unknown_field` for Codex, emitting `cwd` for Claude, swapping root key for VS Code, or emitting `cwd` for Cursor HTTP all fail before write.
- `python3 scripts/install_mcp.py --self-test`
- `python3 scripts/cortex_mcp.py --self-test`
- `npm run commit:check`

Done when negative self-tests cover every forbidden field per host and the mesh doc reflects the rationale.

## SPEC-007 Bearer-Env Authenticated HTTP

Objective: add bearer-env authenticated HTTP without exposing secret values.

Owned files:

- `scripts/install_mcp.py`
- `scripts/install_mcp_hosts/codex.py`
- `scripts/install_mcp_hosts/claude.py`
- `scripts/install_mcp_hosts/cursor.py`
- `scripts/install_mcp_hosts/vscode.py`
- `docs/mesh/CORTEX-MCP.md`

Contract:

- `install_mcp.py` adds `--bearer-env <NAME>` and an optional `--auth-client-id-env <NAME>` for Cursor's `auth` block. Values are never read, printed, or stored.
- Codex adapter emits `bearer_token_env_var = "<NAME>"`.
- Claude adapter emits `headers: {"Authorization": "Bearer ${env:<NAME>}"}`.
- Cursor adapter emits the same interpolated form by default and the `auth` block when `--auth-client-id-env` is set.
- VS Code adapter emits an `inputs` entry with `type: "promptString"` plus `headers.Authorization = "Bearer ${input:<id>}"`.
- The installer's JSON report and evidence event record only the env var name, never the value.

Focused oracles:

- A privacy self-test asserts that no environment variable value appears in installer stdout, the evidence event payload, or any written file.
- Per-host golden tests assert the exact interpolated authorization form.
- `python3 scripts/install_mcp.py --self-test`
- `python3 scripts/cortex_mcp.py --self-test`
- `python3 scripts/private_vocabulary_oracle.py`
- `npm run commit:check`

Done when bearer-env HTTP works for all four hosts and the privacy self-test passes.

## Closeout

After SPEC-007 closes, record the wave-level evidence under `docs/evidence/reports/<date>/cortex-mcp-host-segmentation/REPORT.md` covering wave-by-wave done criteria, oracle outputs, and release identity classification.
