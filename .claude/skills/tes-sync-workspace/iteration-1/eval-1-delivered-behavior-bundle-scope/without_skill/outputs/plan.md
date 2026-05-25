# TES Sync Plan — Closeout for `project_alignment_oracle` new gate

Status: PLAN ONLY (no writes will be executed).
Repo: `/Users/murillo/Dev/tilly-engineer-skills`
Branch: `main` (clean working tree at moment of inspection; the planned scope below presumes the diff scope you described).
Current package version: `0.3.125` (from `package.json`, `bin/tes.js` `TES_VERSION`, `scripts/project_alignment_oracle.py` `VERSION`).
Latest tag: `v0.3.125`.
Governance check (per your run): `NEEDS_VERSION_DECISION`.

The plan below follows `docs/governance/SYNC-AUDIT-CHECKLIST.md` end-to-end and the
`release_identity` block in `AGENTS.md`. Nothing here is run yet — these are the
exact commands and decisions I will execute on your go.

---

## 0. Diff scope read (what the change actually is)

Files you reported as modified:

1. `scripts/project_alignment_oracle.py` — new gate (the delivered behavior).
2. `src/adapters/codex/skills/tes-align/SKILL.md` — Codex skill body.
3. `src/adapters/claude/skills/tes-align/SKILL.md` — Claude skill body.
4. `docs/mesh/TES-ALIGN-SEMANTIC-RESIDUE.md` — the mesh source-of-truth doc.
5. `docs/evidence/reports/2026/05/26/tes-align/<run-id>/REPORT.md` — retained evidence packet for the change.

One-sentence delivered-behavior summary I will use:
> `project_alignment_oracle` gains a new gate (see retained evidence packet) and
> the `tes-align` skill bodies on both adapters now reference it, with
> `docs/mesh/TES-ALIGN-SEMANTIC-RESIDUE.md` as the source-of-truth doc.

This crosses the `release_identity` threshold: oracle behavior change + adapter
skill body change + governed mesh doc update. That is the **default rule** in
`AGENTS.md`: bump the patch version unless you (Murillo) explicitly defer.

---

## 1. Bump scope classification (the decision the checklist forces)

The checklist offers three scopes. My classification with rationale:

| Scope | Trigger | Applies here? |
|---|---|---|
| Source-only sync | hardening / oracle / skill body that does not change installer behavior | Plausible — oracle gate + skill body |
| Source + public refs + bundle | installer refs / `INSTALL.md` / `COMMAND-TRIGGERS.md` / `bin/tes.js` / i18n / HTML need to move | Only if the new gate is adopter-visible through the installed skill surface |
| Defer bump | explicit Murillo exception | Available, must be recorded in closeout |

**My recommendation:** `Source + public refs + bundle`. Reasoning:

- `tes-align` SKILL.md on both adapters changed — that ships through the
  public bundle (`scripts/tes_bundle.py publish`), so adopters fetching
  `#v<new>` get different skill text. That is adopter-visible behavior.
- The new oracle gate ships in `scripts/project_alignment_oracle.py`, which is
  in `REQUIRED_PATHS` of `scripts/validate_reference_package.py` and carries a
  `VERSION = "0.3.125"` constant. A delivered behavior change with a versioned
  constant is the canonical trigger for a patch bump.
- `docs/mesh/TES-ALIGN-SEMANTIC-RESIDUE.md` is a governed mesh doc — its
  `sources_verified_on` and `tver` need to be reconciled with the change.

Target version: **`0.3.126`** (patch bump from `0.3.125`).

If you say "defer," I will instead record the deferral in the closeout under
the `release_identity` exception rule, commit source-only, skip the bundle and
the tag, and explicitly mark the package as **not** sealed by version identity
for this change. I will not move the tag or publish under those conditions.

---

## 2. Pre-flight (read-only commands I will run before any write)

```bash
git -C /Users/murillo/Dev/tilly-engineer-skills status -sb
git -C /Users/murillo/Dev/tilly-engineer-skills diff --stat
git -C /Users/murillo/Dev/tilly-engineer-skills diff scripts/project_alignment_oracle.py
git -C /Users/murillo/Dev/tilly-engineer-skills diff src/adapters/codex/skills/tes-align/SKILL.md
git -C /Users/murillo/Dev/tilly-engineer-skills diff src/adapters/claude/skills/tes-align/SKILL.md
git -C /Users/murillo/Dev/tilly-engineer-skills diff docs/mesh/TES-ALIGN-SEMANTIC-RESIDUE.md
ls docs/evidence/reports/2026/05/26/tes-align/
```

