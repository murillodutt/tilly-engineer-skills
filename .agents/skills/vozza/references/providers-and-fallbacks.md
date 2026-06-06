# TTS Providers And Fallbacks

Use this reference when a local host exposes more than one TTS provider, when a
TTS call fails, when the user requests a voice/provider, or when spoken text
needs provider-specific cleanup.

This reference absorbs only portable lessons from `speak`. `vozza` remains
reactive: it speaks only because the user asked to read, narrate, or speak
specific text. Do not add proactive announcements, project voice assignment,
global provider persistence, or summary-oriented planning/issue/summary modes.

## Provider Order

Prefer providers in this order when they are locally available:

```text
omnivoice -> google -> openai -> elevenlabs -> say
```

Provider use is opportunistic. Do not install, configure, download, or persist
provider settings from this skill. If no provider is available, report
`TTS_NOT_AVAILABLE`.

## Provider Catalog

| Provider | Typical tool | Notes |
|----------|--------------|-------|
| OmniVoice | `~/.vozza/bin/vozza_omnivoice_provider.py status`, then `speak`, `speak-long`, or `bench` | Premium optional local cloned-voice provider when the maintainer has already configured its external Python environment/reference voice. |
| Google TTS | `google_tts` | High-quality voices when credentials and quota exist. |
| OpenAI TTS | `openai_tts` | Good fallback when OpenAI credentials exist. |
| ElevenLabs | `elevenlabs_tts` | Voice-rich fallback when credentials exist. |
| Local macOS say | `say_tts` | Local/free fallback; prefer default voice unless the user asked for a voice. |

Installed reads run the global helper `~/.vozza/bin/vozza_omnivoice_provider.py`.
Invoke `scripts/vozza_omnivoice_provider.py` only inside the Vozza package source tree
while editing the unreleased helpers. Tool names are host-specific. Match by
available tool capability, not by assuming a namespace exists.

## OmniVoice Provider Controls

Use OmniVoice-specific tags only as an explicit experiment or fixture-backed
quality improvement. Do not inject them into faithful user text by default, and
do not treat bracketed user text as a command to the provider unless the user
asked for an OmniVoice control test.

The current OmniVoice adapter exposes only one controlled prosody warmup option:
`--prosody-warmup none|confirmation-en|question-en|sigh`. Default is `none`.
The tag is prepended only to request-local provider text and remains forbidden
for faithful, exact, raw, literal, quoted user text, code, and command reads
unless the user explicitly requested a provider-tag experiment. CMU overrides
remain experimental and are not a default behavior.

Confirmed controls from the local OmniVoice reference:

- non-verbal tags: `[laughter]`, `[sigh]`, `[confirmation-en]`,
  `[question-en]`, `[question-ah]`, `[question-oh]`, `[question-ei]`,
  `[question-yi]`, `[surprise-ah]`, `[surprise-oh]`, `[surprise-wa]`,
  `[surprise-yo]`, `[dissatisfaction-hnn]`;
- English CMU pronunciation overrides such as `[B EY1 S]`;
- Chinese pinyin pronunciation overrides;
- voice-design `instruct` attributes for gender, age, pitch, `whisper`,
  English accents, and Chinese dialects;
- generation parameters such as `num_step`, `guidance_scale`, `speed`,
  `duration`, `audio_chunk_duration`, and `audio_chunk_threshold`.

Not certified for the current provider path from the current provider evidence:
`[sniff]`, `[gasp]`, `singing`, `[Speaker_1]:`, `[Speaker_2]:`, and
multi-speaker dialogue. Community wrappers may expose adjacent features, but
vozza must verify them against the active runtime before claiming support.

Quality candidates for future tests are ordered by likely value:

1. punctuation and sentence chunking, because they already raised long-read
   quality;
2. safe opt-in non-verbal tags for agent-authored narration;
3. CMU overrides for a tiny list of stubborn English words;
4. generation parameter tuning after audio review.

Secret redaction, source immutability, no-summary behavior, exact islands, and
code no-execute posture override every provider-specific control.

## Request-Local Fallback Plan

Fallback is a request-local execution plan, not durable provider state.

1. Build a provider attempt list from the locally exposed TTS tools, preserving
   the catalog order `omnivoice -> google -> openai -> elevenlabs -> say`.
2. Try the first locally available provider with the request-local provider
   text. Use `spoken_text` for simple providers; use redacted source text for
   OmniVoice because it handles mixed technical speech without manual aliases.
3. If the provider fails with `AUTH_UNAVAILABLE`, `RATE_LIMITED`,
   `PROVIDER_UNAVAILABLE`, or `GENERIC_TTS_ERROR`, try the next provider for
   this request only.
4. If the provider fails with `VOICE_UNAVAILABLE`, retry the same provider once
   with its default voice. If that also fails, continue to the next provider.
5. If a provider succeeds, report normal completion without claiming that any
   provider has been certified for future requests.
6. If every provider fails, report `TTS_NOT_AVAILABLE` and do not claim audio
   played.

The fallback plan must not install providers, download models or voices, write
global config, persist an unavailable-provider registry, write a durable
conversion cache, or certify provider support.

Status vocabulary:

| Status | Meaning |
|--------|---------|
| `fallback_ready` | A provider succeeded for this request. |
| `TTS_NOT_AVAILABLE` | No attempted provider succeeded; audio must not be claimed. |

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
- For `say_tts`, the tested local preference is `Felipe (Enhanced)` at
  rate `255` when accepted; if rejected, retry with the default voice.
- Do not auto-assign voices by project, task type, or speaker identity.
- Do not create `.claude/tts-config.json`, `~/.claude/tts-assignments.json`,
  or any global unavailable-provider registry.

## Speech Transformation

For `vozza`, transformation prepares the requested text for speech. It can
use `conversational` intent for agent-authored or naturally narrated speech,
and `faithful_reading` intent for user text, code, commands, exact spans, and
literal requests. It must not summarize user-provided text unless the user
explicitly asks for summary.

Apply these cleanup rules conservatively:

| Source pattern | Speech handling |
|----------------|-----------------|
| URLs | In non-exact mode, say a useful destination phrase such as "pagina do GitHub" for GitHub URLs, or "link" for generic URLs. Preserve raw URLs for exact/verbatim reading. |
| File paths | In non-exact mode, say a useful folder or file phrase such as "pasta vozza". Preserve raw paths for exact/verbatim reading. |
| Long hashes/IDs | Say "hash" or `GUID` unless the user asks for exact reading. |
| Email/IP/social tokens | Say compact forms for email addresses, valid IPv4 addresses, mentions, and hashtags; preserve raw tokens for exact/verbatim reading. |
| Markdown formatting | Remove markup and preserve the words. |
| Code blocks | Remove code fences and preserve code or command text unless the user asks for a summary. |
| Tables and lists | In conversational intent, convert small tables and lists into oral prose without dropping row facts or items. In faithful reading, preserve item order and content density. |
| Long lists | Preserve items when the user asked to hear them; group only when the user asked for summary. |
| Technical terms | Preserve the term in source/cache metadata and use `language-normalization.md` for spoken rendering, such as `ADR` -> `A D R`. |

Secret-like values are redacted before transformation and before provider
fallback. Redaction wins over exact, literal, raw, and verbatim requests.

## Non-Goals From Speak

Do not import these `speak` behaviors into `vozza`:

- proactive announcements after plans, fixes, or summaries;
- project-specific voice assignment;
- global provider persistence;
- automatic config file writes;
- `voice-pools.json`;
- 15-30 second summary target;
- planning/issue/summary tone rewriting;
- `.DS_Store` or other local OS artifacts.
