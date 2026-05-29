---
tds_id: roadmap.tes_tts_spec_010_final_audit_and_closure
tds_class: roadmap
status: proposed
consumer: maintainers, tes-tts maintainers, release reviewers, and final auditors
source_of_truth: false
evidence_level: L2
---

# TES TTS SPEC 010: Final Audit And Closure

## Purpose

Run the closing audit for `tes-tts` and decide whether the skill is complete
for the approved scope or remains explicitly degraded/deferred.

## Scope

- Audit ADR, SPECs, roadmap, fixtures, oracles, adapter parity, command
  triggers, provider posture, and release identity.
- Confirm no proactive `speak` behavior entered `tes-tts`.
- Confirm no durable conversion cache, global provider registry, provider
  install, provider download, or global config write was introduced.
- Close or name the exact next unresolved decision.

## Audit Matrix

| Area | Required result |
|------|-----------------|
| ADR 0004 | Accepted or explicitly proposed/deferred. |
| SPEC 001-009 | Complete, deferred with reason, or blocked with owner decision. |
| fixtures | First-class languages and negative cases covered for claimed scope. |
| oracles | Focused TTS oracles pass. |
| adapters | Codex and Claude source parity holds; Cursor docs stay honest. |
| release | Version/bundle/sync posture is explicit. |
| privacy | Secrets are redacted before speech/provider stages. |
| behavior | No summary unless requested; `tes-tts` remains reactive. |

## Deliverables

- Final audit record.
- Roadmap closure update.
- Owner-facing closure statement.
- Next prompt only if a real unresolved unit remains.

## Oracles

```bash
python3 scripts/tes_tts_fixture_schema_oracle.py --self-test
python3 scripts/tes_tts_instruction_normalizer_oracle.py --self-test
python3 scripts/tes_tts_provider_probe_oracle.py --self-test
python3 scripts/tes_tts_provider_candidate_review_oracle.py --self-test
python3 /Users/murillo/.codex/skills/.system/skill-creator/scripts/quick_validate.py src/adapters/codex/skills/tes-tts
python3 /Users/murillo/.codex/skills/.system/skill-creator/scripts/quick_validate.py src/adapters/claude/skills/tes-tts
python3 scripts/materialize_adapter.py all --check
python3 scripts/command_trigger_oracle.py --self-test
python3 scripts/validate_tds.py
python3 scripts/validate_doc_size.py
python3 scripts/validate_reference_graph.py
python3 scripts/validate_reference_package.py
npm run commit:check
```

## Exit Criteria

- The approved `tes-tts` scope is either complete and ready for the authorized
  release path, or explicitly degraded/deferred with the next decision named.
- The final audit does not perform sync, push, tag, publish, or release unless
  a separate owner-authorized release cycle says so.
