---
tds_id: roadmap.goal_prompt_tes_tts_cap_008_table_list_code_block_oralization
tds_class: roadmap
status: archived
consumer: maintainers, tes-tts maintainers, adapter authors, validation authors, and execution agents
source_of_truth: false
evidence_level: L2
---

# GOAL Prompt: TES TTS CAP-008 Table, List, And Code-Block Oralization

```text
/goal Continue TES TTS conversational rendering.

Canonical artifact:
docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-tes-tts-conversational-rendering.md

Current unit:
CAP-008 Table, List, And Code-Block Oralization

Certified evidence from prior cycle:
- CAP-007 hardened exact islands so only requested fragile spans remain
  literal inside conversational speech.
- CAP-007 added fixtures for selective exact terms, secret redaction over
  exact requests, fragile span classes, and scoped package protection before
  mention rendering.
- CAP-007 kept source text unchanged, `spoken_text` request-local, provider
  claims degraded/deferred, and redaction ahead of speech.
- CAP-007 mirrored converged behavior into Codex and Claude adapter skill
  sources.
- Release identity, sync, provider installs, provider downloads, provider
  certification, durable conversion cache, global config writes, version bump,
  and proactive `speak` behavior remain unauthorized.
- Sync status is REMOTE_SYNC_NOT_REQUESTED.

Task:
Execute only CAP-008 through:
execute -> analyze -> fix -> certify -> create next /goal prompt or close
convergence -> local commit.

Required actions:
1. Run `git status --short --branch --untracked-files=all`.
2. Classify inherited TTS changes and unrelated `.agents/**` drift. Do not
   stage or modify unrelated `.agents/**` changes.
3. Re-read:
   - `docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-tes-tts-conversational-rendering.md`
   - `docs/roadmap/tes-tts/TES-TTS-CAP-007-EXACT-ISLAND-PROTECTED-SPAN-HARDENING.md`
   - `docs/roadmap/tes-tts/TES-TTS-SKILL-ROADMAP.md`
   - `.agents/skills/tes-tts/**`
   - `src/adapters/codex/skills/tes-tts/**`
   - `src/adapters/claude/skills/tes-tts/**`
   - focused TTS fixtures and oracles under `benchmarks/tes-tts/**` and
     `scripts/tes_tts_*_oracle.py`
4. Implement CAP-008 only:
   - improve table, bullet, numbered-list, quote, and code-block oralization;
   - preserve facts and ordering without summarizing user text unless
     explicitly requested;
   - keep code and command spans as text and never actions;
   - preserve protected spans before structural rendering;
   - keep exact islands and secret redaction behavior from CAP-007 intact.
5. Validate the workbench, then mirror converged behavior to Codex and Claude
   adapter skill sources when behavior changes.
6. Analyze the diff for fact preservation, ordering, no-summary behavior,
   code no-execute posture, adapter parity, privacy, and boundary drift.
7. Fix only observed CAP-008 defects.
8. Certify with focused TTS oracles, workbench and adapter quick validation,
   materialization check, TDS/doc-size/reference graph validators,
   `git diff --check`, and package closure only when unrelated drift does not
   make it impossible to interpret.
9. Create the next exact CAP `/goal` prompt before closure unless the
   conversational rendering sequence closes.
10. Update `docs/roadmap/tes-tts/TES-TTS-SKILL-ROADMAP.md` with CAP-008 outcome, next
    prompt pointer, and sync status.
11. Stage only CAP-008 files and commit locally as the final shell action.

Forbidden:
- no sync, release, push, tag, publish, provider install, provider download,
  provider certification, proactive speak behavior, global config writes,
  durable conversion cache, version bump, bundle generation, phoneme output,
  IPA, SSML, lexicon, G2P claim, model bundle, library vendoring, runtime
  dependency import, command execution from spoken content, user-text summary
  without explicit request, provider-backed pronunciation claim, or unrelated
  `.agents/**` changes without explicit current-cycle owner approval.

Stop states:
PASS, DEGRADED, TTS_NOT_AVAILABLE, NEEDS_REVIEW, NEEDS_OWNER_DECISION,
SAFETY_BLOCKED, BLOCKED.

Required closeout:
- changed files;
- focused oracles and result;
- next prompt artifact or closure statement;
- local commit hash;
- sync status: REMOTE_SYNC_NOT_REQUESTED unless explicitly authorized.
```
