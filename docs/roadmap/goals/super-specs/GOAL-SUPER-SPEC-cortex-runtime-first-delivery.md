---
tds_id: roadmap.goal_super_spec_cortex_runtime_first_delivery
tds_class: roadmap
status: active
consumer: maintainers, Cortex runtime authors, TES Align authors, host integration authors, oracle authors, release reviewers, and execution agents
source_of_truth: false
evidence_level: L1
tver: 0.1.0
---

# GOAL Super SPEC: Cortex Runtime-First Delivery

Status: active preflight and implementation plan. This document materializes the runtime delivery plan for ADR 0007. It does not deliver hooks, scripts, MCP behavior, installer changes, skill changes, public bundle changes, release identity changes, or runtime behavior.

Capability: implement ADR 0007 as delivered behavior only through later SPECs, after executable host fixtures prove the per-host hook contracts for Claude Code, Codex, and Cursor.

## Canonical Artifact

Canonical Super SPEC: `docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-cortex-runtime-first-delivery.md`

Primary decision source: `docs/adr/0007-cortex-proactive-memory-and-mesh-drift.md`

Baseline commits: `5d4a9fcf`, `a0b9cf95`, `06774608`

Baseline release: `0.3.201`

Loop ledger: `tmp/GOAL-EXECUTION-LOOP-LEDGER-cortex-runtime-first-delivery.md`

## Anchor Packet

| Field | Value |
|-------|-------|
| `anchor_class` | `ADR` |
| `anchor_path` | `docs/adr/0007-cortex-proactive-memory-and-mesh-drift.md` |
| `anchor_hash_git` | `6713fd1af97271e42e9d732b27f315c65954b069` |
| `anchor_sha256` | `3080ba9787a241de7fb50092b4462d22ae841a014b58578e9508c92504826b3b` |
| `tree_adversary_status` | `OBJECTIONS_REPAIRED` |

## Central Rule

```text
Cortex senses, recalls, proposes, and signals.
/tes-align reconciles, writes, and certifies.
```

Cortex runtime work must not write the operating mesh, run `/tes-align` automatically, copy mem0 implementation, copy mem0 identifiers, copy mem0 branding, assume a mem0 API, assume a storage backend, or introduce cloud assumptions. `NEEDS_ALIGN` is a signal with evidence, not an alignment result.

## Evidence Extract

- ADR 0007 accepts runtime-first Cortex as the target architecture and explicitly defers delivered runtime behavior to later PRD/SPEC work.
- `docs/mesh/CORTEX.md` keeps Markdown Cortex artifacts as truth and derived indexes as caches; proactive runtime behavior remains no-write until later implementation.
- `docs/mesh/CORTEX-MCP.md` keeps MCP project-scoped and governed; it does not grant hook runtime authority.
- `docs/mesh/TES-ALIGN-SKILL-SOURCE-OF-TRUTH.md` and `docs/mesh/TES-ALIGN-SEMANTIC-RESIDUE.md` keep `/tes-align` as the mesh reconciler and freshness gate.
- Existing host notes show hook names and output contracts differ by host; SPEC-001 must refresh and prove them with executable fixtures before any runtime claim.

## Host Matrix Summary

SPEC-001 owns the executable proof. This table is a baseline summary only.

| Host | Hook contract to prove | Output contract to prove | Install surface to prove |
|------|------------------------|--------------------------|--------------------------|
| Claude Code | `SessionStart`, `PreToolUse`, `UserPromptSubmit`, and compact/stop capture where supported | exit-code blocking with agent-visible feedback, advisory context injection, and input rewrite only where supported | `.claude/settings.json`, preserving foreign hooks |
| Codex | `SessionStart`, `PreToolUse`, `UserPromptSubmit`, `PreCompact`, and Codex-only status messaging where supported | Codex hook output semantics for allow/block, advisory context, input rewrite, and status messages | `.codex/config.toml`, feature/trust requirements, preserving foreign config |
| Cursor | `sessionStart`, `preToolUse`, `beforeSubmitPrompt`, and `preCompact` where supported | Cursor JSON permission decisions for blocking and prompt continuation messages, not universal exit-code semantics | `.cursor/hooks.json`, preserving foreign hooks |

