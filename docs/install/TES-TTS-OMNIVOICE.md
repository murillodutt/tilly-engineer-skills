---
tds_id: install.tes_tts_omnivoice
tds_class: adapter
status: active
consumer: adopters, installing agents, tes-tts users, and maintainers
source_of_truth: true
evidence_level: L2
tver: 0.1.0
---

# TES TTS OmniVoice Guide

`tes-tts` is a reactive text-to-speech skill: it speaks only when the user asks
for reading, narration, or a voice test. The default TES contract still protects
secrets, treats commands and code as text, preserves source text, and prepares a
request-local spoken rendering before provider execution.

OmniVoice is the preferred premium local provider when the user chooses to
install it. TES does not bundle OmniVoice, redistribute model weights, or require
it for normal package installation. The provider is optional because it may
download external model assets, uses a Python environment, and carries voice
cloning responsibilities that must remain explicit.

## What This Adds

The OmniVoice path gives `tes-tts` a local cloned-voice provider with stronger
quality than platform fallback voices. The current TES product path is direct
local execution, not a server. Runtime files live under:

```text
~/.tes/runtime/tes-tts/omnivoice/
```

That user-level directory is outside package source and shared by all
TES-enabled projects on the same machine. It may contain the Python virtual
environment, reference audio, voice profile metadata, model caches, generated
audio, and protected voice prompt cache files. Project-local `.tes/**` is only
for lightweight state, logs, evidence, locks, and pointers.

The active default voice profile is:

```text
tes-tts-local-clone
```

The profile points to a local reference WAV and reference transcript. It lets
TES resolve the voice without recloning or rediscovering the reference on every
run. The voice prompt cache is protected local runtime state, not a durable text
conversion cache and not a committed artifact.

## External Project

OmniVoice is maintained by `k2-fsa`. Its public README describes it as a
massively multilingual zero-shot TTS model with voice cloning, voice design,
command-line tools, and fast inference. Its installation section supports PyPI
and source installs, with PyTorch installed first for the target accelerator.

Use the upstream project as the source for hardware-specific install decisions:

