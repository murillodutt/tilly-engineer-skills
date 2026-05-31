---
tds_id: roadmap.goal_prompt_tes_tts_rto_005_instruction_normalizer_runtime_alignment
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
RTO-005 Instruction Normalizer Runtime Alignment

Certified evidence from prior cycle:
- RTO-001 split direct/resident runtime support from the provider facade.
- RTO-002 partitioned provider oracle checks around active direct/resident,
  legacy purge, and dry-run packaging surfaces.
- RTO-003 added explicit timing attribution to active direct/resident payloads.
- RTO-004 added direct-kernel boundary coverage proving the kernel owns only
  optional dependency loading, device/model selection, protected prompt cache,
  text preparation delegation, and synthesis metrics.
- No audio was generated; no provider install, download, certification, sync,
  release, push, tag, publish, global write, durable cache, or proactive speak
  was performed.

Task:
Execute only RTO-005 through:
execute -> analyze -> fix -> certify -> create next /goal prompt or close ->
local commit.

Required actions:
1. Run `git status --short --branch --untracked-files=all`.
2. Re-read:
   - `docs/roadmap/TES-TTS-RUNTIME-PYTHON-OPTIMIZATION-AUDIT.md`
   - `docs/roadmap/GOAL-PROMPT-tes-tts-RTO-004-direct-kernel-boundary-hardening.md`
   - `docs/roadmap/TES-TTS-SKILL-ROADMAP.md`
   - `scripts/tes_tts_instruction_normalizer_oracle.py`
   - `scripts/tes_tts_runtime_ir_oracle.py`
   - `scripts/tes_tts_fast_path_spoken_rendering_oracle.py`
   - `scripts/tes_tts_runtime_adapter.py`
3. Execute RTO-005 only:
   - align instruction-normalizer coverage with the current runtime IR and
     spoken-rendering path;
   - remove or collapse duplicated assertions that now belong to runtime IR,
     fast-path rendering, lexical, or provider oracles;
   - preserve regressions for source immutability, request-local speech,
     redaction, exact islands, no-summary behavior, protected technical terms,
     and code no-execute posture;
   - keep behavior unchanged unless an oracle exposes a real current-runtime
     defect.
4. Analyze the diff for false-green risk, duplicated coverage, runtime claim
   drift, privacy, and line fidelity.
5. Fix only observed RTO-005 defects.
6. Certify with:
   - `python3 -m compileall -q scripts/tes_tts_instruction_normalizer_oracle.py scripts/tes_tts_runtime_ir_oracle.py scripts/tes_tts_fast_path_spoken_rendering_oracle.py scripts/tes_tts_runtime_adapter.py`
   - `python3 scripts/tes_tts_instruction_normalizer_oracle.py --self-test`
   - `python3 scripts/tes_tts_runtime_ir_oracle.py --self-test`
   - `python3 scripts/tes_tts_fast_path_spoken_rendering_oracle.py --self-test`
   - `python3 scripts/tes_tts_runtime_latency_oracle.py --self-test`
   - `python3 scripts/materialize_adapter.py all --check`
   - `python3 scripts/tes_tts_roadmap_partition_oracle.py`
   - `python3 scripts/validate_tds.py`
   - `git diff --check`
   - `git diff --cached --check`
7. Create the next exact RTO `/goal` prompt before closure unless the
   optimization line closes.
8. Update `docs/roadmap/TES-TTS-SKILL-ROADMAP.md` with RTO-005 outcome,
   next prompt pointer, and sync status only if the dashboard state changes.
9. Stage only RTO-005 files and commit locally as the final shell action.

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
- instruction-normalizer alignment outcome;
- focused oracles and result;
- local comparison WAV path when generated, explicitly under `tmp/**`;
- next prompt artifact or closure statement;
- local commit hash;
- sync status: REMOTE_SYNC_NOT_REQUESTED unless explicitly authorized.
