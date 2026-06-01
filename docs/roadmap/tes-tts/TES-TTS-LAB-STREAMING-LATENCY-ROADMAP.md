---
tds_id: roadmap.tes_tts_lab_streaming_latency_roadmap
tds_class: roadmap
status: archived
consumer: maintainers, tes-tts maintainers, adapter authors, and execution agents
source_of_truth: false
evidence_level: L3
---

# TES TTS Lab Streaming Latency Roadmap

Status: archived after lab stop on 2026-06-01
Scope: historical local experiments only. MLX/streaming lab artifacts and
installed lab copies were removed after this evidence record; paths below are
audit pointers, not durable files. The canonical direct OmniVoice product
runtime is outside this lab cleanup.

## Mission

Reduce perceived TES-TTS latency for document reading while preserving the
current human-rated OmniVoice quality baseline. The lab will test a three-step
path: Apple Silicon scheduling, audible cross-fade, and a small TypeScript
queue player. If all three converge, the result can become a proprietary,
lightweight TES-TTS player/runtime path.

## Protected Baseline

- Direct local OmniVoice only; no server resurrection.
- Global runtime: `~/.tes/runtime/tes-tts/omnivoice`.
- Voice profile: `tes-tts-local-clone`.
- Live profile: `technical-live`, `num_step=28`.
- HD profile: `technical-hd`, `num_step=32`.
- Provider language: `en`.
- Text mode: `redacted_source`.
- Instruct: `male, middle-aged, low pitch`.
- No inline warmup tag by default.
- Source text immutable; secrets redacted; commands read as text; no summary.
- WAV evidence under `~/.tes/runtime/**` or `tmp/**`; never committed.

## Current Evidence

