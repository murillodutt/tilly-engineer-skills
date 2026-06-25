---
tds_id: evidence.context_mesh.codex_behavior_backend_readiness_2026_05_05
tds_class: evidence
status: active
consumer: certification reviewers and Codex backend implementers
source_of_truth: false
evidence_level: L3
---

# Codex Behavior Backend Readiness Report

This report decides whether a Codex behavior backend has a clean enough route to design before implementation. It does not implement a backend, run behavior, change the shared contract, change the dataset, change the grader, or claim Codex behavior certification.

## Decision

Result: `GO` for Codex behavior backend design.

Claim:

```text
Codex has a local non-interactive execution route suitable for backend design,
but no Codex behavior claim exists yet.
```

The route is not approved for certification runs until the backend is implemented with raw evidence capture, timeout normalization, and explicit cost controls.

## Head Fields

| Field | Value |
|-------|-------|
| `gate_head` | `e67bf9808c7cc55accc151a1c91ded0215d199c7 Retain adapter behavior readiness design` |
| `run_head` | `N/A` because this is design readiness, not a behavior run |
| `retention_head_pending` | `true` before this report is committed |
| `retention_head_final` | Resolved by the Git commit that retains this report |

Future behavior reports must replace `retention_head_pending` with a retained commit reference and must include a real `run_head`.

## Frozen Inputs

| Input | Value |
|-------|-------|
| Shared contract | `docs/mesh/CONTRACT-MANIFEST.yml` |
| Dataset path | `benchmarks/context-mesh/eval-dataset.json` |
| Dataset SHA | `c47a7b4be0604350c688f48d8088e944dc4b929804f2d6fe094626f5c902e5c6` |
| Grader version | `deterministic-substring@0.1.6` |
| Grader SHA | `8bd4929d30f4b332699f9c29a7414d8877633156ec484ae4a668a1fb28d35318` |
| Runner version | `0.1.5` |
| Shared mesh status | Frozen |

## Local Codex Route

Local discovery found:

| Item | Value |
|------|-------|
| CLI path | `/Applications/Codex.app/Contents/Resources/codex` |
| CLI version | `codex-cli 0.128.0-alpha.1` |
| Non-interactive command | `codex exec` |
| JSON event output | `--json` |
| Final answer file | `--output-last-message <file>` |
| Fresh session option | `--ephemeral` |
| Workspace root option | `--cd <dir>` |
| User config isolation | `--ignore-user-config` |
| Project rule isolation | `--ignore-rules` |
| Approval control | `--ask-for-approval never` |
| Sandbox control | `--sandbox read-only` |

Proposed backend invocation shape:

```bash
codex exec \
  --cd <temporary-materialized-codex-workspace> \
  --sandbox read-only \
  --ask-for-approval never \
  --ignore-user-config \
  --ignore-rules \
  --ephemeral \
  --model <model> \
  --json \
  --output-last-message <raw-output-file> \
  -
```

The sample prompt should be passed on stdin. The backend implementation should wrap this command with a subprocess timeout rather than relying on shell behavior.

## Adapter Measurement Route

The backend must measure the Codex adapter, not generic OpenAI model behavior.

Required route:

1. Materialize the Codex adapter into a temporary workspace outside the source repository.
2. Run `codex exec --cd <temporary-materialized-codex-workspace>` so Codex sees the materialized `AGENTS.md` and `.agents/skills/**` as project context.
3. For `none`, run from an equivalent temporary workspace without Codex adapter context.
4. For `drop:<section>`, use a generated temporary adapter context with only that section removed from the materialized instructions.
5. Keep matrix labels in evidence only; never put `full`, `none`, or `drop:<section>` in the backend prompt.

If implementation instead sends the shared runner prompt to `codex exec` without materialized adapter context, the result must be called generic Codex CLI behavior, not Codex adapter behavior.

## Readiness Matrix

| Criterion | Status | Notes |
|-----------|--------|-------|
| Exact command identified | `GO` | `codex exec` exists locally |
| Prompt isolation described | `GO` | Temporary workspace, stdin prompt, no matrix labels |
| Auth declared | `GO` | Auth uses existing Codex CLI authentication; report must declare auth source |
| Cost/budget declared | `CONDITIONAL` | No dollar budget flag found; use model allowlist, sample cap, shard cap, and explicit run authorization |
| Raw output capturable | `GO` | Capture stdout JSONL, stderr, and `--output-last-message` file |
| Timeout control | `GO` | Backend subprocess must enforce timeout |
| Refusal/tool error normalization | `GO` | Normalize non-zero exit, stderr, timeout, refusal text, and missing output file |
| Evidence fields defined | `GO` | See required fields below |
| No behavior claim | `GO` | This report is readiness only |

## Required Evidence Fields

Any future Codex behavior run must record:

| Field | Required |
|-------|----------|
| `gate_head` | Git commit containing the readiness gate used before run |
| `run_head` | Git commit checked out during behavior execution |
| `retention_head` | Git commit retaining the final report |
| `dataset_sha` | Dataset hash used for the run |
| `grader_sha` | Grader contract hash used for the run |
| `backend` | `codex-cli` or more specific backend id |
| `model` | Exact model argument passed to Codex |
| `prompt_sha` | SHA for every sample prompt |
| `output_sha` | SHA for every captured final output |
| `stdout_jsonl_sha` | SHA for captured `--json` event stream |
| `stderr_sha` | SHA for stderr, even when empty |
| `adapter_workspace_sha` | Hash or manifest of the temporary materialized adapter workspace |

## Failure Normalization

| Failure | Required representation |
|---------|-------------------------|
| CLI missing | Backend error with `codex_cli_missing` |
| Auth failure | Backend error with `codex_auth_failure` |
| Timeout | Backend error with `codex_timeout` and elapsed seconds |
| Non-zero exit | Backend error with exit code and sanitized stderr excerpt |
| Missing final message file | Backend error with `codex_missing_output` |
| Refusal | Normal model output unless CLI exits unsuccessfully |
| Tool attempt | Backend output plus event-stream evidence; certification may NO-GO if tools contaminate prompt isolation |

## GO Criteria For Backend Implementation

Implementation may begin only if it preserves:

| Area | Criterion |
|------|----------|
| Adapter context | Codex materialized workspace is the source of adapter context |
| Isolation | No thread/session state dependency |
| Raw evidence | stdout JSONL, stderr, final output, hashes, and excerpts retained |
| Timeout | Subprocess timeout is enforced |
| Cost control | Model allowlist, sample cap, shard cap, and explicit run command are required |
| Shared mesh | Contract, dataset, grader, and existing Claude evidence remain untouched |

## NO-GO Conditions

- The backend depends on a Codex desktop thread state that cannot be recreated.
- The backend cannot capture raw output and event stream.
- The backend cannot enforce timeout.
- The backend needs contract, dataset, or grader changes before proving need.
- The backend measures generic OpenAI output and calls it Codex adapter behavior without materialized adapter context.
- The backend exposes matrix labels to the model prompt.
- A report declares Codex behavior parity before a retained Codex behavior run.

## Next Step

Implement the smallest `codex-cli` backend only after a separate patch confirms the temporary materialized workspace strategy. First implementation should run a dry fixture or single-sample smoke path before any full paid behavior matrix.
