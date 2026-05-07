---
name: tilly-init
description: Use when the user says /tilly:init, /tilly:update, tilly init, Atualizar a Tilly, a natural init command/prompt, a natural update command/prompt, or asks to initialize, install, retrofit, update, audit, or recertify Tilly Engineer Skills in the current project. Runs the assisted context installer contract through the active agent.
license: MIT
---

# Tilly Init

`/tilly:init`, `/tilly:update`, `tilly init`, and direct command/prompts such as
`Tilly, initialize this project`, `Tilly, inicialize este projeto`, or
`Atualizar a Tilly` are user-facing installer intents. They are not blind shell
commands and not background daemons. The active agent remains the executor.

## Mission

Initialize, retrofit, update, audit, or recertify Tilly Engineer Skills in the
current project by following the assisted context installer contract.

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
4. For `/tilly:update`, run `tilly_update.py plan` when available to compare
   installed/cloud versions, detect applied IDE surfaces, and recommend route.
5. Use the detected runtime as the default route. Ask for route only when the
   installer contract requires it.
6. Preserve local governance, build or update `docs/agents/**`, initialize
   `docs/agents/cortex/**`, keep runtime bootloaders thin, and activate the
   read-only Cortex MCP route when selected.
7. Invoke available package oracles such as `tilly_init.py`, `tilly_update.py`,
   `install_smoke.py`, `install_mcp.py`, and Cortex checks. If local tool
   execution is unavailable, mark the oracle as `BLOCKED` or `SKIP`; do not
   claim it passed.
8. Install or report the Field Reports `pre-push` drain. It is active by
   default and controlled by the user manual prompts.
9. Finish with a short certification report, source snapshot freshness, changed
   surfaces, installed helper set, Field Reports state, evidence path, limits,
   rollback summary, and Git rollback instructions.

## Locks

- Do not overwrite project instructions blindly.
- Do not edit secrets, global MCP config, remotes, package locks, or CI secrets.
- Do not push, amend, tag, publish, or install dependencies without explicit
  user approval after the final report.
- Do not promote Cortex cells automatically.
