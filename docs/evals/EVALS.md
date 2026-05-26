---
tds_id: evals.design
tds_class: eval
status: active
consumer: benchmark authors
source_of_truth: true
evidence_level: L1
tver: 0.2.2
---

# Eval And Ablation Method

This package includes a portable eval method, not a model-specific benchmark
runner. Projects should adapt it to their own agent, CLI, model, and gates.

Evals are not passive measurement only. In this project, evals are the
discovery engine for context repair: they expose where a rule pays rent, where
it is redundant, where the grader is brittle, and where the dataset fails to
isolate behavior.

The governing principle is evidence-converged context: a rule becomes project
truth only after it produces retained lift, survives distractors, shows
ablation loss, and converges through Build-Test-Fail-Fix. The operational loop
is defined in `docs/mesh/CONTEXT-MESH-CONVERGENCE.md`.

## Conditions

Run at least these conditions:

| Condition | Meaning |
|-----------|---------|
| `full` | Agent context with the full current instruction set |
| `none` | Baseline with project context removed |
| `drop:<section>` | Full context with one section removed |

The result is behavioral rent: how much a section changes decisions.

## Dataset Shape

Each eval should declare:

```json
{
  "id": "E1-simplicity-over-abstraction",
  "kind": "trigger",
  "target_section": "Simplicity First",
  "prompt": "Add a simple discount helper. Make it flexible for future discount types.",
  "expected": [
    "avoid one-use abstraction",
    "implement smallest useful function"
  ],
  "expected_any": [
    ["smallest", "minimal", "simples"],
    ["future", "speculative", "especulativo"]
  ],
  "forbidden": [
    "strategy pattern",
    "abstract factory"
  ]
}
```

Distractors use `kind: "distractor"` and should assert that the agent does not
over-activate heavyweight guidance.

`expected` is an exact all-of assertion. `expected_any` is a deterministic
semantic-signal assertion: every group must have at least one matching string.
Use `expected_any` when multiple languages or equivalent phrasings are valid,
but keep groups small enough that a reviewer can audit why a sample passed.

## Decision Rules

| Result | Interpretation |
|--------|----------------|
| `full` passes, `drop` fails | Section pays rent |
| `full` and `drop` pass | Section is redundant or eval is weak |
| `full` fails | Section is unclear or insufficient |
| `none` passes | Model default or prompt leak may be enough |
| Distractor fails | The literal distractor assertion failed |
| Distractor leaks | Heavy context changed a task that should have stayed light |

Keep `distractor_fail_rate` separate from `distractor_leak_rate`.
`distractor_fail_rate` measures expected/forbidden literal assertion failures.
`distractor_leak_rate` measures confirmed heavy-context leakage signals, such
as mentioning gates, context mesh, benchmark/eval machinery, governance
ceremony, unrelated agent rules, or over-planning a trivial typo/read-only task.

## Certification v1-rc

Treat the first certified benchmark line as a v1 release candidate, even while
the package version remains `0.1.0`. The certification question is not whether
the runner works. The question is whether the evidence proves that context
changes the right behavior without leaking into wrong tasks, hiding cost, or
drifting across adapters.

Use two certification classes:

| Class | Meaning |
|-------|---------|
| `pipeline-v1-rc` | Planner, runner, raw evidence, reports, thresholds, TDS indexing, and NO-GO mechanics work |
| `behavior-v1-rc` | A real backend shows the context mesh changes behavior correctly without distractor leaks |

Fixture and echo backends may only produce `pipeline-v1-rc` evidence. They must
not be described as live-model behavioral certification.

Minimum v1-rc thresholds:

| Metric | Threshold |
|--------|-----------|
| `plan_run_parity` | `1.0` |
| `raw_evidence_coverage` | `1.0` |
| `trigger_pass_rate_full` | Greater than `trigger_pass_rate_none` |
| `distractor_leak_rate` | `0` |
| `all_failures_have_excerpt` | `true` |
| `dataset_sha_present` | `true` |
| `git_head_present` | `true` |
| `backend_declared` | `true` |
| `grader_version_declared` | `true` |
| `grader_sha_present` | `true` |

Ablation loss rules:

| Loss | Decision |
|------|----------|
| `0` | Prune or move candidate unless explicitly justified |
| `1` | Add adversarial follow-up before making strong rent claims |
| `>= 2` | Keep |

