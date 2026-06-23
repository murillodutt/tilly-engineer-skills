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
| Maintainer directive, 2026-06-22 | Next-prompt continuation must exist only as an explicitly requested parameter/trigger, not as default Goal Maestro behavior. | high |
| Maintainer directive, 2026-06-22 | Continuous execution requires a separate opt-in runner activated by `--execute-loop`, with parent authority, one active SPEC per worker, local commits, bounded LLM repair, and final executive audit. | high |
| Maintainer audit, 2026-06-22 | Execution Loop must resolve handoff precedence, expose branch statuses, preserve loop counters, classify dirty baselines, require canonical SPEC repairs, require owner-approved cloud redaction, and bound audit expansion. | high |
| Maintainer audit, 2026-06-22 | Execution Loop must resolve failed-attempt residue before retry, require explicit parent fallback authorization, persist loop state for long/repaired loops, and use prompt fixtures rather than only term checks. | high |
| Canary execution audit, 2026-06-23 | Reference implementations, manual builds, browser smoke results, run records and post-facto audits are baseline-only comparison evidence; `--execute-loop` requires strict sequential replay through fresh `ACTIVE_SPEC` execution. | high |

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
- Reject horizontal layer packages such as "all docs", "all scripts",
  "all tests" or broad cleanup when they replace declared vertical slices or
  asset-transfer units.
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
- Include Next Prompt Handoff only when explicitly requested by
  `next_prompt_handoff=true`, `--next-prompt-handoff`, or an equivalent direct
  trigger; when active, it is chat-only, post-`GO`, post-certification,
  non-writing by default and non-executing.
- Run Execution Loop only when explicitly requested by `--execute-loop`; when
  active, the parent runner owns the loop, drafts expected cost from material
  sources, opens one `ACTIVE_SPEC` per fresh worker subagent, validates local
  commit evidence before advancing, and runs Executive Stop Audit before final
  closure.
- When Next Prompt Handoff and Execution Loop are both requested,
  `--execute-loop` owns internal next-prompt continuation; ordinary chat-only
  handoff semantics apply only after the loop stops or completes.
- Execution Loop exposes `NEEDS_MORE_LOOPS`, `NEEDS_OWNER_DECISION`, and
  `SAFETY_BLOCKED` as branch states, carries loop-state evidence per attempt,
  requires canonical material SPEC repair targets, and stops before cloud
  escalation unless the owner approves the exact sanitized payload.
- Execution Loop requires failed-attempt recovery before retry, creates a
  persistent `GOAL-EXECUTION-LOOP-LEDGER-<slug-or-timestamp>.md` for long,
  repaired, audit-expanded or resumed loops, and treats parent-side worker
  fallback as disabled unless explicitly requested by
  the exact `--execute-loop-parent-fallback` flag.
- Execution Loop treats reference implementations, prior manual builds,
  browser smoke results, screenshots, run records and post-facto audits as
  baseline-only comparison evidence. They never satisfy execution credit; the
  loop must perform strict sequential replay through fresh `ACTIVE_SPEC`
  execution and parent validation.

## 2026-06-22 — Exact fallback flag and ledger oracle

- Parent-side fallback authorization now requires the exact
  `--execute-loop-parent-fallback` flag. Natural-language equivalents are no
  longer accepted for this high-risk collapse path.
- Execution-loop ledgers now have a deterministic field schema so generated
  `GOAL-EXECUTION-LOOP-LEDGER-*` artifacts can be validated instead of trusted
  as prose.
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
- Rewriting vertical slices into horizontal layer packages that no longer prove
  one behavior or asset failure end to end.
- Treating empty commits or compacted broad commits as proof of per-unit
  execution.
- Treating prior commits or old closeouts as automatic execution credit.
- Blocking valid safety vocabulary with broad lexical grep while missing the
  forbidden runtime behavior.
- Parallelizing overlapping write scopes in a strict commit-per-unit queue.
- Generating a next `/goal` prompt by default, before certification, into a
  file, or as an auto-executed continuation.
