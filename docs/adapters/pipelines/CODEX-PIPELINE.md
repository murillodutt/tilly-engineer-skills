---
tds_id: adapters.pipelines.codex
tds_class: adapter
status: active
consumer: codex adopters and certification reviewers
source_of_truth: true
evidence_level: L2
tver: 0.2.0
---

# Codex Pipeline

The Codex pipeline materializes the neutral behavioral contract into Codex
runtime instructions and skills. It has retained v1 behavior evidence for the
declared `codex-cli` backend and prompt contract.

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
| Execution backend | `python3 scripts/context_mesh_run.py --backend codex-cli` |
| Evidence class | structural plus retained v1 behavior evidence |

## Known Limits

- Codex skill behavior is instruction-mediated and depends on the active Codex
  runtime.
- Behavior evidence is scoped to the retained run/hash/backend/prompt contract.
- Cross-adapter behavioral parity is not claimed while Cursor remains
  structural-only.

## NO-GO

- Do not declare Codex universal behavioral parity from a single backend run.
- Do not use copied Claude or Cursor text as the parity criterion.
- Do not add hooks, cloud actions, or marketplace assumptions as part of this
  pipeline.
- Do not claim certification without retained evidence artifacts.
