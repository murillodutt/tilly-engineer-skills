---
tds_id: architecture.tes_naming_migration_catalog
tds_class: architecture
status: active
consumer: maintainers, installer authors, adapter authors, and installing agents
source_of_truth: true
evidence_level: L2
tver: 0.1.1
---

# TES Naming Migration Catalog

## Decision

Tilly Engineer Skills keeps its formal package name, but its operational
namespace moves to the acronym `TES`.

The main Tilly project owns the generic `Tilly` runtime surface. This reference
package must not keep active commands, skills, scripts, MCP server IDs, rules, or
installed helper names that collide with that surface.

The migration target is simple:

- Product prose may say `Tilly Engineer Skills`.
- Operational IDs must use `TES`, `tes`, or `tes-*`.
- Active prompt commands must use `/tes:*`.
- Installed runtime files must avoid `tilly-*`, `tilly_*.py`, and `.tilly/**`
  unless a specific migration bridge declares a temporary compatibility reason.

## Why This Exists

The current package exposes many assets as `tilly-*` even though another project
named Tilly is the primary product. Agent runtimes list skills and commands from
different projects in the same context picker. When both projects publish
`Tilly Init`, `Tilly Cortex`, `Tilly MCP`, or `/tilly:init`, users and agents can
select the wrong behavior.

This is not a cosmetic issue. It is a routing and authority issue.

## Naming Rules

- `Tilly Engineer Skills` remains allowed as the human-readable package name.
- `TES` is the user-facing acronym for commands, skills, scripts, rules, and
  installed helper surfaces.
- `tes` is the lowercase executable namespace.
- `tes-*` is the skill, MCP server, issue template, and installed asset prefix.
- `/tes:*` is the only active command prompt namespace.
- `/tilly:*` must not appear in active skill descriptions after migration.
- Historical evidence may keep old names when it records past behavior.
- Migration code may detect old names, but it must not present them as the
  current route.

## Catalog Of Required Renames

### Prompt Commands

The active command prompts move from `/tilly:*` to `/tes:*`.

- `/tilly:init` becomes `/tes:init`.
- `/tilly:update` becomes `/tes:update`.
- `/tilly:cortex` becomes `/tes:cortex`.
- `/tilly:recall` becomes `/tes:recall`.
- `/tilly:learn` becomes `/tes:learn`.
- `/tilly:reflect` becomes `/tes:reflect`.
- `/tilly:curate` becomes `/tes:curate`.
- `/tilly:mcp` becomes `/tes:mcp`.
- `/tilly:field-reports` becomes `/tes:field-reports`.
- `/tilly:doctor` becomes `/tes:doctor`.
- `/tilly:check` becomes `/tes:check`.
- `/tilly:certify` becomes `/tes:certify`.
- `/tilly:adapter` becomes `/tes:adapter`.
- `/tilly:bench` becomes `/tes:bench`.

Natural language triggers must also stop saying `Atualizar a Tilly` as the
default phrase for this package. The current phrase becomes `Atualizar TES` or
`Atualizar Tilly Engineer Skills`.

### NPM Commands

The package scripts that currently use the `tilly:` command namespace must move
to `tes:`.

- `tilly:init` becomes `tes:init`.
- `tilly:init:self-test` becomes `tes:init:self-test`.
- `tilly:update` becomes `tes:update`.
- `tilly:update:self-test` becomes `tes:update:self-test`.

Scripts that already use neutral domain namespaces, such as `cortex:*`,
`mcp:*`, `field-reports:*`, `materialize:*`, and `adapter:*`, may remain unless
their implementation exposes a `tilly-*` runtime name.

### Python Scripts

Top-level script filenames that expose the old package namespace must move to
`tes_*`.

- `scripts/tilly_init.py` becomes `scripts/tes_init.py`.
- `scripts/tilly_update.py` becomes `scripts/tes_update.py`.

Installed helper paths must follow the same rule.

- `.tilly/bin/tilly_update.py` becomes `.tes/bin/tes_update.py`.
- `.tilly/bin/field_reports.py` becomes `.tes/bin/field_reports.py`.
- `.tilly/bin/cortex.py` becomes `.tes/bin/cortex.py`.
- `.tilly/bin/cortex_mcp.py` becomes `.tes/bin/cortex_mcp.py`.
- `.tilly/bin/root_context.py` becomes `.tes/bin/root_context.py`.

