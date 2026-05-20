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
- Produce `READY_GOAL_PROMPT` only after SPEC maturity and tree acceptance.
- Keep output chat-first and save only on request.
- Always include `SPEC-000 Preflight And Baseline`.
- Keep the skill neutral and free of project-specific origin stories,
  absolute paths, or domain examples.

## Known Failure Modes Prevented

- Generating execution prompts from immature SPECs.
- Hiding architectural decisions inside a long `/goal` prompt.
- Mixing semantic meaning with physical mechanics too early.
- Assigning subagents without file ownership.
- Running broad implementation without per-SPEC oracles.
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

## Do Not Lose

The skill is not an implementation runner by default. Its job is to force
SPEC maturity and tree acceptance before producing the `/goal` contract. Do not
weaken that gate for convenience, and do not add project-specific examples.
