# Execution Loop Runner

Use this reference only when `tes-goal-maestro` was explicitly invoked with
`--execute-loop` after a mature input artifact can produce a
`READY_GOAL_PROMPT`.

## Core Rule

```text
The parent runner owns the loop. Workers execute one ACTIVE_SPEC.
```

The execution loop is not default Goal Maestro behavior. It is an opt-in
execution layer that runs after prompt materialization, uses subagents for
bounded execution, and lets the parent validate evidence before the next loop.

## Lifecycle

Use these states:

```text
ready_goal_prompt -> execution_cost_drafted -> active_spec_opened ->
active_spec_committed -> next_prompt_ready -> executive_stop_audit ->
execution_loop_complete
```

Stop or branch with:

- `NEEDS_EXECUTION_LOOP_DRAFT`
- `SPEC_BLOCKED`
- `SPEC_CONTRACT_UNSTABLE`
- `NEEDS_MORE_LOOPS`
- `NEEDS_OWNER_DECISION`
- `SAFETY_BLOCKED`
- `EXECUTION_LOOP_COMPLETE`
- `EXECUTION_LOOP_COMPLETE_WITH_AUDIT_REPAIRS`

## Execution Cost Draft

Before spawning any worker, produce an `Execution Cost Draft` from material
sources only: the SPEC, Super SPEC, accepted tree, generated `/goal`, existing
commits, and relevant oracles. Do not rely on memory.

The draft must state:

1. source artifacts read;
2. predicted SPEC count and order;
3. dependency edges between SPECs;
4. risk level per SPEC;
5. expected oracles per SPEC;
6. likely subagent count;
7. expected local commits;
8. likely repair points;
9. expected final stop;
10. known conditions that would require audit-added loops.

If the draft cannot be produced from material sources, stop with
`NEEDS_EXECUTION_LOOP_DRAFT`.

## Pre-SPEC Reflection

Before every worker spawn, the parent must produce a short pre-SPEC reflection:

1. reread the active SPEC and material evidence from prior loops;
2. declare `ACTIVE_SPEC=SPEC-00N`;
3. restate allowed files and forbidden files/actions;
4. restate focused oracles and negative checks;
5. state local risk and likely repair pressure;
6. confirm the worker may execute only the active SPEC.

This reflection is mandatory even when the previous loop generated a next
prompt.

## Worker Packet

Each worker receives the full generated prompt, not a compacted summary. The
parent must add a hard envelope above it:

```text
ACTIVE_SPEC=SPEC-00N
Execute only ACTIVE_SPEC.
Do not execute any later SPEC.
Do not generate the final next prompt; you may propose next-prompt material.
Do not push or perform remote sync.
Return the evidence block required by the prompt.
```

Workers may repair the active SPEC when execution proves the active SPEC is
incorrect, incomplete, or ambiguous. They may not repair other SPECs.

## Attempts And SPEC Repair

Each SPEC version gets three local attempts.

If the active SPEC itself must change:

1. mark the change as `SPEC_REPAIR_BY_LLM`;
2. state that the repair was proposed and executed by the LLM, not a human;
3. record cause, evidence, diff, impact, and oracle;
4. commit the repair separately before implementation;
5. rerun pre-SPEC reflection;
6. reset the attempt counter because the contract changed.

Allow at most two SPEC repairs per active SPEC. If more repair is needed, run
the escalation ladder before stopping with `SPEC_CONTRACT_UNSTABLE`.

## Escalation Ladder

After three failed attempts for a SPEC version, or after two repairs still
leave the active SPEC unstable, run:

1. predictive code analysis against the material code and SPEC evidence;
2. MCP or official knowledge sources such as Context7 for library/framework/API
   questions;
3. sanitized cloud query only with minimal anonymized error, public API facts,
   and non-secret example context;
4. stop if unresolved.

Never send secrets, private paths, proprietary diffs, project names, storage
backends, credentials, or raw internal payloads to cloud tools.

## Parent Validation

The parent advances only after validating:

1. active SPEC id;
2. changed files are inside the allowed matrix;
3. focused oracles passed;
4. negative checks passed;
5. local commit exists for the active SPEC or accepted no-commit rationale;
6. `git show --stat --oneline <commit>` proves material diff;
7. post-commit status is inspected;
8. sync status is `LOCAL_COMMITTED` or `REMOTE_SYNC_NOT_REQUESTED`;
9. worker did not execute later SPECs.

Remote push is forbidden unless separately authorized by the user.

## Next Prompt Authority

The worker may propose next-prompt material, but the parent generates the next
prompt. The parent must use worker evidence, material commits, and the original
tree to decide whether the next SPEC may open.

If validation fails, do not generate the next prompt. Continue repair within
the active SPEC or stop with the matching status.

## Subagent Lifecycle

Use a new worker subagent per active SPEC. After the parent captures and
validates evidence, close the worker. If subagent capacity is exhausted, the
parent may close completed, degraded, or no-longer-needed subagents after
capturing evidence.

Do not keep subagents open as memory. Git commits and parent-held evidence are
the state.

## Loop State

Default loop state lives in the parent context plus Git. Do not write a ledger
file by default.

If the user explicitly requests `--execute-loop-ledger`, create a compact
ledger and shard it before it becomes ingestion debt.

## Executive Stop Audit

When the planned stop is reached, do not close automatically. Spawn a separate
read-only reviewer for `Executive Stop Audit`.

The reviewer receives:

1. original materialization tree;
2. executed SPECs;
3. commits and `git show --stat` evidence;
4. oracles and negative checks;
5. repair records;
6. final worktree status.

The reviewer does not receive the full original prompt unless the parent
decides that a prompt contract dispute is the audit subject.

The reviewer recommends one of:

- `EXECUTION_LOOP_COMPLETE`
- `EXECUTION_LOOP_COMPLETE_WITH_AUDIT_REPAIRS`
- `NEEDS_MORE_LOOPS`
- `SPEC_BLOCKED`
- `SPEC_CONTRACT_UNSTABLE`
- `NEEDS_OWNER_DECISION`
- `SAFETY_BLOCKED`

The parent makes the final decision.

## Audit Repairs

If audit returns `NEEDS_MORE_LOOPS`, create formal corrective units named
`SPEC-AUDIT-001`, `SPEC-AUDIT-002`, and so on. These are appended as audit
repairs; do not rewrite the original materialization tree.

Audit repair units use the same loop rules: active SPEC envelope, local commit,
oracles, parent validation, and final audit.

## Completion

Use `EXECUTION_LOOP_COMPLETE` only when all declared SPECs passed and the
Executive Stop Audit confirms no more loops are needed.

Use `EXECUTION_LOOP_COMPLETE_WITH_AUDIT_REPAIRS` when the loop converged only
after audit-added corrective SPECs.