No later SPEC may claim runtime delivery from this table alone. The fixtures must exercise the real per-host payload shapes, allowed output fields, block/advisory behavior, trust or reload states, idempotent install/update, and a negative fixture for the wrong host contract.

## Engineering Method Profile

`STRUCTURAL_METHOD=platform-runtime-hooks-v1`

Method packet:

- one semantic Cortex runtime core;
- host-specific hook contracts around that core;
- no fake universal hook protocol;
- no growth of `scripts/cortex.py` into a god script;
- executable topology probes required for every runtime SPEC;
- build/typecheck cannot replace runtime hook probes;
- failed runtime attempts must classify `bug_vs_architecture` before retry.

## Scope Lock

SPEC-000 may create this Super SPEC and, under `SPEC_REPAIR_BY_LLM`, update `docs/tds/DOCS-INDEX.yml` only for TDS index consistency. No blocking ambiguity was found in the baseline read.

Forbidden in SPEC-000: `src/**`, `scripts/**`, adapters, hooks, installers, package files, public bundle files, `docs/dist/**`, README, release identity changes, remote sync, push, tag, publish, cloud, secrets, runtime edits, and any docs/index change beyond the TDS entry.

## Scripts Consumer Classification

| SPEC | `scripts/**` consumer classification |
|------|--------------------------------------|
| SPEC-000 | No script edits. Existing validators run as maintainer gates only. |
| SPEC-001 | Host-contract fixtures/oracles are maintainer-gate unless installed or copied to target runtime. |
| SPEC-002 | Cortex runtime core/helper scripts are delivered behavior when adopter-installed, invoked by hooks, or certified as runtime. |
| SPEC-003 | Host hook adapter scripts for Claude Code, Codex, or Cursor are delivered behavior when adopter-installed or invoked by hooks. |
| SPEC-004 | Skills, MCP, and operator scripts are delivered behavior when installed, invoked, or surfaced to adopters; source-only validators remain maintainer-gate. |
| SPEC-005 | Installer, idempotency, installed-target, and adapter materialization scripts are delivered behavior. |
| SPEC-006 | Documentation validators remain maintainer-gate; public/product docs can become delivered behavior if adopter-visible. |
| SPEC-007 | Release validators are maintainer-gate; version, bundle, installer, adapter, or public-doc script changes remain delivered behavior. |

## Tree Adversary Repair Summary

- SPEC-000 is bounded to plan-only preflight; no runtime files move.
- SPEC-001 must prove host contracts with executable fixtures before runtime claims.
- The runtime core must be hook-shaped and no-write: sense, recall, propose, signal.
- Negative tests must prove no mesh writes, no automatic `/tes-align`, and no copied mem0 implementation, identifiers, branding, API, storage, or cloud assumptions.
- From SPEC-001 onward, the ledger must record release identity, host proof, structural method result, negative checks, and sync status.

## Declared Ordered Units

Declared order is exact:

1. SPEC-000 Preflight And Runtime Plan
2. SPEC-001 Host Contract Fixtures
3. SPEC-002 Cortex Runtime Core
4. SPEC-003 Host-Aware Hook Adapters
5. SPEC-004 Skills, MCP, And Operator Surfaces
6. SPEC-005 Installer, Idempotency, And Installed-Target Proof
7. SPEC-006 Docs And Product Boundary
8. SPEC-007 Release Identity And Local Certification

Do not execute a later SPEC until the prior SPEC is validated and the parent opens the next active unit.

### SPEC-000: Preflight And Runtime Plan

Objective: establish baseline, extract host/reference evidence, classify script consumers, and materialize this implementation PRD/SPEC before code.

Allowed files: `docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-cortex-runtime-first-delivery.md`; `docs/tds/DOCS-INDEX.yml` only for TDS index consistency.

Forbidden moves: runtime edits, script edits, adapter edits, installer edits, package/version/bundle edits, remote sync.

Focused oracles: `python3 scripts/validate_reference_package.py`; `python3 scripts/validate_tds.py`; `python3 scripts/materialize_adapter.py all --check`; `git diff --check`.

