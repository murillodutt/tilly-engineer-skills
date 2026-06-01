---
tds_id: roadmap.goal_prompt_tes_tts_rto_002_provider_oracle_partition
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
RTO-002 Provider Oracle Partition

Certified evidence from prior cycle:
- RTO-001 split direct/resident runtime support out of
  `scripts/tes_tts_omnivoice_provider.py` into
  `scripts/tes_tts_omnivoice_runtime_support.py`.
- RTO-001 preserved CLI names, JSON payload shape, direct/resident behavior,
  review/package/benchmark stability, and dry-run behavior.
- RTO-001 generated no audio because direct `speak-long --dry-run` was enough
  to certify the changed product path.
- Focused RTO-001 gates passed: compileall for provider/direct-kernel/oracle/
  runtime-support, provider oracle self-test, direct `speak-long --dry-run`,
  runtime latency oracle, materialization check, roadmap partition oracle,
  TDS validation, and diff whitespace checks.
- Sync, release, push, tag, publish, provider install, provider download,
  provider certification, global config writes, durable conversion cache,
  committed audio/cache/model/venv, and proactive `speak` remain unauthorized.

Task:
Execute only RTO-002 through:
execute -> analyze -> fix -> certify -> create next /goal prompt or close ->
local commit.

Required actions:
1. Run `git status --short --branch --untracked-files=all`.
2. Re-read:
   - `docs/roadmap/tes-tts/TES-TTS-RUNTIME-PYTHON-OPTIMIZATION-AUDIT.md`
   - `docs/roadmap/goals/prompts/tes-tts/GOAL-PROMPT-tes-tts-RTO-001-provider-hot-path-split.md`
   - `docs/roadmap/tes-tts/TES-TTS-SKILL-ROADMAP.md`
   - `scripts/tes_tts_omnivoice_provider_oracle.py`
   - `scripts/tes_tts_omnivoice_provider.py`
   - `scripts/tes_tts_omnivoice_runtime_support.py`
   - `scripts/tes_tts_omnivoice_direct_kernel.py`
3. Execute RTO-002 only:
   - partition or focus the provider oracle around the active direct/resident
     product path, the extracted runtime support boundary, and package/review
     compatibility checks;
   - reduce repeated subprocess, payload, and assertion boilerplate with
     table-driven helpers where it improves clarity;
   - keep active direct/resident checks product-path aligned;
   - keep obsolete server/lab resurrection checks as safety coverage only;
   - preserve coverage, CLI command names, JSON payload shape, exit-code
     semantics, direct/resident behavior, source immutability, request-local
     spoken text, secret redaction, exact islands, code no-execute posture,
     and no-summary behavior;
   - do not generate audio unless a changed oracle path cannot be certified by
     dry-run or static payload checks.
4. Analyze the diff for oracle clarity, false-green risk, product-route
   coverage, obsolete-route drift, privacy, runtime boundary fit, and line
   fidelity.
5. Fix only observed RTO-002 defects.
6. Certify with:
   - `python3 -m compileall -q scripts/tes_tts_omnivoice_provider_oracle.py scripts/tes_tts_omnivoice_provider.py scripts/tes_tts_omnivoice_runtime_support.py scripts/tes_tts_omnivoice_direct_kernel.py`
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
8. Update `docs/roadmap/tes-tts/TES-TTS-SKILL-ROADMAP.md` with RTO-002 outcome,
   next prompt pointer, and sync status only if the dashboard state changes.
9. Stage only RTO-002 files and commit locally as the final shell action.

Forbidden:
- no sync, release, push, tag, publish, provider install, provider download,
  provider certification, proactive speak behavior, global config writes,
  durable conversion cache, version bump, bundle generation, runtime dependency
  import, full dictionary vendoring, committed audio, committed cache,
  committed model artifact, committed venv, command execution from spoken
  content, user-text summary without explicit request, obsolete route
  resurrection, lab execution copy resurrection, server route resurrection as
  product path, or unrelated `.agents/**` changes.

Stop states:
PASS, DEGRADED, PERFORMANCE_REGRESSION, QUALITY_REGRESSION, NEEDS_REVIEW,
SAFETY_BLOCKED, BLOCKED.

Required closeout:
- changed files;
- provider oracle partition outcome;
- focused oracles and result;
- local comparison WAV path when generated, explicitly under `tmp/**`;
- next prompt artifact or closure statement;
- local commit hash;
- sync status: REMOTE_SYNC_NOT_REQUESTED unless explicitly authorized.
