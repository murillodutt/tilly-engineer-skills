---
tds_id: architecture.installer_tug_of_war_matrix
tds_class: architecture
status: active
consumer: maintainers, installer authors, oracle authors
source_of_truth: false
evidence_level: L2
---

# Installer Tug-of-War Matrix

Every ambiguous contract where two contrary orders collide in the TES installer:
a precondition is unmet, the install verdict reads PASS, and a downstream gate
requires exactly what install dropped. Mapped read-only against package source.

**Decision taken (2026-06-30).** The ceiling resolution is now materialized:
**TES installs, chooses, verifies and blocks Git gates when the project is
eligible; absence of proof never becomes PASS.** All 20 tugs are resolved — see
"Ceiling resolution" below. The three already-honest reference shapes (F16, F19,
F20) are preserved unchanged; the rest are repaired with red-capable oracles.

## The single structural pattern

Install/certification certifies **presence on disk**; a downstream gate (canary
admission, recognition ladder) certifies **proof in the world**. The install
aggregate is an OR-of-presence-checks and never folds in the BLOCKED /
NEEDS_EVIDENCE / UNSEALED signal it already computed one layer down. Two
truthfulness frames — *configured-on-disk* vs *proven-in-the-world* — and the
seam between them leaks green.

Severity legend: **BLOCK** = blocking-ambiguity (two live contrary orders, needs
policy) · **TRUTH** = truthfulness-gap (signal exists but is dropped/buried) ·
**COSM** = cosmetic (already resolved or harmless).

## Group 1 — Silent-skip truthfulness gaps (the grave ones)

Install reads PASS; the downstream gate hard-BLOCKs on exactly what install hid.

| # | Tug | Order A | Order B | Current behavior | Visible today? | Required downstream | Sev |
|---|-----|---------|---------|------------------|----------------|---------------------|-----|
| 1 | **git-repo-absence** | TES must never `git init` / touch adopter repo (INSTALL.md:276) | Admission REQUIRES a Git work tree, BLOCKs otherwise | no-Git installs to INSTALLED/PASS; `field_reports` BLOCKED reason never flips `status` | Buried — reason rides in payload `details`, not the verdict | `canary_admission.git_admission` hard-BLOCK | TRUTH |
| 2 | **pre-push-absence** | On no-`.git` / `hooksPath=/dev/null`, pre-push not installed; install stays advisory | Admission REQUIRES the Field Reports pre-push gate present + marker | BLOCKED swallowed like #1; `tes_field_reports_pre_push` flag is display-only, gates nothing | Cosmetic flag only | `canary_admission.prepush_evidence` BLOCK | TRUTH |
| 3 | **strict-pre-commit-absence** | TES does NOT auto-install strict pre-commit for adopters | Admission REQUIRES a strict pre-commit gate file, BLOCKs when absent | No install path ever writes pre-commit; zero signal it will be demanded | None — invisible until canary | `canary_admission.precommit_evidence` BLOCK | BLOCK |
| 4 | **artifact-hygiene-git-info-exclude** | `.git/info/exclude` hygiene only on a Git repo; no-op otherwise | `installed_certification.artifact_hygiene` is the hygiene oracle | The oracle EXCLUDES `.git` from its scan → certifies hygiene PASS over the surface docs name as hygiene | None — self-blinding | (hygiene contract itself) | TRUTH |
| 5 | **config-present-counts-as-registered** (MCP) | MCP config written = registered | Config presence is NOT host connection; only `initialize`→`tools/list` proves it | `mcp_registration` returns PASS on a substring match; real handshake oracle exists but cert path never calls it; `host_connected_not_inferred=True` hardcoded | Partial — handshake verdict exists elsewhere, unused | recognition ladder / attach_health | TRUTH |
| 6 | **sealed_claim-unknown-as-clean** | — | Missing provenance must not certify sealed | `source_tree_state == "unknown"` grouped with `"clean"` → fail-open | `release_claim_status` emitted but unknown→allowed | release seal | TRUTH |
| 7 | **dirty-tree-bundle-vs-clean-build** | — | A dirty tree is not a clean build | `build`/`publish` never read `source_tree_state`; dirty publishes PUBLISHED with a passive label | None at build | `public_bundle_oracle` / replay provenance | TRUTH |
| 8 | **sealed-claim-not-in-evaluate-status** | — | The seal verdict must reach the headline | Computed correctly but buried under `components.artifact_hygiene`; top-level aggregates only `.status` | Buried field | release seal | TRUTH |
| 9 | **pending-states-real-but-ungated** | — | Honest PENDING_*/HOST_UNOBSERVABLE must gate | The honest verdicts the code can produce are discarded at the presence-consuming cert gate | Split — exist on handshake surface, dropped at cert | attach/admission | TRUTH |
| 10 | **skipped-required-surfaces-while-scaffold** | Required-surface checks bypassed while `mesh_scaffold_only` | Those surfaces become mandatory once refined | No per-surface signal during scaffold; only the umbrella advisory | None per-surface | `project_alignment_oracle` post-align | TRUTH |

