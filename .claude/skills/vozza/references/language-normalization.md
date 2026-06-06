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
| Claude Code | `~/.claude/settings.json` -> `language` | Map `Portuguese` to the configured Portuguese target, currently `pt-BR`. |
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
  rendering_intent: conversational or faithful_reading
  preserved_terms: proper nouns, product names, acronyms, commands, paths
  exact_terms: request-scoped fragile spans to preserve literally, if any
  pronunciation_hints: spoken rendering changes, if any
  redactions: secret-like content removed from speech
```

The cache is for speech only. It is not a translation deliverable unless the
user asks to see it.

`spoken_text` is derived from `normalized_text`. Do not mutate source text to
make speech sound better.

## PT-BR Lexical Evidence Boundary

When PT-BR lexical lookup is available, attach its result only as
request-local evidence metadata during speech preparation:

```text
source_text
-> redacted_source_for_speech
-> normalized_text
-> lexical_evidence
-> spoken_text
```

Rules:

1. Keep `source_text` immutable.
2. Keep `spoken_text` request-local and send only `spoken_text` to TTS.
3. Keep `lexical_evidence.usage` as `evidence_only`.
4. Do not copy IPA, phonemes, SSML, or lexicon text into `spoken_text`.
5. Do not claim provider-backed pronunciation, G2P, or runtime IPA output.
6. Redact secrets before lexical lookup and before TTS.
7. Preserve exact islands, commands, code, paths, URLs, hashes, and protected
   terms according to the selected rendering intent.
8. Treat OOV or provider absence as degraded evidence, not a hard failure for
   basic read-aloud.

The PT-BR lexical data can help future pronunciation decisions, but this skill
does not speak IPA or phoneme strings. A later approved runtime surface must
certify any provider-specific pronunciation use before it is sent to TTS.

## Rendering Intent

Choose the spoken rendering intent before final cleanup:

| Intent | Use | Boundary |
|--------|-----|----------|
| `conversational` | Agent-authored speech or explicit natural narration. | Speak in PT-BR oral prose by default, preserving facts and protected terms. |
| `faithful_reading` | User text, exact reads, code, commands, or literal/verbatim/raw requests. | Preserve order, fragile spans, and content density while removing only speech-hostile markup. |

Conversational rendering may convert headings, bullets, and small tables into
short oral prose. It may add small connectors such as "Primeiro", "Depois",
and "Por fim". It must not summarize, remove facts, infer missing owners,
translate protected terms, or turn code into an action.

Exact islands remain exact inside conversational speech only for the specific
path, URL, command, code identifier, hash, or quoted term the user asked to
hear literally. One exact cue must not force every fragile span in the same
utterance to stay raw. Secret redaction still wins over exact reading.

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
8. Render headings, bullets, and small tables as oral prose only in
   `conversational` intent.
9. Preserve exact islands and code/command text in `faithful_reading` intent;
   in `conversational` intent, preserve exact islands only when explicitly
   scoped by the user.

## Technical Term Handling

Do not translate terms such as:

- ADR, SPEC, MCP, API, SDK, CLI, URL, HTTP, JSON, YAML, SQL
- vozza, Codex, Claude, Cursor, OpenAI
- English workflow terms such as GitHub, Markdown, provider, fallback, cache,
  prompt, workflow, pipeline, branch, commit, release, sync, tag, push, pull
  request, merge, runtime, fixture, oracle, adapter, workbench, rollback,
  checkpoint, canary, debug, build, test, deploy, review, diff, patch, issue,
  milestone, sprint, backlog, standup, roadmap, release candidate, hotfix,
  merge conflict, rebase, cherry-pick, fork, upstream, origin, main,
  workspace, worktree, sandbox, hook, lint, formatter, CI, and CD
- product and platform terms such as GitHub Actions, Docker, Kubernetes,
  Node.js, TypeScript, Playwright, MCP server, LLM, AI, and TTS
- package names, command names, filenames, branch names, model names

Adapt pronunciation without changing the visible term's meaning. English
proper nouns and workflow terms should keep English pronunciation intent even
when the default/system language is `pt-BR`, `es`, `fr`, `it`, `de`, or `he`.
If the local TTS provider cannot honor per-span language or voice hints, keep
the term written and mark the pronunciation as degraded rather than translating
or approximating it in the system language.

For acronyms, prefer a pronunciation that sounds natural in the default
language:

| Term | Spoken rendering guidance |
|------|---------------------------|
| ADR | Read as `A D R` unless exact reading is requested. |
| SPEC | Read as "spec" when used as a technical noun. |
| MCP | Read as `M C P` unless exact reading is requested. |
| API | Read as `A P I` unless exact reading is requested. |
| SDK | Read as `S D K` unless exact reading is requested. |
| CLI | Read as `C L I` unless exact reading is requested. |
| URL | Read as `U R L` unless exact reading is requested. |
| HTTP | Read as `H T T P` unless exact reading is requested. |
| JSON | Use the common local pronunciation, not a literal translation. |
| YAML | Use the common local pronunciation, not a literal translation. |
| SQL | Use the common local pronunciation, not a literal translation. |
| vozza | Preserve as a proper noun; do not translate into generic words. |
| Codex, Claude, Cursor, OpenAI, ChatGPT, GitHub, ElevenLabs | Preserve as proper nouns; keep English pronunciation intent. |
| Markdown, provider, fallback, cache, prompt, workflow, pipeline | Preserve as English workflow terms; keep English pronunciation intent. |
| branch, commit, release, sync, tag, push, pull request, merge | Preserve as English version-control/release terms; keep English pronunciation intent. |
| runtime, fixture, oracle, adapter, workbench, rollback, checkpoint, canary, debug, build, test, deploy | Preserve as English engineering terms; keep English pronunciation intent. |
| review, diff, patch, issue, milestone, sprint, backlog, standup, roadmap, release candidate, hotfix | Preserve as English planning/review terms; keep English pronunciation intent. |
| merge conflict, rebase, cherry-pick, fork, upstream, origin, main, workspace, worktree, sandbox, hook, lint, formatter | Preserve as English engineering/session terms; keep English pronunciation intent. |
| CI, CD, LLM, AI, TTS, PR | Read as spaced letters unless exact reading is requested. |
| GitHub Actions, Docker, Kubernetes, Node.js, TypeScript, Playwright, MCP server | Preserve as product/platform terms; keep English pronunciation intent. |
| URLs | Use a useful destination phrase in non-exact mode, such as "pagina do GitHub" for GitHub URLs; preserve raw URLs for exact reading. |
| Paths | Use a useful folder/file phrase in non-exact mode, such as "pasta vozza"; preserve raw paths for exact reading. |
| Long hashes | Say "hash" in non-exact mode; preserve the raw value for exact reading. |
| GUIDs | Say `GUID` in non-exact mode; preserve the raw value for exact reading. |
| Email addresses | Say a compact address phrase in non-exact mode; preserve the raw address for exact reading. |
| IPv4 addresses | Say valid dotted IPv4 addresses with "ponto" separators in non-exact mode; leave invalid dotted tokens unchanged. |
| Mentions and hashtags | Say "mencao ..." and "hashtag ..." in non-exact mode; preserve raw tokens for exact reading. |
| Commands | Preserve command text exactly; never execute it. |
| Code identifiers | Preserve exact spelling, including underscores, dots, and casing. |
| Package and model names | Preserve written identity, including scopes, hyphens, and version-like tokens. |
| Scoped packages | Preserve tokens such as `@openai/agents` before mention rendering. |
| Branch names | Preserve written identity such as `feature/cap-007`; do not translate it. |
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
