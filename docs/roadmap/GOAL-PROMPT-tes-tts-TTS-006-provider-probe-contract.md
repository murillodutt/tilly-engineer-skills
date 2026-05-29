---
tds_id: roadmap.goal_prompt_tes_tts_tts_006_provider_probe_contract
tds_class: roadmap
status: active
consumer: maintainers, tes-tts maintainers, execution agents, and release reviewers
source_of_truth: false
evidence_level: L2
---

# GOAL Prompt: TES TTS TTS-006 Provider Probe Contract

This is the ready `/goal` prompt for the next circular execution cycle of
`tes-tts`.

```text
/goal Continue TES TTS sequential convergence.

Canonical artifact:
docs/roadmap/GOAL-SUPER-SPEC-tes-tts-sequential-convergence.md

Current unit:
TTS-006 Provider Probe Contract

Certified evidence from prior cycle:
- TTS-005 re-read:
  - `benchmarks/tes-tts/normalization-fixtures.json`
  - `docs/roadmap/TES-TTS-NORMALIZATION-FIXTURE-SCHEMA.md`
  - `docs/roadmap/TES-TTS-NORMALIZATION-EXECUTION-SPEC.md`
  - `docs/roadmap/TES-TTS-SKILL-ROADMAP.md`
  - both `language-normalization.md` references.
- TTS-005 added dependency-free instruction normalizer fixtures:
  - `benchmarks/tes-tts/instruction-normalizer-fixtures.json`
- TTS-005 added the focused instruction normalizer oracle:
  - `python3 scripts/tes_tts_instruction_normalizer_oracle.py --self-test`
- TTS-005 proved instruction-level cache shape without disk writes,
  protected-term preservation, redaction before speech text, and long-text
  chunking without summary.
- Ready prompt artifact for TTS-006 exists at
  docs/roadmap/GOAL-PROMPT-tes-tts-TTS-006-provider-probe-contract.md.
- Focused TTS-005 oracles passed:
  - `python3 scripts/tes_tts_instruction_normalizer_oracle.py --self-test`
  - `python3 scripts/tes_tts_fixture_schema_oracle.py --self-test`
  - `python3 scripts/validate_tds.py`
  - `python3 scripts/validate_doc_size.py`
  - `python3 scripts/validate_reference_package.py`
  - targeted instruction-normalizer `rg` checks.

Task:
Execute only TTS-006 through the circular sequence:
execute -> analyze -> fix -> certify -> create next /goal prompt -> local commit.

Required actions:
1. Run `git status --short --branch --untracked-files=all`.
2. Re-read:
   - `docs/roadmap/TES-TTS-NORMALIZATION-EXECUTION-SPEC.md`
   - `docs/roadmap/TES-TTS-SKILL-ROADMAP.md`
   - `docs/roadmap/GOAL-SUPER-SPEC-tes-tts-sequential-convergence.md`
   - `src/adapters/*/skills/tes-tts/references/providers-and-fallbacks.md`
   - `scripts/tes_tts_instruction_normalizer_oracle.py`
3. Add a no-write local provider probe contract with mocked available,
   unavailable, and needs-review states.
4. Do not probe real providers, call package managers, install dependencies,
   download models, write global config, or certify provider behavior.
5. Certify with a focused self-test, targeted negative `rg` checks, and the
   smallest docs/package oracles.
6. Create the next `/goal` prompt artifact for TTS-007 if TTS-006 is not the
   convergence endpoint.
7. Commit the local execution as the final action of the cycle.

Forbidden:
- no sync, release, push, tag, publish, provider install, provider download,
  proactive speak behavior, global config writes, or durable conversion cache.

Stop states:
BLOCKED, DEGRADED, NEEDS_REVIEW, NEEDS_OWNER_DECISION.
```