| Finding | Evidence | Decision |
| --- | --- | --- |
| Five concurrent OmniVoice workers on MPS are not viable. | `progressive-prefetch-lab-20260601`: first audio 30.3s, 7 projected underruns, max gap 6.59s. | Do not promote 5-worker MPS execution. |
| Sentence-aware first chunk is currently strongest. | `first-chunk-prefetch-benchmark-20260601/first-120`: first audio 6.93s, two chunks 18.85s. | Keep as baseline for streaming-latency work. |
| A single microchunk can start reasonably, but is not better than first-120. | `microchunk-single-worker-20260601`: first audio 8.33s for 5-word head. | Do not make 3-5 word chunks the default. |
| OmniVoice-Streaming offers useful architecture, not a direct product path. | Local references show sentence chunking, ordered queue, prompt reuse, chunk decode/merge optimization. | Mine mechanisms, not server route. |
| CPU inference is not viable for interactive first audio on this Apple Silicon runtime. | `cpu-micro-only-20260601`: 5-word chunk took 103.26s synthesis for 2.12s audio. | Reject CPU for live head generation unless a future runtime changes this evidence. |
| Upstream batch inference is not a low-latency replacement for short local reads. | `batch-only-lab-20260601`: TES provider batch took 37.93s for 5 chunks; upstream `omnivoice.cli.infer_batch` took 59.18s and produced longer 54.72s audio. | Keep upstream batch as learning/reference, not live path. |
| MLX community variants are installable and generate audio locally. | `mlx-variant-benchmark-20260601`: `OmniVoice-4bit` and `OmniVoice-bfloat16` both generated same-input WAVs through `ailuntx/OmniVoice-MLX`. | Keep MLX in lab; do not promote before resident/chunked benchmark and human audio review. |
| MLX cold single-shot did not clearly beat the current PyTorch/MPS product path. | Same-input short read: MLX 4bit `12031.917ms`, MLX bfloat16 `11725.072ms`, PyTorch/MPS control `12599.419ms`; all produced about 14.5s audio. | Treat MLX as a candidate for resident/chunked optimization, not an immediate replacement. |
| MLX resident first-120 is a credible streaming candidate. | `mlx-resident-first120-20260601`: bfloat16 first chunk `5792.703ms`, two chunks `11742.484ms`, total synthesis `33501.603ms`; 4bit first chunk `5570.696ms`, two chunks `11680.133ms`, total synthesis `34242.969ms`. | Continue MLX lab with playback-buffer and human-quality review before promotion. |
| Playback projection favors smaller MLX chunks for start latency. | `playback-queue-projection-20260601`: MLX bfloat16/4bit projected zero underruns with buffer 1; PyTorch/MPS same-input control projected a `4.289s` gap with buffer 1 and zero gap only after buffer 2. | Next real test should play MLX with buffer 1/2 and compare perceived continuity. |
| Same fixed chunks isolate provider speed from chunk planning. | `pytorch-mps-fixed5-first120-20260601`: PyTorch/MPS with the exact MLX 5-chunk plan had first audio `6959.230ms`, two chunks `14576.781ms`, synthesis `42325.224ms`; playback projection still found a `0.368s` buffer-1 gap. | MLX is faster on this machine, but chunk planning is also a product lever. |
| A TypeScript queue dry-run matches the Python projection. | `ts-queue-player-dry-run-20260601`: Node queue scheduler over measured chunks shows MLX bfloat16/4bit buffer 1 with zero projected underruns; PyTorch/MPS fixed 5 chunks still has one `0.368s` projected gap. | TS player can proceed to real playback timing with the same manifest contract. |
| Real `afplay` chunk playback has negligible process gap but chunk-edge silence remains. | `ts-queue-player-afplay-20260601-mlx-bfloat16-resident-first120-buffer1`: max observed process gap `0.100ms`, total `0.279ms`; `chunk-silence-probe-20260601`: MLX bfloat16 leading silence up to `427.667ms` and trailing up to `164.958ms` at `-45dB`. | Next audio work should trim/cross-fade chunk-edge silence, not chase process startup first. |
| Trim/cross-fade A/B variants are ready for human review. | `chunk-edge-ab-20260601`: control `56.190s`; trim45+silence120 `53.740s`; trim45+xfade80 `52.940s`; trim45+xfade120 `52.780s`; trim50+xfade80 `53.295s`; no clipping. | Listen before promotion; strongest candidates are `03-trim45-xfade-80` and `04-trim45-xfade-120`. |
| Boundary proxy favors safer trim before stronger cross-fade. | `boundary-click-probe-20260601`: exact-boundary max sample jump: control `0`, trim45+silence120 `0.000031`, trim45+xfade80 `0.002991`, trim45+xfade120 `0.011688`, trim50+xfade80 `0.003479`. | `04` is shortest but riskier; compare `03` against safer `05` by ear. |
| Human-listening A/B playback packet was executed. | `combined-ab-playback-20260601`: played `03-trim45-xfade-80` and `05-trim50-xfade-80`; `afplay` returned success for both. | Await maintainer score; no promotion yet. |
| Maintainer judged `03` and `05` quality equivalent. | `combined-ab-playback-20260601` human review: equivalent quality for `03-trim45-xfade-80` and `05-trim50-xfade-80`. | Prefer `05-trim50-xfade-80` as safer candidate unless future listening favors `03` rhythm. |
| Candidate `05` generalized mechanically but exposed pronunciation degradation. | `mlx-candidate05-generalization-20260601`: first audio `4949.696ms`, two chunks `10531.989ms`, synthesis `34926.290ms`, combined `42.928s`, no clipping, `afplay` success; maintainer reported degraded technical/English term pronunciation. | Preserve edge recipe; next test must improve technical English provider text before synthesis. |
| Technical-term surface A/B selected English island. | `technical-term-surface-ab-20260601`: control, English-island, and slow technical list all passed synthesis/playback; maintainer selected `02-english-island` as best pronunciation option. | Preserve candidate `05` edge recipe and test English-island surface as the next runtime-text candidate. |
| English-island real-text sample passed human review. | `english-island-real-text-20260601`: first audio `5691.307ms`, two chunks `11803.165ms`, synthesis `57548.031ms`, combined `85.491s`, no clipping, `afplay` success; maintainer rated it `MUITO_BOM`. | Strongest current candidate; next product work must generalize English-island preparation without hard-coded term lists. |
| English-island unseen-term sample is rejected for generality. | `english-island-unseen-terms-20260601`: first audio `5395.163ms`, two chunks `11003.164ms`, synthesis `35481.969ms`, combined `45.762s`, no clipping, but maintainer reported English pronunciation much below target for the new technical list. | Do not claim English-island generality; next test must solve technical English pronunciation and split/pace dense lists. |
| Unseen-term pacing A/B was rejected. | `unseen-terms-pacing-ab-20260601`: PT-BR framed and English framed paced lists both played, but maintainer rated English pronunciation incomprehensible. | Reject pacing/framing as sufficient; return to the pre-MLX human-rated baseline before new latency work. |
| MLX quality path is demoted after severe regression. | `unseen-terms-voice-mode-ab-20260601` was stopped as candidate evidence after maintainer identified severe regression against earlier pre-MLX PT-BR plus English readings. | Keep MLX only as latency lab evidence until it can match the PyTorch/MPS quality baseline. |
| PyTorch/MPS quality baseline retest was generated. | `pytorch-quality-unseen-terms-20260601`: `technical-live`, `num_step=28`, `instruct="male, middle-aged, low pitch"`, combined `21.48s`, first buffered playback `19090.029ms`, no unplanned gap. | Await maintainer score; this is the quality reference check against the MLX regression. |
| STT probe is auxiliary only. | `stt-quality-probe-20260601`: Whisper recognized 10/14 terms in PyTorch retest, 8/14 in rejected MLX PT-BR paced, and 10/14 in rejected MLX English paced. | Do not use STT as quality judge; it can flag missed terms but cannot override human listening. |
| Problem-term PyTorch/MPS A/B is ready for listening. | `pytorch-problem-term-ab-20260601`: raw, readable-alias, and CMU variants generated for FastAPI, Redis, JWT, and Playwright; STT saw raw `3/4`, alias `2/4`, CMU `3/4`, with Redis still missed. | Human listening decides; do not promote alias or CMU unless it beats raw by ear. |

