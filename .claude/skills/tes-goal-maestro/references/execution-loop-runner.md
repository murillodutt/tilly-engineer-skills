# Execution Loop Runner

Use this reference only when `tes-goal-maestro` was explicitly invoked with `--execute-loop` after a mature input artifact can produce a `READY_GOAL_PROMPT`.

## Core Rule

```text
The parent runner owns the loop. Workers execute one ACTIVE_SPEC.
```

The execution loop is not default Goal Maestro behavior. It is an opt-in execution layer that runs after prompt materialization, uses subagents for bounded execution, and lets the parent validate evidence before the next loop.

## Trigger Interaction

If `--execute-loop` appears together with `next_prompt_handoff=true` or `--next-prompt-handoff`, the execution loop takes precedence for internal continuation. The parent runner may generate and execute the next active-SPEC prompt only after parent validation of the current SPEC. The ordinary Next Prompt Handoff rule still applies after the loop stops or completes, and workers remain forbidden from authoritative next-prompt generation or later SPEC execution.

`--execute-loop` authorizes the parent to orchestrate the loop, not to replace worker execution when worker creation is unavailable. Parent-side worker fallback requires the exact `--execute-loop-parent-fallback` flag in the current user request.

## Lifecycle

Use these states:

```text
ready_goal_prompt -> execution_cost_drafted -> pre_edit_gate_passed ->
active_spec_opened -> active_spec_committed -> next_prompt_ready ->
executive_stop_audit -> execution_loop_complete
```

Stop or branch with:

- `NEEDS_EXECUTION_LOOP_DRAFT`
- `NEEDS_ANCHOR_ARTIFACT`
- `NEEDS_TREE_ADVERSARY`
- `NEEDS_INTEGRATION_ORACLE`
- `AXIS_UNPROVEN`
- `VISUAL_CERT_BLOCKED`
- `SPEC_BLOCKED`
- `SPEC_CONTRACT_UNSTABLE`
- `NEEDS_STRUCTURAL_METHOD`
- `NEEDS_MORE_LOOPS`
- `NEEDS_QUORUM_AUDIT`
- `NEEDS_OWNER_DECISION`
- `SAFETY_BLOCKED`
- `EXECUTION_LOOP_COMPLETE`
- `EXECUTION_LOOP_COMPLETE_WITH_AUDIT_REPAIRS`

## Reference Baseline Credit Gate

Reference implementations, prior manual builds, browser smoke results, screenshots, run records and post-facto audits may inform the `Execution Cost Draft`, expected oracles, risk, comparison targets and final review. They are baseline-only comparison evidence.

They never satisfy `--execute-loop` execution credit. The parent must run a strict sequential replay: open each declared SPEC as `ACTIVE_SPEC`, send a fresh worker the full prompt plus envelope, validate evidence produced after that SPEC opened, and commit or accept no-commit rationale before the next SPEC opens.

If the target already contains a complete reference implementation, classify it in the baseline before the first worker. Continue only when the loop can still produce additive, non-empty per-SPEC evidence after loop start. If the existing implementation makes fresh per-SPEC evidence impossible without rewriting history or pretending old commits are new execution, stop with `NEEDS_OWNER_DECISION`.

## Self-Construction: Derive Anchor From Defect

The Anchor Artifact Gate forbids a Super SPEC generated in the SAME run from authorizing itself (`ambition-and-anchor.md:17`). It does NOT forbid the harness from MATERIALIZING an anchor in one session that a LATER session cites — the `anchor_origin` enum explicitly includes `previous-session` (`ambition-and-anchor.md:13`). This is the legitimate two-session bridge the harness uses to originate its own next execution from an observed defect.

When a canary, field report, or audit re-mutation exposes a defect of class (a facade that survived, a missing oracle, a drift), the harness may run a `derive-anchor-from-defect` SPEC whose ONLY material product is a committed `GOAL-SUPER-SPEC-<defect>.md`. That artifact:

