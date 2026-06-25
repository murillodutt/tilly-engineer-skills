---
tds_id: roadmap.goal_super_spec_tes_runtime_surface_attach_detach
tds_class: roadmap
status: proposed
consumer: maintainers, installer authors, MCP authors, hook authors, oracle authors, release reviewers, and execution agents
source_of_truth: false
evidence_level: L2
tver: 0.1.0
---

# GOAL Super SPEC: TES Runtime-Surface Attach/Detach

Status: proposed execution contract derived from ADR 0004 (active). Third execution line of capsule-first isolation. It completes attach/detach for the surfaces produced by runtime writers outside the bundle manifest — `mcp`, `hooks`, and `docs-mesh` — which the prior line (0.3.161) deliberately left as `NEEDS_REVIEW` because no remover existed.

Capability: make `mcp`, `hooks`, and `docs-mesh` individually attachable and detachable with the same reversibility guarantees as manifest-backed surfaces, so a user can add or remove any TES surface without reinstalling and without losing project-owned content.

## Canonical Artifact

Canonical Super SPEC: `docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-tes-runtime-surface-attach-detach.md`

Primary decision source: `docs/adr/0004-tes-capsule-isolation-and-reversible-installation.md` (sections `### Installer model` and `### Attach-health contract for MCP and hooks`).

Related implementation surfaces:

- `scripts/install_mcp.py` and `scripts/install_mcp_hosts/**` (MCP writers)
- `scripts/tes_install.py` (`install_codex_hook`, `install_claude_hook`, `install_cursor_hook`, `remove_tes_claude_sessionstart_hooks`, `attach`, `detach`)
- `scripts/tes_init.py` (docs-mesh writer, `tes-project-manifest.json` writes)
- `scripts/tes_bundle.py` (`detach_surface`, `MANIFEST_BACKED_SURFACES`)
- `scripts/capsule_residue_oracle.py` and `scripts/attach_health_oracle.py`
- `scripts/install_smoke.py`

## Mantra Gate Snapshot

| Field | Record |
|-------|--------|
| `VERIFY` | ADR 0004 (active); the shipped 0.3.160/0.3.161 lines; the manifest-backed detach machine and the `NEEDS_REVIEW` fallback for runtime surfaces; the MCP `merge_into_existing` writer (`install_mcp_hosts/base.py`) with NO remover today; the hook writers in `tes_install.py` with a remover only for Claude (`remove_tes_claude_sessionstart_hooks`); `tes_init` writing `docs/agents/**` and a `tes-project-manifest.json` writes list; docs-mesh being project-owned (uninstall preserves it). All inspected before writing. |
| `SCOPE` | Add this Super SPEC and correlated indexes now (planning-only, version-neutral). The runtime slices it specifies are delivered behavior and carry a patch bump per ADR 0004 Release Identity. |
| `BEST_PATH` | Build each remover as the precise inverse of its writer: MCP removes the `tes-cortex` key from the host server map preserving other servers; hooks remove only TES handlers per host; docs-mesh detach preserves project-owned content by default and removes only with explicit `--purge`. Then promote these surfaces out of the `NEEDS_REVIEW` fallback. |
| `DOCUMENT` | This Super SPEC plus `docs/roadmap/README.md`, `docs/INDEX.md`, `docs/tds/DOCS-INDEX.yml`, and `docs/install/AGENT-ORACLE-INVENTORY.md`. |
| `ORACLE` | `python3 scripts/validate_tds.py`, `python3 scripts/validate_doc_size.py`, `python3 scripts/validate_reference_graph.py`, `python3 scripts/private_vocabulary_oracle.py`, `git diff --check` for this planning artifact; the per-unit focused oracles below for each runtime slice. |
| `RESOLVE` | No private target identifiers enter TES. Removers preserve user-owned config and content; ambiguous removals stop with NEEDS_REVIEW. |
| `STATUS` | `PROCEED` |

## Governing Matrix

| Layer | Meaning |
|-------|---------|
| ADR 0004 | Every project-visible surface is an explicit reversible attachment; detach removes exactly one surface and preserves project-owned content. |
| Manifest `@2` | Drives manifest-backed surfaces (capsule, root-context). Runtime surfaces are not in the manifest; they need writer-inverse removers. |
| Writer-inverse removers | MCP, hook, and docs-mesh removers must be the precise inverse of their writers, preserving any user-owned neighbors (other MCP servers, non-TES hooks, project docs). |
| Attach-health | The 0.3.161 attach-health oracle already proves these surfaces via MCP handshake and hook sentinel; this line makes detach honest too. |
| Non-Change | Does not add GPS capsule mode, Goal Maestro capsule destination, Mantra Gate modes, write-capable MCP, automatic Cortex writes, or remote/publish actions. |

## Current Meaning

`detach mcp`, `detach hooks`, and `detach docs-mesh` return `NEEDS_REVIEW` today because their files are produced outside the bundle and no remover exists: `install_mcp` only installs/merges, only Claude has a hook remover, and `docs/agents/**` is project-owned. This line builds the missing removers as exact inverses of the writers and promotes the three surfaces into real detach.

