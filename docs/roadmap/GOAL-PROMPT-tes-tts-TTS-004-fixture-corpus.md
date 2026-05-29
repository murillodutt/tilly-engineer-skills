---
tds_id: roadmap.goal_prompt_tes_tts_tts_004_fixture_corpus
tds_class: roadmap
status: active
consumer: maintainers, tes-tts maintainers, execution agents, and release reviewers
source_of_truth: false
evidence_level: L2
---

# GOAL Prompt: TES TTS TTS-004 Fixture Corpus

This is the ready `/goal` prompt for the next circular execution cycle of
`tes-tts`.

```text
/goal Continue TES TTS sequential convergence.

Canonical artifact:
docs/roadmap/GOAL-SUPER-SPEC-tes-tts-sequential-convergence.md

Current unit:
TTS-004 Fixture Corpus

Certified evidence from prior cycle:
- TTS-003 re-read:
  - `docs/roadmap/GOAL-SUPER-SPEC-tes-tts-sequential-convergence.md`
  - `docs/roadmap/TES-TTS-NORMALIZATION-EXECUTION-SPEC.md`
  - `docs/roadmap/TES-TTS-SKILL-ROADMAP.md`
  - both `language-normalization.md` references.
- TTS-003 defined the minimal fixture schema at:
  - `benchmarks/tes-tts/normalization-fixture.schema.json`
  - `docs/roadmap/TES-TTS-NORMALIZATION-FIXTURE-SCHEMA.md`
- TTS-003 added the focused schema oracle:
  - `python3 scripts/tes_tts_fixture_schema_oracle.py --self-test`
- The schema covers selector inputs, source text, expected target language,
  protected terms, redaction expectation, provider state, expected status, and
  `no_summary: true`.
- Ready prompt artifact for TTS-004 exists at
  docs/roadmap/GOAL-PROMPT-tes-tts-TTS-004-fixture-corpus.md.
- Focused TTS-003 oracles passed:
  - `python3 scripts/tes_tts_fixture_schema_oracle.py --self-test`
  - `python3 scripts/validate_tds.py`
  - `python3 scripts/validate_doc_size.py`
  - `python3 scripts/validate_reference_package.py`
  - targeted schema `rg` checks.

Task:
Execute only TTS-004 through the circular sequence:
execute -> analyze -> fix -> certify -> create next /goal prompt -> local commit.

Required actions:
1. Run `git status --short --branch --untracked-files=all`.
2. Re-read:
   - `docs/roadmap/TES-TTS-NORMALIZATION-FIXTURE-SCHEMA.md`
   - `benchmarks/tes-tts/normalization-fixture.schema.json`
   - `docs/roadmap/TES-TTS-NORMALIZATION-EXECUTION-SPEC.md`
   - `docs/roadmap/TES-TTS-SKILL-ROADMAP.md`
   - both `language-normalization.md` references.
3. Add the minimal corpus entries required by the current SPEC, beginning with
   selector cases `DLS-001` through `DLS-005`.
4. Do not add provider probing, provider installs, downloads, runtime TTS
   behavior, or certification claims.
5. Certify with the schema oracle, targeted `rg` checks, and the smallest
   docs/package oracles.
6. Create the next `/goal` prompt artifact for TTS-005 if TTS-004 is not the
   convergence endpoint.
7. Commit the local execution as the final action of the cycle.

Forbidden:
- no sync, release, push, tag, publish, provider install, provider download,
  proactive speak behavior, global config writes, or durable conversion cache.

Stop states:
BLOCKED, DEGRADED, NEEDS_REVIEW, NEEDS_OWNER_DECISION.
```
