---
tds_id: roadmap.goal_prompt_tes_tts_spec_002_fixture_corpus_complete
tds_class: roadmap
status: active
consumer: maintainers, tes-tts maintainers, execution agents, and validation authors
source_of_truth: false
evidence_level: L2
---

# GOAL Prompt: TES TTS SPEC-002 Fixture Corpus Complete

This is the ready `/goal` prompt for the next ten-SPEC `tes-tts` convergence
cycle after SPEC-001.

```text
/goal Continue TES TTS ten-SPEC convergence.

Canonical artifact:
docs/roadmap/GOAL-SUPER-SPEC-tes-tts-ten-spec-convergence.md

Current unit:
SPEC-002 Fixture Corpus Complete

Certified evidence from prior cycle:
- SPEC-001 compacted roadmap index noise so historical TTS prompts and
  owner-decision records are no longer treated as active execution SPECs.
- SPEC-001 encoded `agent_default_language` selector policy:
  - Codex: `~/.codex/config.toml` `[desktop].localeOverride`;
  - Claude Code: `~/.claude/settings.json` `language`, normalized by TES
    policy;
  - Cursor: explicit User Rules/project rules first, otherwise Codex default
    first and Claude default second.
- SPEC-001 added selector fixture coverage for Cursor fallback with
  `tts-dls-006`.
- ADR 0004 remains proposed.
- Release identity and sync remain out of scope.
- No provider install, provider download, real provider certification, global
  config write, durable conversion cache, proactive `speak` behavior, push,
  tag, publish, release, or sync was performed.
- Ready prompt artifact for SPEC-002:
  `docs/roadmap/GOAL-PROMPT-tes-tts-SPEC-002-fixture-corpus-complete.md`.

Task:
Execute only SPEC-002 through:
execute -> analyze -> fix -> certify -> create next Super SPEC + /goal prompt
or close convergence -> local commit.

Required actions:
1. Run `git status --short --branch --untracked-files=all`.
2. Classify inherited TTS changes and unrelated `.agents/**` drift. Do not
   stage or modify unrelated `.agents/**` changes.
3. Re-read:
   - `docs/roadmap/GOAL-SUPER-SPEC-tes-tts-ten-spec-convergence.md`
   - `docs/roadmap/TES-TTS-SPEC-002-fixture-corpus-complete.md`
   - `docs/roadmap/TES-TTS-SKILL-ROADMAP.md`
   - `docs/roadmap/TES-TTS-NORMALIZATION-FIXTURE-SCHEMA.md`
   - `docs/roadmap/TES-TTS-NORMALIZATION-EXECUTION-SPEC.md`
   - `benchmarks/tes-tts/normalization-fixture.schema.json`
   - `benchmarks/tes-tts/normalization-fixtures.json`
   - `scripts/tes_tts_fixture_schema_oracle.py`
4. Execute SPEC-002 only:
   - add dependency-free fixture coverage for all first-class languages:
     `pt-BR`, `en`, `es`, `fr`, `it`, `de`, and `he`;
   - add negative fixture classes for Markdown, URLs, paths, code fences,
     long hashes, secret-like values, provider unavailable, voice unavailable,
     and Hebrew degraded posture;
   - preserve `no_summary: true`;
   - update schema only if the required cases cannot be represented.
5. Analyze the diff for quality, efficiency, precision, false-green risk,
   boundary drift, and evidence sufficiency.
6. Fix only observed SPEC-002 defects.
7. Certify with:
   - `python3 scripts/tes_tts_fixture_schema_oracle.py --self-test`
   - `python3 scripts/validate_tds.py`
   - `python3 scripts/validate_doc_size.py`
   - `python3 scripts/validate_reference_graph.py`
   - `git diff --check`
8. Create or update the next `/goal` prompt for SPEC-003 Deterministic
   Instruction Normalizer before closure.
9. Update `docs/roadmap/TES-TTS-SKILL-ROADMAP.md` with SPEC-002 outcome,
   next prompt pointer, and sync status.
10. Stage only SPEC-002 files and the next prompt artifact.
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
