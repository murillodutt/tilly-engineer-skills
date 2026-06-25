---
name: tes-bench
description: Use when the user says /tes-bench, /tes:bench, or asks to plan, run, converge, inspect, or certify TES context-mesh benchmarks and behavior evidence.
license: MIT
---

# TES Bench

`/tes-bench` is the preferred shared TES trigger for benchmark planning, fixture runs, convergence review, and behavior-evidence discussion. `/tes:bench` is a compatible TES intent alias if the host reports it as an invalid slash.

## Context Gate

TES benchmark commands are package-source evidence by default. Before running them, confirm the current workspace exposes `benchmark:plan`, `benchmark:run`, and `benchmark:converge` in `package.json`, or that the TES source package is available.

In an installed target without those scripts, report `NEEDS_SOURCE` or `NOT_AVAILABLE` and route local health checks to `/tes-doctor`. Do not invent benchmark scripts in the target project.

## Evidence Retention

Package benchmark evidence follows the temporal retention contract:

```text
docs/evidence/current/                  current claims and risks
docs/evidence/reports/YYYY/MM/DD/context-mesh/<run-id>/  generated runs
docs/evidence/archive/                  cold audit indexes
```

Historical `docs/evidence/reports/context-mesh/<run-id>/` evidence remains readable retained proof. It is not a current operational claim unless linked from `docs/evidence/current/**` or another active claim document.

## Workflow

1. Start with `npm run benchmark:plan` only after the context gate passes.
2. Prefer the fixture backend for safe local checks: `npm run benchmark:run -- --backend fixture`.
3. Expect new default runs under the temporal `reports/YYYY/MM/DD` path. Use an explicit `--out-root` only for temporary output or intentional legacy writes.
4. Use `npm run benchmark:converge` only after run artifacts exist, passing the exact `summary.json` path when reviewing a specific run.
5. Treat generated reports and raw traces as `source_of_truth: false`; use `docs/evidence/current/**` for current claim interpretation.
6. Preserve raw evidence and manifests when a claim depends on them.
7. State whether the result is planning evidence, fixture evidence, behavior evidence, or certification evidence.

## Locks

- Do not claim behavior parity from fixture-only evidence.
- Do not overwrite benchmark artifacts without explicit reason.
- Do not run network or model-cost backends unless the user authorizes them.
- Do not certify installed-target health with package-source benchmark commands.
