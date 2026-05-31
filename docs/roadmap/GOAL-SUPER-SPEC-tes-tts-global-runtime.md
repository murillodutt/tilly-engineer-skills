---
tds_id: roadmap.goal_super_spec_tes_tts_global_runtime
tds_class: roadmap
status: active
consumer: maintainers, tes-tts maintainers, adapter authors, validation authors, and execution agents
source_of_truth: false
evidence_level: L1
---

# GOAL Super SPEC: TES TTS Global Runtime

Status: active global runtime migration line.

Canonical artifact:
`docs/roadmap/GOAL-SUPER-SPEC-tes-tts-global-runtime.md`

Current execution unit:
`GRT-001 Global OmniVoice Runtime Migration`

Ready prompt:
`none`

## Purpose

Move heavy OmniVoice runtime ownership out of project-local state and into the
user-level TES runtime:

```text
~/.tes/runtime/tes-tts/omnivoice
```

Project-local `.tes/**` remains only lightweight project state, install locks,
evidence, logs, and pointers. This prevents every TES-enabled project from
duplicating the provider venv, model/cache artifacts, generated audio, voice
prompt cache, and cloned voice profile.

## GRT-001 Contract

- Default provider resolution uses the global runtime.
- The legacy project runtime `.tes/runtime/tes-tts/omnivoice` is detection and
  migration-report only.
- If global runtime is valid, it is active.
- If only legacy project runtime exists, status reports `NEEDS_MIGRATION` with
  exact source and destination paths.
- If both exist, global runtime wins and legacy is reported as present.
- If neither exists, status reports setup truthfully without installing or
  downloading anything.
- Default voice profile remains `tes-tts-local-clone`.
- Reference WAV identity remains `audio-modelo-clone-mono24k.wav`.
- Voice prompt cache remains protected: directories `0700`, files `0600`.

## Locks

No sync, release, push, tag, publish, provider install, provider download,
automatic deletion of project-local runtime data, committed audio, committed
cache, committed model artifact, committed venv, global config write,
proactive speak behavior, or durable text conversion cache is authorized by
this line.
