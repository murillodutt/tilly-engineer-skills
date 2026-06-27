---
tds_id: adapters.codex
tds_class: adapter
status: active
consumer: codex adopters
source_of_truth: true
evidence_level: L2
tver: 0.5.3
---

# Codex Derivation

This document describes the Codex-native derivation of Tilly Engineering Discipline.

Project version: `0.3.217`.

It follows the Codex customization order:

1. `AGENTS.md` for durable repository guidance in the target project.
2. Skills for reusable workflows and domain expertise.
3. Scripts and references for progressive disclosure.
4. Cortex MCP through project-scoped `.codex/config.toml`, with ADR 0002 governed remember available by default and `--read-only` as the opt-out.
5. Source-only Codex plugin metadata retained in Git for future packaging proof.

Official reference: <https://developers.openai.com/codex/concepts/customization>

## Files To Copy

| Source | Target |
|--------|--------|
| `src/adapters/codex/AGENTS.md` | Target repo root `AGENTS.md` after `.tes/bk/**` backup; recover old semantics into `docs/agents/**` |
| `src/adapters/codex/skills/tes-engineering-discipline/` | Target repo `.agents/skills/tes-engineering-discipline/` |
| `src/adapters/codex/skills/tes-*/` | Target repo `.agents/skills/tes-*/` command-shortcut skills |
| `scripts/install_mcp.py` | Optional project-scoped Cortex MCP activation |
| `scripts/validate_reference_package.py` | Optional package validation script |

For a global personal skill, copy the skill directory to `$HOME/.agents/skills/tes-engineering-discipline/`.

Do not treat local Codex runtime caches or tool-specific user directories as canonical package source. They are installed/runtime surfaces.

## Source-Only Plugin Metadata

TES keeps Codex plugin metadata under `src/adapters/codex/plugin/**` as a source-only template. The default installer does not write `.agents/plugins/**` or `plugins/tilly-engineer-skills/**` into target projects.

If a target already contains those paths from an older TES install, the bundle apply step removes them only when they are TES-owned/generated or empty. Ambiguous or modified content is preserved, backed up under `.tes/bk/**`, and reported as `NEEDS_REVIEW`.

The retained metadata does not claim marketplace publication, live Codex UI plugin installation, plugin skills, or plugin-bundled MCP servers. Project-scoped hooks are delivered by the installer through `.codex/config.toml`, backed by host fixtures and install smoke, and remain separate from plugin packaging.

## Memory Lifecycle Boundary

Codex receives the TES memory lifecycle as adapter contract text plus project-scoped advisory hooks, not as a write-capable memory runtime.

| Moment | Package stance |
|--------|----------------|
| recall | `/tes-cortex`, Cortex reflection, and runtime recall injection stay no-write unless an explicit memory operation is authorized |
| scope normalization | Deferred to the shared normalizer wave |
| write gate | Durable Cortex writes require explicit parent authorization |
| checkpoint | Deferred to the checkpoint lane wave |
| closeout | Governed by TES oracles, repository Git hooks, and host hook advisories |
| subagent return | Subagents may return evidence only; parent owns memory |

Do not use Codex hooks, memories, or subagent configuration to bypass this boundary. Runtime Cortex may emit `NEEDS_ALIGN`, but it must not write the operating mesh or run `/tes-align` automatically. Parent-owned memory means no durable Cortex writes from a spawned specialist without the parent write gate.

## Why This Shape

Codex uses progressive disclosure for skills:

- Metadata stays visible for discovery.
- `SKILL.md` loads only when the workflow is selected.
- References and scripts load or run only when needed.

The preferred TES shortcuts map to Codex skills. Primary independent commands have visible skills; grouped intents such as `/tes-curate` route through their owning skills. `/tes-update` is a visible skill because update is a commercial user workflow, not a hidden mode of initialization. `tes-goal-maestro` materializes mature SPECs, Super SPECs, PRDs, relational project plans, or accepted execution trees into maestral `/goal` prompts after internal tree, material-diff, material-continuation, semantic negative-grep, sequential ownership, sync-status, and execution-unit fidelity checks. Generated Super SPEC content is written to `GOAL-SUPER-SPEC-*.md` and summarized instead of pasted into chat. Predictive skills such as `/tes-prospect` and `/tes-mine` require explicit invocation and use a cognitive brake. `/tes-bump` is the version governance guard: it auto-activates read-only for commit, release, delivered-behavior, or gate-reported bump conditions, dry-runs target discovery before writing version surfaces, and never commits, tags, pushes, or publishes. They keep the user entrypoint short while delegating real work to deterministic oracles or agent-led codebase exploration:

| Shortcut | Skill |
|----------|-------|
| `/tes-init`, `/tes:init` | `tes-init` |
| `/tes-setup` | `tes-setup` |
| `/tes-update`, `/tes:update` | `tes-update` |
| `/tes-align`, `/tes:align` | `tes-align` |
| `/tes-goal-maestro`, `/tes:goal-maestro` | `tes-goal-maestro` |
| `/tes-prospect`, `/tes:prospect` | `tes-prospect` |
| `/tes-mine`, `/tes:mine` | `tes-mine` |
| `/tes-open-obsidian`, `/tes:open-obsidian` | `tes-open-obsidian` |
| `/tes-cortex`, `/tes:cortex` | `tes-cortex` |
| `/tes-curate`, `/tes:curate` | `tes-cortex` |
| `/tes-mcp`, `/tes:mcp` | `tes-mcp` |
| `/tes-field-reports`, `/tes:field-reports` | `tes-field-reports` |
| `/tes-doctor`, `/tes:doctor` | `tes-doctor` |
| `/tes-adapter`, `/tes:adapter` | `tes-adapter` |
| `/tes-bench`, `/tes:bench` | `tes-bench` |
| `/tes-bump`, `/tes:bump` | `tes-bump` |

This keeps the maturity-aware discipline gates available without bloating every context window.

## Do Not Copy

Do not copy these adapter sources into Codex runtime as authoritative surfaces:

- `src/adapters/claude/**`
- `src/adapters/cursor/**`
- `.DS_Store`

They are tool-specific packages or local OS artifacts. Use them only as source material when maintaining the corresponding tool variant.

## Validation

From this repository:

```bash
python3 scripts/validate_reference_package.py
python3 scripts/context_mesh_plan.py
python3 scripts/codex_plugin_oracle.py --self-test
python3 scripts/materialize_adapter.py codex --check
python3 src/adapters/codex/skills/tes-engineering-discipline/scripts/discipline_oracle.py --self-test
```

In a target Codex repository, add project-specific checks such as tests, typecheck, lint, build, or governance gates. The discipline is successful only when a concrete oracle passes.
