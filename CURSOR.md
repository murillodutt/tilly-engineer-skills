# Using This Repo With Cursor

This project includes a Cursor project rule so the Tilly Engineering Discipline
applies automatically when you work here.

## In This Repository

1. Open the folder in Cursor.
2. Cursor loads `.cursor/rules/tilly-guidelines.mdc`.
3. The rule has `alwaysApply: true`, because the four gates are a behavioral
   overlay for non-trivial engineering work.

## Use In Another Project

Copy `.cursor/rules/tilly-guidelines.mdc` into the target project's
`.cursor/rules/` directory.

If the target project already has rules, merge the four gates rather than
duplicating long prose:

- Think Before Coding
- Simplicity First
- Surgical Changes
- Goal-Driven Execution

## Source Of Truth

`PRINCIPLES.md` is the tool-neutral source. Keep Cursor, Claude, and Codex
variants synchronized with that file.

## Codex And Claude

- Codex: use `AGENTS.md` plus `.agents/skills/tilly-engineering-discipline/`.
- Claude Code: use `CLAUDE.md` or the `.claude-plugin/` metadata.

Do not copy `.cursor/**` into Codex or Claude runtime as authoritative context.
