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
`tes-tts` is reactive-only. PT-BR is the primary quality target. Active work
happens in `.agents/skills/tes-tts`, then mirrors to adapters. The path is
runtime preparation plus optional OmniVoice; `say`/Felipe remains fallback.
Unauthorized: release/sync/push/tag/publish, redistribution, global writes,
durable cache, or proactive `speak`.

## Decisions
- Source text is immutable; speech uses request-local prepared text.
- Secrets are redacted before rendering and provider handoff.
- PT-BR is platform narration; English/technical identity is preserved.
- OmniVoice is optional local capability, not bundled dependency.
- Version/release/sync/push/tag/publish need separate approval.

## Evidence
- Maintainer rating: OmniVoice cloned voice `9.5`; sealed auto profile is
  `fast`; latest live-smoke package passed with avg RTF `0.3864`.
- Long-read correction passed: 12 chunks, `avg_rtf=0.2067`,
  `fallback_used=false`, monitor log under `tmp/**/runtime-logs`.
- Audio variant review supports per-chunk STT language, `combined.wav`,
  `language=auto`, and lab-only English-island variants.
- Latest lab evidence `20260530-162231-615943` improves target chunks 2 and 3;
  chunk 1 needs human scoring and less brittle STT term normalization.
- Community scan produced a tested `speak-server` route for local
  OpenAI-compatible OmniVoice servers; no install, download, or global write.

## Next Cut
Human-score `20260530-162231-615943` against `20260530-151743`, then run the
same chunks through `speak-server` when a local OmniVoice server is available.
Promote only audio that wins by ear; otherwise pivot provider/runtime strategy
before adding more punctuation or alias variants.

## Maintenance Rules
- Hard limit: 80 lines. Review zone starts at 60 lines.
- Keep only current state, active decisions, next cut, and latest evidence;
  move dense pointers to registry and closed lineage to history.
- If evidence needs more than four bullets, move detail to registry/history.
- Keep the root index grouped by product line, not by every prompt/SPEC/audit.
- Every `tes-tts` cycle must update this dashboard or record no-change
  rationale; ambiguous, stale, or repeated status is a defect.
- This roadmap cannot authorize sync, release, provider installs, downloads, or
  global writes.

## Closure Rule
Close material changes after focused TTS/package gates. Commit local only until
new order; never claim release closure without a release identity decision.
