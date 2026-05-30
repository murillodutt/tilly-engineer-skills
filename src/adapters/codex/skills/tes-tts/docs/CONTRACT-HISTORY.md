# TES TTS Contract History

## Purpose

`tes-tts` reads user-provided text aloud through an available local
text-to-speech tool while preserving language, protecting secrets, and keeping
the workflow intentionally small.

## Why This Skill Exists

The maintainer-proven local TTS skill worked well enough across simple mirrored
project installs to promote the portable behavior into TES source. The useful
contract is not the dependency itself; it is the small read-aloud workflow,
speech cleanup, speed handling, and honest unavailable state.

## Origin Signals

| Source | Signal | Confidence |
|--------|--------|------------|
| Maintainer directive | Promote the working simple TTS skill into TES in safe steps. | high |
| Local runtime skill | Established defaults for text extraction, Markdown cleanup, voice, rate, and brief confirmation. | high |
| Current host tool contract | A local `say_tts` style tool can speak text and may accept voice and rate settings. | medium |

## Source Search Ledger

| Window | Query | Occurrences | Meaning |
|--------|-------|-------------|---------|
| 2026-05-28 | `tts`, `TTS`, `mcp-tts`, `read aloud` | local runtime skill only before migration | TES had no canonical adapter source for the behavior. |
| 2026-05-28 | canonical TES TTS skill source | none before migration | New TES skill source was required. |

## Contracts Preserved

- Read only the text the user asked to hear.
- Preserve language and meaning; do not summarize unless asked.
- Convert Markdown, URLs, file paths, and code blocks into speech-friendly
  text.
- Normalize multilingual text into the default reading language through an
  ephemeral TTS conversion cache when requested or needed.
- Preserve technical terms, proper nouns, commands, and acronyms while adapting
  pronunciation for natural speech.
- Distinguish conversational spoken rendering from faithful reading so
  agent-authored speech can become oral prose without summarizing user text.
- Keep exact handling span-scoped so one literal cue does not force unrelated
  fragile spans into raw speech.
- Oralize tables, bullets, numbered lists, quotes, and code blocks in a way
  that preserves facts, ordering, protected spans, exact islands, and
  no-execute behavior.
- Preserve mixed-language English identity for engineering workflow,
  planning, product, package, model, command, and code terms while keeping
  pronunciation hints instruction-level only.
- Use provider fallback and error classification as optional runtime guidance
  without importing proactive `speak` behavior or provider persistence.
- Use the tested local voice/rate when accepted, but degrade to the host
  default voice if needed.
- Compute percentage speed changes from the last spoken rate in the current
  conversation, falling back to `225`.
- Report `TTS_NOT_AVAILABLE` when no local TTS tool exists.
- Redact secret-like values instead of reading them aloud.

## Known Failure Modes Prevented

- Pretending audio played when no TTS tool was available.
- Reading credentials, tokens, or other secret-like content aloud.
- Summarizing user text when the request was to read it.
- Letting conversational speech become silent summary or invented intent.
- Dropping long text instead of chunking it.
- Reading mixed-language text with forced or awkward untranslated pronunciation.
- Translating technical acronyms such as ADR, SPEC, or MCP into the wrong
  semantic object.
- Turning reactive TTS into proactive announcements.
- Persisting provider state, voice assignments, or global config as a side
  effect of a read-aloud request.
- Making the MCP dependency itself part of the TES product contract.

## Relationship To Other Skills

`tes-tts` is a reactive read-aloud skill. It does not replace engineering,
installer, Cortex, Field Reports, or benchmark skills. It should not be used as
a proactive announcement channel for normal TES status updates.

## Changelog

| Date | Change | Evidence | Confidence |
|------|--------|----------|------------|
| 2026-05-28 | Promoted the simple local TTS skill into TES Codex adapter source as `tes-tts`. | Maintainer directive in this session; local runtime skill analysis. | high |
| 2026-05-28 | Added default-language normalization reference and ephemeral TTS conversion cache semantics. | Maintainer directive to analyze text, translate non-default language spans, preserve technical terms, and adapt pronunciation. | high |
| 2026-05-28 | Added provider/fallback reference from portable `speak` lessons while preserving reactive/proactive separation. | Maintainer directive and `tmp/skills/speak/SKILL.md` source review. | high |
| 2026-05-29 | Added CAP-001 deterministic spoken-rendering boundary for acronyms, paths, URLs, exact reads, and no-summary preservation. | CAP-001 feasibility study, instruction normalizer oracle fixtures, and maintainer runtime feedback. | high |
| 2026-05-29 | Hardened CAP-002 speech transformation for Markdown, code fences, hashes, GUIDs, email addresses, valid IPv4 addresses, mentions, hashtags, and exact-read preservation. | CAP-002 instruction normalizer fixtures and speech transformation hardening prompt. | high |
| 2026-05-29 | Hardened CAP-003 pronunciation hints and protected-term preservation for URL, HTTP, JSON, YAML, SQL, SPEC, TES, Tilly, Codex, Claude, Cursor, OpenAI, package/model names, commands, and code identifiers. | CAP-003 instruction normalizer fixtures and protected-term prompt. | high |
| 2026-05-29 | Hardened CAP-004 provider fallback as a request-local catalog plan with error classes, voice-default retry, no provider certification, and no durable provider state. | CAP-004 provider fallback fixtures and provider probe oracle. | high |
| 2026-05-29 | Added an enriched English protected-term pronunciation catalog for proper nouns and engineering workflow terms without claiming provider-backed pronunciation. | Maintainer feedback after live TTS test; instruction normalizer fixture `tts-pronunciation-english-protected-terms`. | high |
| 2026-05-29 | Added CAP-006 conversational spoken-rendering intent with fixture-backed distinction from faithful reading, exact islands, table/list oral prose, and stronger secret redaction. | `GOAL-SUPER-SPEC-tes-tts-conversational-rendering.md`; CAP-006 instruction normalizer fixtures. | high |
| 2026-05-29 | Hardened CAP-007 exact islands and protected spans so selective literal spans survive while paths, URLs, emails, IPs, hashes, GUIDs, mentions, hashtags, scoped packages, branch names, model names, commands, and code identifiers keep safe spoken forms. | CAP-007 instruction normalizer fixtures and exact-island oracle hardening. | high |
| 2026-05-29 | Added CAP-008 table, list, quote, and code-block oralization with ordering, no-summary, exact-island, redaction, and no-execute fixtures. | CAP-008 instruction normalizer fixtures and structure oralization oracle hardening. | high |
| 2026-05-29 | Hardened CAP-009 mixed-language and English identity handling for planning, review, CI/CD, product, package, model, and platform terms without provider-backed pronunciation claims. | CAP-009 instruction normalizer fixtures and English identity oracle hardening. | high |
| 2026-05-30 | Compacted `SKILL.md` back to a runtime-first read-aloud router, removed lab/review command sprawl from the main workflow, and made `clone:tes-tts-local-clone` the concise OmniVoice server default path. | Maintainer directive to purge obsolete layers; local profile smoke and commit `5eebf61`. | high |

## Do Not Lose

Keep this skill small. The durable product behavior is "read this requested
text aloud, safely and honestly," not a full audio subsystem or dependency
manager.
