---
tds_id: roadmap.goal_prompt_tes_tts_lex_003_spoken_rendering_integration_boundary
tds_class: roadmap
status: active
consumer: maintainers, tes-tts maintainers, adapter authors, validation authors, and execution agents
source_of_truth: false
evidence_level: L2
---

# GOAL Prompt: TES TTS LEX-003 Spoken-Rendering Integration Boundary

```text
/goal Continue TES TTS PT-BR lexical normalization.

Canonical artifact:
docs/roadmap/GOAL-SUPER-SPEC-tes-tts-ptbr-lexical-normalization.md

Current unit:
LEX-003 Spoken-Rendering Integration Boundary

Certified evidence from prior cycle:
- LEX-001 created the PT-BR lexical manifest schema, sample JSONL, prondict
  converter, and lexical manifest oracle.
- LEX-002 added dependency-free lookup fixtures at
  `benchmarks/tes-tts/ptbr-lexical-lookup-fixtures.json`.
- LEX-002 added the lookup oracle
  `scripts/tes_tts_ptbr_lexical_lookup_oracle.py`.
- LEX-002 proved exact lookup, casefold lookup, accented and hyphenated
  graphemes, governed degraded OOV fixtures, and unknown OOV fallback.
- Lookup output remains `usage: evidence_only`, preserves source queries, and
  reports `runtime_output: false`.
- No full dictionary vendoring, runtime dependency import, IPA/phoneme/SSML
  runtime output, provider-backed pronunciation claim, release, sync, push,
  tag, publish, provider install, or provider download was performed.
- Sync status is REMOTE_SYNC_NOT_REQUESTED.

Task:
Execute only LEX-003 through:
execute -> analyze -> fix -> certify -> create next /goal prompt or close
convergence -> local commit.

Required actions:
1. Run `git status --short --branch --untracked-files=all`.
2. Classify inherited TTS changes and unrelated `.agents/**` drift. Do not
   stage or modify unrelated `.agents/**` changes.
3. Re-read:
   - `docs/roadmap/GOAL-SUPER-SPEC-tes-tts-ptbr-lexical-normalization.md`
   - `docs/roadmap/TES-TTS-LEX-002-PTBR-LEXICAL-LOOKUP-ORACLE.md`
   - `docs/roadmap/TES-TTS-SKILL-ROADMAP.md`
   - `benchmarks/tes-tts/ptbr-lexical-sample.jsonl`
   - `benchmarks/tes-tts/ptbr-lexical-lookup-fixtures.json`
   - `scripts/tes_tts_ptbr_lexical_lookup_oracle.py`
   - `.agents/skills/tes-tts/**`
   - `src/adapters/codex/skills/tes-tts/**`
   - `src/adapters/claude/skills/tes-tts/**`
4. Execute LEX-003 only:
   - define the boundary for attaching PT-BR lexical evidence to request-local
     speech preparation;
   - preserve immutable `source_text`;
   - keep `spoken_text` request-local;
   - keep IPA/pronunciation evidence out of runtime speech output unless a
     later explicitly approved surface allows it;
   - preserve secret redaction, exact islands, no-summary behavior, code
     no-execute posture, and provider-absence degradation.
5. Analyze the diff for source immutability, runtime claim drift, no-summary
   behavior, privacy, adapter parity, and migration pressure.
6. Fix only observed LEX-003 defects.
7. Certify with lexical oracles, focused TTS oracles, workbench/adapter quick
   validation when skill docs change, materialization check, TDS/doc-size
   reference graph validators, `git diff --check`, and package closure only
   when unrelated drift does not make it impossible to interpret.
8. Create the next exact LEX `/goal` prompt before closure unless the lexical
   sequence closes.
9. Update `docs/roadmap/TES-TTS-SKILL-ROADMAP.md` with LEX-003 outcome, next
   prompt pointer, and sync status.
10. Stage only LEX-003 files and commit locally as the final shell action.

Forbidden:
- no sync, release, push, tag, publish, provider install, provider download,
  provider certification, proactive speak behavior, global config writes,
  durable conversion cache, version bump, bundle generation, full dictionary
  vendoring, runtime dependency import, command execution from spoken content,
  user-text summary without explicit request, IPA/phoneme/SSML runtime output,
  provider-backed pronunciation claim, or unrelated `.agents/**` changes
  without explicit current-cycle owner approval.

Stop states:
PASS, DEGRADED, NEEDS_REVIEW, NEEDS_OWNER_DECISION, SAFETY_BLOCKED, BLOCKED.

Required closeout:
- changed files;
- focused oracles and result;
- next prompt artifact or closure statement;
- local commit hash;
- sync status: REMOTE_SYNC_NOT_REQUESTED unless explicitly authorized.
```
