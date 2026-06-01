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

## SPEC-007 Boundary

The optional translation layer is a speech-preparation plan, not a source-text
mutation and not a provider support claim.

Execution order:

1. Redact secret-like values.
2. Extract protected terms, proper nouns, commands, paths, and code
   identifiers.
3. Decide target language.
4. Plan span-level translation only for spans outside the target language.
5. Keep source text unchanged and keep normalized speech text unsummarized.
6. Report `normalization_degraded` when the translation provider is absent,
   unavailable, needs review, or lacks clear language-pair support.

Because SPEC-006 deferred `Argos Translate` and did not certify any translation
provider or model package, SPEC-007 does not add first-class provider-backed
translation fixtures. Instead it adds instruction-level boundary fixtures that
prove redaction-first, protected-term-first, no-summary, and degraded-honesty
behavior before any provider is introduced.

## SPEC-007 Result

Status: `PASS`.

Instruction-level translation boundary fixtures:

1. `tts-translation-redaction-first`
2. `tts-translation-protected-terms-first`
3. `tts-translation-unclear-pair-degraded`

The oracle now creates an optional translation plan with these required
actions: `redaction_before_translation`,
`protected_terms_before_translation`, `span_level_translation_only`,
`no_summary`, and `preserve_source_text`. The plan remains
`normalization_degraded` when provider availability or language-pair support is
missing or unclear.

No provider was installed, downloaded, bundled, certified, or claimed as
supported.

Next ready prompt:
`docs/roadmap/goals/prompts/tes-tts/GOAL-PROMPT-tes-tts-SPEC-008-optional-g2p-pronunciation-provider-layer.md`.

Sync status: `REMOTE_SYNC_NOT_REQUESTED`.

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
