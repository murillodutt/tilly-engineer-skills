---
name: tes-engineering-discipline
description: Apply a four-gate engineering discipline to non-trivial coding, review, refactor, or instruction-migration work so assumptions are explicit, scope stays small, diffs remain surgical, and success is verified by a concrete oracle.
---

# Tilly Engineering Discipline

Operational contract:

```text
Assumptions visible. Scope smaller. Edits surgical. Success falsifiable.
```

Use this skill for non-trivial coding, review, refactor, debugging, migration,
or agent-instruction work. Skip the full ceremony for obvious one-line fixes,
but keep the spirit.

## Four Gates

| Gate | Rule | Failure Blocked |
|------|------|-----------------|
| Think Before Coding | Name facts, assumptions, ambiguity, tradeoffs, and blockers before acting | Silent wrong interpretation |
| Simplicity First | Delete speculative scope before adding machinery | Overbuilt code and API bloat |
| Surgical Changes | Touch only request-traceable lines and self-created orphans | Drive-by edits and style churn |
| Goal-Driven Execution | Define and run a falsifiable oracle before closure | False completion |

## Discipline Packet

Use this compact packet when the task is material:

```yaml
engineering_discipline:
  assumptions:
  ambiguity:
  simplest_path:
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

For routine writes, commits, generated artifacts, spec execution, or
project-state updates, the visible user marker may be only `[🍳 TES - mg]`.
That marker is UX compression, not evidence deletion: the full gate must be
recorded in the current evidence/report surface, Field Reports/Cortex when
appropriate, or the local `.tes/mantra-gates/` fallback.

Show the full gate instead of the compact marker when risk is high, ambiguity
exists, user approval is required, or the action could affect secrets, data,
databases, remotes, production, authentication, compliance, or public surfaces.
If `VERIFY` or the required `ORACLE` is missing, stop as `BLOCKED`. If `SCOPE`
or `DOCUMENT` is ambiguous for material work, stop as `NEEDS_REVIEW`.

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
3. Delete scope.
   - Remove unrequested features, future-proofing, one-use abstractions, and
     optional configuration.
4. Keep edits surgical.
   - Match local style.
   - Avoid unrelated formatting, comments, or refactors.
   - Remove only orphans created by this change.
5. Verify.
   - For bugs, reproduce the failure first when practical.
   - Run the smallest relevant oracle first.
   - Run broader project gates before claiming convergence.
6. Reflect for Cortex when present.
   - If `docs/agents/cortex/CONTRACT.md` exists and the work changed durable
     decisions, contracts, commands, architecture, evidence, or recurring
     lessons, call `cortex_reflect` through MCP or run
     `python3 .tes/bin/cortex.py reflect --target . "<decision or lesson>"`.
   - Treat the result as a proposal. Do not write Cortex cells without
     explicit user authorization.
   - If the result has `curation_due=true`, call `cortex_curate_plan` through
     MCP or run `python3 .tes/bin/cortex.py curate-plan --target . --backend lexical`
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

## Module Map

| Need | Load |
|------|------|
| Mantra Gate helper | `.tes/bin/mantra_gate.py --self-test` when installed, or `scripts/mantra_gate.py --self-test` in the package source |
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
