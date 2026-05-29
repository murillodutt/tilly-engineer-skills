---
tds_id: roadmap.goal_prompt_tes_tts_cap_002_speech_transformation_hardening
tds_class: roadmap
status: active
consumer: maintainers, tes-tts maintainers, adapter authors, and execution agents
source_of_truth: false
evidence_level: L2
---

# GOAL Prompt: TES TTS CAP-002 Speech Transformation Hardening

```text
/goal Continue TES TTS capability migration.

Canonical artifact:
docs/roadmap/GOAL-SUPER-SPEC-tes-tts-capability-migration.md

Current unit:
CAP-002 Speech Transformation Hardening

Certified evidence from prior cycle:
- CAP-001 created a dependency-free spoken-rendering boundary in the
  instruction normalizer oracle.
- CAP-001 added fixture coverage for:
  - acronyms rendered as separate letters in non-exact mode;
  - semantic path rendering in non-exact mode;
  - semantic GitHub URL rendering in non-exact mode;
  - exact/verbatim preservation of raw technical spans;
  - URL false-positive guards.
- CAP-001 updated the `.agents/skills/tes-tts` workbench, Codex source, and
  Claude source skill references with `spoken_text` semantics.
- CAP-001 preserved reactive-only behavior, no-summary behavior, redaction
  before speech, provider-degraded posture, and no durable conversion cache.
- Release identity, sync, provider installs, provider downloads, provider
  certification, durable conversion cache, and proactive `speak` behavior
  remain unauthorized.
- Sync status is REMOTE_SYNC_NOT_REQUESTED.

Task:
Execute only CAP-002 through:
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
   - `.agents/skills/tes-tts/**`
   - `src/adapters/codex/skills/tes-tts/**`
   - `src/adapters/claude/skills/tes-tts/**`
   - `benchmarks/tes-tts/instruction-normalizer-fixtures.json`
   - `scripts/tes_tts_instruction_normalizer_oracle.py`
4. Harden only dependency-free speech transformation behavior that preserves
   user text without summary. Preferred candidates:
   - Markdown links, code fences, headings, bullets, and emphasis;
   - long hashes and GUID-like identifiers;
   - practical email/IP/mention/hashtag handling;
   - path and URL false-positive guards.
5. Keep source text separate from `spoken_text`; never write durable conversion
   cache data.
6. Validate first in `.agents/skills/tes-tts`, then mirror converged behavior
   to `src/adapters/codex/skills/tes-tts` and Claude when parity is required.
7. Analyze the diff for quality, efficiency, precision, false-green risk,
   adapter parity, privacy, and boundary drift.
8. Fix only observed CAP-002 defects.
9. Certify with the focused TTS oracles, workbench and adapter quick
   validation, materialization check, TDS/doc-size/reference graph validators,
   and `git diff --check`.
10. Create the next exact CAP `/goal` prompt before closure unless CAP-002
    closes the migration sequence.
11. Update `docs/roadmap/TES-TTS-SKILL-ROADMAP.md` with CAP-002 outcome,
    next prompt pointer, and sync status.
12. Stage only CAP-002 files and commit locally as the final shell action.

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
