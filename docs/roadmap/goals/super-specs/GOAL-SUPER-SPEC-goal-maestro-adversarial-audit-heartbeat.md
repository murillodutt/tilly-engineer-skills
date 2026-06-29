---
tds_id: roadmap.goal_super_spec.goal_maestro_adversarial_audit_heartbeat
tds_class: roadmap
status: active
consumer: maintainers, Goal Maestro authors, adapter authors, oracle authors, Cursor rule reviewers, and execution agents
source_of_truth: true
evidence_level: L2
tver: 0.1.0
---

# GOAL-SUPER-SPEC: Goal Maestro Adversarial Audit Heartbeat Prompt

Status: active pre-implementation project SPEC.

Purpose: add an optional universal `Adversarial Audit Heartbeat Prompt`
capability to `tes-goal-maestro`. The capability emits a copy-ready mentor and
auditor prompt for an active Goal Maestro execution loop. It observes only
available execution state, reports drift and risk, and never executes, edits,
schedules, syncs, shares, or takes ownership of the loop.

## Anchor And Origin

```text
anchor_class=owner-directed-product-project
anchor_path=docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-goal-maestro-adversarial-audit-heartbeat.md
anchor_hash=captured by git hash-object after SPEC-000 materialization
anchor_origin=materialized-from-owner-direction
anchor_source=current owner direction, 2026-06-29
```

SPEC-000 is the contract-materialization gate. Runtime, template, adapter, and
oracle behavior may begin only after this contract is committed and its hash is
available to later SPECs.

## Platform Classification

This work is `Platform` from the first line because it touches Goal Maestro,
adapter materialization, installed target surfaces, cross-host harness behavior,
public command semantics, and local package readiness.

Protected baseline:

- Goal Maestro invocation remains explicit.
- Existing `/tes-goal-maestro` activation semantics remain unchanged.
- Existing execution-loop stop states remain authoritative.
- Adapter source remains under `src/adapters/**`.
- Generated or materialized target surfaces are evidence, not hand-edited
  source.
- No remote, release, publication, marketplace, cloud, or automation action is
  authorized by this project.

## Central Rule

```text
The heartbeat is an auditor prompt generator, not a scheduler, executor,
dashboard, telemetry system, automation manager, sharing path, or second Goal
Maestro loop.
```

## Capability Contract

The capability emits a copy-ready English prompt. The emitted prompt may ask a
human or host-level auditor to inspect the latest visible execution state and
report risk. It may recommend a Goal Maestro stop state from the configured
vocabulary, but it must never mutate, claim, or replace the loop's authoritative
state.

The emitted prompt is read-only. It must forbid editing files, staging,
committing, pushing, tagging, publishing, creating branches, scheduling work,
calling remotes, sending data, opening share lanes, managing automations, or
redirecting the execution loop.

## Activation Contract

Activation is closed and opt-in only. The feature activates only when one of the
following is present in the active request, active structured control block, or
active source artifact:

- explicit Goal Maestro option: `--audit-heartbeat-prompt`;
- explicit structured field: `audit_heartbeat=true`;
- explicit Super SPEC field: `adversarial_audit_heartbeat: requested`;
- direct user request: "generate/create an adversarial audit heartbeat prompt".

Forbidden activation:

- broad words such as "heartbeat", "monitor", "audit", "acompanhe",
  "mentoria", "watch this", or "keep an eye on it" are not sufficient;
- documentation examples, historical ledgers, or inactive artifacts do not
  activate the feature by containing the opt-in text;
- no new `/tes-*` command is introduced;
- existing `/tes-goal-maestro` activation semantics do not change;
- ordinary Goal Maestro prompts remain unchanged when exact opt-in is absent.

If an implementation cannot enforce this closed grammar, stop with
`NEEDS_OPT_IN_CONTRACT`.

## Host-State Boundary

The generated heartbeat prompt may instruct the auditor to read the latest
thread or execution state only when the host exposes that capability.

If the host cannot read thread state, the heartbeat must report
`HEARTBEAT_BLOCKED_CONTEXT` and request the smallest missing visible state. It
must not pretend that it observed an unavailable thread.

The prompt must preserve this boundary through explicit placeholders:

- `{available_thread_state}`
- `{state_access_boundary}`

If this cannot be represented honestly, stop with `NEEDS_THREAD_STATE_CONTEXT`.

## Heartbeat Report Status Vocabulary

The heartbeat report status vocabulary is separate from Goal Maestro execution
stop states:

- `HEARTBEAT_OK`
- `HEARTBEAT_RISK`
- `HEARTBEAT_BLOCKED_CONTEXT`
- `HEARTBEAT_COMPLETE`
- `HEARTBEAT_PAUSE_RECOMMENDED`

Goal Maestro stop states remain authoritative to the execution loop. The
heartbeat may recommend a configured stop state but must not write it, claim it,
or replace the parent runner's decision.

