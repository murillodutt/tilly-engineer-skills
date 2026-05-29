---
tds_id: roadmap.goal_prompt_tes_tts_tts_003_fixture_schema
tds_class: roadmap
status: active
consumer: maintainers, tes-tts maintainers, execution agents, and release reviewers
source_of_truth: false
evidence_level: L2
---

# GOAL Prompt: TES TTS TTS-003 Fixture Schema

This is the ready `/goal` prompt for the next circular execution cycle of
`tes-tts`.

```text
/goal Continue TES TTS sequential convergence.

Canonical artifact:
docs/roadmap/GOAL-SUPER-SPEC-tes-tts-sequential-convergence.md

Current unit:
TTS-003 Fixture Schema

Certified evidence from prior cycle:
- TTS-002 re-read:
  - `src/adapters/codex/skills/tes-tts/references/language-normalization.md`
  - `src/adapters/claude/skills/tes-tts/references/language-normalization.md`
  - `docs/roadmap/TES-TTS-NORMALIZATION-ARCHITECTURE-SPEC.md`
  - `docs/roadmap/TES-TTS-NORMALIZATION-EXECUTION-SPEC.md`
  - `docs/roadmap/TES-TTS-SKILL-ROADMAP.md`
- TTS-002 confirmed the selector order:
  1. explicit user language;
  2. declared adapter default only when explicitly declared;
  3. current request language;
  4. dominant provided-text language;
  5. preserve original when still unclear.
- TTS-002 added selector fixture candidates DLS-001 through DLS-005 to the
  Codex/Claude language references and execution SPEC.
- TTS-002 recorded that selector decisions are fixture-testable before
  translation, provider probing, pronunciation enrichment, or TTS playback.
- Ready prompt artifact for TTS-003 exists at
  docs/roadmap/GOAL-PROMPT-tes-tts-TTS-003-fixture-schema.md.
- Focused TTS-002 oracles passed:
  - `python3 scripts/validate_tds.py`
  - `python3 scripts/validate_doc_size.py`
  - `python3 scripts/validate_reference_package.py`
  - targeted selector `rg` checks.

Task:
Execute only TTS-003 through the circular sequence:
execute -> analyze -> fix -> certify -> create next /goal prompt -> local commit.

Required actions:
1. Run `git status --short --branch --untracked-files=all`.
2. Re-read:
   - `docs/roadmap/GOAL-SUPER-SPEC-tes-tts-sequential-convergence.md`
   - `docs/roadmap/TES-TTS-NORMALIZATION-EXECUTION-SPEC.md`
   - `docs/roadmap/TES-TTS-SKILL-ROADMAP.md`
   - both `language-normalization.md` references.
3. Define the minimal fixture schema for future TTS normalization fixtures.
   The schema must cover selector, source text, expected target language,
   protected terms, redaction expectation, provider state, and expected status.
4. Do not add the full corpus yet unless the current SPEC explicitly permits
   it after the schema is stable.
5. Certify with targeted `rg` checks and the smallest docs/package oracles.
6. Create the next `/goal` prompt artifact for TTS-004 if TTS-003 is not the
   convergence endpoint.
7. Commit the local execution as the final action of the cycle.

Forbidden:
- no sync, release, push, tag, publish, provider install, provider download,
  proactive speak behavior, global config writes, or durable conversion cache.

Stop states:
BLOCKED, DEGRADED, NEEDS_REVIEW, NEEDS_OWNER_DECISION.
```
