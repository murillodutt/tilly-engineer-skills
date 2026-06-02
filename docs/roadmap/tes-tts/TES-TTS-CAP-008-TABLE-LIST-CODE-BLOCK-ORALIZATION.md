---
tds_id: roadmap.tes_tts_cap_008_table_list_code_block_oralization
tds_class: roadmap
status: archived
consumer: maintainers, tes-tts maintainers, adapter authors, validation authors, and execution agents
source_of_truth: false
evidence_level: L2
---

# TES TTS CAP-008 Table, List, And Code-Block Oralization

## Purpose

Harden conversational spoken rendering for structured text so `tes-tts` can
turn tables, bullets, numbered lists, quotes, and code blocks into oral prose
without losing facts, changing order, summarizing user text, or executing code.

## Problem

CAP-006 introduced the first conversational rendering boundary and CAP-007
hardened exact islands and protected spans. CAP-008 closes the next gap:
structured content must be spoken as prose, not raw Markdown, while keeping
every row, list item, quote, exact island, redaction, and code/command span
inside the request-local `spoken_text`.

## Implementation Result

Status: `PASS` for the focused CAP-008 scope.

CAP-008 added fixture-backed structure oralization:

- wider Markdown tables become ordered header/value row facts;
- bullets and numbered lists become ordered oral prose with connectors;
- Markdown quotes become explicit quoted speech without `>` marker leakage;
- conversational code blocks are introduced as code text and never executed;
- URL exact islands still survive when punctuation is added by prose
  rendering;
- secret redaction still wins before rendering and before TTS.

The behavior was documented in the active workbench and mirrored into Codex
and Claude adapter skill sources.

## Acceptance Evidence

CAP-008 introduced these required fixtures:

| Fixture | Proves |
|---------|--------|
| `tts-cap008-table-multicolumn-ordered-facts` | Multi-column table rows become ordered spoken facts without dropping headers or values. |
| `tts-cap008-bullet-numbered-list-ordering` | Mixed numbered and bullet lists keep order through oral connectors. |
| `tts-cap008-quote-oralization` | Quote blocks become explicit quoted speech and preserve protected terms. |
| `tts-cap008-code-block-conversational-no-execute` | Code blocks are spoken as text and never executed. |
| `tts-cap008-structure-preserves-exact-and-redaction` | Exact URL islands and secret redaction survive structural oralization. |

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
Prompt artifact purged from tracked source on 2026-06-02