Negative checks: no changed files outside allowed paths; no runtime delivery claim; no mesh write; no automatic `/tes-align`; no mem0 copy assumption.

Commit message: `docs/spec: define cortex runtime-first implementation plan`

### SPEC-001: Host Contract Fixtures

Objective: prove Claude Code, Codex, and Cursor hook names, payloads, output contracts, trust/reload states, and idempotent config behavior with executable fixtures before runtime code.

Allowed files: focused host-contract fixture/oracle files, host capability docs, this Super SPEC if repair is needed, and TDS/index surfaces required by changed docs.

Forbidden moves: runtime core implementation, hook delivery, installer behavior change, release bump, and claims from prose-only host notes.

Focused oracles: new host-contract fixture self-test; `python3 scripts/platform_surface_oracle.py --self-test`; `git diff --check`.

Negative checks: wrong host output contract fails; Cursor is not treated as exit-code blocking; Codex-only features do not leak to Claude/Cursor; fixture cannot pass without executing payload checks.

Commit message: `test(cortex): add runtime host contract fixtures`

### SPEC-002: Cortex Runtime Core

Objective: implement the smallest no-write semantic core that can sense lifecycle context, recall bounded Cortex evidence, propose capture, and emit `NEEDS_ALIGN`.

Allowed files: focused Cortex runtime core/helper files, focused core fixtures, mesh docs, oracle inventory, and correlated TDS/index surfaces.

Forbidden moves: mesh writes, automatic `/tes-align`, durable memory writes without existing gates, host-specific hook config, installer changes, cloud/storage assumptions, and expansion of `scripts/cortex.py` into orchestration.

Focused oracles: core self-test; no-write runtime oracle; existing Cortex self-test; `git diff --check`.

Negative checks: `PROJECT-STATE.md`, `PROJECT-ROADMAP.md`, `EXECUTION-LINE.md`, `QUALITY-GATES.md`, and `DECISIONS/**` are never written; `NEEDS_ALIGN` is a signal only.

Commit message: `feat(cortex): add no-write runtime signal core`

### SPEC-003: Host-Aware Hook Adapters

Objective: connect the semantic core to the Claude Code, Codex, and Cursor hook contracts proven in SPEC-001, with one semantic core and host-specific adapters.

Allowed files: host hook adapter source, hook fixtures, materialized adapter surfaces, correlated docs, and release/version surfaces if authorized.

Forbidden moves: fake universal hook protocol, copying one host protocol as another host's truth, blocking ordinary work without a governed hard-gate condition, mesh writes, automatic `/tes-align`.

Focused oracles: host hook fixture self-test for Claude Code, Codex, and Cursor; materialization check; runtime topology probe; `git diff --check`.

Negative checks: Cursor is not exit-code blocking; Codex-only output fields do not become universal; foreign hooks preserved; advisory failures fail open; hard block only for governed destructive/secret/release/remote/write-gate cases.

Commit message: `feat(cortex): wire host-aware runtime hook adapters`

### SPEC-004: Skills, MCP, And Operator Surfaces

Objective: update Cortex, Align, MCP, and operator surfaces so runtime signals are available, explicit, and governed without changing the central ownership rule.

Allowed files: skill sources, MCP/operator surfaces, focused fixtures, correlated mesh docs, and release/version surfaces if authorized.

Forbidden moves: Cortex mesh writes, automatic `/tes-align`, ungoverned MCP writes, target override leaks, background daemon behavior, private vocabulary in fixtures.

Focused oracles: Cortex/MCP/operator self-tests; `python3 scripts/project_alignment_oracle.py --self-test`; focused `NEEDS_ALIGN` fixture; materialization check; `git diff --check`.

Negative checks: `NEEDS_ALIGN` does not modify mesh files; stale mesh remains `NEEDS_REVIEW` or `FAIL` until `/tes-align` runs and passes; MCP does not bypass the write gate.

Commit message: `feat(cortex): expose governed runtime operator surfaces`

### SPEC-005: Installer, Idempotency, And Installed-Target Proof

