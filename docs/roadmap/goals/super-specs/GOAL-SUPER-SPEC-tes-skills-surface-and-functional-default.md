---
tds_id: roadmap.goal_super_spec_tes_skills_surface_and_functional_default
tds_class: roadmap
status: proposed
consumer: maintainers, installer authors, oracle authors, adapter authors, release reviewers, and execution agents
source_of_truth: false
evidence_level: L2
tver: 0.1.0
---

# GOAL Super SPEC: TES Skills Surface And Functional Default

Status: proposed execution contract derived from ADR 0004 (active). This line
fixes a delivered-behavior defect that contradicts ADR 0004's own capability-
preservation invariant: the default installer materializes no project skills, no
bootloaders, and no `/tes-*` commands, so a fresh `npx ... add` produces a
non-functional TES. This is precisely the "reduced TES" outcome ADR 0004
explicitly rejected (`docs/adr/0004-*.md:277`) and a violation of "capsule mode
must not weaken any TES capability; isolation is an ownership change, not a
feature reduction" (`docs/adr/0004-*.md:205-206`).

Framing principle (binding): TES is a context-and-method platform. The capsule
is the mechanism that lets TES work *without contaminating the host project* and
keeps every write reversible — it is a guarantee, not a reduction. It exists so
the user and the LLM can work in alignment with full TES capability, not so TES
ships a smaller product. Therefore the correct default is a complete, functional
TES whose every project-visible write is capsule-tracked and reversible. A
minimal capsule-only materialization is an explicit opt-in for isolation-
sensitive contexts, never the default.

Capability: make `skills` a first-class, independently attachable surface
(separate from `root-context`), and restore the public default to a fully
functional TES — capsule ownership plus skills plus bootloaders plus mcp plus
hooks — with reversibility and per-surface detach intact.

## Reproduced Defect (evidence, not assumption)

A default-equivalent install was run against a clean temporary target and
verified directly:

```
python3 scripts/tes_install.py install --target <tmp> --agent claude \
  --mode preserve --yes --attach mcp --attach hooks
```

Result: `.claude/skills/` did not exist. All 17 Claude skills were staged inside
the capsule at `.tes/setup/<version>/adapters/claude/.claude/skills/**` but never
materialized to the project. Re-running with `--attach root-context` materialized
all 17 skills. The mechanism works; the surface mapping and default do not.

Root cause: `scripts/tes_bundle.py:attachment_surface_for` maps both
`.agents/skills/**` and `.claude/skills/**` to the `root-context` surface (the
same surface as the `CLAUDE.md`/`AGENTS.md`/`.mdc` bootloaders). The public npx
default attaches only `mcp`+`hooks` (`bin/tes.js:714-715`), so every
`root-context` entry is `skip-not-attached` in `apply_staged_bundle`
(`tes_bundle.py:45-49`) and never reaches disk. The completion notice states
this ("Project-visible bootloaders, skills, and docs mesh were not installed").
The implementation read ADR 0004's ownership change as a materialization
reduction — it conflated "every write is reversible" (correct) with "write
almost nothing by default" (the rejected "reduced TES"). The empty install is
therefore the wrong default, and skills are additionally miscoupled to
bootloaders on one surface.

## Canonical Artifact

Canonical Super SPEC:
`docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-tes-skills-surface-and-functional-default.md`

Primary decision source:
`docs/adr/0004-tes-capsule-isolation-and-reversible-installation.md`
(section `### Installer model`).

Owner decisions binding this line (recorded): the public npx default
materializes capsule + skills + bootloaders; `skills` becomes a first-class
attachment surface separate from `root-context`.

Related implementation surfaces:

- `scripts/tes_bundle.py` (`attachment_surface_for`, `ATTACHMENT_SURFACES`,
  `MANIFEST_BACKED_SURFACES`, `detach_surface`)
- `scripts/tes_install.py` (`ALL_ATTACH_SURFACES`, `resolve_attach`)
- `bin/tes.js` (the forced default attach set and the completion notice)
- `scripts/attach_health_oracle.py`, `scripts/capsule_residue_oracle.py`
- `scripts/install_smoke.py`, `scripts/tes_npx_oracle.py`

## Mantra Gate Snapshot

