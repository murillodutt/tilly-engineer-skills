---
tds_id: roadmap.goal_prompt_tes_tts_rte_001_compiled_lexical_index_contract
tds_class: roadmap
status: archived
consumer: maintainers, tes-tts maintainers, adapter authors, validation authors, and execution agents
source_of_truth: false
evidence_level: L2
---

# GOAL Prompt: TES TTS RTE-001 Compiled Lexical Index Contract

```text
/goal Continue TES TTS lexical runtime engine and latency reduction.

Canonical artifact:
docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-tes-tts-lexical-runtime-engine-latency-reduction.md

Current unit:
RTE-001 Compiled Lexical Index Contract

Certified evidence from prior cycle:
- RTE-000 added dependency-free latency fixtures at
  `benchmarks/tes-tts/runtime-latency-fixtures.json`.
- RTE-000 added `scripts/tes_tts_runtime_latency_oracle.py`.
- RTE-000 measures TES text preparation separately from provider/playback
  timing and keeps provider timing `out_of_scope`.
- RTE-000 proved source immutability, no summary behavior, secret redaction,
  code no-execute posture, no runtime IPA/phoneme/SSML/PLS output, and no
  provider-backed pronunciation claim for baseline fixtures.
- Release identity, sync, provider installs, provider downloads, provider
  certification, durable conversion cache, global config writes, version bump,
  full dictionary vendoring, and proactive `speak` behavior remain
  unauthorized.
- Sync status is REMOTE_SYNC_NOT_REQUESTED.

Task:
Execute only RTE-001 through:
execute -> analyze -> fix -> certify -> create next /goal prompt -> local
commit.

Required actions:
1. Run `git status --short --branch --untracked-files=all`.
2. Classify inherited TTS changes and unrelated `.agents/**` drift. Do not
   stage or modify unrelated `.agents/**` changes.
3. Re-read:
   - `docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-tes-tts-lexical-runtime-engine-latency-reduction.md`
   - `benchmarks/tes-tts/runtime-latency-fixtures.json`
   - `benchmarks/tes-tts/ptbr-lexical-sample.jsonl`
   - `benchmarks/tes-tts/pronunciation-catalog-fixtures.json`
   - `scripts/tes_tts_runtime_latency_oracle.py`
   - `scripts/tes_tts_ptbr_lexical_lookup_oracle.py`
   - `scripts/tes_tts_pronunciation_catalog_oracle.py`
4. Execute RTE-001 only:
   - add a dependency-free compiled lexical index helper or oracle over the
     governed fixture data;
   - compile exact single-token entries and phrase/protected-term entries into
     deterministic in-memory structures;
   - prove lookup order, duplicate handling, priority handling, locale
     boundary, and OOV/degraded behavior;
   - keep JSON/JSONL as canonical source and do not emit IPA, phoneme, SSML,
     PLS, provider lexicon, G2P, or provider-backed pronunciation output;
   - do not optimize production runtime beyond the index contract in this
     unit.
5. Analyze the diff for performance direction, false-green risk, privacy,
   adapter parity, no-summary behavior, release/sync boundary drift, and
   evidence quality.
6. Fix only observed RTE-001 defects.
7. Certify with the new index oracle, runtime latency oracle, lexical oracles,
   focused TTS oracles, materialization check, TDS/doc-size/reference graph
   validators, `git diff --check`, and package closure only when unrelated
   drift does not make it impossible to interpret.
8. Create the next exact RTE `/goal` prompt before closure.
9. Update `docs/roadmap/tes-tts/TES-TTS-SKILL-ROADMAP.md` with RTE-001 outcome, next
   prompt pointer, and sync status.
10. Stage only RTE-001 files and commit locally as the final shell action.

Forbidden:
- no sync, release, push, tag, publish, provider install, provider download,
  provider certification, proactive speak behavior, global config writes,
  durable conversion cache, version bump, bundle generation, full dictionary
  vendoring, runtime dependency import, command execution from spoken content,
  user-text summary without explicit request, IPA/phoneme/SSML/PLS runtime
  output, provider-backed pronunciation claim, G2P claim, or unrelated
  `.agents/**` changes without explicit current-cycle owner approval.

Stop states:
PASS, DEGRADED, PERFORMANCE_REGRESSION, NEEDS_REVIEW, NEEDS_OWNER_DECISION,
SAFETY_BLOCKED, BLOCKED.

Required closeout:
- changed files;
- focused oracles and result;
- next prompt artifact;
- local commit hash;
- sync status: REMOTE_SYNC_NOT_REQUESTED unless explicitly authorized.
```
