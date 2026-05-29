---
tds_id: roadmap.goal_prompt_tes_tts_tts_010_owner_approval_gate
tds_class: roadmap
status: active
consumer: maintainers, tes-tts maintainers, execution agents, and release reviewers
source_of_truth: false
evidence_level: L2
---

# GOAL Prompt: TES TTS TTS-010 Owner Approval Gate

This is the ready `/goal` prompt for the next circular execution cycle of
`tes-tts`.

```text
/goal Continue TES TTS sequential convergence.

Canonical artifact:
docs/roadmap/GOAL-SUPER-SPEC-tes-tts-sequential-convergence.md

Current unit:
TTS-010 Owner Approval Gate

Certified evidence from prior cycle:
- TTS-009 re-read ADR 0004, the normalization architecture SPEC, the
  normalization execution SPEC, the TES TTS roadmap, the GOAL Super SPEC, the
  TTS-009 prompt, focused TTS fixtures, and focused TTS oracles.
- TTS-009 recorded the decision at
  `docs/roadmap/TES-TTS-ACCEPTANCE-AND-RELEASE-DECISION.md`.
- TTS-009 recommends ADR 0004 acceptance for the bounded instruction-level and
  provider-boundary scope, but did not change ADR status because explicit
  maintainer approval is still required.
- TTS-009 decided release identity cannot proceed without separate explicit
  authorization.
- TTS-009 preserved the existing locks: no sync, release, push, tag, publish,
  provider install, provider download, real provider probe, global config
  write, durable conversion cache, or proactive `speak` behavior.
- Ready prompt artifact for TTS-010 exists at
  docs/roadmap/GOAL-PROMPT-tes-tts-TTS-010-owner-approval-gate.md.
- TTS-009 focused oracles passed:
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
Execute only TTS-010 through the circular sequence:
execute -> analyze -> fix -> certify -> create next /goal prompt or close
convergence -> local commit.

Required actions:
1. Run `git status --short --branch --untracked-files=all`.
2. Re-read:
   - `docs/adr/0004-tes-tts-pronunciation-normalization-and-enrichment.md`
   - `docs/roadmap/TES-TTS-ACCEPTANCE-AND-RELEASE-DECISION.md`
   - `docs/roadmap/TES-TTS-SKILL-ROADMAP.md`
   - `docs/roadmap/GOAL-SUPER-SPEC-tes-tts-sequential-convergence.md`
   - `docs/roadmap/GOAL-PROMPT-tes-tts-TTS-010-owner-approval-gate.md`
3. Ask for or apply only explicit maintainer decisions already present in the
   current user message:
   - accept ADR 0004 or keep it proposed;
   - authorize release identity planning or defer it;
   - continue forbidding sync or authorize a later sync cycle.
4. If ADR acceptance is explicitly approved, update only ADR/status and
   directly correlated decision surfaces, then certify.
5. If release identity is explicitly approved, create the next release-identity
   `/goal` prompt. Do not bump, release, push, tag, publish, or sync in this
   cycle unless explicitly authorized in this same prompt.
6. If approval is absent or partial, keep the state `NEEDS_OWNER_DECISION` and
   create the next exact prompt for the unresolved decision.
7. Commit the local execution as the final action of the cycle.

Forbidden:
- no sync, release, push, tag, publish, provider install, provider download,
  proactive speak behavior, global config writes, or durable conversion cache.
- no ADR status change, version bump, release identity claim, or sync claim
  without explicit maintainer approval in the current cycle.

Stop states:
BLOCKED, DEGRADED, NEEDS_REVIEW, NEEDS_OWNER_DECISION.
```
