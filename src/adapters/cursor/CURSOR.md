# Using This Repo With Cursor

This target repository includes a Cursor project rule for Tilly Engineering
Discipline.

## In This Repository

Cursor loads `.cursor/rules/tes-guidelines.mdc` for governance and
`.cursor/rules/tes-runtime-capabilities.mdc` for TES command routing.

## Use In Another Project

Back up existing Cursor rules under `.tes/bk/**`, then copy
`.cursor/rules/tes-guidelines.mdc` and
`.cursor/rules/tes-runtime-capabilities.mdc` into the target project's rule set.

If the target project already has rules, recover useful local semantics into
`docs/agents/**` rather than duplicating long runtime prose:

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
- `/tes-map`
- `/tes-open-obsidian`
- `/tes-cortex`
- `/tes-curate`
- `/tes-mcp`
- `/tes-field-reports`
- `/tes-doctor`
- `/tes-adapter`
- `/tes-bench`
- `/tes-bump`
- `/tes-tts`

Compatible aliases:

- `/tes:init`
- `/tes:update`
- `/tes:align`
- `/tes:gps`
- `/tes:open-obsidian`
- `/tes:cortex`
- `/tes:mcp`
- `/tes:field-reports`
- `/tes:doctor`
- `/tes:adapter`
- `/tes:bench`
- `/tes:bump`
- `/tes:tts`
- `/tes:check`
- `/tes:certify`
- `/tes:recall`
- `/tes:learn`
- `/tes:reflect`
- `/tes:curate`

Natural intents include: tes init, tes update, tes align, tes map, project GPS,
mapa TES, tes open obsidian, tes bump, tes tts, read this text aloud, leia em
voz alta, narrar este texto, align TES, align this project, map this project,
open Obsidian, open this project in Obsidian, Atualizar TES, atualizar TES,
alinhar TES, alinhar projeto, mapear TES, mapear projeto, abrir Obsidian,
abrir no Obsidian, initialize TES, install TES, recertify TES, inicializar TES,
instalar TES, and recertificar TES.

## Behavioral Source Of Truth

Keep Cursor, Claude, and Codex variants synchronized at the behavioral level:
visible assumptions, smaller scope, surgical edits, and falsifiable closure.

## Codex And Claude

- Codex: use `AGENTS.md` plus `.agents/skills/tes-engineering-discipline/`.
- Claude Code: use `CLAUDE.md` plus `.claude/skills/**`.

Do not copy `.cursor/**` into Codex or Claude runtime as authoritative context.
Natural alignment prompts such as `tes align`, `align TES`, `align this project`,
`alinhar TES`, and `alinhar projeto` route to `/tes-align`.
Obsidian opening prompts such as `open Obsidian`,
`open this project in Obsidian`, `abrir Obsidian`, and `abrir no Obsidian`
route to `/tes-open-obsidian`.
