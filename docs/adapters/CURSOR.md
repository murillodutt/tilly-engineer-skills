---
tds_id: adapters.cursor
tds_class: adapter
status: active
consumer: cursor adopters and package maintainers
source_of_truth: true
evidence_level: L2
tver: 0.3.3
---

# Cursor Adapter

This document governs the Cursor derivation of Tilly Engineering Discipline.

Cursor alignment is rule-first. The operative package surfaces are project rules under `.cursor/rules/**`; `CURSOR.md` is a user handoff note only.

## Official Surfaces

| Surface | Role | Package Status |
|---------|------|----------------|
| `.cursor/rules/tes-engineering-discipline.mdc` | Always-on discipline anchor (`alwaysApply: true`) | Included |
| `.cursor/rules/tes-runtime-capabilities.mdc` | Lazy capability rule (`alwaysApply: false` + `description`, Apply Intelligently); loads the full command/gate detail only when relevant | Included |
| `AGENTS.md` | Simple root-only alternative context | Not materialized by default |
| `.cursorrules` | Legacy rule file | Forbidden |
| MCP | Project-scoped Cortex access | Installer route only |
| Hooks | Agent-loop controls | Blocked by default |
| Background agents | Remote async execution | Blocked by default |
| CLI commands | Runtime controls | Not package source |

Official references: [Rules](https://docs.cursor.com/en/context/rules), [MCP](https://docs.cursor.com/en/tools/mcp), [Hooks](https://cursor.com/docs/hooks), and [Background Agents](https://docs.cursor.com/en/background-agents).

## Source Contract

| Source | Purpose |
|--------|---------|
| `src/adapters/cursor/rules/tes-engineering-discipline.mdc` | Always-on discipline anchor source (`alwaysApply: true`) |
| `src/adapters/cursor/rules/tes-runtime-capabilities.mdc` | Lazy capability rule source (`alwaysApply: false` + `description`) |
| `src/adapters/cursor/CURSOR.md` | User adapter note |

The discipline anchor uses `alwaysApply: true` because the maturity-aware gates are a general behavioral overlay for non-trivial coding, review, refactor, and instruction migration work, so they must stay loaded every turn. The capability rule uses `alwaysApply: false` with a `description` (the Cursor-native Apply Intelligently mode, verified against the official Cursor rule-loading model): the full command protocols, gate flows, Cortex reflex, Field Reports, and memory lifecycle boundary load only when the description matches the request. This is the three-layer contract — short always-on anchor, lazy expansion — that the bootloader-to-skill migration established and `materialize_adapter.py` enforces.

Cursor does not receive a separate skill package. The rules treat `/tes-init`, `/tes-update`, `/tes:init`, `/tes:update`, `tes init`, natural init/update command-prompts, `/tes-cortex`, `/tes:cortex`, `/tes-mcp`, `/tes:mcp`, `/tes-field-reports`, `/tes:field-reports`, `/tes-doctor`, `/tes:doctor`, `/tes-adapter`, `/tes:adapter`, `/tes-bench`, `/tes:bench`, `/tes-align`, `/tes:align`, `tes align`, `align TES`, `align this project`, `alinhar TES`, `alinhar projeto`, `/tes-goal-maestro`, `/tes:goal-maestro`, `generate a maestral /goal prompt`, `gerar um /goal maestral`, `/tes-prospect`, `/tes:prospect`, `/tes-mine`, `/tes:mine`, `/tes-open-obsidian`, `/tes:open-obsidian`, `open Obsidian`, `open this project in Obsidian`, `abrir Obsidian`, `abrir no Obsidian`, `/tes-curate`, `/tes:curate`, `/tes-bump`, `/tes:bump`, and `tes bump` as intent shortcuts for the same deterministic oracles used by Codex and Claude. `/tes-goal-maestro`, `/tes-prospect`, and `/tes-mine` remain explicit routes: do not activate them from broad natural-language planning text. `/tes-bump` is a version governance guard: direct bump/sync requests route to it, and commit, release, delivered-behavior, or gate-reported bump conditions auto-activate its read-only governance check. `tes-goal-maestro` may also route from a direct request to generate a maestral `/goal` prompt from a mature SPEC, Super SPEC, PRD, relational project plan, or accepted execution tree. It must preserve declared execution units, validate the tree internally, require material-diff, material-continuation, semantic negative-grep, sequential ownership and sync-status evidence, write generated Super SPEC content to `GOAL-SUPER-SPEC-*.md` instead of pasting it into chat, and generate the final `/goal` when gates pass. `tes-bump` must dry-run target discovery before writes and never commit, tag, push, publish, or edit remotes.

Capability and workflow detail belongs in the lazy `tes-runtime-capabilities.mdc` rule (Apply Intelligently), not in the always-on anchor. Future workflow-specific rules should likewise be separate `Agent Requested` or manual rules, so the always-on layer stays thin.

## Packaging Rules

- Do not reintroduce `.cursorrules`.
- Keep `.mdc` frontmatter with a `description` on both rules: `tes-engineering-discipline.mdc` at `alwaysApply: true` (always-on anchor) and `tes-runtime-capabilities.mdc` at `alwaysApply: false` (lazy capability rule).
- Do not materialize `AGENTS.md` for Cursor without an explicit decision, because it can duplicate `.cursor/rules/**`.
- Back up project-owned Cursor governance rules, apply clean TES rules, and recover durable local semantics into `docs/agents/**`. Refresh manifest-known TES-owned runtime capability rules such as `tes-runtime-capabilities.mdc`.
- Keep hook config and environment files out of Cursor plugin packaging. The project installer may attach `.cursor/hooks.json` for `sessionStart`, `beforeSubmitPrompt`, and `preToolUse` when the hooks surface is selected.
- Cortex MCP may be activated by the assisted installer through project-scoped `.cursor/mcp.json`. ADR 0002 governed remember is available by default and still requires exact approval.

## Sensitive Surface Register

| Surface | Risk | Default |
|---------|------|---------|
| `.cursor/mcp.json` | Adds external tools and approvals | Read-only Cortex only via installer |
| Hooks | Can alter agent loop behavior | Out of package |
| Environment setup | Can install packages or prepare cloud agents | Out of package |
| Background agents | Remote branch execution | Out of package |

## Memory Lifecycle Boundary

Cursor receives the TES memory lifecycle as rule text plus project-scoped advisory hooks, not as a write-capable plugin agent or hook package.

| Moment | Package stance |
|--------|----------------|
| recall | `/tes-cortex`, Cortex reflection, and runtime recall injection stay no-write unless an explicit memory operation is authorized |
| scope normalization | Deferred to the shared normalizer wave |
| write gate | Durable Cortex writes require explicit parent authorization |
| checkpoint | Deferred to the checkpoint lane wave |
| closeout | Governed by TES oracles, repository Git hooks, and host hook advisories |
| subagent return | Agents may return evidence only; parent owns memory |

Cursor plugin hooks and SDK agents remain outside TES plugin packaging. Project-scoped TES hooks may emit `NEEDS_ALIGN`, but they must not write the operating mesh or run `/tes-align` automatically. Parent-owned memory means no durable Cortex writes from an agent without the parent write gate.

## Validation

Run:

```bash
npm run materialize:cursor
npm run materialize:check
npm run commit:check
```

Cursor alignment is complete only when the generated rule keeps the required frontmatter and no legacy rule file exists in the package.
