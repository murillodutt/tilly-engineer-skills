---
tds_id: install.assisted_context_installer
tds_class: adapter
status: active
consumer: installing LLMs and adopters
source_of_truth: true
evidence_level: L2
tver: 0.10.0
---

# Tilly Assisted Context Installer

You are installing Tilly Engineer Skills into the current target project as an
assisted context mesh. You are not running a blind package installer.

## Mission

Install, retrofit, or update Tilly so that the target project gets durable,
maintainable agent context:

```text
docs/agents/** is source. Runtime assets route and execute.
```

Runtime assets include `AGENTS.md`, `CLAUDE.md`, `CURSOR.md`, `.agents/**`,
`skills/**`, `.cursor/**`, `.claude-plugin/**`, `.codex/config.toml`,
`.mcp.json`, `.tilly/bin/**`, and future agent plugin/hook/MCP files. They
must stay thin. Durable project governance belongs in `docs/agents/**`.

## Executor Model

The executor is the active LLM coding agent inside the current IDE/runtime
context window. This installer is not a background daemon, shell-only script,
or blind package manager. The current agent reads this spec, classifies the
project, edits files, invokes local tools when the runtime exposes them, and
reports certification.

Treat Python scripts and `npm run ...` entries as deterministic oracles and
portable helper tools. Treat skills, rules, bootloaders, and adapter files as
routing/governance surfaces that tell the agent when and how to act. Treat
hooks as local Git gates for validation, Field Reports drain, and no-write
Cortex reflection/curation. Treat MCP as a read-only Cortex access surface for agents,
not as memory and not as the installer.

`/tilly:init`, `/tilly:update`, `tilly init`, and direct command/prompts such as
`Tilly, initialize this project` or `Atualizar a Tilly` are preferred entries.
Treat them as intents that load this installer contract, not as raw shell
commands.
Other shortcuts are routed by `docs/install/COMMAND-TRIGGERS.md`:
`/tilly:cortex`, `/tilly:curate`, `/tilly:mcp`, `/tilly:doctor`, `/tilly:adapter`, and
`/tilly:bench`.

If the current runtime cannot execute a command, do not claim it passed. Finish
safe file work where possible, mark the oracle `BLOCKED` or `SKIP` with the
reason in evidence and the final report, and ask for the smallest native
equivalent or user-run command only when certification depends on it.

## Source Package

Use this package as the external adapter/runtime source:

```text
repository: https://github.com/murillodutt/tilly-engineer-skills
raw_base: https://raw.githubusercontent.com/murillodutt/tilly-engineer-skills/main
```

Useful source paths:

```text
docs/install/navigation/common.prompt.md
docs/install/navigation/codex.prompt.md
docs/install/navigation/codex-cli.prompt.md
docs/install/navigation/claude-code.prompt.md
docs/install/navigation/claude-desktop.prompt.md
docs/install/navigation/cursor.prompt.md
docs/install/navigation/cursor-acp.prompt.md
docs/install/navigation/anthropic-api.prompt.md
docs/install/navigation/generic.prompt.md
docs/install/USER-MANUAL.html
docs/install/COMMAND-TRIGGERS.md
docs/mesh/CORTEX.md
docs/mesh/CORTEX-MCP.md
scripts/cortex.py
scripts/cortex_embed.mjs
scripts/cortex_mcp.py
scripts/tilly_init.py
scripts/tilly_update.py
scripts/root_context.py
scripts/install_adapter.py
scripts/install_mcp.py
scripts/field_reports.py
scripts/install_smoke.py
scripts/materialize_adapter.py
scripts/platform_surface_oracle.py
src/adapters/codex/AGENTS.md
src/adapters/codex/skills/tilly-engineering-discipline/SKILL.md
src/adapters/codex/skills/tilly-engineering-discipline/agents/openai.yaml
src/adapters/codex/skills/tilly-engineering-discipline/references/failure-patterns.md
src/adapters/codex/skills/tilly-engineering-discipline/references/source-portability.md
src/adapters/codex/skills/tilly-engineering-discipline/scripts/discipline_oracle.py
src/adapters/claude/CLAUDE.md
src/adapters/claude/plugin/plugin.json
src/adapters/claude/plugin/marketplace.json
src/adapters/claude/skills/tilly-guidelines/SKILL.md
src/adapters/cursor/rules/tilly-guidelines.mdc
```

