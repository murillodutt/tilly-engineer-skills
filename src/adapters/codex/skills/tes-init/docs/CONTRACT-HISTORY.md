# TES Init Contract History

## Purpose

`/tes-init` installs or recertifies TES in a target project and bootstraps Tier
3 project inventory (`PROJECT-CONTEXT`, initial mesh stubs, cortex scaffold).

## Why This Skill Exists

Projects need a deterministic installer that backs up governance, applies thin
runtime bootloaders, and produces auditable project-start evidence — without
conflating scaffold inventory with operational position.

## Contracts Preserved

- Assisted Context Installer spec is canonical for installer behavior.
- `/tes-update` owns mesh refresh without default re-init.
- `/tes-align` owns Tier 2 semantic alignment after init.
- `PROJECT-CONTEXT.md` is Tier 3 init inventory, not cold-start authority once
  `DOCUMENTATION-AUTHORITY.md` exists or after align.
- Central `.tes/bk/**` backup before bootloader overwrite.
- Project-owned governance recovered into `docs/agents/**`, not duplicated in
  bootloaders.

## Known Failure Modes Prevented

- Treating init scaffold as deep project understanding.
- Skipping backup before bootloader writes.
- Rerunning full Project-Start when postinstall sentinel is already `complete`.
- Using `/tes-init` as a hidden update path (route to `/tes-update`).
- Letting `PROJECT-CONTEXT` compete with Tier 2 mesh after `/tes-align`.

## Relationship To Other Skills

`tes-init` bootstraps. `tes-align` positions. `tes-update` refreshes TES
helpers/adapters. `tes-doctor` certifies health. `tes-context-distill` optional
Phase 2 on inherited root context archives.

## Changelog

| Date | Change | Evidence | Confidence |
|------|--------|----------|------------|
| 2026-05-09 | Created installer skill contract. | Assisted Context Installer spec. | high |
| 2026-06-08 | `PROJECT-CONTEXT` demoted to Tier 3 inventory; handoff to align for Tier 2. | Consumer pilot `DOCUMENTATION-AUTHORITY.md`; documentation authority ADR. | high |

## Do Not Lose

Init produces inventory and mesh stubs. Alignment produces the operating line.
Do not claim operational position without `/tes-align` or existing Tier 2 mesh.
