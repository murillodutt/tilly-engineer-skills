---
tds_id: governance.maintainer_correlation_rule
tds_class: governance
status: active
consumer: maintainers and repository agents
source_of_truth: true
evidence_level: L2
tver: 0.1.1
---

# Maintainer Correlation Rule

This rule governs agents developing the Tilly Engineer Skills package. It is not an installed project rule, not an adopter instruction, and not target-project context.

The purpose is simple: when one package surface changes, the agent must check the nearby surfaces that can drift with it. The check happens in the maintainer layer before closure. It must not be copied into `src/adapters/**`, target bootloaders, Cursor rules, Claude skills, Codex skills, or `docs/agents/**` unless the product behavior itself changed.

## Boundary

The maintainer layer is the repository layer used to develop TES. It includes root controls, governance docs, TDS indexes, architecture docs, validation scripts, package metadata, GitHub receiver governance, and local maintainer bootloaders.

The developed layer is the material TES exposes to users and target projects. It includes adapter source, installer prompts, user-facing command triggers, manuals, MCP activation, Cortex runtime contracts, Field Reports behavior, and generated or installed target surfaces.

A maintainer-only rule belongs in `AGENTS.md`, `docs/governance/**`, TDS/index entries, and validators that protect this repository.

A delivered behavior belongs in `docs/install/**`, `src/adapters/**`, user-visible runtime contracts, package scripts that implement adopter-visible behavior, MCP activation, Field Reports behavior, Cortex behavior, or the relevant installer surface.

`scripts/**` is not a layer by itself. A script change is classified by the consumer and behavior it changes. A validator-only change is maintainer layer. A change to `tes_init.py`, `cortex.py`, `install_mcp.py`, `install_adapter.py`, `install_smoke.py`, `field_reports.py`, or an adapter materializer can be delivered behavior when it changes what adopters receive, invoke, or certify.

Every code file changed or added must be documented for future maintainers. The documentation can be direct (module docstring, top-level file comment, or targeted inline comment for non-obvious logic) or associated (an indexed Markdown document that names the code path and explains the contract). Code behavior must not depend on commit history or test names as the only explanation.

## Layer Decision Test

Run this test before applying the correlation map:

1. If a change only alters how agents maintain this repository, it may update `AGENTS.md`, `docs/governance/**`, `docs/tds/**`, `docs/INDEX.md`, architecture notes, and validators. It must not update `src/adapters/**`, `docs/install/**`, user manuals, adapter bootloaders, or target-project surfaces.
2. If a change alters behavior observed by adopters or installing agents, it is delivered behavior. Check user docs, installer prompts, command triggers, adapter sources, runtime contracts, package scripts, and oracles.
3. If a change touches both layers, state both impacts separately and update each correlated surface for its own reason.
4. If the layer cannot be classified in one sentence, stop with `NEEDS_REVIEW` before editing user-facing files.
5. If a maintainer-only patch requires a user-facing edit to pass a gate, the gate or classification is wrong until proven otherwise.

## Correlation Rule

Before closing a material change, classify the changed surface and inspect the correlated files below. Update only the files whose behavior, version, route, or certification claim actually changed.

- Version or release identity: check `package.json`, `README.md`, `docs/tds/DOCS-INDEX.yml`, user-visible version labels, script `VERSION` constants, Claude plugin manifests, GitHub issue placeholders, and `scripts/validate_reference_package.py`. After an authorized release tag is pushed, run `npm run release:check` before claiming the fixed GitHub npx ref is certified.
- Public installer bundle: check `scripts/tes_bundle.py`, `scripts/public_bundle_oracle.py`, `docs/dist/<version>/tilly-engineer-skills-<version>.zip`, the matching `.sha256` sidecar, `docs/dist/<version>/index.json`, source commit metadata, setup-script presence inside the ZIP, GitHub Pages URL claims, and retained canary evidence.
- User command or prompt routing: check `docs/install/COMMAND-TRIGGERS.md`, `docs/install/USER-MANUAL.html`, installer prompts, adapter skills/rules, platform surface oracle, package scripts, and README only when the public entrypoint changes.
- Assisted installer behavior: check `docs/install/INSTALL.md`, `docs/install/MINI-PROMPT.md`, `docs/install/ASSISTED-CONTEXT-INSTALLER.prompt.md`, `docs/install/USER-MANUAL.html`, install scripts, smoke tests, adapter init skills, and navigation prompts.
- Cortex behavior: check `docs/mesh/CORTEX.md`, `docs/mesh/CORTEX-MCP.md`, `docs/install/COMMAND-TRIGGERS.md`, user manual, `scripts/cortex.py`, `scripts/cortex_mcp.py`, package scripts, MCP install, adapter skills/rules, and related oracles.
- Field Reports behavior: check `docs/mesh/FIELD-REPORTS.md`, user manual, command triggers, installer prompts, `scripts/field_reports.py`, `.github/**`, GitHub receiver oracle, package scripts, and platform surface oracle.
- Adapter behavior: check `src/adapters/**`, `docs/adapters/**`, `scripts/materialize_adapter.py`, adapter parity checks, platform surface oracle, and materialization output checks.
- Governed documentation: check frontmatter, `docs/tds/DOCS-INDEX.yml`, `docs/INDEX.md`, document size budget, reference graph, and TDS validation.
- Code documentation: check `scripts/code_documentation_oracle.py`, the touched code file's direct comments/docstrings, and any associated Markdown document that names the code path.
- Repository structure: check `AGENTS.md`, `docs/architecture/PROJECT-STRUCTURE.md`, `README.md` only if the user entrypoint changes, and `scripts/validate_reference_package.py`.
- GitHub receiver governance: check issue templates, workflows, receiver oracle, Field Reports contract, and manual only if user-visible behavior changed.

## No-Go

- Do not update `src/**` merely to teach agents how to maintain this repository.
- Do not update the user manual with maintainer-only coordination rules.
- Do not duplicate this map into adapter bootloaders or target-project files.
- Do not treat `docs/agents/**` as package-maintainer governance.
- Do not bump versions without a material package delta and matching validator updates.
- Do not claim closure if correlated files were skipped without an explicit reason.

## Closure

A package change closes only when the agent can say which correlation group was checked, which files changed, which files were intentionally untouched, and which oracle proved the cut. If that cannot be stated cleanly, the correct status is `NEEDS_REVIEW`, not `PASS`.

## Operational Sequence

This rule states which files correlate. The operational sequence for a delivered-behavior change with version bump, public bundle, tag, and push is captured in `docs/governance/SYNC-AUDIT-CHECKLIST.md`. Use the checklist as the audit path; this document remains the correlation reference.
