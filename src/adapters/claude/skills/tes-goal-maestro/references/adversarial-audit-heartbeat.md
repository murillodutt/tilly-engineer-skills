# Adversarial Audit Heartbeat

Use this reference only when Goal Maestro receives an explicit heartbeat prompt
opt-in. The feature generates a copy-ready auditor prompt. It does not execute
the audit and does not become part of the execution loop.

## Core Rule

```text
The heartbeat observes available state and reports risk; it never owns the loop.
```

The heartbeat is an auditor prompt generator. It is not a scheduler, executor,
visual control surface, collection system, automation manager, sharing path, or
second Goal Maestro loop.

## Activation

Activate only from one of these exact triggers in the active request, active
structured control block, or active source artifact:

- `--audit-heartbeat-prompt`
- `audit_heartbeat=true`
- `adversarial_audit_heartbeat: requested`
- a direct request to generate or create an adversarial audit heartbeat prompt

Do not activate from broad words such as heartbeat, monitor, audit, mentorship,
watch this, keep an eye on it, or translated equivalents unless the request
explicitly asks for this heartbeat prompt capability.

Do not add a new `/tes-*` command, and do not change ordinary
`/tes-goal-maestro` activation. Do not add a new /tes-* command.

## Output

When activated, load
`templates/adversarial-audit-heartbeat.template.md` and emit a copy-ready
English prompt. Ordinary Goal Maestro prompts stay unchanged when the opt-in is
absent.

The generated prompt must preserve every placeholder exactly:

- `{audit_subject}`
- `{execution_command}`
- `{active_goal}`
- `{active_spec}`
- `{available_thread_state}`
- `{state_access_boundary}`
- `{hard_preconditions}`
- `{contract_blockers}`
- `{required_ledger}`
- `{forbidden_actions}`
- `{stop_state_vocabulary}`
- `{heartbeat_report_status_vocabulary}`
- `{completion_condition}`

## Host-State Boundary

The generated prompt may ask the auditor to read the latest execution or thread
state only when the host exposes that capability. If the host cannot provide
state, the auditor must report `HEARTBEAT_BLOCKED_CONTEXT` and request the
smallest missing visible state.

The heartbeat must not infer unavailable state, claim to have inspected a
thread it cannot access, or turn a missing host capability into loop evidence.

## Status Vocabulary

Heartbeat report statuses are:

- `HEARTBEAT_OK`
- `HEARTBEAT_RISK`
- `HEARTBEAT_BLOCKED_CONTEXT`
- `HEARTBEAT_COMPLETE`
- `HEARTBEAT_PAUSE_RECOMMENDED`

These statuses are separate from Goal Maestro stop states. Goal Maestro stop states remain authoritative. The heartbeat may recommend a configured Goal Maestro stop state, but it must never mutate, claim, or replace the authoritative loop state.

## Required Auditor Behavior

The generated prompt must instruct the auditor to:

1. inspect available latest execution or thread state before commenting;
2. report `HEARTBEAT_BLOCKED_CONTEXT` when state access is unavailable;
3. verify the configured command, active goal, active SPEC, hard preconditions,
   required ledger, contract blockers, and forbidden actions;
4. check any configured no-runtime-before-hardening constraint;
5. look for regressions against configured blockers;
6. if green, answer in at most five non-empty lines: heartbeat status, current
   risk, and next recommended checkpoint;
7. if risky, cite the risk, violated contract, minimum corrective action, and
   most specific recommended Goal Maestro stop state;
8. if complete, recommend pausing or deleting the external heartbeat and
   summarize residual risk;
9. avoid edits, staging, repository commits, branch or tag changes, remote Git
   writes, remote calls, host job management, external sharing, and execution
   redirection.

## Universal Scope

Keep the prompt generic. It must work for any active Goal Maestro loop whose
caller fills the placeholders. Do not bind the contract to a single feature,
project name, report type, host reminder, or sidecar artifact.

Use neutral placeholders such as `target-project` and `canary-project` when a
scenario needs a project label.

## Stop If Missing

Stop with:

- `NEEDS_OPT_IN_CONTRACT` when activation can happen without the exact opt-in;
- `NEEDS_THREAD_STATE_CONTEXT` when unavailable host state cannot be represented
  honestly;
- `NEEDS_GOAL_MAESTRO_INTEGRATION` when normal prompts or stop states would
  change without opt-in;
- `NEEDS_UNIVERSAL_GATE` when the focused oracle cannot falsify project-bound
  drift or forbidden authority;
- `SAFETY_BLOCKED` when the design introduces mutation authority, remote action,
  hidden external reporting, host job creation, sharing, or an execution path.

## Done

This reference is satisfied when exact opt-in emits the standalone heartbeat
prompt, absent opt-in emits no heartbeat content, the host-state boundary is
honest, the auditor authority is read-only, and Goal Maestro stop states remain
authoritative to the parent loop.
