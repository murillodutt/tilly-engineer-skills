---
tds_id: evidence.context_mesh.adapter_behavior_readiness_2026_05_05
tds_class: evidence
status: active
consumer: certification reviewers, adapter authors, and backend implementers
source_of_truth: false
evidence_level: L3
---

# Adapter Behavior Readiness Report

This report designs how to measure behavior per adapter without contaminating the shared context mesh. It does not change the contract, dataset, grader, runner, UI, or behavior claims for Codex and Cursor.

## Decision

Result: `GO` for adapter behavior readiness design.

Scope:

```text
Claude: behavior baseline exists
Codex: backend/readiness design required
Cursor: backend/readiness design required or explicitly deferred
Shared mesh: frozen
Dataset/grader: frozen unless failure evidence demands change
```

This is not a behavior parity report. It is a readiness map for future behavior runs.

## Head Fields

Future behavior reports must separate these heads:

| Field | Meaning | Current value |
|-------|---------|---------------|
| `gate_head` | Git commit containing the gate or readiness logic used to decide whether the run is admissible | `bba5307 Retain adapter parity readiness evidence` |
| `run_head` | Git commit checked out when behavior execution was run | `N/A` for this design-only report |
| `retention_head` | Git commit retaining the final evidence package | This report's retaining commit |

Do not collapse these fields. A behavior run can be executed at one Git HEAD, validated by a gate introduced at another HEAD, and retained by a later commit.

## Frozen Shared Mesh

| Surface | State |
|---------|-------|
| Neutral contract | Frozen at `docs/mesh/CONTRACT-MANIFEST.yml` |
| Context principle | `Evidence-Converged Context` adopted |
| Dataset | Frozen at current context-mesh dataset until failure evidence demands change |
| Grader | Frozen at current deterministic substring grader until failure evidence demands change |
| Runner | No changes in this loop |
| Backend set | No new backend in this loop |

## Adapter Readiness Matrix

| Adapter | Current state | Proposed behavior route | Evidence limits | Readiness |
|---------|---------------|-------------------------|-----------------|-----------|
| Claude | Behavior baseline exists | Use existing `claude-cli` backend through `scripts/context_mesh_run.py` | Claude Code is not bare API execution; default Claude Code context may influence output | Ready for scoped reruns |
| Codex | Structural/contract parity only | Design a non-interactive backend adapter only after an explicit execution surface is chosen | Codex app/thread context, local tool affordances, auth, cost, and prompt isolation must be declared before any behavior claim | Design required |
| Cursor | Structural/contract parity only | Design or defer a Cursor execution route; require non-interactive prompt execution and retained raw output | Cursor agent state, project rules, editor context, tool invocation, and prompt isolation must be declared before any behavior claim | Design required or defer |

## Backend Readiness Criteria

Before an adapter can run behavior certification, its backend design must declare:

| Criterion | Required declaration |
|-----------|----------------------|
| Invocation | Exact local command, API, or connector path |
| Prompt isolation | Whether the backend sees only runner prompt or extra tool context |
| Auth/cost | Required credentials and budget controls |
| Raw output | Where stdout/stderr/model output is captured |
| Failure mode | How auth, timeout, refusal, and tool errors are represented |
| Evidence fields | `gate_head`, `run_head`, `retention_head`, dataset SHA, grader SHA, backend, model, prompt SHA, output SHA |
| NO-GO | Conditions that stop certification before behavior interpretation |

## Contamination Risks

| Risk | Applies to | Control |
|------|------------|---------|
| Matrix label leak | All adapters | Do not expose `full`, `none`, or `drop:<section>` labels in backend prompt |
| Tool default context | Claude, Codex, Cursor | Declare non-bare/default-context limits in report |
| Project rule double-loading | Cursor | Separate materialized rule loading from runner prompt assumptions |
| Thread/session memory | Codex, Cursor, Claude | Use non-persistent or fresh execution mode when available |
| Adapter-specific prose drift | All adapters | Use contract parity gate, not text equality |
| Behavior claim from structure | Codex, Cursor | Structural readiness never implies behavior parity |

## GO Criteria

This readiness loop is `GO` when:

| Area | Criterion |
|------|----------|
| Claude | Existing behavior route and evidence limits are documented |
| Codex | Backend design requirements are documented without claiming behavior |
| Cursor | Backend design/defer requirements are documented without claiming behavior |
| Shared mesh | Contract, dataset, grader, and runner remain unchanged |
| Evidence | Future `gate_head`, `run_head`, and `retention_head` fields are defined |
| Claim | Only readiness design is claimed |

## NO-GO Conditions

- A report declares Codex or Cursor behavior certification from structural readiness.
- A report changes shared contract, dataset, grader, or runner without failure evidence.
- A backend design cannot capture raw output and hashes.
- A backend design cannot state prompt isolation limits.
- A behavior report omits `gate_head`, `run_head`, or `retention_head`.
- Adapter prose matching is treated as behavior parity.

## Next Work

Next loop: adapter-specific backend design.

Order:

1. Choose whether Codex behavior will be measured through a local CLI, app connector, or explicit API path.
2. Choose whether Cursor behavior will be measured or deferred.
3. Add backend design docs before adding backend code.
4. Only after design `GO`, implement one backend at a time with retained fixture or dry-run evidence first.
