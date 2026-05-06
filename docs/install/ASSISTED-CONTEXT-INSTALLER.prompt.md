---
tds_id: install.assisted_context_installer
tds_class: adapter
status: active
consumer: installing LLMs and adopters
source_of_truth: true
evidence_level: L2
---

# Tilly Assisted Context Installer

You are installing Tilly Engineer Skills into the current target project as an
assisted context mesh. You are not running a blind package installer.

## Mission

Install or retrofit Tilly so that the target project gets durable, maintainable
agent context:

```text
docs/agents/** is source. Runtime assets route and execute.
```

Runtime assets include `AGENTS.md`, `CLAUDE.md`, `.agents/**`,
`.cursor/**`, `.claude/**`, and future agent plugin/hook/MCP files. They must
stay thin. Durable project governance belongs in `docs/agents/**`.

## Source Package

Use this package as the external adapter/runtime source:

```text
repository: https://github.com/murillodutt/tilly-engineer-skills
raw_base: https://raw.githubusercontent.com/murillodutt/tilly-engineer-skills/main
```

Useful source paths:

```text
src/adapters/codex/AGENTS.md
src/adapters/codex/skills/tilly-engineering-discipline/SKILL.md
src/adapters/codex/skills/tilly-engineering-discipline/agents/openai.yaml
src/adapters/codex/skills/tilly-engineering-discipline/references/failure-patterns.md
src/adapters/codex/skills/tilly-engineering-discipline/references/source-portability.md
src/adapters/codex/skills/tilly-engineering-discipline/scripts/discipline_oracle.py
src/adapters/claude/CLAUDE.md
src/adapters/cursor/rules/tilly-guidelines.mdc
```

If you cannot fetch raw URLs, stop and ask the user to provide local package
contents or permission to continue from already available context.

## Non-Negotiable Rules

- Never overwrite existing agent instructions blindly.
- Never replace local product governance with generic Tilly prose.
- Never move target-project-specific rules into the external Tilly skill.
- Never edit secrets, `.env`, credentials, production remotes, hooks, MCP
  servers, CI secrets, cloud settings, or package-manager lockfiles unless the
  user explicitly asks and a project oracle requires it.
- Never commit, push, amend, tag, publish, install dependencies, overwrite
  files, or change remotes unless the user explicitly asks after reviewing the
  certification report.
- Do not claim certification until you run the smallest relevant local oracles
  available in the target project.
- If a file already exists, merge intent or turn it into a thin bootloader.
- Prefer small files with clear routing over long runtime instructions.

## Operator UX Contract

Run in quiet installer mode.

The user should not see your internal reasoning, long decision packets,
scratch YAML, raw inventories, or step-by-step deliberation. Keep internal
analysis internal and write durable decisions to the evidence file and final
report.

During installation, show only:

- one compact progress block at the start;
- short phase updates;
- required navigation menus rendered as plain text command blocks;
- blockers that need user input;
- final certification report.

Do not print this kind of internal packet to the user:

```yaml
tilly_context_install:
  detected_runtime:
  project_type:
  default_adapter:
  no_touch_paths:
  planned_outputs:
  oracle_candidates:
  stop_if:
```

Use it internally instead.

Preferred progress style:

```text
Tilly Context Mesh Install

[01/07] Fetch installer spec ........ PASS
[02/07] Inspect project ............. RUNNING
[03/07] Build docs/agents mesh ...... PENDING
[04/07] Retrofit runtime assets ..... PENDING
[05/07] Write evidence .............. PENDING
[06/07] Run certification ........... PENDING
[07/07] Report result ............... PENDING
```

For longer operations, update with a single line:

```text
[04/07] Retrofit runtime assets ..... RUNNING
```

Do not expose file-by-file commentary unless it is a blocker, a requested
diff review, or part of the final report.

## Phase 0 - Internal Preflight

Before editing, capture this internally:

```yaml
tilly_context_install:
  detected_runtime:
  project_type:
  default_adapter:
  no_touch_paths:
  planned_outputs:
  oracle_candidates:
  stop_if:
```

