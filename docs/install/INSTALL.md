---
tds_id: install.adapter_installer
tds_class: adapter
status: active
consumer: adopters and release operators
source_of_truth: true
evidence_level: L2
---

# Adapter Installation

The installer copies materialized adapter files into a target project. It is
local-first, multi-platform, and fail-closed on conflicts.

## Compatibility Basis

The installer follows current adapter surfaces:

| Tool | Install Surface |
|------|-----------------|
| Codex | `AGENTS.md` and `.agents/skills/**` |
| Claude Code | `CLAUDE.md`, `.claude-plugin/**`, and `skills/**` |
| Cursor | `.cursor/rules/*.mdc` project rules |

The common pattern is file-based installation into the target repository. The
script does not install hooks, MCP servers, cloud/background agents, secrets, or
marketplace publishing metadata beyond the local Claude plugin files already
materialized by this package.

## Commands

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
/path/to/project/.tilly/retrofit/
```

The command still exits with a conflict status because no install was applied.
That is intentional: retrofit is a merge plan, not a silent write.

Give that file to an LLM or human reviewer. The merge instruction is to add the
Tilly discipline while preserving project-local commands, paths, tests,
ownership, security constraints, and existing agent rules.

## Security Boundaries

- No remote script execution.
- No package manager install.
- No hooks, MCP, background agent, cloud, or secret changes.
- No overwrite without explicit `--overwrite`.
- No non-interactive writes without `--yes`.
- Backups are created before overwrites unless `--no-backup` is set.

## Validation

From this package:

```bash
npm run install:dry-run
npm run materialize:check
npm run commit:check
```

In a target project, run the target project's own smallest relevant oracle
after installing or merging.
