---
tds_id: evals.cortex_memory_benchmarks
tds_class: eval
status: active
consumer: Cortex maintainers, benchmark authors, oracle authors, and release reviewers
source_of_truth: true
evidence_level: L1
tver: 0.1.1
---

# Cortex Memory Benchmarks

The Cortex memory benchmark harness tests recall behavior without changing the Cortex authority model from ADR 0001.

```text
Markdown is truth.
Recall artifacts are evidence.
Scores are judgments.
Checkpoints are resumability.
No benchmark output writes Cortex memory by itself.
```

## Purpose

The harness answers a narrow operational question:

```text
Did Cortex recall enough grounded evidence to answer safely?
```

It does not rank TES against external memory systems. It does not create a new memory backend. It does not promote run outputs, scores, indexes, checkpoints, or model answers into durable memory.

## Native Contract

The native benchmark result is stage-based:

| Stage | Contract |
|-------|----------|
| `fixture` | Stable question, capability, required refs, forbidden refs, and rubric nuggets. |
| `recall` | Query, backend, cutoff, latency, retrieved matches, rank, score, and refs. |
| `judgment` | Retrieval sufficiency, missing evidence, forbidden evidence, nugget scores, and status. |
| `checkpoint` | Optional resumability record outside durable Cortex memory. |
| `compare` | Run-to-run metric deltas and pass/fail flips. |

Retrieved matches are mandatory evidence. A benchmark item cannot pass if the retrieval artifact is missing, even when the final answer looks plausible.

## Capabilities

The first fixture matrix covers:

| Capability | What It Proves |
|------------|----------------|
| `information_extraction` | Exact grounded facts are retrievable from Cortex. |
| `temporal_reasoning` | Current decisions outrank stale historical material. |
| `event_ordering` | Chronological evidence can be reconstructed in order. |
| `knowledge_update` | Updated governed decisions are recoverable. |
| `contradiction_resolution` | Conflicts remain visible until resolved by evidence. |
| `multi_session_reasoning` | Related refs can be combined across sources and cells. |
| `preference_following` | Durable preferences are used only when source-grounded. |
| `instruction_following` | Mutability and read-only boundaries are respected. |
| `summarization` | Synthesis keeps source lineage. |
| `abstention` | Missing evidence produces insufficient-evidence status. |

## Cutoffs

Cutoffs measure how deep a reviewer or agent must search before the necessary evidence appears. The default fixture matrix uses `top_1`, `top_3`, and `top_5`. Later runs may add deeper cutoffs, but every run must record the exact cutoff list in metadata.

## Status Vocabulary

| Status | Meaning |
|--------|---------|
| `PASS` | Required evidence is present and no hard boundary failed. |
| `FAIL` | Required evidence is missing or forbidden evidence appears. |
| `BLOCKED` | Required target, fixture, backend, or schema is unavailable. |
| `DEGRADED` | A fallback backend ran instead of the intended path. |
| `NEEDS_REVIEW` | The oracle cannot decide safely from retained evidence. |
| `NOT_AVAILABLE` | The capability is outside the current run scope. |

## Commands

```bash
python3 scripts/cortex_memory_benchmark.py plan
python3 scripts/cortex_memory_benchmark.py predict-only --target /path/to/project --out recall.json
python3 scripts/cortex_memory_benchmark.py evaluate-only --predictions recall.json --out evaluation.json
python3 scripts/cortex_memory_benchmark.py run --target /path/to/project --out-dir .tes/runs/cortex-memory
python3 scripts/cortex_memory_oracle.py validate-dataset
python3 scripts/cortex_memory_compare.py --baseline baseline.json --candidate candidate.json --out compare.json
python3 scripts/cortex_memory_benchmark.py --self-test
```

`predict-only` and `evaluate-only` are intentionally separate so a recall artifact can be retained, reviewed, replayed, and judged without rerunning retrieval.

## Evidence Rules

- Keep benchmark evidence generic and neutral.
- Do not commit external datasets or large result files.
- Do not store private project names, private paths, storage backends, product names, secrets, or canary identifiers.
- When fixtures model Cortex cells, their evidence refs must use `sources/**`, `docs/agents/cortex/sources/**`, `docs/agents/evidence/**`, or `Assumption:`. Absolute local paths, derived indexes, checkpoints, run scratch, and benchmark outputs are not durable Cortex evidence.
- Treat generated run directories as evidence only after a report is explicitly retained and indexed.
- Use `docs/evidence/**` for retained proof and `.tes/runs/**` for local scratch runs.

## Closure

Harness closure requires the focused self-tests plus the normal documentation and privacy gates:

```bash
python3 scripts/cortex_memory_benchmark.py --self-test
python3 scripts/cortex_memory_oracle.py --self-test
python3 scripts/cortex_memory_compare.py --self-test
python3 scripts/validate_tds.py
python3 scripts/validate_doc_size.py
python3 scripts/validate_reference_graph.py
python3 scripts/private_vocabulary_oracle.py
git diff --check
```

Run `npm run commit:check` before any sealed package claim.
