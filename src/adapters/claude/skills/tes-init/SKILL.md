---
name: tes-init
description: Use when the user says /tes-init, /tes-setup, /tes-update, /tes:init, /tes:update, tes init, tes setup, Atualizar TES, a natural init command/prompt, a natural update command/prompt, or asks to initialize, install, retrofit, update, audit, or recertify TES in the current project. Runs the assisted context installer contract through the active agent.
license: MIT
---

# TES Init

`/tes-init`, `/tes-setup`, `/tes-update`, `/tes:init`, `/tes:update`,
`tes init`, `tes setup`, `tes update`, `initialize TES`, `install TES`, `recertify TES`,
`inicializar TES`, `instalar TES`, `recertificar TES`, and direct
command/prompts such as `TES, initialize this project`,
`TES, inicialize este projeto`, `Atualizar TES`, or `atualizar TES` are
user-facing installer intents. They are not blind shell commands and not
background daemons. The active agent remains the executor.
Across Codex, Claude Code, and Cursor, `/tes-*` forms are the preferred shared
triggers, `/tes-setup` is a setup alias for `/tes-init`, and `/tes:*` forms are
compatible TES intent aliases. If the host reports `/tes:init` as invalid, treat
it as the same TES intent and continue instead of asking for a route.

## Mission

Initialize, retrofit, update, audit, or recertify TES in the current project by
following the assisted context installer contract. `/tes-init` must also
initialize the project for future agent work by reading the strongest project
anchors and writing `docs/agents/PROJECT-CONTEXT.md` as the first durable
project map.

Canonical installer spec:

```text
https://raw.githubusercontent.com/murillodutt/tilly-engineer-skills/main/docs/install/ASSISTED-CONTEXT-INSTALLER.prompt.md
```

Use the local package copy when available. Otherwise fetch the raw spec or ask
the user for package contents.

## Workflow

1. Enter quiet installer mode.
2. Detect the current runtime and classify the project as `new`, `existing`, or
   `meshed`.
3. Run the `/tes-init` router gates before choosing writes:
   - **Install/Update Gate** checks installed/cloud versions, helper contract,
     adapter/runtime drift, MCP activation, and legacy retirement.
   - **Project Context Gate** checks whether
     `docs/agents/PROJECT-CONTEXT.md` exists and passes
     `project_context_oracle.py`.
   Step Zero protects installer/update writes. It must not block
   project-context initialization when TES is already installed/current and the
   Project Context Gate is the only failing gate; report the dirty tree, avoid
   helper/adapter/MCP/bootloader writes, and initialize/certify project context.
   For `/tes-init`, a preflight context PASS does not replace project-start
   execution. After helper-only or adapter repairs, run the **Project-Start
   Gate** before final reporting: execute `python3 .tes/bin/tes_init.py --target
   . --yes` in an installed target, or package `scripts/tes_init.py --target
   <target> --yes`, then run `project_context_oracle.py --target <target>` and
   `project_alignment_oracle.py --target <target>`.
   When `.tes/postinstall.json` is already `complete` from the first-session
   hook and the user asks plain `/tes-init` or `/tes-setup`, treat it as a
   status/report request: read `.tes/postinstall.json` and its `last_run`,
   summarize the completed run, and do not rerun Project-Start unless the user
   explicitly asks to recertify/update, the sentinel is not `complete`, the
   planner reports drift, or evidence is missing.
4. Run Step Zero before installer/update edits: inspect Git status and offer a
   local baseline commit when the tree is dirty and install/update writes are
   required.
5. For `/tes-update` or `/tes:update`, run `tes_update.py plan --json-only`
   when available to compare installed/cloud versions, verify helper contract
   parity, detect applied IDE surfaces, and recommend route plus
   `recommended_update_scope`.
   Use `--record-field-report` only on the final certification probe. Treat
   `recommended_update_scope=helpers-only` or `STALE_HELPERS` as
   update-required and replace only TES-owned
   `.tes/bin/**` helpers with backups through the helper-only Layer Zero route,
   then rerun the update probe before activating MCP configs. After any helper
   overwrite, record the final probe before GO, commit, or push; it must show
   `helper_contract_status=PASS`, `runtime_trigger_status=PASS` or
   `NOT_APPLIED`, `update_available=False`, and `recommended_update_scope=none`.
   If the planner returns `continuation_plan.status=PENDING_APPROVAL`, stop with
   `NEEDS_REVIEW` and include the plan's required phases, approvals, write
   surfaces, commands, and final recorded probe. Do not leave an old meshed
   project with a bare blocker that the next agent cannot resume.
6. Before rewriting root bootloaders, stage the bundle and create a central
   `.tes/bk/<timestamp>/` backup. Analyze previous root context from that
   backup and recover durable semantics into `docs/agents/**`.
7. When `legacy_retirement_required=true`, run `tes_legacy_retirement.py plan`,
   apply only if the run is authorized, then require
   `tes_legacy_retirement.py audit` before copying new TES assets.
8. Use the detected runtime as the default route. Ask for route only when the
   installer contract requires it.
9. Apply clean runtime after central backup, build or update `docs/agents/**`, analyze the
   target project in depth, write or update `docs/agents/PROJECT-CONTEXT.md`,
   create the initial Obsidian-compatible operating mesh when missing,
   initialize `docs/agents/cortex/**`, keep runtime bootloaders thin, and
   activate the read-only Cortex MCP route when selected.
   Treat `tes_init.py` as deterministic scaffold generation for context plus
   first-pass alignment. The active agent must open strong anchors before
   claiming deep project understanding, refine `PROJECT-CONTEXT.md` when
   supported by evidence, or report `Project context: NEEDS_REVIEW` with the
   blocker. `/tes-align` remains the deeper semantic refinement path.
10. Invoke package oracles such as `tes_init.py`, `tes_update.py`,
   `tes_legacy_retirement.py`, `root_context.py`, `install_smoke.py`,
   `install_mcp.py`, and Cortex checks.
   If local execution is unavailable, mark it `BLOCKED` or `SKIP`.
11. Install or report the Field Reports `pre-push` drain. It is active by
   default and controlled by the user manual prompts.
12. Finish with a short certification report, source snapshot freshness, changed
   surfaces, installed helper set, Field Reports state, evidence path, limits,
   project context path, rollback summary, and Git rollback instructions.

## Locks

- Do not overwrite project instructions before `.tes/bk/<timestamp>/manifest.json` exists.
- Do not edit secrets, global MCP config, remotes, package locks, or CI secrets.
- Do not push, amend, tag, publish, or install dependencies without explicit
  user approval after the final report.
- Do not promote Cortex cells automatically.
