---
tds_id: evidence.context_mesh.codex_behavior_matrix_readiness_2026_05_05
tds_class: evidence
status: active
consumer: certification reviewers and Codex backend operators
source_of_truth: false
evidence_level: L3
---

# Codex Behavior Matrix Readiness Report

This report prepares Stage 3 of the V1 convergence loop. It does not run the
Codex behavior matrix, change the shared contract, change the dataset, change
the grader, change the runner, or claim Codex behavior certification.

## Decision

Result: `GO` for a governed Codex behavior matrix attempt after this readiness
report is retained.

Claim:

```text
The Codex backend has smoke evidence and a bounded command shape for a 44-call
behavior matrix. The next run may produce GO or NO-GO behavior evidence, but
either outcome must be retained before repair.
```

## Head Fields

| Field | Value |
|-------|-------|
| `gate_head` | `e67bf9808c7cc55accc151a1c91ded0215d199c7 Retain adapter behavior readiness design` |
| Stage 1 backend head | `6806b580ff94bbbd39a2750945dc49b015979829 Add codex CLI benchmark backend` |
| Stage 2 smoke retention head | `97649bf Retain Codex smoke evidence` |
| `run_head` | To be the repository HEAD checked out when the 44-call matrix is executed |
| `retention_head_pending` | `true` before the future behavior report is committed |
| `retention_head_final` | Resolved by the Git commit that retains the future behavior report |

Future behavior evidence must not leave `retention_head` as an unexplained
stale value. If the runner can only know the pre-commit state, the report must
declare `retention_head_pending=true` and the retaining commit must be recorded
in the closure text or a follow-up retained report.

## Frozen Inputs

| Input | Value |
|-------|-------|
| Shared contract | `docs/mesh/CONTRACT-MANIFEST.yml` |
| Dataset path | `benchmarks/context-mesh/eval-dataset.json` |
| Dataset SHA | `c47a7b4be0604350c688f48d8088e944dc4b929804f2d6fe094626f5c902e5c6` |
| Grader version | `deterministic-substring@0.1.6` |
| Grader SHA | `8bd4929d30f4b332699f9c29a7414d8877633156ec484ae4a668a1fb28d35318` |
| Runner version | `0.1.6` |
| Codex model | `gpt-5.3-codex` |
| Shared mesh status | Frozen |

## Stage 2 Evidence Basis

| Evidence | Value |
|----------|-------|
| Smoke report | `docs/evidence/reports/context-mesh/codex-smoke-2026-05-05-6806b58/REPORT.md` |
| Backend | `codex-cli` |
| Model | `gpt-5.3-codex` |
| Executed calls | `1` |
| Planned calls | `44` |
| Backend errors | `0` |
| Raw evidence | `raw.ndjson` retained |
| Captured hashes | stdout JSONL, stderr, adapter workspace, final output |
| Smoke certification status | `NO-GO` by full-matrix thresholds, expected for `sample_cap=1` |

The Stage 2 smoke only proves route execution and evidence retention. It does
not predict the behavior matrix result.

## Planned Command

Dry-run before execution:

```bash
python3 scripts/context_mesh_run.py \
  --backend codex-cli \
  --model gpt-5.3-codex \
  --allow-full-codex-run \
  --dry-run
```

Behavior matrix command:

```bash
npm run benchmark:run -- \
  --backend codex-cli \
  --model gpt-5.3-codex \
  --run-id codex-behavior-v1-rc-2026-05-05 \
  --timeout-seconds 180 \
  --allow-full-codex-run
```

Expected matrix size:

```text
planned_calls=44
conditions=full, none, drop:<section>
trigger_evals=7
distractors=2
```

## Cost And Time Bounds

The Codex CLI route does not expose a dollar budget flag. Stage 3 therefore
uses operational bounds instead of a cost cap.