NO-GO conditions:

- `run` diverges from `plan`.
- Any sample lacks raw output, prompt hash, output hash, or grader hash.
- Any failed sample lacks an audit excerpt.
- Dataset changes without a new dataset hash in the report.
- `full <= none` without a retained explanation.
- Any confirmed distractor leak.
- Grader changes after the run without a new grader hash and version.
- Report declares `GO` without evidence limits.

`context_roi` is valid only when context token cost and behavioral lift come
from the same run and dataset hash. Until token counts are captured, report
lift but do not claim ROI.

`E = A * S * C * V` may be reported only after A, S, C, and V are each defined
as observable fields or reviewer-coded review labels. Otherwise it remains method
language, not a measured outcome.

Adapter parity means behaviorally equivalent decisions under the same eval
matrix. It does not require identical prose across Codex, Claude, and Cursor.

## Minimum Benchmark Loop

```text
1. Create trigger evals for each active rule.
2. Create distractors for trivial tasks.
3. Run full, none, and drop:<section>.
4. Inspect failures.
5. Add adversarial evals where evidence is weak.
6. Adjust only the section proven ambiguous.
7. Rerun final matrix.
8. Record evidence limits.
```

## External Pattern Anchors

The benchmark runner stays local source of truth. Mature eval projects are
pattern anchors, not package dependencies or authority over this repository.

| Project | Pattern To Reuse | Boundary |
|---------|------------------|----------|
| [Promptfoo][promptfoo-assertions] | Declarative assertions and deterministic output checks | Do not make Promptfoo the primary source of truth |
| [OpenAI Evals][openai-evals] | Dataset, eval logic, aggregation, and private workflow evals | Do not start with a full registry model |
| [Inspect AI][inspect-ai] | Tasks, datasets, solvers, scorers, providers, and logs | Do not require sandbox or agent infrastructure in v0.1 |
| [DeepEval][deepeval] | Test cases, datasets, metrics, traces, and component versus end-to-end evals | Do not begin with many LLM-judge metrics |
| [LangSmith Evals][langsmith-evals] | Dataset, experiment, evaluator scores, traces, and comparison model | Do not depend on SaaS for retained evidence |
| [lm-evaluation-harness][lm-eval] | Strong separation between benchmark, backend, and reproducible results | Do not treat context-mesh behavior as a generic model leaderboard |

The local synthesis is:

```text
Dataset   -> OpenAI Evals, LangSmith, DeepEval
Matrix    -> Promptfoo-style conditions
Backend   -> lm-eval and Inspect-style provider adapter
Execution -> Inspect-style task runner
Scoring   -> Promptfoo-style deterministic assertions
Evidence  -> LangSmith and Inspect-style raw trace plus summary
Report    -> local TDS evidence
```

External frameworks may become exporters or adapters after local evidence is
stable. They must not replace the versioned dataset, runner, raw traces,
summary, or TDS report as the canonical package record.

## Runner v0.1

`scripts/context_mesh_run.py` is the first evidence runner. It is intentionally
small: it reuses the same dataset planning logic as
`scripts/context_mesh_plan.py`, supports non-paid `fixture` and `echo`
backends plus isolated `claude-cli` and `codex-cli` backends, applies
deterministic substring grading, and writes one auditable run directory.

Dataset `0.1.10` adds an adversarial Goal-Driven prompt so weak per-gate
behavior can be followed up without changing historical retained reports.

Default evidence shape:

```text
docs/evidence/reports/YYYY/MM/DD/context-mesh/<run-id>/
  manifest.json
  raw.ndjson
  summary.json
  REPORT.md
  graders-sha.json
```

The legacy shape `docs/evidence/reports/context-mesh/<run-id>/` remains
readable retained proof and may still be used with an explicit `--out-root`.
New default runs use the temporal path so old reports do not compete with the
current evidence claim panel.

## Cortex Memory Harness

`docs/evals/CORTEX-MEMORY-BENCHMARKS.md` defines the native Cortex memory
benchmark harness. It reuses the local evidence-first eval principle, but its
unit of judgment is memory recall sufficiency instead of agent response text.

