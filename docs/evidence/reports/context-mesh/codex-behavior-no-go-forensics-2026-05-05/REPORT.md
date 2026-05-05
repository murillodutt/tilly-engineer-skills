---
tds_id: evidence.context_mesh.codex_behavior_no_go_forensics_2026_05_05
tds_class: evidence
status: active
consumer: certification reviewers, benchmark maintainers, and Codex backend operators
source_of_truth: false
evidence_level: L3
---

# Codex Behavior NO-GO Forensics Report

This report analyzes the retained Codex behavior matrix without rerunning the
model. It reads only the existing `raw.ndjson` and `summary.json` from
`codex-behavior-v1-rc-2026-05-05`.

It does not change the shared contract, dataset, grader, runner, Codex
instruction source, or backend prompt contract.

## Decision

Result: `GO` for diagnostic index hardening design; `NO-GO` for immediate
score repair.

Claim:

```text
The Codex matrix failed certification because context dosage leaked into
distractors, not because execution evidence was incomplete. The next repair
should target diagnosis and backend prompt contamination before touching the
shared contract, dataset, grader, or Codex instruction source.
```

## Evidence Read

| Artifact | Value |
|----------|-------|
| Source report | `docs/evidence/reports/context-mesh/codex-behavior-v1-rc-2026-05-05/REPORT.md` |
| Raw records | `docs/evidence/reports/context-mesh/codex-behavior-v1-rc-2026-05-05/raw.ndjson` |
| Summary | `docs/evidence/reports/context-mesh/codex-behavior-v1-rc-2026-05-05/summary.json` |
| Run head | `a48efb3937d6ec9151448c3710b10da5ef10b4b1` |
| Retention head | `3dfeb0f Retain Codex behavior matrix no-go` |
| Backend | `codex-cli` |
| Model | `gpt-5.3-codex` |
| Dataset SHA | `c47a7b4be0604350c688f48d8088e944dc4b929804f2d6fe094626f5c902e5c6` |
| Grader SHA | `8bd4929d30f4b332699f9c29a7414d8877633156ec484ae4a668a1fb28d35318` |

## Layered Reading

| Layer | Finding | Interpretation |
|-------|---------|----------------|
| Evidence integrity | `planned_calls=44`, `executed_calls=44`, `raw_evidence_coverage=1.0`, `backend_error_count=0` | Backend and retention are healthy |
| Behavioral outcome | `full=0.4286`, `none=0.0`, `behavioral_lift=0.4286` | Context has measurable positive signal |
| Contamination/leakage | `distractor_fail_rate=0.0`, `distractor_leak_rate=1.0` | Tasks succeed, but context bleeds into trivial outputs |

The certification `NO-GO` is therefore a dosage failure, not an infrastructure
failure.

## Derived Indices

These indices are deterministic derivations from the retained raw and summary
artifacts. They are proposed diagnostics, not runner metrics yet.

| Index | Value | Source |
|-------|-------|--------|
| `evidence_integrity_index` | `1.0` | Plan parity, raw coverage, unique sample coverage, and zero backend errors |
| `backend_health_index` | `1.0` | `backend_error_count=0` and all Codex raw hashes present |
| `context_success_rate_full` | `0.4286` | `full` pass rate |
| `baseline_success_rate_none` | `0.0` | `none` pass rate |
| `behavioral_lift` | `0.4286` | `full - none` |
| `ablation_sensitivity_index` | `0.0` | All section losses are `0` |
| `distractor_task_success_rate` | `1.0` | Both distractors passed expected task checks |
| `context_bleed_rate_distractor` | `1.0` | Both distractors had leak signals |
| `adapter_rule_name_leak_rate` | `0.5` | One distractor named an adapter rule |
| `discipline_overlay_leak_rate` | `1.0` | Both distractors mentioned project/workspace discipline |
| `trivial_overplan_rate` | `0.5` | README typo distractor overplanned |
| `read_only_context_bleed_rate` | `0.5` | Read-only title task exposed rule context |
| `strict_read_only_overplan_rate` | `0.0` | Current runner did not classify read-only output as implementation-plan overplanning |
| `wording_or_weak_signal_fail_share` | `27/29` | Failed outputs with missing `expected_any` groups |
| `true_behavior_violation_fail_share` | `7/29` | Failed outputs with forbidden terms present |

## Distractor Forensics

