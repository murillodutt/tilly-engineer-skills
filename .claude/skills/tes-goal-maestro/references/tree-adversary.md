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

## Oracle Synthesis On Repair

When the adversary routes a unit to `NEEDS_TREE_REPAIR` because an oracle is missing or `oracle_strength=facade`, it does not stop at "human, write the oracle." For a named property in a known family, the adversary may EMIT a candidate oracle plus its inversion proof, using `scripts/lib/synth.mjs`:

1. `synthMeasure(PROVEN_PROPERTY)` proposes the honest `MEASURED_QUANTITY` (a decode/count/compute quantity, never a structural proxy) and self-validates it through the independent `scripts/oracle-name-measure.mjs` judge; if the judge rejects it, `honest=false`.
2. `synthMutation(family)` + `synthFixture(family, dir)` produce the `{mutate, revert, decoy_mutate}` plan and the `{violate, revert}` fixtures.
3. The synthesized trio is run through `scripts/audit-remutation.mjs` + `scripts/oracle-wiring-check.mjs` in the same pass. The candidate is admitted only if it fires under mutation of its own named property and ignores the decoy — auto-falsification at birth. The proof is the inversion run, not the author's claim.

The repaired unit then carries `oracle_strength=sufficient` with the synthesized oracle and its re-mutation evidence, exactly as a hand-written oracle would.

A property that is NOT in a known family and is NOT explicitly structural returns `honest=false` from `synthMeasure`. The adversary then routes to `NEEDS_HUMAN_ORACLE` — it must NOT invent a structural proxy to fill the gap. `NEEDS_HUMAN_ORACLE` is an honest degrade: the harness can synthesize falsifiable oracles only for the families whose canonical mutation it knows; outside them, a human (or a later synthesis extension) must supply the oracle. Synthesis never replaces a valid in-family oracle a unit already declares.

## Decision Lens Contract

A specialized decision lens (descobribilidade, independent stress, anti-elegance, structural-method) is a tool to BREAK a decision, not to praise it. Measured loop evidence (ADR 0006): lenses that broke a decision paid for themselves; lenses that only confirmed were ~85% theater at ~0.7–1.2× the cost of the product they protected. The lens system is therefore governed by four rules, and the lens panel itself is held to "affirmation is never credit":

1. **Break-mandate (anti-elegance).** A lens MUST declare, before running, the concrete attack it will attempt on the decision. A lens that cannot name an attack is not run. A lens whose output only restates why the author's approach is good produced no value in the loop and is forbidden as a closure artifact — flag it `LENS_THEATER`, do not cite it. (Codifies "estressar de forma independente em vez de apaixonar-se pela própria elegância.")
2. **Discoverability-first.** The first lens on any non-trivial decision is descobribilidade: *can the claim be discovered or derived from the repo, or is it self-attested?* A decision that cannot be discovered cannot be correct, so this lens runs before correctness lenses. A claim that is self-attested with no repo-derivable pointer routes to `NEEDS_DISCOVERABILITY` until it is discovered or explicitly marked `AXIS_UNPROVEN`.
3. **Risk-gating (cost discipline).** Lens depth is gated by the unit's `structural_method_id` / declared risk axis, not applied uniformly. Doc-surface and mechanical-bump classes get no predictive lens; code/harness/installer classes get the full panel. The gate signal already lives in the materialization tree and ledger.
4. **Audit-over-predict bias.** When a defect class is deterministic and checkable by an executable gate, prefer a wired commit-time gate over predictive stress AND over audit-final. Reserve the independent auditor — now a quorum panel (see `references/execution-loop-runner.md` § Quorum Audit) — for re-mutation and facade-hunting, where it out-yielded stress. Predictive stress is for genuinely open design questions, not for what a gate or an auditor catches better.

The unifying contract: discover first → attack to break (never confirm) → gate by risk → generate the proof and submit it to your own falsifier → wire deterministic checks, panel-audit the rest.

## Done

The adversary pass is done when it has either cleared the tree, forced bounded tree repair before prompt emission, or stopped with a precise status that the owner can resolve before execution cost is spent.