1. names the observed defect, the oracle that SHOULD have caught it, and the named property that was violated;
2. carries a synthesized `remutation-plan.json` for the repair (produced by `scripts/lib/synth.mjs` per `tree-adversary.md` § Oracle Synthesis On Repair), so the repair is born with a falsifiable oracle BEFORE its code exists;
3. is committed with a recomputable provenance hash.

A subsequent `--execute-loop` invocation cites that artifact as `anchor_origin=previous-session`. At the Pre-Edit Gate, `scripts/anchor-rehash.mjs` proves byte-identity (recomputed `git hash-object` matches the declared hash) and benchmark isolation (the path is not a foreign `benchmark-*/`). That is the full executable guarantee `anchor-rehash.mjs` provides — it does NOT read `anchor_origin`, so it cannot, on its own, reject a same-session self-citation.

The same-session firewall is therefore enforced two ways, not by `anchor-rehash.mjs` alone:

- a doc-coherence check that `ambition-and-anchor.md:17` still forbids same-session self-authorization (the rule must remain present and uninverted);
- routing any anchor whose `anchor_origin` would be same-session to `NEEDS_OWNER_DECISION`: the human decides IF the derived repair should exist. The human leaves the floor (materializing SPECs) and stays only at this ceiling gate.

Do not claim `anchor-rehash.mjs` executably rejects a same-session citation; it proves provenance and isolation only.

## Pre-Edit Gate

Before any worker spawn, parent fallback edit, material implementation edit, or execution-unit commit, the parent must emit a Pre-Edit Gate from material sources. This gate is the mechanical permission to edit.

The gate block is mandatory:

```text
EXECUTE_LOOP_REQUESTED=yes
READY_GOAL_PROMPT=present
ANCHOR_CLASS=<class>
ANCHOR_PATH=<path>
ANCHOR_HASH=<hash>
TREE_ADVERSARY_STATUS=<ADVERSARY_CLEARED|OBJECTIONS_REPAIRED|not_required>
DECLARED_UNITS=<exact ordered unit ids from the materialization tree>
FIRST_UNEXECUTED_UNIT=<id>
ACTIVE_SPEC=<id>
BASELINE_ONLY_COMMITS=<hashes or none>
LEDGER=<GOAL-EXECUTION-LOOP-LEDGER-...md>
MAY_EDIT=<yes|no>
```

`MAY_EDIT=yes` is allowed only when:

1. `EXECUTE_LOOP_REQUESTED=yes`;
2. `READY_GOAL_PROMPT=present`;
3. `ANCHOR_PATH` names a persisted non-self artifact and `ANCHOR_HASH` is **recomputed** at the gate — `git hash-object <ANCHOR_PATH>` is run and compared byte-for-byte to the declared `ANCHOR_HASH`; a declared hash that is not re-derived is self-attested provenance, the same hole as a facade oracle. Divergence, a missing path, or `ANCHOR_PATH` resolving to a `benchmark-*/` distinct from the current run → stop with `NEEDS_ANCHOR_ARTIFACT`; the loop does not start (drive with `scripts/anchor-rehash.mjs`);
4. `TREE_ADVERSARY_STATUS` is `ADVERSARY_CLEARED`, `OBJECTIONS_REPAIRED`, or `not_required`;
5. `DECLARED_UNITS` preserves the source-declared queue exactly;
6. `FIRST_UNEXECUTED_UNIT` is the first declared unit without current-loop post-open evidence and accepted commit/no-commit rationale;
7. `ACTIVE_SPEC` equals `FIRST_UNEXECUTED_UNIT`;
8. `BASELINE_ONLY_COMMITS` lists prior commits used only as comparison evidence, or `none`;
9. `LEDGER` names the persistent execution-loop ledger.

If the block is missing, `MAY_EDIT=no`, or `FIRST_UNEXECUTED_UNIT` differs from `ACTIVE_SPEC`, stop with `NEEDS_EXECUTION_UNIT_FIDELITY` before any edit or worker spawn. Do not repair the mismatch by reordering, skipping, renaming or counting old commits.