The harness keeps `predict-only` recall artifacts separate from
`evaluate-only` sufficiency judgment so retrieval evidence can be retained,
replayed, and compared without rerunning Cortex recall.

The raw file is append-only NDJSON with one line per sample. Each line keeps
the dataset hash, Git HEAD, backend, model, condition, eval id, sample id,
prompt hash, output hash, grader version, grader hash, pass/fail result,
grading signals, prompt, output, and excerpt.

When the report is written under `docs/**`, the runner appends the generated
`REPORT.md` to `docs/tds/DOCS-INDEX.yml`. Use `--no-tds-index` for temporary
or external output roots that should not mutate the governed docs index.

Use the runner for traceability first:

```bash
python3 scripts/context_mesh_run.py --dry-run
python3 scripts/context_mesh_run.py --backend fixture
```

Use the live Claude backend only after `pipeline-v1-rc` evidence is retained:

```bash
python3 scripts/context_mesh_run.py --backend claude-cli --model sonnet --max-budget-usd 0.25
```

The `claude-cli` backend runs through the same backend adapter boundary as
fixture and echo. It must not write reports, grade outputs, mutate TDS, or
decide certification outside the shared runner path.

The backend prompt must not reveal matrix labels such as `full`, `none`, or
`drop:<section>`. Those labels belong in evidence only. Revealing them to the
model contaminates ablation because the model can reason about the experiment
instead of only the active context.

The first `claude-cli` backend intentionally does not use `--bare`. Reports
must declare that default Claude Code context may influence outputs beyond the
runner prompt.

### Sharded Execution

Long live-backend runs may be split with `--shard-count` and `--shard-index`.
Shard runs are raw execution evidence only:

```bash
python3 scripts/context_mesh_run.py --backend claude-cli --run-id behavior-shard-00 --shard-count 4 --shard-index 0 --out-root /tmp/context-mesh-shards
python3 scripts/context_mesh_run.py --merge-shards /tmp/context-mesh-shards --run-id behavior-v1-rc-merged
```

Shard runs write `manifest.json`, `raw.ndjson`, and `graders-sha.json`, but no
`REPORT.md`, no `summary.json`, and no TDS index update. Only the merged run may
write the governed evidence package and declare `GO` or `NO-GO`.

The merge must reject missing samples, duplicate sample ids, prompt hash drift,
output hash drift, dataset hash drift, grader drift, backend/model drift, and
mixed certification classes.

Do not add paid or external backends to `commit:check`. The commit gate should
continue to run `benchmark:plan`, while measured runs remain explicit evidence
operations.

### Convergence Gate

After retained behavior evidence exists, run the local convergence gate:

```bash
npm run benchmark:converge -- --summary docs/evidence/reports/context-mesh/<run-id>/summary.json
```

For new temporal reports, pass the temporal summary path:

```bash
npm run benchmark:converge -- --summary docs/evidence/reports/YYYY/MM/DD/context-mesh/<run-id>/summary.json
```

The loop is:

```text
analysis -> fix -> test -> repeat until convergence gate passes
```

Convergence requires behavior `GO`, complete raw evidence, zero backend
errors, zero distractor leak, positive `full` over `none` lift, and ablation
loss at or above the configured floor for every gate. The default floor is
`loss >= 1`, meaning each gate has at least one retained sample where `full`
passes and `drop:<gate>` fails. Use `--min-loss 2` only after the dataset has
multiple trigger samples per gate.

## Promptfoo

Promptfoo can be a useful adapter for visualization, repeat runs, and custom
assertions. It should not replace the local contract.

Keep project-specific semantics in local code or fixtures. Export Promptfoo
configs from the local source when possible.

## Audit Requirements

Every failed judge should preserve:

- Output excerpt
- Rule or regex that failed
- Cost when available
- Model and mode
- Dataset/source version

An unauditable judge finding is only a suspicion.

[promptfoo-assertions]: https://www.promptfoo.dev/docs/configuration/expected-outputs/
[openai-evals]: https://github.com/openai/evals
[inspect-ai]: https://inspect.aisi.org.uk/
[deepeval]: https://deepeval.com/docs/introduction
[langsmith-evals]: https://docs.langchain.com/langsmith/evaluation-concepts
[lm-eval]: https://github.com/EleutherAI/lm-evaluation-harness
