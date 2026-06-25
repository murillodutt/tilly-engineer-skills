---
tds_id: roadmap.goal_super_spec_tes_npx_mcp_convergence
tds_class: roadmap
status: active
consumer: maintainers, installer authors, MCP maintainers, adapter maintainers, release reviewers, and execution agents
source_of_truth: false
evidence_level: L2
tver: 0.1.0
---

# GOAL Super SPEC: TES NPX MCP Convergence

Status: implementation planning artifact for the next package-source cut after TES `0.3.144`.

Capability: make the `npx`/`bunx` installer the primary local executor for project-scoped Cortex MCP installation, update, and repair across the TES runtime adapters while preserving `/tes-init` and `/tes-setup` as automatic post-install redundancy and `/tes-doctor` as the repair fallback.

## Mantra Gate Snapshot

| Field | Decision |
|-------|----------|
| VERIFY | Local analysis reproduced that `npx add --agent all --yes` installs TES helpers and hooks but does not register `tes-cortex` MCP until `install_mcp.py` runs. |
| SCOPE | Plan only. No implementation, version bump, bundle, tag, push, or release certification in this artifact. |
| BEST_PATH | Reuse `install_mcp.py` from `tes_install.py`; do not duplicate host-specific MCP config logic. |
| DOCUMENT | Record goal, decisions, non-objectives, implementation units, oracles, and correlated surfaces in this roadmap SPEC plus indexes. |
| ORACLE | For this planning cut, run `python3 scripts/validate_tds.py` and a focused doc/index check. Implementation will add installer and MCP oracles. |
| RESOLVE | Proceed with a Super SPEC because the behavior change is adopter-visible and needs release identity before execution. |
| STATUS | GO for documentation planning only. |

## Authority

| Layer | Role |
|-------|------|
| Maintainer correlation rule | Classifies installer, MCP activation, adapter docs, public docs, package scripts, and release identity as correlated surfaces for delivered behavior. |
| Platform differences reference | Keeps VS Code MCP as consumer config, not a TES adapter, unless a future explicit decision changes that boundary. |
| `scripts/install_mcp.py` | Existing source of truth for host-specific MCP helper copy, config merge, validation, and self-test. |
| `scripts/tes_install.py` | Existing source of truth for the thin `npx`/`bunx` installer and first-session postinstall bootstrap. |
| `src/adapters/**` | Delivered adapter instructions that define `/tes-init`, `/tes-setup`, `/tes-update`, `/tes-mcp`, and `/tes-doctor` behavior. |

## Problem

The current installer flow is split in a way that makes first-time MCP activation depend on a later skill path:

- `bin/tes.js` delegates to `scripts/tes_install.py install`.
- `scripts/tes_install.py install` stages and applies the bundle, installs selected agent hooks, writes `.tes/postinstall.json`, and writes the install lock.
- The bundle delivers `.tes/bin/install_mcp.py` and `.tes/bin/cortex_mcp.py`, but the installer does not register `tes-cortex` in project-scoped MCP configs.
- The first-session postinstall runs `tes_init.py`, `project_context_oracle.py`, and `project_alignment_oracle.py`; it also does not register or certify MCP.
- `/tes-mcp` and `/tes-doctor` can install or repair MCP, but they are downstream manual routes rather than the primary installation path.

That split creates a false completion risk: a target can have TES helpers, hooks, skills, and `.codex/config.toml` while still lacking a registered `tes-cortex` MCP server.

## Goal

After this goal is implemented, a normal local install or update must make Cortex MCP project-scoped config ready for the selected TES runtime adapters:

```text
npx/bunx add -> bundle apply -> hooks -> MCP config -> postinstall sentinel -> lock
```

`/tes-init` and `/tes-setup` must remain useful as automatic post-install redundancy and reporting. `/tes-doctor` must remain the fallback repair path for MCP drift, conflicts, or host recognition problems.

## Decisions

| Decision | Rationale |
|----------|-----------|
| `npx` is the primary installer for MCP. | Adopters expect install/update/correction to happen through the package installer, not only through follow-up skills. |
| Reuse `install_mcp.py`; do not reimplement MCP merge logic in `tes_install.py`. | Host-specific config schemas, helper copy, validation, backups, and governed-write defaults already live behind the MCP installer contract. |
| `--agent all` maps to Codex, Claude Code, and Cursor for TES adapter behavior. | `bin/tes.js` and `scripts/tes_install.py` define TES agents as `codex`, `claude`, and `cursor`. |
| VS Code MCP stays explicit. | VS Code has certified project-scoped MCP config, but it is not a TES adapter with skills, rules, hooks, or bootloader semantics. |
| Default MCP remains governed-write capable. | ADR 0002 remember tools are already limited by exact approval and evidence requirements; read-only remains explicit. |
| Installer repair may overwrite TES-owned `tes-cortex`. | Update and correction require repairing stale TES-owned server entries while preserving unrelated user MCP servers. |
| Host recognition is separate from file registration. | Config presence can be certified locally; host listing, approval, reload, or connection may still require runtime-specific action. |

## Non-Objectives

- Do not add global MCP config writes.
- Do not make VS Code part of `--agent all` in this cut.
- Do not add remote, cloud, marketplace, publish, push, or tag actions.
- Do not add new MCP tools or expand write authority.
- Do not rename `tes-cortex`.
- Do not claim host-connected status from config file presence.
- Do not promote private canary project names, paths, commands, or vocabulary into TES source, docs, fixtures, commits, evidence, or release notes.

## Implementation Units

