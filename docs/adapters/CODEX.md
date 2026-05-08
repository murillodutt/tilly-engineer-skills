---
tds_id: adapters.codex
tds_class: adapter
status: active
consumer: codex adopters
source_of_truth: true
evidence_level: L2
tver: 0.5.0
---

# Codex Derivation

This document describes the Codex-native derivation of Tilly Engineering
Discipline.

Project version: `0.3.64`.

It follows the Codex customization order:

1. `AGENTS.md` for durable repository guidance in the target project.
2. Skills for reusable workflows and domain expertise.
3. Scripts and references for progressive disclosure.
4. Read-only Cortex MCP through project-scoped `.codex/config.toml`.
5. A local Codex plugin package only for distribution/materialization proof.

Official reference: <https://developers.openai.com/codex/concepts/customization>

## Files To Copy

| Source | Target |
|--------|--------|
| `src/adapters/codex/AGENTS.md` | Target repo root `AGENTS.md` or merge into existing one |
| `src/adapters/codex/skills/tes-engineering-discipline/` | Target repo `.agents/skills/tes-engineering-discipline/` |
| `src/adapters/codex/skills/tes-*/` | Target repo `.agents/skills/tes-*/` command-shortcut skills |
| `src/adapters/codex/plugin/plugin.json` | Target repo `plugins/tilly-engineer-skills/.codex-plugin/plugin.json` |
| `src/adapters/codex/plugin/marketplace.json` | Target repo `.agents/plugins/marketplace.json` |
| `scripts/install_mcp.py` | Optional project-scoped Cortex MCP activation |
| `scripts/validate_reference_package.py` | Optional package validation script |

For a global personal skill, copy the skill directory to
`$HOME/.agents/skills/tes-engineering-discipline/`.

Do not treat local Codex runtime caches or tool-specific user directories as
canonical package source. They are installed/runtime surfaces.

## Local Plugin Package

TES materializes a local Codex plugin package under
`plugins/tilly-engineer-skills/**`. The package contains
`.codex-plugin/plugin.json` and plugin-root `skills/**` generated from the same
canonical skill sources used for project `.agents/skills/**`.

The package is certified as a local materialized artifact only. It does not
claim marketplace publication, live Codex UI installation, native hooks, or
plugin-bundled MCP servers. Those surfaces require separate official-source
proof, safety contract, smoke, and negative tests.

## Why This Shape

Codex uses progressive disclosure for skills:

- Metadata stays visible for discovery.
- `SKILL.md` loads only when the workflow is selected.
- References and scripts load or run only when needed.

The preferred TES shortcuts map to Codex skills. `/tes-init`, `/tes-update`,
`/tes:init`, `/tes:update`, `tes init`, and natural init/update command-prompts all route to
`tes-init`. They keep the user entrypoint short while delegating real work to
deterministic oracles:

| Shortcut | Skill |
|----------|-------|
| `/tes-init`, `/tes:init` | `tes-init` |
| `/tes-update`, `/tes:update` | `tes-init` |
| `/tes-cortex`, `/tes:cortex` | `tes-cortex` |
| `/tes-mcp`, `/tes:mcp` | `tes-mcp` |
| `/tes-doctor`, `/tes:doctor` | `tes-doctor` |
| `/tes-adapter`, `/tes:adapter` | `tes-adapter` |
| `/tes-bench`, `/tes:bench` | `tes-bench` |

This keeps the four gates available without bloating every context window.

## Do Not Copy

Do not copy these adapter sources into Codex runtime as authoritative surfaces:

- `src/adapters/claude/**`
- `src/adapters/cursor/**`
- `.DS_Store`

They are tool-specific packages or local OS artifacts. Use them only as source
material when maintaining the corresponding tool variant.

## Validation

From this repository:

```bash
python3 scripts/validate_reference_package.py
python3 scripts/context_mesh_plan.py
python3 scripts/codex_plugin_oracle.py --self-test
python3 scripts/materialize_adapter.py codex --check
python3 src/adapters/codex/skills/tes-engineering-discipline/scripts/discipline_oracle.py --self-test
```

In a target Codex repository, add project-specific checks such as tests,
typecheck, lint, build, or governance gates. The discipline is successful only
when a concrete oracle passes.
