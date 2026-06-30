---
name: tes-goal-maestro
description: Use when the user explicitly invokes tes-goal-maestro, /tes-goal-maestro, /tes:goal-maestro, $tes-goal-maestro, or directly asks to generate a maestral /goal prompt (gerar um /goal maestral) for incremental, auditable materialization from a mature SPEC, Super SPEC, PRD, relational project plan, or accepted execution tree.
license: MIT
---

# TES Goal Maestro

Operational contract: `tes.goal_maestro@0.5.0`.

Central rule:

```text
The root skill routes; references execute the contract; templates preserve shape.
```

Routing Realignment Mantra:

```text
Root routes. References own depth. Templates preserve emitted shape.
Load the owner before using owned behavior.
If routing and behavior diverge, repair routing first, then execute.
Do not inline owned behavior to make the root feel complete.
```

No behavior may be removed to reduce root size. Move behavior only to a named surface with a load rule and an oracle.

## Invocation Contract

Use only after explicit invocation or a direct request to generate a maestral `/goal` prompt from a mature SPEC, Super SPEC, PRD, relational project plan or accepted execution tree. Do not activate from generic planning, ordinary goal language, or early design discussion.

`tes-goal-maestro` does not execute implementation by default. It builds an execution-grade materialization tree and, when the tree passes the internal gates, emits a ready `/goal` prompt in the same response.

Goal Maestro owns prompt enrichment. The user may provide a mature ADR, PRD, Super SPEC, SPEC, relational project plan, accepted execution tree, or contextualized project objective; they are not required to pre-optimize execution prompts, metrics, lenses, oracle wording, subagent packets, thermometer fields, or heartbeat placeholders. The harness must derive the execution tree, active SPEC queue, structural method, evidence requirements, stop states, local reporting sidecars, and optional prompt sidecars from the material artifact plus explicit options.

When a Super SPEC must be produced or expanded, write it as `GOAL-SUPER-SPEC-<slug-or-timestamp>.md` and summarize the path in chat. This Super SPEC artifact is the only default file write allowed by this skill. Prompt, tree, ledger or other files require explicit save or loop authority.

Next Prompt Handoff is opt-in only. Activate it only when the user explicitly requests `next_prompt_handoff=true`, `--next-prompt-handoff`, or an equivalent direct trigger. Outside `--execute-loop`, it is chat-only, post-certification, non-executing, and must never write the next prompt to disk without an explicit save request.

Adversarial Audit Heartbeat Prompt is opt-in only. Activate it only when the active request, active structured control block, or active source artifact contains `--audit-heartbeat-prompt`, `audit_heartbeat=true`, `adversarial_audit_heartbeat: requested`, or a direct request to generate or create an adversarial audit heartbeat prompt. When activated, load `references/adversarial-audit-heartbeat.md` and `templates/adversarial-audit-heartbeat.template.md`. Without `--execute-loop`, emit only the copy-ready English heartbeat prompt. With `--execute-loop`, keep the execution loop primary and emit that heartbeat prompt as a same-response read-only sidecar in the Goal Maestro response or closeout. Do not create, request, or imply a second `/tes-goal-maestro` command. It is read-only auditor guidance, not execution, scheduling, sharing, or Goal Maestro stop-state authority.

Execution Loop is opt-in only. Activate it only when the user explicitly requests `--execute-loop`. When enabled, produce `READY_GOAL_PROMPT`, then the parent runner creates an `Execution Cost Draft`, opens a mandatory Pre-Edit Gate, creates the loop ledger, opens one `ACTIVE_SPEC` at a time, requires strict sequential replay, validates local commit evidence, and closes only after Executive Stop Audit.

Parent-side execution fallback requires the exact `--execute-loop-parent-fallback` flag. No equivalent wording is valid.

Reference implementation evidence, prior manual builds, browser smoke results, screenshots, run records and post-facto audits are baseline-only comparison evidence. They never satisfy material execution or `--execute-loop` credit. Materializing or expanding a Super SPEC is preparation for the loop, not execution credit for the first declared unit.

Structural Method Gate is active for code, UI, runtime scripts and generated app artifacts. Load `references/structural-method.md` and carry an Engineering Method Profile, `STRUCTURAL_METHOD=<profile-id>`, `bug_vs_architecture`, Failed Attempt Recovery, structural handoff and `NEEDS_STRUCTURAL_METHOD` rules through the tree, prompt, loop ledger and closeout.

Anchor, ambition, runtime certification, tree adversary and execution context handoff gates are active for `--execute-loop` and for any generated prompt whose source artifact declares runtime, visual, integration, shared-contract or quality-ceiling risk. Load their owning references before accepting the tree.

