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

## Trigger Interaction

If `--execute-loop` appears together with `next_prompt_handoff=true` or
`--next-prompt-handoff`, the execution loop takes precedence for internal
continuation. The parent runner may generate and execute the next active-SPEC
prompt only after parent validation of the current SPEC. The ordinary
Next Prompt Handoff rule still applies after the loop stops or completes, and
workers remain forbidden from authoritative next-prompt generation or later
SPEC execution.

`--execute-loop` authorizes the parent to orchestrate the loop, not to replace
worker execution when worker creation is unavailable. Parent-side worker
fallback requires the exact `--execute-loop-parent-fallback` flag in the current
user request.

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

Inspect the worktree before drafting. If `git status --short --branch
--untracked-files=all` shows existing changes, classify them as owner baseline,
current-loop material, unrelated user work, or blocker. Do not open the first
worker until the baseline is clean or explicitly classified in the draft; stop
with `NEEDS_OWNER_DECISION` when ownership cannot be proven.

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
10. known conditions that would require audit-added loops;
11. baseline worktree state and classification;
12. canonical SPEC artifact path for any future `SPEC_REPAIR_BY_LLM`;
13. audit-repair cycle budget;
14. persistent ledger decision and path when required.

If the draft cannot be produced from material sources, stop with
`NEEDS_EXECUTION_LOOP_DRAFT`.

## Pre-SPEC Reflection

Before every worker spawn, the parent must produce a short pre-SPEC reflection:

1. reread the active SPEC and material evidence from prior loops;
2. declare `ACTIVE_SPEC=SPEC-00N`;
3. restate allowed files and forbidden files/actions;
4. restate focused oracles and negative checks;
5. state local risk and likely repair pressure;
6. emit the loop-state block;
7. confirm the worker may execute only the active SPEC.

This reflection is mandatory even when the previous loop generated a next
prompt.

The loop-state block is mandatory before every attempt and after every failed
attempt:

```text
ACTIVE_SPEC=SPEC-00N
spec_version=<source revision or repair version>
attempt=<1..3>
repair_count=<0..2>
audit_repair_cycle=<0..N>
last_commit=<sha or none>
failed_attempt_residue=<none|classified|blocked>
next_allowed_action=<worker_attempt|failed_attempt_recovery|spec_repair|escalation|audit|stop>
worktree_state=<clean|classified_dirty|blocked>
```

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
4. update the canonical material SPEC artifact, such as the source SPEC or the
   generated `GOAL-SUPER-SPEC-<slug-or-timestamp>.md` artifact;
5. commit the repair separately before implementation;
6. rerun pre-SPEC reflection with a new `spec_version`;
7. reset the attempt counter because the contract changed.

If the active SPEC exists only in chat, materialize or expand the required
Super SPEC artifact before the repair commit. If no canonical repair target can
be created from material sources, stop with `NEEDS_TREE_REPAIR`.

Allow at most two SPEC repairs per active SPEC. If more repair is needed, run
the escalation ladder before stopping with `SPEC_CONTRACT_UNSTABLE`.

## Failed Attempt Recovery

After any failed worker attempt, inspect `git status --short --branch
--untracked-files=all` and the diff before opening another attempt. The parent
must emit a `Failed Attempt Recovery` block:

```text
ACTIVE_SPEC=SPEC-00N
failed_attempt=<attempt number>
residue_files=<paths or none>
residue_origin=<current_attempt|preexisting_baseline|mixed|unknown>
decision=<commit_valid_material|spec_repair|revert_current_attempt|stop>
oracle=<command or review proving the decision>
```

The next attempt may start only when residue is resolved. Valid material may be
committed only if it satisfies the active SPEC evidence contract. A SPEC defect
must become `SPEC_REPAIR_BY_LLM` before implementation continues. Reverting is
allowed only for changes proven to belong wholly to the current failed attempt;
never revert pre-existing baseline or user work. If residue is mixed or
ownership is unknown, stop with `NEEDS_OWNER_DECISION`.

## Escalation Ladder

After three failed attempts for a SPEC version, or after two repairs still
leave the active SPEC unstable, run:

1. predictive code analysis against the material code and SPEC evidence;
2. MCP or official knowledge sources such as Context7 for library/framework/API
   questions;
3. sanitized cloud query only after explicit owner approval of the exact
   sanitized payload, using minimal anonymized error, public API facts, and
   non-secret example context;
4. stop if unresolved.

Never send secrets, private paths, proprietary diffs, project names, storage
backends, credentials, or raw internal payloads to cloud tools.

Before any cloud query, produce a `Cloud Query Redaction Block` with:

1. sanitized payload to be sent;
2. redacted terms and categories;
3. confirmation that no secrets, private paths, project names, storage
   backends, credentials or raw internal payloads remain;
4. owner approval reference from the current execution context.

If the owner does not approve the exact sanitized payload, stop with
`NEEDS_OWNER_DECISION`; if sanitization cannot remove sensitive material, stop
with `SAFETY_BLOCKED`.

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
9. worker did not execute later SPECs;
10. parent refreshed local state by rereading the relevant changed files,
    active SPEC artifact and latest `git show` evidence before creating the
    next prompt.

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

If no worker can be created after capacity cleanup, do not silently collapse
the loop. The parent may execute under the same `ACTIVE_SPEC` envelope only
when the current user request explicitly authorized parent-side loop execution
with the exact `--execute-loop-parent-fallback` flag; otherwise stop with
`NEEDS_OWNER_DECISION`.

Do not keep subagents open as memory. Git commits and parent-held evidence are
the state.

## Loop State

Default loop state lives in the parent context plus Git for short clean loops.
The loop-state block is still mandatory in the parent evidence for every
attempt.

Create a persistent Markdown ledger named
`GOAL-EXECUTION-LOOP-LEDGER-<slug-or-timestamp>.md` when the user explicitly
requests `--execute-loop-ledger`, the draft predicts more than three SPECs, a
SPEC repair occurs, an audit repair unit is appended, or execution resumes
after context compaction and the parent cannot prove exact loop state from the
current context plus Git.

Shard the ledger before it becomes ingestion debt. The ledger must carry only
SPEC id, spec version, attempt, repair count, audit cycle, failed-attempt
recovery decision, commit, oracle status, stop state and next allowed action.

### Ledger Schema

Each ledger entry must use one active SPEC or audit unit and include these exact
field labels:

```text
spec_id:
spec_version:
attempt:
repair_count:
audit_repair_cycle:
failed_attempt_recovery_decision:
commit:
oracle_status:
stop_state:
next_allowed_action:
```

The ledger must not store full prompt bodies, raw diffs, secrets, credentials,
private paths, chat transcripts or project-specific names.

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

The audit must name the exact missing units and the expected stop. After one
audit-repair batch, rerun Executive Stop Audit. A second `NEEDS_MORE_LOOPS`
recommendation may open another batch only when it names new material evidence
that was not available to the first audit. Repeated audit expansion without new
material evidence stops with `NEEDS_OWNER_DECISION` or
`SPEC_CONTRACT_UNSTABLE`.

## Completion

Use `EXECUTION_LOOP_COMPLETE` only when all declared SPECs passed and the
Executive Stop Audit confirms no more loops are needed.

Use `EXECUTION_LOOP_COMPLETE_WITH_AUDIT_REPAIRS` when the loop converged only
after audit-added corrective SPECs.
