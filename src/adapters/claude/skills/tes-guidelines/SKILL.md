---
name: tes-guidelines
description: Maturity-aware behavioral engineering discipline to reduce ambiguity, overcomplication, simplification regression, drive-by edits, and false completion. Use when writing, reviewing, refactoring, or migrating code/instructions and the work is non-trivial.
license: MIT
---

# Tilly Guidelines

Core contract:

```text
Assumptions visible. Scope smaller. Edits surgical. Success falsifiable.
```

## Module Map

| Surface | Load when |
|---------|-----------|
| `docs/CONTRACT-HISTORY.md` | Discipline origin, gates, or failure modes |

## TES Trigger Fallback

Treat `/tes-init`, `/tes-setup`, `/tes-update`, `/tes-align`, `/tes-prospect`, `/tes-mine`,
`/tes-open-obsidian`, `/tes-cortex`, `/tes-curate`, `/tes-mcp`,
`/tes-field-reports`, `/tes-doctor`, `/tes-adapter`, `/tes-bench`, and
`/tes-bump` as the
shared TES trigger vocabulary. Treat `/tes:init`, `/tes:update`,
`/tes:align`, `/tes:prospect`, `/tes:mine`, `/tes:open-obsidian`,
`/tes:cortex`, `/tes:mcp`, `/tes:field-reports`, `/tes:doctor`,
`/tes:adapter`, `/tes:bench`, `/tes:bump`, `/tes:check`, `/tes:certify`,
`/tes:recall`, `/tes:learn`, `/tes:reflect`, and `/tes:curate` as compatible
aliases.

Natural intents also route to TES: `tes init`, `tes setup`, `tes update`, `Atualizar TES`,
`atualizar TES`, `tes align`, `align TES`, `align this project`,
`alinhar TES`, `alinhar projeto`, `open Obsidian`,
`open this project in Obsidian`, `abrir Obsidian`, `abrir no Obsidian`,
`initialize TES`, `install TES`, `recertify TES`,
`inicializar TES`, `instalar TES`, and `recertificar TES`.

Do not activate `/tes-prospect` or `/tes-mine` from broad natural language.
They require explicit invocation and must honor the cognitive brake.
`tes-bump` is a version governance guard: direct bump/sync requests route to
it, and commit, release, delivered-behavior, or gate-reported bump conditions
auto-activate its read-only governance check.

If Claude reports `/tes:*` text as an invalid slash, treat it as TES intent and
do not stop to ask for a route when the intended TES action is clear.

Tradeoff: this skill biases toward caution over speed. Use judgment for trivial
one-liners.

## Gate Zero — Declared-Contract Arbiter

The arbiter runs FIRST, before the five gates, whenever the gates tension —
Simplicity-First or Surgical-Changes pulling one way and a contract already in
the repo pulling the other. It answers exactly one binary question:

```text
Does the minimal solution silently violate a contract already DECLARED and
ENUMERABLE in this repo?
```

The question is yes/no with exactly one answer, in the spirit of `tes-mine`: it
works because it is hard and accepts no questioning. `YES` requires a NAMED
declared fact on the table; anything that is not `YES` is `NO`. Gradation —
"partially declared", "sort of a peer-convergence", "mostly violated" — is
forbidden; it is the entry door of ambiguity. This mirrors the oracle grammar:
`maturity_layer` resolves to exactly one enum value or fails, `is_generic`
returns `True`/`False`, `selected_layer` returns one layer or `None`. The
`declared_contract` state resolves to exactly one of `YES`/`NO` or fails as
`NEEDS_REVIEW` — never "partial".

A declared contract is one an oracle could name from source WITHOUT running it.
There are exactly four types:

1. **Frozen-schema cardinality** — a frozen schema's field-cardinality
   invariant (`strictObject`, `.optional()`). A transform that drops a declared
   field violates it.
2. **Closed-domain coverage** — a union or enum of known size `N` reachable on
   the path, AND an acceptance line saying "all `N`", with the implementation
   capped below `N`.
3. **Peer-convergence** — a structural pattern used by a countable majority of
   in-repo sibling units of the same class, with the unit under change the lone
   deviation.
