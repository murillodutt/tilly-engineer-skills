---
tds_id: roadmap.tes_tts_normalization_execution_spec
tds_class: roadmap
status: proposed
consumer: maintainers, tes-tts maintainers, adapter authors, and validation authors
source_of_truth: false
evidence_level: L2
---

# TES TTS Normalization Execution SPEC

This SPEC defines the proposed execution path for ADR 0004 and the companion
architecture SPEC.

It is a proposal. Do not run sync, release, install dependencies, or advertise
certified provider behavior from this document alone.

## Execution Principles

1. Start with fixtures and instruction-level normalization.
2. Execute one work unit at a time until the `tes-tts` behavior converges.
3. Add provider probing before provider use.
4. Keep provider probes read-only and local.
5. Never download or install language models from a skill invocation.
6. Treat missing providers as `normalization_degraded`, not as failure of basic
   `tes-tts`.
7. Certify each language with fixtures before claiming support.

## Sequential Convergence Contract

`tes-tts` normalization work proceeds sequentially. Each decision, fixture,
provider probe, and adapter update must be resolved, documented, and validated
before the next execution branch opens.

Parallel exploration may inform a decision, but it must not create parallel
implementation streams, partial syncs, or multiple unclosed behavior changes.
Convergence means the current unit has:

- an explicit decision or degraded-state classification;
- the smallest correlated source or doc update;
- a local oracle result;
- a known next question or next work unit.

## Work Units

| Unit | Outcome | Oracle |
|------|---------|--------|
| Fixture corpus | Mixed-language samples for `pt-BR`, `en`, `es`, `fr`, `it`, `de`, and `he`. | Fixture schema check. |
| Protected-term extractor | ADR, SPEC, MCP, API, JSON, YAML, CLI, SDK, SQL, commands, paths, and names survive translation. | Deterministic unit fixtures. |
| Cache builder | Ephemeral conversion cache shape is produced without disk writes. | Cache fixture test. |
| Default-language selector | Explicit user language wins, then declared coding-agent adapter default, then Cursor fallback to Codex default and Claude default, then request language, then dominant text language. | Selection fixtures. |
| Provider probe | Detect available provider versions and supported languages without installation. | Probe self-test with mocked providers. |
| Pronunciation hints | Conservative hints are generated without semantic corruption. | Golden-output fixtures. |
| Redaction gate | Secret-like values are removed before translation and TTS. | Negative fixtures. |
| Adapter parity | Codex and Claude skill references stay behaviorally aligned. | `materialize_adapter.py all --check`. |

## Agent Default Language Contract

The coding-agent adapter default language is a selector preference only when
the adapter declares it explicitly. It must never override an explicit user
language request. Codex uses `~/.codex/config.toml`
`[desktop].localeOverride`. Claude Code uses `~/.claude/settings.json`
`language`, with `Portuguese` normalized to the TES Portuguese target
`pt-BR`. Cursor has no native structured language setting identified for this
contract; when Cursor has no explicit User Rules or project rules declaring a
language, the selector falls back to the Codex default first, then the Claude
default.

If the active adapter declaration and fallback declarations are absent, the
value is `unknown` and the selector proceeds to request language or dominant
text language.

Selection fixtures must cover:

- explicit adapter default language present;
- adapter default language absent;
- user language request overriding the declared adapter default;
- Cursor without a declared default falling back to Codex, then Claude;
- mixed text falling through to request or dominant text language.

Expected selector outcomes:

| Case | Active adapter | Explicit user language | Declared adapter default | Codex default | Claude default | Request language | Dominant text language | Expected target |
|------|----------------|------------------------|--------------------------|---------------|----------------|------------------|------------------------|-----------------|
| DLS-001 | Codex | `en` | `pt-BR` | `pt-BR` | `pt-BR` | `pt-BR` | `pt-BR` | `en` |
| DLS-002 | Codex | absent | `pt-BR` | `pt-BR` | `pt-BR` | `en` | `en` | `pt-BR` |
| DLS-003 | unknown | absent | `unknown` | `unknown` | `unknown` | `pt-BR` | `en` | `pt-BR` |
| DLS-004 | unknown | absent | `unknown` | `unknown` | `unknown` | unclear | `de` | `de` |
| DLS-005 | unknown | absent | `unknown` | `unknown` | `unknown` | unclear | unclear | preserve original |
| DLS-006 | Cursor | absent | `unknown` | `pt-BR` | `pt-BR` | `en` | `en` | `pt-BR` |

The future fixture schema owns the executable representation of these cases.
This SPEC owns the expected selector decision order.

## Fixture Schema Contract

Fixture records use the machine-readable schema at
[`benchmarks/tes-tts/normalization-fixture.schema.json`](../../benchmarks/tes-tts/normalization-fixture.schema.json).
The initial dependency-free corpus lives at
[`benchmarks/tes-tts/normalization-fixtures.json`](../../benchmarks/tes-tts/normalization-fixtures.json).
The schema is dependency-free and can be checked with:

```bash
python3 scripts/tes_tts_fixture_schema_oracle.py --self-test
```

Every fixture must include selector inputs, source text, expected target
language, protected terms, redaction expectation, provider state, expected
status, and `no_summary: true`.

## Fixture Classes

Required fixture classes:

- single-language text per first-class language;
- mixed default-language text with one foreign span;
- mixed text with protected technical terms;
- Hebrew text without niqqud;
- Markdown with links, code fences, file paths, and long hashes;
- secret-like values inside multilingual text;
- explicit voice/provider request;
- provider unavailable and voice unavailable failures.

## Provider Probe Contract

Instruction-level normalization is checked before provider probing with:

```bash
python3 scripts/tes_tts_instruction_normalizer_oracle.py --self-test
```

That oracle uses
[`benchmarks/tes-tts/instruction-normalizer-fixtures.json`](../../benchmarks/tes-tts/instruction-normalizer-fixtures.json)
to verify ephemeral cache shape, protected terms, redaction-before-speech, and
chunking without summary.

It also validates selector precedence against the dependency-free
normalization corpus and verifies Markdown speech cleanup for headings, links,
paths, and code fences without changing meaning or summarizing user text.

Provider probes must return only local evidence:

```text
provider_probe:
- provider: candidate provider name
  status: provider_available | provider_not_available | provider_needs_review
  version: local version when available
  languages: locally verified language codes
  license_note: local package/model license signal when known
  reason: short explanation
```

Probes must not call installers, package managers, network downloads, or model
fetch commands.

The initial provider probe contract is mocked and no-write:

```bash
python3 scripts/tes_tts_provider_probe_oracle.py --self-test
```

That oracle covers `provider_available`, `provider_not_available`, and
`provider_needs_review` without probing real providers or claiming provider
support.

Provider candidate review is checked with:

```bash
python3 scripts/tes_tts_provider_candidate_review_oracle.py --self-test
```

The review ranks candidates for future probes only. It must not certify,
install, download, or execute providers.

## Acceptance Gates

Before ADR 0004 can move from `proposed` to accepted:

1. Architecture SPEC reviewed and updated.
2. Execution SPEC reviewed and updated.
3. At least instruction-level fixtures exist for all first-class languages.
4. Protected-term fixtures pass.
5. Redaction-before-provider fixtures pass.
6. Provider probe contract exists and is no-write.
7. Codex and Claude `tes-tts` skills validate.
8. Adapter materialization passes.
9. TDS validation and doc-size validation pass.
10. Murillo explicitly approves ADR acceptance.

## Deferred Work

These remain out of scope until a later accepted implementation decision:

- bundling any provider or model;
- installing language packages;
- SSML or lexicon generation;
- provider-specific phoneme output;
- persisted conversion caches;
- proactive `speak` behavior;
- release identity or sync.
