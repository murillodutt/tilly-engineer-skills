---
tds_id: roadmap.goal_super_spec_tes_tts_lexical_runtime_engine_latency_reduction
tds_class: roadmap
status: active
consumer: maintainers, tes-tts maintainers, adapter authors, validation authors, and execution agents
source_of_truth: false
evidence_level: L1
---

# GOAL Super SPEC: TES TTS Lexical Runtime Engine And Latency Reduction

Status: active runtime-performance line after the PT-BR lexical foundation.

Canonical artifact:
`docs/roadmap/GOAL-SUPER-SPEC-tes-tts-lexical-runtime-engine-latency-reduction.md`

Current execution unit:
`RTE-001 Compiled Lexical Index Contract`

Ready prompt:
`docs/roadmap/GOAL-PROMPT-tes-tts-RTE-001-compiled-lexical-index-contract.md`

Prior line:
`docs/roadmap/GOAL-SUPER-SPEC-tes-tts-ptbr-lexical-normalization.md`

## Mantra Gate Snapshot

- `VERIFY`: LEX-001 through LEX-005 closed the evidence-only lexical
  foundation; live TTS usage exposed latency as an adoption blocker.
- `SCOPE`: create a fast, dependency-free runtime engine path before adding
  G2P or provider-backed pronunciation.
- `BEST_PATH`: measure latency first, then move knowledge lookup into compiled
  indexes outside the hot path.
- `DOCUMENT`: this Super SPEC and one ready `/goal` prompt are the authority.
- `ORACLE`: every runtime claim must have latency fixtures or a benchmark
  oracle.
- `RESOLVE`: no release, sync, provider install, full dictionary vendoring, or
  runtime IPA/phoneme/SSML output in this line.
- `STATUS`: `PASS_TO_EXECUTE`.

## Purpose

Turn the PT-BR lexical foundation into a fast runtime preparation engine for
reactive `tes-tts` speech. The goal is lower time-to-first-audio and lower text
preparation cost without claiming full G2P, provider-backed pronunciation, or
SSML/PLS runtime output.

The operating thesis is:

```text
cold build: lexicon evidence -> compiled indexes
hot path: text -> redact -> match spans -> render spoken_text -> TTS
```

Nothing expensive should happen repeatedly on the hot path.

## Certified Context

- ADR 0004 is active and bounds pronunciation normalization and enrichment.
- CAP-006 through CAP-009 proved conversational rendering, exact islands,
  structure oralization, and English/protected identity behavior.
- LEX-001 through LEX-005 created and audited PT-BR lexical schema, sample
  manifests, lookup oracles, integration boundary, and catalog fixtures.
- The active development workbench remains `.agents/skills/tes-tts`; converged
  behavior is mirrored to `src/adapters/codex/skills/tes-tts` and
  `src/adapters/claude/skills/tes-tts` when adapter-visible.
- Release identity, sync, provider installs, provider downloads, provider
  certification, durable conversion cache, global config writes, version bump,
  and proactive `speak` behavior remain unauthorized.

## Runtime Architecture Target

```text
source_text
-> secret redaction
-> cheap shape scan
-> compiled exact/phrase/path/url/code matchers
-> request-local render plan
-> spoken_text chunks
-> provider call
-> playback
```

The runtime engine may use classic in-memory data structures:

- exact map for single-token protected terms;
- trie for exact lexical and prefix-classified terms;
- Aho-Corasick-style phrase matching when fixture volume justifies it;
- precompiled regular expressions for URLs, paths, hashes, commands, secrets,
  code fences, package names, and model names;
- request-local memoization for repeated spans.

JSON/JSONL remains the TES canonical lexicon format. PLS XML, SSML, IPA,
phoneme, and provider lexicons remain export or future integration surfaces
only, not runtime output in this line.

## Non-Objectives

- no full G2P implementation;
- no runtime IPA, phoneme, SSML, PLS, or provider lexicon output;
- no full PT-BR dictionary vendoring;
- no provider install, provider download, provider certification, release,
  push, tag, publish, version bump, bundle generation, or sync;
- no proactive `speak` behavior;
- no durable conversion cache;
- no user-text summary unless explicitly requested.

## Execution Units

