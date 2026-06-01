---
tds_id: roadmap.goal_prompt_tes_tts_tts_017_owner_decision_open
tds_class: roadmap
status: active
consumer: maintainers, tes-tts maintainers, execution agents, and release reviewers
source_of_truth: false
evidence_level: L2
---

# GOAL Prompt: TES TTS TTS-017 Owner Decision Open

This is the ready `/goal` prompt for the next circular execution cycle of
`tes-tts`.

```text
/goal Continue TES TTS sequential convergence.

Canonical artifact:
docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-tes-tts-sequential-convergence.md

Current unit:
TTS-017 Owner Decision Open

Certified evidence from prior cycle:
- TTS-016 re-read:
  - `docs/adr/0004-tes-tts-pronunciation-normalization-and-enrichment.md`
  - `docs/roadmap/tes-tts/TES-TTS-OWNER-APPROVAL-GATE.md`
  - `docs/roadmap/tes-tts/TES-TTS-OWNER-DECISION-REQUIRED.md`
  - `docs/roadmap/tes-tts/TES-TTS-EXPLICIT-OWNER-DECISION.md`
  - `docs/roadmap/tes-tts/TES-TTS-OWNER-DECISION-PENDING.md`
  - `docs/roadmap/tes-tts/TES-TTS-OWNER-DECISION-STILL-PENDING.md`
  - `docs/roadmap/tes-tts/TES-TTS-OWNER-DECISION-STILL-REQUIRED.md`
  - `docs/roadmap/tes-tts/TES-TTS-ACCEPTANCE-AND-RELEASE-DECISION.md`
  - `docs/roadmap/tes-tts/TES-TTS-SKILL-ROADMAP.md`
  - `docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-tes-tts-sequential-convergence.md`
  - `docs/roadmap/goals/prompts/tes-tts/GOAL-PROMPT-tes-tts-TTS-016-owner-decision-remains-required.md`
- TTS-016 found no explicit maintainer decision in the current goal context to
  accept ADR 0004 or keep it proposed, authorize release identity planning or
  defer it, or continue forbidding sync or authorize a later sync cycle.
- TTS-016 recorded the owner decision remains required result at
  `docs/roadmap/tes-tts/TES-TTS-OWNER-DECISION-REMAINS-REQUIRED.md`.
- TTS-016 updated `docs/roadmap/tes-tts/TES-TTS-SKILL-ROADMAP.md` with the cycle
  outcome, current unit status, and ready prompt pointer.
- ADR 0004 remains `proposed`.
- Release identity remains deferred.
- Sync remains forbidden.
- No provider install, provider download, real provider probe, global config
  write, durable conversion cache, proactive `speak` behavior, version bump,
  release, push, tag, publish, or sync was performed.
- Ready prompt artifact for TTS-017 exists at
  docs/roadmap/goals/prompts/tes-tts/GOAL-PROMPT-tes-tts-TTS-017-owner-decision-open.md.
- TTS-016 focused oracles passed:
  - `python3 scripts/tes_tts_fixture_schema_oracle.py --self-test`
  - `python3 scripts/tes_tts_instruction_normalizer_oracle.py --self-test`
  - `python3 scripts/tes_tts_provider_probe_oracle.py --self-test`
  - `python3 scripts/tes_tts_provider_candidate_review_oracle.py --self-test`
  - `python3 /Users/murillo/.codex/skills/.system/skill-creator/scripts/quick_validate.py src/adapters/codex/skills/tes-tts`
  - `python3 /Users/murillo/.codex/skills/.system/skill-creator/scripts/quick_validate.py src/adapters/claude/skills/tes-tts`
  - `python3 scripts/materialize_adapter.py all --check`
  - `python3 scripts/command_trigger_oracle.py --self-test`
  - `python3 scripts/validate_tds.py`
  - `python3 scripts/validate_doc_size.py`
  - `python3 scripts/validate_reference_graph.py`
  - `python3 scripts/validate_reference_package.py`
  - `python3 scripts/private_vocabulary_oracle.py`
  - `npm run commit:check`

Task:
Execute only TTS-017 through the circular sequence:
execute -> analyze -> fix -> certify -> create next /goal prompt or close
convergence -> local commit.

Required actions:
1. Run `git status --short --branch --untracked-files=all`.
2. Re-read:
   - `docs/adr/0004-tes-tts-pronunciation-normalization-and-enrichment.md`
   - `docs/roadmap/tes-tts/TES-TTS-OWNER-APPROVAL-GATE.md`
   - `docs/roadmap/tes-tts/TES-TTS-OWNER-DECISION-REQUIRED.md`
   - `docs/roadmap/tes-tts/TES-TTS-EXPLICIT-OWNER-DECISION.md`
   - `docs/roadmap/tes-tts/TES-TTS-OWNER-DECISION-PENDING.md`
   - `docs/roadmap/tes-tts/TES-TTS-OWNER-DECISION-STILL-PENDING.md`
   - `docs/roadmap/tes-tts/TES-TTS-OWNER-DECISION-STILL-REQUIRED.md`
   - `docs/roadmap/tes-tts/TES-TTS-OWNER-DECISION-REMAINS-REQUIRED.md`
   - `docs/roadmap/tes-tts/TES-TTS-ACCEPTANCE-AND-RELEASE-DECISION.md`
   - `docs/roadmap/tes-tts/TES-TTS-SKILL-ROADMAP.md`
   - `docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-tes-tts-sequential-convergence.md`
   - `docs/roadmap/goals/prompts/tes-tts/GOAL-PROMPT-tes-tts-TTS-017-owner-decision-open.md`
3. Apply only explicit maintainer decisions already present in the current
   user message:
   - accept ADR 0004 or keep it proposed;
   - authorize release identity planning or defer it;
   - continue forbidding sync or authorize a later sync cycle.
4. If ADR acceptance is explicitly approved, update only ADR/status and
   directly correlated decision surfaces, then certify.
5. If release identity is explicitly approved, create the next release-identity
   `/goal` prompt. Do not bump, release, push, tag, publish, or sync in this
   cycle unless explicitly authorized in this same prompt.
6. If sync is explicitly authorized without release identity approval, stop at
   `NEEDS_REVIEW` because release identity must be handled first.
7. If approval is absent or partial, keep the state `NEEDS_OWNER_DECISION` and
   create the next exact prompt for the unresolved decision.
8. Update `docs/roadmap/tes-tts/TES-TTS-SKILL-ROADMAP.md` with the cycle outcome,
   current unit status, and ready prompt pointer before closure.
9. Commit the local execution as the final action of the cycle.

Forbidden:
- no sync, release, push, tag, publish, provider install, provider download,
  proactive speak behavior, global config writes, or durable conversion cache.
- no ADR status change, version bump, release identity claim, or sync claim
  without explicit maintainer approval in the current cycle.

Stop states:
BLOCKED, DEGRADED, NEEDS_REVIEW, NEEDS_OWNER_DECISION.
```
