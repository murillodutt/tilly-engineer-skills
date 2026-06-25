---
tds_id: evidence.context_mesh.cursor_behavior_scope_decision_2026_05_05
tds_class: evidence
status: active
consumer: certification reviewers, adapter authors, and v1 release decision makers
source_of_truth: false
evidence_level: L3
---

# Cursor Behavior Scope Decision Report

This report closes Stage 4 of the V1 convergence loop. It decides Cursor's v1 behavior scope without running a Cursor behavior backend.

It does not change the shared contract, dataset, grader, runner, Cursor adapter source, Claude evidence, Codex evidence, or UI.

## Decision

Result: `GO` to keep Cursor as `structural/contract parity only` for v1.

Claim:

```text
Context Mesh v1 may close with Claude and Codex behavior evidence while Cursor
remains structural/contract parity only. Cursor behavior certification is
deferred until a clean, non-interactive, raw-output-retaining execution route is
designed and certified.
```

## Current Adapter State

| Adapter | Structural/contract parity | Behavior evidence | V1 scope |
|---------|----------------------------|-------------------|----------|
| Claude | `GO` | `GO`, scoped to retained run/hash/backend/model | Behavior-certified for retained scope |
| Codex | `GO` | `GO`, scoped to retained run/hash/backend/model/prompt contract | Behavior-certified for retained scope |
| Cursor | `GO` | Not run | Structural/contract parity only |

## Evidence Basis

| Evidence | Result |
|----------|--------|
| Adapter parity readiness | `GO` for Claude, Codex, Cursor structural/contract parity |
| Adapter behavior readiness | Cursor requires design or explicit defer |
| Claude behavior evidence | Retained scoped `GO` |
| Codex behavior evidence | Retained scoped `GO` for `codex-adapter-prompt@0.1.1` |
| Cursor behavior route | No certified route |

## Why Cursor Is Deferred

Cursor behavior measurement would need a clean route that proves what is being measured:

| Requirement | Current v1 status |
|-------------|-------------------|
| Non-interactive invocation | Not certified |
| Prompt isolation | Not certified |
| Raw model output capture | Not certified |
| stdout/stderr or equivalent evidence | Not certified |
| Timeout and failure normalization | Not certified |
| Fresh session/thread control | Not certified |
| Matrix label non-leakage | Not certified for Cursor behavior |
| Cost/auth/error limits | Not certified |

Measuring Cursor without these controls would risk certifying editor/session state rather than the Cursor adapter contract.

## V1 Claim Boundary

Allowed v1 wording:

```text
Claude and Codex have scoped behavior evidence. Cursor has structural and
contract parity evidence only.
```

Forbidden v1 wording:

```text
All adapters have behavior parity.
Cursor behavior is certified.
Claude/Codex behavior results imply Cursor behavior.
Structural parity implies behavior parity.
```

## Future Cursor Behavior Route

Cursor behavior can be reopened after v1 through a separate readiness loop:

1. Identify exact non-interactive Cursor invocation, API, connector, or acceptable defer decision.
2. Declare prompt isolation and editor/session context limits.
3. Prove raw output retention and hashes.
4. Normalize auth, timeout, refusal, tool, and missing-output failures.
5. Run a single-sample smoke before any full matrix.
6. Retain GO or NO-GO evidence before repair.

## GO Criteria For This Decision

| Check | Result |
|-------|--------|
| Cursor structural/contract parity remains green | `PASS` |
| Cursor behavior is not claimed | `PASS` |
| Claude/Codex behavior evidence remains scoped | `PASS` |
| No shared mesh surfaces changed | `PASS` |
| Future Cursor route remains possible after v1 | `PASS` |

## Next Step

Proceed to final v1 certification closure with explicit scope:

```text
core: certified for retained pipeline evidence
claude: behavior-certified for retained run/hash/backend/model
codex: behavior-certified for retained run/hash/backend/model/prompt contract
cursor: structural/contract parity only
cross-adapter behavior parity: not claimed
```
