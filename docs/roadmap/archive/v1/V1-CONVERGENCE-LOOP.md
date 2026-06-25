---
tds_id: roadmap.v1_convergence_loop
tds_class: roadmap
status: archived
consumer: maintainers, certification reviewers, and convergence-loop operators
source_of_truth: false
evidence_level: L2
---

# V1 Convergence Loop

This document defines the large convergence loop from the current certified readiness state to a final v1 GO/NO-GO decision.

Status note, 2026-05-06: this loop is retained as planning lineage. The final v1 GO report now exists, and v1.1 closure artifacts cover retention metadata, installer smoke, Claude plugin oracle, reference graph validation, and Cursor behavior readiness.

It is a loop, not a wish list:

```text
Design -> Build -> Smoke -> Behavior -> Fail -> Fix -> Certify -> Decide
```

Each stage must either produce retained evidence or stop with a named NO-GO.

## Current Anchor

The current package state has already reached:

| Layer | State |
|-------|-------|
| Context mesh closure | `GO` for v1-rc closure |
| Adapter parity readiness | `GO` for structural/contract parity |
| Adapter behavior readiness | `GO` as design |
| Codex backend readiness | `GO` as design |
| Claude behavior | `GO` for the retained run only |
| Codex behavior | Not certified |
| Cursor behavior | Not certified |
| Final v1 decision | Not emitted |

The next unresolved evidence gap is Codex behavior.

## Loop Invariants

These invariants hold until failure evidence forces a change:

| Surface | Rule |
|---------|------|
| Contract | Frozen |
| Dataset | Frozen |
| Grader | Frozen |
| Claude retained evidence | Do not rewrite |
| Adapter materialization | Must remain green |
| Matrix labels | Never exposed to backend prompts |
| Claims | Behavior claim requires behavior evidence |

Changing the shared contract, dataset, or grader is allowed only after a retained failure explains why the existing surface cannot answer the current question.

## Stage 1: Codex Backend Implementation

Goal:

```text
Implement the smallest backend that measures Codex adapter behavior, not
generic model behavior.
```

Inputs:

| Input | Source |
|-------|--------|
| Backend route | `codex-behavior-backend-readiness-2026-05-05` |
| Adapter context | Materialized Codex workspace |
| Runner | Existing `scripts/context_mesh_run.py` backend interface |
| Dataset | Current context-mesh dataset hash |
| Grader | Current deterministic substring grader hash |

Implementation checklist:

- [ ] Add a `codex-cli` backend behind the existing runner backend interface.
- [ ] Materialize a temporary Codex adapter workspace per condition.
- [ ] Use `codex exec` non-interactively.
- [ ] Use read-only sandbox and no approvals.
- [ ] Capture stdout JSONL.
- [ ] Capture stderr.
- [ ] Capture final output file.
- [ ] Hash prompt, final output, stdout JSONL, stderr, and adapter workspace.
- [ ] Normalize CLI missing, auth failure, timeout, non-zero exit, missing output, and refusal.
- [ ] Enforce subprocess timeout.
- [ ] Enforce model allowlist and sample cap.
- [ ] Avoid changing contract, dataset, grader, Claude evidence, or UI.

Stage 1 GO:

- [ ] `npm run commit:check` passes.
- [ ] Backend dry run or fixture path proves the new backend wiring can produce report-shaped output without a paid/full behavior matrix.
- [ ] No Codex behavior certification is claimed.

Stage 1 NO-GO:

- [ ] Backend cannot isolate prompt/workspace context.
- [ ] Backend cannot retain raw output.
- [ ] Backend cannot enforce timeout.
- [ ] Backend measures generic model output without materialized Codex adapter context.

## Stage 2: Codex Smoke Evidence

Goal:

```text
Run the smallest real Codex sample that proves the backend can execute and
retain evidence safely.
```

Scope:

- [ ] One trigger sample.
- [ ] One condition only, unless the runner requires a minimal pair.
- [ ] Explicit model.
- [ ] Explicit run authorization.
- [ ] No full matrix.
- [ ] No behavior certification.

