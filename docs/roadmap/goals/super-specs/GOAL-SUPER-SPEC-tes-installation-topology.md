---
tds_id: roadmap.goal_super_spec_tes_installation_topology
tds_class: roadmap
status: proposed
consumer: maintainers, installer authors, hook authors, MCP authors, oracle authors, release reviewers, and execution agents
source_of_truth: false
evidence_level: L2
tver: 0.1.0
---

# GOAL Super SPEC: TES Installation Topology

Status: proposed execution contract extending ADR 0004 (active). This is an asset-organization restructure, not a product behavior change: install, update, postinstall, hooks, restore, uninstall, and rollback must remain equivalent or better. What changes is *where assets live*, so TES stops copying heavy runtime into every target repo (measured today: 3.3 MB / 48 files of identical runtime under `<repo>/.tes/bin/**` per install).

Capability: split installed assets across three homes by a deterministic classification, bridged by a stable pointer keyed on the target's real path — never duplicated, never random-keyed.

## The Formula (topology classification)

For every installed asset, ask in order; the first "yes" decides its home.

| # | Question | Home | Why |
|---|----------|------|-----|
| 1 | Does a host physically require this file at a fixed in-repo path? | `<repo>/` | Non-negotiable platform edge. These are *pointers/config*, not runtime. |
| 2 | If deleted, is the content reconstructible without loss (identical across installs, or a derived cache)? | `~/.tes/runtime/<version>/` (shared, read-only) or regenerate | Shared code is not shared state. |
| 3 | Is it unique to this project AND is its loss irreversible? | `~/.tes/projects/<slug>/` | Durable, per-project, outside the repo so it neither contaminates nor vanishes with `.tes/`. |

Anything left is identity/pointers only → the minimal `<repo>/.tes/` capsule.

### Asset placement (the formula applied)

| Asset | Q | Home |
|-------|---|------|
| `.claude/settings.json`, `.codex/config.toml`, `.cursor/hooks.json`, `.cursor/mcp.json`, `.mcp.json` | 1 | `<repo>/` (host reads exact path; **contains a pointer to runtime — that pointer may be global**) |
| `.git/hooks/pre-push` | 1 | `<repo>/.git/hooks/` (git requires it) |
| Bootloaders `CLAUDE.md`/`AGENTS.md`/`CURSOR.md`, skills `.claude/skills/**`, `.agents/skills/**`, `.cursor/rules/**` | 1 | `<repo>/` (host discovers by path convention) |
| `.tes/bin/**` runtime helpers (48 files, identical per version) | 2 | `~/.tes/runtime/<version>/` |
| `recall.sqlite`, `semantic.sqlite`, `__pycache__` | 2 | derived cache → `~/.tes/projects/<slug>/cache/` (rebuildable; never the repo). It lives in the project namespace, not the capsule, precisely because it is rebuildable: a clone on another machine regenerates it from the versioned source rather than carrying a stale binary cache. |
| Pre-install context backup, restore manifest, rollback substance, setup/materialization staging | 3 | `~/.tes/projects/<slug>/` |
| `manifest.json` (what was written *in this repo* — the detach/uninstall worklist) | — | **mirrored: `<repo>/.tes/` AND `~/.tes/projects/<slug>/`** |
| `tes-install-lock.json` (version + slug + pointer), live state that must travel with the repo | — | `<repo>/.tes/` minimal capsule |

The manifest is **mirrored**, not relocated. The capsule copy serves the common case (fast, local detach/uninstall). The project-namespace copy exists so that uninstall/restore can reconstruct the in-repo worklist — what TES wrote and must remove — *even when the local capsule is gone*. Without the mirror, deleting `<repo>/.tes/` would erase the only record of what to clean from the repo, making oracle #3 (capsule-loss restore) unfalsifiable: restore could recover backed-up context but could not know which configs/skills/bootloaders to strip. The two copies are written together and must stay byte-identical; a divergence is a defect, and the project-namespace copy is authoritative on capsule loss. The capsule copy is derived (rebuildable from the global copy via the realpath slug), so the capsule stays minimal in spirit — it holds a *cache* of the worklist, not its only home.

