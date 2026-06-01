---
tds_id: roadmap.tes_tts_owner_001_acceptance_decision
tds_class: roadmap
status: active
consumer: maintainers, tes-tts maintainers, release reviewers, and sync operators
source_of_truth: false
evidence_level: L2
---

# TES TTS OWNER-001 Acceptance Decision

## Decision

On 2026-05-29 the maintainer explicitly approved and accepted evolving ADR
0004.

ADR 0004 is now active as the architectural boundary for `tes-tts`
pronunciation normalization and enrichment.

## Scope Applied

This decision authorizes architectural evolution inside the accepted ADR
boundary:

- migrate portable capabilities from previously mapped simple TTS and `speak`
  references into `tes-tts`;
- keep `tes-tts` reactive and user-requested only;
- keep provider-backed translation, G2P, phoneme, lexicon, IPA, SSML, and
  real-provider behavior optional until local fixtures and probes certify them;
- preserve user text without summary unless summary is explicitly requested;
- preserve technical terms and proper nouns while adapting pronunciation hints;
- keep conversion cache behavior ephemeral unless a later decision authorizes
  durable storage.

## Still Deferred

The current approval does not authorize:

- release identity, version bump, bundle generation, tag, push, publish,
  release, or sync;
- provider install, provider download, or provider certification;
- global config writes or durable conversion cache;
- proactive `speak` behavior inside `tes-tts`.

## Result

Stop state: `PASS` for ADR acceptance.

Next execution unit:
`docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-tes-tts-capability-migration.md`

Ready prompt:
`docs/roadmap/goals/prompts/tes-tts/GOAL-PROMPT-tes-tts-CAP-001-portable-capability-migration.md`

Sync status: `REMOTE_SYNC_NOT_REQUESTED`.
