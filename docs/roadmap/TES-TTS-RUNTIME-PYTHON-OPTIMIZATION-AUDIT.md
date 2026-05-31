---
tds_id: roadmap.tes_tts_runtime_python_optimization_audit
tds_class: roadmap
status: active
consumer: maintainers, tes-tts maintainers, adapter authors, and execution agents
source_of_truth: false
evidence_level: L2
---

# TES TTS Runtime Python Optimization Audit

This audit is the execution surface for the next `tes-tts` optimization line.
It exists to drive code work, not to start another governance loop.

## Evidence Snapshot

- Branch state before this audit: `main...origin/main [ahead 79]`, clean.
- Tracked server/lab route residue was already purged from product commands.
- Active provider help exposes direct/resident commands only:
  `probe`, `status`, `warm-cache`, `normalize-ref`, `prepare-prompt`,
  `serve`, `synthesize`, `batch`, `speak`, `speak-long`, `session`,
  `live-smoke`, `bench`, `profile-review`, `review`, `decide-review`,
  `product-status`, `candidate`, and `package-review`.
- Largest Python TTS surfaces now are:
  `tes_tts_omnivoice_provider.py` at 3530 lines,
  `tes_tts_omnivoice_provider_oracle.py` at 2246 lines,
  `tes_tts_instruction_normalizer_oracle.py` at 1082 lines,
  `tes_tts_audio_audit.py` at 664 lines, and
  `tes_tts_runtime_classifier.py` at 584 lines.

## Optimization Targets

| Priority | Target | Reason | Desired Result |
|----------|--------|--------|----------------|
| P0 | Provider monolith | Active runtime, review UI, packaging, parser, chunking, and session control share one 3530-line script. | Split stable helpers by responsibility while preserving CLI compatibility. |
| P0 | Provider oracle monolith | 2246-line oracle repeats subprocess and payload checks across product and package paths. | Table-driven partitions with the same coverage and clearer failure output. |
| P0 | Lab vocabulary | The old lab-named output directory remained in skill recipes after the purge. | Use product-neutral `audio-reference-runs` for human-rated comparison output. |
| P1 | Normalizer oracle drift | Old instruction-normalizer logic predates the runtime IR path and duplicates rendering behavior. | Keep only regression coverage that protects current runtime behavior. |
| P1 | Timing attribution | Provider timing exists, but hot path stages are still harder to compare than they should be. | Stable per-stage metrics for prompt cache, model load, synthesis, combine, and playback exclusion. |
| P1 | Direct kernel boundary | Direct kernel is clean but should stay narrow as provider code is split. | Kernel owns resident model and prompt cache only. |
| P2 | Audio audit | STT/audio analysis is useful but maintainer-only. | Keep optional, isolated, and never part of read-aloud hot path. |

## First Code Cut

Start with the smallest durable provider split:

1. Extract product-path payload helpers and command-shared direct execution
   helpers out of `tes_tts_omnivoice_provider.py` only when the extracted module
   is used by `speak`, `speak-long`, `session`, or `product-status`.
2. Do not extract review HTML, packaging, or benchmark code first unless a
   direct product-path edit proves it is blocking cleanup.
3. Keep CLI behavior and output JSON stable.
4. Keep generated audio, caches, reference runs, downloads, and venvs under
   `tmp/**`.

## Guardrails

- No provider install, download, certification, sync, release, push, tag,
  publish, version bump, bundle generation, global config write, proactive
  speak behavior, committed audio, committed cache, committed model artifact,
  committed venv, command execution from spoken content, or user-text summary.
- Optimize code first. Add or update docs only when they keep the active
  execution line unambiguous.
- Commit local only until new order.
