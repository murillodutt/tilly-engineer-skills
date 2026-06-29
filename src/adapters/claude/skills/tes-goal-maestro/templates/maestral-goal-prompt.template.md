# Maestral Goal Prompt Template

```text
/goal Materialize <CanonicalArtifact> as <capability/purpose>, in incremental, auditable, fixture-first execution with commit per SPEC.

Do not restart from zero. Use the real worktree and Git state as the source of truth.

Main SPEC: <path/to/spec.md>

Anchor artifact:
- ANCHOR_CLASS=<PRD|ADR|Super-SPEC|SPEC|relational-project-plan|accepted-execution-tree>
- ANCHOR_PATH=<path>
- ANCHOR_HASH=<hash captured before tree generation>
- ANCHOR_ORIGIN=<provided|materialized-from-anchor|previous-session>

Certified context:
- <certified dependency or prior closeout>
- <existing contract/module that must be reused>
- <phase boundary already decided>
- <known deferred work>

Shared contracts:
- <contract_name, declaring SPEC, frozen surface, extension points, extenders, optionality rule and declaring oracles, or none>

Mission: <short mission explaining the artifact, capability and value>

Phase boundary: <what this phase may do> <what later phases must do instead>

Central rule: <single rule that prevents semantic drift>

Quality ceiling:
- ambition_directive=<quoted source directive or ABSENT>
- quality_ceiling=<required ceiling features or ABSENT>
- ceiling_decision=<oracled_now|owner_deferred|not_applicable>

Do not allow:
- <forbidden move 1>
- <forbidden move 2>
- <forbidden move 3>
- <forbidden move N>

Engineering Method Profile:
- STRUCTURAL_METHOD=<profile-id>
- Stack or language family: <HTML/CSS/JS, TypeScript, Vue, React, Python, CLI, docs generator, adapter, or no-code rationale>
- Intended topology: <files/modules/components/composables/stores/services/adapters/scripts/internal sections>
- Topology decision artifact: <tree block, ledger block, ADR path, or not_applicable>
- Structural boundaries: <UI/domain/storage/runtime/docs/adapter boundaries>
- Topology exceptions: <none or source-mandated single-file deliverable with internal modularity, named sections, narrow APIs and no duplicated logic>
- File topology budget: <max files, max line growth, max section growth or source-proven exception>
- Allowed new modules/internal sections: <paths, names or none>
- Structural debt budget: <none, accepted debt, or owner-decision needed>
- Structural source probes: <line counts, module inventory, import-boundary checks, duplicate-symbol scans, inline CSS/JS scans, framework probes or single-file section-anchor checks>
- Structural negative checks: <god file, duplicated logic, layer mixing, framework-topology bypass, broad inline CSS/JS when separation is expected, unchecked file-size growth>
- Structural oracles: <size thresholds, module/component inventory, import/dependency checks, lint/typecheck/build, rendered UI smoke or source probes>
- Browser metrics contract: <browser-metrics.json fields or not_applicable>
- Visual-spatial oracle: <screenshot, pixel, legibility, canvas, bounding-box/spawn/raycast check or not_applicable>
- Runtime smoke oracle: <command/artifact for integration units or not_applicable>
- Topology probe: <executable command that fails on budget excess or not_applicable>
- Shared contract surface: <frozen fields, extension points and optionality rule or not_applicable>

Subagents:

1. <Role Senior>
Ownership:
- <allowed path or responsibility>
Mission:
- <bounded mission>

2. Tests Senior
Ownership:
- <test paths>
Mission:
- Build focused, adversarial and regression tests for this phase.

3. Reviewer Senior
Read-only per SPEC. Mission:
- Review scope inflation, boundary drift, forbidden moves, missing oracles and false closure.

4. Evidence/Oracle Senior
Ownership:
- <reports/checklists if any>
Mission:
- Track commands, outputs, gaps, closeout and final status.

Work mode:
- Execute small SPECs.
- Do not accumulate multiple SPECs without commit.
- If prior commits, closeouts or partial implementations exist, treat them as baseline context by default, not execution credit for this run.
- Produce a new additive material trail with non-empty commits per material unit unless the source artifact explicitly marks a unit no-material-change or no-commit.
- Do not rewrite, rebase, squash, delete or mask historical evidence.
- Preserve every materialization unit declared by the input artifact.
- Do not merge declared units unless the user explicitly changes the execution contract before implementation.
- A declared no-commit preflight must still be reported as executed.
- Before editing code, UI or generated app artifacts, apply the Engineering Method Profile and do not accept behavior-only green if structure regresses.
- When the source does not mandate topology, record the topology decision before the first material implementation commit.
- When browser, UI, game, canvas or rendered app behavior is in scope, emit a stable browser metrics artifact and visual-spatial evidence when visual or spatial failure is possible.
- When an integration unit wires modules into the executable runtime, run a behavioral runtime smoke; build and typecheck are necessary but not sufficient.
- When workers reuse existing APIs, provide source-derived symbols, import paths, oracle runner commands and API lint status instead of parent-memory summaries.
- Stage only files for the current SPEC.
- Commit and certify the current SPEC before starting the next SPEC.
- Do not revert user changes.
- Preserve unrelated worktree changes.
- Run focused oracle before broader oracle.
- Fix until green or stop honestly.
- No force push, destructive git, hidden live execution or public-surface drift.

Next Prompt Handoff:
- Disabled unless `next_prompt_handoff=true`, `--next-prompt-handoff`, or an equivalent direct trigger was explicitly requested.
- When enabled, after this run reaches `GO` and certification is complete, emit the next `/goal` prompt for the next declared execution unit in this same chat/context window.
- If code, UI, runtime scripts or generated app artifacts changed, include a structural handoff in the next prompt: active `STRUCTURAL_METHOD`, files or modules changed, boundaries preserved, accepted structural debt and next-unit constraints.
- Do not write the next prompt to disk unless the user explicitly asks.
- Do not execute the next prompt automatically.
- If this run stops, certification is incomplete, or no next declared unit exists, report the stop/final state instead of generating a next prompt.
- If `--execute-loop` is also enabled, suspend this ordinary handoff clause for internal continuation; the parent runner owns next-prompt generation and may execute the next active-SPEC prompt only after parent validation.

Execution Loop:
- Disabled unless `--execute-loop` was explicitly requested.
- When enabled, the parent runner must create an `Execution Cost Draft` before spawning any worker.
- Before any edit, worker spawn, parent fallback or material commit, the parent must emit and pass this Pre-Edit Gate: `EXECUTE_LOOP_REQUESTED=yes`, `READY_GOAL_PROMPT=present`, `ANCHOR_CLASS=<class>`, `ANCHOR_PATH=<path>`, `ANCHOR_HASH=<hash>`, `TREE_ADVERSARY_STATUS=<ADVERSARY_CLEARED|OBJECTIONS_REPAIRED|not_required>`, `DECLARED_UNITS=<exact ordered unit ids>`, `FIRST_UNEXECUTED_UNIT=<id>`, `ACTIVE_SPEC=<id>`, `BASELINE_ONLY_COMMITS=<hashes or none>`, `LEDGER=<GOAL-EXECUTION-LOOP-LEDGER-...md>`, `MAY_EDIT=yes`.
- If `FIRST_UNEXECUTED_UNIT != ACTIVE_SPEC`, or if `MAY_EDIT` is not `yes`, stop with `NEEDS_EXECUTION_UNIT_FIDELITY` before editing.
- Materializing or expanding a Super SPEC is preparatory contract work. It does not consume any declared execution unit or advance `FIRST_UNEXECUTED_UNIT`.
- The parent runner opens one `ACTIVE_SPEC` at a time with the full prompt plus a hard active-SPEC envelope.
- Workers may execute only `ACTIVE_SPEC`; they may propose next-prompt material but the parent generates the next prompt.
- Local commit per green SPEC is allowed; remote sync or push remains forbidden without separate user authorization.
- Reference implementations, prior manual builds, browser smoke results, screenshots, run records and post-facto audits are baseline-only comparison evidence. They never count as execution credit for this loop.
- Strict sequential replay is required: a SPEC is complete only from evidence produced after its `ACTIVE_SPEC` was opened and parent-validated before the next SPEC starts.
- The parent must classify the baseline worktree before the first worker, carry the active Engineering Method Profile when code structure is in scope, carry `STRUCTURAL_METHOD=<profile-id>`, topology budget, allowed modules and structural debt budget in the active envelope, maintain a loop-state block for every attempt, repair only canonical SPEC artifacts, resolve failed-attempt residue before the next attempt with `bug_vs_architecture`, carry source-derived contract handoff, enforce runtime smoke for integration, require PASS evidence for required visual axes, and use cloud escalation only after owner-approved redaction.
- Failed Attempt Recovery is mandatory before retrying a failed coding `ACTIVE_SPEC`.
- Parent-side execution fallback is disabled unless the exact `--execute-loop-parent-fallback` flag was requested.
- Create `GOAL-EXECUTION-LOOP-LEDGER-<slug-or-timestamp>.md` before the first `ACTIVE_SPEC` opens for every `--execute-loop`.
- The ledger must carry structural decision fields when code structure is in scope: `structural_method_id`, `topology_decision`, `structural_debt` and `next_structural_constraint`.
- For browser, UI, game or rendered-canvas work, the ledger or closeout must carry the browser metrics contract and visual-spatial oracle result.
- Certification repairs are allowed only as bounded `audit_repair` work inside the active final/audit SPEC, with local commit evidence and rerun oracles.
- Audit-added `SPEC-AUDIT-*` units are bounded; repeated audit expansion without new material evidence stops for owner decision or contract instability.
- Execution Thermometer Hook: after loop close or honest stop, run default/always-on local report/package generation from the persistent ledger, record Thermometer report/share fields separately, and do not rewrite Goal Maestro execution stop states unless report generation was explicitly the active product requirement.
- Final stop requires Executive Stop Audit.

Negative grep semantics:
- Separate valid blocked-state or policy vocabulary from forbidden executable behavior.
- Allow enums, reason codes and fields that record a technical block when they are part of the contract.
- Forbid behavior such as solving CAPTCHA, proxy evasion, fake credentials, leaked secret use, hidden network calls, unauthorized storage or runtime boundary violations.

First mandatory act:
1. Run `git status --short --branch --untracked-files=all`.
2. Run `git log --oneline -12` when lineage matters.
3. Identify unrelated pending changes.
4. Read the main SPEC and existing dependencies.
5. Run read-only baseline oracles.
6. Derive the Engineering Method Profile before editing code, UI or generated app artifacts.
7. Declare `STRUCTURAL_METHOD=<profile-id>`, topology budget, allowed new modules/internal sections and structural source probes before editing.
8. If topology is inferred rather than source-mandated, record the structural decision artifact before the first material implementation commit.
9. Declare the browser metrics and visual-spatial oracle requirements when app, UI, game, canvas or rendered app work is in scope.
10. Declare the runtime-smoke oracle when wiring/integration is in scope.
11. Declare source-derived contract handoff and API lint status when reusing prior APIs.
12. Declare the file matrix before editing.
13. If `--execute-loop` is active, create the ledger and pass the Pre-Edit Gate before the first worker spawn or material edit.

SPEC-000 Preflight And Baseline Objective: <baseline objective> Allowed files:
- <paths>
Forbidden:
- <paths/actions>
Oracles:
- <commands>
Commit: <none or semantic commit when baseline docs are in scope>

Execution unit fidelity:
- Preserve the source-declared queue exactly.
- Execute each declared unit in order.
- Commit after each declared unit unless the unit is explicitly no-commit.
- Empty commits do not satisfy material execution units.
- Prior commits or closeouts do not satisfy this run's material units by default; they are baseline-only unless explicitly accepted by the source artifact or owner.
- Super SPEC materialization does not satisfy or consume a declared execution unit unless that same declared unit is explicitly active.
- Earlier failed or partial closeouts must be preserved as historical evidence and repaired through additive material commits, not overwritten as if they never happened.
- A SPEC is complete only after focused oracle, reviewer diff check, semantic commit, captured commit hash, `git show --stat`, post-commit status and sync status.
- Default sync is local commit certification. Remote sync or push requires explicit user authorization.
- Stop with `NEEDS_EXECUTION_UNIT_FIDELITY` if the prompt cannot preserve this queue.

SPEC-001 <Small Slice> Objective: <one narrow goal> Allowed files:
- <paths>
Forbidden:
- <paths/actions>
Owner: <role> Oracles:
- <focused commands>
Runtime smoke oracle:
- <command/artifact or not_applicable>
Negative checks:
- <rg commands or assertions>
Commit: <semantic commit> Completion evidence:
- Changed files:
- `git show --stat --oneline <commit>`:
- Oracles:
- Negative checks:
- Structural method result:
- Topology probe result:
- Structural handoff:
- Runtime smoke result:
- Contract handoff artifact:
- API lint status:
- Reviewer result:
- Post-commit status:
- Sync status:
  - `LOCAL_COMMITTED`
  - `REMOTE_SYNCED`
  - `REMOTE_SYNC_NOT_REQUESTED`
  - `SYNC_BLOCKED`

SPEC-002 <Small Slice> Objective: <one narrow goal> Allowed files:
- <paths>
Forbidden:
- <paths/actions>
Owner: <role> Oracles:
- <focused commands>
Commit: <semantic commit> Completion evidence:
- Changed files:
- `git show --stat --oneline <commit>`:
- Oracles:
- Negative checks:
- Structural method result:
- Structural handoff:
- Reviewer result:
- Post-commit status:
- Sync status:

Full Oracle And Closeout Run:
- <focused test suite>
- <regression suite>
- <lint/typecheck/contract/doc checks>
- <structural method checks when applicable>
- <browser metrics artifact check when applicable>
- <visual-spatial screenshot/pixel/legibility check when applicable>
- <runtime-smoke artifact check when applicable>
- <contract handoff/API lint check when applicable>
- `git diff --check`
Negative grep:
- <forbidden runtime or provider pattern>
- <unsafe export pattern>
- <phase leakage pattern>
Closeout artifact:
- <report path, if any>
Commit: <semantic certification commit>

Stop criteria:
- `GO`: <green condition>
- `NEEDS_OWNER_DECISION`: <decision condition>
- `BLOCKED`: <critical external blocker>
- `SAFETY_BLOCKED`: <unsafe condition>

Final delivery:
- SPECs executed;
- subagents used;
- commits;
- per-SPEC material-diff evidence;
- sync status per SPEC;
- files changed;
- oracles run;
- structural method result when applicable;
- structural handoff when applicable;
- topology probe result when applicable;
- runtime smoke result when applicable;
- browser metrics artifact and visual-spatial oracle result when applicable;
- contract handoff artifact and API lint status when applicable;
- anchor artifact and Tree Adversary result;
- boundaries preserved;
- blockers or decisions pending;
- next prompt handoff status when explicitly requested;
- execution loop status when `--execute-loop` was requested;
- final status.
```
