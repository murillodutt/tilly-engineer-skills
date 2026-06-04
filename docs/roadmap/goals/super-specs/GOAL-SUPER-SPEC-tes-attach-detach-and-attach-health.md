---
tds_id: roadmap.goal_super_spec_tes_attach_detach_and_attach_health
tds_class: roadmap
status: proposed
consumer: maintainers, installer authors, MCP authors, hook authors, oracle authors, release reviewers, and execution agents
source_of_truth: false
evidence_level: L2
tver: 0.1.0
---

# GOAL Super SPEC: TES Attach/Detach And Attach-Health

Status: proposed execution contract derived from ADR 0004 (active). This is the
second execution line of capsule-first isolation. It builds directly on the
manifest `@2` attachment_surface field, the surface-filtered apply, the
uninstall machine, and the residue oracle delivered by the capsule install +
uninstall line (`0.3.160`).

Capability: turn project-visible surfaces into individually reversible
attachments with `attach`/`detach` subcommands, and replace shallow MCP/hook
validation with an attach-health contract that never reports a clean `PASS` when
host recognition or hook execution cannot be proven.

## Canonical Artifact

Canonical Super SPEC:
`docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-tes-attach-detach-and-attach-health.md`

Primary decision source:
`docs/adr/0004-tes-capsule-isolation-and-reversible-installation.md`
(sections `### Installer model` and `### Attach-health contract for MCP and hooks`).

Related implementation surfaces:

- `scripts/tes_install.py` (`resolve_attach`, `install`, `uninstall`)
- `scripts/tes_bundle.py` (`apply_staged_bundle` surfaces filter,
  `uninstall_capsule`, manifest `@2`)
- `scripts/install_mcp.py` and `scripts/install_mcp_hosts/**`
- `scripts/cortex_mcp.py` (`--self-test`)
- `scripts/capsule_residue_oracle.py` (per-surface detectors)
- `scripts/install_smoke.py`
- new `scripts/attach_health_oracle.py`

## Mantra Gate Snapshot

| Field | Record |
|-------|--------|
| `VERIFY` | ADR 0004 (active), the shipped `0.3.160` capsule line, manifest `@2` `attachment_surface`/`uninstall_action`, `apply_staged_bundle(surfaces=...)`, `uninstall_capsule`, `capsule_residue_oracle` per-surface detectors, the MCP config-only validation (`install_mcp.py:213-233`, `336-351`), the in-process `cortex_mcp.py --self-test`, the hook writers (`tes_install.py:214-363`) with no execution sentinel, and the absence of `attach`/`detach` subcommands and `PENDING_*`/`HOST_UNOBSERVABLE` states were inspected before writing. |
| `SCOPE` | Add this Super SPEC and correlated indexes now (planning-only, version-neutral). The runtime slices it specifies are delivered behavior and carry a patch bump per ADR 0004 Release Identity. |
| `BEST_PATH` | Reuse the manifest `@2` surface machine and the residue detectors. `attach` reuses surface-filtered apply; `detach` is the inverse of uninstall scoped to one surface; attach-health composes residue detection with a real MCP handshake and a hook execution sentinel. Do not write a parallel removal or validation engine. |
| `DOCUMENT` | This Super SPEC plus `docs/roadmap/README.md`, `docs/INDEX.md`, `docs/tds/DOCS-INDEX.yml`, and `docs/install/AGENT-ORACLE-INVENTORY.md`. |
| `ORACLE` | `python3 scripts/validate_tds.py`, `python3 scripts/validate_doc_size.py`, `python3 scripts/validate_reference_graph.py`, `python3 scripts/private_vocabulary_oracle.py`, `git diff --check` for this planning artifact; the per-unit focused oracles below for each runtime slice. |
| `RESOLVE` | No private target identifiers enter TES. Host-observability limits are encoded as explicit terminal states, not silenced. |
| `STATUS` | `PROCEED` |

## Governing Matrix

