---
tds_id: adapters.materialization
tds_class: adapter
status: active
consumer: maintainers and release operators
source_of_truth: true
evidence_level: L2
tver: 0.2.0
---

# Adapter Materialization

`src/**` is the canonical source. Generated install trees are materialized from
that source and are not edited by hand.

## Commands

| Command | Output |
|---------|--------|
| `npm run materialize:codex` | `dist/adapters/codex/**` |
| `npm run materialize:cursor` | `dist/adapters/cursor/**` |
| `npm run materialize:claude` | `dist/adapters/claude/**` |
| `npm run materialize:all` | All adapter outputs |
| `npm run materialize:check` | Temporary materialization with validation |

`dist/**` is ignored because it is generated. The committed source remains in
`src/**`.

## Output Contracts

| Adapter | Generated install tree |
|---------|------------------------|
| Codex | `AGENTS.md` and `.agents/skills/**` |
| Cursor | `CURSOR.md`, `.cursor/rules/tes-guidelines.mdc`, and `.cursor/rules/tes-runtime-capabilities.mdc` |
| Claude | `CLAUDE.md` and `.claude/skills/**` |

## Gate

`npm run commit:check` runs `scripts/materialize_adapter.py all --check`. That
check builds all adapters in a temporary directory and verifies:

- each expected target path exists;
- Codex skill self-test passes after materialization;
- Cursor keeps `.mdc` frontmatter with `description` and `alwaysApply: true`;
- Cursor separates governance (`tes-guidelines.mdc`) from TES-owned command
  capability routing (`tes-runtime-capabilities.mdc`);
- Claude project skills materialize under `.claude/skills/**`;
- plugin metadata under `src/adapters/**/plugin/**` remains source-only and is
  not materialized into target projects;
- installs and updates remove obsolete plugin/root-skill runtime paths only when
  they are TES-owned/generated or empty, while ambiguous paths are backed up and
  reported as `NEEDS_REVIEW`;
- existing project-owned bootloaders are backed up centrally, replaced by clean
  runtime bootloaders, and recovered semantically while adapter assets install;
- no `src/**` source tree leaks into an install output.

`commit:check` also requires required package files to be staged or already
tracked, so the pre-commit hook cannot pass by reading untracked files that
would be absent from the commit.

If a target tool changes packaging rules, update `src/adapters/<tool>/**`,
`scripts/materialize_adapter.py`, and this document in the same patch.

## Packaging Risk Register

| Adapter | Risk | Rule |
|---------|------|------|
| Codex | Editing installed user/runtime skill instead of source | Edit `src/adapters/codex/**` only; target `.agents/skills/**` is generated output |
| Claude | Project installs omit `.claude/skills/**`, or a `CLAUDE.md` conflict blocks clean install | Project skills must be present, and bootloader conflicts must be backed up, clean-applied, and recovered without blocking runtime assets |
| Cursor | Legacy `.cursorrules` leaks back into the package or project-owned rules block TES commands | Validator blocks `.cursorrules`; runtime capabilities materialize as a separate TES-owned rule |
| All | Generated output becomes perceived source | `dist/**` remains ignored and reproducible |

Hooks, write-capable MCP servers, agent definitions, cloud/background
execution, and marketplace publishing are excluded from the default materialized
output. Read-only Cortex MCP is activated by `scripts/install_mcp.py` as a
project-scoped installer layer, not by adapter materialization.
