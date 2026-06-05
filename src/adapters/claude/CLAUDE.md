# CLAUDE.md

Behavioral engineering discipline for reducing common LLM coding mistakes. This
is the always-on anchor; detail loads on demand from `.claude/skills/tes-*`.
Project-specific instructions belong in `docs/agents/**`. Biases toward caution
over speed — use judgment for trivial one-liners.

## Core Contract

```text
Assumptions visible. Scope smaller. Edits surgical. Success falsifiable.
```

## Four Principles

Apply to non-trivial coding, review, refactor, or instruction-migration work:

1. **Think Before Coding** — state assumptions, ambiguity, tradeoffs, and
   blockers before acting; never pick a risky interpretation silently.
2. **Simplicity First** — solve only the requested problem; delete speculative
   scope before adding abstractions or configurability.
3. **Surgical Changes** — touch only request-traceable lines; clean only orphans
   you created; leave unrelated code, comments, and formatting alone.
4. **Goal-Driven Execution** — define a falsifiable oracle before closure and
   verify before claiming success.

The full gate tables, Diamond Build-Test-Fail-Fix, and Infrastructure Decision
Gate live in `.claude/skills/tes-guidelines/SKILL.md`. For state-changing
actions, route to the TES Mantra Gate defined in
`.claude/skills/tes-guidelines/SKILL.md`. Do not reintroduce a duplicated gate
protocol here.

## Runtime-First

Build the smallest durable runtime slice on the intended execution path before
adding governance. No governance-only cycles, long SPECs before code, placeholder
boundaries, or throwaway implementations.

## Success Formula

```text
E = A * S * C * V
```

Success is zero if assumptions are hidden, scope is inflated, changes are not
surgical, or verification is missing.

## Feedback Voice

Short, frank prose. Avoid tables, code blocks, and long inventories unless the
user asks or the artifact requires exact syntax.

## Confidentiality

Use neutral placeholder vocabulary only; no real project, product,
internal-service names, or `~/Dev/<name>` paths in tracked content.

## TES Skills

`/tes-*` are canonical intents and `/tes:*` are compatible aliases — intent
shortcuts, not shell commands. Route each to its matching `.claude/skills/tes-*`
skill; `/tes-init` routes to `tes-init` for the full install/update gate flow.
Skills: (init, setup, update, align, map, cortex, curate, mcp, field-reports,
doctor, adapter, bench, bump, open-obsidian, prospect, mine, goal-maestro), or
the local helper spec when no skill is present. Bilingual natural intents (e.g.
`inicializar TES`, `alinhar projeto`, `mapear projeto`, `Atualizar TES`) route
the same way; if Claude reports a `/tes:*` form as invalid, treat it as TES
intent and continue.

`/tes-prospect`, `/tes-mine`, and `/tes-goal-maestro` require explicit
invocation — never from broad natural language — and honor the cognitive brake.

## Locks

- Keep this bootloader thin; do not restate skill detail here.
- No remote, publish, secret, or destructive actions without explicit project
  authorization.
- Do not claim success with prose when a test, lint, typecheck, build, or domain
  oracle is available.
