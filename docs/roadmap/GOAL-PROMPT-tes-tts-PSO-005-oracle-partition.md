---
tds_id: roadmap.goal_prompt_tes_tts_pso_005_oracle_partition
tds_class: roadmap
status: active
consumer: maintainers, tes-tts maintainers, runtime authors, provider authors, validation authors, and execution agents
source_of_truth: false
evidence_level: L2
---

# GOAL Prompt: TES TTS PSO-005 Oracle Partition

```text
/goal Continue TES TTS Python script optimization.

Canonical artifact:
docs/roadmap/GOAL-SUPER-SPEC-tes-tts-python-script-optimization.md

Current unit:
PSO-005 Oracle partition

Line fidelity:
- Execute only PSO-005 from the PSO sequence.
- Do not skip, rename, merge, or reorder PSO-006 through PSO-007.
- Do not create a competing Super SPEC, new roadmap line, or documentation-only
  cycle.
- Before closure, create the exact next `/goal` prompt for PSO-006 Timing and
  benchmark cleanup unless PSO-005 stops in a non-PASS state.

Certified evidence from prior cycle:
- PSO-001 extracted the active direct/resident OmniVoice kernel into
  `scripts/tes_tts_omnivoice_direct_kernel.py`.
- PSO-002 made short `speak` run in-process through the direct kernel when the
  current interpreter is already the resolved provider Python.
- PSO-003 quarantined server route payloads with
  `route_status: legacy_lab_compatibility`, `product_path:
  direct_resident_omnivoice`, and an explicit legacy reason.
- PSO-004 split audio-lab metadata: resident runs are marked
  `active_direct_resident_audio_recipe`; server runs are marked
  `legacy_server_audio_experiment` with `legacy_lab_compatibility`.
- PSO-004 preserved CLI compatibility and server safety coverage without
  promoting, improving, or routing product reads through server commands.
- PSO-004 generated no audio because active direct/resident audio output was
  not changed.
- Focused PSO-004 gates passed:
  - `python3 -m compileall -q scripts/tes_tts_audio_variant_lab.py scripts/tes_tts_omnivoice_provider.py scripts/tes_tts_omnivoice_direct_kernel.py`
  - `python3 scripts/tes_tts_audio_variant_lab.py self-test`
  - `python3 scripts/tes_tts_audio_variant_lab.py run --chunk-id chunk-001 --variant baseline`
  - `python3 scripts/tes_tts_audio_variant_lab.py run --provider-route server --chunk-id chunk-001 --variant baseline`
- Release identity, sync, provider installs, provider downloads, provider
  certification, durable conversion cache, global config writes, version bump,
  bundle generation, and proactive `speak` behavior remain unauthorized.
- Sync status is REMOTE_SYNC_NOT_REQUESTED.

Task:
Execute only PSO-005 through:
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
   - `scripts/tes_tts_omnivoice_provider_oracle.py`
   - `scripts/tes_tts_omnivoice_provider.py`
   - `scripts/tes_tts_omnivoice_direct_kernel.py`
   - `scripts/tes_tts_audio_variant_lab.py`
4. Execute PSO-005 only:
   - partition or focus provider oracle checks around the extracted boundary:
     active direct kernel, legacy server compatibility, and dry-run packaging;
   - keep active direct/resident checks product-path aligned;
   - keep server checks explicitly legacy/lab and safety-oriented;
   - do not weaken coverage, delete server safety coverage prematurely, or
     promote server execution back into the product path;
   - keep generated audio, caches, model artifacts, downloads, and venvs under
     `tmp/**` only;
   - preserve source immutability, request-local spoken text, secret redaction,
     exact islands, code no-execute posture, no-summary behavior, and protected
     voice prompt cache permissions.
5. Analyze the diff for oracle clarity, active-route coverage, server-lab
   drift, false-green risk, cache privacy, and line fidelity.
6. Fix only observed PSO-005 defects.
7. Certify with the smallest relevant set:
   - `python3 -m compileall -q scripts/tes_tts_omnivoice_provider_oracle.py scripts/tes_tts_omnivoice_provider.py scripts/tes_tts_omnivoice_direct_kernel.py scripts/tes_tts_audio_variant_lab.py`
   - `python3 scripts/tes_tts_omnivoice_provider_oracle.py --self-test`
   - focused direct-kernel, server-legacy, or packaging dry-runs affected by
     this unit
   - `python3 scripts/tes_tts_runtime_latency_oracle.py --self-test`
   - `python3 scripts/materialize_adapter.py all --check`
   - `python3 scripts/validate_tds.py`
   - `python3 scripts/validate_doc_size.py`
   - `python3 scripts/tes_tts_roadmap_partition_oracle.py`
   - `git diff --check`
   Generate no audio unless a change can affect active direct/resident output.
8. Create the next exact PSO `/goal` prompt for PSO-006 Timing and benchmark
   cleanup before closure.
9. Update `docs/roadmap/TES-TTS-SKILL-ROADMAP.md` with PSO-005 outcome, next
   prompt pointer by registry reference, and sync status.
10. Stage only PSO-005 files, roadmap/index updates, and the PSO-006 prompt
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
- oracle partition outcome;
- focused oracles and result;
- local comparison WAV path when generated, explicitly under `tmp/**`;
- next prompt artifact for PSO-006 or stop-state rationale;
- local commit hash;
- sync status: REMOTE_SYNC_NOT_REQUESTED unless explicitly authorized.
```
