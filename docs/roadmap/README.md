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
work. The root is only an index; Current package baseline: TES `0.3.151`.

execution authority lives in the current
dashboard, Super SPEC, prompt, or audit record for each line.

## Folder Map

| Folder | Purpose |
|--------|---------|
| `goals/super-specs/` | Active and historical Goal Super SPECs. |
| `goals/prompts/tes-tts/` | TES TTS circular execution prompts. |
| `tes-tts/` | TES TTS dashboard, registry, audits, specs, and runtime records. |
| `product/` | Product-wide roadmap proposals and readiness work. |
| `archive/v1/` | V1 convergence lineage retained for audit. |
| `archive/notes/` | Historical continuity notes. |
| `cortex-*/*` | Existing Cortex execution-unit partitions. |

## Current Lines

| Line | Status | Authority |
|------|--------|-----------|
| TES TTS | Active | `tes-tts/TES-TTS-SKILL-ROADMAP.md` |
| TES TTS registry | Active | `tes-tts/TES-TTS-SKILL-ROADMAP-REGISTRY.md` |
| TES TTS history | Active | `tes-tts/TES-TTS-SKILL-ROADMAP-HISTORY.md` |
| TES TTS acceptance/release decision | Active | `tes-tts/TES-TTS-ACCEPTANCE-AND-RELEASE-DECISION.md` |
| Cortex MCP capability expansion | Active | `goals/super-specs/GOAL-SUPER-SPEC-cortex-mcp-capability-expansion.md` |
| Cortex MCP host segmentation | Active | `goals/super-specs/GOAL-SUPER-SPEC-cortex-mcp-host-segmentation.md` |
| Cortex memory benchmark harness | Active | `goals/super-specs/GOAL-SUPER-SPEC-cortex-memory-benchmark-harness.md` |
| TES anti-contamination hardening | Active | `goals/super-specs/GOAL-SUPER-SPEC-tes-anti-contamination-hardening.md` |
| TES postinstall/Cortex hardening | Active | `goals/super-specs/GOAL-SUPER-SPEC-tes-postinstall-cortex-hardening.md` |
| TES postinstall recovery symmetry | Active | `goals/super-specs/GOAL-SUPER-SPEC-tes-postinstall-recovery-contract-symmetry.md` |
| TES NPX MCP convergence | Active | `goals/super-specs/GOAL-SUPER-SPEC-tes-npx-mcp-convergence.md` |
| TES installed certification and Field Reports | Active | `goals/super-specs/GOAL-SUPER-SPEC-tes-installed-certification-and-field-reports-hardening.md` |
| RC1 readiness cleanup | Active | `product/RC1-READINESS-ROADMAP.md` |
| TES Align semantic drift hardening | Proposed | `product/TES-ALIGN-SEMANTIC-DRIFT-HARDENING-SUPER-PROMPT.md` |
| Flash-Fry skill gap | Proposed | `product/FLASH-FRY-SKILL-SPEC.md` |
| TES memory lifecycle | Complete | `goals/super-specs/GOAL-SUPER-SPEC-tes-memory-lifecycle.md` |
| Cortex hardening sequence | Complete | `goals/super-specs/GOAL-SUPER-SPEC-cortex-hardening.md` |
| V1 convergence lineage | Historical | `archive/v1/` |
| 2026-05-05 continuity notes | Historical | `archive/notes/` |

## TES TTS Navigation

Use `tes-tts/TES-TTS-SKILL-ROADMAP.md` for current state and next action.
Use `tes-tts/TES-TTS-SKILL-ROADMAP-REGISTRY.md` for durable pointers to
runtime scripts, fixtures, benchmark records, and grouped prompt ranges.
Use `tes-tts/TES-TTS-SKILL-ROADMAP-HISTORY.md` for closed lineage and lessons.

TES TTS prompt artifacts are intentionally grouped under
`goals/prompts/tes-tts/`; do not expand every prompt in this root index.

## Operating Rule

Keep this index short and partitioned:

- Use one row per active product line or grouped historical family.
- Do not list every prompt, SPEC, audit, or owner-decision record here.
- Active dashboards carry current decisions.
- Registries carry dense artifact pointers.
- History files carry closed lineage.
- Every roadmap update must reduce ambiguity for the next executor.

Roadmap partition budgets are enforced by `scripts/validate_doc_size.py`.
`tes-tts` also has `scripts/tes_tts_roadmap_partition_oracle.py`.

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