| Unit | Focus | Boundary |
|------|-------|----------|
| RTE-000 | Preflight and latency baseline | Complete: measurable latency fixtures and dependency-free benchmark oracle without runtime behavior changes. |
| RTE-001 | Compiled lexical index contract | Build dependency-free index shape over governed fixtures; exact map first, trie only if needed. |
| RTE-002 | Hot-path span matcher | Use precompiled matchers for protected terms, paths, URLs, commands, code, hashes, and secrets. |
| RTE-003 | Fast-path spoken rendering | Add a cheap PT-BR prose path that avoids deep analysis when shape scan is simple. |
| RTE-004 | Request-local memoization | Avoid reprocessing repeated spans inside one read-aloud request without creating durable cache. |
| RTE-005 | Chunked preparation boundary | Prepare first speakable chunk quickly while later chunks remain request-local and ordered. |
| RTE-006 | Runtime audit and closure | Certify latency improvement, preserved boundaries, degraded surfaces, and next G2P-lite decision. |

## Performance Targets

Initial targets are deliberately strict enough to expose drag:

- `text_prepare_ms_p50 <= 50` for short/simple PT-BR prose fixtures;
- `text_prepare_ms_p95 <= 150` for mixed technical prose fixtures;
- `first_chunk_ready_ms <= 100` for texts under 1,000 characters;
- no secret leak, source mutation, command execution, user-text summary, or
  runtime IPA/phoneme/SSML output while meeting latency targets.

Provider/network latency must be measured separately from TES preparation
latency. If the provider is the bottleneck, this line must prove TES is not
adding avoidable delay before the provider call.

## Required Loop

```text
execute -> analyze -> fix -> certify -> create next /goal prompt or close
convergence -> local commit
```

Each non-closed unit must update `docs/roadmap/TES-TTS-SKILL-ROADMAP.md` and
create the next ready prompt artifact before local commit.

## Certification

Each unit chooses the smallest relevant set from:

```bash
python3 scripts/tes_tts_runtime_latency_oracle.py --self-test
python3 scripts/tes_tts_ptbr_lexical_manifest_oracle.py --self-test
python3 scripts/tes_tts_ptbr_lexical_lookup_oracle.py --self-test
python3 scripts/tes_tts_ptbr_lexical_integration_oracle.py --self-test
python3 scripts/tes_tts_pronunciation_catalog_oracle.py --self-test
python3 scripts/tes_tts_fixture_schema_oracle.py --self-test
python3 scripts/tes_tts_instruction_normalizer_oracle.py --self-test
python3 /Users/murillo/.codex/skills/.system/skill-creator/scripts/quick_validate.py .agents/skills/tes-tts
python3 /Users/murillo/.codex/skills/.system/skill-creator/scripts/quick_validate.py src/adapters/codex/skills/tes-tts
python3 /Users/murillo/.codex/skills/.system/skill-creator/scripts/quick_validate.py src/adapters/claude/skills/tes-tts
python3 scripts/materialize_adapter.py all --check
python3 scripts/validate_tds.py
python3 scripts/validate_doc_size.py
python3 scripts/validate_reference_graph.py
git diff --check
```

`scripts/tes_tts_runtime_latency_oracle.py` is created by RTE-000 before it is
required outside that unit.

## Stop States

- `PASS`: unit completed, latency or boundary oracle passes, no forbidden
  runtime surface entered.
- `DEGRADED`: runtime improvement is bounded or global package closure is
  affected by unrelated drift.
- `PERFORMANCE_REGRESSION`: preparation latency worsened against the prior
  fixture baseline.
- `NEEDS_REVIEW`: matcher complexity, false-green risk, privacy, adapter
  parity, or performance evidence is ambiguous.
- `NEEDS_OWNER_DECISION`: release identity, sync, full dictionary packaging,
  G2P, SSML/PLS export, provider-backed pronunciation, or language expansion
  needs maintainer approval.
- `SAFETY_BLOCKED`: secret exposure, command execution, global config write,
  provider install/download, push, tag, publish, or forbidden side effect would
  occur.
- `BLOCKED`: continuing would violate an existing lock.

## Closure

This line closes only when RTE-006 proves the runtime path is faster for the
bounded fixtures and preserves ADR 0004 boundaries. Closure does not authorize
release identity, sync, provider certification, full dictionary vendoring, G2P,
SSML, PLS, IPA runtime output, phoneme output, or proactive speech.
