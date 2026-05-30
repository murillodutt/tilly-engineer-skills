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
work. Older v1 planning documents remain auditable, but active execution must
use the smallest current authority for each line.

## Current Line

| Line | Status | Document |
|------|--------|----------|
| Cortex MCP capability expansion | Active | `GOAL-SUPER-SPEC-cortex-mcp-capability-expansion.md` |
| Cortex MCP host segmentation | Active | `GOAL-SUPER-SPEC-cortex-mcp-host-segmentation.md` |
| TES Memory Lifecycle implementation | Complete | `GOAL-SUPER-SPEC-tes-memory-lifecycle.md` |
| Cortex memory benchmark harness | Active | `GOAL-SUPER-SPEC-cortex-memory-benchmark-harness.md` |
| TES anti-contamination hardening | Active | `GOAL-SUPER-SPEC-tes-anti-contamination-hardening.md` |
| TES postinstall and Cortex curation hardening | Active | `GOAL-SUPER-SPEC-tes-postinstall-cortex-hardening.md` |
| TES postinstall recovery contract symmetry | Active | `GOAL-SUPER-SPEC-tes-postinstall-recovery-contract-symmetry.md` |
| TES NPX MCP convergence | Active | `GOAL-SUPER-SPEC-tes-npx-mcp-convergence.md` |
| TES installed certification and Field Reports hardening | Active | `GOAL-SUPER-SPEC-tes-installed-certification-and-field-reports-hardening.md` |
| TES TTS product line | Active | `TES-TTS-SKILL-ROADMAP.md` |
| TES TTS registry | Active | `TES-TTS-SKILL-ROADMAP-REGISTRY.md` |
| TES TTS history | Active | `TES-TTS-SKILL-ROADMAP-HISTORY.md` |
| TES TTS acceptance and release decision | Active | `TES-TTS-ACCEPTANCE-AND-RELEASE-DECISION.md` |
| TES TTS active/runtime sequences | Active/Complete | TTS, SPEC, OWNER, CAP, LEX, RTE, and OmniVoice lineage are indexed in the TES TTS roadmap registry/history, not expanded here. |
| RC1 readiness cleanup | Active | `RC1-READINESS-ROADMAP.md` |
| Cortex hardening sequence | Complete | `GOAL-SUPER-SPEC-cortex-hardening.md` |
| TES Align semantic drift hardening | Proposed | `TES-ALIGN-SEMANTIC-DRIFT-HARDENING-SUPER-PROMPT.md` |
| Flash-Fry skill gap | Proposed | `FLASH-FRY-SKILL-SPEC.md` |
| V1 convergence lineage | Historical | `V1-CONVERGENCE-LOOP.md` |
| V1 goal checklist | Historical | `V1-GOAL-CHECKLIST.md` |
| 2026-05-05 continuity letter | Historical | `NEXT-STEPS-LETTER-2026-05-05.md` |
| Senior mentorship context | Historical | `SENIOR-MENTORSHIP-CONTEXT-2026-05-05.md` |

## Baseline

The current release-readiness baseline is TES `0.3.147`, after ADR 0001 memory
lifecycle implementation, postinstall/Cortex curation hardening, Cortex
reflection slug hygiene, and ADR 0002 governed MCP remember closed locally with
clean bundle metadata. Remote tag/ref release certification is still deferred.

The next work is not to create a release. The next work is to remove obvious
pre-RC1 friction:

- documentation freshness;
- root structure clarity;
- GitHub community and security documents;
- GitHub Pages landing;
- no overclaim against deferred or partial surfaces.

## Operating Rule

Keep this root index short and partitioned:

- Use one row per active product line or grouped historical family.
- Do not list every prompt, SPEC, or audit file here when a line has its own
  dashboard, registry, or history.
- Keep this index and active dashboards under their explicit
  `validate_doc_size.py` budgets. When a roadmap approaches the limit,
  partition it before adding more status.
- Active dashboards carry current decisions; registries carry dense artifact
  pointers; history files carry closed lineage.
- Every update must reduce ambiguity for the next executor.

Roadmap partition budgets are enforced by `scripts/validate_doc_size.py`.
Warning begins at 75% for governed roadmap partitions so maintenance happens
before ambiguity accumulates:

| Partition | Limit | Purpose |
|-----------|-------|---------|
| Root index | 140 lines | Active product lines only. |
| Active dashboard | 120 lines | Current state, decisions, latest evidence, next cut. |
| Registry | 160 lines | Stable artifact pointers and grouped ranges. |
| History | 140 lines | Closed lineage and lessons. |

When a dashboard reaches the warning zone, move detail to registry/history
before adding new status. Ambiguous, repeated, or stale status is a defect, not
documentation.

Roadmap updates must classify their status clearly:

| Status | Meaning |
|--------|---------|
| Active | Current planning authority |
| Needs rewrite | Existing artifact is retained, but should be rewritten before it is reused as execution authority |
| Historical | Retained for lineage, not the next execution source |
| Deferred | Intentionally postponed with reason |
| Complete | Closed by evidence or replaced by a newer source |

Do not delete old roadmap documents merely because they are outdated. Add a
new active document and make the lineage explicit.
