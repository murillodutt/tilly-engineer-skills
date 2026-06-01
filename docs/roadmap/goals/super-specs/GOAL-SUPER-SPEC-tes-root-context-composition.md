---
tds_id: roadmap.goal_super_spec_tes_root_context_composition
tds_class: roadmap
status: active
consumer: maintainers, installer authors, adapter authors, oracle authors, release reviewers, and execution agents
source_of_truth: false
evidence_level: L1
tver: 0.1.0
---

# GOAL Super SPEC: TES Root Context Composition

Status: active planning artifact; no delivered behavior yet.

Capability: make TES root-context installation and update always advance the
TES core while preserving project-owned context, across first install,
postinstall hooks, NPX/BunX updates, adapter refresh, and `/tes-update`.

Canonical artifact:
`docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-tes-root-context-composition.md`

## Mantra Gate Snapshot

| Field | Decision |
|-------|----------|
| VERIFY | Reviewed the target-project report where `context_core_drift` led toward destructive root overwrite, `scripts/tes_update.py`, `scripts/root_context.py`, `scripts/tes_bundle.py`, `scripts/tes_install.py`, `scripts/install_adapter.py`, current Super SPEC precedents, and maintainer boundaries. |
| SCOPE | Create one governed Super SPEC and index it. No runtime code, package version, bundle rebuild, release, tag, push, publish, cloud, marketplace, or target-project write is authorized by this SPEC alone. |
| BEST_PATH | Define a shared root-context composition contract used by installer, bundle apply, postinstall, hook, NPX/BunX update, and `/tes-update`, instead of patching only the planner or accepting whole-file overwrite. |
| DOCUMENT | This Super SPEC plus roadmap/index/TDS correlations and future evidence reports produced during implementation. |
| ORACLE | Planning closeout uses TDS, doc-size, reference-graph, private-vocabulary, and diff-check gates. Implementation must add failing fixtures proving core staleness and overlay loss before repair. |
| RESOLVE | Root context must become composed state: TES owns the core block; the project owns the overlay. Both are mandatory. |
| STATUS | GO for governed implementation planning. |

## Problem

TES currently treats root-context files as whole files in several write and
planning paths:

- `AGENTS.md`
- `CLAUDE.md`
- `CURSOR.md`
- `.cursor/rules/tes-guidelines.mdc`
- related adapter root/rule files when they carry active TES routing

That creates two unacceptable product failures:

1. A project-preserving install or update can leave the TES core stale, so new
   triggers, locks, safety text, or runtime capability routing do not reach the
   adopter.
2. A clean runtime refresh can overwrite project-owned governance, so local
   context, constraints, architecture decisions, and operating rules are lost
   or pushed into backup-only evidence.

Both outcomes violate the product contract. TES core updates must not be
optional, and user/project context must not be lossy.

The observed target-project case exposed the planning symptom: SHA drift of
the whole root file was treated like adapter/runtime drift. The planner
recommended `adapter-config`, which named root bootloader writes that could
remove project governance. The deeper product bug is the whole-file ownership
model, not only the `/tes-update` status wording.

## Goal

After this Super SPEC is implemented, every TES path that writes or certifies
root context must satisfy:

```text
current TES core + preserved project overlay = composed root context
```

Required invariants:

- TES core is current after install/update.
- Project overlay is preserved after install/update.
- Whole-file overwrite of root context is prohibited by default.
- Backup remains mandatory but is not the preservation mechanism.
- SHA drift of the whole file is not a destructive repair signal.
- Core-block drift is a repair signal.
- Overlay loss is a hard failure.

## Non-Objectives

- Do not freeze target root files by editing `.tes/manifest.json`.
- Do not preserve stale TES core merely because the project has custom root
  governance.
- Do not move private target vocabulary, project names, domain decisions,
  filesystem paths, remotes, commits, or raw target logs into TES source,
  docs, fixtures, evidence, commits, tags, or release notes.
- Do not patch installed mirrors such as `.tes/bin/**`, `.agents/skills/**`,
  `.claude/skills/**`, or target root files as the source of truth.
