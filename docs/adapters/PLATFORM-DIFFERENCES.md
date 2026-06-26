---
tds_id: adapters.platform_differences
tds_class: adapter
status: active
consumer: maintainers, adapter authors, and installing agents
source_of_truth: true
evidence_level: L2
tver: 0.1.5
---

# Platform Differences Reference

This reference prevents false symmetry between Codex, Claude Code, and Cursor. TES keeps one shared behavioral contract, but each platform receives that contract through its native packaging shape.

Last official-source check: 2026-05-26.

## Official Sources

| Platform | Official source checked | TES implication |
|----------|-------------------------|-----------------|
| Codex | [`openai/codex`](https://github.com/openai/codex), [AGENTS.md guide](https://developers.openai.com/codex/guides/agents-md), [skills](https://developers.openai.com/codex/skills), [plugins](https://developers.openai.com/codex/plugins/build), [slash commands](https://developers.openai.com/codex/cli/slash-commands), [config reference](https://developers.openai.com/codex/config-reference) | Codex centers project guidance in `AGENTS.md`, reusable workflows in skills, local distribution in `.codex-plugin/plugin.json`, and project-scoped lifecycle hooks installed by TES; plugin marketplace packaging remains source-only. |
| Claude Code | [`anthropics/skills`](https://github.com/anthropics/skills), [skills](https://docs.anthropic.com/en/docs/claude-code/skills), [plugins](https://docs.anthropic.com/en/docs/claude-code/plugins), [slash commands](https://docs.anthropic.com/en/docs/claude-code/slash-commands), [settings](https://docs.anthropic.com/en/docs/claude-code/settings), [hooks](https://docs.anthropic.com/en/docs/claude-code/hooks), [subagents](https://docs.anthropic.com/en/docs/claude-code/sub-agents) | Claude centers project memory in `CLAUDE.md` and skills in `SKILL.md` folders; TES keeps plugin metadata as source-only templates and blocks default subagent memory writes. |
| Cursor | [`cursor/plugins`](https://github.com/cursor/plugins), [`cursor/plugin-template`](https://github.com/cursor/plugin-template), [rules](https://docs.cursor.com/en/context/rules), [plugins](https://cursor.com/docs/plugins), [MCP](https://docs.cursor.com/en/tools/mcp), [hooks](https://cursor.com/docs/hooks), [SDK agents](https://cursor.com/docs/sdk/typescript) | Cursor centers persistent project instructions in `.cursor/rules/*.mdc` and supports richer plugin packaging with rules, skills, agents, commands, hooks, and MCP. |
| VS Code MCP | [MCP configuration](https://code.visualstudio.com/docs/copilot/reference/mcp-configuration) | VS Code is not a TES adapter, but TES certifies project-scoped Cortex MCP registration in `.vscode/mcp.json` under `servers.tes-cortex`. |

## Shared Contract

TES entry vocabulary is shared across platforms:

| Intent | Preferred trigger | Compatible alias | Meaning |
|--------|-------------------|------------------|---------|
| Initialize or recertify | `/tes-init` | `/tes-setup`, `/tes:init` | Load the assisted installer and classify the project. |
| Update existing mesh | `/tes-update` | `/tes:update` | Run the update probe, Layer Zero if needed, then converge. |
| Align project operating mesh | `/tes-align` | `/tes:align` | Deepen initial context into roadmap, state, execution line, gates, boundaries, glossary, decisions, and evidence. |
| Project GPS | `/tes-map` | `/tes:gps` | Refresh only the managed `TES-MAP` block in `PROJECT-ROADMAP.md` with current position, blockers, proof, and next move. |
| Materialize maestral goal | `/tes-goal-maestro` | `/tes:goal-maestro` | Generate an execution-grade materialization tree and a maestral `/goal` prompt from a mature SPEC, Super SPEC, PRD, relational project plan, or accepted execution tree after internal tree, material-diff, material-continuation, semantic negative-grep, sequential ownership, sync-status, and execution-unit fidelity gates pass; generated Super SPEC content is written to `GOAL-SUPER-SPEC-*.md` and summarized in chat. |
| Prospect project stress | `/tes-prospect` | `/tes:prospect` | Explicitly invoke predictive pressure on a plan or design; no broad natural activation. |
| Mine code and domain knowledge | `/tes-mine` | `/tes:mine` | Explicitly invoke code, terminology, context, and ADR mining with a cognitive brake. |
| Open Obsidian | `/tes-open-obsidian` | `/tes:open-obsidian` | Preflight context/alignment and open `docs/agents` as the Obsidian vault without writing `.obsidian/**`. |
| Cortex | `/tes-cortex` | `/tes:cortex`, `/tes:recall`, `/tes:learn`, `/tes:reflect` | Inspect, consolidate, or certify the continuity layer. |
| Curate | `/tes-curate` | `/tes:curate` | Classify Cortex memory quality risks without writing memory. |
| MCP | `/tes-mcp` | `/tes:mcp` | Inspect or activate Cortex MCP; governed remember by default, read-only opt-out. |
| Field Reports | `/tes-field-reports` | `/tes:field-reports` | Inspect or drain sanitized local feedback. |
| Doctor / health check | `/tes-doctor` | `/tes:doctor`, `/tes:check`, `/tes:certify` | Inspect local TES health and blockers. |
| Adapter | `/tes-adapter` | `/tes:adapter` | Materialize, dry-run, retrofit, or certify adapter surfaces. |
| Bench | `/tes-bench` | `/tes:bench` | Plan, run, or inspect context-mesh benchmark evidence under the temporal evidence contract. |
| Bump | `/tes-bump` | `/tes:bump` | Govern, plan, and apply bounded project version bumps through read-only governance and dry-run-first target discovery; no Git or publishing side effects. |

The hyphen form is the preferred cross-platform trigger. The colon form is a compatibility alias and may be rejected by a host slash-command parser. If a host says a `/tes:*` slash command is invalid, the agent must treat the text as TES intent and route to the matching `tes-*` skill, rule, or installer spec. Natural intent text such as `tes init`, `tes setup`, `tes update`, `tes align`, `tes map`, `generate a maestral /goal prompt`, `gerar um /goal maestral`, `project GPS`, `mapa TES`, `tes open obsidian`, `tes bump`, `align TES`, `align this project`, `map this project`, `open Obsidian`, `open this project in Obsidian`, `Atualizar TES`, `atualizar TES`, `alinhar TES`, `alinhar projeto`, `mapear TES`, `mapear projeto`, `abrir Obsidian`, `abrir no Obsidian`, `initialize TES`, `install TES`, `recertify TES`, `inicializar TES`, `instalar TES`, and `recertificar TES` must route to the same contract. `/tes-prospect`, `/tes-mine`, and `/tes-goal-maestro` are intentionally excluded from broad natural intent routing. `tes-goal-maestro` may also route from a direct request to generate a maestral `/goal` prompt from a mature SPEC, Super SPEC, PRD, relational project plan, or accepted execution tree. Generated Super SPEC content must be written to `GOAL-SUPER-SPEC-*.md` and summarized in chat instead of pasted into the context window. Prospecting and mining activate only when named by trigger, alias, or explicit skill invocation, then operate proactively until the user pulls the cognitive brake.

## Surface Differences

| Surface | Codex | Claude Code | Cursor |
|---------|-------|-------------|--------|
| Base guidance | `AGENTS.md` | `CLAUDE.md` | `.cursor/rules/*.mdc`; `AGENTS.md` may be a simple alternative in Cursor projects |
| TES package source | `src/adapters/codex/AGENTS.md` | `src/adapters/claude/CLAUDE.md` | `src/adapters/cursor/rules/tes-engineering-discipline.mdc`, `src/adapters/cursor/rules/tes-runtime-capabilities.mdc`, plus `src/adapters/cursor/CURSOR.md` as a user handoff note |
| Skills | `.agents/skills/**` | `.claude/skills/**` | Official Cursor plugins support `skills/**`; TES currently certifies command capability routing through `.cursor/rules/tes-runtime-capabilities.mdc` |
| Plugin metadata | Source-only under `src/adapters/codex/plugin/**` | Source-only under `src/adapters/claude/plugin/**` | `.cursor-plugin/plugin.json` exists officially; TES v1 does not publish or certify a Cursor plugin |
| Rules | Project guidance through `AGENTS.md` | No Cursor-style `.mdc` rule surface | `.cursor/rules/*.mdc` with frontmatter; TES separates governance from runtime command capability routing |
| MCP config | `.codex/config.toml` | `.mcp.json` | `.cursor/mcp.json` for project config; plugin MCP is a future packaging decision |
| Hooks | Project `SessionStart` and `PreToolUse` hooks are installed by TES through `.codex/config.toml` when the hooks surface is attached; `hooks = true` is set and TES preserves foreign config. Codex also supports `.codex/hooks.json`, so uninstall and residue checks clean legacy TES commands there without making it the TES writer surface. | Project `SessionStart` and `PreToolUse` hooks are installed through `.claude/settings.json` when the hooks surface is attached; TES preserves foreign hook groups. | Project `sessionStart`, `beforeSubmitPrompt`, and `preToolUse` hooks are installed through `.cursor/hooks.json` when the hooks surface is attached; Cursor permission decisions use JSON output, not exit-code blocking. |
| Subagent or agent boundary | Native subagents exist, but TES memory writes stay parent-owned | Native subagents exist, but default package blocks direct durable writes | Native agents exist, but TES package claims only rules, project hooks, and MCP install |

## Memory Lifecycle Boundary

Adapter lifecycle parity means each delivered surface names the same six moments: recall, scope normalization, write gate, checkpoint, closeout, and subagent return. The package may certify that textual and materialized boundary only when `scripts/adapter_parity_readiness.py` passes.

Subagent return is not write authority. Subagents or agents may return findings and evidence to the parent context; the parent owns durable memory promotion and the write gate. Checkpoints and event records remain future waves, not implied by this adapter matrix.

## Platform Decisions

| Decision | Rationale |
|----------|-----------|
| Do not force one filename across all tools. | `AGENTS.md`, `CLAUDE.md`, and `.cursor/rules/*.mdc` are different native surfaces. |
| Keep `/tes-*` as the shared user vocabulary. | The user entrypoint should stay stable even when a host packages commands differently. |
| Treat `/tes:*` as intent text when native slash parsing fails. | This avoids Claude, Cursor, or Codex asking the user to choose a route when TES already knows the route. |
| Do not call `CURSOR.md` the primary Cursor operative surface. | Cursor's governed surface is `.cursor/rules/*.mdc`; `CURSOR.md` is a TES handoff note. |
| Treat VS Code MCP as consumer config, not an adapter. | `.vscode/mcp.json` registers the same project-scoped `tes-cortex` server but does not add TES skills, rules, hooks, or bootloader semantics for VS Code. |
| Do not claim marketplace or plugin publication from local files. | Local plugin metadata is not proof of marketplace distribution or live IDE activation. |
| Do not create false parity from copied prose. | Parity is a retained decision under the same behavioral gate, not matching markdown. |
| Back up project-owned bootloaders before clean runtime refresh. | A conflict in `AGENTS.md`, `CLAUDE.md`, or Cursor handoff files must not block install. The clean route snapshots them under `.tes/bk/**`, applies canonical TES runtime, and recovers durable semantics into `docs/agents/**`; preserve mode is compatibility-only. |

## Maintainer Checklist

When an official platform source changes, update the correlated surfaces in the same patch:

| Change observed | Required local checks |
|-----------------|-----------------------|
| Codex changes AGENTS, skills, plugins, hooks, commands, or MCP semantics | `docs/adapters/CODEX.md`, `src/adapters/codex/**`, `scripts/platform_surface_oracle.py` |
| Claude changes skills, plugins, slash commands, settings, hooks, or MCP semantics | `docs/adapters/CLAUDE.md`, `src/adapters/claude/**`, `scripts/claude_plugin_oracle.py`, `scripts/platform_surface_oracle.py` |
| Cursor changes rules, plugins, skills, commands, hooks, agents, or MCP semantics | `docs/adapters/CURSOR.md`, `src/adapters/cursor/**`, `scripts/platform_surface_oracle.py` |
| VS Code MCP config semantics change | `docs/mesh/CORTEX-MCP.md`, `scripts/install_mcp.py`, `scripts/install_smoke.py`, `scripts/platform_surface_oracle.py` |
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
