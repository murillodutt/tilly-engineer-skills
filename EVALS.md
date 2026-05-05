# Eval And Ablation Method

This package includes a portable eval method, not a model-specific benchmark
runner. Projects should adapt it to their own agent, CLI, model, and gates.

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
  "forbidden": [
    "strategy pattern",
    "abstract factory"
  ]
}
```

Distractors use `kind: "distractor"` and should assert that the agent does not
over-activate heavyweight guidance.

## Decision Rules

| Result | Interpretation |
|--------|----------------|
| `full` passes, `drop` fails | Section pays rent |
| `full` and `drop` pass | Section is redundant or eval is weak |
| `full` fails | Section is unclear or insufficient |
| `none` passes | Model default or prompt leak may be enough |
| Distractor fails | Context is too heavy or judge is too sensitive |

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
