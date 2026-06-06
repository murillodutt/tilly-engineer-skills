---
tds_id: roadmap.goal_super_spec_tes_inherited_context_canonical_source
tds_class: roadmap
status: active
consumer: maintainers, installer authors, adapter authors, skill authors, oracle authors, release reviewers, and execution agents
source_of_truth: false
evidence_level: L2
tver: 0.2.0
---

# GOAL Super SPEC: TES Inherited Context Canonical Source

Status: active execution contract, partially delivered. Derived line, dependent
on the active `GOAL-SUPER-SPEC-tes-root-context-composition.md`. This Super SPEC
assumes the core+overlay composition contract as given and delivers only the
missing layer above it: a single canonical overlay source, two asymmetric root
renderings, and a non-lossy distillation of pre-existing human context into that
source.

Execution status (as of 0.3.172): P0 (SPEC-000/001/002), P1 (SPEC-004/005/006),
and P2 SPEC-007 (installer routing) + SPEC-008 (uninstall restore) + SPEC-003
(`tes-context-distill` skill) + SPEC-009 (`/tes-doctor` recovery) are delivered
with self-test fixtures. Open: SPEC-010 (real-project canary replay).

Capability: when a project already owns rich `CLAUDE.md` / `AGENTS.md` context,
install distills that context into the existing canonical overlay
(`docs/agents/PROJECT-CONTEXT.md`), then writes thin root files that inherit it —
`CLAUDE.md` via an eager `@` import, `AGENTS.md` via an idempotent materialized
managed block — with the original archived as the non-loss oracle.

## Canonical Artifact

Canonical Super SPEC:
`docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-tes-inherited-context-canonical-source.md`

Parent contract (assumed, not redefined):
`docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-tes-root-context-composition.md`

Method authority:
`docs/mesh/RULES-FILE-ENGINEERING.md`

Related implementation surfaces:

- `docs/agents/PROJECT-CONTEXT.md` (canonical overlay source — reused, not new)
- `scripts/project_context_oracle.py` (overlay schema oracle — reused)
- `scripts/root_context.py` (composer; gains rendering + distillation routes)
- `src/adapters/claude/CLAUDE.md`, `src/adapters/codex/AGENTS.md` (thin roots)
- `src/adapters/*/skills/tes-init/SKILL.md`, `.../tes-setup/SKILL.md`
- new `src/adapters/*/skills/tes-context-distill/SKILL.md` (the heavy capability)
- new `scripts/context_distill_coverage_oracle.py` (non-loss gate)
- `scripts/tes_install.py`, `scripts/install_adapter.py` (write routes)

## Mantra Gate Snapshot

| Field | Record |
|-------|--------|
| `VERIFY` | Reviewed `RULES-FILE-ENGINEERING.md` (Codex has no `@import`; the asymmetry is permanent, not transitional), the active `root-context-composition` Super SPEC (core+overlay markers, no-loss composer, legacy migration unit SPEC-007), `project_context_oracle.py` (17 required overlay sections already governed), `tes_init.py` (`root_context_gate`, PROJECT-CONTEXT generation), `install_adapter.py` (today: `.bak` + whole-file copy of `context_governance` paths, no managed block), and `tes-setup`/`tes-init` skills (setup is a thin alias). |
| `SCOPE` | Add this Super SPEC and correlated indexes now (planning-only, version-neutral). The runtime slices it specifies are delivered behavior: new distillation skill, new coverage oracle, thin-root renderings, and managed-block materialization carry the release bump per `<release_identity>`. |
| `BEST_PATH` | Build on the parent composer instead of a parallel engine: reuse `PROJECT-CONTEXT.md` as the canonical overlay, render two asymmetric roots from it (Claude `@`-import, Codex materialized managed block), and isolate the risky distillation in a dedicated skill gated by a coverage oracle whose `.bak` is the non-loss truth. Do not reopen the parent contract. |
| `DOCUMENT` | This Super SPEC plus `docs/roadmap/README.md`, `docs/INDEX.md`, and `docs/tds/DOCS-INDEX.yml`. |
| `ORACLE` | Planning closeout: `python3 scripts/validate_tds.py`, `python3 scripts/validate_doc_size.py`, `python3 scripts/validate_reference_graph.py`, `python3 scripts/private_vocabulary_oracle.py`, `git diff --check`. Per-unit focused oracles below for each runtime slice. |
| `RESOLVE` | One canonical source, two renderings. Distillation never discards a non-trivial human claim without a recorded reason. The pre-existing root is archived and becomes the coverage oracle. No private target identifiers enter TES. |
| `STATUS` | `PROCEED` (planning artifact only; runtime units require their own gates). |

