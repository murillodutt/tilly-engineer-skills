---
tds_id: roadmap.goal_prompt_tes_tts_cap_001_portable_capability_migration
tds_class: roadmap
status: active
consumer: maintainers, tes-tts maintainers, adapter authors, and execution agents
source_of_truth: false
evidence_level: L2
---

# GOAL Prompt: TES TTS CAP-001 Portable Capability Migration

```text
/goal Continue TES TTS capability migration.

Canonical artifact:
docs/roadmap/GOAL-SUPER-SPEC-tes-tts-capability-migration.md

Current unit:
CAP-001 Portable Capability Inventory And First Migration Cut

Certified evidence from prior cycle:
- ADR 0004 is accepted and active as the pronunciation normalization and
  enrichment boundary.
- The ten-SPEC technical convergence completed for the bounded scope.
- OWNER-001 authorized architectural evolution and migration of portable
  capabilities from mapped simple TTS and speak references.
- Release identity, sync, provider installs, provider downloads, provider
  certification, durable conversion cache, and proactive speak behavior remain
  unauthorized.
- Sync status is REMOTE_SYNC_NOT_REQUESTED.

Task:
Execute only CAP-001 through:
execute -> analyze -> fix -> certify -> create next /goal prompt or close
convergence -> local commit.

Required actions:
1. Run `git status --short --branch --untracked-files=all`.
2. Classify inherited TTS changes and unrelated `.agents/**` drift. Do not
   stage or modify unrelated `.agents/**` changes.
3. Re-read:
   - `docs/adr/0004-tes-tts-pronunciation-normalization-and-enrichment.md`
   - `docs/roadmap/GOAL-SUPER-SPEC-tes-tts-capability-migration.md`
   - `docs/roadmap/TES-TTS-OWNER-001-ACCEPTANCE-DECISION.md`
   - `docs/roadmap/TES-TTS-SKILL-ROADMAP.md`
   - `src/adapters/codex/skills/tes-tts/**`
   - `src/adapters/claude/skills/tes-tts/**`
   - the mapped simple TTS and speak references needed for portable capability
     inventory.
4. Build a portable capability inventory and choose the smallest first
   migration cut.
5. Implement only the first cut when it is dependency-free or optional-provider
   guarded.
6. Preserve:
   - reactive-only `tes-tts`;
   - no user-text summary unless requested;
   - protected technical terms and proper nouns;
   - secret redaction before speech/provider stages;
   - provider absence as degraded, not fatal, for basic read-aloud.
7. Analyze the diff for quality, efficiency, precision, false-green risk,
   adapter parity, privacy, and boundary drift.
8. Fix only observed CAP-001 defects.
9. Certify with the smallest relevant TTS oracles, adapter quick validation,
   materialization check, TDS/doc-size/reference graph validators, and
   `git diff --check`.
10. Create the next exact CAP `/goal` prompt before closure unless CAP-001
    closes the migration sequence.
11. Update `docs/roadmap/TES-TTS-SKILL-ROADMAP.md` with CAP-001 outcome,
    next prompt pointer, and sync status.
12. Stage only CAP-001 files and commit locally as the final shell action.

Forbidden:
- no sync, release, push, tag, publish, provider install, provider download,
  provider certification, proactive speak behavior, global config writes,
  durable conversion cache, version bump, bundle generation, or unrelated
  `.agents/**` changes without explicit current-cycle owner approval.

Stop states:
PASS, DEGRADED, NEEDS_REVIEW, NEEDS_OWNER_DECISION, BLOCKED.

Required closeout:
- changed files;
- focused oracles and result;
- next prompt artifact;
- local commit hash;
- sync status: REMOTE_SYNC_NOT_REQUESTED unless explicitly authorized.
```