Pre-flight checks (from `SYNC-AUDIT-CHECKLIST.md` "Pre-flight"):

- [ ] `git status -sb` clean except the 5 expected files. Watch for surprise
      files under `.tes/`, `docs/dist/`, `node_modules/`. Right now I also see
      untracked `.agents/skills/tes-sync/` and `.claude/skills/tes-sync/` —
      these are workspace artifacts of the current skill iteration and must
      **not** be staged in this commit. Confirm with you before touching.
- [ ] Confirm `docs/mesh/TES-ALIGN-SEMANTIC-RESIDUE.md` has
      `sources_verified_on` within `source_refresh_interval_days`. If the doc
      was used as construction truth this session, refresh that date as part
      of the source change.
- [ ] Read `AGENTS.md` `release_identity` block (already inspected, lines
      150–175). Confirm scope per Section 1.

---

## 3. Source change verification

Per checklist "Source change":

- [ ] Edits are surgical and trace to the new gate. I will diff each file
      against `origin/main`.
- [ ] No project-specific vocabulary leaked into generic TES code (the
      mechanism-in-TES, vocabulary-in-target rule).
- [ ] New governed doc lives under `docs/mesh/**` (TES-ALIGN-SEMANTIC-RESIDUE
      already does). No scattered adapter docs.
- [ ] `validate_doc_size.py` would still pass for the touched doc. Confirm
      before commit.
- [ ] **Adapter parity preserved**: both Codex and Claude `tes-align/SKILL.md`
      moved. Cursor is not touched (Cursor does not own the equivalent routing
      surface for tes-align — no fake parity).
- [ ] Each touched skill has a `CONTRACT-HISTORY.md` row dated today citing
      the evidence packet path.

If `CONTRACT-HISTORY.md` rows are missing, I will add them before commit
(treat as part of the source change, not a separate commit).

---

## 4. Oracle / self-test (the gate's own proof)

```bash
python3 scripts/project_alignment_oracle.py --self-test
```

Required outcomes:

- [ ] PASS overall.
- [ ] New gate has at least one **adversarial fixture** — i.e. a fixture
      where the old gate would have falsely returned PASS and the new gate
      now returns FAIL or NEEDS_REVIEW.
- [ ] Allowlist / historical-evidence fixture proves the new gate does not
      over-fire on retained timelines.
- [ ] If the gate uses literal matching, a word-boundary regression fixture
      is present (the `<short-literal>` vs `do<short-literal>` trap).
- [ ] A malformed-input fixture returns a clear `code` rather than a stack
      trace.

If any of these fixtures are missing, I will add them to the oracle as part
of the source change before continuing.

---

## 5. Indexing (correlation rule)

Read-only inspection first:

```bash
grep -n "TES-ALIGN-SEMANTIC-RESIDUE" docs/tds/DOCS-INDEX.yml docs/INDEX.md
grep -n "project_alignment_oracle" scripts/validate_reference_package.py
ls docs/evidence/reports/2026/05/26/tes-align/<run-id>/
grep -n "tes-align" docs/evidence/current/CLAIMS.md 2>/dev/null
```

- [ ] `docs/mesh/TES-ALIGN-SEMANTIC-RESIDUE.md` indexed in
      `docs/tds/DOCS-INDEX.yml` and shown in `docs/INDEX.md` map.
- [ ] If the doc is delivered behavior (a governed source of truth), it must
      be in `REQUIRED_PATHS` of `scripts/validate_reference_package.py`.
- [ ] `scripts/project_alignment_oracle.py` already in `REQUIRED_PATHS`;
      confirm its `VERSION` constant matches the target after bump.
- [ ] The retained evidence packet
      `docs/evidence/reports/2026/05/26/tes-align/<run-id>/REPORT.md` is
      indexed in `docs/tds/DOCS-INDEX.yml` (retained packets are indexed
      under the `evidence` class).
- [ ] If the change creates a current-evidence claim, add a row to
      `docs/evidence/current/CLAIMS.md` with proof, boundary, retention.

Any missing index entry gets added now, before any version surfaces move.

---

## 6. Doc size

```bash
python3 scripts/validate_doc_size.py
```

