---
tds_id: install.assisted_context_installer
tds_class: adapter
designation: self_contained_context_install_gate
status: active
consumer: installing LLMs and adopters
source_of_truth: true
evidence_level: L2
tver: 0.10.8
---

# Tilly Assisted Context Installer

You are installing Tilly Engineer Skills into the current target project as an assisted context mesh. You are not running a blind package installer.

## Mission

Install, retrofit, or update TES so that the target project gets durable,
maintainable agent context and an initial project contextualization:

```text
docs/agents/** is source. Runtime assets route and execute.
```

Runtime assets include `AGENTS.md`, `CLAUDE.md`, `CURSOR.md`, `.agents/**`, `.claude/skills/**`, `.cursor/**`, `.codex/config.toml`, `.mcp.json`, `.tes/bin/**`, and future explicitly approved agent plugin/hook/MCP files. They must stay thin. Durable project governance belongs in `docs/agents/**`.

`/tes-init` must also initialize the project for future agent work. It should
analyze the target root, read the strongest project anchors available, write
`docs/agents/PROJECT-CONTEXT.md`, and make unknowns explicit instead of
claiming domain or architecture facts without evidence.

## Executor Model

The executor is the active LLM coding agent inside the current IDE/runtime context window. This installer is not a background daemon, shell-only script, or blind package manager. The current agent reads this spec, classifies the project, edits files, invokes local tools when the runtime exposes them, and reports certification.

Treat Python scripts and `npm run ...` entries as deterministic oracles and portable helper tools. Treat skills, rules, bootloaders, and adapter files as routing/governance surfaces that tell the agent when and how to act. Treat hooks as local Git gates for validation, Field Reports drain, and no-write Cortex reflection/curation. Treat MCP as a read-only Cortex access surface for agents, not as memory and not as the installer.

`/tes-init`, `/tes-setup`, `/tes-update`, `/tes:init`, `/tes:update`, `tes init`, `tes setup`, and direct command/prompts such as `TES, initialize this project` or `Atualizar TES` are preferred entries. Treat them as intents that load this installer contract, not as raw shell commands. Across Codex, Claude Code, and Cursor, prefer shared hyphen triggers such as `/tes-init`, `/tes-setup`, `/tes-update`, `/tes-goal-maestro`, `/tes-prospect`, `/tes-mine`, and `/tes-cortex`; if a host reports a `/tes:*` alias as invalid, continue as TES intent text through the matching `tes-*` skill/rule/spec instead of asking the user to choose a route. `/tes-setup` is the direct setup alias for `/tes-init`.

Other shortcuts are routed by `docs/install/COMMAND-TRIGGERS.md`: `/tes-goal-maestro`, `/tes-prospect`, `/tes-mine`, `/tes-cortex`, `/tes-curate`, `/tes-mcp`, `/tes-doctor`, `/tes-adapter`, `/tes-bench`, and their `/tes:*` compatibility aliases. `/tes-goal-maestro`, `/tes-prospect`, and `/tes-mine` require explicit invocation; `tes-goal-maestro` may also route from a direct request to generate a maestral `/goal` prompt from a mature SPEC, Super SPEC, PRD, relational project plan, or accepted execution tree after preserving declared execution units, validating the tree internally, and requiring material-diff, material-continuation, semantic negative-grep, sequential ownership and sync-status evidence. Generated Super SPEC content is written to `GOAL-SUPER-SPEC-*.md` and summarized in chat instead of being pasted into the context window.

If the current runtime cannot execute a command, do not claim it passed. Finish safe file work where possible, mark the oracle `BLOCKED` or `SKIP` with the reason in evidence and the final report, and ask for the smallest native equivalent or user-run command only when certification depends on it.

## Source Package

Use this package as the external adapter/runtime source:

```text
repository: https://github.com/murillodutt/tilly-engineer-skills
raw_base: https://raw.githubusercontent.com/murillodutt/tilly-engineer-skills/main
```

Useful source paths, relative to `raw_base`:

```text
docs/install/navigation/{common,codex,codex-cli,claude-code,claude-desktop,cursor,cursor-acp,anthropic-api,generic}.prompt.md
docs/install/{USER-MANUAL.html,COMMAND-TRIGGERS.md}
docs/mesh/{CORTEX.md,CORTEX-MCP.md}
scripts/{cortex.py,cortex_embed.mjs,cortex_mcp.py,scope_contract.py,event_ledger.py,checkpoint.py,consolidation_gate.py,tes_init.py,tes_update.py,tes_legacy_retirement.py,root_context.py,install_adapter.py,install_mcp.py,field_reports.py,install_smoke.py,materialize_adapter.py,platform_surface_oracle.py}
src/adapters/codex/AGENTS.md
src/adapters/codex/skills/{tes-engineering-discipline,tes-goal-maestro}/
src/adapters/claude/{CLAUDE.md,plugin/plugin.json,plugin/marketplace.json,skills/tes-*/SKILL.md}
src/adapters/cursor/rules/tes-guidelines.mdc
```

If you cannot fetch raw URLs, stop and ask the user to provide local package contents or permission to continue from already available context.

