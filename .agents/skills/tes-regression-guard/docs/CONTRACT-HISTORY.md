# TES Regression Guard Contract History

## Purpose

Preserve certified and human-rated TES behavior during all TES repository
analysis and writing while allowing runtime-first engineering to continue.

## Why This Skill Exists

TES-TTS latency and audio-quality work showed that an improvement in one
dimension can silently remove the recipe that made the previous result good:
direct execution can remain correct while prosody, language, chunking, or
pause behavior regresses. This skill creates a local guard before the next risky
runtime change.

## Origin Signals

| Source | Signal | Confidence |
|--------|--------|------------|
| Maintainer directive, 2026-05-31 | Regression loops are dangerous and waste hours; create a development-layer skill and reinforce `AGENTS.md` before returning to the correction line. | High |
| Maintainer directive, 2026-05-31 | The guard must be auto-loaded/self-consumed permanently for every analysis and writing condition, not invoked by the user. | High |
| TES-TTS OmniVoice tests | Human-rated audio quality depended on direct execution, voice profile, chunking, punctuation, and light prosody choices. | High |
| Local runtime evidence | A later direct run used optimized scripts but omitted the winning prosody recipe and exposed fragile hard-coded heuristics. | High |

## Source Search Ledger

| Window | Query | Occurrences | Meaning |
|--------|-------|-------------|---------|
| Creation | `tes_tts_omnivoice_runtime_support.py` line review | Specific lists and heuristics found in runtime path. | Example-bound fixes can become future regressions. |
| Creation | `result.json` from live latency test | Prosody `none` for all chunks. | Same route can still regress quality if recipe invariants are lost. |

## Contracts Preserved

- Runtime-first work continues.
- Human-rated behavior is evidence, not anecdote.
- Audio, cache, model, and provider runtime artifacts stay uncommitted.
- Local development guards do not become shipped product skills.

## Known Failure Modes Prevented

- Regressing a known-good audio recipe while improving latency.
- Mistaking direct execution for full recipe equivalence.
- Adding narrow literal lists that fail on the next unseen term.
- Creating another circular prompt/documentation loop instead of stopping.
- Treating oracle success as enough when the risk is audible quality.

## Relationship To Other Skills

- `tes-tts`: target skill most likely to need this guard during audio work.
- `tes-high-agency-pattern`: can review this guard's agency and packaging.
- `tes-predictive-operations`: decides when to prospect, mine, alternate, or
  package; this skill protects baseline behavior during execution.

## Changelog

| Date | Change | Evidence | Confidence |
|------|--------|----------|------------|
| 2026-05-31 | Created local anti-regression guard for TES development changes. | Maintainer directive in current session; live TES-TTS regression analysis. | High |
| 2026-05-31 | Promoted guard from risky-change-only to always-on self-consumed analysis/write kernel. | Maintainer directive in current session. | High |

## Do Not Lose

The baseline recipe is part of the product. A change that keeps the command
direct but drops voice, prosody, language, chunking, punctuation, redaction, or
comparison evidence is not equivalent.

This guard is not a command. It is a standing local reasoning kernel for every
TES package analysis and write.
