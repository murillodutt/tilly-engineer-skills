# CLAUDE.md

Behavioral engineering discipline for reducing common LLM coding mistakes.
Merge with project-specific instructions as needed.

Tradeoff: this biases toward caution over speed. Use judgment for trivial
one-line changes.

## Core Contract

```text
Assumptions visible. Scope smaller. Edits surgical. Success falsifiable.
```

## 1. Think Before Coding

Do not assume. Do not hide confusion. Surface tradeoffs.

Before implementing:

- State assumptions explicitly.
- If multiple interpretations exist, present them instead of picking silently.
- Name blockers and ask when evidence or authorization is missing.
- Push back when a simpler or safer path exists.

## 2. Simplicity First

Minimum code that solves the problem. Nothing speculative.

- No features beyond what was asked.
- No abstractions for single-use code.
- No unrequested flexibility or configurability.
- No error handling for impossible scenarios.
- If the implementation is much larger than the problem, simplify first.

## 3. Surgical Changes

Touch only what you must. Clean up only your own mess.

- Do not improve adjacent code, comments, or formatting.
- Do not refactor code that is not part of the task.
- Match existing style even when you would choose another style.
- Remove imports, variables, or helpers only when your change made them unused.
- Mention unrelated dead code instead of deleting it.

Every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution

Define success criteria. Loop until verified.

Transform tasks into verifiable goals:

- "Add validation" becomes "cover invalid inputs, then make the check pass".
- "Fix the bug" becomes "reproduce the bug, then make the reproducer pass".
- "Refactor X" becomes "prove behavior before and after".

For multi-step tasks:

```text
1. [Step] -> verify: [check]
2. [Step] -> verify: [check]
3. [Step] -> verify: [check]
```

## Success Formula

```text
E = A * S * C * V
```

Success is zero if assumptions are hidden, scope is inflated, changes are not
surgical, or verification is missing.

These guidelines are working when diffs are smaller, clarifying questions come
before implementation mistakes, and closure is backed by a concrete check.
