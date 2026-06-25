# Structural Method

Use this reference when a materialization tree, prompt, `ACTIVE_SPEC` or loop touches code, UI, runtime scripts or generated app artifacts.

Core rule:

```text
A SPEC only passes when behavior converges without structural degradation.
```

The Structural Method Gate is method, not governance. It turns stack evidence into operational constraints for the worker and parent reviewer.

## Engineering Method Profile

Derive the Engineering Method Profile from material sources, never from memory:

1. language and framework family;
2. current file topology and ownership boundaries;
3. existing helper APIs, module patterns and build/test commands;
4. source-mandated topology exceptions;
5. known structural debt and prohibited growth direction;
6. structural oracles available in the repo.

If the run cannot derive enough stack or topology evidence, stop with `NEEDS_STRUCTURAL_METHOD`.

## Structural Decision Gate

When code, UI, runtime-script or generated-app work has no source-mandated topology, decide the topology before the first material implementation commit. Record the decision in the material tree, ledger or a small ADR-like artifact.

Minimum fields:

```text
topology_decision=<multi-file static project|framework components|module split|internal sections|single-file exception|other>
topology_exception=<none|source-mandated exception with reason>
rationale=<source evidence, not memory>
topology_budget=<files/modules/sections/line-growth limit>
structural_oracles=<source probes and runtime probes>
```

If the source mandates a topology exception, mark it as an LLM execution decision, prove it from source text, and keep the exception bounded. If the worker chooses a single-file exception without source support, stop with `NEEDS_STRUCTURAL_METHOD`.

## Method Enforcement Packet

Every coding or app-building execution unit must carry a compact packet:

```text
STRUCTURAL_METHOD=<profile-id>
stack=<language/framework/runtime>
topology_decision=<chosen topology or not_applicable>
topology_decision_artifact=<tree|ledger|ADR path|chat block>
topology_budget=<files/modules/sections/line-growth limit>
topology_probe=<command that fails when the budget is exceeded>
topology_exemptions=<paths with source-proven reason or none>
allowed_modules_or_internal_sections=<paths or names>
forbidden_layer_moves=<UI/domain/storage/runtime/docs/adapter boundaries>
structural_debt_budget=<none|accepted debt|owner decision>
structural_source_probes=<commands or inspections>
structural_negative_checks=<god file, duplication, layer mixing, topology bypass>
structural_oracles=<lint/typecheck/build/render/source probes>
ambition_floor=<none or anchor-declared ceiling features this unit must reach>
shared_contract_surface=<frozen fields, extension points, optionality rule or none>
```

For single-file deliverables, the exception is valid only when the source contract requires it. A single-file exception still needs internal modularity, named sections, narrow APIs, section anchors, and no duplicated logic.

## Topology Budget

The topology budget must say how much structure may change:

- allowed files, modules, components, composables, stores, services, adapters, scripts or internal sections;
- maximum acceptable file growth or explicit source-proven exception;
- forbidden new dependencies or boundary crossings;
- required split when a file is already near the budget;
- allowed module creation before adding behavior.

The worker must not use a behavior-green result to justify an unbounded god file, framework-topology bypass, duplicated domain logic or mixed unrelated layers.

A numerical line, file, module or section budget must become an executable probe that returns non-zero when the budget is exceeded. A probe that only prints counts is inventory, not enforcement.

Acceptable exceptions must be source-proven before implementation and named in `topology_exemptions`. Orchestration-only and data-catalog exceptions must have negative checks that prove they did not absorb unrelated domain logic. Domain logic files that exceed the budget require split, explicit accepted debt, or `NEEDS_STRUCTURAL_METHOD`.

## Structural Source Probes

Use probes that match the stack:

- line counts and section inventories;
- executable budget assertions, such as line-count or module-count commands that fail on excess;
- module/component/composable/service/store inventory;
- import and dependency-boundary checks;
- duplicate-symbol or duplicate-logic scans;
- inline CSS/JS scans when separation is expected;
- generated output or rendered UI smoke when visual structure matters;
- framework-specific build, lint, typecheck or route probes.

The prompt must name probes before editing. The closeout must report `topology_probe=PASS|FAIL` and the command result, not merely say the structure is fine.

## Failed Attempt Recovery

Before retrying failed coding work, classify `bug_vs_architecture`:

- `behavior_bug`: behavior failed but topology remains valid;
- `test_oracle_bug`: the test/oracle is wrong or incomplete;
- `structural_repair`: behavior may pass or nearly pass, but architecture collapsed, exceeded budget, duplicated logic or mixed layers;
- `SPEC_REPAIR_BY_LLM`: the active SPEC itself forced bad architecture;
- `NEEDS_OWNER_DECISION`: safe correction needs owner direction.

Do not start the next attempt while failed-attempt residue is unresolved. The parent must commit valid material, revert only isolated current-attempt residue after diff review, repair the canonical SPEC artifact, or stop.

## Structural Handoff

Every coding unit that another unit may build on must provide structural handoff:

1. active `STRUCTURAL_METHOD=<profile-id>`;
2. files, modules or internal sections created or changed;
3. boundaries preserved;
4. accepted structural debt;
5. next-unit constraints;
6. structural source probes and oracles run;
7. shared contract surface: frozen fields, open extension points and optionality rule when a later unit may extend the same type or API.

Next Prompt Handoff and `--execute-loop` prompts must carry this structural handoff when code, UI, runtime scripts or generated app artifacts changed.

## Loop Ledger Fields

When `--execute-loop` is active and code structure is in scope, each loop-state entry must include:

```text
structural_method_id:
topology_decision:
topology_decision_artifact:
structural_debt:
next_structural_constraint:
failed_attempt_recovery_decision:
topology_probe_result:
shared_contract_surface:
```

Long, repaired, audit-expanded or resumed loops must persist these fields in `GOAL-EXECUTION-LOOP-LEDGER-<slug-or-timestamp>.md`.

## Audit Repair

If behavior passes but structure regresses, the parent must stop with `NEEDS_STRUCTURAL_METHOD` or append bounded `SPEC-AUDIT-STRUCTURE-*` repair units during `--execute-loop`.

Repeated audit repair without new material evidence becomes `NEEDS_OWNER_DECISION` or `SPEC_CONTRACT_UNSTABLE`.

## Stop If Missing

Stop when any coding or app-building unit lacks:

- Engineering Method Profile;
- Method Enforcement Packet;
- `STRUCTURAL_METHOD=<profile-id>`;
- topology budget;
- executable topology probe or source-proven exception;
- allowed modules/internal sections;
- structural debt budget;
- structural source probes;
- structural handoff requirement;
- `bug_vs_architecture` recovery path;
- `structural_repair` decision path;
- single-file exception rule when applicable.