If both Next Prompt Handoff and Execution Loop are requested, `--execute-loop` owns internal next-prompt generation. Do not include ordinary handoff language that forbids parent-runner continuation between validated active SPECs.

If both Adversarial Audit Heartbeat Prompt and Execution Loop are requested, `--execute-loop` owns execution. The heartbeat prompt is generated internally as a same-response sidecar and never schedules, executes, edits, opens another loop, or changes stop-state authority.

## Mandatory Load Routing

Load only what the run needs, but do not execute from memory when a route is required:

| Need | Load |
|------|------|
| Tree schema, execution-unit fidelity, material diff, commit rhythm, final delivery | `references/materialization-tree.md` |
| Readiness score, stop states, weak-prompt rejection, closeout checks | `references/quality-gates.md` |
| Final `/goal` construction rules and hardening checklist | `references/maestral-goal-prompt.md` |
| Full literal `/goal` prompt body and evidence shape | `templates/maestral-goal-prompt.template.md` |
| Optional Adversarial Audit Heartbeat Prompt behavior and shape | `references/adversarial-audit-heartbeat.md` and `templates/adversarial-audit-heartbeat.template.md`, only after exact heartbeat prompt opt-in |
| Engineering method profile, topology budget, structural source probes and structural repair | `references/structural-method.md` |
| Role ownership, reviewer duties and reusable oracle patterns | `references/subagents-and-oracles.md` |
| Anchor artifact, quality ceiling, ambition directive and shared-contract extension rules | `references/ambition-and-anchor.md` |
| Browser/visual certification, runtime-smoke integration oracle and required-axis stop states | `references/runtime-certification.md` |
| Pre-execution adversarial review, oracle classification and adequacy objections | `references/tree-adversary.md` |
| Source-derived worker handoff, API lint, research budget and Node oracle block | `references/execution-context-handoff.md` |
| `--execute-loop`, `ACTIVE_SPEC`, loop-state block, `GOAL-EXECUTION-LOOP-LEDGER`, SPEC repair and Executive Stop Audit | `references/execution-loop-runner.md` |
| Executable wall harnesses (oracle name↔measure, audit re-mutation, runtime/topology/visual/coherence/wiring/anchor checks, ledger placeholder scan) | `scripts/*.mjs` — each is a per-SPEC oracle that must be **run** (exit≠0 is the stop), not just read; see `references/materialization-tree.md` § Wall harness invocation. `scripts/validate-walls.mjs` runs the full mutation-suite; it is routed by the project's persistent gate (any pre-commit/CI/hook/Makefile identified by the axis `regression_target`, not a hardcoded tool), proven by re-mutation per check 23, never by mention. |
| Domain wall harnesses (database, financeiro, LLM build, UX avançada) — domain-agnostic coverage | `scripts/{db-*,*-idempotency,ledger-double-entry,referential-integrity,batch-reconcile,decimal-precision,audit-trail-immutable,eval-coverage,token-budget,tool-reachability,rag-relevance,i18n-coverage,responsive-check,a11y-audit,web-vitals}.mjs`. Three closure classes: node-puro (deterministic), dep-pesada (PASS or **BLOCKED-proven**, exit 2, never fake PASS), non-deterministic (frozen gold or BLOCKED). `runChecks` exit codes: 0=PASS, 1=FAIL, 2=BLOCKED-proven. |

Before returning `READY_GOAL_PROMPT`, the loaded references must cover every behavior the generated prompt depends on.

## Maturity Gate

Before generating `/goal`, first verify the Anchor Artifact Gate from `references/ambition-and-anchor.md`: the run must cite a persisted non-self anchor artifact with class, path and hash, or stop with `NEEDS_ANCHOR_ARTIFACT`.

Then verify that the input artifact provides or clearly derives:

1. canonical artifact;
2. capability or purpose;
3. certified context and dependencies;
4. phase boundary;
5. non-objectives;
6. central rule;
7. forbidden moves;
8. acceptance criteria or oracle candidates;
9. negative-grep candidates;
10. stop states or owner-decision points;
11. commit strategy;
12. ambition directive and quality ceiling when declared by the anchor;
13. Engineering Method Profile and Method Enforcement Packet when code, runtime, UI or generated app artifacts change;
14. runtime, visual, integration, shared-contract and worker-handoff needs when those risks are in scope;
15. final delivery contract.

Use `references/quality-gates.md` for full status definitions. Root-level statuses are:

- `NEEDS_SPEC_MATURITY`
- `NEEDS_ANCHOR_ARTIFACT`
- `NEEDS_EXECUTION_UNIT_FIDELITY`
- `NEEDS_SLICE_FIDELITY`
- `NEEDS_TREE_REPAIR`
- `NEEDS_HUMAN_ORACLE`
- `NEEDS_DISCOVERABILITY`
- `LENS_THEATER`
- `NEEDS_TREE_ADVERSARY`
- `DRAFT_MATERIALIZATION_TREE`
- `NEEDS_TREE_ACCEPTANCE`
- `READY_GOAL_PROMPT`
- `SUPER_SPEC_MATERIALIZED`
- `SAVE_REQUESTED`
- `NEEDS_EXECUTION_LOOP_DRAFT`
- `NEEDS_CONTEXT`
- `NEEDS_STRUCTURAL_METHOD`
- `NEEDS_AMBITION_RECONCILIATION`
- `NEEDS_CONTRACT_EXTENSION_POINT`
- `NEEDS_INTEGRATION_ORACLE`
- `AXIS_UNPROVEN`
- `VISUAL_CERT_BLOCKED`
- `SPEC_BLOCKED`
- `SPEC_CONTRACT_UNSTABLE`
- `NEEDS_MORE_LOOPS`
- `NEEDS_OWNER_DECISION`
- `SAFETY_BLOCKED`
- `NEEDS_INDEPENDENT_AUDIT`
- `NEEDS_QUORUM_AUDIT`
- `EXECUTION_LOOP_COMPLETE`
- `EXECUTION_LOOP_COMPLETE_WITH_AUDIT_REPAIRS`

If maturity material is missing, stop with `NEEDS_SPEC_MATURITY` and list only the smallest missing set. If the artifact is mature but the tree is absent, generate and validate the tree, then continue to `READY_GOAL_PROMPT` when the tree passes.

Status specificity rule: prefer the most specific Goal Maestro stop state before generic branch states. Do not answer with `SPEC_BLOCKED` or `SAFETY_BLOCKED` when the failure is specifically missing integration proof, missing visual proof, missing source-derived worker handoff, missing anchor, missing Tree Adversary, or unrepaired tree adequacy. Use the named stop state instead.

## Workflow

1. Read the input artifact and any user-provided tree.
2. Run Anchor Artifact Gate, then Maturity Gate, and assign readiness.
3. Preserve every declared execution unit id and order; stop with `NEEDS_EXECUTION_UNIT_FIDELITY` if fidelity fails.
4. Capture any `ambition_directive`, `quality_ceiling` and shared contracts from the anchor before reducing scope.
5. Treat prior commits and closeouts as baseline-only unless the source artifact or owner explicitly grants execution credit.
6. Apply semantic negative-grep rules: block forbidden behavior, not valid blocked-state vocabulary.
7. For code, UI, runtime or generated app work, load `references/structural-method.md` before building the tree.
8. For browser, visual, runtime or integration work, load `references/runtime-certification.md` before building the tree.
9. Prefer centralized sequential writes when commit-per-unit order matters; use subagents for bounded ownership, review and oracles.
10. Load the route-specific references from `Mandatory Load Routing`.
11. Produce the fixed Materialization Tree schema.
12. Validate the tree against anchor, maturity, fidelity, continuation, ownership, oracle adequacy, runtime certification, structural method, context handoff, negative-grep, material-diff, sync-commit and stop-state gates.
13. When `--execute-loop` is requested or risk is high, run the Tree Adversary from `references/tree-adversary.md`; do not self-clear objections.
14. Write a Super SPEC artifact only when a Super SPEC must be produced or expanded; otherwise stay chat-first.
15. Load `references/maestral-goal-prompt.md` and `templates/maestral-goal-prompt.template.md` before emitting a prompt.
16. Produce `READY_GOAL_PROMPT` in the same response when gates pass.
17. If Next Prompt Handoff was explicitly requested, add only the chat-window handoff clause defined by the prompt reference.
18. If `--execute-loop` was explicitly requested, load `references/execution-loop-runner.md` and run only after `READY_GOAL_PROMPT`.

Fixed tree schema:

1. `Canonical Artifact`
2. `Certified Context`
3. `Shared Contracts`
4. `Phase Boundary`
5. `Non-Objectives`
6. `Central Rule`
7. `Forbidden Moves`
8. `Execution Units`
9. `Subagent Ownership`
10. `Per-SPEC Oracles`
11. `Negative Grep`
12. `Commit Strategy`
13. `Review Loop`
14. `Stop States`
15. `Final Delivery Contract`

Every generated `/goal` prompt must include `SPEC-000 Preflight And Baseline`, commit-per-SPEC discipline, material-diff proof, sync status, negative grep, review loop, anchor artifact fields, stop states and final delivery contract.

