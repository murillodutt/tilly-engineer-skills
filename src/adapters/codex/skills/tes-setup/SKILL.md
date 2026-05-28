---
name: tes-setup
description: Use when the user says /tes-setup, tes setup, setup TES, finish TES setup, or asks for the TES first-session report. Direct setup alias for /tes-init.
---

# TES Setup

`/tes-setup` is the direct setup alias for `/tes-init`. It exists as an explicit
skill so hosts that expose slash commands by skill name can resolve the command
instead of treating it as unknown text.

## Workflow

1. Prefer the installed TES Init contract:
   - Project skill: `.agents/skills/tes-init/SKILL.md`
2. Read that skill when available and follow it exactly.
3. When `.tes/postinstall.json` is already `complete`, treat `/tes-setup` as a
   status/report request: read `.tes/postinstall.json` and its `last_run`,
   summarize the completed run, and do not rerun Project-Start unless the user
   explicitly asks to recertify/update, the sentinel is not `complete`, the
   planner reports drift, or evidence is missing.
4. When `.tes/postinstall.json` is `running`, report that first-session setup is
   still in progress, ask the user to wait for the completion notice, and do not
   start project work or run duplicate setup commands. Tell the user to run
   `/tes-setup` again after `.tes/postinstall.json` becomes `complete`.
5. When `.tes/postinstall.json` is `needs_review`, inspect the latest run
   record, repair the focused blocker, then run
   `python3 .tes/bin/tes_install.py postinstall --target . --recover-needs-review`
   to rerun Project-Start, verify selected MCP config, and clear the sentinel
   only on PASS.
6. If the init skill is unavailable but installed helpers exist, run the
   installed Project-Start Gate:
   - `python3 .tes/bin/tes_init.py --target . --yes`
   - `python3 .tes/bin/project_context_oracle.py --target .`
   - `python3 .tes/bin/project_alignment_oracle.py --target .`
7. If helpers are missing, report `BLOCKED` and ask the user to rerun the TES
   GitHub npx installer.

## Locks

- Do not treat `/tes-setup` as a shell command.
- Do not push, publish, tag, or edit remotes from this skill.
- Keep the final response short and report the TES status, evidence, and limits.
