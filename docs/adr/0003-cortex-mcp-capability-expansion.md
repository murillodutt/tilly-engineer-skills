---
tds_id: architecture.adr_0003_cortex_mcp_capability_expansion
tds_class: architecture
status: active
consumer: maintainers, Cortex MCP authors, host integration authors, and release operators
source_of_truth: true
evidence_level: L1
tver: 0.3.0
---

# ADR 0003: Cortex MCP Capability Expansion

Proposed on 2026-05-27 after comparative analysis of the contemporary MCP memory-oriented server patterns of MCP
servers (`external-memory-server-a`, `external-memory-server-b`, `external-memory-server-c`).
Accepted on 2026-05-27 as the active Cortex MCP evolution contract.

TES will expand the Cortex MCP surface along seven targeted capability axes
without changing the source of truth, the write lane, or the dependency
posture. Adopted patterns are observed in the contemporary MCP memory-oriented server patterns but reimplemented
inside the TES boundary.

ADR 0001 and ADR 0002 are now archived bootstrapping records. Their surviving
runtime invariants are carried forward here so the active contract stays thin
instead of accumulating multiple overlapping ADR sources of truth.

## Context

The Cortex MCP server today is a zero-dependency JSON-RPC 2.0 stdio
implementation exposing 14 tools (12 in read-only). It is well certified for
the read and governed-write paths it covers. Three operational gaps remain
visible after comparison with current MCP servers in the field:

1. host integration leaves cell discovery and slash-command surfacing entirely
   to tool calls, even though MCP has native `resources/*` and `prompts/*`
   primitives that hosts already render;
2. tool schemas are assembled by hand with three helpers, producing 30+ lines
   per new tool and a small but real drift risk between schema and
   implementation;
3. operational latency on hot paths (`verify`-prefixed tool calls), feedback
   on long tools (`review`, `curate_plan`, `audit`), durable history of a
   single cell, and remote invocation are all unaddressed.

The contemporary MCP memory-oriented server patterns demonstrates pragmatic answers for several of these (Pydantic
schemas, streamable HTTP transport, server-side prompts, soft history). It
also demonstrates patterns that this ADR explicitly does not adopt:
automatic capture, broad CRUD, multi-tenant scopes, and FastMCP/Pydantic as
a hard dependency.

This ADR records the capability expansion as a single decision so that the
next implementation cycle can sequence the items against a stable contract.

## Decision

TES adopts seven targeted capabilities. Each item lists its surface, the
expected invariants, and the oracle conditions a future implementation must
satisfy.

## Capability Status And Dependency Graph

The ADR is active as an architectural decision. The seven expansion
capabilities are certified in the local package source by their scoped
`cortex_mcp.py --self-test` additions and by the incremental commits listed
below. Release identity remains a separate package decision.

| Capability | Status | Dependency note |
|------------|--------|-----------------|
| Current governed MCP baseline | certified | Existing stdio tools and governed write lane remain certified by current MCP and operator oracles. |
| Schema helper | certified | Landed in `639e6081`; `cortex_recall` has a golden JSONSchema equality self-test. |
| Optional HTTP transport | certified | Landed in `a1a92967`; HTTP is opt-in, localhost by default, stdlib-only, and covered by stdio parity tests. |
| Resources | certified | Landed in `d65e88aa`; `resources/list` and `resources/read` expose only cell Markdown with HTTP parity. |
| Prompts | certified | Landed in `d8104568`; inert prompt registry is covered by prompt list/get and forbidden-term checks. |
| Verify cache | certified | Landed in `9cf4a5ae`; mtime cache hit, invalidation, fallback, and self-test bypass are covered. |
| Progress notifications | certified | Landed in `ee58fa67`; advisory progress and callback-failure tolerance are covered. |
| Cell history | certified | Landed in `13063264`; read-only `TRAIL.md` parsing, empty history, traversal rejection, and HTTP parity are covered. |

Implementation uses two tracks:

- Serial bridge: land the schema helper first, then bring HTTP transport early
  enough that capability closeout can prove dual-transport behavior.
- Parallel capability fronts: resources, prompts, verify cache, progress
  notifications, and cell history may proceed independently after the relevant
  bridge is available.

The merge gate is the consolidated `cortex_mcp.py --self-test`, with each
available capability covered in stdio and HTTP once HTTP exists.

### 1. MCP Resources for Cells

Expose every Markdown cell under `docs/agents/cortex/cells/**` as a native
MCP resource. The server advertises `resources` capability at `initialize`,
implements `resources/list` and `resources/read`, and addresses cells with
URIs of the form `tes-cortex://cells/<stem>`.

