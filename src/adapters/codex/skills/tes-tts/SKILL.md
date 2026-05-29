---
name: tes-tts
description: Use when the user explicitly asks TES to read, speak, narrate, or test text-to-speech, including /tes-tts, /tes:tts, read this text aloud, leia em voz alta, narrar este texto, speed changes, or voice tests.
license: MIT
---

# TES TTS

Operational contract: `tes.tts@0.1.6`.

`/tes-tts` is the small TES text-to-speech skill. It reads user-provided text
aloud through whatever local TTS tool the host exposes. `/tes:tts` is a
compatible TES intent alias if the host reports it as an invalid slash.

## Workflow

1. Extract only the text the user wants read aloud.
2. Convert Markdown, bullets, headings, links, file paths, and code fences into
   speech-friendly plain text.
3. Preserve the user's meaning. Do not summarize unless asked.
4. Keep source text separate from the request-local spoken rendering. The
   spoken rendering is the only text sent to TTS.
5. When the text is multilingual or the user asks for a standard/default
   reading language, load `references/language-normalization.md` and prepare a
   TTS conversion cache before playback.
6. Use the available local TTS tool. When multiple providers exist or one
   fails, load `references/providers-and-fallbacks.md` and apply the
   request-local fallback plan only for this read-aloud request. In a Codex
   host with `mcp-tts`, prefer `mcp__mcp_tts__say_tts`.
7. Use `voice: "Felipe (Enhanced)"` and `rate: 225` when the tool accepts
   those settings. If the host rejects the voice, retry once with the default
   voice and the same text.
8. If the user asks for a different speed, use that speed for the current
   request. For a percentage change, compute it from the last spoken rate in
   this conversation; if there is no last rate, use `225` as the base.
9. Keep chat confirmation brief after playback.

## Modules

| Need | Load |
|------|------|
| Mixed-language text, default-language reading, or pronunciation adaptation | `references/language-normalization.md` |
| Provider choice, fallback, TTS error classification, or voice policy | `references/providers-and-fallbacks.md` |

## Text Cleanup

- Render common acronyms as speech text in non-exact mode: `ADR` -> `A D R`,
  `MCP` -> `M C P`, `API` -> `A P I`, `SDK` -> `S D K`, and `CLI` -> `C L I`.
- Render GitHub URLs as "pagina do GitHub" in non-exact mode; use "link" for
  generic URLs when the exact URL is not essential.
- Render file paths as useful folder or file references in non-exact mode, for
  example `.agents/skills/tes-tts` -> "pasta tes tts".
- Render long hashes and GUID-like identifiers as "hash" or "GUID" in
  non-exact mode.
- Render email addresses, valid IPv4 addresses, mentions, and hashtags into
  compact spoken forms in non-exact mode.
- Preserve raw URLs, paths, hashes, GUIDs, email addresses, IP addresses,
  mentions, hashtags, commands, and code-like spans when the user asks for
  exact, literal, raw, or verbatim reading.
- Remove Markdown code fences while preserving the code or command text unless
  the user asks for a summary.
- Read dates clearly, preserving concrete dates.
- Keep product names, proper nouns, package/model names, commands, code
  identifiers, English-origin workflow terms, and mixed-language technical
  terms as written. Do not translate them into the system language.
- Use request-local pronunciation hints for protected terms; do not claim IPA,
  SSML, phoneme, lexicon, provider-backed pronunciation, or Hebrew enrichment.
- For long text, split into sensible chunks rather than dropping content.

## Safety

- Do not read secret-like values such as API keys, tokens, passwords, private
  keys, or credentials aloud. Say that secret-like content was redacted.
- Do not use this skill for proactive status announcements. It is reactive to
  an explicit read-aloud or TTS request.
- Do not install providers, download provider assets, write global provider
  config, persist unavailable-provider state, or certify provider support from
  a read-aloud fallback.
- If no TTS tool is available, report `TTS_NOT_AVAILABLE` briefly and do not
  pretend audio played.

## Validation

When changing this skill, validate the folder:

```bash
python3 /Users/murillo/.codex/skills/.system/skill-creator/scripts/quick_validate.py <this-skill-dir>
```

## Done

`tes-tts` is done when the requested text has been spoken or the agent reports
`TTS_NOT_AVAILABLE`, with secrets protected and the spoken wording preserving
the user's requested meaning.
