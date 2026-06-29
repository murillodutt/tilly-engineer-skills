# TES Bench Contract History

## Purpose

`tes-bench` routes benchmark planning, safe fixture runs, convergence review, and behavior-evidence certification for TES context-mesh evidence.

## Why This Skill Exists

Benchmark commands are package-source evidence operations. Installed target projects usually do not own the benchmark scripts, so agents need a clear route that avoids inventing target-local benchmark commands or promoting raw evidence into current truth.

## Origin Signals

| Source | Signal | Confidence |
|--------|--------|------------|
| TES eval design contract | Defines context-mesh runner, convergence gate, evidence files, and default temporal report path. | high |
| TES evidence retention policy | Defines current, reports, archive, and source-of-truth boundaries for evidence. | high |
| Package benchmark scripts | Exposes package-source benchmark plan, run, and converge commands. | high |

## Source Search Ledger

| Window | Query | Occurrences | Meaning |
|--------|-------|-------------|---------|
| 2026-06-29 | Documented universal Contract History version semantics so skill contract versions, TES package versions, and `tver` metadata are not conflated. | `docs/dist/0.3.229/tilly-engineer-skills-0.3.229.zip`; `scripts/public_bundle_oracle.py` | high |
| 2026-05-21 | `/tes-bench` | existing skill surface | Skill already routed benchmark evidence work. |
| 2026-05-21 | `docs/evidence/reports/context-mesh` | legacy references remain | Legacy evidence must stay readable but not current by existence alone. |

## Contracts Preserved

- `/tes-bench` is package-source benchmark work, not installed-target health.
- Fixture evidence does not prove behavior parity.
- Raw evidence, manifests, summaries, reports, and grader hashes are retained when a claim depends on them.
- Current evidence interpretation lives in `docs/evidence/current/**`.
- New generated benchmark runs default to temporal `reports/YYYY/MM/DD`.

## Known Failure Modes Prevented

- Running benchmark scripts in target projects that do not have TES source.
- Treating a historical retained report as current operational truth.
- Claiming behavior certification from fixture-only evidence.
- Overwriting benchmark artifacts without explicit reason.
- Running cost or network backends without authorization.

## Relationship To Other Skills

`tes-bench` handles benchmark evidence. `tes-align` handles target-project operating mesh alignment and writes target evidence under `docs/agents/**`. `tes-map` reads the target map. `tes-doctor` is the route for installed-target health.

## Changelog

`Version` records a skill operational contract version only when the skill declares one, followed by the containing TES package version when known. If no operational contract stamp exists, the TES package version is the shipped identity. `tver: 0.1.0` in roadmap, Super SPEC, ledger, or TDS frontmatter is document-template metadata, not a skill runtime or harness version. Patch-level changes can remain inside the same skill contract boundary; in that case the TES package version carries release identity until a future change alters the skill contract boundary itself.

| Date | Change | Evidence | Confidence |
|------|--------|----------|------------|
| 2026-05-21 | Added temporal evidence retention semantics and skill contract memory. | TES evidence retention policy; TES eval design contract; runner dry-run; retention metadata self-test. | high |

## Do Not Lose

Evidence is proof retained for claims, not truth by existence. Use `docs/evidence/current/**` for current claims and keep generated run artifacts under the temporal reports contract unless a caller explicitly chooses another root.
