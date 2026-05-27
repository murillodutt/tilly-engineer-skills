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

`src/adapters/**` is the only local canonical adapter source. Generated install
trees are materialized from that source, are not edited by hand, and are purged
after inspection.

## Commands

| Command | Output |
|---------|--------|
| `npm run materialize:codex` | Temporary inspection output at `dist/adapters/codex/**`; purge after use |
| `npm run materialize:cursor` | Temporary inspection output at `dist/adapters/cursor/**`; purge after use |
| `npm run materialize:claude` | Temporary inspection output at `dist/adapters/claude/**`; purge after use |
| `npm run materialize:all` | Temporary inspection output for all adapters; purge after use |
| `npm run materialize:check` | Temporary materialization with validation |

`dist/**` is ignored because it is generated. The committed source remains in
`src/adapters/**`. Local package validation fails if `dist/adapters/**` remains
after an inspection run.

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
- no generated `dist/adapters/**` inspection output remains in the local source
  package after tests or inspection.

`commit:check` also requires required package files to be staged or already
tracked, so the pre-commit hook cannot pass by reading untracked files that
would be absent from the commit.

## Mantra Gate Ownership

Mantra Gate behavior is skill-owned, not bootloader-owned:

- Codex `AGENTS.md` routes to `.agents/skills/tes-engineering-discipline/SKILL.md`.
- Claude `CLAUDE.md` routes to `.claude/skills/tes-guidelines/SKILL.md`.
- Cursor `.cursor/rules/tes-guidelines.mdc` carries the active rule directly.

Materialization checks reject active bootloaders or rules that reintroduce
retired project-local gate markers or duplicate the gate protocol in the
bootloader. Historical evidence may preserve retired text; active runtime
surfaces may not.

If a target tool changes packaging rules, update `src/adapters/<tool>/**`,
`scripts/materialize_adapter.py`, and this document in the same patch.

## Packaging Risk Register

| Adapter | Risk | Rule |
|---------|------|------|
| Codex | Editing installed user/runtime skill instead of source | Edit `src/adapters/codex/**` only; target `.agents/skills/**` is generated output |
| Claude | Project installs omit `.claude/skills/**`, or a `CLAUDE.md` conflict blocks clean install | Project skills must be present, and bootloader conflicts must be backed up, clean-applied, and recovered without blocking runtime assets |
| Cursor | Legacy `.cursorrules` leaks back into the package or project-owned rules block TES commands | Validator blocks `.cursorrules`; runtime capabilities materialize as a separate TES-owned rule |
| All | Generated output becomes perceived source | `dist/adapters/**` is temporary inspection output and validation requires purging it after use |

Hooks, ungoverned write-capable MCP servers, agent definitions,
cloud/background execution, and marketplace publishing are excluded from the
default materialized output. Cortex MCP is activated by `scripts/install_mcp.py`
as a project-scoped installer layer, not by adapter materialization; governed
remember requires explicit ADR 0002 opt-in.
