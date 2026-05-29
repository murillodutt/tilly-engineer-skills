---
tds_id: roadmap.goal_prompt_tes_tts_cap_004_provider_fallback_catalog_use
tds_class: roadmap
status: archived
consumer: maintainers, tes-tts maintainers, adapter authors, and execution agents
source_of_truth: false
evidence_level: L2
---

# GOAL Prompt: TES TTS CAP-004 Provider Fallback Catalog Use

```text
/goal Continue TES TTS capability migration.

Canonical artifact:
docs/roadmap/GOAL-SUPER-SPEC-tes-tts-capability-migration.md

Current unit:
CAP-004 Provider Fallback Catalog Use

Certified evidence from prior cycle:
- CAP-003 hardened dependency-free pronunciation hints and protected-term
  preservation for URL, HTTP, JSON, YAML, SQL, SPEC, TES, Tilly, Codex,
  Claude, Cursor, OpenAI, package/model names, commands, and code
  identifiers.
- CAP-003 kept source text separate from request-local `spoken_text`.
- CAP-003 preserved no-summary behavior, redaction before speech, provider
  degraded posture, reactive-only `tes-tts`, and no durable conversion cache.
- CAP-003 mirrored converged workbench behavior into Codex and Claude source
  skill references.
- Release identity, sync, provider installs, provider downloads, provider
  certification, durable conversion cache, and proactive `speak` behavior
  remain unauthorized.
- Sync status is REMOTE_SYNC_NOT_REQUESTED.

Task:
Execute only CAP-004 through:
execute -> analyze -> fix -> certify -> create next /goal prompt or close
convergence -> local commit.

Required actions:
1. Run `git status --short --branch --untracked-files=all`.
2. Classify inherited TTS changes and unrelated `.agents/**` drift. Do not
   stage or modify unrelated `.agents/**` changes.
3. Re-read:
   - `docs/roadmap/GOAL-SUPER-SPEC-tes-tts-capability-migration.md`
   - `docs/roadmap/TES-TTS-CAP-001-PORTABLE-CAPABILITY-FEASIBILITY.md`
   - `docs/roadmap/TES-TTS-SKILL-ROADMAP.md`
   - `docs/roadmap/GOAL-PROMPT-tes-tts-CAP-004-provider-fallback-catalog-use.md`
   - `.agents/skills/tes-tts/**`
   - `src/adapters/codex/skills/tes-tts/**`
   - `src/adapters/claude/skills/tes-tts/**`
   - provider references and mocked provider probe fixtures/oracles
4. Harden only dependency-free provider fallback catalog behavior. Preferred
   candidates:
   - request-local provider order and fallback explanation;
   - error classification for auth, quota/rate limit, unavailable provider,
     unavailable voice, and generic failure;
   - voice policy that respects explicit user voice and degrades honestly;
   - catalog use as reference/runtime guidance only, with no provider install,
     download, certification, global unavailable registry, or config write.
5. Keep source text separate from `spoken_text`; never write durable conversion
   cache data or provider state.
6. Validate first in `.agents/skills/tes-tts`, then mirror converged behavior
   to `src/adapters/codex/skills/tes-tts` and Claude when parity is required.
7. Analyze the diff for quality, efficiency, precision, false-green risk,
   adapter parity, privacy, and boundary drift.
8. Fix only observed CAP-004 defects.
9. Certify with the focused TTS oracles, provider probe/candidate review
   oracles, workbench and adapter quick validation, materialization check,
   TDS/doc-size/reference graph validators, and `git diff --check`.
10. Create the next exact CAP `/goal` prompt before closure unless CAP-004
    closes the migration sequence.
11. Update `docs/roadmap/TES-TTS-SKILL-ROADMAP.md` with CAP-004 outcome,
    next prompt pointer, and sync status.
12. Stage only CAP-004 files and commit locally as the final shell action.

Forbidden:
- no sync, release, push, tag, publish, provider install, provider download,
  provider certification, proactive speak behavior, global config writes,
  durable conversion cache, version bump, bundle generation, phoneme output,
  IPA, SSML, model bundle, library vendoring, runtime dependency import, or
  unrelated `.agents/**` changes without explicit current-cycle owner
  approval.

Stop states:
PASS, DEGRADED, NEEDS_REVIEW, NEEDS_OWNER_DECISION, BLOCKED.

Required closeout:
- changed files;
- focused oracles and result;
- next prompt artifact;
- local commit hash;
- sync status: REMOTE_SYNC_NOT_REQUESTED unless explicitly authorized.
```
