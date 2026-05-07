---
tds_id: governance.maintainer_correlation_rule
tds_class: governance
status: active
consumer: maintainers and repository agents
source_of_truth: true
evidence_level: L2
tver: 0.1.0
---

# Maintainer Correlation Rule

This rule governs agents developing the Tilly Engineer Skills package. It is not
an installed project rule, not an adopter instruction, and not target-project
context.

The purpose is simple: when one package surface changes, the agent must check
the nearby surfaces that can drift with it. The check happens in the maintainer
layer before closure. It must not be copied into `src/adapters/**`, target
bootloaders, Cursor rules, Claude skills, Codex skills, or `docs/agents/**`
unless the product behavior itself changed.

## Boundary

The maintainer layer is the repository layer used to develop TES. It includes
root controls, governance docs, TDS indexes, architecture docs, validation
scripts, package metadata, GitHub receiver governance, and local maintainer
bootloaders.

The developed layer is the material TES exposes to users and target projects.
It includes adapter source, installer prompts, user-facing command triggers,
manuals, MCP activation, Cortex runtime contracts, Field Reports behavior, and
generated or installed target surfaces.

A maintainer-only rule belongs in `AGENTS.md` and `docs/governance/**`. A
user-facing behavior belongs in `docs/install/**`, `src/adapters/**`, scripts,
or the relevant runtime contract. Mixing those layers is a contract failure.

## Correlation Rule

Before closing a material change, classify the changed surface and inspect the
correlated files below. Update only the files whose behavior, version, route, or
certification claim actually changed.

- Version or release identity: check `package.json`, `README.md`,
  `docs/tds/DOCS-INDEX.yml`, user-visible version labels, script `VERSION`
  constants, Claude plugin manifests, GitHub issue placeholders, and
  `scripts/validate_reference_package.py`.
- User command or prompt routing: check `docs/install/COMMAND-TRIGGERS.md`,
  `docs/install/USER-MANUAL.html`, installer prompts, adapter skills/rules,
  platform surface oracle, package scripts, and README only when the public
  entrypoint changes.
- Assisted installer behavior: check `docs/install/INSTALL.md`,
  `docs/install/MINI-PROMPT.md`,
  `docs/install/ASSISTED-CONTEXT-INSTALLER.prompt.md`,
  `docs/install/USER-MANUAL.html`, install scripts, smoke tests, adapter init
  skills, and navigation prompts.
- Cortex behavior: check `docs/mesh/CORTEX.md`,
  `docs/mesh/CORTEX-MCP.md`, `docs/install/COMMAND-TRIGGERS.md`, user manual,
  `scripts/cortex.py`, `scripts/cortex_mcp.py`, package scripts, MCP install,
  adapter skills/rules, and related oracles.
- Field Reports behavior: check `docs/mesh/FIELD-REPORTS.md`, user manual,
  command triggers, installer prompts, `scripts/field_reports.py`,
  `.github/**`, GitHub receiver oracle, package scripts, and platform surface
  oracle.
- Adapter behavior: check `src/adapters/**`, `docs/adapters/**`,
  `scripts/materialize_adapter.py`, adapter parity checks, platform surface
  oracle, and materialization output checks.
- Governed documentation: check frontmatter, `docs/tds/DOCS-INDEX.yml`,
  `docs/INDEX.md`, document size budget, reference graph, and TDS validation.
- Repository structure: check `AGENTS.md`,
  `docs/architecture/PROJECT-STRUCTURE.md`, `README.md` only if the human
  entrypoint changes, and `scripts/validate_reference_package.py`.
- GitHub receiver governance: check issue templates, workflows, receiver
  oracle, Field Reports contract, and manual only if user-visible behavior
  changed.

## No-Go

- Do not update `src/**` merely to teach agents how to maintain this repository.
- Do not update the user manual with maintainer-only coordination rules.
- Do not duplicate this map into adapter bootloaders or target-project files.
- Do not treat `docs/agents/**` as package-maintainer governance.
- Do not bump versions without a material package delta and matching validator
  updates.
- Do not claim closure if correlated files were skipped without an explicit
  reason.

## Closure

A package change closes only when the agent can say which correlation group was
checked, which files changed, which files were intentionally untouched, and
which oracle proved the cut. If that cannot be stated cleanly, the correct
status is `NEEDS_REVIEW`, not `PASS`.
