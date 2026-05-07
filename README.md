# Tilly Engineer Skills

Install a durable agent-governance mesh for Codex, Claude Code, and Cursor.

Tilly Engineer Skills helps coding agents work with less ambiguity, less
overbuilding, fewer drive-by edits, and clearer proof before they claim a task
is done.

Version: `0.3.16`

License: MIT

## Install First

For the structured user guide in English, Spanish, and Portuguese, open:

```text
docs/install/USER-MANUAL.html
```

Open your target project in Codex, Claude Code, or Cursor. When the Tilly init
skill or rule is available, type:

```text
/tilly:init
```

That shortcut is the preferred entrypoint. It expands to the assisted installer
workflow below. If the shortcut is not available yet, paste the full prompt:

```text
Install Tilly Engineer Skills as an assisted context mesh, not as blind file
copying.

Read and follow this raw installer spec:

https://raw.githubusercontent.com/murillodutt/tilly-engineer-skills/main/docs/install/ASSISTED-CONTEXT-INSTALLER.prompt.md

Run in quiet installer mode: show compact progress, blockers and the final
certification report only. When navigation is required, load the runtime
navigation library from the spec, use native structured cards only when the
current runtime safely supports them, otherwise render command navigation.
Ask for a route command such as current, codex, claude, cursor, all, mcp, or audit.
Do not display internal reasoning, scratch YAML or long inventories.

Start by detecting the current IDE/runtime and classifying this project as new,
existing, or meshed. If Tilly is already meshed, treat this as an assisted
update/convergence run, not a reinstall. Use the detected IDE as the default
adapter. Ask me for a route command only where the spec requires one. Preserve
local project governance, move durable agent context into docs/agents/** when
needed, create or update the compiled docs/agents/cortex/** Cortex layer, keep
AGENTS.md, CLAUDE.md and Cursor rules as thin runtime bootloaders, activate the
read-only project-scoped Cortex MCP server for the selected runtime route, and
finish with the certification report required by the spec. The final report
must expose the user manual link/path.

Before installation edits, run Step Zero from the spec: inspect Git status and
offer a local baseline commit if the working tree is dirty. At the end, tell me
how to undo the installation with Git.
```

The assisted installer protects the project before editing. If the working tree
is dirty, it offers a local baseline commit first, then reports rollback
commands such as:

```bash
git reset --hard <baseline-head>
git revert <install-commit>
```

The installer must not push, amend, tag, publish, install dependencies,
overwrite files, or change remotes unless the user explicitly asks after
reviewing the certification report.

## What This Solves

Agent instructions tend to rot in root files, diverge between tools, and become
hard to audit. Tilly installs a local context mesh instead:

```text
docs/agents/** is source. Runtime assets route and execute.
```

That means project governance lives in one durable place, Cortex gives the
project a compiled memory layer at `docs/agents/cortex/**`, and
`AGENTS.md`, `CLAUDE.md`, `.cursor/rules/**`, `.agents/**`, and future runtime
assets stay thin.

Cortex memory lives in versioned Markdown artifacts: `sources/**`, `cells/**`,
`MAP.md`, `TRAIL.md`, `LINKS.md`, and `CONTRACT.md`. SQLite FTS5 is only the
derived recall index at `.tilly/cortex/recall.sqlite`; semantic curation uses a
derived `.tilly/cortex/semantic.sqlite` index rebuilt from `cells/**`; `rg` is
the fallback.
Obsidian is a compatible visual surface; the installer does not create or edit
`.obsidian/**`, require plugins, or depend on editor state for certification.
The read-only Cortex MCP server is activated through project-scoped runtime
config, never global config.

## Execution Model

The executor is the active coding agent inside the current IDE or runtime
context window. Codex, Claude Code, Cursor, or another supported agent reads
the mesh, chooses the route, edits files, invokes available local tools, and
reports certification.

The Python scripts and `npm run ...` entries are deterministic oracles and
portable helper tools for that agent. Skills, rules, bootloaders, and adapter
files route behavior and explain when those oracles should be used. Hooks are
local Git gates for validation, no-write Cortex reflection/curation, and Field
Reports drain. MCP is
a read-only Cortex access surface for agents; it is not the memory and not the
installer.

`/tilly:init` is the standard user-facing shortcut for initialization, update,
audit, and recertification. Where a runtime supports skills, it maps to the
`tilly-init` skill. Where it does not, rules and bootloaders should treat the
same phrase as an intent that loads the assisted installer contract.