## Relationship To Parent Contract

The parent (`root-context-composition`) is assumed and reused without
redefinition. This line consumes its primitives:

| Parent primitive (reused) | This line's extension |
|---------------------------|------------------------|
| `current TES core + preserved project overlay = composed root context` | Overlay is not stored inline in the root; it lives in the canonical source `docs/agents/PROJECT-CONTEXT.md`. The root references or materializes it. |
| `TES:CORE` / `TES:PROJECT-OVERLAY` markers | Claude root carries `TES:CORE` plus an `@` pointer to the canonical source. Codex root carries `TES:CORE` plus a materialized `TES:PROJECT-OVERLAY` block (no `@` — Codex cannot import). |
| SPEC-007 Legacy Migration ("split unmarked root into core/overlay by fixture heuristics") | Upgraded from deterministic split to an agent distillation with an adversarial coverage oracle, because "optimize/organize/sanitize" requires judgment the heuristic cannot give. The heuristic split remains the deterministic floor; distillation is the opt-in second phase. |
| `OVERLAY_PRESERVED` status | Strengthened to `OVERLAY_COVERED`: every non-trivial claim in the archived original is traceable in the canonical source or explicitly marked discarded-with-reason. |

Non-redefinition lock: this Super SPEC does not change the parent's status
vocabulary, marker shape, no-whole-file-overwrite rule, or composer ownership. If
a parent invariant would have to change, that is a parent-contract amendment, not
this line.

## Product Contract

One canonical source, two renderings. Permanent, not transitional.

| Surface | Owner | Rule |
|---------|-------|------|
| `docs/agents/PROJECT-CONTEXT.md` | Target project | The single canonical overlay source. Human-editable. Already governed by `project_context_oracle.py`. All inherited context lands here. |
| `CLAUDE.md` | TES core + pointer | Thin `TES:CORE` block plus `@docs/agents/PROJECT-CONTEXT.md` (eager import, loads in full). Claude reads the canonical source by reference. |
| `AGENTS.md` | TES core + generated block | Thin `TES:CORE` block plus a `TES:PROJECT-OVERLAY` managed block **materialized** (not linked) from the canonical source. Re-rendered on every update; never hand-edited. |
| `<root>.bak-<stamp>` | Archive / oracle | The pre-existing root, never discarded. It is the coverage oracle's source of truth for non-loss. |

The asymmetry is a permanent design fact, justified by `RULES-FILE-ENGINEERING.md`:

> Codex has no `@import`, include, or link directive. Writing `@docs/foo.md` in
> `AGENTS.md` puts the literal string in context, not the file.

Therefore Claude points and Codex materializes. There is no "until Codex
supports `@`" path; this is the end state. Authoring this as transitional is
explicitly prohibited (see Required Negative Checks).

## Canonical Source Contract

The canonical source is `docs/agents/PROJECT-CONTEXT.md`. This line does not
invent a schema — it adopts the 17 sections already required by
`project_context_oracle.py` (`# Tilly Project Context`, `## Identity`,
`## Initial Semantic Signals`, … `## Maintenance Rule`). Inherited human context
is distilled into those sections, not into a parallel file.

A **context unit** is the atomic, traceable claim used by the coverage oracle. A
unit is any non-trivial assertion in a root rules file that changes agent
behavior or records a durable project fact:

| Unit kind | Examples | Trivial (not a unit) |
|-----------|----------|-----------------------|
| Directive | "Never commit to main", "Run `npm test` before closeout" | "be careful", "write good code" |
| Convention | naming rule, file-layout rule, import-order rule | restating a language default |
| Routing | "API docs in `docs/api/`", "use X for dates" | — |
| Architecture decision | "we use event sourcing for orders" | — |
| Command / runbook | build, lint, test, deploy commands | — |
| Constraint / boundary | "do not touch `legacy/`", secret handling | — |

Each unit, after distillation, must be in one of exactly two states:

- **Covered** — traceable to a section of the canonical source (the oracle maps
  unit → section anchor).
- **Discarded-with-reason** — explicitly recorded as dropped, with a reason from
  a closed set: `redundant-with-tes-core`, `obsolete`, `duplicate`,
  `superseded-by-<unit>`. No silent drop is permitted.

A unit that is neither covered nor discarded-with-reason is a coverage failure.

## Distillation Contract (Agent + Adversarial Gate)

Distillation is the heavy, judgment-bearing capability and is isolated in its own
skill (`tes-context-distill`), invoked by `tes-init`/`tes-setup`; it is never
inlined into the thin setup alias.

Two phases, separating the irreversible from the optional:

1. **Phase 1 — deterministic extract + archive (always).** Parse the pre-existing
   root, archive it intact as `<root>.bak-<stamp>`, and extract context units
   verbatim into the canonical source. No rewriting of meaning. This phase is the
   deterministic floor inherited from parent SPEC-007.
2. **Phase 2 — agent condense/optimize (opt-in, confirmed).** The agent
   sanitizes, organizes, and condenses the extracted units into clean canonical
   sections. This phase runs only under user confirmation and is the only phase
   permitted to reword.

The adversarial gate (`context_distill_coverage_oracle.py`) is not "the agent
thinks it looks good". It is a coverage diff against the archived `.bak`:

- Every context unit detected in `.bak` is either Covered or
  Discarded-with-reason in the canonical source.
- A lost directive, command, convention, or architecture decision with no
  recorded reason fails the gate.
- The gate emits the coverage map (unit → state → anchor/reason) as evidence.

This is the `<diamond_build_test_fail_fix>` shape for context: archived original
as adversarial fixture, observed loss as failure, recorded coverage as repair.

## Rendering Contract

Both roots are regenerated by the parent composer extended with two renderers.

Claude (`CLAUDE.md`):

```md
<!-- TES:CORE BEGIN version=0.3.x sha256=<core-sha> adapter=claude -->
...thin core: identity, invariants, routing...
<!-- TES:CORE END -->

@docs/agents/PROJECT-CONTEXT.md
```

Codex (`AGENTS.md`):

```md
<!-- TES:CORE BEGIN version=0.3.x sha256=<core-sha> adapter=codex -->
...thin core: identity, invariants, runbook commands...
<!-- TES:CORE END -->

<!-- TES:PROJECT-OVERLAY BEGIN source=docs/agents/PROJECT-CONTEXT.md sha256=<src-sha> -->
...lean structured materialization of the canonical source...
<!-- TES:PROJECT-OVERLAY END -->
```

Rendering rules:

- The Codex overlay block is generated from the canonical source on every
  install/update; its `sha256=<src-sha>` records the source state it was rendered
  from. Source-vs-block SHA mismatch is a re-render signal, not a conflict.
- Hand edits inside the Codex overlay block are not the source of truth; the gate
  warns and the next render overwrites the block (only the block, never the file).
- The Codex materialization is "lean and objective": it is not the full canonical
  source verbatim, but a structured condensation sized well below the 32 KiB
  chain cap (`RULES-FILE-ENGINEERING.md` Codex byte model).
- The Claude `@` import is eager and loads in full; the thin core stays well under
  the ~200-line adherence target.

## Idempotency Contract

Re-running install/update must converge, never cannibalize:

- If a root is already a TES-rendered thin root (core block + `@` pointer for
  Claude, or core block + overlay managed block for Codex), distillation is
  **skipped** — the canonical source is already the truth. Re-distilling a
  pointer would extract emptiness or recurse.
