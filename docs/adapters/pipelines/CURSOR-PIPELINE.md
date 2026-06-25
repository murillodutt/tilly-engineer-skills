---
tds_id: adapters.pipelines.cursor
tds_class: adapter
status: active
consumer: cursor adopters and certification reviewers
source_of_truth: true
evidence_level: L2
tver: 0.2.0
---

# Cursor Pipeline

The Cursor pipeline materializes the neutral behavioral contract into Cursor rules and adapter guidance. It remains structurally certifiable and explicitly behavior-deferred until a clean non-interactive execution backend is declared.

## Contract

- Contract manifest: `docs/mesh/CONTRACT-MANIFEST.yml`
- Adapter guide: `docs/adapters/CURSOR.md`
- Adapter source: `src/adapters/cursor/**`

## Materialization

| Area | Declaration |
|------|-------------|
| Source files | `src/adapters/cursor/**` |
| Temporary materialized files | `dist/adapters/cursor/CURSOR.md`, `dist/adapters/cursor/.cursor/rules/*.mdc`; purge after inspection |
| Validation command | `npm run materialize:check` |
| Execution backend | deferred; no clean non-interactive route certified |
| Evidence class | structural plus installer smoke |

## Known Limits

- Cursor rule loading and interaction model differ from Codex and Claude.
- Cursor has no direct skill equivalent in this package.
- Structural parity proves rule materialization, not behavior.
- Project-scoped MCP config can be installed for Cursor, but MCP config is not behavior evidence.
- Promotion criteria are recorded in `docs/evidence/reports/context-mesh/cursor-behavior-readiness-2026-05-06/REPORT.md`.

## NO-GO

- Do not declare Cursor behavioral parity without an executor.
- Do not force Cursor to mimic Claude plugin or Codex skill layout.
- Do not treat missing skill/plugin equivalents as drift.
- Do not claim certification without retained evidence artifacts.
