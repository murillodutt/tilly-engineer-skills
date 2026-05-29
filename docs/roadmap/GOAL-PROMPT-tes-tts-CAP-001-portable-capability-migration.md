---
tds_id: roadmap.goal_prompt_tes_tts_cap_001_portable_capability_migration
tds_class: roadmap
status: archived
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
- The active development and test workbench is
  `.agents/skills/tes-tts`; converged content is synchronized to
  `src/adapters/codex/skills/tes-tts` after local validation.
- Release identity, sync, provider installs, provider downloads, provider
  certification, durable conversion cache, and proactive speak behavior remain
  unauthorized.
- Sync status is REMOTE_SYNC_NOT_REQUESTED.
- CAP-001 feasibility was strengthened by local code mining under
  `tmp/tts-lib/`: Recognizers-Text, NeMo text processing, gruut, Lingua,
  Argos Translate, ftfy, Babel, humanize, num2words, dateparser, phonemizer,
  and eSpeak NG were treated as learning references only.
- The strongest implementation lesson is to keep source text separate from a
  request-local spoken-rendering field:
  `source_text -> protected/redacted spans -> classified speech spans ->
  spoken_rendering -> TTS provider`.

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
   - `docs/roadmap/TES-TTS-CAP-001-PORTABLE-CAPABILITY-FEASIBILITY.md`
   - `docs/roadmap/TES-TTS-OWNER-001-ACCEPTANCE-DECISION.md`
   - `docs/roadmap/TES-TTS-SKILL-ROADMAP.md`
   - `.agents/skills/tes-tts/**`
   - `src/adapters/codex/skills/tes-tts/**`
   - `src/adapters/claude/skills/tes-tts/**`
   - the mapped simple TTS and speak references needed for portable capability
     inventory.
4. Use the CAP-001 feasibility study as the starting inventory and choose the
   smallest first migration cut from it.
5. Implement the first cut in `.agents/skills/tes-tts` only when it is
   dependency-free or optional-provider guarded. The expected first cut is
   deterministic spoken rendering:
   - `ADR`, `MCP`, `API`, `SDK`, and `CLI` spoken as separate letters in
     non-exact mode;
   - `.agents/skills/tes-tts` spoken as a useful folder reference in
     non-exact mode;
   - GitHub URLs spoken as GitHub page references in non-exact mode;
   - exact/verbatim requests preserving raw paths, URLs, hashes, commands, and
     code-like spans;
   - no summary behavior.
6. Validate the runtime workbench, then mirror the converged content to
   `src/adapters/codex/skills/tes-tts`. Mirror to Claude only when the behavior
   change must be package-parity visible in this unit.
7. Preserve:
   - reactive-only `tes-tts`;
   - no user-text summary unless requested;
   - protected technical terms and proper nouns;
   - secret redaction before speech/provider stages;
   - provider absence as degraded, not fatal, for basic read-aloud.
8. Analyze the diff for quality, efficiency, precision, false-green risk,
   adapter parity, privacy, and boundary drift.
9. Fix only observed CAP-001 defects.
10. Certify with the smallest relevant TTS oracles, runtime workbench quick
   validation, adapter quick validation,
   materialization check, TDS/doc-size/reference graph validators, and
   `git diff --check`.
11. Create the next exact CAP `/goal` prompt before closure unless CAP-001
    closes the migration sequence.
12. Update `docs/roadmap/TES-TTS-SKILL-ROADMAP.md` with CAP-001 outcome,
    next prompt pointer, and sync status.
13. Stage only CAP-001 files and commit locally as the final shell action.

Forbidden:
- no sync, release, push, tag, publish, provider install, provider download,
  provider certification, proactive speak behavior, global config writes,
  durable conversion cache, version bump, bundle generation, phoneme output,
  IPA, SSML, model bundle, library vendoring, runtime dependency import, or
  unrelated `.agents/**` changes without explicit current-cycle owner approval.

Stop states:
PASS, DEGRADED, NEEDS_REVIEW, NEEDS_OWNER_DECISION, BLOCKED.

Required closeout:
- changed files;
- focused oracles and result;
- next prompt artifact;
- local commit hash;
- sync status: REMOTE_SYNC_NOT_REQUESTED unless explicitly authorized.
```
