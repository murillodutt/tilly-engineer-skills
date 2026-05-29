---
tds_id: roadmap.goal_prompt_tes_tts_tts_007_provider_candidate_review
tds_class: roadmap
status: active
consumer: maintainers, tes-tts maintainers, execution agents, and release reviewers
source_of_truth: false
evidence_level: L2
---

# GOAL Prompt: TES TTS TTS-007 Provider Candidate Review

This is the ready `/goal` prompt for the next circular execution cycle of
`tes-tts`.

```text
/goal Continue TES TTS sequential convergence.

Canonical artifact:
docs/roadmap/GOAL-SUPER-SPEC-tes-tts-sequential-convergence.md

Current unit:
TTS-007 Provider Candidate Review

Certified evidence from prior cycle:
- TTS-006 re-read:
  - `docs/roadmap/TES-TTS-NORMALIZATION-EXECUTION-SPEC.md`
  - `docs/roadmap/TES-TTS-SKILL-ROADMAP.md`
  - `docs/roadmap/GOAL-SUPER-SPEC-tes-tts-sequential-convergence.md`
  - `src/adapters/*/skills/tes-tts/references/providers-and-fallbacks.md`
  - `scripts/tes_tts_instruction_normalizer_oracle.py`
- TTS-006 added mocked provider probe fixtures:
  - `benchmarks/tes-tts/provider-probe-fixtures.json`
- TTS-006 added the focused mocked provider probe oracle:
  - `python3 scripts/tes_tts_provider_probe_oracle.py --self-test`
- TTS-006 covered `provider_available`, `provider_not_available`, and
  `provider_needs_review` without probing real providers, package managers,
  network calls, downloads, global config writes, or provider certification.
- Ready prompt artifact for TTS-007 exists at
  docs/roadmap/GOAL-PROMPT-tes-tts-TTS-007-provider-candidate-review.md.
- Focused TTS-006 oracles passed:
  - `python3 scripts/tes_tts_provider_probe_oracle.py --self-test`
  - `python3 scripts/tes_tts_instruction_normalizer_oracle.py --self-test`
  - `python3 scripts/tes_tts_fixture_schema_oracle.py --self-test`
  - `python3 scripts/validate_tds.py`
  - `python3 scripts/validate_doc_size.py`
  - `python3 scripts/validate_reference_package.py`
  - targeted no-provider/no-install `rg` checks.

Task:
Execute only TTS-007 through the circular sequence:
execute -> analyze -> fix -> certify -> create next /goal prompt -> local commit.

Required actions:
1. Run `git status --short --branch --untracked-files=all`.
2. Re-read:
   - `docs/roadmap/TES-TTS-NORMALIZATION-ARCHITECTURE-SPEC.md`
   - `docs/roadmap/TES-TTS-NORMALIZATION-EXECUTION-SPEC.md`
   - `docs/roadmap/TES-TTS-SKILL-ROADMAP.md`
   - `src/adapters/*/skills/tes-tts/references/providers-and-fallbacks.md`
   - `scripts/tes_tts_provider_probe_oracle.py`
3. Rank provider candidates after the no-write probe contract exists.
4. Do not probe real providers, call package managers, install dependencies,
   download models, write global config, or certify provider behavior.
5. Certify with targeted provider-review checks and the smallest docs/package
   oracles.
6. Create the next `/goal` prompt artifact for TTS-008 if TTS-007 is not the
   convergence endpoint.
7. Commit the local execution as the final action of the cycle.

Forbidden:
- no sync, release, push, tag, publish, provider install, provider download,
  proactive speak behavior, global config writes, or durable conversion cache.

Stop states:
BLOCKED, DEGRADED, NEEDS_REVIEW, NEEDS_OWNER_DECISION.
```
