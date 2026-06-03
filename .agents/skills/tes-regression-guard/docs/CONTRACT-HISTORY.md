# TES Regression Guard Contract History

## Purpose

Preserve certified, installed, materialized, generated, measured, and
human-rated TES behavior during all repository analysis and writing while
allowing runtime-first engineering to continue.

## Why This Skill Exists

A prior latency and audio-quality work line exposed the immediate failure mode,
but the risk is project-wide: an improvement in one dimension can silently remove
the contract that made a previous result good. The same pattern can affect
skills, docs, adapters, installers, runtime scripts, oracles, roadmap lines,
generated public surfaces, release identity, and user-facing behavior.

## Origin Signals

| Source | Signal | Confidence |
|--------|--------|------------|
| Maintainer directive, 2026-05-31 | Regression loops are dangerous and waste hours; create a development-layer skill and reinforce `AGENTS.md` before returning to the correction line. | High |
| Maintainer directive, 2026-05-31 | The guard must be auto-loaded/self-consumed permanently for every analysis and writing condition, not invoked by the user. | High |
| Maintainer directive, 2026-05-31 | Regression is not exclusive to Python or one capability; it must be treated broadly across the whole TES project. | High |
| Prior audio-quality tests | Human-rated audio quality depended on direct execution, voice profile, chunking, punctuation, and light prosody choices. | High |
| Local runtime evidence | A later direct run used optimized scripts but omitted the winning prosody recipe and exposed fragile hard-coded heuristics. | High |

## Source Search Ledger

| Window | Query | Occurrences | Meaning |
|--------|-------|-------------|---------|
| Creation | runtime support line review | Specific lists and heuristics found in runtime path. | Example-bound fixes can become future regressions. |
| Creation | `result.json` from live latency test | Prosody `none` for all chunks. | Same route can still regress quality if recipe invariants are lost. |
| Generalization | Project-surface review from maintainer directive | Applies to source, docs, adapters, installer, runtime, roadmap, release identity, and generated outputs. | Regression guard must protect TES as a product, not one code path. |

## Contracts Preserved

- Runtime-first work continues.
- Human-rated behavior is evidence, not anecdote.
- Installed behavior, generated docs, materialized adapters, public surfaces,
  and CLI/oracle contracts are product evidence.
- Audio, cache, model, and provider runtime artifacts stay uncommitted.
- Local development guards do not become shipped product skills.

## Known Failure Modes Prevented

- Regressing a known-good audio recipe while improving latency.
- Mistaking direct execution for full recipe equivalence.
- Regressing skill triggers, adapter parity, installer behavior, roadmap
  continuity, generated docs, release identity, private-vocabulary safety, or
  CLI payload shape while changing a neighboring surface.
- Adding narrow literal lists that fail on the next unseen term.
- Creating another circular prompt/documentation loop instead of stopping.
- Treating one passing oracle as enough when another surface owns the actual
  risk.

## Relationship To Other Skills

- `tes-sync`: release/bump/publish line must not hide regressions behind
  package closure.
- `tes-goal-maestro`: prompts and Super SPECs must not create circular drift
  when no runtime/product delta exists.
- `tes-high-agency-pattern`: can review this guard's agency and packaging.
- `tes-predictive-operations`: decides when to prospect, mine, alternate, or
  package; this skill protects baseline behavior during execution.

## Changelog

| Date | Change | Evidence | Confidence |
|------|--------|----------|------------|
| 2026-05-31 | Created local anti-regression guard for TES development changes. | Maintainer directive in current session; live runtime regression analysis. | High |
| 2026-05-31 | Promoted guard from risky-change-only to always-on self-consumed analysis/write kernel. | Maintainer directive in current session. | High |
| 2026-05-31 | Generalized guard from capability/Python-centered regression to whole-project regression protection. | Maintainer directive in current session. | High |

## Do Not Lose

The baseline recipe is part of the product, and this applies across every
capability. A
change that preserves one visible command while changing triggers, routing,
docs, materialization, generated public pages, release identity, safety,
latency, audio, or comparison evidence is not equivalent.

This guard is not a command. It is a standing local reasoning kernel for every
TES package analysis and write.
