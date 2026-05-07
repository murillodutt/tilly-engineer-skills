---
tds_id: architecture.project_structure
tds_class: architecture
status: active
consumer: maintainers and adapter authors
source_of_truth: true
evidence_level: L2
tver: 0.2.0
---

# Project Structure

The repository is a source package, not a target-project install tree.

## Root

Root files are only entrypoints and local project controls:

| Path | Responsibility |
|------|----------------|
| `README.md` | Human entrypoint |
| `AGENTS.md` | Thin repository bootloader for agents working here |
| `package.json` | Local validation commands |
| `.githooks/**` | Local commit gates |
| `scripts/**` | Deterministic package checks |
| `benchmarks/**` | Portable eval data |
| `docs/**` | Method, architecture, and eval explanation |
| `src/**` | Canonical copyable adapter source |
| `dist/**` | Generated adapter output, ignored by Git |
| Git history | Versioning and changelog trail |

## Source

`src/**` is the only canonical home for installable agent material.

| Path | Responsibility |
|------|----------------|
| `src/adapters/codex/AGENTS.md` | Codex target bootloader source |
| `src/adapters/codex/skills/**` | Codex-native skill source |
| `src/adapters/claude/CLAUDE.md` | Claude Code instruction source |
| `src/adapters/claude/plugin/**` | Claude plugin metadata source |
| `src/adapters/claude/skills/**` | Claude Code skill source |
| `src/adapters/cursor/CURSOR.md` | Cursor adapter note |
| `src/adapters/cursor/rules/**` | Cursor project rule source |

## Materialization

`scripts/materialize_adapter.py` turns canonical source into installable target
trees under `dist/adapters/**`:

| Adapter | Materialized shape |
|---------|--------------------|
| Codex | `AGENTS.md` plus `.agents/skills/**` |
| Claude | `CLAUDE.md`, `.claude-plugin/**`, and `skills/**` |
| Cursor | `CURSOR.md` plus `.cursor/rules/**` |

Use `npm run materialize:check` to verify this without writing to `dist/**`.

`scripts/install_mcp.py` is separate from adapter materialization. It activates
the read-only Cortex MCP server in a target project by copying local helpers to
`.tilly/bin/**` and writing project-scoped runtime config.

`scripts/field_reports.py` installs the local Field Reports `pre-push` drain
and records sanitized operational facts under `.tilly/field-reports/**`. That
directory is local transport state, not repository truth.

`scripts/install_smoke.py`, `scripts/claude_plugin_oracle.py`,
`scripts/retention_metadata.py`, and `scripts/validate_reference_graph.py`
provide deterministic closure gates for assisted installation, local Claude
plugin shape, evidence retention policy, and governed link drift.

## Docs

`docs/**` explains the mesh and keeps large context out of the root.

| Path | Responsibility |
|------|----------------|
| `docs/mesh/**` | Method, principles, scorecard |
| `docs/evals/**` | Eval design and examples |
| `docs/governance/**` | Cross-tool authority and alignment rules |
| `docs/adapters/**` | Human adapter guidance |
| `docs/architecture/**` | Repository topology and boundaries |
| `docs/tds/**` | Documentation contract and governed index |

## Structural Locks

- Root hidden tool folders such as `.agents`, `.cursor`, and `.claude-plugin`
  are not canonical source in this repository.
- Target projects may receive hidden adapter folders during installation, but
  this reference package keeps source in `src/**`.
- A new adapter must create one source directory under `src/adapters/<tool>/`
  and one short human guide under `docs/adapters/` only when needed.
- Validation must fail if source leaks back into the root.
- Generated `dist/**` output must be reproducible from `src/**`.
- Do not add `CHANGELOG.md`; commit history is the changelog.
