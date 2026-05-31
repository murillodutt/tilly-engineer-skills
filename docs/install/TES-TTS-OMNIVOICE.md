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
.tes/runtime/tes-tts/omnivoice/
```

That directory is ignored by Git. It may contain the Python virtual
environment, reference audio, voice profile metadata, model caches, generated
audio, and protected voice prompt cache files.

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

Run these commands from the target repository root. Python 3.11 is the safest
default for the current TES local path; adjust only when OmniVoice upstream
requires a different version.

```bash
mkdir -p .tes/runtime/tes-tts/omnivoice
python3.11 -m venv .tes/runtime/tes-tts/omnivoice/venv
source .tes/runtime/tes-tts/omnivoice/venv/bin/activate
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

Place a short reference WAV under the local runtime. Upstream recommends a short
reference clip; TES currently standardizes on mono 24 kHz WAV for the local
profile.

```bash
mkdir -p .tes/runtime/tes-tts/omnivoice/refs
python3 scripts/tes_tts_omnivoice_provider.py normalize-ref \
  --input /path/to/your-reference.wav \
  --output .tes/runtime/tes-tts/omnivoice/refs/audio-modelo-clone-mono24k.wav
```

Create the profile metadata:

```bash
mkdir -p .tes/runtime/tes-tts/omnivoice/profiles/tes-tts-local-clone
cat > .tes/runtime/tes-tts/omnivoice/profiles/tes-tts-local-clone/meta.json <<'JSON'
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
chmod 700 .tes/runtime/tes-tts/omnivoice/profiles
chmod 600 .tes/runtime/tes-tts/omnivoice/profiles/tes-tts-local-clone/meta.json
```

The `language` value is the provider hint used for the current reference. Keep
the transcript faithful. A wrong transcript can harm cloning quality and may
increase latency because the provider has less reliable voice conditioning.

## Warm The Voice Prompt Cache

After installation and profile setup, verify status:

```bash
python3 scripts/tes_tts_omnivoice_provider.py status
python3 scripts/tes_tts_omnivoice_provider.py product-status
```

Warm the cache once:

```bash
python3 scripts/tes_tts_omnivoice_provider.py warm-cache
python3 scripts/tes_tts_omnivoice_provider.py warm-cache --dry-run
```

A healthy warmed profile reports `voice_prompt_cache_exists: true` on dry run.
The cache lives under:

```text
.tes/runtime/tes-tts/omnivoice/provider-cache/voice-prompts/
```

Treat `*.pt` files there as sensitive local voice artifacts. They must not be
committed, copied into public docs, or treated as portable fixtures.

## Read Text

Short reads:

```bash
python3 scripts/tes_tts_omnivoice_provider.py speak \
  --text "Teste real do TES-TTS com OmniVoice." \
  --output .tes/runtime/tes-tts/omnivoice/provider-cache/audio/latest.wav \
  --play
```

Long reads should use chunking and combined WAV output. The buffered first-audio
path reduces the wait before the first audible chunk while later chunks are
prepared.

```bash
python3 scripts/tes_tts_omnivoice_provider.py speak-long \
  --text-file /path/to/text.txt \
  --output-dir .tes/runtime/tes-tts/omnivoice/provider-cache/audio/tes-tts-run \
  --combine \
  --inter-chunk-silence-ms 450 \
  --first-audio-buffered \
  --first-audio-chars 160 \
  --first-audio-buffer-chunks 2 \
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
  -> WAV/playback is written under .tes/runtime/**
```

The server route is legacy lab compatibility only. It should not be promoted as
the product path unless a future accepted runtime decision explicitly changes
that direction.

## Troubleshooting

If `status` reports OmniVoice missing, confirm the venv path and run:

```bash
.tes/runtime/tes-tts/omnivoice/venv/bin/python -c "import omnivoice, torch; print(omnivoice.__version__); print(torch.__version__)"
```

If the first read is slow, run `warm-cache --dry-run`. A cache miss means the
profile has not been warmed or the reference metadata changed.

If pronunciation regresses, first inspect the prepared spoken text before
changing provider settings. Many technical-speech failures come from text
shape, not model quality.

If audio overlaps, cuts, or produces noisy boundaries, prefer shorter chunks and
longer `--inter-chunk-silence-ms` before changing voice or reinstalling the
provider.

If generated audio or model artifacts appear in Git status, stop and move them
back under `.tes/runtime/**` or `tmp/**`. TES package commits must not include
audio, model weights, venvs, or local voice cache artifacts.

## What TES Does Not Promise

This guide does not certify OmniVoice for every platform, language, GPU, or
voice. It documents the TES integration contract and the local setup path. The
quality target is practical engineering narration: good enough to listen to
technical work, compare results, and keep improving the runtime without turning
voice setup into the product itself.
