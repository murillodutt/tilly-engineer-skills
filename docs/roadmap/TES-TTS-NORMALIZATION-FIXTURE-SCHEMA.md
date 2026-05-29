---
tds_id: roadmap.tes_tts_normalization_fixture_schema
tds_class: roadmap
status: proposed
consumer: maintainers, tes-tts maintainers, validation authors, and execution agents
source_of_truth: false
evidence_level: L2
---

# TES TTS Normalization Fixture Schema

This document defines the minimum fixture shape for future `tes-tts`
normalization tests. It does not add the fixture corpus, provider probing,
runtime dependencies, sync, release, or certified language behavior.

Machine-readable schema:
[`benchmarks/tes-tts/normalization-fixture.schema.json`](../../benchmarks/tes-tts/normalization-fixture.schema.json)

Minimal corpus:
[`benchmarks/tes-tts/normalization-fixtures.json`](../../benchmarks/tes-tts/normalization-fixtures.json)

Instruction normalizer fixtures:
[`benchmarks/tes-tts/instruction-normalizer-fixtures.json`](../../benchmarks/tes-tts/instruction-normalizer-fixtures.json)

Focused oracle:
`python3 scripts/tes_tts_fixture_schema_oracle.py --self-test`

Instruction normalizer oracle:
`python3 scripts/tes_tts_instruction_normalizer_oracle.py --self-test`

## Fixture Record

Each fixture is one JSON object with these required fields:

| Field | Meaning |
|-------|---------|
| `id` | Stable lowercase fixture id, such as `tts-selector-user-language-wins`. |
| `class` | Fixture class: selector, normalization, protected terms, redaction, Markdown transform, provider fallback, or pronunciation hint. |
| `selector` | Inputs for the default-language selector. |
| `source_text` | The original user text or span to prepare for speech. |
| `expected_target_language` | Expected target language or `preserve_original`. |
| `protected_terms` | Terms that must survive normalization without semantic translation. |
| `redaction` | Whether secret-like content is present and which redactions are expected. |
| `provider_state` | Local provider/enrichment posture expected for the fixture. |
| `expected_status` | Expected oracle status for the fixture. |
| `no_summary` | Must be `true`; fixtures must not permit summarizing user text unless a later accepted contract adds that class explicitly. |

## Selector Shape

`selector` records the decision inputs without invoking translation or TTS:

```json
{
  "active_adapter": "cursor",
  "explicit_user_language": "absent",
  "declared_adapter_default": "unknown",
  "codex_default": "pt-BR",
  "claude_default": "pt-BR",
  "request_language": "pt-BR",
  "dominant_text_language": "en"
}
```

Allowed first-class language codes are `pt-BR`, `en`, `es`, `fr`, `it`, `de`,
and `he`. Selector fields may also use `absent`, `unknown`, or `unclear` where
the schema permits them. Cursor fixtures may keep `declared_adapter_default` as
`unknown` and use `codex_default` then `claude_default` as fallback inputs when
no Cursor User Rules or project rules declare a language.

## Status Values

Fixtures use the same stop vocabulary as the convergence loop:

| Status | Meaning |
|--------|---------|
| `PASS` | The expected instruction-level behavior should pass. |
| `DEGRADED` | Basic read-aloud remains possible, but enrichment is intentionally partial. |
| `NEEDS_REVIEW` | The fixture exposes an ambiguity that must not be auto-certified. |
| `BLOCKED` | Continuing would violate a boundary such as privacy, provider posture, or unavailable TTS. |

## Provider State Values

`provider_state` is a fixture expectation, not provider discovery:

- `provider_available`
- `provider_not_available`
- `provider_needs_review`
- `normalization_degraded`
- `tts_not_available`

Fixtures must not install, download, probe the network, write global config, or
persist conversion caches.

## Corpus Coverage

The SPEC-002 corpus covers:

- first-class languages: `pt-BR`, `en`, `es`, `fr`, `it`, `de`, and `he`;
- mixed-language default-language text with one foreign span;
- protected terms including ADR, SPEC, MCP, API, JSON, YAML, CLI, SDK,
  commands, paths, and code identifiers;
- redaction of secret-like values before speech text;
- Markdown, URLs, paths, code fences, and long hashes;
- provider unavailable and voice unavailable degraded states;
- Hebrew degraded posture when niqqud or certified local Hebrew voice support
  is absent.

The schema oracle validates required corpus coverage so a structurally valid
but incomplete corpus does not pass silently.

## TTS-004 Boundary

The corpus uses this schema and stays dependency-free. It includes the selector
cases `DLS-001` through `DLS-006` and the SPEC-002 language and negative
fixtures before provider work opens.

The schema oracle validates both the schema and the corpus shape. It does not
execute translation, TTS playback, provider probing, network calls, downloads,
or install steps.

The instruction normalizer oracle validates only dependency-free preparation
behavior: ephemeral cache shape, protected-term preservation, redaction before
speech text, and long-text chunking without summary.
