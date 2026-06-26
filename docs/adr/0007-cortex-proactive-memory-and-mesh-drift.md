---
tds_id: architecture.adr_0007_cortex_proactive_memory_and_mesh_drift
tds_class: architecture
status: active
consumer: maintainers, Cortex authors, TES Align authors, host integration authors, and release operators
source_of_truth: true
evidence_level: L1
tver: 0.2.0
---

# ADR 0007: Cortex Runtime-First Memory And Mesh Drift

Accepted on 2026-06-26. This ADR corrects the initial ADR 0007 framing: Cortex runtime-first behavior is the accepted TES target architecture, not an optional aspiration. This ADR records architecture only. It does not deliver hooks, scripts, MCP behavior, installer changes, skill changes, release identity, or public bundle changes.

## Core Rule

Cortex SHALL target a proactive, host-aware, runtime-first memory and sensing layer, but it must not become the operational mesh writer. `/tes-align` remains the canonical reconciler for `docs/agents/**`.

```text
Cortex runtime-first target: observe, capture, recall, inject, and signal drift.
Align reconciles, writes, and certifies the operating mesh.
Future implementation must prove host-specific behavior before delivery.
```

## Context

The current Cortex contract makes filesystem Markdown the durable memory source of truth and treats SQLite as a derived cache. `tes-cortex` exposes recall, read, verify, audit, rebuild, curate, learn, reflect, apply, remember, forget, and consolidation routes. Durable writes already require evidence and explicit authorization.

The current `/tes-align` contract owns semantic project alignment. It turns initial context into an evidenced operating mesh with project state, roadmap, execution line, quality gates, boundaries, glossary, decisions, and retained alignment evidence. It must discover before writing and must not invent architecture.

The current gap is continuity between those surfaces. Cortex can know or propose durable lessons, while the mesh can still lag behind until `/tes-align` runs. That lag is not a reason to let Cortex edit the mesh; it is a reason to make drift observable at runtime and route it to the correct reconciler.

A read-only mem0-plugin reference review shows a mature multi-host memory pattern: host-specific lifecycle hooks, startup context loading, prompt-time context/rubric injection, file/tool context injection, stop/pre-compact capture, tolerant hot paths, host wrappers, idempotent install/update behavior, and regression tests derived from production failures. This is architectural reference only; TES must not copy its implementation, identifiers, branding, API assumptions, or storage model.

TES can exceed the reference model by combining runtime memory with local Markdown truth, governed Cortex writes, explicit mesh-drift signaling, `/tes-align` reconciliation, project-scoped evidence, and deterministic oracles. The goal is not cloud memory alone; the goal is a local, auditable, agent-usable operating memory that can sense when the operational mesh is stale without silently rewriting it.

## Decision

1. **Runtime-first target architecture.** Cortex SHALL target proactive host-aware runtime behavior that can observe lifecycle context, capture candidate evidence, inject relevant recall context, summarize recent memory evidence, and signal drift before the agent loses the project lane.
2. **Reference-proven, TES-native translation.** The mem0-plugin reference validates the pattern of per-host lifecycle contracts, prompt-time injection, file/tool context, stop/pre-compact capture, tolerant hot paths, host wrappers, idempotent installers, and regression tests from real failures. TES adopts those principles only through TES-native implementation.
3. **TES ceiling beyond mem0-plugin.** TES pairs runtime memory with local Markdown truth, governed memory writes, explicit `NEEDS_ALIGN`, `/tes-align` reconciliation, retained evidence, source/package oracles, and Git-visible project history. That makes Cortex an operating-memory layer, not just a remote memory recall layer.
4. **No automatic mesh writes.** Cortex may emit a `NEEDS_ALIGN` signal with evidence, impacted mesh surfaces, confidence, and suggested next action, but it must not write `PROJECT-STATE.md`, `PROJECT-ROADMAP.md`, `EXECUTION-LINE.md`, `QUALITY-GATES.md`, `DECISIONS/**`, or any other operational mesh file.
5. **Align remains the reconciler.** `/tes-align` consumes project anchors, decisions, evidence packets, and future Cortex drift evidence, then updates and certifies the operating mesh through `project_alignment_oracle.py`.
6. **Host-aware hooks.** Future runtime Cortex behavior must be modeled as a host matrix. Claude Code, Codex, and Cursor may share semantic intent, but their hook names, lifecycle layers, install paths, output contracts, feature flags, platform assumptions, and trust/reload behavior must be verified per host before implementation.
7. **Tolerant hot path.** Runtime memory hooks must be advisory by default. They may inject context or report drift, but they must fail open for ordinary work unless a separate governed write, destructive action, secret, release, remote action, or owner-approved hard gate is involved.
8. **Evidence before capture.** Automatic or semi-automatic capture must preserve the existing Cortex write gate: no durable memory from loose chat, no derived cache as truth, no secrets, and no write without evidence and authorization.
9. **Implementation deferred.** Runtime work requires a later PRD/SPEC with host-contract fixtures, false-positive checks, idempotent installer tests, no-copy verification against the reference, and focused oracles for `NEEDS_ALIGN`.

## Boundary Matrix

| Surface | Target Capability | Must Not Do |
|---------|--------|-------------|
| `tes-cortex` | Recall, inspect, curate, reflect, propose capture, propose durable memory, inject relevant recall context, signal drift | Rewrite the operating mesh or certify project alignment |
| `/tes-align` | Reconcile evidence into `docs/agents/**`, update mesh state, certify alignment | Become a background daemon or session-end auto-run |
| Host hooks | Observe lifecycle events and inject advisory context when future runtime implementation is authorized | Pretend Claude Code, Codex, and Cursor share one universal contract |
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
- Future implementation must spend proof on host contracts, hot-path tolerance, false positives, no-copy boundaries, and idempotent installation, not on broad governance prose.

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
