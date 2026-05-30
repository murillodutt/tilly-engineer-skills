---
name: tes-tts
description: Use when the user explicitly asks TES to read, speak, narrate, or test text-to-speech, including /tes-tts, /tes:tts, read this text aloud, leia em voz alta, narrar este texto, speed changes, or voice tests.
license: MIT
---

# TES TTS

Operational contract: `tes.tts@0.1.8`.

`/tes-tts` is the small TES text-to-speech skill. It reads user-provided text
aloud through whatever local TTS tool the host exposes. `/tes:tts` is a
compatible TES intent alias if the host reports it as an invalid slash.

## Workflow

1. Extract only the text the user wants read aloud.
2. Choose the request-local rendering intent:
   - `conversational` for agent-authored speech or user-requested natural
     narration;
   - `faithful_reading` for user-provided text, exact reads, or literal
     reading requests.
3. Convert Markdown, bullets, headings, small tables, links, file paths, and
   code fences into speech-friendly spoken rendering for the selected intent.
4. Preserve the user's meaning. Do not summarize unless asked.
5. Keep source text separate from the request-local spoken rendering. The
   spoken rendering is the only text sent to TTS.
   When the TES runtime helper is available, prepare this with
   `python3 scripts/tes_tts_runtime.py --text "<text>" --locale pt-BR` and use
   the returned `spoken_text`.
6. When the text is multilingual or the user asks for a standard/default
   reading language, load `references/language-normalization.md` and prepare a
   TTS conversion cache before playback.
7. Use the available local TTS tool. When multiple providers exist or one
   fails, load `references/providers-and-fallbacks.md` and apply the
   request-local fallback plan only for this read-aloud request. In a Codex
   host with `mcp-tts`, prefer `mcp__mcp_tts__say_tts`.
8. When the optional OmniVoice provider is already configured by the
   maintainer, prefer `scripts/tes_tts_omnivoice_provider.py` for premium
   cloned-voice reads, while preserving `say` as the local fallback.
9. Use `voice: "Felipe (Enhanced)"` and `rate: 255` when the tool accepts
   those settings. If the host rejects the voice, retry once with the default
   voice and the same text.
10. If the user asks for a different speed, use that speed for the current
   request. For a percentage change, compute it from the last spoken rate in
   this conversation; if there is no last rate, use `255` as the base.
11. Keep chat confirmation brief after playback.

## Modules

| Need | Load |
|------|------|
| Mixed-language text, default-language reading, or pronunciation adaptation | `references/language-normalization.md` |
| Provider choice, fallback, TTS error classification, or voice policy | `references/providers-and-fallbacks.md` |

## Spoken Rendering

- Use `conversational` intent when the content is agent-authored or the user
  asks for natural narration. Speak in oral prose, not tables, raw Markdown,
  YAML-like dumps, or mechanical bullet lists.
- Use `faithful_reading` intent when reading user-provided text, exact spans,
  code, commands, or anything the user asks to hear literally.
- Conversational rendering may add small oral connectors, such as "Primeiro",
  "Depois", and "Por fim", but it must not drop facts, invent intent, or merge
  separate decisions into a vague summary.
- Small tables become ordered row facts. Keep every row fact and preserve row
  order; for wider tables, speak each header/value pair in sequence.
- Bullets and numbered lists become ordered oral prose with connectors such as
  "Primeiro", "Depois", and "Por fim". Do not collapse the list into a
  summary.
- Quotes become explicit quoted speech, for example "Citacao: ...", without
  leaking Markdown `>` markers.
- Code blocks and commands are introduced as code text, spoken as text, and
  never executed.
- Exact handling is span-scoped inside conversational speech: preserve only the
  path, URL, command, code identifier, hash, quoted term, or other fragile span
  the user specifically asked to hear literally.
- Secret-like values are redacted before rendering and before TTS. Redaction
  overrides exact, literal, raw, and verbatim requests.

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
- Preserve scoped package names, branch names, model names, and code
  identifiers as protected identity before mention or path rendering can change
  them.
- Preserve raw URLs, paths, hashes, GUIDs, email addresses, IP addresses,
  mentions, hashtags, commands, and code-like spans only for the exact island
  requested by the user. Do not turn one literal cue into a global raw dump.
- Remove Markdown code fences while preserving the code or command text unless
  the user asks for a summary.
- Read dates clearly, preserving concrete dates.
- Keep product names, proper nouns, package/model names, commands, code
  identifiers, English-origin workflow terms, and mixed-language technical
  terms as written. Do not translate them into the system language.
- In PT-BR platform narration, keep English engineering words and product
  names as English identity: review, diff, patch, issue, milestone, backlog,
  roadmap, worktree, sandbox, GitHub Actions, Docker, Kubernetes, Node.js,
  TypeScript, Playwright, and MCP server.
- Use request-local pronunciation hints for protected terms when the active
  provider needs them. Prefer raw redacted source text for OmniVoice because
  local evidence shows it handles mixed PT-BR technical speech better than
  manual respelling.
- For long text, split into sensible chunks rather than dropping content.

## Safety

- Do not read secret-like values such as API keys, tokens, passwords, private
  keys, bearer tokens, environment values, or credentials aloud. Say that
  secret-like content was redacted. This remains true for exact reads.
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
