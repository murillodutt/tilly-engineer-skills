# Tilly Engineer Skills

Mesh a project with portable agent governance for Codex, Claude Code, and
Cursor.

Tilly Engineer Skills helps coding agents work with less ambiguity, less
overbuilding, fewer drive-by edits, stronger memory, and clearer proof before
they claim a task is done.

Version: `0.3.33`

License: MIT

## Start Here

Open the user manual:

```text
docs/install/USER-MANUAL.html
```

Then open your target project in Codex, Claude Code, or Cursor and type an
intent in the agent window:

```text
/tes:init
```

Natural command/prompts are accepted too:

```text
tes init
TES, initialize this project.
TES, inicialize este projeto.
Install Tilly here.
Update and recertify TES.
/tes:update
Atualizar TES.
```

These are not shell commands. The active agent is the executor. It reads the
assisted installer contract, protects the Git state, meshes the project, runs
available local oracles, and returns a compact certification report.
For already meshed projects, `/tes:update` checks the installed version
against the cloud package version, detects applied IDE surfaces, and recommends
the smallest safe route.
Before new assets are copied, `tes_legacy_retirement.py` removes known old
runtime surfaces, migrates Field Reports state, and blocks unknown legacy.
Before root bootloaders are overwritten, Tilly scans `AGENTS.md`, `CLAUDE.md`
and Cursor rules for project-owned context and requires migration first.

If the command/prompt router is not available yet, paste this fallback prompt
into the agent window:

```text
Mesh Tilly Engineer Skills into this project as an assisted context mesh, not
as blind file copying.

Read and follow this raw installer spec:
https://raw.githubusercontent.com/murillodutt/tilly-engineer-skills/main/docs/install/ASSISTED-CONTEXT-INSTALLER.prompt.md

Run in quiet installer mode. Detect the current IDE/runtime, classify this
project as new, existing, or meshed, run Step Zero before edits, preserve local
governance, create or update docs/agents/** and docs/agents/cortex/**, keep
runtime bootloaders thin, activate read-only Cortex MCP for the selected route,
and finish with the required certification report and Git rollback path.
```

## What Tilly Meshes

Tilly does not copy a pile of prompt files into a project. It creates a local
context mesh.

Project truth lives in `docs/agents/**`. Runtime files such as `AGENTS.md`,
`CLAUDE.md`, Cursor rules, skills, plugin metadata, hooks, and MCP config stay
thin and route back to that mesh.

Cortex is the compiled memory layer under `docs/agents/cortex/**`. Its memory
lives in versioned Markdown artifacts: `sources/**`, `cells/**`, `MAP.md`,
`TRAIL.md`, `LINKS.md`, and `CONTRACT.md`. SQLite files under `.tes/cortex/**`
are derived indexes only. They are rebuildable and never the memory.

Obsidian is a visual surface, not a dependency. Tilly keeps Cortex readable in
Obsidian without creating or editing `.obsidian/**`.

MCP is read-only in this package. It gives agents access to Cortex recall,
audit, read, reflection, and curation tools. It is not memory and not the
installer.

Field Reports are active by default. They send only sanitized operational facts
to GitHub issues during push, never code, diffs, prompts, file contents,
secrets, personal data, private paths, raw remotes, branch names, or stack
traces. The GitHub receiver has a template, schema oracle, labels, and a
quarantine workflow. Opt-out and re-enable prompts live in the user manual.

## Execution Model

The executor is always the active coding agent inside the current context
window. Python scripts and `npm run ...` entries are deterministic oracles the
agent may invoke when local tools are available.

Skills, rules, bootloaders, and adapter files are routing surfaces. Hooks are
local Git gates. Git remains the project history. Tilly does not push, amend,
tag, publish, install dependencies, change remotes, or overwrite project
governance without explicit user approval.

When a target is a Git repo, Tilly protects local-only runtime artifacts through
`.git/info/exclude`: rollback backups, Python bytecode, Field Reports transport,
and Cortex SQLite caches stay out of normal staging. Installed helper scripts
under `.tes/bin/*.py` are not ignored because they are the project-scoped
runtime surface.

The standard intent surface is intentionally small:

- `/tes:init` or an init command/prompt: mesh, update, audit, or recertify.
- `/tes:update` or `Atualizar TES`: detect version drift and update route.
- `/tes:cortex`: query, inspect, audit, rebuild, learn, reflect, or apply
  Cortex memory.
- `/tes:curate`: run no-write Cortex semantic curation.
- `/tes:mcp`: activate or verify read-only Cortex MCP.
- `/tes:field-reports`: inspect, drain, disable, or re-enable Field Reports.
- `/tes:doctor`: run health and certification gates.
- `/tes:adapter`: materialize, dry-run, retrofit, or apply adapter surfaces.
- `/tes:bench`: plan, run, or converge context-mesh benchmarks.

See `docs/install/COMMAND-TRIGGERS.md` for routing detail and
`docs/install/USER-MANUAL.html` for user-facing usage.

## Certification

Every assisted mesh, retrofit, update, or audit run ends with a certification
report. A `GO meshed` result means the selected route was created or updated,
routed, and locally checked. It does not mean the result was committed, pushed,
published, or proven universal across every model and project.

The report must also state the Tilly source snapshot used. If that snapshot is
behind the current `main`, the run is certified only for the recorded snapshot
and must say `STALE_SOURCE`.

Step Zero protects the working tree before edits. If the target is dirty, the
agent offers a local baseline commit first. Rollback is always reported with
Git instructions.

## Repository Shape

Root stays thin.

- `src/**` contains adapter source.
- `docs/**` contains method, contracts, manuals, evidence, and architecture.
- `scripts/**` contains deterministic oracles.
- `benchmarks/**` contains evaluation fixtures.
- `dist/**` is generated materialization output and ignored by Git.

Start with `docs/INDEX.md` for the complete documentation map.

## Maintainer Gates

For package work in this repository, use the local gates:

```bash
npm run validate
npm run tds:validate
npm run docs:size
npm run cortex:self-test
npm run cortex:mcp:self-test
npm run field-reports:self-test
npm run field-reports:github-oracle
npm run install:smoke
npm run platform:surface:check
npm run materialize:check
npm run commit:check
```

`commit:check` is the closure gate. It is stricter than `validate` and catches
required files that are untracked or unstaged.

Manual adapter materialization is for maintainers and debugging only. Real
target projects should use the assisted context mesh flow so existing
governance is preserved.
