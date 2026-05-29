---
tds_id: roadmap.tes_tts_lex_003_spoken_rendering_integration_boundary
tds_class: roadmap
status: archived
consumer: maintainers, tes-tts maintainers, adapter authors, validation authors, and execution agents
source_of_truth: false
evidence_level: L1
---

# TES TTS LEX-003 Spoken-Rendering Integration Boundary

## Purpose

Define and prove the boundary for attaching PT-BR lexical evidence to
request-local speech preparation without turning pronunciation evidence into
runtime speech output.

## Result

Status: `PASS`.

LEX-003 added:

- `benchmarks/tes-tts/ptbr-lexical-integration-fixtures.json`
- `scripts/tes_tts_ptbr_lexical_integration_oracle.py`
- PT-BR lexical evidence boundary notes in the `.agents`, Codex, and Claude
  `tes-tts` language-normalization references.

The oracle proves source immutability, request-local `spoken_text`, lexical
evidence as `usage: evidence_only`, secret redaction before speech, code as
text with no execution, no summary behavior, provider absence degradation, and
no IPA, phoneme, or SSML runtime output.

## Boundary

LEX-003 does not authorize provider-backed pronunciation, G2P, runtime IPA,
SSML, phoneme output, full dictionary vendoring, release, sync, push, tag,
publish, provider install, provider download, or provider certification.

Next prompt:
`docs/roadmap/GOAL-PROMPT-tes-tts-LEX-004-fixture-migration-from-markdown-shaped-tts-cases.md`.
