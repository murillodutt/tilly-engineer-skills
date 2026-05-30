---
tds_id: roadmap.goal_prompt_tes_tts_pso_002_short_read_path_unification
tds_class: roadmap
status: active
consumer: maintainers, tes-tts maintainers, runtime authors, provider authors, validation authors, and execution agents
source_of_truth: false
evidence_level: L2
---

# GOAL Prompt: TES TTS PSO-002 Short-Read Path Unification

```text
/goal Continue TES TTS Python script optimization.

Canonical artifact:
docs/roadmap/GOAL-SUPER-SPEC-tes-tts-python-script-optimization.md

Current unit:
PSO-002 Short-read path unification

Line fidelity:
- Execute only PSO-002 from the PSO sequence.
- Do not skip, rename, merge, or reorder PSO-003 through PSO-007.
- Do not create a competing Super SPEC, new roadmap line, or documentation-only
  cycle.
- Before closure, create the exact next `/goal` prompt for PSO-003 Server
  legacy quarantine unless PSO-002 stops in a non-PASS state.

Certified evidence from prior cycle:
- PSO-001 extracted the active direct/resident OmniVoice kernel into
  `scripts/tes_tts_omnivoice_direct_kernel.py`.
- `scripts/tes_tts_omnivoice_provider.py` remains the CLI/server/lab facade.
- Active `prepare-prompt`, `synthesize`, `batch`, and `serve` execution now
  route model load, protected voice prompt cache, prepared text synthesis, and
  audio writing through the direct kernel.
- Server commands were not redesigned or promoted back into the product path.
- Local comparison WAV was generated under
  `tmp/tes-tts-omnivoice-provider/pso-001-comparison/combined.wav` with
  `status: PASS`, `language=en`, `quality`, one chunk, voice prompt cache
  `hit`, `model_load_ms: 909.204`, `generation_ms: 11161.005`, and
  `avg_rtf: 0.7064`.
- Focused PSO-001 gates passed:
  - `python3 -m compileall -q scripts/tes_tts_omnivoice_provider.py scripts/tes_tts_omnivoice_direct_kernel.py scripts/tes_tts_omnivoice_provider_oracle.py`
  - `python3 scripts/tes_tts_omnivoice_provider_oracle.py --self-test`
  - `python3 scripts/tes_tts_runtime_latency_oracle.py --self-test`
  - `python3 scripts/tes_tts_instruction_normalizer_oracle.py --self-test`
  - `python3 scripts/tes_tts_fixture_schema_oracle.py --self-test`
- Release identity, sync, provider installs, provider downloads, provider
  certification, durable conversion cache, global config writes, version bump,
  bundle generation, and proactive `speak` behavior remain unauthorized.
- Sync status is REMOTE_SYNC_NOT_REQUESTED.

Task:
Execute only PSO-002 through:
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
4. Execute PSO-002 only:
   - make the short `speak` path use the direct kernel path more directly or
     share the same resident/direct implementation boundary where practical;
   - remove avoidable extra CLI/process/model churn for repeated short reads
     when this can be done without changing public CLI semantics;
   - preserve current `speak` JSON dry-run shape unless an oracle is updated
     with a deliberate compatibility decision;
   - do not redesign `speak-long`; it is already the product hot path;
   - do not touch or improve obsolete server execution;
   - keep generated audio, caches, model artifacts, downloads, and venvs under
     `tmp/**` only;
   - preserve source immutability, request-local spoken text, secret redaction,
     exact islands, code no-execute posture, no-summary behavior, and protected
     voice prompt cache permissions.
5. Analyze the diff for short-read latency direction, CLI compatibility,
   resident/direct boundary reuse, cache privacy, audio-quality risk,
   false-green risk, and line fidelity.
6. Fix only observed PSO-002 defects.
7. Certify with the smallest relevant set:
   - `python3 -m compileall -q scripts/tes_tts_omnivoice_provider.py scripts/tes_tts_omnivoice_direct_kernel.py`
   - `python3 scripts/tes_tts_omnivoice_provider_oracle.py --self-test`
   - `python3 scripts/tes_tts_runtime_latency_oracle.py --self-test`
   - `python3 scripts/tes_tts_instruction_normalizer_oracle.py --self-test`
   - `python3 scripts/tes_tts_fixture_schema_oracle.py --self-test`
   - `python3 scripts/materialize_adapter.py all --check`
   - `python3 scripts/validate_tds.py`
   - `python3 scripts/validate_doc_size.py`
   - `python3 scripts/tes_tts_roadmap_partition_oracle.py`
   - `git diff --check`
   Generate one local short-read comparison WAV under `tmp/**` if short-read
   runtime behavior changes beyond dry-run routing.
8. Create the next exact PSO `/goal` prompt for PSO-003 Server legacy
   quarantine before closure.
9. Update `docs/roadmap/TES-TTS-SKILL-ROADMAP.md` with PSO-002 outcome, next
   prompt pointer by registry reference, and sync status.
10. Stage only PSO-002 files, roadmap/index updates, and the PSO-003 prompt
    artifact.
11. Commit locally as the final shell action of the cycle.

Forbidden:
- no sync, release, push, tag, publish, provider install, provider download,
  provider certification, proactive speak behavior, global config writes,
  durable conversion cache, version bump, bundle generation, runtime dependency
  import, full dictionary vendoring, committed audio, committed cache, committed
  model artifact, committed venv, command execution from spoken content,
  user-text summary without explicit request, server route resurrection as
  product path, or unrelated `.agents/**` changes without explicit current-cycle
  owner approval.

Stop states:
PASS, DEGRADED, PERFORMANCE_REGRESSION, QUALITY_REGRESSION, NEEDS_REVIEW,
SAFETY_BLOCKED, BLOCKED.

Required closeout:
- changed files;
- short-read path boundary outcome;
- focused oracles and result;
- local comparison WAV path when generated, explicitly under `tmp/**`;
- next prompt artifact for PSO-003 or stop-state rationale;
- local commit hash;
- sync status: REMOTE_SYNC_NOT_REQUESTED unless explicitly authorized.
```