| Field | Record |
|-------|--------|
| `VERIFY` | The defect was reproduced (see above). `ALL_ATTACH_SURFACES` (`tes_install.py:869`) and `ATTACHMENT_SURFACES` (`tes_bundle.py:469-479`) have no `skills` member. `attachment_surface_for` returns `root-context` for skills (`tes_bundle.py:489-490`). The npx default forces `mcp`+`hooks` (`bin/tes.js:714-715`). `capsule_residue_oracle.py` already treats project-visible skills as active residue (`:298-301`), so the residue model already recognizes skills as a distinct presence. `MANIFEST_BACKED_SURFACES = {"root-context"}` (`tes_bundle.py:1455`). The marketplace artifacts `plugins/**` and root `skills/**` are source-only by contract (`materialize_adapter.py:343-347`) and stay out of scope. |
| `SCOPE` | Add this Super SPEC and correlated indexes now (planning-only, version-neutral). The runtime slices change delivered installer behavior and the public default; they carry a patch bump per ADR 0004 Release Identity. |
| `BEST_PATH` | Add `skills` as a manifest-backed surface so it inherits the existing per-entry removal machine (sha256-fail-safe, surface-filtered apply, detach). Move only the skills path mapping off `root-context`; leave bootloaders on `root-context`. Change the default attach set in one place (`bin/tes.js`) plus the engine help/notice text. Do not write a parallel materialization path. |
| `DOCUMENT` | This Super SPEC plus `docs/roadmap/README.md`, `docs/INDEX.md`, `docs/tds/DOCS-INDEX.yml`, ADR 0004 default note, and `docs/install/AGENT-ORACLE-INVENTORY.md` if oracle coverage changes. |
| `ORACLE` | `python3 scripts/validate_tds.py`, `python3 scripts/validate_doc_size.py`, `python3 scripts/private_vocabulary_oracle.py`, `git diff --check` for this planning artifact; the per-unit focused oracles below for each runtime slice. |
| `RESOLVE` | No private target identifiers enter TES. The default is restored to ADR 0004's capability-preservation invariant; the capsule stays the reversibility guarantee, not a materialization cap. An isolation-only install remains explicitly selectable. |
| `STATUS` | `PROCEED` |

## Governing Matrix

| Layer | Meaning |
|-------|---------|
| ADR 0004 (capability) | "Capsule mode must not weaken any TES capability; isolation is an ownership change, not a feature reduction" (`:205-206`); "reduced TES" is a rejected alternative (`:277`). The empty default violates this. This line restores conformance. |
| Capsule semantics | The capsule is reversible ownership and non-contamination, not a materialization budget. Every project-visible write stays manifest-backed and detachable; that guarantee is what makes a full default safe. |
| Owner decision | Public default = full functional TES (capsule + skills + bootloaders + mcp + hooks). `skills` is a first-class surface separate from `root-context`. A minimal capsule-only install remains available via explicit `--attach capsule` / a no-surface selection. |
| Manifest `@2` | The new `skills` surface is manifest-backed so detach/uninstall reuse the existing per-entry machine; no new removal engine. |
| Coupling fix | Skills move off `root-context`; bootloaders stay on `root-context`. After this line a user can attach skills without bootloaders and vice versa. |
| Non-Change | Does not materialize marketplace artifacts (`plugins/**`, root `skills/**`), change MCP/hook writers, alter GPS/Goal/Mantra surfaces, weaken reversibility, or take remote/publish action. |

## Current Meaning

Today skills are silently coupled to bootloaders under `root-context` and the
public default attaches neither. A fresh `npx ... add` yields a capsule with MCP
config and a startup hook, but no `/tes-*` commands and no engineering-discipline
bootloader — a TES that cannot actually do TES work until the adopter reads the
notice and reruns with `--attach all`. That is the "reduced TES" the ADR
rejected, shipped as the default. This line makes skills their own surface and
restores the default to a complete, functional TES while keeping every write
capsule-reversible.

## Invariants (must hold after every unit)

- Functional default: a fresh public install materializes the skills and
  bootloaders so `/tes-*` commands and the discipline bootloader are present
  without an extra flag.
- Surface separation: attaching `skills` materializes only skills; attaching
  `root-context` materializes only bootloaders/rules. Neither pulls the other.
