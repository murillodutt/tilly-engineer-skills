---
tds_id: roadmap.goal_prompt_tes_tts_spec_010_final_audit_and_closure
tds_class: roadmap
status: archived
consumer: maintainers, tes-tts maintainers, execution agents, and final auditors
source_of_truth: false
evidence_level: L2
---

# GOAL Prompt: TES TTS SPEC-010 Final Audit And Closure

This is the ready `/goal` prompt for the next ten-SPEC `tes-tts` convergence
cycle after SPEC-009.

Status note: archived after SPEC-010. Next decision gate:
`docs/roadmap/goals/prompts/tes-tts/GOAL-PROMPT-tes-tts-OWNER-001-acceptance-release-sync-decision.md`.

```text
/goal Continue TES TTS ten-SPEC convergence.

Canonical artifact:
docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-tes-tts-ten-spec-convergence.md

Current unit:
SPEC-010 Final Audit And Closure

Certified evidence from prior cycle:
- SPEC-009 confirmed the evidence is sufficient to recommend ADR 0004
  acceptance for the bounded instruction-level and provider-boundary scope.
- SPEC-009 found no explicit maintainer approval in the current cycle to
  accept ADR 0004, authorize release identity work, or authorize sync.
- ADR 0004 remains proposed.
- Package identity remains anchored at `0.3.147`; no version, bundle, release,
  tag, push, publish, or sync surface changed.
- Provider-backed claims remain optional, degraded, or deferred; no real
  provider runtime is certified.
- No provider install, provider download, real provider certification, global
  config write, durable conversion cache, proactive `speak` behavior, push,
  tag, publish, release, or sync was performed.
- Ready prompt artifact for SPEC-010:
  `docs/roadmap/goals/prompts/tes-tts/GOAL-PROMPT-tes-tts-SPEC-010-final-audit-and-closure.md`.

Task:
Execute only SPEC-010 through:
execute -> analyze -> fix -> certify -> create next Super SPEC + /goal prompt
or close convergence -> local commit.

Required actions:
1. Run `git status --short --branch --untracked-files=all`.
2. Classify inherited TTS changes and unrelated `.agents/**` drift. Do not
   stage or modify unrelated `.agents/**` changes.
3. Re-read:
   - `docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-tes-tts-ten-spec-convergence.md`
   - `docs/roadmap/tes-tts/TES-TTS-SPEC-010-final-audit-and-closure.md`
   - `docs/roadmap/tes-tts/TES-TTS-SKILL-ROADMAP.md`
   - `docs/roadmap/tes-tts/TES-TTS-SPEC-001-roadmap-compaction-agent-default-language.md`
     through `docs/roadmap/tes-tts/TES-TTS-SPEC-009-release-identity-sync-readiness.md`
   - `docs/adr/0004-tes-tts-pronunciation-normalization-and-enrichment.md`
   - `src/adapters/codex/skills/tes-tts/**`
   - `src/adapters/claude/skills/tes-tts/**`
   - adapter and install docs that mention `tes-tts`
   - focused TTS fixtures and oracles under `benchmarks/tes-tts/**` and
     `scripts/tes_tts_*_oracle.py`
4. Execute SPEC-010 only:
   - audit ADR, SPECs, roadmap, fixtures, oracles, adapter parity, command
     triggers, provider posture, and release identity;
   - confirm whether `tes-tts` is complete for the approved scope or remains
     explicitly proposed/degraded/deferred;
   - keep ADR 0004 proposed unless explicit owner approval is present in the
     current cycle;
   - keep release identity, sync, version bump, bundle, tag, push, publish,
     release, and provider certification out of scope unless explicitly
     authorized in the current cycle;
   - confirm no proactive `speak` behavior, durable conversion cache, global
     config write, provider install, provider download, or user-text summary
     behavior entered `tes-tts`.
5. Analyze the diff for quality, efficiency, precision, false-green risk,
   boundary drift, evidence sufficiency, and audit completeness.
6. Fix only observed SPEC-010 defects.
7. Certify with:
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
   - `git diff --check`
   - `npm run commit:check` only as package closure evidence when unrelated
     drift does not make it impossible to interpret
8. If the approved scope is complete, close convergence with a final audit
   record and no next prompt. If owner approval or release identity remains
   unresolved, create the exact next `/goal` prompt for that unresolved
   decision.
9. Update `docs/roadmap/tes-tts/TES-TTS-SKILL-ROADMAP.md` with SPEC-010 outcome,
   closure state, next prompt pointer or closure statement, and sync status.
10. Stage only SPEC-010 files, roadmap/index updates, and any next prompt
    artifact created by this cycle.
11. Commit locally as the final shell action for the cycle.

Forbidden:
- no sync, release, push, tag, publish, provider install, provider download,
  provider certification, proactive speak behavior, global config writes,
  durable conversion cache, version bump, bundle generation, ADR status
  change, or unrelated `.agents/**` changes without explicit current-cycle
  owner approval.

Stop states:
PASS, DEGRADED, NEEDS_REVIEW, NEEDS_OWNER_DECISION, BLOCKED.

Required closeout:
- changed files;
- focused oracles and result;
- next prompt artifact or closure statement;
- local commit hash;
- sync status: REMOTE_SYNC_NOT_REQUESTED unless explicitly authorized.
```
