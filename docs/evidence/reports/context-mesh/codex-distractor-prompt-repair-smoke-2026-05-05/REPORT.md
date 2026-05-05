---
tds_id: evidence.context_mesh.codex_distractor_prompt_repair_smoke_2026_05_05
tds_class: evidence
status: active
consumer: certification reviewers, benchmark maintainers, and Codex backend operators
source_of_truth: false
evidence_level: L4
---

# Codex Distractor Prompt Repair Smoke Report

This report retains the targeted smoke for `codex-adapter-prompt@0.1.1`.
It validates only the Codex distractor prompt contract repair. It does not
certify Codex behavior, adapter parity, or the full matrix.

## Decision

Result: `GO` for the narrow distractor prompt repair smoke.

Claim:

```text
Codex can keep project discipline latent on the two retained distractors when
the backend prompt no longer asks every sample to make context influence
visible.
```

## Patch Scope

| Item | Value |
|------|-------|
| File changed | `scripts/context_mesh_run.py` |
| Runner version | `0.1.7` |
| Previous prompt contract | `codex-adapter-prompt@0.1.0` |
| New prompt contract | `codex-adapter-prompt@0.1.1` |
| Contract change | Distractor prompts answer directly and avoid naming rules, gates, governance, benchmarks, evals, or project discipline |
| No-touch surfaces | Shared contract, dataset, grader, Codex adapter source, Claude evidence, Cursor, UI |

Triggers still keep the context-visible instruction. Distractors now keep
discipline latent unless context is necessary to answer the task.

## Smoke Commands

```bash
npm run benchmark:run -- \
  --backend codex-cli \
  --model gpt-5.3-codex \
  --run-id codex-distractor-d1-prompt-011 \
  --shard-count 44 \
  --shard-index 42 \
  --sample-cap 1 \
  --timeout-seconds 180
```

```bash
npm run benchmark:run -- \
  --backend codex-cli \
  --model gpt-5.3-codex \
  --run-id codex-distractor-d2-prompt-011 \
  --shard-count 44 \
  --shard-index 43 \
  --sample-cap 1 \
  --timeout-seconds 180
```

Both runs are shards and therefore report `SHARD-NOT-CERTIFIED`. That status is
expected; the smoke is a targeted prompt repair proof, not a matrix
certification.

## Smoke Results

| Sample | Run ID | Task Pass | Distractor Leak | Backend Error | Prompt Contract |
|--------|--------|-----------|-----------------|---------------|-----------------|
| `0043-distractor-D1-typo` | `codex-distractor-d1-prompt-011` | `true` | `false` | none | `codex-adapter-prompt@0.1.1` |
| `0044-distractor-D2-read-only` | `codex-distractor-d2-prompt-011` | `true` | `false` | none | `codex-adapter-prompt@0.1.1` |

## Raw Evidence Checks

| Check | D1 | D2 |
|-------|----|----|
| `codex_stdout_jsonl_sha` present | `PASS` | `PASS` |
| `codex_stderr_sha` present | `PASS` | `PASS` |
| `codex_adapter_workspace_sha` present | `PASS` | `PASS` |
| `codex_final_output_sha` present | `PASS` | `PASS` |
| `output_sha` present | `PASS` | `PASS` |
| `distractor_leak_reasons` empty | `PASS` | `PASS` |

## Evidence Files

```text
docs/evidence/reports/context-mesh/codex-distractor-d1-prompt-011/
  manifest.json
  raw.ndjson
  graders-sha.json

docs/evidence/reports/context-mesh/codex-distractor-d2-prompt-011/
  manifest.json
  raw.ndjson
  graders-sha.json
```

## Interpretation

The repaired prompt contract removes the likely harness contamination identified
in the Codex NO-GO forensics. This does not prove that the full Codex matrix
will certify. It proves the two distractors can pass without context bleed under
the repaired prompt contract.

## Next Step

Open a new Codex behavior matrix readiness note or run plan referencing this
repair, then execute a full 44-call matrix once. The next matrix must be
retained whether it returns GO or NO-GO.