- Reversibility preserved: `detach skills` removes exactly the skills it wrote,
  sha256-fail-safe for user-modified files, leaving the capsule and other
  surfaces intact; `uninstall` still proves zero active residue including skills.
- Capsule-first preserved: default writes still record every project-visible
  file in the manifest as a reversible attachment; nothing becomes irreversible.
- Marketplace artifacts stay source-only: `plugins/**` and root `skills/**` are
  never materialized into a target.
- Honesty preserved: `--help`, the completion notice, AND ADR 0004 describe
  exactly what the default materializes; no claim diverges from behavior, and the
  decision record is not left contradicting the shipped default.

## Required Fix Matrix

| Fix | Owned Surface | Gap Today | Required Correction | Focused Oracle |
|-----|---------------|-----------|---------------------|----------------|
| Skills surface | `scripts/tes_bundle.py` | `attachment_surface_for` maps skills to `root-context`; `ATTACHMENT_SURFACES` has no `skills`. | Add `skills` to `ATTACHMENT_SURFACES` and `MANIFEST_BACKED_SURFACES`; map `.agents/skills/**` and `.claude/skills/**` to `skills`; keep bootloaders/rules on `root-context`. | `python3 scripts/tes_bundle.py --self-test`. |
| Surface registry | `scripts/tes_install.py` | `ALL_ATTACH_SURFACES` has no `skills`; `resolve_attach` cannot select it. | Add `skills` to `ALL_ATTACH_SURFACES`; ensure `--attach all` and `--attach skills` resolve it. | `python3 scripts/tes_install.py --self-test`. |
| Functional default | `bin/tes.js`, engine help/notice | Default forces `mcp`+`hooks` only; skills/bootloaders excluded — the rejected "reduced TES". | Restore the default to a full functional TES (capsule + skills + bootloaders + mcp + hooks); keep an explicit minimal/isolation install selectable; update `--help` and the completion notice to describe full materialization and how to opt into minimal. | `python3 scripts/tes_npx_oracle.py --self-test`. |
| Detach coverage | `scripts/tes_bundle.py` | `detach_surface` has no `skills` path. | Route `skills` through the manifest-backed per-entry remover; reject ambiguous shared files; keep other surfaces intact. | `python3 scripts/tes_bundle.py --self-test`. |
| Health + residue | `scripts/attach_health_oracle.py`, `scripts/capsule_residue_oracle.py` | No per-surface health for `skills`; residue already detects skills presence but not surface-scoped detach agreement. | Add a `skills` presence/health verdict; ensure residue detectors and detach agree on what `skills` owns. | `python3 scripts/attach_health_oracle.py --self-test`; `python3 scripts/capsule_residue_oracle.py --self-test`. |
| Round-trip coverage | `scripts/install_smoke.py`, `scripts/tes_npx_oracle.py` | No probe asserts default materializes skills, nor a skills-only attach/detach round-trip. | Add probes: default install materializes skills+bootloaders; attach-only-skills materializes skills but not bootloaders; detach skills returns to prior state. | `python3 scripts/install_smoke.py --self-test`; `python3 scripts/tes_npx_oracle.py --self-test`. |
| ADR amendment | `docs/adr/0004-*.md` | Installer model table (`:102`) and Test Plan (`:246-247`) hard-assert `install` = capsule-only, contradicting the new functional default and the SPEC-005 oracles. | Amend the `install` row, the context paragraph (`:41`), and the Test Plan to define a functional default with reversible writes plus an explicit minimal opt-in; leave the ownership/reversibility text untouched. | `python3 scripts/validate_tds.py`; `git diff --check`. |

## Execution Discipline

Run units sequentially. Do not implement a later unit before the current unit
has its focused oracle green, a release identity classification, and a closure
note. Before each unit state owned files, no-touch files, release identity
impact, focused oracle, and stop condition.

## SPEC-000: Reentry And Boundary

Owned files: this Super SPEC; no runtime files.

Tasks:

1. `git status --short --branch --untracked-files=all` and `git log -8 --oneline`.
2. Re-run the reproduction to confirm the defect still holds against HEAD.
3. Confirm no private target evidence enters TES; this artifact is doc-only and
   version-neutral.

Focused oracle:

```bash
python3 scripts/validate_tds.py
python3 scripts/private_vocabulary_oracle.py
git diff --check
```

Stop condition: if the reproduction no longer holds (defect already fixed), stop
and reclassify this line before changing code.

