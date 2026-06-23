# Maestral Goal Prompt

Use this reference only after:

1. the SPEC passes the Maturity Gate;
2. the materialization tree has been produced;
3. the tree passes the skill's internal fidelity and quality gates.

Do not ask the user for an extra acceptance step before producing `/goal`
unless the user explicitly requested staged review or the tree would change the
declared execution contract.

This reference is the router and hardening checklist. The full literal prompt
body lives in `templates/maestral-goal-prompt.template.md`. Load that template
before returning `READY_GOAL_PROMPT`.

## Core Rule

```text
A maestral /goal prompt is an execution contract, not a long request.
```

It must let a future agent execute without inventing artifact, scope,
boundaries, owners, tests, commit rhythm or stop states.

If the source flow created a Super SPEC, the prompt must name the
`GOAL-SUPER-SPEC-<slug-or-timestamp>.md` artifact path as the canonical Super
SPEC reference. Do not embed the full Super SPEC body inside the `/goal`
prompt unless the user explicitly requests a self-contained prompt and accepts
the larger context footprint.

If the source artifact declares a materialization queue, the prompt must
preserve that queue. The prompt is not allowed to compress declared execution
units into fewer execution commits.

A commit message is not execution evidence. The prompt must require material
diff proof, focused oracles, reviewer result, post-commit status and sync
status for every material unit.

## Required Output Shape

The final prompt must include:

1. `/goal` opening line.
2. Mission.
3. Main SPEC path.
4. Super SPEC artifact path when one was created.
5. Certified context.
6. Phase boundary.
7. Central rule.
8. Non-objectives and forbidden moves.
9. Specialized subagents with ownership.
10. Work mode.
11. First mandatory act.
12. `SPEC-000 Preflight And Baseline`.
13. Narrow execution units.
14. Full oracle.
15. Negative grep.
16. Stop criteria.
17. Final delivery contract.
18. Execution unit fidelity statement when the input artifact declares units.
19. Per-unit material-diff and sync-commit evidence requirements.
20. Material continuation rule when prior commits, closeouts or partial
    implementations may exist.
21. Semantic negative-grep rules when blocked-state vocabulary is valid inside
    the contract.
22. Engineering Method Profile and Method Enforcement Packet when the run
    changes code, UI, runtime scripts or generated app artifacts.
23. Optional Next Prompt Handoff clause only when explicitly requested by
    `next_prompt_handoff=true`, `--next-prompt-handoff`, or an equivalent
    direct trigger.
24. Optional Execution Loop boundary only when explicitly requested by
    `--execute-loop`.

## Template Load Contract

Before returning `READY_GOAL_PROMPT`, load
`templates/maestral-goal-prompt.template.md` and verify that the generated
prompt carries the required shape.

The template must carry, when relevant:

- `Execution Loop:`
- Engineering Method Profile
- `STRUCTURAL_METHOD=<profile-id>`
- Structural method result
- Structural handoff
- `bug_vs_architecture`
- failed-attempt residue
- `GOAL-EXECUTION-LOOP-LEDGER`
- strict sequential replay
- reference implementations
- exact `--execute-loop-parent-fallback` flag
- Executive Stop Audit

## Prompt Hardening Checklist

Before returning `READY_GOAL_PROMPT`, verify the prompt:

1. starts from a real SPEC;
2. includes `SPEC-000`;
3. names allowed files per slice;
4. names forbidden moves;
5. assigns ownership;
6. includes per-slice oracles;
7. includes negative grep;
8. requires commit per SPEC;
9. preserves every declared execution unit without silent merge;
10. forbids empty commits as proof of material execution;
11. requires `git show --stat` evidence per material unit;
12. states how prior commits or closeouts are treated when they exist;
13. distinguishes allowed policy vocabulary from forbidden behavior in negative
    grep;
14. requires sync status per unit;
15. preserves unrelated worktree changes;
16. includes reviewer and evidence/oracle roles when complexity warrants them;
17. includes an Engineering Method Profile, `STRUCTURAL_METHOD=<profile-id>`,
    topology budget, structural source probes and structural oracles when code,
    UI or generated app artifacts are in scope;
18. records a structural decision artifact before implementation when topology
    is inferred rather than source-mandated;
19. includes browser metrics and visual-spatial oracle requirements when app,
    UI, game or rendered-canvas work can fail visually or spatially;
20. defines stop criteria;
21. defines final delivery;
22. includes a Next Prompt Handoff clause only when explicitly requested, and
    that clause is chat-only, post-certification, non-executing, and does not
    write prompt/tree files without an explicit save request;
23. includes an Execution Loop boundary only when `--execute-loop` is
    explicitly requested, and that boundary preserves parent authority,
    `ACTIVE_SPEC` isolation, baseline classification, loop-state evidence,
    failed-attempt recovery, persistent ledger triggers, local-only commit
    sync, baseline-only comparison for reference implementations, strict
    sequential replay, bounded repair/audit behavior, explicit parent-fallback
    authorization, `bug_vs_architecture` recovery classification, structural
    decision ledger fields and Executive Stop Audit.

## Stop If Missing

Stop with `NEEDS_SPEC_MATURITY`, `NEEDS_TREE_REPAIR`,
`NEEDS_EXECUTION_UNIT_FIDELITY`, `NEEDS_STRUCTURAL_METHOD` or
`NEEDS_TREE_ACCEPTANCE` when:

1. the canonical artifact is unclear;
2. the execution phase is unclear;
3. forbidden moves are missing;
4. oracles are missing;
5. the materialization tree fails internal gates;
6. the prompt would need to invent file ownership or stop states;
7. the prompt would need to merge or drop declared execution units;
8. code, UI or generated app artifacts are in scope but the prompt lacks an
   Engineering Method Profile, `STRUCTURAL_METHOD=<profile-id>`, topology
   budget, structural source probes, structural negative checks, structural
   oracles or structural handoff requirements;
9. browser, UI, game or rendered-canvas work is in scope but the prompt lacks
   a browser metrics contract or visual-spatial oracle when visual or spatial
   failure is realistic;
10. `templates/maestral-goal-prompt.template.md` was not loaded before prompt
   construction.

Use `NEEDS_TREE_ACCEPTANCE` only when changing the declared execution contract
requires owner acceptance or the user explicitly asked for staged review.

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
16. use broad lexical greps that fail valid blocked-state vocabulary instead of
    targeting forbidden behavior;
17. include Next Prompt Handoff without an explicit parameter/trigger or allow
    it to execute the next prompt automatically;
18. include Execution Loop without explicit `--execute-loop` or let a worker
    execute outside `ACTIVE_SPEC`, push remotely, or bypass Executive Stop
    Audit;
19. let a reference implementation, prior manual build, browser smoke result,
    run record or post-facto audit satisfy `--execute-loop` without strict
    sequential replay;
20. accept a behavior-green implementation that collapsed into a god file,
    duplicated domain logic, bypassed framework topology or misused a
    single-file exception to mix unrelated layers;
21. retry a failed coding SPEC without classifying `bug_vs_architecture` and
    deciding whether the next action is bug repair, `structural_repair`, SPEC
    repair, escalation or stop;
22. generate a next prompt after code changes without structural handoff for
    the active method, changed topology, accepted debt and next-unit
    constraints;
23. certify browser, UI, game, canvas, spawn, raycast, layout or 3D-render work
    from logic-only checks when a visual-spatial failure can still occur;
24. hide certification-time repairs as ordinary closeout instead of bounded,
    committed `audit_repair` evidence.
