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
`TES-TTS-SKILL-ROADMAP-HISTORY.md`. ADR 0004 remains the boundary.

Partition contract: dashboard = objective state, registry = structured pointers, history = organized lineage, validators = budgets.

## State
`tes-tts` is reactive-only. PT-BR is the primary quality target. The path is
runtime preparation plus optional OmniVoice; `say`/Felipe remains fallback.

Active work happens in `.agents/skills/tes-tts`, then mirrors to adapters.
Unauthorized: release/sync/push/tag/publish, redistribution, global writes,
durable cache, or proactive `speak`.

## Decisions
- Source text is immutable; speech uses request-local prepared text.
- Secrets are redacted before rendering and provider handoff.
- PT-BR is platform narration; English/technical identity is preserved.
- OmniVoice is optional local capability, not bundled dependency.
- Version/release/sync/push/tag/publish need separate approval.

## Evidence
- Maintainer live rating: OmniVoice cloned voice result `9.5`.
- Sealed profile review selected `fast` as the current auto latency profile.
- Latest live-smoke review package passed: 3 WAVs, `review.html`, ZIP package,
  avg RTF `0.3864`, package SHA starts `eafb9419`.
- Long-read OmniVoice correction passed: 12 chunks played, `avg_rtf=0.2067`,
  `fallback_used=false`, monitor log under `tmp/**/runtime-logs`.
- Audio variant review now packages WAVs, STT/WER, and HTML review. In latest
  `chunk-002` evidence, `fast` stayed degraded while `quality` passed for both
  baseline and `audio_quality`; human listening remains the final decision.

## Next Cut
Listen to packaged baseline-vs-`audio_quality` reviews, then decide whether
mixed technical chunks should prefer `quality`, `audio_quality`, or both.

## Maintenance Rules
- Hard limit: 80 lines. Review zone starts at 60 lines.
- Keep only current state, active decisions, next cut, and latest evidence.
- Move dense artifacts to `TES-TTS-SKILL-ROADMAP-REGISTRY.md`.
- Move historical detail to `TES-TTS-SKILL-ROADMAP-HISTORY.md`.
- If evidence needs more than four bullets, move it to registry/history and
  leave only the current conclusion here.
- Keep the root index grouped by product line, not by every prompt/SPEC/audit.
- Every `tes-tts` cycle must update this dashboard or record no-change
  rationale; ambiguous, stale, or repeated status is a defect.
- Do not use this roadmap to authorize sync, release, provider installs,
  provider downloads, or global config writes.

## Closure Rule
Close material changes after focused TTS/package gates. Never claim release
closure without a release identity decision.
