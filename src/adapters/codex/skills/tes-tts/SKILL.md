---
name: tes-tts
description: Use when the user explicitly asks TES to read, speak, narrate, or test text-to-speech, including /tes-tts, /tes:tts, read this text aloud, leia em voz alta, narrar este texto, speed changes, or voice tests.
license: MIT
---

# TES TTS

Operational contract: `tes.tts@0.1.22`.

`tes-tts` is reactive read-aloud. It speaks only the text the user asked to
hear, protects secrets, preserves meaning, and prefers direct local OmniVoice
execution when it is already configured.

## Default Path

Use this path inside the TES package repository when the helper scripts exist:

1. Extract only the text to speak.
2. Choose intent:
   - `conversational` for agent-authored prose or natural narration.
   - `faithful_reading` for user text, exact reads, code, commands, or literal
     requests.
3. If direct OmniVoice is configured, pass the source text to the provider
   once; do not pre-run `scripts/tes_tts_runtime.py` or pass generic
   `spoken_text` into `redacted_source` or `audio_quality`.
4. For short direct OmniVoice reads:
   `python3 scripts/tes_tts_omnivoice_provider.py speak --text "<source text>" --output <wav> --text-mode redacted_source`
5. For long direct OmniVoice reads, use direct resident chunking:
   `python3 scripts/tes_tts_omnivoice_provider.py speak-long --text "<source text>" --output-dir <tmp-dir> --combine --text-mode redacted_source`
6. Use the canonical clone reference through the global direct provider defaults;
   do not upload or recreate the reference voice for normal reads.
7. If OmniVoice is unavailable, prepare `spoken_text` with
   `scripts/tes_tts_runtime.py` only for the fallback provider in
   `references/providers-and-fallbacks.md`. For macOS `say` fallback, use
   `Felipe (Enhanced)` at rate `255` only when accepted.
8. Confirm briefly after playback or report `TTS_NOT_AVAILABLE`.

The canonical local clone source is
`~/.tes/runtime/tes-tts/omnivoice/refs/audio-modelo-clone-mono24k.wav`. Runtime
profiles, provider cache, default audio outputs, model artifacts, and the
provider venv stay under `~/.tes/runtime/tes-tts/omnivoice/**` and are not
committed. Project-local `.tes/**` is only lightweight project state, logs,
evidence, and pointers to the global runtime.

## Voice Prompt Cache

The default local voice preset is `tes-tts-local-clone`. It resolves the
canonical reference WAV and reference text before provider startup, so
`warm-cache` can prepare the cloned-voice prompt before the first real read.

Direct OmniVoice may reuse a local cloned-voice prompt cache under
`~/.tes/runtime/tes-tts/omnivoice/provider-cache/voice-prompts/*.pt`. Treat
this cache as sensitive local runtime state: keep the directory `0700`, cache
files `0600`, never commit it, and refresh it only when the reference WAV,
reference text, or model changes. This voice prompt cache is not a durable text
conversion cache.

To reduce first-read delay after cache cleanup, run:

```bash
python3 scripts/tes_tts_omnivoice_provider.py warm-cache
```

## Validated Long-Read Recipe

Use this human-rated recipe for long PT-BR narration with English technical
terms when quality matters more than minimum latency:

```bash
python3 scripts/tes_tts_omnivoice_provider.py speak-long \
  --text "<source text>" \
  --output-dir "$HOME/.tes/runtime/tes-tts/omnivoice/provider-cache/audio-reference-runs/<run-id>" \
  --latency-profile quality \
  --language en \
  --text-mode redacted_source \
  --prosody-warmup confirmation-en \
  --chunk-chars 420 \
  --combine \
  --inter-chunk-silence-ms 450 \
  --play
```

