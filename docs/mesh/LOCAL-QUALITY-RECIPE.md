---
tds_id: mesh.local_quality_recipe
tds_class: mesh
status: active
consumer: adopters, installing agents, and package maintainers
source_of_truth: true
evidence_level: L2
tver: 0.1.0
---

# Local Quality Recipe

This recipe installs a project-local quality layer that adapts to the files, manifests, and tools present in each repository. It is a pattern, not a fixed stack.

## Contract

```text
staged files -> detected surfaces -> smallest local gates -> full closure gate
```

The local layer must:

- keep Git mutation local unless the user approves commit or push;
- route checks from evidence in the repository, not hard-coded preference;
- fail before commit for deterministic issues;
- keep network, publish, push, and remote mutation outside default hooks;
- prefer the smallest reproducing command before a full closure run.

## Files

Copy this shape into each target project:

| Path | Role |
|------|------|
| `lefthook.yml` | Hook command router with staged-file globs |
| `.githooks/pre-commit` | Git entrypoint delegating to Lefthook |
| `.githooks/pre-push` | Optional non-blocking local drain or smoke |
| `scripts/staged_surface_check.py` | JSON, YAML, and JavaScript syntax gate |
| `package.json` or project task file | User commands and full closure |
| `.git/info/exclude` | Local caches, bytecode, rollback files |

Activate hooks locally:

```bash
git config core.hooksPath .githooks
```

Do not put local cache exclusions in the project `.gitignore` unless they are real project policy.

## Pre-Commit Hook

The pre-commit hook should stay small:

```sh
#!/bin/sh
set -eu

exec lefthook run pre-commit
```

It should not push, publish, install cloud services, rewrite history, or require network access.

## Auto-Adaptive Router

The router reads staged paths and checks only relevant surfaces. It should use tool detection before running a command:

| Evidence | Surface | Preferred gate |
|----------|---------|----------------|
| `*.md`, docs index, frontmatter | Markdown docs | markdown lint, doc size, links, frontmatter |
| `tsconfig.json`, `*.ts` | TypeScript | package typecheck or `tsc --noEmit` |
| `*.tsx`, React dependency | React TSX | typecheck, lint, component tests when present |
| `*.vue`, Vue dependency | Vue SFC | `vue-tsc --noEmit`, eslint vue when present |
| `*.json` | JSON | parse, schema when known |
| `*.yml`, `*.yaml` | YAML | parse, schema when known |
| `*.css`, `*.scss` | Styles | stylelint or formatter check when present |
| scripts or CLIs | Runtime helpers | self-test or focused smoke |
| generated output | Materialization | source-to-output check, never hand-edit generated files |

When a tool is missing, the router should report `SKIP` with the missing tool and continue only if that surface is optional. Required project surfaces must fail with a clear command to install or run.

## Command Names

Use stable command names so agents and devs can rely on them:

| Command | Meaning |
|---------|---------|
| `quality:staged` | Run the router against staged files |
| `quality:docs` | Run documentation gates |
| `quality:types` | Run type gates |
| `quality:lint` | Run lint gates |
| `quality:test` | Run focused tests |
| `quality:diff` | Run Git whitespace checks |
| `commit:check` | Run the full local closure gate |

For npm projects, expose them in `package.json`. For Python, Go, Rust, or mixed repos, keep the same public names in `make`, `just`, `task`, or a project CLI.

## Full Closure

`commit:check` is the local CI contract. It should include every gate needed to say the repository is locally ready:

```text
structure validation
docs validation
typecheck
lint
tests
materialization or generated-output checks
contract/self-tests
git diff checks
```

Keep expensive external checks out of `commit:check` unless they are deterministic, authenticated locally, and required for the project contract.

## Failure Loop

Use one loop for every stack:

1. Name the failing gate and exact command.
1. Reproduce with the smallest command.
1. Fix the cause, not the symptom.
1. Re-run the smallest command.
1. Re-run `quality:staged` or the failed group.
1. Re-run `commit:check` before claiming closure.

Do not use `--no-verify` unless the user explicitly authorizes it and the risk is named.

## Replication Steps

1. Install `lefthook` and add `lefthook.yml`.
1. Install `.githooks/pre-commit` and optional `.githooks/pre-push`.
1. Add stable quality commands to the project task runner.
1. Add local cache and rollback patterns to `.git/info/exclude`.
1. Run `npm run hooks:install` (sets `core.hooksPath .githooks`).
1. Run `quality:staged` with representative staged fixtures.
1. Run `commit:check`.
1. Record which surfaces are `PASS`, `SKIP`, or `BLOCKED`.

The recipe is replicated only when the target project can answer: which surfaces were detected, which gates ran, which gates skipped with reason, and which command proves local closure.
