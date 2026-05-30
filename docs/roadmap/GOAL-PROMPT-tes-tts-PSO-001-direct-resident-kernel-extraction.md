---
tds_id: roadmap.goal_prompt_tes_tts_pso_001_direct_resident_kernel_extraction
tds_class: roadmap
status: active
consumer: maintainers, tes-tts maintainers, runtime authors, provider authors, validation authors, and execution agents
source_of_truth: false
evidence_level: L2
---

# GOAL Prompt: TES TTS PSO-001 Direct/Resident Kernel Extraction

```text
/goal Continue TES TTS Python script optimization.

Canonical artifact:
docs/roadmap/GOAL-SUPER-SPEC-tes-tts-python-script-optimization.md

Current unit:
PSO-001 Direct/resident kernel extraction

Line fidelity:
- Execute only PSO-001 from the PSO sequence.
- Do not skip, rename, merge, or reorder PSO-002 through PSO-007.
- Do not create a competing Super SPEC, new roadmap line, or documentation-only
  cycle.
- Before closure, create the exact next `/goal` prompt for PSO-002 Short-read
  path unification unless PSO-001 stops in a non-PASS state.

Certified evidence from prior cycle:
- `docs/roadmap/TES-TTS-PYTHON-SCRIPT-EFFICIENCY-ANALYSIS.md` concluded that
  TES text preparation is already sub-millisecond in-process and is not the
  current bottleneck.
- The active product path is direct/resident OmniVoice, not the obsolete server
  route.
- The human-rated direct long-read recipe remains the behavior to preserve:
  `language=en`, `quality`, 420-character chunks, combined WAV, and 450 ms
  inter-chunk silence.
- The voice prompt cache under
  `tmp/tes-tts-omnivoice-provider/voice-prompts/*.pt` is protected local
  runtime state with private permissions; it is not a durable text conversion
  cache and must not be committed.
- Release identity, sync, provider installs, provider downloads, provider
  certification, durable conversion cache, global config writes, version bump,
  bundle generation, and proactive `speak` behavior remain unauthorized.
- Sync status is REMOTE_SYNC_NOT_REQUESTED.

Task:
Execute only PSO-001 through:
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
   - `scripts/tes_tts_omnivoice_provider_oracle.py`
   - focused runtime scripts under `scripts/tes_tts_runtime*.py`
   - `.agents/skills/tes-tts/SKILL.md`
   - `src/adapters/codex/skills/tes-tts/SKILL.md`
   - `src/adapters/claude/skills/tes-tts/SKILL.md`
4. Execute PSO-001 only:
   - identify the active direct/resident OmniVoice responsibilities inside
     `scripts/tes_tts_omnivoice_provider.py`;
   - extract active OmniVoice load, voice prompt cache use, chunk synthesis,
     WAV combine, and playback orchestration behind a small internal direct
     kernel interface;
   - preserve existing CLI compatibility for active commands;
   - keep server code behaviorally unchanged except for imports/call routing
     required by extraction;
   - do not optimize or redesign short `speak` beyond what is necessary to
     preserve compatibility; PSO-002 owns short-read unification;
   - keep generated audio, caches, model artifacts, downloads, and venvs under
     `tmp/**` only;
   - preserve source immutability, request-local spoken text, secret redaction,
     exact islands, code no-execute posture, no-summary behavior, and protected
     voice prompt cache permissions.
5. Analyze the diff for latency direction, code-size reduction, coupling,
   server-route drift, cache privacy, CLI compatibility, audio-quality risk,
   false-green risk, and line fidelity.
6. Fix only observed PSO-001 defects.
7. Certify with the smallest relevant set:
   - `python3 -m compileall -q scripts/tes_tts_omnivoice_provider.py`
   - any new extracted provider module with `python3 -m compileall -q`
   - `python3 scripts/tes_tts_omnivoice_provider_oracle.py --self-test`
   - `python3 scripts/tes_tts_runtime_latency_oracle.py --self-test`
   - `python3 scripts/tes_tts_instruction_normalizer_oracle.py --self-test`
   - `python3 scripts/tes_tts_fixture_schema_oracle.py --self-test`
   - `python3 /Users/murillo/.codex/skills/.system/skill-creator/scripts/quick_validate.py .agents/skills/tes-tts`
   - `python3 /Users/murillo/.codex/skills/.system/skill-creator/scripts/quick_validate.py src/adapters/codex/skills/tes-tts`
   - `python3 /Users/murillo/.codex/skills/.system/skill-creator/scripts/quick_validate.py src/adapters/claude/skills/tes-tts`
   - `python3 scripts/materialize_adapter.py all --check`
   - `python3 scripts/validate_tds.py`
   - `python3 scripts/validate_doc_size.py`
   - `python3 scripts/tes_tts_roadmap_partition_oracle.py`
   - `git diff --check`
   Generate one local comparison WAV under `tmp/**` only if the extraction can
   affect audio output or chunk assembly.
8. Create the next exact PSO `/goal` prompt for PSO-002 Short-read path
   unification before closure.
9. Update `docs/roadmap/TES-TTS-SKILL-ROADMAP.md` with PSO-001 outcome, next
   prompt pointer by registry reference, and sync status.
10. Stage only PSO-001 files, roadmap/index updates, and the PSO-002 prompt
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
- extracted direct kernel boundary;
- focused oracles and result;
- local comparison WAV path when generated, explicitly under `tmp/**`;
- next prompt artifact for PSO-002 or stop-state rationale;
- local commit hash;
- sync status: REMOTE_SYNC_NOT_REQUESTED unless explicitly authorized.
```
