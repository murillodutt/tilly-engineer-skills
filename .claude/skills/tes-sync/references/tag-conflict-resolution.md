# Tag Conflict Resolution

Load this when `git tag -l v<new>` or `git ls-remote --tags origin v<new>` shows the tag already exists.

This is the trap that surfaced in the 0.3.124 cycle: a public tag `v0.3.124` existed on origin pointing to an abandoned commit (`9877682` — a bump attempt that never merged). The new release commit landed on `main`, and the tag pointing to the orphan was actively misleading: anyone running `npx ... #v0.3.124` would have received the abandoned source.

## Diagnosis Order

```bash
# 1. Does the tag exist locally?
git tag -l v<new>

# 2. Does the tag exist on remote?
git ls-remote --tags origin v<new>

# 3. Where does the tag point (locally)?
git rev-list -n 1 v<new>

# 4. Where does it point dereferenced (remote)?
git ls-remote --tags origin v<new>^{}

# 5. Where is HEAD?
git rev-parse HEAD

# 6. Do (3), (4), and (5) match?
```

## Decision Tree

### Case A: tag does not exist anywhere

Safe. Create and push:

```bash
git tag -a v<new> -m "<message>"
git push origin v<new>
```

### Case B: local tag matches HEAD, remote does not exist

Push the existing tag:

```bash
git push origin v<new>
```

### Case C: local tag points to HEAD, remote points to HEAD

Already pushed. No action needed. Run `npm run release:check` to confirm.

### Case D: tag points to an old commit, locally or remotely

**Stop.** This is the trap. Quote the conflict to the user:

```
Tag v<new> already exists, pointing to <old-commit-hash>.
HEAD is <head-hash>.

To move the tag to HEAD, I need to delete the local tag, delete the
remote tag, and recreate. This rewrites public release identity. Want
me to proceed?
```

Wait for explicit authorization. If denied, abort the sync and surface the conflict to the user with options:

- Bump again to a new patch (skips the conflict, leaves the stale tag untouched but unused).
- Investigate why the old tag exists (orphan branch? abandoned bump?).
- Manually clean up later.

### Case E: authorized move

Once the user authorizes:

```bash
# delete local
git tag -d v<new>

# delete remote
git push origin :refs/tags/v<new>

# create annotated at HEAD
git tag -a v<new> -m "<message>"

# verify
git rev-list -n 1 v<new>   # must equal git rev-parse HEAD

# push
git push origin v<new>

# verify remote
git ls-remote --tags origin v<new>^{}   # must equal HEAD

# certify
npm run release:check
```

The certification must return `status: PASS`, `resolved_commit` = HEAD.

## Why The Trap Exists

The TES bump flow encourages tagging every release. When an attempted release fails part-way through (e.g., bundle generation breaks, gates fail, user cancels), the commit and sometimes the tag may have already landed before the rollback. Future cycles see the tag and either:

1. Skip tagging (silent — the new release ships without a public ref).
2. Force-overwrite without authorization (destructive — the old tag target is lost from anyone watching tags as immutable artifacts).

Both are wrong. The skill enforces explicit user authorization for any public-tag move.

## Mantra

Tags are public artifacts. Treat them like signed commits: inspect before touching, never overwrite silently, always quote the conflict.
