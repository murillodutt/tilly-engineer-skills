---
tds_id: mesh.git_safety
tds_class: governance
status: active
consumer: adopters, installing agents, and package maintainers
source_of_truth: true
evidence_level: L2
tver: 0.1.0
---

# Tilly Git Safety

Git is the project history. Tilly may use Git to protect, inspect, and certify
an installation, but Git mutation stays explicit and local unless the user asks
for more.

## User Contract

Tilly may inspect `git status`, record the current `HEAD`, offer a local
baseline commit before installation edits, install local hooks, write rollback
instructions, and prepare a semantic local commit after the certification
report.

Tilly must not push, publish, tag, amend, rewrite history, change remotes, or
run destructive rollback commands without explicit user approval in the current
conversation.

`GO meshed` means the selected Tilly route was installed or updated and locally
checked. It does not mean commit or push. `GO committed` and `GO published`
require separate user approval.

## Local Artifact Hygiene

When the target is a Git repository, the installer must protect local transport
and cache files through `.git/info/exclude`. This is local to the target repo
and does not modify the user's project `.gitignore`.

The local exclude must cover:

- `.tilly/bin/*.bak-*`
- `.tilly/bin/__pycache__/`
- `*.pyc`
- `.tilly/field-reports/`
- `.tilly/cortex/*.sqlite`
- `.tilly/cortex/*.sqlite-*`

These paths are rollback, transport, bytecode, or derived cache artifacts. They
are not project memory and not durable Tilly surfaces.

The installer must not ignore `.tilly/bin/*.py`. Those helper scripts are the
project-scoped Tilly runtime surface and may be committed when the user chooses
to preserve the installed mesh.

## Rollback

Every installation or update report must include the baseline commit and the
safe rollback path. Tilly may show `git reset --hard <baseline-head>` or
`git revert <install-commit>`, but it must not run either command automatically.

If an earlier installation already committed ignored local artifacts, the next
installer run should prevent new artifacts from being staged. Removing already
tracked local artifacts is a separate reviewed Git change.