4. **Affordance-deliverable** — a user-facing control whose label is verb+noun
   naming a concrete artifact that must cross the app boundary.

Decision is three-way:

- **Override-and-bind-oracle.** If `YES` and the contract is satisfiable in
  scope, the broad default (Simplicity-First / Surgical-Changes) is OVERRIDDEN
  and the closure oracle MUST bind to the declared contract.
- **Escalate-collision.** If `YES` but satisfying it would breach a SECOND
  declared boundary — a frozen surface, a SPEC stop-state — you MUST NOT pick
  the broad default silently. NAME the collision to the user as an escalated
  trade-off. Resolving a collision silently is itself a failure the discipline
  oracle's plan check is meant to surface.
- **Broad-default-wins.** If `NO` declared contract is violated,
  Simplicity-First and Surgical-Changes WIN unchanged. Undeclared aspirations —
  craft, polish, "could be nicer" — do NOT trigger the override.

When the override fires, the obligation is per-line rigor, not more lines: route
to the Effort Gate and promote the effort tier to `Premium` (see Effort Gate).
Premium authorizes a heavier oracle bound to the declared contract; it never
authorizes a new abstraction, strategy interface, or config knob to "cover" the
contract.

Worked example (override). Request: "Persist the designer draft by
round-tripping it through `JSON.parse(JSON.stringify(draft))` before save — it's
the smallest serialization and the snapshot looks identical." A frozen
`strictObject` with `.optional()` fields is on the path, and a JSON round-trip
silently drops keys whose value is `undefined`. Verdict: `declared_contract =
YES`, type frozen-schema cardinality. The broad default (smallest
serialization) is OVERRIDDEN; the closure oracle MUST bind to the frozen schema
— a structural clone that preserves declared-optional fields, with a test that
asserts an `undefined`-valued optional field survives the round-trip. Effort
tier promotes to `Premium` (heavier oracle, same scope). Do not add a
serializer abstraction; repair the one path.

Worked example (collision). Request: "Wire the 'Exportar PDF' button to deliver
the file; the export module boundary is frozen and exposes no byte path, so just
have the handler resolve and toast success." Two declared contracts collide: an
affordance-deliverable invariant (a control labeled verb+noun — "Exportar PDF" —
promising a delivered artifact across the app boundary) and a frozen module
boundary that exposes no byte path to deliver it. Verdict: `declared_contract =
YES` on the affordance, but satisfying it breaches the frozen boundary. You MUST
NOT silently ship the toast-only handler (the affordance lies) and MUST NOT
silently widen the frozen boundary (the surface lies). NAME the collision as an
escalated trade-off: stopping at the frozen boundary is correct; the failure is
not escalating the deliverable-vs-boundary collision to the user. Resolve only
after the user picks which boundary moves.

## Four Gates

| Gate | Rule | Failure Blocked |
|------|------|-----------------|
| Think Before Coding | State assumptions, ambiguity, tradeoffs, and blockers before acting | Silent wrong interpretation |
| Maturity Layer Gate | Default to `Birth`; promote only with evidence naming baseline, allowed complexity, forbidden complexity, and oracle | Flattening mature architecture or inflating birth work |
| Simplicity First | Solve only the requested problem with the smallest useful shape for the selected maturity layer | Overbuilt code and API bloat |
| Surgical Changes | Touch only request-traceable lines and self-created orphans | Drive-by refactors and hidden churn |
| Goal-Driven Execution | Define a falsifiable oracle and verify before closure | False completion |

The Declared-Contract Arbiter (Gate Zero) runs FIRST, before all six gates: when
the gates tension, it can override the broad default, force a collision
escalation, or leave Simplicity-First and Surgical-Changes untouched.

## Maturity Layer Gate

Maturity is classificatory, not a phase of execution. The layer is decided
during thinking — which converges before the first line — and the artifact is
born at the layer the thinking settled on. There is no "execute `Birth`, then
promote and re-execute": a `Platform` change is `Platform` from its first line,
a `Birth` change is `Birth` from its first line. Nobody builds a simple house to
demolish it into a palace; the simple phase is the THINKING, and it ends before
the first beam. Promotion is reclassification of the work, never a rebuild of
shipped lines. (Protecting an existing `Platform` baseline is not a rebuild — it
is correctly classifying that the work was `Platform` all along.)