- [ ] PASS.
- [ ] If `docs/mesh/TES-ALIGN-SEMANTIC-RESIDUE.md` crossed 500 lines after
      the edits, extract a focused reference doc under `docs/mesh/**` and
      cross-link. **Do not raise the budget.**

---

## 7. Version governance decision (the verdict you already saw)

```bash
python3 scripts/tes_bump.py --governance-check
```

Already returned `NEEDS_VERSION_DECISION`. Per Section 1 the chosen scope is
**Source + public refs + bundle**, target `0.3.126`. Recording the decision
explicitly here is part of the audit trail.

---

## 8. Identity bump 0.3.125 → 0.3.126 (the coordinated set)

Every file listed in the checklist "Identity bump" section must move together.
This is the order I will write them in:

Core identity:

- [ ] `package.json` `"version": "0.3.125"` → `"0.3.126"`.
- [ ] `bin/tes.js` `TES_VERSION` constant → `"0.3.126"`.
- [ ] `README.md` version shield badge → `0.3.126`.
- [ ] `docs/tds/DOCS-INDEX.yml` header `version: 0.3.126`.
- [ ] `docs/INDEX.md` `Public installer bundle` row → `v0.3.126`.
- [ ] `docs/adapters/CODEX.md` `Project version` → `0.3.126`.
- [ ] `docs/roadmap/README.md` baseline line → `0.3.126`.
- [ ] `docs/roadmap/RC1-READINESS-ROADMAP.md` `Package version` row → `0.3.126`.

Scripts:

- [ ] Every `scripts/**.py` with `VERSION = "0.3.125"` → `"0.3.126"`. I will
      enumerate with:
      `grep -rn 'VERSION\s*=\s*"0\.3\.125"' scripts/`
      and update each match.
- [ ] `scripts/validate_reference_package.py` `REQUIRED_PATHS` entries that
      reference `docs/dist/0.3.125/...` → `docs/dist/0.3.126/...`.
- [ ] `scripts/project_alignment_oracle.py` any fixture frontmatter with
      `tes_version: 0.3.125` → `0.3.126` (and any other oracle fixture that
      embeds the version).
- [ ] `scripts/tes_npx_oracle.py` `--github-ref` help-text example → updated.

Plugin manifests:

- [ ] `src/adapters/codex/plugin/plugin.json` and `marketplace.json` → `0.3.126`.
- [ ] `src/adapters/claude/plugin/plugin.json` and `marketplace.json` → `0.3.126`.

Public refs (because bump scope is source + public refs + bundle):

- [ ] `docs/install/INSTALL.md` install commands (`#v0.3.126`).
- [ ] `docs/install/COMMAND-TRIGGERS.md` install row → `v0.3.126`.
- [ ] `docs/llms.txt` install line → `v0.3.126`.
- [ ] `docs/i18n/tes-public.content.json`:
      - `release_meta`, `manual_meta`, `version`,
      - every code block with `#v0.3.125`,
      - all three languages (verify exhaustively, do not assume parity).
- [ ] `docs/i18n/tes-public.structure.yml`:
      - `bundle_index` reference,
      - `bundle_sha256` placeholder (will be replaced after bundle rebuild).

Sanity scan after writing (still part of this phase):

```bash
grep -rn "0\.3\.125" --include="*.py" --include="*.json" --include="*.md" --include="*.yml" \
  | grep -v "docs/dist/" \
  | grep -v "docs/evidence/" \
  | grep -v "RELEVANT-FINDINGS-CHANGELOG"
```

Every remaining hit must be either:
(a) a deliberate historical reference, or
(b) a miss I have to fix now.
No silent leftovers.

---

## 9. Public bundle (only because scope = bundle)

```bash
python3 scripts/tes_bundle.py publish --adapter all
ls docs/dist/
```

- [ ] `docs/dist/0.3.126/` exists with `index.json`, the zip, and the
      `.sha256` sidecar.
- [ ] **Single-current-dist policy**: `docs/dist/` contains exactly
      `docs/dist/0.3.126/` — the prior `docs/dist/0.3.125/` is pruned by
      `tes_bundle.py publish` automatically. If it is not pruned, the policy
      regressed and I stop and flag it. Historical bundles remain reachable
      via Git tags and GitHub releases.
- [ ] Capture the sha printed by `tes_bundle.py` and confirm it matches the
      `.sha256` sidecar.
- [ ] Hand-update `docs/i18n/tes-public.structure.yml` `bundle_sha256` with
      that sha (this is the trap that broke `tds-surface` previously).
