# TES Goal Maestro Contract History

## Purpose

`tes-goal-maestro` materializes a mature SPEC and accepted materialization tree
into a ready maestral `/goal` prompt.

## Why This Skill Exists

Repeated mature-SPEC execution loops showed that high-leverage work succeeds
when the execution prompt is treated as a contract: artifact, context,
non-objectives, phase boundary, ownership, oracles, review, commit discipline,
and stop states are explicit before implementation begins.

The skill preserves that portable pattern without baking in project-specific
examples or origins.

## Origin Signals

| Source | Signal | Confidence |
|--------|--------|------------|
| Maintainer-provided maestral materialization recipe, 2026-05-20 | `/goal` prompts work best as execution contracts after SPEC maturity. | high |
| Maintainer directive, 2026-05-20 | The skill must be neutral and must not mention project-specific origin stories. | high |
| Maintainer directive, 2026-05-20 | Output is chat-first and saved only on explicit request. | high |

## Source Search Ledger

| Window | Query | Occurrences | Meaning |
|--------|-------|-------------|---------|
| 2026-05-20 | `tes-goal-maestro` | none before creation | New delivered TES skill. |
| 2026-05-20 | `maestral`, `/goal` | recipe existed outside TES package source | Portable method promoted without project-specific references. |

## Contracts Preserved

- Activate only after explicit invocation or a direct request for a maestral
  `/goal` prompt.
- Refuse immature SPECs with `NEEDS_SPEC_MATURITY`.
- Produce `DRAFT_MATERIALIZATION_TREE` when the SPEC is mature but the tree is
  not explicit and accepted.
- Return `NEEDS_TREE_ACCEPTANCE` when a draft tree exists but has not been
  explicitly accepted.
- Produce `READY_GOAL_PROMPT` only after SPEC maturity and tree acceptance.
- Assign a readiness score before final prompt generation.
- Keep output chat-first and save only on request.
- Always include `SPEC-000 Preflight And Baseline`.
- Require every SPEC slice to name objective, files, owner, oracles, negative
  checks when relevant, and semantic commit.
- Keep the skill neutral and free of project-specific origin stories,
  absolute paths, or domain examples.

## Known Failure Modes Prevented

- Generating execution prompts from immature SPECs.
- Hiding architectural decisions inside a long `/goal` prompt.
- Mixing semantic meaning with physical mechanics too early.
- Assigning subagents without file ownership.
- Running broad implementation without per-SPEC oracles.
- Emitting weak materialization trees without file ownership, negative grep,
  review loop, stop states, or commit rhythm.
- Generating prompts that accidentally authorize live execution, persistence,
  public-surface drift, destructive operations, external access, secrets, or
  private data without SPEC authority.
- Accumulating many SPECs before commit.
- Ending with prose instead of evidence and stop states.

## Relationship To Other Skills

`tes-goal-maestro` sits after design/specification and before implementation.
`tes-prospect` pressures a plan or design. `tes-mine` extracts durable language
and decisions. Tilly Engineering Discipline remains the general implementation
discipline once execution begins.

## Changelog

| Date | Change | Evidence | Confidence |
|------|--------|----------|------------|
| 2026-05-20 | Created `tes-goal-maestro` as a neutral SPEC-to-`/goal` materialization skill. | Maintainer alignment in current session; maestral materialization recipe. | high |
| 2026-05-20 | Promoted the <project-A>-hardened `0.2.0` contract: readiness scoring, tree acceptance state, modular materialization-tree, subagent/oracle, and quality-gate references. | `/Users/murillo/Dev/<project-a>/.agents/skills/tes-goal-maestro/**`; maintainer directive to bring improvements back to TES. | high |

## Do Not Lose

The skill is not an implementation runner. Its job is to force SPEC maturity,
execution-grade tree acceptance, readiness scoring, and prompt hardening before
producing the `/goal` contract. Do not weaken that gate for convenience, and do
not add project-specific examples.
