---
tds_id: roadmap.goal_prompt_tes_tts_spec_007_optional_translation_layer
tds_class: roadmap
status: active
consumer: maintainers, tes-tts maintainers, execution agents, and validation authors
source_of_truth: false
evidence_level: L2
---

# GOAL Prompt: TES TTS SPEC-007 Optional Translation Layer

This is the ready `/goal` prompt for the next ten-SPEC `tes-tts` convergence
cycle after SPEC-006.

```text
/goal Continue TES TTS ten-SPEC convergence.

Canonical artifact:
docs/roadmap/GOAL-SUPER-SPEC-tes-tts-ten-spec-convergence.md

Current unit:
SPEC-007 Optional Translation Layer

Certified evidence from prior cycle:
- SPEC-006 selected optional local probe candidates `ftfy`, `Babel`, and
  `Lingua`.
- SPEC-006 classified every provider candidate as selected, deferred,
  degraded, or rejected.
- SPEC-006 recorded license, offline, maintenance, and language-coverage notes
  for every candidate.
- SPEC-006 kept provider use optional and avoided provider install, download,
  bundle, certification, or support claims.
- ADR 0004 remains proposed.
- Release identity and sync remain out of scope.
- No provider install, provider download, real provider certification, global
  config write, durable conversion cache, proactive `speak` behavior, push,
  tag, publish, release, or sync was performed.
- Ready prompt artifact for SPEC-007:
  `docs/roadmap/GOAL-PROMPT-tes-tts-SPEC-007-optional-translation-layer.md`.

Task:
Execute only SPEC-007 through:
execute -> analyze -> fix -> certify -> create next Super SPEC + /goal prompt
or close convergence -> local commit.

Required actions:
1. Run `git status --short --branch --untracked-files=all`.
2. Classify inherited TTS changes and unrelated `.agents/**` drift. Do not
   stage or modify unrelated `.agents/**` changes.
3. Re-read:
   - `docs/roadmap/GOAL-SUPER-SPEC-tes-tts-ten-spec-convergence.md`
   - `docs/roadmap/TES-TTS-SPEC-007-optional-translation-layer.md`
   - `docs/roadmap/TES-TTS-PROVIDER-CANDIDATE-REVIEW.md`
   - `docs/roadmap/TES-TTS-SKILL-ROADMAP.md`
   - `benchmarks/tes-tts/normalization-fixtures.json`
   - `benchmarks/tes-tts/instruction-normalizer-fixtures.json`
   - `scripts/tes_tts_instruction_normalizer_oracle.py`
   - `scripts/tes_tts_fixture_schema_oracle.py`
   - `scripts/tes_tts_provider_probe_oracle.py`
4. Execute SPEC-007 only:
   - define the optional translation boundary without adding a provider
     dependency;
   - require redaction before translation planning;
   - require protected-term extraction before translation planning;
   - keep source text unchanged and translation as speech preparation only;
   - preserve no-summary behavior unless the user explicitly requests summary;
   - keep provider absence or unclear language-pair support as
     `normalization_degraded`;
   - avoid provider install, download, bundle, certification, or support claim.
5. Analyze the diff for quality, efficiency, precision, false-green risk,
   boundary drift, and evidence sufficiency.
6. Fix only observed SPEC-007 defects.
7. Certify with:
   - `python3 scripts/tes_tts_instruction_normalizer_oracle.py --self-test`
   - `python3 scripts/tes_tts_fixture_schema_oracle.py --self-test`
   - `python3 scripts/tes_tts_provider_probe_oracle.py --self-test`
   - `python3 scripts/validate_tds.py`
   - `python3 scripts/validate_doc_size.py`
   - `python3 scripts/validate_reference_graph.py`
   - `git diff --check`
8. Create or update the next `/goal` prompt for SPEC-008 Optional G2P
   Pronunciation Provider Layer before closure.
9. Update `docs/roadmap/TES-TTS-SKILL-ROADMAP.md` with SPEC-007 outcome,
   next prompt pointer, and sync status.
10. Stage only SPEC-007 files and the next prompt artifact.
11. Commit locally as the final shell action for the cycle.

Forbidden:
- no sync, release, push, tag, publish, provider install, provider download,
  provider certification, proactive speak behavior, global config writes,
  durable conversion cache, or unrelated `.agents/**` changes.

Stop states:
PASS, DEGRADED, NEEDS_REVIEW, NEEDS_OWNER_DECISION, BLOCKED.

Required closeout:
- changed files;
- focused oracles and result;
- next prompt artifact;
- local commit hash;
- sync status: REMOTE_SYNC_NOT_REQUESTED unless explicitly authorized.
```
