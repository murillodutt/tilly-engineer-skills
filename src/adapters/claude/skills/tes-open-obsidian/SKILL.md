---
name: tes-open-obsidian
description: Use when the user says /tes-open-obsidian, /tes:open-obsidian, tes open obsidian, open Obsidian, open this project in Obsidian, abrir Obsidian, abrir no Obsidian, or asks TES to open the current project as an Obsidian visualization surface after project context and alignment have been certified.
license: MIT
---

# TES Open Obsidian

`/tes-open-obsidian` is the preferred shared TES trigger for opening a
TES-initialized project in Obsidian. `/tes:open-obsidian` is a compatible TES
intent alias if the host reports it as invalid slash text.

Use this skill after `/tes-init` and `/tes-align` have produced an
Obsidian-ready Markdown mesh under `docs/agents/**`.

## Contract

TES prepares and verifies the Markdown knowledge mesh. Obsidian belongs to the
human or host project.

This skill opens `docs/agents` as the Obsidian vault when explicitly invoked,
because that folder is the TES operating mesh. It must not create, edit, clean,
or version `.obsidian/**`.

Prefer the official Obsidian CLI when it is available and registered. The CLI
requires the Obsidian 1.12+ installer with **Command line interface** enabled in
Obsidian settings: <https://obsidian.md/help/cli>. On macOS, the helper may fall
back to opening `<target>/docs/agents` with the Obsidian app.

## Workflow

1. Confirm the user explicitly asked to open Obsidian.
2. Run the installed preflight:

```bash
python3 .tes/bin/tes_open_obsidian.py --target . --dry-run --open
```

Use the source helper when working inside the TES package:

```bash
python3 scripts/tes_open_obsidian.py --target <target> --dry-run --open
```

3. If the result is `BLOCKED`, report the missing gate. Usually the fix is to
   run `/tes-init` first.
4. If the result is `READY` and the user asked to open, run:

```bash
python3 .tes/bin/tes_open_obsidian.py --target . --open
```

5. Report whether the project was `OPENED`, `READY`, or `BLOCKED`, including
   `vault_root`, `vault_root_relative`, and whether the helper used the
   Obsidian CLI or the macOS app fallback.

## Done

Close with:

```text
Obsidian Open Gate: OPENED|READY|BLOCKED, with explicit limits.
```

## Locks

- Do not run installer/update writes from this skill.
- Do not create `.obsidian/**`.
- Do not modify `.obsidian/**`.
- Do not install Obsidian plugins.
- Do not change Obsidian workspace, cache, graph, or app settings.
- Do not claim Obsidian is required for TES operation.
- Do not bypass `project_context_oracle.py` or `project_alignment_oracle.py`.
