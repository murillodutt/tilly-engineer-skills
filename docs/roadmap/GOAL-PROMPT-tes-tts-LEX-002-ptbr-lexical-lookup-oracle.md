---
tds_id: roadmap.goal_prompt_tes_tts_lex_002_ptbr_lexical_lookup_oracle
tds_class: roadmap
status: archived
consumer: maintainers, tes-tts maintainers, adapter authors, validation authors, and execution agents
source_of_truth: false
evidence_level: L2
---

# GOAL Prompt: TES TTS LEX-002 PT-BR Lexical Lookup Oracle

```text
/goal Continue TES TTS PT-BR lexical normalization.

Canonical artifact:
docs/roadmap/GOAL-SUPER-SPEC-tes-tts-ptbr-lexical-normalization.md

Current unit:
LEX-002 PT-BR Lexical Lookup Oracle

Certified evidence from prior cycle:
- LEX-001 created the PT-BR lexical manifest schema at
  `benchmarks/tes-tts/ptbr-lexical-manifest.schema.json`.
- LEX-001 created the governed sample manifest at
  `benchmarks/tes-tts/ptbr-lexical-sample.jsonl`.
- LEX-001 added the dependency-free prondict converter
  `scripts/tes_tts_ptbr_prondict_to_manifest.py`.
- LEX-001 added the dependency-free lexical manifest oracle
  `scripts/tes_tts_ptbr_lexical_manifest_oracle.py`.
- LEX-001 preserved pronunciation and IPA as evidence metadata only.
- No full dictionary vendoring, runtime dependency import, IPA/phoneme/SSML
  runtime output, provider-backed pronunciation claim, release, sync, push,
  tag, publish, provider install, or provider download was performed.
- Sync status is REMOTE_SYNC_NOT_REQUESTED.

Task:
Execute only LEX-002 through:
execute -> analyze -> fix -> certify -> create next /goal prompt or close
convergence -> local commit.

Required actions:
1. Run `git status --short --branch --untracked-files=all`.
2. Classify inherited TTS changes and unrelated `.agents/**` drift. Do not
   stage or modify unrelated `.agents/**` changes.
3. Re-read:
   - `docs/roadmap/GOAL-SUPER-SPEC-tes-tts-ptbr-lexical-normalization.md`
   - `docs/roadmap/TES-TTS-LEX-001-PTBR-LEXICAL-DATASET-MANIFEST.md`
   - `docs/roadmap/TES-TTS-SKILL-ROADMAP.md`
   - `benchmarks/tes-tts/ptbr-lexical-manifest.schema.json`
   - `benchmarks/tes-tts/ptbr-lexical-sample.jsonl`
   - `scripts/tes_tts_ptbr_prondict_to_manifest.py`
   - `scripts/tes_tts_ptbr_lexical_manifest_oracle.py`
   - focused TTS fixtures and oracles under `benchmarks/tes-tts/**` and
     `scripts/tes_tts_*_oracle.py`
4. Execute LEX-002 only:
   - add a dependency-free lexical lookup helper or oracle over the governed
     PT-BR sample manifest;
   - prove exact grapheme lookup, case handling, accented graphemes,
     hyphenated graphemes, and OOV/degraded behavior;
   - keep lookup output as evidence metadata, not runtime IPA/phoneme/SSML
     speech output;
   - keep source text unchanged and keep any future `spoken_text`
     integration out of scope for this unit.
5. Analyze the diff for lookup determinism, false-green risk, provenance,
   runtime claim drift, adapter parity, privacy, and migration pressure.
6. Fix only observed LEX-002 defects.
7. Certify with the lexical manifest oracle, new lookup oracle, focused TTS
   oracles, materialization check, TDS/doc-size/reference graph validators,
   `git diff --check`, and package closure only when unrelated drift does not
   make it impossible to interpret.
8. Create the next exact LEX `/goal` prompt before closure unless the lexical
   sequence closes.
9. Update `docs/roadmap/TES-TTS-SKILL-ROADMAP.md` with LEX-002 outcome, next
   prompt pointer, and sync status.
10. Stage only LEX-002 files and commit locally as the final shell action.

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