- [ ] Regenerate public HTML:
      `python3 scripts/build_public_docs.py`
- [ ] Verify no stale version in HTML:
      `grep -c "0\.3\.125" docs/index.html docs/install/USER-MANUAL.html`
      must return `0` for both files.

---

## 10. Final gate (`npm run commit:check`)

```bash
git -C /Users/murillo/Dev/tilly-engineer-skills add -A
npm run commit:check
```

**Important about `git add -A`:** before running it, I will explicitly confirm
with you that the two untracked workspace folders
(`.agents/skills/tes-sync/` and `.claude/skills/tes-sync/`) should be excluded.
If they should be excluded, I will either:
(a) `git add` only the specific paths in the diff scope plus the new bundle
   files under `docs/dist/0.3.126/`, or
(b) confirm those workspace folders are covered by `.gitignore`.

Expected `commit:check` tag set (from the checklist, 33 tags):

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

Traps I expect to handle in this run:

- `tes-reference FAIL: untracked package path` → `git add` the missing file.
- `tds-surface BLOCKER: bundle_sha_mismatch` → copy published sha into
  `structure.yml`, rerun `build_public_docs.py`.
- `tds FAIL: missing index entry` → add to `docs/tds/DOCS-INDEX.yml`.
- `doc-size FAIL` → extract / modularize, do not raise the budget.
- `project-alignment FAIL` → likely the new gate or its fixtures; fix in
  source.

Then re-verify governance:

```bash
python3 scripts/tes_bump.py --governance-check
```

Must return: `Version governance: PASS — version bump surfaces are synchronized`.

Do **not** proceed to commit until both `commit:check` is green and
`--governance-check` is PASS.

---

## 11. Commit

Only after green:

```bash
git -C /Users/murillo/Dev/tilly-engineer-skills diff --cached --stat | tail -3
```

Confirm:

- [ ] File count matches the coordinated set (source 5 files + bump surfaces
      ~15 files + bundle dir + i18n + HTML). Order-of-magnitude check, not
      exact count.
- [ ] No surprise binary files outside `docs/dist/0.3.126/`.

Commit message template (HEREDOC, exactly per the standard footer):

```
feat(tes-align): add <gate-name> gate to project_alignment_oracle; release 0.3.126

What changed: project_alignment_oracle gains a new <gate-name> gate. The
tes-align skill body on Codex and Claude adapters now references the gate
and docs/mesh/TES-ALIGN-SEMANTIC-RESIDUE.md is updated as the source of
truth.

Why: <narrative of the false-green / retired claim that motivated the gate>.

Evidence: docs/evidence/reports/2026/05/26/tes-align/<run-id>/REPORT.md

Release identity: 0.3.125 -> 0.3.126 (source + public refs + bundle).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
```

I will fill `<gate-name>`, `<run-id>`, and the "Why" narrative from the actual
diff and the retained evidence packet before composing the message. I will
**not** amend; if a pre-commit hook fails, I will fix the issue, re-stage, and
create a new commit (per the `Git Safety Protocol` and the checklist
"Commit" section).

After commit:

```bash
git -C /Users/murillo/Dev/tilly-engineer-skills status
git -C /Users/murillo/Dev/tilly-engineer-skills log -1 --stat
```

Must show clean tree and the expected file set.

---

## 12. Push

```bash
git -C /Users/murillo/Dev/tilly-engineer-skills status -sb
# expect: ## main...origin/main [ahead 1]
git -C /Users/murillo/Dev/tilly-engineer-skills push origin main
git -C /Users/murillo/Dev/tilly-engineer-skills status -sb
# expect: ## main...origin/main (no ahead)
```

No `--force`, no `--no-verify`.

---

## 13. Tag (because bump publishes a new public ref)

This is the trap area. Pre-checks:

```bash
git -C /Users/murillo/Dev/tilly-engineer-skills tag -l v0.3.126
git -C /Users/murillo/Dev/tilly-engineer-skills ls-remote --tags origin v0.3.126
```

Branches:

- **Tag does not exist locally or remotely** (expected): proceed.
- **Tag exists** (stale from an earlier attempt):
  - Run `git rev-list -n 1 v0.3.126` and compare to `git rev-parse HEAD`.
  - If they match: tag is correct, just push.
  - If they differ: I **stop and ask for explicit authorization** before
    deleting the stale tag locally and on the remote. The checklist "Locks"
    forbid me from moving a public tag without that confirmation. If
    authorized:
    ```bash
    git tag -d v0.3.126
    git push origin :refs/tags/v0.3.126
    ```

