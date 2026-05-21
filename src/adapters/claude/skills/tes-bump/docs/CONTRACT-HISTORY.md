# TES Bump Contract History

## Purpose

`tes-bump` is the version governance guard for deciding, planning, and applying
bounded project version bumps inside TES-managed targets.

## Why This Skill Exists

Version bumps are small but fragile: agents can skip the source of truth,
forget plugin manifests, invent changelog behavior, or update broad files by
string replacement. They can also reach commit or release closure after
delivered behavior changed without making a version decision. The <project-B> bump
skill had useful operational logic, but its release-note and changelog behavior
is <project-B>-owned. TES needs the portable version-sync contract and a commit/release
governance guard without importing <project-B> product assumptions.

## Origin Signals

| Source | Signal | Confidence |
|--------|--------|------------|
| `/Users/murillo/Dev/<project-b>-private/<project-b>-plugin/<project-b>/skills/bump/SKILL.md` | Mature bump workflow with source detection, SemVer calculation, target discovery, config safety, ordered writes, and validation. | high |
| Murillo directive, 2026-05-21 | Create a TES version of the skill as a migration, not a port; use only the logic inside TES standards. | high |
| Murillo directive, 2026-05-21 | `tes-bump` must auto-activate for commit or bump-triggering conditions and govern correct version bumps. | high |
| `docs/governance/MAINTAINER-CORRELATION-RULE.md` | Delivered adapter behavior must check command routing, adapter source, helper delivery, and release identity. | high |

## Source Search Ledger

| Window | Query | Occurrences | Meaning |
|--------|-------|-------------|---------|
| 2026-05-21 | `bump/SKILL.md` source read | one <project-B> source skill | Logic source identified; product-specific <project-B> behavior excluded. |
| 2026-05-21 | `tes-prospect`, `tes-mine`, `tes-bench` | existing adapter skills and command routes | TES skill shape, agents metadata, contract history, and router surfaces identified. |

## Contracts Preserved

- Activate for explicit version bump intent and as a governance guard when
  commit, release, or delivered behavior creates a version-decision condition.
- Read the current source version before computing the next version.
- Run a read-only governance check before inferred commit/release bump
  conditions write anything.
- Use strict SemVer: patch, minor, major, exact release, and prerelease.
- Discover bounded targets instead of broad string replacing.
- Write the source of truth first and stop if that write fails.
- Support custom targets only through safe relative paths.
- Validate updated targets before reporting success.
- Report old version, new version, updated targets, failures, and Git next
  steps.
- Never commit, tag, push, publish, or mutate remotes from the bump skill.
- Stop closure on `NEEDS_VERSION_DECISION` or `NEEDS_REVIEW`.

## Known Failure Modes Prevented

- Bumping package manifests while leaving `VERSION` stale.
- Treating every version-looking string as a target.
- Accepting absolute or parent-traversal config paths.
- Updating marketplace manifests with lossy replace-all behavior.
- Importing <project-B> changelog MCP, Oracle, or spec behavior into TES.
- Claiming TES package release readiness without release identity gates.
- Partially bumping the TES package source while leaving release identity
  surfaces stale.
- Treating version governance as optional during commit or release closure.

## Relationship To Other Skills

`tes-bump` is narrower than `tes-update` and `tes-doctor`: it changes version
surfaces only. `tes-doctor` owns health and commit readiness. TES package
release closure remains governed by maintainer correlation, public bundle
oracles, and `npm run commit:check`.

## Changelog

| Date | Change | Evidence | Confidence |
|------|--------|----------|------------|
| 2026-05-21 | Created `tes-bump` as a TES migration of portable <project-B> bump logic, excluding <project-B>-specific changelog and Oracle behavior. | Murillo directive; <project-B> bump source read; `scripts/tes_bump.py --self-test`. | high |
| 2026-05-21 | Added a package-source guard so the generic helper cannot partially bump `tilly-engineer-skills` without explicit TES bump config. | `python3 scripts/tes_bump.py --target . --dry-run patch` exposed only `package.json` in package source. | high |
| 2026-05-21 | Changed contract to auto-activate as version governance for commit/release/bump conditions, adding `--governance-check` and stop statuses. | Murillo correction in chat; `python3 scripts/tes_bump.py --self-test`. | high |

## Do Not Lose

This is a version governance skill, not a general implementation utility.
Preserve the governance-check-first, dry-run-first, bounded-target,
source-first, self-validating shape. Do not allow <project-B>-specific release notes,
MCP submission, Oracle ports, or spec classification to become TES default
behavior. Do not let the helper perform a partial TES package release bump.