- [k2-fsa/OmniVoice](https://github.com/k2-fsa/OmniVoice)
- [OmniVoice community projects](https://github.com/k2-fsa/OmniVoice/blob/master/docs/community-projects.md)

TES only documents how to place OmniVoice behind `tes-tts` once the user chooses
that provider.

## Provider Controls Audit

OmniVoice exposes provider-specific controls that can enrich speech, but TES
keeps them behind code-defined profiles and explicit experiments. They are a
quality layer on top of redaction, chunking, and request-local provider text,
not a replacement for those safety surfaces.

Confirmed by the local OmniVoice reference and upstream documentation:

| Capability | Confirmed surface | TES posture |
|------------|-------------------|-------------|
| Non-verbal tags | `[laughter]`, `[sigh]`, `[confirmation-en]`, `[question-en]`, `[question-ah]`, `[question-oh]`, `[question-ei]`, `[question-yi]`, `[surprise-ah]`, `[surprise-oh]`, `[surprise-wa]`, `[surprise-yo]`, `[dissatisfaction-hnn]` | Experimental. Allow only by explicit opt-in or controlled fixture; never inject into faithful user text by default. |
| English pronunciation override | CMU bracket form such as `[B EY1 S]` | Experimental provider control. It may improve isolated English words, but it is not a generic TES pronunciation contract. |
| Chinese pronunciation override | Pinyin with tone numbers | Out of PT-BR scope for the current default voice. |
| Voice-design `instruct` | gender, age, pitch, `whisper`, English accents, and Chinese dialects | Active PT-BR quality surface for cloned voice. TES uses `male, middle-aged, low pitch` as a silent prosody instruction in code-defined long-read profiles. |
| Generation parameters | `num_step`, `guidance_scale`, `speed`, `duration`, `audio_chunk_duration`, and `audio_chunk_threshold` | Runtime-tuning surface. TES fixes PT-BR Live at `num_step=28` and PT-BR HD audio at `num_step=32`; 26 was distortion-prone in maintainer review. |

Not certified for TES from the current local evidence: `[sniff]`, `[gasp]`,
`singing`, `[Speaker_1]:`, `[Speaker_2]:`, and multi-speaker dialogue. They may
exist in community wrappers, but they must not be documented as TES-supported
until the active OmniVoice runtime proves them with local audio.

Provider tags are also an injection boundary. If a user asks for faithful
reading of text that contains bracket tags, TES should read them as text unless
the user explicitly requests an OmniVoice tag experiment. Secret redaction still
wins over every provider control.

The active product option is intentionally narrow. Manual `--prosody-warmup`
accepts only `none`, `confirmation-en`, `question-en`, or `sigh`, and defaults
to `none`. Code-defined long-read profiles own the approved product recipe:
`technical-live` and `technical-hd` use provider language `en`,
`redacted_source`, no inline provider tag, and
`instruct="male, middle-aged, low pitch"`. Live uses `num_step=28` for lower
latency; HD uses `num_step=32` for audio review and was human-rated 9.3 at
`instruct-premium-hd-20260601/01-instruct-male-middle-aged-low-pitch-num-step-32.wav`.
TES does not mutate source text, does not enable CMU by default, and does not
apply tags to faithful, exact, raw, literal, quoted user text, code, or command
reads unless the user explicitly requested that provider-tag experiment.
Repeating `confirmation-en` on every chunk is preserved only as an explicit
experiment pattern, not as product default.

The most promising enrichment path is practical and narrow:

1. Preserve the existing direct cloned-voice recipe.
2. Keep sentence-aware chunking and controlled punctuation as the default.
3. Add a small opt-in audio experiment for confirmed non-verbal tags and CMU
   overrides.
4. Promote only tags that improve generated WAV review without causing
   surprise sounds, language leakage, or pronunciation regression.

## Safety Rules

Use a voice you own or are authorized to clone. Do not use this path for
impersonation, fraud, unauthorized cloning, or public distribution of another
person's voice. Keep reference audio, generated audio, model cache, and voice
prompt cache in ignored local runtime folders unless the user explicitly
authorizes a different destination.

TES keeps these boundaries:

- no proactive speech;
- no command execution from spoken content;
- no user-text summary unless requested;
- secret redaction before provider execution;
- source text remains immutable;
- generated audio stays local by default;
- provider absence is `TTS_NOT_AVAILABLE` or `DEGRADED`, not a package failure.

## Install OmniVoice For TES

Run these commands from any TES-enabled project. Installed TES helpers live in
`.tes/bin/**`; use `scripts/**` only when you are operating inside the TES
package source tree. Python 3.11 is the safest default for the current TES
global runtime path; adjust only when OmniVoice upstream requires a different
version.

```bash
mkdir -p "$HOME/.tes/runtime/tes-tts/omnivoice"
python3.11 -m venv "$HOME/.tes/runtime/tes-tts/omnivoice/venv"
source "$HOME/.tes/runtime/tes-tts/omnivoice/venv/bin/activate"
python -m pip install --upgrade pip
```

Install PyTorch for your hardware first. Examples:

```bash
# Apple Silicon
python -m pip install torch==2.8.0 torchaudio==2.8.0

# NVIDIA CUDA example from upstream docs; choose the wheel that matches your CUDA.
python -m pip install torch==2.8.0+cu128 torchaudio==2.8.0+cu128 \
  --extra-index-url https://download.pytorch.org/whl/cu128
```

Then install OmniVoice:

```bash
# Stable PyPI release
python -m pip install omnivoice

# Or latest source, when you intentionally want upstream master
python -m pip install git+https://github.com/k2-fsa/OmniVoice.git
```

The first real synthesis may download model assets through OmniVoice or
Hugging Face. That is an OmniVoice runtime action, not a TES package install
action.

## Configure The Default Voice Profile

Place a short reference WAV under the global runtime. Upstream recommends a
short reference clip; TES currently standardizes on mono 24 kHz WAV for the
local profile.

```bash
TES_TTS_PROVIDER=".tes/bin/tes_tts_omnivoice_provider.py"
test -f "$TES_TTS_PROVIDER" || TES_TTS_PROVIDER="scripts/tes_tts_omnivoice_provider.py"

mkdir -p "$HOME/.tes/runtime/tes-tts/omnivoice/refs"
python3 "$TES_TTS_PROVIDER" normalize-ref \
  --input /path/to/your-reference.wav \
  --output "$HOME/.tes/runtime/tes-tts/omnivoice/refs/audio-modelo-clone-mono24k.wav"
```

Create the profile metadata:

```bash
mkdir -p "$HOME/.tes/runtime/tes-tts/omnivoice/profiles/tes-tts-local-clone"
cat > "$HOME/.tes/runtime/tes-tts/omnivoice/profiles/tes-tts-local-clone/meta.json" <<'JSON'
{
  "id": "tes-tts-local-clone",
  "provider": "omnivoice",
  "status": "active",
  "ref_audio": "../../refs/audio-modelo-clone-mono24k.wav",
  "ref_text": "Short transcript of the reference audio, written exactly as spoken.",
  "language": "en",
  "latency_profile": "quality"
}
JSON
chmod 700 "$HOME/.tes/runtime/tes-tts/omnivoice/profiles"
chmod 600 "$HOME/.tes/runtime/tes-tts/omnivoice/profiles/tes-tts-local-clone/meta.json"
```

The `language` value is the provider hint used for the current reference. Keep
the transcript faithful. A wrong transcript can harm cloning quality and may
increase latency because the provider has less reliable voice conditioning.

## Warm The Voice Prompt Cache

After installation and profile setup, verify status:

```bash
TES_TTS_PROVIDER=".tes/bin/tes_tts_omnivoice_provider.py"
test -f "$TES_TTS_PROVIDER" || TES_TTS_PROVIDER="scripts/tes_tts_omnivoice_provider.py"

python3 "$TES_TTS_PROVIDER" probe
python3 "$TES_TTS_PROVIDER" status
python3 "$TES_TTS_PROVIDER" product-status
```

Warm the cache once:

```bash
python3 "$TES_TTS_PROVIDER" warm-cache
python3 "$TES_TTS_PROVIDER" warm-cache --dry-run
```

A healthy warmed profile reports `voice_prompt_cache_exists: true` on dry run.
The cache lives under:

```text
~/.tes/runtime/tes-tts/omnivoice/provider-cache/voice-prompts/
```

Treat `*.pt` files there as sensitive local voice artifacts. They must not be
committed, copied into public docs, or treated as portable fixtures.

## Read Text

Short reads:

```bash
python3 "$TES_TTS_PROVIDER" speak \
  --text "Teste real do TES-TTS com OmniVoice." \
  --output "$HOME/.tes/runtime/tes-tts/omnivoice/provider-cache/audio/latest.wav" \
  --play
```

Optional conversational warmup, for explicit comparison runs only:

```bash
python3 "$TES_TTS_PROVIDER" speak \
  --text "Narração técnica curta para comparação." \
  --prosody-warmup confirmation-en \
  --output "$HOME/.tes/runtime/tes-tts/omnivoice/provider-cache/audio/warmup.wav" \
  --play
```

Long reads should use a code-defined read profile, chunking, and combined WAV
output. `technical-live` is the human-approved PT-BR interactive reference:
direct resident OmniVoice, `language=en`, `redacted_source`, no inline warmup
tag, `instruct="male, middle-aged, low pitch"`, `num_step=28`, chunk size
`420`, `450 ms` combined-WAV silence, and buffered first audio. `technical-hd`
is the audio/review profile with the same recipe at `num_step=32`.
Compatibility aliases remain: `technical-streamer` maps to Live and
`technical-quality` maps to HD.

```bash
python3 "$TES_TTS_PROVIDER" speak-long \
  --text "$(cat /path/to/text.txt)" \
  --output-dir "$HOME/.tes/runtime/tes-tts/omnivoice/provider-cache/audio/tes-tts-run" \
  --read-profile technical-live \
  --play
```

Use generated WAV files for human review. Audio files make it easier to pause,
replay, compare versions, and diagnose whether a problem came from text
preparation, provider pronunciation, chunking, playback, or hardware latency.

## TES Runtime Shape

The intended path is:

```text
user request
  -> tes_tts_runtime.py prepares request-local spoken_text
  -> direct OmniVoice provider executes local synthesis
  -> WAV/playback is written under ~/.tes/runtime/**
```

The server route is legacy lab compatibility only. It should not be promoted as
the product path unless a future accepted runtime decision explicitly changes
that direction.

## Troubleshooting

`probe` and `status` auto-resolve
`~/.tes/runtime/tes-tts/omnivoice/venv/bin/python` before declaring provider
availability. Pass `--python` only for explicit diagnostics or overrides. If an
explicit `--python` run reports `provider_runtime_present_but_wrong_interpreter`,
rerun without `--python` or point it at the runtime venv:

```bash
"$HOME/.tes/runtime/tes-tts/omnivoice/venv/bin/python" -c "import omnivoice, torch; print(omnivoice.__version__); print(torch.__version__)"
```

If `status` reports `NEEDS_MIGRATION`, a legacy project-local runtime was found
under `.tes/runtime/tes-tts/omnivoice/` and no valid global runtime was found.
Move it manually to `~/.tes/runtime/tes-tts/omnivoice/` only after reviewing the
source and destination. TES reports the exact paths but does not delete or move
user data automatically.

If the first read is slow, run `warm-cache --dry-run`. A cache miss means the
profile has not been warmed or the reference metadata changed.

If pronunciation regresses, first inspect the prepared spoken text before
changing provider settings. Many technical-speech failures come from text
shape, not model quality.

If audio overlaps, cuts, or produces noisy boundaries, prefer shorter chunks and
longer `--inter-chunk-silence-ms` before changing voice or reinstalling the
provider.

If generated audio or model artifacts appear in Git status, stop and move them
back under `~/.tes/runtime/**` or `tmp/**`. TES package commits must not
include audio, model weights, venvs, or local voice cache artifacts.

## What TES Does Not Promise

This guide does not certify OmniVoice for every platform, language, GPU, or
voice. It documents the TES integration contract and the local setup path. The
quality target is practical engineering narration: good enough to listen to
technical work, compare results, and keep improving the runtime without turning
voice setup into the product itself.