Create and push the tag (annotated):

```bash
git -C /Users/murillo/Dev/tilly-engineer-skills tag -a v0.3.126 \
  -m "tes-align: add <gate-name> gate; evidence docs/evidence/reports/2026/05/26/tes-align/<run-id>/REPORT.md"
git -C /Users/murillo/Dev/tilly-engineer-skills rev-list -n 1 v0.3.126
git -C /Users/murillo/Dev/tilly-engineer-skills rev-parse HEAD
# both must match
git -C /Users/murillo/Dev/tilly-engineer-skills push origin v0.3.126
git -C /Users/murillo/Dev/tilly-engineer-skills ls-remote --tags origin v0.3.126^{}
# must resolve to the HEAD commit
```

---

## 14. Release certification

```bash
npm run release:check
```

Must return:

- `status: PASS`
- `classification: certified_local`
- `resolved_commit` equals current HEAD.

If any of those drift, the tag did not propagate cleanly. I will stop and
diagnose rather than retry blindly.

---

## 15. Closeout report (recorded after success)

Per the checklist "Closeout report":

- [ ] Final claim sentence: "PASS — `project_alignment_oracle` gained the
      `<gate-name>` gate; tes-align Codex and Claude skill bodies updated;
      released as 0.3.126 with public bundle and certified tag."
- [ ] Commit hash and tag (`v0.3.126`).
- [ ] Retained evidence packet path:
      `docs/evidence/reports/2026/05/26/tes-align/<run-id>/REPORT.md`.
- [ ] Limits and remaining follow-ups (e.g., target-project canary still
      owes a real rerun against the hardened oracle, if applicable).
- [ ] Any deferred bump exception → **none** in this plan; bump executed.

---

## 16. Locks I will honor

From the checklist "Locks" section — repeating explicitly so you can hold me
to them:

- I will **not** push without `npm run commit:check` PASS.
- I will **not** move the `v0.3.126` tag (or any public tag) without your
  explicit go if it already exists pointing somewhere other than HEAD.
- I will **not** hand-edit `docs/dist/0.3.126/**`. Always regenerated by
  `scripts/tes_bundle.py publish`.
- I will **not** hand-edit `docs/index.html` or
  `docs/install/USER-MANUAL.html`. Always regenerated by
  `scripts/build_public_docs.py`.
- I will **not** raise `validate_doc_size.py` budgets to fit a doc.
- I will **not** embed project-specific vocabulary in generic TES code.
- I will **not** keep more than one `docs/dist/<version>/` directory.
- I will **not** skip hooks (`--no-verify`) or amend.
- I will **not** stage the workspace folders `.agents/skills/tes-sync/` or
  `.claude/skills/tes-sync/` in this commit unless you tell me to.

---

## 17. Decision points where I will pause and ask

I will stop and confirm with you before executing the write path at each of
these points:

1. **Bump scope** — confirm "source + public refs + bundle" with target
   `0.3.126`, or override (source-only / defer).
2. **Workspace folders** — confirm `.agents/skills/tes-sync/` and
   `.claude/skills/tes-sync/` are **not** part of this commit (and ideally
   ignored).
3. **`CONTRACT-HISTORY.md` rows** — confirm they are part of this commit
   (treated as part of the source change), not a follow-up.
4. **Missing adversarial fixture** — if the oracle does not already have an
   adversarial fixture for the new gate, confirm that adding it is part of
   this commit before bumping.
5. **Stale `v0.3.126` tag** — if it already exists and points away from
   HEAD, confirm explicit authorization to delete it locally and remotely
   before recreating it.
6. **Sanity-scan leftovers** — show you any remaining `0.3.125` references
   from the grep scan that are not in `docs/dist/`, `docs/evidence/`, or
   `RELEVANT-FINDINGS-CHANGELOG`, and decide together whether each is
   deliberate history or a miss.

I will not run any write command until you say go.

---

## Single-line summary

Bump `0.3.125 → 0.3.126` (source + public refs + bundle), move the 20+
coordinated identity surfaces, regenerate the public bundle and HTML, run
`npm run commit:check` to green plus `tes_bump.py --governance-check` to PASS,
commit with the standard footer and evidence path, push `main`, create and
push annotated tag `v0.3.126`, and certify with `npm run release:check`.