If the anchor fields are missing or self-referential, stop with `NEEDS_ANCHOR_ARTIFACT`. If the adversary status is missing or uncleared, stop with `NEEDS_TREE_ADVERSARY`.

Materializing, expanding or repairing a Super SPEC before the loop is preparatory contract work. It does not consume the first declared execution unit, advance `FIRST_UNEXECUTED_UNIT`, or count as material execution unless the source artifact explicitly declares that same unit as the active execution unit.

## Execution Cost Draft

Before spawning any worker, produce an `Execution Cost Draft` from material sources only: the SPEC, Super SPEC, accepted tree, generated `/goal`, existing commits, and relevant oracles. Do not rely on memory.

Inspect the worktree before drafting. If `git status --short --branch --untracked-files=all` shows existing changes, classify them as owner baseline, current-loop material, unrelated user work, or blocker. Do not open the first worker until the baseline is clean or explicitly classified in the draft; stop with `NEEDS_OWNER_DECISION` when ownership cannot be proven.

The draft must state source artifacts, declared SPEC order, dependency edges, risk, expected oracles, expected commits, likely repair points, final stop, baseline worktree classification, canonical SPEC repair target, audit budget, structural method cost, runtime/visual/integration plans, shared contracts, source-derived handoff plan, Tree Adversary result and the persistent ledger path. Use the owning references for detail: `ambition-and-anchor.md`, `structural-method.md`, `runtime-certification.md`, `execution-context-handoff.md` and `tree-adversary.md`.

If the draft cannot be produced from material sources, stop with `NEEDS_EXECUTION_LOOP_DRAFT`.

## Pre-SPEC Reflection

Before every worker spawn, the parent must produce a short pre-SPEC reflection: active SPEC id, allowed/forbidden files, focused oracles, negative checks, Engineering Method Profile, structural packet, runtime/visual/integration packet, source-derived handoff packet, local risk, Pre-Edit Gate, loop-state block and the hard statement that the worker may execute only the active SPEC.

This reflection is mandatory even when the previous loop generated a next prompt.

