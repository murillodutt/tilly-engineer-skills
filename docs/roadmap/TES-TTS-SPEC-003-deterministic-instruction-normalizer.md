---
tds_id: roadmap.tes_tts_spec_003_deterministic_instruction_normalizer
tds_class: roadmap
status: proposed
consumer: maintainers, tes-tts maintainers, validation authors, and adapter authors
source_of_truth: false
evidence_level: L2
---

# TES TTS SPEC 003: Deterministic Instruction Normalizer

## Purpose

Make the instruction-level speech preparation deterministic enough to test
without external providers.

## Scope

- Build or harden pure local logic for selector, cache shape, protected terms,
  redaction, Markdown cleanup, and chunking.
- Do not translate through external services.
- Do not summarize user text unless the user explicitly requests summary.
- Do not write conversion caches to disk.

## Required Behaviors

| Behavior | Requirement |
|----------|-------------|
| selector | Apply SPEC 001 precedence exactly. |
| cache builder | Produce ephemeral cache entries with stable required keys. |
| protected terms | Preserve technical terms and proper nouns before cleanup. |
| redaction | Remove secret-like values before speech text is assembled. |
| chunking | Split long text without dropping words. |
| Markdown cleanup | Make speech-friendly text without changing meaning. |

## Deliverables

- Updated instruction normalizer oracle or helper module.
- Fixtures proving the behaviors above.
- Skill references updated only when user-facing contract changes.

## Oracles

```bash
python3 scripts/tes_tts_instruction_normalizer_oracle.py --self-test
python3 scripts/tes_tts_fixture_schema_oracle.py --self-test
python3 scripts/validate_reference_package.py
```

## Exit Criteria

- Instruction-level preparation is repeatable and fixture-backed.
- Provider absence remains `normalization_degraded`, not failure of basic TTS.
- No dependency, provider, global state, durable cache, release, or sync action
  is introduced.
