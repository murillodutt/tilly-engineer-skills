---
tds_id: roadmap.tes_tts_acceptance_and_release_decision
tds_class: roadmap
status: active
consumer: maintainers, tes-tts maintainers, execution agents, and release reviewers
source_of_truth: false
evidence_level: L2
---

# TES TTS Acceptance And Release Decision

This record closes TTS-009 as a decision cycle. It does not accept ADR 0004,
change release identity, run sync, publish, tag, push, or certify provider
behavior.

## Decision

TTS-009 recommends accepting ADR 0004 for the current bounded scope:
instruction-level pronunciation normalization, ephemeral conversion cache
semantics, protected-term preservation, secret redaction, no-summary behavior,
mocked no-write provider probing, provider candidate review, and adapter
parity.

ADR 0004 remains `proposed` because explicit maintainer approval to change its
status was not provided in this cycle.

Release identity must not proceed in this cycle. `tes-tts` is adopter-visible
delivered behavior and will require a separate authorized release identity
decision before any version, bundle, sync, tag, push, release, or publication
surface changes.

## Evidence

The acceptance recommendation is based on completed sequential units:

- TTS-000 through TTS-002 established the roadmap, SPEC coherence, and
  default-language selector contract.
- TTS-003 through TTS-004 added a dependency-free fixture schema and selector
  corpus.
- TTS-005 added the instruction-level normalizer oracle.
- TTS-006 added the mocked no-write provider probe contract.
- TTS-007 added the provider candidate review queue.
- TTS-008 confirmed Codex and Claude parity, Cursor/install trigger honesty,
  and adapter materialization.

Focused evidence surfaces:

- `benchmarks/tes-tts/normalization-fixture.schema.json`
- `benchmarks/tes-tts/normalization-fixtures.json`
- `benchmarks/tes-tts/instruction-normalizer-fixtures.json`
- `benchmarks/tes-tts/provider-probe-fixtures.json`
- `benchmarks/tes-tts/provider-candidate-review.json`
- `scripts/tes_tts_fixture_schema_oracle.py`
- `scripts/tes_tts_instruction_normalizer_oracle.py`
- `scripts/tes_tts_provider_probe_oracle.py`
- `scripts/tes_tts_provider_candidate_review_oracle.py`

## Classification

| Question | TTS-009 result |
|----------|----------------|
| Can ADR 0004 be recommended for acceptance? | Yes, for the bounded instruction-level and provider-boundary scope. |
| Can ADR 0004 status be changed now? | No. Explicit maintainer approval is still required. |
| Can release identity proceed now? | No. Release identity needs separate explicit approval. |
| Can sync proceed now? | No. Sync remains forbidden until complete skill approval. |
| Are providers certified? | No. Provider review and probe behavior remain mocked/no-write and non-certifying. |
| Is basic `tes-tts` still useful without providers? | Yes. Provider absence degrades enrichment, not basic read-aloud behavior. |

## Owner Decision Needed

Next state: `NEEDS_OWNER_DECISION`.

The next cycle must ask for an explicit maintainer decision on:

1. Accept ADR 0004 now or keep it proposed.
2. Authorize release identity planning or defer it.
3. Continue forbidding sync or authorize a later sync cycle after release
   identity is handled.

Until those decisions are explicit, the correct state is recommended but not
accepted, installable from source but not released/synced, and provider-aware
but not provider-certified.
