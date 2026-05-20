---
tds_id: adapters.cursor
tds_class: adapter
status: active
consumer: cursor adopters and package maintainers
source_of_truth: true
evidence_level: L2
tver: 0.3.2
---

# Cursor Adapter

This document governs the Cursor derivation of Tilly Engineering Discipline.

Cursor alignment is rule-first. The operative package surfaces are project
rules under `.cursor/rules/**`; `CURSOR.md` is a user handoff note only.

## Official Surfaces

| Surface | Role | Package Status |
|---------|------|----------------|
| `.cursor/rules/tes-guidelines.mdc` | Governance overlay with frontmatter | Included |
| `.cursor/rules/tes-runtime-capabilities.mdc` | TES-owned command router refreshed after central backup and clean runtime install | Included |
| `AGENTS.md` | Simple root-only alternative context | Not materialized by default |
| `.cursorrules` | Legacy rule file | Forbidden |
| MCP | Project-scoped Cortex access | Installer route only |
| Hooks | Agent-loop controls | Blocked by default |
| Background agents | Remote async execution | Blocked by default |
| CLI commands | Runtime controls | Not package source |

Official references: [Rules](https://docs.cursor.com/en/context/rules),
[MCP](https://docs.cursor.com/en/tools/mcp),
[Hooks](https://cursor.com/docs/hooks), and
[Background Agents](https://docs.cursor.com/en/background-agents).

## Source Contract

| Source | Purpose |
|--------|---------|
| `src/adapters/cursor/rules/tes-guidelines.mdc` | Always-on Cursor rule source |
| `src/adapters/cursor/rules/tes-runtime-capabilities.mdc` | TES-owned runtime capability router |
| `src/adapters/cursor/CURSOR.md` | User adapter note |

The base discipline uses `alwaysApply: true` because the four gates are a
general behavioral overlay for non-trivial coding, review, refactor, and
instruction migration work.

Cursor does not receive a separate skill package. The rules treat
`/tes-init`, `/tes-update`, `/tes:init`, `/tes:update`, `tes init`, natural
init/update command-prompts, `/tes-cortex`, `/tes:cortex`, `/tes-mcp`,
`/tes:mcp`, `/tes-field-reports`, `/tes:field-reports`, `/tes-doctor`,
`/tes:doctor`, `/tes-adapter`, `/tes:adapter`, `/tes-bench`, `/tes:bench`,
`/tes-align`, `/tes:align`, `tes align`, `align TES`, `align this project`,
`alinhar TES`, `alinhar projeto`, `/tes-goal-maestro`,
`/tes:goal-maestro`, `generate a maestral /goal prompt`,
`gerar um /goal maestral`, `/tes-prospect`, `/tes:prospect`,
`/tes-mine`, `/tes:mine`, `/tes-open-obsidian`,
`/tes:open-obsidian`, `open Obsidian`, `open this project in Obsidian`,
`abrir Obsidian`, `abrir no Obsidian`, `/tes-curate`, and `/tes:curate` as
intent shortcuts for the same deterministic oracles used by Codex and Claude.
`/tes-goal-maestro`, `/tes-prospect`, and `/tes-mine` remain explicit routes:
do not activate them from broad natural-language planning text.
`tes-goal-maestro` may also route from a direct request to generate a maestral
`/goal` prompt from a mature SPEC.

Future workflow-specific rules should be separate `Agent Requested` or
manual rules instead of expanding the always-on rule.

## Packaging Rules

- Do not reintroduce `.cursorrules`.
- Keep `.mdc` frontmatter with `description` and `alwaysApply: true`.
- Do not materialize `AGENTS.md` for Cursor without an explicit decision,
  because it can duplicate `.cursor/rules/**`.
- Back up project-owned Cursor governance rules, apply clean TES rules, and
  recover durable local semantics into `docs/agents/**`. Refresh manifest-known
  TES-owned runtime capability rules such as `tes-runtime-capabilities.mdc`.
- Do not add hook config or environment files to the default package.
- Read-only Cortex MCP may be activated by the assisted installer through
  project-scoped `.cursor/mcp.json`.

## Sensitive Surface Register

| Surface | Risk | Default |
|---------|------|---------|
| `.cursor/mcp.json` | Adds external tools and approvals | Read-only Cortex only via installer |
| Hooks | Can alter agent loop behavior | Out of package |
| Environment setup | Can install packages or prepare cloud agents | Out of package |
| Background agents | Remote branch execution | Out of package |

## Validation

Run:

```bash
npm run materialize:cursor
npm run materialize:check
npm run commit:check
```

Cursor alignment is complete only when the generated rule keeps the required
frontmatter and no legacy rule file exists in the package.
