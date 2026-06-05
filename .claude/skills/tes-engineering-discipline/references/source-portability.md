# Source Portability

Use this reference when adapting the discipline to another agent tool.

## Canonical Behavior

Tool-specific files are reductions, not independent truth. Copy the behavior:
visible assumptions, smaller scope, surgical edits, and falsifiable closure.

## Codex

Use:

- `AGENTS.md` for small durable repository guidance.
- `.agents/skills/tes-engineering-discipline/SKILL.md` for the reusable
  workflow.
- `references/**` for progressive disclosure.
- `scripts/**` for deterministic validation.

Do not treat Cursor or Claude packaging as Codex runtime truth.

## Cursor

Use `.cursor/rules/tes-guidelines.mdc` with `alwaysApply: true` when the four
gates should be available for every non-trivial coding task.

Keep the Cursor rule short. Put long examples outside the always-loaded rule.

## Claude Code

Use `CLAUDE.md` as root project guidance or distribute a tool-native skill
package when the target Claude environment supports it.

Keep Claude instructions, Cursor rules, and Codex skill behavior synchronized at
the behavioral level, even when the packaging differs.

## Generic LLM Agents

If the target tool supports only one instruction file, copy the Core Contract,
Four Gates, Success Formula, and Minimum Prompt Packet.

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