## The Pointer (deterministic project key)

```
slug = safe_slug(os.path.realpath(target))[:12] + "-" + sha256(realpath)[:12]
```

- Keyed on `realpath(target)`, NOT on `install_id` (a random UUID living in the capsule, `field-reports/install_id`). The repo must find its global project namespace **even if `<repo>/.tes/` is deleted** — `realpath` is the only stable thing that survives capsule loss; `install_id` is not.
- `safe_slug` already exists (`scripts/field_reports.py:179`) — reuse it.
- The path-hash component disambiguates two projects with the same basename (oracle #4). Same-name, different-path → different slug.

## Invariants (must hold after every unit)

- Behavioral equivalence: install/update/postinstall/hooks/restore/uninstall/rollback produce the same observable outcome as the pre-restructure baseline, or strictly better. No capability regresses.
- Runtime is shared *code*, not shared *state*: `~/.tes/runtime/<version>/` is read-only and identical across projects. This does NOT violate ADR 0004 inbound isolation because no project state is shared.
- State isolation is absolute: `~/.tes/projects/<slug>/` is the isolation boundary. No project may read or write another project's namespace. This is the ADR 0004 invariant, refined: "global compartmentalized per project" is allowed; "global state shared between projects" is not.
- Reversibility survives capsule loss: uninstall/restore reconstruct from `~/.tes/projects/<slug>/` using the realpath-derived slug, even if `<repo>/.tes/bk` (or all of `<repo>/.tes/`) is absent. This requires the manifest worklist to be mirrored into the project namespace (capsule copy is a derived cache); the project-namespace copy is authoritative on capsule loss.
- Pointer integrity: every host config and hook references a path that exists. A reference to a missing runtime is a hard failure (oracle #5 — the highest-risk regression this line can introduce).
- Migration safety: an install made by an older version migrates forward without losing restore capability, and the migration is itself reversible (rollback).
- Migration ordering (no dangling-pointer window): migration must never leave a host config or hook pointing at a path that does not exist, not even mid-run. The only safe order is (1) write runtime to the global home, (2) rewrite every config/hook pointer to the global path, (3) verify every rewritten pointer resolves to an existing file, (4) only then prune the in-repo runtime. If the process is interrupted before step 4, configs still point at the intact in-repo runtime; if interrupted after step 4, they point at the verified global one. Pruning before verification is forbidden.
- Capsule minimality: `<repo>/.tes/` carries identity + pointers + the manifest worklist cache only; no heavy runtime, no backup, no rebuildable index. The concrete contents are exactly: `tes-install-lock.json` (version, slug, pointer to the project namespace) and the `manifest.json` worklist cache. "Live state that must travel with the repo" is, in this design, the empty set — the slug is re-derivable from realpath and the manifest mirror is authoritative globally, so nothing in the capsule is irreplaceable. If a future need for must-travel state appears, it must be added here explicitly, not assumed.

## Required Fix Matrix

| Fix | Owned Surface | Gap Today | Required Correction | Focused Oracle |
|-----|---------------|-----------|---------------------|----------------|
| Topology resolver | new `scripts/tes_paths.py` | No notion of runtime-global / project-global; everything resolves under `<repo>/.tes/`. | Add `runtime_root(version)`, `project_root(target)` (realpath slug), `capsule_root(target)`; single source of truth for every path decision. | `python3 scripts/tes_paths.py --self-test`. |
| Runtime centralization | `scripts/tes_bundle.py`, `scripts/tes_install.py` | `.tes/bin/**` copied into every repo. | Stage runtime into `~/.tes/runtime/<version>/` once; the capsule keeps a pointer, not a copy. Idempotent across installs of the same version. | `tes_bundle.py --self-test`; `tes_install.py --self-test`. |
| Project namespace | `scripts/tes_install.py`, `scripts/tes_bundle.py` | Backup/setup/rollback live under `<repo>/.tes/bk`. | Write backup/restore-manifest/rollback to `~/.tes/projects/<slug>/`; capsule records the slug + pointer. | `install_smoke.py --self-test`. |
| Pointer-aware hooks/MCP | hook writers (`tes_install.py`), `install_mcp_hosts/**` | Configs reference `<repo>/.tes/bin/...`. | Emit the runtime-global path in each host format (toml, json, json) and host var convention (`CLAUDE_PROJECT_DIR`, `git rev-parse`, relative). Old installs rewritten on update. | hook + MCP self-tests; oracle #5. |
| Migration + rollback | `scripts/tes_install.py` (update path) | No migration from in-repo runtime to split topology. | `update` detects legacy in-repo runtime and migrates copy-then-verify-then-prune: copy runtime→global, mirror backup+manifest→project namespace, rewrite pointers, verify every pointer resolves, only then prune in-repo runtime; records a rollback manifest before pruning. | `install_smoke.py` migration probe + interrupted-migration probe (oracle #2). |
| Capsule-loss restore | `scripts/tes_bundle.py` (uninstall/restore) | Restore reads `<repo>/.tes/bk`. | Restore resolves the project namespace from `realpath` and reconstructs even with the local capsule gone. | `install_smoke.py` probe (oracle #3). |

## Execution Discipline

Run units sequentially. Do not implement a later unit before the current unit's focused oracle is green, with a release-identity note. Before each unit state owned files, no-touch files, release-identity impact, focused oracle, stop condition. **Do not alter the hook architecture itself** (the two-phase announce/rewake contract is fixed); only where its config points may change.

## SPEC-000: Reentry, Boundary, Baseline

Owned files: this Super SPEC; no runtime files.

Tasks:
1. `git status`, `git log -8`. Confirm clean boundary at the post-hook-fix HEAD.
2. Capture the pre-restructure baseline: a real install's full asset inventory (paths, sizes, hook/MCP pointer targets) as the equivalence reference.
3. Record the host-real canary baseline if available (hook fires, pre-push exists, oracles certify) — the behavior the restructure must preserve.

Focused oracle: `validate_tds.py`; `private_vocabulary_oracle.py`; `git diff --check`.

Stop condition: if the host-real baseline is not yet observed, the restructure may proceed against the bench baseline but the closeout claim is capped at "bench-equivalent", not "real-use-equivalent", until the host canary reruns.

## SPEC-001: Topology Resolver

Owned files: new `scripts/tes_paths.py`.

Implementation: pure path logic, no I/O side effects. `runtime_root(version)` -> `~/.tes/runtime/<version>`; `project_root(target)` -> `~/.tes/projects/<slug>` via realpath slug; `capsule_root(target)` -> `<repo>/.tes`. Honor a `TES_HOME` override for tests. Provide the slug function reusing `safe_slug`.

Focused oracle: `python3 scripts/tes_paths.py --self-test` (same realpath -> same slug; different path same basename -> different slug; capsule loss does not change the slug).

Stop condition: if any resolver needs the capsule to compute the project key, stop — the key must derive from realpath alone.

## SPEC-002: Runtime Centralization

Owned files: `scripts/tes_bundle.py`, `scripts/tes_install.py`.

Implementation: stage `.tes/bin/**` into `runtime_root(version)` once; reuse it across installs of that version; the capsule stores a pointer. Bundle/manifest unchanged in shape; only the destination of runtime entries moves.

Release identity impact: delivered behavior; bump decided at SPEC-006.

Focused oracle: `tes_bundle.py --self-test`; `tes_install.py --self-test`.

Stop condition: if two installs of the same version would race on the shared runtime dir, make the write atomic/idempotent before proceeding.

## SPEC-003: Project Namespace + Pointer-Aware Hooks/MCP

Owned files: `scripts/tes_install.py` hook writers, `scripts/install_mcp_hosts/**`, `scripts/tes_bundle.py`.

Implementation: backup/restore-manifest/rollback/setup -> `project_root(target)`. Write the manifest worklist to both the capsule and `project_root(target)` in the same operation, byte-identical (the mirror that makes capsule-loss restore work). Hook and MCP configs emit the runtime-global entrypoint path in each host format and var convention. **Hook two-phase contract unchanged** — only the path inside the command string moves.

Release identity impact: delivered behavior; bump at SPEC-006.

Focused oracle: hook self-tests; `install_mcp.py --self-test`; oracle #5 (every emitted config/hook references an existing path).

Stop condition: if any host format cannot express the global pointer safely, keep that host's runtime in-repo and record the exception explicitly — never emit a dangling pointer.

## SPEC-004: Migration, Rollback, Capsule-Loss Restore

Owned files: `scripts/tes_install.py` (update), `scripts/tes_bundle.py` (uninstall/restore).

Implementation: `update` migrates a legacy in-repo install to the split topology in the mandated dangling-pointer-free order — (1) copy runtime to the global home, (2) mirror the backup to the project namespace and write the manifest mirror, (3) rewrite every config/hook pointer to the global path, (4) verify every rewritten pointer resolves, (5) only then prune the in-repo runtime — and records a rollback manifest in the project namespace before step 5. The runtime is *copied then pruned*, never *moved*, so an interruption before step 5 leaves the legacy install fully intact. `uninstall`/restore resolve the project namespace from realpath and reconstruct even with the local capsule absent, using the project-namespace manifest mirror as the authoritative worklist.

Release identity impact: delivered behavior; bump at SPEC-006.

Focused oracle: `install_smoke.py --self-test` migration probe (#2), capsule-loss restore probe (#3), same-name no-collision probe (#4), and an interrupted-migration probe that stops after each step and asserts every config/hook still resolves (legacy intact before prune, global intact after).

Stop condition: if migration cannot prove restore is preserved, stop and keep the legacy layout for that install; never migrate destructively without a verified rollback. Pruning the in-repo runtime before all pointers are rewritten AND verified is forbidden — copy-then-verify-then-prune, never move-then-rewrite.

## SPEC-005: Full Oracle Coverage

Owned files: `scripts/install_smoke.py`, `scripts/installed_certification_oracle.py`, `scripts/attach_health_oracle.py`, `scripts/materialize_adapter.py` (checks only).

Implementation: encode all seven mandated oracles as probes:
1. new install creates runtime-global + project namespace + minimal capsule, with the manifest mirrored byte-identical into both the capsule and the namespace;
2. update migrates a legacy install without losing restore, and an interrupted-migration variant leaves every pointer resolvable at each step;
3. uninstall restores via the global namespace (using the namespace manifest mirror as the worklist) even if local `.tes/bk` — or all of `<repo>/.tes/` — is gone;
4. two same-name projects do not collide;
5. real hooks reference valid paths;
6. install_smoke + installed_certification + attach_health + materialize pass;
7. host-real canary per host AFTER the self-tests.

Release identity impact: delivered oracle behavior; bump at SPEC-006.

Focused oracle: the four oracles above, all green.

Stop condition: oracle #5 (valid pointer paths) is a hard gate — a single dangling hook/MCP pointer fails the line.

## SPEC-006: Release Identity, Host-Real Canary, Closure

Owned files: `package.json`, `bin/tes.js` `TES_VERSION`, script `VERSION` constants, correlated bundle/public surfaces.

Tasks:
1. Classify release identity (delivered behavior changed -> patch bump).
2. Run every focused oracle + `npm run commit:check`.
3. Host-real canary per host (codex, claude, cursor): install, open the project in the real host, observe the SessionStart/first-session hook fire, confirm `.tes/postinstall.json` and `.git/hooks/pre-push`, rerun `attach_health_oracle` (reads the execution sentinel) and `installed_certification_oracle`.
4. Only after step 3 may the closeout claim "product hooks converged in real use". Until then the maximum claim is "hooks written correctly to disk and the two-phase contract bench-certified".

Stop condition: bench green + host-real not yet observed -> ship as bench-certified, schedule the host-real canary, do not over-claim.

## Private Vocabulary Guard

No private project names, paths, remotes, or canary identifiers enter TES. Use `target project`, `<project-slug>`, `<absolute-path>`, `private target canary`.

## Evidence Plan

| Evidence | Location | Requirement |
|----------|----------|-------------|
| Pre/post asset inventory | closeout | Show runtime moved out of repo; capsule shrank; behavior equivalent. |
| Migration round-trip | retained report | Legacy install -> migrated -> rollback returns to legacy, no restore loss. |
| Capsule-loss restore | retained report | Delete `<repo>/.tes`, restore from global namespace succeeds. |
| Host-real canary per host | closeout or RUN-RECORD | Hook fire observed; sentinel + pre-push present; oracles certify. |

## Execution Findings (first attempt, 2026-06-05)

A first execution attempt completed SPEC-001 (the resolver, green and isolated) and built working production code for SPEC-002, then reverted SPEC-002 to keep the repository coherent. The attempt surfaced facts that re-shape the remaining units; treat these as binding for the next pass:

1. There are TWO runtime writers, not one: `tes_bundle.apply_staged_bundle` (the bundle path) AND `install_mcp.install_server_files` (which copies its own helper list into `<repo>/.tes/bin/` for the MCP attach path). Both must be centralized together or the capsule ends up half-populated.
2. There were TWO divergent helper lists: `tes_bundle.HELPER_FILES` (34) and `install_mcp.SERVER_FILES` (~30). The divergence is what left `tes_paths.py` (a transitive import of `tes_bundle`) uninstalled and broke the MCP server with `ModuleNotFoundError`. SERVER_FILES must derive from HELPER_FILES.
3. `tes_paths.py` must be a HELPER_FILE: once `tes_bundle` imports it, every context that imports `tes_bundle` (including the installed runtime) needs it.
4. SPEC-002 and SPEC-003 are INSEPARABLE in delivery. Centralizing the runtime without rewriting the hook pointer leaves the Claude/Codex/Cursor hooks pointing at `<repo>/.tes/bin/` which no longer exists — a dangling pointer, the exact oracle #5 regression. They must land in one coherent change, never committed separately. Merge SPEC-002 and SPEC-003 into one unit next pass.
5. The hook pointer carries a version-coupling trap: embedding `runtime/<version>/bin/...` in the host config means an update must rewrite every hook, or the hook points at an old runtime dir. Decide the hook pointer form explicitly (versioned-and-rewritten-on-update, or a stable `runtime/current` symlink the update repoints) before writing it.
6. The migration surface is ~50 in-repo `.tes/bin/` literal references across `tes_install.py` (21), `tes_bundle.py` (11), `install_mcp.py` (9), plus ~16 other scripts and ~10 oracles. Most are self-test assertions and fixtures encoding the runtime-in-repo baseline. Each needs a classification (runtime->global via a lookup helper, config->repo, or legacy path to keep). This is the bulk of the work and should be its own unit with a single shared `helper_lookup`/`physical_dest_for` seam so no literal `.tes/bin/` survives in logic.

Recommended re-sequencing for the next pass: keep SPEC-001 (done); make a single "centralize runtime + rewrite all pointers + migrate every assertion behind one seam" unit (merging 002+003 with the literal-reference sweep) that is only ever green or fully reverted; then SPEC-004 (migration/rollback) and SPEC-005 (oracles) as written. Do not deliver a partial centralization.

## Final Closure Report Requirements

Report: implemented units; the asset placement before/after; the slug formula in use; pointer-rewrite coverage across all three host formats; migration/rollback proof; capsule-loss restore proof; release identity; oracle results; whether `npm run commit:check` passed; the host-real canary result per host (or its absence, capping the claim); residual risks; and confirmation that the hook architecture was not altered and no private identifiers entered TES.
