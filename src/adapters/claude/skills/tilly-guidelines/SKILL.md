---
name: tilly-guidelines
description: Behavioral engineering discipline to reduce ambiguity, overcomplication, drive-by edits, and false completion. Use when writing, reviewing, refactoring, or migrating code/instructions and the work is non-trivial.
license: MIT
---

# Tilly Guidelines

Core contract:

```text
Assumptions visible. Scope smaller. Edits surgical. Success falsifiable.
```

Tradeoff: this skill biases toward caution over speed. Use judgment for trivial
one-liners.

## Four Gates

| Gate | Rule | Failure Blocked |
|------|------|-----------------|
| Think Before Coding | State assumptions, ambiguity, tradeoffs, and blockers before acting | Silent wrong interpretation |
| Simplicity First | Solve only the requested problem with the smallest useful shape | Overbuilt code and API bloat |
| Surgical Changes | Touch only request-traceable lines and self-created orphans | Drive-by refactors and hidden churn |
| Goal-Driven Execution | Define a falsifiable oracle and verify before closure | False completion |

## Workflow

1. Classify the task.
   - For trivial typo-level work, proceed with judgment.
   - For coding, review, refactor, or instruction migration, use the four gates.
2. Make assumptions visible.
   - Separate facts from guesses.
   - Ask only when the answer changes material scope, authorization, or risk.
3. Delete scope.
   - Remove speculative features and one-use abstractions before implementation.
4. Keep the diff surgical.
   - Match existing style.
   - Do not clean unrelated code.
   - Remove only orphans created by this change.
5. Verify.
   - Run the smallest relevant check first.
   - Run broader gates when the blast radius requires them.

## Success Formula

```text
E = A * S * C * V
```

Each factor is binary at closure:

- `A`: assumptions visible
- `S`: scope simplified
- `C`: changes constrained
- `V`: verification complete

If any factor is zero, stop or repair before claiming success.

## Done

The skill worked when the diff is smaller than the first impulse, every changed
line traces to the request, and success is backed by a concrete oracle.
