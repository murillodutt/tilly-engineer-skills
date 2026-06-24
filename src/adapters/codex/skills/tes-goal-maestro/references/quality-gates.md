# Quality Gates

Use this reference when the SPEC, materialization tree or `/goal` prompt might
be too weak to execute safely.

## Readiness Score

Assign the lowest applicable status.

### NEEDS_SPEC_MATURITY

Use when the SPEC lacks any required foundation:

1. canonical artifact;
2. capability or purpose;
3. certified context or dependencies;
4. phase boundary;
5. non-objectives;
6. central rule;
7. forbidden moves;
8. acceptance criteria or oracle candidates;
9. stop states or owner-decision points;
10. final delivery contract.

Return only the smallest missing set.

### NEEDS_ANCHOR_ARTIFACT

Use when the run cannot cite a persisted non-self anchor artifact with
`anchor_class`, `anchor_path` and `anchor_hash`, or when the generated tree is
trying to act as its own anchor.

Do not use this for semantically immature input. Use `NEEDS_SPEC_MATURITY` when
the content itself lacks maturity.

### READY_GOAL_PROMPT

Use when:

1. SPEC is mature;
2. tree is explicit and passes internal gates;
3. file ownership is clear;
4. oracles are falsifiable;
5. stop states are explicit;
6. coding, UI, runtime-script or generated-app units include an Engineering
   Method Profile, `STRUCTURAL_METHOD=<profile-id>`, topology budget,
   structural source probes, structural negative checks, structural oracles and
   structural handoff requirements;
7. the tree cites a persisted non-self anchor artifact;
8. any declared quality ceiling has an oracle or explicit owner deferral;
9. integration units include runtime-smoke oracles;
10. required visual/browser/runtime axes include PASS-capable certification
    units;
11. required Tree Adversary review is cleared or repaired;
12. `--execute-loop` worker context handoff is source-derived rather than parent
    memory.

Explicit skill invocation is enough to produce both the tree and the final
`/goal` prompt in one response when these conditions are true.

When a Super SPEC is generated in the flow, readiness also requires that the
full Super SPEC is written to `GOAL-SUPER-SPEC-<slug-or-timestamp>.md` and that
chat output contains only the artifact path and a short summary.

### NEEDS_EXECUTION_UNIT_FIDELITY

Use when the source artifact declares materialization units and the proposed
tree or prompt would omit, merge, rename, reorder or otherwise compress them.
Also use it when the prompt would treat empty commits, compacted broad commits,
prior commits, old closeouts or broad-only oracles as proof that individual
material units executed in a new materialization run.

Also use it when a mature artifact declares vertical slices or asset-transfer
units and the proposed tree rewrites them into horizontal layer packages such
as "all docs", "all scripts", "all tests", or broad cleanup.

Return the declared unit list and the proposed correction. Do not produce
`READY_GOAL_PROMPT` until the tree preserves the declared list or the user
explicitly accepts a changed execution contract.

`NEEDS_SLICE_FIDELITY` is a backward-compatible alias for older prompts, but
new skill output should prefer `NEEDS_EXECUTION_UNIT_FIDELITY`.

### NEEDS_TREE_REPAIR

Use when the generated tree fails fixed schema, ownership, oracle,
execution-unit fidelity, material-continuation, structural-method,
negative-grep semantics, commit-rhythm or closeout checks.

Also use it when the tree lacks source-derived worker handoff for a loop that
will reuse prior APIs, carries unvalidated API facts in the worker envelope, or
uses a parent-memory summary where repository symbols are available.

### NEEDS_STRUCTURAL_METHOD

Use when code, UI, generated app artifacts or runtime scripts are in scope and
the tree or prompt lacks a safe Engineering Method Profile.

Also use it when the profile or evidence shows behavior can pass while the
implementation collapses into a god file, duplicates domain logic, mixes UI,
domain, storage, runtime or adapter layers without contract, bypasses framework
topology, or misuses a single-file exception as permission for unbounded file
growth.

