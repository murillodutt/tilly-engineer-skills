---
tds_id: roadmap.goal_super_spec_tes_capsule_install_and_uninstall
tds_class: roadmap
status: proposed
consumer: maintainers, installer authors, manifest authors, release reviewers, and execution agents
source_of_truth: false
evidence_level: L2
tver: 0.1.0
---

# GOAL Super SPEC: TES Capsule Install And Uninstall

Status: proposed execution contract derived from ADR 0004. This is the first and foundational line of capsule-first isolation: capsule-only install plus a reversible uninstall that proves zero active residue. Attach/detach, attach-health for MCP/hooks, and GPS capsule mode are later lines that depend on the manifest and reversibility primitives this line delivers.

Capability: a default `install` that writes only `.tes/**`, and an `uninstall` that restores project-owned files, removes TES-owned surfaces, removes the capsule, and proves no active TES residue remains.

## Canonical Artifact

Canonical Super SPEC: `docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-tes-capsule-install-and-uninstall.md`

Primary decision source: `docs/adr/0004-tes-capsule-isolation-and-reversible-installation.md`

Related implementation surfaces:

- `scripts/tes_install.py`
- `scripts/tes_init.py`
- `scripts/tes_bundle.py`
- `scripts/install_adapter.py`
- `scripts/install_mcp.py`
- `bin/` (npx/Bun entrypoint)
- `scripts/install_smoke.py`
- new `scripts/capsule_residue_oracle.py`

## Mantra Gate Snapshot

| Field | Record |
|-------|--------|
| `VERIFY` | ADR 0004, ADR 0003.1 certification vocabulary, the existing manifest `tes-bundle-manifest@1` (`scripts/tes_bundle.py`), `clean_backup`/`restore_backup`/`cleanup_obsolete_runtime`, the install-all defaults in `tes_install.py`/`tes_init.py`/`install_adapter.py`/`install_mcp.py`, and the absence of any `uninstall`/`attach`/`detach` command were inspected before writing. |
| `SCOPE` | Add this Super SPEC and correlated indexes now (planning-only, version-neutral). The runtime slices it specifies are delivered behavior and carry the release bump per ADR 0004 Release Identity. |
| `BEST_PATH` | Compose the existing backup/restore/cleanup primitives into capsule install + uninstall and add a residue proof, rather than write a new removal engine. Extend the manifest in place to `@2` instead of a parallel manifest. |
| `DOCUMENT` | This Super SPEC plus `docs/roadmap/README.md`, `docs/INDEX.md`, and `docs/tds/DOCS-INDEX.yml`. |
| `ORACLE` | `python3 scripts/validate_tds.py`, `python3 scripts/validate_doc_size.py`, `python3 scripts/validate_reference_graph.py`, `python3 scripts/private_vocabulary_oracle.py`, and `git diff --check` for this planning artifact; the per-unit focused oracles below for each runtime slice. |
| `RESOLVE` | No private target identifiers enter TES. Reversibility is proven on neutral fixtures and a private canary replay kept off-repo. |
| `STATUS` | `PROCEED` |

## Governing Matrix

| Layer | Meaning |
|-------|---------|
| ADR 0004 | Capsule (`.tes/**`) is runtime ownership authority; project-visible writes are explicit reversible attachments; uninstall proves zero active residue. |
| ADR 0003.1 | Certification vocabulary `PASS`/`PARTIAL`/`NEEDS_REVIEW`/`BLOCKED`; `INSTALLED` is an operation status, not a verdict. Reused, not redefined. |
| Manifest | `tes-bundle-manifest@1` extended to `@2` with `attachment_surface`, `restore_policy`, `uninstall_action`. Every write is owner/layer/checksum tagged and reversible. |
| Reversibility primitives | `clean_backup`, `restore_backup`, `cleanup_obsolete_runtime` already exist and are sha256-fail-safe; this line composes them, it does not replace them. |
| Non-Change | Does not add attach/detach surfaces, attach-health oracles, GPS capsule mode, write-capable MCP, automatic Cortex writes, remotes, tags, or publishing. Those are later ADR-0004 lines. |

