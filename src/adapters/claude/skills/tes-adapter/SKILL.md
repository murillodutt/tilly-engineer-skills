---
name: tes-adapter
description: Use when the user says /tes:adapter or asks to materialize, install, dry-run, retrofit, validate, or certify Codex, Claude, Cursor, or all TES adapters.
license: MIT
---

# TES Adapter

`/tes:adapter` is the shortcut for adapter materialization, dry-run install,
retrofit review, and adapter certification.

## Workflow

1. Determine adapter route: `codex`, `claude`, `cursor`, or `all`.
2. For package work, use `materialize_adapter.py <route> --check` before
   writing generated adapter trees.
3. For target projects, dry-run first with `install_adapter.py --dry-run`.
4. If conflicts exist, create or review the retrofit plan instead of overwriting.
5. Write only with explicit authorization such as `--yes`.
6. Run `install_smoke.py --self-test`, `claude_plugin_oracle.py --self-test`,
   or `platform_surface_oracle.py --self-test` as applicable.

## Locks

- Do not overwrite existing project instructions blindly.
- Do not reintroduce legacy `.cursorrules`.
- Do not treat generated `dist/**` as canonical source.
- Do not publish marketplace packages from this shortcut.
