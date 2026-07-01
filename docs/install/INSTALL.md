---
tds_id: install.adapter_installer
tds_class: adapter
status: active
consumer: adopters and release operators
source_of_truth: true
evidence_level: L2
tver: 0.9.8
---

# Installer Contract

This Markdown file is the technical installer contract for agents and release operators. It is not the first-read user guide. Users should start with the generated manual:

- Web: https://murillodutt.github.io/tilly-engineer-skills/install/USER-MANUAL.html
- Local package path: `docs/install/USER-MANUAL.html`

The public installer path is the GitHub package-spec command through npx or Bun after a fixed ref is authorized and release-certified. Version `0.3.238` is the fixed release identity for this install surface; treat the remote ref as certified only after the tag is published and `npm run release:check` passes.

For the agent-side contract behind runtime commands, gates, schemas, and closure vocabulary after installation, open `docs/install/AGENT-MANUAL.md`.

## GitHub Package-Spec Form

```bash
npx --loglevel=error -y --package github:murillodutt/tilly-engineer-skills#v0.3.238 tilly-engineer-skills add
```

```bash
bunx --silent --bun --package github:murillodutt/tilly-engineer-skills#v0.3.238 tilly-engineer-skills add
```

The interactive installer asks for the target project, agent hooks, install mode, and final confirmation before writing files. `--loglevel=error` keeps package-runner warnings out of the first-run screen while preserving real command failures. `--silent` does the same for Bun's package runner while keeping TES output visible.

For non-interactive installs:

```bash
npx --loglevel=error -y --package github:murillodutt/tilly-engineer-skills#v0.3.238 tilly-engineer-skills add --agent all --yes
```

`#v0.3.238` is the intended fixed-ref form for a release-certified install channel. Do not call that remote ref certified until `npm run release:check` passes after the tag or fixed ref is authorized and available.

During install, update, and clean-runtime refresh, obsolete plugin/root-skill surfaces are removed only when TES-owned/generated/empty; ambiguous content is preserved, backed up under `.tes/bk/**`, and reported as `NEEDS_REVIEW`.

## Runtime Support

TES supports Node.js 18, 20, 22, and newer Node releases through npx. It also supports Bun 1.0 or newer through `bunx --bun`.

If neither `node`/`npm` nor `bun`/`bunx` is available, install one runtime first. TES also requires Python 3.11+ for the local setup engine and oracles:

- Node.js LTS: https://nodejs.org/en/download
- Bun: https://bun.sh/docs/installation
- Python: https://www.python.org/downloads/

After the CLI starts, it checks the active runtime and exits with those install links when the JavaScript runtime or Python runtime is unsupported or unknown.

## Install Semantics

The installer stages a versioned TES bundle, applies runtime capabilities, writes `.tes/tes-install-lock.json` and `.tes/postinstall.json`, then installs first-session hooks.

Hooks call `.tes/bin/tes_install.py hook --agent <agent> --target .` through the Python 3.11+ executable validated by the installer. When the sentinel is `pending`, post-install runs `tes_init.py`, `project_context_oracle.py`, and `project_alignment_oracle.py`, then marks the sentinel `complete` or `needs_review`. Repeated hooks exit quickly. If the sentinel is `needs_review`, `/tes-init` repairs the focused blocker, then runs `tes_install.py postinstall --recover-needs-review`. That reruns Project-Start, records the recovery run, and clears the sentinel only on PASS.

Claude Code receives first-session results as `SessionStart` hook context, not as a normal chat message. TES installs two Claude `SessionStart` handlers: a fast synchronous notice that shows `IMPORTANT: TES setup is running. Please wait; do not start project work.`, then a native `asyncRewake` handler that runs setup without blocking startup and wakes the session when the post-install routine finishes. When it completes, Claude should tell the user: `Please, run /tes-setup for the report.` Claude reads `.tes/postinstall.json` and the latest run record to report `complete`, `running`, or `needs_review`.

