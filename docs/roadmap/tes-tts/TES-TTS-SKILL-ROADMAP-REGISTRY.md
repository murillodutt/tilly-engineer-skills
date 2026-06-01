---
tds_id: roadmap.tes_tts_skill_roadmap_registry
tds_class: roadmap
status: active
consumer: maintainers, tes-tts maintainers, adapter authors, and release reviewers
source_of_truth: false
evidence_level: L2
---

# TES TTS Roadmap Registry

This registry keeps dense `tes-tts` artifact pointers out of the active
roadmap dashboard. Add only durable surfaces or grouped ranges; avoid listing
every prompt when a range is enough.

## Runtime And Skill Surfaces

| Surface | Role | Status |
|---------|------|--------|
| `.agents/skills/tes-tts/**` | Local development and live test workbench. | active |
| `src/adapters/codex/skills/tes-tts/**` | Codex adapter source. | active |
| `src/adapters/claude/skills/tes-tts/**` | Claude adapter source. | active |
| `src/adapters/*/skills/tes-tts/agents/openai.yaml` | Agent-facing invocation guidance. | active |
| `src/adapters/*/skills/tes-tts/docs/CONTRACT-HISTORY.md` | Skill lineage, contracts, and failure modes. | active |
| `src/adapters/*/skills/tes-tts/references/language-normalization.md` | Default-language and pronunciation normalization reference. | active |
| `src/adapters/*/skills/tes-tts/references/providers-and-fallbacks.md` | Provider order, fallback, error classes, and voice policy. | active |

## Runtime Scripts And Oracles

| Surface | Role | Status |
|---------|------|--------|
| `scripts/tes_tts_runtime.py` | CLI facade for dependency-free preparation. | active |
| `scripts/tes_tts_runtime_adapter.py` | Shared adapter for runtime preparation. | active |
| `scripts/tes_tts_runtime_ir_oracle.py` | Runtime IR contract oracle. | active |
| `scripts/tes_tts_fast_path_spoken_rendering_oracle.py` | Fast-path spoken rendering oracle. | active |
| `scripts/tes_tts_live_session_utterance_oracle.py` | Live mixed PT-BR/English utterance oracle. | active |
| `scripts/tes_tts_runtime_latency_oracle.py` | Text-preparation latency oracle. | active |
| `scripts/tes_tts_provider_probe_oracle.py` | Request-local provider probe and fallback oracle. | active |
| `scripts/tes_tts_provider_candidate_review_oracle.py` | Candidate review queue oracle. | active |
| `scripts/tes_tts_omnivoice_provider.py` | Optional OmniVoice direct/resident status, warm-cache, session, live-smoke review packages, auto latency-profile selection, product-status cockpit, candidate replay/open cockpit, speak, bench, review, decide-review, package-review, probe, synthesize, normalize-ref, and batch facade. | active |
| `scripts/tes_tts_omnivoice_runtime_support.py` | Direct/resident runtime helpers for playback, WAV combine, JSONL process control, chunk planning, and monitoring. | active |
| `scripts/tes_tts_omnivoice_provider_oracle.py` | Optional OmniVoice provider safety oracle. | active |
| `scripts/tes_tts_roadmap_partition_oracle.py` | Dashboard, registry, and history partition oracle. | active |

## Benchmark Fixtures

| Surface | Role | Status |
|---------|------|--------|
| `benchmarks/tes-tts/normalization-*.json` | Normalization schema and corpus fixtures. | active |
| `benchmarks/tes-tts/instruction-normalizer-fixtures.json` | Instruction-level normalizer fixtures. | active |
| `benchmarks/tes-tts/provider-probe-fixtures.json` | Mocked provider probe fixtures. | active |
| `benchmarks/tes-tts/provider-fallback-fixtures.json` | Request-local fallback fixtures. | active |
| `benchmarks/tes-tts/provider-candidate-review.json` | Provider candidate review queue. | active |
| `benchmarks/tes-tts/pronunciation-catalog-fixtures.json` | Protected term pronunciation catalog. | active |
| `benchmarks/tes-tts/runtime-ir-fixtures.json` | Runtime IR fixtures. | active |
| `benchmarks/tes-tts/live-session-utterance-fixtures.json` | Real mixed-language utterance fixtures. | active |
| `benchmarks/tes-tts/runtime-latency-fixtures.json` | Latency measurement fixtures. | active |
| `benchmarks/tes-tts/ptbr-lexical-*.json*` | PT-BR lexical manifest, lookup, and integration fixtures. | active |
| `benchmarks/tes-tts/omnivoice-provider-cases.json` | Optional OmniVoice provider benchmark cases. | active |

