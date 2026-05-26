---
tds_id: evidence.cortex_memory_benchmark_harness_20260526
tds_class: evidence
status: active
consumer: Cortex maintainers, benchmark authors, oracle authors, and release reviewers
source_of_truth: false
evidence_level: L2
tver: 0.1.0
---

# Cortex Memory Benchmark Harness Report

This report records the local package-source implementation of the Cortex
Memory Benchmark Harness on 2026-05-26.

## Claim

The Cortex Memory Benchmark Harness is implemented at the local package-source
level:

- native result schema is present;
- neutral fixtures cover recall capabilities;
- `predict-only` preserves retrieved Cortex matches;
- `evaluate-only` judges retrieval sufficiency;
- rubric nuggets and event-order checks are deterministic;
- checkpoint and resume behavior are covered by self-test;
- compare-run output reports improvements and regressions;
- benchmark artifacts remain evidence and do not write durable Cortex memory.

## Material Surfaces

| Surface | Path |
|---------|------|
| Harness docs | `docs/evals/CORTEX-MEMORY-BENCHMARKS.md` |
| Fixture dataset | `benchmarks/cortex-memory/eval-dataset.json` |
| Result schema | `benchmarks/cortex-memory/result-schema.json` |
| Runner | `scripts/cortex_memory_benchmark.py` |
| Oracle | `scripts/cortex_memory_oracle.py` |
| Compare tool | `scripts/cortex_memory_compare.py` |
| Planning source | `docs/roadmap/GOAL-SUPER-SPEC-cortex-memory-benchmark-harness.md` |
| Execution units | `docs/roadmap/cortex-memory-benchmark-harness/EXECUTION-UNITS.md` |

## Release Identity

Package version: `0.3.135`.

Bundle: `docs/dist/0.3.135/tilly-engineer-skills-0.3.135.zip`.

Bundle SHA-256:
`4358d39fd6c5afdf9e92413f0d6f42359e88b0bca5ae14ac48d407136eaadad2`.

Remote release, tag, push, marketplace, and package publishing remain outside
this run.

## Closure Oracles

Focused gates:

```bash
python3 scripts/cortex_memory_benchmark.py --self-test
python3 scripts/cortex_memory_oracle.py --self-test
python3 scripts/cortex_memory_compare.py --self-test
python3 scripts/cortex_memory_benchmark.py plan
npm run cortex-memory:self-test
```

Governance and documentation gates:

```bash
python3 scripts/validate_tds.py
python3 scripts/validate_doc_size.py
python3 scripts/validate_reference_graph.py
python3 scripts/private_vocabulary_oracle.py
python3 scripts/command_trigger_oracle.py --self-test
python3 scripts/validate_reference_package.py
python3 scripts/tes_bump.py --governance-check --json
python3 scripts/build_public_docs.py --check
python3 scripts/public_bundle_oracle.py
git diff --check
```

Observed status: all listed commands passed during this run.

`npm run commit:check` is the required sealed-package gate before a commit or
sealed package claim. This report does not claim a remote release or pushed
fixed ref.

## Boundary

The harness is a benchmark and evidence layer. It does not:

- make benchmark output a memory source of truth;
- add write-capable MCP;
- write Cortex cells automatically;
- add an external memory backend;
- commit external benchmark datasets;
- certify commercial memory quality;
- authorize remote publishing.

## Residual Risk

- The first fixture set is intentionally small and neutral.
- Optional model-assisted judging is not implemented.
- UI/dashboard work is deferred until the CLI contract remains stable.
- Broader real-project canary replay is required before commercial-use claims.

## Decision

Status: `GO` for local Cortex Memory Benchmark Harness implementation.

Status: `DEFERRED` for remote release certification, commercial-use claim,
write-capable MCP, external datasets, and UI.
