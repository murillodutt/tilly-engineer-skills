---
tds_id: roadmap.tes_skill_benchmark_convergence
tds_class: roadmap
status: proposed
consumer: maintainers and benchmark operators
source_of_truth: false
evidence_level: L2
tver: 0.1.0
---

# TES Skill Benchmark Convergence Roadmap

## Goal

Establish benchmark coverage for TES skills that can regress by agent behavior,
then run progressive goal loops until each covered skill has live evidence,
focused failure classification, and a clear stop point.

This roadmap does not authorize commits, release identity changes, bundle
updates, publishing, or broad documentation work. It is an execution control
surface for benchmark convergence.

## Baseline

| Surface | Current evidence | Decision |
|---------|------------------|----------|
| Engineering discipline / guidelines | `benchmarks/context-mesh/eval-dataset.json`; L1-L4 runtime-skill GO for Maturity Layer Gate | Keep as the reference progressive benchmark. |
| Cortex memory behavior | `benchmarks/cortex-memory/eval-dataset.json` and schema | Treat as existing benchmark family; add route-level coverage only when a real drift appears. |
| Progress logging | `scripts/context_mesh_run.py` progress events and latest run status | Required for every live benchmark loop. |
| Operational package checks | validator, TDS, doc-size, package, and private vocabulary oracles | Prefer deterministic gates over LLM benchmarks for operational skills. |

## Benchmark Policy

Benchmarks are instruments of truth, not scoreboards. A useful benchmark must
separate false green from real behavior, preserve distractors, emit runtime
evidence, and make the next repair cause obvious.

Use LLM/runtime benchmarks only for skills whose value depends on judgment,
routing, restraint, or agent behavior. Use deterministic oracles for skills
whose contract is file layout, install behavior, command output, package
correlation, or adapter materialization.

## Coverage Matrix

| Skill family | Required coverage | Current status | Next action |
|--------------|-------------------|----------------|-------------|
| `tes-engineering-discipline` / `tes-guidelines` | Context mesh gates, maturity layer, distractors, progressive L1-L4 | Covered and recently converged | Retain as canary gate before related behavior claims. |
| `tes-goal-maestro` | Behavioral benchmark for execution-unit fidelity, stop states, no commit, no scope drift, and goal prompt quality | Missing | Create focused dataset and progressive loop first. |
| `tes-prospect` | Behavioral benchmark for one-question pressure, hidden dependency discovery, cognitive brake, and no premature redesign | Missing | Create focused dataset after Goal Maestro fixtures exist. |
| `tes-mine` | Behavioral benchmark for durable vocabulary extraction, no private leakage, no overcapture, and useful synthesis | Missing | Create focused dataset after Prospect fixtures exist. |
| `tes-align` | Canary benchmark for roadmap/mesh alignment, semantic residue handling, and anti-scaffold behavior | Partial docs and skill source exist; benchmark missing | Define a compact real-project-safe canary with neutral placeholders. |
| `tes-bench` | Meta-benchmark for benchmark routing, level selection, progress evidence, and convergence stop language | Missing | Add after at least two skill benchmark families exist. |
| `tes-cortex` | Memory benchmark plus command-route certification | Partly covered by Cortex memory benchmark | Do not broaden unless route drift appears. |
| `tes-init`, `tes-setup`, `tes-update` | Installer and lifecycle deterministic gates | Package validators and install docs exist | Add oracles only when a specific install path changes. |
| `tes-map`, `tes-mcp`, `tes-field-reports`, `tes-doctor`, `tes-adapter`, `tes-bump`, `tes-open-obsidian` | CLI, file, adapter, and correlation deterministic gates | Mixed validator coverage | Inventory existing oracles before adding any LLM fixtures. |

## Execution Waves

### Wave 0: Inventory Gate

Acceptance:

- list every source skill by adapter and route;
- classify each as behavioral benchmark, deterministic oracle, existing
  benchmark, or no new coverage needed;
- preserve adapter parity and keep private project vocabulary out of fixtures.

### Wave 1: Behavioral Core

Acceptance:

- create progressive datasets for `tes-goal-maestro`, `tes-prospect`, and
  `tes-mine`;
- each dataset includes positive cases, negative cases, distractors, and at
  least one regression sample for scope drift;
- live runs write structured progress logs.

### Wave 2: Alignment Canary

Acceptance:

- create one compact neutral canary for `tes-align`;
- verify semantic residue behavior without naming private projects;
- fail scaffold-only or roadmap-only outputs that do not improve execution.

### Wave 3: Benchmark Meta-Gate

Acceptance:

- benchmark `tes-bench` against routing, level selection, evidence reading,
  failure classification, and convergence stop discipline;
- prevent score-chasing language from replacing behavioral evidence.

### Wave 4: Retention And Closure

Acceptance:

- every covered family has a latest run pointer, progress logs, and a
  classification note;
- deterministic-only skills have named oracles or an explicit no-new-coverage
  decision;
- `git diff --check`, focused validators, and `npm run commit:check` pass only
  at final closure;
- no stage, commit, push, tag, publish, bundle, or release action occurs before
  owner authorization.

## Goal Loop Template

Each skill benchmark loop follows the same progression:

1. L0 fixture validation: dataset and schema are coherent.
2. L1 smoke: one representative sample proves the harness path.
3. L2 contrast: positives, negatives, and distractors separate behavior.
4. L3 family: all samples for one skill family run with progress logs.
5. L4 retained evidence: full relevant benchmark set runs without distractor
   leak or backend defects.

Each repair cycle must name the current level, run id, failure classification,
single fix target, and next oracle. Stop after convergence; do not polish.

## Stop Conditions

Stop with `CONVERGED_NO_COMMIT` when all required levels for the current skill
family are GO, focused validators pass, progress logs exist, and no forbidden
git or release action occurred.

Stop with `NEEDS_REORIENTATION` when the next action is not tied to a failed
sample, the fix target is unclear, or the loop starts broadening TES instead of
converging the benchmark.

Stop with `NEEDS_OWNER_DECISION` when convergence requires release identity,
benchmark contract changes, or accepting residual risk.

Stop with `BLOCKED_BACKEND` when live runtime evidence cannot be obtained.

## First Cut

Start with `tes-goal-maestro`. It is the highest-leverage behavioral skill
because it creates the loop prompts that later benchmark runs will execute.
If Goal Maestro drifts, every downstream convergence loop inherits that drift.
