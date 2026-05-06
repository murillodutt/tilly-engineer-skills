---
tds_id: evals.parity_gate
tds_class: eval
status: active
consumer: certification reviewers
source_of_truth: true
evidence_level: L2
tver: 0.1.0
---

# Parity Gate

The parity gate compares adapters by contract behavior and retained evidence,
not by text equality.

```text
Text equality is not required.
Decision equivalence is required.
```

## Levels

| Level | Criterion |
|-------|-----------|
| Structural parity | All declared adapter pipelines materialize without error. |
| Contract parity | All declared adapter pipelines load or point to the four gates in `docs/mesh/CONTRACT-MANIFEST.yml`. |
| Eval parity | The same dataset runs where a behavior backend exists. |
| Behavioral parity | Decisions are equivalent per gate for comparable runs. |
| Evidence parity | Each certified run has `manifest.json`, `raw.ndjson`, `summary.json`, `REPORT.md`, and `graders-sha.json`. |

## Decision Equivalence

A decision is equivalent when the adapter reaches the same gate outcome for the
same dataset sample and condition, within the declared evidence limits for that
backend. Equivalent decisions may use different wording, structure, or tool
mechanics.

## Current Certification Posture

| Area | Status |
|------|--------|
| Core contract | certified for structural use after TDS and materialization gates pass |
| Claude | behavior run executable through `claude-cli`; behavior status depends on retained report |
| Codex | structural only until backend exists |
| Cursor | structural only until backend exists |
| Parity | partial by design |

## NO-GO

- Do not compare adapters by literal text equality.
- Do not declare behavioral parity for an adapter without a backend run.
- Do not declare full parity if one adapter is structural-only.
- Do not hide backend limits in a GO report.
- Do not create separate datasets or contracts per adapter to make parity look
  easier.
