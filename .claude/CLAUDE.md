# CLAUDE.md

Maintainer bootloader for the independent Tilly Engineer Skills package. Thin by
contract: the material discipline below mirrors the delivered Claude core
(`src/adapters/claude/CLAUDE.md`); the maintainer governance that constrains work
on the package itself lives in the root `AGENTS.md`, which is the complete
authority. Do not restate `AGENTS.md` here — point to it.

Distributable agent source lives in `src/**`. People-facing method, eval, and
architecture material lives in `docs/**`. Keep this file small.

## Core Contract

```text
Assumptions visible. Scope smaller. Edits surgical. Success falsifiable.
```

## Material Discipline

Apply to non-trivial coding, review, refactor, or instruction-migration work:

1. **Think Before Coding** — state assumptions, ambiguity, tradeoffs, and
   blockers before acting; never pick a risky interpretation silently.
2. **Simplicity First** — keep the root thin, avoid duplicate source copies, and
   solve only the requested problem; delete speculative scope before adding it.
3. **Surgical Changes** — treat `src/**` as adapter source and `docs/**` as
   governed explanation; touch only request-traceable lines. Classify every
   `scripts/**` change by consumer (maintainer gate vs. delivered behavior)
   before deciding which surfaces move.
4. **Goal-Driven Execution** — define a falsifiable oracle and run the smallest
   relevant gate before claiming closure.

```text
E = A * S * C * V
```

Success is zero if assumptions are hidden, scope is inflated, changes are not
surgical, or verification is missing.

## Runtime-First

TES is a product, not a governance archive. Build the smallest durable runtime
slice on the intended execution path before adding governance. No governance-only
cycles, long SPECs before code, placeholder boundaries, or throwaway runtimes.
Documentation must not become the work; prefer fixtures, oracles, and runtime
evidence over parallel explanatory documents.

## Always-On Regression Guard

For every package analysis, write, runtime change, oracle change, commit, or
closeout, self-consume `.agents/skills/tes-regression-guard/SKILL.md` as a local
reasoning kernel — not a user-invoked skill. Before changing behavior that
already has certified, installed, materialized, generated, or measured evidence,
name the last-known-good baseline, classify whether the change preserves,
extends, or replaces it, and list protected invariants first. Regression is
project-wide: a passing source check is not enough when the risk lives in an
installed, generated, materialized, public, or CLI surface.

## Mantra Gate

Before state-changing actions, use the TES Mantra Gate. When it permits
proceeding, show only `[🍳 Flash-Fry]`; the full gate still records `VERIFY`,
`SCOPE`, `BEST_PATH`, `DOCUMENT`, `ORACLE`, `RESOLVE`, and `STATUS` in the
evidence surface. Report gate detail only on `BLOCKED`/`NEEDS_REVIEW`, when
approval is needed, or when asked. The full gate protocol and adoption oracle are
defined in `AGENTS.md`.

## Feedback Voice

Short, frank prose. Lead with the conclusion, then the reasoning. Avoid tables,
bullet dumps, code blocks, and long inventories unless the user asks or the
artifact requires exact syntax (a routing table, a command, a roadmap partition).

## Confidentiality

Use neutral placeholder vocabulary only; no real project, product,
internal-service names, storage backends, archive formats, or `~/Dev/<name>`
paths in tracked content. The project's own infrastructure names (e.g.
`~/Dev/tes-canaries`) are allowed. Detail in `AGENTS.md`
`<confidentiality>`.

## Maintainer Authority

The complete maintainer governance for working on this package — maturity-layer
gate, real-project learning standard, target/source boundary, release identity,
operating calibration, and locks — is the root `AGENTS.md`. Read it before
closing any material package change. This file is the Claude entry point; it does
not duplicate that authority.

Key locks (full set in `AGENTS.md` `<locks>`):

- Do not put full source packages back in the repository root, or duplicate
  adapter source between `src/**` and hidden root tool folders.
- Commit locally by default; remote, push, publish, cloud, or marketplace
  actions need an explicit per-request private decision.
- Do not claim the package is sealed without `npm run commit:check`.
- Delivered behavior changes require a release-identity decision before closure
  (`AGENTS.md` `<release_identity>`).

## Routing

| Need | Source |
|------|--------|
| Maintainer governance authority | `AGENTS.md` |
| Project map | `docs/INDEX.md` |
| Repository structure | `docs/architecture/PROJECT-STRUCTURE.md` |
| Maintainer correlation rule | `docs/governance/MAINTAINER-CORRELATION-RULE.md` |
| Cross-tool governance | `docs/governance/AGENTIC-ALIGNMENT-GOVERNANCE.md` |
| Tool-neutral principles | `docs/mesh/PRINCIPLES.md` |
| Claude instruction source | `src/adapters/claude/CLAUDE.md` |
| Package validation | `python3 scripts/validate_reference_package.py` |
| Closure gate | `npm run commit:check` |
