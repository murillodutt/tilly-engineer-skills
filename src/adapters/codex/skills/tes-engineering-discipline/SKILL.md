---
name: tes-engineering-discipline
description: Apply a maturity-aware engineering discipline to non-trivial coding, review, refactor, or instruction-migration work so assumptions are explicit, maturity is evidenced, scope stays small, diffs remain surgical, and success is verified by a concrete oracle.
---

# Tilly Engineering Discipline

Operational contract:

```text
Assumptions visible. Scope smaller. Edits surgical. Success falsifiable.
```

Use this skill for non-trivial coding, review, refactor, debugging, migration, or agent-instruction work when explicitly invoked or when bootloader/project rules call for deeper discipline. Skip the full ceremony for obvious one-line fixes, and honor an owner-requested no-skill run unless destructive, remote, secret, release, or safety risk requires escalation.

## Gate Zero — Declared-Contract Arbiter

The arbiter runs FIRST, before the five gates, whenever the gates tension — Simplicity-First or Surgical-Changes pulling one way and a contract already in the repo pulling the other. It answers exactly one binary question:

```text
Does the minimal solution silently violate a contract already DECLARED and
ENUMERABLE in this repo?
```

The question is yes/no with exactly one answer, in the spirit of `tes-mine`: it works because it is hard and accepts no questioning. `YES` requires a NAMED declared fact on the table; anything that is not `YES` is `NO`. Gradation — "partially declared", "sort of a peer-convergence", "mostly violated" — is forbidden; it is the entry door of ambiguity. This mirrors the oracle grammar: `maturity_layer` resolves to exactly one enum value or fails, `is_generic` returns `True`/`False`, `selected_layer` returns one layer or `None`. The `declared_contract` state resolves to exactly one of `YES`/`NO` or fails as `NEEDS_REVIEW` — never "partial".

A declared contract is one an oracle could name from source WITHOUT running it. There are exactly four types:

1. **Frozen-schema cardinality** — a frozen schema's field-cardinality invariant (`strictObject`, `.optional()`). A transform that drops a declared field violates it.
2. **Closed-domain coverage** — a union or enum of known size `N` reachable on the path, AND an acceptance line saying "all `N`", with the implementation capped below `N`.
3. **Peer-convergence** — a structural pattern used by a countable majority of in-repo sibling units of the same class, with the unit under change the lone deviation.
4. **Affordance-deliverable** — a user-facing control whose label is verb+noun naming a concrete artifact that must cross the app boundary.

Decision is three-way:

- **Override-and-bind-oracle.** If `YES` and the contract is satisfiable in scope, the broad default (Simplicity-First / Surgical-Changes) is OVERRIDDEN and the closure oracle MUST bind to the declared contract.
- **Escalate-collision.** If `YES` but satisfying it would breach a SECOND declared boundary — a frozen surface, a SPEC stop-state — you MUST NOT pick the broad default silently. NAME the collision to the user as an escalated trade-off. Resolving a collision silently is itself a failure the discipline oracle's plan check is meant to surface.
- **Broad-default-wins.** If `NO` declared contract is violated, Simplicity-First and Surgical-Changes WIN unchanged. Undeclared aspirations — craft, polish, "could be nicer" — do NOT trigger the override.

When the override fires, the obligation is per-line rigor, not more lines: route to the Effort Gate and promote the effort tier to `Premium` (see Effort Gate). Premium authorizes a heavier oracle bound to the declared contract; it never authorizes a new abstraction, strategy interface, or config knob to "cover" the contract.

Worked example (override). Request: "Persist the designer draft by round-tripping it through `JSON.parse(JSON.stringify(draft))` before save — it's the smallest serialization and the snapshot looks identical." A frozen `strictObject` with `.optional()` fields is on the path, and a JSON round-trip silently drops keys whose value is `undefined`. Verdict: `declared_contract = YES`, type frozen-schema cardinality. The broad default (smallest serialization) is OVERRIDDEN; the closure oracle MUST bind to the frozen schema — a structural clone that preserves declared-optional fields, with a test that asserts an `undefined`-valued optional field survives the round-trip. Effort tier promotes to `Premium` (heavier oracle, same scope). Do not add a serializer abstraction; repair the one path.