Also use it when the prompt names a profile but does not enforce it through a
Method Enforcement Packet: `STRUCTURAL_METHOD=<profile-id>`, file topology
budget, allowed new modules/internal sections, structural debt budget,
structural source probes, `bug_vs_architecture` recovery classification and
structural handoff constraints.

Also use it when browser, UI, game or rendered-canvas work requires
certification but the prompt or closeout lacks a stable browser metrics
contract or visual-spatial oracle for risks such as render, layout, spawn,
raycast, camera framing or spatial alignment.

Also use it when a topology budget is only reported as prose or line count
inventory. A numerical budget must have an executable probe or a source-proven
exception.

### NEEDS_AMBITION_RECONCILIATION

Use when the anchor declares a quality ceiling or ambition directive and the
tree silently lowers it to minimum viable behavior, future work, or
Non-Objectives without an owner decision or PASS-capable oracle.

### NEEDS_CONTRACT_EXTENSION_POINT

Use when a later unit needs to extend a shared contract frozen by an earlier
unit and no reserved extension point exists.

### NEEDS_INTEGRATION_ORACLE

Use when a runtime-wiring, game-loop, adapter-wiring or integration unit has
only build/typecheck/lint as proof. Build can accompany the runtime smoke; it
cannot replace it.

### AXIS_UNPROVEN

Use when an anchor-declared or tree-required quality/runtime axis lacks PASS
evidence at closeout. `DEGRADED` is honest evidence, but it does not satisfy a
required axis.

### VISUAL_CERT_BLOCKED

Use when browser or visual proof is required and no real browser/render attempt
was made, or the attempt failed for a captured environment reason. A blocked
environment must include command output in the ledger.

### NEEDS_TREE_ADVERSARY

Use when a required Pre-Execution Tree Adversary pass is absent, when the parent
self-clears its own adequacy objections, or when objections remain unrepaired
before `READY_GOAL_PROMPT`.

### DRAFT_MATERIALIZATION_TREE

Use only when the user explicitly asks for staged review before `/goal`.

### NEEDS_TREE_ACCEPTANCE

Use only when changing the declared execution contract requires owner
acceptance, or when a user-requested staged review tree has not been accepted.

## Maturity Failure Examples

Stop if the SPEC says:

1. "implement the feature" without canonical artifact;
2. "use best effort" without stop criteria;
3. "run everything" without phase boundary;
4. "add tests" without oracle candidates;
5. "integrate with storage/live/API" while saying the phase is contract-only;
6. "generate report" when the artifact is actually a machine contract.
7. "execute these slices" but the prompt collapses them into fewer commits.
8. "commit per slice" but there is no material-diff or sync evidence gate.
9. "continue from history" without saying whether prior commits are
   baseline-only or execution credit.
10. "execute these vertical slices" but the prompt rewrites them as all docs,
    all scripts, all tests or broad cleanup.
11. "build this app" without stating the intended code topology, structural
    boundaries or structure-sensitive oracles.
12. "certify this browser app/game/UI" without a machine-readable metrics
    artifact and visual-spatial evidence when visual or spatial failure is a
    realistic risk.
13. "wire the runtime" while listing only build/typecheck as proof.
14. "aim for the ceiling" or equivalent anchor language while routing ceiling
    features to future work without owner decision.
15. "continue with this tree" without a persisted anchor path and hash.

## Weak Prompt Rejection

Reject a prompt if it lacks:

1. `SPEC-000 Preflight And Baseline`;
2. allowed files per slice;
3. forbidden files or actions;
4. commit per SPEC;
5. material-diff proof per material SPEC;
6. focused oracles;
7. negative grep;
8. reviewer loop;
9. sync status per SPEC;
10. stop states;
11. final closeout.
12. exact preservation of any slice list declared by the SPEC.
13. treatment of prior commits or closeouts when they may exist.
14. semantic negative-grep separation for valid blocked-state vocabulary.
15. rejection of horizontal layer packages when the SPEC declares vertical
    slices or asset-transfer units.