## Invariants (must hold after every unit)

- Writer-inverse precision: a remover removes only what TES wrote and preserves every user-owned neighbor (other MCP servers, non-TES hooks, project docs).
- Detach reversibility: after detach, attach-health for that surface reports NOT_APPLIED and the residue oracle shows it gone (or, for docs-mesh, preserved-as-project-content).
- Project content is sacred: docs-mesh detach preserves `docs/agents/**` by default; removal requires explicit `--purge` and is reported file by file.
- sha256/user-edit safety: a user-modified TES config or hook is preserved and reported `needs-review`, never silently rewritten or deleted.
- No false green: detach `PASS` requires the surface to be actually gone (or explicitly preserved); a no-op on a present surface is not PASS.

## Required Fix Matrix

| Fix | Owned Surface | Gap Today | Required Correction | Focused Oracle |
|-----|---------------|-----------|---------------------|----------------|
| MCP remover | `scripts/install_mcp_hosts/**`, `scripts/install_mcp.py` | `merge_into_existing` adds `tes-cortex`; no inverse. | Add `remove_registration` removing only the `tes-cortex` key from the host server map, preserving other servers and the rest of the file; delete the file only if it becomes empty and TES created it. | `python3 scripts/install_mcp.py --self-test`. |
| Hook removers (Codex, Cursor) | `scripts/tes_install.py` | Only Claude has a remover. | Add `remove_tes_codex_hooks` and `remove_tes_cursor_hooks` as inverses of the writers, preserving non-TES hooks; unify a `remove_tes_hooks(target, agent)` entry. | `python3 scripts/tes_install.py --self-test`. |
| docs-mesh detach | `scripts/tes_bundle.py` or `scripts/tes_init.py` | docs/agents is project-owned; no detach path. | Add a docs-mesh detach that preserves `docs/agents/**` by default and removes only generated files (per the `tes_init` writes list) when `--purge` is passed; report preserved vs removed. | `python3 scripts/tes_init.py --self-test`. |
| Promote surfaces in detach_surface | `scripts/tes_bundle.py` | mcp/hooks/docs-mesh return NEEDS_REVIEW. | Route these surfaces to their removers and drop them from the `NEEDS_REVIEW` fallback; keep gps/goals (still nonexistent) in the fallback. | `python3 scripts/tes_bundle.py --self-test`. |
| attach for runtime surfaces | `scripts/tes_install.py` | attach returns NEEDS_REVIEW for runtime surfaces. | `attach mcp` runs the MCP installer; `attach hooks` runs the hook writers; `attach docs-mesh` runs tes_init. Each then verifies via the attach-health oracle. | `python3 scripts/tes_install.py attach --dry-run`. |
| Round-trip coverage | `scripts/install_smoke.py` | Round-trip covers only manifest-backed surfaces. | Extend the attach/detach round-trip probe to mcp, hooks, and docs-mesh: attach, assert attach-health, detach, assert gone/preserved and neighbors intact. | `python3 scripts/install_smoke.py --self-test`. |

## Execution Discipline

Run units sequentially. Do not implement a later unit before the current unit has its focused oracle green, a release identity classification, and a closure note. Before each unit state owned files, no-touch files, release identity impact, focused oracle, and stop condition.

## SPEC-000: Reentry And Boundary

Owned files: this Super SPEC; no runtime files.

Tasks:

1. `git status --short --branch --untracked-files=all` and `git log -8 --oneline`.
2. Classify dirty changes as inherited, current-task delta, or unrelated.
3. Confirm no private target evidence enters TES.
4. Confirm this planning artifact is doc-only and version-neutral.

Focused oracle:

```bash
python3 scripts/validate_tds.py
python3 scripts/private_vocabulary_oracle.py
git diff --check
```

Closure note: SPEC-000 PASS means a clean boundary and the writers (MCP merge, hook writers, tes_init) are confirmed as the inverses to build against.

## SPEC-001: MCP Registration Remover

Owned files: `scripts/install_mcp_hosts/base.py` and each host module; `scripts/install_mcp.py`.

Implementation:

1. Add `remove_registration(target, ...)` to each host: parse the config, delete only the `tes-cortex` entry from the `server_key` map, write back preserving field order and other servers.
2. If the server map becomes empty and TES created the file, remove the file; otherwise keep the user's file.
3. If the existing `tes-cortex` entry was user-modified away from the expected shape, preserve and report `needs-review`.

Release identity impact: delivered behavior; patch bump decided at SPEC-007.

Focused oracle:

```bash
python3 scripts/install_mcp.py --self-test
```

Stop condition: if a host config shape cannot be safely edited (unknown structure), stop with `NEEDS_REVIEW` rather than rewriting the file.

## SPEC-002: Hook Removers (Codex, Cursor)

Owned files: `scripts/tes_install.py`.

Implementation:

1. Add `remove_tes_codex_hooks(data)` and `remove_tes_cursor_hooks(data)` as inverses of `install_codex_hook` / `install_cursor_hook`, removing only TES handlers (matched by the TES command token) and preserving non-TES hooks.
2. Add a unified `remove_tes_hooks(target, agent)` that writes back the cleaned config and removes the file only if TES created it and it is now empty.
3. Reuse the existing Claude remover; keep idempotency (removing twice is safe).

