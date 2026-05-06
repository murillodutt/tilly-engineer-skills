---
tds_id: adapters.capability_matrix
tds_class: adapter
status: active
consumer: maintainers and adapter authors
source_of_truth: true
evidence_level: L2
tver: 0.1.0
---

# Adapter Capability Matrix

Adapters are aligned by behavioral contract and evidence, not by identical
text. Different tool capabilities are expected. Drift exists when equivalent
contract gates produce divergent decisions, or when an adapter claims a
capability without evidence.

## Core Rule

One contract, three adapter surfaces, one parity gate.

```text
Core Contract
  -> Adapter Materialization
  -> Adapter Execution
  -> Adapter Evidence
  -> Cross-Adapter Parity Report
```

The neutral contract is `docs/mesh/CONTRACT-MANIFEST.yml`.

## Capability Matrix

| Capability | Codex | Claude | Cursor |
|------------|-------|--------|--------|
| Root instruction | `AGENTS.md` | `CLAUDE.md` | optional `AGENTS.md` |
| Always-on rule | root guidance | root guidance | `.cursor/rules/*.mdc` |
| Skill | `.agents/skills/**` | `skills/**` | no direct equivalent |
| Plugin | possible later | `.claude-plugin/**` | n/a |
| Hooks | possible, excluded | possible, excluded | possible, excluded |
| Behavioral execution backend | pending | `claude-cli` | pending |

Capability difference is not drift. Decision divergence under the same
behavioral gate is drift.

## Certification Implication

| Adapter | Current certifiable level | Reason |
|---------|---------------------------|--------|
| Codex | structural | Materialization can be checked; no behavior backend is declared yet. |
| Claude | structural plus behavioral candidate | Materialization can be checked and `claude-cli` can execute context mesh runs. |
| Cursor | structural | Materialization can be checked; no behavior backend is declared yet. |

## NO-GO

- Do not create separate contracts per adapter.
- Do not copy text between adapters to manufacture parity.
- Do not declare Cursor behavioral parity without an executor.
- Do not declare Codex behavioral parity without a backend.
- Do not block Claude behavior certification waiting for symmetric adapter
  capability.