- Do not rely on LLM judgment to hand-merge root context at install time.
- Do not weaken command-trigger, materialization, or installed certification
  oracles to hide composition failures.
- Do not add cloud, marketplace, global config, remote write, or external
  service behavior.

## Product Contract

Root context has two mandatory layers.

| Layer | Owner | Rule |
|-------|-------|------|
| TES Core | TES package | Versioned, generated from adapter source, updated on every install/update path. |
| Project Overlay | Target project | Preserved, migrated to `docs/agents/**` when useful, never discarded silently. |

The install mode names remain user-facing, but root context ignores their old
whole-file implications:

| Mode | Root-Context Meaning |
|------|----------------------|
| `preserve` | Update TES core and preserve overlay. |
| `clean-runtime` | Recompose from current TES core and preserved overlay. |
| `/tes-update` adapter refresh | Recompose from current TES core and preserved overlay. |
| first-session hook/postinstall | Certify composition; repair only through the composer or report `NEEDS_REVIEW`. |
| NPX/BunX update | Use the same composer as local update; do not bypass it. |

## Composition Markers

The implementation should use explicit block markers or an equivalent
machine-readable boundary. Proposed marker shape:

```md
<!-- TES:CORE BEGIN version=0.3.x sha256=<core-sha> adapter=<adapter> -->
...
<!-- TES:CORE END -->

<!-- TES:PROJECT-OVERLAY BEGIN source=docs/agents/... -->
...
<!-- TES:PROJECT-OVERLAY END -->
```

Rules:

- Manifest parity checks compare the TES core block, not the whole file.
- Whole-file SHA can be retained as evidence only.
- Existing unmarked files are legacy input and must be migrated by fixture-backed
  heuristics before any write.
- Unknown non-core content becomes overlay candidate, not garbage.
- Conflicts close as `NEEDS_REVIEW_CONFLICT`, with no overwrite.

## Required Status Semantics

| Status | Required Meaning |
|--------|------------------|
| `PASS` | Core is current, overlay is preserved, and oracles agree for the claimed route. |
| `COMPOSED` | A root file was written by the composer from current core plus preserved overlay. |
| `CORE_STALE` | TES core block is missing or behind the staged/current package. |
| `OVERLAY_PRESENT` | Project-owned context exists and is protected from whole-file overwrite. |
| `OVERLAY_PRESERVED` | Overlay before and after composition matches the preservation contract. |
| `NEEDS_REVIEW_CONFLICT` | Existing content cannot be safely classified or merged; no overwrite occurred. |
| `BLOCKED_OVERLAY_UNRECOVERABLE` | Required overlay source is missing from both active root and backup/evidence. |

`DRIFT` remains valid for runtime trigger or helper parity failures. It must not
be the final word for project-owned root context.

## Implementation Units