## 2026-06-01 Lab Stop

Maintainer decision: evidence is sufficient to wait for OmniVoice ecosystem
evolution before another round. MLX remains latency-only historical evidence
because it regressed technical-English pronunciation. Installed MLX/streaming
lab runtimes, caches, model artifacts, WAVs, and local lab clones are obsolete
and removed after this record. The canonical direct OmniVoice runtime at
`~/.tes/runtime/tes-tts/omnivoice` remains the optional `tes-tts` product
provider path. Do not resume from deleted lab artifacts; restart future latency
research from fresh provider/community evidence and compare against the
documented PyTorch/MPS quality baseline.

## Degrau 1: Apple Silicon Parallelism

Goal: find the maximum safe scheduling strategy for Apple Silicon without
assuming CUDA-style parallelism.

### MLX Variant Checkpoint

Community reference:

- `mlx-community/OmniVoice` documents MLX-converted OmniVoice variants for
  Apple Silicon and points to `ailuntx/OmniVoice-MLX` as the runtime.
- Local lab runtime: `~/.tes/runtime/tes-tts/omnivoice-mlx`.
- Local MLX models:
  - `~/.tes/runtime/tes-tts/omnivoice-mlx/models/OmniVoice-4bit`
  - `~/.tes/runtime/tes-tts/omnivoice-mlx/models/OmniVoice-bfloat16`

Executed steps:

1. Read official/community model cards before runtime decisions.
2. Installed and isolated `ailuntx/OmniVoice-MLX` under the global lab runtime.
3. Downloaded `mlx-community/OmniVoice-4bit` and
   `mlx-community/OmniVoice-bfloat16` under the MLX runtime model cache.
4. Generated same-input WAVs with the canonical clone reference,
   `language=en`, `num_step=28`, and no product default change.
5. Generated a PyTorch/MPS control WAV through the current direct provider.

Evidence:

- Manifest:
  `~/.tes/runtime/tes-tts/omnivoice-mlx/provider-cache/audio-reference-runs/mlx-variant-benchmark-20260601/manifest.json`
- MLX 4bit WAV:
  `~/.tes/runtime/tes-tts/omnivoice-mlx/provider-cache/audio-reference-runs/mlx-variant-benchmark-20260601/mlx-4bit/sample.wav`
- MLX bfloat16 WAV:
  `~/.tes/runtime/tes-tts/omnivoice-mlx/provider-cache/audio-reference-runs/mlx-variant-benchmark-20260601/mlx-bfloat16/sample.wav`
