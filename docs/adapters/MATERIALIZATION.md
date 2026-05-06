---
tds_id: adapters.materialization
tds_class: adapter
status: active
consumer: maintainers and release operators
source_of_truth: true
evidence_level: L2
tver: 0.1.0
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
| Codex | `AGENTS.md` and `.agents/skills/tilly-engineering-discipline/**` |
| Cursor | `CURSOR.md` and `.cursor/rules/tilly-guidelines.mdc` |
| Claude | `CLAUDE.md`, `.claude-plugin/**`, and `skills/tilly-guidelines/**` |

## Gate

`npm run commit:check` runs `scripts/materialize_adapter.py all --check`. That
check builds all adapters in a temporary directory and verifies:

- each expected target path exists;
- Codex skill self-test passes after materialization;
- Cursor keeps `.mdc` frontmatter with `description` and `alwaysApply: true`;
- Claude plugin metadata points to a root-contained materialized skill;
- no `src/**` source tree leaks into an install output.

`commit:check` also requires required package files to be staged or already
tracked, so the pre-commit hook cannot pass by reading untracked files that
would be absent from the commit.

If a target tool changes packaging rules, update `src/adapters/<tool>/**`,
`scripts/materialize_adapter.py`, and this document in the same patch.

## Packaging Risk Register

| Adapter | Risk | Rule |
|---------|------|------|
| Codex | Editing installed user/runtime skill instead of source | Edit `src/adapters/codex/**` only |
| Claude | Plugin metadata depends on `../` outside the plugin root | Skill paths must be root-relative |
| Cursor | Legacy `.cursorrules` leaks back into the package | Validator blocks `.cursorrules` |
| All | Generated output becomes perceived source | `dist/**` remains ignored and reproducible |

Hooks, MCP servers, agent definitions, cloud/background execution, and
marketplace publishing are excluded from the default materialized output. They
are sensitive operational surfaces and require separate authorization, tests,
and documentation.
