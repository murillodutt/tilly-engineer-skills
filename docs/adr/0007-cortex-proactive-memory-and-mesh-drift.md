---
tds_id: architecture.adr_0007_cortex_proactive_memory_and_mesh_drift
tds_class: architecture
status: active
consumer: maintainers, Cortex authors, TES Align authors, host integration authors, and release operators
source_of_truth: true
evidence_level: L1
tver: 0.1.0
---

# ADR 0007: Cortex Proactive Memory And Mesh Drift

Accepted on 2026-06-26. This ADR records architecture only. It does not deliver hooks, scripts, MCP behavior, installer changes, skill changes, release identity, or public bundle changes.

## Core Rule

Cortex may evolve into a proactive memory and sensing layer, but it must not become the operational mesh writer. `/tes-align` remains the canonical reconciler for `docs/agents/**`.

```text
Future Cortex observes, captures, recalls, and signals drift.
Align reconciles, writes, and certifies the operating mesh.
```

## Context

The current Cortex contract makes filesystem Markdown the durable memory source of truth and treats SQLite as a derived cache. `tes-cortex` exposes recall, read, verify, audit, rebuild, curate, learn, reflect, apply, remember, forget, and consolidation routes. Durable writes already require evidence and explicit authorization.

The current `/tes-align` contract owns semantic project alignment. It turns initial context into an evidenced operating mesh with project state, roadmap, execution line, quality gates, boundaries, glossary, decisions, and retained alignment evidence. It must discover before writing and must not invent architecture.

The current gap is continuity between those surfaces. Cortex can know or propose durable lessons, while the mesh can still lag behind until `/tes-align` runs. That lag is not a reason to let Cortex edit the mesh; it is a reason to make drift observable and route it to the correct reconciler.

A read-only mem0-plugin reference review shows a mature multi-host memory pattern: host-specific lifecycle hooks, startup context loading, prompt-time context/rubric injection, stop/pre-compact capture, tolerant hot paths, and idempotent Codex hook installation. This is architectural reference only; TES must not copy its implementation, identifiers, branding, API assumptions, or storage model.

## Decision

1. **Cortex proactive extension.** A future Cortex layer may observe host lifecycle events, capture candidate session memory, inject relevant recall context, and summarize recent memory evidence before the agent acts.
2. **No automatic mesh writes.** Cortex may emit a `NEEDS_ALIGN` signal with evidence, impacted mesh surfaces, confidence, and suggested next action, but it must not write `PROJECT-STATE.md`, `PROJECT-ROADMAP.md`, `EXECUTION-LINE.md`, `QUALITY-GATES.md`, `DECISIONS/**`, or any other operational mesh file.
3. **Align remains the reconciler.** `/tes-align` consumes project anchors, decisions, evidence packets, and future Cortex drift evidence, then updates and certifies the operating mesh through `project_alignment_oracle.py`.
4. **Host-aware hooks.** Future proactive Cortex behavior must be modeled as a host matrix. Claude Code, Codex, and Cursor may share semantic intent, but their hook names, lifecycle layers, install paths, output contracts, feature flags, and trust/reload behavior must be verified per host before implementation.
5. **Tolerant hot path.** Proactive memory hooks must be advisory by default. They may inject context or report drift, but they must fail open for ordinary work unless a separate governed write, destructive action, secret, release, remote action, or owner-approved hard gate is involved.
6. **Evidence before capture.** Automatic or semi-automatic capture must preserve the existing Cortex write gate: no durable memory from loose chat, no derived cache as truth, no secrets, and no write without evidence and authorization.
7. **Implementation deferred.** Runtime work requires a later PRD/SPEC with host-contract fixtures, false-positive checks, idempotent installer tests, no-copy verification against the reference, and focused oracles for `NEEDS_ALIGN`.

## Boundary Matrix

| Surface | May Do | Must Not Do |
|---------|--------|-------------|
| `tes-cortex` | Recall, inspect, curate, reflect, propose capture, propose durable memory, signal drift | Rewrite the operating mesh or certify project alignment |
| `/tes-align` | Reconcile evidence into `docs/agents/**`, update mesh state, certify alignment | Become a background daemon or session-end auto-run |
| Host hooks | Observe lifecycle events and inject advisory context | Pretend Claude Code, Codex, and Cursor share one universal contract |
| MCP/CLI | Provide governed read and write lanes | Bypass the Cortex approval/evidence gate |

## `NEEDS_ALIGN` Contract

`NEEDS_ALIGN` is a bridge signal, not a write permission. A future Cortex implementation may produce it when durable memory evidence and the operational mesh diverge.

Minimum future shape:

```text
status=NEEDS_ALIGN
evidence_refs=<bounded repository-relative refs>
stale_surfaces=<mesh files or missing mesh claims>
reason=<why Cortex evidence and mesh position diverge>
next_action=run /tes-align or inspect retained evidence
```

The signal must be specific enough for `/tes-align` to act, but it must not contain target-specific private names in TES source code and must not imply that alignment already happened.

## Consequences

- TES gains a clean path toward proactive memory without confusing memory capture with operational position.
- The same project can be worked through Claude Code, Codex, and Cursor without relying on one host's hook semantics as the universal model.
- Forgetting to run `/tes-align` remains visible as drift instead of silently turning Cortex into a mesh writer.
- Future implementation must spend proof on hook contracts and false positives, not on broad governance prose.

## Non-Goals

- No hook runtime in this ADR phase.
- No changes to `tes-cortex` or `tes-align` skill behavior in this ADR phase.
- No automatic `/tes-align` at session end.
- No copied mem0-plugin code or TES behavior claim based on the reference alone.
- No release, public bundle, push, tag, publish, marketplace, cloud, secret, or destructive action.

## Future Implementation Gates

A later PRD/SPEC must prove:

1. host-specific hook contracts for Claude Code, Codex, and Cursor;
2. tolerant advisory output on ordinary work;
3. governed Cortex capture with evidence and explicit authorization;
4. `NEEDS_ALIGN` false-positive and false-negative fixtures;
5. `/tes-align` consumption of drift evidence without becoming a daemon;
6. idempotent install/update behavior for any hook or runtime surface;
7. negative checks that no reference implementation code, identifiers, or branding became TES source behavior.

## Evidence References

- `docs/mesh/CORTEX.md`
- `docs/mesh/CORTEX-MCP.md`
- `docs/mesh/TES-ALIGN-SKILL-SOURCE-OF-TRUTH.md`
- `docs/mesh/TES-ALIGN-SEMANTIC-RESIDUE.md`
- `docs/install/COMMAND-TRIGGERS.md`
- `src/adapters/codex/skills/tes-cortex/SKILL.md`
- `src/adapters/claude/skills/tes-cortex/SKILL.md`
- `src/adapters/codex/skills/tes-align/SKILL.md`
- `src/adapters/claude/skills/tes-align/SKILL.md`
- read-only mem0-plugin reference review: README, CHANGELOG, hook manifests, lifecycle scripts, skill surfaces, and regression tests

## Done

ADR 0007 is satisfied when the architecture is indexed, discoverable from Cortex and Align references, and locally validated without claiming runtime delivery. Runtime implementation remains deferred until a later authorized PRD/SPEC.
