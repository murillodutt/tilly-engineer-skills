---
tds_id: governance.sync_audit_checklist
tds_class: governance
status: active
consumer: maintainers running a delivered-behavior change with bump + commit + push
source_of_truth: true
evidence_level: L2
tver: 0.1.0
---

# Sync Audit Checklist

Use this checklist when a TES source change is large enough to need a version
bump, a public bundle, a tag, and a push. It captures the real sequence that
worked end-to-end and the traps that came up along the way.

It is not a substitute for `npm run commit:check`. It is the human-readable
audit path that wraps that gate.

## Pre-flight

- [ ] `git status -sb` shows the expected diff scope; no surprise files in
  `.tes/`, `docs/dist/`, or `node_modules/`.
- [ ] You can name in one sentence what delivered behavior changed. If you
  cannot, the bump is premature.
- [ ] `docs/mesh/TES-ALIGN-SKILL-SOURCE-OF-TRUTH.md` or any other touched
  source-of-truth doc has `sources_verified_on` within
  `source_refresh_interval_days`. Refresh the date if the doc was used as
  construction truth this session.
- [ ] Read `AGENTS.md` `release_identity` block. Confirm whether this change
  is patch / minor / major and whether bundle generation is required.

## Source change

- [ ] Edits are surgical and trace to the stated change.
- [ ] No real project name or project-specific vocabulary was embedded into
  generic TES code, docs, evidence, commit messages, or tag annotations.
  Mechanism in TES, vocabulary in target.
- [ ] If you added a new governed doc, it lives under `docs/mesh/**` or
  `docs/governance/**`, not scattered across adapters.
- [ ] If you split a doc to satisfy `validate_doc_size.py`, the parent and
  the extracted file cross-reference each other and both are indexed.
- [ ] Adapter parity preserved: changes applied to Codex and Claude skill
  sources, and to Cursor only if Cursor owns an equivalent routing surface.
  No fake Cursor skill folder for symmetry.
- [ ] `CONTRACT-HISTORY.md` for each touched skill has a dated row referring
  to the change and the evidence backing it.

## Oracle / self-test

- [ ] `python3 scripts/<touched_oracle>.py --self-test` PASS.
- [ ] New behavior carries at least one adversarial fixture (the old gate
  would falsely PASS; the new gate must FAIL or NEEDS_REVIEW).
- [ ] Allowlist / historical-evidence fixture proves the gate does not
  over-fire on retained timelines.
- [ ] Word-boundary regression covered when literal-match was added (the
  short-literal-vs-longer-word trap).
- [ ] Malformed-input fixture surfaces a clear `code` rather than a stack
  trace.

## Indexing (correlation rule)

- [ ] New doc added under `docs/**`?
  - [ ] Entry in `docs/tds/DOCS-INDEX.yml`.
  - [ ] Row in `docs/INDEX.md` map.
  - [ ] Required path appended to `scripts/validate_reference_package.py`
    `REQUIRED_PATHS` when the doc is mandatory.
- [ ] New script added under `scripts/**`?
  - [ ] Listed in `REQUIRED_PATHS` if it is delivered behavior.
  - [ ] Has `VERSION = "<current>"` constant if it ships behavior tied to
    the package version.
- [ ] New current-evidence claim?
  - [ ] Added to `docs/evidence/current/CLAIMS.md` with proof, boundary, and
    retention status.
- [ ] New retained packet?
  - [ ] Lives under `docs/evidence/reports/YYYY/MM/DD/<domain>/<run-id>/`.
  - [ ] Indexed in `docs/tds/DOCS-INDEX.yml`.

## Doc size

- [ ] `python3 scripts/validate_doc_size.py` PASS.
- [ ] If a touched doc crossed 500 lines, extract a focused reference doc
  under `docs/mesh/**` and link it from the parent — do not raise the
  override budget by default.

## Version governance decision

Run `python3 scripts/tes_bump.py --governance-check`. Interpret the verdict:

- [ ] `PASS` → no bump needed; continue to **Commit**.
- [ ] `NEEDS_VERSION_DECISION` → choose the scope explicitly:
  - [ ] **Source-only sync** (recommended for hardening / oracle / skill
    body changes that do not change installer behavior).
  - [ ] **Source + public refs + bundle** (chosen this session: installer
    refs in `INSTALL.md`, `COMMAND-TRIGGERS.md`, `bin/tes.js`, i18n, and
    HTML all need to move together with a freshly generated bundle).
  - [ ] **Defer bump** with an explicit exception recorded in the closeout
    (allowed by `release_identity`).