Before using copied or cloned package files, record the exact package snapshot:

- `source_package_commit`: commit of the local package copy when Git metadata is available, otherwise `unknown`;
- `source_remote_head`: current `origin/main` from `https://github.com/murillodutt/tilly-engineer-skills` when Git/network is available, otherwise `unknown`;
- `source_freshness`: `PASS` when both commits are known and equal, or when a public bundle's `source_commit` is an ancestor of the current remote `main` distribution commit for the same published version; `STALE_SOURCE` when both commits are known and unrelated or the bundle version/hash is not the current published artifact; `BLOCKED` when freshness cannot be checked.

When installing from the public versioned ZIP, use the bundle `index.json` and
staged `tes-bundle-manifest.json` as the package snapshot source. They must
expose `source_commit`, `source_repository`, `created_at`, and SHA-256
metadata. The ZIP must also contain its setup installer scripts so it can be
staged and applied without a full source checkout. Treat `source_commit` as the
source package commit that generated the bundle; the later Git commit that
publishes the ZIP/hash may be a distribution commit and cannot be embedded in
its own artifact without a circular hash.
If the public index and staged manifest agree on version, SHA-256, and
`source_commit`, and that source commit is an ancestor of remote `main`, report
freshness as `PASS` with meaning `current public bundle`, not `STALE_SOURCE`.
Use the deterministic helper when available:
`python3 <tes-package-or-staged-bundle>/scripts/tes_bundle.py freshness --target <target-root>`.
Do not infer freshness only from unequal commit strings; public bundle source
commits may intentionally be ancestors of the later distribution commit.

If `source_freshness` is `STALE_SOURCE`, continue only as a snapshot certification. The final report must say that the target was certified against the recorded snapshot, not against the latest Tilly Engineer Skills `main`. If `source_freshness` is `BLOCKED`, do not claim latest-source certification. This is not a target-project failure; it is certification metadata that protects the user from stale installer conclusions.

For `/tes-update` or `/tes:update`, `CURRENT` also requires helper contract parity. If installed helper hashes or required contract markers differ from the package source, report `STALE_HELPERS`, route to update, and do not call the target current even when installed and cloud versions match.

## Non-Negotiable Rules

- Never overwrite existing agent instructions blindly.
- Never replace local product governance with generic Tilly prose.
- Never move target-project-specific rules into the external Tilly skill.
- Never edit secrets, `.env`, credentials, production remotes, non-Tilly hooks, CI secrets, cloud settings, or package-manager lockfiles unless the user explicitly asks and a project oracle requires it.
- Never edit global MCP configuration. Project-scoped TES Cortex MCP config may be created only by the selected install route and only for the read-only local `tes-cortex` server.
- Never push, amend, tag, publish, install dependencies, overwrite files outside the selected TES clean-runtime route, overwrite root runtime files before `.tes/bk/<timestamp>/manifest.json` exists, or change remotes unless the user explicitly asks after reviewing the certification report.
- A local baseline commit before installation is allowed only through Step Zero below. Post-install commits still require explicit approval after the certification report.
- Do not claim certification until you run the smallest relevant local oracles available in the target project.
- If a file already exists, merge intent or turn it into a thin bootloader.
- Prefer small files with clear routing over long runtime instructions.

## Operator UX Contract

Run in quiet installer mode.

The user should not see your internal reasoning, long decision packets, scratch YAML, raw inventories, or step-by-step deliberation. Keep internal analysis internal and write durable decisions to the evidence file and final report.

During installation, show only:

- one compact progress block at the start;
- short phase updates;
- required navigation menus rendered through the runtime navigation library;
- blockers that need user input;
- final certification report.
- user manual access in the final certification report.

Do not print internal installer packets, scratch YAML, or file-by-file inventories. Keep the progress block to the nine phases: fetch spec, inspect project, build mesh, build Cortex, retrofit assets, activate MCP, write evidence, run certification, and report result.

For longer operations, update with a single line:

```text
[05/09] Retrofit runtime assets ..... RUNNING
```

Do not expose file-by-file commentary unless it is a blocker, a requested diff review, or part of the final report.

## Step Zero - Local Git Baseline

Before any installation edit, protect the target project with a local Git baseline.
For `/tes-init`, run the router gates first:

- **Install/Update Gate** determines whether installer, helper, adapter, MCP,
  bootloader, or legacy-retirement writes are needed.
- **Project Context Gate** determines whether
  `docs/agents/PROJECT-CONTEXT.md` is absent, bootstrap-only, stale, weak, or
  failing the project-context oracle.
- **Project-Start Gate** is the `/tes-init` execution gate. It runs the
  installed project-context initializer and oracle before the final report. A
  preflight context PASS does not replace project-start execution.
- When `.tes/postinstall.json` is `needs_review`, `/tes-init` is recovery:
  inspect the latest postinstall run, repair the focused blocker, then run
  `python3 .tes/bin/tes_install.py postinstall --target . --recover-needs-review`.
  That command reruns Project-Start, records the recovery run, and clears the
  sentinel only on PASS.

