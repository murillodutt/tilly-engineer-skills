---
tds_id: evidence.context_mesh.v1_final_certification_2026_05_05
tds_class: evidence
status: active
consumer: certification reviewers, adapter authors, and v1 release decision makers
source_of_truth: false
evidence_level: L4
---

# Context Mesh V1 Final Certification Report

This report closes Context Mesh v1 on May 5, 2026. It consolidates retained pipeline evidence, Claude behavior evidence, Codex behavior evidence, and the Cursor scope decision.

It does not add a backend, rerun behavior, change the shared contract, change the dataset, change the grader, change adapter sources, or claim cross-adapter behavior parity.

## Final Decision

Result: `GO` for Context Mesh v1 with scoped adapter behavior claims.

Certified v1 scope:

```text
core: certified for retained pipeline evidence
claude: behavior-certified for retained run/hash/backend/model
codex: behavior-certified for retained run/hash/backend/model/prompt contract
cursor: structural/contract parity only
cross-adapter behavior parity: not claimed
```

## Certified Claims

| Claim | Status | Scope |
|-------|--------|-------|
| Core evidence pipeline | `GO` | Planner, runner, raw evidence, summary, reports, TDS validation, and gates |
| Claude behavior | `GO` | Dataset SHA, grader SHA, `claude-cli`, `sonnet`, retained run |
| Codex behavior | `GO` | Dataset SHA, grader SHA, `codex-cli`, `gpt-5.3-codex`, runner `0.1.7`, prompt contract `codex-adapter-prompt@0.1.1`, retained run |
| Cursor adapter | `GO` structural only | Contract/materialization parity only |
| Evidence-converged context method | `GO` | Build-Test-Fail-Fix loops with retained evidence |

## Explicit Non-Claims

- No universal model behavior claim.
- No cross-adapter behavior parity claim.
- No Cursor behavior certification.
- No N>1 statistical stability claim.
- No strong ROI or cost-efficiency claim.
- No strong per-gate rent claim for all gates across all adapters.
- No claim that structural parity implies behavior parity.

## Evidence Anchors

| Area | Anchor |
|------|--------|
| V1 convergence loop | `95186fc Define v1 convergence loop` |
| Claude behavior closure | `behavior-v1-rc-claude-2026-05-05-convergence-08` |
| Codex backend implementation | `6806b58 Add codex CLI benchmark backend` |
| Codex prompt repair | `7f65d25 Repair Codex distractor prompt contract` |
| Codex behavior closure | `codex-behavior-v1-rc-prompt-011-2026-05-05` |
| Cursor scope decision | `6d4dba6 Defer Cursor behavior certification for v1` |
| Final certification head | `6d4dba6 Defer Cursor behavior certification for v1` |

## Shared Inputs

| Input | Value |
|-------|-------|
| Dataset path | `benchmarks/context-mesh/eval-dataset.json` |
| Dataset SHA | `c47a7b4be0604350c688f48d8088e944dc4b929804f2d6fe094626f5c902e5c6` |
| Grader version | `deterministic-substring@0.1.6` |
| Grader SHA | `8bd4929d30f4b332699f9c29a7414d8877633156ec484ae4a668a1fb28d35318` |
| Planned calls | `44` |
| Conditions | `full`, `none`, `drop:<section>`, `distractor` |
| Gates | Think Before Coding, Simplicity First, Surgical Changes, Goal-Driven Execution |

## Adapter Certification Matrix

| Adapter | Backend | Model | Behavior Status | Structural Status | V1 Claim |
|---------|---------|-------|-----------------|-------------------|----------|
| Claude | `claude-cli` | `sonnet` | `GO` | `GO` | Behavior-certified for retained scope |
| Codex | `codex-cli` | `gpt-5.3-codex` | `GO` | `GO` | Behavior-certified for retained scope |
| Cursor | none | none | Deferred | `GO` | Structural/contract parity only |

## Claude Behavior Evidence

Source: `docs/evidence/reports/context-mesh/behavior-v1-rc-claude-2026-05-05-convergence-08/`

| Metric | Value |
|--------|-------|
| Certification status | `GO` |
| Planned calls | `44` |
| Executed calls | `44` |
| Pass rate | `0.5682` |
| Plan/run parity | `1.0` |
| Raw evidence coverage | `1.0` |
| Backend error count | `0` |
| Trigger pass rate full | `0.8571` |
| Trigger pass rate none | `0.1429` |
| Behavioral lift | `0.7142` |
| Distractor fail rate | `0.5` |
| Distractor leak rate | `0.0` |

Claude ablation losses:

| Gate | Loss | Interpretation |
|------|------|----------------|
| Think Before Coding | `2` | Strong retained signal |
| Simplicity First | `1` | Minimum floor; adversarial follow-up remains useful |
| Surgical Changes | `2` | Strong retained signal |
| Goal-Driven Execution | `1` | Minimum floor; adversarial follow-up remains useful |

## Codex Behavior Evidence

Source: `docs/evidence/reports/context-mesh/codex-behavior-v1-rc-prompt-011-2026-05-05/`

| Metric | Value |
|--------|-------|
| Certification status | `GO` |
| Runner version | `0.1.7` |
| Prompt contract | `codex-adapter-prompt@0.1.1` |
| Planned calls | `44` |
| Executed calls | `44` |
| Pass rate | `0.3182` |
| Plan/run parity | `1.0` |
| Raw evidence coverage | `1.0` |
| Backend error count | `0` |
| Trigger pass rate full | `0.4286` |
| Trigger pass rate none | `0.0` |
| Behavioral lift | `0.4286` |
| Distractor fail rate | `0.0` |
| Distractor leak rate | `0.0` |

Codex ablation losses:

| Gate | Loss | Interpretation |
|------|------|----------------|
| Think Before Coding | `0` | Not strong enough for isolated rent claim |
| Simplicity First | `0` | Not strong enough for isolated rent claim |
| Surgical Changes | `1` | Minimum floor; adversarial follow-up required |
| Goal-Driven Execution | `0` | Not strong enough for isolated rent claim |

The Codex pass rate is low in absolute terms, but the v1 threshold does not claim high absolute accuracy. It certifies full-vs-none lift, intact raw evidence, zero backend errors, and zero confirmed distractor leak for the retained scope.

## Cursor Scope

Source: `docs/evidence/reports/context-mesh/cursor-behavior-scope-decision-2026-05-05/REPORT.md`

Cursor is included in v1 only as structural/contract parity. Behavior certification is deferred because no clean non-interactive route has been certified for prompt isolation, raw output capture, timeout, auth/cost limits, and editor/session-state separation.

## Evidence Limits

- Claude behavior is scoped to one retained Claude CLI run and is not a bare API measurement.
- Codex behavior is scoped to one retained Codex CLI run and prompt contract `codex-adapter-prompt@0.1.1`.
- Cursor behavior is not certified.
- Deterministic substring grading remains wording-sensitive.
- `retention_head=pending` appears in some generated manifests because the runner writes reports before the Git commit that retains them. The retaining commits are recorded in this final report and Git history.
- `gate_head`, `run_head`, and `retention_head` are intentionally separate evidence concepts; older reports do not always encode the final retaining commit directly in generated manifests.
- The final v1 claim is evidence-scoped, not universal.

## Residual Debts

| Debt | Blocking v1? | Next action |
|------|--------------|-------------|
| `retention_head=pending` in generated manifests | No | Add post-retention metadata strategy in v1.1 |
| Cursor behavior route absent | No | Open Cursor Behavior Backend Readiness after v1 |
| Codex per-gate ablation weak | No | Add adversarial per-gate follow-up after final closure |
| Claude/Codex behavior parity absent | No | Design parity comparison only after adapter-specific behavior routes mature |
| Absolute pass rate still low | No | Use targeted dataset/grader forensics, not score chasing |

## Final GO/NO-GO

| Gate | Result |
|------|--------|
| Core pipeline evidence retained | `GO` |
| Claude behavior scoped evidence retained | `GO` |
| Codex behavior scoped evidence retained | `GO` |
| Cursor structural/contract scope explicit | `GO` |
| Cross-adapter behavior parity avoided | `GO` |
| Non-claims explicit | `GO` |
| Known debts listed | `GO` |

Final decision:

```text
GO: Context Mesh v1 certified for Claude + Codex scoped behavior, with Cursor
structural/contract parity only.
```

## Next Loop

Recommended v1.1 work:

1. Add a retention metadata strategy that resolves `retention_head` after commit.
2. Add Cursor Behavior Backend Readiness only if a clean execution route exists.
3. Add adversarial per-gate follow-ups for weak Codex ablation signals.
4. Design cross-adapter behavior parity only after adapter-specific behavior evidence matures.

## Post-Retention Update - 2026-05-06

The first three v1.1 follow-ups now have governed closure artifacts:

- Retention metadata strategy: `docs/evidence/reports/context-mesh/retention-metadata-strategy-2026-05-06/REPORT.md` and `python3 scripts/retention_metadata.py --check`.
- Cursor behavior readiness: `docs/evidence/reports/context-mesh/cursor-behavior-readiness-2026-05-06/REPORT.md`.
- Adversarial per-gate follow-up: dataset `0.1.10` adds `E8-goal-driven-no-test-pressure`.

Historical run conclusions above remain scoped to their original dataset SHA and report date.