The broader shortcut surface is intentionally small:

| Shortcut | Intent |
|----------|--------|
| `/tilly:init` | install, update, audit, or recertify Tilly in a project |
| `/tilly:cortex` | query, inspect, audit, rebuild, curate, learn, reflect, or apply Cortex memory |
| `/tilly:curate` | run no-write semantic curation over Cortex memory |
| `/tilly:mcp` | activate or verify read-only Cortex MCP |
| `/tilly:field-reports` | inspect, drain, disable, or re-enable sanitized operational reports |
| `/tilly:doctor` | run health, certification, and commit-readiness gates |
| `/tilly:adapter` | materialize, dry-run, retrofit, or install adapter surfaces |
| `/tilly:bench` | plan, run, or converge context-mesh benchmarks |

See `docs/install/COMMAND-TRIGGERS.md` for the full command-to-trigger matrix.
Field Reports is active by default and sends only sanitized operational facts
to the TES GitHub issue tracker on push. Privacy and opt-out prompts are in the
user manual.

When a runtime has no shell/tool access, the agent must not pretend a command
ran. It should complete the file work it can safely perform, mark unavailable
oracles as `BLOCKED` or `SKIP` with a reason, and ask for the smallest native
equivalent or user-run command only when certification depends on it.

When this package is available locally, `tilly_init.py` is the project
initialization and recertification command. It verifies package health, scans
the target project, writes `docs/agents/PROJECT-REGISTER.md`, and stores a full
manifest under `docs/agents/evidence/**`. Cortex can also be initialized and
checked directly:

```bash
python3 scripts/tilly_init.py --target /path/to/project --yes
python3 scripts/tilly_init.py --self-test
python3 scripts/field_reports.py status --target /path/to/project
python3 scripts/field_reports.py --self-test
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
python3 scripts/cortex_mcp.py --target /path/to/project-or-vault
python3 scripts/install_mcp.py --target /path/to/project --adapter all --yes
python3 scripts/install_mcp.py --self-test
```

## Business Value

| Outcome | Practical gain |
|---------|----------------|
| Faster onboarding | New projects get an agent-ready governance mesh in one assisted flow. |
| Safer retrofits | Existing instructions are migrated instead of blindly overwritten. |
| Less context drift | Codex, Claude, and Cursor point to the same project truth. |
| Better execution | Agents are pushed to expose assumptions, reduce scope, edit surgically, and verify. |
| Compounding memory | Cortex keeps immutable sources separate from compiled, versioned cells. |
| Easier rollback | Step Zero creates or records a Git baseline before installation changes. |
| Audit-ready reports | Every install, retrofit, update, or audit run ends with a certification report and explicit non-claims. |

## Core Method

Every non-trivial coding, review, refactor, or instruction-migration task must
pass four gates:

| Gate | Blocks |
|------|--------|
| Think Before Coding | Silent assumptions, hidden confusion, wrong interpretation |
| Simplicity First | Overbuilt APIs, speculative features, one-use abstractions |
| Surgical Changes | Drive-by edits, style churn, unrelated cleanup |
| Goal-Driven Execution | Vague closure, missing tests, "make it work" loops |

The operating contract is short:

```text
Assumptions visible. Scope smaller. Edits surgical. Success falsifiable.
```

## Why It Is Different

Tilly is not a file copier and not a prompt dump. The assisted installer:

1. Detects the active runtime.
2. Classifies the project as new, existing, or meshed.
3. Protects the working tree with Step Zero.
4. Preserves local product governance.
5. Moves durable context into `docs/agents/**`.
6. Creates `docs/agents/cortex/**` as the compiled Cortex memory layer.
7. Leaves runtime files as thin bootloaders.
8. Runs the smallest safe local oracles.
9. Produces a professional certification report.

Navigation is also runtime-aware. Claude Code can use `AskUserQuestion` when
available, Codex can use `request_user_input` when the active schema supports
it, Cursor can use native/ACP question tools when exposed, and every platform
has a command-navigation fallback.

## Compatibility

| Runtime | Installed surface |
|---------|-------------------|
| Codex | `AGENTS.md` and `.agents/skills/**` |
| Claude Code | `CLAUDE.md`, Claude-scoped rules, plugin or skill assets when appropriate |
| Cursor | `.cursor/rules/*.mdc` |
| Shared mesh | `docs/agents/**` |
| Cortex memory | `docs/agents/cortex/**` |

Different tools do not need identical text. They need equivalent routing to the
same project contract.

## Certification Output

