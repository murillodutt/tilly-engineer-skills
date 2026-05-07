# Using This Repo With Cursor

This target repository includes a Cursor project rule for Tilly Engineering
Discipline.

## In This Repository

Cursor loads `.cursor/rules/tes-guidelines.mdc`.

## Use In Another Project

Copy `.cursor/rules/tes-guidelines.mdc` into the target project's rule set.

If the target project already has rules, merge the four gates rather than
duplicating long prose:

- Think Before Coding
- Simplicity First
- Surgical Changes
- Goal-Driven Execution

## Behavioral Source Of Truth

Keep Cursor, Claude, and Codex variants synchronized at the behavioral level:
visible assumptions, smaller scope, surgical edits, and falsifiable closure.

## Codex And Claude

- Codex: use `AGENTS.md` plus `.agents/skills/tes-engineering-discipline/`.
- Claude Code: use `CLAUDE.md` or tool-native plugin metadata.

Do not copy `.cursor/**` into Codex or Claude runtime as authoritative context.
