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
| 2026-05-28 | Promoted the simple local TTS skill into TES Claude adapter source as `tes-tts`. | Maintainer directive in this session; local runtime skill analysis. | high |
| 2026-05-28 | Added default-language normalization reference and ephemeral TTS conversion cache semantics. | Maintainer directive to analyze text, translate non-default language spans, preserve technical terms, and adapt pronunciation. | high |
| 2026-05-28 | Added provider/fallback reference from portable `speak` lessons while preserving reactive/proactive separation. | Maintainer directive and `tmp/skills/speak/SKILL.md` source review. | high |

## Do Not Lose

Keep this skill small. The durable product behavior is "read this requested
text aloud, safely and honestly," not a full audio subsystem or dependency
manager.
