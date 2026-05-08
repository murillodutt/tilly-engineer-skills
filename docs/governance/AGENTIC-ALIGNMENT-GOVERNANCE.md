---
tds_id: governance.agentic_alignment
tds_class: governance
status: active
consumer: maintainers, adapter authors, and release operators
source_of_truth: true
evidence_level: L2
tver: 0.5.0
---

# Agentic Alignment Governance

This document governs how the Tilly Engineer Skills package stays aligned
across Codex, Claude Code, and Cursor without pretending the tools share the
same native contract.

The common truth is behavioral. The package format is adapter-specific.

Adapter alignment requires converged behavior, not matching prose. Codex,
Claude Code, and Cursor may materialize different files and affordances; they
are aligned only when retained evidence shows equivalent decisions under the
shared contract.

## Official Source Map

| Surface | Codex | Claude Code | Cursor |
|---------|-------|-------------|--------|
| Base instructions | [AGENTS.md](https://developers.openai.com/codex/guides/agents-md) | [Memory and CLAUDE.md](https://code.claude.com/docs/en/memory) | [Rules and AGENTS.md](https://docs.cursor.com/en/context/rules) |
| Reusable workflows | [Skills](https://developers.openai.com/codex/skills) | [Skills](https://code.claude.com/docs/en/skills) | Project rules, commands, and agent mode |
| Distribution | [Plugins](https://developers.openai.com/codex/plugins/build) | [Plugins](https://code.claude.com/docs/en/plugins) | Versioned project files |
| Hooks | [Hooks](https://developers.openai.com/codex/hooks) | [Hooks](https://code.claude.com/docs/en/hooks) | [Hooks](https://cursor.com/docs/hooks) |
| MCP | [MCP](https://developers.openai.com/codex/mcp) | [MCP](https://code.claude.com/docs/en/mcp) | [MCP](https://docs.cursor.com/en/tools/mcp) |
| Agents | [Subagents](https://developers.openai.com/codex/concepts/subagents) | [Subagents](https://code.claude.com/docs/en/sub-agents) | Agent, CLI, and background agents |

If any official source changes the packaging model, update this document, the
affected adapter guide, the materializer, and the TDS index in the same patch.

## Governance Layers

| Layer | Source | Rule |
|-------|--------|------|
| Behavioral truth | `docs/mesh/PRINCIPLES.md` | Defines the four gates and success formula |
| Evidence convergence | `docs/mesh/CONTEXT-MESH-CONVERGENCE.md` | Defines when context becomes contract |
| Documentation contract | `docs/tds/TDS-SPEC.md` | Defines classes, index rules, and evidence levels |
| Cross-tool governance | This document | Defines alignment, boundaries, and no-go rules |
| Adapter guidance | `docs/adapters/**` | Explains tool-specific installation and risks |
| Canonical source | `src/adapters/**` | Only source for installable adapter files |
| Generated output | `dist/adapters/**` | Reproducible output, ignored by Git |
| Installed runtime | Target repo or user cache | Never edited as package truth |

## Alignment Matrix

| Need | Codex Adapter | Claude Adapter | Cursor Adapter | Governance Decision |
|------|---------------|----------------|----------------|---------------------|
| Durable base guidance | `AGENTS.md` | `CLAUDE.md` | `.cursor/rules/*.mdc`; `AGENTS.md` only by explicit choice | Do not force one filename across all tools |
| Reusable discipline workflow | Skill in `.agents/skills/**` | Project skill in `.claude/skills/**`; plugin copy in `skills/**` | Always-on project rule | Preserve behavioral parity, not packaging parity |
| Distribution | Future `.codex-plugin/**` if needed | `.claude-plugin/**` plus plugin root skills | Repository files | Distribution is adapter-specific |
| Hooks | Sensitive, feature-gated | Sensitive enforcement surface | Sensitive agent-loop surface | Excluded from default package until separately authorized |
| MCP | External capability layer | External capability layer | External capability layer | Read-only Cortex MCP is installer-gated; other MCP requires decision and tests |
| Agents and subagents | Powerful specialist layer | Powerful specialist layer | Agent/background execution layer | Excluded by default; requires permission, tools, and oracle contract |
| Commands | Shared `/tes-*` trigger vocabulary plus `/tes:*` aliases | Shared `/tes-*` trigger vocabulary plus `/tes:*` aliases | Shared `/tes-*` trigger vocabulary plus `/tes:*` aliases | Keep entry vocabulary consistent while materialization stays adapter-specific |

## Authority Rules

1. `docs/mesh/PRINCIPLES.md` is the tool-neutral behavioral source of truth.
2. Context becomes project truth only through retained convergence evidence,
   not by matching wording across adapters.
3. `src/adapters/**` is the only installable source tree.
4. Tool-specific files in `dist/**`, target repos, or user caches are
   materialized outputs, not canonical package sources.
5. `AGENTS.md`, `CLAUDE.md`, and Cursor rules are guidance layers. Enforcement
   belongs to deterministic validators, repository hooks, settings, or
   tool-native hook systems when explicitly adopted.
6. Do not create false symmetry. If a tool does not have Codex-style skills,
   Claude-style plugins, or Cursor-style rules, do not invent those names for
   the package.

## Decision Gates

| Change | Required Gate |
|--------|---------------|
| New adapter file | TDS index entry, materializer rule, validation check |
| New official tool surface | Official source link, risk classification, adapter guide update |
| New hook | Security review, explicit command path, denial behavior, local test |
| New MCP server | Scope, auth model, allowed tools, output budget, lifecycle test |
| New agent or subagent | Tool allowlist, invocation rule, max-turn or stop condition, oracle |
| New distribution format | Installer proof or documented uncertified status |

## Adapter Obligations

| Adapter | Must Preserve | Must Not Do |
|---------|---------------|-------------|
| Codex | Thin `AGENTS.md`, repo skill in `.agents/skills/**`, progressive disclosure | Treat plugin cache or user runtime as source |
| Claude | Short `CLAUDE.md`, project skills in `.claude/skills/**`, root-contained plugin skills, read-only Cortex MCP only through project config | Use `../` skill paths inside plugin metadata or make Claude-only trigger names |
| Cursor | `.cursor/rules/*.mdc`, `alwaysApply: true` for the base discipline, no `.cursorrules` | Treat `CURSOR.md` as the primary operative context |

## Current Certification State

| Area | State | Evidence |
|------|-------|----------|
| Source layout | Certified locally | `scripts/validate_reference_package.py` |
| TDS index | Certified locally | `scripts/validate_tds.py` |
| Materialization | Certified locally | `scripts/materialize_adapter.py all --check` |
| Codex skill oracle | Certified locally | `discipline_oracle.py --self-test` |
| Cursor rule shape | Certified locally | Materializer frontmatter checks |
| Claude plugin install | Certified locally | `scripts/claude_plugin_oracle.py --self-test` |
| Cortex MCP activation | Certified locally | `scripts/install_mcp.py --self-test` |
| Assisted install routes | Certified locally | `scripts/install_smoke.py --self-test` |
| Retention metadata policy | Certified locally | `scripts/retention_metadata.py --check` |
| Reference graph | Certified locally | `scripts/validate_reference_graph.py` |
| Document size budgets | Certified locally | `scripts/validate_doc_size.py` |
| Cortex reflection | Certified locally | `scripts/cortex.py reflect` and read-only `cortex_reflect` |
| Cortex semantic curation | Certified locally | `scripts/cortex.py curate-plan` and read-only `cortex_curate_plan` |

## No-Go Rules

- Do not add `.cursorrules`; it is a legacy Cursor surface.
- Do not add `CHANGELOG.md`; Git history is the changelog.
- Do not publish or install plugins from this package without an explicit
  private decision.
- Do not add target-project hooks, write-capable MCP, or agents to the default
  installer package because they are operational surfaces, not passive
  documentation.
- Do not use commit-time reflection or curation to write or delete Cortex
  content automatically.
- Read-only Cortex MCP is allowed only as project-scoped installer activation
  with lifecycle tests and no global config mutation.
- Do not duplicate the same behavioral prose in every layer. Keep the common
  contract small and route detail to the proper adapter.
