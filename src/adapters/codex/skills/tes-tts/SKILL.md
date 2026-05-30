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
3. Prepare request-local speech text:
   `python3 scripts/tes_tts_runtime.py --text "<text>" --locale pt-BR`
   and send only the returned `spoken_text` to TTS.
4. If direct OmniVoice is configured, speak with:
   `python3 scripts/tes_tts_omnivoice_provider.py speak --text "<spoken_text>" --output <wav>`
5. For long text, use direct resident chunking:
   `python3 scripts/tes_tts_omnivoice_provider.py speak-long --text "<spoken_text>" --output-dir <tmp-dir> --combine`
6. Use the canonical clone reference through the local direct provider defaults;
   do not upload or recreate the reference voice for normal reads.
7. If OmniVoice is unavailable, use the request-local provider fallback in
   `references/providers-and-fallbacks.md`. For macOS `say` fallback, use
   `Felipe (Enhanced)` at rate `255` only when accepted.
8. Confirm briefly after playback or report `TTS_NOT_AVAILABLE`.

The canonical local clone source is
`tmp/tes-tts-lab/omnivoice/refs/audio-modelo-clone-mono24k.wav`. Profile and
audio outputs stay under `tmp/**` and are not committed.

## Validated Long-Read Recipe

Use this human-rated recipe for long PT-BR narration with English technical
terms when quality matters more than minimum latency:

```bash
python3 scripts/tes_tts_omnivoice_provider.py speak-long \
  --text "<prepared text>" \
  --output-dir "tmp/tes-tts-omnivoice-provider/audio-variant-lab/<run-id>" \
  --latency-profile quality \
  --language en \
  --text-mode redacted_source \
  --chunk-chars 420 \
  --combine \
  --inter-chunk-silence-ms 450 \
  --play
```

This recipe was rated 7.5/10 for a long mixed PT-BR technical read. Preserve
its shape unless a newer human-rated reference supersedes it: direct resident
`speak-long`, provider language `en`, `quality` profile, combined WAV, 420-char
chunks, and 450 ms silence between chunks. Prepare the text with natural
Portuguese narration, keep fragile paths and URLs as useful references, redact
secrets before speech, and group difficult English technical terms in a short
English phrase when that improves pronunciation.

## Speech Invariants

- Do not summarize unless the user asked for a summary.
- Keep source text immutable; only `spoken_text` is sent to TTS.
- Let `scripts/tes_tts_runtime.py` own rendering, exact islands, protected
  terms, paths, URLs, tables, lists, and mixed-language preparation.
- Redact secrets before TTS. Redaction overrides exact, literal, raw, and
  verbatim requests.
- Speak code and commands as text; never execute spoken content.
- Split long text into chunks instead of sending large reports as one request.

## Provider Rules

- Prefer OmniVoice only when already configured and verified.
- Use direct local OmniVoice execution as the active `tes-tts` path.
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
  environment values, or credentials aloud. Redaction overrides exact,
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
