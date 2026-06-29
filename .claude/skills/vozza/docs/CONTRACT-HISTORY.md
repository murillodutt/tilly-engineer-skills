# Vozza Contract History

## Purpose

`vozza` reads user-provided text aloud through an available local text-to-speech tool while preserving language, protecting secrets, and keeping the workflow intentionally small.

## Why This Skill Exists

The maintainer-proven local TTS skill worked well enough across simple mirrored project installs to promote the portable behavior into a standalone product. The useful contract is not the dependency itself; it is the small read-aloud workflow, speech cleanup, speed handling, and honest unavailable state.

## Lineage

`vozza` originates from a maintainer-internal read-aloud skill that was extracted from a prior internal read-aloud line into this standalone `vozza` product. The product identity, contract id, command, script names, and runtime path were rebranded during extraction; the durable read-aloud behavior was preserved. Historic dated rows below describe that single behavioral lineage.

## Origin Signals

| Source | Signal | Confidence |
|--------|--------|------------|
| Maintainer directive | Promote the working simple TTS skill into a standalone product in safe steps. | high |
| Local runtime skill | Established defaults for text extraction, Markdown cleanup, voice, rate, and brief confirmation. | high |
| Current host tool contract | A local `say_tts` style tool can speak text and may accept voice and rate settings. | medium |

## Source Search Ledger

| Window | Query | Occurrences | Meaning |
|--------|-------|-------------|---------|
| 2026-06-29 | Documented universal Contract History version semantics so skill contract versions, TES package versions, and `tver` metadata are not conflated. | `docs/dist/0.3.229/tilly-engineer-skills-0.3.229.zip`; `scripts/public_bundle_oracle.py` | high |
| 2026-05-28 | `tts`, `TTS`, `mcp-tts`, `read aloud` | local runtime skill only before migration | No canonical standalone source existed for the behavior. |
| 2026-05-28 | canonical read-aloud skill source | none before migration | A new canonical skill source was required. |

## Contracts Preserved

- Read only the text the user asked to hear.
- Preserve language and meaning; do not summarize unless asked.
- Convert Markdown, URLs, file paths, and code blocks into speech-friendly text.
- Normalize multilingual text into the default reading language through an ephemeral TTS conversion cache when requested or needed.
- Preserve technical terms, proper nouns, commands, and acronyms while adapting pronunciation for natural speech.
- Distinguish conversational spoken rendering from faithful reading so agent-authored speech can become oral prose without summarizing user text.
- Keep exact handling span-scoped so one literal cue does not force unrelated fragile spans into raw speech.
- Oralize tables, bullets, numbered lists, quotes, and code blocks in a way that preserves facts, ordering, protected spans, exact islands, and no-execute behavior.
- Preserve mixed-language English identity for engineering workflow, planning, product, package, model, command, and code terms while keeping pronunciation hints instruction-level only.
- Use provider fallback and error classification as optional runtime guidance without importing proactive `speak` behavior or provider persistence.
- Use the tested local voice/rate when accepted, but degrade to the host default voice if needed.
- Compute percentage speed changes from the last spoken rate in the current conversation, falling back to `225`.
- Report `TTS_NOT_AVAILABLE` when no local TTS tool exists.
- Redact secret-like values instead of reading them aloud.

## Known Failure Modes Prevented

- Pretending audio played when no TTS tool was available.
- Reading credentials, tokens, or other secret-like content aloud.
- Summarizing user text when the request was to read it.
- Letting conversational speech become silent summary or invented intent.
- Dropping long text instead of chunking it.
- Reading mixed-language text with forced or awkward untranslated pronunciation.
- Translating technical acronyms such as ADR, SPEC, or MCP into the wrong semantic object.
- Turning reactive TTS into proactive announcements.
- Persisting provider state, voice assignments, or global config as a side effect of a read-aloud request.
- Making the MCP dependency itself part of the product contract.

