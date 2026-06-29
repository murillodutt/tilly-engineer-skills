# TES Cortex Contract History

## Purpose

`/tes-cortex` governs Cortex memory: recall, read, verify, audit, rebuild, curate, learn, reflect, apply, remember, forget, consolidation, and runtime advisory signals.

## Why This Skill Exists

Memory boundaries are easy to violate (SQLite as truth, writing sources after import, ungoverned remember). This skill maps intents to safe operations.

## Contracts Preserved

- `docs/agents/cortex/sources/**`, cells, MAP, TRAIL, LINKS, CONTRACT are memory.
- SQLite recall/semantic DBs are rebuildable caches.
- Governed remember: plan then explicit approval.
- Apply/remember/forget require evidence and approval lanes.
- Read-only MCP preferred for recall/curate when available.
- Runtime Cortex may recall or inject context, propose capture, and emit `NEEDS_ALIGN`; it never writes the operating mesh or runs `/tes-align` automatically.

## Known Failure Modes Prevented

- Treating SQLite as source of truth.
- Writing `sources/**` after import.
- Ungoverned durable memory promotion.
- Skipping consolidation gate for forget.
- Treating `NEEDS_ALIGN` as alignment certification or a mesh write permission.

## Relationship To Other Skills

`tes-init` scaffolds cortex tree. `tes-mcp` exposes Cortex tools. `tes-align` may suggest Cortex promotion after Tier 1/2 review and remains the only operating-mesh reconciler.

## Changelog

`Version` records a skill operational contract version only when the skill declares one, followed by the containing TES package version when known. If no operational contract stamp exists, the TES package version is the shipped identity. `tver: 0.1.0` in roadmap, Super SPEC, ledger, or TDS frontmatter is document-template metadata, not a skill runtime or harness version. Patch-level changes can remain inside the same skill contract boundary; in that case the TES package version carries release identity until a future change alters the skill contract boundary itself.

| Date | Change | Evidence | Confidence |
|------|--------|----------|------------|
| 2026-06-29 | Documented universal Contract History version semantics so skill contract versions, TES package versions, and `tver` metadata are not conflated. | `docs/dist/0.3.229/tilly-engineer-skills-0.3.229.zip`; `scripts/public_bundle_oracle.py` | high |
| 2026-05-09 | Created cortex intent map skill. | Cortex MCP and `cortex.py` contract. | high |
| 2026-06-08 | Added contract history per Tilly skill standard. | Documentation authority tiers program. | high |
| 2026-06-26 | Added runtime-first advisory lane: recall/inject context, propose capture, and report `NEEDS_ALIGN` without mesh writes or automatic `/tes-align`. | SPEC-004 of Cortex runtime-first delivery and ADR 0007. | high |

## Do Not Lose

Markdown artifacts are truth; SQLite is derived recall. `NEEDS_ALIGN` is a signal, not a write permission.
