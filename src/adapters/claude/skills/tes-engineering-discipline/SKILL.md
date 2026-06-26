---
name: tes-engineering-discipline
description: Maturity-aware behavioral engineering discipline to reduce ambiguity, overcomplication, simplification regression, drive-by edits, and false completion. Use when writing, reviewing, refactoring, or migrating code/instructions and the work is non-trivial.
license: MIT
---

# Tilly Engineering Discipline

Core contract:

```text
Assumptions visible. Scope smaller. Edits surgical. Success falsifiable.
```

## Module Map

| Surface | Load when |
|---------|-----------|
| `docs/CONTRACT-HISTORY.md` | Discipline origin, gates, or failure modes |

## TES Trigger Fallback

Treat `/tes-init`, `/tes-setup`, `/tes-update`, `/tes-align`, `/tes-prospect`, `/tes-mine`, `/tes-open-obsidian`, `/tes-cortex`, `/tes-curate`, `/tes-mcp`, `/tes-field-reports`, `/tes-doctor`, `/tes-adapter`, `/tes-bench`, and `/tes-bump` as the shared TES trigger vocabulary. Treat `/tes:init`, `/tes:update`, `/tes:align`, `/tes:prospect`, `/tes:mine`, `/tes:open-obsidian`, `/tes:cortex`, `/tes:mcp`, `/tes:field-reports`, `/tes:doctor`, `/tes:adapter`, `/tes:bench`, `/tes:bump`, `/tes:check`, `/tes:certify`, `/tes:recall`, `/tes:learn`, `/tes:reflect`, and `/tes:curate` as compatible aliases.

Natural intents also route to TES: `tes init`, `tes setup`, `tes update`, `Atualizar TES`, `atualizar TES`, `tes align`, `align TES`, `align this project`, `alinhar TES`, `alinhar projeto`, `open Obsidian`, `open this project in Obsidian`, `abrir Obsidian`, `abrir no Obsidian`, `initialize TES`, `install TES`, `recertify TES`, `inicializar TES`, `instalar TES`, and `recertificar TES`.

Do not activate `/tes-prospect` or `/tes-mine` from broad natural language. They require explicit invocation and must honor the cognitive brake. `tes-bump` is a version governance guard: direct bump/sync requests route to it, and commit, release, delivered-behavior, or gate-reported bump conditions auto-activate its read-only governance check.

If Claude reports `/tes:*` text as an invalid slash, treat it as TES intent and do not stop to ask for a route when the intended TES action is clear.

Tradeoff: this skill biases toward caution over speed. Use judgment for trivial one-liners, and honor an owner-requested no-skill run unless destructive, remote, secret, release, or safety risk requires escalation.

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

## Six Gates

Gate Zero is the Declared-Contract Arbiter; it runs before the six gates and owns every collision between them. The table below lists Gate Zero plus the six gates it arbitrates.

| Gate | Rule | Failure Blocked |
|------|------|-----------------|
| Declared-Contract Arbiter (Gate Zero) | Before closing any tensioned change, answer one binary question — does the minimal solution silently violate a contract already declared and source-nameable in this repo? Resolve collisions here, never inside another gate | Silent contract breach and silent collision resolution |
| Think Before Coding | State assumptions, ambiguity, tradeoffs, and blockers before acting | Silent wrong interpretation |
| Maturity Layer Gate | Default to `Birth`; promote only with evidence naming baseline, allowed complexity, forbidden complexity, and oracle | Flattening mature architecture or inflating birth work |
| Simplicity First | Solve only the requested problem with the smallest useful shape for the selected maturity layer | Overbuilt code and API bloat |
| Surgical Changes | Touch only request-traceable lines and self-created orphans | Drive-by refactors and hidden churn |
| Goal-Driven Execution | Define a falsifiable oracle and verify before closure | False completion |
| Effort Gate | Default to `Standard`; promote to `Premium` only when the Declared-Contract Arbiter or named consequence evidence obligates deeper rigor per line, never more lines | Under-rigor on declared-contract lines and invented rigor on undeclared ones |

Scope gates: Maturity Layer, Simplicity First, Surgical Changes. Craft gates: Think Before Coding, Goal-Driven Execution, Effort Gate. The two axes are orthogonal: scope decides how many lines exist; effort decides how much rigor each line carries. Neither gate may move the other axis.

The Declared-Contract Arbiter (Gate Zero) runs FIRST, before all six gates: when the gates tension, it can override the broad default, force a collision escalation, or leave Simplicity-First and Surgical-Changes untouched.

## Maturity Layer Gate

Maturity is classificatory, not a phase of execution. The layer is decided during thinking — which converges before the first line — and the artifact is born at the layer the thinking settled on. There is no "execute `Birth`, then promote and re-execute": a `Platform` change is `Platform` from its first line, a `Birth` change is `Birth` from its first line. Nobody builds a simple house to demolish it into a palace; the simple phase is the THINKING, and it ends before the first beam. Promotion is reclassification of the work, never a rebuild of shipped lines. (Protecting an existing `Platform` baseline is not a rebuild — it is correctly classifying that the work was `Platform` all along.)

