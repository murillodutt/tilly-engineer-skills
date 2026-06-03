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
happens in `.agents/skills/tes-tts`, then mirrors to adapters. The optional
OmniVoice product runtime remains
`~/.tes/runtime/tes-tts/omnivoice`; only MLX/streaming lab runtimes were
removed after 2026-06-01 quality-regression evidence. `say`/Felipe remains a
fallback when OmniVoice is unavailable.
Unauthorized: release/sync/push/tag/publish, redistribution, global writes,
durable conversion cache, or proactive `speak`.

## Decisions
- Source text is immutable; speech is request-local; secrets are redacted.
- PT-BR is platform narration; English/technical identity is preserved.
- OmniVoice is optional local capability, not bundled dependency.
- Direct OmniVoice `redacted_source`/`audio_quality` modes consume source text
  once; generic `spoken_text` is fallback or explicit non-OmniVoice prep only.
- OmniVoice light provider tags may be used only as controlled prosody warmup
  for conversational narration after audio evidence; faithful reads stay
  tag-free by default.
- Version/release/sync/push/tag/publish need separate approval.

## Evidence
- OmniVoice cloned voice reached maintainer rating `9.5`; direct/resident
  recipe `20260530-190552-healthy-reference-read` was rated 7.5/10.
- TFA-001 added opt-in buffered first-audio for long reads. Baseline
  combined-only readiness was 49.8s; candidate first audio began at 21.9s,
  a 55.94% improvement with max unplanned gap 0.073 ms.
- GRT-001 moved direct OmniVoice defaults to
  `~/.tes/runtime/tes-tts/omnivoice/**`; legacy project runtime is
  detection/migration-report only. Status now reports `global_runtime`,
  `legacy_project_runtime`, `active_runtime`, profile, reference WAV, and cache
  status.
- Default voice preset `tes-tts-local-clone` now resolves the canonical
  reference audio/text, and `warm-cache` prebuilds the voice prompt cache.
- Python cleanup removed obsolete lab execution copies from tracked source:
  the active provider surface is direct/resident only, timing is attributable,
  and voice prompt cache permissions are protected.
- Human A/B evidence first ranked OmniVoice tag-only prosody above CMU-heavy
  output, then found the better product route: keep tags experimental and use
  the silent voice-design channel for default prosody.
- OPW-001 exposed `--prosody-warmup none|confirmation-en|question-en|sigh`
  on the direct provider path and generated comparison WAVs at
  `~/.tes/runtime/tes-tts/omnivoice/provider-cache/audio-reference-runs/opw-001-prosody-warmup-20260531-210442/`.
- A regression review found that pre-running `tes_tts_runtime.py` before
  OmniVoice long reads weakened technical identity and pauses; provider oracles
  now guard source-text quality modes and compact enumeration pauses.
- The long-read recipe is code-defined from the approved PT-BR baseline:
  `technical-live` now uses direct resident OmniVoice, provider language `en`,
  `redacted_source`, no inline provider tag, silent instruct
  `male, middle-aged, low pitch`, `num_step=28`, chunk size `420`, `450 ms`
  combined-WAV silence, first-audio buffering, and `combined.wav` review
  output. `technical-hd` preserves the same recipe with `num_step=32`; the
  comparison WAV
  `~/.tes/runtime/tes-tts/omnivoice/provider-cache/audio-reference-runs/instruct-premium-hd-20260601/01-instruct-male-middle-aged-low-pitch-num-step-32.wav`
  was human-rated 9.3. Compatibility aliases remain: `technical-streamer` maps
  to Live and `technical-quality` maps to HD; 26 remains rejected.
- The streaming-latency lab is archived as of 2026-06-01. Evidence remains in
  `TES-TTS-LAB-STREAMING-LATENCY-ROADMAP.md`; MLX/streaming lab artifacts are
  obsolete and removed. The canonical direct OmniVoice runtime remains
  required when the optional provider is configured.
- SUB-001/PLH-001: opt-in external-player integration. `serve` `emit_subtitle` returns redacted `subtitle_text`; `speak-long --player-handoff` hands progressive playback to `TES_TTS_PLAYER_BIN` (afplay fallback). Verified live. Registry holds detail.

## Next Cut
No active OmniVoice lab cut. A future round must start from fresh community
evidence, reinstall in disposable runtime space, and beat the documented
PyTorch/MPS quality baseline by same-input human review. Sync status remains
`REMOTE_SYNC_NOT_REQUESTED`. SUB-001 is delivered behavior with the version
bump intentionally deferred (owner decision): committed at the current version;
the next release cycle must advance 0.3.158 → 0.3.159 with `docs/dist/0.3.159/**`.

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