| Unit | Owned Surfaces | Required Behavior | Required Oracle |
|------|----------------|-------------------|-----------------|
| SPEC-000 Reproducer And Boundary | `scripts/tes_update.py` fixtures, `scripts/root_context.py` fixtures, neutral target fixtures | Reproduce both failures: stale core preserved by install/update and project overlay lost by clean root overwrite. Keep target identity generic. | New failing fixture before repair; `python3 scripts/private_vocabulary_oracle.py`; `git diff --check`. |
| SPEC-001 Root Context Composer | `scripts/root_context.py` or a focused shared composer module | Detect core, extract overlay, compose root, preserve line endings where practical, and fail closed on unclassified conflicts. | Composer self-test covering create, preserve, clean-runtime, conflict, and idempotent recomposition. |
| SPEC-002 Bundle Apply Integration | `scripts/tes_bundle.py`, bundle manifest handling | `apply_staged_bundle` routes root-context entries through the composer in both `preserve` and `clean-runtime`; whole-file copy is prohibited for root context by default. | `python3 scripts/tes_bundle.py --self-test`; fixture proving core updates while overlay survives. |
| SPEC-003 Installer And NPX Path Integration | `scripts/tes_install.py`, `bin/tes.js`, public install docs if needed | First install and NPX/BunX update use the composer for root files; `--mode preserve` still updates core; `--mode clean-runtime` still preserves overlay. | `python3 scripts/tes_install.py --self-test`; `python3 scripts/tes_npx_oracle.py --self-test`; install fixture with preexisting root governance. |
| SPEC-004 Hook And Postinstall Certification | `scripts/tes_install.py`, postinstall run records, installed certification if needed | Hook/postinstall certify `core_current` and `overlay_preserved`; they never call setup complete when root composition is stale or lossy. | Postinstall fixture proving run record includes composition status and blocks lossy repair. |
| SPEC-005 Update Planner Semantics | `scripts/tes_update.py`, `/tes-update` skills if user-visible behavior changes | Planner reports `CORE_STALE` separately from `OVERLAY_PRESENT`; recommends composition repair instead of adapter-config overwrite when runtime triggers are PASS. | `python3 scripts/tes_update.py --self-test`; fixture where custom root context no longer recommends destructive refresh. |
| SPEC-006 Manifest Contract | `scripts/tes_bundle.py`, `scripts/tes_update.py`, validators | Manifest records core-block hash and composed-file evidence separately. Installed manifest upgrades safely from whole-file SHA entries. | Manifest migration self-test; reference package validation. |
| SPEC-007 Legacy Migration | composer module, `scripts/root_context.py`, recovery evidence | Existing unmarked root files are split into TES-like core candidates and project overlay; overlay may be copied or referenced in `docs/agents/**` with evidence. | Fixture for legacy root with TES text plus project governance; no content loss; evidence report created. |
| SPEC-008 Adapter Parity And Materialization | `src/adapters/**`, `scripts/materialize_adapter.py`, adapter oracles | Adapter source remains the canonical TES core generator across Codex, Claude, and Cursor. Materialized targets include markers or equivalent metadata. | `python3 scripts/materialize_adapter.py all --check`; `python3 scripts/platform_surface_oracle.py --self-test`. |
| SPEC-009 Doctor And Recovery UX | `src/adapters/*/skills/tes-doctor/SKILL.md`, `docs/install/AGENT-MANUAL.md`, repair docs | `/tes-doctor` explains stale core, preserved overlay, composition conflict, and recovery commands without instructing manual whole-file overwrite. | Doctor route fixture or focused text oracle; command-trigger oracle if skills change. |
| SPEC-010 Post-Correction Analysis Packet | evidence docs, Field Reports payload shaping if touched | Every repaired install/update run emits a compact analysis: before core SHA, after core SHA, overlay preservation proof, write route, conflicts, and rollback pointer. | Field Reports/self-test or evidence fixture proving packet fields exist and omit private identifiers. |
| SPEC-011 Canary Replay | private canary process kept outside TES source; neutral fixture in package | Replay the original failure class on a neutral fixture and at least one private target canary without copying private details into TES. | Neutral fixture PASS; private canary summarized generically as local evidence outside tracked content. |
| SPEC-012 Release Identity And Sync | `package.json`, version constants, public bundle, docs indexes, release gates when authorized | Delivered composer behavior receives patch bump, public bundle rebuild, tag, release check, and Pages check before public claim. | `npm run commit:check`; `npm run release:check`; `public_pages_oracle.py --version <new>` after authorized sync. |

## P0 Cut: No-Loss Composer

The first execution wave should be small and decisive:

1. Add neutral fixtures for stale core and overlay loss.
2. Implement the shared composer with marker support.
3. Integrate the composer into `tes_bundle.py apply` for root-context entries.
4. Prove `preserve` and `clean-runtime` both update core and preserve overlay.
5. Update `tes_update.py` semantics so project overlay is not treated as
   adapter/runtime drift.

P0 is complete only when the old destructive recommendation fails its new
regression test and the composed route passes.

## P1 Cut: Installer And Postinstall Coverage

After P0:

1. Route `tes_install.py` and NPX/BunX install/update through the same composer.
2. Add hook/postinstall certification fields for core and overlay.
3. Ensure first-session setup cannot report complete when composition is stale
   or lossy.
4. Update installer docs and user-facing summaries if behavior wording changes.

P1 is complete only when first install, update install, hook, and postinstall
all exercise the same composition contract.

## P2 Cut: Legacy Migration And UX

After P1:

1. Add legacy unmarked-root migration.
2. Improve `/tes-doctor` and recovery UX for composition conflicts.
3. Add evidence packet and Field Reports actionability.
4. Replay neutral and private canary evidence.

P2 is complete only when a pre-marker target can upgrade without losing context
and without freezing TES core.

## Required Negative Checks

- No whole-file root-context overwrite unless an explicit emergency restore
  command is invoked with backup id and owner approval.
- No `PASS` when the TES core block is stale.
- No `PASS` when project overlay content is missing after composition.
- No `update_available=false` if core is stale.
- No `adapter-config` recommendation solely because project overlay differs
  from the package core.
- No loss hidden by backup-only recovery.
- No target-project vocabulary, private path, private product name, internal
  service name, branch name, remote, commit, or raw target log in TES source.
- No duplicated composer logic in install/update paths.
- No installed-target mirror patch as final repair.
- No release claim without patch-version and bundle decision.

## Required Oracles Before Implementation Closeout

Run focused gates during each unit. Before claiming convergence of this Super
SPEC, run:

```bash
python3 scripts/root_context.py --self-test
python3 scripts/tes_bundle.py --self-test
python3 scripts/tes_install.py --self-test
python3 scripts/install_smoke.py --self-test
python3 scripts/tes_update.py --self-test
python3 scripts/installed_certification_oracle.py --self-test
python3 scripts/command_trigger_oracle.py --self-test
python3 scripts/mantra_gate_adoption_oracle.py --self-test
python3 scripts/materialize_adapter.py all --check
python3 scripts/platform_surface_oracle.py --self-test
python3 scripts/tes_npx_oracle.py --self-test
python3 scripts/private_vocabulary_oracle.py
python3 scripts/validate_tds.py
python3 scripts/validate_doc_size.py
python3 scripts/validate_reference_graph.py
git diff --check
npm run commit:check
```

If implementation lands in waves, each closeout must name the narrower oracle
packet that passed and the remaining units still open.

## Post-Correction Analysis

Every implementation closeout must include:

- baseline behavior before correction;
- exact old failure reproduced by fixture;
- exact fixed route used by install/update/hook/NPX;
- root files touched and whether they were composed or skipped;
- before/after TES core hash;
- before/after overlay preservation proof;
- backup id and rollback command;
- installer/update summary classification;
- canary replay result using generic target language only;
- release identity decision.

## Certification Standard

The final claim may be `PASS` only when all are true:

- core update is mandatory and observed across all root-context write paths;
- overlay preservation is mandatory and observed across all root-context write
  paths;
- stale-core and overlay-loss fixtures fail before repair and pass after repair;
- installed-target behavior and package-source behavior agree;
- public bundle, NPX/BunX, hook/postinstall, and `/tes-update` route through the
  same composition contract;
- private canary replay is summarized without private identifiers;
- release identity is resolved.

Otherwise close as `NEEDS_REVIEW` with the exact remaining unit.

## Ready Goal Prompt

```text
/goal Execute the TES Root Context Composition Super SPEC.

Authority:
- docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-tes-root-context-composition.md
- scripts/root_context.py
- scripts/tes_bundle.py
- scripts/tes_install.py
- scripts/tes_update.py
- scripts/install_adapter.py
- docs/governance/MAINTAINER-CORRELATION-RULE.md

Objective:
Implement a shared root-context composer so TES core always updates and
project overlay is always preserved across first install, NPX/BunX update,
hook/postinstall, bundle apply, install_adapter, and /tes-update.

Start with P0 only unless the focused oracles prove P0 is complete and the
owner authorizes continuing to P1/P2 in the same run.
```
