---
tds_id: roadmap.v1_goal_checklist
tds_class: roadmap
status: active
consumer: maintainers, certification reviewers, and next-loop planners
source_of_truth: false
evidence_level: L2
---

# V1 Goal Checklist

This checklist preserves the project objective so future loops do not confuse
progress with the finish line.

## Objective

`tilly-engineer-skills` exists to turn engineering guidelines for coding agents
into behavioral contracts that are testable, portable, and certified across
adapter ecosystems.

The core claim is:

```text
Guidelines are not enough. A useful context package must prove that it changes
agent behavior, avoids unwanted leakage, survives adapter materialization, and
leaves auditable evidence.
```

## Base Idea

The project uses a neutral context mesh:

```text
canonical contract
-> adapter materialization
   -> Claude
   -> Codex
   -> Cursor
-> benchmark conditions
-> retained evidence
-> GO/NO-GO decision
```

The behavioral gates are:

| Gate | Purpose |
|------|---------|
| Think Before Coding | Surface assumptions and ambiguity before acting |
| Simplicity First | Avoid premature abstraction and speculative scope |
| Surgical Changes | Keep edits traceable to the request |
| Goal-Driven Execution | Close only against falsifiable success criteria |

## Current Certification Position

| Layer | Status | Evidence |
|-------|--------|----------|
| Canonical contract | Done | `docs/mesh/CONTRACT-MANIFEST.yml` |
| Context mesh principle | Done | `Evidence-Converged Context` adopted |
| Fixture pipeline | Done | `pipeline-v1-rc` convergence evidence retained |
| Claude behavior | Done for retained run only | `behavior-v1-rc` convergence evidence retained |
| Context mesh closure | Done | `context-mesh-v1-rc-closure-2026-05-05` |
| Adapter parity readiness | Done | `adapter-parity-readiness-2026-05-05` |
| Adapter behavior readiness | Done as design | `adapter-behavior-readiness-2026-05-05` |
| Codex backend readiness | Done as design | `codex-behavior-backend-readiness-2026-05-05` |
| Codex behavior run | Not done | Requires backend implementation and retained evidence |
| Cursor backend readiness | Not done or deferred | Requires explicit design/defer report |
| Cursor behavior run | Not done | Requires route, or explicit non-goal for v1 |
| Statistical stability | Not done | Current Claude behavior evidence is scoped, not N>1 |
| Final v1 decision | Not done | Requires explicit GO/NO-GO report |

## V1-RC Checklist

- [x] Define the four behavioral gates.
- [x] Create a canonical contract independent of any single adapter.
- [x] Materialize Claude, Codex, and Cursor adapter surfaces.
- [x] Validate planner and benchmark matrix shape.
- [x] Retain fixture pipeline evidence.
- [x] Retain first Claude behavior evidence.
- [x] Separate literal distractor failure from real distractor leak.
- [x] Run Build-Test-Fail-Fix convergence until Claude behavior reaches GO.
- [x] Adopt Evidence-Converged Context as an engineering principle.
- [x] Retain context-mesh v1-rc closure.
- [x] Certify adapter structural and contract parity readiness.
- [x] Retain adapter behavior readiness design.
- [x] Retain Codex behavior backend readiness design.
- [ ] Implement the smallest Codex behavior backend.
- [ ] Run Codex fixture or single-sample smoke evidence before full matrix.
- [ ] Run retained Codex behavior matrix only after smoke GO.
- [ ] Decide Cursor path: backend readiness, explicit defer, or non-goal for v1.
- [ ] Produce final v1 GO/NO-GO report.

## Full V1 Checklist

- [ ] Claude behavior evidence is either repeated with stronger stability or
      explicitly scoped as single-run evidence.
- [ ] Codex behavior evidence is retained, or Codex behavior is explicitly
      excluded from v1 with rationale.
- [ ] Cursor behavior evidence is retained, or Cursor behavior is explicitly
      excluded from v1 with rationale.
- [ ] Adapter behavior reports use `gate_head`, `run_head`, and
      `retention_head`.
- [ ] Dataset SHA, grader SHA, prompt SHA, output SHA, backend, and model are
      retained for every behavior run.
- [ ] No report claims universal model behavior.
- [ ] No report claims behavior parity from structural parity.
- [ ] No report claims section ROI beyond the evidence floor.
- [ ] Final v1 report states exact claims, limits, and next research debt.

## Do Not Forget

The project is close to v1-rc because the architecture is already right. It is
not yet full v1 because behavior has not been certified across adapters.

Do not solve that gap by adding more philosophy, more gates, or more UI.

The next valuable work is evidence:

```text
Codex backend implementation -> smoke evidence -> Codex behavior run
```

Only after that should the team decide whether Cursor is measured, deferred, or
excluded from the first v1 certification.

## Claim Boundaries

| Claim | Allowed now? | Reason |
|-------|--------------|--------|
| The context mesh has a certified fixture pipeline | Yes | Retained fixture evidence exists |
| Claude behavior improved on the retained run | Yes | Retained behavior evidence exists |
| Codex and Cursor preserve the contract structurally | Yes | Adapter parity readiness is GO |
| Codex behavior is certified | No | No retained Codex behavior run yet |
| Cursor behavior is certified | No | No retained Cursor behavior run yet |
| The package proves universal behavior improvement | No | Evidence is scoped by backend, model, dataset, and run |
| The package is ready for v1-rc decision | Nearly | Needs Codex/Cursor scope decision or Codex behavior evidence |
| The package is ready for full v1 | Not yet | Needs final claim boundary and behavior evidence/defer decisions |

## Next Loop

Recommended next loop:

```text
Codex Behavior Backend Implementation
```

Minimum scope:

- [ ] Use the existing Codex backend readiness report as the implementation
      contract.
- [ ] Materialize a temporary Codex adapter workspace.
- [ ] Invoke `codex exec` non-interactively.
- [ ] Capture stdout JSONL, stderr, final output, hashes, timeout, and errors.
- [ ] Prevent matrix labels from entering the prompt.
- [ ] Run a smoke sample before any full matrix.
- [ ] Retain evidence before claiming behavior.

Stop if:

- [ ] The backend depends on unreproducible desktop thread state.
- [ ] Raw output cannot be retained.
- [ ] Timeout cannot be enforced.
- [ ] The backend measures generic model behavior without the Codex adapter
      context.
- [ ] Implementing the backend requires changing the shared contract, dataset,
      or grader before failure evidence exists.
