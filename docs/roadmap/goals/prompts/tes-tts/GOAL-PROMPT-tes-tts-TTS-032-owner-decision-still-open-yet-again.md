---
tds_id: roadmap.goal_prompt_tes_tts_tts_032_owner_decision_still_open_yet_again
tds_class: roadmap
status: archived
consumer: maintainers, tes-tts maintainers, execution agents, and release reviewers
source_of_truth: false
evidence_level: L2
---

# GOAL Prompt: TES TTS TTS-032 Roadmap Compaction And Agent Default Language Contract

This prompt is archived. The active execution prompt is
`docs/roadmap/goals/prompts/tes-tts/GOAL-PROMPT-tes-tts-CAP-001-portable-capability-migration.md`.

```text
/goal Continue TES TTS sequential convergence.

Canonical artifact:
docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-tes-tts-sequential-convergence.md

Current unit:
TTS-032 Roadmap Compaction And Agent Default Language Contract

Certified evidence from prior cycle:
- TTS-031 re-read ADR 0004, all previous TES TTS owner decision records from
  TTS-010 onward, the TTS-009 decision record, the TES TTS roadmap, the Super
  SPEC, and the TTS-031 prompt.
- TTS-031 found no explicit maintainer decision in the current goal context to
  accept ADR 0004 or keep it proposed, authorize release identity planning or
  defer it, or continue forbidding sync or authorize a later sync cycle.
- TTS-031 recorded the owner decision remains open yet again result at
  `docs/roadmap/tes-tts/TES-TTS-OWNER-DECISION-REMAINS-OPEN-YET-AGAIN.md`.
- TTS-031 updated `docs/roadmap/tes-tts/TES-TTS-SKILL-ROADMAP.md` with the cycle
  outcome, current unit status, and ready prompt pointer.
- ADR 0004 remains `proposed`.
- Release identity remains deferred.
- Sync remains forbidden.
- No provider install, provider download, real provider probe, global config
  write, durable conversion cache, proactive `speak` behavior, version bump,
  release, push, tag, publish, or sync was performed.
- Ready prompt artifact for TTS-032 exists at
  docs/roadmap/goals/prompts/tes-tts/GOAL-PROMPT-tes-tts-TTS-032-owner-decision-still-open-yet-again.md.
- The repeated owner-decision loop is now classified as non-convergent unless
  the current user message explicitly asks to preserve that stop state again.
- TTS-031 focused oracles passed:
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
Execute only TTS-032 through the circular sequence:
execute -> analyze -> fix -> certify -> create next /goal prompt or close
convergence -> local commit.

Required actions:
1. Run `git status --short --branch --untracked-files=all`.
2. Re-read ADR 0004, roadmap, this Super SPEC, normalization SPECs,
   language-normalization references, selector fixtures, and this TTS-032
   prompt.
3. Keep ADR 0004 proposed unless the current user message explicitly accepts
   it.
4. Keep release identity and sync out of scope unless the current user message
   explicitly authorizes them.
5. Compact `docs/roadmap/README.md` so historical TTS prompts and owner
   records are not shown as active SPECs.
6. Encode the `agent_default_language` selector contract:
   - Codex: `~/.codex/config.toml` `[desktop].localeOverride`;
   - Claude Code: `~/.claude/settings.json` `language`, normalized by TES
     policy;
   - Cursor: explicit User Rules/project rules first; if absent, Codex default
     first and Claude default second.
7. Add or update selector fixture coverage for the Cursor fallback.
8. Update `docs/roadmap/tes-tts/TES-TTS-SKILL-ROADMAP.md` with the cycle outcome,
   current unit status, and ready prompt posture before closure.
9. Certify with fixture schema, TDS, doc-size, and focused TTS validators.
10. Commit the local execution as the final action of the cycle.

Forbidden:
- no sync, release, push, tag, publish, provider install, provider download,
  proactive speak behavior, global config writes, or durable conversion cache.
- no ADR status change, version bump, release identity claim, or sync claim
  without explicit maintainer approval in the current cycle.

Stop states:
BLOCKED, DEGRADED, NEEDS_REVIEW, NEEDS_OWNER_DECISION.
```