- Detection: a root whose only non-core content is the `@` pointer (Claude) or
  the `TES:PROJECT-OVERLAY` managed block (Codex) is "already inherited".
- Re-render updates the core block and (Codex) the overlay block from the current
  canonical source; it does not re-run Phase 1/2 distillation.

## Reversibility Contract

Because install now overwrites the human root with a thin one, TES owns the
obligation to give it back:

- `<root>.bak-<stamp>` is mandatory and is referenced by the uninstall route
  (aligns with ADR 0004 reversible installation).
- Uninstall restores the archived original root; it does not leave the thin root
  or a half-distilled canonical source as the only artifact.
- The coverage map produced at distillation time is retained as the evidence that
  the canonical source faithfully carries the archived content.

## Required Status Semantics

Reuses the parent vocabulary; adds the coverage and rendering states this line
introduces.

| Status | Required Meaning |
|--------|------------------|
| `INHERITED` | Pre-existing root context was distilled into the canonical source and the root was re-rendered thin. |
| `OVERLAY_COVERED` | Every non-trivial unit in `.bak` is Covered or Discarded-with-reason in the canonical source. |
| `RENDER_CLAUDE_OK` | `CLAUDE.md` is a thin core block plus a resolving `@` pointer to the canonical source. |
| `RENDER_CODEX_OK` | `AGENTS.md` overlay managed block matches the current canonical source (`src-sha` parity). |
| `ALREADY_INHERITED` | Root is already a TES thin root; distillation correctly skipped (idempotent). |
| `NEEDS_REVIEW_COVERAGE` | One or more units are neither Covered nor Discarded-with-reason; no overwrite finalized. |
| `BLOCKED_ARCHIVE_MISSING` | The pre-existing root could not be archived; distillation refused (no destructive write without the `.bak` oracle). |

Parent statuses (`PASS`, `COMPOSED`, `CORE_STALE`, `OVERLAY_PRESENT`,
`NEEDS_REVIEW_CONFLICT`, `BLOCKED_OVERLAY_UNRECOVERABLE`) remain valid and
unchanged.

## Implementation Units

