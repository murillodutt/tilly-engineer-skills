---
tds_id: roadmap.goal_prompt_tes_tts_pso_007_final_optimization_audit
tds_class: roadmap
status: active
consumer: maintainers, tes-tts maintainers, runtime authors, provider authors, validation authors, and execution agents
source_of_truth: false
evidence_level: L2
---

# GOAL Prompt: TES TTS PSO-007 Final Optimization Audit

```text
/goal Continue TES TTS Python script optimization.

Canonical artifact:
docs/roadmap/GOAL-SUPER-SPEC-tes-tts-python-script-optimization.md

Current unit:
PSO-007 Final optimization audit

Line fidelity:
- Execute only PSO-007 from the PSO sequence.
- Do not create a competing Super SPEC, new roadmap line, or documentation-only
  cycle.
- Close this PSO line only if executable evidence proves the active
  direct/resident path is stable, measurable, cache-safe, and no longer
  governed by obsolete server assumptions.

Certified evidence from prior cycle:
- PSO-001 extracted the active direct/resident OmniVoice kernel into
  `scripts/tes_tts_omnivoice_direct_kernel.py`.
- PSO-002 made short `speak` run in-process through the direct kernel when the
  current interpreter is already the resolved provider Python.
- PSO-003 quarantined server routes as legacy/lab compatibility.
- PSO-004 split audio-lab metadata between active direct/resident recipes and
  legacy server experiments.
- PSO-005 partitioned the provider oracle around source safety, provider
  status, active direct kernel, legacy server compatibility, dry-run packaging,
  and fixture contract.
- PSO-006 clarified timing names while keeping compatibility aliases:
  `text_prepare_ms`, `provider_synthesis_ms`, `audio_write_ms`,
  `combine_wall_ms`, `playback_wall_ms`, and `total_wall_ms`.
- PSO-006 generated no audio because active direct/resident audio output was
  not changed.
- Release identity, sync, provider installs, provider downloads, provider
  certification, durable conversion cache, global config writes, version bump,
  bundle generation, and proactive `speak` behavior remain unauthorized.
- Sync status is REMOTE_SYNC_NOT_REQUESTED.

Task:
Execute only PSO-007 through:
execute -> analyze -> fix -> certify -> close PSO convergence or create exact
next /goal prompt -> local commit.

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
4. Execute PSO-007 only:
   - audit PSO-001 through PSO-006 for latency, code-size, command-count,
     cache privacy, timing clarity, server legacy isolation, and audio-quality
     risk;
   - confirm whether this Python optimization line can close locally or needs
     an exact follow-up prompt;
   - do not optimize server execution or route active reads through server;
   - keep generated audio, caches, model artifacts, downloads, and venvs under
     `tmp/**` only;
   - preserve source immutability, request-local spoken text, secret redaction,
     exact islands, code no-execute posture, no-summary behavior, and protected
     voice prompt cache permissions.
5. Analyze the diff for audit completeness, active-route coverage, false-green
   risk, cache privacy, and line fidelity.
6. Fix only observed PSO-007 defects.
7. Certify with:
   - `python3 -m compileall -q scripts/tes_tts_omnivoice_provider.py scripts/tes_tts_omnivoice_direct_kernel.py scripts/tes_tts_omnivoice_provider_oracle.py scripts/tes_tts_runtime_latency_oracle.py`
   - `python3 scripts/tes_tts_omnivoice_provider_oracle.py --self-test`
   - `python3 scripts/tes_tts_runtime_latency_oracle.py --self-test`
   - focused dry-runs needed by the audit
   - `python3 scripts/materialize_adapter.py all --check`
   - `python3 scripts/validate_tds.py`
   - `python3 scripts/validate_doc_size.py`
   - `python3 scripts/tes_tts_roadmap_partition_oracle.py`
   - `git diff --check`
   Generate no audio unless audit evidence requires one for active
   direct/resident quality risk.
8. Update `docs/roadmap/TES-TTS-SKILL-ROADMAP.md` with PSO-007 closure state
   or next prompt pointer by registry reference, and sync status.
9. Stage only PSO-007 files, roadmap/index updates, and any exact next prompt
   artifact if needed.
10. Commit locally as the final shell action of the cycle.

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
- final optimization audit outcome;
- focused oracles and result;
- local comparison WAV path when generated, explicitly under `tmp/**`;
- closure statement or next prompt artifact;
- local commit hash;
- sync status: REMOTE_SYNC_NOT_REQUESTED unless explicitly authorized.
```
