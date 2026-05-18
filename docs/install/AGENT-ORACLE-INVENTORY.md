---
tds_id: install.agent_oracle_inventory
tds_class: adapter
status: active
consumer: installing agents and runtime adapters
source_of_truth: true
evidence_level: L2
tver: 0.1.0
---

# TES Agent Oracle Inventory

Agent-callable oracles. Use the TES package root for package checks, or
`--target` when operating on another project or vault.

## Init / Update / Context

```bash
python3 scripts/tes_init.py --target /path/to/project --yes
python3 scripts/tes_init.py --self-test
python3 scripts/project_context_oracle.py --target /path/to/project && python3 scripts/project_alignment_oracle.py --target /path/to/project
python3 scripts/project_context_oracle.py --self-test && python3 scripts/project_alignment_oracle.py --self-test
python3 scripts/tes_update.py plan --target /path/to/project --json-only
python3 scripts/tes_update.py plan --target /path/to/project --json-only --record-field-report
python3 scripts/tes_update.py --self-test
python3 scripts/tes_legacy_retirement.py plan --target /path/to/project
python3 scripts/tes_legacy_retirement.py apply --target /path/to/project --yes
python3 scripts/tes_legacy_retirement.py audit --target /path/to/project
python3 scripts/tes_legacy_retirement.py --self-test
python3 scripts/root_context.py analyze --target /path/to/project
python3 scripts/root_context.py --self-test
python3 scripts/tes_bundle.py stage --target /path/to/project
python3 scripts/tes_bundle.py backup --target /path/to/project --adapter all --yes
python3 scripts/tes_bundle.py apply --target /path/to/project --mode clean-runtime --backup-id <backup-id> --yes
python3 scripts/tes_bundle.py recover-plan --target /path/to/project --backup-id <backup-id> --apply-safe --yes
python3 scripts/tes_bundle.py restore --target /path/to/project --backup-id <backup-id> --yes
```

`tes_init.py` recertifies package health, scans the target project,
writes `docs/agents/PROJECT-REGISTER.md`, writes
`docs/agents/PROJECT-CONTEXT.md` as the initial project map, creates the
first-pass Obsidian-compatible operating mesh when missing, and stores a
full manifest under `docs/agents/evidence/**`. If a later oracle is
blocked, the run closes as `NEEDS_REVIEW` with evidence instead of
leaving the project uninitialized.

## Field Reports

```bash
python3 scripts/field_reports.py status --target /path/to/project
python3 scripts/field_reports.py drain --target /path/to/project
python3 scripts/field_reports.py disable --target /path/to/project
python3 scripts/field_reports.py enable --target /path/to/project
python3 scripts/field_reports.py --self-test
```

## Cortex

```bash
python3 scripts/cortex.py init --target /path/to/project-or-vault
python3 scripts/cortex.py verify --target /path/to/project-or-vault
python3 scripts/cortex.py audit --target /path/to/project-or-vault
python3 scripts/cortex.py rebuild --target /path/to/project-or-vault
python3 scripts/cortex.py curate-plan --target /path/to/project-or-vault --backend lexical
python3 scripts/cortex.py recall --target /path/to/project-or-vault "query"
python3 scripts/cortex.py read-cell --target /path/to/project-or-vault --cell cell-name
python3 scripts/cortex.py absorb-plan --target /path/to/project-or-vault --source docs/agents/cortex/sources/source.md
python3 scripts/cortex.py learn --target /path/to/project-or-vault --source docs/agents/cortex/sources/source.md
python3 scripts/cortex.py reflect --target /path/to/project-or-vault "decision or lesson"
python3 scripts/cortex.py apply --target /path/to/project-or-vault --cell cell-name --claim "durable claim" --evidence sources/source.md --yes
python3 scripts/cortex.py --self-test
```

## Adapters And MCP Install

