---
tds_id: roadmap.goal_super_spec_tes_gps_capsule_mode
tds_class: roadmap
status: proposed
consumer: maintainers, GPS/MAP authors, oracle authors, installer authors, release reviewers, and execution agents
source_of_truth: false
evidence_level: L2
tver: 0.1.0
---

# GOAL Super SPEC: TES GPS Capsule Mode

Status: proposed execution contract derived from ADR 0004 (active). Fourth execution line of capsule-first isolation. Unlike the prior lines, this one is an architectural inversion that REPLACES behavior currently certified by an oracle, so it is run as a migration line with an explicit oracle renegotiation and a coexistence rule — not a patch.

Capability: GPS/MAP runs by default from an internal capsule projection (`.tes/gps/**` / `.tes/context/**`) with no dependency on `docs/agents/**`, and exports the managed `TES-MAP` block to `docs/agents/PROJECT-ROADMAP.md` only when the `docs-mesh` surface is attached.

## Canonical Artifact

Canonical Super SPEC: `docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-tes-gps-capsule-mode.md`

Primary decision source: `docs/adr/0004-tes-capsule-isolation-and-reversible-installation.md` (section `### GPS/MAP`).

Related implementation surfaces:

- `scripts/tes_map.py` (`ROADMAP_REL`, `AGENTS_REL`, `classify_status`, `build_model`, `update_roadmap`, `create_fixture`)
- `scripts/tes_map_oracle.py` (the oracle that certifies current behavior)
- `scripts/capsule_residue_oracle.py` and `scripts/attach_health_oracle.py` (docs-mesh detection)
- `scripts/tes_bundle.py` (`detach_docs_mesh`, capsule layout)
- `scripts/install_smoke.py`

## Mantra Gate Snapshot

| Field | Record |
|-------|--------|
| `VERIFY` | ADR 0004 (active); the shipped 0.3.160/0.3.161/0.3.162 lines; `tes_map.py` anchoring on `docs/agents/PROJECT-ROADMAP.md` and `docs/agents/` with `classify_status` returning NEEDS_CONTEXT/NEEDS_ALIGN when absent and `update_roadmap` writing only on PASS; `tes_map_oracle.py:114-115` explicitly certifying that a missing roadmap returns NEEDS_ALIGN; and `.tes/gps`/`.tes/context` being entirely new construction. All inspected before writing. |
| `SCOPE` | Add this Super SPEC and correlated indexes now (planning-only, version-neutral). The runtime slices it specifies are delivered behavior AND replace an oracle-certified contract, so they carry a patch bump and an explicit oracle renegotiation per ADR 0004 Release Identity and the regression guard. |
| `BEST_PATH` | Build the internal projection first, make GPS read it, then make `docs/agents/**` an export gated on docs-mesh, and renegotiate the oracle to certify both capsule-only and attached modes with a coexistence rule — rather than flipping the anchor in place and breaking the certified contract. |
| `DOCUMENT` | This Super SPEC plus `docs/roadmap/README.md`, `docs/INDEX.md`, `docs/tds/DOCS-INDEX.yml`, and `docs/mesh` GPS/alignment docs only where the contract is operator-visible. |
| `ORACLE` | `python3 scripts/validate_tds.py`, `python3 scripts/validate_doc_size.py`, `python3 scripts/validate_reference_graph.py`, `python3 scripts/private_vocabulary_oracle.py`, `git diff --check` for this planning artifact; the per-unit focused oracles below for each runtime slice. |
| `RESOLVE` | The last-known-good behavior (docs/agents anchor) is preserved as the attached-mode path; capsule mode is added beside it; the oracle change is explicit and additive, not a silent overwrite. |
| `STATUS` | `PROCEED` |

## Governing Matrix

