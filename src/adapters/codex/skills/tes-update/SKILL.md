---
name: tes-update
description: Use when the user says /tes-update, /tes:update, tes update, Atualizar TES, atualizar TES, or asks to update, refresh, repair, or recertify an already installed TES mesh without rerunning project initialization by default.
---

# TES Update

`/tes-update` is the visible update entrypoint for an already installed TES
mesh. `/tes:update` is a compatible intent alias; if a host rejects the colon
form as slash text, continue as `/tes-update`.

The engine is `tes_update.py`. Do not reimplement update planning in the skill.

## Workflow

1. Classify the workspace:
   - Installed target: `.tes/bin/tes_update.py` exists.
   - Package source: `scripts/tes_update.py` exists.
   - Otherwise report `BLOCKED` and ask the user to run the GitHub npx
     installer.
2. Run the read-only plan first:
   - Installed target:
     `python3 .tes/bin/tes_update.py plan --target . --json-only`
   - Package source or canary:
     `python3 scripts/tes_update.py plan --target <target> --json-only`
3. Report a compact product status, never raw JSON:
   - `Current version`
   - `Available version`
   - `Scope`
   - `Route`
   - `Action`
   - `Proof`
   Include `No project work started` when the plan was read-only.
4. If the plan reports `CURRENT` and `recommended_update_scope=none`, do not
   write. Close with the proof and any declared limits.
5. If the plan reports `STALE_HELPERS` or
   `recommended_update_scope=helpers-only`, repair only TES-owned
   `.tes/bin/**` helpers through the helper-only Layer Zero route, then rerun
   the plan before any adapter or MCP work.
6. If the plan reports adapter/runtime drift, refresh adapter configuration
   only after helper parity is `PASS`.
7. Do not rerun `/tes-init` by default. Route to `/tes-init` only when the
   planner declares Project-Start, missing context, evidence drift, or the user
   explicitly asks to recertify/reinitialize.
8. After any write, run the final recorded probe before claiming `PASS`:
   `python3 .tes/bin/tes_update.py plan --target . --json-only --record-field-report`
   The final probe must show:
   - `helper_contract_status=PASS`
   - `runtime_trigger_status=PASS` or `NOT_APPLIED`
   - `update_available=False`
   - `recommended_update_scope=none`

## Locks

- Do not treat `/tes-update` as a shell command.
- Do not edit secrets, remotes, package locks, global config, or CI secrets.
- Do not start project feature work from this skill.
- Do not record Field Reports for exploratory read-only probes.
- Do not call the target current while helper parity is `STALE_HELPERS` or
  runtime triggers are `DRIFT`.
