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
[🍳 TES - mg]
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

Never allow `PROCEED` by prose alone when a concrete oracle exists.

## Helper

The deterministic helper is:

```bash
python3 .tes/bin/mantra_gate.py --self-test
python3 .tes/bin/mantra_gate.py emit-marker
python3 .tes/bin/mantra_gate.py validate --gate gate.json --state-changing --closure-claim --record --target .
```

From the source package, use `scripts/mantra_gate.py`.