Default material work to `Birth`. Promote only with evidence:

| Layer | Use When | Simplicity Means |
|-------|----------|------------------|
| `Birth` | No higher-layer evidence exists | Less structure; the smallest slice in SCOPE, built at full craft — never an executable draft to be redone |
| `Consolidation` | Real duplication, a second real consumer, repeated fixture, or maintenance cost justifies a small contract | Less repeated maintenance |
| `Evolution` | Accepted architecture, mature SPEC, established contract, compatibility boundary, or execution tree exists | Less architectural regression; Fit First |
| `Platform` | Release, installer, CLI, adapter, MCP, public docs, memory, compatibility, migration, or rollback surface is at risk | Less operational risk |

Invalid promotion evidence means `NEEDS_REVIEW`; no evidence means `Birth`. Higher layers permit necessary complexity backed by consumers, contracts, or operational risk, not speculative complexity.

`Birth` is invalid when the prompt names existing installs, an accepted contract, a compatibility interface, installer, fallback, rollback, release, migration, CLI, MCP, adapter, or public-doc surface. Those are promotion evidence: classify the work at that higher layer from its first line, and simplify inside that classification — not by building lower and rebuilding up.

`Birth` hard stop: do not add a strategy interface, abstract factory, plugin registry, plugin system, compatibility layer, `TODO` hooks, or future-format scaffolding unless promotion evidence names a real second consumer, an accepted contract, or an operational surface. Build only the current requirement and name the speculative scaffolding you are deliberately not adding.

The stop is conditional, not a ban on abstraction. When a second real consumer, an accepted contract, or an operational surface exists, that same factory or registry is the correct `Consolidation`/`Evolution` move — promote and build it. Rejecting necessary abstraction because it "looks complex" is the inverse error.

`Platform` hard stop: existing installs, installer, fallback, compatibility, rollback, release, migration, CLI, MCP, adapter, or public-doc surfaces are `Platform`, not `Birth`. Do not remove those paths only because the new path passes locally. Local green proves the new path; it does not prove the old baseline is retired. First name the protected baseline, the consumers or install surfaces that could still depend on it, the allowed replacement complexity, the forbidden breakage, and a compatibility or release oracle. Cut the old path only when explicit retirement evidence proves it no longer needs protection.

### Platform Ceiling Classification

The goal is ceiling-grade product behavior, not floor-grade patching. Any work that touches or evaluates hooks, installers, update/uninstall paths, adapter materialization, MCP, Cortex runtime, Field Reports, public bundle identity, host contracts, generated target surfaces, or real installed-target evidence is `Platform` from the first line.

Do not reclassify this work as a small local fix because the user says "direct", "sem nova spec", "ajuste fino", "rápido", or "no governance". Those phrases remove document ceremony only; they never remove runtime rigor.

For `Platform` work, the minimum acceptable execution is: name the protected installed baseline, preserve host-specific contracts instead of flattening them, reproduce or fixture the reported behavior when practical, patch package source instead of installed mirrors, add or update the red-capable oracle, run the focused host/runtime gate, and make a release-identity decision.

If host behavior is uncertain, consult official docs or installed/source fixtures before coding. If evidence cannot distinguish bug from host contract, stop as `NEEDS_DISCOVERABILITY` or `NEEDS_OWNER_DECISION`; do not guess and do not collapse to a generic hook contract.

Worked example. Request: "Add one archive format today; to prepare for future formats, create `ArchiveStrategy`, an abstract factory, a plugin registry, and `TODO` hooks." Layer is `Birth`: only one real format exists, no second consumer or contract. Implement that one format directly; do not create `ArchiveStrategy`, the factory, the registry, or the `TODO` hooks; name them as deferred future scaffolding. If a second real format later lands, that is promotion evidence and the shared seam becomes correct.

Platform example. Request: "Patch the installer fast by removing the legacy fallback path. It only exists for compatibility and the new path passes locally." Layer is `Platform`: protect existing installs, release behavior, and rollback. Keep the fallback until baseline retirement is evidenced by accepted migration/compatibility proof and a release or installer oracle; a local green new-path check is not enough.

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

For critical capabilities, build from the finished contract down: state the final behavior, create or identify the adversarial fixture that should fail first, observe the failure, implement the smallest repair, and rerun the gate until it passes.

Do not call certified behavior experimental. Use `blocked`, `degraded`, `not available`, `certified`, or `fail`.

## Mantra Gate

The Mantra Gate is a continuous senior manager, not a pointwise checkpoint: it watches the whole task, derives obligations from the active contracts (ADR/PRD/SPEC) and the protected baseline, and on doubt pulls you toward the right move before you act — a lens, maturity acquisition before coding, reuse over new code, a package fix over a local workaround. It supervises by surfacing that obligation, never by deciding for you. Two registers, by risk: proactive supervision on ordinary work (advise, do not block) and the hard gate on risk (wake and block).