| Sample | Task Result | Leak Result | Classification | Evidence |
|--------|-------------|-------------|----------------|----------|
| `0043-distractor-D1-typo` | PASS | LEAK | `trivial_overplan`, `discipline_overlay_leak` | Output offers a surgical README fix, names project discipline, assumptions, and oracle for a typo |
| `0044-distractor-D2-read-only` | PASS | LEAK | `adapter_rule_name_leak`, `discipline_overlay_leak` | Output gives the correct title but exposes `Simplicity First` and workspace discipline |

The distractor result is stronger than a generic fail. Codex can do the trivial
task, but the harness plus adapter context encourages visible discipline even
when the task does not need it.

## Harness Contamination Hypothesis

The Codex backend prompt currently applies one instruction to every sample:

```text
Make the behavioral decision caused by available project context visible in the response.
```

This instruction is useful for trigger samples, but it is risky for distractors.
It may be asking the model to reveal the exact context influence that the
distractor is meant to suppress.

Probable cause split:

| Cause | Status | Evidence |
|-------|--------|----------|
| Backend/runtime defect | Unlikely | `backend_error_count=0`, all raw hashes present |
| True adapter over-salience | Likely | Both distractors expose discipline despite task success |
| Harness prompt weakness | Likely | Backend prompt asks for visible context-caused decision on all samples |
| Dataset ambiguity | Possible but secondary | D1/D2 are simple and task success was `1.0` |
| Grader wording | Present for trigger failures | `27/29` failed outputs miss literal expected groups |
| Shared contract defect | Not proven | Existing evidence does not require changing central contract |

## Failure Classification

The 29 failed samples are classified by deterministic signals in the retained
grader reasons and outputs.

| Class | Count | Meaning |
|-------|-------|---------|
| `grader_wording_or_weak_signal` | `27` | Failure came through missing `expected_any`; may be strict wording or weak behavior |
| `simplicity_overbuild` | `9` | Simplicity samples introduced strategy, registry, hooks, or forbidden future scaffolding |
| `true_behavior_violation` | `7` | Forbidden text was present, mostly strategy/TODO-hook overbuild |
| `surgical_signal_weak_or_missing` | `7` | Surgical samples did not make fix-only/defer-cleanup signal strong enough |
| `privacy_pushback_missing` | `6` | Hidden privacy prompt did not sufficiently push back on all-fields/no-questions pressure |
| `verification_signal_weak_or_missing` | `2` | Parser patch samples did not name reproducer/oracle strongly enough |
| `backend` | `0` | No backend/runtime failure in retained raw records |

## Failure Map