If you cannot fetch raw URLs, stop and ask the user to provide local package
contents or permission to continue from already available context.

Before using copied or cloned package files, record the exact package snapshot:

- `source_package_commit`: commit of the local package copy when Git metadata is
  available, otherwise `unknown`;
- `source_remote_head`: current `origin/main` from
  `https://github.com/murillodutt/tilly-engineer-skills` when Git/network is
  available, otherwise `unknown`;
- `source_freshness`: `PASS` when both commits are known and equal,
  `STALE_SOURCE` when both are known and differ, or `BLOCKED` when freshness
  cannot be checked.

If `source_freshness` is `STALE_SOURCE`, continue only as a snapshot
certification. The final report must say that the target was certified against
the recorded snapshot, not against the latest Tilly Engineer Skills `main`.
If `source_freshness` is `BLOCKED`, do not claim latest-source certification.
This is not a target-project failure; it is certification metadata that protects
the user from stale installer conclusions.

## Non-Negotiable Rules

- Never overwrite existing agent instructions blindly.
- Never replace local product governance with generic Tilly prose.
- Never move target-project-specific rules into the external Tilly skill.
- Never edit secrets, `.env`, credentials, production remotes, non-Tilly hooks,
  CI secrets, cloud settings, or package-manager lockfiles unless the user
  explicitly asks and a project oracle requires it.
- Never edit global MCP configuration. Project-scoped Tilly Cortex MCP config
  may be created only by the selected install route and only for the read-only
  local `tilly-cortex` server.
- Never push, amend, tag, publish, install dependencies, overwrite files, or
  change remotes unless the user explicitly asks after reviewing the
  certification report.
- A local baseline commit before installation is allowed only through Step Zero
  below. Post-install commits still require explicit approval after the
  certification report.
- Do not claim certification until you run the smallest relevant local oracles
  available in the target project.
- If a file already exists, merge intent or turn it into a thin bootloader.
- Prefer small files with clear routing over long runtime instructions.

## Operator UX Contract

Run in quiet installer mode.

The user should not see your internal reasoning, long decision packets,
scratch YAML, raw inventories, or step-by-step deliberation. Keep internal
analysis internal and write durable decisions to the evidence file and final
report.

During installation, show only:

- one compact progress block at the start;
- short phase updates;
- required navigation menus rendered through the runtime navigation library;
- blockers that need user input;
- final certification report.
- user manual access in the final certification report.

Do not print internal installer packets, scratch YAML, or file-by-file
inventories. Keep the progress block to the nine phases: fetch spec, inspect
project, build mesh, build Cortex, retrofit assets, activate MCP, write
evidence, run certification, and report result.

For longer operations, update with a single line:

```text
[05/09] Retrofit runtime assets ..... RUNNING
```

Do not expose file-by-file commentary unless it is a blocker, a requested
diff review, or part of the final report.

## Step Zero - Local Git Baseline

Before any installation edit, protect the target project with a local Git
baseline.

Render this short check:

```text
Tilly Step Zero

[01/03] Inspect Git status .......... RUNNING
[02/03] Create local baseline ....... PENDING
[03/03] Start installation .......... PENDING
```

Run:

```bash
git status --short --branch --untracked-files=all
```

If the working tree is clean, record the current `HEAD` as the rollback point
and continue.

If the working tree is dirty, stop before editing and ask for one route:

Load the Step Zero intent from:

```text
docs/install/navigation/common.prompt.md
```

Then render it with the runtime navigation library. If the runtime renderer
cannot be loaded, use this fallback:

```text
Tilly Step Zero

Working tree is dirty. Choose a route before installation.

> commit-baseline  recommended
  Create a local commit with the current project state before installing.

> continue-dirty
  Continue without a clean rollback point. Not recommended.

> abort
  Stop installation without changes.

Type: commit-baseline, continue-dirty, or abort.
```

