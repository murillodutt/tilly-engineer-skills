# Public Bundle Traps

Load this when `npm run commit:check` returns a failure tag or when the
publish phase produced unexpected output. Each trap below was observed
in real cycles and has a specific resolution.

## `[tds-surface] BLOCKER: bundle_sha_mismatch`

**Symptom:** the `tds-surface` oracle reports a SHA mismatch between
`docs/i18n/tes-public.structure.yml` `bundle_sha256` and the actual zip
sidecar.

**Cause:** `bundle_sha256` in `structure.yml` is hand-maintained. The
publish phase produces a new sha on every run, but the structure file
keeps the previous value until you copy the new one over.

**Resolution:**

```bash
# read the sha printed by tes_bundle.py publish, or:
cat docs/dist/<new>/tilly-engineer-skills-<new>.zip.sha256
# update docs/i18n/tes-public.structure.yml: "bundle_sha256": "<new sha>"
python3 scripts/build_public_docs.py
python3 scripts/tds_surface_oracle.py
```

Re-run `npm run commit:check`.

## `[tes-reference] FAIL: untracked package path`

**Symptom:** the reference validator reports a required path is not
staged or tracked.

**Cause:** the validator runs with `--staged-ready`, which requires every
file in `REQUIRED_PATHS` to be either tracked or in the index. A new
governance doc or evidence packet that was created but not staged trips
this check.

**Resolution:**

```bash
git add <new path>
```

Or, if the file is genuinely not required (rare), remove it from
`REQUIRED_PATHS`.

## `[tds] FAIL: missing index entry`

**Symptom:** `validate_tds.py` reports a Markdown file with frontmatter
that is not declared in `docs/tds/DOCS-INDEX.yml`.

**Cause:** any TDS-labeled doc must be indexed.

**Resolution:** add an entry under the matching class with `path`, `id`,
`class`, `status`, `consumer`, `source_of_truth`, `evidence_level`.

## `[doc-size] FAIL`

**Symptom:** a doc exceeded the budget (default 500 lines).

**Cause:** new content pushed the file past its budget.

**Resolution:** extract the deepest section into a focused reference doc
under `docs/mesh/**` and reference it from the parent. Do **not** raise
the override in `validate_doc_size.py`. The whole point of the limit is
that long docs are hard to maintain.

When the extracted doc gets new content of its own, it must be indexed
in TDS and `validate_reference_package.py` `REQUIRED_PATHS`.

## `[validate_reference_package] FAIL: required path missing`

**Symptom:** a required path declared in `REQUIRED_PATHS` does not exist
on disk.

**Cause:** typo, premature delete, or — frequently — a stale dist path
from an aborted bump. The most common case: the validator points to
`docs/dist/<new>/tilly-engineer-skills-<old>.zip` because a global sed
mutilated the filename.

**Resolution:** read `references/bump-scope.md` "Why the scoped pattern
matters" section. Hand-fix the three dist lines if needed.

## `pruned_versions: []` when expected to prune

**Symptom:** `tes_bundle.py publish` ran but did not remove peer dist
directories.

**Cause:** the publish flow only prunes after a successful write of the
current version. If `build_bundle` failed earlier, prune is skipped.

**Resolution:** read the full publish output for the actual failure.
Often a stale `.tes/setup/` cache or a dirty worktree.

## `git push` rejected (non-fast-forward)

**Symptom:** the push fails because remote has commits HEAD does not
know about.

**Cause:** another branch was merged or a hotfix landed on `origin/main`.

**Resolution:** investigate. Do **not** `--force` push. Run `git pull
--rebase`, resolve conflicts, re-run `npm run commit:check`, push again.

If the rebase touches identity surfaces (version, bundle), bump again to
a new patch and republish before pushing.

## Stale tag pre-existing on remote

See `references/tag-conflict-resolution.md`. This deserves its own
document because the recovery is destructive and needs care.

## Bundle source_tree_state: dirty

**Symptom:** `tes_bundle.py publish` returns `source_tree_state: dirty`
in the metadata.

**Cause:** the publish ran with uncommitted changes in the working
tree. The bundle still produces, but its source commit reference will
not match a future tag.

**Resolution:** this is informational, not a blocker. The
`release:check` after tag push validates the tag/commit alignment
separately. For a fully clean run, stage and commit before publishing.

## `npm run commit:check` runs `tes_bundle.py publish` as a side effect

**Symptom:** historical dist directories disappeared after running
commit:check, even though you did not invoke publish.

**Cause:** `commit:check` includes oracles that touch the bundle layer.
After the single-current-dist policy was added, any oracle path that
re-publishes (e.g., a smoke test) also prunes.

**Resolution:** this is intentional behavior under the new policy. If
you need to preserve a historical bundle for a one-off audit, copy it
out of the working tree before running the gate.

## Recovery Mantra

When something fails:

1. Stop. Do not stack more writes on top of a broken state.
2. Read the actual oracle output — every gate names the file and rule
   it failed on.
3. Fix the root cause, not the symptom. The bundle sha mismatch is
   fixed by updating the sha, not by skipping the gate.
4. Re-run `npm run commit:check` once. Green means proceed; red means
   investigate the new error before retrying.
