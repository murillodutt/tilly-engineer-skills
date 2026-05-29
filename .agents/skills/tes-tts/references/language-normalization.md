# TTS Language Normalization

Use this reference when the text to read is multilingual, when the user asks
for a standard/default reading language, or when technical terms need better
spoken rendering.

## Goal

Create an ephemeral TTS conversion cache: a speech-ready version of the user's
requested text. Do not edit the source text. Do not write the cache to disk
unless the user explicitly asks for an artifact.

## Default Language

Choose the default reading language in this order:

1. The language explicitly requested by the user.
2. The default language declared by the active coding agent adapter, such as
   Claude, Codex, or Cursor, when that declaration exists.
3. If the active adapter is Cursor and no Cursor language rule is declared,
   use the Codex default first, then the Claude default.
4. The language of the current user request.
5. The dominant language of the provided text.
6. If still unclear, preserve the original language and do not guess.

Use the adapter default only when the active adapter declares its default
language explicitly. Do not infer it from the assistant name, host locale,
prior chat history, or repository text. The current recognized declarations
are:

| Adapter | Declaration source | Normalization |
|---------|--------------------|---------------|
| Codex | `~/.codex/config.toml` -> `[desktop].localeOverride` | Use the locale value directly, for example `pt-BR`. |
| Claude Code | `~/.claude/settings.json` -> `language` | Map `Portuguese` to the configured TES Portuguese target, currently `pt-BR`. |
| Cursor | Cursor User Rules or project rules when explicitly declared | If absent, use Codex default first, then Claude default. |

If the adapter default and fallback defaults are all unknown, continue with
the current request language.

Selector fixture candidates:

| Case | Inputs | Expected target |
|------|--------|-----------------|
| DLS-001 | User requests `en`; adapter declares `pt-BR`; request is `pt-BR`; text is `pt-BR`. | `en` |
| DLS-002 | No user language; adapter declares `pt-BR`; request is `en`; text is `en`. | `pt-BR` |
| DLS-003 | No user language; adapter default is `unknown`; request is `pt-BR`; text is `en`. | `pt-BR` |
| DLS-004 | No user language; adapter default is `unknown`; request language is unclear; text is mostly `de`. | `de` |
| DLS-005 | No user language; adapter default is `unknown`; request language is unclear; text language is unclear. | preserve original |
| DLS-006 | Cursor has no declared default; Codex default is `pt-BR`; Claude default is `pt-BR`; request/text are `en`. | `pt-BR` |

These cases define selector expectations for future fixtures. They do not
certify translation quality, provider behavior, or spoken output.

## Conversion Cache

Prepare a compact internal cache before calling TTS:

```text
tts_conversion_cache:
- source_span: original sentence or paragraph
  detected_language: language inferred from the span
  target_language: default reading language
  normalized_text: source-faithful cleaned text
  spoken_text: request-local text that will be spoken
  preserved_terms: proper nouns, product names, acronyms, commands, paths
  pronunciation_hints: spoken rendering changes, if any
  redactions: secret-like content removed from speech
```

The cache is for speech only. It is not a translation deliverable unless the
user asks to see it.

`spoken_text` is derived from `normalized_text`. Do not mutate source text to
make speech sound better.

## Normalization Rules

1. Segment text by paragraph first, then by sentence when a paragraph mixes
   languages.
2. Translate spans that are not in the default language into the default
   language.
3. Preserve proper nouns, project names, product names, file paths, commands,
   flags, code identifiers, acronyms, and accepted technical terms.
4. Preserve meaning over literal wording. Prefer natural spoken language over
   word-for-word translation.
5. Keep quoted user text faithful. Translate it for speech only when the user
   asked for standard-language reading.
6. Remove code fences for speech while preserving code or command text unless
   the user explicitly asks for a summary.
7. Redact secret-like values before translation and before speech.

## Technical Term Handling

Do not translate terms such as:

- ADR, SPEC, MCP, API, SDK, CLI, URL, HTTP, JSON, YAML, SQL
- TES, Tilly, Codex, Claude, Cursor, OpenAI
- package names, command names, filenames, branch names, model names

Adapt pronunciation without changing the visible term's meaning. For acronyms,
prefer a pronunciation that sounds natural in the default language:

| Term | Spoken rendering guidance |
|------|---------------------------|
| ADR | Read as `A D R` unless exact reading is requested. |
| SPEC | Read as "spec" when used as a technical noun. |
| MCP | Read as `M C P` unless exact reading is requested. |
| API | Read as `A P I` unless exact reading is requested. |
| SDK | Read as `S D K` unless exact reading is requested. |
| CLI | Read as `C L I` unless exact reading is requested. |
| JSON | Use the common local pronunciation, not a literal translation. |
| YAML | Use the common local pronunciation, not a literal translation. |
| SQL | Use the common local pronunciation, not a literal translation. |
| URLs | Use a useful destination phrase in non-exact mode, such as "pagina do GitHub" for GitHub URLs; preserve raw URLs for exact reading. |
| Paths | Use a useful folder/file phrase in non-exact mode, such as "pasta tes tts"; preserve raw paths for exact reading. |
| Long hashes | Say "hash" in non-exact mode; preserve the raw value for exact reading. |
| GUIDs | Say `GUID` in non-exact mode; preserve the raw value for exact reading. |
| Email addresses | Say a compact address phrase in non-exact mode; preserve the raw address for exact reading. |
| IPv4 addresses | Say valid dotted IPv4 addresses with "ponto" separators in non-exact mode; leave invalid dotted tokens unchanged. |
| Mentions and hashtags | Say "mencao ..." and "hashtag ..." in non-exact mode; preserve raw tokens for exact reading. |
| Commands | Preserve command text exactly; never execute it. |
| Proper nouns | Preserve written identity; add spacing only if the TTS engine would distort it. |

Pronunciation hints are cache metadata. They must not alter the visible source
text, translate a protected term into a different concept, or claim IPA, SSML,
phoneme, provider-backed, or Hebrew enrichment support before a later SPEC
certifies it. Hebrew pronunciation remains degraded unless niqqud or local
voice support is explicitly certified later.

When unsure, preserve the written term and add spacing only if the TTS engine
would otherwise pronounce it poorly.

## Output To TTS

Send only `spoken_text` to the TTS tool. Keep chat confirmation short. Do not
print the cache unless the user asks for debug detail.
