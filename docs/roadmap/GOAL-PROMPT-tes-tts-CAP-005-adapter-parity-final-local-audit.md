---
tds_id: roadmap.goal_prompt_tes_tts_cap_005_adapter_parity_final_local_audit
tds_class: roadmap
status: active
consumer: maintainers, tes-tts maintainers, adapter authors, and execution agents
source_of_truth: false
evidence_level: L2
---

# GOAL Prompt: TES TTS CAP-005 Adapter Parity And Final Local Audit

```text
/goal Continue TES TTS capability migration.

Canonical artifact:
docs/roadmap/GOAL-SUPER-SPEC-tes-tts-capability-migration.md

Current unit:
CAP-005 Adapter Parity And Final Local Audit

Certified evidence from prior cycle:
- CAP-004 hardened provider fallback catalog use as request-local guidance.
- CAP-004 added mocked fallback fixtures for catalog order, auth failure,
  rate limit, unavailable provider, unavailable voice retry, generic failure,
  explicit voice preservation, and all-provider failure.
- CAP-004 kept provider behavior dependency-free and did not install,
  download, certify, persist unavailable-provider state, write global config,
  write durable conversion cache, or claim provider support.
- CAP-004 mirrored workbench behavior into Codex and Claude skill references.
- Release identity, sync, provider installs, provider downloads, provider
  certification, durable conversion cache, and proactive `speak` behavior
  remain unauthorized.
- Sync status is REMOTE_SYNC_NOT_REQUESTED.

Task:
Execute only CAP-005 through:
execute -> analyze -> fix -> certify -> close convergence or create the exact
next /goal prompt -> local commit.

Required actions:
1. Run `git status --short --branch --untracked-files=all`.
2. Classify inherited TTS changes and unrelated `.agents/**` drift. Do not
   stage or modify unrelated `.agents/**` changes.
3. Re-read:
   - `docs/roadmap/GOAL-SUPER-SPEC-tes-tts-capability-migration.md`
   - `docs/roadmap/TES-TTS-CAP-001-PORTABLE-CAPABILITY-FEASIBILITY.md`
   - `docs/roadmap/TES-TTS-SKILL-ROADMAP.md`
   - `docs/roadmap/GOAL-PROMPT-tes-tts-CAP-005-adapter-parity-final-local-audit.md`
   - `.agents/skills/tes-tts/**`
   - `src/adapters/codex/skills/tes-tts/**`
   - `src/adapters/claude/skills/tes-tts/**`
   - focused TTS fixtures and oracles under `benchmarks/tes-tts/**` and
     `scripts/tes_tts_*_oracle.py`
4. Audit adapter parity, command triggers, source/workbench drift, no-summary
   behavior, redaction-before-speech, protected terms, request-local
   `spoken_text`, provider fallback posture, and forbidden side effects.
5. Fix only observed CAP-005 defects. Do not broaden scope into release,
   sync, provider install, provider certification, version bump, bundle
   generation, or proactive `speak`.
6. Certify with the focused TTS oracles, workbench and adapter quick
   validation, materialization check, command trigger oracle, TDS/doc-size/
   reference graph validators, `git diff --check`, and package closure gate
   only when unrelated drift does not make it impossible to interpret.
7. If migration convergence is locally complete, update the roadmap with the
   closure state and no next prompt. If an unresolved decision remains, create
   the exact next `/goal` prompt for that decision.
8. Stage only CAP-005 files and commit locally as the final shell action.

Forbidden:
- no sync, release, push, tag, publish, provider install, provider download,
  provider certification, proactive speak behavior, global config writes,
  durable conversion cache, version bump, bundle generation, phoneme output,
  IPA, SSML, model bundle, library vendoring, runtime dependency import, or
  unrelated `.agents/**` changes without explicit current-cycle owner
  approval.

Stop states:
PASS, DEGRADED, NEEDS_REVIEW, NEEDS_OWNER_DECISION, BLOCKED.

Required closeout:
- changed files;
- focused oracles and result;
- next prompt artifact or closure statement;
- local commit hash;
- sync status: REMOTE_SYNC_NOT_REQUESTED unless explicitly authorized.
```
