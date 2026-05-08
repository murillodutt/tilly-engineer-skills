---
name: tes-init
description: Use when the user says /tes:init, /tes:update, tes init, Atualizar TES, a natural init command/prompt, a natural update command/prompt, or asks to initialize, install, retrofit, update, audit, or recertify TES in the current project. Runs the assisted context installer contract through the active agent.
---

# TES Init

`/tes:init`, `/tes:update`, `tes init`, and direct command/prompts such as
`TES, initialize this project`, `TES, inicialize este projeto`, or
`Atualizar TES` are user-facing installer intents. They are not blind shell
commands and not background daemons. The active agent remains the executor.

## Mission

Initialize, retrofit, update, audit, or recertify TES in the current project by
following the assisted context installer contract.

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
3. Run Step Zero before edits: inspect Git status and offer a local baseline
   commit when the tree is dirty.
4. For `/tes:update`, run `tes_update.py plan --json-only` when available to
   compare installed/cloud versions, verify helper contract parity, detect
   applied IDE surfaces, and recommend route plus `recommended_update_scope`.
   Use `--record-field-report` only on the final certification probe. Treat
   `recommended_update_scope=helpers-only` or `STALE_HELPERS` as
   update-required and replace only TES-owned
   `.tes/bin/**` helpers with backups through the helper-only Layer Zero route,
   then rerun the update probe before activating MCP configs. After any helper
   overwrite, record the final probe before GO, commit, or push; it must show
   `helper_contract_status=PASS`, `update_available=False`, and
   `recommended_update_scope=none`.
5. Before rewriting root bootloaders, run `root_context.py analyze` when
   available and migrate durable root context into `docs/agents/**` first.
6. When `legacy_retirement_required=true`, run `tes_legacy_retirement.py plan`,
   apply only if the run is authorized, then require
   `tes_legacy_retirement.py audit` before copying new TES assets.
7. Use the detected runtime as the default route. Ask for route only when the
   installer contract requires it.
8. Preserve local governance, build or update `docs/agents/**`, initialize
   `docs/agents/cortex/**`, keep runtime bootloaders thin, and activate the
   read-only Cortex MCP route when selected.
9. Invoke package oracles such as `tes_init.py`, `tes_update.py`,
   `tes_legacy_retirement.py`, `root_context.py`, `install_smoke.py`,
   `install_mcp.py`, and Cortex checks.
   If local execution is unavailable, mark it `BLOCKED` or `SKIP`.
10. Install or report the Field Reports `pre-push` drain. It is active by
   default and controlled by the user manual prompts.
11. Finish with a short certification report, source snapshot freshness, changed
   surfaces, installed helper set, Field Reports state, evidence path, limits,
   rollback summary, and Git rollback instructions.

## Locks

- Do not overwrite project instructions blindly.
- Do not edit secrets, global MCP config, remotes, package locks, or CI secrets.
- Do not push, amend, tag, publish, or install dependencies without explicit
  user approval after the final report.
- Do not promote Cortex cells automatically.