Host follow-up differs by platform after hooks are written: Codex may mark the Session Start hook as `needs review` in Settings > Hooks, so inspect, Trust, and enable it before expecting setup to run; Claude Code runs setup through `SessionStart`, so reopen it, wait for the completion notice, then run `/tes-setup`; Cursor reloads `.cursor/hooks.json` on workspace open, so reopen the workspace, let first-session setup complete, then run `/tes-setup`. If the sentinel is already `complete`, `/tes-init` should report current evidence unless the user explicitly asks to recertify. Do not start project work until `install -> hook -> /tes-setup -> /tes-align` has completed; use `/tes-update` for updates, `/tes-doctor` for repair, and `/tes-align` for Markdown mesh refresh.

Release certification gates:

```bash
python3 scripts/tes_npx_oracle.py --self-test
python3 scripts/tes_npx_oracle.py --runtime-matrix
npm run release:check
```

`release:check` is the post-tag remote gate: the fixed GitHub ref must exist, include the public bundle `source_commit`, and dry-run through npm/npx and Bun.

## Compatibility Basis

Per ADR 0004 as amended by the skills-surface line, `install` delivers a **functional default**: capsule (`.tes/**`) plus skills (`root-context` + `skills`), `mcp`, and startup `hooks`. The capsule is a reversible-ownership and non-contamination guarantee, not a materialization cap — every project-visible write is manifest-recorded and reversible (`detach <surface>` restores from backup; `uninstall` removes every surface and the capsule with zero residue). `docs-mesh` stays opt-in. For a minimal install pass an explicit selection (`--attach capsule` for capsule-only). Full surface list: `mcp`, `hooks`, `root-context`, `skills`, `docs-mesh`, `gps`, `goals`, `mantra`, `field-reports`, `all`. The canonical maintainer map of this machinery is `docs/architecture/INSTALLATION-FRAMEWORK.md` (source of truth); any older "capsule-first, `.tes/**`-only default" description predates the skills-surface amendment and is superseded.

| Tool | Functional default | Capsule-only (`--attach capsule`) |
|------|--------------------|------------------------------------|
| Codex | `.tes/**` + `AGENTS.md` + `.agents/skills/**` + `.codex/config.toml` + SessionStart | `.tes/**` only |
| Claude Code | `.tes/**` + `CLAUDE.md` + `.claude/skills/**` + `.mcp.json` + `.claude/settings.json` | `.tes/**` only |
| Cursor | `.tes/**` + `.cursor/rules/**` + `.cursor/mcp.json` + `.cursor/hooks.json` | `.tes/**` only |

Attach health is verified per surface by execution proof, never assumed from config presence (`PENDING_HOST_RESTART` / `PENDING_TRUST` / `HOST_UNOBSERVABLE` instead of a false `PASS`). Detaching a surface, uninstalling with proof of zero residue, backups, and the full attach-health state table are in [`REVERSIBILITY.md`](REVERSIBILITY.md). In capsule mode GPS/MAP runs from `.tes/gps/**` / `.tes/context/**`; the `docs/agents/**` mesh below materializes only when `docs-mesh` is attached. Memory lives in versioned plain-Markdown artifacts (`sources/**`, `cells/**`, `MAP.md`, `TRAIL.md`, `LINKS.md`, `CONTRACT.md`); the SQLite under `.tes/cortex/**` is derived recall/curation, never memory. The full operator contract lives in `docs/mesh/CORTEX.md`.

Cortex is Obsidian-compatible plain Markdown. The installer does not create `.obsidian/**`, require community plugins, or depend on Obsidian state. After `/tes-init` and `/tes-align`, `/tes-open-obsidian` may open the project. `/tes-goal-maestro`, `/tes-prospect`, and `/tes-mine` install as explicit skills; Goal maestro emits `/goal` after maturity, internal tree, material-diff, material-continuation, negative-grep, sequential ownership, sync-status, structural-method, and browser/visual gates. Prospecting and mining keep the brake.

