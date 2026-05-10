# Tilly Engineer Skills (TES)

[![Version](https://img.shields.io/badge/version-0.3.80-1f6feb)](package.json)
[![License](https://img.shields.io/github/license/murillodutt/tilly-engineer-skills)](LICENSE)
[![Field Report Governance](https://github.com/murillodutt/tilly-engineer-skills/actions/workflows/field-report-governance.yml/badge.svg)](https://github.com/murillodutt/tilly-engineer-skills/actions/workflows/field-report-governance.yml)
[![Context Mesh](https://img.shields.io/badge/context--mesh-agent--operating--layer-2ea44f)](docs/mesh/CONTEXT-MESH-METHOD.md)
[![Local Gates](https://img.shields.io/badge/local--gates-certified-6f42c1)](package.json)
[![Live Landing](https://img.shields.io/badge/live--landing-GitHub%20Pages-0969da)](https://murillodutt.github.io/tilly-engineer-skills/)

<p align="center">
  <img src="https://github.com/user-attachments/assets/1e8f35f0-2d30-4a86-b6d4-1593a528d70d" alt="Tilly Engineer Skills: agent operating layer for LLM development across Codex, Claude Code, Cursor, and Obsidian-ready project knowledge" width="100%">
</p>

**Live landing:** [murillodutt.github.io/tilly-engineer-skills](https://murillodutt.github.io/tilly-engineer-skills/)

**Turn AI coding agents into a governed, auditable engineering system.**

TES is a local operating layer for LLM development. It governs Codex, Claude
Code, and Cursor while compiling project knowledge into an Obsidian-ready
Markdown mesh that survives agent windows, supports audits, and gives people a
visual way to inspect context, evidence, decisions, and execution state.

Codex, Claude Code, and Cursor are execution surfaces. Obsidian is the optional
people-facing visualization layer over versioned Markdown. TES does not require
Obsidian, install Obsidian plugins, or write `.obsidian/**`.

Retained v1 evidence shows up to **6x baseline disciplined behavior** in scoped
Claude CLI evals, positive Codex lift, and zero confirmed distractor leaks in
the certified scope.
[Evidence](docs/evidence/reports/context-mesh/context-mesh-v1-final-certification-2026-05-05/REPORT.md)

## 1. Install TES

Open your target project in Codex, Claude Code, or Cursor and paste this into
the agent window:

```text
Install Tilly Engineer Skills as an assisted context mesh, not as blind file
copying.

Read and follow this raw installer spec:

https://raw.githubusercontent.com/murillodutt/tilly-engineer-skills/main/docs/install/ASSISTED-CONTEXT-INSTALLER.prompt.md

Run in quiet installer mode: show compact progress, blockers and the final
certification report only. Start by detecting the current IDE/runtime and
classifying this project as new, existing, or meshed. Preserve local project
governance, build or update docs/agents/** as the canonical context mesh, stage
the deterministic TES bundle under .tes/setup/<version>/ from the public ZIP
when available, verify its SHA-256 before apply, keep AGENTS.md, CLAUDE.md and
project-owned Cursor rules preserved for semantic review, install TES-owned
runtime capabilities such as /tes-align and /tes-open-obsidian,
create the docs/agents/cortex/** continuity layer when needed, activate the
read-only project-scoped Cortex MCP server for the selected runtime route, and
finish with the certification report required by the spec.

Before installation edits, run Step Zero from the spec: inspect Git status and
offer a local baseline commit if the working tree is dirty. At the end, tell
me how to undo the installation with Git. Do not push, amend, tag, publish,
install dependencies, overwrite files, or change remotes unless I explicitly
ask after reviewing the certification report.
```

Short intents also work after the route is available:

```text
/tes-init
/tes-update
/tes-open-obsidian
/tes:init
/tes:update
Atualizar TES.
```

`/tes-init`, `/tes-update`, and `/tes-open-obsidian` are the preferred
cross-platform triggers. `/tes:init`, `/tes:update`, and
`/tes:open-obsidian` remain compatible intent aliases.

Canonical mini prompt: [docs/install/MINI-PROMPT.md](docs/install/MINI-PROMPT.md)

## Why Teams Use TES

| Without TES | With TES |
|-------------|----------|
| Each agent has separate prompt files and habits. | One context mesh governs Codex, Claude Code, Cursor, and an Obsidian-ready knowledge view. |
| Installation can overwrite local agent rules. | Step Zero and root-context gates preserve project governance. |
| Completion depends on model confidence. | Local oracles produce certification evidence. |
| Context disappears after the chat window. | Durable docs, evidence, Cortex, and wikilinks preserve continuity. |
| Teams cannot tell what changed agent behavior. | Benchmarks, parity gates, and Field Reports create feedback loops. |

TES is for teams that use AI coding agents inside real repositories and need
the agents to behave like careful collaborators, not disposable chat windows.

## What It Orchestrates

```text
docs/agents/**          project context mesh
AGENTS.md               Codex route
CLAUDE.md               Claude Code route
CURSOR.md               Cursor route
.tes/bin/**             local helper runtime
docs/agents/cortex/**   continuity and compiled knowledge
docs/agents/evidence/** certification records
Obsidian                optional visual workbench over Markdown
```

Runtime files stay thin. Project truth lives in versioned Markdown so people
can inspect it, review it, open it in Obsidian, and roll it back.

## Product Layers

| Layer | Role |
|-------|------|
| Governance | Four engineering gates: assumptions, simplicity, surgical scope, verification. |
| Adapter runtime | Thin Codex, Claude Code, and Cursor surfaces that route to one contract. |
| Assisted installer | Detects runtime, classifies project state, preserves existing governance, and reports rollback. |
| Obsidian-ready mesh | Markdown properties, wikilinks, state, roadmap, decisions, quality gates, and evidence under `docs/agents/**`. |
| Local oracles | Validation, smoke, platform, materialization, MCP, Cortex, and Field Reports checks. |
| Evidence loop | Certification reports, evals, parity gates, and sanitized operational feedback. |
| Cortex | The continuity layer: auditable Markdown memory, recall, curation, and read-only MCP access. |

## 2. Trust And Audit

TES does **not** push, publish, tag, amend commits, change remotes, install
marketplace assets, send code telemetry, write `.obsidian/**`, or overwrite
project-owned governance without explicit approval.

For this reference package, the full local closure gate is:

```bash
npm run commit:check
```

Focused maintainer gates:

```bash
npm run validate
npm run install:smoke
npm run cortex:self-test
npm run cortex:quality:self-test
npm run cortex:mcp:self-test
npm run field-reports:self-test
npm run field-reports:quality:self-test
npm run platform:surface:check
```

## Documentation

| Need | Link |
|------|------|
| Installation mini prompt | [docs/install/MINI-PROMPT.md](docs/install/MINI-PROMPT.md) |
| Live GitHub Pages landing | [murillodutt.github.io/tilly-engineer-skills](https://murillodutt.github.io/tilly-engineer-skills/) |
| Public installer bundle | [docs/dist/0.3.80/tilly-engineer-skills-0.3.80.zip](docs/dist/0.3.80/tilly-engineer-skills-0.3.80.zip) |
| GitHub Pages landing source | [docs/index.html](docs/index.html) |
| Current roadmap | [docs/roadmap/README.md](docs/roadmap/README.md) |
| RC1 readiness roadmap | [docs/roadmap/RC1-READINESS-ROADMAP.md](docs/roadmap/RC1-READINESS-ROADMAP.md) |
| User manual | [docs/install/USER-MANUAL.html](docs/install/USER-MANUAL.html) |
| Agent manual | [docs/install/AGENT-MANUAL.md](docs/install/AGENT-MANUAL.md) |
| Command routing | [docs/install/COMMAND-TRIGGERS.md](docs/install/COMMAND-TRIGGERS.md) |
| Context mesh method | [docs/mesh/CONTEXT-MESH-METHOD.md](docs/mesh/CONTEXT-MESH-METHOD.md) |
| Cortex continuity | [docs/mesh/CORTEX.md](docs/mesh/CORTEX.md) |
| Read-only MCP | [docs/mesh/CORTEX-MCP.md](docs/mesh/CORTEX-MCP.md) |
| Field Reports | [docs/mesh/FIELD-REPORTS.md](docs/mesh/FIELD-REPORTS.md) |
| Adapter support | [docs/adapters/ADAPTER-CAPABILITY-MATRIX.md](docs/adapters/ADAPTER-CAPABILITY-MATRIX.md) |

## License

MIT. See [LICENSE](LICENSE).
