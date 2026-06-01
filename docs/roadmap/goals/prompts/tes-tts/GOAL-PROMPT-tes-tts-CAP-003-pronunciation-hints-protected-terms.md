---
tds_id: roadmap.goal_prompt_tes_tts_cap_003_pronunciation_hints_protected_terms
tds_class: roadmap
status: archived
consumer: maintainers, tes-tts maintainers, adapter authors, and execution agents
source_of_truth: false
evidence_level: L2
---

# GOAL Prompt: TES TTS CAP-003 Pronunciation Hints And Protected Terms

```text
/goal Continue TES TTS capability migration.

Canonical artifact:
docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-tes-tts-capability-migration.md

Current unit:
CAP-003 Pronunciation Hints And Protected Terms

Certified evidence from prior cycle:
- CAP-002 hardened dependency-free spoken rendering for Markdown links,
  code fences, headings, bullets, emphasis, long hashes, GUID-like
  identifiers, email addresses, valid IPv4 addresses, mentions, hashtags,
  path/URL false-positive guards, and exact-read preservation.
- CAP-002 kept source text separate from request-local `spoken_text`.
- CAP-002 preserved no-summary behavior, redaction before speech, provider
  degraded posture, reactive-only `tes-tts`, and no durable conversion cache.
- CAP-002 mirrored converged workbench behavior into Codex and Claude source
  skill references.
- Release identity, sync, provider installs, provider downloads, provider
  certification, durable conversion cache, and proactive `speak` behavior
  remain unauthorized.
- Sync status is REMOTE_SYNC_NOT_REQUESTED.

Task:
Execute only CAP-003 through:
execute -> analyze -> fix -> certify -> create next /goal prompt or close
convergence -> local commit.

Required actions:
1. Run `git status --short --branch --untracked-files=all`.
2. Classify inherited TTS changes and unrelated `.agents/**` drift. Do not
   stage or modify unrelated `.agents/**` changes.
3. Re-read:
   - `docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-tes-tts-capability-migration.md`
   - `docs/roadmap/tes-tts/TES-TTS-CAP-001-PORTABLE-CAPABILITY-FEASIBILITY.md`
   - `docs/roadmap/tes-tts/TES-TTS-SKILL-ROADMAP.md`
   - `docs/roadmap/goals/prompts/tes-tts/GOAL-PROMPT-tes-tts-CAP-003-pronunciation-hints-protected-terms.md`
   - `.agents/skills/tes-tts/**`
   - `src/adapters/codex/skills/tes-tts/**`
   - `src/adapters/claude/skills/tes-tts/**`
   - `benchmarks/tes-tts/instruction-normalizer-fixtures.json`
   - `scripts/tes_tts_instruction_normalizer_oracle.py`
4. Harden only dependency-free pronunciation-hint and protected-term behavior
   that preserves user text without summary. Preferred candidates:
   - technical terms beyond CAP-001 acronyms, such as URL, HTTP, JSON, YAML,
     SQL, SPEC, TES, Tilly, Codex, Claude, Cursor, and OpenAI;
   - proper nouns and package/model names that must not be translated;
   - command and code identifier preservation;
   - request-local hint metadata that never claims IPA, SSML, phoneme,
     lexicon, provider-backed pronunciation, or Hebrew enrichment support.
5. Keep source text separate from `spoken_text`; never write durable conversion
   cache data.
6. Validate first in `.agents/skills/tes-tts`, then mirror converged behavior
   to `src/adapters/codex/skills/tes-tts` and Claude when parity is required.
7. Analyze the diff for quality, efficiency, precision, false-green risk,
   adapter parity, privacy, and boundary drift.
8. Fix only observed CAP-003 defects.
9. Certify with the focused TTS oracles, workbench and adapter quick
   validation, materialization check, TDS/doc-size/reference graph validators,
   and `git diff --check`.
10. Create the next exact CAP `/goal` prompt before closure unless CAP-003
    closes the migration sequence.
11. Update `docs/roadmap/tes-tts/TES-TTS-SKILL-ROADMAP.md` with CAP-003 outcome,
    next prompt pointer, and sync status.
12. Stage only CAP-003 files and commit locally as the final shell action.

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