| Layer | Meaning |
|-------|---------|
| ADR 0004 | Project-visible surfaces are explicit reversible attachments; MCP/hook attach `PASS` requires proof beyond config presence; `HOST_UNOBSERVABLE` is a terminal partial-success state, not a failure. |
| ADR 0003.1 | Certification vocabulary `PASS`/`PARTIAL`/`NEEDS_REVIEW`/`BLOCKED`; config presence is not host connection. Reused, not redefined. |
| Manifest `@2` | `attachment_surface` and `uninstall_action` per entry drive both attach (apply one surface) and detach (remove one surface). Reused, not extended. |
| Attach-health | New `PENDING_HOST_RESTART` / `PENDING_TRUST` / `PENDING_RELOAD` / `HOST_UNOBSERVABLE` states added on top of the existing vocabulary, with host-specific achievable evidence. |
| Non-Change | Does not add GPS capsule mode, Goal Maestro capsule destination, Mantra Gate mode formalization, write-capable MCP, automatic Cortex writes, or remote/publish actions. Those are later ADR-0004 lines. |

## Current Meaning

Today `--attach` exists only as an install-time flag; there is no way to add or
remove a single surface after install without reinstalling or fully
uninstalling. `detach` does not exist. MCP validation checks config presence and
schema in-process (`install_mcp.py`), and `cortex_mcp.py --self-test` exercises
the server in-process — neither proves the host actually spawned and connected
to the server. Hook writers register handlers idempotently but nothing proves a
hook ever fired. The status vocabulary lacks `PENDING_*` and `HOST_UNOBSERVABLE`,
so a config-present-but-host-silent install can only be reported as `PASS` or
`FAIL`, both wrong.

This line makes each surface independently attachable/detachable and makes
attach health honest about what the host environment can and cannot prove.

## Invariants (must hold after every unit)

- Reversibility preserved: `detach <surface>` removes exactly that surface,
  restoring project-owned content (TES:CORE decomposition for bootloaders),
  and leaves the capsule and other surfaces intact.
- No false green: MCP/hook attach `PASS` requires execution evidence, not config
  presence. When evidence is unreachable, the state is an explicit `PENDING_*`
  or `HOST_UNOBSERVABLE`, never a clean `PASS`.
- `NOT_APPLIED` cannot satisfy a user-selected attachment.
- `HOST_UNOBSERVABLE` is terminal partial success, not failure: TES did all it
  can verify and the rest depends on host action TES cannot observe.
- sha256-fail-safe preserved: detach never deletes a user-modified file without
  recording it `needs-review`.
- Inbound isolation preserved: no attach/detach write resolves outside the
  target; the MCP server still refuses a runtime `target` argument.

## Required Fix Matrix

| Fix | Owned Surface | Gap Today | Required Correction | Focused Oracle |
|-----|---------------|-----------|---------------------|----------------|
| Detach machine | `scripts/tes_bundle.py` | `uninstall_capsule` removes everything; no single-surface removal exists. | Add `detach_surface(target, surface)` reusing `uninstall_action` filtered by `attachment_surface`, with TES:CORE decomposition and sha256-fail-safe, keeping capsule and other surfaces. | `python3 scripts/tes_bundle.py --self-test`. |
| attach/detach subcommands | `scripts/tes_install.py` | `--attach` is install-only; no post-install add/remove. | Add `attach <surface>` (stage-if-needed + surface-filtered apply) and `detach <surface>` (detach machine + residue/attach-health verdict). Require `--yes`, support `--dry-run`. | `python3 scripts/tes_install.py attach --dry-run` / `detach --dry-run` plus oracle. |
| Attach-health states | new `scripts/attach_health_oracle.py` | `PENDING_*` and `HOST_UNOBSERVABLE` do not exist; MCP/hook `PASS` means config-present. | Add the four states and a per-surface health verdict that requires execution evidence for MCP/hooks and falls to an explicit pending/unobservable state otherwise. | `python3 scripts/attach_health_oracle.py --self-test`. |
| MCP out-of-process handshake | `scripts/attach_health_oracle.py`, reuse `cortex_mcp.py` | Self-test is in-process; no proof the host-spawned entrypoint initializes. | Spawn the installed server entrypoint the host would launch and drive a real initialize/capabilities/`tools/list` handshake over stdio; map outcomes to `PASS` / `PENDING_HOST_RESTART` / `HOST_UNOBSERVABLE`. | `python3 scripts/attach_health_oracle.py --self-test` MCP fixtures. |
| Hook execution sentinel | `scripts/tes_install.py` hook writers, `scripts/attach_health_oracle.py` | No proof a hook fired; weak Codex duplicate detection. | Hooks write a sentinel under `.tes/**` on execution; health checks the sentinel for fired/idempotent/single-handler and maps absence to `PENDING_TRUST`/`PENDING_RELOAD`/`HOST_UNOBSERVABLE`. | `python3 scripts/attach_health_oracle.py --self-test` hook fixtures. |
| Per-surface detector coverage | `scripts/capsule_residue_oracle.py` | Detects capsule/bootloader/mcp/hooks; missing docs-mesh/field-reports/gps/goals/mantra. | Extend detectors to all surfaces so attach/detach/residue agree on what each surface owns. | `python3 scripts/capsule_residue_oracle.py --self-test`. |
| attach/detach round-trip | `scripts/install_smoke.py` | No probe proves attach then detach returns to the prior state. | Add a probe: capsule install, attach a surface, assert health, detach it, assert the surface is gone and the capsule plus project files are intact. | `python3 scripts/install_smoke.py --self-test`. |

