---
name: tes-sync
description: Local-only self-consumed guidance for running the complete sync routine on the TES source package: identity bump, public bundle, validate, commit, push, tag, release certification. Use when the user says sync completo, bump + commit + push, release, publica, /tes-sync, or asks to ship a delivered-behavior change end-to-end. Mirror of the audit checklist that survived the 0.3.124 and 0.3.125 cycles. Do not present as a user-facing TES product skill.
license: MIT
---

# TES Sync

Local development surface only. This skill captures the bump + commit + push +
tag + release certification routine that worked end-to-end on the TES source
package. It is not a public TES product skill and must not be materialized to
target projects.

`docs/governance/SYNC-AUDIT-CHECKLIST.md` is the human-readable contract.
This skill is the agent-facing condensation of the same flow.

Self-consume when the user asks for a complete sync, a release, a bump
followed by push, or invokes `/tes-sync`. Do not ask the user to invoke this
skill.

## When To Activate

Activate on these signals from the user:

- "sync completo", "sincronia completa", "fechar release", "release X"
- "bump + commit + push", "publica release", "ship this"
- "/tes-sync"
- An external review or canary report that closes with a delivered behavior
  change waiting to ship.

Do not activate for read-only inspection, draft commits, or single-file
edits. The skill is for the whole route.

## Operating Principle

Sync is one operation with many synchronized surfaces. Skipping a surface
breaks something downstream. The skill enforces the order, the scope
decision, and the traps that already cost time in prior sessions.

Three sync scopes exist. Pick one **before** touching files — the wrong
scope name is itself a class of error (no-bump and source-only are not
synonyms; calling one by the other's name leaks into commit messages and
audit trails):

| Scope | When | Bumps version? |
|-------|------|---------------:|
| **No bump** | `tes_bump.py --governance-check` returns `PASS`. Changes do not move delivered behavior (governance docs, internal evidence, test fixtures). Commit + push only. | No |
| **Bump source-only** | Delivered behavior changes but no installer / i18n / bundle ref moves. Bump source identity, no bundle regeneration. Rare in practice. | Yes |
| **Bump + bundle + public refs** | Default for delivered-behavior changes. Every identity surface, bundle, installer, i18n, public HTML, tag, `release:check`. | Yes |

If unsure, read `references/bump-scope.md` to decide.

Skills under `.claude/skills/**` and `.agents/skills/**` are local
development surface. New skill source files go in the same commit as the
sync they were authored for — they are not separate "workspace
artifacts" to defer. The decision is only whether the new skill itself
constitutes delivered behavior (it usually does not, because local
development skills are not materialized to targets).

## Workflow

The phases are sequential. Do not stage the next phase until the prior one
is clean.

### 1. Pre-flight

```bash
git status -sb
python3 scripts/tes_bump.py --governance-check
```

- Diff scope is intentional; no surprise files in `.tes/` or stale dist.
- Governance check verdict declares whether a bump is needed and which
  paths drive the decision.

### 2. Scope decision

Match the governance verdict to one of the three scopes above. Announce the
choice in one sentence before any write.

### 3. Source identity bump (when bumping)

Touch every file in this set. Missing one creates a sync drift that the
parity checks catch downstream.

- `package.json` `version`
- `bin/tes.js` `TES_VERSION`
- `README.md` version shield badge
- `docs/tds/DOCS-INDEX.yml` header `version`
- `docs/INDEX.md` `Public installer bundle` row
- `docs/adapters/CODEX.md` `Project version`
- `docs/roadmap/README.md` baseline line
- `docs/roadmap/RC1-READINESS-ROADMAP.md` `Package version` row
- All `scripts/**.py` `VERSION = "<old>"` constants (bulk `sed` is safe; see
  `references/bump-scope.md` for the canonical list).
- `scripts/validate_reference_package.py` `REQUIRED_PATHS`
  `docs/dist/<old>/...` entries. The zip filename embeds the version, so
  a naive `sed -i 's|<old>|<new>|g'` against the whole file leaves
  `tilly-engineer-skills-<old>.zip` referenced under `dist/<new>/`. Use a
  scoped pattern or hand-edit those three lines.
- `scripts/project_alignment_oracle.py` fixture frontmatter
  `tes_version: <old>`
- `scripts/tes_npx_oracle.py` `--github-ref` help-text example
- `src/adapters/codex/plugin/plugin.json` and `marketplace.json`
- `src/adapters/claude/plugin/plugin.json` and `marketplace.json`

### 4. Public refs and i18n (bundle scope only)

- `docs/install/INSTALL.md` `#v<new>`
- `docs/install/COMMAND-TRIGGERS.md` install row
- `docs/llms.txt` install line
- `docs/i18n/tes-public.content.json` (release_meta, manual_meta, version,
  every `#v<old>` code block, three languages — EN, ES, PT)
- `docs/i18n/tes-public.structure.yml` `bundle_index`. `bundle_sha256`
  gets a separate update after publish.

Sanity scan to catch leftovers:

```bash
grep -rn "0\.3\.<old>" --include="*.py" --include="*.json" \
  --include="*.md" --include="*.yml" \
  | grep -v "docs/dist/" | grep -v "docs/evidence/" \
  | grep -v "RELEVANT-FINDINGS-CHANGELOG"
```

Anything that surfaces is either a deliberate historical reference or a
missed file. Decide explicitly.

### 5. Publish bundle (bundle scope only)

```bash
python3 scripts/tes_bundle.py publish --adapter all
```

- `docs/dist/<new>/` now contains `index.json`, the zip, and `.sha256`.
- `pruned_versions` in the publish report lists the historical dirs that
  the single-current-dist policy removed.

Copy the printed sha into `docs/i18n/tes-public.structure.yml`
`bundle_sha256`. **This is hand-maintained.** Skipping it triggers
`[tds-surface] BLOCKER: bundle_sha_mismatch`. See
`references/public-bundle-traps.md`.

### 6. Regenerate public HTML

```bash
python3 scripts/build_public_docs.py
```

Sanity check the regenerated files:

```bash
grep -c "0\.3\.<old>" docs/index.html docs/install/USER-MANUAL.html
```

Both must return `0`.

### 7. Final validation

```bash
git add -A
npm run commit:check
python3 scripts/tes_bump.py --governance-check
```

`npm run commit:check` runs the full 33-gate suite. Treat any `FAIL` or
`BLOCKER` as a stop condition. Common traps with their resolution live in
`references/public-bundle-traps.md`.

Governance check must return `PASS: version bump surfaces are
synchronized`.

### 8. Commit

```bash
git commit -m "$(cat <<'EOF'
<type>(<scope>): <one-sentence subject>

<why this matters; the failure pattern being closed when applicable>

<bump scope statement: "Release identity X -> Y synchronized..." when applicable>

Retained certification packet: <path to evidence>.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

Verify after commit:

```bash
git status
git log -1 --stat
```

### 9. Push

```bash
git push origin main
git status -sb
```

Status must show `## main...origin/main` without `[ahead]`.

### 10. Tag (bundle scope only)

Tags are the trap that bit us at 0.3.124. Always inspect before creating:

```bash
git tag -l v<new>
git ls-remote --tags origin v<new>
```

If a stale tag exists (points to an abandoned commit), see
`references/tag-conflict-resolution.md`. **Never** move a public tag
without explicit user authorization.

Annotated tag at HEAD:

```bash
git tag -a v<new> -m "<short rationale + evidence path>"
git rev-list -n 1 v<new>   # must equal git rev-parse HEAD
git push origin v<new>
```

### 11. Release certification

```bash
npm run release:check
```

This is the **named** certification gate. Generic phrases like "CI will
verify the tag" or "the release pipeline picks it up" do not satisfy
this step — the TES package owns `npm run release:check` specifically,
and that command is the only thing that resolves the public ref against
the tag and source.

Required result: `status: PASS`, `classification: certified_local`,
`resolved_commit` equals HEAD. Anything else means tag and source are not
aligned — stop and reconcile.

### 12. Closeout

Report in one block:

- Final claim (PASS / NEEDS_REVIEW with reason).
- Commit hash, tag, bundle sha.
- Evidence packet path.
- Limits and follow-ups.

## Brake

On `pause`, `pausa`, `freia`, `segura`, `para`, `hold`, `step back`,
`volta um nivel`, `cancel`, or `resuma onde estamos`, stop. Summarize the
current phase, the next planned write, and wait for explicit resume.

## Locks

- Do not skip `npm run commit:check`. The 33-gate suite catches the
  bundle sha mismatch, missing index entries, and parity drift that hand
  inspection misses.
- Do not edit `docs/dist/<version>/**` by hand. Always regenerate via
  `scripts/tes_bundle.py publish`.
- Do not hand-edit `docs/index.html` or `docs/install/USER-MANUAL.html`.
  They are generated by `scripts/build_public_docs.py` from `docs/i18n/**`.
- Do not raise `validate_doc_size.py` budgets to make a doc fit.
  Modularize and link from the parent.
- Do not embed project-specific vocabulary into TES generic code.
  Mechanism in TES, vocabulary in target.
- Do not keep more than one `docs/dist/<version>/` in the repository.
  `tes_bundle.py publish` enforces single-current-dist; reverting that
  state requires explicit policy reversal.
- Do not move a public tag without quoting the conflict to the user and
  waiting for authorization. Stale tags from orphan commits are the
  trap; treat them with care.
- Do not push or tag without `npm run commit:check` PASS.
- Do not present this skill as a user-facing TES product slash command.
  It is local development guidance.

## Output Shape

When activated, produce in this order:

1. `Scope`: no-bump | source-only | bundle. One sentence justifying.
2. `Plan`: numbered phases from the workflow you will execute.
3. `Active phase`: the current step, the command about to run, the
   expected post-condition.
4. `Trap watch`: any condition from `references/public-bundle-traps.md`
   that applies given the diff.
5. `Closeout`: final claim, hashes, evidence path.

Skip phases that do not apply (e.g., no bundle phases when scope is
no-bump), but state the skip explicitly so it is auditable.
