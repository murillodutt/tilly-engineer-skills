---
tds_id: roadmap.goal_super_spec_cortex_mcp_host_segmentation
tds_class: roadmap
status: active
consumer: maintainers, Cortex MCP authors, installer authors, host integration authors, release reviewers, and execution agents
source_of_truth: false
evidence_level: L1
tver: 0.1.0
---

# GOAL Super SPEC: Cortex MCP Host Segmentation

Status: active execution plan. The Cortex MCP server already supports stdio and opt-in HTTP transports at `scripts/cortex_mcp.py`; the project-scoped installer at `scripts/install_mcp.py` only emits stdio config and shares a single JSON builder across Claude Code, Cursor, and VS Code. This Super SPEC plans the segmentation of the installer into one module per host, with explicit schemas aligned to each host's official documentation, executed in four serial waves.

Capability: segment Cortex MCP installer output per host (Codex CLI, Claude Code CLI, Cursor, VS Code) with explicit per-host schemas covering stdio and opt-in local HTTP transports, and extend coverage to authenticated HTTP without changing ADR 0003 invariants, write lane behavior, or the boundary between Markdown truth and derived indexes.

## Canonical Artifact

Canonical Super SPEC: `docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-cortex-mcp-host-segmentation.md`

Primary decision source: `docs/adr/0003-cortex-mcp-capability-expansion.md`

Bootstrapping references retained for lineage only: `docs/adr/0001-tes-memory-lifecycle.md` `docs/adr/0002-cortex-governed-mcp-write-lane.md`

Execution unit companion (created with SPEC-000): `docs/roadmap/cortex-mcp-host-segmentation/EXECUTION-UNITS.md`

Primary related surfaces:

- `docs/mesh/CORTEX-MCP.md`
- `docs/mesh/CORTEX.md`
- `docs/mesh/EVENT-LEDGER.md`
- `docs/governance/MAINTAINER-CORRELATION-RULE.md`
- `scripts/cortex_mcp.py`
- `scripts/install_mcp.py`
- `.codex/config.toml`
- `.mcp.json`
- `.cursor/mcp.json`
- `.vscode/mcp.json`

## Governing Matrix

| Layer | Meaning |
|-------|---------|
| ADR 0001 | Markdown under `docs/agents/cortex/**` remains durable memory truth; indexes, events, checkpoints, and oracles are derived or evidence surfaces. |
| ADR 0003 | Cortex MCP capability surface is the active contract; transports (stdio, HTTP), resources, prompts, verify cache, progress, and cell history are governed inside the TES boundary. |
| Host Segmentation | Project-scoped installer emits one explicit schema per host instead of a shared JSON object. |
| Oracles | Per-host self-tests validate generated configs against fields, forbidden fields, and registered server objects on disk. |
| Boundary | Installer is local and project-scoped only; never mutates global host configuration, secrets, hooks, remotes, lockfiles, or Cortex source material. |

## Current Meaning

The Cortex MCP server already speaks two transports. The installer does not. `install_mcp.py` uses one TOML f-string for Codex and one shared JSON builder for Claude Code, Cursor, and VS Code. This shared shape works for stdio only because the three JSON hosts converge on `command`, `args`, and `env`. It will diverge once HTTP enters the picture because each host has a distinct HTTP schema:

- Codex declares HTTP as the `StreamableHttp` untagged variant of `McpServerTransportConfig` with `url`, `bearer_token_env_var`, `http_headers`, and `env_http_headers`, and enforces `deny_unknown_fields`.
- Claude Code declares HTTP as `{"type": "http", "url": ..., "headers": ...}` in `mcpServers.<name>`, with stdio also accepting an optional `type: "stdio"` for back-compat.
- Cursor declares HTTP as `{"type": "http" | "sse", "url": ..., "headers":...}` in `mcpServers.<name>`, additionally accepting an `auth` block with `CLIENT_ID`, `CLIENT_SECRET`, and `scopes`. Cursor rejects `cwd` in cloud mode and supports `${workspaceFolder}` and `${env:NAME}` interpolation.
- VS Code uses `servers.<name>` (not `mcpServers`) and accepts an `inputs` array for prompt-driven secrets.

This Super SPEC plans the refactor and the new HTTP coverage as four serial waves. The package-source implementation is intentionally deferred to focused execution units that follow this document.

## Creation Gate Record

