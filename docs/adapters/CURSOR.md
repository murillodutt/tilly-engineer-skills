---
tds_id: adapters.cursor
tds_class: adapter
status: active
consumer: cursor adopters and package maintainers
source_of_truth: true
evidence_level: L2
tver: 0.1.0
---

# Cursor Adapter

This document governs the Cursor derivation of Tilly Engineering Discipline.

Cursor alignment is rule-first. The operative package surface is the project
rule under `.cursor/rules/**`; `CURSOR.md` is a human handoff note only.

## Official Surfaces

| Surface | Role | Package Status |
|---------|------|----------------|
| `.cursor/rules/*.mdc` | Project rules with frontmatter | Included |
| `AGENTS.md` | Simple root-only alternative context | Not materialized by default |
| `.cursorrules` | Legacy rule file | Forbidden |
| MCP | External tool integration | Blocked by default |
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
| `src/adapters/cursor/rules/tilly-guidelines.mdc` | Always-on Cursor rule source |
| `src/adapters/cursor/CURSOR.md` | Human adapter note |

The base discipline uses `alwaysApply: true` because the four gates are a
general behavioral overlay for non-trivial coding, review, refactor, and
instruction migration work.

Future workflow-specific rules should be separate `Agent Requested` or
manual rules instead of expanding the always-on rule.

## Packaging Rules

- Do not reintroduce `.cursorrules`.
- Keep `.mdc` frontmatter with `description` and `alwaysApply: true`.
- Do not materialize `AGENTS.md` for Cursor without an explicit decision,
  because it can duplicate `.cursor/rules/**`.
- Do not add `.cursor/mcp.json`, hook config, or environment files to the
  default package.

## Sensitive Surface Register

| Surface | Risk | Default |
|---------|------|---------|
| `.cursor/mcp.json` | Adds external tools and approvals | Out of package |
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
