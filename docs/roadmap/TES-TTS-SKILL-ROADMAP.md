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
runtime preparation plus optional OmniVoice with the canonical local reference
WAV; `say`/Felipe is only a fallback when OmniVoice is unavailable.
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
- Live server evidence `20260530-174724-539838` synthesized chunks 2 and 3
  through local `omnivoice-server`: 12 results, fast/quality presets, combined
  WAVs, review HTML, and package under `tmp/**`.
- Community scan supports the local OpenAI-compatible server path first; UI,
  MLX, audiobook, and dubbing projects remain research references.
- `server-status`, `speak-server`, `speak-long-server`, and audio variant lab
  cover readiness, clone synthesis, chunked review, combined WAVs, and
  `SERVER_UNAVAILABLE` preflight without install/download/write.
- Current `127.0.0.1:8000` check is not a valid OmniVoice server: TCP responds,
  but capability endpoints return Laravel 404 / `NO_CAPABILITY_ENDPOINTS`.

## Next Cut
Future goal 1: start or target a verified OmniVoice server, then create a local
voice profile from
`tmp/tes-tts-lab/omnivoice/refs/audio-modelo-clone-mono24k.wav`, then use
`clone:<profile-id>` for synthesis so repeated reads do not upload the
reference WAV each time. Human-score `20260530-174724-539838` before promoting
any preset or profile workflow as default.

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
