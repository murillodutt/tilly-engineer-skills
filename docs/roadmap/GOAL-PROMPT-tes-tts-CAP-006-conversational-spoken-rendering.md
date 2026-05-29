---
tds_id: roadmap.goal_prompt_tes_tts_cap_006_conversational_spoken_rendering
tds_class: roadmap
status: archived
consumer: maintainers, tes-tts maintainers, adapter authors, validation authors, and execution agents
source_of_truth: false
evidence_level: L2
---

# GOAL Prompt: TES TTS CAP-006 Conversational Spoken Rendering

```text
/goal Continue TES TTS conversational rendering.

Canonical artifact:
docs/roadmap/GOAL-SUPER-SPEC-tes-tts-conversational-rendering.md

Current unit:
CAP-006 Conversational Spoken Rendering

Certified evidence from prior cycle:
- CAP-005 closed the previous local capability migration sequence.
- ADR 0004 is active as the pronunciation normalization and enrichment
  boundary.
- OWNER-001 authorized architectural evolution and migration of portable
  capabilities from mapped TTS references.
- The active development and test workbench is `.agents/skills/tes-tts`;
  converged behavior is mirrored into `src/adapters/codex/skills/tes-tts`
  after local validation.
- A post-CAP live TTS test showed that voice and rate are good, but speech
  quality depends on better distinction between conversational prose,
  faithful reading, exact islands, and protected English/technical identity.
- The prior English protected-term enrichment added instruction-level hints
  for proper nouns and engineering workflow terms without claiming
  provider-backed pronunciation.
- Local research under `tmp/tts-lib/` supports a dependency-free architecture:
  protect/redact spans first, classify block shape and intent, derive
  request-local `spoken_rendering`, and then send only the final speech text to
  TTS.
- Release identity, sync, provider installs, provider downloads, provider
  certification, durable conversion cache, global config writes, and proactive
  `speak` behavior remain unauthorized.
- Sync status is REMOTE_SYNC_NOT_REQUESTED.

Task:
Execute only CAP-006 through:
execute -> analyze -> fix -> certify -> create next /goal prompt or close
convergence -> local commit.

Required actions:
1. Run `git status --short --branch --untracked-files=all`.
2. Classify inherited TTS changes and unrelated `.agents/**` drift. Do not
   stage or modify unrelated `.agents/**` changes.
3. Re-read:
   - `docs/roadmap/GOAL-SUPER-SPEC-tes-tts-conversational-rendering.md`
   - `docs/roadmap/TES-TTS-CAP-006-CONVERSATIONAL-SPOKEN-RENDERING.md`
   - `docs/roadmap/TES-TTS-SKILL-ROADMAP.md`
   - `docs/roadmap/TES-TTS-CAP-005-FINAL-LOCAL-AUDIT.md`
   - `docs/adr/0004-tes-tts-pronunciation-normalization-and-enrichment.md`
   - `.agents/skills/tes-tts/**`
   - `src/adapters/codex/skills/tes-tts/**`
   - `src/adapters/claude/skills/tes-tts/**`
   - focused TTS fixtures and oracles under `benchmarks/tes-tts/**` and
     `scripts/tes_tts_*_oracle.py`
4. Implement CAP-006 only:
   - introduce a tested rendering intent boundary between `conversational` and
     `faithful_reading`;
   - add fixture coverage for CAP-006 required cases before claiming behavior;
   - keep source text unchanged and keep `spoken_text` request-local;
   - protect/redact fragile spans before conversational rendering;
   - preserve PT-BR as platform narration while keeping English/proper/
     technical terms un-translated with pronunciation intent;
   - preserve exact path, URL, command, code, hash, and quoted-term islands
     when requested;
   - make secret redaction override exact/verbatim/raw/literal requests;
   - ensure code blocks are spoken as text and never executed;
   - do not summarize user text unless the user explicitly requested summary.
5. Validate the runtime workbench, then mirror converged behavior to
   `src/adapters/codex/skills/tes-tts`. Mirror to Claude when behavior change
   must be package-parity visible.
6. Analyze the diff for quality, efficiency, precision, false-green risk,
   adapter parity, privacy, no-summary behavior, protected identity, and
   boundary drift.
7. Fix only observed CAP-006 defects.
8. Certify with the smallest relevant TTS oracles, workbench and adapter quick
   validation, materialization check, TDS/doc-size/reference graph validators,
   `git diff --check`, and package closure only when unrelated drift does not
   make it impossible to interpret.
9. Create the next exact CAP `/goal` prompt before closure unless CAP-006
   closes this conversational rendering sequence.
10. Update `docs/roadmap/TES-TTS-SKILL-ROADMAP.md` with CAP-006 outcome, next
    prompt pointer, and sync status.
11. Stage only CAP-006 files and commit locally as the final shell action.

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
