---
tds_id: roadmap.goal_prompt_tes_tts_rto_001_provider_hot_path_split
tds_class: roadmap
status: active
consumer: maintainers, tes-tts maintainers, adapter authors, validation authors, and execution agents
source_of_truth: false
evidence_level: L2
---

/goal Continue TES TTS runtime Python optimization.

Canonical artifact:
docs/roadmap/tes-tts/TES-TTS-RUNTIME-PYTHON-OPTIMIZATION-AUDIT.md

Current unit:
RTO-001 Provider Hot Path Split

Certified evidence from prior cycle:
- Obsolete tracked lab execution copies were purged.
- The active `tes-tts` provider path is direct/resident OmniVoice only.
- `scripts/tes_tts_audio_variant_lab.py` was deleted.
- Server/lab commands are absent from `tes_tts_omnivoice_provider.py` CLI help.
- The provider oracle contains `server_lab_purge` coverage to prevent route
  resurrection.
- `npm run commit:check` passed after the purge.
- Local commit `c131a08` recorded the cleanup.
- Sync, release, push, tag, publish, provider install, provider download,
  provider certification, global config writes, durable conversion cache,
  committed audio, and proactive `speak` remain unauthorized.

Task:
Execute only RTO-001 through:
execute -> analyze -> fix -> certify -> create next /goal prompt or close ->
local commit.

Required actions:
1. Run `git status --short --branch --untracked-files=all`.
2. Re-read:
   - `docs/roadmap/tes-tts/TES-TTS-RUNTIME-PYTHON-OPTIMIZATION-AUDIT.md`
   - `docs/roadmap/tes-tts/TES-TTS-SKILL-ROADMAP.md`
   - `scripts/tes_tts_omnivoice_provider.py`
   - `scripts/tes_tts_omnivoice_direct_kernel.py`
   - `scripts/tes_tts_omnivoice_provider_oracle.py`
   - `.agents/skills/tes-tts/SKILL.md`
   - `src/adapters/codex/skills/tes-tts/SKILL.md`
   - `src/adapters/claude/skills/tes-tts/SKILL.md`
3. Execute RTO-001 only:
   - split the smallest durable product-path helper module from
     `tes_tts_omnivoice_provider.py`;
   - prioritize helpers used by `speak`, `speak-long`, `session`, and
     `product-status`;
   - preserve CLI command names, JSON payload shape, exit-code semantics,
     direct/resident behavior, protected voice prompt cache permissions,
     source immutability, request-local spoken text, secret redaction,
     exact islands, code no-execute posture, and no-summary behavior;
   - keep review UI, package-review, benchmark, and candidate surfaces stable;
   - do not generate audio unless a changed product-path behavior cannot be
     certified by dry-run.
4. Analyze the diff for runtime clarity, hot-path latency risk, false-green
   risk, oracle coverage, adapter parity, privacy, and boundary drift.
5. Fix only observed RTO-001 defects.
6. Certify with:
   - `python3 -m compileall -q scripts/tes_tts_omnivoice_provider.py scripts/tes_tts_omnivoice_direct_kernel.py scripts/tes_tts_omnivoice_provider_oracle.py`
   - `python3 scripts/tes_tts_omnivoice_provider_oracle.py --self-test`
   - a direct `speak-long --dry-run` using the canonical local reference env
     when available;
   - `python3 scripts/tes_tts_runtime_latency_oracle.py --self-test`
   - `python3 scripts/materialize_adapter.py all --check`
   - `python3 scripts/tes_tts_roadmap_partition_oracle.py`
   - `python3 scripts/validate_tds.py`
   - `git diff --check`
   - `git diff --cached --check`
   - `npm run commit:check` only if touched surfaces require package closure.
7. Create the next exact RTO `/goal` prompt before closure unless the
   optimization line closes.
8. Update `docs/roadmap/tes-tts/TES-TTS-SKILL-ROADMAP.md` with RTO-001 outcome,
   next prompt pointer, and sync status only if the dashboard state changes.
9. Stage only RTO-001 files and commit locally as the final shell action.

Forbidden:
- no sync, release, push, tag, publish, provider install, provider download,
  provider certification, proactive speak behavior, global config writes,
  durable conversion cache, version bump, bundle generation, runtime dependency
  import, full dictionary vendoring, committed audio, committed cache,
  committed model artifact, committed venv, command execution from spoken
  content, user-text summary without explicit request, obsolete route
  resurrection, lab execution copy resurrection, or unrelated `.agents/**`
  changes.

Stop states:
PASS, DEGRADED, PERFORMANCE_REGRESSION, QUALITY_REGRESSION, NEEDS_REVIEW,
SAFETY_BLOCKED, BLOCKED.

Required closeout:
- changed files;
- provider hot-path split outcome;
- focused oracles and result;
- local comparison WAV path when generated, explicitly under `tmp/**`;
- next prompt artifact or closure statement;
- local commit hash;
- sync status: REMOTE_SYNC_NOT_REQUESTED unless explicitly authorized.