## Current Meaning

Today a default install writes four project-visible surfaces (root bootloaders, host hooks, MCP configs, `docs/agents/**`) and there is no uninstall. The closest removal mechanism, `cleanup_obsolete_runtime` in `scripts/tes_bundle.py`, only removes paths that left a manifest between versions and preserves any file whose sha256 no longer matches the manifest (it records `preserve-obsolete-runtime-needs-review`). That sha256-fail-safe is the last-known-good safety behavior this line must preserve: uninstall must never remove a file the user edited.

This line delivers the missing direction — a clean entry that writes only the capsule, and a clean exit that restores and proves.

## Invariants (must hold after every unit)

- Inbound isolation preserved: no capsule write resolves outside the target; the MCP server still refuses a runtime `target` argument.
- sha256-fail-safe preserved: uninstall never deletes a project-owned or TES-owned file whose checksum diverges from the manifest without recording it as `needs-review` and preserving it.
- No false green: `INSTALLED` is not certification; uninstall `PASS` requires the residue oracle to pass, not just that removal ran.
- Reversibility: a target that received capsule-only install returns, after uninstall, to a state where project-owned files are byte-identical to pre-install and no active TES surface remains.

## Required Fix Matrix

| Fix | Owned Surface | Failure Mode Today | Required Correction | Focused Oracle |
|-----|---------------|--------------------|---------------------|----------------|
| Manifest reversibility fields | `scripts/tes_bundle.py` | Manifest `@1` lacks `attachment_surface`, `restore_policy`, `uninstall_action`, so detach/uninstall cannot be deterministic. | Add the three fields, bump schema to `tes-bundle-manifest@2`, keep `@1` readable for migration. | `python3 scripts/tes_bundle.py --self-test`. |
| Capsule-only install default | `scripts/tes_install.py`, `scripts/tes_init.py` | Default install writes root/hooks/MCP/`docs/agents/**`. | Default `install` writes only `.tes/**`; project-visible writes occur only behind an explicit attach profile (delivered in a later line; here they are simply off by default). | `python3 scripts/install_smoke.py` fresh-target capsule assertion. |
| Uninstall command | `scripts/tes_install.py`, `scripts/tes_bundle.py` | No uninstall exists. | Add `uninstall`: snapshot, restore project-owned files via `restore_backup`, remove tes-owned surfaces via the manifest `uninstall_action`, remove the capsule, then run the residue oracle. Fail-closed and require `--yes`. | `python3 scripts/tes_install.py uninstall --dry-run` plus residue oracle. |
| Zero-residue proof | new `scripts/capsule_residue_oracle.py` | No proof that uninstall left zero active residue. | New oracle scans the target for any active TES surface (`.tes/**`, root bootloader TES blocks, hook entries, MCP `tes-cortex` config) and returns `PASS` only when none remain or only user-retained exports remain, reported explicitly. | `python3 scripts/capsule_residue_oracle.py --self-test`. |
| Reversibility round-trip | `scripts/install_smoke.py` | No test proves install→uninstall returns to pre-install state. | Add an install→uninstall round-trip fixture asserting byte-identity of project-owned files and zero active residue. | `python3 scripts/install_smoke.py`. |

## Execution Discipline

Run units sequentially. Do not implement a later unit before the current unit has its focused oracle green, a release identity classification, and a closure note. Before each unit state owned files, no-touch files, release identity impact, focused oracle, and stop condition.

## SPEC-000: Reentry And Boundary

Owned files: this Super SPEC; no runtime files.

Tasks:

1. `git status --short --branch --untracked-files=all` and `git log -8 --oneline`.
2. Classify dirty changes as inherited, current-task delta, or unrelated.
3. Confirm no private target evidence will enter TES.
4. Confirm this planning artifact is doc-only and version-neutral.

Focused oracle:

```bash
python3 scripts/validate_tds.py
python3 scripts/private_vocabulary_oracle.py
git diff --check
```

