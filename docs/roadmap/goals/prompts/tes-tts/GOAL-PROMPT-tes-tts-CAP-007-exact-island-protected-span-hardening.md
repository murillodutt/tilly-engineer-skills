---
tds_id: roadmap.goal_prompt_tes_tts_cap_007_exact_island_protected_span_hardening
tds_class: roadmap
status: archived
consumer: maintainers, tes-tts maintainers, adapter authors, validation authors, and execution agents
source_of_truth: false
evidence_level: L2
---

# GOAL Prompt: TES TTS CAP-007 Exact-Island And Protected-Span Hardening

```text
/goal Continue TES TTS conversational rendering.

Canonical artifact:
docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-tes-tts-conversational-rendering.md

Current unit:
CAP-007 Exact-Island And Protected-Span Hardening

Certified evidence from prior cycle:
- CAP-006 introduced a tested rendering intent boundary between
  `conversational` and `faithful_reading`.
- CAP-006 added eight required conversational fixtures:
  `tts-cap006-interlocutor-oral-prose-ptbr`,
  `tts-cap006-faithful-reading-markdown`,
  `tts-cap006-exact-path-url-code-islands`,
  `tts-cap006-ptbr-default-english-protected-terms`,
  `tts-cap006-no-summary-long-operational-note`,
  `tts-cap006-code-block-faithful-no-execute`,
  `tts-cap006-table-to-prose-no-loss`, and
  `tts-cap006-secret-redaction-beats-exact`.
- CAP-006 kept source text unchanged, `spoken_text` request-local, provider
  claims degraded/deferred, and redaction ahead of speech.
- CAP-006 updated the workbench and adapter skill contracts to document
  conversational vs faithful reading.
- Release identity, sync, provider installs, provider downloads, provider
  certification, durable conversion cache, global config writes, version bump,
  and proactive `speak` behavior remain unauthorized.
- Sync status is REMOTE_SYNC_NOT_REQUESTED.

Task:
Execute only CAP-007 through:
execute -> analyze -> fix -> certify -> create next /goal prompt or close
convergence -> local commit.

Required actions:
1. Run `git status --short --branch --untracked-files=all`.
2. Classify inherited TTS changes and unrelated `.agents/**` drift. Do not
   stage or modify unrelated `.agents/**` changes.
3. Re-read:
   - `docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-tes-tts-conversational-rendering.md`
   - `docs/roadmap/tes-tts/TES-TTS-CAP-006-CONVERSATIONAL-SPOKEN-RENDERING.md`
   - `docs/roadmap/tes-tts/TES-TTS-SKILL-ROADMAP.md`
   - `.agents/skills/tes-tts/**`
   - `src/adapters/codex/skills/tes-tts/**`
   - `src/adapters/claude/skills/tes-tts/**`
   - focused TTS fixtures and oracles under `benchmarks/tes-tts/**` and
     `scripts/tes_tts_*_oracle.py`
4. Implement CAP-007 only:
   - harden exact islands so only the requested fragile spans remain literal
     inside conversational speech;
   - keep secret redaction stronger than any exact/literal/raw/verbatim cue;
   - protect paths, URLs, commands, code identifiers, hashes, GUIDs, emails,
     IPs, mentions, hashtags, branch names, model names, and package names
     before conversational rendering;
   - preserve protected English/proper/technical identity without translating
     it into platform-language approximations;
   - keep code and command spans as text, never actions.
5. Validate the workbench, then mirror converged behavior to Codex and Claude
   adapter skill sources when behavior changes.
6. Analyze the diff for exact-span precision, false positives, no-summary
   preservation, privacy, adapter parity, and boundary drift.
7. Fix only observed CAP-007 defects.
8. Certify with focused TTS oracles, workbench and adapter quick validation,
   materialization check, TDS/doc-size/reference graph validators,
   `git diff --check`, and package closure only when unrelated drift does not
   make it impossible to interpret.
9. Create the next exact CAP `/goal` prompt before closure unless the
   conversational rendering sequence closes.
10. Update `docs/roadmap/tes-tts/TES-TTS-SKILL-ROADMAP.md` with CAP-007 outcome, next
    prompt pointer, and sync status.
11. Stage only CAP-007 files and commit locally as the final shell action.

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
