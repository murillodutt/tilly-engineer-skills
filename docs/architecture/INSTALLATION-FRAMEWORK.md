---
tds_id: architecture.installation_framework
tds_class: architecture
status: active
consumer: maintainers, installer authors, hook authors, MCP authors, and oracle authors
source_of_truth: true
evidence_level: L2
tver: 0.3.170
---

# TES Installation Framework

The internal architecture map of how TES installs into, lives in, updates, and removes itself from a target project. This is the maintainer-facing layer. It exists because the install surface is wide and entangled in ways no single document captured before — a gap that caused the installation-topology Super SPEC to underestimate its own scope on first execution.

## The three documentation layers

| Layer | Audience | Where |
|-------|----------|-------|
| Architecture map (this doc) | Maintainers / installer & hook & MCP authors | `docs/architecture/INSTALLATION-FRAMEWORK.md` |
| Contract / governance | Release reviewers, decision record | `docs/adr/0004-tes-capsule-isolation-and-reversible-installation.md` (invariants, reversibility, capsule isolation) and `docs/adr/0003-1-...` (certification vocabulary) |
| Adopter guide | People installing TES into a project | `docs/install/INSTALL.md`, `docs/install/AGENT-MANUAL.md`, `docs/install/USER-MANUAL.html` |

This doc does not restate the contract (the ADRs own the invariants) or the adopter commands (INSTALL.md owns those). It maps the machinery between them.

## Command surface

Two entrypoints, one engine. The npx `bin/tes.js` is a thin renderer that validates shape and delegates; all install/remove/health logic lives in the Python engine `scripts/tes_install.py`.

| npx (`bin/tes.js`) | engine (`scripts/tes_install.py`) | Effect |
|--------------------|-----------------------------------|--------|
| `add` / `install` | `install` | Materialize the functional default (capsule + skills + bootloaders + mcp + hooks; docs-mesh opt-in). |
| `attach <surface>` | `attach` | Add one project-visible surface to an install. |
| `detach <surface>` | `detach` | Remove one surface; capsule and others stay. |
| `uninstall` | `uninstall` | Restore project, remove TES surfaces, prove zero residue. |
| `doctor` | `doctor` | Read-only capsule + per-surface attachment health. |
| (internal) | `hook` | First-session SessionStart handler (two-phase: announce-start, rewake-on-complete). |
| (internal) | `postinstall` / `status` | First-run materialization sentinel and state. |

The npx command guard is in `bin/tes.js` `parse`/`parseManage`; the engine subparsers and dispatch are in `tes_install.py` `main`.

## Attachment surfaces

`ALL_ATTACH_SURFACES` (`tes_install.py`): `mcp`, `docs-mesh`, `root-context`, `skills`, `hooks`, `field-reports`, `gps`, `goals`, `mantra`. The bundle-side mapping is `attachment_surface_for` (`tes_bundle.py`). Surfaces split into:

- bundle-applied (manifest entries): `root-context` (bootloaders/rules), `skills` (the `/tes-*` command set);
- runtime-writer (produced outside the bundle): `mcp` (`install_mcp.py`), `hooks` (the hook writers in `tes_install.py`), `docs-mesh` (`tes_init.py`);
- still-conceptual (no detach writer yet): `field-reports`, `gps`, `goals`, `mantra` — `detach` returns `NEEDS_REVIEW` for these, by design.

## Runtime writers — there are two

This is the most error-prone part of the framework and the one least obvious from any single file. TES runtime helpers reach the target through **two independent writers** that must agree:

1. `tes_bundle.apply_staged_bundle` — copies HELPER_FILES manifest entries (`.tes/bin/**`) as part of a bundle apply.
2. `install_mcp.install_server_files` — copies its own helper list into `.tes/bin/**` for the MCP attach path, so the MCP server can run even when a full bundle apply did not.

The helper lists behind them (`tes_bundle.HELPER_FILES` and `install_mcp.SERVER_FILES`) must not diverge. A divergence is what broke the MCP server with `ModuleNotFoundError` when a new transitive import was added to one list but not the other. `SERVER_FILES` should derive from `HELPER_FILES`. Any file imported by `tes_bundle` (directly or transitively) must be a HELPER_FILE, because every context that imports `tes_bundle` — including the installed runtime — needs it.

## Asset placement (current topology, 0.3.175)

Today everything lives under `<repo>/.tes/`. The installation-topology Super SPEC (`docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-tes-installation-topology.md`) proposes splitting this into a shared global runtime, a per-project namespace, and a minimal capsule — see that SPEC for the target topology and the resolver `scripts/tes_paths.py` (the only delivered piece of that line so far).