## Execution Discipline

Run units sequentially. Do not implement a later unit before the current unit
has its focused oracle green, a release identity classification, and a closure
note. Before each unit state owned files, no-touch files, release identity
impact, focused oracle, and stop condition.

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

Closure note: SPEC-000 PASS means a clean boundary and the manifest `@2` surface
machine plus residue detectors are confirmed as the baseline to reuse.

## SPEC-001: Detach Machine

Owned files: `scripts/tes_bundle.py`.

Implementation:

1. Add `detach_surface(target, surface, *, dry_run, yes)` reusing the
   `uninstall_capsule` ordering but scoped to entries whose
   `attachment_surface == surface`.
2. Reuse TES:CORE decomposition for `root-context` and the sha256-fail-safe for
   modified files; never touch capsule paths or other surfaces.
3. Return surface-scoped actions, review items, and a status using the ADR
   0003.1 vocabulary.

Release identity impact: delivered behavior; patch bump decided at SPEC-007.

Focused oracle:

```bash
python3 scripts/tes_bundle.py --self-test
```

Stop condition: if a surface's removal is ambiguous (shared file across
surfaces), stop with `NEEDS_REVIEW` and define ownership before deleting.

## SPEC-002: Attach And Detach Subcommands

Owned files: `scripts/tes_install.py`.

Implementation:

1. Add `attach <surface>`: stage the bundle if not already staged, then
   `apply_staged_bundle(surfaces={surface})`; record the attachment.
2. Add `detach <surface>`: call `detach_surface` and fold the attach-health /
   residue verdict for that surface into the result.
3. Require `--yes`, support `--dry-run`, validate the surface name against the
   known surface set.

Release identity impact: delivered installer behavior; patch bump decided at
SPEC-007.

Focused oracle:

```bash
python3 scripts/tes_install.py attach --dry-run --target <fixture> mcp
python3 scripts/tes_install.py detach --dry-run --target <fixture> mcp
```

Stop condition: if attaching a surface requires another surface to function,
stop with `NEEDS_REVIEW` and declare the dependency, do not auto-attach silently.

## SPEC-003: Attach-Health States And Oracle

Owned files: new `scripts/attach_health_oracle.py`.

Implementation:

1. Add states `PENDING_HOST_RESTART`, `PENDING_TRUST`, `PENDING_RELOAD`,
   `HOST_UNOBSERVABLE` alongside the existing vocabulary.
2. Provide a per-surface `evaluate(target, surface)` that reuses the residue
   detectors for presence and adds execution evidence for `mcp` and `hooks`.
3. `NOT_APPLIED` may not satisfy a user-selected attachment; reflect that in the
   verdict.
4. `--self-test` with fixtures for each terminal state.

Release identity impact: delivered oracle behavior; patch bump decided at
SPEC-007.

Focused oracle:

```bash
python3 scripts/attach_health_oracle.py --self-test
```

Stop condition: if a state cannot be reached deterministically in a fixture,
default to the most conservative state (fail-closed) and record it.

## SPEC-004: MCP Out-Of-Process Handshake

Owned files: `scripts/attach_health_oracle.py`; reuse `scripts/cortex_mcp.py`.

Implementation:

1. Spawn the installed server entrypoint the host would launch and drive a real
   stdio handshake: initialize, capabilities, `tools/list`.