If the Install/Update Gate finds an old meshed project that needs helper,
adapter, legacy-retirement, context, or alignment repairs but the user has not
authorized the required writes yet, close the pass as `NEEDS_REVIEW` and include
the `continuation_plan` from `tes_update.py plan --json-only`. The plan must
name the required phases, approvals, write surfaces, commands, final recorded
probe, and the fact that Project-Start Gate still runs after repairs. A
`NEEDS_REVIEW` report without this continuation plan is incomplete.

Step Zero protects installer/update writes. It must not block project-context
initialization when TES is already installed/current and the only failing gate
is the Project Context Gate. In that case, report the dirty tree as rollback
context, avoid helper/adapter/MCP/bootloader writes, run the project-context
scaffold, and certify with `project_context_oracle.py`.

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

If the working tree is clean, record the current `HEAD` as the rollback point and continue.

If the working tree is dirty and the Install/Update Gate needs installer/update
writes, stop before editing and ask for one route:

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

If the user selects `continue-dirty`, record that rollback may require manual review because pre-existing work is mixed with installation changes.

If the user selects `abort`, stop with `NEEDS_REVIEW`.

At final report time, always include rollback guidance:

```bash
git reset --hard <baseline-head>
```

Use this command only when the user wants to discard all changes after the baseline commit. If the install was committed separately, also offer:

```bash
git revert <install-commit>
```

Do not run rollback commands automatically.

## Local Git Hygiene

If the target is a Git repository, protect local-only Tilly artifacts through
`.git/info/exclude` before creating backups, caches, Field Reports state, or
derived Cortex indexes. This is a local repo exclude, not a project `.gitignore`
rewrite.

Required local excludes:

- `.tes/bin/*.bak-*`
- `.tes/bin/__pycache__/`
- `*.pyc`
- `.tes/bk/`
- `.tes/setup/`
- `.tes/field-reports/`
- `.tes/cortex/*.sqlite`
- `.tes/cortex/*.sqlite-*`

Do not ignore `.tes/bin/*.py`; installed helper scripts are the
project-scoped runtime surface.

## Phase 0 - Internal Preflight

Before editing, capture this internally:

```yaml
tes_context_install:
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

Use local evidence. Do not ask the user questions that local inspection can answer safely.

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
Codex app/IDE host -> docs/install/navigation/codex.prompt.md
Codex CLI -> docs/install/navigation/codex-cli.prompt.md
Claude Code -> docs/install/navigation/claude-code.prompt.md
Claude Desktop -> docs/install/navigation/claude-desktop.prompt.md
Cursor -> docs/install/navigation/cursor.prompt.md
Cursor ACP -> docs/install/navigation/cursor-acp.prompt.md
Anthropic API -> docs/install/navigation/anthropic-api.prompt.md
Generic -> docs/install/navigation/generic.prompt.md
```

Resolve renderer paths against `raw_base`. If a runtime renderer cannot be fetched, continue with the common command navigation fallback. If the common library cannot be fetched, use the embedded fallback menus in this installer prompt.

Do not display fetched navigation library contents unless the user asks.

## Phase 2 - Classify Project

Inspect the target root.

Classify as `new` when none of these exist or they are clearly placeholder files:

```text
AGENTS.md, CLAUDE.md, .agents/**, .claude/**, .cursor/**, docs/agents/**
```

Classify as `meshed` when Tilly's canonical mesh already exists and is routed or partially routed from runtime assets:

```text
docs/agents/**, docs/agents/cortex/**, AGENTS.md routing to docs/agents/**,
CLAUDE.md routing to docs/agents/**, .cursor/rules/** routing to docs/agents/**
```

Classify as `existing` when any local agent guidance, project rules, architecture docs, decision docs, or validation scripts already exist, but the TES mesh is not yet present enough to treat as `meshed`.

For an existing project, treat all current instructions as project-owned until
proven otherwise.

Before rewriting root runtime files, stage the bundle and create a central clean backup: `python3 scripts/tes_bundle.py stage --target <target-root>`, then `python3 scripts/tes_bundle.py backup --target <target-root> --adapter <route> --yes`. Use `python3 scripts/root_context.py analyze --target <target-root> --backup-id <backup-id>` or `tes_bundle.py recover-plan` to read previous governance from `.tes/bk/<timestamp>/**`, not from the active runtime after overwrite.

The default installer route is clean runtime: `python3 scripts/tes_bundle.py apply --target <target-root> --adapter <route> --mode clean-runtime --backup-id <backup-id> --yes`, followed by `python3 scripts/tes_bundle.py recover-plan --target <target-root> --backup-id <backup-id> --apply-safe --yes`. Close the root-context gate as `RECOVERED` when backup evidence and the recovery report exist; use `NEEDS_REVIEW` for ambiguous legacy semantics.

