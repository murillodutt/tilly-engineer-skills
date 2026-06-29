---
tds_id: roadmap.goal_super_spec.goal_maestro_execution_thermometer.experience_data_contract
tds_class: roadmap
status: active
consumer: maintainers, Goal Maestro authors, report renderer authors, schema authors, and execution agents
source_of_truth: true
evidence_level: L2
tver: 0.1.0
---

# Goal Maestro Execution Thermometer: Experience And Data Contract

This document defines the user-visible report experience and the canonical
YAML/JSON data package. Renderers may change layout, but they must not invent
fields, hide `UNPROVEN` metrics, or treat HTML as source data.

## Markdown Context Receipt

The Markdown receipt is the small report shown in the chat context window after a
Goal Maestro loop. It is optimized for immediate user understanding, not full
analysis.

Required sections:

1. title and run identity;
2. model, reasoning profile, harness version, and report status;
3. five signals for the latest loop;
4. objective feedback in short bullets;
5. run context;
6. next actions;
7. source package references.

Required signal columns:

| Column | Meaning |
|--------|---------|
| Signal | Delivery, Fidelity, Proof, Efficiency, or Protection |
| Status | `ON TRACK`, `UNPROVEN`, `NEEDS REVIEW`, `BLOCKED`, or `FAIL` |
| Score | Percentage only when evidence-backed |
| vs Plan | Difference from accepted baseline, if available |
| Notes | One concise evidence-backed observation |

The receipt may use plain Markdown tables only. It must not depend on inline
HTML, CSS, Mermaid, images, or interactive controls because the context window is
Markdown-only.

## Static HTML Report

The HTML report is a static enterprise report, not a dashboard. It must open from
disk with no build step, server, database, tracking pixel, external CSS, external
JavaScript, CDN, or network fetch.

Required top sections:

1. header identity block;
2. accumulated loops index;
3. selected loop detail;
4. SPEC results for selected loop;
5. evidence references for selected loop;
6. key metrics for selected loop;
7. model and harness metadata;
8. unproven metrics;
9. source files and package checksums.

Loop selection rule:

```text
Each loop row links to a stable anchor such as #loop-L4.
The selected-loop detail area changes according to the clicked loop.
Opening the file at #loop-L4 must show Loop L4 as selected.
Printing must include enough loop detail to preserve review evidence.
```

Preferred v1 behavior: render one anchor-backed loop section per loop and use
small local enhancement script only for focus, table highlighting, and selected
detail convenience. If JavaScript is unavailable, anchor navigation must still
show the selected loop section.

## Evidence Package Layout

```text
execution-thermometer-<run-id>/
  README.md
  context-receipt.md
  exec_identity.yaml
  exec_metrics.json
  execution-thermometer.html
  checksums.sha256
```

The package is local-first. It is shareable only after sanitization and explicit
owner approval. Rendered Markdown and HTML are package outputs; YAML plus JSON
are the data source.

## `exec_identity.yaml`

`exec_identity.yaml` captures stable identity and governance metadata. It should
remain human-readable and diff-friendly.

Required top-level fields:

```yaml
schema_version: 1
report_id: "<uuid-or-stable-id>"
run_id: "<goal-maestro-run-id>"
loop_series_id: "<series-id>"
generated_at_utc: "2026-06-29T00:00:00Z"
timezone: "UTC"
report_class: "execution_thermometer"
report_status: "local_only"
```

Required `harness` fields:

```yaml
harness:
  name: "tes-goal-maestro"
  version: "<package-or-skill-version>"
  adapter: "codex|claude|cursor|other"
  command: "--execute-loop"
  schema_version: "<ledger-schema-version>"
```

Required `model` fields:

```yaml
model:
  provider: "<provider>"
  identity: "<model-name>"
  reasoning_profile: "<profile-label>"
  effort_multiplier: "<label-or-number>"
  metadata_source: "operator_declared|runtime_reported|unproven"
```

Required governance fields:

```yaml
anchor:
  path: "<accepted-artifact-path>"
  hash: "<hash-or-unproven>"
  class: "<artifact-class>"
ledger:
  path: "<ledger-path-or-unproven>"
  hash: "<hash-or-unproven>"
git:
  repo_state: "clean|dirty|unproven"
  head: "<sha-or-unproven>"
privacy:
  sanitizer_version: "<version>"
  private_vocabulary_status: "pass|fail|unproven"
share:
  status: "not_requested|declined|approved_local_export|draft_pr_opened|blocked"
```

Unknown identity fields must be explicit `UNPROVEN` values or structured
`unproven` statuses. They must not be inferred from surrounding prose.

## `exec_metrics.json`

`exec_metrics.json` stores normalized execution data. It is optimized for
machine rendering and validation.

Required top-level sections:

```json
{
  "schema_version": 1,
  "identity_ref": "exec_identity.yaml",
  "sources": [],
  "loop_summary": {},
  "loops": [],
  "latest_loop": {},
  "spec_results": [],
  "five_signals": [],
  "lens_results": [],
  "flash_fry": {},
  "cache_economy": {},
  "model_profile": {},
  "oracle_strength": {},
  "structural_health": {},
  "runtime_visual": {},
  "commits": {},
  "audit": {},
  "anti_gaming_flags": [],
  "privacy": {},
  "gold_analysis": {},
  "share_gate": {},
  "unproven_metrics": [],
  "final_status": {}
}
```

Every metric object must include:

```json
{
  "name": "metric_name",
  "value": null,
  "unit": "percent|count|ms|tokens|usd|text",
  "status": "proven|unproven|blocked|not_applicable",
  "evidence_refs": [],
  "notes": ""
}
```

## Loop Objects

Each loop object must be addressable by the HTML report.

Required fields:

```json
{
  "loop_id": "L4",
  "label": "L4 (Latest)",
  "started_at_utc": "2026-06-29T00:00:00Z",
  "ended_at_utc": "2026-06-29T00:00:00Z",
  "objective": "",
  "status": "on_track|unproven|needs_review|blocked|fail",
  "scores": {},
  "spec_ids": [],
  "evidence_refs": [],
  "summary": "",
  "next_actions": []
}
```

## SPEC Result Objects

Each SPEC result captures behavior, not just pass/fail status.

Required fields:

```json
{
  "spec_id": "SPEC-004",
  "title": "Static HTML Report Renderer",
  "type": "functional|non_functional|governance|safety",
  "status": "pass|unproven|needs_review|blocked|fail",
  "intent_score": null,
  "fidelity_score": null,
  "proof_score": null,
  "attempts": 1,
  "rework_count": 0,
  "evidence_refs": [],
  "unproven_metrics": [],
  "notes": ""
}
```

## Evidence References

Evidence references are local package references, not remote URLs by default.

Required fields:

```json
{
  "ref": "EV-401",
  "type": "test_report|oracle|screenshot|fixture|ledger|commit|manual_review",
  "description": "",
  "source": "artifact|generated|operator_declared",
  "path": "evidence/perf/load/ev-401.html",
  "hash": "<sha256-or-unproven>",
  "sanitized": true
}
```

## Renderer Constraints

- Markdown must render as Markdown only.
- HTML must be static and offline.
- HTML may embed normalized sanitized data at generation time.
- HTML must show source hashes and schema versions.
- HTML must visibly mark `UNPROVEN`, `BLOCKED`, and `NEEDS REVIEW`.
- Renderers must never calculate hidden pass/fail gates from unproven metrics.
- The report must remain useful with one loop or dozens of loops.
