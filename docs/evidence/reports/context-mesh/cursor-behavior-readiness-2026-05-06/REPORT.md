---
tds_id: evidence.context_mesh.cursor_behavior_readiness_2026_05_06
tds_class: evidence
status: active
consumer: Cursor adapter maintainers and certification reviewers
source_of_truth: false
evidence_level: L3
---

# Cursor Behavior Readiness - 2026-05-06

## Decision

Cursor remains structurally certified and behavior-deferred. This is an
explicit non-claim, not an accidental gap.

## Reason

The repository has deterministic materialization and installer smoke checks for
Cursor files and project-scoped MCP config. It does not yet have a clean,
repeatable, non-interactive Cursor execution backend equivalent to
`claude-cli` or `codex-cli`.

## Current Gates

```bash
npm run materialize:check
python3 scripts/install_smoke.py --route cursor
python3 scripts/adapter_parity_readiness.py
```

## Promotion Criteria

Cursor can move from structural to behavioral only after a retained run records:

- backend identity and version;
- dataset SHA;
- grader SHA;
- raw outputs;
- summary;
- report;
- `gate_head`, `run_head`, and retention metadata.

## No-Go

Do not declare Cursor behavioral parity from materialized files, MCP config, or
manual UI observation alone.
