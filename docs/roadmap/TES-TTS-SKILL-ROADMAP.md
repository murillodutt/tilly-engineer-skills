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
- Audio variant review now requires STT when requested, audits `combined.wav`,
  rejects stale audit summaries, and flags raw STT drift even when domain
  normalization explains protected-term drift.
- Research-guided audio lab now supports provider/STT language selection,
  microsecond run IDs, and an OmniVoice `language=auto` long-read plan that
  routes whole chunks only when the chunk is clearly an English island.
- Latest evidence: single English phrase with global `en` remains the best STT
  score (`20260530-151743`); routed PT/PT/EN/PT chunk synthesis now passes
  audio-metric audit without STT certification (`20260530-153447-843321`).

## Next Cut
Listen to `20260530-151743` and `20260530-153447-843321`; decide whether the
chunk-language routed `combined.wav` improves the mixed technical phrase enough
to promote `language=auto` into the runtime path, or keep it lab-only pending
human scores.

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
Close material changes after focused TTS/package gates. Commit local only until
new order; never claim release closure without a release identity decision.