## Universal Template Placeholder Contract

The template must preserve every placeholder below exactly:

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

No placeholder may bind the feature to one project, one prior report, one
sharing lane, one host automation, or one Goal Maestro sidecar.

## Prompt Behavior Contract

The emitted prompt must instruct the auditor to:

1. read available latest execution or thread state before commenting;
2. report `HEARTBEAT_BLOCKED_CONTEXT` when state access is unavailable;
3. verify configured command, active goal, active SPEC, hard preconditions,
   ledger, contract blockers, and forbidden actions;
4. check no-runtime-before-hardening when configured;
5. look for regressions against configured blockers;
6. if green, respond in at most five lines: status, current risk, next
   recommended checkpoint;
7. if risky, cite the risk, violated contract, minimum corrective action, and
   most specific recommended stop state;
8. if complete, recommend pausing or deleting the external heartbeat and
   summarize residual risk;
9. never edit, stage, commit, push, call remotes, schedule automation, manage
   automations, or redirect execution.

## Adapter Topology

Root skill surfaces route only. Owned behavior lives in
`references/adversarial-audit-heartbeat.md`. Emitted shape lives in
`templates/adversarial-audit-heartbeat.template.md`.

Codex source:

- `src/adapters/codex/skills/tes-goal-maestro/SKILL.md`
- `src/adapters/codex/skills/tes-goal-maestro/references/adversarial-audit-heartbeat.md`
- `src/adapters/codex/skills/tes-goal-maestro/templates/adversarial-audit-heartbeat.template.md`

Claude Code source:

- `src/adapters/claude/skills/tes-goal-maestro/SKILL.md`
- `src/adapters/claude/skills/tes-goal-maestro/references/adversarial-audit-heartbeat.md`
- `src/adapters/claude/skills/tes-goal-maestro/templates/adversarial-audit-heartbeat.template.md`

Cursor source:

- `src/adapters/cursor/rules/tes-runtime-capabilities.mdc`

Cursor receives a lazy runtime capability summary only. Cursor parity is
structural and materialization coverage, not a fake skill package.

## Forbidden Complexity

Do not add:

- scheduler abstraction;
- automation manager;
- telemetry, tracking, analytics, hidden network behavior, CDN, or reporting
  subsystem;
- dashboard;
- new command registry entry;
- host-specific executor;
- implicit sharing path;
- package logic tied to one prior Goal Maestro feature;
- changes to Goal Maestro stop-state authority.

## Shared Contracts

```text
contract_name: goal-maestro-audit-heartbeat-activation
declared_in: this Super SPEC
frozen_surface: exact opt-in grammar and forbidden broad activation
extension_points: none
extenders: SKILL routing, prompt reference, prompt template, focused oracle
optionality_rule: absent opt-in means absent heartbeat prompt
declaring_oracles: adversarial-audit-heartbeat-contract.mjs
extension_oracles: validate-walls.mjs, command_trigger_oracle.py when trigger text changes
```

```text
contract_name: goal-maestro-audit-heartbeat-authority
declared_in: this Super SPEC
frozen_surface: read-only auditor prompt generator, no executor authority
extension_points: template placeholders only
extenders: Codex reference, Claude reference, Cursor lazy rule
optionality_rule: recommendations only, never authoritative stop-state mutation
declaring_oracles: adversarial-audit-heartbeat-contract.mjs
extension_oracles: materialize_adapter.py all --check, adapter_parity_readiness.py
```

## Execution Isolation Gate

Before every material SPEC, inspect Git state and overlapping Goal Maestro work.
If another active execution is modifying or certifying the same files, or the
worktree contains unclassified changes in overlapping files, stop with
`NEEDS_EXECUTION_ISOLATION`.

Prior commits, prior manual heartbeat use, external host heartbeat reminders,
and prior reports are baseline-only comparison evidence unless the owner
explicitly accepts them as current execution credit.

## SPEC Queue

The execution queue is fixed:

1. `SPEC-000 Contract Hardening And Baseline Protection`
2. `SPEC-001 Add Universal Heartbeat Reference And Template`
3. `SPEC-002 Integrate Optional Goal Maestro Routing`
4. `SPEC-003 Preserve Cross-Harness Adapter Behavior`
5. `SPEC-004 Add Universal Heartbeat Oracle`
6. `SPEC-005 Documentation And Contract History`
7. `SPEC-006 Source, Materialization, And Installed Canary Readiness`

Each material SPEC requires a non-empty local commit, focused oracle evidence,
reviewer diff check, `git show --stat --oneline <commit>`, post-commit status,
and sync status. Remote sync is not authorized.

## Acceptance Criteria

- SPEC-000 closes every activation, state-boundary, auditor/executor,
  adapter-placement, and canary-readiness ambiguity.
