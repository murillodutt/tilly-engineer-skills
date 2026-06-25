# Tree Adversary

Use this reference before `READY_GOAL_PROMPT` when `--execute-loop` is requested or when a materialization tree has many material units, browser/runtime risk, shared contracts, quality ceiling language, or inferred topology.

## Core Rule

```text
The author of the tree may not be the only judge of the tree.
```

The Tree Adversary is a read-only pre-execution reviewer. It receives only the anchor artifact, generated tree, relevant source evidence, and declared constraints. It does not receive the tree author's rationale as authority.

## Required Result

Before `READY_GOAL_PROMPT`, the parent must record:

```text
tree_adversary_status=<ADVERSARY_CLEARED|OBJECTIONS_REPAIRED|NEEDS_TREE_ADVERSARY|NEEDS_TREE_REPAIR|NEEDS_OWNER_DECISION>
adversary_objections=<none or compact list>
adversary_repair_evidence=<tree diff summary or owner decision>
```

`READY_GOAL_PROMPT` requires `ADVERSARY_CLEARED` or `OBJECTIONS_REPAIRED`. Stop with `NEEDS_TREE_ADVERSARY` when the adversary pass is required but absent.

## Adversarial Charter

For each unit and final closeout, try to falsify:

1. **Facade oracle:** build/typecheck-only proof for integration, runtime, game-loop, browser, UI, or adapter wiring.
2. **Decorative budget:** topology budget without an executable probe that fails when the budget is exceeded.
3. **Unproven axis:** a declared quality axis covered only by `DEGRADED`, prose, or an escape hatch without a real attempt log.
4. **Ceiling collapse:** anchor-declared ambition routed to future work, Non-Objectives, or simplest-correct output without owner decision.
5. **Shared contract looseness:** later units forced to make fields optional or mutate frozen surfaces because no extension point was declared.
6. **Context handoff loss:** worker envelope depends on parent memory instead of source-derived symbol, oracle, or environment facts.
7. **Unsafe authority:** remote sync, cloud escalation, destructive actions, or parent fallback implied without explicit authorization.

The parent may repair the tree and resubmit. The parent may not self-clear an objection by saying the field exists; the repair must add a stronger oracle, explicit owner decision, executable probe, anchor citation, or stop state.

## Oracle Classification

Every unit with executable behavior must classify its oracles:

```text
oracle_class=<behavioral|structural|build-only|visual-runtime|contract>
oracle_strength=<sufficient|facade|blocked>
```

`build-only` is never sufficient for `unit_role=integration`, browser/runtime certification, or visual-spatial axes. The adversary routes such units to `NEEDS_INTEGRATION_ORACLE`, `VISUAL_CERT_BLOCKED`, or `NEEDS_TREE_REPAIR`.

An oracle is `facade` not only when its proof is build/typecheck-only, but whenever the quantity it MEASURES is a structural proxy for the property it NAMES. A function named for a semantic property (luminance, frame rate, world position, color, distinct-cell count) but whose body measures a structural proxy (`statSync(.size)` bytes, mtime, byte count, path existence) is a facade — it executes at runtime and passes every gate while proving nothing about the named property. Each executable oracle must declare the pair:

```text
PROVEN_PROPERTY=<the semantic property the name promises>
MEASURED_QUANTITY=<the quantity the body actually computes>
```

If `MEASURED_QUANTITY` is a structural proxy that can stay constant while `PROVEN_PROPERTY` is violated, set `oracle_strength=facade` and route to `NEEDS_TREE_REPAIR`. The decisive test is post-execution and belongs to the independent auditor: mutate only the named property (make the frame black, freeze the camera, zero the FPS) and the oracle MUST turn exit≠0. An oracle that stays PASS under the mutation of its own named property is a facade by construction.

## Done

The adversary pass is done when it has either cleared the tree, forced bounded tree repair before prompt emission, or stopped with a precise status that the owner can resolve before execution cost is spent.
