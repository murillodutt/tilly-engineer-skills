---
name: tes-engineering-discipline
description: Apply a maturity-aware engineering discipline to non-trivial coding, review, refactor, or instruction-migration work so assumptions are explicit, maturity is evidenced, scope stays small, diffs remain surgical, and success is verified by a concrete oracle.
---

# Tilly Engineering Discipline

Operational contract:

```text
Assumptions visible. Scope smaller. Edits surgical. Success falsifiable.
```

Use this skill for non-trivial coding, review, refactor, debugging, migration,
or agent-instruction work. Skip the full ceremony for obvious one-line fixes,
but keep the spirit.

## Core Gates

| Gate | Rule | Failure Blocked |
|------|------|-----------------|
| Think Before Coding | Name facts, assumptions, ambiguity, tradeoffs, and blockers before acting | Silent wrong interpretation |
| Maturity Layer Gate | Default to `Birth`; promote only with evidence naming baseline, allowed complexity, forbidden complexity, and oracle | Flattening mature architecture or inflating birth work |
| Simplicity First | Delete speculative scope before adding machinery for the selected maturity layer | Overbuilt code and API bloat |
| Surgical Changes | Touch only request-traceable lines and self-created orphans | Drive-by edits and style churn |
| Goal-Driven Execution | Define and run a falsifiable oracle before closure | False completion |

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

Classify material work before applying `Simplicity First`:

| Layer | Use When | Simplicity Means |
|-------|----------|------------------|
| `Birth` | No higher-layer evidence exists | Less structure; the smallest slice in SCOPE, built at full craft — never an executable draft to be redone |
| `Consolidation` | Real duplication, a second real consumer, repeated fixture, or maintenance cost justifies a small contract | Less repeated maintenance |
| `Evolution` | Accepted architecture, mature SPEC, established contract, compatibility boundary, or execution tree exists | Less architectural regression; Fit First |
| `Platform` | Release, installer, CLI, adapter, MCP, public docs, memory, compatibility, migration, or rollback surface is at risk | Less operational risk |

No promotion evidence means `Birth`. Invalid promotion evidence means
`NEEDS_REVIEW`. Higher layers do not permit speculative complexity; they permit
necessary complexity backed by consumers, contracts, or operational risk.

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
  stop_if:
```

Keep it in conversation or working notes unless the target project requires a
retained artifact.

## Mantra Gate

Before state-changing work, use the TES Mantra Gate:

```text
VERIFY -> SCOPE -> BEST_PATH -> DOCUMENT -> ORACLE -> RESOLVE -> STATUS
```

For routine writes, commits, generated artifacts, spec execution, high-risk
work, or project-state updates, show only `[🍳 Flash-Fry]` to the user when the
gate permits proceeding. That marker is UX compression, not evidence deletion:
the full gate must be recorded in the current evidence/report surface, Field
Reports/Cortex when appropriate, or the local `.tes/mantra-gates/` fallback.

Report gate detail only when the gate returns `BLOCKED` or `NEEDS_REVIEW`,
approval is required, or the user explicitly asks for audit detail. If `VERIFY`
or the required `ORACLE` is missing, stop as `BLOCKED`. If `SCOPE` or
`DOCUMENT` is ambiguous for material work, stop as `NEEDS_REVIEW`.

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

## Diamond Build-Test-Fail-Fix

For critical capabilities, build from the finished contract down:

1. State the final behavior.
2. Create or identify the adversarial fixture that should fail first.
3. Observe the failure.
4. Implement the smallest repair.
5. Run the gate again until it passes.

Do not call certified behavior experimental. Use `blocked`, `degraded`,
`not available`, `certified`, or `fail`.

## Workflow

1. Classify the task.
   - If authority, irreversible risk, external surface, or secret handling is
     unclear, stop and ask.
   - If the task is clear and bounded, continue.
2. Make assumptions visible.
   - Resolve safe ambiguity locally.
   - Ask only when the answer changes scope, authorization, or risk.
3. Select the maturity layer.
   - Default to `Birth`.
   - Promote only with protected baseline, allowed complexity, forbidden
     complexity, and oracle.
   - Use Fit First in `Evolution`: preserve accepted architecture instead of
     flattening it for local minimalism.
   - In `Platform`, preserve fallback, compatibility, release, installer,
     migration, and rollback baselines until retirement evidence and a
     compatibility or release oracle prove they can be removed.
4. Delete scope.
   - Remove unrequested features, future-proofing, one-use abstractions, and
     optional configuration.
   - In higher layers, delete accidental complexity but preserve necessary
     complexity backed by consumers, contracts, or operational risk.
5. Keep edits surgical.
   - Match local style.
   - Avoid unrelated formatting, comments, or refactors.
   - Remove only orphans created by this change.
6. Verify.
   - For bugs, reproduce the failure first when practical.
   - Run the smallest relevant oracle first.
   - Run broader project gates before claiming convergence.
7. Reflect for Cortex when present.
   - If `docs/agents/cortex/CONTRACT.md` exists and the work changed durable
     decisions, contracts, commands, architecture, evidence, or recurring
     lessons, call `cortex_reflect` through MCP or run
     `python3 .tes/bin/cortex.py reflect --target . "<decision or lesson>"`.
   - Treat the result as a proposal. Do not write Cortex cells without
     explicit user authorization.
   - If the result has `curation_due=true`, call `cortex_curate_plan` through
     MCP or run `python3 .tes/bin/cortex.py curate-plan --target . --backend lexical`
     before proposing any merge, split, compaction, or rejection.
8. Respect Field Reports when present.
   - Field Reports is active by default, sanitized, and drained by the local
     pre-push hook.
   - If the user asks to disable, enable, check, or drain it, run the matching
     `field_reports.py` oracle without expanding collection levels or schema.
9. Keep feedback grounded for people.
   - Prefer short, frank prose.
   - Avoid tables, code blocks, YAML/property dumps, and long inventories unless
     the user asks or the artifact requires exact syntax.

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
- scope normalization is handled by the parent context until the shared
  normalizer exists;
- write gate means durable Cortex writes require explicit parent authorization;
- checkpoint state is resumability, not durable memory;
- closeout is proven by TES oracles and repository Git hooks;
- subagent return is evidence return only.

Parent owns durable memory. Agents may inspect, patch, or report findings inside
their assigned scope, but they must not perform durable Cortex writes or promote
checkpoint/event state into memory directly.

## Validation

Run the bundled self-test when changing this skill:

```bash
python3 .agents/skills/tes-engineering-discipline/scripts/discipline_oracle.py --self-test
```

In a target repository, also run the smallest real project oracle: unit test,
typecheck, lint, build, contract test, or governance gate.

## Done

The skill is applied when assumptions are visible, implementation is smaller
than the first impulse, every changed line traces to the request, closure is
backed by evidence, and durable learning has been considered for Cortex without
automatic writing.
