---
tds_id: roadmap.goal_prompt_tes_tts_tts_005_instruction_normalizer_oracle
tds_class: roadmap
status: active
consumer: maintainers, tes-tts maintainers, execution agents, and release reviewers
source_of_truth: false
evidence_level: L2
---

# GOAL Prompt: TES TTS TTS-005 Instruction Normalizer Oracle

This is the ready `/goal` prompt for the next circular execution cycle of
`tes-tts`.

```text
/goal Continue TES TTS sequential convergence.

Canonical artifact:
docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-tes-tts-sequential-convergence.md

Current unit:
TTS-005 Instruction Normalizer Oracle

Certified evidence from prior cycle:
- TTS-004 re-read:
  - `docs/roadmap/tes-tts/TES-TTS-NORMALIZATION-FIXTURE-SCHEMA.md`
  - `benchmarks/tes-tts/normalization-fixture.schema.json`
  - `docs/roadmap/tes-tts/TES-TTS-NORMALIZATION-EXECUTION-SPEC.md`
  - `docs/roadmap/tes-tts/TES-TTS-SKILL-ROADMAP.md`
  - both `language-normalization.md` references.
- TTS-004 added the minimal dependency-free corpus:
  - `benchmarks/tes-tts/normalization-fixtures.json`
- TTS-004 began the corpus with selector cases `tts-dls-001` through
  `tts-dls-005`, corresponding to DLS-001 through DLS-005.
- TTS-004 strengthened the focused schema oracle so it validates both schema
  and corpus shape:
  - `python3 scripts/tes_tts_fixture_schema_oracle.py --self-test`
- Ready prompt artifact for TTS-005 exists at
  docs/roadmap/goals/prompts/tes-tts/GOAL-PROMPT-tes-tts-TTS-005-instruction-normalizer-oracle.md.
- Focused TTS-004 oracles passed:
  - `python3 scripts/tes_tts_fixture_schema_oracle.py --self-test`
  - `python3 scripts/validate_tds.py`
  - `python3 scripts/validate_doc_size.py`
  - `python3 scripts/validate_reference_package.py`
  - targeted corpus `rg` checks.

Task:
Execute only TTS-005 through the circular sequence:
execute -> analyze -> fix -> certify -> create next /goal prompt -> local commit.

Required actions:
1. Run `git status --short --branch --untracked-files=all`.
2. Re-read:
   - `benchmarks/tes-tts/normalization-fixtures.json`
   - `docs/roadmap/tes-tts/TES-TTS-NORMALIZATION-FIXTURE-SCHEMA.md`
   - `docs/roadmap/tes-tts/TES-TTS-NORMALIZATION-EXECUTION-SPEC.md`
   - `docs/roadmap/tes-tts/TES-TTS-SKILL-ROADMAP.md`
   - both `language-normalization.md` references.
3. Prove instruction-level behavior before provider work:
   - conversion cache shape exists without disk writes;
   - protected terms survive translation planning;
   - secret-like values are redacted before provider or TTS;
   - long text is chunked without summarizing unless requested.
4. Do not add provider probing, provider installs, downloads, runtime TTS
   behavior, or certification claims.
5. Certify with focused self-test/oracle coverage, targeted `rg` checks, and
   the smallest docs/package oracles.
6. Create the next `/goal` prompt artifact for TTS-006 if TTS-005 is not the
   convergence endpoint.
7. Commit the local execution as the final action of the cycle.

Forbidden:
- no sync, release, push, tag, publish, provider install, provider download,
  proactive speak behavior, global config writes, or durable conversion cache.

Stop states:
BLOCKED, DEGRADED, NEEDS_REVIEW, NEEDS_OWNER_DECISION.
```
