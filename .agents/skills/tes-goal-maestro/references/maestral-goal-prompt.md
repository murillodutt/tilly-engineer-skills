# Maestral Goal Prompt

Use this reference only after:

1. the SPEC passes the Maturity Gate;
2. the materialization tree has been produced;
3. the tree passes the skill's internal fidelity and quality gates.

Do not ask the user for an extra acceptance step before producing `/goal` unless the user explicitly requested staged review or the tree would change the declared execution contract.

This reference is the router and hardening checklist. The full literal prompt body lives in `templates/maestral-goal-prompt.template.md`. Load that template before returning `READY_GOAL_PROMPT`.

## Core Rule

```text
A maestral /goal prompt is an execution contract, not a long request.
```

It must let a future agent execute without inventing artifact, scope, boundaries, owners, tests, commit rhythm or stop states.

It must start from a persisted non-self anchor artifact and must not make the generated tree its own source of truth.

If the source flow created a Super SPEC, the prompt must name the `GOAL-SUPER-SPEC-<slug-or-timestamp>.md` artifact path as the canonical Super SPEC reference. Do not embed the full Super SPEC body inside the `/goal` prompt unless the user explicitly requests a self-contained prompt and accepts the larger context footprint.

If the source artifact declares a materialization queue, the prompt must preserve that queue. The prompt is not allowed to compress declared execution units into fewer execution commits.

A commit message is not execution evidence. The prompt must require material diff proof, focused oracles, reviewer result, post-commit status and sync status for every material unit.

## Optional Adversarial Audit Heartbeat Prompt

Adversarial Audit Heartbeat Prompt is a separate opt-in prompt-generation mode.
It activates only from `--audit-heartbeat-prompt`, `audit_heartbeat=true`,
`adversarial_audit_heartbeat: requested`, or a direct request to generate or
create an adversarial audit heartbeat prompt in the active request, active
structured control block, or active source artifact.

When activated, load `references/adversarial-audit-heartbeat.md` and
`templates/adversarial-audit-heartbeat.template.md`, then emit only the
copy-ready English heartbeat prompt. Do not embed a heartbeat section in an
ordinary maestral `/goal` prompt, and do not alter Goal Maestro stop-state
semantics. Do not embed a heartbeat section in an ordinary maestral /goal prompt.

Do not activate from broad words such as heartbeat, monitor, audit, mentorship,
watch this, keep an eye on it, or translated equivalents. Documentation
examples, historical ledgers, or inactive artifacts do not activate the feature
by containing the opt-in text.

## Required Output Shape

The final prompt must include:

1. `/goal` opening line.
2. Mission.
3. Main SPEC path.
4. Anchor artifact class, path and hash.
5. Super SPEC artifact path when one was created.
6. Certified context.
7. Shared contracts when units cross a type/API boundary.
8. Phase boundary.
9. Central rule and quality ceiling when the anchor declares one.
10. Non-objectives and forbidden moves.
11. Specialized subagents with ownership.
12. Work mode.
13. First mandatory act.
14. `SPEC-000 Preflight And Baseline`.
15. Narrow execution units.
16. Full oracle.
17. Negative grep.
18. Stop criteria.
19. Final delivery contract.
20. Execution unit fidelity statement when the input artifact declares units.
21. Per-unit material-diff and sync-commit evidence requirements.
22. Material continuation rule when prior commits, closeouts or partial implementations may exist.
23. Semantic negative-grep rules when blocked-state vocabulary is valid inside the contract.
24. Engineering Method Profile and Method Enforcement Packet when the run changes code, UI, runtime scripts or generated app artifacts.
25. Runtime-smoke oracle when any unit has `unit_role=integration`.
26. Browser/visual runtime certification unit when a required visual axis exists.
27. Source-derived contract handoff and API lint for `--execute-loop` workers that reuse prior APIs.
28. Tree Adversary status when `--execute-loop` or high-risk execution is in scope.
29. Optional Next Prompt Handoff clause only when explicitly requested by `next_prompt_handoff=true`, `--next-prompt-handoff`, or an equivalent direct trigger.
30. Optional Execution Loop boundary only when explicitly requested by `--execute-loop`.
31. Optional Adversarial Audit Heartbeat Prompt output only when exact heartbeat prompt opt-in is present; this output uses the separate heartbeat template and is not added to ordinary `/goal` prompts.

