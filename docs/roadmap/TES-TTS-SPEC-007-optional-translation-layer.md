---
tds_id: roadmap.tes_tts_spec_007_optional_translation_layer
tds_class: roadmap
status: proposed
consumer: maintainers, tes-tts maintainers, provider reviewers, and validation authors
source_of_truth: false
evidence_level: L2
---

# TES TTS SPEC 007: Optional Translation Layer

## Purpose

Define the boundary for translating non-default-language spans into the default
reading language when a local optional translation provider is available.

## Scope

- Translation is speech preparation only.
- Source text remains unchanged.
- Protected terms and proper nouns must not be semantically translated.
- Translation providers must already be locally available and pass no-write
  probe checks.
- Provider absence keeps basic TTS available as `normalization_degraded`.

## Required Safeguards

| Safeguard | Requirement |
|-----------|-------------|
| redaction first | Secret-like values are removed before translation. |
| protected terms first | Terms are extracted before language detection/translation. |
| span-level translation | Translate only spans outside target language. |
| no summary | Translation must not shorten or summarize user text. |
| degraded honesty | Missing or unclear provider support reports degraded state. |

## Deliverables

- Translation fixtures for first-class languages where provider evidence
  exists.
- Negative fixtures for protected terms and secrets.
- Provider-specific behavior docs only after local probe evidence.

## Oracles

```bash
python3 scripts/tes_tts_instruction_normalizer_oracle.py --self-test
python3 scripts/tes_tts_provider_probe_oracle.py --self-test
python3 scripts/tes_tts_fixture_schema_oracle.py --self-test
```

## Exit Criteria

- Translation layer is optional and locally evidenced.
- No unsupported language receives a certified translation claim.
- No provider install, model download, durable cache, release, or sync occurs.