## Governing Documents

| Surface | Role | Status |
|---------|------|--------|
| `docs/adr/0004-tes-tts-pronunciation-normalization-and-enrichment.md` | Architectural boundary. | active |
| `docs/roadmap/tes-tts/TES-TTS-SKILL-ROADMAP.md` | Current dashboard and next decisions. | active |
| `docs/roadmap/tes-tts/TES-TTS-SKILL-ROADMAP-HISTORY.md` | Compressed evolution history. | active |
| `docs/roadmap/tes-tts/TES-TTS-OWNER-001-ACCEPTANCE-DECISION.md` | ADR 0004 owner acceptance record. | active |
| `docs/roadmap/tes-tts/TES-TTS-RTE-006-RUNTIME-AUDIT-AND-CLOSURE.md` | Runtime-first closure audit. | active |
| `docs/roadmap/tes-tts/TES-TTS-RUNTIME-PYTHON-OPTIMIZATION-AUDIT.md` | Provider hot-path optimization audit and target map. | active |
| `docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-tes-tts-global-runtime.md` | Global user-level OmniVoice runtime migration authority. | active |
| `docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-tes-tts-omnivoice-prosody-warmup.md` | Controlled OmniVoice prosody warmup quality line. | active |
| `docs/roadmap/goals/prompts/tes-tts/GOAL-PROMPT-tes-tts-OPW-001-controlled-prosody-warmup-runtime-option.md` | Ready circular prompt for the first provider-tag warmup runtime option. | active |
| `docs/roadmap/goals/prompts/tes-tts/GOAL-PROMPT-tes-tts-RTO-001-provider-hot-path-split.md` | Executed circular prompt for provider hot-path split. | historical |
| `docs/roadmap/goals/prompts/tes-tts/GOAL-PROMPT-tes-tts-RTO-002-provider-oracle-partition.md` | Executed circular prompt for provider oracle partition. | historical |
| `docs/roadmap/goals/prompts/tes-tts/GOAL-PROMPT-tes-tts-RTO-003-timing-attribution-cleanup.md` | Executed circular prompt for provider timing attribution cleanup. | historical |
| `docs/roadmap/goals/prompts/tes-tts/GOAL-PROMPT-tes-tts-RTO-004-direct-kernel-boundary-hardening.md` | Executed circular prompt for direct kernel boundary hardening. | historical |
| `docs/roadmap/goals/prompts/tes-tts/GOAL-PROMPT-tes-tts-RTO-005-instruction-normalizer-runtime-alignment.md` | Executed circular prompt for instruction-normalizer runtime alignment and local RTO closure. | historical |
| `docs/roadmap/goals/prompts/tes-tts/GOAL-PROMPT-tes-tts-TFA-001-buffered-first-audio-benchmark.md` | Executed circular prompt for buffered first-audio benchmark and implementation. | historical |
| `docs/roadmap/tes-tts/TES-TTS-TFA-001-BUFFERED-FIRST-AUDIO-BENCHMARK.md` | TFA-001 benchmark result, first-audio metrics, and local closure. | active |
| `docs/roadmap/tes-tts/TES-TTS-LAB-STREAMING-LATENCY-ROADMAP.md` | Archived lab roadmap for Apple Silicon scheduling, cross-fade, and TypeScript queue player evidence. | historical |
| `docs/roadmap/tes-tts/TES-TTS-ACCEPTANCE-AND-RELEASE-DECISION.md` | Release identity decision record. | active |

## Historical Ranges

| Range | Meaning | Status |
|-------|---------|--------|
| `GOAL-PROMPT-tes-tts-TTS-000*.md` through `TTS-032*.md` | Baseline, acceptance, and owner-decision prompts. | historical |
| `TES-TTS-OWNER-*.md` | Owner-decision records TTS-010 through TTS-031. | historical |
| `TES-TTS-SPEC-001-*.md` through `TES-TTS-SPEC-010-*.md` | Ten-SPEC convergence draft/result set. | historical |
| `TES-TTS-CAP-*.md` and matching prompts | Capability migration and conversational rendering sequence. | historical |
| `TES-TTS-LEX-*.md` and matching prompts | PT-BR lexical foundation sequence. | historical |
| `TES-TTS-RTE-*.md` and matching prompts | Runtime engine and latency sequence. | historical |

## Indexing Rule

New durable artifacts must be indexed in TDS only when they are stable
continuation surfaces. Ephemeral local audio, caches, provider downloads, venvs,
and scratch benchmark outputs remain under `tmp/**` and stay out of this
registry.
