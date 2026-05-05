---
name: tilly-engineering-discipline
description: Apply a four-gate engineering discipline to non-trivial coding, review, refactor, or instruction-migration work so assumptions are explicit, scope stays small, diffs remain surgical, and success is verified by a concrete oracle.
---

# Tilly Engineering Discipline

Operational contract:

```text
Assumptions visible. Scope smaller. Edits surgical. Success falsifiable.
```

Use this skill for non-trivial coding, review, refactor, debugging, migration,
or agent-instruction work. Skip the full ceremony for obvious one-line fixes,
but keep the spirit.

## Four Gates

| Gate | Rule | Failure Blocked |
|------|------|-----------------|
| Think Before Coding | Name facts, assumptions, ambiguity, tradeoffs, and blockers before acting | Silent wrong interpretation |
| Simplicity First | Delete speculative scope before adding machinery | Overbuilt code and API bloat |
| Surgical Changes | Touch only request-traceable lines and self-created orphans | Drive-by edits and style churn |
| Goal-Driven Execution | Define and run a falsifiable oracle before closure | False completion |

## Discipline Packet

Use this compact packet when the task is material:

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

Keep it in conversation or working notes unless the target project requires a
retained artifact.

## Workflow

1. Classify the task.
   - If authority, irreversible risk, external surface, or secret handling is
     unclear, stop and ask.
   - If the task is clear and bounded, continue.
2. Make assumptions visible.
   - Resolve safe ambiguity locally.
   - Ask only when the answer changes scope, authorization, or risk.
3. Delete scope.
   - Remove unrequested features, future-proofing, one-use abstractions, and
     optional configuration.
4. Keep edits surgical.
   - Match local style.
   - Avoid unrelated formatting, comments, or refactors.
   - Remove only orphans created by this change.
5. Verify.
   - For bugs, reproduce the failure first when practical.
   - Run the smallest relevant oracle first.
   - Run broader project gates before claiming convergence.

## Module Map

| Need | Load |
|------|------|
| Common failure patterns | `references/failure-patterns.md` |
| Port this discipline across tools | `references/source-portability.md` |
| Deterministic self-test or plan check | `scripts/discipline_oracle.py` |

Do not bulk-load references unless the task needs them.

## Success Formula

```text
E = A * S * C * V
```

Each factor is binary at closure:

- `A`: assumptions visible
- `S`: scope simplified
- `C`: change constrained
- `V`: verification complete

If any factor is missing, success is zero and the work must stop or be repaired.

## Validation

Run the bundled self-test when changing this skill:

```bash
python3 .agents/skills/tilly-engineering-discipline/scripts/discipline_oracle.py --self-test
```

In a target repository, also run the smallest real project oracle: unit test,
typecheck, lint, build, contract test, or governance gate.

## Done

The skill is applied when assumptions are visible, implementation is smaller
than the first impulse, every changed line traces to the request, and closure is
backed by evidence.
