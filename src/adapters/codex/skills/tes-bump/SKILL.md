---
name: tes-bump
description: Use when the user invokes tes-bump, /tes-bump, /tes:bump, $tes-bump, asks to bump/sync a project version, prepares a commit or release that may require a version decision, or any workflow/tool says a bump is needed. Acts as the governance guard for correct version bumps.
license: MIT
---

# TES Bump

Operational contract: `tes.bump@0.1.1`.

`tes-bump` carries the portable version-sync logic for TES-managed targets.
It is the version governance guard for source detection, SemVer computation,
bounded target discovery, ordered writes, and dry-run planning.

## Activation Contract

Activate when any of these are true:

- The user names `tes-bump`, `/tes-bump`, `/tes:bump`, `tes bump`, or
  `$tes-bump`.
- The user directly asks to bump, sync, change, or check a project version.
- A commit, release, package, installer, adapter, plugin, public-doc, MCP,
  Cortex, Field Reports, helper, or delivered-behavior change may require a
  version decision.
- Another TES workflow, oracle, review, commit gate, release gate, or package
  check reports that a bump is required, missing, partial, stale, or unsafe.

Do not auto-write a bump. Auto-activation first runs the governance check and
classifies whether a version decision is required. Writing still needs explicit
authorization from the user or the caller's release workflow.

Casual mentions of release, version, package metadata, or changelog activate
only the read-only governance guard when a state-changing action, commit,
release, or version-sensitive workflow is in flight.

## Workflow

1. Classify the workspace:
   - Installed target: `.tes/bin/tes_bump.py` exists.
   - Package source or canary: `scripts/tes_bump.py` exists.
   - Otherwise report `BLOCKED` and do not rewrite version files manually.
2. Detect source of truth before computing anything:
   - `VERSION` at project root wins.
   - Otherwise use root `package.json#version`.
   - If neither exists, report `BLOCKED`.
3. If activation came from commit, release, or an inferred bump condition, run
   the read-only governance check first:
   - Installed target:
     `python3 .tes/bin/tes_bump.py --target . --governance-check`
   - Package source or canary:
     `python3 scripts/tes_bump.py --target <target> --governance-check`
4. Interpret governance status:
   - `PASS`: no bump is required, or version surfaces are synchronized.
   - `NEEDS_VERSION_DECISION`: delivered behavior changed and no synchronized
     bump was detected; stop commit/release closure until the decision is made.
   - `NEEDS_REVIEW`: version surfaces changed but are out of sync; repair
     before closure.
5. For an actual bump, run a dry plan first:
   - Installed target:
     `python3 .tes/bin/tes_bump.py --target . --dry-run <patch|minor|major|x.y.z>`
   - Package source or canary:
     `python3 scripts/tes_bump.py --target <target> --dry-run <patch|minor|major|x.y.z>`
6. Review the target list. Proceed only when every target is expected and
   version-specific.
7. Apply with explicit write confirmation from the user or from the caller's
   release workflow:
   - Installed target:
     `python3 .tes/bin/tes_bump.py --target . --yes <patch|minor|major|x.y.z>`
   - Package source or canary:
     `python3 scripts/tes_bump.py --target <target> --yes <patch|minor|major|x.y.z>`
8. After writing, require the helper self-validation result. If any target
   fails, report `NEEDS_REVIEW` with the failed path and do not claim release
   readiness.

## Version Rules

| Argument | Result |
|----------|--------|
| omitted or `patch` | Increment patch and drop prerelease suffix. |
| `minor` | Increment minor and reset patch to `0`. |
| `major` | Increment major and reset minor and patch to `0`. |
| `x.y.z` | Set exact SemVer. |
| `x.y.z-tag` | Set exact prerelease SemVer. |

Reject non-SemVer input. Never guess a version format.

## Target Discovery

The helper discovers only bounded version surfaces:

- Root `VERSION` when present.
- Root `package.json`.
- Workspace `package.json` files declared by root `workspaces`, or direct
  child `*/package.json` files when no workspaces are declared.
- Known plugin manifests under `.claude-plugin`, `.codex-plugin`, and
  `.agents/plugins`.
- Root `VERSION.md` using `**Current Version**: X.Y.Z`.
- Root `CLAUDE.md` using `> Version: X.Y.Z`.
- Optional TES config from `.tes/bump.json` or
  `~/.tes/bump/bump-{project}.json`.

Config paths must be relative, stay inside the target, and contain no `..`.
Regex custom targets must include a `{{VERSION}}` placeholder. JSON custom
targets update only a top-level `version` field.

## Scope

In scope: source detection, SemVer computation, bounded target discovery,
ordered writes, config path safety, dry-run planning, self-validation and
concise reporting.

Out of scope: changelog publishing pipelines, external spec lookups,
release-notes synthesis, service port discovery, and any caller-specific
config paths. TES release notes, public bundle identity, tags, pushes, and
publishing remain owned by the caller's release workflow.

When the target is the `tilly-engineer-skills` package source, do not allow a
generic bump that only updates `package.json`. Use the package release workflow
or an explicit `.tes/bump.json` that covers release identity surfaces.

## Locks

- Do not bump without reading the current source version first.
- Do not create a missing `VERSION` file.
- Do not modify files outside the discovered target list.
- Do not commit, tag, push, publish, or edit remotes.
- Do not update package locks as part of this skill.
- Do not let a commit or release close while `--governance-check` returns
  `NEEDS_VERSION_DECISION` or `NEEDS_REVIEW`.
- Do not claim TES package release closure without the package release gates
  and release identity decision.
- Do not partially bump the TES package source without an explicit TES bump
  config.
- Do not hardcode project-specific changelog, MCP, API, or Oracle behavior.

## Validation

Validate the helper:

```bash
python3 scripts/tes_bump.py --self-test
python3 scripts/tes_bump.py --target . --governance-check
```

Validate adapter exposure after source changes:

```bash
npm run command-triggers:self-test
npm run materialize:check
```

## Done

`tes-bump` is complete when it has either proved no bump is needed, stopped
closure with `NEEDS_VERSION_DECISION`, or applied a synchronized bump and
reported the old version, new version, source file, updated targets, validation
result, and next Git steps. If any target is out of sync, close as
`NEEDS_REVIEW`, not `PASS`.
