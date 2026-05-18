---
tds_id: evidence.context_mesh.mantra_gate_adoption_hardening_2026_05_18
tds_class: evidence
status: active
consumer: TES maintainers
source_of_truth: false
evidence_level: L4
---

# Mantra Gate Adoption Hardening Report

## Summary

TES `0.3.110` strengthens Mantra Gate from a validatable micro-gate into a
local adoption-health layer. The compact marker remains `[🍳 TES - mg]`, but
state-changing work now has a read-only oracle that can detect missing records,
high-risk compact-only gates, missing closure oracles, forbidden risk classes,
and sanitized local metrics.

## Changed Behavior

- `scripts/mantra_gate.py` now includes deterministic risk classification:
  `routine`, `material`, `high-risk`, and `forbidden`.
- `scripts/mantra_gate_adoption_oracle.py` correlates Git diff, staged files,
  recent commit metadata, Field Reports presence, local gate JSONL records,
  action intent, risk, and closure claims.
- `/tes-doctor` guidance now treats `BYPASS_SUSPECTED`, `NEEDS_REVIEW`, and
  `BLOCKED` from Mantra Gate adoption as stop conditions for closure,
  commit, or push claims.
- Installed bundles now include the adoption oracle under `.tes/bin/**`.

## Focused Evidence

| Gate | Result |
|------|--------|
| `python3 scripts/mantra_gate.py --self-test` | PASS |
| `python3 scripts/mantra_gate_adoption_oracle.py --self-test` | PASS |
| `python3 scripts/field_reports.py --self-test` | PASS |
| `python3 scripts/command_trigger_oracle.py --self-test` | PASS |
| `python3 scripts/validate_reference_package.py` | PASS |
| `python3 scripts/public_bundle_oracle.py` | PASS |
| `python3 scripts/materialize_adapter.py all --check` | PASS |
| `git diff --check` | PASS |

## Adoption Probe

A local full Mantra Gate record was written to
`.tes/field-reports/mantra-gates.jsonl` for this package change. The adoption
oracle classified the working change as `high-risk` because it touches generated
runtime packaging and public package surfaces, then returned `OK` because a
visible full gate record existed.

## Limits

- No remote telemetry was added.
- No push was performed.
- The adoption oracle is intentionally read-only; it reports suspicious bypass
  instead of mutating project state.