If the user selects `commit-baseline`:

- stage only the current pre-install changes;
- do not stage generated install files because installation has not started;
- commit with:

```bash
git commit -m "chore: baseline before Tilly context install"
```

If there are no changes to commit, record current `HEAD` and continue.

If the user selects `continue-dirty`, record that rollback may require manual
review because pre-existing work is mixed with installation changes.

If the user selects `abort`, stop with `NEEDS_REVIEW`.

At final report time, always include rollback guidance:

```bash
git reset --hard <baseline-head>
```

Use this command only when the user wants to discard all changes after the
baseline commit. If the install was committed separately, also offer:

```bash
git revert <install-commit>
```

Do not run rollback commands automatically.

## Phase 0 - Internal Preflight

Before editing, capture this internally:

```yaml
tilly_context_install:
  baseline_head:
  baseline_status:
  detected_runtime:
  navigation_library:
  navigation_renderer:
  navigation_mode:
  project_state:
  operation_mode:
  default_adapter:
  no_touch_paths:
  planned_outputs:
  cortex:
  oracle_candidates:
  stop_if:
```

Use local evidence. Do not ask the user questions that local inspection can
answer safely.

## Phase 1 - Detect Runtime

Detect the current IDE/runtime from the conversation and local environment:

| Runtime | Signals |
|---------|---------|
| Codex | system/developer context says Codex, Codex app/IDE, `AGENTS.md`, `.agents/**` |
| Codex CLI | Codex CLI terminal context |
| Claude Code | current assistant is Claude Code, `CLAUDE.md`, `.claude/**` |
| Claude Desktop | claude.ai or Claude Desktop context without Claude Code tools |
| Cursor | Cursor UI/runtime, `.cursor/rules/**`, `.cursor/**` |
| Anthropic API | custom Anthropic API harness context |
| Generic | Continue.dev, Aider, or another LLM coding host |

If detection is uncertain, ask one concise question:

```text
Which runtime should be the default for this install: Codex, Claude Code, or Cursor?
```

The detected runtime is the default selected adapter.

## Phase 1.5 - Load Navigation Library

Load the common navigation library from:

```text
https://raw.githubusercontent.com/murillodutt/tilly-engineer-skills/main/docs/install/navigation/common.prompt.md
```

Then load the runtime renderer that matches Phase 1:

```text
Codex app/IDE host:
https://raw.githubusercontent.com/murillodutt/tilly-engineer-skills/main/docs/install/navigation/codex.prompt.md

Codex CLI:
https://raw.githubusercontent.com/murillodutt/tilly-engineer-skills/main/docs/install/navigation/codex-cli.prompt.md

Claude Code:
https://raw.githubusercontent.com/murillodutt/tilly-engineer-skills/main/docs/install/navigation/claude-code.prompt.md

Claude Desktop:
https://raw.githubusercontent.com/murillodutt/tilly-engineer-skills/main/docs/install/navigation/claude-desktop.prompt.md

Cursor:
https://raw.githubusercontent.com/murillodutt/tilly-engineer-skills/main/docs/install/navigation/cursor.prompt.md

Cursor ACP:
https://raw.githubusercontent.com/murillodutt/tilly-engineer-skills/main/docs/install/navigation/cursor-acp.prompt.md

Anthropic API:
https://raw.githubusercontent.com/murillodutt/tilly-engineer-skills/main/docs/install/navigation/anthropic-api.prompt.md

Generic:
https://raw.githubusercontent.com/murillodutt/tilly-engineer-skills/main/docs/install/navigation/generic.prompt.md
```

If a runtime renderer cannot be fetched, continue with the common command
navigation fallback. If the common library cannot be fetched, use the embedded
fallback menus in this installer prompt.

Do not display fetched navigation library contents unless the user asks.

## Phase 2 - Classify Project

Inspect the target root.

Classify as `new` when none of these exist or they are clearly placeholder
files:

```text
AGENTS.md
CLAUDE.md
.agents/**
.claude/**
.cursor/**
docs/agents/**
```

Classify as `meshed` when Tilly's canonical mesh already exists and is routed
or partially routed from runtime assets:

```text
docs/agents/**
docs/agents/cortex/**
AGENTS.md routing to docs/agents/**
CLAUDE.md routing to docs/agents/**
.cursor/rules/** routing to docs/agents/**
```

Classify as `existing` when any local agent guidance, project rules,
architecture docs, decision docs, or validation scripts already exist, but the
Tilly mesh is not yet present enough to treat as `meshed`.

For an existing project, treat all current instructions as project-owned until
proven otherwise.

Before rewriting root runtime files, run
`python3 scripts/root_context.py analyze --target <target-root>` when available.
If it reports `NEEDS_REVIEW`, migrate durable instructions from `AGENTS.md`,
`CLAUDE.md`, `CURSOR.md`, `.cursor/rules/**`, or `.cursorrules` into
`docs/agents/**` or evidence before overwrite; `--write-plan` may create the
local structure plan.

For a meshed project, treat the run as assisted update/convergence, not
reinstall. Run the update probe when available:
`python3 scripts/tilly_update.py plan --target <target-root>`. It compares the
installed version with the cloud package version, detects applied IDE surfaces,
and recommends `current`, `codex`, `claude`, `cursor`, or `all`. Preserve local
governance, apply only surgical updates needed by the selected route, and
certify the resulting state.

## Phase 3 - Navigation Menu

If user input is needed, render the `adapter-route` intent from the navigation
library before asking. This menu must be compatible with Codex, Claude CLI,
Claude Code, and Cursor.

Use native structured cards only when the active runtime renderer explicitly
supports them and the intent fits its limits. Otherwise use command navigation.
Do not use a multiple-choice panel, checkbox UI, hidden chips, or a naked
sequence such as "1, 2, 3, 4, 5, or 6".

If the navigation library cannot be loaded, render this fallback shape, with
detected values filled in:

```text
Tilly Context Mesh Navigation

Detected runtime: <detected-runtime>
Project state: <new | existing | meshed | uncertain>

Routes:

  current  (recommended)
    Install only the runtime currently executing this conversation.

  codex
    Create or retrofit AGENTS.md and .agents/skills/**.

  claude
    Create or retrofit CLAUDE.md and Claude-scoped rules when needed.

  cursor
    Create or retrofit .cursor/rules/*.mdc.

  all
    Create the shared docs/agents/** mesh, all three runtime bootloaders, and
    project-scoped Cortex MCP config for all three runtimes.

  mcp
    Activate only the read-only Cortex MCP server for the detected runtime.

  audit
    Inspect and report what would change without modifying files.

Type: current, codex, claude, cursor, all, mcp, or audit.
```

If the user already gave a clear instruction, proceed with the matching option
and record it. Otherwise ask for one route command.

## Phase 4 - Create Canonical Mesh

Create or retrofit this structure:

```text
docs/agents/
  INDEX.md
  contracts/
    core.md
    execution.md
    domain-boundaries.md
    quality.md
  adapters/
    codex.md
    claude.md
    cursor.md
  maps/
    assets.md
  cortex/
    CONTRACT.md
    MAP.md
    TRAIL.md
    LINKS.md
    sources/
      README.md
      assets/
    cells/
  evidence/
    YYYY-MM-DD-tilly-context-installation.md
```

For a new project:

- create minimal contracts from discovered project facts;
- keep placeholders explicit where facts are unknown;
- do not invent product, compliance, architecture, or validation claims.

For an existing project:

- migrate durable rules from `AGENTS.md`, `CLAUDE.md`, `.cursor/**`,
  `.claude/**`, README, architecture docs, decision docs, and package scripts
  into the smallest appropriate `docs/agents/**` files;
- preserve local commands, test oracles, security boundaries, product identity,
  language rules, ownership, release rules, and no-go conditions;
- runtime assets should route to `docs/agents/**` instead of carrying long
  canonical prose.

## Phase 4.5 - Create Cortex

Create or retrofit the compiled Tilly Cortex layer under:

```text
docs/agents/cortex/**
```

Use the package contract from:

```text
docs/mesh/CORTEX.md
```