Use the TES Mantra Gate for destructive, remote, release, sync, secret-bearing, or high-impact state changes, and for closure claims that depend on those actions. For ordinary local edits, focused oracles, staging, and local commits, keep the check inline and do not block on gate artifacts, markers, or skill loading — supervise and advise, surfacing a contract obligation or lens only when doubt or drift is real, and stay silent otherwise.

Gate fields are `VERIFY`, `SCOPE`, `BEST_PATH`, `DOCUMENT`, `ORACLE`, `RESOLVE`, and `STATUS`. Report gate detail only when the gate returns `BLOCKED` or `NEEDS_REVIEW`, approval is required, or the user explicitly asks for audit detail.

For destructive, remote, release, sync, secret-bearing, or high-impact closure claims, the adoption oracle may check that a gate record exists near the state change. If it reports `BYPASS_SUSPECTED`, `NEEDS_REVIEW`, or `BLOCKED`, stop and recover before claiming that risky action progressed.

## Infrastructure Decision Gate

Before any infrastructure decision, run a Stack Surface Scan. This applies to native wrappers, deployment targets, database clients, queues, crypto primitives, build tools, hosting assumptions, and runtime-bound dependencies.

Inspect the target project's actual stack evidence before choosing: package and lock files, framework config, runtime config, deployment preset, existing adapters, generated output contracts, and project governance. Then check Context7 or official documentation for the framework, runtime, or cloud surface that owns the behavior. If evidence is missing, stale, or contradictory, stop as `NEEDS_REVIEW` instead of guessing.

For Nuxt or Nitro projects, Nitro changes the runtime surface. Inspect the Nitro preset, `node` target, and deployment runtime before choosing a native OpenSSL wrapper, a pure Node DER builder, Web Crypto, or another runtime-bound implementation. A Node-looking repository can still target edge, worker, serverless, or compatibility layers.

The decision must name the stack evidence, documentation source, rejected alternatives, chosen path, and smallest runtime oracle before implementation.

## Workflow

1. Classify the task.
   - For trivial typo-level work, proceed with judgment.
   - For coding, review, refactor, or instruction migration, use the maturity-aware gates.
2. Make assumptions visible.
   - Separate facts from guesses.
   - Ask only when the answer changes material scope, authorization, or risk.
3. Delete scope.
   - Select the maturity layer first; use `Birth` unless promotion evidence names baseline, allowed complexity, forbidden complexity, and oracle.
   - Remove speculative features and one-use abstractions before implementation.
   - In `Evolution`, use Fit First: preserve accepted architecture instead of flattening it for local minimalism.
4. Keep the diff surgical.
   - Match existing style.
   - Do not clean unrelated code.
   - Remove only orphans created by this change.
5. Verify.
   - Run the smallest relevant check first.
   - Run broader gates when the blast radius requires them.
6. Reflect for Cortex when present.
   - If `docs/agents/cortex/CONTRACT.md` exists and the work produced a durable decision, contract change, command, evidence, or lesson, call read-only `cortex_reflect` through MCP or run `python3 .tes/bin/cortex.py reflect --target . "<decision or lesson>"`.
   - Treat the output as a proposal. Do not write Cortex cells without explicit user authorization.
   - If the result has `curation_due=true`, call read-only `cortex_curate_plan` through MCP or run `python3 .tes/bin/cortex.py curate-plan --target . --backend lexical` before proposing any merge, split, compaction, or rejection.
7. Respect Field Reports when present.
   - Field Reports is active by default, sanitized, and drained by the local pre-push hook.
   - If the user asks to disable, enable, check, or drain it, run the matching `field_reports.py` oracle without expanding collection levels or schema.
8. Keep feedback grounded for people.
   - Prefer short, frank prose.
   - Avoid tables, code blocks, YAML/property dumps, and long inventories unless the user asks or the artifact requires exact syntax.

## Success Formula

```text
E = A * S * C * V
```

Each factor is binary at closure:

- `A`: assumptions visible
- `S`: scope simplified
- `C`: changes constrained
- `V`: verification complete

If any factor is zero, stop or repair before claiming success.

## TES Memory Lifecycle Boundary

When Cortex is the durable memory surface, keep the lifecycle boundary explicit:

- recall stays read-only unless a specific TES skill or oracle authorizes more;
- scope normalization is handled by the parent context until the shared normalizer exists;
- write gate means durable Cortex writes require explicit parent authorization;
- checkpoint state is resumability, not durable memory;
- closeout is proven by TES oracles and repository Git hooks;
- subagent return is evidence return only.

Parent owns durable memory. Subagents may inspect, patch, or report findings inside their assigned scope, but they must not perform durable Cortex writes or promote checkpoint/event state into memory directly.

## Done

The skill worked when the diff is smaller than the first impulse, every changed line traces to the request, success is backed by a concrete oracle, and durable learning has been considered for Cortex without automatic writing.