| Field | Record |
|-------|--------|
| `VERIFY` | ADR 0001, ADR 0002, ADR 0003, `docs/mesh/CORTEX-MCP.md`, `scripts/install_mcp.py`, `scripts/cortex_mcp.py`, and host docs for Codex CLI (`mcp_types.rs`), Claude Code (`code.claude.com/docs/en/agent-sdk/mcp`, `code.claude.com/docs/en/mcp`), and Cursor (`cursor.com/docs/mcp`, `cursor.com/docs/sdk/typescript`) were inspected before writing. |
| `SCOPE` | Add this Super SPEC and correlated documentation indexes only. No runtime, package version, adapter, installer, MCP server, or bundle changes. |
| `BEST_PATH` | Plan segmentation as serial waves under ADR 0003 instead of opening a fourth ADR or rewriting `install_mcp.py` in one commit. |
| `DOCUMENT` | This Super SPEC plus `docs/roadmap/README.md`, `docs/INDEX.md`, and `docs/tds/DOCS-INDEX.yml`. |
| `ORACLE` | `python3 scripts/validate_tds.py`, `python3 scripts/validate_doc_size.py`, `python3 scripts/validate_reference_graph.py`, and `git diff --check`. |
| `RESOLVE` | No blocker found; runtime implementation is intentionally deferred to the execution units. |
| `STATUS` | `PROCEED` |

## Assumptions

- Markdown under `docs/agents/cortex/**` remains durable memory truth.
- The Cortex MCP server contract from ADR 0003 stays unchanged. No new tools, no schema removals, no changes to the write lane.
- Cortex MCP transports stay limited to stdio (default) and opt-in localhost HTTP. Remote HTTP requires explicit `--allow-non-localhost` and is out of scope for this Super SPEC.
- Project-scoped installation continues to be the only supported route. No mutation of global Codex, Claude, Cursor, or VS Code configuration.
- Codex HTTP transport target is the `StreamableHttp` variant. Codex stdio remains the default for local installs.
- Claude Code HTTP transport target is `{"type": "http", ...}` only; SSE remains documented as deprecated by the host and is not generated.
- Cursor HTTP transport target is `{"type": "http", ...}`. SSE may be exposed later but is not part of this plan.
- VS Code stays in scope because the current installer already supports it and release operators use it; it does not appear in the goal title only because Codex, Claude Code CLI, and Cursor were the explicit ask.
- Any runtime command, script, fixture, or user-visible documentation added in a later wave is delivered behavior and needs release identity review.

## Non-Objectives

- Create a new ADR. ADR 0003 governs the capability surface; this Super SPEC is the execution plan, not a new contract.
- Add new Cortex MCP tools, prompts, or resources.
- Change the write lane (`cortex_remember_plan` / `cortex_remember`).
- Expose `target` as a tool argument or accept tool-level transport overrides.
- Allow remote HTTP binds without `--allow-non-localhost`.
- Mutate global host configuration files, user-scope MCP registries, secrets, hooks, remotes, package lockfiles, `.obsidian/**`, or Cortex source material.
- Copy a third-party MCP installer, FastMCP-style framework, or hosted memory service into TES.
- Store private project names, product names, paths, or canary identifiers in tracked TES source, fixtures, reports, or commits.

## Central Rule

The installer segments per host without expanding the server's authority:

```text
host adapter -> explicit schema -> validated registration -> evidence event
```

Every per-host adapter must preserve this invariant:

```text
Markdown is truth.
MCP is transport, not memory.
stdio is default.
HTTP is opt-in and localhost-only without explicit override.
Writes go through the cortex_remember plan-then-apply lane only.
No installer wave grants new server authority; it only changes how config is
generated, validated, and recorded.
```

## Per-Host Field Matrix

Authoritative reference for adapters built under this Super SPEC.

| Field | Codex `.codex/config.toml` | Claude `.mcp.json` | Cursor `.cursor/mcp.json` | VS Code `.vscode/mcp.json` |
|---|---|---|---|---|
| Root key | `[mcp_servers.<name>]` | `mcpServers.<name>` | `mcpServers.<name>` | `servers.<name>` |
| stdio discriminator | absence of `url` (untagged) | optional `type: "stdio"` | optional `type: "stdio"` | `type: "stdio"` |
| http discriminator | presence of `url` | `type: "http"` (SSE deprecated) | `type: "http"` or `type: "sse"` | `type: "http"` or `type: "sse"` |
| `command` (stdio) | yes | yes | yes | yes |
| `args` (stdio) | yes | yes | yes | yes |
| `env` (stdio) | sub-table `[mcp_servers.<name>.env]` | object | object (cloud passes to VM) | object |
| `cwd` | yes | not supported | yes (local only; cloud rejects) | yes |
| `url` (http) | yes | yes | yes | yes |
| HTTP headers | `http_headers` + `env_http_headers` | `headers` | `headers` | `headers` |
| Bearer auth | `bearer_token_env_var` | inline `headers.Authorization` | inline `headers.Authorization` or `auth` block | inline `headers.Authorization` or `inputs` |
| Timeouts | `startup_timeout_sec`, `tool_timeout_sec` | not exposed | not exposed | not exposed |
| Enable flag | `enabled = true` | host-managed | host-managed | host-managed |
| Interpolation | none documented | `${env:NAME}` | `${workspaceFolder}`, `${env:NAME}` | `${env:NAME}`, `inputs` |
| Strict fields | `deny_unknown_fields` | tolerant | tolerant | tolerant |

