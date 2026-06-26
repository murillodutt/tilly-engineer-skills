---
tds_id: mesh.mantra_gate
tds_class: mesh
status: active
consumer: adapter authors, TES agents, and adopters
source_of_truth: true
evidence_level: L2
tver: 0.1.1
---

# TES Mantra Gate

Mantra Gate is the TES senior-manager operating layer for agents. It watches the whole task, derives obligations from active ADR/PRD/SPEC contracts and the protected baseline, and surfaces the smallest useful correction before drift becomes behavior.

It is not a second planning framework and not a user-facing workflow. The gate injects context for the agent and blocks only where the runtime has a governed reason to stop.

## Operating Bands

The contract has two bands:

| Band | Runtime behavior |
|------|------------------|
| Proactive supervision | Ordinary local edits, focused oracles, staging, and local commits. Advise or inject context only when a real contract obligation or drift appears; otherwise stay silent. Do not require gate artifacts, markers, or skill loading for this band. |
| Hard gate | Destructive, remote, release, sync, secret-bearing, or high-impact state changes, plus closure claims that depend on those actions. Require the hard-gate schema before proceeding. |

This is anti-cry-wolf behavior: benign reads and ordinary code edits are silent; governed material edits are supervised; forbidden actions are blocked.

## Compact Marker

The compact marker is rendered with Markdown backticks:

```markdown
`🍳 Flash-Fry`
```

The marker is a discreet signal, not an invocation surface. Do not create, advertise, or route a `/flash-fry` skill or command.

Use the marker only when a visible compact signal is useful. It must not hide blockers, unresolved decisions, failed oracles, or approval needs. In those cases, report `BLOCKED` or `NEEDS_REVIEW`, or provide audit detail when explicitly asked.

## Hard-Gate Schema

Hard-gate records use this schema:

| Field | Meaning |
|-------|---------|
| `VERIFY` | Concrete evidence consulted before action |
| `SCOPE` | Allowed territory and anti-scope |
| `BEST_PATH` | Alternatives considered and chosen path |
| `DOCUMENT` | Where action or evidence will be recorded |
| `ORACLE` | Minimum falsifiable closure proof |
| `RESOLVE` | Issue found and resolved, or `none found` |
| `STATUS` | `PROCEED`, `BLOCKED`, or `NEEDS_REVIEW` |

The schema is still available for explicit validation and audits. It is not required as visible ceremony for ordinary supervision-band work.

## Risk Classes

Mantra Gate classifies action risk deterministically:

| Risk | Meaning |
|------|---------|
| `routine` | Read-only or low-impact local work; supervision band |
| `material` | Local writes, governed artifacts, staging, or commits; supervision band unless a host runtime classifies the specific action as forbidden |
| `high-risk` | Remotes/push, release, sync, secrets/env, DB/schema, auth/RBAC, real customer data, production, compliance/legal, public API/surface, destructive Git, or generated runtime packaging |
| `forbidden` | Destructive Git, secret disclosure, or production action without an explicit contract |

`high-risk` and `forbidden` actions wake the hard gate. `forbidden` work blocks until explicitly resolved and authorized.

## Host-Aware Hooks

Installed hooks are projections of the contract, not a flattened cross-host protocol.

| Host | Existing behavior |
|------|-------------------|
| Claude | `SessionStart` handles first-session setup context. `PreToolUse` blocks forbidden actions with exit `2` plus `stderr`; governed material edits are allowed with `additionalContext`; benign work is silent. |
| Codex | `SessionStart` and `PreToolUse` are installed through TOML hook blocks with hook feature activation. Forbidden actions block with exit `2` plus `stderr`; governed material edits are supervised; benign work is silent. |
| Cursor | `preToolUse` uses the host JSON permission contract. Forbidden actions return JSON permission deny with process exit `0`; governed material edits are allowed with a JSON user message; benign work is silent. |

Install and uninstall are ownership-marker based and preserve foreign hooks. Reinstalling must be idempotent across Claude, Codex, and Cursor.

The runtime accepts host payload differences instead of flattening them: hook event and tool fields may arrive in snake_case or camelCase, `MultiEdit` is treated as a mutating tool, and PreToolUse execution writes a best-effort local sentinel so attach-health can distinguish configured hooks from hooks that actually fired.

