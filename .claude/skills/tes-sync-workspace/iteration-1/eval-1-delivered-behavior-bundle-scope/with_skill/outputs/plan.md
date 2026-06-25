# TES Sync Plan — 0.3.125 → 0.3.126 (Dry Plan, No Writes)

Skill self-consumed: `.claude/skills/tes-sync/SKILL.md` References cross-checked: `references/bump-scope.md`, `references/public-bundle-traps.md`, `references/tag-conflict-resolution.md`.

Working state captured before drafting this plan (read-only):

- `HEAD` = `ff923cc feat(tes-align): close external review + single-current-dist; release 0.3.125`
- `package.json` `version` = `0.3.125`
- `bin/tes.js` `TES_VERSION` = `0.3.125`
- Branch = `main`, clean per user statement
- `tes_bump.py --governance-check` per user = `NEEDS_VERSION_DECISION`

Target identity after bump: **`0.3.126`**.

---

## 1. Scope

**Bundle (Bump + bundle + public refs) — default.**

Justification (one sentence): the diff adds a new gate to `scripts/project_alignment_oracle.py` (oracle behavior change observable by adopters) and rewrites both adapter SKILL bodies (`src/adapters/codex/skills/tes-align/SKILL.md` and `src/adapters/claude/skills/tes-align/SKILL.md`), so a target project that installs the new version will observe a different delivered behavior — the `bump-scope.md` heuristic ("would a target project that installs the new version observe a difference?") answers **yes** on two surfaces, which is the canonical signal for the bundle scope. Source-only is rejected because both adapter skill bodies moved — those flow through the public installer bundle, not just source identity.

---

## 2. Plan (sequential phases — every phase blocks the next)

### Phase 1 — Pre-flight (read-only, confirm baseline)
- `git status -sb` — must show clean tree on `main`, only the announced diff staged/unstaged.
- `python3 scripts/tes_bump.py --governance-check` — re-confirm `NEEDS_VERSION_DECISION` and capture which paths drove the decision (for closeout note).
- Inspect diff list against the announced set: `scripts/project_alignment_oracle.py`, `src/adapters/codex/skills/tes-align/SKILL.md`, `src/adapters/claude/skills/tes-align/SKILL.md`, `docs/mesh/TES-ALIGN-SEMANTIC-RESIDUE.md`, `docs/evidence/reports/2026/05/26/tes-align/<...>/REPORT.md`. No surprise files in `.tes/` or stale `docs/dist/`.

**Post-condition:** clean tree on `main`, governance verdict `NEEDS_VERSION_DECISION`, no stray paths.

### Phase 2 — Scope announcement
- State out loud: "Scope = bundle. Bumping `0.3.125 → 0.3.126` across all identity, bundle, public refs, and tag surfaces."
- No writes yet.

### Phase 3 — Source identity bump (touch every file; missing one = drift)

Canonical set from `bump-scope.md` (each cell becomes one targeted edit; no global `sed` across the whole tree):

| Surface | Path | Edit |
|---|---|---|
| Package manifest | `package.json` | `"version": "0.3.125"` → `0.3.126` |
| CLI bin | `bin/tes.js` | `TES_VERSION = "0.3.125"` → `0.3.126` |
| Public badge | `README.md` | shields.io URL `0.3.125` → `0.3.126` |
| TDS header | `docs/tds/DOCS-INDEX.yml` | top-level `version: 0.3.125` → `0.3.126` |
| Doc index | `docs/INDEX.md` | "Public installer bundle" row |
| Codex doc | `docs/adapters/CODEX.md` | "Project version" line |
| Roadmap | `docs/roadmap/README.md` | baseline sentence |
| RC roadmap | `docs/roadmap/RC1-READINESS-ROADMAP.md` | "Package version" row |
| Script VERSION constants | `scripts/**.py` | anchored sed: `^VERSION = "0\.3\.125"$ → 0.3.126` |
| Validator paths | `scripts/validate_reference_package.py` | three `docs/dist/0.3.125/...` entries — **hand-edit, scoped pattern, see Trap watch** |
| Oracle fixture | `scripts/project_alignment_oracle.py` | `tes_version: 0.3.125` fixture frontmatter → `0.3.126` |
| npx help text | `scripts/tes_npx_oracle.py` | `--github-ref` example `v0.3.125` → `v0.3.126` |
| Codex plugin | `src/adapters/codex/plugin/plugin.json` | `version` |
| Codex marketplace | `src/adapters/codex/plugin/marketplace.json` | **two** `version` keys |
| Claude plugin | `src/adapters/claude/plugin/plugin.json` | `version` |
| Claude marketplace | `src/adapters/claude/plugin/marketplace.json` | **two** `version` keys |