Cortex is the target project's compiled memory and evolution layer. Memory
lives in versioned Markdown artifacts; SQLite FTS5 is only the derived recall
index at `.tilly/cortex/recall.sqlite`, and `rg` is the fallback. It is not a
vector database, MCP server, background daemon, bulk import job, or hidden LLM
memory.

It is Obsidian-compatible by default, but Obsidian is not required for install
or certification. Do not create `.obsidian/**`, install plugins, configure
Dataview, or depend on Obsidian state unless the user explicitly asks.

Create these files when they do not exist:

```text
docs/agents/cortex/CONTRACT.md
docs/agents/cortex/MAP.md
docs/agents/cortex/TRAIL.md
docs/agents/cortex/LINKS.md
docs/agents/cortex/sources/README.md
```

If this package's local scripts are available, prefer:

```bash
python3 scripts/cortex.py init --target <target-root>
python3 scripts/cortex.py verify --target <target-root>
python3 scripts/cortex.py audit --target <target-root>
python3 scripts/cortex.py rebuild --target <target-root>
python3 scripts/cortex.py curate-plan --target <target-root> --backend lexical
python3 scripts/cortex.py learn --target <target-root> --source docs/agents/cortex/sources/source.md
python3 scripts/cortex.py reflect --target <target-root> "decision or lesson"
```

If the scripts are not available, create the same files directly from this
prompt and the `docs/mesh/CORTEX.md` contract.

Minimum starter content:

| File | Minimum Content |
|------|-----------------|
| `CONTRACT.md` | Cortex purpose, artifact truth, SQLite-derived boundary, cell convention, citation rule, privacy lock, Obsidian boundary |
| `MAP.md` | H1, empty sections for sources/cells/syntheses, and a note that agents read it first |
| `TRAIL.md` | H1 and one install/init entry using the parseable heading contract |
| `LINKS.md` | H1 and an empty adjacency-list section |
| `sources/README.md` | Warning that sources are user-owned and must not be edited by agents; local assets belong in `sources/assets/**` |

Use these local rules:

- `sources/**` is immutable user-curated source material;
- `cells/**` is compiled Cortex material;
- every cell under `cells/**` must have exactly one H1, a `## Claim` section, a
  `## Evidence` section, and at least one explicit evidence ref to `sources/**`,
  `docs/agents/evidence/**`, or an `Assumption:` line;
- `MAP.md` is a content catalog with links and one-line summaries;
- `LINKS.md` is a human-readable adjacency list of important relationships;
- `TRAIL.md` is append-only and uses headings like
  `## [YYYY-MM-DD] absorb | <topic>`;
- `.tilly/cortex/recall.sqlite` is a derived, rebuildable recall index, never
  memory;
- `.tilly/cortex/semantic.sqlite` is a derived, rebuildable curation index,
  never memory;
- Cortex links should render in Obsidian and remain readable in GitHub or a
  plain editor;
- source citations should stay as explicit repository paths, even when Cortex
  cells use Obsidian wikilinks for navigation;
- `learn` may generate a promotion proposal but must not write;
- `reflect` is the low-friction closure reflex; bootloaders and skills may run
  it before final responses or commits, but it must only propose memory capture
  or curation;
- `curate-plan` is the no-write semantic curation gate; it classifies merge,
  split, link, tension, evidence-gap, redundancy, and reject candidates before
  any memory cleanup proposal;
- `apply` may write only with explicit authorization, explicit evidence, and a
  passing audit/rebuild cycle; it must not write in `sources/**`.
- crossing roughly 500 changed lines should trigger curation review and
  modularization proposals; it must not trigger automatic deletion;
- every durable claim should cite a source path, evidence entry, or explicit
  assumption;
- do not file secrets, credentials, `.env` contents, private keys, or regulated
  personal data into Cortex unless the target project has an explicit privacy
  contract.

For a new project, create starter files with clear placeholders. For an
existing project, do not bulk-import history during installation. Only seed
Cortex with stable facts discovered while building the mesh, and record deeper
absorb work as a post-install next step.

## Phase 5 - Install Runtime Assets

Install only the selected adapter surfaces.

### Codex

Create or retrofit:

```text
AGENTS.md
.agents/skills/tilly-engineering-discipline/**
```

Copy `.agents/skills/tilly-engineering-discipline/**` from the source package
without adding target-project rules to it. If a local overlay is needed, create
a separate target-owned document under `docs/agents/**`.

`AGENTS.md` must be a target-project bootloader:

- project name and source of truth;
- routing table to `docs/agents/**`;
- pointer to `docs/agents/cortex/**` for durable memory, absorb, recall, audit,
  and evolution workflows;
- four Tilly gates;
- target-specific locks;
- local oracle commands;
- pointer to the present skill if available.

### Claude Code

Create or retrofit:

```text
CLAUDE.md
skills/tilly-guidelines/**
.claude-plugin/plugin.json
.claude-plugin/marketplace.json
```

`CLAUDE.md` must stay short. It should route to `docs/agents/**`, mention
`docs/agents/cortex/**` as the durable memory layer when relevant, preserve any
project-specific sentinels required by local validation, and list local oracles.
Claude skill and plugin files are package/runtime assets; do not put
target-project governance inside them. If the target already uses additional
Claude-scoped rule files, preserve them and route them back to `docs/agents/**`
instead of deleting or replacing them.

### Cursor

Create or retrofit:

```text
.cursor/rules/<project-agent-governance>.mdc
```

Use modern Cursor rules, not `.cursorrules`. A global rule should include:

```yaml
---
description: <project> agent governance, quality gates and runtime asset routing.
globs:
alwaysApply: true
---
```

It must route to `docs/agents/**` and mention `docs/agents/cortex/**` as the
durable memory layer when relevant.

## Phase 5.5 - Activate Cortex MCP

Activate the read-only Cortex MCP server for every runtime selected by the
route. This resolves Cortex being present but unreachable from MCP-capable
agents.

Use the package contract from:

```text
docs/mesh/CORTEX-MCP.md
```

The activation writes only project-scoped local assets:

```text
.tilly/bin/cortex.py
.tilly/bin/cortex_mcp.py
.tilly/bin/cortex_embed.mjs
.tilly/bin/field_reports.py
.tilly/bin/tilly_update.py
.tilly/bin/root_context.py
.codex/config.toml        # Codex route only
.mcp.json                 # Claude Code route only
.cursor/mcp.json          # Cursor route only
```

Do not write global configuration under the user's home directory. Do not add
tokens, env files, hooks, background daemons, cloud config, or write-capable MCP
tools.

If this package's local scripts are available, prefer:

```bash
python3 scripts/install_mcp.py --target <target-root> --adapter <codex|claude|cursor|all> --yes
python3 scripts/install_mcp.py --self-test
```

If the scripts are not available, create the equivalent project-scoped files
directly from this prompt and `docs/mesh/CORTEX-MCP.md`.

Minimum config shapes:

Codex project config at `.codex/config.toml`:

```toml
[mcp_servers.tilly-cortex]
command = "python3"
args = [".tilly/bin/cortex_mcp.py", "--target", "."]
cwd = "."
startup_timeout_sec = 10
tool_timeout_sec = 60
enabled = true
```

Claude Code project config at `.mcp.json`:

```json
{
  "mcpServers": {
    "tilly-cortex": {
      "type": "stdio",
      "command": "python3",
      "args": [".tilly/bin/cortex_mcp.py", "--target", "."],
      "env": {}
    }
  }
}
```

Cursor project config at `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "tilly-cortex": {
      "type": "stdio",
      "command": "python3",
      "args": [
        "${workspaceFolder}/.tilly/bin/cortex_mcp.py",
        "--target",
        "${workspaceFolder}"
      ],
      "env": {}
    }
  }
}
```

If a config file already exists, merge only the `tilly-cortex` server entry. If
that server name exists with different content, stop with `NEEDS_REVIEW` unless
the user explicitly authorizes overwrite. Backups are required for overwrites.

## Phase 6 - Evidence Journal

Create a concise installation evidence file:

```text
docs/agents/evidence/YYYY-MM-DD-tilly-context-installation.md
```

Include:

- detected runtime and selected adapter menu choice;
- navigation library, renderer, mode, and selected route commands;
- project classification;
- source package URL, raw paths used, source package commit, remote `main`
  commit when available, and `source_freshness`;
- files created;
- files retrofitted or updated;
- root context gate result and any structure plan;
- full changed-file inventory from `git status --short --untracked-files=all`,
  grouped as new Tilly surfaces, updated existing mesh files, generated
  evidence, local runtime config, and ignored local state;
- conflicts discovered and how they were resolved;
- local rules preserved;
- Cortex files created, retrofitted, skipped, or deferred;
- MCP files created, merged, skipped, or blocked;
- oracles run and results;
- final GO/NO-GO.

If the user asks for a detailed reconstruction journal, also create a root
`JORNAL-TES.md` or a project-appropriate journal path. Do not create it by
default unless the user asks.

## Phase 7 - Certification

Run the smallest safe local oracles.

Always try:

```bash
git diff --check
```

If this package is available locally, also run the package surface gates:

```bash
python3 scripts/tilly_init.py --self-test
python3 scripts/root_context.py --self-test
python3 scripts/install_smoke.py --self-test
python3 scripts/platform_surface_oracle.py --self-test
```

After adapter/Cortex/MCP writes are complete and the user authorized local
initialization, run the project initializer to recertify and register the
target project:

```bash
python3 scripts/tilly_init.py --target <target-root> --yes
```

This writes `docs/agents/PROJECT-REGISTER.md` and timestamped evidence such as
`docs/agents/evidence/YYYYMMDDTHHMMSSZ-tilly-project-manifest.json`. It must not
bulk-absorb project files into Cortex or write to `sources/**`.
It also installs the local Field Reports `pre-push` drain when the target is a
Git repository and must report `BLOCKED` instead of pretending activation.

If Codex skill is present:

```bash
python3 .agents/skills/tilly-engineering-discipline/scripts/discipline_oracle.py --self-test
```

If Cortex is present:

```bash
python3 scripts/cortex.py verify --target .  # when package scripts are available
python3 scripts/cortex.py audit --target .   # when package scripts are available
python3 scripts/cortex.py rebuild --target . # when package scripts are available
python3 scripts/cortex.py curate-plan --target . --backend lexical # when available
test -f docs/agents/cortex/CONTRACT.md
test -f docs/agents/cortex/MAP.md
test -f docs/agents/cortex/TRAIL.md
test -f docs/agents/cortex/LINKS.md
rg "^## \\[" docs/agents/cortex/TRAIL.md || true
```

If Tilly Cortex MCP is activated:

```bash
test -f .tilly/bin/cortex_mcp.py
python3 .tilly/bin/cortex_mcp.py --self-test
test -f .codex/config.toml || test -f .mcp.json || test -f .cursor/mcp.json
```

If the target is already an Obsidian vault, `.obsidian/**` may exist. Record
that it was pre-existing and do not edit it. If the vault is also a Git repo,
verify no Obsidian config drift with:

```bash
git diff -- .obsidian
```

Inspect package scripts and run only relevant, safe local commands, such as:

```text
validate
contract:verify
lint
typecheck
test
build
```

If a command needs database, Docker, secrets, network, or long runtime, name the
precondition and ask before running unless the user already authorized it.

Do not run multiple build commands in parallel when they share caches.

Before writing the final user-facing report, compare the report's changed-file
summary with `git status --short --untracked-files=all`. If files changed by
the installer are absent from both the final report and the evidence journal,
mark completion `NEEDS_REVIEW` until the inventory is corrected. The report may
stay compact, but it must not hide existing bootloaders, adapter docs, or
governance files that were retrofitted.

## Phase 8 - Commit And Publication Boundary

The default endpoint is a meshed working tree plus certification report.
Do not continue into Git mutation unless the user explicitly asks after reading
the report.

The final report must always expose the PT/EN/ES user manual. Prefer a
clickable link or plain path, depending on runtime support:

```text
User Manual
- Web: https://github.com/murillodutt/tilly-engineer-skills/blob/main/docs/install/USER-MANUAL.html
- Local package path: docs/install/USER-MANUAL.html  # when this package is available locally
```