## Visibility Rules

- Routine read-only work: no output required.
- Supervised local work: inject context only when a real obligation appears, and avoid repeating the same nudge in a session.
- Hard-gate work: require the schema and report only the blocking or review detail needed to proceed.
- Approval, `BLOCKED`, and `NEEDS_REVIEW`: show detail.
- Explicit audit request: show the relevant record or validation result.

Do not print success noise. A clean proceed may stay quiet.

## Storage

When a hard-gate record is required or explicitly requested, use existing TES evidence, Field Reports, or Cortex surfaces when present; otherwise use the current cycle's local evidence or `.tes/mantra-gates/records.jsonl` as a local fallback.

Stored gate records must be sanitized. Never store secrets, credentials, personal data, raw private URLs, raw prompts, raw stack traces, or sensitive raw file contents.

## Failure Behavior

- Missing `VERIFY`: `BLOCKED`.
- Ambiguous or missing `SCOPE` for a hard-gate action: `NEEDS_REVIEW`.
- Missing `DOCUMENT` for a hard-gate record: `NEEDS_REVIEW`.
- Missing `ORACLE` when closure is claimed: `BLOCKED`.
- Non-empty unresolved `RESOLVE`: `BLOCKED`.
- Hard-gate evidence without a nearby gate record: `BYPASS_SUSPECTED`.

Never allow `PROCEED` by prose alone when the hard gate is active and a concrete oracle exists.

## Adoption Oracle

The adoption oracle is read-only. By default, it runs in `health` mode for doctor-style checks: dirty files, staged files, recent commits, and historical records are reported as context and metrics, not treated as the current action.

When invoked with `--state-changing`, `--commit-push`, `--closure-claim`, or `--audit-history`, it checks whether Mantra Gate is actually being used for that current action or explicit history audit. It correlates Git diff, staged files, the recent commit, Field Reports, local gate JSONL records, action intent, risk class, and closure claims.

Statuses:

| Status | Recovery |
|--------|----------|
| `OK` | Continue; compact marker is enough when the full record exists |
| `DEGRADED` | Repair the gate record or rerun with a complete gate |
| `BYPASS_SUSPECTED` | Stop closure; reconstruct evidence and record a gate |
| `NEEDS_REVIEW` | Resolve ambiguity, request approval, or report audit detail |
| `BLOCKED` | Resolve the blocker before acting |

The oracle also emits local sanitized metrics: compact/full counts, status counts, missing fields, bypass suspicion, and actions without a closure oracle. Compact display is normal when the full internal gate is complete and the gate returns `PROCEED`. The oracle does not collect secrets, raw prompts, private content, or remote telemetry.

The oracle also reports adapter surface health. It distinguishes whether the skill-owned behavior is present, whether bootloaders route to that behavior instead of duplicating it, whether local hook config is present or not applied, and whether retired project-local gate markers appear in active runtime surfaces. Historical docs and evidence may preserve retired text; active bootloaders and rules may not.

## Helpers

The deterministic helper is:

```bash
python3 .tes/bin/mantra_gate.py --self-test
python3 .tes/bin/mantra_gate.py emit-marker
python3 .tes/bin/mantra_gate.py validate --gate gate.json --state-changing --closure-claim --record --target .
python3 .tes/bin/mantra_gate.py classify-risk --action "git push to origin"
python3 .tes/bin/mantra_gate_adoption_oracle.py --target .
python3 .tes/bin/mantra_gate_adoption_oracle.py --target . --action "commit" --state-changing
python3 .tes/bin/mantra_gate_adoption_oracle.py --target . --commit-push
python3 .tes/bin/mantra_gate_adoption_oracle.py --target . --audit-history
```

From the source package, use `scripts/mantra_gate.py` and `scripts/mantra_gate_adoption_oracle.py`.

Source package runtime oracles:

```bash
python3 scripts/mantra_gate.py --self-test
python3 scripts/mantra_gate_band_oracle.py --self-test
python3 scripts/mantra_gate_pretooluse_oracle.py --self-test
python3 scripts/mantra_gate_agent_idempotency_oracle.py
python3 scripts/materialize_adapter.py all --check
```