Closure note: SPEC-000 PASS means a clean boundary and the manifest/backup primitives are confirmed as the last-known-good baseline to compose.

## SPEC-001: Manifest Reversibility Fields

Owned files: `scripts/tes_bundle.py`; docs only if the manifest contract is operator-visible.

Implementation:

1. Add `attachment_surface` (`capsule` for `.tes/**`; the eight attach surfaces for project-visible writes), `restore_policy`, and `uninstall_action` to `BundleEntry` and `manifest_payload`.
2. Bump manifest schema to `tes-bundle-manifest@2`; keep an `@1` reader so existing installed manifests migrate forward, not break.
3. Default `attachment_surface=capsule`, `uninstall_action=remove`, `restore_policy=restore-from-backup` for tes-owned capsule paths; preserve the existing `owner`/`layer`/`obsolete_policy` semantics unchanged.
4. Update `validate_manifest` for the new required fields.

Release identity impact: delivered manifest behavior; patch bump decided at SPEC-006.

Focused oracle:

```bash
python3 scripts/tes_bundle.py --self-test
```

Stop condition: if any existing layer needs a non-`remove` uninstall action that is not yet defined, stop with `NEEDS_REVIEW` rather than guessing.

## SPEC-002: Capsule-Only Install (explicit --attach capsule)

> **Superseded default (reconciled with the ADR 0004 amendment, 2026-06-05).** This SPEC originally made capsule-only the *documented default*. The skills-surface line (0.3.167) amended ADR 0004 so the public `install` default now materializes a full functional TES — capsule + skills + root-context + mcp + hooks, with only `docs-mesh` opt-in. Capsule-only is now the **explicit `--attach capsule` mode**, not the default. The capsule-only-default framing below is retained as execution-line history; it is no longer the current contract. The live default is owned by `docs/architecture/INSTALLATION-FRAMEWORK.md` and `docs/install/INSTALL.md`.

Owned files: `scripts/tes_install.py`, `scripts/tes_init.py`; `bin/` only for flag parsing.

Implementation:

1. Make default `install` write only `.tes/**`: capsule state, helpers, manifest, lock, postinstall record.
2. Gate every project-visible write (root bootloaders, hooks, MCP configs, `docs/agents/**`) behind explicit selection that defaults off. In this line the gate is simply "off unless explicitly requested"; the named attach profiles arrive in a later line.
3. Preserve existing flags as compatibility shims where a maintainer relies on them. (Reconciled: capsule-only is the explicit `--attach capsule` opt-in, not the documented public default — see the amendment note above and ADR 0004 amendment 2026-06-05.)

Release identity impact: delivered installer behavior; adopter-visible; patch bump decided at SPEC-006.

Focused oracle:

```bash
python3 scripts/install_smoke.py
```

Stop condition: if any capsule capability silently requires a project-visible write to function, that is a capability-preservation defect — stop with `NEEDS_REVIEW` and route it through the attach design, not a hidden write.

## SPEC-003: Uninstall Command

Owned files: `scripts/tes_install.py`, `scripts/tes_bundle.py`.

Implementation:

1. Add the `uninstall` subcommand. It must require `--yes` and support `--dry-run`, mirroring `restore_backup`.
2. Order: snapshot current state; restore project-owned files via `restore_backup` using the recorded `restore_policy`; remove tes-owned surfaces by manifest `uninstall_action`; remove the capsule directory last.
3. Inherit the sha256-fail-safe from `cleanup_obsolete_runtime`: any file whose checksum diverges from the manifest is preserved and reported as `needs-review`, never silently deleted.
4. Run `capsule_residue_oracle` at the end and fold its verdict into the uninstall status using the ADR 0003.1 vocabulary (`PASS`/`PARTIAL`/`NEEDS_REVIEW`/`BLOCKED`).

Release identity impact: delivered installer behavior; patch bump decided at SPEC-006.

Focused oracle:

```bash
python3 scripts/tes_install.py uninstall --dry-run --target <fixture>
python3 scripts/capsule_residue_oracle.py --self-test
```