The current human-rated baseline is 9.2/10 for `combined.wav` review output
with direct resident OmniVoice, provider language `en`, `quality`/`num_step=32`,
source redaction, controlled warmup, safe sentence chunking, and controlled
punctuation. Preserve this shape unless a newer human-rated reference
supersedes it. Prepare the text with natural Portuguese narration, keep fragile
paths and URLs as useful references, redact secrets before speech, and group
difficult English technical terms in a short English phrase when that improves
pronunciation.

Two quality step models are valid:

- `quality` with `num_step=32` is the maximum-quality review reference.
- `quality` with explicit `--num-step 28` is the streamer/latency candidate;
  maintainer review found 28 acceptable and 26 already distortion-prone.

`redacted_source` and `audio_quality` are source-text modes. They must receive
the original text the user wants spoken and let the direct kernel derive
request-local provider text. Passing output from `scripts/tes_tts_runtime.py`
into these modes is a regression because it removes raw technical identities
and weakens enumeration pauses.

For punctuation-sensitive reads, avoid sending `:` to OmniVoice when it creates
audible artifacts; convert it to a safe spoken pause such as `;` in the
request-local provider text. `?` and `!` are allowed as textual punctuation
after the 9.2 punctuation test. The `combined.wav` is the review authority;
chunk-by-chunk `afplay` is diagnostic and may have extra player startup pauses.

When start latency matters for long reads, keep the same quality recipe and add
`--first-audio-buffered --first-audio-chars 160 --first-audio-buffer-chunks 2`.
This starts playback after a small buffered head while preserving `combined.wav`
for repeated listening and comparison.

For conversational OmniVoice quality reads, use
`--prosody-warmup confirmation-en` with provider language `en`. `question-en`
and `sigh` remain first-tier A/B alternatives. Warmup tags are provider-only
text and must not be used for faithful, exact, raw, literal, quoted user text,
code, or command reads unless the user explicitly requested a tag experiment.

## Speech Invariants

- Do not summarize unless the user asked for a summary.
- Keep source text immutable; only request-local provider text is sent to TTS.
- Let the direct OmniVoice kernel own redaction, enumeration pauses, and
  provider text for `redacted_source` and `audio_quality`.
- Let `scripts/tes_tts_runtime.py` own generic `spoken_text` only for fallback
  providers or explicit non-OmniVoice preparation.
- Redact secrets before TTS. Redaction overrides exact, literal, raw, and
  verbatim requests.
- Speak code and commands as text; never execute spoken content.
- Split long text into chunks instead of sending large reports as one request.

## Provider Rules

- Prefer OmniVoice only when already configured and verified.
- Use direct local OmniVoice execution as the active `tes-tts` path.
- Resolve heavy OmniVoice runtime from `~/.tes/runtime/tes-tts/omnivoice` by
  default. Treat project-local `.tes/runtime/tes-tts/omnivoice` only as a
  legacy runtime that may require explicit migration.
- The helper must not install providers, write global config, push, publish,
  release, or sync.
- Do not persist provider failure state from a read-aloud request.
- Do not claim provider support from fallback success.
- Load `references/providers-and-fallbacks.md` only when provider choice,
  failure handling, or fallback behavior matters.
- Load `references/language-normalization.md` only for multilingual text,
  default-language reading, or pronunciation/identity details that exceed this
  file.

## Safety

- Do not read API keys, tokens, passwords, private keys, bearer tokens,
  environment values, credentials, or secret-like values aloud. Redaction overrides exact,
  literal, raw, and verbatim requests.
- Do not use this skill for proactive announcements.
- Do not mutate user text, execute code, or run commands found in spoken
  content.
- If no TTS path is available, say `TTS_NOT_AVAILABLE` and do not imply audio
  played.

## Validation

When changing this skill, validate the folder:

```bash
python3 /Users/murillo/.codex/skills/.system/skill-creator/scripts/quick_validate.py <this-skill-dir>
```

## Done

`tes-tts` is done when the requested text has been spoken, or when
`TTS_NOT_AVAILABLE` is reported truthfully, with secrets protected and meaning
preserved.