- PyTorch/MPS control WAV:
  `~/.tes/runtime/tes-tts/omnivoice/provider-cache/audio-reference-runs/mlx-variant-benchmark-20260601/pytorch-mps-control/sample.wav`

Measured cold single-shot result:

| Variant | Wall time | Audio duration | Decision |
| --- | ---: | ---: | --- |
| MLX 4bit | `12031.917ms` | `14.64s` | viable lab candidate, not promoted |
| MLX bfloat16 | `11725.072ms` | `14.46s` | strongest MLX cold result so far |
| PyTorch/MPS control | `12599.419ms` | `14.68s` | remains product baseline |

MLX promotion requires a resident/chunked comparison because cold CLI
single-shot time does not prove lower perceived latency.

Resident/chunked evidence:

- Manifest:
  `~/.tes/runtime/tes-tts/omnivoice-mlx/provider-cache/audio-reference-runs/mlx-resident-first120-20260601/manifest.json`
- MLX bfloat16 combined WAV:
  `~/.tes/runtime/tes-tts/omnivoice-mlx/provider-cache/audio-reference-runs/mlx-resident-first120-20260601/mlx-bfloat16-resident-first120/combined.wav`
- MLX 4bit combined WAV:
  `~/.tes/runtime/tes-tts/omnivoice-mlx/provider-cache/audio-reference-runs/mlx-resident-first120-20260601/mlx-4bit-resident-first120/combined.wav`

Measured resident first-120 result:

| Variant | Load | Voice prompt | First audio | Two chunks | Synthesis wall | Combined duration | Decision |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| MLX bfloat16 resident | `465.638ms` | `834.710ms` | `5792.703ms` | `11742.484ms` | `33501.603ms` | `54.99s` | strongest current MLX candidate |
| MLX 4bit resident | `1186.892ms` | `731.071ms` | `5570.696ms` | `11680.133ms` | `34242.969ms` | `54.73s` | slightly faster first chunk, slower total |

The resident result is the first MLX evidence that looks product-relevant:
after a two-chunk buffer, synthesis appears able to stay ahead of playback for
this 5-chunk sample. It still requires human audio review and a queue-player
gap measurement before promotion.

Playback projection evidence:

- Manifest:
  `~/.tes/runtime/tes-tts/omnivoice-mlx/provider-cache/audio-reference-runs/playback-queue-projection-20260601/manifest.json`
- PyTorch/MPS same-input control:
  `~/.tes/runtime/tes-tts/omnivoice/provider-cache/audio-reference-runs/pytorch-mps-resident-first120-20260601/result.json`
- PyTorch/MPS control WAV:
  `~/.tes/runtime/tes-tts/omnivoice/provider-cache/audio-reference-runs/pytorch-mps-resident-first120-20260601/combined.wav`
- PyTorch/MPS fixed 5-chunk control:
  `~/.tes/runtime/tes-tts/omnivoice/provider-cache/audio-reference-runs/pytorch-mps-fixed5-first120-20260601/manifest.json`
- PyTorch/MPS fixed 5-chunk WAV:
  `~/.tes/runtime/tes-tts/omnivoice/provider-cache/audio-reference-runs/pytorch-mps-fixed5-first120-20260601/combined.wav`

Projection result:

| Variant | Buffer | Start latency | Projected underruns | Max projected gap | Note |
| --- | ---: | ---: | ---: | ---: | --- |
| MLX bfloat16 resident | `1` | `5.791s` | `0` | `0.000s` | best quality-leaning candidate |
| MLX 4bit resident | `1` | `5.569s` | `0` | `0.000s` | fastest first audio so far |
| PyTorch/MPS product control | `1` | `6.949s` | `1` | `4.289s` | same input, product planner made 3 chunks |
| PyTorch/MPS product control | `2` | `18.488s` | `0` | `0.000s` | no gap, but start latency too high |
| PyTorch/MPS fixed 5 chunks | `1` | `6.959s` | `1` | `0.368s` | isolates chunk planning from provider |
| PyTorch/MPS fixed 5 chunks | `2` | `14.577s` | `0` | `0.000s` | better than product planner, still slower than MLX |