## SPEC-001: Skills As A First-Class Surface

Owned files: `scripts/tes_bundle.py`.

Implementation:

1. Add `"skills"` to `ATTACHMENT_SURFACES` and `MANIFEST_BACKED_SURFACES`.
2. In `attachment_surface_for`, return `"skills"` for `.agents/skills/**` and
   `.claude/skills/**`; remove those prefixes from the `root-context` branch so
   bootloaders/rules remain `root-context`.
3. Keep `.cursor/rules/**` and `context_governance` on `root-context`.

Release identity impact: delivered behavior; patch bump decided at SPEC-007.

Focused oracle:

```bash
python3 scripts/tes_bundle.py --self-test
```

Stop condition: if any non-skill file currently maps to skills paths, stop and
declare ownership before reassigning the surface.

## SPEC-002: Surface Registry And Resolve

Owned files: `scripts/tes_install.py`.

Implementation:

1. Add `"skills"` to `ALL_ATTACH_SURFACES`.
2. Confirm `resolve_attach` selects `skills` for `--attach skills` and `--attach
   all`; capsule-only (no attach) still excludes it at the engine layer.

Release identity impact: delivered behavior; patch bump decided at SPEC-007.

Focused oracle:

```bash
python3 scripts/tes_install.py --self-test
python3 scripts/tes_install.py install --dry-run --target <fixture> --attach skills
```

Stop condition: if `skills` requires another surface to function, declare the
dependency rather than auto-attaching it.

## SPEC-003: Functional Public Default

Owned files: `bin/tes.js`; engine help/notice text.

Implementation:

1. Restore the default so a no-flag public install resolves to a full functional
   TES: capsule + `skills` + `root-context` + `mcp` + `hooks`. Full
   materialization is the default because every write is capsule-reversible; the
   capsule is the guarantee that makes this safe, not a reason to withhold.
2. Provide an explicit minimal/isolation path (e.g. a documented `--attach`
   selection that resolves to capsule-only) for adopters who deliberately want
   non-contaminating isolation over full materialization.
3. Update `printHelp()` ("Defaults to ...") and the `skip-capsule-only`
   completion notice: the default now describes full materialization and points
   to the opt-in minimal path.

Release identity impact: delivered adopter-visible default change (restores ADR
conformance); patch bump decided at SPEC-007.

Focused oracle:

```bash
python3 scripts/tes_npx_oracle.py --self-test
```

Stop condition: if changing the default would make `uninstall` non-reversible for
any newly defaulted surface, stop and confirm detach coverage first (SPEC-004).

## SPEC-004: Detach And Reversibility For Skills

Owned files: `scripts/tes_bundle.py`.

Implementation:

1. Route `skills` through the manifest-backed per-entry remover in
   `detach_surface`, reusing sha256-fail-safe and project-content safety.
2. Ensure `uninstall_capsule` removes skills via the same machine and the residue
   proof covers them.

Release identity impact: delivered behavior; patch bump decided at SPEC-007.

Focused oracle:

```bash
python3 scripts/tes_bundle.py --self-test
python3 scripts/capsule_residue_oracle.py --self-test
```

Stop condition: if a skill file is user-modified, preserve and report
`needs-review`; never delete it on detach/uninstall.

## SPEC-005: Health, Residue, And Round-Trip Coverage

Owned files: `scripts/attach_health_oracle.py`,
`scripts/capsule_residue_oracle.py`, `scripts/install_smoke.py`,
`scripts/tes_npx_oracle.py`.

Implementation:

1. Add a `skills` per-surface health verdict and ensure residue detectors and
   detach agree on skills ownership.
2. Add probes: default install materializes skills + bootloaders; attach-only-
   skills materializes skills but NOT bootloaders (proves decoupling); detach
   skills returns to the prior state with the capsule intact.

Release identity impact: delivered oracle/test behavior; participates in the
patch release.

Focused oracle:

```bash
python3 scripts/attach_health_oracle.py --self-test
python3 scripts/capsule_residue_oracle.py --self-test
python3 scripts/install_smoke.py --self-test
python3 scripts/tes_npx_oracle.py --self-test
```

Stop condition: if the decoupling probe shows bootloaders appearing on a
skills-only attach, fix the surface mapping before claiming separation.

