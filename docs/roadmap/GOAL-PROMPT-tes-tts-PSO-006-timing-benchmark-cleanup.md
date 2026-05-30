---
tds_id: roadmap.goal_prompt_tes_tts_pso_006_timing_benchmark_cleanup
tds_class: roadmap
status: active
consumer: maintainers, tes-tts maintainers, runtime authors, provider authors, validation authors, and execution agents
source_of_truth: false
evidence_level: L2
---

# GOAL Prompt: TES TTS PSO-006 Timing And Benchmark Cleanup

```text
/goal Continue TES TTS Python script optimization.

Canonical artifact:
docs/roadmap/GOAL-SUPER-SPEC-tes-tts-python-script-optimization.md

Current unit:
PSO-006 Timing and benchmark cleanup

Line fidelity:
- Execute only PSO-006 from the PSO sequence.
- Do not skip, rename, merge, or reorder PSO-007.
- Do not create a competing Super SPEC, new roadmap line, or documentation-only
  cycle.
- Before closure, create the exact next `/goal` prompt for PSO-007 Final
  optimization audit unless PSO-006 stops in a non-PASS state.

Certified evidence from prior cycle:
- PSO-001 extracted the active direct/resident OmniVoice kernel into
  `scripts/tes_tts_omnivoice_direct_kernel.py`.
- PSO-002 made short `speak` run in-process through the direct kernel when the
  current interpreter is already the resolved provider Python.
- PSO-003 quarantined server routes as legacy/lab compatibility.
- PSO-004 split audio-lab metadata between active direct/resident recipes and
  legacy server experiments.
- PSO-005 partitioned `scripts/tes_tts_omnivoice_provider_oracle.py` into
  source safety, provider status, active direct kernel, legacy server
  compatibility, dry-run packaging, and fixture-contract checks.
- PSO-005 generated no audio because active direct/resident audio output was
  not changed.
- Release identity, sync, provider installs, provider downloads, provider
  certification, durable conversion cache, global config writes, version bump,
  bundle generation, and proactive `speak` behavior remain unauthorized.
- Sync status is REMOTE_SYNC_NOT_REQUESTED.

Task:
Execute only PSO-006 through:
execute -> analyze -> fix -> certify -> create next /goal prompt -> local
commit.

Required actions:
1. Run `git status --short --branch --untracked-files=all`.
2. Classify inherited TTS changes and unrelated `.agents/**` drift. Do not
   stage or modify unrelated `.agents/**` changes.
3. Re-read:
   - `docs/roadmap/GOAL-SUPER-SPEC-tes-tts-python-script-optimization.md`
   - `docs/roadmap/TES-TTS-PYTHON-SCRIPT-EFFICIENCY-ANALYSIS.md`
   - `docs/roadmap/TES-TTS-SKILL-ROADMAP.md`
   - `scripts/tes_tts_omnivoice_provider.py`
   - `scripts/tes_tts_omnivoice_direct_kernel.py`
   - `scripts/tes_tts_omnivoice_provider_oracle.py`
   - `scripts/tes_tts_runtime_latency_oracle.py`
4. Execute PSO-006 only:
   - clean timing and benchmark names so text preparation, provider
     preparation, model load, voice prompt, synthesis, combine, playback, and
     total wall time are not conflated;
   - keep active direct/resident timing product-path aligned;
   - keep server timing legacy/lab only and do not improve server execution;
   - avoid changing audio recipe behavior unless the timing cleanup requires a
     small metadata fix;
   - keep generated audio, caches, model artifacts, downloads, and venvs under
     `tmp/**` only;
   - preserve source immutability, request-local spoken text, secret redaction,
     exact islands, code no-execute posture, no-summary behavior, and protected
     voice prompt cache permissions.
5. Analyze the diff for timing clarity, active-route coverage, benchmark
   usefulness, false-green risk, cache privacy, and line fidelity.
6. Fix only observed PSO-006 defects.
7. Certify with the smallest relevant set:
   - `python3 -m compileall -q scripts/tes_tts_omnivoice_provider.py scripts/tes_tts_omnivoice_direct_kernel.py scripts/tes_tts_omnivoice_provider_oracle.py scripts/tes_tts_runtime_latency_oracle.py`
   - `python3 scripts/tes_tts_omnivoice_provider_oracle.py --self-test`
   - focused timing or benchmark dry-runs affected by this unit
   - `python3 scripts/tes_tts_runtime_latency_oracle.py --self-test`
   - `python3 scripts/materialize_adapter.py all --check`
   - `python3 scripts/validate_tds.py`
   - `python3 scripts/validate_doc_size.py`
   - `python3 scripts/tes_tts_roadmap_partition_oracle.py`
   - `git diff --check`
   Generate no audio unless a change can affect active direct/resident output.
8. Create the next exact PSO `/goal` prompt for PSO-007 Final optimization
   audit before closure.
9. Update `docs/roadmap/TES-TTS-SKILL-ROADMAP.md` with PSO-006 outcome, next
   prompt pointer by registry reference, and sync status.
10. Stage only PSO-006 files, roadmap/index updates, and the PSO-007 prompt
    artifact.
11. Commit locally as the final shell action of the cycle.

Forbidden:
- no sync, release, push, tag, publish, provider install, provider download,
  provider certification, proactive speak behavior, global config writes,
  durable conversion cache, version bump, bundle generation, runtime dependency
  import, full dictionary vendoring, committed audio, committed cache, committed
  model artifact, committed venv, command execution from spoken content,
  user-text summary without explicit request, server route resurrection as
  product path, server feature expansion, or unrelated `.agents/**` changes
  without explicit current-cycle owner approval.

Stop states:
PASS, DEGRADED, PERFORMANCE_REGRESSION, QUALITY_REGRESSION, NEEDS_REVIEW,
SAFETY_BLOCKED, BLOCKED.

Required closeout:
- changed files;
- timing and benchmark cleanup outcome;
- focused oracles and result;
- local comparison WAV path when generated, explicitly under `tmp/**`;
- next prompt artifact for PSO-007 or stop-state rationale;
- local commit hash;
- sync status: REMOTE_SYNC_NOT_REQUESTED unless explicitly authorized.
```
