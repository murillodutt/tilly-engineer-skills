---
tds_id: roadmap.goal_prompt_tes_tts_tts_008_adapter_parity
tds_class: roadmap
status: active
consumer: maintainers, tes-tts maintainers, execution agents, and release reviewers
source_of_truth: false
evidence_level: L2
---

# GOAL Prompt: TES TTS TTS-008 Adapter Parity

This is the ready `/goal` prompt for the next circular execution cycle of
`tes-tts`.

```text
/goal Continue TES TTS sequential convergence.

Canonical artifact:
docs/roadmap/GOAL-SUPER-SPEC-tes-tts-sequential-convergence.md

Current unit:
TTS-008 Adapter Parity

Certified evidence from prior cycle:
- TTS-007 re-read:
  - `docs/roadmap/TES-TTS-NORMALIZATION-ARCHITECTURE-SPEC.md`
  - `docs/roadmap/TES-TTS-NORMALIZATION-EXECUTION-SPEC.md`
  - `docs/roadmap/TES-TTS-SKILL-ROADMAP.md`
  - `src/adapters/*/skills/tes-tts/references/providers-and-fallbacks.md`
  - `scripts/tes_tts_provider_probe_oracle.py`
- TTS-007 added provider candidate review artifacts:
  - `docs/roadmap/TES-TTS-PROVIDER-CANDIDATE-REVIEW.md`
  - `benchmarks/tes-tts/provider-candidate-review.json`
- TTS-007 added the focused provider candidate review oracle:
  - `python3 scripts/tes_tts_provider_candidate_review_oracle.py --self-test`
- TTS-007 ranked provider candidates only for future probes. It did not probe
  real providers, install dependencies, fetch model artifacts, write global
  config, or certify provider behavior.
- Ready prompt artifact for TTS-008 exists at
  docs/roadmap/GOAL-PROMPT-tes-tts-TTS-008-adapter-parity.md.
- Focused TTS-007 oracles passed:
  - `python3 scripts/tes_tts_provider_candidate_review_oracle.py --self-test`
  - `python3 scripts/tes_tts_provider_probe_oracle.py --self-test`
  - `python3 scripts/tes_tts_instruction_normalizer_oracle.py --self-test`
  - `python3 scripts/tes_tts_fixture_schema_oracle.py --self-test`
  - `python3 scripts/validate_tds.py`
  - `python3 scripts/validate_doc_size.py`
  - `python3 scripts/validate_reference_package.py`
  - targeted provider-review `rg` checks.

Task:
Execute only TTS-008 through the circular sequence:
execute -> analyze -> fix -> certify -> create next /goal prompt -> local commit.

Required actions:
1. Run `git status --short --branch --untracked-files=all`.
2. Re-read:
   - `src/adapters/codex/skills/tes-tts/**`
   - `src/adapters/claude/skills/tes-tts/**`
   - `docs/adapters/CODEX.md`
   - `docs/adapters/CLAUDE.md`
   - `docs/adapters/PLATFORM-DIFFERENCES.md`
   - `docs/install/COMMAND-TRIGGERS.md`
   - `scripts/materialize_adapter.py`
   - `scripts/command_trigger_oracle.py`
3. Keep Codex and Claude skill content behaviorally aligned and Cursor/install
   documentation honest.
4. Do not run sync, release, push, tag, publish, provider installs, provider
   downloads, real provider probes, global config writes, or provider
   certification.
5. Certify with quick skill validation, materialization, command-trigger
   oracle, targeted `rg`, and the smallest docs/package oracles.
6. Create the next `/goal` prompt artifact for TTS-009 if TTS-008 is not the
   convergence endpoint.
7. Commit the local execution as the final action of the cycle.

Forbidden:
- no sync, release, push, tag, publish, provider install, provider download,
  proactive speak behavior, global config writes, or durable conversion cache.

Stop states:
BLOCKED, DEGRADED, NEEDS_REVIEW, NEEDS_OWNER_DECISION.
```