The PyTorch/MPS product control used the same text, but its current planner
produced three larger chunks. The fixed 5-chunk control removes that ambiguity:
smaller chunks improve the product route, while MLX still wins first audio,
two-chunk readiness, and total synthesis for this sample. The next decision
requires human listening of `combined.wav` plus a real queue-player run.

Lab variants:

1. `mps-1w-first120`: one resident MPS worker, first-120 sentence-aware
   chunking, two-chunk playback buffer.
2. `mps-2w-semaphore`: two resident MPS workers behind an ordered queue and
   concurrency cap of two.
3. `mlx-bfloat16-resident-first120`: one resident MLX bfloat16 worker with
   first-120 sentence-aware chunking.
4. `mlx-4bit-resident-first120`: one resident MLX 4bit worker with first-120
   sentence-aware chunking.
5. `cpu-1w-microhead`: retained only as rejected baseline unless a future
   runtime changes the CPU evidence.

Required metrics:

- provider startup ms;
- time to first audio;
- time to two chunks ready;
- total synthesis wall time;
- provider synthesis sum;
- audio duration;
- projected underrun count;
- max unplanned gap ms;
- human quality note.

Promotion gate:

- first audio improves over `first-120`;
- max unplanned gap is zero or below the human-audible threshold accepted in
  review;
- quality does not regress from the `technical-live` baseline;
- provider cost does not explode like the 5-worker lab run.

## Degrau 2: Audible Cross-Fade

Goal: smooth chunk boundaries without eating words, overlapping speech, or
masking latency failures.

Lab variants:

1. `silence-450`: current fixed silence control.
2. `fade-80`: fade-out/fade-in without overlap.
3. `xfade-80`: true overlap mix.
4. `xfade-120`: true overlap mix.
5. `xfade-160`: true overlap mix.
6. `xfade-200`: stress case for over-blending.

Required metrics:

- combined WAV path;
- chunk boundary timestamps;
- overlap duration;
- RMS change near boundaries;
- max clipped sample;
- human boundary rating;
- notes for lost word, doubled word, or audible seam.

Promotion gate:

- human listener prefers cross-fade over silence control;
- no clipped audio;
- no lost or doubled words;
- same chunk WAVs can produce both control and cross-fade outputs for fair A/B.

## Degrau 3: TypeScript Queue Player

Goal: prove a minimal playback loop that separates synthesis from playback and
keeps ordered audio flowing.

Minimal player contract:

- reads a manifest with numeric chunk order;
- waits for the configured buffer count before starting;
- plays chunks in order even if synthesis finishes out of order;
- preloads next WAVs before the current one ends;
- records `queued`, `ready`, `playing`, `ended`, `gap_ms`, and `underrun`;
- writes a playback report under `tmp/**` or `~/.tes/runtime/**`;
- does not synthesize, mutate text, or execute spoken content.

Lab variants:

1. `player-combined-control`: compare against `combined.wav`.
2. `player-two-buffer`: start after two chunks ready.
3. `player-three-buffer`: start after three chunks ready.
4. `player-adaptive-buffer`: start when projected ready audio exceeds a
   configurable threshold.

Promotion gate:

- playback gaps are lower than direct chunk-by-chunk `afplay`;
- perceived start time remains acceptable;
- player does not hide synthesis underruns;
- report is deterministic enough to drive future regression tests.

Dry-run evidence:

- Manifest:
  `~/.tes/runtime/tes-tts/omnivoice-mlx/provider-cache/audio-reference-runs/ts-queue-player-dry-run-20260601/manifest.json`
- Scope: TypeScript queue scheduler only, no audio playback.
- Result: MLX bfloat16 and 4bit project zero underruns with buffer 1; PyTorch/MPS fixed 5 chunks still projects one `0.368s` gap with buffer 1 and needs buffer 2 for zero gap.

Next player step: real playback timing over the same manifest contract,
capturing process start/end, observed gap, and whether `afplay` startup adds
human-audible pauses not present in `combined.wav`.

Real playback and edge-silence evidence:

- Real playback manifest:
  `~/.tes/runtime/tes-tts/omnivoice-mlx/provider-cache/audio-reference-runs/ts-queue-player-afplay-20260601/mlx-bfloat16-resident-first120-buffer1.json`
