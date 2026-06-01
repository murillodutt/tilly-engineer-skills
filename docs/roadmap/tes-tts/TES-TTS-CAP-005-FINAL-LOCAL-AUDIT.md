---
tds_id: roadmap.tes_tts_cap_005_final_local_audit
tds_class: roadmap
status: archived
consumer: maintainers, tes-tts maintainers, adapter authors, and release reviewers
source_of_truth: false
evidence_level: L2
---

# TES TTS CAP-005 Final Local Audit

## Purpose

Close the local `tes-tts` capability migration sequence after CAP-001 through
CAP-004, without authorizing release identity, sync, provider installation,
provider certification, or proactive `speak` behavior.

## Audit Result

Status: `DEGRADED`.

The `tes-tts` migration is locally complete for the approved bounded scope:

- reactive read-aloud only;
- no user-text summary unless explicitly requested;
- source text separated from request-local `spoken_text`;
- secret-like values redacted before speech/provider stages;
- dependency-free spoken rendering for acronyms, paths, URLs, hashes, GUIDs,
  email, IPv4, mentions, hashtags, Markdown, code fences, commands, package
  names, model names, and protected terms;
- provider fallback kept request-local and catalog-based;
- no provider install, provider download, provider certification, global
  unavailable registry, global config write, durable conversion cache, IPA,
  SSML, phoneme, model bundle, library vendoring, release, tag, push, publish,
  or sync.

The local package closure gate remains degraded because unrelated development
skill parity drift exists outside the `tes-tts` scope:

- `tes-high-agency-pattern`;
- `tes-predictive-operations`.

CAP-005 did not modify or stage that unrelated `.agents/**` drift.

## Adapter Parity

Workbench and Codex source are byte-aligned:

```text
diff -qr .agents/skills/tes-tts src/adapters/codex/skills/tes-tts
```

Codex and Claude source are behaviorally aligned. The only observed difference
is the intentional adapter-specific contract-history line that names whether
the original promotion target was Codex or Claude.

## Command Triggers

The command trigger surface includes:

- `/tes-tts`;
- `/tes:tts`;
- `tes tts`;
- `read this text aloud`;
- `leia em voz alta`;
- `narrar este texto`.

The command trigger oracle remains the authority for install/manual/adapter
trigger consistency.

## Certification Set

Focused CAP-005 certification uses:

```bash
python3 scripts/tes_tts_fixture_schema_oracle.py --self-test
python3 scripts/tes_tts_instruction_normalizer_oracle.py --self-test
python3 scripts/tes_tts_provider_probe_oracle.py --self-test
python3 scripts/tes_tts_provider_candidate_review_oracle.py --self-test
python3 /Users/murillo/.codex/skills/.system/skill-creator/scripts/quick_validate.py .agents/skills/tes-tts
python3 /Users/murillo/.codex/skills/.system/skill-creator/scripts/quick_validate.py src/adapters/codex/skills/tes-tts
python3 /Users/murillo/.codex/skills/.system/skill-creator/scripts/quick_validate.py src/adapters/claude/skills/tes-tts
python3 scripts/materialize_adapter.py all --check
python3 scripts/command_trigger_oracle.py --self-test
python3 scripts/validate_tds.py
python3 scripts/validate_doc_size.py
python3 scripts/validate_reference_graph.py
git diff --check
```

`npm run commit:check` and
`python3 scripts/validate_reference_package.py --staged-ready` are package
closure gates. In CAP-005 they are interpreted as degraded if they fail only
because of the unrelated development skill parity drift named above.

## Closure

No next CAP prompt is created. The local capability migration sequence is
closed. Remaining decisions are outside CAP migration:

- release identity planning or continued deferral;
- sync authorization or continued `REMOTE_SYNC_NOT_REQUESTED`.
