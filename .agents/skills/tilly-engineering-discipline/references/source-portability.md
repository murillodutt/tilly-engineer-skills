# Source Portability

Use this reference when adapting the discipline to another agent tool.

## Canonical Source

`PRINCIPLES.md` is the tool-neutral source. Tool-specific files are reductions,
not independent truth.

## Codex

Use:

- `AGENTS.md` for small durable repository guidance.
- `.agents/skills/tilly-engineering-discipline/SKILL.md` for the reusable
  workflow.
- `references/**` for progressive disclosure.
- `scripts/**` for deterministic validation.

Do not treat `.cursor/**` or `.claude-plugin/**` as Codex runtime truth.

## Cursor

Use `.cursor/rules/tilly-guidelines.mdc` with `alwaysApply: true` when the four
gates should be available for every non-trivial coding task.

Keep the Cursor rule short. Put long examples in `EXAMPLES.md`.

## Claude Code

Use `CLAUDE.md` as root project guidance or distribute the legacy skill through
`.claude-plugin/**`.

Keep `CLAUDE.md`, Cursor rules, and Codex skill behavior synchronized with
`PRINCIPLES.md`.

## Generic LLM Agents

If the target tool supports only one instruction file, copy the Core Contract,
Four Gates, Success Formula, and Minimum Prompt Packet from `PRINCIPLES.md`.

If the target tool supports reusable skills, keep the root instruction small and
move detailed workflow into the skill.

## Migration Rule

Do not copy packaging. Copy behavior.

Reduce each external tool's format into:

1. Persistent bootloader.
2. Reusable skill or workflow.
3. Optional references.
4. Optional deterministic scripts.
5. Concrete validation command.