- No runtime/template/adapter behavior lands before SPEC-000 is committed.
- The prompt is generated only by exact opt-in grammar.
- The prompt is read-only and universal.
- The prompt reports unavailable host state honestly.
- Heartbeat report statuses remain separate from Goal Maestro stop states.
- Codex and Claude carry native source reference and template surfaces.
- Cursor carries lazy capability coverage without fake skill packaging.
- The focused oracle fails on no-opt-in, mutation authority, product-specific
  drift, missing state review, missing host boundary, missing compact green
  response, missing risk report, missing completion pause/delete guidance,
  mixed auditor/executor authority, absent Cursor coverage, and stop-state
  pollution.
- Materialized/installed-like surfaces prove prompt availability without
  scheduling a real heartbeat.

## Documentation Contract

The smallest governed documentation surface for this feature is this Super SPEC
plus `tes-goal-maestro/docs/CONTRACT-HISTORY.md` in Codex and Claude source.

Those surfaces must preserve:

- purpose: an optional copy-ready mentor/auditor prompt for active Goal Maestro
  execution loops;
- authority: read-only prompt generation, never execution, repository mutation,
  host job management, network behavior, sharing, or stop-state ownership;
- activation: exact opt-in grammar only, with broad wording and inactive
  examples rejected;
- shape: the universal placeholder contract and heartbeat report status
  vocabulary;
- context boundary: unavailable host/thread state reports
  `HEARTBEAT_BLOCKED_CONTEXT`;
- adapter placement: Codex/Claude references and templates, with Cursor lazy
  capability coverage only;
- oracle: `adversarial-audit-heartbeat-contract.mjs` and GM11 in
  `validate-walls.mjs` guard opt-in, read-only authority, universal wording,
  host-state honesty, Cursor coverage, and stop-state separation;
- canary handoff: the later combined feedback-system plus heartbeat canary is
  separate owner-authorized work after both systems are locally certified.

## Negative Grep

Semantic negative grep must forbid executable behavior, not policy vocabulary.
Allowed vocabulary includes heartbeat status names, stop-state names used as
recommendations, and "pause/delete heartbeat" guidance after completion.

Forbidden behavior includes dashboards, telemetry, tracking, hidden network
behavior, implicit sharing, automation scheduling or management, file mutation,
Git mutation, remote sync, publication, release, and project-specific prompt
binding.

## Stop States

- `PASS_LOCAL_NO_REMOTE_RELEASE`: all declared SPECs passed locally, material
  commits exist, opt-in/read-only contract is enforced, materialized
  installed-like prompt availability is proven, Cursor lazy coverage exists, no
  real automation or remote action occurred, and final worktree is clean or only
  intentionally ahead locally.
- `NEEDS_EXECUTION_ISOLATION`: overlapping active Goal Maestro execution or
  unclassified dirty worktree touches the same surfaces.
- `NEEDS_AUDIT_HEARTBEAT_CONTRACT`: SPEC-000 cannot close opt-in,
  state-boundary, auditor/executor, adapter placement, or canary-readiness
  contract.
- `NEEDS_OPT_IN_CONTRACT`: activation grammar is ambiguous or broad natural
  language can trigger the feature.
- `NEEDS_THREAD_STATE_CONTEXT`: host-state boundary cannot be represented
  honestly.
- `NEEDS_UNIVERSAL_GATE`: focused oracle cannot falsify product-specific drift
  or forbidden authority.
- `NEEDS_GOAL_MAESTRO_INTEGRATION`: optional prompt integration weakens normal
  Goal Maestro prompts or stop states.
- `NEEDS_ADAPTER_PARITY`: Codex, Claude, or Cursor materialization/native
  placement is missing.
- `NEEDS_ORACLE`: focused heartbeat oracle or wall integration is missing or a
  facade.
- `NEEDS_INSTALLED_CANARY`: materialized/installed-like prompt availability is
  not proven.
- `NEEDS_COMBINED_CANARY_AUTHORIZATION`: only the later combined
  feedback-system plus heartbeat stress canary remains and needs separate owner
  authorization.
- `SAFETY_BLOCKED`: any mutation, remote, telemetry, hidden network,
  automation scheduling, sharing, or dashboard path is introduced.

## Release Identity Decision

This project changes delivered adapter behavior. A patch-version and public
bundle decision is required before any release claim. The current execution is
local-only unless the owner separately authorizes version bump, bundle refresh,
tag, push, publish, marketplace, or remote release actions.

## Combined Canary Boundary

The later combined feedback-system plus adversarial heartbeat canary is separate
work. Do not run or claim it here unless both systems are already locally sealed
and the owner explicitly starts that canary.

## Done Means

The feature is complete locally when Goal Maestro can emit the universal
adversarial audit heartbeat prompt from exact opt-in grammar across Codex and
Claude source/materialized surfaces, Cursor has lazy capability coverage, the
focused oracle and wall suite protect the contract, installed-like canary
evidence proves prompt availability and read-only behavior, and no real
automation, sharing, remote, release, or dashboard path exists.