## Wave Plan

Four serial waves. Each wave has owned files, its own focused oracle, and an explicit done criterion. Later waves do not start until the prior wave passes its oracle and records evidence.

### Wave 1 — Mechanical segmentation, stdio only, behavior preserved

Owned files:

- `scripts/install_mcp.py` (orchestrator only after refactor)
- `scripts/install_mcp_hosts/__init__.py`
- `scripts/install_mcp_hosts/base.py`
- `scripts/install_mcp_hosts/codex.py`
- `scripts/install_mcp_hosts/claude.py`
- `scripts/install_mcp_hosts/cursor.py`
- `scripts/install_mcp_hosts/vscode.py`

Behavior:

- Extract the per-host config builders into one module per host behind a `HostAdapter` base contract with `build_stdio`, `merge_into_existing`, and `validate_registered`.
- `install_mcp.py` becomes an orchestrator: argument parsing, helper copy, adapter loop, validation, JSON report, evidence event. No behavior change.
- The generated stdio configs must be byte-identical to the pre-refactor output. Existing self-tests must pass without modification.

Done criterion:

- `python3 scripts/install_mcp.py --self-test` passes.
- `python3 scripts/cortex_mcp.py --self-test` passes.
- A per-host golden test asserts the exact generated stdio object for each of the four hosts.

Oracle:

- `python3 scripts/install_mcp.py --self-test`
- `python3 scripts/cortex_mcp.py --self-test`
- `npm run commit:check`

### Wave 2 — Opt-in localhost HTTP transport

Owned files:

- `scripts/install_mcp.py`
- `scripts/install_mcp_hosts/codex.py`
- `scripts/install_mcp_hosts/claude.py`
- `scripts/install_mcp_hosts/cursor.py`
- `scripts/install_mcp_hosts/vscode.py`
- `docs/mesh/CORTEX-MCP.md`

Behavior:

- Add `--transport http` and `--port` flags to `install_mcp.py`. Default remains `--transport stdio`.
- Each host adapter implements `build_http` with the host's exact HTTP schema:
  - Codex: `StreamableHttp` variant with `url`, no `command`/`args`/`cwd`.
  - Claude: `{"type": "http", "url": "..."}` in `mcpServers.<name>`.
  - Cursor: `{"type": "http", "url": "..."}` in `mcpServers.<name>`.
  - VS Code: `{"type": "http", "url": "..."}` in `servers.<name>`.
- HTTP installs default to `http://127.0.0.1:<port>/mcp`. Remote URLs require an explicit `--allow-non-localhost` flag mirroring the server-side guard.
- The mesh doc gains an HTTP transport section that mirrors the per-host matrix and references this Super SPEC.

Done criterion:

- `python3 scripts/install_mcp.py --self-test` now covers a `stdio × http × read-only` matrix per host.
- Each host adapter validates the registered server object on disk after write.
- HTTP install rejects non-localhost URLs without `--allow-non-localhost`.

Oracle:

- `python3 scripts/install_mcp.py --self-test`
- `python3 scripts/cortex_mcp.py --self-test`
- `npm run commit:check`

### Wave 3 — Strict per-host validation and forbidden-field guards

Owned files:

- `scripts/install_mcp_hosts/codex.py`
- `scripts/install_mcp_hosts/claude.py`
- `scripts/install_mcp_hosts/cursor.py`
- `scripts/install_mcp_hosts/vscode.py`
- `docs/mesh/CORTEX-MCP.md`

Behavior:

- Each host adapter exposes an allowed-field set and a forbidden-field set. Codex applies `deny_unknown_fields` semantics by validating against the closed list of `McpServerConfig` and `StreamableHttp` fields before write.
- Claude adapter asserts `cwd` is never emitted.
- Cursor adapter asserts `cwd` is never emitted in HTTP mode and never points outside the workspace in stdio mode.
- VS Code adapter validates `servers` (not `mcpServers`) and that any future `inputs` array stays opt-in.
- Mesh doc gains a forbidden-field row per host and a short rationale.

Done criterion:

- Negative self-tests assert that injecting an unknown field for Codex, emitting `cwd` for Claude, or using `mcpServers` for VS Code are detected before write.
- Positive self-tests still pass for the full `stdio × http × read-only` matrix.

Oracle:

- `python3 scripts/install_mcp.py --self-test`
- `python3 scripts/cortex_mcp.py --self-test`
- `npm run commit:check`

### Wave 4 — Authenticated HTTP transport

Owned files:

- `scripts/install_mcp.py`
- `scripts/install_mcp_hosts/codex.py`
- `scripts/install_mcp_hosts/claude.py`
- `scripts/install_mcp_hosts/cursor.py`
- `scripts/install_mcp_hosts/vscode.py`
- `docs/mesh/CORTEX-MCP.md`

Behavior:

- Add `--bearer-env` flag to `install_mcp.py` that names an environment variable. The installer never reads, prints, or stores the secret value.
- Codex adapter emits `bearer_token_env_var = "<name>"`.
- Claude adapter emits `headers: {"Authorization": "Bearer ${env:<name>}"}` using the host's interpolation syntax.
- Cursor adapter emits the same interpolated `headers.Authorization` form by default; an optional `--auth-client-id-env` flag emits the `auth` block.
- VS Code adapter emits an `inputs` entry with `type: "promptString"` plus the matching `${input:<id>}` reference in `headers.Authorization`.
- The installer's JSON report records the bearer env var name; never the value.

Done criterion:

- Self-test fixtures simulate the `--bearer-env` flag without setting the environment variable. The installer must succeed and the generated config must not contain a secret value.
- Per-host golden tests assert the exact interpolated authorization form for each host.
- A privacy self-test asserts no environment variable values appear in the installer's stdout, evidence event, or written files.

Oracle:

- `python3 scripts/install_mcp.py --self-test`
- `python3 scripts/cortex_mcp.py --self-test`
- `python3 scripts/private_vocabulary_oracle.py`
- `npm run commit:check`

## Execution Units

Detailed execution units live in `docs/roadmap/cortex-mcp-host-segmentation/EXECUTION-UNITS.md` once SPEC-000 is started. The first eight units are:

| Unit | Purpose |
|------|---------|
| `SPEC-000` | Prove boundary, no new server authority, and index the plan. |
| `SPEC-001` | Land the `HostAdapter` base contract and the per-host module skeleton. |
| `SPEC-002` | Migrate Codex to `codex.py` with byte-identical stdio output. |
| `SPEC-003` | Migrate Claude Code and Cursor to their modules with byte-identical stdio output. |
| `SPEC-004` | Migrate VS Code and close Wave 1 with the per-host stdio golden tests. |
| `SPEC-005` | Add `build_http` to every adapter and the `--transport http` orchestration (Wave 2). |
| `SPEC-006` | Add strict per-host validation and forbidden-field guards (Wave 3). |
| `SPEC-007` | Add bearer-env authenticated HTTP (Wave 4) and close evidence. |

Execution agents must read this Super SPEC first, then the companion execution unit document for the current unit only. Do not load or implement later units as active scope until the current unit has passed its focused oracles.

## Release Identity Rule

This Super SPEC alone does not require a package version bump.

Wave 1 is a mechanical refactor with byte-identical generated configs; it is not delivered behavior on its own, but the closeout records the refactor.

Waves 2, 3, and 4 add user-visible installer flags and generated config shapes; they are delivered behavior unless explicitly classified otherwise. Default release policy is a patch bump per delivered wave, unless the owner explicitly defers that bump and the closeout records the deferral.

## Global Stop Conditions

Stop and report `BLOCKED`, `DEGRADED`, or `NEEDS_REVIEW` when:

- a wave would change the Cortex MCP server contract from ADR 0003;
- a wave would expose new write tools, hide existing write tools without `--read-only`, or weaken the `cortex_remember_plan` / `cortex_remember` approval lane;
- a wave would mutate global host configuration, user-scope MCP registries, secrets, hooks, remotes, package lockfiles, `.obsidian/**`, or Cortex source material;
- HTTP installs accept non-localhost URLs without an explicit `--allow-non-localhost` flag in both installer and server;
- a bearer secret value is read, printed, or written to any tracked file by the installer;
- private identifiers appear in adapters, fixtures, docs, reports, commits, or tags;
- release identity is required but unresolved;
- per-host validation passes silently when the registered server object on disk does not match the host adapter contract.

## Definition Of Complete Host Segmentation

The segmentation is complete only when:

- one host adapter module exists per host (`codex`, `claude`, `cursor`, `vscode`) with explicit allowed-field and forbidden-field sets;
- stdio configs generated by each adapter are byte-identical to the pre-refactor output;
- HTTP configs generated by each adapter follow the host's official schema and reject non-localhost URLs without `--allow-non-localhost`;
- per-host validation reads the registered server object on disk and fails when fields drift;
- bearer-env authenticated HTTP works for all four hosts without exposing secret values in stdout, evidence events, or tracked files;
- `docs/mesh/CORTEX-MCP.md` reflects the per-host matrix, the HTTP transport surface, the forbidden-field rationale, and the bearer-env contract;
- `python3 scripts/install_mcp.py --self-test`, `python3 scripts/cortex_mcp.py --self-test`, and `npm run commit:check` all pass before any sealed package claim.