Cortex MCP is activated by default for selected runtime routes. It is project-scoped and exposes only the governed `cortex_remember_plan` /`cortex_remember` write lane (`--read-only` for inspection-only). MCP activation writes the `.tes/bin/**` helpers plus per-host config (`.mcp.json`, `.codex/config.toml`, `.cursor/mcp.json`, `.vscode/mcp.json`) with absolute paths, and must not touch global MCP config, secrets, hooks, or ungoverned write-capable tools. Read-only Cortex tools never create the derived semantic index or write memory. The MCP self-test and the exact helper/config inventory live in `docs/architecture/INSTALLATION-FRAMEWORK.md` and `docs/mesh/CORTEX.md`; activation reports distinguish `config_present`, `host_connected`, and `session_restart_required`.

TES Field Reports is active by default: a local `pre-push` drain for sanitized operational facts under `.tes/field-reports/**`, installed at the active Git hook path, never sending project code or private paths, with opt-out/reactivation in the user manual. Real GitHub publication depends on local `gh`, auth, and network and stays a partial surface until authorized and replayed. Drains report explicit transport states (suppressed, blocked, invalid, sent, disabled, empty); blocked/invalid drains keep pending events and write payload-free receipts. On a Git repository, Tilly maintains artifact hygiene in `.git/info/exclude` (rollback backups, bytecode, Field Reports state, Cortex caches excluded; `.tes/bin/*.py` helpers are not, since they are the installed runtime).

When this package is available locally, `tes_init.py` is the project initialization and recertification command. It verifies package health, scans the target project, writes `docs/agents/PROJECT-REGISTER.md`, writes `docs/agents/PROJECT-CONTEXT.md` as the initial project map for future agents, creates the first-pass Obsidian-compatible operating mesh when missing, stores a full manifest under `docs/agents/evidence/**`, and can be certified with `project_context_oracle.py` plus `project_alignment_oracle.py`. Cortex can be initialized directly. The user-facing `/tes-init` intent is a router, and `/tes-setup` is a direct setup alias for the same route. It first runs an Install/Update Gate and a Project Context Gate. Installer or update writes still require Step Zero protection. If TES is already installed/current and only the project context is missing or weak, Step Zero protects installer/update writes but must not block project-context initialization; the agent reports the dirty tree, avoids helper/adapter/MCP changes, runs `tes_init.py`, and certifies both `PROJECT-CONTEXT.md` and the first-pass operating mesh. For `/tes-init`, the Project-Start Gate always runs before final reporting: a preflight context PASS does not replace project-start execution. After helper-only or adapter repairs, run `tes_init.py --target <target> --yes` and both project oracles again. For `needs_review`, use `tes_install.py postinstall --recover-needs-review` so the retained run record and sentinel move together. For old meshed projects with stale helpers, trigger drift, or incomplete alignment, report the planner `continuation_plan` instead of a bare `NEEDS_REVIEW`; include phases, approvals, write surfaces, commands, and the final recorded probe that must return helper/runtime/context/alignment PASS.

The register and project context are written before slower certification gates finish. If a later oracle is blocked or times out, the run closes as `NEEDS_REVIEW` with local evidence instead of leaving the project uninitialized.

```bash
python3 scripts/tes_init.py --target /path/to/project --yes
python3 scripts/project_context_oracle.py --target /path/to/project
python3 scripts/project_alignment_oracle.py --target /path/to/project
python3 scripts/tes_update.py plan --target /path/to/project --json-only
python3 scripts/tes_update.py plan --target /path/to/project --json-only --record-field-report
python3 scripts/field_reports.py status --target /path/to/project
python3 scripts/cortex.py health --target /path/to/project-or-vault
python3 scripts/cortex.py review --target /path/to/project-or-vault --backend lexical
```

Run the correlated `--self-test` commands from `scripts/**` when certifying the package source.

The `npx`/`bunx add` installer is the primary first-registration path for project-scoped MCP on Codex, Claude Code, and Cursor. Its `--agent all` route does not create VS Code config. Explicit MCP work, including VS Code, uses:

```bash
python3 scripts/install_mcp.py --target /path/to/project --adapter codex --yes
python3 scripts/install_mcp.py --target /path/to/project --adapter all --yes
python3 scripts/install_mcp.py --target /path/to/project --adapter all --read-only --yes
python3 scripts/install_mcp.py --self-test
```

