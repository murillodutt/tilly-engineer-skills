---
tds_id: roadmap.tes_tts_lex_002_ptbr_lexical_lookup_oracle
tds_class: roadmap
status: archived
consumer: maintainers, tes-tts maintainers, adapter authors, validation authors, and execution agents
source_of_truth: false
evidence_level: L1
---

# TES TTS LEX-002 PT-BR Lexical Lookup Oracle

## Purpose

Prove a dependency-free PT-BR lexical lookup over the governed sample manifest
created by LEX-001. This unit validates lookup behavior only; it does not
integrate lexical evidence into runtime speech rendering.

## Result

Status: `PASS`.

LEX-002 added:

- `benchmarks/tes-tts/ptbr-lexical-lookup-fixtures.json`
- `scripts/tes_tts_ptbr_lexical_lookup_oracle.py`

The oracle validates exact grapheme lookup, casefold lookup, accented and
hyphenated graphemes, governed degraded OOV fixtures, and unknown OOV fallback.
All lookup results keep `usage: evidence_only`, preserve the source query, and
report `runtime_output: false`.

## Boundary

Lookup output remains pronunciation evidence metadata. This cycle did not send
IPA, phonemes, SSML, or lexicon data to TTS; did not add a runtime dependency;
did not vendor the full dictionary; and did not perform release, sync, push,
tag, publish, provider install, provider download, or provider certification.

Next prompt:
Prompt artifact purged from tracked source on 2026-06-02.
