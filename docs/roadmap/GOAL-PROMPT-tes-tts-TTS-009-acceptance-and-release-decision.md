---
tds_id: roadmap.goal_prompt_tes_tts_tts_009_acceptance_and_release_decision
tds_class: roadmap
status: active
consumer: maintainers, tes-tts maintainers, execution agents, and release reviewers
source_of_truth: false
evidence_level: L2
---

# GOAL Prompt: TES TTS TTS-009 Acceptance And Release Decision

This is the ready `/goal` prompt for the next circular execution cycle of
`tes-tts`.

```text
/goal Continue TES TTS sequential convergence.

Canonical artifact:
docs/roadmap/GOAL-SUPER-SPEC-tes-tts-sequential-convergence.md

Current unit:
TTS-009 Acceptance And Release Decision

Certified evidence from prior cycle:
- TTS-008 re-read:
  - `src/adapters/codex/skills/tes-tts/**`
  - `src/adapters/claude/skills/tes-tts/**`
  - `docs/adapters/CODEX.md`
  - `docs/adapters/CLAUDE.md`
  - `docs/adapters/PLATFORM-DIFFERENCES.md`
  - `docs/install/COMMAND-TRIGGERS.md`
  - `scripts/materialize_adapter.py`
  - `scripts/command_trigger_oracle.py`
- TTS-008 confirmed the Codex and Claude `tes-tts` skill file sets match.
- TTS-008 diffed the Codex and Claude skill trees. The only intentional
  difference is the contract-history line naming the adapter-specific promotion
  target.
- TTS-008 confirmed `/tes-tts`, `/tes:tts`, `tes tts`, `read this text
  aloud`, `leia em voz alta`, and `narrar este texto` are registered across
  adapter docs, install docs, source bootloaders/rules, and the command trigger
  oracle.
- TTS-008 did not run sync, release, push, tag, publish, provider installs,
  provider downloads, real provider probes, global config writes, provider
  certification, or proactive `speak` behavior.
- Ready prompt artifact for TTS-009 exists at
  docs/roadmap/GOAL-PROMPT-tes-tts-TTS-009-acceptance-and-release-decision.md.
- TTS-008 focused oracles passed:
  - `python3 /Users/murillo/.codex/skills/.system/skill-creator/scripts/quick_validate.py src/adapters/codex/skills/tes-tts`
  - `python3 /Users/murillo/.codex/skills/.system/skill-creator/scripts/quick_validate.py src/adapters/claude/skills/tes-tts`
  - `python3 scripts/materialize_adapter.py all --check`
  - `python3 scripts/command_trigger_oracle.py --self-test`
  - `python3 scripts/tes_tts_provider_candidate_review_oracle.py --self-test`
  - `python3 scripts/tes_tts_provider_probe_oracle.py --self-test`
  - `python3 scripts/tes_tts_instruction_normalizer_oracle.py --self-test`
  - `python3 scripts/tes_tts_fixture_schema_oracle.py --self-test`
  - `python3 scripts/validate_tds.py`
  - `python3 scripts/validate_doc_size.py`
  - `python3 scripts/validate_reference_graph.py`
  - `python3 scripts/validate_reference_package.py`
  - `python3 scripts/private_vocabulary_oracle.py`
  - targeted adapter parity and forbidden-action `rg` checks.

Task:
Execute only TTS-009 through the circular sequence:
execute -> analyze -> fix -> certify -> create next /goal prompt or close
convergence -> local commit.

Required actions:
1. Run `git status --short --branch --untracked-files=all`.
2. Re-read:
   - `docs/adr/0004-tes-tts-pronunciation-normalization-and-enrichment.md`
   - `docs/roadmap/TES-TTS-NORMALIZATION-ARCHITECTURE-SPEC.md`
   - `docs/roadmap/TES-TTS-NORMALIZATION-EXECUTION-SPEC.md`
   - `docs/roadmap/TES-TTS-SKILL-ROADMAP.md`
   - `docs/roadmap/GOAL-SUPER-SPEC-tes-tts-sequential-convergence.md`
   - `docs/roadmap/GOAL-PROMPT-tes-tts-TTS-009-acceptance-and-release-decision.md`
   - focused TTS fixture and oracle files under `benchmarks/tes-tts/**` and
     `scripts/tes_tts_*_oracle.py`
3. Decide whether the current evidence is enough to recommend ADR 0004
   acceptance. If maintainer approval is still required, report
   `NEEDS_OWNER_DECISION` without changing ADR status.
4. Decide whether release identity can proceed. Do not edit version, bundle,
   release, tag, or sync surfaces unless the maintainer explicitly authorizes
   that separate release action.
5. If convergence is not complete, create the next `/goal` prompt artifact for
   the exact unresolved acceptance or release-decision sub-unit. If convergence
   is complete and owner approval is present, close without a next prompt.
6. Certify with the focused TTS oracles, TDS/doc-size/reference validators,
   and `npm run commit:check` only as package closure evidence.
7. Commit the local execution as the final action of the cycle.

Forbidden:
- no sync, release, push, tag, publish, provider install, provider download,
  proactive speak behavior, global config writes, or durable conversion cache.
- no ADR status change, version bump, release identity claim, or sync claim
  without explicit maintainer approval in the current cycle.

Stop states:
BLOCKED, DEGRADED, NEEDS_REVIEW, NEEDS_OWNER_DECISION.
```
