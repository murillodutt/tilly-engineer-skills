---
tds_id: roadmap.tes_tts_spec_004_pronunciation_enrichment_rules
tds_class: roadmap
status: proposed
consumer: maintainers, tes-tts maintainers, adapter authors, and validation authors
source_of_truth: false
evidence_level: L2
---

# TES TTS SPEC 004: Pronunciation Enrichment Rules

## Purpose

Improve spoken rendering of protected technical terms without semantic
translation or provider dependency.

## Scope

- Add conservative pronunciation hints for common technical terms.
- Keep visible/source text unchanged.
- Preserve proper nouns, commands, file paths, code identifiers, and acronyms.
- Avoid phoneme/IPA/SSML claims until provider-backed SPECs prove them.

## Initial Term Policy

| Term class | Rule |
|------------|------|
| ADR, MCP, API, SDK, CLI | Read as separate letters unless project policy says otherwise. |
| SPEC | Read as a technical noun. |
| JSON, YAML, SQL | Use common local pronunciation; do not translate. |
| Paths and commands | Speak only relevant parts unless exact reading is requested. |
| Proper nouns | Preserve written identity; add spacing only if TTS would distort it. |

## Deliverables

- Pronunciation hint fixture cases.
- Updated `language-normalization.md` references.
- Instruction normalizer oracle checks for hint generation.

## SPEC-004 Result

Status: `PASS`.

The instruction normalizer oracle now generates conservative pronunciation
hints for ADR, SPEC, MCP, API, SDK, CLI, JSON, YAML, SQL, proper nouns, paths,
and commands while leaving visible speech text unchanged. The oracle rejects
IPA, SSML, phoneme, provider-backed, and translation claims inside hints.
Hebrew and provider-backed pronunciation remain explicitly degraded.

Next ready prompt:
`docs/roadmap/goals/prompts/tes-tts/GOAL-PROMPT-tes-tts-SPEC-005-provider-probe-no-write.md`.

Sync status: `REMOTE_SYNC_NOT_REQUESTED`.

## Oracles

```bash
python3 scripts/tes_tts_instruction_normalizer_oracle.py --self-test
python3 scripts/tes_tts_fixture_schema_oracle.py --self-test
python3 /Users/murillo/.codex/skills/.system/skill-creator/scripts/quick_validate.py src/adapters/codex/skills/tes-tts
python3 /Users/murillo/.codex/skills/.system/skill-creator/scripts/quick_validate.py src/adapters/claude/skills/tes-tts
```

## Exit Criteria

- Protected terms survive and get conservative hints when useful.
- No term is semantically translated into another object.
- Hebrew or provider-backed pronunciation remains degraded unless later SPECs
  certify it.
