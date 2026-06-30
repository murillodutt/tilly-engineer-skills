---
tds_id: roadmap.goal_super_spec.goal_maestro_p1_cross_host_report_parity
tds_class: roadmap
status: active
consumer: maintainers, Goal Maestro authors, adapter authors, report authors, installed-canary operators, and execution agents
source_of_truth: true
evidence_level: L2
tver: 0.1.0
---

# GOAL-SUPER-SPEC: Goal Maestro P1 Cross-Host Report Parity

Status: active corrective Super SPEC.

Purpose: after P0 blocks false closure, make the Goal Maestro feedback
experience consistent across Codex, Claude Code, and Cursor. P1 does not relax
P0. It standardizes what each host produces and how users see the result.

This is the second of three linked corrective Super SPECs. It carries exactly
six slices: SPEC-025 through SPEC-030.

## Dependency

P1 must not start before P0 can fail the observed canary defects. If P0 has not
closed, stop with `NEEDS_P0_HARNESS_ORCHESTRATION_FEEDBACK_FIDELITY`.

## Central Rule

```text
Cross-host parity means equivalent evidence and report semantics, not identical
host packaging or copied prose.
```

## Protected Baseline

- Codex and Claude Code keep skill-package behavior through their native skill
  surfaces.
- Cursor keeps lazy-rule coverage and must not claim fake skill parity.
- Reports stay local and static.
- Heartbeat remains opt-in, read-only, and non-scheduling.

## Stop States

- `NEEDS_CROSS_HOST_EVIDENCE_MATRIX`
- `NEEDS_HOST_ADAPTER_PARITY`
- `NEEDS_CANARY_EVALUATION_GATE`
- `NEEDS_CONTEXT_RECEIPT`
- `NEEDS_HTML_PRECISION`
- `NEEDS_REPORT_FAILURE_HIGHLIGHTING`
- `PASS_P1_CROSS_HOST_REPORT_PARITY`

## Execution Slices

### SPEC-025 - Cross-Host Evidence Matrix

Goal: define the minimum package every host must produce or honestly classify as
not applicable.

Required behavior:

- Codex, Claude Code, and Cursor runs produce or classify the same evidence
  classes: ledger, pre-edit gate, enrichment packet, document analysis, visual
  packet, browser metrics, thermometer package, context receipt, heartbeat
  sidecar, install chronology, and commit enforcement classification.
- The matrix records host-native path, status, hash, and missing-reason.

Acceptance:

- A host missing an evidence class without classification fails.
- Cursor may use lazy-rule coverage for capability documentation but must still
  report evidence class status honestly.
- Stop state: `NEEDS_CROSS_HOST_EVIDENCE_MATRIX`.

### SPEC-026 - Host Adapter Parity

Goal: ensure delivered behavior is equivalent while packaging stays native.

Required behavior:

- Codex source under `src/adapters/codex/**` materializes to `.agents/**`.
- Claude Code source under `src/adapters/claude/**` materializes to
  `.claude/**`.
- Cursor source under `src/adapters/cursor/**` materializes lazy runtime
  capability coverage without fake skill claims.
- Adapter parity oracles compare contracts, not file layout sameness.

Acceptance:

- Cursor depending silently on `.agents` for Goal Maestro feedback fails unless
  classified as fallback evidence.
- Codex/Claude drift in ledger/report contract fails.
- Stop state: `NEEDS_HOST_ADAPTER_PARITY`.

### SPEC-027 - Canary Evaluation Gate

Goal: make validation runs evaluate the harness, not just the delivered result.

Required behavior:

- Add a canary evaluation model with separate scores:
  `delivered_output_quality`, `harness_linearity`, `enrichment_quality`,
  `evidence_quality`, `thermometer_accuracy`, `heartbeat_delivery`,
  `adapter_parity`, and `install_chronology`.
- Delivered output quality cannot mask harness failure.
- The final canary verdict uses the weakest required harness dimension.

Acceptance:

- A strong delivered output with missing Thermometer fidelity fails harness pass.
- A complete harness with weaker delivered-output quality reports the output gap
  separately.
- Stop state: `NEEDS_CANARY_EVALUATION_GATE`.

### SPEC-028 - Context Receipt

Goal: make the short in-chat report mandatory and consistent.

Required behavior:

- Every `--execute-loop` closeout emits the compact receipt in chat or records a
  reason it could not be emitted.
- Receipt carries five signals: Delivery, Fidelity, Proof, Efficiency,
  Protection.
- Receipt includes active loop, SPEC summary, unproven count, report path, and
  next action.
- Receipt cannot contradict the full package.

Acceptance:

- HTML-only feedback fails.
- Receipt that says pass while metrics say unproven fails.
- Stop state: `NEEDS_CONTEXT_RECEIPT`.

### SPEC-029 - HTML Report Precision

Goal: make the static HTML useful for audit, not only presentation.

Required behavior:

- HTML shows declared SPECs vs executed SPECs.
- HTML shows gate statuses: passed, failed, skipped, not required, blocked.
- HTML shows timeline order and install chronology.
- HTML shows selected loop details without dashboard or runtime data loading.

Acceptance:

- HTML that hides missing SPECs fails.
- HTML that uses runtime script, fetch, storage, CDN, or telemetry fails.
- Stop state: `NEEDS_HTML_PRECISION`.

### SPEC-030 - Report Failure Highlighting

Goal: make reports surface weakness instead of smoothing it away.

Required behavior:

- Missing Flash-Fry, missing cloud-search classification, weak visual evidence,
  manual commit mode, unproven cache/cost fields, and Thermometer parser repairs
  appear as explicit report findings.
- Failure highlighting affects five-signal scores.
- The report distinguishes failure, blocked, not required, and unproven.

Acceptance:

- A report that hides skipped gates under overall pass fails.
- A report that highlights gaps and blocks complete closeout when required
  fields are missing passes.
- Stop state: `NEEDS_REPORT_FAILURE_HIGHLIGHTING`.

## Required P1 Oracles

- Cross-host evidence matrix oracle.
- Adapter parity oracle.
- Canary evaluation classifier.
- Context receipt coherence oracle.
- Static HTML precision and safety oracle.
- Failure-highlighting fixture suite.

## Done Means

P1 is complete only when the same unchanged installed-target canary produces
comparable local evidence and feedback across Codex, Claude Code, and Cursor,
without claiming false host parity or hiding required gaps.
