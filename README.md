# Tilly Engineer Skills

Portable agent-engineering discipline for reducing ambiguity, overbuilding,
drive-by edits, and false completion in coding agents.

Version: `0.1.0`.

This is the independent DUTT reference project for Tilly Engineering
Discipline. It started from a small Codex/Claude/Cursor guideline package, then
was regressed into a clean standalone source package so other projects can
adopt the method without inheriting local repo history.

The field result was much larger than the file size: when the four gates were
connected to a context mesh, ambiguity dropped sharply and code became smaller,
more precise, and easier to converge.

## Core Contract

```text
Assumptions visible. Scope smaller. Edits surgical. Success falsifiable.
```

For non-trivial coding, review, refactor, or instruction-migration work, every
agent must pass four gates:

| Gate | Blocks |
|------|--------|
| Think Before Coding | Silent assumptions, hidden confusion, wrong interpretation |
| Simplicity First | Overbuilt APIs, speculative features, one-use abstractions |
| Surgical Changes | Drive-by edits, style churn, unrelated cleanup |
| Goal-Driven Execution | Vague closure, missing tests, "make it work" loops |

## Success Formula

For portable use, success is multiplicative:

```text
E = A * S * C * V
```

| Factor | Meaning |
|--------|---------|
| `A` | Assumptions and ambiguity are visible before action |
| `S` | Scope is simplified before implementation |
| `C` | Changes are constrained to the requested cut |
| `V` | Verification is explicit before closure |

If any factor is zero, the agent should stop, ask, or repair before claiming
success.

## Repository Shape

Root is intentionally thin. Source belongs in `src/**`; method and evaluation
material belongs in `docs/**`.

| Path | Purpose |
|------|---------|
| `AGENTS.md` | Thin bootloader for agents working in this repository |
| `src/adapters/codex/**` | Codex bootloader and skill source |
| `src/adapters/claude/**` | Claude instruction, plugin, and legacy skill source |
| `src/adapters/cursor/**` | Cursor guide and always-on rule source |
| `docs/mesh/**` | Principles, context mesh method, and scorecard |
| `docs/evals/**` | Eval design and examples |
| `docs/governance/**` | Cross-tool alignment, authority, and no-go rules |
| `docs/adapters/**` | Human adapter guidance |
| `docs/architecture/**` | Repository structure and ownership |
| `docs/tds/**` | Documentation contract and governed index |
| `benchmarks/context-mesh/eval-dataset.json` | Starter eval dataset |
| `scripts/**` | Deterministic package checks |
| `dist/adapters/**` | Generated install trees, ignored by Git |

Start with [docs/INDEX.md](docs/INDEX.md) for the complete documentation map.

## Install

Open the target project in Codex, Claude Code, or Cursor. Paste this prompt:

```text
Install Tilly Engineer Skills as an assisted context mesh, not as blind file
copying.

Read and follow this raw installer spec:

https://raw.githubusercontent.com/murillodutt/tilly-engineer-skills/main/docs/install/ASSISTED-CONTEXT-INSTALLER.prompt.md

Run in quiet installer mode: show compact progress, blockers and the final
certification report only. When a menu is required, render the complete labeled
menu from the spec before asking for a number. Do not display internal
reasoning, scratch YAML or long inventories.

Start by detecting the current IDE/runtime and classifying this project as new
or existing. Use the detected IDE as the default adapter. Ask me for a menu
choice only where the spec requires one. Preserve local project governance,
move durable agent context into docs/agents/**, keep AGENTS.md, CLAUDE.md and
Cursor rules as thin runtime bootloaders, and finish with the certification
report required by the spec.
```

## Manual Install By Tool

### Codex

1. Copy or merge `src/adapters/codex/AGENTS.md` into the target repository
   root `AGENTS.md`.
2. Copy `src/adapters/codex/skills/tilly-engineering-discipline/` into the
   target repository's `.agents/skills/tilly-engineering-discipline/`.
3. Run this package's validation locally before distributing changes:

```bash
npm run validate
```

Codex should load `AGENTS.md` as persistent repo guidance and discover the skill
through metadata. The skill body and references load only when the task needs
them.

### Cursor

Copy `src/adapters/cursor/rules/tilly-guidelines.mdc` into the target repo's
`.cursor/rules/` directory. It uses `alwaysApply: true` because the four gates
are a behavioral overlay.

### Claude Code

Use `src/adapters/claude/CLAUDE.md` as the target root instruction file, or use
the plugin metadata in `src/adapters/claude/plugin/` when packaging for Claude.

## Local Development

This repository is optimized for local-only commits:

```bash
npm run validate
npm run tds:validate
npm run materialize:check
npm run benchmark:plan
npm run commit:check
```

To create an explicit local context-mesh evidence run without paid backends:

```bash
npm run benchmark:run -- --backend fixture
```

`commit:check` is stricter than `validate`: required package files must be
staged or already tracked, which prevents local hooks from passing with critical
new files left outside the commit.

To generate installable adapter trees:

```bash
npm run materialize:all
```

The generated output lands in `dist/adapters/**`. Do not edit it directly; edit
`src/adapters/**` and materialize again.

The local Git hook in `.githooks/pre-commit` runs the same package checks before
commit. No remote or publishing flow is configured by default.
