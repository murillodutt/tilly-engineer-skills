---
tds_id: roadmap.tes_tts_skill_roadmap
tds_class: roadmap
status: active
consumer: maintainers, tes-tts maintainers, adapter authors, and release reviewers
source_of_truth: false
evidence_level: L2
---

# TES TTS Skill Roadmap

This is the active dashboard for `tes-tts`: short, current, and
decision-oriented. Historical detail and dense artifact listings live in
`TES-TTS-SKILL-ROADMAP-REGISTRY.md` and
`TES-TTS-SKILL-ROADMAP-HISTORY.md`. ADR 0004 remains the architectural
boundary.

Partition contract:

- Dashboard: current state, active decisions, latest evidence, and next cut.
- Registry: durable artifact lists and grouped historical ranges.
- History: compressed lineage and lessons from closed sequences.
- Gates: `validate_doc_size.py` enforces the dashboard and partition budgets.

## Current State

Current product position:

- `tes-tts` is reactive delivered behavior only when explicitly requested.
- Runtime-first direction is active: durable runtime slices beat
  governance-only cycles.
- PT-BR is the primary quality target.
- OmniVoice is the current premium local provider path when the maintainer has
  configured the optional external Python environment and reference voice.
- `say` with `Felipe (Enhanced)` at rate `255` remains the offline fallback.
- Release identity, sync, push, tag, publish, provider redistribution, global
  config writes, and durable conversion cache remain unauthorized.

## Active Product Surfaces

Active surfaces are `.agents/skills/tes-tts/**`, Codex and Claude
`src/adapters/*/skills/tes-tts/**`, the dependency-free runtime scripts, the
optional OmniVoice provider facade/oracle, governed TTS benchmarks, and ADR
0004. Detailed registry: `TES-TTS-SKILL-ROADMAP-REGISTRY.md`.

## Product Decisions

- Reactive-only skill; no proactive `speak` behavior.
- Source text is immutable; speech uses request-local prepared text.
- Secrets are redacted before rendering and provider handoff.
- PT-BR is platform narration; English/technical identity is preserved.
- Runtime-first implementation beats governance-only cycles.
- OmniVoice is optional local capability, not bundled dependency.
- Version, release, sync, push, tag, and publish need separate approval.

## Current Evidence

Latest local product evidence:

- Recent commits: `eb44ce7` optional OmniVoice provider; `62fbc4b`
  product shortcut.
- Maintainer live rating: OmniVoice cloned voice result `9.5`.
- Local optional provider probe: `provider_available`; package remains
  dependency-optional.
- Package gate: `npm run commit:check` passed before the commit.
- Product shortcut: `status` auto-discovers the local OmniVoice env/reference,
  and `speak` delegates synthesis without long CLI arguments.
- Product benchmark: `bench --play --open --package` writes WAVs, metrics,
  review HTML, and ZIP manifest. `decide-review --review-json <exported-json>
  --package` seals `review-decision.json`. `product-status --format text`
  reports the provider cockpit for humans; `product-status --strict` gates
  promotion unless the sealed state is `AUDIO_CANDIDATE`. Latest packaged run
  produced `32.69s` of audio in `30.19s` total with average RTF `0.9422`;
  decision-sealed package SHA starts `0206b249`.

Relevant gates are the focused TTS provider/runtime/oracle suite,
`materialize_adapter.py all --check`, TDS/doc-size/reference validators, and
`npm run commit:check` when package closure is claimed.

## Next Decisions

Open decisions before public claims: release identity, provider redistribution
and license posture, sync/push/tag/publish, and the next concrete audible
quality or latency target.

Recommended next product cut:

1. Run `python3 scripts/tes_tts_omnivoice_provider.py bench --play --open --package`
   and score audible quality by fixture in the generated review page.
2. Export review JSON and run
   `python3 scripts/tes_tts_omnivoice_provider.py decide-review --review-json <exported-json> --package`.
3. Run `python3 scripts/tes_tts_omnivoice_provider.py product-status --format text --strict`.
4. Decide whether the OmniVoice provider path is ready for release identity
   planning or needs one targeted runtime/provider fix.
5. Keep docs limited to this dashboard, registry/history pointers, and the
   active audit result.

## Maintenance Rules

- Hard limit: 150 lines. Warning zone means partition before adding detail.
- Keep only current state, active decisions, next decisions, and latest
  evidence here.
- Move dense artifact listings to `TES-TTS-SKILL-ROADMAP-REGISTRY.md`.
- Move historical cycle detail to `TES-TTS-SKILL-ROADMAP-HISTORY.md`.
- Keep the root roadmap index grouped by product line, not by every prompt,
  SPEC, or audit artifact.
- Every `tes-tts` execution cycle must update this dashboard or record an
  explicit no-change rationale in the active audit/commit message.
- Do not use this roadmap to authorize sync, release, provider installs,
  provider downloads, or global config writes.

## Closure Rule

For material `tes-tts` changes, close only after the smallest relevant TTS
oracles pass plus the package gates needed for the touched surfaces. Use
`npm run commit:check` before claiming package closure. Do not claim release
closure without a release identity decision.
