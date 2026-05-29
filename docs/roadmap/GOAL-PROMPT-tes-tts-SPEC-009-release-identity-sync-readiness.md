---
tds_id: roadmap.goal_prompt_tes_tts_spec_009_release_identity_sync_readiness
tds_class: roadmap
status: active
consumer: maintainers, tes-tts maintainers, execution agents, and release reviewers
source_of_truth: false
evidence_level: L2
---

# GOAL Prompt: TES TTS SPEC-009 Release Identity And Sync Readiness

This is the ready `/goal` prompt for the next ten-SPEC `tes-tts` convergence
cycle after SPEC-008.

```text
/goal Continue TES TTS ten-SPEC convergence.

Canonical artifact:
docs/roadmap/GOAL-SUPER-SPEC-tes-tts-ten-spec-convergence.md

Current unit:
SPEC-009 Release Identity And Sync Readiness

Certified evidence from prior cycle:
- SPEC-008 defined optional G2P/pronunciation provider boundaries without
  adding a provider dependency.
- SPEC-008 kept instruction-level pronunciation hints as the baseline.
- SPEC-008 blocked IPA, SSML, phoneme, lexicon, and provider-backed
  pronunciation outputs until fixtures and probes prove local behavior.
- SPEC-008 kept Hebrew explicitly degraded until local quality, language,
  runtime, and license evidence exists.
- ADR 0004 remains proposed.
- Release identity and sync remain out of scope until SPEC-009 owner decision
  handling.
- No provider install, provider download, real provider certification, global
  config write, durable conversion cache, proactive `speak` behavior, push,
  tag, publish, release, or sync was performed.
- Ready prompt artifact for SPEC-009:
  `docs/roadmap/GOAL-PROMPT-tes-tts-SPEC-009-release-identity-sync-readiness.md`.

Task:
Execute only SPEC-009 through:
execute -> analyze -> fix -> certify -> create next Super SPEC + /goal prompt
or close convergence -> local commit.

Required actions:
1. Run `git status --short --branch --untracked-files=all`.
2. Classify inherited TTS changes and unrelated `.agents/**` drift. Do not
   stage or modify unrelated `.agents/**` changes.
3. Re-read:
   - `docs/roadmap/GOAL-SUPER-SPEC-tes-tts-ten-spec-convergence.md`
   - `docs/roadmap/TES-TTS-SPEC-009-release-identity-sync-readiness.md`
   - `docs/roadmap/TES-TTS-SKILL-ROADMAP.md`
   - `docs/roadmap/TES-TTS-ACCEPTANCE-AND-RELEASE-DECISION.md`
   - `docs/adr/0004-tes-tts-pronunciation-normalization-and-enrichment.md`
   - adapter and install docs that mention `tes-tts`
   - relevant version, bundle, and release surfaces only for read-only review
4. Execute SPEC-009 only:
   - decide whether evidence is sufficient to recommend ADR 0004 acceptance;
   - if explicit owner approval is absent, keep ADR 0004 proposed and report
     `NEEDS_OWNER_DECISION`;
   - decide whether release identity planning can proceed, but do not bump,
     bundle, release, tag, push, publish, or sync without explicit approval;
   - preserve provider-backed claims as optional, degraded, or deferred unless
     certified by local fixtures and probes.
5. Analyze the diff for quality, efficiency, precision, false-green risk,
   boundary drift, and evidence sufficiency.
6. Fix only observed SPEC-009 defects.
7. Certify with:
   - `python3 scripts/command_trigger_oracle.py --self-test`
   - `python3 scripts/materialize_adapter.py all --check`
   - `python3 scripts/tes_tts_fixture_schema_oracle.py --self-test`
   - `python3 scripts/tes_tts_instruction_normalizer_oracle.py --self-test`
   - `python3 scripts/tes_tts_provider_probe_oracle.py --self-test`
   - `python3 scripts/tes_tts_provider_candidate_review_oracle.py --self-test`
   - `python3 scripts/validate_tds.py`
   - `python3 scripts/validate_doc_size.py`
   - `python3 scripts/validate_reference_graph.py`
   - `python3 scripts/validate_reference_package.py`
   - `git diff --check`
   - `npm run commit:check` only as package closure evidence when unrelated
     drift does not make it impossible to interpret
8. Create or update the next `/goal` prompt for SPEC-010 Final Audit And
   Closure before closure unless owner approval creates a narrower release
   decision prompt.
9. Update `docs/roadmap/TES-TTS-SKILL-ROADMAP.md` with SPEC-009 outcome,
   next prompt pointer, and sync status.
10. Stage only SPEC-009 files and the next prompt artifact.
11. Commit locally as the final shell action for the cycle.

Forbidden:
- no sync, release, push, tag, publish, provider install, provider download,
  provider certification, proactive speak behavior, global config writes,
  durable conversion cache, version bump, bundle generation, ADR status change,
  or unrelated `.agents/**` changes without explicit current-cycle owner
  approval.

Stop states:
PASS, DEGRADED, NEEDS_REVIEW, NEEDS_OWNER_DECISION, BLOCKED.

Required closeout:
- changed files;
- focused oracles and result;
- next prompt artifact;
- local commit hash;
- sync status: REMOTE_SYNC_NOT_REQUESTED unless explicitly authorized.
```