Objective: install and update the runtime surfaces idempotently in target projects and prove installed-target behavior without using this repository root as the target.

Allowed files: installer, adapter materialization, installed-target fixtures, install/update docs, correlated package surfaces, and release/version surfaces if authorized.

Forbidden moves: global host config mutation, destructive overwrite of project-owned hooks, hidden trust/reload requirements, cloud/plugin assumptions, mesh writes, automatic `/tes-align`.

Focused oracles: installer self-test; idempotency fixture; installed-target smoke; `python3 scripts/materialize_adapter.py all --check`; `git diff --check`.

Negative checks: reinstall does not duplicate hooks; foreign hooks are preserved; host recognition state is reported instead of inferred from file presence; installed-target proof is not run against the package root.

Commit message: `feat(installer): install cortex runtime hooks idempotently`

### SPEC-006: Docs And Product Boundary

Objective: update adopter-visible docs and product-boundary references so they describe delivered runtime behavior without overstating certification, cloud, memory, or automatic alignment.

Allowed files: mesh docs, adapter docs, install docs, public docs sources, TDS/index surfaces, and release/version surfaces if authorized.

Forbidden moves: claiming runtime delivery before SPEC-003..SPEC-005 proof, calling Cortex a mesh writer, implying automatic `/tes-align`, adding mem0 implementation/API/storage/cloud assumptions, private vocabulary.

Focused oracles: `python3 scripts/validate_tds.py`; `python3 scripts/validate_reference_package.py`; public-doc checks if public docs change; `git diff --check`.

Negative checks: docs do not claim automatic alignment, cloud memory, universal hook protocol, or runtime certification beyond observed oracles.

Commit message: `docs(cortex): document runtime-first product boundary`

### SPEC-007: Release Identity And Local Certification

Objective: resolve delivered-behavior release identity, update correlated version/bundle/public surfaces if authorized, and certify the full runtime-first delivery locally.

Allowed files: package version surfaces, bundle/public docs, docs indexes, release validators, correlated source/docs from SPEC-001..SPEC-006, and evidence surfaces.

Forbidden moves: push, tag, publish, marketplace, cloud, remote sync, or release claim without explicit owner authorization for that exact action.

Focused oracles: `npm run commit:check`; `python3 scripts/validate_reference_package.py`; `python3 scripts/validate_tds.py`; `python3 scripts/materialize_adapter.py all --check`; full host runtime smoke suite; `git diff --check`.

Negative checks: no missing correlated version surface; no stale bundle pointer; no unproved host; no mem0 copied identifiers; no private vocabulary; no remote-release claim.

Commit message: `release: certify cortex runtime-first delivery`

## Stop States

- `GO`: active SPEC is bounded, validated, and may close locally.
- `NEEDS_OWNER_DECISION`: release identity, scope, host behavior, or risk requires owner choice.
- `NEEDS_DISCOVERABILITY`: TDS/index/docs routing is missing or out of allowed scope.
- `NEEDS_INTEGRATION_ORACLE`: runtime or hook integration lacks executable proof.
- `NEEDS_STRUCTURAL_METHOD`: topology, ownership, or method profile is unproven.
- `BLOCKED`: local required proof cannot run or fails without a safe repair in scope.
- `SAFETY_BLOCKED`: destructive, secret, remote, release, cloud, or privacy risk lacks explicit authorization.

## Release Identity Plan

SPEC-000 has no delivered behavior and no release identity change.

From SPEC-001 onward, any change that adds, removes, or changes adopter-visible skills, triggers, installer behavior, helper/runtime scripts, plugin metadata, public docs, MCP, Field Reports, Cortex behavior, adapter materialization, or generated installed surfaces defaults to patch bump plus correlated bundle/version surfaces.

No SPEC may push, tag, publish, create a release, run marketplace actions, or perform remote sync without explicit owner authorization for that exact action.

## SPEC-000 Closeout Contract

This document claims no runtime delivery. SPEC-000 may close only with changed-file evidence, the requested focused oracles, negative-check summary, and an explicit statement that runtime delivery remains deferred to later SPECs.
