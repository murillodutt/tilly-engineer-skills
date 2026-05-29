---
tds_id: roadmap.goal_prompt_tes_tts_spec_004_pronunciation_enrichment_rules
tds_class: roadmap
status: archived
consumer: maintainers, tes-tts maintainers, execution agents, and validation authors
source_of_truth: false
evidence_level: L2
---

# GOAL Prompt: TES TTS SPEC-004 Pronunciation Enrichment Rules

Status: archived after SPEC-004 local execution. The next ready prompt is
`docs/roadmap/GOAL-PROMPT-tes-tts-SPEC-005-provider-probe-no-write.md`.

This is the ready `/goal` prompt for the next ten-SPEC `tes-tts` convergence
cycle after SPEC-003.

```text
/goal Continue TES TTS ten-SPEC convergence.

Canonical artifact:
docs/roadmap/GOAL-SUPER-SPEC-tes-tts-ten-spec-convergence.md

Current unit:
SPEC-004 Pronunciation Enrichment Rules

Certified evidence from prior cycle:
- SPEC-003 made selector behavior deterministic from the normalization corpus
  according to SPEC-001 precedence.
- SPEC-003 kept the instruction-level cache ephemeral and checked for no disk
  write surfaces in the oracle.
- SPEC-003 preserved protected terms before speech cleanup.
- SPEC-003 redacted secret-like values before speech text was assembled.
- SPEC-003 chunked long text without dropping words or summarizing.
- SPEC-003 cleaned Markdown for speech without changing meaning.
- ADR 0004 remains proposed.
- Release identity and sync remain out of scope.
- No provider install, provider download, real provider certification, global
  config write, durable conversion cache, proactive `speak` behavior, push,
  tag, publish, release, or sync was performed.
- Ready prompt artifact for SPEC-004:
  `docs/roadmap/GOAL-PROMPT-tes-tts-SPEC-004-pronunciation-enrichment-rules.md`.

Task:
Execute only SPEC-004 through:
execute -> analyze -> fix -> certify -> create next Super SPEC + /goal prompt
or close convergence -> local commit.

Required actions:
1. Run `git status --short --branch --untracked-files=all`.
2. Classify inherited TTS changes and unrelated `.agents/**` drift. Do not
   stage or modify unrelated `.agents/**` changes.
3. Re-read:
   - `docs/roadmap/GOAL-SUPER-SPEC-tes-tts-ten-spec-convergence.md`
   - `docs/roadmap/TES-TTS-SPEC-004-pronunciation-enrichment-rules.md`
   - `docs/roadmap/TES-TTS-SKILL-ROADMAP.md`
   - `docs/roadmap/TES-TTS-NORMALIZATION-EXECUTION-SPEC.md`
   - `benchmarks/tes-tts/instruction-normalizer-fixtures.json`
   - `benchmarks/tes-tts/normalization-fixtures.json`
   - `scripts/tes_tts_instruction_normalizer_oracle.py`
   - `src/adapters/codex/skills/tes-tts/references/language-normalization.md`
   - `src/adapters/claude/skills/tes-tts/references/language-normalization.md`
4. Execute SPEC-004 only:
   - add conservative pronunciation hints for protected technical terms;
   - keep visible/source text unchanged;
   - preserve proper nouns, commands, paths, code identifiers, and acronyms;
   - avoid IPA, SSML, phoneme, provider-backed, or semantic translation claims;
   - keep Hebrew/provider-backed pronunciation explicitly degraded unless
     later SPECs certify more.
5. Analyze the diff for quality, efficiency, precision, false-green risk,
   boundary drift, and evidence sufficiency.
6. Fix only observed SPEC-004 defects.
7. Certify with:
   - `python3 scripts/tes_tts_instruction_normalizer_oracle.py --self-test`
   - `python3 scripts/tes_tts_fixture_schema_oracle.py --self-test`
   - `python3 /Users/murillo/.codex/skills/.system/skill-creator/scripts/quick_validate.py src/adapters/codex/skills/tes-tts`
   - `python3 /Users/murillo/.codex/skills/.system/skill-creator/scripts/quick_validate.py src/adapters/claude/skills/tes-tts`
   - `python3 scripts/validate_tds.py`
   - `python3 scripts/validate_doc_size.py`
   - `python3 scripts/validate_reference_graph.py`
   - `git diff --check`
8. Create or update the next `/goal` prompt for SPEC-005 Provider Probe
   No-Write before closure.
9. Update `docs/roadmap/TES-TTS-SKILL-ROADMAP.md` with SPEC-004 outcome,
   next prompt pointer, and sync status.
10. Stage only SPEC-004 files and the next prompt artifact.
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