Every assisted install, retrofit, update, or audit run finishes with:

```text
Tilly Context Mesh Convergence Report

Status: GO | NEEDS_REVIEW | NO-GO
Scope: new project install | existing project retrofit | meshed project update | audit
Detected Runtime: Codex | Claude Code | Cursor | uncertain
Selected Adapters: ...
Canonical Source: docs/agents/**
Cortex: docs/agents/cortex/**
Navigation Library: ...
Navigation Renderer: ...
Navigation Mode: ...
Integration Matrix: ...
Certification: ...
Evidence: ...
User Manual: ...
Rollback: ...
Limits: ...
Next Step: ...
```

GO means the selected integration was meshed, routed, and locally checked.
It does not mean the integration was committed, pushed, published, or proven
universal across every model and project.

## Evidence-Converged Context

The package follows one principle:

```text
Context only becomes contract when it converges by evidence.
```

Instructions are not accepted as project truth because they are well written.
They earn authority when they produce measurable lift, survive distractors,
show ablation loss, keep raw evidence, and converge through build-test-fix
loops.

## Repository Shape

Root is intentionally thin. Source belongs in `src/**`; method, install, and
evaluation material belongs in `docs/**`.

| Path | Purpose |
|------|---------|
| `AGENTS.md` | Thin bootloader for agents working in this repository |
| `src/adapters/codex/**` | Codex bootloader and skill source |
| `src/adapters/claude/**` | Claude instruction, plugin, and legacy skill source |
| `src/adapters/cursor/**` | Cursor guide and always-on rule source |
| `docs/install/**` | Assisted installer prompt, navigation library, and install docs |
| `docs/mesh/**` | Principles, context mesh method, and scorecard |
| `docs/evals/**` | Eval design and examples |
| `docs/governance/**` | Cross-tool alignment, authority, and no-go rules |
| `docs/adapters/**` | Human adapter guidance |
| `docs/architecture/**` | Repository structure and ownership |
| `docs/tds/**` | Documentation contract and governed index |
| `benchmarks/context-mesh/eval-dataset.json` | Starter eval dataset |
| `scripts/**` | Deterministic package checks |
| `dist/adapters/**` | Generated install trees, ignored by Git |

Start with [docs/INDEX.md](docs/INDEX.md) for the complete documentation map.

## Legacy / Maintainer Install

Manual install is for package maintainers, controlled packaging, and adapter
debugging. Real target projects should use the assisted context installer so
existing governance is preserved and migrated into `docs/agents/**`.

### Codex

1. Copy or merge `src/adapters/codex/AGENTS.md` into the target repository
   root `AGENTS.md`.
2. Copy `src/adapters/codex/skills/tilly-engineering-discipline/` into the
   target repository's `.agents/skills/tilly-engineering-discipline/`.
3. Run this package's validation locally before distributing changes:

```bash
npm run validate
```

Codex should load `AGENTS.md` as persistent repo guidance and discover the skill
through metadata. The skill body and references load only when the task needs
them.

### Claude Code

Use `src/adapters/claude/CLAUDE.md` as the target root instruction file, or use
the plugin metadata in `src/adapters/claude/plugin/` when packaging for Claude.

### Cursor

Copy `src/adapters/cursor/rules/tilly-guidelines.mdc` into the target repo's
`.cursor/rules/` directory. It uses `alwaysApply: true` because the four gates
are a behavioral overlay.

## Local Development

This repository is optimized for local-only commits:

```bash
npm run validate
npm run tds:validate
npm run cortex:self-test
npm run cortex:mcp:self-test
npm run mcp:self-test
npm run field-reports:self-test
npm run install:smoke
npm run tilly:init -- --target /path/to/project --yes
npm run tilly:init:self-test
npm run claude:plugin:oracle
npm run platform:surface:check
npm run retention:check
npm run reference:graph
npm run docs:size
npm run materialize:check
npm run benchmark:plan
npm run commit:check
```

To create an explicit local context-mesh evidence run without paid backends:

```bash
npm run benchmark:run -- --backend fixture
```

`commit:check` is stricter than `validate`: required package files must be
staged or already tracked, which prevents local hooks from passing with
critical new files left outside the commit.

To generate installable adapter trees:

```bash
npm run materialize:all
```

The generated output lands in `dist/adapters/**`. Do not edit it directly; edit
`src/adapters/**` and materialize again.

The local Git hook in `.githooks/pre-commit` runs the same package checks before
commit. No remote or publishing flow is configured by default.
