---
tds_id: roadmap.goal_super_spec_cortex_memory_benchmark_harness
tds_class: roadmap
status: active
consumer: maintainers, Cortex maintainers, oracle authors, benchmark authors, release reviewers, and execution agents
source_of_truth: false
evidence_level: L1
tver: 0.2.0
---

# GOAL Super SPEC: Cortex Memory Benchmark Harness

Status: retained execution plan. The harness was locally implemented and certified in package-source version `0.3.135`; remote release certification and commercial-use claims remain deferred.

Capability: add a governed Cortex memory benchmark harness that tests recall, retrieval sufficiency, temporal reasoning, contradiction handling, and regression without changing the ADR 0001 memory authority boundary.

## Canonical Artifact

Canonical Super SPEC: `docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-cortex-memory-benchmark-harness.md`

Primary decision source: `docs/adr/0001-tes-memory-lifecycle.md`

Execution unit companion: `docs/roadmap/cortex-memory-benchmark-harness/EXECUTION-UNITS.md`

Primary related surfaces:

- `docs/evals/EVALS.md`
- `docs/mesh/CORTEX.md`
- `docs/mesh/CORTEX-MCP.md`
- `docs/mesh/CHECKPOINTS.md`
- `docs/mesh/EVENT-LEDGER.md`
- `docs/mesh/SCOPE-CONTRACT.md`
- `docs/governance/MAINTAINER-CORRELATION-RULE.md`
- `benchmarks/context-mesh/eval-dataset.json`
- `benchmarks/cortex-memory/eval-dataset.json`
- `benchmarks/cortex-memory/result-schema.json`
- `scripts/cortex_memory_benchmark.py`
- `scripts/cortex_memory_oracle.py`
- `scripts/cortex_memory_compare.py`

## Governing Matrix

| Layer | Meaning |
|-------|---------|
| ADR 0001 | Markdown remains durable memory truth; indexes, events, checkpoints, and oracles are derived or evidence surfaces. |
| Memory Benchmark Harness | Measures Cortex recall and memory behavior through repeatable fixtures and run artifacts. |
| Oracles | Judge retrieval sufficiency, factual grounding, temporal order, contradiction handling, and abstention. |
| Evidence | Stores reproducible run outputs, summaries, and reports without promoting them to memory truth. |
| Non-Change | Does not add a memory backend, write-capable MCP, automatic Cortex writes, or benchmark registry authority. |

## Current Meaning

This document is the retained implementation plan and boundary record. The local package-source implementation is recorded in `docs/evidence/reports/2026/05/26/cortex-memory-benchmark-harness/REPORT.md`.

The benchmark harness must strengthen ADR 0001 by proving memory behavior. It must not create a second memory architecture. Run registries, indexes, result JSON, SQLite files, checkpoints, model outputs, and judge decisions remain derived evidence unless an authorized Cortex write path promotes a durable claim with source evidence.

## Creation Gate Record

| Field | Record |
|-------|--------|
| `VERIFY` | ADR 0001, Cortex mesh docs, eval method docs, roadmap precedents, TDS index, and the local memory benchmark study were inspected before writing. |
| `SCOPE` | Add this Super SPEC and correlated documentation indexes only. No runtime, package version, adapter, MCP, installer, or bundle changes. |
| `BEST_PATH` | Create a governed roadmap artifact under ADR 0001 instead of opening a second ADR or copying an external benchmark stack. |
| `DOCUMENT` | This Super SPEC plus `docs/roadmap/README.md`, `docs/INDEX.md`, and `docs/tds/DOCS-INDEX.yml`. |
| `ORACLE` | `python3 scripts/validate_tds.py`, `python3 scripts/validate_doc_size.py`, `python3 scripts/validate_reference_graph.py`, and `git diff --check`. |
| `RESOLVE` | No blocker found; runtime implementation is intentionally deferred to later waves. |
| `STATUS` | `PROCEED` |

## Assumptions

- The local benchmark study is a pattern anchor, not package source of truth.
- Cortex Markdown remains the durable source of memory truth.
- MCP remains read-only.
- The first implementation should be CLI and evidence oriented, not UI first.
- Existing context mesh eval machinery remains separate from Cortex memory benchmarks until an explicit adapter or shared helper earns its keep.
- Any runtime command, script, fixture, or user-visible documentation added in a later wave may be delivered behavior and needs release identity review.

## Non-Objectives

- Create a new ADR.
- Copy an external memory-server, vector database, Docker, SaaS, or web-app stack into TES.
- Treat benchmark results or run registries as durable memory.
- Add write-capable MCP or automatic Cortex writes.
- Commit external datasets or large benchmark result files.
- Claim commercial memory quality from local fixtures alone.
- Add a UI before the CLI contract and evidence schema are stable.
- Store private project names, product names, paths, or canary identifiers in tracked TES source, fixtures, reports, or commits.

## Central Rule

The harness tests memory behavior without becoming memory:

```text
fixture -> recall artifact -> sufficiency oracle -> rubric score -> report
```

Every benchmark artifact must preserve this invariant:

```text
Markdown is truth.
Recall artifacts are evidence.
Scores are judgments.
Run registries are indexes.
Checkpoints are resumability.
No benchmark output writes Cortex memory by itself.
```

## Capability Taxonomy

The first Cortex memory benchmark matrix should cover:

| Capability | TES Meaning |
|------------|-------------|
| `information_extraction` | Retrieve exact grounded facts from Cortex cells and sources. |
| `temporal_reasoning` | Prefer the correct time window and avoid stale facts. |
| `event_ordering` | Reconstruct chronological order from `TRAIL.md`, event ledger, or source refs. |
| `knowledge_update` | Prefer the current governed decision while retaining historical context. |
| `contradiction_resolution` | Surface conflicts instead of flattening them into false certainty. |
| `multi_session_reasoning` | Combine related evidence across sources, cells, and prior lifecycle events. |
| `preference_following` | Use durable user or project preference only when it is source-grounded. |
| `instruction_following` | Respect Cortex mutability, source, and privacy boundaries while answering. |
| `summarization` | Produce compact, source-backed synthesis without losing evidence lineage. |
| `abstention` | Return insufficient-evidence status instead of inventing memory. |

## Target Result Contract

The first native result schema should be small and explicit:

| Field | Purpose |
|-------|---------|
| `schema_version` | Version the benchmark artifact contract. |
| `metadata` | Run id, git head, benchmark id, model or backend, adapter, scope, and timestamps. |
| `fixture` | Stable fixture id, capability, question, expected evidence, and stop condition. |
| `recall` | Query, backend, cutoff, latency, matches, ranks, scores, refs, and score debug. |
| `synthesis` | Optional generated answer, prompt hash, output hash, and cited refs. |
| `judgment` | Deterministic or LLM-assisted score, rubric nuggets, status, and rationale. |
| `cutoffs` | Results for `top_5`, `top_10`, `top_20`, `top_50`, or another declared matrix. |
| `checkpoint` | Optional resume state reference; never durable memory. |
| `evidence` | Paths to retained raw artifacts and summary report. |

Retrieved Cortex matches must always be preserved. A passing answer without preserved retrieval evidence is a benchmark failure.

## Scoring Model

Use simple status plus rubric nuggets before adding complex metrics.

| Status | Meaning |
|--------|---------|
| `PASS` | Retrieved evidence and answer satisfy the fixture. |
| `FAIL` | Evidence or answer contradicts the fixture. |
| `BLOCKED` | Required backend, model, fixture, or source is unavailable. |
| `DEGRADED` | Fallback backend ran, but the intended path did not. |
| `NEEDS_REVIEW` | Oracle cannot decide safely from retained evidence. |
| `NOT_AVAILABLE` | Capability is out of scope for the current run. |

Rubric nuggets should be scored `0`, `0.5`, or `1` when semantic judgment is needed. Deterministic checks should remain exact when exactness is the point.

## Execution Units

Detailed execution units live in `docs/roadmap/cortex-memory-benchmark-harness/EXECUTION-UNITS.md`.

| Unit | Purpose |
|------|---------|
| `SPEC-000` | Prove boundary, no new memory authority, and index the plan. |
| `SPEC-001` | Define the native Cortex memory eval contract. |
| `SPEC-002` | Add neutral Cortex fixtures. |
| `SPEC-003` | Implement predict-only recall artifacts. |
| `SPEC-004` | Implement retrieval-sufficiency oracle. |
| `SPEC-005` | Add rubric nuggets and event-ordering checks. |
| `SPEC-006` | Add checkpoint and compare-run behavior. |
| `SPEC-007` | Close evidence and release identity. |

Execution agents must read this Super SPEC first, then the companion execution unit document for the current unit only. Do not load or implement later units as active scope until the current unit has passed its focused oracles.

## Deferred UI Path

A local viewer or dashboard may be useful later, but it is deferred until the CLI result contract, fixtures, oracles, and compare-run behavior are stable. If a UI is added, it should consume retained result artifacts and follow the TES frontend and Nuxt governance path instead of copying an external Next.js application wholesale.

## Release Identity Rule

This Super SPEC alone does not require a package version bump.

Later waves that add scripts, fixtures, package commands, adopter-visible docs, adapter behavior, MCP behavior, installer behavior, public docs, or generated bundle content are delivered behavior unless explicitly classified otherwise. Default release policy is a patch bump for delivered behavior, unless the owner explicitly defers that bump and the closeout records the deferral.

## Global Stop Conditions

Stop and report `BLOCKED`, `DEGRADED`, or `NEEDS_REVIEW` when:

- a benchmark artifact would become memory source of truth;
- a write-capable MCP path is introduced;
- Cortex writes occur without explicit authorization and evidence;
- external datasets or large result files are about to be committed;
- private identifiers appear in fixtures, docs, reports, commits, or tags;
- a judge prompt can pass without preserved retrieval evidence;
- release identity is required but unresolved;
- a UI or backend is added before the CLI contract is proven.

## Definition Of Complete Harness Implementation

The harness is complete only when:

- native Cortex memory eval schema exists and is validated;
- neutral fixtures cover the capability taxonomy;
- predict-only recall artifacts preserve retrieved evidence;
- retrieval-sufficiency oracle can pass, fail, block, and request review;
- rubric nuggets expose partial memory failures;
- compare-run output identifies regressions and improvements;
- checkpoints resume long runs without becoming memory;
- retained evidence names residual risk without overclaim;
- release identity is resolved before any delivered-behavior closure;
- `npm run commit:check` passes before any sealed package claim.
