---
tds_id: adapters.pipelines.cursor
tds_class: adapter
status: active
consumer: cursor adopters and certification reviewers
source_of_truth: true
evidence_level: L2
tver: 0.1.0
---

# Cursor Pipeline

The Cursor pipeline materializes the neutral behavioral contract into Cursor
rules and adapter guidance. It remains structurally certifiable until a
behavior execution backend is declared.

## Contract

- Contract manifest: `docs/mesh/CONTRACT-MANIFEST.yml`
- Adapter guide: `docs/adapters/CURSOR.md`
- Adapter source: `src/adapters/cursor/**`

## Materialization

| Area | Declaration |
|------|-------------|
| Source files | `src/adapters/cursor/**` |
| Materialized files | `dist/adapters/cursor/CURSOR.md`, `dist/adapters/cursor/.cursor/rules/*.mdc` |
| Validation command | `npm run materialize:check` |
| Execution backend | pending |
| Evidence class | structural until a backend exists |

## Known Limits

- Cursor rule loading and interaction model differ from Codex and Claude.
- Cursor has no direct skill equivalent in this package.
- Structural parity proves rule materialization, not behavior.

## NO-GO

- Do not declare Cursor behavioral parity without an executor.
- Do not force Cursor to mimic Claude plugin or Codex skill layout.
- Do not treat missing skill/plugin equivalents as drift.
- Do not claim certification without retained evidence artifacts.