| Unit | Owned Surfaces | Required Behavior | Required Oracle |
|------|----------------|-------------------|-----------------|
| SPEC-000 Reproducer And Boundary | neutral fixtures: a rich pre-existing `CLAUDE.md` and `AGENTS.md` with directives, commands, conventions, decisions | Reproduce the failure: install today `.bak`s and whole-file overwrites, archiving the human context out of active context instead of inheriting it. Keep target identity generic. | New failing fixture before repair; `python3 scripts/private_vocabulary_oracle.py`; `git diff --check`. |
| SPEC-001 Context Unit Model And Coverage Oracle | new `scripts/context_distill_coverage_oracle.py` | Define the context-unit detector and the coverage diff (`.bak` units → Covered / Discarded-with-reason). Emit the coverage map as evidence. Fail on silent loss. | Oracle self-test: a fixture with N units must report N classified; a deliberately dropped directive must fail. |
| SPEC-002 Canonical Source Adoption | `docs/agents/PROJECT-CONTEXT.md` mapping, `scripts/project_context_oracle.py` | Map context-unit kinds to the existing 17 sections; confirm distilled output still satisfies the existing overlay oracle. No new schema. | `python3 scripts/project_context_oracle.py --self-test`; mapping fixture proving each unit kind has a home section. |
| SPEC-003 Distillation Skill | new `src/adapters/{claude,codex}/skills/tes-context-distill/SKILL.md`; `tes-init`/`tes-setup` invoke it | Two-phase distill (deterministic extract+archive, then opt-in confirmed condense). Phase 2 gated by the coverage oracle. Setup alias stays thin and only invokes. | `python3 scripts/command_trigger_oracle.py --self-test`; skill text oracle; distillation run against SPEC-000 fixture yields `OVERLAY_COVERED`. |
| SPEC-004 Claude Renderer (`@` pointer) | `scripts/root_context.py`, `src/adapters/claude/CLAUDE.md` | Render `CLAUDE.md` as thin core + `@docs/agents/PROJECT-CONTEXT.md`. Verify the import resolves and the thin core stays under the adherence target. | `python3 scripts/root_context.py --self-test`; fixture asserting `RENDER_CLAUDE_OK` and import resolution. |
| SPEC-005 Codex Renderer (materialized block) | `scripts/root_context.py`, `src/adapters/codex/AGENTS.md` | Materialize a lean `TES:PROJECT-OVERLAY` block from the canonical source, with `src-sha`. No `@`. Keep chain well under 32 KiB. | `python3 scripts/root_context.py --self-test`; fixture asserting `RENDER_CODEX_OK`, `src-sha` parity, and byte budget. |
| SPEC-006 Idempotency And Re-Render | `scripts/root_context.py`, `scripts/tes_bundle.py`, `scripts/tes_install.py` | Already-inherited roots skip distillation; re-render updates core (both) and overlay block (Codex) from the current source; no recursion, no emptied source. | Idempotent recomposition self-test: run twice, second run reports `ALREADY_INHERITED` and stable output. |
| SPEC-007 Installer And Adapter Integration | `scripts/tes_install.py`, `scripts/install_adapter.py` | Route `context_governance` root writes through distill + render instead of whole-file `.bak` + copy. Managed-block markers replace blind copy for Codex. | `python3 scripts/tes_install.py --self-test`; `python3 scripts/install_smoke.py --self-test`; install fixture with preexisting rich root yields `INHERITED`. |
| SPEC-008 Reversibility Integration | uninstall route, `<root>.bak-<stamp>` handling | Uninstall restores the archived original root; coverage map retained as evidence. Aligns with ADR 0004. | Uninstall fixture proving archived root is restored byte-faithful; coverage evidence present. |
| SPEC-009 Doctor And Recovery UX | `src/adapters/*/skills/tes-doctor/SKILL.md`, recovery docs | `/tes-doctor` explains inherited state, coverage gaps, re-render, and how to recover the archived root — without instructing manual whole-file overwrite. | Doctor route fixture or focused text oracle; command-trigger oracle if skills change. |
| SPEC-010 Canary Replay | private canary process kept outside TES source; neutral fixture in package | Replay the inherited-context class on a neutral fixture and at least one private target canary; no private details copied into TES. | Neutral fixture `INHERITED`+`OVERLAY_COVERED`; private canary summarized generically as local evidence. |
| SPEC-011 Release Identity And Sync | `package.json`, version constants, public bundle, docs indexes, release gates when authorized | Delivered distillation/rendering behavior receives patch bump, bundle rebuild, tag, release check, and Pages check before public claim. | `npm run commit:check`; `npm run release:check`; `public_pages_oracle.py --version <new>` after authorized sync. |

## P0 Cut: Canonical Source + Coverage Oracle

The first wave proves the non-loss contract before any rendering:

1. Add the SPEC-000 neutral rich-root fixtures.
2. Implement the context-unit model and `context_distill_coverage_oracle.py`
   (SPEC-001).
3. Map units onto the existing `PROJECT-CONTEXT.md` sections (SPEC-002).
4. Implement Phase 1 distillation (deterministic extract + archive) and prove a
   rich root distills to `OVERLAY_COVERED` with zero unexplained loss.

P0 is complete only when a deliberately dropped directive fails the coverage
oracle and a faithful distillation passes it.

## P1 Cut: Two Renderings + Idempotency

After P0:

1. Claude `@`-pointer renderer (SPEC-004).
2. Codex materialized managed-block renderer (SPEC-005).
3. Idempotent re-render and already-inherited skip (SPEC-006).

P1 is complete only when both roots render from the one canonical source and a
second install run reports `ALREADY_INHERITED` with stable output.

## P2 Cut: Installer Integration + Reversibility + UX

After P1:

1. Route installer/adapter writes through distill+render (SPEC-007).
2. Wire uninstall to restore the archived root (SPEC-008).
3. Distillation skill UX and `/tes-doctor` recovery (SPEC-003, SPEC-009).
4. Canary replay (SPEC-010).

