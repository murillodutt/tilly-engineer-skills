---
tds_id: roadmap.goal_prompt_tes_tts_lex_004_fixture_migration_from_markdown_shaped_tts_cases
tds_class: roadmap
status: archived
consumer: maintainers, tes-tts maintainers, adapter authors, validation authors, and execution agents
source_of_truth: false
evidence_level: L2
---

# GOAL Prompt: TES TTS LEX-004 Fixture Migration From Markdown-Shaped TTS Cases

```text
/goal Continue TES TTS PT-BR lexical normalization.

Canonical artifact:
docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-tes-tts-ptbr-lexical-normalization.md

Current unit:
LEX-004 Fixture Migration From Markdown-Shaped TTS Cases

Certified evidence from prior cycle:
- LEX-001 created the PT-BR lexical manifest schema, sample JSONL, prondict
  converter, and lexical manifest oracle.
- LEX-002 added dependency-free lexical lookup fixtures and oracle coverage.
- LEX-003 added PT-BR lexical integration fixtures and the oracle
  `scripts/tes_tts_ptbr_lexical_integration_oracle.py`.
- LEX-003 updated `.agents`, Codex, and Claude `tes-tts`
  `references/language-normalization.md` with the lexical evidence boundary.
- LEX-003 proved source immutability, request-local `spoken_text`, evidence as
  `usage: evidence_only`, secret redaction before speech, code no-execute
  posture, no-summary behavior, provider absence degradation, and no IPA,
  phoneme, or SSML runtime output.
- No full dictionary vendoring, runtime dependency import, provider-backed
  pronunciation claim, release, sync, push, tag, publish, provider install, or
  provider download was performed.
- Sync status is REMOTE_SYNC_NOT_REQUESTED.

Task:
Execute only LEX-004 through:
execute -> analyze -> fix -> certify -> create next /goal prompt or close
convergence -> local commit.

Required actions:
1. Run `git status --short --branch --untracked-files=all`.
2. Classify inherited TTS changes and unrelated `.agents/**` drift. Do not
   stage or modify unrelated `.agents/**` changes.
3. Re-read:
   - `docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-tes-tts-ptbr-lexical-normalization.md`
   - `docs/roadmap/tes-tts/TES-TTS-LEX-003-SPOKEN-RENDERING-INTEGRATION-BOUNDARY.md`
   - `docs/roadmap/tes-tts/TES-TTS-SKILL-ROADMAP.md`
   - `benchmarks/tes-tts/**`
   - `scripts/tes_tts_*_oracle.py`
   - `.agents/skills/tes-tts/**`
   - `src/adapters/codex/skills/tes-tts/**`
   - `src/adapters/claude/skills/tes-tts/**`
4. Execute LEX-004 only:
   - identify Markdown-shaped TTS pronunciation evidence that should move
     toward JSON/JSONL lexical manifests;
   - add or migrate the smallest representative fixture set without deleting
     still-used legacy fixtures;
   - preserve existing normalizer and provider oracles;
   - keep source text immutable, `spoken_text` request-local, and lexical
     evidence metadata-only;
   - do not introduce runtime IPA/phoneme/SSML output or provider-backed
     pronunciation claims.
5. Analyze the diff for fixture stability, false-green risk, source
   immutability, no-summary behavior, privacy, adapter parity, and migration
   pressure.
6. Fix only observed LEX-004 defects.
7. Certify with lexical oracles, focused TTS oracles, workbench/adapter quick
   validation when skill docs change, materialization check, TDS/doc-size
   reference graph validators, `git diff --check`, and package closure only
   when unrelated drift does not make it impossible to interpret.
8. Create the next exact LEX `/goal` prompt before closure unless the lexical
   sequence closes.
9. Update `docs/roadmap/tes-tts/TES-TTS-SKILL-ROADMAP.md` with LEX-004 outcome, next
   prompt pointer, and sync status.
10. Stage only LEX-004 files and commit locally as the final shell action.

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
