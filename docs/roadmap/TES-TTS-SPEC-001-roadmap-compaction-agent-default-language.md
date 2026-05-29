---
tds_id: roadmap.tes_tts_spec_001_roadmap_compaction_agent_default_language
tds_class: roadmap
status: active
consumer: maintainers, tes-tts maintainers, adapter authors, and execution agents
source_of_truth: false
evidence_level: L2
---

# TES TTS SPEC 001: Roadmap Compaction And Agent Default Language

## Purpose

End the non-convergent owner-decision preservation loop and make
`agent_default_language` executable as selector policy.

## Scope

- Compact roadmap index noise so historical TTS prompts are not active SPECs.
- Keep ADR 0004 `proposed` unless explicitly accepted.
- Keep release identity and sync out of scope.
- Define the default-language source order for Codex, Claude Code, and Cursor.

## Contract

Default-language selector precedence:

1. Explicit user language.
2. Active adapter declaration.
3. Cursor fallback to Codex default.
4. Cursor fallback to Claude default.
5. Request language.
6. Dominant text language.
7. Preserve original.

Adapter declarations:

| Adapter | Source | Handling |
|---------|--------|----------|
| Codex | `~/.codex/config.toml` -> `[desktop].localeOverride` | Use the locale directly. |
| Claude Code | `~/.claude/settings.json` -> `language` | Normalize by TES policy; `Portuguese` maps to `pt-BR`. |
| Cursor | Explicit User Rules or project rules | If absent, Codex first, then Claude. |

## Deliverables

- Updated language references for Codex and Claude skill source.
- Updated normalization architecture and execution SPECs.
- Selector fixture for Cursor fallback.
- Roadmap and roadmap index compaction.

## Oracles

```bash
python3 scripts/tes_tts_fixture_schema_oracle.py --self-test
python3 scripts/validate_tds.py
python3 scripts/validate_doc_size.py
python3 /Users/murillo/.codex/skills/.system/skill-creator/scripts/quick_validate.py src/adapters/codex/skills/tes-tts
python3 /Users/murillo/.codex/skills/.system/skill-creator/scripts/quick_validate.py src/adapters/claude/skills/tes-tts
```

## Exit Criteria

- The TTS roadmap no longer treats repeated owner-decision prompts as active
  execution SPECs.
- `tts-dls-006` proves Cursor fallback to Codex then Claude.
- No release, sync, provider install, global config write, or durable cache is
  introduced.

## SPEC-001 Result

Status: `PASS`.

SPEC-001 is complete when the focused oracles in the execution prompt pass and
the local commit records the scoped TTS changes. The next unit is SPEC-002
Fixture Corpus Complete.