| Layer | Meaning |
|-------|---------|
| ADR 0004 | Default GPS runs from the internal capsule projection; missing `docs/agents/**` is no longer NEEDS_ALIGN in capsule mode; it is required only when docs-mesh is attached. |
| Regression guard | `tes_map_oracle` certifies the current docs/agents-anchored behavior. Replacing it requires naming the baseline, renegotiating the oracle to cover both modes, and a coexistence rule — not deleting the old assertion. |
| Coexistence rule | When both capsule projection and `docs/agents/**` exist, the capsule projection is the source of truth and the managed `TES-MAP` block is a projection of it. Existing populated `docs/agents/**` keeps working through this rule, never via silent overwrite. |
| Capsule layout | Adds `.tes/gps/**` (GPS state) and `.tes/context/**` (read state) as capsule-owned destinations. |
| Non-Change | Does not add Goal Maestro capsule destination, Mantra Gate modes, write-capable MCP, automatic Cortex writes, or remote/publish actions. |

## Current Meaning

`tes_map.py` is fully dependent on `docs/agents/**`: it anchors on `docs/agents/PROJECT-ROADMAP.md`, returns NEEDS_CONTEXT/NEEDS_ALIGN when the directory or roadmap is missing, and writes the managed block only on PASS. `tes_map_oracle.py` certifies exactly this (a missing roadmap MUST return NEEDS_ALIGN). There is no internal projection. So in capsule-only installs (the 0.3.160 default), `/tes-map` cannot produce useful output — it reports NEEDS_ALIGN because the project-visible docs surface is intentionally absent.

This line makes GPS run from capsule state by default and treats `docs/agents/**` as an export surface, with the oracle renegotiated to certify both modes.

## Invariants (must hold after every unit)

- Capsule-mode usefulness: with no `docs/agents/**`, `/tes-map` produces a useful position from `.tes/gps/**` / `.tes/context/**` plus repository scan evidence, not NEEDS_ALIGN.
- Attached-mode parity: when docs-mesh is attached, GPS still exports/updates the managed `TES-MAP` block in `docs/agents/PROJECT-ROADMAP.md` exactly as today.
- Coexistence: when both exist, capsule state is source of truth; the docs block is a projection; the project's own roadmap content is never overwritten.
- No silent regression: the old NEEDS_ALIGN-on-missing assertion is replaced by an explicit two-mode oracle, not deleted; attached-mode behavior is preserved.
- Capsule scope: GPS state writes stay under `.tes/**`; no GPS write touches `docs/agents/**` unless docs-mesh is attached and export is requested.

## Required Fix Matrix

| Fix | Owned Surface | Gap Today | Required Correction | Focused Oracle |
|-----|---------------|-----------|---------------------|----------------|
| Internal GPS projection | `scripts/tes_map.py` | No `.tes/gps`/`.tes/context` exists. | Add a capsule projection writer/reader under `.tes/gps/**` and `.tes/context/**` capturing position, phase, next step, evidence pointers from capsule state plus a repository scan. | `python3 scripts/tes_map.py --self-test`. |
| Mode-aware classify_status | `scripts/tes_map.py` | Missing `docs/agents/**` -> NEEDS_ALIGN always. | Detect docs-mesh attachment. In capsule mode, classify from the projection (PASS with capsule evidence, or a capsule-specific needs state). Only require `docs/agents/**` when docs-mesh is attached. | `python3 scripts/tes_map.py --self-test`. |
| Export gated on docs-mesh | `scripts/tes_map.py` | `update_roadmap` always targets `docs/agents/PROJECT-ROADMAP.md`. | Default `--write` updates the capsule projection. Exporting the managed `TES-MAP` block to `docs/agents/PROJECT-ROADMAP.md` happens only when docs-mesh is attached or an explicit `--export` is passed. | `python3 scripts/tes_map.py --self-test`. |
| Oracle renegotiation | `scripts/tes_map_oracle.py` | Certifies docs/agents-anchored behavior; missing roadmap MUST be NEEDS_ALIGN. | Replace with a two-mode contract: capsule-only fixture asserts useful capsule output and `.tes/gps/**` state without docs export; attached fixture asserts the managed block export and idempotency; coexistence fixture asserts capsule-as-source-of-truth. | `python3 scripts/tes_map_oracle.py --self-test`. |
| Coexistence rule | `scripts/tes_map.py` | No rule for both-present. | When both capsule projection and `docs/agents/**` exist, read position from the capsule and render the docs block as a projection; never overwrite project roadmap content outside the managed markers. | `python3 scripts/tes_map_oracle.py --self-test`. |
| Round-trip coverage | `scripts/install_smoke.py` | No probe for GPS capsule mode. | Add a probe: capsule-only install, run map (assert useful output + `.tes/gps/**`, no docs export), attach docs-mesh, export the block, detach, assert capsule still works. | `python3 scripts/install_smoke.py --self-test`. |