For a meshed project, treat the run as assisted update/convergence, not reinstall. Run read-only update probes when available: `python3 scripts/tes_update.py plan --target <target-root> --json-only`. If continuation is needed, stage the deterministic bundle under `.tes/setup/`, create `.tes/bk/<timestamp>/`, certify freshness, apply the clean runtime, then run semantic recovery: `tes_bundle.py stage`, `tes_bundle.py backup`, `tes_bundle.py freshness`, `tes_bundle.py apply --mode clean-runtime`, and `tes_bundle.py recover-plan --apply-safe`. Bundle staging and clean backups are local cache/history and must be ignored through target-local Git exclude. If the probe reports `recommended_update_scope=helpers-only` or `STALE_HELPERS`, run Layer Zero first and require `helper_contract_status=PASS` before adapter/MCP config activation. If the probe reports `runtime_trigger_status=DRIFT` or `recommended_update_scope=adapter-config`, do not leave old bootloaders active; backup, clean-apply, recover. After any helper overwrite or adapter refresh, a final recorded probe is mandatory before GO, evidence closeout, commit, or push: run `python3 .tes/bin/tes_update.py plan --target <target-root> --json-only --record-field-report` (or package `scripts/tes_update.py` when certifying from the package tree). The recorded event must show `helper_contract_status=PASS`, `runtime_trigger_status=PASS` or `NOT_APPLIED`, `update_available=False`, and `recommended_update_scope=none`.

If legacy retirement is required, run `python3 scripts/tes_legacy_retirement.py plan --target <target-root>` after the root context gate and before materializing new assets. The gate may remove only known old runtime assets, migrate `.tilly/field-reports/**` to `.tes/field-reports/**`, archive `.tilly/retrofit/**` under `.tes/legacy-retirement/retrofit/**`, and preserve project context. If it reports `NEEDS_REVIEW`, stop; do not copy new TES assets over old surfaces. When it is clean and the run is authorized, apply with `python3 scripts/tes_legacy_retirement.py apply --target <target-root> --yes`, then certify with `python3 scripts/tes_legacy_retirement.py audit --target <target-root>`.

Recover local governance from `.tes/bk/**`, apply only surgical updates needed by the selected route, and certify the resulting state.

## Phase 3 - Navigation Menu

If user input is needed, render the `adapter-route` intent from the navigation library before asking. This menu must be compatible with Codex, Claude CLI, Claude Code, and Cursor.

Use native structured cards only when the active runtime renderer explicitly supports them and the intent fits its limits. Otherwise use command navigation. Do not use a multiple-choice panel, checkbox UI, hidden chips, or a naked sequence such as "1, 2, 3, 4, 5, or 6".

If the navigation library cannot be loaded, render this fallback shape, with
detected values filled in:

```text
TES Context Mesh Navigation

Detected runtime: <detected-runtime>
Project state: <new | existing | meshed | uncertain>

Routes:

  current  (recommended)
    Install or refresh only the runtime currently executing this conversation after central backup.

  codex
    Apply clean AGENTS.md and .agents/skills/** after backup; recover local semantics into docs/agents/**.

  claude
    Apply clean CLAUDE.md, .claude/skills/**, and Claude MCP after backup; recover local semantics into docs/agents/**.

  cursor
    Apply clean .cursor/rules/*.mdc after backup; recover local semantics into docs/agents/**.

  all
    Create the shared docs/agents/** mesh, all three runtime bootloaders, and
    project-scoped Cortex MCP config for all three runtimes.

  mcp
    Activate only the read-only Cortex MCP server for the detected runtime.

  audit
    Inspect and report what would change without modifying files.

Type: current, codex, claude, cursor, all, mcp, or audit.
```

If the user already gave a clear instruction, proceed with the matching option and record it. Otherwise ask for one route command.

## Phase 4 - Create Canonical Mesh

Create or refresh this canonical mesh:

```text
docs/agents/
  INDEX.md
  PROJECT-CONTEXT.md
  PROJECT-REGISTER.md
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
    YYYY-MM-DD-tes-context-installation.md
```

For a new project: create minimal contracts from discovered project facts, keep placeholders explicit where facts are unknown, and do not invent product, compliance, architecture, or validation claims.

For an existing project:

- migrate durable rules from `AGENTS.md`, `CLAUDE.md`, `.cursor/**`, `.claude/**`, README, architecture docs, decision docs, and package scripts into the smallest appropriate `docs/agents/**` files;
- create or update `docs/agents/PROJECT-CONTEXT.md` as the initial project
  map, citing the project anchors actually read;
- preserve local commands, test oracles, security boundaries, product identity,
  language rules, ownership, release rules, and no-go conditions;
- runtime assets should route to `docs/agents/**` instead of carrying long canonical prose.

## Phase 4.1 - Initialize Project Context

`/tes-init` is not only an installer. It is the project start ritual for agents.
It routes internally through the **Install/Update Gate** and **Project Context
Gate**. If the install/update surface is current but the project context is
missing or weak, `/tes-init` performs only project-context initialization and
must not refresh helpers, adapters, MCP config, bootloaders, remotes, tags, or
release surfaces.