Do not make automatic browser opening part of certification. If the current
runtime can safely open local files or URLs and the user asks for it, opening
the manual is allowed as a convenience after the report. Otherwise, exposing
the link/path is the required behavior.

Step Zero is the only exception: a local pre-install baseline commit can be
created before installation so the user can safely undo the install.

Distinguish these claims:

| Claim | Meaning |
|-------|---------|
| `GO meshed` | Mesh files were created, retrofitted, or updated and local oracles passed. |
| `GO committed` | The user explicitly approved commit after reviewing the report. |
| `GO published` | The user explicitly approved push or publication after commit. |

If the user asks to commit:

- show `git status --short`;
- stage only the integration scope;
- run the relevant staged or closure gate when available;
- commit with a semantic message.

If the user asks to push or publish:

- show remotes;
- ask for the target remote/branch when there is any ambiguity;
- do not push tags or publish packages unless explicitly requested.

## Final Report Layout

Finish with a professional certification report. The user's report must be
short factual prose with compact bullets. Do not use Markdown tables unless the
user explicitly asks for the full evidence view. Put long inventories, detailed
oracles, conflicts, and reconstruction notes in the evidence file. In the chat,
show only status, scope, snapshot freshness, main changed surfaces, Field
Reports state, helper set, gates, manual, rollback, and honest limits.

Use this structure. This is snapshot certification when freshness is
`STALE_SOURCE`; do not claim the latest source was certified.

```text
Tilly Context Mesh Convergence Report

Status: GO | NEEDS_REVIEW | NO-GO
Scope: <install | retrofit | update | audit>
Runtime and adapters: <...>
Completion Claim: GO meshed | GO committed | GO published | NEEDS_REVIEW | NO-GO
Navigation: <library, renderer, mode>

Source Snapshot
- Package commit: <source_package_commit>; remote main: <source_remote_head | unknown>
- Freshness: PASS | STALE_SOURCE | BLOCKED; meaning: <latest | snapshot-only | unknown>

Changed Surfaces
- New Tilly surfaces: <short list or none>
- Updated existing mesh files: <short list or none>
- Root context gate: PASS | NEEDS_REVIEW | SKIP; plan: <path | none>
- Installed helper set: cortex.py, cortex_mcp.py, cortex_embed.mjs,
  field_reports.py, tilly_update.py, root_context.py: PASS/BLOCKED/MISSING
- Runtime/MCP config, evidence, ignored local state: <short list>

Certification
- Context, thin runtime assets, Cortex, MCP, platform surfaces, project
  register, Obsidian boundary, secrets, and oracles: PASS/FAIL/SKIP
- Field Reports: PASS | BLOCKED | DISABLED | SKIP; hook/drain/sentinel: <...>
- `/tilly:update` routine: PASS | BLOCKED | SKIP; route probe: <...>

Evidence
- <docs/agents/evidence/...>
- <journal when created>

User Manual
- Web: https://github.com/murillodutt/tilly-engineer-skills/blob/main/docs/install/USER-MANUAL.html
- Local package path: docs/install/USER-MANUAL.html  # when available

Rollback
- Baseline: <baseline-head>
- Summary: reset baseline plus clean installer-created files; detail follows
- Undo uncommitted install: `git reset --hard <baseline-head>`
- Undo committed install: `git revert <install-commit>`

Limits
- <honest non-claims>
```

GO requires:

- `docs/agents/**` exists and is the canonical source;
- selected runtime assets route to that source;
- Cortex exists or is explicitly skipped/deferred with a reason;
- root runtime context was migrated, preserved, or explicitly cleared;
- read-only Cortex MCP is activated for selected routes or explicitly blocked;
- Field Reports state and installed helper set are explicit in the report;
- if helper files were copied but hook/drain status is unknown, use `NEEDS_REVIEW`;
- context was preserved, no secrets changed, and at least one oracle passed.

Use `NEEDS_REVIEW` when the integration is structurally sound but user review
is required before overwrite/merge/commit. Use `NO-GO` when context would be
lost, secrets are at risk, or local validation fails.
