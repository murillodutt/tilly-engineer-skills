---
tds_id: roadmap.goal_super_spec_tes_memory_lifecycle
tds_class: roadmap
status: active
consumer: maintainers, Cortex maintainers, adapter authors, oracle authors, release reviewers, and execution agents
source_of_truth: false
evidence_level: L1
tver: 0.1.1
---

# GOAL Super SPEC: TES Memory Lifecycle Implementation

Status: implemented through Wave 7 at local package-source level.

Capability: implement the TES memory lifecycle model in staged, releasable waves without promoting roadmap text into certified behavior.

## Canonical Artifact

Canonical Super SPEC: `docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-tes-memory-lifecycle.md`

Primary decision source: `docs/adr/0001-tes-memory-lifecycle.md`

Primary architecture and runtime surfaces:

- `docs/mesh/CORTEX.md`
- `docs/mesh/CORTEX-MCP.md`
- `docs/mesh/FIELD-REPORTS.md`
- `docs/adapters/ADAPTER-CAPABILITY-MATRIX.md`
- `docs/adapters/PLATFORM-DIFFERENCES.md`
- `src/adapters/**`
- `scripts/cortex.py`
- `scripts/cortex_mcp.py`
- `scripts/cortex_quality_oracle.py`
- `scripts/field_reports.py`
- `scripts/field_reports_quality_oracle.py`
- `scripts/materialize_adapter.py`
- `scripts/adapter_parity_readiness.py`
- `scripts/platform_surface_oracle.py`

## Current Meaning

This document is the retained execution plan, not delivered behavior.

The Wave 7 closure evidence records what was implemented and certified. This roadmap does not certify write-capable MCP tools, remote release readiness, or commercial-use claims.

ADR 0001 remains the memory source-of-truth architecture decision. ADR 0002 supersedes this roadmap's earlier read-only MCP assumption for current runtime posture: governed remember is now the narrow default MCP write lane, with `--read-only` as opt-out. Runtime and adapter source remain the delivered behavior. Evidence reports and oracles remain the only accepted path to certification.

## Assumptions

- TES Markdown memory remains the durable source of truth.
- At planning time, MCP stayed read-only until a later explicit decision changed that boundary. ADR 0002 is now that decision for governed remember only.
- Field Reports remain sanitized operational transport, not doctrine memory.
- Subagents may return findings to a parent, but must not write durable Cortex memory directly.
- Checkpoints preserve resumability and must not be promoted into Cortex cells automatically.
- Event records are evidence and coordination artifacts, not a replacement for governed Markdown source.
- Adapter capability sources must be refreshed before adapter implementation work because the current matrix has a dated refresh policy.
- Each behavior wave needs its own release identity decision before closeout.

## Non-Objectives

- Rebuild Cortex as a database-first product.
- Add write-capable MCP tools during planning.
- Treat repository Git hooks as platform lifecycle hooks.
- Patch installed target-project mirrors as the source of truth.
- Add cloud sync, remote services, publishing, marketplace, or push behavior.
- Introduce private project names, paths, product names, storage backends, or canary identifiers into tracked TES content.
- Claim `certified` before focused oracles and release identity are resolved.

## Maestro Operating Model

The maestro owns integration, scope, release identity, and final status. Specialists may investigate or patch bounded surfaces, but the maestro decides whether their output becomes package source.

| Role | Responsibility | Default Mode |
|------|----------------|--------------|
| Maestro | Scope, sequencing, integration, final status | Write only after gate |
| Cortex lifecycle builder | Cortex, MCP, operator, and consolidation behavior | Bounded worker |
| Adapter lifecycle builder | Codex, Claude, Cursor lifecycle contracts | Bounded worker |
| Oracle engineer | Fixtures, negative checks, focused gates | Bounded worker |
| Governance/TDS reviewer | Indexes, release identity, evidence policy | Read first |
| Field Reports/event reviewer | Ledger, feedback, sanitization boundary | Read first |
| Audit reviewer | False-green scan and 4D learning packet | Read-only by default |

Subagent protocol:

- Explorers are read-only unless a later prompt assigns a disjoint write set.
- Workers must receive explicit file ownership and must not revert others.
- Specialist output returns to the maestro as findings or patches.
- Durable memory writes are parent-owned and require the relevant write gate.
- No worker may certify a wave by summary alone.

## Central Rule

Memory lifecycle maturity means governed flow, not more storage:

```text
scope -> recall -> event -> checkpoint -> review -> authorized write -> evidence
```

Every wave must preserve this invariant:

```text
Markdown is truth.
Events are evidence.
Checkpoints are resumability.
Field Reports are transport.
MCP is read-only unless separately authorized.
```

## Required Preflight

Run before any implementation wave:

1. `git status --short --branch --untracked-files=all`
2. Classify dirty files as inherited, current, or unrelated.
3. Run the TES Mantra Gate for the intended state-changing action.
4. Re-read ADR 0001 and this Super SPEC.
5. Classify release identity for the wave before edits.
6. Select focused oracles before writing code or docs.

Stop if the worktree has unclassified changes, release identity is ambiguous, or the required oracle cannot be named.