16. Next Prompt Handoff only when explicitly requested, with post-`GO`
    certification, chat-only emission and no automatic execution.
17. Execution Loop only when `--execute-loop` is explicitly requested, with an
    Execution Cost Draft, Pre-Edit Gate, `ACTIVE_SPEC` isolation, parent
    validation, local-only commit sync, mandatory ledger and Executive Stop
    Audit.
18. Engineering Method Profile for coding, UI or generated-app work, including
    topology, exceptions, structural negative checks and structural oracles.
19. `STRUCTURAL_METHOD=<profile-id>`, topology budget, structural source
    probes, structural debt budget and structural handoff requirements for
    coding, UI, runtime-script or generated-app work.
20. persisted non-self anchor artifact path and hash.
21. Tree Adversary status when `--execute-loop` or high-risk execution is in
    scope.
22. runtime-smoke oracle for integration units.
23. PASS-capable browser/visual certification unit for required visual axes.
24. source-derived contract handoff artifact and API lint status for fresh
    workers that reuse existing APIs.

## Boundary Leakage Checks

Ask whether the prompt accidentally permits:

1. runtime execution in a contract-only phase;
2. storage or migration in a semantic phase;
3. public API or UI changes in an internal phase;
4. network/live access in a fixture-first phase;
5. destructive git or filesystem operations;
6. secrets, credentials or private data;
7. raw payload export;
8. final interpretation, verdict or score;
9. god-file growth above `FILE_TOPOLOGY_BUDGET` measured by an executable
   probe, framework-topology bypass or accidental UI/domain/storage mixing in
   coding or app-building work.
10. next-unit architecture regression because no structural handoff carried the
    active method, changed topology, accepted debt and constraints.

If yes, revise before returning the prompt.

## Interaction Checks

A valid skill response must not stop to ask permission between a valid tree and
the `/goal` prompt after explicit invocation. The tree gate is technical:
generate, validate, then emit `READY_GOAL_PROMPT`.

A valid response must not paste a generated Super SPEC into the context window.
Use the `GOAL-SUPER-SPEC-<slug-or-timestamp>.md` artifact instead, then continue
to the tree and `/goal` prompt when the remaining gates pass.

Next Prompt Handoff is valid only when explicitly requested by
`next_prompt_handoff=true`, `--next-prompt-handoff`, or an equivalent direct
trigger. When requested, the generated prompt must require chat-only next
prompt emission after `GO` and certification, must not write the next prompt to
disk without an explicit save request, and must not execute it automatically.
When not requested, the prompt must not include a next-prompt handoff clause.

Execution Loop is valid only when explicitly requested by `--execute-loop`.
When requested, the generated response must require an `Execution Cost Draft`
from material sources before spawning, one fresh worker per `ACTIVE_SPEC`,
full prompt plus hard active-SPEC envelope, a Pre-Edit Gate with
`EXECUTE_LOOP_REQUESTED=yes`, `READY_GOAL_PROMPT=present`, `DECLARED_UNITS`,
`FIRST_UNEXECUTED_UNIT`, `ACTIVE_SPEC`, `BASELINE_ONLY_COMMITS`, `LEDGER`,
`ANCHOR_CLASS`, `ANCHOR_PATH`, `ANCHOR_HASH`, `TREE_ADVERSARY_STATUS` and
`MAY_EDIT=yes`, parent validation before advancing, local automatic commit per
green SPEC, no remote push, bounded
`SPEC_REPAIR_BY_LLM`, a loop-state block for every attempt, classified
baseline state before the first worker, owner-approved cloud escalation only,
failed-attempt recovery before the next attempt, persistent ledger for every
`--execute-loop`, exact parent-fallback flag authorization, bounded audit
repairs, strict sequential replay, baseline-only comparison for reference
implementations or manual builds, no Super SPEC materialization counted as a
declared execution unit, active Engineering Method Profile when code structure
is in scope, `STRUCTURAL_METHOD=<profile-id>` envelope fields, structural
decision ledger fields, `bug_vs_architecture` recovery classification,
source-derived contract handoff, runtime-smoke for integration units, PASS-only
required visual axes, and Executive Stop Audit before final stop.
When not requested, the prompt must not include execution-loop behavior.

