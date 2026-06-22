---
tds_id: roadmap.goal_super_spec.goal_maestro_execute_loop
tds_class: roadmap
status: active
consumer: maintainers, Goal Maestro authors, adapter authors, oracle authors, and execution agents
source_of_truth: true
evidence_level: L2
tver: 0.1.0
---

# Goal Maestro Execute Loop Super SPEC

## Canonical Artifact

`tes-goal-maestro` must gain an opt-in execution runner contract activated only
by `--execute-loop`.

## Certified Context

`tes-goal-maestro` already materializes mature artifacts into execution-grade
trees and `/goal` prompts. `next_prompt_handoff=true` and
`--next-prompt-handoff` are chat-only continuation helpers and do not execute
implementation.

## Phase Boundary

This phase defines the delivered skill contract, references, trigger docs, and
oracles for `--execute-loop`. It does not create hidden background automation,
remote push behavior, secrets handling, or a separate CLI runner.

## Central Rule

The parent runner is the authority. Subagents execute one active SPEC; the
parent validates material evidence before opening the next loop.

## Non-Objectives

- No default execution behavior.
- No remote sync or push.
- No ledger file by default.
- No compacted prompt package for worker subagents.
- No execution of the next prompt by the worker.

## Execution Contract

`--execute-loop` requires:

1. an `Execution Cost Draft` from material SPEC/tree sources before spawning;
2. one clean worker subagent per `ACTIVE_SPEC`;
3. the full prompt plus a hard `ACTIVE_SPEC=SPEC-00N` envelope for each worker;
4. local automatic commit per green SPEC;
5. three attempts per SPEC version;
6. up to two `SPEC_REPAIR_BY_LLM` commits per active SPEC, each resetting the
   attempt counter because the contract changed;
7. escalation after failed attempts or unstable repair: predictive code
   analysis, MCP/official knowledge such as Context7, sanitized cloud query,
   then stop;
8. parent-generated next prompt using worker evidence as input;
9. `Executive Stop Audit` by a separate read-only reviewer before final stop;
10. `SPEC-AUDIT-*` corrective units when the audit returns `NEEDS_MORE_LOOPS`.

## Stop States

- `NEEDS_EXECUTION_LOOP_DRAFT`: material sources are insufficient to draft the
  loop cost.
- `SPEC_BLOCKED`: a SPEC cannot converge after attempts and escalation.
- `SPEC_CONTRACT_UNSTABLE`: a SPEC needs more repairs than allowed after
  escalation.
- `NEEDS_OWNER_DECISION`: safe progress needs owner authority.
- `EXECUTION_LOOP_COMPLETE`: all declared SPECs pass and audit confirms stop.
- `EXECUTION_LOOP_COMPLETE_WITH_AUDIT_REPAIRS`: audit-added SPECs converged.

## Acceptance

- `tes-goal-maestro` clearly separates prompt generation from opt-in execution.
- The `--execute-loop` flow is documented in a dedicated reference.
- Public trigger docs mention the opt-in runner and local-commit/no-push
  boundary.
- Command trigger oracle verifies the new trigger terms.
- Adapter source and local mirrors remain in parity.
