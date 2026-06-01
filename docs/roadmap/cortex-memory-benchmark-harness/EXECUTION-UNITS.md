---
tds_id: roadmap.cortex_memory_benchmark_harness.execution_units
tds_class: roadmap
status: active
consumer: maintainers, Cortex maintainers, oracle authors, benchmark authors, release reviewers, and execution agents
source_of_truth: false
evidence_level: L1
tver: 0.1.0
---

# Cortex Memory Benchmark Harness Execution Units

This document is the execution-detail companion to
`docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-cortex-memory-benchmark-harness.md`.

Read the canonical Super SPEC first. Use this file only for the current
execution unit, so the harness can advance in small auditable waves without
turning planning detail into runtime behavior.

## SPEC-000 Preflight And Boundary

Objective: prove that this harness is an ADR 0001 implementation surface, not a
new memory authority.

Allowed files:

- `docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-cortex-memory-benchmark-harness.md`
- `docs/roadmap/cortex-memory-benchmark-harness/EXECUTION-UNITS.md`
- `docs/evals/**`
- `docs/mesh/**`
- `docs/tds/DOCS-INDEX.yml`
- `docs/INDEX.md`
- `docs/roadmap/README.md`

Forbidden:

- Runtime implementation.
- Package version bump.
- Remote, publish, push, or bundle updates.
- External dataset import.

Focused oracles:

- `python3 scripts/validate_tds.py`
- `python3 scripts/validate_doc_size.py`
- `python3 scripts/validate_reference_graph.py`
- `git diff --check`

Done when the harness boundary, non-objectives, result contract, and wave queue
are documented and indexed.

## SPEC-001 Native Memory Eval Contract

Objective: define a native TES Cortex memory eval schema and minimal docs.

Likely files:

- `docs/evals/CORTEX-MEMORY-BENCHMARKS.md`
- `benchmarks/cortex-memory/schema.json` or equivalent fixture-readable schema
- focused validator only if schema validation cannot stay inside the runner

Deliverables:

- normalized result schema;
- capability taxonomy;
- cutoff matrix;
- retained retrieval evidence rule;
- clear separation between deterministic and judge-assisted scoring.

Oracles:

- schema self-test;
- TDS validation;
- reference graph validation.

Negative checks:

- no benchmark registry as source of truth;
- no result file promoted as Cortex memory;
- no private project vocabulary in fixtures or docs.

## SPEC-002 Neutral Cortex Fixtures

Objective: create small generic fixtures that expose memory behavior without
importing external datasets.

Likely files:

- `benchmarks/cortex-memory/eval-dataset.json`
- fixture source documents under a neutral local fixture directory only if the
  runner needs materialized Cortex files

Required fixture families:

- stale versus current decision;
- contradiction retained versus resolved;
- temporal order;
- multi-source synthesis;
- insufficient evidence and abstention;
- preference grounded in source;
- instruction boundary and mutability lock.

Oracles:

- dataset shape validation;
- private vocabulary check;
- deterministic expected-ref check.

Negative checks:

- no private project names;
- no target-project package-manager assumptions;
- no synthetic fixture that encodes only the happy path.

## SPEC-003 Predict-Only Recall Runner

Objective: produce recall artifacts without judging or generating answers.

Likely files:

- `scripts/cortex_memory_benchmark.py`
- `scripts/cortex_memory_oracle.py`
- `benchmarks/cortex-memory/**`

Deliverables:

- `predict-only` mode;
- configurable cutoff matrix;
- preserved query, matches, ranks, refs, score debug, and latency;
- deterministic JSON output;
- no durable Cortex writes.

Oracles:

- runner self-test on tiny fixture;
- no-hidden-write snapshot check;
- Cortex self-test when shared Cortex behavior is touched.

Negative checks:

- read-only mode cannot append to `TRAIL.md`;
- missing recall evidence fails the run;
- fallback backend reports `DEGRADED` instead of pretending success.

## SPEC-004 Retrieval-Sufficiency Oracle

Objective: judge whether recalled evidence is enough to answer safely before
answer generation.

Likely files:

- `scripts/cortex_memory_oracle.py`
- `docs/evals/CORTEX-MEMORY-BENCHMARKS.md`
- `benchmarks/cortex-memory/**`

Deliverables:

- `evaluate-only` mode over retained recall artifacts;
- sufficiency status;
- required and forbidden evidence refs;
- abstention handling;
- no answer-generation dependency for recall certification.

Oracles:

- PASS fixture with complete evidence;
- FAIL fixture with missing evidence;
- NEEDS_REVIEW fixture with ambiguous contradiction;
- private vocabulary check.

Negative checks:

- answer fluency cannot compensate for missing evidence;
- highest-ranked match cannot override contradictory source refs;
- stale evidence cannot pass current-decision fixtures.

## SPEC-005 Rubric Nuggets And Event Ordering

Objective: add structured scoring for complex memory behavior.

Likely files:

- `scripts/cortex_memory_oracle.py`
- `benchmarks/cortex-memory/eval-dataset.json`
- `docs/evals/CORTEX-MEMORY-BENCHMARKS.md`

Deliverables:

- nugget scoring;
- event-ordering metric;
- contradiction and update rubrics;
- report fields that show which nugget failed.

Oracles:

- deterministic event-ordering fixture;
- partial-credit nugget fixture;
- contradiction-resolution fixture.

Negative checks:

- score cannot hide a hard source-boundary failure;
- event ledger evidence cannot replace durable Cortex truth;
- partial credit cannot certify a required mutability lock.

## SPEC-006 Checkpoint And Compare Runs

Objective: make long runs resumable and regression-friendly without turning
checkpoints into memory.

Likely files:

- `scripts/cortex_memory_benchmark.py`
- `scripts/cortex_memory_compare.py`
- `docs/evals/CORTEX-MEMORY-BENCHMARKS.md`

Deliverables:

- per-fixture checkpoint;
- resume mode;
- compare mode with metric deltas and pass/fail flips;
- config diff in report output.

Oracles:

- interrupted-run resume fixture;
- compare fixture with one regression and one improvement;
- checkpoint TTL or cleanup check when checkpoint files are introduced.

Negative checks:

- checkpoint state cannot certify memory behavior;
- compare output is evidence, not source of truth;
- broad reruns are not required for a focused fixture failure.

## SPEC-007 Evidence And Release Closure

Objective: close the harness only after docs, scripts, fixtures, evidence, and
release identity agree.

Likely files:

- `docs/evidence/**` only for current retained proof;
- `docs/evidence/current/CLAIMS.md` only if a supported claim changes;
- package version and bundle surfaces only after owner authorization;
- public docs only when adopter-visible behavior changes.

Required closure oracles:

- all focused harness self-tests;
- `python3 scripts/validate_tds.py`;
- `python3 scripts/validate_doc_size.py`;
- `python3 scripts/validate_reference_graph.py`;
- `python3 scripts/private_vocabulary_oracle.py`;
- `npm run commit:check` before any sealed package claim.

Negative checks:

- no commercial-use claim from local fixtures alone;
- no release claim if version identity is deferred;
- no target project workaround promoted into TES;
- no generated public HTML edited as source.