Use the first `tes_update.py plan --json-only` form for inspection. It is read-only and must not write Field Reports. Use `--record-field-report` only for the final certification probe. When the probe returns `recommended_update_scope=helpers-only`, run Layer Zero with `install_mcp.py --helpers-only` before adapter or MCP config activation. When it returns `recommended_update_scope=adapter-config` because `runtime_trigger_status=DRIFT`, run the clean runtime route for the selected adapter: stage the bundle, create `.tes/bk/<timestamp>/`, apply `tes_bundle.py apply --mode clean-runtime`, then run `recover-plan --apply-safe`. After Layer Zero, record the final proof with `tes_update.py plan --json-only --record-field-report` before commit or push. Self-tests run from `scripts/**` certify the package source contract; self-tests run from `.tes/bin/**` certify the installed helper contract.

Navigation is runtime-aware. The installer declares menus as intent, loads the shared navigation library, then loads the renderer for Codex, Claude Code, or Cursor. Native cards are used only when the active runtime supports them safely; command navigation remains the certified fallback.

## New vs Existing Projects

For a new project, the installer creates a minimal `docs/agents/**` mesh and thin runtime files for the selected IDE. It also creates `docs/agents/PROJECT-CONTEXT.md` from discovered project facts and names unknowns explicitly, then creates an Obsidian-compatible first-pass operating mesh with project state, roadmap, execution line, quality gates, boundaries, knowledge lifecycle, glossary, decisions, and evidence. `project_context_oracle.py` and `project_alignment_oracle.py` must pass or the installer must close as `NEEDS_REVIEW` with a concrete blocker.

For an existing project, the functional default materializes the capsule (`.tes/**`) plus skills, root context, `mcp`, and startup `hooks`; only `docs-mesh` stays opt-in because it authors project docs. For a minimal, isolation-only install, pass an explicit selection (`--attach capsule` for capsule-only `.tes/**`). Existing context is treated as recovery evidence and every surface is reversible via `detach`/`uninstall`. When `docs-mesh` is attached (or `root-context` on a capsule-only install), TES migrates durable rules from agent files/docs into `docs/agents/**`, then composes `AGENTS.md`, `CLAUDE.md`, `.cursor/rules/**`, `.claude/**`, and `.agents/**` as runtime assets that route to the mesh, reading strong anchors and synthesizing the initial project map in `PROJECT-CONTEXT.md`.

The deterministic initializer creates the scaffold. The active agent must then open strong anchors before claiming deep project understanding, and either refine `PROJECT-CONTEXT.md` with supported semantic context or report `Project context: NEEDS_REVIEW`.

Existing context is recovery evidence by default. Conflicts mean central backup, clean runtime overwrite, and semantic recovery into `docs/agents/**`.

For a meshed project, the installer treats the run as update/convergence. It inspects the existing `docs/agents/**` mesh, compares the installed Tilly version with the cloud package version, detects applied IDE surfaces, recommends `all`, `codex`, `claude`, `cursor`, or `current`, applies only surgical updates, preserves durable `.tes/**` state, refreshes active runtime from the canonical bundle, recovers local governance semantics, and certifies the resulting state. VS Code remains an explicit MCP-only route rather than an adapter install route.

## Certification Output

Every install, retrofit, update, or audit run ends with:

