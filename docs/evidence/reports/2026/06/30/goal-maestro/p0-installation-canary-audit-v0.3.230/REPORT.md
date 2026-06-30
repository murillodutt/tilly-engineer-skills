---
tds_id: evidence.goal_maestro.p0_installation_canary_audit_2026_06_30_v0_3_230
tds_class: evidence
status: active
consumer: maintainers, Goal Maestro authors, installer authors, hook authors, MCP authors, and release reviewers
source_of_truth: false
evidence_level: L3
tver: 0.1.3
---

# Goal Maestro P0 Installation Canary Audit - 2026-06-30 - v0.3.230

## Decision

SOURCE_REPAIRED_NEEDS_CANARY_REINSTALL. The three original local host canaries
prove package version `0.3.230` was installed, staged, postinstalled, aligned,
mapped, and MCP-registered, but they do not authorize Goal Maestro execution as
installed. The `codex` canary has final hook-surface drift: the install lock
says `hooks` is attached, while the final hook configs and runtime ledger show
no configured hook execution path. No original canary has evidence of a
persistent Git `pre-commit` gate; any Goal Maestro run that claims pre-commit
enforcement would be unsupported until that gate is installed and proven, or the
run is explicitly classified as manual/no-precommit mode.

Package source has since been repaired and locally versioned as `0.3.231`.
Fresh replay targets prove `install -> postinstall (/tes-setup) -> /tes-align
-> /tes-map` for `cursor`, `claude`, and `codex`; the original canary
directories were intentionally not modified.

This report is based on installed artifacts, source oracles, direct file
inspection, lock/manifest records, and hook runtime ledgers. The host-written
post-install reports were treated as input claims, not as the authority.

## Repair Update - Source Package

Status: SOURCE_PACKAGE_REPAIRED_AND_LOCALLY_BUNDLED,
INSTALLED_CANARIES_NOT_REPAIRED. The package source now detects the primary
false-green states that this audit exposed:

- `hook-health` returns `DEGRADED` when `.tes/tes-install-lock.json` declares
  `hooks` but no host hook config is present.
- `installed_certification_oracle.py` includes `hook_runtime_health` and returns
  `PARTIAL` for attached hook surfaces with no config, instead of hiding the
  issue behind a global PASS.
- `precommit_enforced` in Goal Maestro now requires material installed-hook
  proof, not only `precommit_evidence.status=installed`.
- The active `/tes-setup` mesh text no longer points to the nonexistent
  `/tes-setup --install-gate` flag.
- Local development mirrors `.agents/skills/tes-goal-maestro/**` and
  `.claude/skills/tes-goal-maestro/**` are byte-aligned with
  `src/adapters/{codex,claude}/skills/tes-goal-maestro/**`.
- Package identity advanced locally from `0.3.230` to `0.3.231`.
- Local public bundle `docs/dist/0.3.231/tilly-engineer-skills-0.3.231.zip`
  is certified with sha256
  `2a548463442e6e2c1a66337b1d2d4905daad49f4bb7a4ca3875c998afc68dac3`.

The three canary directories were intentionally not modified. They remain
evidence targets for reinstall/replay.

## Fresh Replay Evidence - v0.3.231

Replay targets under `~/Dev/tes-canaries/tmp-replay-0.3.231-20260630092532/**`
were created as Git repositories and installed from the local `0.3.231` bundle.
The first `/tes-align` check before postinstall failed, which confirms the
required sequence: install alone leaves `.tes/postinstall.json` pending; the
postinstall step materializes `docs/agents/**`.

| Replay target | Install | Postinstall | `/tes-align` after postinstall | `/tes-map` after postinstall | Installed certification | Hook health | Git hooks |
|---------------|---------|-------------|--------------------------------|------------------------------|-------------------------|-------------|-----------|
| `cursor` | PASS, 379 manifest entries, all attachment surfaces declared | PASS, sentinel `complete` | PASS | PASS | PASS | `NEEDS_EVIDENCE`, configured without host runtime observation | `pre-push` present, `pre-commit` absent |
| `claude` | PASS, 379 manifest entries, all attachment surfaces declared | PASS, sentinel `complete` | PASS | PASS | PASS | `NEEDS_EVIDENCE`, configured without host runtime observation | `pre-push` present, `pre-commit` absent |
| `codex` | PASS, 379 manifest entries, all attachment surfaces declared | PASS, sentinel `complete` | PASS | PASS | PASS | `NEEDS_EVIDENCE`, configured without host runtime observation | `pre-push` present, `pre-commit` absent |