If Next Prompt Handoff and Execution Loop are both explicitly requested,
Execution Loop owns internal continuation. Reject prompts that also include the
ordinary handoff constraint in a way that forbids parent-runner execution of
the next validated active-SPEC prompt.

## Commit Rhythm Checks

A valid prompt must require:

1. no accumulated multi-slice commits;
2. stage only current-unit files;
3. semantic commit messages;
4. no empty commits for material units;
5. `git show --stat --oneline <commit>` evidence for each material unit;
6. changed files inside the unit's allowed file matrix;
7. no unrelated revert;
8. no force push;
9. worktree status inspection after each commit and before final closeout;
10. one visible commit per declared unit unless explicitly no-commit;
11. sync status per unit;
12. prior commits are baseline-only by default unless explicitly accepted as
    execution credit;
13. no rewrite, rebase, squash or deletion of historical evidence to repair
    materialization fidelity.

## Material Execution Checks

Before `GO`, verify:

1. declared unit count matches executed unit count;
2. each material unit has a non-empty diff or explicit no-material-change
   rationale accepted by the source artifact;
3. each material unit has focused oracle evidence;
4. broad regression did not replace missing per-unit oracles;
5. compacted implementation commits were not masked by later empty commits;
6. prior commits or closeouts were not counted as new material execution by
   default;
7. earlier failed or partial closeouts were preserved as historical evidence
   and repaired through additive material commits when applicable;
8. reference implementations, prior manual builds, browser smoke results, run
   records and post-facto audits were baseline-only comparison evidence, not
   execution credit;
9. structural method evidence exists for coding, UI or generated-app units;
10. structural source probes ran; numerical topology probes cannot be waived as
    impossible unless the probe target does not exist and the unit stops;
11. structural handoff exists when another unit can build on the same code;
12. browser metrics artifact exists when browser app, UI, game or rendered
    canvas certification is in scope;
13. visual-spatial oracle evidence exists, or a real browser/render attempt
    failed with captured environment output when visual or spatial failure is
    in scope;
14. remote sync is reported only when explicitly authorized;
15. persisted non-self anchor was cited by path and hash;
16. Tree Adversary status is cleared or repaired when required;
17. integration units have runtime-smoke artifacts that pass;
18. required browser/visual axes have `status=PASS`, `visual.proven=true` and
    at least one evidence artifact;
19. `DEGRADED` or `BLOCKED` required axes route to `AXIS_UNPROVEN` or
    `VISUAL_CERT_BLOCKED`, not `GO`;
20. worker envelopes that reuse APIs include a source-derived handoff artifact
    and `api_lint_status=PASS`.

If any execution-fidelity check fails, use `NEEDS_EXECUTION_UNIT_FIDELITY`.
If structural method evidence is missing or failing, use
`NEEDS_STRUCTURAL_METHOD`.
If runtime-smoke is missing for an integration unit, use
`NEEDS_INTEGRATION_ORACLE`. If a required axis is unproven, use
`AXIS_UNPROVEN` or `VISUAL_CERT_BLOCKED`.

## Closeout Checks

Final delivery must report:

1. status: `GO`, `NEEDS_OWNER_DECISION`, `BLOCKED` or `SAFETY_BLOCKED`;
2. execution units executed;
3. commits;
4. files changed;
5. tests and oracles run;
6. failures fixed;
7. boundaries preserved;
8. pending owner decisions.
9. declared unit count versus executed unit count.
10. material units with non-empty diff versus empty/no-diff units.
11. sync status for each unit.
12. whether prior commits/closeouts were baseline-only or explicitly credited.
13. whether negative grep allowed valid blocked-state vocabulary while
    forbidding unsafe behavior.
