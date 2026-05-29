# TTS Providers And Fallbacks

Use this reference when a local host exposes more than one TTS provider, when a
TTS call fails, when the user requests a voice/provider, or when spoken text
needs provider-specific cleanup.

This reference absorbs only portable lessons from `speak`. `tes-tts` remains
reactive: it speaks only because the user asked to read, narrate, or speak
specific text. Do not add proactive announcements, project voice assignment,
global provider persistence, or summary-oriented planning/issue/summary modes.

## Provider Order

Prefer providers in this order when they are locally available:

```text
google -> openai -> elevenlabs -> say
```

Provider use is opportunistic. Do not install, configure, download, or persist
provider settings from this skill. If no provider is available, report
`TTS_NOT_AVAILABLE`.

## Provider Catalog

| Provider | Typical tool | Notes |
|----------|--------------|-------|
| Google TTS | `google_tts` | High-quality voices when credentials and quota exist. |
| OpenAI TTS | `openai_tts` | Good fallback when OpenAI credentials exist. |
| ElevenLabs | `elevenlabs_tts` | Voice-rich fallback when credentials exist. |
| Local macOS say | `say_tts` | Local/free fallback; prefer default voice unless the user asked for a voice. |

Tool names are host-specific. Match by available tool capability, not by
assuming a namespace exists.

## Error Classification

| Error class | Signals | Action |
|-------------|---------|--------|
| `AUTH_UNAVAILABLE` | API key missing, unauthorized, authentication, credential, `GOOGLE_API_KEY`, `OPENAI_API_KEY`, `ELEVENLABS_API_KEY` | Try the next provider. Do not write config or persist unavailable state. |
| `RATE_LIMITED` | rate limit, quota, 429, exhausted | Try the next provider for this request. |
| `PROVIDER_UNAVAILABLE` | tool missing, provider unavailable, network unavailable, model unavailable | Try the next provider. |
| `VOICE_UNAVAILABLE` | voice rejected, invalid voice, unsupported voice | Retry once with provider default voice. |
| `GENERIC_TTS_ERROR` | other provider failure | Try the next provider; if none remains, report `TTS_NOT_AVAILABLE`. |

Never claim audio played after every provider failed.

## Voice Policy

- Respect an explicit user-requested voice when the provider supports it.
- Otherwise prefer the provider or system default voice.
- For `say_tts`, the tested TES local preference is `Felipe (Enhanced)` at
  rate `225` when accepted; if rejected, retry with the default voice.
- Do not auto-assign voices by project, task type, or speaker identity.
- Do not create `.claude/tts-config.json`, `~/.claude/tts-assignments.json`,
  or any global unavailable-provider registry.

## Speech Transformation

For `tes-tts`, transformation prepares the requested text for speech. It must
not summarize user-provided text unless the user explicitly asks for summary.

Apply these cleanup rules conservatively:

| Source pattern | Speech handling |
|----------------|-----------------|
| URLs | In non-exact mode, say a useful destination phrase such as "pagina do GitHub" for GitHub URLs, or "link" for generic URLs. Preserve raw URLs for exact/verbatim reading. |
| File paths | In non-exact mode, say a useful folder or file phrase such as "pasta tes tts". Preserve raw paths for exact/verbatim reading. |
| Long hashes/IDs | Say "hash" or `GUID` unless the user asks for exact reading. |
| Email/IP/social tokens | Say compact forms for email addresses, valid IPv4 addresses, mentions, and hashtags; preserve raw tokens for exact/verbatim reading. |
| Markdown formatting | Remove markup and preserve the words. |
| Code blocks | Remove code fences and preserve code or command text unless the user asks for a summary. |
| Long lists | Preserve items when the user asked to hear them; group only when the user asked for summary. |
| Technical terms | Preserve the term in source/cache metadata and use `language-normalization.md` for spoken rendering, such as `ADR` -> `A D R`. |

## Non-Goals From Speak

Do not import these `speak` behaviors into `tes-tts`:

- proactive announcements after plans, fixes, or summaries;
- project-specific voice assignment;
- global provider persistence;
- automatic config file writes;
- `voice-pools.json`;
- 15-30 second summary target;
- planning/issue/summary tone rewriting;
- `.DS_Store` or other local OS artifacts.