```text
TES Context Mesh Convergence Report

Status: GO | NEEDS_REVIEW | NO-GO
Scope: new project install | existing project retrofit | meshed project update | audit
Detected Runtime: Codex | Claude Code | Cursor | uncertain
Selected Adapters: ...
Canonical Source: docs/agents/**
Project Context: docs/agents/PROJECT-CONTEXT.md
Project Alignment: docs/agents/PROJECT-STATE.md, PROJECT-ROADMAP.md System X-Ray + Convergence Line, EXECUTION-LINE.md, QUALITY-GATES.md, BOUNDARIES-AND-CONSTRAINTS.md, KNOWLEDGE-LIFECYCLE.md, GLOSSARY.md, DECISIONS/**
Cortex: docs/agents/cortex/**
Navigation Library: ...
Navigation Renderer: ...
Navigation Mode: ...
Source Snapshot: package commit, remote main, freshness
Changed Surfaces: new surfaces, updated existing mesh files, runtime config
Clean Backup: .tes/bk/<timestamp>/manifest.json plus restore command
Semantic Recovery: RECOVERED | NEEDS_REVIEW | SKIP, evidence path
Root Context Gate: PASS | RECOVERED | NEEDS_REVIEW | SKIP
Installed Helper Set: cortex.py, cortex_mcp.py, cortex_embed.mjs, scope_contract.py, event_ledger.py, checkpoint.py, consolidation_gate.py, field_reports.py, tes_update.py, tes_legacy_retirement.py, root_context.py, tes_init.py, project_context_oracle.py, project_alignment_oracle.py, tes_open_obsidian.py
Field Reports: PASS | BLOCKED | DISABLED | SKIP, with pending outbox count
Certification: compact PASS/FAIL/SKIP bullets, including Project Quality Gates PASS/BLOCKED/NEEDS_REVIEW/NOT_APPLIED with lint/typecheck/test/build/CI details
Evidence: ...
User Manual: ...
Rollback Summary: reset baseline plus clean installer-created files
Limits: ...
```

The chat report is deliberately short. Detailed inventories, conflicts, oracles, and reconstruction notes belong in the evidence file. A report must not use tables by default, and it must not hide files changed by the installer. Before closing, compare the changed-file summary against `git status --short --untracked-files=all`. Do not collapse Field Reports into a generic gate: the report must say whether the hook/drain is `PASS`, `BLOCKED`, `DISABLED`, or `SKIP`. Because the pre-push hook drains silently, confirm created upstream reports by checking `field_reports.py status` or `.tes/field-reports/receipts/**` after push.

GO requires canonical `docs/agents/**`, selected-runtime MCP activation or named blocker, central backup, semantic recovery evidence, safe discovered quality gates such as lint, typecheck, test, build or CI-equivalent checks run and passed, no secret mutation, and at least one local oracle. Unsafe or unavailable quality gates are explicit `BLOCKED` or `NEEDS_REVIEW`, never hidden under `Limits`. `RECOVERED` is a passing root-context state when the old bootloader content is safely represented in `.tes/bk/**` and a recovery report exists under `docs/agents/evidence/**`.

Source freshness is certification metadata: stale snapshots are `STALE_SOURCE` and cannot claim latest TES certification. For public bundles, the ZIP records the product `source_commit`; the later ZIP/hash/index commit is a distribution commit and cannot be embedded without a circular hash. If the public bundle version/hash matches the staged manifest and `source_commit` is an ancestor of remote `main`, report `PASS` with meaning `current public bundle`, not `STALE_SOURCE`. Use `tes_bundle.py freshness --target <project>`; do not infer staleness from unequal commit strings alone. Bundle staging is local cache: ensure `.tes/setup/**` is ignored through target-local Git exclude and do not commit staged ZIPs or setup scripts. If a public ZIP is manually extracted only to reach its scripts, immediately rerun extracted `tes_bundle.py stage`; manual unzip is not certified staging. GO does not imply the integration was committed or pushed. The certification report must distinguish:

| Claim | Meaning |
|-------|---------|
| `GO meshed` | Mesh files were created, retrofitted, or updated and local oracles passed. |
| `GO committed` | The user explicitly approved commit after reviewing the report. |
| `GO published` | The user explicitly approved push or publication after commit. |

Every report must expose the user manual:

```text
User Manual
- Web: https://murillodutt.github.io/tilly-engineer-skills/install/USER-MANUAL.html
- Local package path: docs/install/USER-MANUAL.html
```

Automatic browser opening is optional convenience only. It is not required for certification because not every runtime can safely open local files or browser tabs.

Every report must include rollback guidance. If the install is uncommitted, the standard undo command is:

```bash
git reset --hard <baseline-head>
```

If the install was committed separately, prefer:

```bash
git revert <install-commit>
```

## Script Support

