---
tds_id: architecture.adr_0004_tes_tts_pronunciation_normalization_and_enrichment
tds_class: architecture
status: proposed
consumer: maintainers, adapter authors, tes-tts maintainers, and release operators
source_of_truth: false
evidence_level: L1
---

# ADR 0004: TES TTS Pronunciation Normalization And Enrichment

Proposed on 2026-05-28 during `tes-tts` skill construction.

TES will treat pronunciation normalization and language enrichment for
`tes-tts` as an optional, locally verified speech-preparation boundary, not as
a bundled translation stack, audio subsystem, dependency manager, or proactive
announcement channel.

This ADR is proposed, not accepted. It must not be treated as release
certification, sync approval, or permission to bundle new models, binaries, or
third-party libraries.

## Context

`tes-tts` is reactive. It speaks only when the user explicitly asks TES to
read, narrate, or speak specific text. The skill already owns text cleanup,
secret redaction, default voice/rate handling, and honest
`TTS_NOT_AVAILABLE` reporting.

The next hard-to-reverse design choice is the boundary for multilingual and
technical speech quality. TES needs better spoken output for mixed-language
text, acronyms, product names, code identifiers, and first-class languages
such as `pt-BR`, `en`, `es`, `fr`, `it`, `de`, and `he`. No single library is
the obvious source of truth for detection, translation, text normalization,
and pronunciation across that set.

## Decision

TES adopts this architectural boundary:

1. `tes-tts` may prepare an ephemeral conversion cache before playback.
2. The cache is speech preparation only: it is not durable memory, Field
   Reports, Event Ledger, or translation evidence.
3. Third-party libraries, language models, TTS services, phonemizers, and
   locale data are optional providers only.
4. TES must not install, download, bundle, persist, or auto-enable those
   providers without a separate accepted implementation decision.
5. Provider absence degrades enrichment, not basic read-aloud behavior.
6. Technical terms and proper nouns may receive pronunciation hints, but must
   not be semantically translated.
7. `tes-tts` remains reactive; proactive announcements belong to `speak` or a
   future explicitly accepted skill.

The detailed architecture and execution plan are intentionally not embedded in
this ADR. They live in roadmap SPECs:

- `docs/roadmap/TES-TTS-NORMALIZATION-ARCHITECTURE-SPEC.md`
- `docs/roadmap/TES-TTS-NORMALIZATION-EXECUTION-SPEC.md`

## Invariants

- Source text remains unchanged. Only the speech payload is normalized.
- Secret-like content is redacted before translation, provider calls, or
  playback.
- Provider use is local and evidence-based.
- No provider name becomes a product claim until an oracle verifies the local
  version, license posture, and language coverage.
- Hebrew quality must explicitly report degraded state when niqqud, G2P, or
  local voice support is missing.
- Library-backed normalization cannot be called certified until the execution
  SPEC or successor oracles prove it.

## Rejected Alternatives

| Alternative | Rejection |
|-------------|-----------|
| Bundle a full translation stack in TES by default. | Increases install size, license surface, model lifecycle, and support burden before certification. |
| Choose one library as the universal normalizer. | No single candidate cleanly covers detection, translation, TTS normalization, and pronunciation for the required languages. |
| Keep provider and pipeline details in this ADR. | Those details are volatile and belong in architecture/execution SPECs that can evolve without rewriting the boundary decision. |
| Translate every unfamiliar token. | Breaks proper nouns, code identifiers, acronyms, and technical meaning. |
| Store conversion caches as durable evidence by default. | The cache may contain user text and belongs to ephemeral speech preparation. |
| Auto-download missing language models. | Violates TES local, explicit, auditable dependency posture. |

## Consequences

This decision gives `tes-tts` a clear north star without overclaiming current
implementation. The skill can improve speech quality incrementally while the
package remains boring at its dependency boundary.

Until this ADR is accepted and the execution oracles exist:

- `tes-tts` may document the strategy and use instruction-level normalization;
- optional provider catalogs remain references, not certified behavior;
- TES must not claim bundled or library-backed normalization;
- TES must not sync, release, or advertise this behavior from the proposed ADR
  alone.