Default material work to `Birth`. Promote only with evidence:

| Layer | Use When | Simplicity Means |
|-------|----------|------------------|
| `Birth` | No higher-layer evidence exists | Less structure; the smallest slice in SCOPE, built at full craft — never an executable draft to be redone |
| `Consolidation` | Real duplication, a second real consumer, repeated fixture, or maintenance cost justifies a small contract | Less repeated maintenance |
| `Evolution` | Accepted architecture, mature SPEC, established contract, compatibility boundary, or execution tree exists | Less architectural regression; Fit First |
| `Platform` | Release, installer, CLI, adapter, MCP, public docs, memory, compatibility, migration, or rollback surface is at risk | Less operational risk |

Invalid promotion evidence means `NEEDS_REVIEW`; no evidence means `Birth`.
Higher layers permit necessary complexity backed by consumers, contracts, or
operational risk, not speculative complexity.

`Birth` is invalid when the prompt names existing installs, an accepted
contract, a compatibility interface, installer, fallback, rollback, release,
migration, CLI, MCP, adapter, or public-doc surface. Those are promotion
evidence: classify the work at that higher layer from its first line, and
simplify inside that classification — not by building lower and rebuilding up.

`Birth` hard stop: do not add a strategy interface, abstract factory, plugin
registry, plugin system, compatibility layer, `TODO` hooks, or future-format
scaffolding unless promotion evidence names a real second consumer, an accepted
contract, or an operational surface. Build only the current requirement and name
the speculative scaffolding you are deliberately not adding.

The stop is conditional, not a ban on abstraction. When a second real consumer,
an accepted contract, or an operational surface exists, that same factory or
registry is the correct `Consolidation`/`Evolution` move — promote and build it.
Rejecting necessary abstraction because it "looks complex" is the inverse error.

`Platform` hard stop: existing installs, installer, fallback, compatibility,
rollback, release, migration, CLI, MCP, adapter, or public-doc surfaces are
`Platform`, not `Birth`. Do not remove those paths only because the new path
passes locally. Local green proves the new path; it does not prove the old
baseline is retired. First name the protected baseline, the consumers or install
surfaces that could still depend on it, the allowed replacement complexity, the
forbidden breakage, and a compatibility or release oracle. Cut the old path only
when explicit retirement evidence proves it no longer needs protection.

Worked example. Request: "Add one archive format today; to prepare for future
formats, create `ArchiveStrategy`, an abstract factory, a plugin registry, and
`TODO` hooks." Layer is `Birth`: only one real format exists, no second consumer
or contract. Implement that one format directly; do not create `ArchiveStrategy`,
the factory, the registry, or the `TODO` hooks; name them as deferred future
scaffolding. If a second real format later lands, that is promotion evidence and
the shared seam becomes correct.

Platform example. Request: "Patch the installer fast by removing the legacy
fallback path. It only exists for compatibility and the new path passes
locally." Layer is `Platform`: protect existing installs, release behavior, and
rollback. Keep the fallback until baseline retirement is evidenced by accepted
migration/compatibility proof and a release or installer oracle; a local green
new-path check is not enough.

## Diamond Build-Test-Fail-Fix

For critical capabilities, build from the finished contract down: state the
final behavior, create or identify the adversarial fixture that should fail
first, observe the failure, implement the smallest repair, and rerun the gate
until it passes.

Do not call certified behavior experimental. Use `blocked`, `degraded`,
`not available`, `certified`, or `fail`.

## Mantra Gate

Before state-changing actions, use the TES Mantra Gate. For routine writes,
commits, generated artifacts, spec execution, high-risk work, or project-state
updates, show only `[🍳 Flash-Fry]` to the user when the gate permits
proceeding; the full gate is still retained as evidence.

