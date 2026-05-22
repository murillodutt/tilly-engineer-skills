# TES Goal Maestro Contract History

## Purpose

`tes-goal-maestro` materializes a mature input artifact and internally
validated materialization tree into a ready maestral `/goal` prompt.

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
| Maintainer corrective audit, 2026-05-20 | Commit messages and empty commits are not execution evidence; each unit needs material-diff proof and sync certification. | high |
| Maintainer directive, 2026-05-22 | Generated Super SPEC content must leave the context window and be materialized as `GOAL-SUPER-SPEC-**.md`. | high |

## Source Search Ledger

| Window | Query | Occurrences | Meaning |
|--------|-------|-------------|---------|
| 2026-05-20 | `tes-goal-maestro` | none before creation | New delivered TES skill. |
| 2026-05-20 | `maestral`, `/goal` | recipe existed outside TES package source | Portable method promoted without project-specific references. |

## Contracts Preserved

- Activate only after explicit invocation or a direct request for a maestral
  `/goal` prompt.
- Refuse immature SPECs with `NEEDS_SPEC_MATURITY`.
- Produce `READY_GOAL_PROMPT` in the same response when the input artifact is
  mature and the generated tree passes internal gates.
- Stop with `NEEDS_TREE_REPAIR` when the tree fails schema, ownership, oracle,
  fidelity, material-continuation, semantic negative-grep, commit-rhythm or
  closeout gates.
- Require material-diff proof, focused oracles, reviewer result, post-commit
  status and sync status for each material execution unit.
- Treat prior commits and closeouts as baseline context by default, not
  execution credit for a new materialization run.
- Keep negative grep semantic when policy vocabulary is valid but the behavior
  is forbidden.
- Prefer centralized material edits for strict commit-per-unit queues unless
  write scopes are explicitly disjoint and serialized.
- Treat local commit certification as default sync. Remote sync requires
  explicit authorization.
- Ask for tree acceptance only when the user explicitly requests staged review
  or a change to the declared execution contract requires owner acceptance.
- Keep output chat-first and save only on request, except generated Super SPEC
  artifacts, which must be written as `GOAL-SUPER-SPEC-<slug-or-timestamp>.md`
  and summarized in chat.
- Always include `SPEC-000 Preflight And Baseline`.
- Keep the skill neutral and free of project-specific origin stories,
  absolute paths, or domain examples.

## Known Failure Modes Prevented

- Generating execution prompts from immature SPECs.
- Hiding architectural decisions inside a long `/goal` prompt.
- Pasting generated Super SPEC bodies into the context window instead of
  linking to a durable Markdown artifact.
- Mixing semantic meaning with physical mechanics too early.
- Assigning subagents without file ownership.
- Running broad implementation without per-SPEC oracles.
- Accumulating many SPECs before commit.
- Treating empty commits or compacted broad commits as proof of per-unit
  execution.
- Treating prior commits or old closeouts as automatic execution credit.
- Blocking valid safety vocabulary with broad lexical grep while missing the
  forbidden runtime behavior.
- Parallelizing overlapping write scopes in a strict commit-per-unit queue.
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
| 2026-05-20 | Changed tree acceptance from conversational permission to internal quality gate. | Maintainer bug report after skill stopped at tree acceptance despite explicit invocation. | high |
| 2026-05-20 | Added material-diff and sync-commit gates so empty commits cannot certify material units. | Corrective audit after execution-unit fidelity mismatch. | high |
| 2026-05-20 | Added material-continuation, semantic negative-grep and sequential ownership gates. | Maintainer-evolved canary skill in `~/Dev/<project-a>/.agents/skills/tes-goal-maestro/**`. | high |
| 2026-05-22 | Added default Super SPEC artifact materialization as `GOAL-SUPER-SPEC-<slug-or-timestamp>.md` and forbade pasting the full generated Super SPEC in chat. | Maintainer requested smaller context-window footprint for Goal Maestro. | high |

## Do Not Lose

The skill is not an implementation runner by default. Its job is to force input
artifact maturity and internal tree validation before producing the `/goal`
contract. Do not turn the tree gate into an unnecessary permission prompt, do
not weaken fidelity for convenience, do not let prior commits or empty commits
mask missing material execution, do not collapse semantic negative grep into
broad vocabulary bans, do not paste generated Super SPEC bodies into chat, and
do not add project-specific examples.
