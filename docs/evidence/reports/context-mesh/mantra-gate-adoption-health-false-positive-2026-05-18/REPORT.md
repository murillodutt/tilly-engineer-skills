---
tds_id: evidence.context_mesh.mantra_gate_adoption_health_false_positive_2026_05_18
tds_class: evidence
status: archived
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

TES `0.3.111` separated adoption modes:

- default `health`: read-only; reports dirty state and historical compact
  records as contextual metrics;
- `--state-changing`: validates the current state-changing action;
- `--closure-claim`: requires a closure `ORACLE`;
- `--commit-push`: keeps push readiness strict;
- `--audit-history`: explicitly inspected historical records.

This report is archived because its historical expectation for current-action
compact display was superseded. The current contract treats compact
`[🍳 Flash-Fry]` display as valid when the internal gate record is complete and
the gate returns `PROCEED`.

## Focused Evidence

| Fixture | Expected | Result |
|---------|----------|--------|
| dirty tree + completed historical gate record + default health | not `NEEDS_REVIEW` | PASS |
| same fixture with `--audit-history` | historical inspection | SUPERSEDED |
| current-action compact display | valid when the internal record is complete | SUPERSEDED |
| `--commit-push` without gate | `BYPASS_SUSPECTED` or `BLOCKED` | PASS |
| `--closure-claim` missing `ORACLE` | `BLOCKED` | PASS |
| read-only clean without records | `OK` | PASS |

## Limit

Historical findings remain visible. Current policy is defined by
`docs/mesh/MANTRA-GATE.md`; this report must not be used as active operating
guidance.
