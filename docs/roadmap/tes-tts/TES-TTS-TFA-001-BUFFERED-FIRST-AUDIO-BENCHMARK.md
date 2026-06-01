---
tds_id: roadmap.tes_tts_tfa_001_buffered_first_audio_benchmark
tds_class: roadmap
status: active
consumer: maintainers, tes-tts maintainers, adapter authors, validation authors, and execution agents
source_of_truth: false
evidence_level: L3
---

# TES TTS TFA-001 Buffered First-Audio Benchmark

TFA-001 implemented an opt-in buffered first-audio path for direct/resident
OmniVoice long reads. The accepted quality recipe remains `quality`,
`language en`, 420-char normal chunks, 450 ms inter-chunk silence, and combined
WAV output for repeat review.

## Result

Status: PASS.

Baseline combined-only run:
`tmp/tes-tts-omnivoice-provider/tfa-001-baseline/20260530-2250/result.json`

- chunks: 3
- startup: 3991.886 ms
- total provider synthesis: 45312.914 ms
- combine: 1.221 ms
- deterministic time-to-ready-for-audio proxy: 49776.669 ms
- combined WAV:
  `tmp/tes-tts-omnivoice-provider/tfa-001-baseline/20260530-2250/combined.wav`

Candidate buffered first-audio run:
`tmp/tes-tts-omnivoice-provider/tfa-001-candidate/20260530-2251/result.json`

- chunks: 4, with a 153-char first-audio head and 2-chunk buffer
- startup: 3014.442 ms
- time-to-first-audio: 21929.043 ms
- total provider synthesis: 51815.938 ms
- combine: 1.323 ms
- max unplanned playback gap: 0.073 ms
- combined WAV:
  `tmp/tes-tts-omnivoice-provider/tfa-001-candidate/20260530-2251/combined.wav`

Measured improvement:
`(49776.669 - 21929.043) / 49776.669 = 55.94%`.

## Behavior

The new path is opt-in through `speak-long --first-audio-buffered`. It starts
background playback only after the configured buffer is ready, continues
synthesis while audio is playing, preserves combined WAV output, and reports
`time_to_first_audio_ms`, played chunk count, planned gap, and max unplanned
gap in the result payload.

No provider install, download, sync, release, global config write, durable
conversion cache, committed audio/cache/model/venv, command execution from
spoken content, source mutation, or user-text summary was performed.

## Closure

No follow-up prompt is created. The TFA line closes locally because the first
audible output begins before full synthesis completes, the improvement exceeds
the 40% target, and no immediate measured defect remains.
