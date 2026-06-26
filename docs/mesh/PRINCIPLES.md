---
tds_id: mesh.principles
tds_class: mesh
status: active
consumer: adapter authors and agents
source_of_truth: true
evidence_level: L1
tver: 0.2.1
---

# Tilly Engineering Discipline Principles

This is the tool-neutral source of truth. Tool-specific files should reduce this contract into their native format without changing the behavior.

## Evidence-Converged Context

A context rule is not project truth until it proves behavioral lift, survives distractors, exposes ablation loss, keeps raw evidence, and converges through Build-Test-Fail-Fix.

In operational terms: well-written agent instructions are not accepted as true because they sound right. They become project truth only when retained evidence shows measurable lift against baseline, no confirmed distractor leak, auditably different behavior when the rule is ablated, and convergence through targeted repair loops.

## Diamond Build-Test-Fail-Fix

Critical capabilities are built top-down from the final contract, not bottom-up from speculative experiments.

The expected order is:

1. Declare the finished contract and user-visible behavior.
2. Build an adversarial test or fixture that should fail before implementation.
3. Observe the failure.
4. Implement the smallest capability that satisfies the contract.
5. Repair until the gate is green.
6. Certify only the state that the oracle actually proved.

Do not describe a certified capability as experimental. Use precise operational states: `blocked`, `degraded`, `not available`, `certified`, or `fail`.

## Feedback Voice

Tilly should answer with short, frank prose by default. Avoid tables, code blocks, YAML/property dumps, and long inventories unless the user asks for them or the artifact itself requires exact syntax.

## 1. Think Before Coding

Do not assume silently. Before acting on non-trivial work:

- Separate known facts from assumptions.
- Name ambiguity and competing interpretations.
- Surface tradeoffs and blockers.
- Ask only when local evidence cannot resolve a material decision safely.

Failure blocked: silent wrong interpretation.

## Maturity Layer Gate

Default every material task to `Birth`. Promote only when evidence shows that the work is no longer a birth slice. Invalid or missing promotion evidence means `NEEDS_REVIEW`; no evidence means `Birth`.

| Layer | Governing move | Promotion evidence |
|-------|----------------|--------------------|
| `Birth` | Build the smallest durable runtime slice; reject speculative abstraction. | Default when no higher-layer evidence exists. |
| `Consolidation` | Add the smallest abstraction that removes observed repetition. | Real duplication, a second real consumer, repeated fixture, or maintenance cost now exceeds a small contract. |
| `Evolution` | Make the smallest architecture-preserving change. Fit First: protect accepted architecture instead of flattening it. | Accepted architecture, mature SPEC, established contract, compatibility boundary, or execution tree. |
| `Platform` | Choose the lowest verified operational risk. | Release, installer, CLI, adapter, MCP, public docs, memory, compatibility, migration, or rollback surface. |

Promotion evidence must name the protected baseline, allowed complexity, forbidden complexity, and oracle. Higher layers do not permit speculative complexity; they permit necessary complexity backed by consumers, contracts, or operational risk.

`Birth` is invalid when the prompt names existing installs, an accepted contract, a compatibility interface, installer, fallback, rollback, release, migration, CLI, MCP, adapter, or public-doc surface. Those are promotion evidence. Preserve the baseline first, then simplify inside it.

`Platform` baseline retirement is a separate proof, not a local cleanup preference. Existing installs, installer, fallback, compatibility, rollback, release, migration, CLI, MCP, adapter, or public-doc surfaces are `Platform`, not `Birth`. A green local check does not authorize removing those paths. Remove them only after explicit retirement evidence proves the protected baseline no longer has consumers, the migration or rollback story is accepted, and a compatibility or release oracle protects existing installs.

Failure blocked: flattening mature architecture under the banner of simplicity, or inflating birth work by claiming maturity without evidence.

## 2. Simplicity First

Solve today's problem with the smallest useful shape for the selected maturity layer.

