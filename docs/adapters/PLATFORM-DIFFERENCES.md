---
tds_id: adapters.platform_differences
tds_class: adapter
status: active
consumer: maintainers, adapter authors, and installing agents
source_of_truth: true
evidence_level: L2
tver: 0.1.1
---

# Platform Differences Reference

This reference prevents false symmetry between Codex, Claude Code, and Cursor.
TES keeps one shared behavioral contract, but each platform receives that
contract through its native packaging shape.

Last official-source check: 2026-05-08.

## Official Sources

| Platform | Official source checked | TES implication |
|----------|-------------------------|-----------------|
| Codex | [`openai/codex`](https://github.com/openai/codex), [AGENTS.md guide](https://developers.openai.com/codex/guides/agents-md), [skills](https://developers.openai.com/codex/skills), [slash commands](https://developers.openai.com/codex/cli/slash-commands) | Codex centers project guidance in `AGENTS.md` and reusable workflows in skills. |
| Claude Code | [`anthropics/skills`](https://github.com/anthropics/skills), [skills](https://code.claude.com/docs/en/skills), [plugins](https://code.claude.com/docs/en/plugins), [slash commands](https://code.claude.com/docs/en/slash-commands), [settings](https://code.claude.com/docs/en/settings) | Claude centers project memory in `CLAUDE.md`, skills in `SKILL.md` folders, and optional plugin metadata under `.claude-plugin/**`. |
| Cursor | [`cursor/plugins`](https://github.com/cursor/plugins), [`cursor/plugin-template`](https://github.com/cursor/plugin-template), [rules](https://cursor.com/docs/rules), [plugins](https://cursor.com/docs/plugins), [MCP](https://cursor.com/docs/mcp) | Cursor centers persistent project instructions in `.cursor/rules/*.mdc` and supports richer plugin packaging with rules, skills, agents, commands, hooks, and MCP. |

## Shared Contract

TES entry vocabulary is shared across platforms:

| Intent | Preferred trigger | Compatible alias | Meaning |
|--------|-------------------|------------------|---------|
| Initialize or recertify | `/tes-init` | `/tes:init` | Load the assisted installer and classify the project. |
| Update existing mesh | `/tes-update` | `/tes:update` | Run the update probe, Layer Zero if needed, then converge. |
| Cortex | `/tes-cortex` | `/tes:cortex`, `/tes:recall`, `/tes:learn`, `/tes:reflect` | Inspect or certify the continuity layer. |
| Curate | `/tes-curate` | `/tes:curate` | Classify Cortex memory quality risks without writing memory. |
| MCP | `/tes-mcp` | `/tes:mcp` | Inspect or activate read-only Cortex MCP. |
| Field Reports | `/tes-field-reports` | `/tes:field-reports` | Inspect or drain sanitized local feedback. |
| Doctor / health check | `/tes-doctor` | `/tes:doctor`, `/tes:check`, `/tes:certify` | Inspect local TES health and blockers. |
| Adapter | `/tes-adapter` | `/tes:adapter` | Materialize, dry-run, retrofit, or certify adapter surfaces. |
| Bench | `/tes-bench` | `/tes:bench` | Plan, run, or inspect context-mesh benchmark evidence. |

The hyphen form is the preferred cross-platform trigger. The colon form is a
compatibility alias and may be rejected by a host slash-command parser. If a
host says a `/tes:*` slash command is invalid, the agent must treat the text as
TES intent and route to the matching `tes-*` skill, rule, or installer spec.
Natural intent text such as `tes init`, `tes update`, `Atualizar TES`,
`atualizar TES`, `initialize TES`, `install TES`, `recertify TES`,
`inicializar TES`, `instalar TES`, and `recertificar TES` must route to the
same contract.

## Surface Differences

| Surface | Codex | Claude Code | Cursor |
|---------|-------|-------------|--------|
| Base guidance | `AGENTS.md` | `CLAUDE.md` | `.cursor/rules/*.mdc`; `AGENTS.md` may be a simple alternative in Cursor projects |
| TES package source | `src/adapters/codex/AGENTS.md` | `src/adapters/claude/CLAUDE.md` | `src/adapters/cursor/rules/tes-guidelines.mdc` plus `src/adapters/cursor/CURSOR.md` as a human handoff note |
| Skills | `.agents/skills/**` | `.claude/skills/**` and plugin `skills/**` | Official Cursor plugins support `skills/**`; TES v1 does not yet claim a Cursor plugin skill package |
| Plugin metadata | Native support exists, but TES does not ship Codex plugin metadata yet | `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` | `.cursor-plugin/plugin.json` exists officially; TES v1 does not publish or certify a Cursor plugin |
| Rules | Project guidance through `AGENTS.md` | No Cursor-style `.mdc` rule surface | `.cursor/rules/*.mdc` with frontmatter such as `description` and `alwaysApply` |
| MCP config | `.codex/config.toml` | `.mcp.json` | `.cursor/mcp.json` for project config; plugin MCP is a future packaging decision |
| Hooks | Tool-native hooks are sensitive and not claimed by TES default package | Tool-native hooks are sensitive and not claimed by TES default package | Plugin hooks exist officially; TES default package still uses repository Git hooks only |

## Platform Decisions

| Decision | Rationale |
|----------|-----------|
| Do not force one filename across all tools. | `AGENTS.md`, `CLAUDE.md`, and `.cursor/rules/*.mdc` are different native surfaces. |
| Keep `/tes-*` as the shared user vocabulary. | The human entrypoint should stay stable even when a host packages commands differently. |
| Treat `/tes:*` as intent text when native slash parsing fails. | This avoids Claude, Cursor, or Codex asking the user to choose a route when TES already knows the route. |
| Do not call `CURSOR.md` the primary Cursor operative surface. | Cursor's governed surface is `.cursor/rules/*.mdc`; `CURSOR.md` is a TES handoff note. |
| Do not claim marketplace or plugin publication from local files. | Local plugin metadata is not proof of marketplace distribution or live IDE activation. |
| Do not create false parity from copied prose. | Parity is a retained decision under the same behavioral gate, not matching markdown. |

## Maintainer Checklist

When an official platform source changes, update the correlated surfaces in the
same patch:

| Change observed | Required local checks |
|-----------------|-----------------------|
| Codex changes AGENTS, skills, plugins, hooks, commands, or MCP semantics | `docs/adapters/CODEX.md`, `src/adapters/codex/**`, `scripts/platform_surface_oracle.py` |
| Claude changes skills, plugins, slash commands, settings, hooks, or MCP semantics | `docs/adapters/CLAUDE.md`, `src/adapters/claude/**`, `scripts/claude_plugin_oracle.py`, `scripts/platform_surface_oracle.py` |
| Cursor changes rules, plugins, skills, commands, hooks, agents, or MCP semantics | `docs/adapters/CURSOR.md`, `src/adapters/cursor/**`, `scripts/platform_surface_oracle.py` |
| Any command trigger behavior changes | `docs/install/COMMAND-TRIGGERS.md`, `docs/install/MINI-PROMPT.md`, `docs/install/ASSISTED-CONTEXT-INSTALLER.prompt.md`, adapter skills/rules |
| Trigger parity changes across adapters | `scripts/command_trigger_oracle.py --self-test` |

Minimum closure gates:

```bash
python3 scripts/validate_tds.py
python3 scripts/validate_reference_package.py
python3 scripts/command_trigger_oracle.py --self-test
python3 scripts/platform_surface_oracle.py --self-test
python3 scripts/materialize_adapter.py all --check
npm run commit:check
```