## Execution Discipline

Run units sequentially. Do not implement a later unit before the current unit has its focused oracle green, a release identity classification, and a closure note. Before each unit state owned files, no-touch files, release identity impact, focused oracle, and stop condition.

## SPEC-000: Reentry And Baseline

Owned files: this Super SPEC; no runtime files.

Tasks:

1. `git status --short --branch --untracked-files=all` and `git log -8 --oneline`.
2. Classify dirty changes as inherited, current-task delta, or unrelated.
3. Name the last-known-good baseline: the docs/agents-anchored GPS behavior certified by `tes_map_oracle`, to be preserved as attached mode.
4. Confirm this planning artifact is doc-only and version-neutral.

Focused oracle:

```bash
python3 scripts/validate_tds.py
python3 scripts/private_vocabulary_oracle.py
git diff --check
```

Closure note: SPEC-000 PASS means the baseline is named and the projection is confirmed as new construction beside the certified attached-mode path.

## SPEC-001: Internal GPS Projection

Owned files: `scripts/tes_map.py`.

Implementation:

1. Add a capsule projection under `.tes/gps/**` (GPS state) and `.tes/context/**` (read state) capturing position, current phase, next step, blocking items, unknowns, confidence, and evidence pointers.
2. Build the projection from capsule state (`.tes/postinstall.json`, `.tes/tes-install-lock.json`, manifest) plus a repository scan, with no dependency on `docs/agents/**`.
3. Keep writes capsule-scoped.

Release identity impact: delivered behavior; patch bump decided at SPEC-007.

Focused oracle:

```bash
python3 scripts/tes_map.py --self-test
```

Stop condition: if the projection cannot be built without `docs/agents/**`, the capsule state model is insufficient — stop with NEEDS_REVIEW and define the minimum capsule evidence first.

## SPEC-002: Mode-Aware classify_status

Owned files: `scripts/tes_map.py`.

Implementation:

1. Detect docs-mesh attachment (reuse the residue/attach-health detector).
2. In capsule mode (docs-mesh not attached): classify from the projection — PASS when capsule evidence is sufficient, or a capsule-specific needs state with a clear remediation, never NEEDS_ALIGN-for-missing-docs.
3. In attached mode: keep the existing docs/agents requirement and statuses.

Release identity impact: delivered behavior; patch bump decided at SPEC-007.

Focused oracle:

```bash
python3 scripts/tes_map.py --self-test
```

Stop condition: if a capsule-mode project genuinely cannot be positioned, return an explicit capsule needs state, not a silent PASS.

## SPEC-003: Export Gated On docs-mesh

Owned files: `scripts/tes_map.py`.

Implementation:

1. Default `--write` updates the capsule projection only.
2. Export the managed `TES-MAP` block to `docs/agents/PROJECT-ROADMAP.md` only when docs-mesh is attached, or when an explicit `--export` is passed.
3. Preserve the existing managed-block markers and idempotency for export.

Release identity impact: delivered behavior; patch bump decided at SPEC-007.

Focused oracle:

```bash
python3 scripts/tes_map.py --self-test
```

Stop condition: if export would write `docs/agents/**` in capsule mode without docs-mesh or `--export`, that is a contamination defect — stop and gate it.