The script remains available for maintainers, package checks, and low-risk mechanical smoke tests. `install_smoke.py --self-test` also runs portable project-context fixtures for minimal, docs-only, npm, Python, monorepo, already-meshed, and project-owned bootloader targets.

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

The gate archives legacy retrofit records from `.tilly/retrofit/**` under `.tes/legacy-retirement/retrofit/**`; these records must not block runtime retirement when all other legacy paths are known.
The npx installer runs this closed-catalog retirement before applying the fresh bundle; legacy hook ledgers move under `.tes/legacy-retirement/hooks/**`, exact duplicate hook-runtime rows are compacted with an archive copy, and hook-smoke harness scripts are removed while `SKILL.md` smoke evidence stays in place.

macOS/Linux bootstrap entrypoint:

```bash
./scripts/bootstrap/install.sh --adapter codex --target /path/to/project --dry-run
```

Windows PowerShell bootstrap entrypoint:

```powershell
.\scripts\bootstrap\install.ps1 --adapter codex --target C:\path\to\project --dry-run
```

## Conflict Policy

If a governance file exists and differs, installation first snapshots it under `.tes/bk/<timestamp>/`, then installs the canonical TES runtime. Old instructions are not active runtime after install; they are recovery evidence.

Allowed responses: `--dry-run` to preview, `tes_bundle.py backup` for the central snapshot, `tes_bundle.py apply --mode clean-runtime --yes` to install, `tes_bundle.py recover-plan --apply-safe --yes` for recovery evidence, and `tes_bundle.py restore --backup-id <id> --yes` to restore. `--mode preserve` exists only as a compatibility escape hatch.

## LLM Retrofit

Retrofit is a legacy compatibility escape hatch, not the normal install flow. Use it only when an operator explicitly keeps old bootloaders active while reviewing a migration plan:

```bash
python3 scripts/install_adapter.py \
  --adapter codex \
  --target /path/to/project \
  --retrofit-plan
```

The generated file lives under `/path/to/project/.tes/retrofit/`.

The compatibility route preserves conflicting bootloaders and still installs non-conflicting TES-owned assets. The default route is clean runtime: `INSTALLED_CLEAN_RUNTIME` with `clean_backup`, `semantic_recovery`, `layer_results`, and `installed_capabilities`. Normal merge work recovers durable semantics into `docs/agents/**`; active bootloaders are canonical TES runtime unless the operator explicitly uses compatibility preserve mode.

Give that file to an LLM or reviewer. Merge Tilly discipline while preserving project-local commands, paths, tests, ownership, security constraints, and existing agent rules.

## Security Boundaries

- No remote script execution.
- No package manager install.
- No unrequested hooks, background agent, cloud, secret changes, global MCP config, or ungoverned write-capable MCP tools. TES project-scoped hooks are installed only through the selected installer surface and stay idempotent (single backup, foreign hooks chained before the TES gate, never an orphan). When the project is Git-eligible, TES installs and verifies its Git gates — the Field Reports `pre-push` drain and a strict `pre-commit` gate, choosing the hook manager deterministically (husky for Node/TS, `pre-commit` when a `.pre-commit-config.yaml` exists, lefthook as the polyglot default, deferring to any existing manager). Readiness blocks (`NEEDS_GIT`) when the gates cannot be installed; absence of an installable gate on an eligible target is never reported as a silent pass.
- Project-scoped Cortex MCP config is allowed only through the selected route and explicit installer report; governed remember is default and `--read-only` is the inspection-only opt-out.
- No runtime overwrite before `.tes/bk/<timestamp>/manifest.json` exists; `.tes/bk/**` is local rollback history and stays out of Git. No non-interactive writes without `--yes`. Backup/restore and uninstall detail: [`REVERSIBILITY.md`](REVERSIBILITY.md).

## Validation

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
npm run git-gate:converge
npm run commit:check
npm run commit:closure
```

`commit:check` is the default staged gate. `git-gate:converge` is the focused recursive loop for Git gate changes. Run `commit:closure` only when explicitly certifying the full package.

In a target project, run the target project's own smallest relevant oracle after installing or merging.
