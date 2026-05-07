---
name: tes-bench
description: Use when the user says /tes:bench or asks to plan, run, converge, inspect, or certify TES context-mesh benchmarks and behavior evidence.
license: MIT
---

# TES Bench

`/tes:bench` is the shortcut for benchmark planning, fixture runs, convergence
review, and behavior-evidence discussion.

## Workflow

1. Start with `npm run benchmark:plan`.
2. Prefer the fixture backend for safe local checks:
   `npm run benchmark:run -- --backend fixture`.
3. Use `npm run benchmark:converge` only after run artifacts exist.
4. Preserve raw evidence and manifests when a claim depends on them.
5. State whether the result is planning evidence, fixture evidence, behavior
   evidence, or certification evidence.

## Locks

- Do not claim behavior parity from fixture-only evidence.
- Do not overwrite benchmark artifacts without explicit reason.
- Do not run network or model-cost backends unless the user authorizes them.
