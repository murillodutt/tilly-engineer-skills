---
tds_id: roadmap.tes_tts_normalization_architecture_spec
tds_class: roadmap
status: proposed
consumer: maintainers, tes-tts maintainers, adapter authors, and provider reviewers
source_of_truth: false
evidence_level: L2
---

# TES TTS Normalization Architecture SPEC

This SPEC expands ADR 0004 into the architecture for optional language
normalization and pronunciation enrichment in `tes-tts`.

It is a proposal. It does not certify providers, authorize sync, or permit
dependency installation.

## Goal

Improve speech preparation for user-requested read-aloud text while preserving
the reactive, local, and dependency-light TES boundary.

## Architecture

The target speech-preparation pipeline is:

```text
input text
-> cleanup and secret redaction
-> paragraph/sentence span segmentation
-> protected-term extraction
-> language detection
-> default-language translation for non-default spans
-> locale-aware text normalization
-> pronunciation hints
-> TTS provider call
```

Each stage is optional except cleanup, redaction, and honest fallback. Missing
providers degrade enrichment instead of blocking basic read-aloud behavior.

## Ephemeral Conversion Cache

The cache is internal to one read-aloud request:

```text
tts_conversion_cache:
- source_span: original sentence or paragraph
  detected_language: inferred source language
  target_language: default reading language
  normalized_text: speech-ready text
  preserved_terms: proper nouns, acronyms, commands, paths, code identifiers
  pronunciation_hints: rendering hints for awkward TTS terms
  redactions: secret-like content removed from speech
  provider_notes: optional provider used, if any
```

The cache is not written to disk unless the user explicitly asks for an
artifact.

## Agent Default Language

`tes-tts` may use the default language of the active coding-agent adapter as
a default-language preference only when that adapter declares it explicitly.
An explicit user language request has higher priority than the adapter
default. The skill must not infer this value from the assistant name, host
locale, prior chat history, or repository text.

When no explicit adapter declaration exists, the adapter default is `unknown`
and the selector proceeds to the request language and dominant text language.

## First-Class Languages

| Language | Target code | Architectural note |
|----------|-------------|--------------------|
| Brazilian Portuguese | `pt-BR` | Must not collapse Brazilian pronunciation into generic Portuguese without review. |
| English | `en` | Variant should follow the selected voice or user request. |
| Spanish | `es` | Regional claims stay out of default behavior. |
| French | `fr` | Acronym pronunciation differs from English and needs hints. |
| Italian | `it` | Provider support must be verified before certification. |
| German | `de` | Compound words and acronyms need conservative handling. |
| Hebrew | `he` | Unvowelled Hebrew, niqqud absence, and voice support are explicit quality risks. |

## Provider Layers

| Layer | Candidates | Boundary |
|-------|------------|----------|
| Language detection | Lingua, fastText `lid.176`, CLD3 | Optional; must be locally probed. |
| Translation | Argos Translate | Optional; language packages are never auto-downloaded. |
| Locale normalization | ICU / CLDR, Babel | Optional helper layer, not full TTS normalization. |
| TTS text normalization | NVIDIA NeMo text processing | Reference or advanced optional provider. |
| Pronunciation / G2P / IPA | eSpeak NG, phonemizer, gruut, Epitran | Optional; exact language support must be verified. |
| Hebrew enrichment | eSpeak NG `he`, Phonikud candidate | Research/provider candidate with degraded-state handling. |
| Unicode cleanup | ftfy | Optional lightweight cleanup candidate. |

Provider evaluation must include license, offline posture, privacy, model
size, maintenance health, determinism, language coverage, G2P/IPA support,
SSML/lexicon support, and unsupported-language behavior.

## Protected Terms

Preserve before translation:

- TES terms: TES, Tilly, Codex, Claude, Cursor, Cortex, Field Reports.
- Technical acronyms: ADR, SPEC, MCP, API, SDK, CLI, URL, HTTP, JSON, YAML,
  SQL, TTS, ASR.
- Code and shell tokens: commands, flags, package names, filenames, paths,
  branches, versions, model names, identifiers.
- Proper nouns: people, products, repositories, companies, standards.

Protected terms are extracted before language detection and translation so
acronyms, commands, paths, code identifiers, and names do not pollute language
classification or become translation targets. Protected terms may receive
pronunciation hints. They must not be translated into different semantic
objects.

## Provider States

| State | Meaning |
|-------|---------|
| `provider_available` | Local provider exists and needed language support was verified. |
| `provider_not_available` | No compatible provider was found; use instruction-only normalization. |
| `provider_needs_review` | Provider exists but language support, license, model, or behavior is unclear. |
| `normalization_degraded` | Basic TTS can proceed, but enrichment is partial. |
| `tts_not_available` | No local playback tool exists. |

## Non-Goals

- No proactive announcements.
- No automatic config writes.
- No global provider registry.
- No bundled models or binaries.
- No auto-downloads.
- No durable storage of conversion caches.
- No certified language-quality claim without execution fixtures.
