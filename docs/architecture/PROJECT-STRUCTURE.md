---
tds_id: architecture.project_structure
tds_class: architecture
status: active
consumer: maintainers and adapter authors
source_of_truth: true
evidence_level: L2
tver: 0.2.5
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
| `scripts/**` | Deterministic oracles and package helpers |
| `benchmarks/**` | Portable eval data |
| `docs/**` | Method, architecture, and eval explanation |
| `src/**` | Canonical copyable adapter source |
| `dist/**` | Generated adapter output, ignored by Git |
| `docs/dist/**` | Versioned public installer bundles served by GitHub Pages |
| Git history | Versioning and changelog trail |

`scripts/**` is classified by consumer, not by directory. Validator-only
scripts are maintainer gates. Installer, Cortex, MCP, Field Reports, and adapter
scripts are delivered behavior when adopters receive, invoke, or certify them.
Bootstrap script entrypoints live under `scripts/bootstrap/**`; installer
wrappers do not belong in the repository root.

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
| Claude | `CLAUDE.md`, `.claude/skills/**`, `.claude-plugin/**`, and `skills/**` |
| Cursor | `CURSOR.md` plus `.cursor/rules/**` |

Use `npm run materialize:check` to verify this without writing to `dist/**`.

`docs/dist/<version>/` is the exception to the ignored `dist/**` rule. It holds
the public TES ZIP, `.sha256`, and `index.json` used by installer staging.

`scripts/bootstrap/install.sh` and `scripts/bootstrap/install.ps1` are the
canonical shell entrypoints for mechanical adapter installation. Root
`install.sh` and `install.ps1` are intentionally absent so the root remains
human-facing rather than a script surface.

`scripts/install_mcp.py` is separate from adapter materialization. It activates
the read-only Cortex MCP server in a target project by copying local helpers to
`.tes/bin/**` and writing project-scoped runtime config.

`scripts/tes_update.py` plans low-friction updates by comparing installed and
cloud package versions, detecting applied IDE surfaces, and recommending the
route behind `/tes-update` and its `/tes:update` compatibility alias.

`scripts/tes_init.py` initializes and recertifies a target project. It writes
`docs/agents/PROJECT-REGISTER.md` and `docs/agents/PROJECT-CONTEXT.md` before
slower gates finish, so blocked gates leave auditable evidence instead of an
uninitialized runtime.

`scripts/project_context_oracle.py` certifies that the generated
`PROJECT-CONTEXT.md` is useful rather than decorative: it checks identity,
manifest evidence, territories, source anchors, quality scripts, explicit
unknowns, and absence of bulk-copied source code.

`scripts/tes_legacy_retirement.py` is the closed-catalog cleanup gate for
updates. It removes known old runtime assets, migrates Field Reports state,
archives legacy retrofit records, and preserves project context.

`scripts/root_context.py` scans root runtime files such as `AGENTS.md`,
`CLAUDE.md`, and Cursor rules before overwrite. Project-owned instructions must
be migrated into `docs/agents/**` or evidence first.

`scripts/field_reports.py` installs the local Field Reports `pre-push` drain
and records sanitized operational facts under `.tes/field-reports/**`. That
directory is local transport state, not repository truth.

`.github/ISSUE_TEMPLATE/tes-field-report.yml` and
`.github/workflows/field-report-governance.yml` govern the central GitHub
receiver for those reports. The local oracle is
`scripts/field_reports_github_oracle.py`. GitHub automation readiness,
including Dependabot ecosystem and directory sanity when
`.github/dependabot.yml` exists, is checked by
`scripts/github_readiness_oracle.py`.

`scripts/install_smoke.py`, `scripts/claude_plugin_oracle.py`,
`scripts/github_readiness_oracle.py`, `scripts/retention_metadata.py`, and
`scripts/validate_reference_graph.py` provide deterministic closure gates for
assisted installation, local Claude plugin shape, GitHub automation readiness,
portable project-context fixtures, evidence retention policy, and governed link
drift.

## Docs

`docs/**` explains the mesh and keeps large context out of the root.

| Path | Responsibility |
|------|----------------|
| `docs/mesh/**` | Method, principles, scorecard |
| `docs/evals/**` | Eval design and examples |
| `docs/governance/**` | Cross-tool authority and alignment rules |
| `docs/governance/MAINTAINER-CORRELATION-RULE.md` | Local maintainer map for package edits, not installed project context |
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
- Generated `dist/**` output must be reproducible from `src/**`; versioned
  public bundles under `docs/dist/**` must pass `public_bundle_oracle.py`.
- Do not add `CHANGELOG.md`; commit history is the changelog.
