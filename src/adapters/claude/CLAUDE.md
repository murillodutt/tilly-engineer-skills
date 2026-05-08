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

## Diamond Build-Test-Fail-Fix

For critical capabilities, build from the finished contract down: final
behavior, adversarial fixture, observed failure, smallest repair, and green
gate. Do not call certified behavior experimental; use `blocked`, `degraded`,
`not available`, `certified`, or `fail`.

## Feedback Voice

Default to short, frank prose. Avoid tables, code blocks, YAML/property dumps,
and long inventories unless the user asks for them or the artifact itself
requires exact syntax.

## TES Shortcuts

Treat `/tes:init`, `/tes:update`, `tes init`, and natural command/prompts
such as `TES, initialize this project`, `TES, inicialize este projeto`, or
`Atualizar TES` as installer intents. `/tes:update` first checks installed
version, cloud version, helper contract parity, applied IDE surfaces,
recommended route, and `recommended_update_scope`. Read-only update probes use
`--json-only`; the final certification probe may add `--record-field-report`.
`recommended_update_scope=helpers-only` or `STALE_HELPERS` is repaired first
through the helper-only Layer Zero route before MCP config activation. Also
treat `/tes:cortex`,
`/tes:curate`, `/tes:mcp`, `/tes:field-reports`, `/tes:doctor`,
`/tes:adapter`, and `/tes:bench` as intent shortcuts. Use the matching skill
and let the agent choose the smallest safe oracle. These are not shell commands.

## Cortex Reflection

If `docs/agents/cortex/CONTRACT.md` exists, Cortex is the durable memory
surface. Before the final response for material work, use read-only
`cortex_reflect` when available, or run:

```bash
python3 .tes/bin/cortex.py reflect --target . "<decision or lesson>"
```

Mention useful proposals. Do not write Cortex cells without explicit user
authorization.
If `curation_due=true`, run read-only `cortex_curate_plan` when available, or:

```bash
python3 .tes/bin/cortex.py curate-plan --target . --backend lexical
```

## Field Reports

TES Field Reports is active by default. It records only sanitized operational
facts and drains them through the local pre-push hook. When the user asks to
disable, enable, check, or drain Field Reports, run the matching
`field_reports.py` oracle and never expand collection levels or schema.