| Unit | Owned Surfaces | Required Behavior | Focused Oracle |
|------|----------------|-------------------|----------------|
| SPEC-001 Installer MCP bootstrap | `scripts/tes_install.py`, `scripts/tes_npx_oracle.py`, `scripts/install_smoke.py` | `install` calls the installed MCP helper after bundle apply and hook install, records MCP summary in installer JSON, and fails or marks `NEEDS_REVIEW` on unrepaired MCP config failure. | `python3 scripts/tes_install.py --self-test`; `python3 scripts/tes_npx_oracle.py --self-test` |
| SPEC-002 Route mapping | `scripts/tes_install.py`, `bin/tes.js`, installer docs | Selected TES agents map to MCP adapters; `all` means `codex,claude,cursor`; VS Code remains an explicit MCP route. | New fixture proves `--agent all` creates Codex, Claude, and Cursor MCP configs but not `.vscode/mcp.json`. |
| SPEC-003 Postinstall redundancy | `scripts/tes_install.py`, adapter init/setup skills | First-session postinstall verifies or repairs MCP idempotently before marking setup complete, or records `needs_review` with a concrete MCP failure. | Hook fixture proves completed postinstall includes MCP command evidence and retry is quiet/idempotent. |
| SPEC-004 Update convergence | `scripts/tes_update.py`, `/tes-update` skills, update docs | Update planning includes MCP config refresh when adapter config or full convergence is required, not helper-only copy alone. | `python3 scripts/tes_update.py --self-test` plus fixture for stale `tes-cortex` config. |
| SPEC-005 Doctor fallback | `/tes-doctor`, `/tes-mcp`, docs | Doctor remains fallback for drift, explicit repair, host recognition, and certification; it no longer carries first-install MCP responsibility. | Existing MCP fallback instructions still pass platform surface and command trigger checks. |
| SPEC-006 Correlation and release identity | `package.json`, script `VERSION` constants, public docs, bundle surfaces, indexes | Delivered behavior change has an explicit version/bundle decision before closure. | `npm run commit:check`; release check only after authorized tag/push. |

## Expected Installer Semantics

### Fresh install

| Input | Expected Project-Scoped MCP Config |
|-------|------------------------------------|
| `--agent codex` | `.codex/config.toml` contains `[mcp_servers.tes-cortex]`. |
| `--agent claude` | `.mcp.json` contains `mcpServers.tes-cortex`. |
| `--agent cursor` | `.cursor/mcp.json` contains `mcpServers.tes-cortex`. |
| `--agent all` | Codex, Claude Code, and Cursor MCP configs are present. |

Fresh install must also copy MCP helpers under `.tes/bin/**`, preserve unrelated MCP servers, record field-report/git-exclude hygiene through the MCP installer, and leave postinstall ready to verify the same state.

### Update or repair

When existing `tes-cortex` config differs from the packaged desired config, the installer may overwrite that TES-owned entry after user installer consent. It must not overwrite unrelated MCP server entries.

If existing host config is invalid JSON/TOML, or if repair cannot be performed without risk, the installer must report `NEEDS_REVIEW` or `FAIL` with the specific config path and leave `/tes-doctor` as the explicit repair route.

### Dry run

`--dry-run` must include planned MCP helper/config actions in the installer summary without writing files.

### No postinstall

`--no-postinstall` disables the first-session semantic bootstrap only. It must not disable installer-time MCP config registration unless a future explicit `--no-mcp` flag is authorized.

## Result Shape

The installer JSON summary should expose MCP as a first-class section:

```json
{
  "mcp": {
    "status": "INSTALLED",
    "adapters": ["codex", "claude", "cursor"],
    "server": "tes-cortex",
    "configs": [],
    "config_registrations": [],
    "failures": []
  }
}
```

The summary must not claim `host_connected`. Runtime host recognition remains reported separately by `/tes-mcp` or `/tes-doctor`.

## Acceptance Criteria

- `npx`/`bunx` install with `--agent all --yes` registers `tes-cortex` for Codex, Claude Code, and Cursor in project-scoped config.
- `--agent all` does not create `.vscode/mcp.json`.
- Existing unrelated MCP servers survive installer updates.
- Stale TES-owned `tes-cortex` entries are repaired or reported with an actionable `NEEDS_REVIEW`/`FAIL`.
- `/tes-init` and `/tes-setup` can report or recover postinstall MCP state without becoming the primary MCP installer.
- `/tes-doctor` remains the explicit fallback for MCP repair and host recognition checks.
- Tests distinguish `config_present`, `server_self_test_pass`, `protocol_handshake_pass`, `host_listed`, `host_connected`, and `session_restart_required`.
- Correlated docs, adapter instructions, public docs, package metadata, bundle surfaces, and release identity are resolved before closure.
- Private vocabulary oracle passes.

## Required Oracles Before Implementation Closure

Run the smallest focused oracles first, then the package gate:

```bash
python3 scripts/install_mcp.py --self-test
python3 scripts/tes_install.py --self-test
python3 scripts/tes_npx_oracle.py --self-test
python3 scripts/install_smoke.py --route mcp
python3 scripts/tes_update.py --self-test
python3 scripts/validate_tds.py
npm run commit:check
```

If delivered behavior is implemented and authorized for release identity, prepare the versioned public bundle and run the release checklist before claiming any fixed GitHub `npx` ref is certified.

## Open Questions

| Question | Default For Implementation |
|----------|----------------------------|
| Should there be an explicit `--no-mcp` escape hatch? | No, unless a real adopter scenario needs it. |
| Should `bin/tes.js` accept `--agent vscode`? | No in this cut; VS Code is explicit MCP consumer config, not a TES adapter. |
| Should postinstall repair MCP with `--overwrite`? | Yes for TES-owned `tes-cortex`, while preserving unrelated servers. |
| Should MCP failure block install completely? | Block or mark `NEEDS_REVIEW` depending on existing installer semantics; do not print `INSTALLED` while MCP registration failed silently. |
