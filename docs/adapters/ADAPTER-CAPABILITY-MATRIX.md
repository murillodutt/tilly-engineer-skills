---
tds_id: adapters.capability_matrix
tds_class: adapter
status: active
consumer: maintainers and adapter authors
source_of_truth: true
evidence_level: L2
tver: 0.2.0
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
| Behavioral execution backend | `codex-cli` retained v1 scope | `claude-cli` retained v1 scope | deferred; no clean non-interactive route certified |

Capability difference is not drift. Decision divergence under the same
behavioral gate is drift.

## Certification Implication

| Adapter | Current certifiable level | Reason |
|---------|---------------------------|--------|
| Codex | structural plus retained behavior evidence | Materialization and `codex-cli` v1 evidence exist for the retained run/hash/backend/prompt contract. |
| Claude | structural plus retained behavior evidence | Materialization and `claude-cli` v1 evidence exist for the retained run/hash/backend/model. |
| Cursor | structural | Materialization and installer smoke can be checked; behavior remains explicitly deferred until a non-interactive backend exists. |

## NO-GO

- Do not create separate contracts per adapter.
- Do not copy text between adapters to manufacture parity.
- Do not declare Cursor behavioral parity without an executor.
- Do not declare Codex or Claude universal behavior from one retained backend
  run; evidence is scoped to the retained run/hash/backend/model or prompt
  contract.
- Do not block Claude behavior certification waiting for symmetric adapter
  capability.