2. Map outcomes: successful handshake -> `PASS`; entrypoint present but no
   response within timeout -> `PENDING_HOST_RESTART`; host environment cannot be
   probed -> `HOST_UNOBSERVABLE`.
3. Keep the existing in-process `cortex_mcp.py --self-test` as server-readiness
   evidence, distinct from host-connection evidence.

Release identity impact: delivered oracle behavior; patch bump decided at
SPEC-007.

Focused oracle:

```bash
python3 scripts/attach_health_oracle.py --self-test
python3 scripts/cortex_mcp.py --self-test
```

Stop condition: if the handshake cannot be made deterministic in CI, encode it
as `HOST_UNOBSERVABLE` rather than a flaky `PASS`.

## SPEC-005: Hook Execution Sentinel

Owned files: `scripts/tes_install.py` hook writers; `scripts/attach_health_oracle.py`.

Implementation:

1. Hooks write a sentinel under `.tes/**` on execution (timestamp, agent, event).
2. Health reads the sentinel: present and single-handler -> `PASS`; config
   written but no sentinel -> `PENDING_TRUST`/`PENDING_RELOAD`; host cannot run
   hooks observably -> `HOST_UNOBSERVABLE`.
3. Strengthen duplicate-handler detection (especially Codex) and assert
   idempotency: a second event does not create a second handler.

Release identity impact: delivered installer + oracle behavior; patch bump
decided at SPEC-007.

Focused oracle:

```bash
python3 scripts/attach_health_oracle.py --self-test
python3 scripts/tes_install.py --self-test
```

Stop condition: if the sentinel write would run outside `.tes/**` or leak
project paths, stop and keep it capsule-scoped.

## SPEC-006: Detector Coverage And Round-Trip

Owned files: `scripts/capsule_residue_oracle.py`, `scripts/install_smoke.py`.

Implementation:

1. Extend residue detectors to all surfaces (docs-mesh, field-reports, gps,
   goals, mantra) so attach/detach/residue agree.
2. Add an attach/detach round-trip probe: capsule install, attach a surface,
   assert attach-health, detach it, assert the surface is gone and the capsule
   plus project-owned files are intact and byte-identical.

Release identity impact: delivered oracle/test behavior; participates in the
patch release because runtime changed earlier.

Focused oracle:

```bash
python3 scripts/capsule_residue_oracle.py --self-test
python3 scripts/install_smoke.py --self-test
```

Stop condition: if a surface has no durable on-disk marker to detect, define one
before claiming detach coverage for it.

## SPEC-007: Release Identity And Closure

Owned files: `package.json`, `bin/tes.js` `TES_VERSION`, script `VERSION`
constants, correlated bundle/public surfaces; docs/evidence only if retained.

Tasks:

1. Classify release identity: SPEC-001..006 change delivered installer, oracle,
   and hook behavior — a patch bump is required unless the owner explicitly
   defers, per ADR 0004 Release Identity.
2. Run every implemented unit's focused oracle.
3. Run baseline gates and `npm run commit:check`.
4. If a bump is performed, run the bundle/governance checks via the source
   release flow (do not partial-bump the source package).

Stop condition: if release identity requires a bump and owner authorization for
remote actions is unclear, stop with `NEEDS_REVIEW` and keep the work local.

## Private Vocabulary Guard

No private project names, repository paths, remotes, commit narratives, target
product vocabulary, domain decisions, or canary identifiers may enter TES. Use
generic forms only: `target project`, `private target canary`, `<absolute-path>`,
`<redacted-token>`.

## Evidence Plan

| Evidence | Location | Requirement |
|----------|----------|-------------|
| Unit self-test output | closeout summary or retained report | Commands and PASS/FAIL only. |
| attach/detach round-trip proof | retained report | Generic; assert surface isolation and byte-identity without target identifiers. |
| Host-observability note | closeout summary | Record which states were reachable in CI and which are `HOST_UNOBSERVABLE` by design. |

## Final Closure Report Requirements

The executor must report: implemented SPEC units; files changed; release
identity decision; focused oracle results; baseline gate results; whether
`npm run commit:check` passed; which attach-health states are CI-reachable vs
`HOST_UNOBSERVABLE`; residual risks; deferred work (GPS capsule mode, Goal
Maestro capsule destination, Mantra Gate modes); and confirmation that no private
target identifiers were added.