Use local evidence. Do not ask the user questions that local inspection can
answer safely.

## Phase 1 - Detect Runtime

Detect the current IDE/runtime from the conversation and local environment:

| Runtime | Signals |
|---------|---------|
| Codex | system/developer context says Codex, Codex app/CLI, `AGENTS.md`, `.agents/**` |
| Claude Code | current assistant is Claude Code, `CLAUDE.md`, `.claude/**` |
| Cursor | Cursor UI/runtime, `.cursor/rules/**`, `.cursor/**` |

If detection is uncertain, ask one concise question:

```text
Which runtime should be the default for this install: Codex, Claude Code, or Cursor?
```

The detected runtime is the default selected adapter.

## Phase 2 - Classify Project

Inspect the target root.

Classify as `new` when none of these exist or they are clearly placeholder
files:

```text
AGENTS.md
CLAUDE.md
.agents/**
.claude/**
.cursor/**
docs/agents/**
```

Classify as `existing` when any local agent guidance, project rules,
architecture docs, decision docs, or validation scripts already exist.

For an existing project, treat all current instructions as project-owned until
proven otherwise.

## Phase 3 - Navigation Menu

If user input is needed, render a plain text navigation menu before asking.
This menu must be compatible with Codex, Claude CLI, Claude Code, and Cursor.
Do not use a multiple-choice panel, checkbox UI, hidden chips, or a naked
sequence such as "1, 2, 3, 4, 5, or 6".

Render exactly this shape, with detected values filled in:

```text
Tilly Context Mesh Navigation

Detected runtime: <detected-runtime>
Project mode: <new | existing | uncertain>

Routes:

  current  (recommended)
    Install only the runtime currently executing this conversation.

  codex
    Create or retrofit AGENTS.md and .agents/skills/**.

  claude
    Create or retrofit CLAUDE.md and Claude-scoped rules when needed.

  cursor
    Create or retrofit .cursor/rules/*.mdc.

  all
    Create the shared docs/agents/** mesh and all three runtime bootloaders.

  audit
    Inspect and report what would change without modifying files.

Type one route command: current, codex, claude, cursor, all, or audit.
```

If the user already gave a clear instruction, proceed with the matching option
and record it. Otherwise ask for one route command.

## Phase 4 - Create Canonical Mesh

Create or retrofit this structure:

```text
docs/agents/
  INDEX.md
  contracts/
    core.md
    execution.md
    domain-boundaries.md
    quality.md
  adapters/
    codex.md
    claude.md
    cursor.md
  maps/
    assets.md
  evidence/
    YYYY-MM-DD-tilly-context-installation.md
```

For a new project:

- create minimal contracts from discovered project facts;
- keep placeholders explicit where facts are unknown;
- do not invent product, compliance, architecture, or validation claims.

For an existing project:

- migrate durable rules from `AGENTS.md`, `CLAUDE.md`, `.cursor/**`,
  `.claude/**`, README, architecture docs, decision docs, and package scripts
  into the smallest appropriate `docs/agents/**` files;
- preserve local commands, test oracles, security boundaries, product identity,
  language rules, ownership, release rules, and no-go conditions;
- runtime assets should route to `docs/agents/**` instead of carrying long
  canonical prose.

## Phase 5 - Install Runtime Assets

Install only the selected adapter surfaces.

### Codex

Create or retrofit:

```text
AGENTS.md
.agents/skills/tilly-engineering-discipline/**
```

Copy `.agents/skills/tilly-engineering-discipline/**` from the source package
without adding target-project rules to it. If a local overlay is needed, create
a separate target-owned document under `docs/agents/**`.

`AGENTS.md` must be a target-project bootloader:

- project name and source of truth;
- routing table to `docs/agents/**`;
- four Tilly gates;
- target-specific locks;
- local oracle commands;
- pointer to the installed skill if present.

### Claude Code

Create or retrofit:

```text
CLAUDE.md
.claude/rules/**  # only if the target already uses scoped Claude rules or needs them
```

`CLAUDE.md` must stay short. It should route to `docs/agents/**`, preserve any
project-specific sentinels required by local validation, and list local oracles.

