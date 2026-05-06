---
tds_id: install.navigation.common
tds_class: adapter
status: active
consumer: installing LLMs
source_of_truth: true
evidence_level: L2
tver: 0.1.0
---

# Common Navigation Renderer

navigation_library: tilly-navigation@0.1.1

Use this renderer for every runtime unless a runtime-specific renderer safely
upgrades the user interface.

## Rules

- Declare menus as intent first.
- Ask only when the installer is genuinely blocked.
- Prefer one question per menu.
- Prefer 2-4 mutually exclusive routes. Use command navigation for larger
  finite route sets.
- Use stable command labels, not numbers.
- Put the recommended command first.
- Never add a manual `Other` option.
- Never show raw intent objects, JSON, YAML, or internal analysis.
- Never use a multiple-choice panel that renders as naked numbers.
- For typed host tools, inspect the active schema before calling it.
- For unknown hosts, command navigation is safer than pretending support.

## Command Navigation Fallback

Render this shape:

```text
<title>

<one-line reason the user must choose>

> <recommended-command>  recommended
  <honest trade-off>

> <other-command>
  <honest trade-off>

Type: <command-a>, <command-b>, or <command-c>.
```

Accept only the listed command strings. If a host returns numeric or
letter-based selections, map them only when the menu displayed an explicit
command mapping and the answer is unambiguous. Treat free text as untrusted
input.

## Standard Intents

### Step Zero Baseline

```text
id: step-zero-baseline
type: single-select
question: Create a local Git baseline before installing?
header: Baseline
default: commit-baseline
options:
  - command: commit-baseline
    label: Commit baseline
    recommended: true
    description: Create a local commit with the current project state before installing.
  - command: continue-dirty
    label: Continue dirty
    recommended: false
    description: Continue without a clean rollback point. Not recommended.
  - command: abort
    label: Abort
    recommended: false
    description: Stop installation without changes.
```

Fallback rendering:

```text
Tilly Step Zero

Working tree is dirty. Choose a route before installation.

> commit-baseline  recommended
  Create a local commit with the current project state before installing.

> continue-dirty
  Continue without a clean rollback point. Not recommended.

> abort
  Stop installation without changes.

Type: commit-baseline, continue-dirty, or abort.
```

### Adapter Route

```text
id: adapter-route
type: single-select
question: Which runtime route should Tilly install?
header: Route
default: current
options:
  - command: current
    label: Current runtime
    recommended: true
    description: Install only the runtime currently executing this conversation.
  - command: codex
    label: Codex
    recommended: false
    description: Create or retrofit AGENTS.md and .agents/skills/**.
  - command: claude
    label: Claude
    recommended: false
    description: Create or retrofit CLAUDE.md and Claude-scoped rules when needed.
  - command: cursor
    label: Cursor
    recommended: false
    description: Create or retrofit .cursor/rules/*.mdc.
  - command: all
    label: All runtimes
    recommended: false
    description: Create the shared docs/agents/** mesh and all runtime bootloaders.
  - command: audit
    label: Audit only
    recommended: false
    description: Inspect and report what would change without modifying files.
```

For this six-route intent, use command navigation even on platforms whose
native card limits are 2-4 options. Do not split it into multiple cards unless
the user asks for guided narrowing.
