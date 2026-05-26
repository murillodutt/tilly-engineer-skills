---
tds_id: architecture.adr_0001_tes_memory_lifecycle
tds_class: architecture
status: active
consumer: maintainers, Cortex authors, adapter authors, installer authors, and release operators
source_of_truth: true
evidence_level: L1
tver: 0.1.0
---

# ADR 0001: TES Memory Lifecycle And Cortex Operational Maturity

Accepted on 2026-05-26.

TES will treat Cortex memory as an operational lifecycle, not only as durable
Markdown recall. Markdown remains the source of truth; hooks, MCP, SQLite,
events, checkpoints, and reviewers are governed access and evidence surfaces.

## Context

Cortex already has a strong truth boundary:

- durable memory lives in versioned Markdown under `docs/agents/cortex/**`;
- `.tes/cortex/recall.sqlite` and `.tes/cortex/semantic.sqlite` are derived;
- MCP is read-only in v1;
- `learn` and `reflect` propose; only `apply --yes` writes with evidence and
  authorization.

The missing maturity layer is not another storage backend. The missing layer is
an explicit memory lifecycle: when memory is recalled, when scope is injected,
when writes are blocked, when checkpoints are created, when closeout asks for
learning, when subagents may report evidence, and when curation or consolidation
is due.

This decision follows a local source inspection of current TES Cortex and MCP
contracts plus an external memory-system study. The transferable pattern is
recorded here without making the external project part of TES source material.

## Decision

TES adopts a Memory Lifecycle architecture for Cortex evolution.

The architecture has six rules:

1. Cortex Markdown remains authoritative memory.
2. Runtime indexes, event logs, hook outputs, and checkpoints are evidence or
   acceleration surfaces, not memory truth.
3. Memory writes require explicit authorization, evidence, and a Cortex write
   path such as `apply --yes` or a future approved equivalent.
4. Subagents do not write durable memory directly. They return findings to the
   parent agent, which may propose or apply memory through the authorized path.
5. Adapter hooks are modeled as lifecycle contracts, not ad hoc scripts.
6. Every new memory automation needs an oracle proving it cannot silently create
   ungrounded, duplicate, stale, or cross-scope memory.

## Adopted Components

| Component | Contract | Source Of Truth |
|-----------|----------|-----------------|
| Adapter hook matrix | Declare supported lifecycle moments per host: recall, scope normalization, write gate, checkpoint, closeout, and subagent return. | Governed adapter docs and materialization oracles |
| Scope normalizer | Deterministically attach project, adapter, agent, run, source, and evidence metadata before Cortex or Field Reports operations. | Local deterministic helper or hook |
| Write gate | Block direct durable-memory writes outside approved Cortex promotion paths. | Hook/tool boundary plus oracle |
| Event ledger | Record memory lifecycle events in a structured, agent-readable surface. | Local evidence or Field Reports surface |
| Checkpoint lane | Store resumability state with TTL semantics outside durable Cortex cells. | Local checkpoint contract |
| Operator layer | Expose small read-only or explicitly mutating commands such as health, peek, review, checkpoint, remember, and forget. | Skills and CLI contracts |
| Quality reviewer | Detect duplicates, contradictions, swollen cells, weak evidence, stale claims, and transient material promoted as durable memory. | Read-only Cortex oracle |
| Consolidation gate | Run cheap local gates first, use a lock, and certify completion only after observed write behavior. | Deterministic oracle |

## Lifecycle Model

| Moment | Purpose | Default Write Authority |
|--------|---------|-------------------------|
| Session start | Publish identity, scope, memory availability, and recovery instructions. | none |
| User prompt | Recall relevant Cortex context by task intent. | none |
| File read | Recall context tied to the code or document surface being inspected. | none |
| Tool failure | Recall prior failures, fixes, and local gate knowledge. | none |
| Pre-tool memory operation | Normalize scope and block unsafe writes. | restricted |
| Subagent return | Feed reusable findings to the parent agent. | parent only |
| Pre-compact | Create resumability checkpoint, not durable doctrine. | checkpoint only |
| Stop or closeout | Reflect on durable decisions, lessons, and curation needs. | proposal only |
| Apply | Promote durable memory with evidence and authorization. | explicit approval |
| Curation | Review duplicates, tensions, links, splits, and evidence gaps. | no write by default |

## Event Ledger

TES will add a structured event ledger only as an operational evidence surface.
It must not replace `TRAIL.md`, Cortex cells, or Field Reports.

Required event fields for future implementation:

| Field | Meaning |
|-------|---------|
| `event_id` | Stable local identifier |
| `event_type` | `reflect`, `learn`, `apply`, `audit`, `curate`, `checkpoint`, `blocked`, `degraded`, or successor enum |
| `status` | `PASS`, `FAIL`, `BLOCKED`, `DEGRADED`, `NEEDS_REVIEW`, `NOT_AVAILABLE`, or `CERTIFIED` |
| `scope` | Project, adapter, agent, run, and source scope after normalization |
| `evidence` | Paths or retained evidence references, never secrets |
| `writes` | Files or derived artifacts touched, if any |
| `oracle` | Command or tool result that proves the event |
| `created_at` | UTC timestamp |

The ledger is inspectable by agents through future `event list` and
`event status` style commands. Human-facing summaries may remain in `TRAIL.md`
or retained evidence reports.

## Durable Memory Versus Checkpoint State

Durable Cortex cells require claim, evidence, links, and authorization.

Checkpoint state is different. It may preserve compact summaries, session
reentry hints, current run position, failed command context, or pending
handoffs. Checkpoints must have TTL or explicit cleanup semantics and must not
be promoted into Cortex cells without the normal evidence path.

This distinction prevents transient session state from becoming doctrine.

## Subagent Boundary

Subagents may:

- inspect code and documents;
- run read-only analysis;
- return findings, evidence paths, and recommendations to the parent;
- propose candidate learnings.

Subagents must not:

- write durable Cortex memory directly;
- update the future event ledger as if they owned final authority;
- bypass the parent agent's evidence and authorization gate;
- create permanent memory in an ephemeral namespace without a parent merge.

## MCP Boundary

The v1 Cortex MCP remains read-only. Write-capable MCP tools are rejected by
this ADR until a later decision proves:

1. explicit user authorization is preserved;
2. evidence grounding is mechanically enforced;
3. scope normalization cannot be bypassed;
4. destructive or broad writes are blocked;
5. the write path is covered by contract, oracle, and rollback evidence.

## Rejected Alternatives

| Alternative | Rejection |
|-------------|-----------|
| Make vector or semantic index the memory source of truth | Conflicts with Cortex filesystem-first auditability. |
| Let hooks write durable memory automatically | Creates unreviewed doctrine and weakens explicit authorization. |
| Allow subagents to write durable memory | Produces fragmented authority and orphaned learning. |
| Resolve contradictions by LLM output alone | TES requires evidence and review for durable claims. |
| Call an entity boost a graph | Names must match implementation and oracle coverage. |
| Copy an external memory system wholesale | TES needs transferable contracts, not project-specific behavior. |

## Implementation Waves

| Wave | Deliverable | Required Oracle |
|------|-------------|-----------------|
| 1 | Adapter hook matrix and subagent memory boundary contract. | Adapter parity or materialization oracle proves docs and delivered adapters agree. |
| 2 | Scope normalizer contract for Cortex and Field Reports events. | Fixtures prove missing scope is injected and cross-scope access is rejected. |
| 3 | Read-only event ledger prototype and `event list/status` inspection. | Ledger oracle proves schema, sanitization, status enums, and no hidden writes. |
| 4 | Checkpoint lane with TTL semantics. | Checkpoint oracle proves state does not become durable Cortex memory. |
| 5 | Cortex operator layer: health, peek, review, checkpoint, remember, forget. | Mutability oracle proves read-only commands cannot write and mutating commands require approval. |
| 6 | Consolidation gate with lock and observed-write certification. | Gate oracle proves no completion claim without observed authorized write behavior. |

Each wave is independently releasable only after its correlated docs, adapters,
skills, scripts, and package surfaces are classified through the maintainer
correlation rule.

## Release Identity

This ADR is a documentation and architecture decision. It does not by itself
deliver new adopter-visible behavior.

Any later change that adds or changes hooks, skills, installer behavior, helper
scripts, MCP tools, public docs, adapter materialization, or runtime behavior is
delivered behavior and requires a release identity decision under the repository
release rules.

## Consequences

TES gains a clearer path from memory as files to memory as an auditable
operating system. The cost is stricter governance: every automation must declare
scope, authority, evidence, status, and oracle before it can touch durable
memory.

Future implementation must keep the system boring at the boundary:

- no hidden memory writes;
- no source-of-truth drift from derived stores;
- no subagent authority inflation;
- no automatic doctrine from transient checkpoints;
- no `CERTIFIED` claim without an oracle that covers the actual lifecycle.
