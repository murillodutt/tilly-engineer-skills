# Tilly Engineering Discipline

Portable agent-engineering discipline for reducing ambiguity, overbuilding,
drive-by edits, and false completion in coding agents.

Version: `0.1.0`.

This is the independent DUTT reference project for Tilly Engineering Discipline.
It started from a small Claude/Cursor guideline package, then regressed into a
clean standalone baseline so other projects can adopt the method without
inheriting local repo history.

The field result was much larger than the file size: when the four gates were
connected to a context mesh, ambiguity dropped sharply and code became smaller,
more precise, and easier to converge.

The hardened version keeps that simple behavioral core and adds a Codex-native
derivation with progressive disclosure, validation, and explicit context
boundaries.

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

For Codex context systems, see [CODEX.md](CODEX.md) and the Codex skill in
`.agents/skills/tilly-engineering-discipline/`.

## Repository Layout

| Path | Purpose |
|------|---------|
| `PRINCIPLES.md` | Tool-neutral source of truth |
| `METHOD.md` | Context-mesh method: rent, ablation, adversarial evals, distractors |
| `EVALS.md` | Portable eval and ablation design |
| `AGENTS.md` | Codex repository bootloader template |
| `CODEX.md` | Codex-specific installation and usage |
| `SCORECARD.md` | Adoption scorecard for real convergence |
| `CLAUDE.md` | Claude Code root instruction variant |
| `.cursor/rules/tilly-guidelines.mdc` | Cursor always-on project rule |
| `skills/tilly-guidelines/SKILL.md` | Legacy Claude-style skill |
| `.agents/skills/tilly-engineering-discipline/**` | Codex-native skill derivation |
| `benchmarks/context-mesh/eval-dataset.json` | Starter eval dataset |
| `EXAMPLES.md` | Optional detailed examples; do not load by default |
| `scripts/validate_reference_package.py` | Local package integrity check |
| `scripts/context_mesh_plan.py` | Deterministic ablation matrix planner |

## Install By Tool

### Codex

1. Copy or merge `AGENTS.md` into the target repository root.
2. Copy `.agents/skills/tilly-engineering-discipline/` into the target
   repository's `.agents/skills/`.
3. Run:

```bash
npm run validate
```

Codex should load `AGENTS.md` as persistent repo guidance and discover the skill
through metadata. The skill body and references load only when the task needs
them.

### Cursor

Copy `.cursor/rules/tilly-guidelines.mdc` into the target repo. It uses
`alwaysApply: true` because the four gates are a behavioral overlay.

### Claude Code

Use `CLAUDE.md` as the root instruction file or install the Claude plugin
metadata included in `.claude-plugin/`.

## Operating Rule

Use the full discipline for material work. Use judgment for trivial changes
such as typo fixes or obvious one-liners.

This package is working if diffs are smaller, clarifying questions happen
before mistakes, implementation avoids speculative machinery, and closure is
proved by a concrete oracle.

## Local Development

This repository is optimized for local-only commits:

```bash
npm run validate
npm run benchmark:plan
npm run commit:check
```

The local Git hook in `.githooks/pre-commit` runs the same package checks before
commit. No remote or publishing flow is configured by default.