## Relationship To Other Skills

`vozza` is a reactive read-aloud skill. It does not replace engineering, installer, or benchmark skills. It should not be used as a proactive announcement channel for normal status updates.

## Changelog

`Version` records a skill operational contract version only when the skill declares one, followed by the containing TES package version when known. If no operational contract stamp exists, the TES package version is the shipped identity. `tver: 0.1.0` in roadmap, Super SPEC, ledger, or TDS frontmatter is document-template metadata, not a skill runtime or harness version. Patch-level changes can remain inside the same skill contract boundary; in that case the TES package version carries release identity until a future change alters the skill contract boundary itself.

| Date | Change | Evidence | Confidence |
|------|--------|----------|------------|
| 2026-05-28 | Promoted the simple local TTS skill into standalone source as the canonical read-aloud skill. | Maintainer directive in this session; local runtime skill analysis. | high |
| 2026-05-28 | Added default-language normalization reference and ephemeral TTS conversion cache semantics. | Maintainer directive to analyze text, translate non-default language spans, preserve technical terms, and adapt pronunciation. | high |
| 2026-05-28 | Added provider/fallback reference from portable `speak` lessons while preserving reactive/proactive separation. | Maintainer directive and `tmp/skills/speak/SKILL.md` source review. | high |
| 2026-05-29 | Added CAP-001 deterministic spoken-rendering boundary for acronyms, paths, URLs, exact reads, and no-summary preservation. | CAP-001 feasibility study, instruction normalizer oracle fixtures, and maintainer runtime feedback. | high |
| 2026-05-29 | Hardened CAP-002 speech transformation for Markdown, code fences, hashes, GUIDs, email addresses, valid IPv4 addresses, mentions, hashtags, and exact-read preservation. | CAP-002 instruction normalizer fixtures and speech transformation hardening prompt. | high |
| 2026-05-29 | Hardened CAP-003 pronunciation hints and protected-term preservation for URL, HTTP, JSON, YAML, SQL, SPEC, product, command, and code identifiers. | CAP-003 instruction normalizer fixtures and protected-term prompt. | high |
| 2026-05-29 | Hardened CAP-004 provider fallback as a request-local catalog plan with error classes, voice-default retry, no provider certification, and no durable provider state. | CAP-004 provider fallback fixtures and provider probe oracle. | high |
| 2026-05-29 | Added an enriched English protected-term pronunciation catalog for proper nouns and engineering workflow terms without claiming provider-backed pronunciation. | Maintainer feedback after live TTS test; instruction normalizer fixture `tts-pronunciation-english-protected-terms`. | high |
| 2026-05-29 | Added CAP-006 conversational spoken-rendering intent with fixture-backed distinction from faithful reading, exact islands, table/list oral prose, and stronger secret redaction. | Conversational-rendering Super SPEC; CAP-006 instruction normalizer fixtures. | high |
| 2026-05-29 | Hardened CAP-007 exact islands and protected spans so selective literal spans survive while paths, URLs, emails, IPs, hashes, GUIDs, mentions, hashtags, scoped packages, branch names, model names, commands, and code identifiers keep safe spoken forms. | CAP-007 instruction normalizer fixtures and exact-island oracle hardening. | high |
| 2026-05-29 | Added CAP-008 table, list, quote, and code-block oralization with ordering, no-summary, exact-island, redaction, and no-execute fixtures. | CAP-008 instruction normalizer fixtures and structure oralization oracle hardening. | high |
| 2026-05-29 | Hardened CAP-009 mixed-language and English identity handling for planning, review, CI/CD, product, package, model, and platform terms without provider-backed pronunciation claims. | CAP-009 instruction normalizer fixtures and English identity oracle hardening. | high |
| 2026-05-30 | Compacted `SKILL.md` back to a runtime-first read-aloud router, removed lab/review command sprawl from the main workflow, and made `vozza-local-clone` the concise OmniVoice clone identity. | Maintainer directive to purge obsolete layers; local profile smoke and commit `5eebf61`. | high |
| 2026-05-30 | Removed obsolete OmniVoice lab execution copies from tracked skill source and kept direct/resident execution as the only active provider path. | Maintainer decision after human-rated long-read recipe `20260530-190552-healthy-reference-read`; cleanup certified by provider oracle and runtime gates. | high |
| 2026-05-30 | Protected the direct OmniVoice voice prompt cache as local sensitive runtime state with private permissions and documented that it is not a durable text conversion cache. | Maintainer directive after confirming direct execution uses the provider-cache `voice-prompts/*.pt` cache hits. | high |
| 2026-05-30 | Relocated the local OmniVoice runtime out of lab `tmp/**` into the global runtime tree and kept it gitignored. | Maintainer directive that OmniVoice is no longer a lab install and must not exist in both old and new locations. | high |
| 2026-05-30 | Added the `vozza-local-clone` voice preset as the default resolver for reference audio/text and used `warm-cache` to prebuild the voice prompt. | Maintainer directive to avoid recloning/reprocessing the voice on every first read after cache cleanup. | high |
| 2026-05-31 | Superseded the project-local OmniVoice runtime with the user-level runtime `~/.vozza/runtime/omnivoice`; project `.vozza/**` is now lightweight state only and old project runtime is migration-report legacy. | GRT-001 commit `0c77401`; provider status reports `global_runtime`, `legacy_project_runtime`, `active_runtime`, profile, reference WAV, and cache status. | high |
| 2026-06-03 | Extracted the read-aloud skill from a prior internal read-aloud line into the standalone `vozza` product: rebranded contract `vozza@0.1.22`, command `/vozza`, scripts `scripts/vozza_*.py`, canonical runtime `~/.vozza/runtime/omnivoice` (older runtimes moved manually, no automatic migration), and product version reset to `0.1.0`. | Standalone extraction directive; single-source skill at `skills/vozza/`. | high |
| 2026-06-04 | Promoted the local package installer as the single adopter install path for the `vozza` skill, helper scripts, compiled Vozza Player binary, and approved processed voice prompt cache `audio-modelo-clone-mono24k.pt`; the player source project and `audio-modelo-clone-mono24k.wav` are not shipped to adopters. | Owner decision in package-install cycle; installer oracle covers binary install, cache permissions, and WAV rejection. | high |
| 2026-06-04 | Reclassified OmniVoice as the current Vozza Provider instead of the Vozza project layer, introduced the generic provider facade and canonical provider runtime path `~/.vozza/runtime/providers/omnivoice`, and kept `~/.vozza/runtime/omnivoice` as legacy fallback. | Provider architecture migration loop; installer oracle, provider oracle, and full oracle suite. | high |
| 2026-06-06 | Hardened the local installer to reconcile helpers (sweep stale `vozza_*.py` ghosts), gate `--player-version` against package release identity, declare the protected legacy provider runtime in the manifest, and emit machine JSON on stdout with status on stderr; introduced `vozza_runtime_paths.py` as the single `~/.vozza` layout source. | Installer drift audit and fixes; installer oracle and full oracle suite. | high |
| 2026-06-06 | Centralized adopter execution on the installed global helpers. Corrected installed `vozza` helper invocation to `.vozza/bin/**`: the `SKILL.md` Default Path now runs `~/.vozza/bin/vozza_omnivoice_provider.py` (`probe`/`speak`/`speak-long`) and `~/.vozza/bin/vozza_runtime.py`, with `scripts/**` kept only as a package-source-tree exception, and reactivated the dormant adapter-skill invocation gate. | Owner directive to centralize execution under `~/.vozza/**`; provider oracle invocation contract and full oracle suite. | high |

## Do Not Lose

Keep this skill small. The durable product behavior is "read this requested text aloud, safely and honestly," not a full audio subsystem or dependency manager.