Bulk-sed (script VERSION constants only — anchored to avoid touching docstrings/help text/fixtures):

```bash
for f in scripts/*.py; do
  sed -i '' 's/^VERSION = "0\.3\.125"$/VERSION = "0.3.126"/' "$f"
done
```

**Post-condition:** all 16 source identity surfaces synchronized to `0.3.126`. No `0.3.125` leftovers outside `docs/dist/`, `docs/evidence/`, and `RELEVANT-FINDINGS-CHANGELOG`.

### Phase 4 — Public refs + i18n (bundle scope only)

- `docs/install/INSTALL.md` — three `#v0.3.125` install commands → `#v0.3.126`.
- `docs/install/COMMAND-TRIGGERS.md` — install row.
- `docs/llms.txt` — install line.
- `docs/i18n/tes-public.content.json` — for **each** language (EN, ES, PT): `release_meta`, `manual_meta`, `version`, every `#v0.3.125` code block.
- `docs/i18n/tes-public.structure.yml` — `bundle_index`. **Do not yet touch `bundle_sha256`** — that gets updated post-publish in Phase 5.

Sanity sweep (must return zero hits outside the allowlisted paths):

```bash
grep -rn "0\.3\.125" --include="*.py" --include="*.json" \
  --include="*.md" --include="*.yml" \
  | grep -v "docs/dist/" | grep -v "docs/evidence/" \
  | grep -v "RELEVANT-FINDINGS-CHANGELOG"
```

**Post-condition:** zero unaccounted-for `0.3.125` references in source.

### Phase 5 — Publish bundle (bundle scope only)

```bash
python3 scripts/tes_bundle.py publish --adapter all
```

Verify the publish output:
- `docs/dist/0.3.126/` now contains `index.json`, the zip, and `.sha256`.
- `pruned_versions` lists `docs/dist/0.3.125/` (single-current-dist policy).
- Capture the printed `bundle_sha256`.

Hand-edit `docs/i18n/tes-public.structure.yml` `bundle_sha256` → the new SHA. **This is the trap that triggers `[tds-surface] BLOCKER: bundle_sha_mismatch` if skipped.** See Trap watch.

**Post-condition:** `docs/dist/0.3.126/**` exists, old dist pruned, `bundle_sha256` in `structure.yml` matches the new sidecar.

### Phase 6 — Regenerate public HTML

```bash
python3 scripts/build_public_docs.py
grep -c "0\.3\.125" docs/index.html docs/install/USER-MANUAL.html
```

Both must return `0`. Never hand-edit the HTML.

**Post-condition:** public HTML rebuilt from i18n, no stale version references.

### Phase 7 — Final validation

```bash
git add -A
npm run commit:check
python3 scripts/tes_bump.py --governance-check
```

- `commit:check` must return all 33 gates PASS.
- `tes_bump.py --governance-check` must return `PASS: version bump surfaces are synchronized`.
- Any `FAIL`/`BLOCKER` → stop, route through `public-bundle-traps.md`, fix root cause, re-run once. Do not stack writes on a red state.

**Post-condition:** clean gate suite, governance PASS.

### Phase 8 — Commit (atomic, one commit for the whole sync)

Conventional commit, HEREDOC for safety. Draft body:

```
feat(project-alignment-oracle): add <new-gate-name> gate; release 0.3.126

Closes the evidence at docs/evidence/reports/2026/05/26/tes-align/<...>/REPORT.md.
The new gate <one-line behavior summary> prevents <failure pattern>.
Adapter skill bodies (Codex + Claude) updated in lockstep so the
materialized contract on target projects matches the source oracle.

Release identity 0.3.125 -> 0.3.126 synchronized across package.json,
bin/tes.js, README badge, docs/tds/DOCS-INDEX.yml, docs/INDEX.md,
docs/adapters/CODEX.md, roadmap docs, scripts/**.py VERSION constants,
validate_reference_package.py REQUIRED_PATHS, oracle fixture frontmatter,
tes_npx_oracle.py help text, both plugin.json/marketplace.json pairs,
docs/install/INSTALL.md, docs/install/COMMAND-TRIGGERS.md, docs/llms.txt,
docs/i18n/tes-public.content.json (EN/ES/PT), structure.yml bundle_index +
bundle_sha256, docs/dist/0.3.126/ bundle, and regenerated public HTML.

Retained certification packet:
docs/evidence/reports/2026/05/26/tes-align/<...>/REPORT.md.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
```

Verify:
- `git status` — clean.
- `git log -1 --stat` — confirms expected files in the commit.

**Post-condition:** one commit on `main`, message references the evidence packet path.

### Phase 9 — Push

```bash
git push origin main
git status -sb
```

Status must read `## main...origin/main` with no `[ahead]`.

If push is rejected (non-fast-forward), do **not** force. Diagnose, `git pull --rebase`, re-run `commit:check`, and if rebase touches identity surfaces bump again to `0.3.127` and republish.

**Post-condition:** `origin/main` = local `main`.

### Phase 10 — Tag (bundle scope only)

Inspect before creating:

```bash
git tag -l v0.3.126
git ls-remote --tags origin v0.3.126
```

Decision tree (`tag-conflict-resolution.md`):
- **Case A (expected):** tag does not exist anywhere → safe to create at HEAD and push.
- **Case D (trap):** tag exists pointing to a non-HEAD commit → **stop**, quote the conflict to the user verbatim, wait for explicit authorization. The 0.3.124 incident is precedent: never move a public tag silently.

Assuming Case A:

```bash
git tag -a v0.3.126 -m "release 0.3.126 — <new gate name>; evidence at docs/evidence/reports/2026/05/26/tes-align/<...>/REPORT.md"
git rev-list -n 1 v0.3.126   # must equal git rev-parse HEAD
git push origin v0.3.126
git ls-remote --tags origin v0.3.126^{}   # must equal HEAD
```

**Post-condition:** annotated tag at HEAD, on remote, dereferenced remote hash equals HEAD.

### Phase 11 — Release certification

```bash
npm run release:check
```

Required result:
- `status: PASS`
- `classification: certified_local`
- `resolved_commit` = `git rev-parse HEAD`

Anything else means tag and source are not aligned — stop and reconcile. Do **not** patch the certification by editing source.

**Post-condition:** release certified.

### Phase 12 — Closeout

Single block report (see "Closeout (preview)" section below).

---

## 3. Active phase

**Phase 1 — Pre-flight.**

Command about to run (read-only):
```bash
git status -sb && python3 scripts/tes_bump.py --governance-check
```

Expected post-condition: clean tree on `main` with the announced 5-file diff; governance check returns `NEEDS_VERSION_DECISION` and names `scripts/project_alignment_oracle.py` and the two adapter SKILL.md files as the drivers (consistent with the bundle-scope justification).

User has frozen writes for this run, so Phases 3–11 will not execute until explicit go-ahead.

---

## 4. Trap watch (conditions active for THIS diff)

Given the announced diff (oracle gate + both adapter SKILLs + mesh doc + evidence report), these traps apply:

1. **`validate_reference_package.py` REQUIRED_PATHS scoped-sed trap** (`bump-scope.md` "Why the scoped pattern matters", `public-bundle-traps.md` "[validate_reference_package] FAIL: required path missing"). A naive `sed 's|0.3.125|0.3.126|g'` against the whole file replaces the directory version but leaves the zip filename `tilly-engineer-skills-0.3.125.zip` referenced under `docs/dist/0.3.126/`, which passes Python syntax but fails `commit:check`. Resolution: hand-edit the three lines, or use a regex anchored to both directory and filename. **Watch in Phase 3.**

2. **`bundle_sha256` is hand-maintained** (`public-bundle-traps.md` "[tds-surface] BLOCKER: bundle_sha_mismatch"). `tes_bundle.py publish` writes the new SHA to the sidecar but does **not** write it to `docs/i18n/tes-public.structure.yml`. Forgetting this copy step is the most common 33-gate failure. **Watch in Phase 5; the literal action is "read the printed sha and paste it into structure.yml `bundle_sha256` before regenerating HTML in Phase 6."**

3. **Evidence packet and mesh doc must be tracked** (`public-bundle-traps.md` "[tes-reference] FAIL: untracked package path"). The new `docs/evidence/reports/2026/05/26/tes-align/<...>/REPORT.md` and `docs/mesh/TES-ALIGN-SEMANTIC-RESIDUE.md` are in the diff. If either is referenced from `REQUIRED_PATHS` or needs a TDS index entry (`docs/tds/DOCS-INDEX.yml`), confirm before `commit:check`. The mesh doc almost certainly needs a TDS entry. **Watch in Phase 4/7.**

4. **TDS doc-size budget** (`public-bundle-traps.md` "[doc-size] FAIL"). The new mesh doc and the modified adapter SKILLs may push past the 500-line default. Do **not** raise the override in `validate_doc_size.py`; extract a sub ref under `docs/mesh/**` and link from the parent. **Watch in Phase 7.**

5. **Stale-tag trap on `v0.3.126`** (`tag-conflict-resolution.md` Case D, precedent: 0.3.124). The diagnosis order in Phase 10 covers this. If `git ls-remote --tags origin v0.3.126` returns a pre-existing tag pointing to a non-HEAD commit, **stop and quote the conflict to the user**. Do not move the tag without explicit authorization.

6. **`source_tree_state: dirty` in publish metadata** (`public-bundle-traps.md`). Phase 5 runs before Phase 8 commit, so the bundle will publish with a dirty working tree — informational, not a blocker. `release:check` in Phase 11 validates tag/commit alignment separately. Acceptable; no action.

7. **`commit:check` side-effect republish** (`public-bundle-traps.md` "`npm run commit:check` runs `tes_bundle.py publish` as a side effect"). Expected behavior under the single-current-dist policy. If gate output shows additional `pruned_versions`, this is not a regression.

---

## 5. Closeout (preview — to be filled at Phase 12)

To be reported as one block once Phases 3–11 execute:

- **Final claim:** PASS — release `0.3.126` certified locally, or NEEDS_REVIEW with the specific failing gate and the trap it maps to.
- **Commit hash:** `<git rev-parse HEAD after Phase 8>`.
- **Tag:** `v0.3.126`, dereferenced remote hash equals commit hash.
- **Bundle SHA:** `<copied from docs/dist/0.3.126/tilly-engineer-skills-0.3.126.zip.sha256>`.
- **Evidence packet path:** `docs/evidence/reports/2026/05/26/tes-align/<...>/REPORT.md`.
- **Pruned dists:** `docs/dist/0.3.125/` (single-current-dist policy).
- **Limits:** new oracle gate exercised only against in-tree fixtures; adopter projects on `<v0.3.126` will not pick it up until next install.
- **Follow-ups:** (a) confirm mesh doc TDS index entry stayed within doc-size budget; (b) monitor first adopter install of `0.3.126` for unexpected gate failures attributable to the new behavior.

---

## Skipped phases

None — bundle scope runs all 12 phases per `SKILL.md` §Workflow.

## Awaiting user authorization

No writes have been performed. Awaiting explicit go to execute Phase 1 read-only commands, then Phase 2 scope announcement, then Phase 3 onwards.
