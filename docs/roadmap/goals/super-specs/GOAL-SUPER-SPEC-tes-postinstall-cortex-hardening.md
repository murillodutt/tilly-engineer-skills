---
tds_id: roadmap.goal_super_spec_tes_postinstall_cortex_hardening
tds_class: roadmap
status: active
consumer: maintainers, installer authors, Cortex maintainers, adapter maintainers, release reviewers, and execution agents
source_of_truth: false
evidence_level: L2
tver: 0.1.0
---

# GOAL Super SPEC: TES Postinstall And Cortex Curation Hardening

Status: implementation artifact for the `0.3.137` local package-source cut.

Capability: convert portable learning from a private installed-target canary into TES runtime behavior, fixtures, and documentation without promoting any target-specific vocabulary, paths, commits, commands, or project decisions.

## Authority

| Layer | Role |
|-------|------|
| ADR 0001 | Markdown remains durable Cortex memory truth; indexes, run records, and sentinels are derived evidence or lifecycle state. |
| Private canary dossier | Source-of-record kept outside TES; used only to identify generic failure modes. |
| Maintainer correlation rule | Runtime and adapter behavior changes must update correlated docs, skills, and release identity. |

## Portable Findings

| Finding | Product Risk | Required TES Behavior |
|---------|--------------|-----------------------|
| Postinstall `needs_review` recovery depended on a hidden forced rerun. | A user can be told `/tes-init` recovers setup while the sentinel remains blocked. | Provide an explicit recovery command that only runs when `.tes/postinstall.json` is `needs_review`, reruns Project-Start, records the recovery run, and clears the sentinel only on PASS. |
| Cortex split detection treated the bullet threshold as a hard standalone trigger. | A narrow evidence-dense Cortex cell can be marked as a split candidate solely because it has one more evidence bullet than the cutoff. | Make bullet pressure compound: claim bullets, non-evidence bullets, long claims, many headings, high line count, or mixed-topic markers must contribute before curation blocks a narrow evidence list. |

## Implementation Units

| Unit | Owned Surfaces | Focused Oracle | Stop Condition |
|------|----------------|----------------|----------------|
| SPEC-001 Postinstall recovery command | `scripts/tes_install.py`, `/tes-init` and `/tes-setup` router docs/skills | `python3 scripts/tes_install.py --self-test` | `needs_review` sentinel cannot be cleared by the explicit recovery command after gates PASS. |
| SPEC-002 Cortex curation heuristic | `scripts/cortex.py`, `docs/mesh/CORTEX.md` | `python3 scripts/cortex.py --self-test` | Evidence-dense narrow cell becomes a split candidate or swollen claim cells stop failing. |
| SPEC-003 Correlation and release closure | docs indexes, evidence report, version/bundle surfaces | baseline gates plus `npm run commit:check` | Any private identifier enters tracked TES content or release identity is unresolved. |

## Non-Objectives

- Do not add write-capable MCP.
- Do not add automatic Cortex writes.
- Do not add an external memory backend.
- Do not migrate private target project commands, paths, names, decisions, or vocabulary.
- Do not claim remote tag, fixed-ref, marketplace, cloud, or commercial-use certification.

## Acceptance Criteria

- `tes_install.py postinstall --recover-needs-review` is idempotent and sentinel-scoped.
- `/tes-init` and `/tes-setup` instructions route `needs_review` through that explicit recovery path.
- `curate-plan` preserves narrow evidence-dense cells while still failing swollen claim cells.
- Correlated install, adapter, Cortex, roadmap, TDS, and evidence surfaces are updated with neutral language only.
- Private vocabulary and staged diff checks pass.
- Release identity is classified before closure.