## Template Load Contract

Before returning `READY_GOAL_PROMPT`, load `templates/maestral-goal-prompt.template.md` and verify that the generated prompt carries the required shape.

The template must carry, when relevant:

- `Execution Loop:`
- Pre-Edit Gate
- `FIRST_UNEXECUTED_UNIT`
- `MAY_EDIT=yes`
- Engineering Method Profile
- `STRUCTURAL_METHOD=<profile-id>`
- Structural method result
- Structural handoff
- `bug_vs_architecture`
- failed-attempt residue
- `GOAL-EXECUTION-LOOP-LEDGER`
- `ANCHOR_CLASS`
- `ANCHOR_PATH`
- Tree Adversary
- Runtime smoke oracle
- Contract handoff artifact
- API lint status
- strict sequential replay
- reference implementations
- exact `--execute-loop-parent-fallback` flag
- Executive Stop Audit

## Prompt Hardening Checklist

Before returning `READY_GOAL_PROMPT`, verify the prompt:

1. starts from a real SPEC;
2. cites a persisted non-self anchor artifact with path and hash;
3. includes `SPEC-000`;
4. names allowed files per slice;
5. names forbidden moves;
6. assigns ownership;
7. includes per-slice oracles;
8. includes negative grep;
9. requires commit per SPEC;
10. preserves every declared execution unit without silent merge;
11. forbids empty commits as proof of material execution;
12. requires `git show --stat` evidence per material unit;
13. states how prior commits or closeouts are treated when they exist;
14. distinguishes allowed policy vocabulary from forbidden behavior in negative grep;
15. requires sync status per unit;
16. preserves unrelated worktree changes;
17. includes reviewer and evidence/oracle roles when complexity warrants them;
18. includes an Engineering Method Profile, `STRUCTURAL_METHOD=<profile-id>`, topology budget, structural source probes and structural oracles when code, UI or generated app artifacts are in scope;
19. enforces topology budgets with executable probes or source-proven exceptions;
20. records a structural decision artifact before implementation when topology is inferred rather than source-mandated;
21. includes runtime-smoke for integration units;
22. includes browser metrics and visual-spatial certification requirements that require PASS evidence for required axes;
23. includes source-derived contract handoff and API lint for reused APIs in fresh-worker loops;
24. includes Tree Adversary status when required;
25. defines stop criteria;
26. defines final delivery;
27. includes a Next Prompt Handoff clause only when explicitly requested, and that clause is chat-only, post-certification, non-executing, and does not write prompt/tree files without an explicit save request;
28. includes an Execution Loop boundary only when `--execute-loop` is explicitly requested, and that boundary preserves parent authority, Pre-Edit Gate, `ACTIVE_SPEC` isolation, baseline classification, loop-state evidence, failed-attempt recovery, mandatory persistent ledger, local-only commit sync, baseline-only comparison for reference implementations, no Super SPEC materialization as unit credit, strict sequential replay, bounded repair/audit behavior, explicit parent-fallback authorization, `bug_vs_architecture` recovery classification, structural decision ledger fields and Executive Stop Audit.
29. emits Adversarial Audit Heartbeat Prompt content only when exact heartbeat prompt opt-in is present, and then uses the separate heartbeat template instead of altering ordinary `/goal` prompt shape.

## Stop If Missing

Stop with `NEEDS_SPEC_MATURITY`, `NEEDS_TREE_REPAIR`, `NEEDS_EXECUTION_UNIT_FIDELITY`, `NEEDS_STRUCTURAL_METHOD` or `NEEDS_TREE_ACCEPTANCE`, `NEEDS_ANCHOR_ARTIFACT`, `NEEDS_AMBITION_RECONCILIATION`, `NEEDS_INTEGRATION_ORACLE`, `VISUAL_CERT_BLOCKED`, `NEEDS_CONTEXT` or `NEEDS_TREE_ADVERSARY` when:

1. the canonical artifact is unclear;
2. the anchor artifact is missing, self-referential or unhashed;
3. the execution phase is unclear;
4. forbidden moves are missing;
5. oracles are missing;
6. the materialization tree fails internal gates;
7. the prompt would need to invent file ownership or stop states;
8. the prompt would need to merge or drop declared execution units;
9. code, UI or generated app artifacts are in scope but the prompt lacks an Engineering Method Profile, `STRUCTURAL_METHOD=<profile-id>`, topology budget, structural source probes, structural negative checks, structural oracles or structural handoff requirements;
10. integration units have only build/typecheck proof;
11. browser, UI, game or rendered-canvas work is in scope but the prompt lacks required-axis PASS certification;
12. fresh-worker loops would depend on parent memory instead of source-derived handoff;
13. Tree Adversary is required but absent or uncleared;
14. `templates/maestral-goal-prompt.template.md` was not loaded before prompt construction;
15. Adversarial Audit Heartbeat Prompt activation would depend on broad wording instead of exact opt-in, in which case stop with `NEEDS_OPT_IN_CONTRACT`;
16. any anchor-traceable axis would reach a worker without resolved context — `runtime_target`, an `oracle_runner_contract` with a regression target, or (under isolation) `forbidden-write`/`forbidden-import` constraints — in which case stop with `NEEDS_CONTEXT` and do not emit the prompt. This gate runs at prompt generation, not only inside `--execute-loop`: a holed envelope must be caught before the worker, not after.

Use `NEEDS_TREE_ACCEPTANCE` only when changing the declared execution contract requires owner acceptance or the user explicitly asked for staged review.

## Anti-Patterns

Reject prompts that:

1. say "implement everything" without slices;
2. allow broad best effort;
3. mix contract, runtime, storage and live execution accidentally;
4. omit `git status` preflight;
5. omit per-SPEC commit;
6. allow empty commits to satisfy material execution;
7. omit `git show --stat` material-diff proof;
8. omit sync status;
9. omit negative grep;
10. treat reviewer as optional for high-risk work;
11. end with prose instead of evidence;
12. hide owner decisions;
13. authorize actions not present in the SPEC;
14. compress a declared multi-SPEC queue into fewer commits;
15. let prior commits satisfy a new materialization run by default;
16. use broad lexical greps that fail valid blocked-state vocabulary instead of targeting forbidden behavior;
17. include Next Prompt Handoff without an explicit parameter/trigger or allow it to execute the next prompt automatically;
18. include Adversarial Audit Heartbeat Prompt behavior without exact heartbeat prompt opt-in or add it into ordinary `/goal` prompts;
19. include Execution Loop without explicit `--execute-loop` or let a worker execute outside `ACTIVE_SPEC`, push remotely, or bypass Executive Stop Audit;
19. let a reference implementation, prior manual build, browser smoke result, run record or post-facto audit satisfy `--execute-loop` without strict sequential replay;
20. accept a behavior-green implementation that collapsed into a god file, duplicated domain logic, bypassed framework topology or misused a single-file exception to mix unrelated layers;
21. retry a failed coding SPEC without classifying `bug_vs_architecture` and deciding whether the next action is bug repair, `structural_repair`, SPEC repair, escalation or stop;
22. generate a next prompt after code changes without structural handoff for the active method, changed topology, accepted debt and next-unit constraints;
23. certify browser, UI, game, canvas, spawn, raycast, layout or 3D-render work from logic-only checks when a visual-spatial failure can still occur;
24. close a required visual axis with `DEGRADED`, no screenshots, or no browser attempt;
25. accept build/typecheck-only proof for runtime integration;
26. send fresh workers into reused APIs with only parent-memory summaries;
27. hide certification-time repairs as ordinary closeout instead of bounded, committed `audit_repair` evidence.