P2 is complete only when a preexisting rich-root target installs to `INHERITED`,
uninstalls back to the archived original, and the canary replays the class.

## Required Negative Checks

- No "until Codex supports `@`" framing anywhere: the Claude-points /
  Codex-materializes asymmetry is the permanent end state.
- No new canonical-source file: the source is `docs/agents/PROJECT-CONTEXT.md`,
  reusing `project_context_oracle.py`. No parallel `project_rules.md`.
- No destructive root write without an existing `<root>.bak-<stamp>` archive.
- No `INHERITED` or `PASS` when any `.bak` unit is neither Covered nor
  Discarded-with-reason.
- No silent unit drop: every discard carries a reason from the closed set.
- No re-distillation of an already-inherited root (idempotency).
- No hand-edited Codex overlay block treated as source of truth.
- No `@` directive written into `AGENTS.md` as if Codex resolved it.
- No reopening or redefinition of the parent `root-context-composition` contract.
- No distillation capability inlined into the thin `tes-setup` alias.
- No target-project vocabulary, private path, private product name, internal
  service name, branch name, remote, commit, or raw target log in TES source.
- No release claim without patch-version and bundle decision.

## Required Oracles Before Implementation Closeout

Run focused gates during each unit. Before claiming convergence:

```bash
python3 scripts/context_distill_coverage_oracle.py --self-test
python3 scripts/project_context_oracle.py --self-test
python3 scripts/root_context.py --self-test
python3 scripts/tes_bundle.py --self-test
python3 scripts/tes_install.py --self-test
python3 scripts/install_smoke.py --self-test
python3 scripts/command_trigger_oracle.py --self-test
python3 scripts/materialize_adapter.py all --check
python3 scripts/platform_surface_oracle.py --self-test
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

- baseline behavior before correction (today: `.bak` + whole-file overwrite);
- exact old failure reproduced by fixture (human context archived out of active
  context, not inherited);
- exact fixed route (distill → canonical source → two renderings);
- root files touched and how they were rendered (Claude `@`, Codex block);
- coverage map: units detected, Covered, Discarded-with-reason;
- before/after canonical-source state and overlay `src-sha`;
- archive (`.bak`) id and restore command;
- idempotency proof (second run `ALREADY_INHERITED`);
- canary replay result using generic target language only;
- release identity decision.

## Certification Standard

The final claim may be `PASS` only when all are true:

- a preexisting rich-root target installs to `INHERITED` with `OVERLAY_COVERED`;
- both roots render from the one canonical source (`RENDER_CLAUDE_OK`,
  `RENDER_CODEX_OK`);
- a deliberately dropped unit fails the coverage oracle before repair and is
  covered after;
- a second install run reports `ALREADY_INHERITED` with stable output;
- uninstall restores the archived original root byte-faithful;
- the parent `root-context-composition` contract is untouched and still passes;
- private canary replay is summarized without private identifiers;
- release identity is resolved.

Otherwise close as `NEEDS_REVIEW` with the exact remaining unit.

## Ready Goal Prompt

```text
/goal Execute the TES Inherited Context Canonical Source Super SPEC, P0 only.

Authority:
- docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-tes-inherited-context-canonical-source.md
- docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-tes-root-context-composition.md
- docs/mesh/RULES-FILE-ENGINEERING.md
- docs/agents/PROJECT-CONTEXT.md
- scripts/project_context_oracle.py
- scripts/root_context.py
- docs/governance/MAINTAINER-CORRELATION-RULE.md

Objective:
Deliver the non-loss canonical-source contract (P0): neutral rich-root
fixtures, the context-unit model and context_distill_coverage_oracle.py,
the mapping onto docs/agents/PROJECT-CONTEXT.md sections, and Phase 1
deterministic distillation (extract + archive). Prove a faithful
distillation reports OVERLAY_COVERED and a deliberately dropped directive
fails the coverage oracle.

Do not start P1 rendering until P0 oracles pass and the owner authorizes
continuing in the same run. Do not reopen the parent root-context-composition
contract. Planning-only authorities; runtime units carry their own gates and
the release-identity decision.
```
