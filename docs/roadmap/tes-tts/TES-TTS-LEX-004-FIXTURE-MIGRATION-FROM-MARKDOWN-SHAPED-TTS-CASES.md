---
tds_id: roadmap.tes_tts_lex_004_fixture_migration_from_markdown_shaped_tts_cases
tds_class: roadmap
status: archived
consumer: maintainers, tes-tts maintainers, adapter authors, validation authors, and execution agents
source_of_truth: false
evidence_level: L1
---

# TES TTS LEX-004 Fixture Migration From Markdown-Shaped TTS Cases

## Purpose

Move a representative slice of human Markdown-shaped pronunciation guidance
toward governed JSON fixtures without deleting still-used legacy instructions.

## Result

Status: `PASS`.

LEX-004 added:

- `benchmarks/tes-tts/pronunciation-catalog-fixtures.json`
- `scripts/tes_tts_pronunciation_catalog_oracle.py`

The migrated slice covers acronyms, a technical noun, a proper noun, URL
destination rendering, path rendering, and command preservation. The catalog
keeps `usage: evidence_only`, `runtime_output: false`, exact-read raw
preservation, and `runtime_claim: none`.

## Boundary

This unit did not delete legacy fixtures, did not vendor the full dictionary,
did not import runtime dependencies, and did not introduce IPA, phoneme, SSML,
provider-backed pronunciation, release, sync, push, tag, publish, provider
install, provider download, or provider certification.

Next prompt:
Prompt artifact purged from tracked source on 2026-06-02.