## Group 2 — Genuine two-contrary-orders (needs a product decision)

Not "add a signal" — both orders are currently true and incompatible.

| # | Tug | The live conflict | The decision you must make | Sev |
|---|-----|-------------------|----------------------------|-----|
| 11 | **vscode-excluded-from-agent-all** | `all` installs all certified consumers ↔ `all` must NOT touch VS Code | Does a VS Code adopter get a `NOT_INSTALLED (use --adapter vscode)` signal, or stay correct-by-design-and-invisible? | BLOCK |
| 12 | **active-host-only observation** | One canary session can prove at most one host | Is two-of-three `CONFIGURED_NOT_OBSERVED` a failure, a permanent expected state, or a per-host progress ledger? | BLOCK |
| 13 | **scaffold-PASS-vs-mesh-not-refined** | Install must complete green ↔ mesh is not semantically real until `/tes-align` | Is scaffold-only a PASS-with-advisory (current) or a distinct typed `PASS_SCAFFOLD` tier? | TRUTH |
| 14 | **docs-mesh-opt-in-vs-context-needs-review** | docs-mesh is opt-in (absent by default) ↔ context may be NEEDS_REVIEW | Reconcile "absent-by-design" against "context wants it" — which wins? | BLOCK |
| 15 | **unpublished-tag-vs-certified-ref** | JSON `status=STALE_SOURCE/BLOCKED` ↔ freshness CLI exit code is 0 | Is the standalone `freshness` command a query (exit 0) or a gate (non-zero on non-sealed)? A scripted caller on exit code sees the opposite of the JSON. | BLOCK |

## Group 3 — Already resolved correctly (the target shape)

Proof the meta-rule is solvable in-house; these are the reference implementations.

| # | Tug | How it is already honest |
|---|-----|--------------------------|
| 16 | **configured-but-never-fired** | install INSTALLED, but `hook_health_payload` NEEDS_EVIDENCE + cert finding + canary CONFIGURED_NOT_OBSERVED all surface it — honestly two-faced |
| 17 | **Codex trust / Cursor reopen** | `attach_health_oracle` emits PENDING_TRUST / PENDING_HOST_RESTART; `doctor` shows them. Residual: `attach()` flattens to ATTACHED + no reopen/trust line in closeout (surfacing gap). Cursor writer also omits `preToolUse` (real secondary gap) |
| 18 | **host-real vs bench-certified** | visible at the boundary; only residue: ledger rows aren't tagged fixture-vs-host-real, so a synthetic-seeded target could read NATIVE_PASS |
| 19 | **helper-drift-without-version-bump** | fails loudly RED with the exact closure path — the model citizen |
| 20 | **stale-advisory (Gap 3)** | already repaired + time-scoped with `derived_at`. The template: re-derive from this-run's payload, stamp provenance, drop on non-PASS |