Worked example (collision). Request: "Wire the 'Exportar PDF' button to deliver the file; the export module boundary is frozen and exposes no byte path, so just have the handler resolve and toast success." Two declared contracts collide: an affordance-deliverable invariant (a control labeled verb+noun — "Exportar PDF" — promising a delivered artifact across the app boundary) and a frozen module boundary that exposes no byte path to deliver it. Verdict: `declared_contract = YES` on the affordance, but satisfying it breaches the frozen boundary. You MUST NOT silently ship the toast-only handler (the affordance lies) and MUST NOT silently widen the frozen boundary (the surface lies). NAME the collision as an escalated trade-off: stopping at the frozen boundary is correct; the failure is not escalating the deliverable-vs-boundary collision to the user. Resolve only after the user picks which boundary moves.

## Core Gates

Gate Zero is the Declared-Contract Arbiter; it runs before the six gates and owns every collision between them. The table below lists Gate Zero plus the six gates it arbitrates.

| Gate | Rule | Failure Blocked |
|------|------|-----------------|
| Declared-Contract Arbiter (Gate Zero) | Before closing any tensioned change, answer one binary question — does the minimal solution silently violate a contract already declared and source-nameable in this repo? Resolve collisions here, never inside another gate | Silent contract breach and silent collision resolution |
| Think Before Coding | Name facts, assumptions, ambiguity, tradeoffs, and blockers before acting | Silent wrong interpretation |
| Maturity Layer Gate | Default to `Birth`; promote only with evidence naming baseline, allowed complexity, forbidden complexity, and oracle | Flattening mature architecture or inflating birth work |
| Simplicity First | Delete speculative scope before adding machinery for the selected maturity layer | Overbuilt code and API bloat |
| Surgical Changes | Touch only request-traceable lines and self-created orphans | Drive-by edits and style churn |
| Goal-Driven Execution | Define and run a falsifiable oracle before closure; when the oracle is a broad closure gate, also name the red-capable proof for the behavior changed | False completion |
| Effort Gate | Default to `Standard`; promote to `Premium` only when the Declared-Contract Arbiter or named consequence evidence obligates deeper rigor per line, never more lines | Under-rigor on declared-contract lines and invented rigor on undeclared ones |

Scope gates: Maturity Layer, Simplicity First, Surgical Changes. Craft gates: Think Before Coding, Goal-Driven Execution, Effort Gate. The two axes are orthogonal: scope decides how many lines exist; effort decides how much rigor each line carries. Neither gate may move the other axis.

The Declared-Contract Arbiter (Gate Zero) runs FIRST, before all six gates: when the gates tension, it can override the broad default, force a collision escalation, or leave Simplicity-First and Surgical-Changes untouched.

## Maturity Layer Gate

Maturity is classificatory, not a phase of execution. The layer is decided during thinking — which converges before the first line — and the artifact is born at the layer the thinking settled on. There is no "execute `Birth`, then promote and re-execute": a `Platform` change is `Platform` from its first line, a `Birth` change is `Birth` from its first line. Nobody builds a simple house to demolish it into a palace; the simple phase is the THINKING, and it ends before the first beam. Promotion is reclassification of the work, never a rebuild of shipped lines. (Protecting an existing `Platform` baseline is not a rebuild — it is correctly classifying that the work was `Platform` all along.)

Classify material work before applying `Simplicity First`:

| Layer | Use When | Simplicity Means |
|-------|----------|------------------|
| `Birth` | No higher-layer evidence exists | Less structure; the smallest slice in SCOPE, built at full craft — never an executable draft to be redone |
| `Consolidation` | Real duplication, a second real consumer, repeated fixture, or maintenance cost justifies a small contract | Less repeated maintenance |
| `Evolution` | Accepted architecture, mature SPEC, established contract, compatibility boundary, or execution tree exists | Less architectural regression; Fit First |
| `Platform` | Release, installer, CLI, adapter, MCP, public docs, memory, compatibility, migration, or rollback surface is at risk | Less operational risk |

No promotion evidence means `Birth`. Invalid promotion evidence means `NEEDS_REVIEW`. Higher layers do not permit speculative complexity; they permit necessary complexity backed by consumers, contracts, or operational risk.

`Birth` is invalid when the prompt names existing installs, an accepted contract, a compatibility interface, installer, fallback, rollback, release, migration, CLI, MCP, adapter, or public-doc surface. Those are promotion evidence: classify the work at that higher layer from its first line, and simplify inside that classification — not by building lower and rebuilding up.