Release identity impact: delivered behavior; patch bump decided at SPEC-007.

Focused oracle:

```bash
python3 scripts/tes_install.py --self-test
```

Stop condition: if a host hook block mixes TES and user handlers ambiguously, preserve the block and report `needs-review`.

## SPEC-003: docs-mesh Detach (Project-Content-Safe)

Owned files: `scripts/tes_bundle.py` or `scripts/tes_init.py`.

Implementation:

1. Add a docs-mesh detach that, by default, preserves `docs/agents/**` (it is project-owned content) and reports it as preserved.
2. With explicit `--purge`, remove only files TES generated, read from the `tes_init` writes list / project manifest; never delete files the project added under `docs/agents/**`.
3. Report preserved vs removed file by file.

Release identity impact: delivered behavior; patch bump decided at SPEC-007.

Focused oracle:

```bash
python3 scripts/tes_init.py --self-test
```

Stop condition: if generated vs project-authored files under `docs/agents/**` cannot be distinguished, default to preserve and report `needs-review`.

## SPEC-004: Promote Surfaces In detach_surface

Owned files: `scripts/tes_bundle.py`.

Implementation:

1. Route `mcp`, `hooks`, `docs-mesh` to their removers (SPEC-001..003) instead of the `NEEDS_REVIEW` fallback.
2. Keep `gps`/`goals` in the fallback (still produced by no writer).
3. Preserve the capsule guard and unknown-surface guard.

Release identity impact: delivered behavior; patch bump decided at SPEC-007.

Focused oracle:

```bash
python3 scripts/tes_bundle.py --self-test
```

Stop condition: if a remover reports `needs-review`, surface it through detach, do not downgrade to a clean DETACHED.

## SPEC-005: Attach For Runtime Surfaces

Owned files: `scripts/tes_install.py`.

Implementation:

1. `attach mcp` runs the MCP installer for the selected agent; `attach hooks` runs the hook writers; `attach docs-mesh` runs tes_init.
2. After each attach, verify with the attach-health oracle and fold the verdict into the result.
3. Drop these surfaces from the attach `NEEDS_REVIEW` fallback.

Release identity impact: delivered installer behavior; patch bump decided at SPEC-007.

Focused oracle:

```bash
python3 scripts/tes_install.py attach mcp --dry-run --target <fixture>
python3 scripts/tes_install.py --self-test
```

Stop condition: if an attach cannot verify its surface health, report the explicit pending/unobservable state, not a clean ATTACHED.

## SPEC-006: Round-Trip Coverage

Owned files: `scripts/install_smoke.py`.

Implementation:

1. Extend the attach/detach round-trip probe to mcp, hooks, and docs-mesh.
2. For each: attach, assert attach-health PASS (or the explicit pending state), detach, assert the surface is gone (or docs-mesh preserved) and that user-owned neighbors survived.

Release identity impact: delivered test behavior; participates in the patch release because runtime changed earlier.

Focused oracle:

```bash
python3 scripts/install_smoke.py --self-test
```

Stop condition: if a neighbor (other MCP server, non-TES hook, project doc) is disturbed by a remover, the remover is not writer-inverse — stop and fix it.

## SPEC-007: Release Identity And Closure

Owned files: `package.json`, `bin/tes.js` `TES_VERSION`, script `VERSION` constants, correlated bundle/public surfaces; docs/evidence only if retained.

Tasks:

1. Classify release identity: SPEC-001..006 change delivered installer and oracle behavior — a patch bump is required unless the owner explicitly defers, per ADR 0004 Release Identity.
2. Run every implemented unit's focused oracle.
3. Run baseline gates and `npm run commit:check`.
4. If a bump is performed, run the bundle/governance checks via the source release flow (do not partial-bump the source package).

Stop condition: if release identity requires a bump and owner authorization for remote actions is unclear, stop with `NEEDS_REVIEW` and keep the work local.

## Private Vocabulary Guard

No private project names, repository paths, remotes, commit narratives, target product vocabulary, domain decisions, or canary identifiers may enter TES. Use generic forms only: `target project`, `private target canary`, `<absolute-path>`, `<redacted-token>`.

## Evidence Plan

| Evidence | Location | Requirement |
|----------|----------|-------------|
| Unit self-test output | closeout summary or retained report | Commands and PASS/FAIL only. |
| Writer-inverse proof | retained report | Generic; assert TES removed only its own entries and preserved user neighbors. |
| docs-mesh preserve proof | retained report | Assert project content survived detach without identifiers. |

## Final Closure Report Requirements

The executor must report: implemented SPEC units; files changed; release identity decision; focused oracle results; baseline gate results; whether `npm run commit:check` passed; confirmation that removers are writer-inverse and preserve user neighbors; residual risks; deferred work (GPS capsule mode, Goal Maestro capsule destination, Mantra Gate modes); and confirmation that no private target identifiers were added.