Interpretation: `pre-push` is a Field Reports postinstall surface and is present
in Git-backed replay targets after postinstall. Git `pre-commit` is not a
default installed TES surface; Goal Maestro must classify commit enforcement as
manual/no-precommit unless a project-specific pre-commit gate is explicitly
installed and proven.

## Scope

- Package version: `0.3.230`.
- Source commit installed in all three canaries: `d05b050a`.
- Canary targets: `~/Dev/tes-canary/cursor`, `~/Dev/tes-canary/claude`,
  and `~/Dev/tes-canary/codex`.
- Required sequence under audit: `install -> /tes-setup -> /tes-align -> /tes-map`.
- Protected baseline: default local install must materialize `capsule`,
  `skills`, `root-context`, `mcp`, and `hooks`; `docs-mesh` is postinstall
  project output, not a default attached surface in the install lock.

## Installation Evidence Matrix

| Canary | Install lock | Stage | Manifest | Postinstall | MCP | Installed certification |
|--------|--------------|-------|----------|-------------|-----|-------------------------|
| `cursor` | `version=0.3.230`, `source_commit=d05b050a`, surfaces `capsule,hooks,mcp,root-context,skills` | `STAGED`, 379 entries | 379 entries: skills 326, root-context 5, capsule 48 | `complete`, `PASS`, executed by `cursor`, 1 run | `INSTALLED` | PASS |
| `claude` | `version=0.3.230`, `source_commit=d05b050a`, surfaces `capsule,hooks,mcp,root-context,skills` | `STAGED`, 379 entries | 379 entries: skills 326, root-context 5, capsule 48 | `complete`, `PASS`, executed by `claude`, 1 run | `INSTALLED` | PASS |
| `codex` | `version=0.3.230`, `source_commit=d05b050a`, surfaces `capsule,hooks,mcp,root-context,skills` | `STAGED`, 379 entries | 379 entries: skills 326, root-context 5, capsule 48 | `complete`, `PASS`, executed by `codex`, 2 runs, `recovery=needs_review` | `INSTALLED` | PASS |

## Direct Artifact Evidence

| Canary | Codex skill files | Claude skill files | `.tes/bin` files | `.tes/setup` files | `.tes/gps` files | Hook ledger records |
|--------|-------------------|--------------------|------------------|--------------------|------------------|---------------------|
| `cursor` | 165 | 161 | 73 | 382 | 8 | 151 |
| `claude` | 165 | 161 | 72 | 382 | 8 | 41 |
| `codex` | 165 | 161 | 72 | 382 | 8 | 0 |

Critical capsule hashes match the manifest for
`.tes/docs/architecture/PRETOOLUSE-CONTRACT.md` and
`.cursor/rules/tes-runtime-capabilities.mdc` in all three canaries. Root
bootloaders and `.cursor/rules/tes-engineering-discipline.mdc` are present and
manifested, but no longer byte-identical to the original bundle entries after
target-specific root-context/postinstall alignment. `command_trigger_parity`
still passes for all three canaries, so this is not treated as trigger loss.

## Hook And MCP Evidence

| Canary | Codex hook config | Claude hook config | Cursor hook config | MCP configs | Hook health |
|--------|-------------------|--------------------|--------------------|-------------|-------------|
| `cursor` | `.codex/config.toml` contains `tes_install.py`, `SessionStart`, `PreToolUse`, `tes-cortex` | `.claude/settings.json` contains `tes_install.py`, `SessionStart`, `PreToolUse` | `.cursor/hooks.json` contains `tes_install.py`, `sessionStart`, `preToolUse` | `.codex/config.toml`, `.mcp.json`, `.cursor/mcp.json` all contain `tes-cortex` | `NEEDS_EVIDENCE`: Cursor and Claude PreToolUse observed; Codex not observed |
| `claude` | `.codex/config.toml` contains `tes_install.py`, `SessionStart`, `PreToolUse`, `tes-cortex` | `.claude/settings.json` contains `tes_install.py`, `SessionStart`, `PreToolUse` | `.cursor/hooks.json` contains `tes_install.py`, `sessionStart`, `preToolUse` | `.codex/config.toml`, `.mcp.json`, `.cursor/mcp.json` all contain `tes-cortex` | `NEEDS_EVIDENCE`: Claude observed; Cursor and Codex not observed |
| `codex` | `.codex/config.toml` contains `tes-cortex` but not `tes_install.py`, `SessionStart`, or `PreToolUse` | `.claude/settings.json` lacks `tes_install.py` and `PreToolUse` | `.cursor/hooks.json` is absent | `.codex/config.toml`, `.mcp.json`, `.cursor/mcp.json` all contain `tes-cortex` | `PASS` from `hook-health`, but with no configured host rows and hook ledger missing; treat as ambiguous, not certification |