| Invariant |
|-----------|
| Resources are read-only. No `resources/subscribe` or write surface. |
| URI scheme is fixed to `tes-cortex://`. No alternate schemes. |
| `resources/list` enumerates only files under `cells/**`. `MAP.md`, `LINKS.md`, `TRAIL.md`, and `sources/**` are not exposed as resources. |
| Resource content equals the on-disk Markdown byte-for-byte. No rendering. |
| Resources are stateless; the server target remains fixed at startup. |

### 2. Server-side Prompts

Expose Cortex operator prompts via `prompts/list` and `prompts/get`. Initial
set: `cortex/closure-reflection`, `cortex/curation-review`,
`cortex/remember-checklist`. Hosts surface these as slash commands without
the user needing to remember skill names.

| Invariant |
|-----------|
| Prompts are templates only. They never invoke tools, never mutate state, and never embed credentials. |
| Each prompt has a stable name and a versioned body string stored in the server module. |
| Adding or changing a prompt requires updating the prompt registry and the self-test. |
| Prompts must not reference target-specific paths; they describe operator intent in target-neutral language. |

### 3. Schema Helper without Pydantic

Replace ad-hoc `schema_string` / `schema_integer` / `schema_string_array`
calls with a single declarative helper. The helper accepts a mapping of
property name to a small type descriptor (`("string", description)`,
`("integer", description, default)`, `("string-array", description)`, etc.)
and the `required` list, and emits the JSONSchema dict the server already
expects.

| Invariant |
|-----------|
| No new dependencies. `dataclasses`, `typing`, and stdlib only. |
| Pydantic, FastMCP, and Smithery decorators remain explicitly out of scope. |
| The helper must produce the exact same JSONSchema shape currently emitted, so existing host integrations and self-tests do not regress. |
| Tools migrate to the helper incrementally. Old and new style coexist during transition. |

### 4. Verify Cache by Mtime

Cache the result of `cortex.verify(target)` keyed by the maximum `mtime`
across `docs/agents/cortex/**`. Invalidate on any change. Tools that today
call `cortex.verify` at the top of their handler consult the cache instead.

| Invariant |
|-----------|
| Cache lives in process memory. No disk persistence. No file-watchers. |
| Cache key is derived from `os.stat().st_mtime_ns` across the cortex tree, not from a hash. Cheap to compute, monotonic, sufficient. |
| Any failure to compute the key falls back to the uncached path. The cache never masks a verify failure. |
| Cache is bypassed by `--self-test` runs. |

### 5. Progress Notifications

Long-running tools emit MCP `notifications/progress` updates. Initial
coverage: `cortex_review`, `cortex_audit`, `cortex_curate_plan` (when
`backend` is not `lexical`).

| Invariant |
|-----------|
| Progress is advisory only. Cancellation is not supported in this expansion. |
| The total step count is best-effort. Tools may emit fewer or more updates than initially advertised. |
| Failure to emit progress never fails the tool. The notification path is best-effort. |
| Tools that do not benefit (sub-second handlers) do not emit progress. |

### 6. Cell History Tool

Add one read-only tool, `cortex_cell_history`, that reads the `TRAIL.md`
associated with a cell and returns structured entries (timestamp,
evidence_ref, claim summary, links delta). Source of truth remains
`TRAIL.md`; the tool parses and structures it.

| Invariant |
|-----------|
| Read-only. Adds no new mutability class. |
| Parses existing `TRAIL.md`; does not introduce a new ledger format. |
| Returns an empty list with `status: PASS` when a cell has no trail entries. |
| Rejects path traversal and target override identically to existing read tools. |

### 7. Optional Streamable HTTP Transport

Add `--transport http` as an opt-in transport alongside default stdio. HTTP
mode binds to `127.0.0.1:<port>` by default. Implementation uses the
standard library (`http.server` or equivalent stdlib primitives). The
JSON-RPC handler is unchanged; only the framing differs.

| Invariant |
|-----------|
| Default transport remains stdio. HTTP is opt-in. |
| No third-party HTTP framework. No `anyio`, `aiohttp`, `starlette`, `fastapi`. |
| HTTP mode is stateless per request. Each request carries one JSON-RPC envelope; sessions are not persisted across requests. |
| HTTP mode honors the same `--read-only` and target-fixing semantics as stdio. |
| Bind address defaults to localhost. Non-localhost bind requires an explicit flag and prints a clear warning. |
| The same `--self-test` runs against both transports. |

## Active Cortex MCP Contract

This ADR now owns the active Cortex MCP contract. The following invariants are
carried forward from ADR 0001 and ADR 0002:

