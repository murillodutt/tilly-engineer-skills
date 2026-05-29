---
tds_id: roadmap.goal_prompt_tes_tts_spec_005_provider_probe_no_write
tds_class: roadmap
status: active
consumer: maintainers, tes-tts maintainers, execution agents, and validation authors
source_of_truth: false
evidence_level: L2
---

# GOAL Prompt: TES TTS SPEC-005 Provider Probe No-Write

This is the ready `/goal` prompt for the next ten-SPEC `tes-tts` convergence
cycle after SPEC-004.

```text
/goal Continue TES TTS ten-SPEC convergence.

Canonical artifact:
docs/roadmap/GOAL-SUPER-SPEC-tes-tts-ten-spec-convergence.md

Current unit:
SPEC-005 Provider Probe No-Write

Certified evidence from prior cycle:
- SPEC-004 added conservative pronunciation hints for protected technical
  terms.
- SPEC-004 kept visible/source text unchanged and preserved proper nouns,
  commands, paths, code identifiers, and acronyms.
- SPEC-004 avoided IPA, SSML, phoneme, provider-backed, and semantic
  translation claims.
- SPEC-004 kept Hebrew/provider-backed pronunciation explicitly degraded until
  later SPECs certify more.
- ADR 0004 remains proposed.
- Release identity and sync remain out of scope.
- No provider install, provider download, real provider certification, global
  config write, durable conversion cache, proactive `speak` behavior, push,
  tag, publish, release, or sync was performed.
- Ready prompt artifact for SPEC-005:
  `docs/roadmap/GOAL-PROMPT-tes-tts-SPEC-005-provider-probe-no-write.md`.

Task:
Execute only SPEC-005 through:
execute -> analyze -> fix -> certify -> create next Super SPEC + /goal prompt
or close convergence -> local commit.

Required actions:
1. Run `git status --short --branch --untracked-files=all`.
2. Classify inherited TTS changes and unrelated `.agents/**` drift. Do not
   stage or modify unrelated `.agents/**` changes.
3. Re-read:
   - `docs/roadmap/GOAL-SUPER-SPEC-tes-tts-ten-spec-convergence.md`
   - `docs/roadmap/TES-TTS-SPEC-005-provider-probe-no-write.md`
   - `docs/roadmap/TES-TTS-SKILL-ROADMAP.md`
   - `docs/roadmap/TES-TTS-NORMALIZATION-EXECUTION-SPEC.md`
   - `benchmarks/tes-tts/provider-probe-fixtures.json`
   - `scripts/tes_tts_provider_probe_oracle.py`
   - `scripts/tes_tts_fixture_schema_oracle.py`
4. Execute SPEC-005 only:
   - harden local provider probe fixtures for available, unavailable,
     needs-review, and degraded states;
   - keep probes read-only, no-network, no-install, no-download, and no-write;
   - return local evidence only: version, language signal, license note, and
     reason when present;
   - avoid provider support certification from probe existence alone.
5. Analyze the diff for quality, efficiency, precision, false-green risk,
   boundary drift, and evidence sufficiency.
6. Fix only observed SPEC-005 defects.
7. Certify with:
   - `python3 scripts/tes_tts_provider_probe_oracle.py --self-test`
   - `python3 scripts/tes_tts_fixture_schema_oracle.py --self-test`
   - `python3 scripts/validate_tds.py`
   - `python3 scripts/validate_doc_size.py`
   - `python3 scripts/validate_reference_graph.py`
   - `git diff --check`
8. Create or update the next `/goal` prompt for SPEC-006 Provider Candidate
   Selection before closure.
9. Update `docs/roadmap/TES-TTS-SKILL-ROADMAP.md` with SPEC-005 outcome,
   next prompt pointer, and sync status.
10. Stage only SPEC-005 files and the next prompt artifact.
11. Commit locally as the final shell action for the cycle.

Forbidden:
- no sync, release, push, tag, publish, provider install, provider download,
  provider certification, proactive speak behavior, global config writes,
  durable conversion cache, or unrelated `.agents/**` changes.

Stop states:
PASS, DEGRADED, NEEDS_REVIEW, NEEDS_OWNER_DECISION, BLOCKED.

Required closeout:
- changed files;
- focused oracles and result;
- next prompt artifact;
- local commit hash;
- sync status: REMOTE_SYNC_NOT_REQUESTED unless explicitly authorized.
```
