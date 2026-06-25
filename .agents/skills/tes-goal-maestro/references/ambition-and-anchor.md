# Ambition And Anchor

Use this reference before accepting a materialization tree from a mature input artifact. It owns the admission gate, quality ceiling capture, and shared contract extension rules.

## Anchor Artifact Gate

Goal Maestro must not let the generated tree become its own source of truth. A run that emits `READY_GOAL_PROMPT` must cite a persisted anchor artifact that is distinct from the generated tree:

```text
anchor_class=<PRD|ADR|Super-SPEC|SPEC|relational-project-plan|accepted-execution-tree>
anchor_path=<path>
anchor_hash=<hash captured before tree generation>
anchor_origin=<provided|materialized-from-anchor|previous-session>
anchor_source=<path or not_applicable>
```

Accepted anchor classes are the invocation-contract classes only when they are persisted and citeable. A Super SPEC generated during the same run may formalize a PRD or ADR, but it cannot authorize itself. A generated Super SPEC is a valid anchor only when it was materialized in a prior session or is derived from an already cited PRD or ADR in the same run.

Stop with `NEEDS_ANCHOR_ARTIFACT` when no persisted anchor can be cited, when the anchor is the generated tree itself, or when the hash cannot be captured. Use `NEEDS_SPEC_MATURITY` instead when the problem is missing semantic maturity rather than missing persistence.

## Quality Ceiling Gate

When an anchor declares a quality or ambition directive, treat it as contract, not motivational prose.

The tree must capture:

```text
ambition_directive=<quoted source text or ABSENT>
quality_ceiling=<required ceiling features, axis, or ABSENT>
ceiling_decision=<oracled_now|owner_deferred|not_applicable>
```

If `ambition_directive` is present, the Central Rule must say that simplest-correct behavior is the floor, not the target. Deferring a ceiling feature to "future work" requires `NEEDS_OWNER_DECISION` or a cited owner deferral; it cannot hide inside `Non-Objectives`.

Stop with `NEEDS_AMBITION_RECONCILIATION` when the anchor names a ceiling but the tree lowers it to a minimum viable path without an oracle, explicit owner decision, or bounded phase reason.

## Shared Contracts

When two or more units read or write the same named type, schema, runtime surface, fixture helper, or command contract, the tree must include a Shared Contracts section.

Each shared contract entry must name:

```text
contract_name:
declared_in:
frozen_surface:
extension_points:
extenders:
optionality_rule:
declaring_oracles:
extension_oracles:
```

A later unit may write an upstream contract file only when the tree marks that file as `extension-only`, the declaring unit reserved the extension point, the write does not mutate the frozen surface, and the declaring oracles rerun green. If no extension point exists, stop with `NEEDS_CONTRACT_EXTENSION_POINT` instead of silently making the new field optional.

## Done

This reference is satisfied when the tree cites a persisted non-self anchor, captures any declared quality ceiling, names shared contracts that cross unit boundaries, and routes missing anchor, ceiling, or extension evidence to the specific stop state before `READY_GOAL_PROMPT`.
