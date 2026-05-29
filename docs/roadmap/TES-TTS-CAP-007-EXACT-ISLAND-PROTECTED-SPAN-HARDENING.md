---
tds_id: roadmap.tes_tts_cap_007_exact_island_protected_span_hardening
tds_class: roadmap
status: archived
consumer: maintainers, tes-tts maintainers, adapter authors, validation authors, and execution agents
source_of_truth: false
evidence_level: L2
---

# TES TTS CAP-007 Exact-Island And Protected-Span Hardening

## Purpose

Harden conversational spoken rendering so exact/literal handling is scoped to
the requested fragile span instead of turning the whole utterance into a raw
dump.

## Problem

CAP-006 proved the first `conversational` versus `faithful_reading` boundary,
but the instruction normalizer still treated exact cues globally. That could
preserve unrelated paths, URLs, hashes, mentions, or other fragile spans in raw
form even when only one span needed literal reading.

The same layer also needed a stronger guard for scoped packages, branch names,
model names, mentions, hashtags, emails, IP addresses, hashes, GUIDs, commands,
and code identifiers before conversational prose conversion.

## Implementation Result

Status: `PASS` for the focused CAP-007 scope.

CAP-007 added fixture-backed selective exact islands:

- `exact_terms` may scope literal preservation to the requested fragile spans;
- older global exact fixtures remain compatible when no `exact_terms` field is
  present;
- secret redaction still wins over exact/literal/raw/verbatim requests;
- scoped package names such as `@openai/agents` are protected before mention
  rendering;
- branch names, model names, package names, commands, and code identifiers keep
  written identity;
- paths, GitHub URLs, long hashes, GUIDs, emails, IPs, mentions, and hashtags
  receive safe spoken forms in non-exact conversational speech.

The behavior was documented in the local workbench and mirrored into Codex and
Claude adapter skill sources.

## Acceptance Evidence

CAP-007 introduced these required fixtures:

| Fixture | Proves |
|---------|--------|
| `tts-cap007-selective-exact-islands` | Only the explicitly requested URL remains literal while unrelated path and GitHub URL use spoken forms. |
| `tts-cap007-secret-redaction-over-selective-exact` | Redaction overrides selective exact handling. |
| `tts-cap007-protect-fragile-span-classes` | Fragile path, URL, command, code, hash, GUID, email, IP, mention, hashtag, branch, model, and package spans remain protected. |
| `tts-cap007-protect-scoped-package-before-mention` | Scoped packages are not misread as ordinary mentions. |

## Boundaries Preserved

- No sync, release, push, tag, publish, provider install, provider download,
  provider certification, global config write, durable conversion cache,
  version bump, bundle generation, IPA, SSML, lexicon, G2P, model bundle, or
  runtime dependency import was performed.
- No proactive `speak` behavior entered `tes-tts`.
- Code and command spans remain text only and are never actions.
- User text is not summarized unless the user explicitly asks for summary.

## Next Prompt

Ready prompt:
`docs/roadmap/GOAL-PROMPT-tes-tts-CAP-008-table-list-code-block-oralization.md`
