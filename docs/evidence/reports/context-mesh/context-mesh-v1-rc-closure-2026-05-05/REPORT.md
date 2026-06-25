---
tds_id: evidence.context_mesh.v1_rc_closure_2026_05_05
tds_class: evidence
status: active
consumer: certification reviewers and next-loop planners
source_of_truth: false
evidence_level: L4
---

# Context Mesh V1-RC Closure Report

This report freezes the best retained context-mesh state after the Evidence-Converged Context principle was adopted. It does not add a dataset, runner, backend, judge, or adapter surface.

## Closure Decision

| Area | Status | Scope |
|------|--------|-------|
| Core | Structurally validated | `commit:check`, TDS validation, planner parity, materialization check |
| Principle | Adopted | `Evidence-Converged Context` recorded in `docs/mesh/PRINCIPLES.md` and `docs/mesh/CONTEXT-MESH-CONVERGENCE.md` |
| Fixture pipeline | Certified | `pipeline-v1-rc` evidence retained for convergence loop 8 |
| Claude behavior | Certified for this run | `behavior-v1-rc` evidence retained and convergence gate passed |
| Codex | Structural only | Adapter materialization validates, no behavior backend certified |
| Cursor | Structural only | Adapter materialization validates, no behavior backend certified |
| Cross-adapter parity | Partial by design | Governance exists; behavior parity is not claimed |

Decision: `GO` for current context-mesh v1-rc closure. `NO-GO` for universal model behavior, Codex behavior parity, Cursor behavior parity, or statistical stability claims.

## Anchors

| Anchor | Value |
|--------|-------|
| Principle commit | `cc8ea65 Adopt evidence-converged context principle` |
| Latest fixture run | `pipeline-v1-rc-fixture-2026-05-05-convergence-08` |
| Latest behavior run | `behavior-v1-rc-claude-2026-05-05-convergence-08` |
| Behavior backend | `claude-cli` |
| Behavior model | `sonnet` |
| Runner version | `0.1.5` |
| Grader version | `deterministic-substring@0.1.6` |
| Dataset SHA | `c47a7b4be0604350c688f48d8088e944dc4b929804f2d6fe094626f5c902e5c6` |
| Behavior run Git HEAD | `bc1f1d26bc395f518a476cac1dc0ac41ef3204de` |
| Planned calls | `44` |
| Executed calls | `44` |

## Latest Fixture Evidence

Source: `docs/evidence/reports/context-mesh/pipeline-v1-rc-fixture-2026-05-05-convergence-08/`

| Metric | Value |
|--------|-------|
| Certification class | `pipeline-v1-rc` |
| Certification status | `GO` |
| Plan/run parity | `1.0` |
| Raw evidence coverage | `1.0` |
| Trigger pass rate full | `1.0` |
| Trigger pass rate none | `0.0` |
| Behavioral lift | `1.0` |
| Distractor leak rate | `0.0` |
| Backend error count | `0` |

Fixture ablation losses:

| Gate | Loss |
|------|------|
| Think Before Coding | `2` |
| Simplicity First | `2` |
| Surgical Changes | `2` |
| Goal-Driven Execution | `1` |

## Latest Claude Evidence

Source: `docs/evidence/reports/context-mesh/behavior-v1-rc-claude-2026-05-05-convergence-08/`

| Metric | Value |
|--------|-------|
| Certification class | `behavior-v1-rc` |
| Certification status | `GO` |
| Convergence gate | `CONVERGED` |
| Plan/run parity | `1.0` |
| Raw evidence coverage | `1.0` |
| Trigger pass rate full | `0.8571` |
| Trigger pass rate none | `0.1429` |
| Behavioral lift | `0.7142` |
| Distractor fail rate | `0.5` |
| Distractor leak rate | `0.0` |
| Backend error count | `0` |

Claude ablation losses:

| Gate | Loss | Closure interpretation |
|------|------|------------------------|
| Think Before Coding | `2` | Keep |
| Simplicity First | `1` | Certified at minimum floor; adversarial follow-up remains useful |
| Surgical Changes | `2` | Keep |
| Goal-Driven Execution | `1` | Certified at minimum floor; adversarial follow-up remains useful |

## Evidence Limits

- The behavior claim is scoped to one Claude run, one dataset SHA, one grader version, one backend, and one model.
- The Claude backend uses Claude Code through `claude-cli`; it is not a bare API execution path.
- Deterministic substring grading is intentionally strict and can be wording-sensitive.
- `distractor_fail_rate` was `0.5`, but confirmed `distractor_leak_rate` was `0.0`; this closure treats literal distractor failure separately from leak.
- Codex and Cursor are not behavior-certified.
- Cross-adapter parity is governance-ready, not behavior-certified.
- No N>1 stability, confidence interval, cost ROI, or universal model claim is made here.

## Next Loop

Recommended next loop: `Adapter Parity Readiness`.

Goal:

```text
source contract -> adapter materialization -> benchmark condition
```

Success criteria:

| Criterion | Required result |
|-----------|-----------------|
| Source contract | One neutral contract remains canonical |
| Adapter materialization | Codex, Claude, and Cursor materialize without drift |
| Benchmark condition | Each adapter can be mapped to benchmark conditions without exposing matrix labels to the backend |
| Parity claim | Structural and contract parity only unless behavior evidence exists |

Do not start this next loop by adding behavior backends. First prove the adapter surfaces preserve the same behavioral contract without semantic drift.