14. structural method result for coding, UI or generated-app units.
15. structural handoff for coding, UI or generated-app units when applicable.
16. browser metrics artifact and visual-spatial oracle result when applicable.
17. anchor artifact path and hash.
18. Tree Adversary result.
19. runtime-smoke result for integration units.
20. contract handoff artifact and API lint status when workers reused APIs.

## Stop-State Mapping

Use:

- `GO` when all required slices are committed, oracles are green and no
  boundary is violated.
- `NEEDS_OWNER_DECISION` when the next safe step needs product, architecture,
  public-surface, data, legal, live-execution or ownership decision.
- `NEEDS_STRUCTURAL_METHOD` when code, UI or generated-app work lacks a safe
  Engineering Method Profile or fails structure-sensitive checks.
- `NEEDS_ANCHOR_ARTIFACT` when no persisted non-self anchor is available.
- `NEEDS_TREE_ADVERSARY` when a required adversarial tree pass is missing or
  uncleared.
- `NEEDS_AMBITION_RECONCILIATION` when anchor-declared ceiling is silently
  lowered.
- `NEEDS_CONTRACT_EXTENSION_POINT` when a shared contract needs a reserved
  extension point before later units can extend it.
- `NEEDS_INTEGRATION_ORACLE` when integration proof is build-only.
- `AXIS_UNPROVEN` when a required runtime/quality axis has no PASS evidence.
- `VISUAL_CERT_BLOCKED` when required visual/browser evidence was not attempted
  or is blocked by captured environment limits.
- `BLOCKED` when a critical oracle fails outside the slice's control.
- `SAFETY_BLOCKED` when the task would require unsafe access, fake authority,
  secrets, destructive operations, bypass, private data, or hidden production
  changes.

## Final Prompt Strength Test

Before returning `READY_GOAL_PROMPT`, run this compact strength test. Route the
first failed answer to the named status.

1. Persisted non-self anchor path and hash exist:
   `NEEDS_ANCHOR_ARTIFACT`.
2. A capable agent can execute without asking artifact, files, oracles, commit
   rhythm or stop state: `NEEDS_TREE_REPAIR`.
3. Declared units remain visible, ordered and mapped to commit decisions:
   `NEEDS_EXECUTION_UNIT_FIDELITY`.
4. Prior commits and closeouts are explicitly baseline-only or credited by the
   source/owner: `NEEDS_TREE_REPAIR`.
5. Negative greps forbid behavior without rejecting valid policy vocabulary:
   `NEEDS_TREE_REPAIR`.
6. Anchor-declared ceiling and shared-contract extension checks pass
   `references/ambition-and-anchor.md`:
   `NEEDS_AMBITION_RECONCILIATION` or
   `NEEDS_CONTRACT_EXTENSION_POINT`.
7. Coding/UI/generated-app units pass `references/structural-method.md`,
   including executable topology probes: `NEEDS_STRUCTURAL_METHOD`.
8. Runtime, integration, browser and visual axes pass
   `references/runtime-certification.md`: `NEEDS_INTEGRATION_ORACLE`,
   `AXIS_UNPROVEN` or `VISUAL_CERT_BLOCKED`.
9. Fresh-worker API reuse passes `references/execution-context-handoff.md`:
   `NEEDS_TREE_REPAIR`.
10. Required adversarial review passes `references/tree-adversary.md`:
    `NEEDS_TREE_ADVERSARY`.
11. Optional Next Prompt Handoff and `--execute-loop` clauses appear only when
    explicitly requested and carry the runner contract:
    `NEEDS_TREE_REPAIR`. Parent fallback must require the exact
    `--execute-loop-parent-fallback` flag.