- Markdown under `docs/agents/cortex/**` is the durable memory source of truth.
- Runtime indexes, event logs, checkpoints, resources, prompts, transports, and
  notifications are access, evidence, acceleration, or operator surfaces, not
  memory truth.
- The two-step `cortex_remember_plan` / `cortex_remember` write lane and its
  approval-phrase semantics are unchanged.
- `cortex_remember` may create only one new cell plus correlated `MAP.md`,
  `LINKS.md`, `TRAIL.md`, and derived recall-index writes already owned by the
  Cortex write gate.
- `cortex_remember` must not overwrite existing cells and must not write
  `sources/**`.
- Target is fixed at process startup. Tools never accept a `target` argument.
- No new destructive surface (no delete, no update, no forget, no
  checkpoint, no apply over MCP).
- No automatic capture. Reflection remains no-write.
- Event tools are evidence inspection only and must report no writes.
- No multi-tenant scope (`user_id` / `agent_id` / `app_id` / `run_id`).
- No multi-target single process.

## Rejected Alternatives

| Alternative | Rejection |
|-------------|-----------|
| Adopt FastMCP and Pydantic for schema ergonomics | Replaces a zero-dependency stdlib server with a transitive dependency graph (Pydantic v2, anyio, optional Smithery). The ergonomic gain does not justify losing audit-easy and embedded-Python compatibility. |
| Add update / delete / forget tools | The non-destructive surface is itself a feature. Adding mutability beyond the governed write lane increases incident surface without a matching operational need. |
| Automatic capture from reflection or hooks | Promotes transient closure output into durable memory without review. The `reflect` → `remember_plan` → `remember` chain already covers the intentional capture path. |
| Multi-tenant scopes on tool arguments | Cortex is project-scoped. Per-call tenancy dilutes the boundary and adds authorization surface the project model does not need. |
| Multi-target single process | Breaks the "one process, one target" invariant that makes the server auditable. One MCP process per project already works. |
| `resources/subscribe` and write resources | Out of scope for read-only resource exposure. Would require a watch loop and reopen the destructive surface question. |
| SSE legacy transport | Streamable HTTP supersedes SSE in MCP spec 2025-03-26+. SSE is not adopted. |
| Server-side prompts that invoke tools | Prompts must remain inert templates. A tool-invoking prompt would create an authorization loophole. |

## Required Oracles

Each capability requires extending the existing oracles, not creating new
standalone ones. The expansion must keep `cortex_mcp.py --self-test` as the
single point of truth for MCP contract validation.

| Capability | Self-test addition |
|------------|-------------------|
| Resources | `resources/list` returns exactly the set of `cells/**` paths, `resources/read` matches on-disk bytes, non-cell URIs are rejected. |
| Prompts | `prompts/list` returns the registered set, each `prompts/get` returns a non-empty body, prompts cannot trigger tool calls. |
| Schema helper | A migrated tool produces a JSONSchema equal to the pre-migration schema (golden comparison). |
| Verify cache | Two consecutive tool calls with no filesystem change use the cache; a touched cell invalidates it; `--self-test` runs bypass the cache. |
| Progress notifications | A long tool emits at least one `notifications/progress` message; notification failure does not fail the tool result. |
| Cell history | Empty trail returns PASS with empty list; populated trail returns structured entries; path traversal and target override are rejected. |
| HTTP transport | `--transport http` boots, accepts a JSON-RPC POST, returns the same envelope as stdio; non-localhost bind requires explicit flag; read-only and approval semantics behave identically to stdio. |

Before a sealed package or release claim, the full repository commit gate
runs as before. `install_mcp.py --self-test` must continue to pass without
modification (resources, prompts, progress, HTTP, and history must not
require installer changes — installer remains a project-scoped registration
helper).

## Consequences

The Cortex MCP server grows by roughly 600 lines without adding
dependencies and without changing the write lane. Hosts gain native
discovery of cells and slash-command surfacing for operator prompts. The
schema authoring path becomes shorter. Long tool calls become observable.
Remote invocation becomes possible without coupling the project to a web
framework. A new read tool, `cortex_cell_history`, exposes durable change
history that today requires reading raw Markdown.

The cost is stricter self-test scope: every new capability is contract-
verified inside the same binary, and the next time a external memory-oriented pattern is
proposed, this ADR is the reference for what was deliberately not adopted.

ADR status `active` means the direction and carried-forward Cortex MCP
invariants are accepted. Capability status `certified` means the specific
capability has landed with its self-test extension and, once HTTP exists,
stdio/HTTP parity.
