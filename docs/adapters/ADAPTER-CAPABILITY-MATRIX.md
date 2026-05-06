---
tds_id: adapters.capability_matrix
tds_class: adapter
status: active
consumer: maintainers and adapter authors
source_of_truth: true
evidence_level: L3
tver: 0.3.0
---

# Adapter Capability Matrix

Adapters are aligned by behavioral contract and evidence, not by identical
text. Different tool capabilities are expected. Drift exists when equivalent
contract gates produce divergent decisions, or when an adapter claims a
capability without evidence.

## Core Rule

One contract, three adapter surfaces, one parity gate.

```text
Core Contract
  -> Adapter Materialization
  -> Adapter Execution
  -> Adapter Evidence
  -> Cross-Adapter Parity Report
```

The neutral contract is `docs/mesh/CONTRACT-MANIFEST.yml`.

## Platform Surface Matrix

| Surface | Codex | Claude | Cursor |
|---------|-------|--------|--------|
| Agent bootloader | `AGENTS.md` | `CLAUDE.md` | `CURSOR.md` plus project rules |
| Always-on rules | `AGENTS.md` project guidance | `CLAUDE.md` project guidance | `.cursor/rules/*.mdc` |
| Skill | `.agents/skills/**` | `skills/**` | no native equivalent |
| Plugin | native platform support; deferred by Tilly | `.claude-plugin/**` certified locally | no native package claimed |
| Hooks | native platform support; Tilly uses Git hook only | native platform support; Tilly plugin hook deferred | Git hook only |
| MCP | project `.codex/config.toml` | project `.mcp.json` | project `.cursor/mcp.json` |
| Behavior backend | `codex-cli` retained v1 scope | `claude-cli` retained v1 scope | deferred; no clean non-interactive route certified |

Capability difference is not drift. Decision divergence under the same
behavioral gate is drift.

## Documentation Baseline

The platform-surface oracle tracks official documentation URLs as evidence
inputs:

| Platform | Relevant docs |
|----------|---------------|
| Codex | `https://developers.openai.com/codex/guides/agents-md`, `https://developers.openai.com/codex/skills`, `https://developers.openai.com/codex/plugins`, `https://developers.openai.com/codex/hooks`, `https://developers.openai.com/codex/rules`, `https://developers.openai.com/codex/mcp` |
| Claude | `https://code.claude.com/docs/en/features-overview`, `https://code.claude.com/docs/en/skills`, `https://code.claude.com/docs/en/plugins-reference`, `https://code.claude.com/docs/en/hooks` |
| Cursor | `https://docs.cursor.com/context/rules`, `https://docs.cursor.com/context/model-context-protocol` |
| MCP | `https://modelcontextprotocol.io/specification/latest` |

## Surface Oracle

Run:

```bash
npm run platform:surface:check
```

This certifies local package shape against the platform-surface contract:

- Codex agent, skill, MCP install config, and Git-governed hook surface.
- Claude bootloader, skill, plugin manifests, MCP install config, and plugin
  non-claims.
- Cursor bootloader, `.cursor/rules/*.mdc`, MCP install config, and legacy
  `.cursorrules` exclusion through materialization.
- Shared pre-commit hook for document size and Cortex reflection.

The oracle does not claim live marketplace publication, live IDE UI behavior,
or platform hooks that are intentionally not packaged.

## Certification Implication

| Adapter | Current certifiable level | Reason |
|---------|---------------------------|--------|
| Codex | structural plus retained behavior evidence | Materialization, platform-surface oracle, and `codex-cli` v1 evidence exist for the retained run/hash/backend/prompt contract. |
| Claude | structural plus retained behavior evidence | Materialization and `claude-cli` v1 evidence exist for the retained run/hash/backend/model. |
| Cursor | structural | Materialization and installer smoke can be checked; behavior remains explicitly deferred until a non-interactive backend exists. |

## NO-GO

- Do not create separate contracts per adapter.
- Do not copy text between adapters to manufacture parity.
- Do not declare Cursor behavioral parity without an executor.
- Do not declare Codex or Claude universal behavior from one retained backend
  run; evidence is scoped to the retained run/hash/backend/model or prompt
  contract.
- Do not block Claude behavior certification waiting for symmetric adapter
  capability.
- Do not claim Codex plugin packaging until a `.codex-plugin/plugin.json`
  package exists and has its own oracle.
- Do not claim platform lifecycle hooks just because the repository Git hook is
  active.
