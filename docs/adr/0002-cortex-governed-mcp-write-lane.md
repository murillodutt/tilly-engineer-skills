---
tds_id: architecture.adr_0002_cortex_governed_mcp_write_lane
tds_class: architecture
status: active
consumer: maintainers, Cortex authors, MCP adapter authors, installer authors, and release operators
source_of_truth: true
evidence_level: L1
tver: 0.1.0
---

# ADR 0002: Cortex Governed MCP Write Lane

Accepted on 2026-05-27.

TES will add a governed Cortex MCP write lane. The default MCP surface remains
read-only; write-capable tools are exposed only when the server is started with
an explicit write flag.

## Context

ADR 0001 kept v1 Cortex MCP read-only until a later decision could prove five
conditions:

1. explicit user authorization is preserved;
2. evidence grounding is mechanically enforced;
3. scope normalization cannot be bypassed;
4. destructive or broad writes are blocked;
5. the write path is covered by contract, oracle, and rollback evidence.

The current Cortex operator layer now has those pieces: `remember` delegates to
the same durable-memory gate as `apply`, evidence refs are validated before
write, target override is rejected at the MCP boundary, destructive `forget`
remains blocked, and focused MCP/operator oracles prove the behavior.

The external memory MCP pattern is useful as inspiration for tool ergonomics,
but TES does not adopt its backend, hosted service, graph store, update/delete
surface, entity deletion, or automatic memory authority.

## Decision

TES adopts a narrow, native MCP write lane:

| Tool | Contract |
|------|----------|
| `cortex_remember_plan` | No-write validation of one durable Cortex memory proposal. Returns an approval id and exact approval phrase tied to the target, cell, claim, evidence, summary, and links. |
| `cortex_remember` | Writes one new Cortex cell only when the server was started with `--enable-writes` and the exact approval phrase from `cortex_remember_plan` is supplied. |
| `cortex_list_events` | Read-only inspection of sanitized lifecycle events. |
| `cortex_get_event_status` | Read-only lookup of one lifecycle event status by id. |

The write lane is opt-in at process startup. Project-scoped MCP activation
continues to install read-only MCP by default. Operators may opt in with
`install_mcp.py --enable-writes`, which only appends `--enable-writes` to the
project-scoped MCP server args.

## Invariants

- Markdown under `docs/agents/cortex/**` remains durable memory truth.
- MCP is access and operation transport, not a memory backend.
- `cortex_remember` may create only a new cell plus the correlated `MAP.md`,
  `LINKS.md`, `TRAIL.md`, and derived recall index writes already owned by the
  Cortex write gate.
- `cortex_remember` must not overwrite existing cells.
- `cortex_remember` must not write `sources/**`.
- `cortex_remember` must not expose `target` as a tool argument; the server
  target is fixed at process startup.
- MCP must not expose `forget`, update, delete, bulk delete, entity delete,
  checkpoint write, or direct `apply`.
- Event tools are evidence inspection only and must report no writes.

## Authorization Model

The authorization unit is the exact `cortex_remember_plan` payload. The plan
hash includes:

- target path;
- cell name;
- claim text;
- evidence refs;
- optional summary;
- optional links.

`cortex_remember` recomputes the approval id and refuses to write unless the
provided approval phrase matches exactly. This does not turn model output into
permission; agents must still obtain explicit user approval before passing the
phrase. The phrase makes the reviewed payload auditable and prevents accidental
or stale approval reuse across changed claims, evidence, or targets.

## Rejected Alternatives

| Alternative | Rejection |
|-------------|-----------|
| Port a full external memory MCP API | Would add backend and authority drift beyond Cortex Markdown. |
| Expose update/delete/bulk/entity tools | Destructive and broad writes are outside the proven gate. |
| Enable writes by default | Violates the boring default boundary established by ADR 0001. |
| Let MCP write from reflection automatically | Converts transient closure output into doctrine without review. |
| Use event ledger records as memory certification | Event records are evidence, not durable Cortex memory. |

## Required Oracles

Focused certification for this decision requires:

- `python3 scripts/cortex_mcp.py --self-test`;
- `python3 scripts/cortex_operator_oracle.py --self-test`;
- `python3 scripts/event_ledger.py --self-test`;
- `python3 scripts/install_mcp.py --self-test`;
- `python3 scripts/cortex.py --self-test`;
- `python3 scripts/validate_tds.py`;
- `python3 scripts/validate_reference_graph.py`;
- `python3 scripts/private_vocabulary_oracle.py`;
- `git diff --check`.

Before a sealed package or release claim, run the full repository commit gate.

## Consequences

TES crosses from read-only MCP into governed MCP mutability without changing the
source of truth. The gain is operational: an MCP-capable runtime can now create
grounded Cortex memory through the same authorization and evidence gate as the
CLI. The cost is stricter audit language: any future automatic capture,
overwrite, deletion, graph backend, hosted backend, or subagent-owned write must
return to ADR before implementation.
