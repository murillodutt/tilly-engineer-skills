---
tds_id: roadmap.goal_super_spec_tes_tts_python_script_optimization
tds_class: roadmap
status: active
consumer: maintainers, tes-tts maintainers, runtime authors, provider authors, and validation authors
source_of_truth: false
evidence_level: L2
---

# GOAL Super SPEC: TES TTS Python Script Optimization

Status: active implementation authority for optimizing Python scripts tied to
`tes-tts`.

Canonical artifact:
`docs/roadmap/GOAL-SUPER-SPEC-tes-tts-python-script-optimization.md`

Input analysis:
`docs/roadmap/TES-TTS-PYTHON-SCRIPT-EFFICIENCY-ANALYSIS.md`

Ready prompt:
`docs/roadmap/GOAL-PROMPT-tes-tts-PSO-004-lab-surface-split.md`

## Purpose

Turn the Python efficiency analysis into runtime-first implementation work. The
goal is maximum practical optimization of `tes-tts` Python surfaces without
rebuilding governance, changing provider choice, or improving obsolete server
execution.

The product direction is:

```text
active path: direct/resident OmniVoice -> protected voice prompt cache -> chunked WAV
inactive path: server/lab legacy -> quarantine, then remove when safe
```

Optimization must reduce latency, memory churn, command overhead, and
maintenance risk while preserving the human-rated direct long-read recipe.

## Certified Context

- `tes-tts` is reactive-only and PT-BR remains the primary quality target.
- Direct/resident OmniVoice is the active cloned-voice execution path.
- The canonical reference voice WAV is
  `tmp/tes-tts-lab/omnivoice/refs/audio-modelo-clone-mono24k.wav`.
- Voice prompt cache under `tmp/tes-tts-omnivoice-provider/voice-prompts/*.pt`
  is protected local runtime state, not a committed or durable conversion
  cache.
- Text preparation is not the current bottleneck: in-process runtime is already
  sub-millisecond in the efficiency analysis.
- The main risks are the provider monolith, repeated CLI/process overhead,
  obsolete server/lab controls, and coarse timing labels.

## Optimization Targets

| Target | Current evidence | Desired result |
|--------|------------------|----------------|
| `scripts/tes_tts_omnivoice_provider.py` | Provider/lab/server monolith with thousands of lines. | Extract active direct/resident kernel and isolate legacy server/lab code. |
| `speak` short path | Separate subprocess-style shortcut. | Reuse the same direct implementation path as long reads. |
| `speak-long` direct path | Correct product hot path. | Keep behavior stable while making the kernel smaller and easier to benchmark. |
| Server route | Obsolete for product execution. | Keep only as quarantined reference or remove after oracle coverage changes. |
| Audio variant lab | Contains active recipe and obsolete server controls. | Split active direct lab from legacy server experiments. |
| Provider oracle | Protects one large mixed surface. | Split or focus after the provider boundary is extracted. |
| Timing output | Some names blur prep, synthesis, playback, and wall time. | Report separate preparation, model load, voice prompt, synthesis, combine, playback, and wall timings. |

## Execution Units

| Unit | Focus | Required outcome |
|------|-------|------------------|
| PSO-001 | Direct/resident kernel extraction | Active OmniVoice load, voice prompt cache, chunk synthesis, combine, and playback are isolated behind a small internal interface while CLI compatibility remains intact. |
| PSO-002 | Short-read path unification | `speak` and `speak-long` use the same direct implementation path where practical; repeated short reads avoid avoidable process/model churn. |
| PSO-003 | Server legacy quarantine | Server commands, presets, and tests are marked or moved out of the product path without deleting safety evidence prematurely. |
| PSO-004 | Lab surface split | Active audio recipe tests stay concise; historical server/lab variants move behind explicit legacy names. |
| PSO-005 | Oracle partition | Provider oracle follows the new boundary: active direct kernel, legacy server compatibility, and dry-run packaging are tested separately. |
| PSO-006 | Timing and benchmark cleanup | Timing names and benchmark output separate text prep, provider preparation, synthesis, combine, playback, and total wall time. |
| PSO-007 | Final optimization audit | Confirm latency, code-size, command-count, cache, privacy, and audio-quality evidence; close or create the next runtime cut. |

Do not add a separate documentation-only unit. If a unit does not change code,
fixtures, or executable validation, it should be merged into the adjacent code
cut.

## Engineering Rules

- Optimize the intended runtime path first, not obsolete routes.
- Keep public CLI behavior compatible until a removal decision is explicit.
- Keep `tmp/**` out of commits.
- Keep model artifacts, voice prompt cache, generated WAV files, provider
  downloads, and venvs local only.
- Preserve source immutability, request-local spoken text, secret redaction,
  exact islands, code no-execute posture, and no-summary behavior.
- Do not introduce provider installs, provider downloads, provider
  certification, release, sync, push, tag, publish, version bump, bundle
  generation, global config writes, or proactive `speak`.

## Performance Goals

| Metric | Goal |
|--------|------|
| Text preparation | Keep existing sub-millisecond in-process behavior. |
| Short-read overhead | Remove avoidable extra CLI/process/model churn. |
| Long-read path | Preserve the 7.5/10 human-rated recipe behavior or improve it. |
| Voice prompt cache | Keep cache hits private, local, and fast. |
| Timing evidence | Make bottlenecks attributable without guessing. |
| Code maintainability | Shrink active product path and reduce monolith coupling. |

## Certification Set

Each implementation cut uses the smallest relevant subset:

```bash
python3 scripts/tes_tts_omnivoice_provider_oracle.py --self-test
python3 scripts/tes_tts_runtime_latency_oracle.py --self-test
python3 scripts/tes_tts_instruction_normalizer_oracle.py --self-test
python3 scripts/tes_tts_fixture_schema_oracle.py --self-test
python3 /Users/murillo/.codex/skills/.system/skill-creator/scripts/quick_validate.py .agents/skills/tes-tts
python3 /Users/murillo/.codex/skills/.system/skill-creator/scripts/quick_validate.py src/adapters/codex/skills/tes-tts
python3 /Users/murillo/.codex/skills/.system/skill-creator/scripts/quick_validate.py src/adapters/claude/skills/tes-tts
python3 scripts/materialize_adapter.py all --check
python3 scripts/validate_tds.py
python3 scripts/validate_doc_size.py
python3 scripts/tes_tts_roadmap_partition_oracle.py
git diff --check
```

For provider changes, also generate one local comparison WAV under `tmp/**`
when audio quality or timing could regress. The WAV is evidence for listening,
not a committed artifact.

## Stop States

- `PASS`: active path improved or stayed stable with clearer code and passing
  focused gates.
- `DEGRADED`: improvement is partial, but boundaries and safety hold.
- `PERFORMANCE_REGRESSION`: timing worsens against the latest local baseline.
- `QUALITY_REGRESSION`: generated audio is materially worse in human review.
- `NEEDS_REVIEW`: code movement, timing evidence, or legacy-server handling is
  ambiguous.
- `SAFETY_BLOCKED`: cache privacy, secret redaction, command no-execute, or
  local-only provider boundaries would be violated.
- `BLOCKED`: continuing would require release, sync, provider install,
  provider download, or global write approval.

## Closure

This line closes only after PSO-007 confirms the active direct/resident path is
smaller, faster or equally fast, measurable, cache-safe, and no longer governed
by obsolete server assumptions. Closure does not authorize release identity,
sync, provider redistribution, provider certification, or durable conversion
cache.