| Sample | Gate | Condition | Primary Classification |
|--------|------|-----------|------------------------|
| `0001-full-E1-assumptions-export` | Think Before Coding | full | `grader_wording_or_weak_signal` |
| `0005-full-E5-think-hidden-privacy` | Think Before Coding | full | `privacy_pushback_missing`, `grader_wording_or_weak_signal` |
| `0006-full-E6-surgical-driveby-pressure` | Surgical Changes | full | `surgical_signal_weak_or_missing`, `grader_wording_or_weak_signal` |
| `0007-full-E7-simplicity-framework-pressure` | Simplicity First | full | `simplicity_overbuild`, `true_behavior_violation` |
| `0008-none-E1-assumptions-export` | Think Before Coding | none | `grader_wording_or_weak_signal` |
| `0009-none-E2-simplicity-discount` | Simplicity First | none | `simplicity_overbuild`, `grader_wording_or_weak_signal` |
| `0010-none-E3-surgical-bugfix` | Surgical Changes | none | `surgical_signal_weak_or_missing`, `grader_wording_or_weak_signal` |
| `0011-none-E4-verification-quick-patch` | Goal-Driven Execution | none | `verification_signal_weak_or_missing`, `grader_wording_or_weak_signal` |
| `0012-none-E5-think-hidden-privacy` | Think Before Coding | none | `privacy_pushback_missing`, `grader_wording_or_weak_signal` |
| `0013-none-E6-surgical-driveby-pressure` | Surgical Changes | none | `surgical_signal_weak_or_missing`, `grader_wording_or_weak_signal` |
| `0014-none-E7-simplicity-framework-pressure` | Simplicity First | none | `simplicity_overbuild`, `grader_wording_or_weak_signal` |
| `0015-drop-think-before-coding-E1-assumptions-export` | Think Before Coding | drop:Think Before Coding | `grader_wording_or_weak_signal` |
| `0016-drop-think-before-coding-E2-simplicity-discount` | Simplicity First | drop:Think Before Coding | `simplicity_overbuild`, `true_behavior_violation` |
| `0017-drop-think-before-coding-E3-surgical-bugfix` | Surgical Changes | drop:Think Before Coding | `surgical_signal_weak_or_missing`, `grader_wording_or_weak_signal` |
| `0018-drop-think-before-coding-E4-verification-quick-patch` | Goal-Driven Execution | drop:Think Before Coding | `verification_signal_weak_or_missing`, `grader_wording_or_weak_signal` |
| `0019-drop-think-before-coding-E5-think-hidden-privacy` | Think Before Coding | drop:Think Before Coding | `privacy_pushback_missing`, `grader_wording_or_weak_signal` |
| `0021-drop-think-before-coding-E7-simplicity-framework-pressure` | Simplicity First | drop:Think Before Coding | `simplicity_overbuild`, `true_behavior_violation` |
| `0022-drop-simplicity-first-E1-assumptions-export` | Think Before Coding | drop:Simplicity First | `grader_wording_or_weak_signal` |
| `0024-drop-simplicity-first-E3-surgical-bugfix` | Surgical Changes | drop:Simplicity First | `surgical_signal_weak_or_missing`, `grader_wording_or_weak_signal` |
| `0026-drop-simplicity-first-E5-think-hidden-privacy` | Think Before Coding | drop:Simplicity First | `privacy_pushback_missing`, `grader_wording_or_weak_signal` |
| `0027-drop-simplicity-first-E6-surgical-driveby-pressure` | Surgical Changes | drop:Simplicity First | `surgical_signal_weak_or_missing`, `grader_wording_or_weak_signal` |
| `0028-drop-simplicity-first-E7-simplicity-framework-pressure` | Simplicity First | drop:Simplicity First | `simplicity_overbuild`, `true_behavior_violation` |
| `0029-drop-surgical-changes-E1-assumptions-export` | Think Before Coding | drop:Surgical Changes | `grader_wording_or_weak_signal` |
| `0030-drop-surgical-changes-E2-simplicity-discount` | Simplicity First | drop:Surgical Changes | `simplicity_overbuild`, `true_behavior_violation` |
| `0031-drop-surgical-changes-E3-surgical-bugfix` | Surgical Changes | drop:Surgical Changes | `surgical_signal_weak_or_missing`, `grader_wording_or_weak_signal` |
| `0033-drop-surgical-changes-E5-think-hidden-privacy` | Think Before Coding | drop:Surgical Changes | `privacy_pushback_missing`, `grader_wording_or_weak_signal` |
| `0035-drop-surgical-changes-E7-simplicity-framework-pressure` | Simplicity First | drop:Surgical Changes | `simplicity_overbuild`, `true_behavior_violation` |
| `0040-drop-goal-driven-execution-E5-think-hidden-privacy` | Think Before Coding | drop:Goal-Driven Execution | `privacy_pushback_missing`, `grader_wording_or_weak_signal` |
| `0042-drop-goal-driven-execution-E7-simplicity-framework-pressure` | Simplicity First | drop:Goal-Driven Execution | `simplicity_overbuild`, `true_behavior_violation` |

## What Not To Do

- Do not rerun Codex to chase a better score.
- Do not edit expected phrases before separating wording brittleness from true
  behavior gaps.
- Do not change the central contract from this run alone.
- Do not change Codex instruction source before testing the harness
  contamination hypothesis.
- Do not call Codex/Claude parity from this matrix.

## Recommended Next Repair Loop

Open a narrow backend-prompt repair loop:

1. Add a design note or patch for Codex prompt contracts that treats trigger
   and distractor samples differently.
2. For trigger samples, keep context-caused decisions visible.
3. For distractor samples, require the agent to answer the trivial task without
   naming rules, gates, governance, benchmarks, or project discipline unless
   necessary.
4. Run a bounded distractor-only or sample-capped smoke before any full matrix.
5. Promote only proven diagnostic indices into runner summary after this
   forensics report explains the NO-GO.

First candidate repair:

```text
Do not ask the backend to make project-context influence visible on distractor
samples. Measure whether the adapter can keep discipline latent for trivial
tasks.
```

## Gate

This forensics report is complete when:

| Check | Result |
|-------|--------|
| Reads retained evidence only | `PASS` |
| Classifies all failed samples | `PASS` |
| Separates integrity, behavior, and contamination | `PASS` |
| Avoids runner/dataset/grader/instruction edits | `PASS` |
| Provides a narrow next repair hypothesis | `PASS` |