| Path | Holds | Weight (typical) |
|------|-------|------------------|
| `<repo>/.tes/bin/**` | 33 `HELPER_FILES` runtime helpers (plus the `install_mcp_hosts/` package and bytecode cache), identical across installs | ~1.7 MB |
| `<repo>/.tes/setup/**` | bundle staging cache | ~1.8 MB |
| `<repo>/.tes/manifest.json` | detach/uninstall worklist | ~64 KB |
| `<repo>/.tes/tes-install-lock.json` | version, agents, attached surfaces | ~4 KB |
| `<repo>/.tes/postinstall.json` | first-session sentinel (the hook reads this) | ~4 KB |
| `<repo>/.tes/cortex/**` | recall/semantic indexes (per-target, rebuildable) | varies |
| `<repo>/.tes/field-reports/**` | telemetry outbox + install_id | ~8 KB |

## Hooks — per-host, by-path

Each host gets a SessionStart-style hook whose command references the engine entrypoint. The pointer form differs per host:

| Host | Config file | Entrypoint reference |
|------|-------------|----------------------|
| Claude Code | `.claude/settings.json` | `${CLAUDE_PROJECT_DIR}/.tes/bin/tes_install.py` |
| Codex | `.codex/config.toml` | `$(git rev-parse --show-toplevel)/.tes/bin/tes_install.py` |
| Cursor | `.cursor/hooks.json` | `.tes/bin/tes_install.py` (relative) |
| git | active `pre-push` hook (`core.hooksPath` aware) | field-reports pre-push gate |

The hook writers are `install_codex_hook` / the Claude entry builders (`claude_notice_hook_entry`, `claude_setup_hook_entry`) / `install_cursor_hook` in `tes_install.py`. The two-phase contract is fixed (do not alter it):

- `--announce-start` (synchronous): if a `pending` sentinel exists, emit the "setup is running" systemMessage; otherwise stay quiet.
- `--rewake-on-complete` (asyncRewake): run the post-install flow, advance the sentinel to `complete`, announce completion, exit 2 (the rewake signal).

The sentinel `.tes/postinstall.json` is what the hook reads. It is gated on the `hooks` surface being attached (`postinstall_disabled = ... or "hooks" not in surfaces`). Gating it on anything else (it was once gated on `docs-mesh`) leaves the hook firing into an empty state — a real defect shipped in 0.3.167 and fixed in 0.3.175.

## MCP registration

`install_mcp.py` plus `install_mcp_hosts/{codex,claude,cursor,vscode}.py` write the `tes-cortex` server registration into each host's config format. The server entrypoint path is resolved by `target_script` and the server arg is `<entrypoint> --target <repo>`. Config presence is not host connection: the attach-health contract (`attach_health_oracle.py`) drives a real stdio handshake (`initialize` → `tools/list`) to distinguish `PASS` from `PENDING_*` /`HOST_UNOBSERVABLE`. Cortex storage is per-target (`.tes/cortex/recall.sqlite`) and the MCP server refuses a runtime `target` argument — the ADR 0004 inbound isolation invariant.

## Reversibility machine

- `manifest.json` is the worklist: each entry carries `owner`, `layer`, `attachment_surface`, `sha256`, `uninstall_action`, `restore_policy`.
- `detach_surface` (`tes_bundle.py`) removes one surface via the shared per-entry remover (`remove_manifest_entry`): TES:CORE decomposition for bootloaders, sha256-fail-safe for user-modified files, empty-parent pruning so no directory shells remain.
- `uninstall_capsule` runs the same machine across all surfaces, then the `capsule_residue_oracle` proves zero active residue.
- Backups live under `.tes/bk/<id>/` today; the topology SPEC moves durable backup/rollback to a per-project namespace so restore survives capsule loss.

## Certification and oracles

The install surface is protected by a layered oracle set; see `docs/install/AGENT-ORACLE-INVENTORY.md` for the full inventory. The load-bearing ones for the framework:

- `tes_bundle.py --self-test` — build/stage/apply/backup/restore round-trip.
- `tes_install.py --self-test` — thin install, hooks, MCP mapping, sentinel.
- `install_mcp.py --self-test` — helper install + real MCP handshake.
- `install_smoke.py --self-test` — capsule install, reversibility, attach/detach, skills surface, GPS capsule mode probes.
- `attach_health_oracle.py` / `capsule_residue_oracle.py` — per-surface health and zero-residue proof.
- `tes_npx_oracle.py --self-test` / `--release-check` — the bin contract and the published GitHub ref certification.
- `public_pages_oracle.py` — GitHub Pages live serving.

A passing source self-test is not enough when the risk lives in an installed, materialized, or host-real surface; the canary battery in `~/Dev/tes-canaries` exercises real and synthetic target projects, and the host-real canary (open the project in the actual host and observe the hook fire) is the only thing that upgrades a claim from "hooks written correctly to disk and bench-certified" to "hooks converged in real use".

## Known sharp edges (for the next maintainer)

- Two runtime writers, two helper lists — keep them derived from one source.
- The post-install sentinel must be gated on `hooks`, not on any other surface.
- Hook and MCP configs embed a path to the entrypoint; any move of the runtime must rewrite every config/hook pointer and verify it resolves before pruning the old location, or hooks dangle (oracle #5).
- Centralizing the runtime (the topology SPEC) and rewriting the pointers are inseparable — never deliver one without the other.
