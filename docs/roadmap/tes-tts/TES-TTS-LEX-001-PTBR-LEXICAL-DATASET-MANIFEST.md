---
tds_id: roadmap.tes_tts_lex_001_ptbr_lexical_dataset_manifest
tds_class: roadmap
status: archived
consumer: maintainers, tes-tts maintainers, adapter authors, validation authors, and execution agents
source_of_truth: false
evidence_level: L1
---

# TES TTS LEX-001 PT-BR Lexical Dataset Manifest

## Purpose

Define the first PT-BR lexical pronunciation dataset contract for `tes-tts`.
This SPEC replaces ad hoc Markdown pronunciation evidence with structured
manifest records inspired by mature TTS/G2P systems.

## Scope

LEX-001 creates the schema and sample evidence only. It does not integrate a
runtime G2P engine, does not vendor NeMo, does not install providers, and does
not send IPA, SSML, phonemes, or lexicon data to a TTS provider.

## Required Manifest Shape

The first manifest records must be JSON or JSONL-compatible objects:

```json
{
  "id": "ptbr-lexical-000001",
  "language": "pt-BR",
  "text_graphemes": "ABACAXI",
  "pronunciation": "ˌabakaʃˈi",
  "pronunciation_system": "ipa",
  "source": "pt_br_prondict",
  "source_path": "tmp/tts-lib/NeMo/scripts/tts_dataset_files/pt_BR/pt_br_prondict-v1.0.dict",
  "license_note": "public dictionary reference; provenance to be retained",
  "usage": "evidence_only",
  "status": "reference"
}
```

Required fields:

- `id`
- `language`
- `text_graphemes`
- `pronunciation`
- `pronunciation_system`
- `source`
- `source_path`
- `license_note`
- `usage`
- `status`

## Acceptance Criteria

- A PT-BR lexical manifest schema exists.
- A small PT-BR lexical sample exists using representative entries from the
  available dictionary reference.
- A Python converter exists for transforming
  `tmp/tts-lib/NeMo/scripts/tts_dataset_files/pt_BR/pt_br_prondict-v1.0.dict`
  into JSONL/manifest records without importing NeMo.
- The sample includes ordinary words, accented words, hyphenated words, and at
  least one OOV/degraded case.
- A lexical manifest oracle validates shape, uniqueness, PT-BR scope,
  provenance fields, and `usage: evidence_only`.
- Existing `tes-tts` oracles continue to pass.
- The roadmap points to the next lexical execution prompt.

## Boundaries

- No runtime dependency import.
- No library vendoring.
- No full dictionary copy unless explicitly approved in the current cycle.
- No provider certification.
- No IPA/phoneme/SSML runtime output claim.
- No sync, release, push, tag, publish, version bump, or bundle generation.
- No proactive `speak` behavior.

## Expected Next Prompt

Ready prompt after LEX-001 should be for LEX-002 PT-BR lexical lookup oracle,
unless LEX-001 finds a provenance or schema blocker.

## Result

Status: `PASS`.

LEX-001 created a structured PT-BR lexical manifest foundation without adding
runtime dependencies or copying the full dictionary. The implemented artifacts
are:

- `benchmarks/tes-tts/ptbr-lexical-manifest.schema.json`
- `benchmarks/tes-tts/ptbr-lexical-sample.jsonl`
- `scripts/tes_tts_ptbr_prondict_to_manifest.py`
- `scripts/tes_tts_ptbr_lexical_manifest_oracle.py`

The sample preserves grapheme/pronunciation separation, provenance,
`source_line`, and `usage: evidence_only`. IPA remains evidence metadata only;
no runtime IPA, phoneme, SSML, provider-backed pronunciation claim, full
dictionary vendoring, release, sync, push, tag, or publish was performed.

Next prompt:
Prompt artifact purged from tracked source on 2026-06-02.