- Silence probe manifest:
  `~/.tes/runtime/tes-tts/omnivoice-mlx/provider-cache/audio-reference-runs/chunk-silence-probe-20260601/manifest.json`

The measured `afplay` process gap for MLX bfloat16 buffer 1 was tiny:
`0.100ms` max and `0.279ms` total across chunk boundaries. However, chunk WAVs
carry their own leading/trailing silence. At `-45dB`, MLX bfloat16 reached
`427.667ms` leading silence and `164.958ms` trailing silence; MLX 4bit reached
`423.875ms` leading and `142.917ms` trailing; PyTorch/MPS fixed 5 chunks
reached `247.500ms` leading and `332.792ms` trailing. The next useful
experiment is therefore chunk-edge trimming or cross-fade over identical WAVs,
with the original chunks retained for A/B review.

Cross-fade A/B evidence:

- Manifest:
  `~/.tes/runtime/tes-tts/omnivoice-mlx/provider-cache/audio-reference-runs/chunk-edge-ab-20260601/manifest.json`
- Control WAV:
  `~/.tes/runtime/tes-tts/omnivoice-mlx/provider-cache/audio-reference-runs/chunk-edge-ab-20260601/01-control-silence-450/combined.wav`
- Candidate WAVs:
  - `~/.tes/runtime/tes-tts/omnivoice-mlx/provider-cache/audio-reference-runs/chunk-edge-ab-20260601/02-trim45-silence-120/combined.wav`
  - `~/.tes/runtime/tes-tts/omnivoice-mlx/provider-cache/audio-reference-runs/chunk-edge-ab-20260601/03-trim45-xfade-80/combined.wav`
  - `~/.tes/runtime/tes-tts/omnivoice-mlx/provider-cache/audio-reference-runs/chunk-edge-ab-20260601/04-trim45-xfade-120/combined.wav`
  - `~/.tes/runtime/tes-tts/omnivoice-mlx/provider-cache/audio-reference-runs/chunk-edge-ab-20260601/05-trim50-xfade-80/combined.wav`

All variants preserved source chunks and generated only derived combined WAVs
for local review. No variant clipped. Trimmed variants reduced combined leading
and trailing silence to about `80ms` at `-45dB`. The shortest candidate is
`04-trim45-xfade-120` at `52.780s`; the less aggressive cross-fade candidate is
`03-trim45-xfade-80` at `52.940s`. Human listening decides whether either loses
words, doubles consonants, or sounds unnaturally tight.

Boundary proxy:

- Manifest:
  `~/.tes/runtime/tes-tts/omnivoice-mlx/provider-cache/audio-reference-runs/boundary-click-probe-20260601/manifest.json`
- Exact-boundary max sample jump:
  - `01-control-silence-450`: `0.000000`
  - `02-trim45-silence-120`: `0.000031`
  - `03-trim45-xfade-80`: `0.002991`
  - `04-trim45-xfade-120`: `0.011688`
  - `05-trim50-xfade-80`: `0.003479`

This is a click/cut proxy, not an audio-quality verdict. It suggests `04` buys
the shortest file with higher transition risk, while `03` is a balanced
candidate and `05` is technically safer but less aggressive.

Human-listening packet:

- Manifest:
  `~/.tes/runtime/tes-tts/omnivoice-mlx/provider-cache/audio-reference-runs/combined-ab-playback-20260601/manifest.json`
- Played candidates:
  - `03-trim45-xfade-80`, duration `52.940s`, `afplay` wall `53289.477ms`
  - `05-trim50-xfade-80`, duration `53.295s`, `afplay` wall `54057.783ms`

The playback packet is intentionally decision-neutral. Promotion requires a
maintainer listening score and notes for continuity, lost words, doubled words,
and natural rhythm.

Maintainer review result: `03-trim45-xfade-80` and `05-trim50-xfade-80` have
equivalent perceived quality. Because quality is equivalent, the current lab
candidate is `05-trim50-xfade-80`: it is slightly less aggressive, carries a
low exact-boundary jump (`0.003479`), and preserves more safety margin than
`04-trim45-xfade-120`. This is a lab candidate, not a product promotion.

Generalization sample:

- Manifest:
  `~/.tes/runtime/tes-tts/omnivoice-mlx/provider-cache/audio-reference-runs/mlx-candidate05-generalization-20260601/manifest.json`