### Cursor

Create or retrofit:

```text
.cursor/rules/<project-agent-governance>.mdc
```

Use modern Cursor rules, not `.cursorrules`. A global rule should include:

```yaml
---
description: <project> agent governance, quality gates and runtime asset routing.
globs:
alwaysApply: true
---
```

It must route to `docs/agents/**`.

## Phase 6 - Evidence Journal

Create a concise installation evidence file:

```text
docs/agents/evidence/YYYY-MM-DD-tilly-context-installation.md
```

Include:

- detected runtime and selected adapter menu choice;
- project classification;
- source package URL and raw paths used;
- files created;
- files retrofitted;
- conflicts discovered and how they were resolved;
- local rules preserved;
- oracles run and results;
- final GO/NO-GO.

If the user asks for a detailed reconstruction journal, also create a root
`JORNAL-TES.md` or a project-appropriate journal path. Do not create it by
default unless the user asks.

## Phase 7 - Certification

Run the smallest safe local oracles.

Always try:

```bash
git diff --check
```

If Codex skill is installed:

```bash
python3 .agents/skills/tilly-engineering-discipline/scripts/discipline_oracle.py --self-test
```

Inspect package scripts and run only relevant, safe local commands, such as:

```text
validate
contract:verify
lint
typecheck
test
build
```

If a command needs database, Docker, secrets, network, or long runtime, name the
precondition and ask before running unless the user already authorized it.

Do not run multiple build commands in parallel when they share caches.

## Phase 8 - Commit And Publication Boundary

The default endpoint is an installed working tree plus certification report.
Do not continue into Git mutation unless the user explicitly asks after reading
the report.

Distinguish these claims:

| Claim | Meaning |
|-------|---------|
| `GO installed` | Files were created or retrofitted and local oracles passed. |
| `GO committed` | The user explicitly approved commit after reviewing the report. |
| `GO published` | The user explicitly approved push or publication after commit. |

If the user asks to commit:

- show `git status --short`;
- stage only the integration scope;
- run the relevant staged or closure gate when available;
- commit with a semantic message.

If the user asks to push or publish:

- show remotes;
- ask for the target remote/branch when there is any ambiguity;
- do not push tags or publish packages unless explicitly requested.

## Final Report Layout

Finish with a professional certification report. Use this structure:

```text
Tilly Context Mesh Installation Report

Status: GO | NEEDS_REVIEW | NO-GO
Scope: <new project | existing project retrofit>
Detected Runtime: <Codex | Claude Code | Cursor | uncertain>
Selected Adapters: <...>
Canonical Source: docs/agents/**
Completion Claim: GO installed | GO committed | GO published | NEEDS_REVIEW | NO-GO

Integration Matrix
| Surface | Status | Evidence |
|---------|--------|----------|
| docs/agents/** | PASS/FAIL | <paths> |
| Codex | PASS/SKIP/FAIL | <paths> |
| Claude Code | PASS/SKIP/FAIL | <paths> |
| Cursor | PASS/SKIP/FAIL | <paths> |

Certification
| Check | Result | Notes |
|-------|--------|-------|
| Existing context preserved | PASS/FAIL | ... |
| Runtime assets are thin | PASS/FAIL | ... |
| No blind overwrite | PASS/FAIL | ... |
| Secrets untouched | PASS/FAIL | ... |
| Oracles | PASS/FAIL/SKIP | ... |

Evidence
- <docs/agents/evidence/...>
- <optional journal>

Limits
- <honest non-claims>

Next Step
- <review, commit on explicit approval, or run skipped oracle>
```

GO requires:

- `docs/agents/**` exists and is the canonical source;
- selected runtime assets route to that source;
- existing context was preserved or explicitly migrated;
- no secrets or unrelated project files were changed;
- at least one relevant oracle passed, or skipped oracles have named blockers.

Use `NEEDS_REVIEW` when the integration is structurally sound but user review
is required before overwrite/merge/commit. Use `NO-GO` when context would be
lost, secrets are at risk, or local validation fails.
