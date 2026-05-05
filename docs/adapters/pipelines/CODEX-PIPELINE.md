---
tds_id: adapters.pipelines.codex
tds_class: adapter
status: active
consumer: codex adopters and certification reviewers
source_of_truth: true
evidence_level: L2
---

# Codex Pipeline

The Codex pipeline materializes the neutral behavioral contract into Codex
runtime instructions and skills. It is not behavior-certified until an
execution backend exists.

## Contract

- Contract manifest: `docs/mesh/CONTRACT-MANIFEST.yml`
- Adapter guide: `docs/adapters/CODEX.md`
- Adapter source: `src/adapters/codex/**`

## Materialization

| Area | Declaration |
|------|-------------|
| Source files | `src/adapters/codex/**` |
| Materialized files | `dist/adapters/codex/AGENTS.md`, `dist/adapters/codex/.agents/skills/**` |
| Validation command | `npm run materialize:check` |
| Execution backend | pending |
| Evidence class | structural until a backend exists |

## Known Limits

- Codex skill behavior is instruction-mediated and depends on the active Codex
  runtime.
- No behavior backend is currently declared for context mesh execution.
- Structural parity proves materialization, not model behavior.

## NO-GO

- Do not declare Codex behavioral parity without a backend run.
- Do not use copied Claude or Cursor text as the parity criterion.
- Do not add hooks, cloud actions, or marketplace assumptions as part of this
  pipeline.
- Do not claim certification without retained evidence artifacts.