Every material unit must define objective, allowed files, forbidden files or actions where risky, owner, focused oracles, negative checks where relevant, semantic commit message, completion evidence and structural method requirements when applicable. Integration units must define a runtime-smoke oracle; browser or visual units must define required-axis certification evidence; code units must carry source-derived handoff evidence when reused APIs cross SPEC boundaries.

Each per-unit evidence block must require changed files, `git show --stat --oneline <commit>`, focused oracles, negative checks, structural method result, structural handoff, reviewer result, post-commit status and sync status: `LOCAL_COMMITTED`, `REMOTE_SYNCED`, `REMOTE_SYNC_NOT_REQUESTED` or `SYNC_BLOCKED`.

Default sync is local Git commit certification. Remote sync, push, tag, publication, marketplace, cloud or external execution requires explicit owner authorization for that action.

## Critical Locks

- Do not generate `/goal` from an immature input artifact.
- Do not generate `READY_GOAL_PROMPT` without a persisted non-self anchor artifact when the Anchor Artifact Gate applies.
- Do not ask for a separate permission between tree and `/goal` after explicit invocation when the tree passes all gates.
- Do not execute implementation unless the user separately asks for execution or explicitly enables `--execute-loop`.
- Do not write files except the required Super SPEC artifact, explicit save requests, or required execution-loop ledger.
- Do not include Next Prompt Handoff without an explicit handoff trigger.
- Do not include Adversarial Audit Heartbeat Prompt behavior without exact heartbeat prompt opt-in, and never let it execute, schedule, share, mutate files, or claim Goal Maestro stop-state authority.
- Do not turn `--audit-heartbeat-prompt` into a second `/tes-goal-maestro` command when it is combined with `--execute-loop`; emit it as a same-response read-only sidecar.
- Do not run Execution Loop without explicit `--execute-loop` and an `Execution Cost Draft`, Pre-Edit Gate and `GOAL-EXECUTION-LOOP-LEDGER`.
- Do not run Execution Loop unless the Tree Adversary is cleared or its objections are repaired.
- Do not allow parent fallback without the exact `--execute-loop-parent-fallback` flag.
- Do not let workers execute outside `ACTIVE_SPEC`, execute the next SPEC, push remotely, or own authoritative next-prompt generation.
- Do not edit, spawn a worker, or use parent fallback unless the Pre-Edit Gate declares `EXECUTE_LOOP_REQUESTED=yes`, `READY_GOAL_PROMPT=present`, `DECLARED_UNITS=<exact ordered ids>`, `FIRST_UNEXECUTED_UNIT=<id>`, matching `ACTIVE_SPEC=<id>`, `BASELINE_ONLY_COMMITS=<hashes or none>`, `LEDGER=<GOAL-EXECUTION-LOOP-LEDGER-...md>` and `MAY_EDIT=yes`.
- Do not let a generated or expanded Super SPEC consume a declared execution unit or advance `FIRST_UNEXECUTED_UNIT`.
- Do not let a reference implementation, prior build, browser smoke, run record, screenshot or post-facto audit satisfy material execution.
- Do not retry failed coding work before Failed Attempt Recovery classifies `bug_vs_architecture` and chooses bug repair, `structural_repair`, SPEC repair, `SPEC_REPAIR_BY_LLM`, escalation or stop.
- Do not run or close any `--execute-loop` without the required `GOAL-EXECUTION-LOOP-LEDGER`.
- Do not compress declared execution units into fewer implementation units.
- Do not allow empty commits to satisfy material execution units.
- Do not let build/typecheck alone satisfy an integration or runtime-wiring unit; stop with `NEEDS_INTEGRATION_ORACLE`.
- Do not close a required visual/browser axis as complete with `DEGRADED`, missing screenshots, or `browser_attempt=not_attempted`.
- Do not let a topology budget pass as prose; it must have an executable probe or an explicit source-proven exception.
- Do not let a parent-memory summary replace a source-derived contract handoff when workers reuse existing APIs; stop with `NEEDS_TREE_REPAIR` before worker spawn.
- Do not use broad lexical negative greps that reject valid policy vocabulary.
- Do not perform cloud escalation without owner approval of the exact sanitized payload and Cloud Query Redaction Block.
- Do not close an execution loop without Executive Stop Audit.
- Do not require or imply remote sync unless explicitly authorized.
- Do not embed project-specific domain examples in the skill. Domain specifics must come from the input artifact.

## Done

`tes-goal-maestro` is complete when it either stops with a precise status, delivers a faithful `READY_GOAL_PROMPT`, materializes a requested Super SPEC artifact, or completes an explicitly requested `--execute-loop` with certified loop status after parent validation and Executive Stop Audit.
