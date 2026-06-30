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
Decision NOT taken here — this is the map that precedes the decision.

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

## Anchor citations

- `scripts/tes_init.py:2474-2528` — status computed from gates only; field-report BLOCKED rides in details/payload.
- `scripts/tes_install.py:1282-1303` — `aggregate_install_status` reads only apply + certification.
- `scripts/installed_certification_oracle.py:330-345` — 8 components, none checks Git.
- `scripts/field_reports.py:1125-1129` — `install_hook` BLOCKED on no `.git`.
- `scripts/canary_admission_oracle.py:127-158` — `git_admission` hard-BLOCK + strict-gate definition.