## Source Freshness Gate

`docs/adapters/ADAPTER-CAPABILITY-MATRIX.md` declares a source verification date of 2026-05-09 and a 15 day refresh interval. On 2026-05-26, that matrix is past its own refresh window.

Before any adapter or platform-hook implementation:

- verify official platform sources for Codex, Claude, and Cursor;
- update the capability matrix only when the source changed or freshness must be re-established;
- run `python3 scripts/platform_surface_oracle.py --self-test`;
- do not use stale platform notes as construction truth.

## Global Stop Conditions

Stop the wave and report `blocked`, `degraded`, or `needs_review` when any of these appear:

- adapter source freshness is stale for the files being changed;
- private vocabulary would enter source, docs, fixtures, evidence, commits, or tags;
- MCP mutability is introduced without an explicit ADR or equivalent decision;
- a checkpoint is promoted into Cortex memory automatically;
- Field Reports are treated as durable source of truth;
- subagents are granted direct durable memory write authority;
- an oracle passes only happy-path fixtures;
- a release bump is required but deferred without owner decision;
- a target-project workaround is being promoted without portable evidence;
- `CERTIFIED` would be claimed from prose rather than observed behavior.

## Wave 0: Baseline And Cut Line

Purpose: prove the repository is ready for memory lifecycle implementation.

Owned surfaces: this roadmap, ADR 0001, the maintainer correlation rule, the adapter capability matrix, and baseline oracle scripts only when a real blocker is discovered.

Deliverables: classified worktree, refreshed adapter-source status or explicit `blocked` note, release identity decision for Wave 1, selected canary policy, and evidence-retention plan.

Oracles: `validate_tds.py`, `validate_doc_size.py`, `validate_reference_graph.py`, `git diff --check`, and `platform_surface_oracle.py --self-test`.

Done when Wave 1 has an explicit cut line, owned files, no-touch files, focused oracles, and no runtime behavior claim from this plan.

## Wave 1: Adapter Lifecycle Matrix And Subagent Boundary

Purpose: make the ADR lifecycle moments explicit across Codex, Claude, and Cursor before adding runtime behavior.

Lifecycle moments: recall, scope normalization, write gate, checkpoint, closeout, and subagent return.

Likely files: `docs/adapters/**`, `src/adapters/codex/AGENTS.md`, `src/adapters/claude/CLAUDE.md`, `src/adapters/cursor/rules/**`, `scripts/adapter_parity_readiness.py`, `scripts/materialize_adapter.py`, and `scripts/platform_surface_oracle.py`.

Deliverables: adapter by lifecycle moment matrix, status vocabulary limited to `certified`, `blocked`, `deferred`, `not available`, and `git-governed`, shared subagent boundary language, and a parity or materialization gate that fails when the boundary disappears.

Oracles: adapter parity, platform surface, materialization check, and a new or updated lifecycle matrix oracle when implemented.

Negative checks: repository Git hooks are not native platform lifecycle hooks, Cursor remains structural unless behavior is directly certified, subagents return evidence to the parent, and no adapter claims `certified` without an oracle.

Release identity: likely delivered behavior if adapter source or materialized surfaces change; default patch bump unless the owner explicitly defers.

## Wave 2: Scope Normalizer Contract

Purpose: create one deterministic scope contract shared by Cortex, Field Reports, event ledger, checkpoints, and future operator commands.

Likely files: `scripts/cortex.py`, `scripts/field_reports.py`, their quality oracles, one shared helper only if it removes real duplication, and docs under `docs/mesh/**` or `docs/architecture/**` when behavior changes.

Required scope fields: project, adapter, agent or parent agent, run, source, evidence reference, timestamp, and trust level or status.

Deliverables: deterministic normalizer, missing/malformed/cross-scope fixtures, shared unsafe-reference rejection, and docs that distinguish runtime scope from private identifiers.

Oracles: scope normalizer self-test, Cortex quality oracle, Field Reports quality oracle, and private vocabulary oracle when fixtures or docs are added.

Negative checks: no private path in fixtures, no broad target fallback, no target-specific package-manager assumption, and no hidden write during normalization.

Release identity: delivered behavior if scripts or adapter-visible contracts change.

## Wave 3: Event Ledger Read-Only Inspection

Purpose: introduce an inspectable lifecycle event ledger without replacing Field Reports, `TRAIL.md`, evidence reports, or Cortex memory.

Likely files: new `scripts/event_ledger.py` and oracle, `scripts/field_reports.py`, `docs/mesh/FIELD-REPORTS.md`, `docs/mesh/CORTEX.md`, and `docs/install/AGENT-ORACLE-INVENTORY.md`.

Minimum commands: `event list`, `event status`, and fixture-backed schema inspection.

Deliverables: local event schema, status enum, lifecycle mapping, sanitization for secrets and private context, read-only inspection, and no automatic Cortex write.

Oracles: event ledger self-test, sanitization fixtures, no-hidden-write check, and Field Reports quality oracle.

Negative checks: ledger is not Field Reports with another name, Field Reports are not durable truth, event entries cannot carry private identifiers, and happy-path schema validation is not enough.

