---
tds_id: roadmap.tes_tts_python_script_efficiency_analysis
tds_class: roadmap
status: active
consumer: maintainers, tes-tts maintainers, runtime authors, and validation authors
source_of_truth: false
evidence_level: L2
---

# TES TTS Python Script Efficiency Analysis

Status: analysis complete for the first optimization pass. This is not a SPEC
and does not authorize code changes by itself.

## Scope

This document records the Python script efficiency levantamento after
`tes-tts` moved back to direct/resident OmniVoice execution. The goal is to
identify where optimization work should happen before changing code.

No runtime code, provider code, fixture, or committed audio artifact was changed
by this analysis.

## Evidence Commands

| Command | Result |
|---------|--------|
| `git status --short --branch --untracked-files=all` | Clean working tree; branch ahead locally. |
| `rg --files scripts \| rg 'tes_tts\|tts' \| sort` | Found 27 TTS-related Python scripts. |
| `wc -l scripts/*tts*.py scripts/tes_tts_*.py` | Largest scripts are provider/lab/oracle surfaces. |
| `python3 scripts/tes_tts_runtime_latency_oracle.py --self-test` | PASS. |
| `python3 -m compileall -q ...` on focused runtime/provider scripts | PASS. |

## Script Inventory Findings

| Surface | Size | Finding |
|---------|------|---------|
| `scripts/tes_tts_runtime.py` | 39 lines | Thin CLI facade; not a major optimization target. |
| `scripts/tes_tts_runtime_adapter.py` | 58 lines | Small adapter around classify/verbalize. |
| `scripts/tes_tts_runtime_verbalizer.py` | 32 lines | Small request-local rendering joiner. |
| `scripts/tes_tts_runtime_classifier.py` | 584 lines | Real text-preparation core; currently fast enough. |
| `scripts/tes_tts_omnivoice_provider.py` | 4466 lines | Main complexity and maintenance risk. |
| `scripts/tes_tts_omnivoice_provider_oracle.py` | 2909 lines | Large safety oracle; likely needs partitioning after provider split. |
| `scripts/tes_tts_audio_variant_lab.py` | 1542 lines | Lab surface still carries obsolete server-oriented controls. |

## Runtime Timing Findings

The dependency-free text runtime is not the latency bottleneck.

| Measurement | Result |
|-------------|--------|
| Runtime latency oracle, simple PT-BR prose | p50 `0.026 ms`, p95 `0.235 ms`. |
| Runtime latency oracle, mixed technical prose | p50 `0.027 ms`, p95 `0.1 ms`. |
| Runtime latency oracle, path/URL/code/secret case | p50 `0.034 ms`, p95 `0.088 ms`. |
| In-process `prepare_spoken_text`, warmed | median `0.0296 ms`, p95 `0.0535 ms`. |
| First in-process call after import | `0.7067 ms`. |
| CLI loop around `tes_tts_runtime.py` | median `32.66 ms`, p95 `38.05 ms`. |
| `tes_tts_runtime_adapter` import | `10.737 ms`. |
| `tes_tts_omnivoice_provider` import | `21.375 ms`. |

The current text path is already suitable for interactive use when reused
inside one Python process. Repeated CLI calls are the avoidable overhead.

## Provider Timing Findings

The active audio path is direct/resident OmniVoice:

```text
speak-long -> provider Python -> serve -> JSONL chunk requests -> combined WAV
```

That path is correct because it loads the model and voice prompt once, then
processes chunks in one resident subprocess.

The short `speak` shortcut still shells into `synthesize`, which is a separate
subprocess path. For repeated short utterances, that is a likely inefficiency
and should converge toward the same resident kernel used by `speak-long`.

## Obsolete Route Findings

The OmniVoice server route is no longer product execution for `tes-tts`. It
still exists inside helper scripts and oracles for historical/lab compatibility,
but it must not drive active skill behavior.

Optimization work should not spend effort improving:

- `server-status`
- `speak-server`
- `speak-long-server`
- server-only presets in the audio variant lab

Those surfaces are candidates for isolation, deprecation, or later removal
after safety oracles are adjusted.

## Priority Queue

| Priority | Work | Rationale |
|----------|------|-----------|
| P0 | Keep direct/resident `speak-long` as the product hot path. | Human-rated recipe reached 7.5/10 and avoids server overhead/ambiguity. |
| P0 | Avoid repeated CLI calls for text preparation inside chunk loops. | In-process runtime is sub-millisecond; CLI startup is ~33 ms. |
| P1 | Make short `speak` reuse the resident synthesis kernel or share the same direct implementation path. | Current shortcut shells into `synthesize`; repeated short reads may reload more than needed. |
| P1 | Split `tes_tts_omnivoice_provider.py` by responsibility. | The 4466-line monolith mixes direct product path, server legacy, review packaging, playback, profile selection, and utilities. |
| P1 | Partition `tes_tts_audio_variant_lab.py` into active direct lab vs obsolete server lab. | The current lab still exposes server controls that are no longer product direction. |
| P2 | Split the provider oracle after provider split. | The 2909-line oracle should follow the product/lab boundary instead of protecting one monolith. |
| P2 | Improve timing output names. | `wall_ms` includes playback in long reads and can confuse performance decisions. |

## Non-Goals

- Do not optimize the dependency-free text runtime before provider work; current
  measurements do not justify it.
- Do not resurrect server execution as a product path.
- Do not add new provider dependencies during this optimization phase.
- Do not commit `tmp/**` audio, caches, venvs, provider downloads, or local
  model artifacts.

## Next Engineering Cut

The next code cut should be small and runtime-first:

1. Extract the direct/resident OmniVoice kernel from the provider monolith.
2. Route both long and short direct reads through that kernel.
3. Leave server code quarantined as legacy/lab until a later removal pass.
4. Preserve current human-rated long-read recipe behavior.
5. Certify with focused provider self-tests, runtime latency oracle, and one
   generated local audio comparison under `tmp/**`.
