---
tds_id: install.adapter_installer
tds_class: adapter
status: active
consumer: adopters and release operators
source_of_truth: true
evidence_level: L2
tver: 0.9.3
---

# Adapter Installation

The primary installer is an assisted context prompt. It uses the target
project's active LLM window to inspect local governance, create or retrofit
`docs/agents/**`, keep runtime files thin, and certify the integration.

For a practical user-facing walkthrough in Portuguese, English, and Spanish,
open:

```text
docs/install/USER-MANUAL.html
```

The script installer remains as a maintainer tool for materialization smoke
tests and mechanical copying. It is not the recommended path for projects that
already have agent instructions.

## Primary Flow

Open the target project in Codex, Claude Code, or Cursor and paste:

```text
Install Tilly Engineer Skills as an assisted context mesh, not as blind file
copying.

Read and follow this raw installer spec:

https://raw.githubusercontent.com/murillodutt/tilly-engineer-skills/main/docs/install/ASSISTED-CONTEXT-INSTALLER.prompt.md

Start by detecting the current IDE/runtime and classifying this project as new,
existing, or meshed. If Tilly is already meshed, treat this as an assisted
update/convergence run, not a reinstall. `/tes:update` means "Atualizar a
Tilly" and should run the update probe before route selection. Run in quiet
installer mode: show
compact progress, blockers and the final certification report only. When
navigation is required, load the runtime navigation library from the spec, use
native structured cards only when the current runtime safely supports them,
otherwise render command navigation. Ask for a route command such as current,
codex, claude, cursor, all, mcp, or audit. Use the detected IDE as the default
adapter. Ask me for a route command only where the spec requires one.
Preserve local project governance, move durable agent context into
docs/agents/**, keep AGENTS.md, CLAUDE.md and Cursor rules as thin runtime
bootloaders, activate the read-only project-scoped Cortex MCP server for the
selected runtime route, and finish with the certification report required by the spec.
The update probe must be read-only by default, verify installed/cloud versions,
helper contract parity, and `recommended_update_scope`; `STALE_HELPERS` is
update-required, not `CURRENT`. For `recommended_update_scope=helpers-only`,
replace only TES-owned `.tes/bin/**` helpers with backups on the selected Layer
Zero route, rerun the update probe, then continue only after parity is PASS.
Use `--record-field-report` only on the final certification probe. After any
helper overwrite, that final recorded probe is mandatory before GO, evidence
closeout, commit, or push, and it must show `helper_contract_status=PASS`,
`update_available=False`, and `recommended_update_scope=none`.
The final report must expose the user manual link/path.

Before installation edits, run Step Zero from the spec: inspect Git status and
offer a local baseline commit if the working tree is dirty. At the end, tell me
how to undo the installation with Git. Do not push, amend, tag, publish, install
dependencies, overwrite files, or change remotes unless I explicitly ask after
reviewing the certification report.
```

Short source:

```text
docs/install/MINI-PROMPT.md
```

Full raw spec:

```text
docs/install/ASSISTED-CONTEXT-INSTALLER.prompt.md
```

## Install Semantics

The context installer is not a file copier. It performs:

```text
environment detection
  -> new, existing, or meshed project classification
  -> runtime navigation library
  -> adapter menu
  -> docs/agents/** canonical mesh
  -> docs/agents/cortex/** memory layer
  -> thin runtime assets
  -> project-scoped Cortex MCP activation
  -> evidence journal
  -> certification report
```

## Compatibility Basis

The installer follows current adapter surfaces:

| Tool | Install Surface |
|------|-----------------|
| Codex | `AGENTS.md` and `.agents/skills/**` |
| Claude Code | `CLAUDE.md`, `.claude-plugin/**`, and `skills/**` |
| Cursor | `.cursor/rules/*.mdc` project rules |

The common pattern is file-based installation into the target repository, but
project-specific governance belongs in `docs/agents/**`.

Cortex is the default compiled memory layer under `docs/agents/cortex/**`.
Memory lives in versioned artifacts: immutable `sources/**`, compiled
`cells/**`, `MAP.md`, `TRAIL.md`, `LINKS.md`, and `CONTRACT.md`. SQLite FTS5 at
`.tes/cortex/recall.sqlite` is a derived recall index, never memory, and `rg`
is the fallback. `.tes/cortex/semantic.sqlite` is a derived curation index,
also never memory, rebuilt by `curate-plan` from `cells/**`.

Cortex is Obsidian-compatible plain Markdown. The installer does not create
`.obsidian/**`, require community plugins, or depend on Obsidian state for
certification.

Cortex MCP is activated by default for selected runtime routes. It remains
read-only and project-scoped. The installer may write `.tes/bin/cortex.py`,
`.tes/bin/cortex_mcp.py`, `.tes/bin/cortex_embed.mjs`,
`.tes/bin/field_reports.py`, `.tes/bin/tes_update.py`,
`.tes/bin/tes_legacy_retirement.py`,
`.tes/bin/root_context.py`,
`.codex/config.toml`, `.mcp.json`, and
`.cursor/mcp.json`; MCP activation must not edit global MCP configuration,
secrets, hooks, or write-capable MCP tools.

TES Field Reports is active by default. The initializer installs a local
`pre-push` drain for sanitized operational facts, stores pending state under
`.tes/field-reports/**`, never sends project code or private paths, and
documents opt-out and reactivation prompts in the user manual.

When the target is a Git repository, Tilly also maintains local artifact hygiene
in `.git/info/exclude`. Rollback backups, Python bytecode, Field Reports state,
and Cortex SQLite caches are excluded from normal staging; `.tes/bin/*.py`
helpers are not excluded because they are the installed runtime surface.

When this package is available locally, `tes_init.py` is the project
initialization and recertification command. It verifies package health, scans
the target project, writes `docs/agents/PROJECT-REGISTER.md`, and stores a full
manifest under `docs/agents/evidence/**`. Cortex can also be initialized and
checked directly:

The register is written before slower certification gates finish. If a later
oracle is blocked or times out, the run closes as `NEEDS_REVIEW` with local
evidence instead of leaving the project unregistered.

```bash
python3 scripts/tes_init.py --target /path/to/project --yes
python3 scripts/tes_init.py --self-test
python3 scripts/tes_update.py plan --target /path/to/project --json-only
python3 scripts/tes_update.py plan --target /path/to/project --json-only --record-field-report
python3 scripts/field_reports.py status --target /path/to/project
python3 scripts/field_reports.py --self-test
python3 scripts/cortex.py init --target /path/to/project-or-vault
python3 scripts/cortex.py verify --target /path/to/project-or-vault
python3 scripts/cortex.py audit --target /path/to/project-or-vault
python3 scripts/cortex.py rebuild --target /path/to/project-or-vault
python3 scripts/cortex.py curate-plan --target /path/to/project-or-vault --backend lexical
```

Project-scoped MCP can be installed and checked with:

```bash
python3 scripts/install_mcp.py --target /path/to/project --adapter codex --yes
python3 scripts/install_mcp.py --target /path/to/project --adapter all --yes
python3 scripts/install_mcp.py --self-test
```

Use the first `tes_update.py plan --json-only` form for inspection. It is
read-only and must not write Field Reports. Use
`--record-field-report` only for the final certification probe. When the probe
returns `recommended_update_scope=helpers-only`, run Layer Zero with
`install_mcp.py --helpers-only` before adapter or MCP config activation.
After Layer Zero, record the final proof with
`tes_update.py plan --json-only --record-field-report` before commit or push.
Self-tests run from `scripts/**` certify the package source contract; self-tests
run from `.tes/bin/**` certify the installed helper contract.

Navigation is runtime-aware. The installer declares menus as intent, loads
`docs/install/navigation/common.prompt.md`, then loads the renderer for Codex,
Claude Code, or Cursor. Native cards are used only when the active runtime
supports them safely; command navigation remains the certified fallback.

## New vs Existing Projects

For a new project, the installer creates a minimal `docs/agents/**` mesh and
thin runtime files for the selected IDE.

For an existing project, the installer migrates durable rules from existing
agent files and docs into `docs/agents/**`, then turns `AGENTS.md`, `CLAUDE.md`,
`.cursor/rules/**`, `.claude/**`, and `.agents/**` into runtime assets that
route to the mesh.

Existing context is project-owned by default. Conflicts mean retrofit, not
overwrite.

For a meshed project, the installer treats the run as update/convergence. It
inspects the existing `docs/agents/**` mesh, compares the installed Tilly
version with the cloud package version, detects applied IDE surfaces, recommends
`all`, `codex`, `claude`, `cursor`, or `current`, applies only surgical updates,
preserves local governance, and certifies the resulting state.

## Certification Output

Every assisted install, retrofit, update, or audit run ends with:

```text
TES Context Mesh Convergence Report

Status: GO | NEEDS_REVIEW | NO-GO
Scope: new project install | existing project retrofit | meshed project update | audit
Detected Runtime: Codex | Claude Code | Cursor | uncertain
Selected Adapters: ...
Canonical Source: docs/agents/**
Cortex: docs/agents/cortex/**
Navigation Library: ...
Navigation Renderer: ...
Navigation Mode: ...
Source Snapshot: package commit, remote main, freshness
Changed Surfaces: new surfaces, updated existing mesh files, runtime config
Rollback Backups: short list or none; .bak-* files are rollback artifacts, not new surfaces
Root Context Gate: PASS | PRESERVED | NEEDS_REVIEW | SKIP
Installed Helper Set: cortex.py, cortex_mcp.py, cortex_embed.mjs, field_reports.py, tes_update.py, tes_legacy_retirement.py, root_context.py
Field Reports: PASS | BLOCKED | DISABLED | SKIP, with pending outbox count
Certification: compact PASS/FAIL/SKIP bullets
Evidence: ...
User Manual: ...
Rollback Summary: reset baseline plus clean installer-created files
Limits: ...
Next Step: ...
```

The chat report is deliberately short. Detailed inventories, conflicts,
oracles, and reconstruction notes belong in the evidence file. A report must
not use tables by default, and it must not hide files changed by the installer.
Before closing, compare the changed-file summary against
`git status --short --untracked-files=all`. Do not collapse Field Reports into a
generic gate: the report must say whether the hook/drain is `PASS`, `BLOCKED`,
`DISABLED`, or `SKIP`.
Because the pre-push hook drains silently, confirm created upstream reports by
checking `field_reports.py status` or `.tes/field-reports/receipts/**` after
push.

GO requires canonical `docs/agents/**`, a created or explicitly deferred
Cortex layer, selected-runtime Cortex MCP activation or a named blocker, thin
runtime assets, root context migrated or preserved before overwrite, no blind
overwrite, no secret mutation, and at least one relevant local oracle.
`PRESERVED` is a passing root-context state only when project-owned bootloaders
were intentionally left untouched; it remains a blocker for overwrites.
If the raw root context analyzer says `NEEDS_REVIEW` and the installer did not
overwrite roots, the final report should say `PRESERVED`, not `FAIL`.

Source freshness is part of certification metadata. If the package snapshot
commit differs from the current `main` commit for
`murillodutt/tilly-engineer-skills`, the install may still be `GO meshed` for
that snapshot, but it must be labeled `STALE_SOURCE` and must not claim latest
Tilly Engineer Skills certification.

GO does not imply the integration was committed or pushed. The certification
report must distinguish:

| Claim | Meaning |
|-------|---------|
| `GO meshed` | Mesh files were created, retrofitted, or updated and local oracles passed. |
| `GO committed` | The user explicitly approved commit after reviewing the report. |
| `GO published` | The user explicitly approved push or publication after commit. |

Every report must expose the user manual:

```text
User Manual
- Web: https://github.com/murillodutt/tilly-engineer-skills/blob/main/docs/install/USER-MANUAL.html
- Local package path: docs/install/USER-MANUAL.html
```

Automatic browser opening is optional convenience only. It is not required for
certification because not every runtime can safely open local files or browser
tabs.

Every report must include rollback guidance. If the install is uncommitted, the
standard undo command is:

```bash
git reset --hard <baseline-head>
```

If the install was committed separately, prefer:

```bash
git revert <install-commit>
```

## Script Support

The script remains available for maintainers, package checks, and low-risk
mechanical smoke tests.

Dry-run all adapters into a target project:

```bash
python3 scripts/install_adapter.py --target /path/to/project --dry-run
```

Install all adapters:

```bash
python3 scripts/install_adapter.py --target /path/to/project --yes
```

Install one adapter:

```bash
python3 scripts/install_adapter.py --adapter codex --target /path/to/project --yes
python3 scripts/install_adapter.py --adapter claude --target /path/to/project --yes
python3 scripts/install_adapter.py --adapter cursor --target /path/to/project --yes
```

Retire known legacy runtime before an update:

```bash
python3 scripts/tes_legacy_retirement.py plan --target /path/to/project
python3 scripts/tes_legacy_retirement.py apply --target /path/to/project --yes
python3 scripts/tes_legacy_retirement.py audit --target /path/to/project
```

The gate archives legacy retrofit records from `.tilly/retrofit/**` under
`.tes/legacy-retirement/retrofit/**`; these records must not block runtime
retirement when all other legacy paths are known.

macOS/Linux wrapper:

```bash
./install.sh --adapter codex --target /path/to/project --dry-run
```

Windows PowerShell wrapper:

```powershell
.\install.ps1 --adapter codex --target C:\path\to\project --dry-run
```

## Conflict Policy

If a target file exists and differs, installation stops before copying files.
This protects existing project instructions.

Allowed responses:

| Need | Command |
|------|---------|
| See what would happen | `--dry-run` |
| Generate an LLM merge plan | `--retrofit-plan` |
| Replace conflicting files with backups | `--overwrite --yes` |
| Replace without backups | `--overwrite --no-backup --yes` |

`--overwrite` creates `.bak-<timestamp>` files by default.
Those backups are local rollback artifacts and must be ignored through
`.git/info/exclude`, not counted as new TES surfaces.

## LLM Retrofit

Use retrofit when a target project already has `AGENTS.md`, `CLAUDE.md`, or
Cursor rules that should be merged instead of replaced:

```bash
python3 scripts/install_adapter.py \
  --adapter codex \
  --target /path/to/project \
  --retrofit-plan
```

The generated file lives under:

```text
/path/to/project/.tes/retrofit/
```

The command still exits with a conflict status because no install was applied.
That is intentional: retrofit is a merge plan, not a silent write.

Give that file to an LLM or human reviewer. The merge instruction is to add the
Tilly discipline while preserving project-local commands, paths, tests,
ownership, security constraints, and existing agent rules.

## Security Boundaries

- No remote script execution.
- No package manager install.
- No hooks, background agent, cloud, secret changes, global MCP config, or
  write-capable MCP tools.
- Project-scoped read-only Cortex MCP config is allowed only through the
  selected route and explicit installer report.
- No overwrite without explicit `--overwrite`.
- No non-interactive writes without `--yes`.
- Backups are created before overwrites unless `--no-backup` is set.

## Validation

From this package:

```bash
npm run install:dry-run
npm run mcp:self-test
npm run install:smoke
npm run tes:init -- --target /path/to/project --yes
npm run tes:init:self-test
npm run tes:update -- --target /path/to/project
npm run tes:update:self-test
npm run claude:plugin:oracle
npm run platform:surface:check
npm run retention:check
npm run reference:graph
npm run docs:size
npm run materialize:check
npm run commit:check
```

In a target project, run the target project's own smallest relevant oracle
after installing or merging.
