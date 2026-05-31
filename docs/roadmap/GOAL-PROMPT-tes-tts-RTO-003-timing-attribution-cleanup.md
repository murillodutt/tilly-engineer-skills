---
tds_id: roadmap.goal_prompt_tes_tts_rto_003_timing_attribution_cleanup
tds_class: roadmap
status: active
consumer: maintainers, tes-tts maintainers, adapter authors, validation authors, and execution agents
source_of_truth: false
evidence_level: L2
---

/goal Continue TES TTS runtime Python optimization.

Canonical artifact:
docs/roadmap/TES-TTS-RUNTIME-PYTHON-OPTIMIZATION-AUDIT.md

Current unit:
RTO-003 Timing Attribution Cleanup

Certified evidence from prior cycle:
- RTO-001 split direct/resident runtime support into
  `scripts/tes_tts_omnivoice_runtime_support.py`.
- RTO-002 focused the provider oracle with a shared JSON subprocess helper,
  table-driven dry-run collection, and explicit runtime-support boundary
  coverage.
- RTO-002 preserved provider CLI names, JSON payload shape, exit-code
  semantics, direct/resident behavior, package/review coverage, and obsolete
  server/lab purge safety coverage.
- RTO-002 generated no audio because dry-run and static payload checks were
  enough to certify the oracle change.
- Sync, release, push, tag, publish, provider install, provider download,
  provider certification, global config writes, durable conversion cache,
  committed audio/cache/model/venv, and proactive `speak` remain unauthorized.

Task:
Execute only RTO-003 through:
execute -> analyze -> fix -> certify -> create next /goal prompt or close ->
local commit.

Required actions:
1. Run `git status --short --branch --untracked-files=all`.
2. Re-read:
   - `docs/roadmap/TES-TTS-RUNTIME-PYTHON-OPTIMIZATION-AUDIT.md`
   - `docs/roadmap/GOAL-PROMPT-tes-tts-RTO-002-provider-oracle-partition.md`
   - `docs/roadmap/TES-TTS-SKILL-ROADMAP.md`
   - `scripts/tes_tts_omnivoice_provider.py`
   - `scripts/tes_tts_omnivoice_runtime_support.py`
   - `scripts/tes_tts_omnivoice_provider_oracle.py`
   - `scripts/tes_tts_runtime_latency_oracle.py`
3. Execute RTO-003 only:
   - clarify provider timing attribution for active direct/resident dry-run
     and runtime payloads without changing synthesis behavior;
   - keep provider/playback timing separate from TES text preparation timing;
   - preserve latency-profile fields, provider prepare fields, generation/
     synthesis timing aliases, combine/playback exclusion semantics, and
     package/review compatibility;
   - add or focus oracle coverage only where timing attribution is ambiguous;
   - do not generate audio unless dry-run/static payload checks cannot certify
     a changed timing surface.
4. Analyze the diff for timing usefulness, false-green risk, payload drift,
   runtime hot-path cost, oracle clarity, privacy, and line fidelity.
5. Fix only observed RTO-003 defects.
6. Certify with:
   - `python3 -m compileall -q scripts/tes_tts_omnivoice_provider.py scripts/tes_tts_omnivoice_runtime_support.py scripts/tes_tts_omnivoice_provider_oracle.py scripts/tes_tts_runtime_latency_oracle.py`
   - `python3 scripts/tes_tts_omnivoice_provider_oracle.py --self-test`
   - `python3 scripts/tes_tts_runtime_latency_oracle.py --self-test`
   - the smallest affected direct/resident or package dry-run checks;
   - `python3 scripts/materialize_adapter.py all --check`
   - `python3 scripts/tes_tts_roadmap_partition_oracle.py`
   - `python3 scripts/validate_tds.py`
   - `git diff --check`
   - `git diff --cached --check`
   - `npm run commit:check` only if touched surfaces require package closure.
7. Create the next exact RTO `/goal` prompt before closure unless the
   optimization line closes.
8. Update `docs/roadmap/TES-TTS-SKILL-ROADMAP.md` with RTO-003 outcome,
   next prompt pointer, and sync status only if the dashboard state changes.
9. Stage only RTO-003 files and commit locally as the final shell action.

Forbidden:
- no sync, release, push, tag, publish, provider install, provider download,
  provider certification, proactive speak behavior, global config writes,
  durable conversion cache, version bump, bundle generation, runtime dependency
  import, full dictionary vendoring, committed audio, committed cache,
  committed model artifact, committed venv, command execution from spoken
  content, user-text summary without explicit request, obsolete route
  resurrection, lab execution copy resurrection, server route resurrection as
  product path, timing claims from provider/playback when only text-prep was
  measured, or unrelated `.agents/**` changes.

Stop states:
PASS, DEGRADED, PERFORMANCE_REGRESSION, QUALITY_REGRESSION, NEEDS_REVIEW,
SAFETY_BLOCKED, BLOCKED.

Required closeout:
- changed files;
- timing attribution outcome;
- focused oracles and result;
- local comparison WAV path when generated, explicitly under `tmp/**`;
- next prompt artifact or closure statement;
- local commit hash;
- sync status: REMOTE_SYNC_NOT_REQUESTED unless explicitly authorized.