Existing installed projects need a one-way migration plan that removes stale
`.tilly/bin/**` helpers after `.tes/bin/**` is certified.

### Local Runtime Directories

The hidden local runtime root must move from `.tilly/**` to `.tes/**`.

- `.tilly/bin/**` becomes `.tes/bin/**`.
- `.tilly/field-reports/**` becomes `.tes/field-reports/**`.
- `.tilly/cortex/recall.sqlite` becomes `.tes/cortex/recall.sqlite`.
- `.tilly/cortex/semantic.sqlite` becomes `.tes/cortex/semantic.sqlite`.

This does not change the Cortex memory source of truth. The memory still lives
in versioned Markdown artifacts under `docs/agents/cortex/**` in an installed
project. SQLite remains a derived cache.

### Codex Skills

Codex skill directory names and frontmatter names must move to `tes-*`.

- `tilly-engineering-discipline` becomes `tes-engineering-discipline`.
- `tilly-init` becomes `tes-init`.
- `tilly-cortex` becomes `tes-cortex`.
- `tilly-mcp` becomes `tes-mcp`.
- `tilly-doctor` becomes `tes-doctor`.
- `tilly-adapter` becomes `tes-adapter`.
- `tilly-bench` becomes `tes-bench`.

Descriptions must name TES command prompts and must not advertise `/tilly:*`.
Skill display names should use `TES Init`, `TES Cortex`, `TES MCP`, and similar
forms so the runtime picker separates them from the main Tilly project.

### Claude Skills And Plugin Surface

Claude skill directory names and frontmatter names must also move to `tes-*`.

- `tilly-guidelines` becomes `tes-guidelines`.
- `tilly-init` becomes `tes-init`.
- `tilly-cortex` becomes `tes-cortex`.
- `tilly-mcp` becomes `tes-mcp`.
- `tilly-doctor` becomes `tes-doctor`.
- `tilly-adapter` becomes `tes-adapter`.
- `tilly-bench` becomes `tes-bench`.

The Claude plugin and marketplace metadata may keep the formal package name
where it identifies the repository, but skill names exposed to the runtime must
use TES.

### Cursor Rules

Cursor rule files that expose the old namespace must move to TES naming.

- `src/adapters/cursor/rules/tilly-guidelines.mdc` becomes
  `src/adapters/cursor/rules/tes-guidelines.mdc`.

Installed Cursor rules must also use the TES name. If a project already has a
project-owned rule with old Tilly content, the installer must run the root
context structure gate before replacing or preserving it.

### MCP Surface

The Cortex MCP server must move to the TES namespace.

- MCP server ID `tilly-cortex` becomes `tes-cortex`.
- MCP package name `tilly-cortex-mcp` becomes `tes-cortex-mcp`.
- Codex config section `mcp_servers.tilly-cortex` becomes
  `mcp_servers.tes-cortex`.
- Claude and Cursor MCP configs must use `tes-cortex` as the server key.
- Tool titles should say `TES Cortex MCP`.

The installer may detect and remove old `tilly-cortex` configs only after the
new `tes-cortex` config passes the MCP self-test.

### Field Reports

Field Reports must become a TES operational surface.

- `Tilly Field Reports` becomes `TES Field Reports`.
- `.github/ISSUE_TEMPLATE/tilly-field-report.yml` becomes
  `.github/ISSUE_TEMPLATE/tes-field-report.yml`.
- Schema marker `tilly-field-report@1` becomes `tes-field-report@1`.
- Issue titles and labels should use `TES Field Report`.

The GitHub destination may remain `murillodutt/tilly-engineer-skills` because it
is the package repository. The payload must not expose old runtime command
names as current commands.

### Installer And Manual

The assisted installer, command trigger guide, install docs, and user manual
must present TES commands as the only active prompt surface.

Required updates:

- `docs/install/ASSISTED-CONTEXT-INSTALLER.prompt.md`
- `docs/install/COMMAND-TRIGGERS.md`
- `docs/install/INSTALL.md`
- `docs/install/USER-MANUAL.html`
- `docs/install/MINI-PROMPT.md`
- navigation prompts under `docs/install/navigation/**`
- `README.md`
- `AGENTS.md`

