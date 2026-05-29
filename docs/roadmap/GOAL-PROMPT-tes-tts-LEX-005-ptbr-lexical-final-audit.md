---
tds_id: roadmap.goal_prompt_tes_tts_lex_005_ptbr_lexical_final_audit
tds_class: roadmap
status: active
consumer: maintainers, tes-tts maintainers, adapter authors, validation authors, and execution agents
source_of_truth: false
evidence_level: L2
---

# GOAL Prompt: TES TTS LEX-005 PT-BR Lexical Final Audit

```text
/goal Continue TES TTS PT-BR lexical normalization.

Canonical artifact:
docs/roadmap/GOAL-SUPER-SPEC-tes-tts-ptbr-lexical-normalization.md

Current unit:
LEX-005 PT-BR Lexical Final Audit

Certified evidence from prior cycle:
- LEX-001 created the PT-BR lexical manifest schema, sample JSONL, prondict
  converter, and lexical manifest oracle.
- LEX-002 added dependency-free lexical lookup fixtures and oracle coverage.
- LEX-003 defined the request-local lexical evidence boundary across
  workbench, Codex, and Claude references.
- LEX-004 migrated a representative slice of Markdown-shaped pronunciation
  guidance into `benchmarks/tes-tts/pronunciation-catalog-fixtures.json`.
- LEX-004 added `scripts/tes_tts_pronunciation_catalog_oracle.py`.
- The migrated catalog keeps `usage: evidence_only`, `runtime_output: false`,
  exact-read raw preservation, and `runtime_claim: none`.
- No legacy fixture deletion, full dictionary vendoring, runtime dependency
  import, provider-backed pronunciation claim, release, sync, push, tag,
  publish, provider install, or provider download was performed.
- Sync status is REMOTE_SYNC_NOT_REQUESTED.

Task:
Execute only LEX-005 through:
execute -> analyze -> fix -> certify -> close convergence or create exact next
/goal prompt -> local commit.

Required actions:
1. Run `git status --short --branch --untracked-files=all`.
2. Classify inherited TTS changes and unrelated `.agents/**` drift. Do not
   stage or modify unrelated `.agents/**` changes.
3. Re-read:
   - `docs/roadmap/GOAL-SUPER-SPEC-tes-tts-ptbr-lexical-normalization.md`
   - `docs/roadmap/TES-TTS-LEX-001-PTBR-LEXICAL-DATASET-MANIFEST.md`
   - `docs/roadmap/TES-TTS-LEX-002-PTBR-LEXICAL-LOOKUP-ORACLE.md`
   - `docs/roadmap/TES-TTS-LEX-003-SPOKEN-RENDERING-INTEGRATION-BOUNDARY.md`
   - `docs/roadmap/TES-TTS-LEX-004-FIXTURE-MIGRATION-FROM-MARKDOWN-SHAPED-TTS-CASES.md`
   - `docs/roadmap/TES-TTS-SKILL-ROADMAP.md`
   - `benchmarks/tes-tts/**`
   - `scripts/tes_tts_*_oracle.py`
   - `.agents/skills/tes-tts/**`
   - `src/adapters/codex/skills/tes-tts/**`
   - `src/adapters/claude/skills/tes-tts/**`
4. Execute LEX-005 only:
   - audit the PT-BR lexical foundation end to end;
   - confirm what is complete, degraded, deferred, and unauthorized;
   - confirm no source mutation, no user-text summary, no command execution,
     no secret leak, no runtime IPA/phoneme/SSML output, and no
     provider-backed pronunciation claim;
   - decide whether the PT-BR lexical sequence closes locally or needs an exact
     follow-up prompt.
5. Analyze the diff for audit completeness, false-green risk, privacy,
   adapter parity, release/sync boundary drift, and migration pressure.
6. Fix only observed LEX-005 defects.
7. Certify with all lexical oracles, focused TTS oracles, workbench/adapter
   quick validation when skill docs change, materialization check,
   TDS/doc-size/reference graph validators, `git diff --check`, and package
   closure only when unrelated drift does not make it impossible to interpret.
8. Update `docs/roadmap/TES-TTS-SKILL-ROADMAP.md` with LEX-005 outcome,
   closure state or next prompt pointer, and sync status.
9. Stage only LEX-005 files and commit locally as the final shell action.

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