The `codex` canary is the blocker. `installed_certification_oracle.py` reports
overall PASS, but its `mantra_gate_adoption.surface_health.hooks` component
reports `DEGRADED` for Codex/Claude and `NOT_APPLIED` for Cursor. The direct
file inspection confirms the final hook configs do not match the attached
`hooks` surface declared in `.tes/tes-install-lock.json`.

## Git Gate Evidence

The package-source pre-commit/staged gate is a maintainer-repository surface:
`npm run commit:check` runs `scripts/staged_commit_gate.py`, and
`quality:staged` delegates to `lefthook run pre-commit`. That gate is not the
same surface as the installed target host hooks declared by the TES installer.

The default install contract requires TES host hooks, MCP, root context, skills,
and capsule materialization. Its Git hook row names a Field Reports `pre-push`
gate, not a Git `pre-commit` gate. Separately, Goal Maestro commit-enforcement
checks require evidence before a report may claim `precommit_enforced`; without
evidence, the honest classification is manual/no-precommit, not enforced.

Direct audit of the three local canaries found no persistent Git gate materialized:

| Canary | Git repo | `core.hooksPath` | `pre-commit` evidence | `pre-push` evidence | Result |
|--------|----------|------------------|-----------------------|---------------------|--------|
| `cursor` | no | absent | no `.git/hooks/pre-commit`, `.githooks/pre-commit`, `.husky/pre-commit`, `lefthook.yml`, or `.pre-commit-config.yaml` | no `.git/hooks/pre-push`, `.githooks/pre-push`, or `.husky/pre-push` | no persistent Git gate identified |
| `claude` | no | absent | no `.git/hooks/pre-commit`, `.githooks/pre-commit`, `.husky/pre-commit`, `lefthook.yml`, or `.pre-commit-config.yaml` | no `.git/hooks/pre-push`, `.githooks/pre-push`, or `.husky/pre-push` | no persistent Git gate identified |
| `codex` | no | absent | no `.git/hooks/pre-commit`, `.githooks/pre-commit`, `.husky/pre-commit`, `lefthook.yml`, or `.pre-commit-config.yaml` | no `.git/hooks/pre-push`, `.githooks/pre-push`, or `.husky/pre-push` | no persistent Git gate identified |

Conclusion: the user's observation is correct. No canary currently proves
pre-commit enforcement. This is a Goal Maestro fidelity/admission blocker for
any pre-commit-enforced claim. By itself, it is not proof that the default TES
installer failed to install a required Git `pre-commit` hook, because the
install framework does not identify Git `pre-commit` as a default installed
surface.

## Align And Map Evidence

| Canary | `/tes-align` oracle | Notable warnings | `/tes-map` oracle |
|--------|---------------------|------------------|-------------------|
| `cursor` | PASS | No Semantic Residue contract; newest ADR tokens absent from active mesh | PASS, managed roadmap block present, seven Atlas views present |
| `claude` | PASS | No Semantic Residue contract; newest ADR tokens absent from active mesh | PASS, managed roadmap block present, seven Atlas views present |
| `codex` | PASS | None | PASS, managed roadmap block present, seven Atlas views present |

The seven map views present in all canaries are `data_map`, `dependency_map`,
`gates_evidence`, `module_tree`, `project_gps`, `project_overview`, and
`runtime_integrations`.

## Oracles Run

