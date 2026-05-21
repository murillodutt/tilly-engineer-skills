---
tds_id: mesh.mantra_gate
tds_class: mesh
status: active
consumer: adapter authors, TES agents, and adopters
source_of_truth: true
evidence_level: L2
tver: 0.1.0
---

# TES Mantra Gate

Mantra Gate is a micro-gate that turns intention into auditable action:
evidence, scope, path, record, oracle, and stop rule.

It is not a second planning framework. It is the compact pre-action checkpoint
for state-changing work.

## User-Facing Marker

The default visible marker is:

```text
[🍳 Flash-Fry]
```

Agents may show only this marker before routine state-changing actions when a
full block would add noise. Compact display is UX compression, not evidence
deletion.

The compact marker must not hide blockers, failures, unresolved decisions, user
approval needs, or high-risk choices. In those cases, show the full gate or stop
with `BLOCKED` / `NEEDS_REVIEW`.

## Full Internal Schema

Every recorded Mantra Gate uses this schema:

| Field | Meaning |
|-------|---------|
| `VERIFY` | Concrete evidence consulted before action |
| `SCOPE` | Allowed territory and anti-scope |
| `BEST_PATH` | Alternatives considered and chosen path |
| `DOCUMENT` | Where action or evidence will be recorded |
| `ORACLE` | Minimum falsifiable closure proof |
| `RESOLVE` | Issue found and resolved, or `none found` |
| `STATUS` | `PROCEED`, `BLOCKED`, or `NEEDS_REVIEW` |

## Risk Classes

Mantra Gate classifies action risk deterministically:

| Risk | Meaning |
|------|---------|
| `routine` | Read-only or low-impact local work |
| `material` | Local writes, generated artifacts, staging, or commits |
| `high-risk` | Remotes/push, secrets/env, DB/schema, auth/RBAC, real customer data, production, compliance/legal, public API/surface, destructive Git, or generated runtime packaging |
| `forbidden` | Destructive Git, secret disclosure, or production action without an explicit contract |

`high-risk` work requires a visible full gate. `forbidden` work blocks.

## Activation

Required before:

- writes;
- commits;
- destructive operations;
- spec execution;
- architectural changes;
- migrations;
- external calls;
- generated artifacts;
- project-state updates.

Optional or implicit for pure read-only exploration.

Escalate from compact marker to visible full gate when risk is high, ambiguity
exists, user approval is required, or the action could affect secrets, data,
databases, remotes, production, authentication, compliance, or public surfaces.

## Storage

Do not spam user chat with the full gate by default. Preserve the full gate
internally when a state-changing action occurs.

Preferred storage order:

1. Existing TES evidence, Field Reports, or Cortex surfaces when present.
2. The current cycle's local evidence, spec, report, or certification file.
3. `.tes/mantra-gates/records.jsonl` as a local fallback.

Stored gate records must be sanitized. Never store secrets, credentials,
personal data, raw private URLs, raw prompts, raw stack traces, or sensitive raw
file contents.

## Failure Behavior

- Missing `VERIFY`: `BLOCKED`.
- Ambiguous or missing `SCOPE` for a state-changing action: `NEEDS_REVIEW`.
- Missing `DOCUMENT` for material work: `NEEDS_REVIEW`.
- Missing `ORACLE` when closure is claimed: `BLOCKED`.
- Non-empty unresolved `RESOLVE`: `BLOCKED`.
- High-risk `PROCEED` with only compact display: `NEEDS_REVIEW`.
- State-changing evidence without a nearby gate record: `BYPASS_SUSPECTED`.

Never allow `PROCEED` by prose alone when a concrete oracle exists.

## Adoption Oracle

The adoption oracle is read-only. By default, it runs in `health` mode for
doctor-style checks: dirty files, staged files, recent commits, and historical
records are reported as context and metrics, not treated as the current action.

When invoked with `--state-changing`, `--commit-push`, `--closure-claim`, or
`--audit-history`, it checks whether Mantra Gate is actually being used for that
current action or explicit history audit. It correlates Git diff, staged files,
the recent commit, Field Reports, local gate JSONL records, action intent, risk
class, and closure claims.

Statuses:

| Status | Recovery |
|--------|----------|
| `OK` | Continue; compact marker is enough when the full record exists |
| `DEGRADED` | Repair the gate record or rerun with a complete gate |
| `BYPASS_SUSPECTED` | Stop closure; reconstruct evidence and record a gate |
| `NEEDS_REVIEW` | Show the full gate, resolve ambiguity, or request approval |
| `BLOCKED` | Resolve the blocker before acting |

The oracle also emits local sanitized metrics: compact/full counts, status
counts, missing fields, bypass suspicion, historical compact high-risk records,
and actions without a closure oracle. Historical compact high-risk records are
shown as `history_findings` in health mode; they become `NEEDS_REVIEW` only
under `--audit-history` or an active high-risk action. It does not collect
secrets, raw prompts, private content, or remote telemetry.

The oracle also reports adapter surface health. It distinguishes whether the
skill-owned behavior is present, whether bootloaders route to that behavior
instead of duplicating it, whether local hook config is present or not applied,
and whether retired project-local gate markers appear in active runtime
surfaces. Historical docs and evidence may preserve retired text; active
bootloaders and rules may not.

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

From the source package, use `scripts/mantra_gate.py` and
`scripts/mantra_gate_adoption_oracle.py`.
