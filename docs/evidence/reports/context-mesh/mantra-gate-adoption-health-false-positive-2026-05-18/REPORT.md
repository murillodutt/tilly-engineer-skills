---
tds_id: evidence.context_mesh.mantra_gate_adoption_health_false_positive_2026_05_18
tds_class: evidence
status: active
consumer: TES maintainers
source_of_truth: false
evidence_level: L4
---

# Mantra Gate Adoption Health False Positive Report

## Classification

- `oracle_gap`
- `false_positive_control`
- Portable TES product behavior, not a target-owned workaround

## Cause

TES `0.3.110` made the Mantra Gate adoption oracle correlate dirty worktree,
staged files, recent commit files, and existing gate records. In `/tes-doctor`,
that default read-only health check could inherit `high-risk` from historical
or unrelated local state, then validate old compact records as if they were the
gate for the current doctor action.

## Correction

TES `0.3.111` separates adoption modes:

- default `health`: read-only; reports dirty state and historical compact
  high-risk records as contextual metrics/history findings;
- `--state-changing`: validates the current state-changing action;
- `--closure-claim`: requires a closure `ORACLE`;
- `--commit-push`: keeps push readiness strict;
- `--audit-history`: explicitly escalates historical compact high-risk records
  to `NEEDS_REVIEW`.

## Focused Evidence

| Fixture | Expected | Result |
|---------|----------|--------|
| dirty tree + compact high-risk historical record + default health | not `NEEDS_REVIEW` | PASS |
| same fixture with `--audit-history` | `NEEDS_REVIEW` | PASS |
| `--state-changing` high-risk compact | `NEEDS_REVIEW` | PASS |
| `--commit-push` without gate | `BYPASS_SUSPECTED` or `BLOCKED` | PASS |
| `--closure-claim` missing `ORACLE` | `BLOCKED` | PASS |
| read-only clean without records | `OK` | PASS |

## Limit

Historical findings remain visible. The fix only prevents read-only doctor
health from treating historical compact gates as blockers for the current
doctor action.
