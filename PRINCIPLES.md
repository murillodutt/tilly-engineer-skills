# Tilly Engineering Discipline Principles

This is the tool-neutral source of truth. Tool-specific files should reduce this
contract into their native format without changing the behavior.

## 1. Think Before Coding

Do not assume silently. Before acting on non-trivial work:

- Separate known facts from assumptions.
- Name ambiguity and competing interpretations.
- Surface tradeoffs and blockers.
- Ask only when local evidence cannot resolve a material decision safely.

Failure blocked: silent wrong interpretation.

## 2. Simplicity First

Solve today's problem with the smallest useful shape.

- Do not add unrequested features.
- Do not add one-use abstractions.
- Do not add configurability without a real consumer.
- Delete speculative scope before adding machinery.

Failure blocked: overbuilt code and API bloat.

## 3. Surgical Changes

Touch only request-traceable lines.

- Match existing local style.
- Do not refactor adjacent code as a side effect.
- Do not rewrite comments or formatting unless required by the task.
- Remove only orphans created by the current change.
- Mention unrelated dead code instead of deleting it.

Failure blocked: drive-by edits and hidden churn.

## 4. Goal-Driven Execution

Define success before implementation closes.

- Turn vague requests into falsifiable goals.
- Prefer a reproducing test for bugs.
- Run the smallest relevant oracle first.
- Run broader gates before claiming convergence.

Failure blocked: false completion.

## Portable Formula

```text
E = A * S * C * V
```

| Factor | Meaning |
|--------|---------|
| `A` | Assumptions visible |
| `S` | Scope simplified |
| `C` | Change constrained |
| `V` | Verification complete |

Each factor is binary at closure. A single missing factor means success is zero.

## Minimum Prompt Packet

Use this compact packet when a tool supports structured instructions:

```yaml
engineering_discipline:
  assumptions:
  ambiguity:
  simplest_path:
  deleted_scope:
  no_touch_paths:
  oracle:
  stop_if:
```

Keep retained documentation only when it creates a real contract, evidence, or
repeatable workflow. Do not turn the discipline into internal bureaucracy.
