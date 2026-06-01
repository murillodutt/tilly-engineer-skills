---
tds_id: roadmap.goal_prompt_tes_tts_rto_004_direct_kernel_boundary_hardening
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
RTO-004 Direct Kernel Boundary Hardening

Certified evidence from prior cycle:
- RTO-001 split direct/resident runtime support into
  `scripts/tes_tts_omnivoice_runtime_support.py`.
- RTO-002 focused the provider oracle around shared JSON subprocess execution,
  table-driven dry-run collection, and runtime-support boundary coverage.
- RTO-003 added explicit timing attribution metadata to active direct/resident
  dry-run and runtime payloads while preserving existing timing fields and
  provider/playback separation.
- RTO-003 kept provider/playback timing separate from TES text preparation,
  preserved latency-profile fields and timing aliases, and generated no audio.
- Sync, release, push, tag, publish, provider install, provider download,
  provider certification, global config writes, durable conversion cache,
  committed audio/cache/model/venv, and proactive `speak` remain unauthorized.

Task:
Execute only RTO-004 through:
execute -> analyze -> fix -> certify -> create next /goal prompt or close ->
local commit.

Required actions:
1. Run `git status --short --branch --untracked-files=all`.
2. Re-read:
   - `docs/roadmap/tes-tts/TES-TTS-RUNTIME-PYTHON-OPTIMIZATION-AUDIT.md`
   - `docs/roadmap/goals/prompts/tes-tts/GOAL-PROMPT-tes-tts-RTO-003-timing-attribution-cleanup.md`
   - `docs/roadmap/tes-tts/TES-TTS-SKILL-ROADMAP.md`
   - `scripts/tes_tts_omnivoice_direct_kernel.py`
   - `scripts/tes_tts_omnivoice_provider.py`
   - `scripts/tes_tts_omnivoice_runtime_support.py`
   - `scripts/tes_tts_omnivoice_provider_oracle.py`
3. Execute RTO-004 only:
   - harden the direct kernel boundary so it owns only optional dependency
     loading, model/device selection, protected voice prompt cache, text
     preparation delegation, and synthesis metrics;
   - keep CLI, review, packaging, playback, combine, subprocess/session
     control, and roadmap concerns outside the direct kernel;
   - add or focus oracle coverage for the direct kernel boundary if the
     current coverage is indirect;
   - preserve direct/resident behavior, timing attribution, source
     immutability, request-local spoken text, secret redaction, exact islands,
     code no-execute posture, and no-summary behavior;
   - do not generate audio unless dry-run/static coverage cannot certify the
     changed boundary.
4. Analyze the diff for boundary clarity, false-green risk, runtime hot-path
   cost, optional dependency leakage, cache privacy, oracle clarity, and line
   fidelity.
5. Fix only observed RTO-004 defects.
6. Certify with:
   - `python3 -m compileall -q scripts/tes_tts_omnivoice_direct_kernel.py scripts/tes_tts_omnivoice_provider.py scripts/tes_tts_omnivoice_runtime_support.py scripts/tes_tts_omnivoice_provider_oracle.py`
   - `python3 scripts/tes_tts_omnivoice_provider_oracle.py --self-test`
   - the smallest affected direct/resident or package dry-run checks;
   - `python3 scripts/tes_tts_runtime_latency_oracle.py --self-test`
   - `python3 scripts/materialize_adapter.py all --check`
   - `python3 scripts/tes_tts_roadmap_partition_oracle.py`
   - `python3 scripts/validate_tds.py`
   - `git diff --check`
   - `git diff --cached --check`
   - `npm run commit:check` only if touched surfaces require package closure.
7. Create the next exact RTO `/goal` prompt before closure unless the
   optimization line closes.
8. Update `docs/roadmap/tes-tts/TES-TTS-SKILL-ROADMAP.md` with RTO-004 outcome,
   next prompt pointer, and sync status only if the dashboard state changes.
9. Stage only RTO-004 files and commit locally as the final shell action.

Forbidden:
- no sync, release, push, tag, publish, provider install, provider download,
  provider certification, proactive speak behavior, global config writes,
  durable conversion cache, version bump, bundle generation, runtime dependency
  import at module import time, full dictionary vendoring, committed audio,
  committed cache, committed model artifact, committed venv, command execution
  from spoken content, user-text summary without explicit request, obsolete
  route resurrection, lab execution copy resurrection, server route
  resurrection as product path, or unrelated `.agents/**` changes.

Stop states:
PASS, DEGRADED, PERFORMANCE_REGRESSION, QUALITY_REGRESSION, NEEDS_REVIEW,
SAFETY_BLOCKED, BLOCKED.

Required closeout:
- changed files;
- direct kernel boundary outcome;
- focused oracles and result;
- local comparison WAV path when generated, explicitly under `tmp/**`;
- next prompt artifact or closure statement;
- local commit hash;
- sync status: REMOTE_SYNC_NOT_REQUESTED unless explicitly authorized.