## SPEC-006: ADR 0004 Amendment

Owned files:
`docs/adr/0004-tes-capsule-isolation-and-reversible-installation.md`.

Rationale: ADR 0004 conflates two distinct ideas — reversible *ownership* (every
project-visible write is manifest-backed and detachable) and the materialization
*default* (what appears in the project). The capability-preservation invariant
(`:88`, `:93`, `:205-206`, `:277`) says the default must not be a "reduced TES",
but the Installer model table (`:102`) and the Test Plan (`:246-247`) hard-assert
`install` = capsule-only with "no root files, no MCP configs, no hooks". After
SPEC-001..005, `tes_npx_oracle` and `install_smoke` assert a functional default;
those would directly contradict the ADR's own table and test plan. The ADR is
the cited decision source for both this line and the sibling npx-parity line, so
it must be amended in the same cut, not left contradictory.

Implementation (amend exactly these points; do not touch the ownership text at
`:15`, `:50`, `:58`, `:88`, `:93`, which is correct):

1. Installer model table row `install` (`:102`): redefine `install` as
   materializing a full functional TES by default (capsule ownership + skills +
   bootloaders + mcp + hooks), with every write manifest-backed and reversible;
   record a minimal/isolation install as an explicit opt-in, not the default.
2. Context paragraph (`:41`): clarify that the defect being corrected was
   *irreversible* project-visible writes, not project-visible writes as such;
   capsule-first fixes reversibility and ownership, it does not mandate an empty
   default.
3. Test Plan "Fresh target" (`:246-247`): replace the "assert no root files, no
   MCP configs, no hooks" capsule-only assertion with two assertions — a default
   install materializes a functional TES (skills, bootloaders, mcp, hooks) and
   every write is manifest-backed/reversible; AND an explicit minimal/isolation
   install materializes capsule-only. Keep the reversibility assertion intact.
4. Add a short `### Materialization default` note (or amend `### Installer model`)
   stating the binding framing: the capsule is reversibility and non-
   contamination, not a materialization cap; the default is full capability.
5. Bump the ADR `tver` and keep `status: active`; record the amendment date and a
   one-line lineage note so the change is auditable.

Release identity impact: the ADR amendment itself is doc-only, but it ratifies
the delivered default change in SPEC-003; classify with the bump at SPEC-007.

Focused oracle:

```bash
python3 scripts/validate_tds.py
python3 scripts/validate_doc_size.py
git diff --check
```

Stop condition: if amending the ADR would contradict a still-true invariant
(inbound isolation, reversibility, no-false-green), stop and reconcile the
invariant text before changing the table; never weaken reversibility to justify
the default.

## SPEC-007: Release Identity And Closure

Owned files: `package.json`, `bin/tes.js` `TES_VERSION`, script `VERSION`
constants, correlated bundle/public surfaces; docs/evidence only if retained.

Tasks:

1. Classify release identity: SPEC-001..006 change the delivered installer
   surface set and the public default — a patch bump is required unless the owner
   explicitly defers, per ADR 0004 Release Identity. Check `package.json`,
   `bin/` `TES_VERSION`, script `VERSION` constants, plugin manifests,
   `docs/dist/<version>/**`, `.sha256` sidecars, `index.json`, public docs, and
   the maintainer correlation rule.
2. Run every implemented unit's focused oracle and `npm run commit:check`.
3. If a bump is performed, run the bundle/governance checks via the source
   release flow (do not partial-bump the source package).
4. Validate on a real project canary that a fresh default install yields working
   `/tes-*` commands, per `<learning_and_boundaries>`.

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
| Defect reproduction | closeout summary | Generic target; show default install yields no skills before the fix. |
| Decoupling proof | retained report | attach-only-skills materializes skills but not bootloaders. |
| Round-trip proof | retained report | default install -> uninstall returns to clean state with skills removed. |
| Canary proof | closeout summary | A fresh default install exposes working `/tes-*` commands. |

## Final Closure Report Requirements

The executor must report: implemented SPEC units; files changed; the surface map
before/after (which paths moved from `root-context` to `skills`); the new default
attach set; release identity decision; focused oracle results; baseline gate
results; whether `npm run commit:check` passed; canary result; residual risks;
and confirmation that no marketplace artifacts were materialized and no private
target identifiers were added.