For `/tes-init`, the **Project-Start Gate** must run before final closeout even
when Project Context Gate preflight reports `PASS`. Run
`python3 .tes/bin/tes_init.py --target . --yes` in an installed target, or
`python3 scripts/tes_init.py --target <target-root> --yes` from the package
source. Then run `project_context_oracle.py --target <target-root>` and
`project_alignment_oracle.py --target <target-root>`. The initializer creates
the first-pass Obsidian-compatible operating mesh when missing; `/tes-align`
remains the deeper semantic refinement route. After helper-only or adapter
repairs, rerun the Project-Start Gate; preflight context PASS does not replace
project-start execution.

If `.tes/postinstall.json` is `needs_review`, do not leave the user with a
manual hidden `--force` step. Treat `/tes-init` as recovery, inspect the latest
run, repair the focused blocker, then run
`python3 .tes/bin/tes_install.py postinstall --target . --recover-needs-review`
as the Project-Start closure. If that recovery does not return PASS, report
`NEEDS_REVIEW` with the new run record and blocker.

When the update planner returns `continuation_plan.status=PENDING_APPROVAL`, do
not improvise a shorter route. Present the approval-gated plan compactly in the
report and stop. After the user approves, resume at the first required phase,
then rerun the exact final recorded probe required by the plan.

After classification and before certification closeout, analyze the project as
deeply as the current context window and local tools permit:

- inventory tracked and unignored files;
- read the strongest project anchors first: README, package or build
  manifests, architecture docs, root agent instructions, local validation
  scripts, source entrypoints, test roots, deployment/configuration docs, and
  existing `docs/agents/**`;
- synthesize project identity, territories, runtime/build/test signals,
  governance surfaces, quality gates, source anchors, known unknowns, and
  recommended deep reads;
- write the synthesis to `docs/agents/PROJECT-CONTEXT.md`;
- create the initial alignment mesh under `docs/agents/**` when missing:
  `PROJECT-STATE.md`, `PROJECT-ROADMAP.md` with Mermaid System X-Ray and
  Convergence Line graphs, `EXECUTION-LINE.md`, `QUALITY-GATES.md`,
  `BOUNDARIES-AND-CONSTRAINTS.md`, `KNOWLEDGE-LIFECYCLE.md`, `GLOSSARY.md`,
  `DECISIONS/**`, and retained project-alignment evidence;
- write the deterministic inventory to `docs/agents/PROJECT-REGISTER.md`;
- store full manifests and evidence under `docs/agents/evidence/**`.

Distinguish deterministic scaffold from semantic refinement. `tes_init.py`
creates the inventory-backed scaffold: identity, anchors, territories, scripts,
surfaces, evidence, and gaps. The active agent performs semantic refinement by
opening the strongest anchors and improving `PROJECT-CONTEXT.md` with supported
project meaning. For a non-trivial project, do not claim deep context until the
agent has opened strong anchors in the current run. If anchor reading is
blocked, close as `Project context: NEEDS_REVIEW` with the reason.

The context file must be evidence-led. Cite repository paths and say
`unknown`, `not found`, or `needs deeper read` when the project files do not
support a claim. Do not copy source code, secrets, or raw private content into
the context file. Do not bulk-absorb history into Cortex during installation;
only seed stable facts discovered while initializing and record deeper absorb
work as a post-install next step.

## Phase 4.5 - Create Cortex

Create or refresh the compiled TES Cortex layer under:

```text
docs/agents/cortex/**
```

Use the package contract from:

```text
docs/mesh/CORTEX.md
```

Cortex is the target project's compiled memory and evolution layer. Memory lives in versioned Markdown artifacts; SQLite FTS5 is only the derived recall index at `.tes/cortex/recall.sqlite`, and `rg` is the fallback. It is not a vector database, MCP server, background daemon, bulk import job, or hidden LLM memory.

It is Obsidian-compatible by default, but Obsidian is not required for install or certification. Do not create `.obsidian/**`, install plugins, configure Dataview, or depend on Obsidian state unless the user explicitly asks.

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

If the scripts are not available, create the same files directly from this prompt and the `docs/mesh/CORTEX.md` contract.

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
- every cell under `cells/**` must have exactly one H1, a `## Claim` section, a `## Evidence` section, and at least one explicit evidence ref to `sources/**`, `docs/agents/evidence/**`, or an `Assumption:` line;
- `MAP.md` is a content catalog with links and one-line summaries;
- `LINKS.md` is a plain-language adjacency list of important relationships;
- `TRAIL.md` is append-only and uses headings like `## [YYYY-MM-DD] absorb | <topic>`;
- `.tes/cortex/recall.sqlite` is a derived, rebuildable recall index, never memory;
- `.tes/cortex/semantic.sqlite` is a derived, rebuildable curation index, never memory;
- Cortex links should render in Obsidian and remain readable in GitHub or a plain editor;
- source citations should stay as explicit repository paths, even when Cortex cells use Obsidian wikilinks for navigation;
- `learn` may generate a promotion proposal but must not write;
- `reflect` is the low-friction closure reflex; bootloaders and skills may run it before final responses or commits, but it must only propose memory capture or curation;
- `curate-plan` is the no-write semantic curation gate; it classifies merge, split, link, tension, evidence-gap, redundancy, and reject candidates before any memory cleanup proposal;
- `apply` may write only with explicit authorization, explicit evidence, and a passing audit/rebuild cycle; it must not write in `sources/**`;
- crossing roughly 500 changed lines should trigger curation review and modularization proposals; it must not trigger automatic deletion;
- every durable claim should cite a source path, evidence entry, or explicit assumption;
- do not file secrets, credentials, `.env` contents, private keys, or regulated personal data into Cortex unless the target project has an explicit privacy contract.

