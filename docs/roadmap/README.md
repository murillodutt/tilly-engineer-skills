---
tds_id: roadmap.index
tds_class: roadmap
status: active
consumer: maintainers, release reviewers, and next-loop operators
source_of_truth: false
evidence_level: L2
tver: 0.1.4
---

# Roadmap Index

This folder preserves roadmap lineage without turning the roadmap into the
work. Current package baseline: TES `0.3.162`. Execution authority lives in the
current dashboard, Super SPEC, audit record, or runtime oracle for each line.

## Folder Map

| Folder | Purpose |
|--------|---------|
| `goals/super-specs/` | Active and historical Goal Super SPECs. |
| `goals/prompts/` | Local execution prompts; ignored and not package governance. |
| `product/` | Product-wide roadmap proposals and readiness work. |
| `archive/v1/` | V1 convergence lineage retained for audit. |
| `archive/notes/` | Historical continuity notes. |
| `cortex-*/*` | Existing Cortex execution-unit partitions. |

## Goal Artifact Policy

`docs/roadmap/goals/super-specs/` remains tracked because Super SPECs are
execution contracts or durable lineage. The 2026-06-02 audit found 26 tracked
Super SPECs: 15 active, 6 proposed, and 5 archived. `goals/prompts/` is ignored
because generated goal prompts are execution residue; durable outcomes belong
in dashboards, registries, history, audits, fixtures, or oracles.

## Current Lines

| Line | Status | Authority |
|------|--------|-----------|
| Cortex MCP capability expansion | Active | `goals/super-specs/GOAL-SUPER-SPEC-cortex-mcp-capability-expansion.md` |
| Cortex MCP host segmentation | Active | `goals/super-specs/GOAL-SUPER-SPEC-cortex-mcp-host-segmentation.md` |
| Cortex memory benchmark harness | Active | `goals/super-specs/GOAL-SUPER-SPEC-cortex-memory-benchmark-harness.md` |
| TES anti-contamination hardening | Active | `goals/super-specs/GOAL-SUPER-SPEC-tes-anti-contamination-hardening.md` |
| TES capsule install and uninstall | Active | `goals/super-specs/GOAL-SUPER-SPEC-tes-capsule-install-and-uninstall.md` |
| TES attach/detach and attach-health | Active | `goals/super-specs/GOAL-SUPER-SPEC-tes-attach-detach-and-attach-health.md` |
| TES runtime-surface attach/detach | Proposed | `goals/super-specs/GOAL-SUPER-SPEC-tes-runtime-surface-attach-detach.md` |
| TES postinstall/Cortex hardening | Active | `goals/super-specs/GOAL-SUPER-SPEC-tes-postinstall-cortex-hardening.md` |
| TES postinstall recovery symmetry | Active | `goals/super-specs/GOAL-SUPER-SPEC-tes-postinstall-recovery-contract-symmetry.md` |
| TES NPX MCP convergence | Active | `goals/super-specs/GOAL-SUPER-SPEC-tes-npx-mcp-convergence.md` |
| TES installed certification and Field Reports | Active | `goals/super-specs/GOAL-SUPER-SPEC-tes-installed-certification-and-field-reports-hardening.md` |
| TES root context composition | Active | `goals/super-specs/GOAL-SUPER-SPEC-tes-root-context-composition.md` |
| RC1 readiness cleanup | Active | `product/RC1-READINESS-ROADMAP.md` |
| TES Align semantic drift hardening | Proposed | `product/TES-ALIGN-SEMANTIC-DRIFT-HARDENING-SUPER-PROMPT.md` |
| Flash-Fry skill gap | Proposed | `product/FLASH-FRY-SKILL-SPEC.md` |
| TES memory lifecycle | Complete | `goals/super-specs/GOAL-SUPER-SPEC-tes-memory-lifecycle.md` |
| Cortex hardening sequence | Complete | `goals/super-specs/GOAL-SUPER-SPEC-cortex-hardening.md` |
| V1 convergence lineage | Historical | `archive/v1/` |
| 2026-05-05 continuity notes | Historical | `archive/notes/` |

## Operating Rule

Keep this index short and partitioned:

- Use one row per active line or grouped historical family.
- Do not list every prompt, SPEC, audit, or owner-decision record here.
- Dashboards carry decisions; registries carry pointers; history carries closed lineage.
- Every roadmap update must reduce ambiguity for the next executor.

Roadmap partition budgets are enforced by `scripts/validate_doc_size.py`.

| Partition | Limit | Purpose |
|-----------|-------|---------|
| Root index | 140 lines | Active product lines and folder map only. |
| Active dashboard | 100 lines | Current state, decisions, latest evidence, next cut. |
| Registry | 160 lines | Stable artifact pointers and grouped ranges. |
| History | 140 lines | Closed lineage and lessons. |

When a dashboard reaches the warning zone, move detail to registry/history
before adding new status. Ambiguous, repeated, or stale roadmap text is a
defect to fix in the same execution cycle.

## Status Vocabulary

| Status | Meaning |
|--------|---------|
| Active | Current planning authority. |
| Proposed | Retained proposal; not execution authority without owner choice. |
| Historical | Retained for lineage, not the next execution source. |
| Deferred | Intentionally postponed with reason. |
| Complete | Closed by evidence or replaced by a newer source. |

Do not delete old roadmap documents merely because they are outdated. Move
them to the right partition and make the lineage explicit.