| Command | Result |
|---------|--------|
| `python3 scripts/installed_certification_oracle.py --target ~/Dev/tes-canary/cursor --json-only` | PASS before repair; PASS after repair with `hook_runtime_health=NEEDS_EVIDENCE` finding |
| `python3 scripts/installed_certification_oracle.py --target ~/Dev/tes-canary/claude --json-only` | PASS before repair; PASS after repair with `hook_runtime_health=NEEDS_EVIDENCE` finding |
| `python3 scripts/installed_certification_oracle.py --target ~/Dev/tes-canary/codex --json-only` | PASS before repair; PARTIAL after repair with `hook_runtime_health=PARTIAL` |
| `python3 scripts/tes_install.py hook-health --target ~/Dev/tes-canary/cursor --json-only` | NEEDS_EVIDENCE before and after repair |
| `python3 scripts/tes_install.py hook-health --target ~/Dev/tes-canary/claude --json-only` | NEEDS_EVIDENCE before and after repair |
| `python3 scripts/tes_install.py hook-health --target ~/Dev/tes-canary/codex --json-only` | PASS ambiguous before repair; DEGRADED after repair |
| `python3 scripts/project_alignment_oracle.py --target ~/Dev/tes-canary/cursor --json` | PASS |
| `python3 scripts/project_alignment_oracle.py --target ~/Dev/tes-canary/claude --json` | PASS |
| `python3 scripts/project_alignment_oracle.py --target ~/Dev/tes-canary/codex --json` | PASS |
| `python3 scripts/tes_map_oracle.py --target ~/Dev/tes-canary/cursor` | PASS |
| `python3 scripts/tes_map_oracle.py --target ~/Dev/tes-canary/claude` | PASS |
| `python3 scripts/tes_map_oracle.py --target ~/Dev/tes-canary/codex` | PASS |
| Direct Git gate audit across the three local canaries | NO_GIT_REPO, NO_PRECOMMIT_GATE, NO_PREPUSH_GATE |
| `python3 scripts/tes_install.py --self-test` | PASS after source repair |
| `python3 scripts/installed_certification_oracle.py --self-test` | PASS after source repair |
| `python3 scripts/tes_init.py --self-test` | PASS after source repair |
| `node src/adapters/claude/skills/tes-goal-maestro/scripts/validate-walls.mjs` | PASS, 138/138 walls |
| `node src/adapters/codex/skills/tes-goal-maestro/scripts/validate-walls.mjs` | PASS, 138/138 walls |
| `node .agents/skills/tes-goal-maestro/scripts/validate-walls.mjs` | PASS, 138/138 walls |
| `node .claude/skills/tes-goal-maestro/scripts/validate-walls.mjs` | PASS, 138/138 walls |
| `python3 scripts/materialize_adapter.py all --check` | PASS |
| `python3 scripts/validate_reference_package.py` | PASS |
| `python3 scripts/validate_tds.py` | PASS |
| `python3 scripts/build_public_docs.py --check` | PASS |
| `python3 scripts/public_bundle_oracle.py` | PASS for `0.3.231`, sha256 `2a548463442e6e2c1a66337b1d2d4905daad49f4bb7a4ca3875c998afc68dac3` |
| `python3 scripts/tes_bundle.py --self-test` | PASS |
| `python3 scripts/tes_bump.py --governance-check --json` | PASS, version bump surfaces synchronized |
| `python3 scripts/command_trigger_oracle.py --self-test` | PASS |
| `python3 scripts/tes_npx_oracle.py --self-test` | PASS |
| `python3 scripts/platform_surface_oracle.py --self-test` | PASS |
| `python3 scripts/validate_doc_size.py --paths ...` | PASS |
| `python3 scripts/private_vocabulary_oracle.py --paths ...` | PASS |
| `git diff --check` | PASS |
| Fresh replay `cursor`: install, postinstall, `/tes-align`, `/tes-map`, installed certification | PASS; hook health `NEEDS_EVIDENCE` until native host runtime rows exist |
| Fresh replay `claude`: install, postinstall, `/tes-align`, `/tes-map`, installed certification | PASS; hook health `NEEDS_EVIDENCE` until native host runtime rows exist |
| Fresh replay `codex`: install, postinstall, `/tes-align`, `/tes-map`, installed certification | PASS; hook health `NEEDS_EVIDENCE` until native host runtime rows exist |

## Required Repair Before Goal Maestro

1. Reinstall the original canary set from package `0.3.231`, or replace it with
   fresh Git-backed canaries.
2. Run postinstall before `/tes-align`; install alone is only the pending
   first-session state.
3. Re-run installed certification and hook health on the final canary set.
4. Require direct final-state evidence that `.codex/config.toml`,
   `.claude/settings.json`, and `.cursor/hooks.json` either contain the
   expected TES hook entrypoints or are explicitly outside the canary scope.
5. Require nonzero `.tes/runtime/hooks/executed.jsonl` evidence for the host
   that will execute Goal Maestro, or explicitly downgrade the claim to
   configured-only.
6. Before Goal Maestro execution, classify commit enforcement from evidence:
   `manual`, `no-commit`, or `precommit_enforced`.
7. If `precommit_enforced` is required, initialize/repair the target Git gate
   and prove it with a Git repository, `core.hooksPath` or default hook path,
   an executable `pre-commit` hook or governed equivalent, and a gate command
   rerun. Otherwise, explicitly carry the manual/no-precommit downgrade.
8. Keep Field Reports `pre-push` evidence separate from Git `pre-commit`
   evidence: fresh replay proves `pre-push` after postinstall, not
   `pre-commit`.

## Boundary

This report is a preflight audit. It does not change installed canaries, does
not repair the original `codex` target, does not start Goal Maestro, does not
push, and does not publish a remote release. It does make a local release
identity decision: repaired source is `0.3.231` with a certified local public
bundle, but the fixed GitHub ref is not certified until an authorized tag/push
and `npm run release:check`.
