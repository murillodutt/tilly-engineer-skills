---
tds_id: roadmap.tes_tts_spec_002_fixture_corpus_complete
tds_class: roadmap
status: proposed
consumer: maintainers, tes-tts maintainers, validation authors, and execution agents
source_of_truth: false
evidence_level: L2
---

# TES TTS SPEC 002: Fixture Corpus Complete

## Purpose

Complete the dependency-free fixture corpus before claiming multilingual
normalization behavior.

## Scope

- Add fixture coverage for `pt-BR`, `en`, `es`, `fr`, `it`, `de`, and `he`.
- Add negative fixtures for Markdown, URLs, paths, code fences, long hashes,
  secret-like values, provider unavailable, and voice unavailable cases.
- Preserve `no_summary: true` for user-provided text.

## Required Fixture Classes

| Class | Minimum coverage |
|-------|------------------|
| single language | One fixture per first-class language. |
| mixed language | Default-language text with one foreign span. |
| protected terms | ADR, SPEC, MCP, API, JSON, YAML, CLI, SDK, paths, commands. |
| redaction | Secret-like value appears before translation/TTS. |
| Markdown transform | Links, headings, lists, paths, code fences. |
| provider fallback | Provider unavailable and voice unavailable. |
| Hebrew degraded | Hebrew without niqqud or local voice support. |

## Deliverables

- Expanded `benchmarks/tes-tts/normalization-fixtures.json`.
- Schema updates only if the current schema cannot represent a required case.
- Roadmap status update naming remaining fixture gaps, if any.

## SPEC-002 Result

Status: `PASS`.

The corpus now includes dependency-free fixtures for every first-class
language: `pt-BR`, `en`, `es`, `fr`, `it`, `de`, and `he`.

Negative fixture coverage now includes Markdown, URLs, paths, code fences,
long hashes, secret-like values, provider unavailable, voice unavailable, and
Hebrew degraded posture. The schema already represented these cases, so no
schema expansion was needed.

`no_summary: true` remains mandatory for every corpus entry.

Next ready prompt:
`docs/roadmap/GOAL-PROMPT-tes-tts-SPEC-003-deterministic-instruction-normalizer.md`.

Sync status: `REMOTE_SYNC_NOT_REQUESTED`.

## Oracles

```bash
python3 scripts/tes_tts_fixture_schema_oracle.py --self-test
python3 scripts/validate_tds.py
python3 scripts/validate_doc_size.py
```

## Exit Criteria

- Every first-class language has at least one fixture.
- Every required fixture class is represented.
- No provider, network, install, download, playback, release, or sync action is
  performed.