```bash
python3 scripts/install_adapter.py --dry-run --target /path/to/project --adapter all
python3 scripts/install_adapter.py --target /path/to/project --adapter codex --yes
python3 scripts/install_adapter.py --target /path/to/project --adapter all --yes
python3 scripts/install_smoke.py --self-test
python3 scripts/install_smoke.py --route mcp
python3 scripts/claude_plugin_oracle.py --self-test
python3 scripts/install_mcp.py --target /path/to/project --adapter codex --yes
python3 scripts/install_mcp.py --target /path/to/project --adapter all --yes
python3 scripts/install_mcp.py --self-test
python3 scripts/cortex_mcp.py --target /path/to/project-or-vault
python3 scripts/cortex_mcp.py --self-test
python3 scripts/materialize_adapter.py all --check
python3 scripts/materialize_adapter.py all
```

## Validation Gates

```bash
python3 scripts/validate_reference_package.py
python3 scripts/validate_reference_package.py --staged-ready
python3 scripts/validate_tds.py
python3 scripts/validate_doc_size.py
python3 scripts/retention_metadata.py --check
python3 scripts/validate_reference_graph.py
python3 scripts/platform_surface_oracle.py --self-test
python3 scripts/adapter_parity_readiness.py
python3 scripts/context_mesh_plan.py
python3 scripts/context_mesh_run.py --backend fixture
python3 scripts/context_mesh_convergence.py
python3 src/adapters/codex/skills/tes-engineering-discipline/scripts/discipline_oracle.py --self-test
```

## npm Wrappers

These wrappers are package-source conveniences for the
`tilly-engineer-skills` repository. They are not target-project guarantees. In
an installed target, first use the installed helpers under `.tes/bin/**` and
the target's own discovered `package.json` scripts. Do not certify an
`npm run ...` command unless that command exists in the current workspace.

```bash
npm run validate
npm run install:dry-run
npm run install:smoke
npm run tes:init -- --target /path/to/project --yes
npm run tes:init:self-test
npm run tes:update -- --target /path/to/project
npm run tes:update:self-test
npm run tes:legacy:plan -- --target /path/to/project
npm run tes:legacy:apply -- --target /path/to/project --yes
npm run tes:legacy:audit -- --target /path/to/project
npm run tes:legacy:self-test
npm run install:adapter -- --target /path/to/project --adapter all --yes
npm run mcp:dry-run -- --target /path/to/project --adapter all
npm run mcp:install -- --target /path/to/project --adapter codex --yes
npm run mcp:install -- --target /path/to/project --adapter all --yes
npm run mcp:self-test
npm run field-reports:self-test
npm run field-reports:status -- --target /path/to/project
npm run field-reports:drain -- --target /path/to/project
npm run claude:plugin:oracle
npm run retention:check
npm run reference:graph
npm run docs:size
npm run tds:validate
npm run cortex:init -- --target /path/to/project-or-vault
npm run cortex:verify -- --target /path/to/project-or-vault
npm run cortex:audit -- --target /path/to/project-or-vault
npm run cortex:rebuild -- --target /path/to/project-or-vault
npm run cortex:curate-plan -- --target /path/to/project-or-vault --backend lexical
npm run cortex:recall -- --target /path/to/project-or-vault "query"
npm run cortex:read-cell -- --target /path/to/project-or-vault --cell cell-name
npm run cortex:absorb-plan -- --target /path/to/project-or-vault --source docs/agents/cortex/sources/source.md
npm run cortex:learn -- --target /path/to/project-or-vault --source docs/agents/cortex/sources/source.md
npm run cortex:reflect -- --target /path/to/project-or-vault "decision or lesson"
npm run cortex:apply -- --target /path/to/project-or-vault --cell cell-name --claim "durable claim" --evidence sources/source.md --yes
npm run cortex:self-test
npm run cortex:mcp:self-test
npm run materialize:all
npm run materialize:codex
npm run materialize:cursor
npm run materialize:claude
npm run materialize:check
npm run benchmark:plan
npm run benchmark:run -- --backend fixture
npm run benchmark:converge
npm run adapter:parity:check
npm run platform:surface:check
npm run oracle:self-test
npm run git:diff-check
npm run commit:check
```

Routing matrix: `docs/install/COMMAND-TRIGGERS.md`.
