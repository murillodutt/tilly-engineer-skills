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
3. The language of the current user request.
4. The dominant language of the provided text.
5. If still unclear, preserve the original language and do not guess.

Use the adapter default only when the active adapter declares its default
language explicitly. Do not infer it from the assistant name, host locale,
prior chat history, or repository text. If the adapter default is not declared,
treat it as `unknown` and continue with the current request language.

## Conversion Cache

Prepare a compact internal cache before calling TTS:

```text
tts_conversion_cache:
- source_span: original sentence or paragraph
  detected_language: language inferred from the span
  target_language: default reading language
  normalized_text: text that will be spoken
  preserved_terms: proper nouns, product names, acronyms, commands, paths
  pronunciation_hints: spoken rendering changes, if any
  redactions: secret-like content removed from speech
```

The cache is for speech only. It is not a translation deliverable unless the
user asks to see it.

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
6. Keep code blocks summarized unless the user explicitly asks to read code
   verbatim.
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
| ADR | Read as separate letters unless the user has a project pronunciation. |
| SPEC | Read as "spec" when used as a technical noun. |
| MCP | Read as separate letters. |
| API | Read as separate letters. |
| JSON | Use the common local pronunciation, not a literal translation. |
| YAML | Use the common local pronunciation, not a literal translation. |

When unsure, preserve the written term and add spacing only if the TTS engine
would otherwise pronounce it poorly.

## Output To TTS

Send only the normalized speech text to the TTS tool. Keep chat confirmation
short. Do not print the cache unless the user asks for debug detail.
