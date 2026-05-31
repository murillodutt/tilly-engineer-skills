---
tds_id: roadmap.tes_tts_skill_roadmap
tds_class: roadmap
status: active
consumer: maintainers, tes-tts maintainers, adapter authors, and release reviewers
source_of_truth: false
evidence_level: L2
---

# TES TTS Skill Roadmap
Dashboard for current decisions, latest evidence, and the next cut only. Dense
pointers live in `TES-TTS-SKILL-ROADMAP-REGISTRY.md`; closed lineage lives in
`TES-TTS-SKILL-ROADMAP-HISTORY.md`.

Partition contract: dashboard = objective state, registry = structured pointers, history = organized lineage, validators = budgets.

## State
`tes-tts` is reactive-only. PT-BR is the primary quality target. Active work
happens in `.agents/skills/tes-tts`, then mirrors to adapters. The path is
runtime preparation plus optional OmniVoice with the canonical local reference
WAV through direct/resident execution; `say`/Felipe is only a fallback when
OmniVoice is unavailable.
Unauthorized: release/sync/push/tag/publish, redistribution, global writes,
durable conversion cache, or proactive `speak`.

## Decisions
- Source text is immutable; speech is request-local; secrets are redacted.
- PT-BR is platform narration; English/technical identity is preserved.
- OmniVoice is optional local capability, not bundled dependency.
- Version/release/sync/push/tag/publish need separate approval.

## Evidence
- OmniVoice cloned voice reached maintainer rating `9.5`; direct/resident
  recipe `20260530-190552-healthy-reference-read` was rated 7.5/10.
- Python runtime optimization now targets provider hot path and oracle
  monoliths, not text-prep rewrites.
- Direct voice prompt cache is permitted only as protected local `tmp/**`
  runtime state, never as committed or shared artifact.
- Python cleanup removed obsolete lab execution copies from tracked source:
  the active provider surface is direct/resident only, timing is attributable,
  and voice prompt cache permissions are protected.

## Next Cut
Ready prompt is indexed in registry as RTO-001. Optimize the active provider
hot path first. Keep `tmp/**` artifacts out of commits.

## Maintenance Rules
- Hard limit: 100 lines. Review zone starts at 75 lines.
- Keep only current state, active decisions, next cut, and latest evidence;
  move dense pointers to registry and closed lineage to history.
- If evidence needs more than four bullets, move detail to registry/history.
- Keep the root index grouped by product line, not by every prompt/SPEC/audit.
- Every `tes-tts` cycle must update this dashboard or record no-change
  rationale; ambiguous, stale, or repeated status is a defect.
- This roadmap cannot authorize sync, release, provider installs, downloads, or
  global writes.

## Closure Rule
Close after focused gates. Commit local only until new order; never claim
release closure without a release identity decision.
