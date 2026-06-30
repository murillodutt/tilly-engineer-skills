# GIT-GATES

Generated: 2026-06-30T14:06:00Z (repair round 2 — owner audit response)

Proof command:

```bash
for t in cursor claude codex; do
  TARGET=/Users/murillo/Dev/tes-canary/$t
  echo "=== $t ==="
  git -C "$TARGET" rev-parse --is-inside-work-tree
  git -C "$TARGET" rev-parse --short HEAD
  git -C "$TARGET" status --short --branch
  test -x "$TARGET/.git/hooks/pre-commit" && echo pre-commit: yes || echo pre-commit: no
  test -x "$TARGET/.git/hooks/pre-push" && echo pre-push: yes || echo pre-push: no
  grep -q strict "$TARGET/.git/hooks/pre-commit" && echo pre-commit-strict: yes || echo pre-commit-strict: no
  git -C "$TARGET" hook run pre-commit; echo pre-commit-run-exit:$?
done
```

## cursor

| Check | Result |
|-------|--------|
| inside work tree | true |
| HEAD | `44c80e7` |
| git status | clean |
| pre-commit | yes (`--strict` on alignment oracle) |
| pre-push | yes |
| `git hook run pre-commit` | exit **0**; `[project-alignment] PASS` |

## claude

| Check | Result |
|-------|--------|
| inside work tree | true |
| HEAD | `3fe7bc2` |
| git status | clean |
| pre-commit | yes (`--strict` on alignment oracle) |
| pre-push | yes |
| `git hook run pre-commit` | exit **0**; `[project-alignment] PASS` |

## codex

| Check | Result |
|-------|--------|
| inside work tree | true |
| HEAD | `6f9f118` |
| git status | clean |
| pre-commit | yes (`--strict` on alignment oracle) |
| pre-push | yes |
| `git hook run pre-commit` | exit **0**; `[project-alignment] PASS` |

## Notes

- Prior HEAD rows (`edd9ead` / `0d586dc` / `cb2c6a1`) were stale evidence; superseded by this file.
- Pre-commit now fails on `project_alignment_oracle.py --strict` when status is `NEEDS_REVIEW` (exit 2), not only on `FAIL`.
