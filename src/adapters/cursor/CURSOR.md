# Using This Repo With Cursor

Thin pointer to the Cursor rule layer. Cursor loads
`.cursor/rules/tes-guidelines.mdc` as the always-on discipline anchor and
`.cursor/rules/tes-runtime-capabilities.mdc` as the lazy capability rule (Apply
Intelligently) that carries the full gate flows and `/tes-*` command protocols.
The rules are the runtime authority; this file is only an outward pointer.

## Use In Another Project

Back up existing Cursor rules under `.tes/bk/**`, then copy both rules into the
target project's rule set. If the target already has rules, recover useful local
semantics into `docs/agents/**` rather than duplicating runtime prose. The four
principles — Think Before Coding, Simplicity First, Surgical Changes,
Goal-Driven Execution — live in the discipline anchor.

## TES Intents

`/tes-*` are canonical intents and `/tes:*` are compatible aliases — intent
shortcuts, not shell commands. The full list and protocol live in
`tes-runtime-capabilities.mdc`; common ones are `/tes-init`, `/tes-update`,
`/tes-align`, `/tes-map`, `/tes-cortex`, `/tes-mcp`, `/tes-doctor`, and
`/tes-bump`. Bilingual natural intents (tes init, align this project,
alinhar projeto, map this project, mapear projeto, Atualizar TES,
open Obsidian, abrir Obsidian) route the same way. `/tes-prospect`, `/tes-mine`,
and `/tes-goal-maestro` require explicit invocation and honor the cognitive
brake.

## Confidentiality

Use neutral placeholder vocabulary only; no real project, product,
internal-service names, or `~/Dev/<name>` paths in tracked content.

## Behavioral Source Of Truth

Keep Cursor, Claude, and Codex variants synchronized at the behavioral level:
visible assumptions, smaller scope, surgical edits, and falsifiable closure.

- Codex: `AGENTS.md` plus `.agents/skills/tes-*/**`.
- Claude Code: `CLAUDE.md` plus `.claude/skills/**`.

Do not copy `.cursor/**` into Codex or Claude runtime as authoritative context.
