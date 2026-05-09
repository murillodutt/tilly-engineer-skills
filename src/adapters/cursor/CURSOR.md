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

## TES Command Intents

Use these exact TES intents when the project rule is unavailable, preserved, or
owned by the target project:

- `/tes-init`
- `/tes-update`
- `/tes-align`
- `/tes-cortex`
- `/tes-curate`
- `/tes-mcp`
- `/tes-field-reports`
- `/tes-doctor`
- `/tes-adapter`
- `/tes-bench`

Compatible aliases:

- `/tes:init`
- `/tes:update`
- `/tes:align`
- `/tes:cortex`
- `/tes:mcp`
- `/tes:field-reports`
- `/tes:doctor`
- `/tes:adapter`
- `/tes:bench`
- `/tes:check`
- `/tes:certify`
- `/tes:recall`
- `/tes:learn`
- `/tes:reflect`
- `/tes:curate`

Natural intents include: tes init, tes update, initialize TES, install TES,
recertify TES, Atualizar TES, atualizar TES, inicializar TES, instalar TES, and
recertificar TES.

## Behavioral Source Of Truth

Keep Cursor, Claude, and Codex variants synchronized at the behavioral level:
visible assumptions, smaller scope, surgical edits, and falsifiable closure.

## Codex And Claude

- Codex: use `AGENTS.md` plus `.agents/skills/tes-engineering-discipline/`.
- Claude Code: use `CLAUDE.md` or tool-native plugin metadata.

Do not copy `.cursor/**` into Codex or Claude runtime as authoritative context.
Natural alignment prompts such as `tes align`, `align TES`, `align this
project`, `alinhar TES`, and `alinhar projeto` route to `/tes-align`.