Release identity: delivered behavior if a script, command, oracle, or public doc changes.

## Wave 4: Checkpoint Lane With TTL

Purpose: support resumability without confusing temporary execution state with durable memory or evidence certification.

Likely files: new `scripts/checkpoint.py` and oracle, Cortex and Field Reports scripts, their mesh docs, and the oracle inventory.

Deliverables: checkpoint schema, TTL and cleanup behavior, resume status model, explicit non-promotion rule, and fixture proving expired checkpoint cleanup.

Oracles: checkpoint self-test, TTL and cleanup oracle, no automatic Cortex write test, and private vocabulary oracle for fixtures.

Negative checks: checkpoint is not certification evidence, not a Cortex cell, cannot bypass closeout or release identity, and failed resume state remains visible and bounded.

Release identity: delivered behavior if runtime, command, adapter, or user-facing docs change.

## Wave 5: Cortex Operator Layer

Purpose: provide explicit operator commands after scope, ledger, and checkpoint boundaries are proven.

Candidate commands: `health`, `peek`, `review`, `checkpoint`, `remember`, and `forget`.

Likely files: Cortex runtime, Cortex MCP, Cortex quality oracle, Cortex mesh docs, MCP docs, and adapter skill docs under `src/adapters/**/skills/tes-cortex/**`.

Deliverables: read-only commands remain mechanically read-only, mutating commands require explicit authorization, operator docs name mutability class, and MCP remains read-only unless separately authorized.

Oracles: Cortex self-test, Cortex quality oracle, MCP self-test, and mutability oracle for read-only and write-capable paths.

Negative checks: no hidden write from read-only commands, no write-capable MCP drift, no `remember` or `forget` without write gate, and no command certifies itself without evidence.

Release identity: delivered behavior and likely public surface change.

## Wave 6: Consolidation Gate

Purpose: make durable memory writes rare, authorized, observable, and reviewable.

Likely files: Cortex runtime and quality oracle, event ledger, checkpoint lane, Cortex docs, Mantra Gate docs, and current claims only if a supported claim changes.

Deliverables: consolidation workflow, observed authorized write evidence, lock or review model, and rejection path for ambiguous, stale, or cross-scope memory proposals.

Oracles: consolidation gate oracle, observed-write fixture, rejection fixtures, private vocabulary oracle, and relevant Cortex, ledger, and checkpoint oracles.

Negative checks: no `certified` without observed authorized write, no stale checkpoint promoted into durable memory, no event-only evidence promoted into doctrine, and no subagent direct memory write.

Release identity: delivered behavior requiring package version and public bundle decision unless explicitly deferred by the owner.

## Wave 7: Release And Real-Project Canary Closure

Purpose: close the full ADR implementation only after the package behavior, docs, adapters, oracles, and release identity agree.

Likely files: version surfaces, installer and public docs sources, plugin manifests, bundles, indexes, and release scripts required by the bump.

Deliverables: version, bundle, public docs, and installer decisions; current evidence claim only if supported; and canary replay using neutral tracked vocabulary.

Required closure oracles: all focused wave oracles, TDS, doc size, reference graph, private vocabulary, `tes_bump.py --governance-check`, `npm run commit:check`, and `npm run release:check` only after an authorized release tag or fixed public installer ref is part of the claim.

Negative checks: no release claim if version identity is deferred, no commercial-use claim from one canary, no private canary identifier in tracked content, and no generated public HTML edited as source.

Done when the maintainer correlation rule is satisfied, all relevant oracles pass, release identity is explicit, and final evidence names residual risk without overclaim.

## Evidence Policy

Use evidence only when it proves a claim or explains a blocker.

Evidence may include:

- current claim deltas in `docs/evidence/current/CLAIMS.md`;
- retained reports under `docs/evidence/reports/YYYY/MM/DD/<domain>/<run-id>/`;
- command output summaries when the raw output is retained or reproducible;
- canary notes with neutral placeholders only.

Evidence must not include:

- private project names;
- private filesystem paths;
- secrets, tokens, remotes, or credentials;
- target-specific workaround text as package doctrine.

## Release Identity Rule

This Super SPEC alone does not require a package bump.

Any future wave that changes adopter-visible skills, triggers, installer behavior, helper/runtime scripts, plugin metadata, public docs, MCP, Field Reports, Cortex behavior, or adapter materialization requires a release identity decision before closeout.

Default rule: bump the patch version and update correlated release surfaces when delivered behavior changes.

Exception rule: if the owner explicitly defers the bump, state the deferral in the closeout and do not call the package sealed by version identity.

## Definition Of Complete ADR Implementation

The ADR is fully implemented only when:

- Wave 0 through Wave 7 are either complete or explicitly deferred;
- every delivered behavior has a focused oracle and retained evidence;
- adapter lifecycle claims match delivered adapter source;
- scope normalization is shared by Cortex, Field Reports, events, and checkpoints;
- event ledger and checkpoint behavior are inspectable and sanitized;
- operator commands have explicit mutability classes;
- durable memory writes require authorization and observed evidence;
- release identity is resolved;
- `npm run commit:check` passes before any sealed package claim.
