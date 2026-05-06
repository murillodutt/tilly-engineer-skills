---
tds_id: install.adapter_installer
tds_class: adapter
status: active
consumer: adopters and release operators
source_of_truth: true
evidence_level: L2
---

# Adapter Installation

The primary installer is an assisted context prompt. It uses the target
project's active LLM window to inspect local governance, create or retrofit
`docs/agents/**`, keep runtime files thin, and certify the integration.

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

Start by detecting the current IDE/runtime and classifying this project as new
or existing. Run in quiet installer mode: show compact progress, blockers and
the final certification report only. When navigation is required, render the
plain text navigation menu from the spec and ask for a route command such as
current, codex, claude, cursor, all, or audit. Use the detected IDE as the
default adapter. Ask me for a route command only where the spec requires one.
Preserve local project governance, move durable agent context into
docs/agents/**, keep AGENTS.md, CLAUDE.md and Cursor rules as thin runtime
bootloaders, and finish with the certification report required by the spec.

Do not commit, push, amend, tag, publish, install dependencies, overwrite
files, or change remotes unless I explicitly ask after reviewing the
certification report.
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
  -> new/existing project classification
  -> adapter menu
  -> docs/agents/** canonical mesh
  -> thin runtime assets
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

## New vs Existing Projects

For a new project, the installer creates a minimal `docs/agents/**` mesh and
thin runtime files for the selected IDE.

For an existing project, the installer migrates durable rules from existing
agent files and docs into `docs/agents/**`, then turns `AGENTS.md`, `CLAUDE.md`,
`.cursor/rules/**`, `.claude/**`, and `.agents/**` into runtime assets that
route to the mesh.

Existing context is project-owned by default. Conflicts mean retrofit, not
overwrite.

## Certification Output

Every assisted install ends with:

```text
Tilly Context Mesh Installation Report

Status: GO | NEEDS_REVIEW | NO-GO
Scope: new project | existing project retrofit
Detected Runtime: Codex | Claude Code | Cursor | uncertain
Selected Adapters: ...
Canonical Source: docs/agents/**
Integration Matrix: ...
Certification: ...
Evidence: ...
Limits: ...
Next Step: ...
```

GO requires canonical `docs/agents/**`, thin runtime assets, preserved local
context, no blind overwrite, no secret mutation, and at least one relevant
local oracle.

GO does not imply the integration was committed or pushed. The certification
report must distinguish:

| Claim | Meaning |
|-------|---------|
| `GO installed` | Files were created or retrofitted and local oracles passed. |
| `GO committed` | The user explicitly approved commit after reviewing the report. |
| `GO published` | The user explicitly approved push or publication after commit. |

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
