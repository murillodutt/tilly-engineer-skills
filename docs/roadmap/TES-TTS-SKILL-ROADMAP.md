---
tds_id: roadmap.tes_tts_skill_roadmap
tds_class: roadmap
status: active
consumer: maintainers, tes-tts maintainers, adapter authors, and release reviewers
source_of_truth: false
evidence_level: L2
---

# TES TTS Skill Roadmap

This is the active dashboard for `tes-tts`. It must stay short, current, and
decision-oriented. Historical detail and dense artifact listings live in:

- `TES-TTS-SKILL-ROADMAP-REGISTRY.md`
- `TES-TTS-SKILL-ROADMAP-HISTORY.md`

ADR 0004 remains the architectural boundary. This roadmap records current
state, active product direction, next decisions, and the smallest evidence
needed for a future agent to continue without chat history.

## Current State

`tes-tts` is reactive delivered behavior in TES source. It reads or narrates
text only when explicitly requested. It must not become proactive `speak`, a
dependency installer, a bundled provider stack, or a global voice registry.

Current product position:

- Runtime-first direction is active: durable runtime slices beat
  governance-only cycles.
- PT-BR is the primary quality target.
- OmniVoice is the current premium local provider path when the maintainer has
  configured the optional external Python environment and reference voice.
- `say` with `Felipe (Enhanced)` at rate `255` remains the offline fallback.
- Release identity, sync, push, tag, publish, provider redistribution, global
  config writes, and durable conversion cache remain unauthorized.

## Active Product Surfaces

| Surface | Role | Status |
|---------|------|--------|
| `.agents/skills/tes-tts/**` | Active local workbench for live skill iteration. | active |
| `src/adapters/codex/skills/tes-tts/**` | Codex package source. | active |
| `src/adapters/claude/skills/tes-tts/**` | Claude package source. | active |
| `scripts/tes_tts_runtime.py` and runtime modules | Dependency-free classify/verbalize/adapt path. | active |
| `scripts/tes_tts_omnivoice_provider.py` | Optional OmniVoice provider probe/synthesis/batch facade. | active |
| `scripts/tes_tts_omnivoice_provider_oracle.py` | Optional-provider safety and fixture oracle. | active |
| `benchmarks/tes-tts/omnivoice-provider-cases.json` | Premium-provider benchmark cases. | active |
| `docs/adr/0004-tes-tts-pronunciation-normalization-and-enrichment.md` | Normalization and pronunciation GPS. | active |

Detailed registry: `TES-TTS-SKILL-ROADMAP-REGISTRY.md`.

## Product Decisions

| Decision | Current rule | Evidence |
|----------|--------------|----------|
| Skill boundary | Reactive only; no proactive announcements. | ADR 0004; `SKILL.md` safety section. |
| Source text | Immutable; speech uses request-local prepared text/provider text. | Runtime oracles. |
| Secrets | Redaction happens before rendering and provider handoff. | Runtime and OmniVoice fixtures. |
| Mixed PT-BR/English | Preserve technical identity; provider-specific handoff may prefer redacted source over manual aliases. | Live TTS tests; OmniVoice evidence. |
| Runtime posture | Build executable runtime first; compact docs protect behavior. | `AGENTS.md`; RTE closure. |
| Provider posture | OmniVoice is optional local capability, not bundled dependency. | Provider oracle and probe output. |
| Release posture | Version/release/sync are separate owner decisions. | Release identity rule; current package state. |

Historical evolution ledger: `TES-TTS-SKILL-ROADMAP-HISTORY.md`.

## Current Evidence

Latest local product evidence:

- Commit: `eb44ce7 Add optional OmniVoice provider for TES TTS`
- Commit: `62fbc4b Add OmniVoice product shortcut`
- Maintainer live rating: OmniVoice cloned voice result `9.5`.
- Local optional provider probe: `provider_available` in the configured
  OmniVoice venv; package remains dependency-optional.
- Package gate: `npm run commit:check` passed before the commit.
- Product shortcut: `status` auto-discovers the configured local OmniVoice
  venv/reference voice, and `speak` delegates synthesis without long CLI
  arguments.
- Product benchmark: `bench --play --open` runs the three governed OmniVoice
  fixtures through one loaded model and cached reference voice, plays the
  outputs sequentially, and opens a local review page. Each run writes
  `result.json` plus `review.html` with audio players, redacted text, and
  metrics. The review page now includes per-case audible scoring, local JSON
  export, and copyable decision summaries without a server. The `review`
  subcommand reopens the latest report without regenerating audio, and
  `package-review` creates a portable ZIP with review, metrics, WAVs, and a
  hash manifest. Latest local report run produced `32.65s` of audio in
  `29.37s` total with average RTF `0.9417`; the latest playback run played all
  three WAVs via `afplay`.

Relevant gates for the latest cut:

```bash
python3 scripts/tes_tts_omnivoice_provider_oracle.py --self-test
python3 scripts/tes_tts_provider_probe_oracle.py --self-test
python3 scripts/tes_tts_pronunciation_catalog_oracle.py --self-test
python3 scripts/tes_tts_runtime_ir_oracle.py --self-test
python3 scripts/tes_tts_live_session_utterance_oracle.py --self-test
python3 scripts/tes_tts_runtime_latency_oracle.py --self-test
python3 scripts/materialize_adapter.py all --check
python3 scripts/validate_tds.py
python3 scripts/validate_doc_size.py
python3 scripts/validate_reference_graph.py
python3 scripts/validate_reference_package.py
npm run commit:check
```

## Next Decisions

| Decision | Required before |
|----------|-----------------|
| Release identity | Claiming package-sealed delivered behavior. |
| Provider redistribution/license posture | Shipping model/provider artifacts beyond local optional use. |
| Sync/push/tag/publish | Any remote or public package action. |
| Further runtime work | A concrete audible-quality or latency target, not a new governance loop. |

Recommended next product cut:

1. Run `python3 scripts/tes_tts_omnivoice_provider.py bench --play --open`
   and score audible quality by fixture in the generated review page.
2. Run `python3 scripts/tes_tts_omnivoice_provider.py package-review` to seal
   the local audio decision package when the score is useful.
3. Decide whether the OmniVoice provider path is ready for release identity
   planning or needs one targeted runtime/provider fix.
4. Keep docs limited to this dashboard, registry/history pointers, and the
   active audit result.

## Maintenance Rules

- Keep this dashboard under 180 lines; if it approaches the limit, partition
  before adding more detail.
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