For a new project, create starter files with clear placeholders. For an existing project, do not bulk-import history into Cortex during installation. Use `PROJECT-CONTEXT.md` for the initial project map, seed Cortex only with stable facts discovered while building the mesh, and record deeper absorb work as a post-install next step.

## Phase 5 - Install Runtime Assets

Install only the selected adapter surfaces.

### Codex

Apply clean runtime assets after central backup:

```text
AGENTS.md
.agents/skills/tes-engineering-discipline/**
```

Copy `.agents/skills/tes-engineering-discipline/**` from the source package without adding target-project rules to it. If a local overlay is needed, create a separate target-owned document under `docs/agents/**`.

`AGENTS.md` must be a target-project bootloader:

- project name and source of truth;
- routing table to `docs/agents/**`;
- pointer to `docs/agents/cortex/**` for durable memory, absorb, recall, audit, and evolution workflows;
- four Tilly gates;
- target-specific locks;
- local oracle commands;
- pointer to the present skill if available.

### Claude Code

Apply clean runtime assets after central backup:

```text
CLAUDE.md
.claude/skills/tes-*/**
```

`CLAUDE.md` must stay short. It should route to `docs/agents/**`, mention `docs/agents/cortex/**` as the durable memory layer when relevant, recover project-specific sentinels required by local validation, and list local oracles. Claude project skills live under `.claude/skills/**`; plugin metadata and plugin-root skill copies remain source-only in the TES Git package unless a separate plugin packaging decision is made. Claude runtime files are package assets; do not put target-project governance inside them. If `CLAUDE.md` already differs, back it up in `.tes/bk/**`, apply the clean bootloader, and recover useful semantics into `docs/agents/**`. If the target already uses additional Claude-scoped rule files, back them up and route their durable semantics back to `docs/agents/**` instead of leaving them as active runtime.

Before reporting install/update success, scan for obsolete TES plugin/root-skill
runtime surfaces: `skills/**`, `.claude-plugin/**`, `.agents/plugins/**`, and
`plugins/tilly-engineer-skills/**`. Remove them only when they are TES-owned,
generated, or empty. If any path is ambiguous, modified, non-TES, or
secret-like, preserve it, back it up under `.tes/bk/**`, write review evidence,
and return `NEEDS_REVIEW`.

### Cursor

Apply clean runtime assets after central backup:

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

It must route to `docs/agents/**` and mention `docs/agents/cortex/**` as the durable memory layer when relevant.

## Phase 5.5 - Activate Cortex MCP

Activate the read-only Cortex MCP server for every runtime selected by the route. This resolves Cortex being present but unreachable from MCP-capable agents.

Use the package contract from:

```text
docs/mesh/CORTEX-MCP.md
```

The activation writes only project-scoped local assets:

```text
.tes/bin/cortex.py
.tes/bin/cortex_mcp.py
.tes/bin/cortex_embed.mjs
.tes/bin/field_reports.py
.tes/bin/tes_update.py
.tes/bin/tes_legacy_retirement.py
.tes/bin/root_context.py
.codex/config.toml        # Codex route only
.mcp.json                 # Claude Code route only
.cursor/mcp.json          # Cursor route only
```

Do not write global configuration under the user's home directory. Do not add tokens, env files, hooks, background daemons, cloud config, or write-capable MCP tools.

If this package's local scripts are available, prefer:

```bash
python3 scripts/install_mcp.py --target <target-root> --adapter <codex|claude|cursor|all> --yes
python3 scripts/install_mcp.py --self-test
```

If the scripts are not available, create the equivalent project-scoped files directly from this prompt and `docs/mesh/CORTEX-MCP.md`.

Minimum config shapes:

Codex project config at `.codex/config.toml`:

```toml
[mcp_servers.tes-cortex]
command = "python3"
args = [".tes/bin/cortex_mcp.py", "--target", "."]
cwd = "."
startup_timeout_sec = 10
tool_timeout_sec = 60
enabled = true
```

Claude Code project config at `.mcp.json`:

```json
{
  "mcpServers": {
    "tes-cortex": {
      "type": "stdio",
      "command": "python3",
      "args": [".tes/bin/cortex_mcp.py", "--target", "."],
      "env": {}
    }
  }
}
```

Cursor project config at `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "tes-cortex": {
      "type": "stdio",
      "command": "python3",
      "args": [
        "${workspaceFolder}/.tes/bin/cortex_mcp.py",
        "--target",
        "${workspaceFolder}"
      ],
      "env": {}
    }
  }
}
```

If a config file already exists, merge only the `tes-cortex` server entry. If that server name exists with different content, stop with `NEEDS_REVIEW` unless the user explicitly authorizes overwrite. Backups are required for overwrites.