(#21 `pending-states-real-but-ungated` is listed at #9; the MCP cluster contributes
3 tugs — #5, #11, #9.)

## Step 1 — Git-at-install: candidate resolutions (no pick)

Hard boundary: TES must never `git init` the adopter repo. Resolution space is
**signalling, not acting**.

| Option | What it does | Tradeoff |
|--------|--------------|----------|
| **A. Typed `NEEDS_GIT` in the verdict** | New install-cert component (or fold `field_reports` BLOCKED into `aggregate_install_status`) emitting `INSTALLED_NEEDS_GIT` / `PASS_PENDING_GIT` | Max truthfulness, reuses existing BLOCKED reason. Cost: a third verdict tier the whole closeout + exit-code consumers must learn; risks turning a deliberately Git-free install scary-non-green — collides with order A's "advisory/idempotent" |
| **B. Mandatory typed advisory + contract flag** | Mirror `mesh.scaffold_only`: a `git.absent` advisory with `derived_at`; promote `git_work_tree`/pre-push flag from display-only to a contract field read by canary + doctor; status stays PASS | Smallest diff, preserves order A exactly, matches Group-3 shape. Cost: still PASS at the headline — truthful-if-read, not truthful-if-glanced, unless the advisory is contractually required in the closeout |
| **C. Bifurcate by frame** | install reports `INSTALLED` (presence) and ALWAYS prints `canary_admission: BLOCKED (NEEDS_GIT)` from the same payload | Most honest to the real two-frame structure; generalizes to every Group-1 tug. Cost: every closeout grows an always-on readiness block; must define what "admission" means for adopters who never run a canary, or it reads as noise |

**The fork underneath all three:** is a non-Git target a *first-class supported
install mode* (→ B, advisory) or a *degraded one* (→ A/C, typed non-green)? That
policy call, not the plumbing, is the real decision.

## Step 4 — Candidate unifying rule (covers the class, not the policy)

> Every precondition a delivered surface or downstream gate depends on must, when
> unmet, produce a **typed, provenance-stamped, verdict-bearing state** that
> propagates into the install/certification headline — never a silent skip, a
> display-only flag, or a value buried one component deep. TES surfaces the unmet
> precondition; TES never performs the irreversible adopter action (git init,
> trust, reopen). Two frames (configured-on-disk vs proven-in-the-world) each
> carry their own verdict; the aggregate folds the strictest known downstream
> signal it already computed, not a weaker presence-only one.

Three enforceable clauses, each already prototyped in Group 3:
- **(i)** re-derive verdicts from this-run's payload + stamp `derived_at` (the Gap-3 fix).
- **(ii)** the aggregate folds the **min** over all component signals *including* pending/blocked, not just `.status==PASS` (fixes #6, #8, #9, #1, #2).
- **(iii)** provenance is a **measured** field, never a hardcoded constant (kills `host_connected_not_inferred=True` and `unknown==clean`).

**Covers:** all 10 Group-1 silent-skip gaps + the MCP/bundle fail-open constants.
**Does NOT cover (still your call):** the 5 Group-2 tugs — the rule guarantees no
contradiction stays *invisible*, but cannot choose whether non-Git / scaffold-only
/ two-of-three-hosts / VS Code-absence / freshness-CLI is a *supported mode*
(advisory-green) or a *deficiency* (typed non-green).

## Ceiling resolution (materialized 2026-06-30)

Ceiling: **TES installs, chooses, verifies and blocks Git gates when the project
is eligible; absence of proof never becomes PASS.** Each repair carries a
red-capable oracle. The hook-manager selection is deterministic: an existing
manager is respected; otherwise husky for Node/TS/npm-first, pre-commit when a
`.pre-commit-config.yaml` exists, lefthook as the polyglot default;
`Makefile`/CI is a fallback integrator, never the sole local proof.

| # | Decision materialized | Where | Oracle |
|---|-----------------------|-------|--------|
| 1 | Hooks attached + no Git → headline `NEEDS_GIT` (exit 0, reversible); never a green hiding field-reports BLOCKED | `tes_install.git_readiness` + `aggregate_install_status` | `tes_install.self_test` |
| 2 | Pre-push installed/verified when Git exists; the gate is a contract field (canary + doctor), not a cosmetic flag | `field_reports.install_hook` / `canary_admission.prepush_evidence` | `canary_admission`, `hook_manager_awareness` |
| 3 | **Strict pre-commit installed & verified** (manager chosen by project type), overturning the advisory-only contract | `field_reports.select_hook_manager` + `install_pre_commit_hook` | `hook_manager_awareness.validate_selection_and_precommit` |
| 4 | Artifact hygiene no longer self-blinds wholesale (scoped) | `installed_certification_oracle` hygiene scan | `installed_certification.self_test` |
| 5 | MCP registration ladder: config written → host recognizes → handshake proves; `host_connected` measured, not hardcoded | `installed_certification.mcp_registration` (real handshake) | `installed_certification.self_test` (server-no-handshake fixture) |
| 6 | Provenance `unknown` is fail-closed, never folded with `clean` | `installed_certification` hygiene seal | `installed_certification.self_test` (unknown-provenance fixture) |
| 7 | Dirty source refuses publish (`--allow-dirty` escape) | `tes_bundle.publish_public_bundle` | `tes_bundle.self_test` |
| 8 | Seal verdict reaches the certification headline (`release_claim_status`) | `installed_certification.evaluate` | `installed_certification.self_test` |
| 9 | `NEEDS_EVIDENCE` / `PENDING_*` / `HOST_UNOBSERVABLE` gate the aggregate (fold MIN over all signals) | `installed_certification.status_from_findings` | `installed_certification.self_test` |
| 10 | Scaffold required-surface emits per-surface signal, not umbrella advisory | `project_alignment_oracle.analyze` | `project_alignment_oracle.self_test` |
| 11 | `all` surfaces VS Code as `NOT_INSTALLED_BY_POLICY` (no auto-install) | `tes_install.mcp_policy_verdicts` | `install_mcp` / `tes_install` self-test |
| 12 | Per-host ledger: each host passes only on its own evidence (preserved) | `pretooluse_ceiling_evidence` per_host | `canary_admission.self_test` |
| 13 | `PASS_SCAFFOLD` typed distinct from `PASS_ALIGNED` | `project_alignment_oracle.analyze` | `project_alignment_oracle.self_test` |
| 14 | Context-demanded mesh absent → `NEEDS_REVIEW` (opt-in only without demand) | `attach_health_oracle` docs-mesh branch | `attach_health_oracle.self_test` |
| 15 | Freshness `--gate` exits non-zero on `BLOCKED`/`STALE_SOURCE`; `--query` stays 0 | `tes_bundle` freshness CLI | `tes_bundle.self_test` |
| 16 | `CONFIGURED_NOT_OBSERVED` until native proof (preserved reference shape) | `tes_install` hook health | preserved |
| 17 | Closeout surfaces `PENDING_TRUST`/`PENDING_HOST_RESTART`; Cursor writes `preToolUse` | `tes_install.attach` + `install_cursor_pretooluse_hook` | `tes_install.self_test` |
| 18 | Ledger rows tagged `host-real` vs fixture; only host-real authorizes `PASS_CEILING` | `pretooluse_ceiling_evidence` provenance | `tes_install.self_test` |
| 19 | Helper-drift fails loud RED with closure path (preserved reference shape) | `public_bundle_oracle` | preserved |
| 20 | Stale-advisory `derived_at` + per-run re-derivation (preserved reference shape) | `tes_install` advisory stamp | preserved |

Fresh-install readiness: a clean install whose only open findings are
host-pending (MCP/host not yet restarted, hooks not yet fired) or a
release-identity advisory reports the typed tier **`READY_PENDING_HOST`**
(exit 0, reversible) — neither a false PASS nor a defect.

## Anchor citations (original read-only map)

- `scripts/tes_init.py:2474-2528` — status computed from gates only; field-report BLOCKED rides in details/payload.
- `scripts/tes_install.py:1282-1303` — `aggregate_install_status` reads only apply + certification.
- `scripts/installed_certification_oracle.py:330-345` — 8 components, none checks Git.
- `scripts/field_reports.py:1125-1129` — `install_hook` BLOCKED on no `.git`.
- `scripts/canary_admission_oracle.py:127-158` — `git_admission` hard-BLOCK + strict-gate definition.

## Ceiling resolution — second wave (materialized 2026-06-30, findings 21-36)

A second audit surfaced 16 more tugs (the critical one: canary admission
validated the Field Reports pre-push with the wrong predicate). All resolved to
the same ceiling — absence of proof never PASS; query and gate are distinct
exit-code modes; each claim proven by its own predicate. A final adversarial
ceiling audit confirmed 36/36 findings RESOLVED with a red-capable oracle each.

| # | Decision materialized | Where | Oracle |
|---|-----------------------|-------|--------|
| 21 | `field_reports_prepush_drain` (HOOK_MARKER, advisory) separated from `project_prepush_gate` (gate-pre-git, blocking); neither marker proves the other | `canary_admission.prepush_evidence` | `canary_admission.self_test` (drain-only / gate-only) |
| 22 | Strict pre-commit proven by executability (`os.access X_OK`) + a gate token in CODE (comments stripped), never a substring | `canary_admission.precommit_evidence` | `canary_admission.self_test` (comment-stub / non-exec) |
| 23 | hook-health `--gate` exits non-zero on `NEEDS_EVIDENCE`; `--query` (default) stays 0 | `tes_install` hook-health CLI | `tes_install.self_test` |
| 24 | `certification_tier` distinguishes `PASS_BASIC` from `PASS_CEILING`; `ceiling_evidence` surfaced (INFO, non-gating on fresh install) | `installed_certification.evaluate` | `installed_certification.self_test` |
| 25 | Field Reports pre-push is an advisory non-blocking drain; admission gates on the drain, the project gate is observational | `canary_admission.git_admission` | `canary_admission.self_test` (gate-only BLOCKS) |
| 26 | Expected MCP derived from the install lock — lock attached MCP but no config = FAIL, never silent PASS | `installed_certification.mcp_registration` | `installed_certification.self_test` (attached-but-absent) |
| 27 | `attach`/`detach` transact the install lock + recertify (honor `--dry-run`, additive merge, capsule preserved) | `tes_install.transact_lock_surface` | `tes_install.self_test` (F27 lock-transaction) |
| 28 | `doctor` separates `report_status` (capsule) from `readiness_status` (folds worst attachment); `PENDING_*`/`DEGRADED` never hidden | `tes_install.doctor` + `_fold_attachment_readiness` | `tes_install.self_test` (F28 fold) |
| 29 | `public_bundle_oracle` validates `tes-public.structure.yml` `bundle_sha256`; `tds_surface` dist-missing is a BLOCKER (caught a real stale SHA) | `public_bundle_oracle` + `tds_surface_oracle` | live `public_bundle_oracle` run |
| 30 | `tes-update --gate`/`status` exits non-zero on drift/`AVAILABLE`; `plan` stays query (exit 0) | `tes_update` CLI | `tes_update.self_test` |
| 31 | Version gate scans all `scripts/**.py` `VERSION` constants with an independent-version allowlist | `validate_reference_package` | the scan itself (planted-stale RED) |
| 32 | `tes_bump --governance-check` + `--self-test` sealed into `commit:closure` | `package.json` closure chain | closure chain |
| 33 | `pretooluse_evidence_oracle --self-test` sealed into `commit:closure` | `package.json` closure chain | closure chain |
| 34 | `hook_manager_awareness` + `runtime_topology` self-tests sealed into `commit:closure` | `package.json` closure chain | closure chain |
| 35 | `tes_bundle` per-subcommand `--gate` exits non-zero on `BLOCKED`/`STALE_SOURCE`/`NEEDS_REVIEW`; default query stays 0 | `tes_bundle` shared exit map | `tes_bundle.self_test` |
| 36 | `context_core_status=UNKNOWN` composes `PENDING`/`NEEDS_EVIDENCE`, never `READY`; ready fixtures prove the core | `tes_update.post_layer_zero_final_probe` | `tes_update.self_test` (UNKNOWN ≠ READY) |