- Turning Goal Maestro into an unbounded autopilot, letting workers advance
  beyond `ACTIVE_SPEC`, skipping local commit evidence, attributing
  `SPEC_REPAIR_BY_LLM` to humans, or closing without Executive Stop Audit.
- Losing attempt/repair counters across context pressure, repairing SPEC text
  only in memory, querying cloud tools without owner-approved redaction, or
  expanding `SPEC-AUDIT-*` indefinitely after repeated audits.
- Carrying failed-attempt residue into a later attempt, silently replacing
  unavailable workers with parent execution, or relying on context-only state in
  long/repaired loops that need a ledger.
- Certifying `--execute-loop` from a reference implementation, manual build,
  browser smoke result, run record or post-facto audit instead of strict
  sequential replay.
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
| 2026-05-20 | Added material-continuation, semantic negative-grep and sequential ownership gates. | Maintainer-evolved canary skill in a private canary project (source-of-record kept off TES repository per project-confidentiality lock). | high |
| 2026-05-22 | Added default Super SPEC artifact materialization as `GOAL-SUPER-SPEC-<slug-or-timestamp>.md` and forbade pasting the full generated Super SPEC in chat. | Maintainer requested smaller context-window footprint for Goal Maestro. | high |
| 2026-06-22 | Added Vertical Slice Fidelity Gate to reject horizontal layer packages that replace declared vertical slices or asset-transfer units. | ADR 0005 asset-transfer run; `GM5-vertical-slices-not-horizontal-layers`; `python3 scripts/context_mesh_plan.py --dataset benchmarks/goal-maestro/eval-dataset.json`. | high |
| 2026-06-22 | Added opt-in Next Prompt Handoff through `next_prompt_handoff=true` or `--next-prompt-handoff`, restricted to chat-only post-certification prompt emission with no automatic execution. | Maintainer directive in current session; source skill and references updated. | high |
| 2026-06-22 | Added opt-in `--execute-loop` execution runner contract with Execution Cost Draft, active-SPEC worker isolation, local commits, bounded LLM SPEC repair, escalation ladder, parent next-prompt authority, and Executive Stop Audit. | `docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-goal-maestro-execute-loop.md`; maintainer directive in current session. | high |
| 2026-06-22 | Hardened `--execute-loop` after P1/P2/P3 audit: handoff precedence, branch statuses, baseline classification, loop-state block, canonical SPEC repair, owner-approved cloud redaction, bounded audit repairs and stronger trigger oracle coverage. | Maintainer audit in current session; source skill, references, command triggers and oracle updated. | high |
| 2026-06-22 | Closed remaining loop debts: failed-attempt recovery, explicit parent fallback trigger, automatic persistent ledger triggers, and generated-prompt fixture checks for execute-loop contracts. | Maintainer audit in current session; source skill, references, command triggers and oracle updated. | high |
| 2026-06-23 | Added reference-baseline credit gate: previous implementations, manual builds, browser smokes, run records and post-facto audits cannot validate `--execute-loop` without fresh sequential active-SPEC execution. | Real-project canary audit; source skill, references and oracle updated. | high |

## Do Not Lose

The skill is not an implementation runner by default. Its job is to force input
artifact maturity and internal tree validation before producing the `/goal`
contract. Do not turn the tree gate into an unnecessary permission prompt, do
not weaken fidelity for convenience, do not let prior commits or empty commits
mask missing material execution, do not collapse semantic negative grep into
broad vocabulary bans, do not paste generated Super SPEC bodies into chat, and
do not add project-specific examples. Do not make next-prompt continuation the
default; it requires an explicit parameter/trigger and remains chat-only,
post-certification, non-writing by default and non-executing. Do not make
execution automatic by default; `--execute-loop` is the only execution trigger,
and it requires material cost drafting, parent authority, local commit evidence,
bounded LLM repair, loop-state evidence, canonical SPEC repair artifacts,
failed-attempt recovery, persistent ledger triggers, explicit parent fallback
authorization, owner-approved cloud redaction, bounded audit repair, no remote
push, strict sequential replay, baseline-only treatment for reference
implementations and Executive Stop Audit.