## Identity bump 0.3.X → 0.3.Y

The bump touches more than `package.json`. The full set that has to move
together (verified this session):

- [ ] `package.json` `version`.
- [ ] `bin/tes.js` `TES_VERSION`.
- [ ] `README.md` version shield badge.
- [ ] `docs/tds/DOCS-INDEX.yml` header `version`.
- [ ] `docs/INDEX.md` `Public installer bundle` row.
- [ ] `docs/adapters/CODEX.md` `Project version`.
- [ ] `docs/roadmap/README.md` baseline line.
- [ ] `docs/roadmap/RC1-READINESS-ROADMAP.md` `Package version` row.
- [ ] All `scripts/**.py` `VERSION = "<old>"` constants.
- [ ] `scripts/validate_reference_package.py` `REQUIRED_PATHS` `docs/dist/<old>/...`
  entries.
- [ ] `scripts/project_alignment_oracle.py` fixture frontmatter
  `tes_version: <old>` (and any other oracle fixtures that embed the version).
- [ ] `scripts/tes_npx_oracle.py` `--github-ref` help-text example.
- [ ] `src/adapters/codex/plugin/plugin.json` and `marketplace.json`.
- [ ] `src/adapters/claude/plugin/plugin.json` and `marketplace.json`.

If the bump is **source + public refs**:

- [ ] `docs/install/INSTALL.md` install commands (`#v<new>`).
- [ ] `docs/install/COMMAND-TRIGGERS.md` install row.
- [ ] `docs/llms.txt` install line.
- [ ] `docs/i18n/tes-public.content.json` (release_meta, manual_meta,
  version, every code block with `#v<old>`, all three languages).
- [ ] `docs/i18n/tes-public.structure.yml` `bundle_index` and
  `bundle_sha256` (sha gets updated again after bundle is rebuilt).

Sanity scan:

```bash
grep -rn "0\.3\.<old>" --include="*.py" --include="*.json" --include="*.md" --include="*.yml" \
  | grep -v "docs/dist/" | grep -v "docs/evidence/" | grep -v "RELEVANT-FINDINGS-CHANGELOG"
```

Anything that surfaces here is either a deliberate historical reference or a
missed file. Decide explicitly; do not let it slide.

## Public bundle

Only when the bump scope is **source + public refs + bundle**:

- [ ] `python3 scripts/tes_bundle.py publish --adapter all` succeeds.
- [ ] `docs/dist/<new>/` contains `index.json`, the zip, and the `.sha256`
  sidecar.
- [ ] sha printed by `tes_bundle.py` matches `docs/dist/<new>/*.zip.sha256`.
- [ ] Copy that sha into `docs/i18n/tes-public.structure.yml`
  `bundle_sha256` (the structure.yml sha is hand-maintained; this is the
  trap that failed `tds-surface` this session).
- [ ] `python3 scripts/build_public_docs.py` regenerates `docs/index.html`
  and `docs/install/USER-MANUAL.html` against the refreshed i18n.
- [ ] `grep -c "0\.3\.<old>" docs/index.html docs/install/USER-MANUAL.html`
  returns `0` for both files.
- [ ] **Single-current-dist policy**: `docs/dist/` contains exactly one
  directory after publish: `docs/dist/<new>/`. Any prior `docs/dist/<old>/`
  is pruned automatically by `tes_bundle.py publish`; if it is not, the
  policy regressed. Historical bundles remain reachable through Git tags
  and the GitHub release surface. The TES repository keeps only the
  current public distribution.

## Final gate

- [ ] `git add -A` stages the full coordinated set (including the bundle
  binaries under `docs/dist/<new>/`, which are checked in by design).
