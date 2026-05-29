---
tds_id: roadmap.tes_tts_acceptance_and_release_decision
tds_class: roadmap
status: active
consumer: maintainers, tes-tts maintainers, execution agents, and release reviewers
source_of_truth: false
evidence_level: L2
---

# TES TTS Acceptance And Release Decision

This record closed TTS-009 as a decision cycle. TTS-009 recommended ADR 0004
acceptance but did not itself accept the ADR, change release identity, run
sync, publish, tag, push, or certify provider behavior.

OWNER-001 later accepted ADR 0004 on 2026-05-29. Release identity, sync, and
provider certification remain separate deferred decisions.

## Decision

TTS-009 recommends accepting ADR 0004 for the current bounded scope:
instruction-level pronunciation normalization, ephemeral conversion cache
semantics, protected-term preservation, secret redaction, no-summary behavior,
mocked no-write provider probing, provider candidate review, and adapter
parity.

OWNER-001 supersedes the TTS-009 status limitation: ADR 0004 is now `active`
because explicit maintainer approval was provided on 2026-05-29.

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
| Can ADR 0004 status be changed now? | Yes. OWNER-001 accepted ADR 0004 on 2026-05-29. |
| Can release identity proceed now? | No. Release identity needs separate explicit approval. |
| Can sync proceed now? | No. Sync remains forbidden until complete skill approval. |
| Are providers certified? | No. Provider review and probe behavior remain mocked/no-write and non-certifying. |
| Is basic `tes-tts` still useful without providers? | Yes. Provider absence degrades enrichment, not basic read-aloud behavior. |

## Owner Decision Needed

Next state after OWNER-001: ADR acceptance `PASS`; release identity and sync
remain deferred.

The next cycle must ask for an explicit maintainer decision on:

1. Accept ADR 0004 now or keep it proposed.
2. Authorize release identity planning or defer it.
3. Continue forbidding sync or authorize a later sync cycle after release
   identity is handled.

After OWNER-001, the correct state is accepted architecture, installable from
source but not released/synced, and provider-aware but not provider-certified.