- WAV:
  `~/.tes/runtime/tes-tts/omnivoice-mlx/provider-cache/audio-reference-runs/mlx-candidate05-generalization-20260601/combined-candidate05.wav`
- Metrics:
  - first audio: `4949.696ms`
  - two chunks ready: `10531.989ms`
  - synthesis wall: `34926.290ms`
  - combined duration: `42.928s`
  - peak: `0.437098`
  - `afplay` wall: `43894.164ms`

This second sample includes technical English terms, a folder reference, a
command-as-text, and a redacted secret marker. It proves the candidate edge
recipe can run outside the original sample, but the maintainer review marked
technical and English term pronunciation as degraded. The next experiment must
hold the `05` edge recipe constant and vary only pre-synthesis technical-term
provider text, so continuity and pronunciation are not conflated.

### Technical English Quality Checkpoint

MLX improved first-audio latency, but human review found severe technical
English regression once terms moved beyond the first successful sample.

- `technical-term-surface-ab-20260601`: English island won within MLX.
- `english-island-real-text-20260601`: human review `MUITO_BOM`.
- `english-island-unseen-terms-20260601`: human review
  `QUALITY_REGRESSION_TECHNICAL_ENGLISH`.
- `unseen-terms-pacing-ab-20260601`: human review
  `INCOMPREHENSIBLE_ENGLISH_PRONUNCIATION`.
- `unseen-terms-voice-mode-ab-20260601`: human review
  `REGRESSION_AGAINST_PRE_MLX_BASELINE`.

Decision: MLX is latency evidence only until it can match the PyTorch/MPS
quality baseline. The current quality source of truth remains:

- HD baseline:
  `~/.tes/runtime/tes-tts/omnivoice/provider-cache/audio-reference-runs/instruct-premium-hd-20260601/01-instruct-male-middle-aged-low-pitch-num-step-32.wav`
- Live recipe: PyTorch/MPS direct OmniVoice, `tes-tts-local-clone`,
  `language=en`, `redacted_source`, `instruct="male, middle-aged, low pitch"`,
  `num_step=28`, semicolon pauses, no inline audible tag.
- Latest quality retest:
  `~/.tes/runtime/tes-tts/omnivoice/provider-cache/audio-reference-runs/pytorch-quality-unseen-terms-20260601/combined.wav`
  with result metadata beside it; human review pending.
- STT probe:
  `~/.tes/runtime/tes-tts/omnivoice/provider-cache/audio-reference-runs/stt-quality-probe-20260601/manifest.json`.
  It is diagnostic only: Whisper term recognition did not align cleanly with
  human intelligibility judgments.

## Systematic Lab Record

Every run must write a compact manifest with this shape:

```json
{
  "run_id": "descriptive-id",
  "status": "PASS | DEGRADED | FAIL",
  "step": "apple-silicon | cross-fade | ts-player",
  "baseline": "first-120 technical-live",
  "recipe": {
    "provider": "omnivoice",
    "route": "direct_resident",
    "device": "mps | cpu",
    "workers": 1,
    "num_step": 28,
    "text_mode": "redacted_source",
    "instruct": "male, middle-aged, low pitch"
  },
  "metrics": {
    "time_to_first_audio_ms": 0,
    "ready_after_two_chunks_ms": 0,
    "synthesis_wall_ms": 0,
    "max_unplanned_gap_ms": 0
  },
  "artifacts": {
    "combined_wav": "path",
    "manifest": "path"
  },
  "human_review": {
    "score": null,
    "notes": ""
  },
  "decision": "promote | repeat | reject"
}
```

## Promotion Rules

- Product defaults move only after same-input A/B evidence and human review.
- Server paths remain legacy lab references, not product routes.
- CUDA claims stay out of TES-TTS until tested on CUDA hardware.
- Apple Silicon changes must be validated on this runtime before promotion.
- A narrower special case is not acceptable unless represented as governed
  data or a deliberate profile.

## Next Lab Action

No active lab action. A future round must start from new OmniVoice/community
evidence, install only lab candidates in disposable runtime space, and beat the
documented PyTorch/MPS quality baseline by same-input human review before
promotion.