## Phase 6 - Evidence Journal

Create a concise installation evidence file:

```text
docs/agents/evidence/YYYY-MM-DD-tes-context-installation.md
```

Include:

- detected runtime and selected adapter menu choice;
- navigation library, renderer, mode, and selected route commands;
- project classification;
- source package URL, raw paths used, source package commit, remote `main` commit when available, and `source_freshness`;
- files created;
- files retrofitted or updated;
- clean backup id and restore command;
- root context gate result and semantic recovery evidence;
- full changed-file inventory from `git status --short --untracked-files=all`, grouped as new TES surfaces, updated existing mesh files, generated evidence, local runtime config, and ignored local state;
- conflicts discovered and how they were resolved;
- local rules recovered from backup evidence or marked `NEEDS_REVIEW`;
- Cortex files created, retrofitted, skipped, or deferred;
- MCP files created, merged, skipped, or blocked;
- oracles run and results;
- final GO/NO-GO.

If the user asks for a detailed reconstruction journal, also create a root `JORNAL-TES.md` or a project-appropriate journal path. Do not create it by default unless the user asks.

## Phase 7 - Certification

Run the smallest safe local oracles.

Always try:

```bash
git diff --check
```

If this package is available locally, also run the package surface gates:

```bash
python3 scripts/tes_init.py --self-test
python3 scripts/project_context_oracle.py --self-test
python3 scripts/root_context.py --self-test
python3 scripts/tes_legacy_retirement.py --self-test
python3 scripts/install_smoke.py --self-test
python3 scripts/platform_surface_oracle.py --self-test
```

Package self-tests report `self_test_mode=package` and certify the source-package
contract. Installed helper self-tests report `self_test_mode=installed` and
certify only the materialized helper contract. When package source is not
available, use installed helper self-tests instead of claiming package-source
coverage:

```bash
python3 .tes/bin/root_context.py --self-test
python3 .tes/bin/tes_update.py --self-test
```

After adapter/Cortex/MCP writes are complete and the user authorized local initialization, run the project initializer to recertify and register the target project:

```bash
python3 scripts/tes_init.py --target <target-root> --yes
python3 scripts/project_context_oracle.py --target <target-root>
```

This writes `docs/agents/PROJECT-REGISTER.md`,
`docs/agents/PROJECT-CONTEXT.md`, and timestamped evidence such as
`docs/agents/evidence/YYYYMMDDTHHMMSSZ-tes-project-manifest.json`. The
initializer writes provisional register/context files before later gates, so a
slow or blocked oracle must leave auditable `NEEDS_REVIEW` evidence instead of
leaving the project uninitialized. It must not bulk-absorb project files into
Cortex or write to `sources/**`. It also installs the local Field Reports
`pre-push` drain and local Git hygiene excludes when the target is a Git
repository, and must report `BLOCKED` instead of pretending activation.
The project-context oracle is the executable quality gate for the generated
project map. It must pass before the report claims `Project context: PASS`; if
it fails, report `Project context: NEEDS_REVIEW` and include the missing
anchors, territories, scripts, or explicit unknowns in evidence.
Passing the oracle proves the scaffold contract, not reviewer-grade semantic
mastery; the agent must still report whether semantic refinement was completed,
blocked, or left as next work.

If Codex skill is present:

```bash
python3 .agents/skills/tes-engineering-discipline/scripts/discipline_oracle.py --self-test
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

If TES Cortex MCP is activated:

```bash
test -f .tes/bin/cortex_mcp.py
python3 .tes/bin/cortex_mcp.py --self-test
test -f .codex/config.toml || test -f .mcp.json || test -f .cursor/mcp.json
```

If the target is already an Obsidian vault, `.obsidian/**` may exist. Record that it was pre-existing and do not edit it. If the vault is also a Git repo, verify no Obsidian config drift with:

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

Project quality gates are part of GO, not optional polish. If `package.json`,
Makefile, CI config, or project docs expose safe `lint`, `typecheck`, `test`,
`build`, `contract`, `validate`, or CI-equivalent gates, run the relevant local
commands before final report. If a command needs database, Docker, secrets,
network, destructive writes, or long runtime, name the precondition and report
that gate as `BLOCKED` or `NEEDS_REVIEW` with the reason. Do not hide skipped
quality gates under `Limits` while claiming `GO`.

Do not run multiple build commands in parallel when they share caches.

Before writing the final user-facing report, compare the report's changed-file summary with `git status --short --untracked-files=all`. If files changed by the installer are absent from both the final report and the evidence journal, mark completion `NEEDS_REVIEW` until the inventory is corrected. The report may stay compact, but it must not hide existing bootloaders, adapter docs, or governance files that were retrofitted.

## Phase 8 - Commit And Publication Boundary

The default endpoint is a meshed working tree plus certification report. Do not continue into Git mutation unless the user explicitly asks after reading the report.

The final report must always expose the PT/EN/ES user manual. Prefer a clickable link or plain path, depending on runtime support:

```text
User Manual
- Web: https://murillodutt.github.io/tilly-engineer-skills/install/USER-MANUAL.html
- Local package path: docs/install/USER-MANUAL.html  # when this package is available locally
```

Do not make automatic browser opening part of certification. If the current runtime can safely open local files or URLs and the user asks for it, opening the manual is allowed as a convenience after the report. Otherwise, exposing the link/path is the required behavior.

Step Zero is the only exception: a local pre-install baseline commit can be created before installation so the user can safely undo the install.

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

Finish with a professional certification report. The user's report must be short factual prose with compact bullets. Do not use Markdown tables unless the user explicitly asks for the full evidence view. Put long inventories, detailed oracles, conflicts, and reconstruction notes in the evidence file. In the chat, show only status, scope, snapshot freshness, main changed surfaces, Field Reports state, helper set, gates, manual, rollback, and honest limits.

Use this structure. This is snapshot certification when freshness is `STALE_SOURCE`; do not claim the latest source was certified. When installing from a public bundle whose source commit is an ancestor of the distribution commit on remote `main`, report `PASS` with meaning `current public bundle`.

```text
TES Context Mesh Convergence Report

Status: GO | NEEDS_REVIEW | NO-GO
Scope: <install | retrofit | update | audit>
Runtime and adapters: <...>
Completion Claim: GO meshed | GO committed | GO published | NEEDS_REVIEW | NO-GO
Navigation: <library, renderer, mode>

Source Snapshot
- Package commit: <source_package_commit>; remote main: <source_remote_head | unknown>
- Freshness: PASS | STALE_SOURCE | BLOCKED; meaning: <latest | current public bundle | snapshot-only | unknown>

Changed Surfaces
- New TES surfaces: <short list or none>
- Updated existing mesh files: <short list or none>
- Clean backup: <.tes/bk/<timestamp>/manifest.json | none>; restore: <command>
- Semantic recovery: RECOVERED | NEEDS_REVIEW | SKIP; evidence: <path | none>
- Root context gate: PASS | RECOVERED | NEEDS_REVIEW | SKIP; plan/resolution: <path | backup recovery | none>
- Installed helper set: cortex.py, cortex_mcp.py, cortex_embed.mjs, scope_contract.py, event_ledger.py, checkpoint.py, consolidation_gate.py, field_reports.py, tes_update.py, tes_legacy_retirement.py, root_context.py, tes_init.py, project_context_oracle.py: PASS/BLOCKED/MISSING
- Helper contract parity: PASS | STALE_HELPERS | BLOCKED | NOT_INSTALLED
- Project context: docs/agents/PROJECT-CONTEXT.md PASS | NEEDS_REVIEW | SKIP
- Continuation plan: NONE | READY | PENDING_APPROVAL; required phases: <short list>
- Runtime/MCP config, evidence, ignored local state: <short list>

Certification
- Context, project register, project context, thin runtime assets, Cortex, MCP, platform surfaces, Obsidian boundary, secrets, and oracles: PASS/FAIL/SKIP
- Project quality gates: PASS | BLOCKED | NEEDS_REVIEW | NOT_APPLIED; commands run or reason: <lint/typecheck/test/build/CI details>
- Field Reports: PASS | BLOCKED | DISABLED | SKIP; hook/drain/sentinel/outbox pending count: <...>
- `/tes-update` routine: PASS | BLOCKED | SKIP; route probe and post-Layer Zero final Field Reports `tes_update` event: <...>

Evidence
- <docs/agents/evidence/...>
- <journal when created>

User Manual
- Web: https://murillodutt.github.io/tilly-engineer-skills/install/USER-MANUAL.html
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
- root runtime context was backed up before clean overwrite and semantic recovery evidence exists, or root context was explicitly absent;
- read-only Cortex MCP is activated for selected routes or explicitly blocked;
- Field Reports state and installed helper set are explicit in the report;
- helper contract parity is PASS or NOT_INSTALLED; `STALE_HELPERS` cannot close as GO;
- runtime trigger parity is PASS or NOT_APPLIED; `DRIFT` cannot close as GO;
- discovered safe project quality gates such as lint, typecheck, test, build,
  contract, validate, or CI-equivalent commands passed, or unsafe/unavailable
  gates are explicitly `BLOCKED` or `NEEDS_REVIEW` with reasons;
- final `tes_update` evidence is recorded when Field Reports is installed;
- if Layer Zero copied helpers, final `tes_update` evidence must be recorded after the overwrite and must show `helper_contract_status=PASS`, `runtime_trigger_status=PASS` or `NOT_APPLIED`, `update_available=False`, and `recommended_update_scope=none`;
- when Field Reports drains through the silent pre-push hook, verify `field_reports.py status` or `.tes/field-reports/receipts/**` before claiming that no upstream issue was created;
- if helper files were copied but hook/drain status is unknown, use `NEEDS_REVIEW`;
- context was recovered or explicitly absent, no secrets changed, and at least one oracle passed.

Use `NEEDS_REVIEW` when the integration is structurally sound but user review is required before overwrite/merge/commit. Use `NO-GO` when context would be lost, secrets are at risk, or local validation fails.