Stop condition: if restore would overwrite a user-modified file (checksum mismatch on a project-owned path), stop and report `NEEDS_REVIEW` with the divergent paths; do not force.

## SPEC-004: Zero-Residue Oracle

Owned files: new `scripts/capsule_residue_oracle.py`.

Implementation:

1. Scan the target for active TES surfaces: `.tes/**`, TES-managed blocks in root bootloaders, hook entries pointing at TES, and MCP `tes-cortex` config entries.
2. Return `PASS` only when no active surface remains, or only when surfaces the user explicitly chose to retain (exports) remain and are reported by name.
3. Distinguish active residue (a live route or capsule state) from inert user-retained exports. Inert retained exports do not fail; unexplained active residue does.
4. Provide `--self-test` with fixtures: clean target (PASS), target with leftover `.tes/**` (FAIL), target with a stale hook entry (FAIL), target with a user-retained export only (PASS with reported retention).

Release identity impact: delivered oracle behavior; patch bump decided at SPEC-006.

Focused oracle:

```bash
python3 scripts/capsule_residue_oracle.py --self-test
```

Stop condition: if "active" vs "inert retained" cannot be classified for a surface, default that surface to active (fail-closed) and record it for review.

## SPEC-005: Reversibility Round-Trip

Owned files: `scripts/install_smoke.py`.

Implementation:

1. Add a fixture that performs capsule-only install then uninstall.
2. Assert project-owned files are byte-identical to the pre-install snapshot.
3. Assert `capsule_residue_oracle` returns `PASS` with no active residue.
4. Assert the inbound isolation guard still holds: no write resolved outside the target and the MCP server still refuses a runtime `target` argument.

Release identity impact: delivered test/smoke behavior; participates in the patch release because runtime changed earlier.

Focused oracle:

```bash
python3 scripts/install_smoke.py
```

Stop condition: if byte-identity fails for any project-owned file, the line is not reversible — stop with `NEEDS_REVIEW` and fix the offending write/restore.

## SPEC-006: Release Identity And Closure

Owned files: `package.json`, `bin/` `TES_VERSION`, script `VERSION` constants, correlated bundle/public surfaces only if delivered behavior changed; docs/evidence only if retained proof is created.

Tasks:

1. Classify release identity: SPEC-001..005 change delivered installer, manifest, and oracle behavior — a patch bump from `0.3.159` is required unless the owner explicitly defers, per ADR 0004 Release Identity.
2. Run every implemented unit's focused oracle.
3. Run baseline gates:

```bash
python3 scripts/validate_tds.py
python3 scripts/validate_doc_size.py
python3 scripts/validate_reference_graph.py
python3 scripts/private_vocabulary_oracle.py
git diff --check
```

4. Before any sealed claim: `npm run commit:check`.
5. If a bump is performed:

```bash
python3 scripts/tes_bump.py --governance-check --json
python3 scripts/build_public_docs.py --check
python3 scripts/public_bundle_oracle.py
```

Stop condition: if release identity requires a bump and owner authorization is unclear, stop with `NEEDS_REVIEW` rather than bumping or publishing.

## Private Vocabulary Guard

No private project names, repository paths, remotes, commit narratives, target product vocabulary, domain decisions, or canary identifiers may enter TES. Use generic forms only: `private target canary`, `target project`, `source-of-record kept outside TES`, `<project-A>`, `<absolute-path>`, `<redacted-token>`.

## Evidence Plan

| Evidence | Location | Requirement |
|----------|----------|-------------|
| Unit self-test output | closeout summary or retained report | Commands and PASS/FAIL only. |
| Round-trip reversibility proof | retained report | Generic; assert byte-identity and zero active residue without target identifiers. |
| Private canary replay | private source-of-record, not TES | Mention only that a canary replay was used. |

## Final Closure Report Requirements

The executor must report: implemented SPEC units; files changed; release identity decision; focused oracle results; baseline gate results; whether `npm run commit:check` passed; residual risks; deferred work (attach/detach, attach-health, GPS capsule mode); and confirmation that no private target identifiers were added.
