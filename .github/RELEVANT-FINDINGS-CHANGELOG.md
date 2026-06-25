# Relevant Findings Change Log

This file records follow-up objectives from the full-project inspection on 2026-05-22. It is intentionally not `CHANGELOG.md`: Git remains the project changelog, while this file preserves actionable findings that should not be lost before the team chooses an implementation window.

## Scope

- Source: local inspection of `~/Dev/tilly-engineer-skills`.
- Status: deferred; no implementation is authorized by this note.
- Closure rule: each item needs its own focused change, evidence, and the smallest relevant oracle before it can be marked complete.

## Findings To Carry Forward

| Finding | Objective | Evidence To Preserve | Future Closure Signal |
|---------|-----------|----------------------|-----------------------|
| Project is mature but large | Keep the source package navigable as TES grows. | 520 files, 45 top-level scripts, 93 adapter files, and 245 governed docs/data files were observed during inspection. | A maintainer can explain source ownership from `docs/INDEX.md`, `docs/architecture/PROJECT-STRUCTURE.md`, and `AGENTS.md` without reading generated or historical evidence first. |
| Complexity is concentrated in long scripts | Gradually modularize the largest scripts without changing behavior. | Largest scripts include `scripts/tes_init.py`, `scripts/build_public_docs.py`, `scripts/cortex.py`, `scripts/tes_update.py`, `scripts/tes_bundle.py`, `scripts/context_mesh_run.py`, `scripts/field_reports.py`, and `scripts/tes_install.py`. | Extracted modules keep existing CLI contracts and the same focused self-tests pass before and after each extraction. |
| Governed docs are near modularization limits | Reduce context load before warning thresholds become maintenance drag. | `npm run docs:size` passes but warns near-limit docs: `docs/install/USER-MANUAL.html`, `docs/install/ASSISTED-CONTEXT-INSTALLER.prompt.md`, `docs/evals/EXAMPLES.md`, `docs/install/AGENT-MANUAL.md`, and `docs/install/INSTALL.md`. | Large docs are split only through governed source boundaries; `npm run docs:size`, `npm run tds:validate`, and public-doc checks remain green. |
| Release identity has local/public separation | Make local-ahead work explicit before public release claims. | Local `HEAD` was `58b580c`, ahead of `origin/main`; public `v0.3.123` resolved to `fc044be`. `npm run release:check` certified the published ref, not the local-ahead commit. | Closeout states whether a change is local-only, pushed, tagged, bundled, or intentionally deferred from release identity. |
| Adapter materialization is now temporary output | Preserve the source/output boundary and prevent `dist/adapters/**` from becoming perceived source. | `docs/adapters/MATERIALIZATION.md`, `docs/architecture/PROJECT-STRUCTURE.md`, and `scripts/validate_reference_package.py` now state and enforce that `dist/adapters/**` is temporary inspection output. | `npm run materialize:check` passes, `dist/adapters/**` is absent after inspection, and adapter source remains only under `src/adapters/**`. |
| Regex coverage oracle outweighs its role | Shrink `context_distill_coverage_oracle` to pure diagnostic (or retire it) now that the LLM authors the canonical context and the `.bak` archive is the non-loss guarantee. | Coverage is advisory on the install path since 0.3.175; the standalone oracle still reports literal-fragment gaps as a diagnostic only. | Coverage is documented and used strictly as an informational signal; no path treats it as a non-loss gate. |

## Delivered Evolution (2026-05-22 → 2026-06-07, v0.3.123 → v0.3.175)

The inherited-context capability was designed, built, and shipped to the production install path. When a project already owns a rich `CLAUDE.md` /`AGENTS.md`, install now inherits that context instead of overwriting or leaving the TES core stale:

- **Canonical source + two renderings.** One overlay source (`docs/agents/PROJECT-CONTEXT.md`); `CLAUDE.md` renders thin with an `@`-pointer, `AGENTS.md` with a materialized overlay block. Asymmetry is a permanent design fact (Codex has no `@import`). Authored as Super SPEC `GOAL-SUPER-SPEC-tes-inherited-context-canonical-source.md`.
- **Non-loss by archive.** The pre-existing root is archived as `<root>.bak-<stamp>` and restored byte-faithful on uninstall.
- **Judgment where it belongs.** The LLM (`tes-init`/`tes-context-distill`) authors and condenses the project context; the deterministic layer is the floor, not the product. Regex coverage is advisory, not a gate.
- **On the production path.** Inheritance runs in `tes_bundle.compose_context_from_staged` (the function `tes_install` → `apply_staged_bundle` calls), is idempotent across reinstalls, and was validated end-to-end on a real-project canary at v0.3.175.

Closure signal satisfied: shipped and certified across v0.3.172–v0.3.175 (`release:check` PASS, public bundle + Pages live), line dashboard at `docs/roadmap/inherited-context/DASHBOARD.md`. Remaining carry-forward: the regex-oracle-role item above.

## Review Cadence

Review this file before broad TES maintenance waves, release preparation, or large refactors. Remove or archive an item only after the future closure signal has been satisfied and the proof is visible in Git history or governed docs.