- [ ] `npm run commit:check` PASS end-to-end. The 33 expected tags this
  session were:

  ```
  tes-reference, public-docs, tds, tds-surface, doc-size,
  context-mesh-plan, cortex, cortex-quality-oracle, cortex-mcp,
  field-reports, field-reports-quality, field-reports-github,
  root-context, public-bundle-oracle, tes-install:self-test,
  tes-npx:self-test, install-mcp, install-smoke, tes-init,
  project-context, project-alignment, tes-open-obsidian, tes-update,
  tes-legacy-retirement, tes-namespace, codex-plugin-oracle,
  claude-plugin-oracle, command-triggers, platform-surface,
  retention-metadata, reference-graph, materialize,
  adapter-parity-readiness
  ```

  If any tag flips to `FAIL` or `BLOCKER`, do **not** commit until the root
  cause is fixed. Common traps observed this session:

  - `tes-reference FAIL: untracked package path` → run `git add` for the
    new file before re-running.
  - `tds-surface BLOCKER: bundle_sha_mismatch` → copy the published sha
    into `structure.yml` and rebuild HTML.
  - `tds FAIL: missing index entry` → add to `docs/tds/DOCS-INDEX.yml`.
  - `doc-size FAIL` → extract or modularize, do not raise the budget.

- [ ] `python3 scripts/tes_bump.py --governance-check` returns
  `Version governance: PASS — version bump surfaces are synchronized`.

## Commit

- [ ] `git diff --cached --stat | tail -3` shows the expected file count
  and insertion/deletion magnitude.
- [ ] Commit message:
  - states what changed (one sentence subject);
  - explains why in the body (the retired-claim / false-green narrative
    when applicable);
  - cites the retained evidence packet path;
  - declares the bump scope (`Release identity X -> Y`) when a bump
    happened;
  - keeps the standard `Co-Authored-By` footer.
- [ ] After commit, `git status` shows clean tree and
  `git log -1 --stat` matches expectations.

## Push

- [ ] `git status -sb` shows `## main...origin/main [ahead N]` with the
  expected `N`.
- [ ] `git push origin main` succeeds.
- [ ] `git status -sb` now shows `## main...origin/main` without `[ahead]`.

## Tag (only when the bump publishes a new public ref)

This is the trap that surfaced this session: a stale `v<new>` tag may
already exist locally and remotely from a previous attempt.

- [ ] `git tag -l v<new>` → check local presence.
- [ ] `git ls-remote --tags origin v<new>` → check remote presence.
- [ ] `git rev-list -n 1 v<new>` → if the tag exists, confirm it points to
  HEAD; if not, the tag is stale.
- [ ] When the tag is stale and you have explicit user authorization to
  move it:
  - [ ] `git tag -d v<new>` (local).
  - [ ] `git push origin :refs/tags/v<new>` (remote).
- [ ] Create annotated tag at HEAD:
  - [ ] `git tag -a v<new> -m "<short rationale + evidence path>"`.
- [ ] `git rev-list -n 1 v<new>` equals `git rev-parse HEAD`.
- [ ] `git push origin v<new>` succeeds.
- [ ] `git ls-remote --tags origin v<new>^{}` resolves to HEAD commit.
- [ ] `npm run release:check` returns `status: PASS`,
  `classification: certified_local`, and `resolved_commit` equals HEAD.

## Closeout report

Record in the session closeout:

- [ ] Final claim sentence (PASS / NEEDS_REVIEW with explicit reason).
- [ ] Commit hash and tag (when applicable).
- [ ] Retained evidence packet path.
- [ ] Limits and remaining follow-ups (e.g., target-project canary still
  owes a real rerun against the hardened oracle).
- [ ] Any deferred bump exception (per `release_identity`).

## Locks

- Do not push without `npm run commit:check` PASS.
- Do not move a public tag without explicit user authorization, even when
  the stale tag points to an abandoned attempt. Quote the conflict and
  wait for the call.
- Do not edit `docs/dist/<version>/**` by hand. Always regenerate via
  `scripts/tes_bundle.py publish`.
- Do not hand-edit `docs/index.html` or `docs/install/USER-MANUAL.html`.
  They are generated by `scripts/build_public_docs.py` from
  `docs/i18n/**`.
- Do not raise `validate_doc_size.py` budgets to make a doc fit.
  Modularize instead.
- Do not embed project-specific vocabulary in TES generic code. Mechanism
  in TES, vocabulary in target.
- Do not keep more than one `docs/dist/<version>/` directory in the
  repository. The publish step prunes peers automatically. If you need a
  historical bundle, fetch it via the Git tag (`git checkout v<X> -- docs/dist/<X>`)
  or download the published release artifact; do not re-add it to the
  working tree on `main`.