Stage 2 GO:

- [ ] Raw output retained.
- [ ] Hashes retained.
- [ ] Timeout/cost controls demonstrated.
- [ ] Failure normalization works if the sample fails.
- [ ] Report includes `gate_head`, `run_head`, and `retention_head`.

Stage 2 NO-GO:

- [ ] CLI execution depends on unreproducible desktop/thread state.
- [ ] Output cannot be captured deterministically.
- [ ] Auth or refusal errors are ambiguous.
- [ ] Any matrix label reaches the model prompt.

## Stage 3: Codex Behavior Matrix

Goal:

```text
Run Codex behavior certification against the existing matrix.
```

Stage 3 GO criteria:

- [ ] `planned_calls == executed_calls`.
- [ ] `raw_evidence_coverage == 1.0`.
- [ ] `trigger_pass_rate_full > trigger_pass_rate_none`.
- [ ] `distractor_leak_rate == 0.0`.
- [ ] `backend_error_count == 0`.
- [ ] Every failure has excerpt and reason.
- [ ] Every sample records prompt and output hashes.
- [ ] Report states evidence limits.

Stage 3 interpretation:

| Result | Action |
|--------|--------|
| Codex GO | Retain evidence and update v1 checklist |
| Codex NO-GO from backend/auth/timeout | Fix backend, rerun smoke before matrix |
| Codex NO-GO from prompt weakness | Retain failure, then decide whether dataset or contract change is justified |
| Codex NO-GO from generic adapter mismatch | Revisit materialized workspace route |

Do not patch the dataset or grader inside the same stage that discovers a behavior failure. First retain the failure and classify it.

## Stage 4: Cursor Decision

Goal:

```text
Decide whether Cursor is measured, deferred, or explicitly excluded from the
first v1 behavior claim.
```

Options:

| Option | Meaning | Evidence required |
|--------|---------|-------------------|
| Measure | Implement a Cursor behavior route | Cursor backend readiness report |
| Defer | Keep Cursor structural only for v1 | Explicit defer rationale |
| Exclude | State Cursor behavior is not part of v1 | Final v1 claim boundary |

Stage 4 GO:

- [ ] Cursor path decision is retained.
- [ ] No report silently implies Cursor behavior parity.
- [ ] Final v1 scope is unambiguous.

## Stage 5: Final V1 Certification

Goal:

```text
Emit a final v1 GO/NO-GO decision with exact claim boundaries.
```

Required sections:

- [ ] Scope.
- [ ] Evidence anchors.
- [ ] Certified claims.
- [ ] Explicit non-claims.
- [ ] Adapter status matrix.
- [ ] Behavior metrics by certified backend.
- [ ] Known limits.
- [ ] Next research debt.
- [ ] GO/NO-GO decision.

Possible decisions:

| Decision | Meaning |
|----------|---------|
| `GO: v1 Claude+Codex` | Claude and Codex have retained behavior evidence; Cursor scoped out or deferred |
| `GO: v1 Claude-only` | Claude behavior remains the only behavior claim; Codex/Cursor explicitly scoped out |
| `NO-GO` | Evidence is insufficient or contradictory |

The final decision must prefer a smaller honest v1 over a larger ambiguous one.

## Convergence Stop Rules

Stop the loop only for material blockers:

- [ ] Worktree or retained evidence cannot be reconciled.
- [ ] Raw evidence cannot be captured.
- [ ] Adapter context cannot be isolated.
- [ ] Shared contract/dataset/grader must change, but no retained failure justifies the change.
- [ ] A report would need to claim behavior from structure.
- [ ] Cost/auth risk is not bounded.

Do not stop just because a smoke or behavior run fails. Failure is loop input.

## Operating Rhythm

Use this rhythm for every stage:

```text
Frame -> Build smallest increment -> Run smallest oracle -> Retain failure or
success -> Fix only the proven cause -> Rerun -> Commit -> Reassess claim
```

No stage should end with "probably works." It ends with retained evidence, named NO-GO, or a deliberately scoped next loop.