| Bound | Value |
|-------|-------|
| Model allowlist | Runner-enforced for `codex-cli` |
| Explicit full-run flag | `--allow-full-codex-run` required |
| Timeout per call | `180` seconds |
| Maximum calls | `44` |
| Worst-case wall-clock estimate | Up to about `132` minutes if every call hits timeout sequentially |
| Practical expected runtime | Unknown until first full retained run |
| Cost estimate | Unknown from local CLI; treat as paid/valuable execution |

Do not rerun the matrix just to improve score. Any failed or partial matrix
must be retained and classified first.

## Stop Conditions

Stage 3 must stop downstream interpretation and repair if any condition occurs:

| Condition | Action |
|-----------|--------|
| `codex-cli` command missing | Stop; classify as `codex_cli_missing` |
| Auth/login failure | Stop; classify as `codex_auth_failure` |
| Any backend error in retained summary | Retain report; classify before repair |
| Missing `raw.ndjson`, `summary.json`, `REPORT.md`, or `manifest.json` | Stop; treat as evidence retention failure |
| Missing stdout/stderr/final output hashes in any raw record | Stop; treat as backend evidence failure |
| Matrix labels appear in model-facing prompt | Stop; treat as prompt contamination |
| Dataset, grader, or shared contract changes before run | Stop; create a new readiness report with new hashes |
| `commit:check` fails before or after run | Stop; fix the gate before certification language |

The current runner does not fail fast on the first backend error during a full
matrix. Therefore `backend_error_count > 0` is a post-run NO-GO condition for
behavior certification, not permission to silently rerun.

## Interpretation Rules

| Result | Interpretation |
|--------|----------------|
| `backend_error_count=0` and full thresholds pass | Candidate Codex behavior evidence for this dataset/hash/backend/model/run |
| `backend_error_count=0` and behavior thresholds fail | Valid Codex behavior NO-GO; classify grader, prompt, adapter, or rule weakness |
| `backend_error_count>0` | Backend/runtime NO-GO; do not tune behavior first |
| Grader fail with plausible behavior | Classify as wording sensitivity; do not edit dataset without retained failure analysis |
| Distractor fail without leak signal | Do not call it context leak unless leak heuristics confirm it |
| `full <= none` | Behavior NO-GO until explained by retained analysis |

## Evidence Package Required

The future run must retain:

```text
docs/evidence/reports/context-mesh/codex-behavior-v1-rc-2026-05-05/
  manifest.json
  raw.ndjson
  summary.json
  REPORT.md
  graders-sha.json
```

Required fields include:

| Field | Requirement |
|-------|-------------|
| `dataset_sha` | Must match frozen input unless a new readiness report exists |
| `grader_sha` | Must match frozen input unless a new readiness report exists |
| `backend` | `codex-cli` |
| `model` | `gpt-5.3-codex` |
| `gate_head` | Adapter behavior readiness gate |
| `run_head` | Git HEAD used during matrix execution |
| `retention_head` | Final retaining commit or explicit pending/final policy |
| `prompt_sha` | Present on every raw record |
| `output_sha` | Present on every raw record |
| `codex_stdout_jsonl_sha` | Present on every raw record |
| `codex_stderr_sha` | Present on every raw record |
| `codex_adapter_workspace_sha` | Present on every raw record |
| `codex_final_output_sha` | Present on every non-backend-error raw record |

## NO-GO For Stage 3 Execution

- Running without `--allow-full-codex-run`.
- Running without explicit `--model gpt-5.3-codex`.
- Running with dirty contract, dataset, grader, or runner changes.
- Treating a smoke or partial run as behavior certification.
- Editing expected phrases or grader logic before retaining the first full
  Codex matrix outcome.
- Declaring Codex/Claude parity from one Codex run.

## Next Step

After this report is committed and `npm run commit:check` is green, run the
dry-run command above. If the dry-run shows `planned_calls=44` and
`plan_parity=true`, execute the behavior matrix once and retain the result
before any repair.