Full gate fields are `VERIFY`, `SCOPE`, `BEST_PATH`, `DOCUMENT`, `ORACLE`,
`RESOLVE`, and `STATUS`. Report gate detail only when the gate returns
`BLOCKED` or `NEEDS_REVIEW`, approval is required, or the user explicitly asks
for audit detail.

For closure, commit, or push claims, the adoption oracle may check that a gate
record exists near the state change. If it reports `BYPASS_SUSPECTED`,
`NEEDS_REVIEW`, or `BLOCKED`, stop and recover before claiming progress.

## Infrastructure Decision Gate

Before any infrastructure decision, run a Stack Surface Scan. This applies to
native wrappers, deployment targets, database clients, queues, crypto
primitives, build tools, hosting assumptions, and runtime-bound dependencies.

Inspect the target project's actual stack evidence before choosing: package and
lock files, framework config, runtime config, deployment preset, existing
adapters, generated output contracts, and project governance. Then check
Context7 or official documentation for the framework, runtime, or cloud surface
that owns the behavior. If evidence is missing, stale, or contradictory, stop
as `NEEDS_REVIEW` instead of guessing.

For Nuxt or Nitro projects, Nitro changes the runtime surface. Inspect the
Nitro preset, `node` target, and deployment runtime before choosing a native
OpenSSL wrapper, a pure Node DER builder, Web Crypto, or another runtime-bound
implementation. A Node-looking repository can still target edge, worker,
serverless, or compatibility layers.

The decision must name the stack evidence, documentation source, rejected
alternatives, chosen path, and smallest runtime oracle before implementation.

## Workflow

1. Classify the task.
   - For trivial typo-level work, proceed with judgment.
   - For coding, review, refactor, or instruction migration, use the
     maturity-aware gates.
2. Make assumptions visible.
   - Separate facts from guesses.
   - Ask only when the answer changes material scope, authorization, or risk.
3. Delete scope.
   - Select the maturity layer first; use `Birth` unless promotion evidence
     names baseline, allowed complexity, forbidden complexity, and oracle.
   - Remove speculative features and one-use abstractions before implementation.
   - In `Evolution`, use Fit First: preserve accepted architecture instead of
     flattening it for local minimalism.
4. Keep the diff surgical.
   - Match existing style.
   - Do not clean unrelated code.
   - Remove only orphans created by this change.
5. Verify.
   - Run the smallest relevant check first.
   - Run broader gates when the blast radius requires them.
6. Reflect for Cortex when present.
   - If `docs/agents/cortex/CONTRACT.md` exists and the work produced a durable
     decision, contract change, command, evidence, or lesson, call read-only
     `cortex_reflect` through MCP or run
     `python3 .tes/bin/cortex.py reflect --target . "<decision or lesson>"`.
   - Treat the output as a proposal. Do not write Cortex cells without
     explicit user authorization.
   - If the result has `curation_due=true`, call read-only `cortex_curate_plan`
     through MCP or run
     `python3 .tes/bin/cortex.py curate-plan --target . --backend lexical`
     before proposing any merge, split, compaction, or rejection.
7. Respect Field Reports when present.
   - Field Reports is active by default, sanitized, and drained by the local
     pre-push hook.
   - If the user asks to disable, enable, check, or drain it, run the matching
     `field_reports.py` oracle without expanding collection levels or schema.
8. Keep feedback grounded for people.
   - Prefer short, frank prose.
   - Avoid tables, code blocks, YAML/property dumps, and long inventories unless
     the user asks or the artifact requires exact syntax.

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
- scope normalization is handled by the parent context until the shared
  normalizer exists;
- write gate means durable Cortex writes require explicit parent authorization;
- checkpoint state is resumability, not durable memory;
- closeout is proven by TES oracles and repository Git hooks;
- subagent return is evidence return only.

Parent owns durable memory. Subagents may inspect, patch, or report findings
inside their assigned scope, but they must not perform durable Cortex writes or
promote checkpoint/event state into memory directly.

## Done

The skill worked when the diff is smaller than the first impulse, every changed
line traces to the request, success is backed by a concrete oracle, and durable
learning has been considered for Cortex without automatic writing.