## SPEC-004: Oracle Renegotiation

Owned files: `scripts/tes_map_oracle.py`.

Implementation:

1. Replace the single docs/agents-anchored contract with a two-mode contract.
2. Capsule-only fixture: assert useful capsule output and `.tes/gps/**` state with no docs export.
3. Attached fixture: assert the managed block export, idempotency, and unique markers (preserve the current attached-mode assertions).
4. Coexistence fixture: both present -> capsule is source of truth; the docs block is a projection; project roadmap content outside markers is untouched.

Release identity impact: delivered oracle behavior; patch bump decided at SPEC-007.

Focused oracle:

```bash
python3 scripts/tes_map_oracle.py --self-test
```

Stop condition: if the attached-mode assertions cannot be preserved alongside the new capsule assertions, stop — the renegotiation must not drop the last-known-good attached behavior.

## SPEC-005: Coexistence Rule

Owned files: `scripts/tes_map.py`.

Implementation:

1. When both the capsule projection and `docs/agents/**` exist, read position from the capsule and render the docs block as a projection of it.
2. Never overwrite project roadmap content outside the managed `TES-MAP` markers.
3. Report which source was authoritative.

Release identity impact: delivered behavior; patch bump decided at SPEC-007.

Focused oracle:

```bash
python3 scripts/tes_map_oracle.py --self-test
```

Stop condition: if capsule and docs disagree in a way that cannot be reconciled by projection, report NEEDS_REVIEW rather than picking silently.

## SPEC-006: Round-Trip Coverage

Owned files: `scripts/install_smoke.py`.

Implementation:

1. Add a GPS capsule-mode probe: capsule-only install, run map, assert useful output and `.tes/gps/**` state with no docs export.
2. Attach docs-mesh, export the managed block, assert it appears; detach docs-mesh and assert the capsule projection still produces useful output.

Release identity impact: delivered test behavior; participates in the patch release because runtime changed earlier.

Focused oracle:

```bash
python3 scripts/install_smoke.py --self-test
```

Stop condition: if capsule-mode map output is empty or NEEDS_ALIGN with no docs, the inversion is incomplete — stop and fix SPEC-001/002.

## SPEC-007: Release Identity And Closure

Owned files: `package.json`, `bin/tes.js` `TES_VERSION`, script `VERSION` constants, correlated bundle/public surfaces; docs/evidence only if retained.

Tasks:

1. Classify release identity: SPEC-001..006 change delivered GPS behavior and renegotiate an oracle — a patch bump is required unless the owner explicitly defers, per ADR 0004 Release Identity.
2. Run every implemented unit's focused oracle.
3. Run baseline gates and `npm run commit:check`.
4. If a bump is performed, run the bundle/governance checks via the source release flow (do not partial-bump the source package).

Stop condition: if release identity requires a bump and owner authorization for remote actions is unclear, stop with NEEDS_REVIEW and keep the work local.

## Private Vocabulary Guard

No private project names, repository paths, remotes, commit narratives, target product vocabulary, domain decisions, or canary identifiers may enter TES. Use generic forms only: `target project`, `private target canary`, `<absolute-path>`, `<redacted-token>`.

## Evidence Plan

| Evidence | Location | Requirement |
|----------|----------|-------------|
| Unit self-test output | closeout summary or retained report | Commands and PASS/FAIL only. |
| Capsule-mode map proof | retained report | Assert useful output without docs/agents, generically. |
| Oracle renegotiation proof | retained report | Show both capsule-only and attached fixtures pass; attached assertions preserved. |

## Final Closure Report Requirements

The executor must report: implemented SPEC units; files changed; release identity decision; focused oracle results; baseline gate results; whether `npm run commit:check` passed; confirmation that attached-mode (last-known-good) behavior was preserved through the oracle renegotiation; residual risks; deferred work (Goal Maestro capsule destination, Mantra Gate modes); and confirmation that no private target identifiers were added.