The loop-state block is mandatory before every attempt and after every failed attempt:

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
first_unexecuted_unit=<id>
bug_vs_architecture=<behavior_bug|structural_collapse|mixed|unknown|not_applicable>
browser_metrics_required=<yes|no|not_applicable>
visual_spatial_oracle_required=<yes|no|not_applicable>
browser_attempt=<tool_invoked|not_attempted|not_applicable>
visual_evidence=<paths|degraded_with_proof|none|not_applicable>
runtime_smoke_oracle=<pass|fail|missing|not_applicable>
adversary_objection=<none|open|repaired|not_applicable>
shared_contract_extended=<yes|no|not_applicable>
extension_point_proven=<yes|no|not_applicable>
contract_handoff_artifact=<path|ledger-section|prompt-block|not_applicable>
api_lint_status=<PASS|FAIL|not_applicable>
```

## Worker Packet

Each worker receives the full generated prompt, not a compacted summary. The parent must add a hard envelope above it:

```text
ACTIVE_SPEC=SPEC-00N
Execute only ACTIVE_SPEC.
Do not execute any later SPEC.
Do not generate the final next prompt; you may propose next-prompt material.
Do not push or perform remote sync.
Apply the active Engineering Method Profile when present.
STRUCTURAL_METHOD=<profile-id or not_applicable>
FILE_TOPOLOGY_BUDGET=<budget or not_applicable>
ALLOWED_NEW_MODULES=<paths, internal sections or none>
STRUCTURAL_DEBT_BUDGET=<none, accepted debt or owner-decision needed>
STRUCTURAL_SOURCE_PROBES=<commands or source checks>
BROWSER_METRICS_CONTRACT=<artifact path and required fields or not_applicable>
VISUAL_SPATIAL_ORACLE=<screenshot/pixel/legibility/bounding-box requirement or not_applicable>
RUNTIME_SMOKE_ORACLE=<command or not_applicable>
CONTRACT_HANDOFF_ARTIFACT=<source-derived symbols/oracles or not_applicable>
API_LINT_STATUS=<PASS|not_applicable>
RESEARCH_BUDGET=<official source + local cross-check or not_applicable>
Return the evidence block required by the prompt.
```

Workers may repair the active SPEC when execution proves the active SPEC is incorrect, incomplete, or ambiguous. They may not repair other SPECs.

## Attempts And SPEC Repair

Each SPEC version gets three local attempts.

If the active SPEC itself must change:

1. mark the change as `SPEC_REPAIR_BY_LLM`;
2. state that the repair was proposed and executed by the LLM, not a human;
3. record cause, evidence, diff, impact, and oracle;
4. update the canonical material SPEC artifact, such as the source SPEC or the generated `GOAL-SUPER-SPEC-<slug-or-timestamp>.md` artifact;
5. commit the repair separately before implementation;
6. rerun pre-SPEC reflection with a new `spec_version`;
7. reset the attempt counter because the contract changed.

If the active SPEC exists only in chat, materialize or expand the required Super SPEC artifact before the repair commit. If no canonical repair target can be created from material sources, stop with `NEEDS_TREE_REPAIR`.

Allow at most two SPEC repairs per active SPEC. If more repair is needed, run the escalation ladder before stopping with `SPEC_CONTRACT_UNSTABLE`.

## Failed Attempt Recovery

After any failed worker attempt, inspect `git status --short --branch --untracked-files=all` and the diff before opening another attempt. The parent must emit a `Failed Attempt Recovery` block:

```text
ACTIVE_SPEC=SPEC-00N
failed_attempt=<attempt number>
residue_files=<paths or none>
residue_origin=<current_attempt|preexisting_baseline|mixed|unknown>
decision=<commit_valid_material|spec_repair|revert_current_attempt|stop>
bug_vs_architecture=<behavior_bug|structural_collapse|mixed|unknown|not_applicable>
structural_decision=<bug_repair|structural_repair|spec_repair|escalation|stop|not_applicable>
oracle=<command or review proving the decision>
```

The next attempt may start only when residue is resolved. Valid material may be committed only if it satisfies the active SPEC evidence contract. A SPEC defect must become `SPEC_REPAIR_BY_LLM` before implementation continues. Reverting is allowed only for changes proven to belong wholly to the current failed attempt; never revert pre-existing baseline or user work. If residue is mixed or ownership is unknown, stop with `NEEDS_OWNER_DECISION`.

## Escalation Ladder

After three failed attempts for a SPEC version, or after two repairs still leave the active SPEC unstable, run:

1. predictive code analysis against the material code and SPEC evidence, explicitly deciding whether the unresolved failure is a behavior bug, architecture collapse, mixed failure or unknown;
2. MCP or official knowledge sources such as Context7 for library/framework/API questions;
3. sanitized cloud query only after explicit owner approval of the exact sanitized payload, using minimal anonymized error, public API facts, and non-secret example context;
4. stop if unresolved.

Never send secrets, private paths, proprietary diffs, project names, storage backends, credentials, sensitive architecture structure, or raw internal payloads to cloud tools.

Before any cloud query, produce a `Cloud Query Redaction Block` with:

1. sanitized payload to be sent;
2. redacted terms and categories;
3. confirmation that no secrets, private paths, project names, storage backends, credentials, sensitive architecture structure or raw internal payloads remain;
4. owner approval reference from the current execution context.

If the owner does not approve the exact sanitized payload, stop with `NEEDS_OWNER_DECISION`; if sanitization cannot remove sensitive material, stop with `SAFETY_BLOCKED`.

## Parent Validation

The parent advances only after validating the active SPEC id, Pre-Edit Gate, allowed file matrix, focused oracles, negative checks, local commit or accepted no-commit rationale, `git show --stat`, post-commit status, sync status, fresh post-open evidence, no later-SPEC execution, refreshed local state before next prompt, structural method packet, runtime certification packet, integration runtime-smoke, shared-contract extension packet, source-derived handoff packet and Tree Adversary status. Route failures to the specific stop state named by the owning reference, not to a broad green closeout.

Validating "focused oracles" means running them. Any wall harness a reference names for the active gate (`scripts/<name>.mjs`, per `references/materialization-tree.md` § Wall harness invocation) must be executed with its literal exit code captured as evidence — a paraphrased or assumed result is not validation, and a harness mentioned but not run leaves the gate `facade`.

When `RUNTIME_TARGET=browser`, the negative checks must include a runtime-import grep over the `allowed_files` (`scripts/runtime-import-grep.mjs`): a non-stubbed `node:`, `child_process`, bare `fs`, `path`, or `os` import in browser-bound source → stop with `NEEDS_TREE_REPAIR` before the commit. This catches the node-in-browser class inside the active-SPEC span, where typecheck and build are blind to it.

Remote push is forbidden unless separately authorized by the user.

## Certification Repair Rule

The final certification SPEC may perform bounded code repairs only when the repair is discovered by certification evidence and remains inside the active SPEC contract.

Allowed certification repairs must:

1. be recorded as `audit_repair`, not as skipped or reordered implementation;
2. name the failing oracle and the exact repair scope;
3. change only files allowed by the active certification or audit unit;
4. create a local non-empty repair commit unless the repair is documentation or evidence-only with an accepted no-commit rationale;
5. rerun the failing oracle plus the final closeout oracle;
6. keep the original SPEC sequence intact.

If the repair requires new product scope, changes a prior SPEC contract, or cannot be proven from certification evidence, stop with `NEEDS_MORE_LOOPS`, `SPEC_CONTRACT_UNSTABLE` or `NEEDS_OWNER_DECISION` instead of folding it into the final certification SPEC.

## Next Prompt Authority

The worker may propose next-prompt material, but the parent generates the next prompt. The parent must use worker evidence, material commits, and the original tree to decide whether the next SPEC may open.

If validation fails, do not generate the next prompt. Continue repair within the active SPEC or stop with the matching status.

## Subagent Lifecycle

Use a new worker subagent per active SPEC. After the parent captures and validates evidence, close the worker. If subagent capacity is exhausted, the parent may close completed, degraded, or no-longer-needed subagents after capturing evidence.

If no worker can be created after capacity cleanup, do not silently collapse the loop. The parent may execute under the same `ACTIVE_SPEC` envelope only when the current user request explicitly authorized parent-side loop execution with the exact `--execute-loop-parent-fallback` flag; otherwise stop with `NEEDS_OWNER_DECISION`.

Do not keep subagents open as memory. Git commits and parent-held evidence are the state.

## Loop State

Default loop state lives in the parent context plus Git, but a persistent ledger is mandatory for every `--execute-loop`. The loop-state block is still mandatory in the parent evidence for every attempt.

Create a persistent Markdown ledger named `GOAL-EXECUTION-LOOP-LEDGER-<slug-or-timestamp>.md` before the first `ACTIVE_SPEC` opens. `--execute-loop-ledger` may request a specific ledger path or stricter retention, but it is not required to make the ledger mandatory.

Shard the ledger before it becomes ingestion debt. The ledger must carry only SPEC id, spec version, attempt, repair count, audit cycle, failed-attempt recovery decision, commit, oracle status, structural decision fields, stop state, browser/visual oracle fields, runtime-smoke fields, shared-contract extension fields, source-handoff fields and next allowed action.

### Ledger Schema

Each ledger entry must use one active SPEC or audit unit and include these exact field labels:

```text
spec_id:
spec_version:
attempt:
repair_count:
audit_repair_cycle:
first_unexecuted_unit:
failed_attempt_recovery_decision:
commit:
oracle_status:
structural_method_id:
topology_decision:
topology_decision_artifact:
structural_debt:
next_structural_constraint:
topology_probe_result:
browser_metrics_contract:
visual_spatial_oracle:
browser_attempt:
visual_evidence:
runtime_smoke_oracle:
adversary_objection:
shared_contract_extended:
extension_point_proven:
contract_handoff_artifact:
api_lint_status:
auditor_distinct_from_operator:
auditor_rewrote_no_oracle:
audit_remutation:
distinct_refuters:
stop_state:
next_allowed_action:
```

The three `audit_*`/`auditor_*` fields are written only by the `Executive Stop Audit` reviewer, never by the operator that ran the oracles; they stay `not_applicable` on operator-written SPEC entries and carry `yes`/`yes`/`ran` only on the audit unit. A green oracle is not execution credit until `audit_remutation=ran` and the re-mutation made it fail.

The ledger must not store full prompt bodies, raw diffs, secrets, credentials, private paths, chat transcripts or project-specific names.

Use `not_applicable` for structural decision fields when the active SPEC has no code, UI, runtime-script or generated-app structure. These fields are a compact decision ledger, not a design essay. They record only the active method, topology choice, accepted debt and constraint that the next loop must preserve. Use `not_applicable` for browser and visual fields when the active SPEC has no browser, UI, game, canvas, layout or spatial-rendering risk. Use `not_applicable` for runtime-smoke fields when the active SPEC is not an integration or wiring unit. Use `not_applicable` for handoff fields only when the worker does not reuse existing APIs.

## Executive Stop Audit

When the planned stop is reached, do not close automatically. Spawn a separate reviewer for `Executive Stop Audit`. The reviewer must be distinct from any subagent that authored or ran a required-axis oracle: receiving evidence is not auditing it. A reviewer who only inspects artifacts the operator produced is the defendant judging itself, and a facade oracle survives that.

The reviewer receives the original tree, executed SPECs, commits and `git show --stat`, oracles and negative checks, repair records, final worktree status, baseline-only classification, structural evidence, runtime/visual evidence, integration smoke evidence, source-derived handoff evidence, and Tree Adversary result.

The reviewer does not stop at inspection. For every required-axis oracle, the reviewer **re-executes** it in a clean worktree and then **re-mutates** it: inject a violation into the named property the oracle claims to prove and confirm the oracle turns to exit≠0. An oracle that stays PASS under the mutation of its own named property is a facade, however green it looked. Record three binary fields, all required for `EXECUTION_LOOP_COMPLETE`:

- `AUDITOR_DISTINCT_FROM_OPERATOR=<yes|no>` — the reviewer authored and ran none of the oracles under audit;
- `AUDITOR_REWROTE_NO_ORACLE=<yes|no>` — the reviewer edited no oracle to make it pass;
- `audit_remutation=<ran|skipped>` — every required-axis oracle was re-executed and re-mutated.

Any field missing, `no`, or `skipped`, or any oracle staying PASS under re-mutation → stop with `NEEDS_INDEPENDENT_AUDIT`. Drive the re-execution and re-mutation with `scripts/audit-remutation.mjs`. The reviewer also runs `scripts/ledger-no-placeholder.mjs` over the ledger and SCORECARD; any placeholder `commit:` (`<...>`, empty, `TODO`, `TBD`, `<hash>`) → `NEEDS_EXECUTION_UNIT_FIDELITY`.

### Quorum Audit (panel mode)

The three binary fields prove that AT LEAST ONE mind distinct from the operator audited the oracle. When the audit runs `scripts/audit-remutation.mjs` in panel mode (an oracle with `refuters[]`, see SPEC-004), distinction becomes cardinal, not binary:

```text
DISTINCT_REFUTERS=<integer count of refuters with distinct {mutate,revert,decoy_mutate} bodies>
```

A required-axis oracle audited by panel earns credit only when `DISTINCT_REFUTERS >= R` for the contract's chosen `R` (default `R=2`), every refuter kept the oracle clean-PASS and FAIL-under-its-own-mutation, and `scripts/panel-diversity.mjs` confirms the refuter bodies are not clones (different lens labels with identical bodies are vacuous diversity, rejected by body). If fewer than `R` distinct refuters could be instantiated, or `panel-diversity.mjs` flags clones, stop with `NEEDS_QUORUM_AUDIT` — the exact panel-mode parallel of `NEEDS_INDEPENDENT_AUDIT`. A single refuter that leaves the oracle PASS under its own mutation vetoes the credit (`harness.mjs` FAIL-domination), regardless of how many others passed.

The reviewer does not receive the full original prompt unless the parent decides that a prompt contract dispute is the audit subject.

The reviewer recommends one of:

- `EXECUTION_LOOP_COMPLETE`
- `EXECUTION_LOOP_COMPLETE_WITH_AUDIT_REPAIRS`
- `NEEDS_MORE_LOOPS`
- `NEEDS_STRUCTURAL_METHOD`
- `NEEDS_INTEGRATION_ORACLE`
- `AXIS_UNPROVEN`
- `VISUAL_CERT_BLOCKED`
- `NEEDS_TREE_ADVERSARY`
- `NEEDS_QUORUM_AUDIT`
- `SPEC_BLOCKED`
- `SPEC_CONTRACT_UNSTABLE`
- `NEEDS_OWNER_DECISION`
- `SAFETY_BLOCKED`

The parent makes the final decision.

## Audit Repairs

If audit returns `NEEDS_MORE_LOOPS`, create formal corrective units named `SPEC-AUDIT-001`, `SPEC-AUDIT-002`, and so on. These are appended as audit repairs; do not rewrite the original materialization tree.

Audit repair units use the same loop rules: active SPEC envelope, local commit, oracles, parent validation, and final audit.

When the missing evidence is structural, name the corrective units `SPEC-AUDIT-STRUCTURE-001`, `SPEC-AUDIT-STRUCTURE-002`, and so on.

The audit must name the exact missing units and the expected stop. After one audit-repair batch, rerun Executive Stop Audit. A second `NEEDS_MORE_LOOPS` recommendation may open another batch only when it names new material evidence that was not available to the first audit. Repeated audit expansion without new material evidence stops with `NEEDS_OWNER_DECISION` or `SPEC_CONTRACT_UNSTABLE`.

## Completion

Use `EXECUTION_LOOP_COMPLETE` only when all declared SPECs passed, the Pre-Edit Gate had valid anchor fields, required Tree Adversary review was cleared or repaired, the Executive Stop Audit confirms no more loops are needed, and no declared SPEC was skipped, credited from Super SPEC materialization, or credited from baseline-only reference evidence. Coding, UI or generated-app SPECs must also have passing structural method evidence. "Passing" here means the structural source probe actually ran and exited zero: the loop-state and Ledger Schema field `topology_probe_result=<PASS|FAIL|not_applicable>` must carry `PASS` from a versioned probe in the diff, not a prose claim that the budget was respected. `topology_probe_result=FAIL` (or a `FILE_TOPOLOGY_BUDGET≠not_applicable` unit with the field missing) → stop with `NEEDS_STRUCTURAL_METHOD` before the commit, and the reviewer re-runs the probe in the `Executive Stop Audit`.

Required browser, visual or runtime axes must have PASS evidence. Required visual axes need `browser_attempt=tool_invoked`, `status=PASS`, `visual.proven=true` and at least one evidence artifact. Integration units need a passing runtime-smoke artifact. A required axis with `DEGRADED`, `BLOCKED`, `not_attempted` or missing runtime smoke cannot close as `EXECUTION_LOOP_COMPLETE`.

Use `EXECUTION_LOOP_COMPLETE_WITH_AUDIT_REPAIRS` when the loop converged only after audit-added corrective SPECs.