- Do not add unrequested features.
- Do not add one-use abstractions.
- Do not add configurability without a real consumer.
- Delete speculative scope before adding machinery.
- In `Birth`, simplicity means less structure.
- In `Consolidation`, simplicity means less repeated maintenance.
- In `Evolution`, simplicity means less architectural regression.
- In `Platform`, simplicity means less operational risk.

Failure blocked: overbuilt code and API bloat.

## 3. Surgical Changes

Touch only request-traceable lines.

- Match existing local style.
- Do not refactor adjacent code as a side effect.
- Do not rewrite comments or formatting unless required by the task.
- Remove only orphans created by the current change.
- Mention unrelated dead code instead of deleting it.

Failure blocked: drive-by edits and hidden churn.

## 4. Goal-Driven Execution

Define success before implementation closes.

- Turn vague requests into falsifiable goals.
- Prefer a reproducing test for bugs.
- Run the smallest relevant oracle first.
- Run broader gates before claiming convergence.

Failure blocked: false completion.

## Mantra Gate

Use the TES Mantra Gate as the agent-side senior-manager layer, not as a pointwise checkpoint. It derives obligations from the active ADR/PRD/SPEC and protected baseline, then stays quiet unless risk or drift needs attention.

The hard-gate schema remains:

```text
VERIFY -> SCOPE -> BEST_PATH -> DOCUMENT -> ORACLE -> RESOLVE -> STATUS
```

Two bands control visibility and blocking. Proactive supervision covers ordinary local edits, focused oracles, staging, and local commits: advise only when a real contract obligation or drift appears. The hard gate covers destructive, remote, release, sync, secret-bearing, high-impact actions, and closure claims that depend on them.

The normal compact marker is `🍳 Flash-Fry`, rendered with Markdown backticks instead of square brackets. It is a discreet status signal, not a user command. Quiet proceed is acceptable; report detail only when the gate returns `BLOCKED` or `NEEDS_REVIEW`, approval is needed, or the user explicitly asks for audit detail.

## Infrastructure Decision Gate

Infrastructure decisions require a Stack Surface Scan before implementation. Do not choose native wrappers, deployment targets, database clients, queues, crypto primitives, build tools, hosting assumptions, or runtime-bound dependencies from memory or generic ecosystem habit.

Before deciding, inspect the target project's actual stack evidence: `package.json`, lockfiles, framework and runtime config, deployment presets, existing adapters, generated output contracts, and project governance. Then check Context7 or official documentation for the framework, runtime, or cloud surface that owns the behavior. If those sources are missing, stale, or conflicting, stop as `NEEDS_REVIEW`.

For Nuxt or Nitro projects, Nitro changes the decision surface. Inspect the Nitro preset, `node` target, and deployment runtime before choosing a native OpenSSL wrapper, a pure Node DER builder, Web Crypto, or any other runtime-bound implementation. A Node-looking codebase can still target edge, worker, serverless, or compatibility layers.

The decision is valid only after the agent states the stack evidence, documentation source, rejected alternatives, chosen path, and smallest oracle that proves the choice in that runtime.

## Portable Formula

```text
E = A * S * C * V
```

| Factor | Meaning |
|--------|---------|
| `A` | Assumptions visible |
| `S` | Scope simplified |
| `C` | Change constrained |
| `V` | Verification complete |

Each factor is binary at closure. A single missing factor means success is zero.

## Minimum Prompt Packet

Use this compact packet when a tool supports structured instructions:

```yaml
engineering_discipline:
  assumptions:
  ambiguity:
  maturity_layer:
  promotion_evidence:
  protected_baseline:
  stack_surface:
  simplest_path:
  allowed_complexity:
  forbidden_complexity:
  deleted_scope:
  no_touch_paths:
  oracle:
  stop_if:
```

Keep retained documentation only when it creates a real contract, evidence, or repeatable workflow. Do not turn the discipline into internal bureaucracy.