The manual may include one short migration note explaining that earlier
installations used `/tilly:*`, but it must not teach users to keep using old
commands.

### Validators And Oracles

All gates that hard-code old paths or scripts must move to TES.

Required updates include:

- `scripts/validate_reference_package.py`
- `scripts/install_smoke.py`
- `scripts/install_adapter.py`
- `scripts/install_mcp.py`
- `scripts/platform_surface_oracle.py`
- `scripts/materialize_adapter.py`
- `scripts/claude_plugin_oracle.py`
- `scripts/root_context.py`
- package `commit:check`

The validation suite must include a namespace oracle that fails if active
runtime surfaces still expose `tilly-*`, `tilly_`, `.tilly/**`, or `/tilly:*`.

## Compatibility Policy

Compatibility exists only to migrate old installations, not to keep both
namespaces alive.

Allowed temporary behavior:

- Detect old `tilly-*` installed assets.
- Create backups before replacing project-owned bootloaders.
- Copy state from `.tilly/**` to `.tes/**` when the data is local runtime state.
- Remove stale old MCP configs after the TES MCP config passes.
- Record the migration in installation evidence.

Forbidden behavior:

- Install both `tilly-*` and `tes-*` skills.
- Keep `/tilly:*` in active skill descriptions.
- Keep `tilly-cortex` as an active MCP server.
- Keep `.tilly/bin/**` as the active helper runtime.
- Present old commands as equivalent current commands in the user manual.

## Source Boundaries

This migration must not rename everything that contains the word Tilly.

Keep these names unless a later decision says otherwise:

- Repository name `tilly-engineer-skills`.
- Formal product name `Tilly Engineer Skills`.
- GitHub destination repository `murillodutt/tilly-engineer-skills`.
- Historical evidence and past reports.
- Human prose that clearly refers to the product name instead of an operational
  command or runtime ID.

## Implementation Order

1. Add this catalog and certify the blast radius.
2. Add `scripts/tes_namespace.py` as a no-write namespace oracle that reports
   current violations without rewriting. Its `inventory` mode must cross-check
   paths and content with `find`, `rg --line-number --column`, and recursive
   `grep` before any apply-style migration is considered.
3. Rename source skills, scripts, rules, MCP IDs, and package commands.
4. Update materializers and installers to emit TES surfaces.
5. Add migration logic for existing `.tilly/**`, `tilly-*`, and `tilly-cortex`
   installations.
6. Update docs and manual so TES is the only active user command surface.
7. Run install/update probes in clean and already-meshed projects.
8. Remove stale compatibility bridges once real installations converge.

## Required Gates

The migration is not certified until these checks pass:

- `python3 scripts/tes_namespace.py report`.
- `python3 scripts/tes_namespace.py inventory`.
- `python3 scripts/tes_namespace.py audit`.
- No active skill directory under `src/adapters/**/skills/tilly-*`.
- No active skill frontmatter name beginning with `tilly-`.
- No active command prompt `/tilly:*` in current installer, manual, rules, or
  skill descriptions.
- No installed helper path `.tilly/bin/**` in generated configs.
- No MCP server key `tilly-cortex` in generated configs.
- `python3 scripts/validate_reference_package.py`.
- `python3 scripts/validate_tds.py`.
- `python3 scripts/install_smoke.py --self-test`.
- `python3 scripts/install_mcp.py --self-test`.
- `python3 scripts/platform_surface_oracle.py --self-test`.
- `npm run commit:check`.

## Open Decisions

These decisions should be closed before code migration starts:

- Whether the Claude plugin package ID should remain the repository-oriented
  name or move to a TES-specific runtime ID.
- Whether old `/tilly:*` prompts should be recognized only by the installer for
  one migration release, or rejected immediately to avoid ambiguity.
- Whether installed `.tilly/field-reports/outbox.jsonl` should be moved to
  `.tes/field-reports/outbox.jsonl` automatically or left in place with a final
  drain attempt before migration.
- Whether GitHub issue labels should be renamed immediately or dual-labeled
  during the transition.

## Certification Claim

This catalog does not implement the rename. It defines the required migration
surface and the certification boundary. The package is not TES-namespaced until
the required gates pass and installed project probes show no active `tilly-*`
runtime surfaces.
