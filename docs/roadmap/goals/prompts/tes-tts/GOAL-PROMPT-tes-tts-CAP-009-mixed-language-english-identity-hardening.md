---
tds_id: roadmap.goal_prompt_tes_tts_cap_009_mixed_language_english_identity_hardening
tds_class: roadmap
status: archived
consumer: maintainers, tes-tts maintainers, adapter authors, validation authors, and execution agents
source_of_truth: false
evidence_level: L2
---

# GOAL Prompt: TES TTS CAP-009 Mixed-Language And English Identity Hardening

```text
/goal Continue TES TTS conversational rendering.

Canonical artifact:
docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-tes-tts-conversational-rendering.md

Current unit:
CAP-009 Mixed-Language And English Identity Hardening

Certified evidence from prior cycle:
- CAP-008 improved table, bullet, numbered-list, quote, and code-block
  oralization.
- CAP-008 added fixtures for multi-column table facts, mixed list ordering,
  quote oralization, conversational code-block no-execute behavior, and
  preservation of exact islands plus secret redaction through structural
  rendering.
- CAP-008 kept source text unchanged, `spoken_text` request-local, provider
  claims degraded/deferred, and redaction ahead of speech.
- CAP-008 mirrored converged behavior into Codex and Claude adapter skill
  sources.
- Release identity, sync, provider installs, provider downloads, provider
  certification, durable conversion cache, global config writes, version bump,
  and proactive `speak` behavior remain unauthorized.
- Sync status is REMOTE_SYNC_NOT_REQUESTED.

Task:
Execute only CAP-009 through:
execute -> analyze -> fix -> certify -> create next /goal prompt or close
convergence -> local commit.

Required actions:
1. Run `git status --short --branch --untracked-files=all`.
2. Classify inherited TTS changes and unrelated `.agents/**` drift. Do not
   stage or modify unrelated `.agents/**` changes.
3. Re-read:
   - `docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-tes-tts-conversational-rendering.md`
   - `docs/roadmap/tes-tts/TES-TTS-CAP-008-TABLE-LIST-CODE-BLOCK-ORALIZATION.md`
   - `docs/roadmap/tes-tts/TES-TTS-SKILL-ROADMAP.md`
   - `.agents/skills/tes-tts/**`
   - `src/adapters/codex/skills/tes-tts/**`
   - `src/adapters/claude/skills/tes-tts/**`
   - focused TTS fixtures and oracles under `benchmarks/tes-tts/**` and
     `scripts/tes_tts_*_oracle.py`
4. Implement CAP-009 only:
   - harden mixed-language speech so PT-BR platform narration keeps protected
     English, proper-noun, product, package, model, command, code identifier,
     and workflow terms un-translated;
   - enrich fixture-backed protected identity for common English terms used in
     TES sessions;
   - preserve exact islands, secret redaction, no-summary behavior, and
     CAP-008 structural oralization;
   - keep pronunciation as instruction-level intent only, without IPA, SSML,
     phoneme, lexicon, G2P, or provider-backed claims.
5. Validate the workbench, then mirror converged behavior to Codex and Claude
   adapter skill sources when behavior changes.
6. Analyze the diff for protected identity, translation drift, fact
   preservation, no-summary behavior, adapter parity, privacy, and boundary
   drift.
7. Fix only observed CAP-009 defects.
8. Certify with focused TTS oracles, workbench and adapter quick validation,
   materialization check, TDS/doc-size/reference graph validators,
   `git diff --check`, and package closure only when unrelated drift does not
   make it impossible to interpret.
9. Create the next exact CAP `/goal` prompt before closure unless the
   conversational rendering sequence closes.
10. Update `docs/roadmap/tes-tts/TES-TTS-SKILL-ROADMAP.md` with CAP-009 outcome, next
    prompt pointer, and sync status.
11. Stage only CAP-009 files and commit locally as the final shell action.

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