`Birth` hard stop: do not add a strategy interface, abstract factory, plugin registry, plugin system, compatibility layer, `TODO` hooks, or future-format scaffolding unless promotion evidence names a real second consumer, an accepted contract, or an operational surface. Build only the current requirement and name the speculative scaffolding you are deliberately not adding.

The stop is conditional, not a ban on abstraction. When a second real consumer, an accepted contract, or an operational surface exists, that same factory or registry is the correct `Consolidation`/`Evolution` move — promote and build it. Rejecting necessary abstraction because it "looks complex" is the inverse error.

`Platform` hard stop: existing installs, installer, fallback, compatibility, rollback, release, migration, CLI, MCP, adapter, or public-doc surfaces are `Platform`, not `Birth`. Do not remove those paths only because the new path passes locally. Local green proves the new path; it does not prove the old baseline is retired. First name the protected baseline, the consumers or install surfaces that could still depend on it, the allowed replacement complexity, the forbidden breakage, and a compatibility or release oracle. Cut the old path only when explicit retirement evidence proves it no longer needs protection.

Worked example. Request: "Add one archive format today; to prepare for future formats, create `ArchiveStrategy`, an abstract factory, a plugin registry, and `TODO` hooks." Layer is `Birth`: only one real format exists, no second consumer or contract. Implement that one format directly; do not create `ArchiveStrategy`, the factory, the registry, or the `TODO` hooks; name them as deferred future scaffolding. If a second real format later lands, that is promotion evidence and the shared seam becomes correct.

Platform example. Request: "Patch the installer fast by removing the legacy fallback path. It only exists for compatibility and the new path passes locally." Layer is `Platform`: protect existing installs, release behavior, and rollback. Keep the fallback until baseline retirement is evidenced by accepted migration/compatibility proof and a release or installer oracle; a local green new-path check is not enough.

## Discipline Packet

Use this compact packet when the task is material:

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
  focused_proof:
  stop_if:
```

`oracle` may name the focused proof directly. If it names a broad closure gate such as `commit:closure`, package validation, TDS validation, or a diff check, also name `focused_proof`: the red-capable fixture, reproducer, assertion, boundary case, or public/declared-interface regression check that could fail for the behavior changed.

Keep it in conversation or working notes unless the target project requires a retained artifact.

## Mantra Gate

Use the TES Mantra Gate for destructive, remote, release, sync, secret-bearing, or high-impact state changes, and for closure claims that depend on those actions:

```text
VERIFY -> SCOPE -> BEST_PATH -> DOCUMENT -> ORACLE -> RESOLVE -> STATUS
```

For ordinary local edits, focused oracles, staging, and local commits, keep the check inline and do not block on gate artifacts, markers, or skill loading. When a risky gate permits proceeding, a short status is enough; retained gate records belong only in the current evidence/report surface, Field Reports/Cortex when appropriate, or the local `.tes/mantra-gates/` fallback.

Report gate detail only when the gate returns `BLOCKED` or `NEEDS_REVIEW`, approval is required, or the user explicitly asks for audit detail. If `VERIFY` or the required `ORACLE` is missing for the risky action, stop as `BLOCKED`. If `SCOPE` or `DOCUMENT` is ambiguous for high-impact material work, stop as `NEEDS_REVIEW`.

## Infrastructure Decision Gate

Before any infrastructure decision, run a Stack Surface Scan. This applies to native wrappers, deployment targets, database clients, queues, crypto primitives, build tools, hosting assumptions, and runtime-bound dependencies.

Inspect the target project's actual stack evidence before choosing: package and lock files, framework config, runtime config, deployment preset, existing adapters, generated output contracts, and project governance. Then check Context7 or official documentation for the framework, runtime, or cloud surface that owns the behavior. If evidence is missing, stale, or contradictory, stop as `NEEDS_REVIEW` instead of guessing.

For Nuxt or Nitro projects, Nitro changes the runtime surface. Inspect the Nitro preset, `node` target, and deployment runtime before choosing a native OpenSSL wrapper, a pure Node DER builder, Web Crypto, or another runtime-bound implementation. A Node-looking repository can still target edge, worker, serverless, or compatibility layers.

The decision must name the stack evidence, documentation source, rejected alternatives, chosen path, and smallest runtime oracle before implementation.

## Effort Gate

The Effort Gate is an elevation axis, not a barrier, and it is orthogonal to scope. It sets how much rigor each line carries, never how many lines exist. Default material work to `Standard`. Promote only with evidence:

| Tier | When | Authorizes |
|------|------|------------|
| `Standard` | No declared-contract or named-consequence evidence obligates deeper rigor | The high-craft project baseline: lint, typecheck, test, surgical diff — already premium-grade, not a mediocrity ceiling |
| `Premium` | The plan NAMES one of two declared, binary-hard triggers: a `declared_contract` resolving to one of the four arbiter types (frozen-schema cardinality, closed-domain coverage, peer-convergence, affordance-deliverable), OR a `named_consequence_surface` resolving to one named surface (a credit-decision threshold, a ledger row, an auth/session issuance, an irreversible migration, a PII export across the app boundary). Both are declared facts, not words found in prose; neither outranks the other. A surface that resolves to no known member fails as `NEEDS_REVIEW` (the curation signal — the enum grows by governance, not by prose). With neither trigger named, `Premium` fails as `NEEDS_REVIEW` | More adversarial cases, a heavier named oracle class, mandatory upstream/Context7 verification, adversarial-first Diamond execution — all on the existing lines |

Promote only when the Declared-Contract Arbiter answers YES or named consequence evidence is on the table. The trigger is always a source-nameable fact — a declared contract an oracle could name, or a named consequence surface — never an adjective. "Could be more thorough", "feels important", "deserves polish" are not `Premium` triggers; they are undeclared aspirations and they leave the tier at `Standard`. Invalid promotion evidence means `NEEDS_REVIEW`; no evidence means `Standard`. The tier resolves to exactly one of `Standard` or `Premium` or fails as `NEEDS_REVIEW`; "partially Premium" is not a state.

Scope isolation (absolute): `Premium` authorizes more rigor per line, never more lines, abstractions, or features. A `Premium` plan that adds a strategy interface, an abstract factory, a config knob, or any new seam is a `Birth` hard stop violation dressed as thoroughness — the Effort Gate cannot buy a scope promotion. Both `Birth` + `Premium` and `Platform` + `Standard` are legal and expressible: a one-line fix on a frozen schema is `Birth` scope at `Premium` craft; a multi-surface release with no declared-contract tension can be `Platform` scope at `Standard` craft.

When two declared contracts collide on the same line (an affordance-deliverable that must ship versus a frozen boundary it would breach), the Effort Gate does not resolve it — the Declared-Contract Arbiter does, and the correct move is to escalate the conflict, never to silently stop or silently breach.

Worked example — minimal scope plus `Premium` craft. Request: "Flip the credit approval threshold from 0.70 to 0.75." Scope is `Birth`: one declared constant changes, no new consumer or contract. None of the four arbiter contract types is on the path, so this promotes on the OTHER declared trigger: a `named_consequence_surface` of `credit-decision-threshold` is named — so effort promotes to `Premium`. Correct `Premium` response on the same one-line diff: a failing boundary fixture at 0.74/0.75/0.76 that proves the new cut, a contract oracle binding the decision path to the declared value, and rollback reasoning for the flip. Adding a `ThresholdStrategy` class, a thresholds config map, or a pluggable policy seam is not `Premium` craft — it is a `Birth` hard stop violation dressed as thoroughness. Premium deepens the proof on the line that changed; it never grows the line count.

Worked example — `Premium` not required. Request: "Change a debug log string in a throwaway script from 'starting' to 'starting run'." No declared contract is on the path: no frozen schema, no closed-domain coverage line, no peer pattern, no affordance deliverable, no money/auth/ledger surface. The Declared-Contract Arbiter answers NO, so the tier stays `Standard` and the standard baseline closes it. Inventing `Premium` rigor here — an adversarial fixture suite, a mandated upstream check, a Diamond cycle — is the inverted bug: rigor spent where no declared contract obligates it is wasted scope-of-effort, the mirror of under-rigor on a contract line.

## Diamond Build-Test-Fail-Fix

For critical capabilities, build from the finished contract down:

1. State the final behavior.
2. Create or identify the adversarial fixture that should fail first.
3. Observe the failure.
4. Implement the smallest repair.
5. Run the gate again until it passes.

Do not call certified behavior experimental. Use `blocked`, `degraded`, `not available`, `certified`, or `fail`.

## Workflow

1. Classify the task.
   - If authority, irreversible risk, external surface, or secret handling is unclear, stop and ask.
   - If the task is clear and bounded, continue.
2. Make assumptions visible.
   - Resolve safe ambiguity locally.
   - Ask only when the answer changes scope, authorization, or risk.
3. Select the maturity layer.
   - Default to `Birth`.
   - Promote only with protected baseline, allowed complexity, forbidden complexity, and oracle.
   - Use Fit First in `Evolution`: preserve accepted architecture instead of flattening it for local minimalism.
   - In `Platform`, preserve fallback, compatibility, release, installer, migration, and rollback baselines until retirement evidence and a compatibility or release oracle prove they can be removed.
4. Delete scope.
   - Remove unrequested features, future-proofing, one-use abstractions, and optional configuration.
   - In higher layers, delete accidental complexity but preserve necessary complexity backed by consumers, contracts, or operational risk.
5. Keep edits surgical.
   - Match local style.
   - Avoid unrelated formatting, comments, or refactors.
   - Remove only orphans created by this change.
6. Verify.
   - For bugs, reproduce the failure first when practical.
   - Run the smallest relevant oracle first.
   - Run broader project gates before claiming convergence.
7. Reflect for Cortex when present.
   - If `docs/agents/cortex/CONTRACT.md` exists and the work changed durable decisions, contracts, commands, architecture, evidence, or recurring lessons, call `cortex_reflect` through MCP or run `python3 .tes/bin/cortex.py reflect --target . "<decision or lesson>"`.
   - Treat the result as a proposal. Do not write Cortex cells without explicit user authorization.
   - If the result has `curation_due=true`, call `cortex_curate_plan` through MCP or run `python3 .tes/bin/cortex.py curate-plan --target . --backend lexical` before proposing any merge, split, compaction, or rejection.
8. Respect Field Reports when present.
   - Field Reports is active by default, sanitized, and drained by the local pre-push hook.
   - If the user asks to disable, enable, check, or drain it, run the matching `field_reports.py` oracle without expanding collection levels or schema.
9. Keep feedback grounded for people.
   - Prefer short, frank prose.
   - Avoid tables, code blocks, YAML/property dumps, and long inventories unless the user asks or the artifact requires exact syntax.

## Module Map

| Need | Load |
|------|------|
| Mantra Gate helper | `.tes/bin/mantra_gate.py --self-test` when installed, or `scripts/mantra_gate.py --self-test` in the package source |
| Mantra Gate adoption health | `.tes/bin/mantra_gate_adoption_oracle.py --target .` when installed, or `scripts/mantra_gate_adoption_oracle.py --target .` in the package source |
| Common failure patterns | `references/failure-patterns.md` |
| Port this discipline across tools | `references/source-portability.md` |
| Deterministic self-test or plan check | `scripts/discipline_oracle.py` |

Do not bulk-load references unless the task needs them.

## Success Formula

```text
E = A * S * C * V
```

Each factor is binary at closure:

- `A`: assumptions visible
- `S`: scope simplified
- `C`: change constrained
- `V`: verification complete

If any factor is missing, success is zero and the work must stop or be repaired.

## TES Memory Lifecycle Boundary

When Cortex is the durable memory surface, keep the lifecycle boundary explicit:

- recall stays read-only unless a specific TES skill or oracle authorizes more;
- scope normalization is handled by the parent context until the shared normalizer exists;
- write gate means durable Cortex writes require explicit parent authorization;
- checkpoint state is resumability, not durable memory;
- closeout is proven by TES oracles and repository Git hooks;
- subagent return is evidence return only.

Parent owns durable memory. Agents may inspect, patch, or report findings inside their assigned scope, but they must not perform durable Cortex writes or promote checkpoint/event state into memory directly.

## Validation

Run the bundled self-test when changing this skill:

```bash
python3 .agents/skills/tes-engineering-discipline/scripts/discipline_oracle.py --self-test
```

In a target repository, also run the smallest real project oracle: unit test, typecheck, lint, build, contract test, or governance gate.

## Done

The skill is applied when assumptions are visible, implementation is smaller than the first impulse, every changed line traces to the request, closure is backed by evidence, and durable learning has been considered for Cortex without automatic writing.
