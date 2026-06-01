---
tds_id: roadmap.goal_prompt_tes_tts_spec_001_roadmap_compaction_agent_default_language
tds_class: roadmap
status: archived
consumer: maintainers, tes-tts maintainers, execution agents, and release reviewers
source_of_truth: false
evidence_level: L2
---

# GOAL Prompt: TES TTS SPEC-001 Roadmap Compaction And Agent Default Language

This is the ready `/goal` prompt to start the ten-SPEC `tes-tts` convergence
sequence.

```text
/goal Continue TES TTS ten-SPEC convergence.

Canonical artifact:
docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-tes-tts-ten-spec-convergence.md

Current unit:
SPEC-001 Roadmap Compaction And Agent Default Language

Certified context:
- The prior owner-decision preservation loop is non-convergent unless the user
  explicitly asks to preserve that stop state again.
- The ten draft SPECs exist as `docs/roadmap/tes-tts/TES-TTS-SPEC-001-*.md`
  through `docs/roadmap/tes-tts/TES-TTS-SPEC-010-*.md`.
- ADR 0004 remains proposed unless explicitly accepted in the current user
  message.
- Release identity and sync remain out of scope unless explicitly authorized
  in the current user message.
- Provider install, provider download, real provider certification, global
  config writes, durable conversion cache, proactive `speak` behavior, push,
  tag, publish, release, and sync are forbidden.

Task:
Execute only SPEC-001 through:
execute -> analyze -> fix -> certify -> create next Super SPEC + /goal prompt
or close convergence -> local commit.

Required actions:
1. Run `git status --short --branch --untracked-files=all`.
2. Classify inherited TTS changes and unrelated `.agents/**` drift. Do not
   stage or modify unrelated `.agents/**` changes.
3. Re-read:
   - `docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-tes-tts-ten-spec-convergence.md`
   - `docs/roadmap/tes-tts/TES-TTS-SPEC-001-roadmap-compaction-agent-default-language.md`
   - `docs/roadmap/tes-tts/TES-TTS-SKILL-ROADMAP.md`
   - `docs/roadmap/README.md`
   - `docs/roadmap/tes-tts/TES-TTS-NORMALIZATION-ARCHITECTURE-SPEC.md`
   - `docs/roadmap/tes-tts/TES-TTS-NORMALIZATION-EXECUTION-SPEC.md`
   - `src/adapters/codex/skills/tes-tts/references/language-normalization.md`
   - `src/adapters/claude/skills/tes-tts/references/language-normalization.md`
   - `benchmarks/tes-tts/normalization-fixtures.json`
   - `scripts/tes_tts_fixture_schema_oracle.py`
4. Execute SPEC-001 only:
   - compact roadmap index noise so historical TTS prompts and owner-decision
     records are not active SPECs;
   - encode `agent_default_language` selector policy:
     Codex `~/.codex/config.toml` `[desktop].localeOverride`;
     Claude Code `~/.claude/settings.json` `language`, normalized by TES
     policy;
     Cursor explicit User Rules/project rules first, otherwise Codex default
     first and Claude default second;
   - maintain selector fixture coverage for Cursor fallback.
5. Analyze the diff for quality, efficiency, precision, false-green risk,
   boundary drift, and evidence sufficiency.
6. Fix only observed SPEC-001 defects.
7. Certify with:
   - `python3 scripts/tes_tts_fixture_schema_oracle.py --self-test`
   - `python3 scripts/tes_tts_instruction_normalizer_oracle.py --self-test`
   - `python3 /Users/murillo/.codex/skills/.system/skill-creator/scripts/quick_validate.py src/adapters/codex/skills/tes-tts`
   - `python3 /Users/murillo/.codex/skills/.system/skill-creator/scripts/quick_validate.py src/adapters/claude/skills/tes-tts`
   - `python3 scripts/materialize_adapter.py all --check`
   - `python3 scripts/validate_tds.py`
   - `python3 scripts/validate_doc_size.py`
   - `python3 scripts/validate_reference_graph.py`
   - `git diff --check`
8. Create or update the next `/goal` prompt for SPEC-002 Fixture Corpus
   Complete before closure.
9. Update `docs/roadmap/tes-tts/TES-TTS-SKILL-ROADMAP.md` with SPEC-001 outcome,
   next prompt pointer, and sync status.
10. Stage only SPEC-001 files and the next prompt artifact.
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
