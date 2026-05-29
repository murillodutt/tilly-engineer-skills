---
tds_id: roadmap.goal_prompt_tes_tts_lex_001_ptbr_lexical_dataset_manifest
tds_class: roadmap
status: archived
consumer: maintainers, tes-tts maintainers, adapter authors, validation authors, and execution agents
source_of_truth: false
evidence_level: L2
---

# GOAL Prompt: TES TTS LEX-001 PT-BR Lexical Dataset Manifest

```text
/goal Continue TES TTS PT-BR lexical normalization.

Canonical artifact:
docs/roadmap/GOAL-SUPER-SPEC-tes-tts-ptbr-lexical-normalization.md

Current unit:
LEX-001 PT-BR Lexical Dataset Manifest

Certified evidence from prior cycle:
- Conversational rendering CAP-006 through CAP-009 produced useful local
  behavior but exposed a scalability risk: manual pronunciation rules and
  Markdown-shaped fixtures will require broad refactoring soon.
- Local NeMo analysis identified a stronger architecture: dictionary-backed
  lexical lookup, explicit grapheme/pronunciation separation, structured
  manifests, and fallback after lookup.
- `tmp/tts-lib/NeMo/scripts/tts_dataset_files/pt_BR/pt_br_prondict-v1.0.dict`
  is a strong PT-BR pronunciation reference with `WORD<TAB>IPA` shape.
- The maintainer approved focusing on PT-BR first and pivoting toward a
  NeMo-inspired lexical foundation without importing NeMo as a runtime
  dependency.
- Release identity, sync, provider installs, provider downloads, provider
  certification, durable conversion cache, global config writes, version bump,
  IPA runtime output, SSML, phoneme output, and proactive `speak` behavior
  remain unauthorized.
- Sync status is REMOTE_SYNC_NOT_REQUESTED.

Task:
Execute only LEX-001 through:
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
   - `.agents/skills/tes-tts/**`
   - `src/adapters/codex/skills/tes-tts/**`
   - `src/adapters/claude/skills/tes-tts/**`
   - focused TTS fixtures and oracles under `benchmarks/tes-tts/**` and
     `scripts/tes_tts_*_oracle.py`
   - local NeMo reference files needed for PT-BR dictionary format analysis
4. Execute LEX-001 only:
   - define a PT-BR lexical manifest schema;
   - add a Python converter for
     `tmp/tts-lib/NeMo/scripts/tts_dataset_files/pt_BR/pt_br_prondict-v1.0.dict`
     to JSONL/manifest records;
   - create a small PT-BR lexical sample manifest from representative
     dictionary-style entries;
   - include provenance and `usage: evidence_only`;
   - create a dependency-free lexical manifest oracle;
   - keep IPA/pronunciation as evidence metadata only, not runtime output.
5. Analyze the diff for provenance, schema stability, false-green risk,
   runtime claim drift, adapter parity, privacy, and migration pressure.
6. Fix only observed LEX-001 defects.
7. Certify with the converter self-test, lexical oracle, focused TTS oracles,
   workbench and adapter quick validation when skill docs change,
   materialization check, TDS/doc-size reference graph validators,
   `git diff --check`, and package closure only when unrelated drift does not
   make it impossible to interpret.
8. Create the next exact LEX `/goal` prompt before closure unless the lexical
   sequence closes.
9. Update `docs/roadmap/TES-TTS-SKILL-ROADMAP.md` with LEX-001 outcome, next
   prompt pointer, and sync status.
10. Stage only LEX-001 files and commit locally as the final shell action.

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
