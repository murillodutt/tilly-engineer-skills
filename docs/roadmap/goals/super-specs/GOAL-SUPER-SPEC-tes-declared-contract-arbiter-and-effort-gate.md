---
tds_id: roadmap.goal_super_spec_declared_contract_arbiter_and_effort_gate
tds_class: roadmap
status: active
consumer: maintainers, tes-engineering-discipline authors, discipline-oracle authors, adapter materialization authors, and execution agents
source_of_truth: false
evidence_level: L1
tver: 0.1.0
---

# GOAL Super SPEC: Declared-Contract Arbiter + Effort Gate

Status: active execution artifact. This Super SPEC carries the COMPLETE LITERAL solution — every paste-ready block of text and code — not a recipe. The next window in the TES execution flow applies the embedded literal blocks in the ordered Materialization Tree; it does not re-design.

Capability: extend the TES engineering-discipline protocol with (1) a **Gate Zero — Declared-Contract Arbiter** that resolves gate tension deterministically by binary-hard declared-contract evidence instead of letting the broad/generic default win by gravity; (2) a sixth **Effort Gate** as an orthogonal elevation axis (`Standard` default, `Premium` on named consequence) that separates *how much rigor per line* from *how much scope*; (3) a **classificatory reframe** of the Maturity Layer Gate so maturity is decided in thinking and the artifact is born at the converged level (the house-palace thesis), removing the temporal "build small then rebuild" defect; and (4) **oracle teeth** in `discipline_oracle.py` (Stage A string validation) that bind effort and declared-contract fields to the proven validation spine. All without forking the existing gate vocabulary, breaking the sha256-sealed bootloader regions, or overclaiming enforcement the oracle does not perform.

## Why this exists — lived provenance (not theory)

This change was discovered through REAL USE of the TES protocol on a real project, not by theorizing about the protocol. The five gate-conflict cases that dictated the design are lived decisions; the arbiter rule was EXTRACTED from them, then adversarially verified back against them. Anonymized:

| Lived case | Gate tension | What won | Lesson encoded |
|------------|--------------|----------|----------------|
| Frozen schema vs JSON round-trip | Simplicity (use `JSON.parse(JSON.stringify)`) vs a frozen `strictObject` with `.optional()` fields | true-scenario (chose a field-preserving clone) | **frozen-schema cardinality** is a declared contract; the arbiter must override the smaller fix |
| Export affordance vs frozen module boundary | a control labeled `Export PDF` (verb+noun) promising a file vs a frozen module exposing no byte path | broad-default, correct-but-lucky | **affordance-deliverable** vs a second frozen contract = a COLLISION; the failure was not stopping, it was failing to ESCALATE the collision |
| Closed 9-type palette capped at 8 | "unit tests green = done" vs an enum of size 9 with acceptance "all 9" | true-scenario only because an external integration oracle forced it | **closed-domain coverage**; the protocol got lucky — it must arbitrate, not depend on an external oracle |
| Lone-deviation page layout | Surgical (smallest CSS patch) vs a structural convention used by a countable majority of sibling pages | true-scenario (aligned to the peers) | **peer-convergence** is a declared contract |
| "1 star of 5" craft | Simplicity ("I built the requested widgets") vs no declared contract at decision time | broad-default, correctly | NO declared contract existed → broad default MUST win; inventing craft from nothing is the inverted "always do more" bug. This is the gate the absence of an effort axis silenced. |

The separating signal the experience dictated is NOT consequence-class (correctness vs completeness) and NOT a list of soft contexts. It is: **a violation of a contract already DECLARED and source-checkable in the repo at decision time.** When that exists and is satisfiable, the true scenario wins; when it collides with another declared contract, escalate; when no declared contract exists, the broad default correctly wins. The signal is binary-hard, in the spirit of `tes-mine`: a yes/no question has exactly one answer; gradation is the entry door of ambiguity and is forbidden.

## Canonical Artifact

Canonical Super SPEC: `docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-tes-declared-contract-arbiter-and-effort-gate.md`

Primary edit surfaces (sources, not installed copies):

- `src/adapters/claude/skills/tes-engineering-discipline/SKILL.md` — the discipline anchor (Gate Zero, Six Gates table, Effort Gate section, maturity reframe).
- `src/adapters/codex/skills/tes-engineering-discipline/SKILL.md` — the Codex mirror that `discipline_oracle.py --self-test` actually reads (`parents[1]/SKILL.md`); receives the same gate detail AND the new `REQUIRED_TERMS`.
- `src/adapters/codex/skills/tes-engineering-discipline/scripts/discipline_oracle.py` — the Stage A teeth.
- `src/adapters/claude/CLAUDE.md`, `src/adapters/codex/AGENTS.md`, and `src/adapters/cursor/CURSOR.md` — the thin bootloaders of the PRODUCT layer (the adapters shipped to adopting projects). Adapters render shared INTENT, not byte-identical text.
- `src/adapters/claude/skills/tes-engineering-discipline/docs/CONTRACT-HISTORY.md` — the append-only changelog (mandatory before claiming done).

Two-layer boundary (do not confuse them). This change is **delivered-behavior**, so it lives ENTIRELY in the **product layer** under `src/adapters/**` (the files above) — the adapters this repo ships. The **work layer** — the active bootloaders that govern working inside THIS repo (`.claude/**`, `.agents/**`, the repo-root `AGENTS.md`, `.claude/CLAUDE.md`) — is NOT a target of this SPEC and is left untouched. The repo-root `AGENTS.md` is the maintainer/work bootloader, not the shipped Codex adapter; the shipped Codex adapter is `src/adapters/codex/AGENTS.md`. Whether the work layer later adopts these gates is a separate governance decision, out of scope here.

Sealed-region rule: the installed bootloaders carry an sha256-sealed `TES:CORE` region. NEVER hand-edit a sealed region. Edit the unsealed SOURCE files above and re-run `scripts/materialize_adapter.py` to re-seal.

## Certified Context

- The existing five gates (Think Before Coding, Maturity Layer Gate, Simplicity First, Surgical Changes, Goal-Driven Execution), the Mantra Gate, Diamond Build-Test-Fail-Fix, and the Infrastructure Decision Gate are accepted and preserved. This change ADDS Gate Zero and the Effort Gate and reframes two sentences of the Maturity Layer Gate; it does not flatten the existing structure.
- `discipline_oracle.py` is pure string validation (no git/subprocess): `PLAN_FIELDS`, `parse_plan_fields`, `is_generic(GENERIC_VALUES)`, `selected_layer(VALID_LAYERS)`, `ORACLE_SIGNALS`, `validate_plan_text`, `semantic_self_test` (valid/vague fixture pair), `main` with `--self-test` and `--plan`. Wired via `npm run oracle:self-test` inside `commit:check`.
- The `ArchiveStrategy` and Platform worked examples in the Maturity Layer Gate SURVIVE UNCHANGED — they were always about not building speculative scaffolding, which the reframe reinforces.

## Phase Boundary

This phase MAY: add Gate Zero, add the Effort Gate, reframe the two temporal sentences of the Maturity Layer Gate, extend `discipline_oracle.py` with Stage A string-validation teeth, add the bootloader lines, and re-materialize adapters to re-seal.

This phase MUST NOT: implement a live git/diff audit (Stage B) — the oracle stays string-validation only; alter the Mantra Gate, Diamond, or Infrastructure Decision Gate; rewrite the surviving worked examples; rename or remove any of the five existing gates; or hand-edit a sha256-sealed region.

## Non-Objectives

- No Stage B (live diff/git audit) of the arbiter or effort gate. Explicitly deferred; the honest teeth are Stage A intake validation.
- No third effort tier (a `Draft`/throwaway demotion). Two tiers (`Standard`/`Premium`) ship for binary-hard falsifiability. A third tier is a separate, owner-authorized change.
- No expansion of `CONSEQUENCE_SIGNALS`/`EFFORT_WEASEL`/declared-contract taxonomy beyond what the five lived cases require. The lists need governance curation over time, exactly like `ORACLE_SIGNALS`.
- No change to project-side installed copies in this SPEC; materialization installs them.

## Central Rule

```text
When gates tension, a binary-hard DECLARED contract overrides the broad default;
a collision of two declared contracts is escalated, never resolved silently;
absent any declared contract, Simplicity and Surgical win unchanged.
Effort raises rigor per line; it never raises scope.
```

## Forbidden Moves

- No adjective-as-criteria. Every trigger is a source-nameable fact (frozen-schema cardinality / closed-domain coverage / peer-convergence /affordance-deliverable / a named consequence surface). "Important", "sensitive", "premium-looking", "could be nicer" are NOT triggers.
- No gradation. `declared_contract` and `effort_tier` resolve to exactly one state or fail as `NEEDS_REVIEW`. "Partially declared" / "somewhat premium" do not exist (the `tes-mine` binary-hard criterion).
- No scope inflation via effort. A `Premium` plan that adds a strategy interface, factory, registry, config knob, or any new seam is a `Birth` hard stop violation dressed as thoroughness.
- No silent collision resolution. Two colliding declared contracts MUST be named to the user.
- No overclaim of enforcement. The oracle validates that the plan DECLARES the contract and tier (string validation); it does NOT detect the violation in a diff. Say so.
- No hand-edit of a sealed `TES:CORE` region. Edit source, re-materialize.
- No empty commits to satisfy a unit; each unit changes its named files and passes its oracle.

## Materialization Tree

One commit per unit, in order. The literal blocks for each unit are embedded in the "Literal Solution" appendix below; the unit references the block by id.

### SPEC-000 — Preflight & baseline

- Owned files: none (read-only).
- Forbidden: runtime edits, commits, remote actions.
- Behavior: confirm the source paths exist (the five edit surfaces above), run `npm run oracle:self-test` to capture the GREEN baseline, run `git status --short --branch --untracked-files=all` and `git log --oneline -12` to record worktree state and confirm prior commits are baseline-only, and confirm the sealed bootloader regions are materialized (not hand-edited).
- Done: baseline oracle PASS recorded; worktree state and edit surfaces confirmed.
- Oracle: `python3 src/adapters/codex/skills/tes-engineering-discipline/scripts/discipline_oracle.py --self-test` returns PASS before any edit.
- Commit: **none** (preflight is a no-commit decision per `tes-goal-maestro`; this unit carries no material change). Evidence: baseline oracle results, worktree status, unrelated-change list, and the file matrix for SPEC-010. Recorded in SPEC-010's evidence block.

### SPEC-010 — Maturity reframe (classificatory, not temporal)

- Owned files: `src/adapters/claude/skills/tes-engineering-discipline/SKILL.md` and the Codex mirror `src/adapters/codex/skills/tes-engineering-discipline/SKILL.md`.
- Behavior: apply literal block **[L2 maturity-reframe]** — insert the born-at-converged-level paragraph under the Maturity Layer Gate heading; replace the temporal sentence "Preserve the baseline first, then simplify inside it." with its classificatory form; shield "smallest durable runtime slice" so "smallest" reads as scope, never executable-draft craft. The `ArchiveStrategy` and Platform worked examples are LEFT UNCHANGED.
- Done: the temporal sentence is gone; the reframe paragraph is present; the two worked examples are byte-unchanged.
- Oracle: `grep -c "Preserve the baseline first, then simplify" SKILL.md` == 0; `grep "born at the layer" SKILL.md` matches; `--self-test` still PASS.
- Commit: `docs(discipline): reframe maturity as classificatory, not temporal`

### SPEC-020 — Gate Zero: Declared-Contract Arbiter

- Owned files: both SKILL.md surfaces (Claude + Codex mirror).
- Behavior: apply literal block **[L1 gate-zero-arbiter]** — insert the `## Gate Zero — Declared-Contract Arbiter` section before the gates table; append the companion note line after the table.
- Done: the section is present with the binary question, the binary-hard `tes-mine` clause, the four declared-contract types, the three-way decision, and the two worked examples (override + collision).
- Oracle: `grep "Declared-Contract Arbiter" SKILL.md` matches in BOTH surfaces; `grep "Escalate-collision" SKILL.md` matches (the enum token from block [L1]; this is the same string later added to `REQUIRED_TERMS` in SPEC-040).
- Commit: `feat(discipline): add Gate Zero declared-contract arbiter`

### SPEC-030 — Effort Gate (sixth gate)

- Owned files: both SKILL.md surfaces.
- Behavior: apply literal block **[L3 effort-gate]** — replace the `## Four Gates` heading/table with the `## Six Gates` block (preserving the five original rows verbatim, adding the Gate Zero note row and the Effort Gate row, and the scope/craft axis note); insert the `## Effort Gate` section between the Maturity Layer Gate and Diamond sections.
- Done: the Six Gates table lists Gate Zero + six gates; the Effort Gate section carries the `Standard`/`Premium` tier table, the scope-isolation absolute clause, the collision-ownership sentence, and the two worked examples (minimal-scope-plus-Premium, Premium-not-required).
- Oracle: `grep "## Effort Gate" SKILL.md` matches; `grep "Standard" SKILL.md` and `grep "Premium" SKILL.md` match in the Codex mirror; `--self-test` still PASS (terms not yet required until SPEC-040 adds them).
- Commit: `feat(discipline): add Effort Gate elevation axis (Standard/Premium)`

### SPEC-040 — Oracle teeth (Stage A string validation)

- Owned files: `src/adapters/codex/skills/tes-engineering-discipline/scripts/discipline_oracle.py` and the Codex mirror SKILL.md (for the new `REQUIRED_TERMS`).
- Behavior: apply literal block **[L4 oracle-diff]** — the five hunks (REQUIRED_TERMS, PLAN_FIELDS, module constants with word-boundary matching, resolver/matcher helpers + the Effort Gate block in `validate_plan_text`, and the four new `semantic_self_test` plans + assertions). Word-boundary matching prevents the verified false-fires (`drop`≠`dropdown`, `important` co-occurring with a real consequence).
- Done: `selected_tier`/`declared_contract` resolve binary-hard; UNDER_EFFORT fires; the four new self-tests are present.
- Oracle: `python3 ...discipline_oracle.py --self-test` PASS with the six self tests (the original Evolution pair + the four new plans: valid-premium PASS, under-effort FAIL-as-expected, benign-Standard PASS, real-Premium PASS).
- Commit: `feat(discipline): give effort gate + arbiter Stage A oracle teeth`

### SPEC-050 — Bootloaders (thin) + re-materialization

- Owned files (PRODUCT layer only): `src/adapters/claude/CLAUDE.md`, `src/adapters/codex/AGENTS.md`, `src/adapters/cursor/CURSOR.md` — each rendered in its adapter's voice.
- Forbidden: the work/maintainer layer — repo-root `AGENTS.md`, `.claude/CLAUDE.md`, `.claude/**`, `.agents/**` — is out of scope and untouched.
- Behavior: apply literal block **[L5 bootloader]** as EQUIVALENT INTENT per adapter (CLAUDE.md `## Gate Principles` numbered list; AGENTS.md `<instructions>` XML; CURSOR.md rule). Add the Gate-Zero principle and the Effort principle; shield the Runtime-First "smallest durable runtime slice" sentence. Keep bootloaders THIN — name the gates and point to the skill; do not restate detail. Then re-run `scripts/materialize_adapter.py` to re-seal the `TES:CORE` regions.
- Done: each bootloader names the two new gates; the sealed regions are re-materialized (not hand-edited); `materialize_adapter.py` and `adapter_parity_readiness.py` pass.
- Oracle: `python3 scripts/adapter_parity_readiness.py` PASS; the installed bootloaders carry a fresh valid `sha256=` seal; `grep "Declared-Contract"` matches each bootloader.
- Commit: `feat(discipline): surface arbiter+effort gates in thin bootloaders`

### SPEC-060 — Contract history + full gate

- Owned files: `src/adapters/claude/skills/tes-engineering-discipline/docs/CONTRACT-HISTORY.md` (append only) and any benchmark/parity surface the full gate touches.
- Behavior: append literal block **[L6 contract-history]** changelog rows and the new contracts-preserved/failure-modes entries; run the full repo gate (`npm run commit:check` or the documented closure gate).
- Done: CONTRACT-HISTORY has the new dated rows; the full gate is green.
- Oracle: `npm run commit:check` (the full 60+ oracle suite) returns PASS.
- Commit: `docs(discipline): record arbiter+effort gate in contract history`

## Release Identity Rule

Pre-stable (0.x). This is a MINOR-class change (additive gates + a behavioral reframe of an existing gate; no removal). Bump per the repo's version workflow after SPEC-060 is green; do not bump mid-tree.

## Global Stop Conditions

Stop and escalate to the owner if: applying a literal block reveals the source text drifted from what the block assumes (line anchors no longer match); the `materialize_adapter.py` re-seal fails or the parity oracle rejects the bootloader change; any unit's oracle cannot be made to pass without breaching the Phase Boundary; or a sealed region would have to be hand-edited.

## Honest Limits (carried, not hidden)

- **Stage A only.** The oracle validates that the plan DECLARES the contract, tier, and escalation — string validation. It does NOT run a live diff/git audit, so it cannot detect a dishonest plan that simply omits the contract it secretly knows about. This is the identical residual trust the Maturity Gate already places in honest promotion evidence. Stage B is deferred.
- **Token/glob lists can be gamed or go stale.** `CONSEQUENCE_SIGNALS` /`EFFORT_WEASEL` need governance curation, like `ORACLE_SIGNALS`. Keyword stuffing fails safe (more rigor, never more scope) but pollutes the audit trail.
- **Two tiers are deliberately coarse.** A money/credit surface and a single-consumer validator get the same `Premium` ceiling though blast radius differs by orders of magnitude — the accepted price of a falsifiable enum over a vibe slider, mirroring the four-layer maturity coarseness.
- **`irreversible` is the one near-adjective in `CONSEQUENCE_SIGNALS`.** It is justified as a checkable property (revert+redeploy cannot undo it before a reader sees it), not a feeling; the inline comment says so.

## Definition Of Complete

Complete when: SPEC-000 preflight is recorded as a no-commit decision and the six material units (SPEC-010..060) are committed in order with their oracles green; the two new gates are present in both SKILL.md surfaces and the three bootloaders; `discipline_oracle.py --self-test` passes with the six self-tests; the sealed bootloader regions are freshly materialized; CONTRACT-HISTORY records the change; and `npm run commit:check` is green. The protocol then arbitrates gate tension by binary-hard declared-contract evidence, carries an orthogonal effort axis, treats maturity as classificatory, and overclaims nothing.

---

# Literal Solution (paste-ready blocks)

> These are the COMPLETE final words/code, forged in the protocol voice and adversarially verified against the anti-ambiguity bar and the five lived cases. The Materialization Tree applies them by id. Anchors (line numbers) are indicative; match on the quoted BEFORE text, not the line number.

**Per-adapter rule for every "both SKILL.md surfaces" block (L1, L2, L3).** The literal text below is authored in the CLAUDE surface voice and structure. The Claude surface receives it byte-for-byte. The CODEX mirror (`.agents/skills/tes-engineering-discipline/SKILL.md` /`src/adapters/codex/skills/tes-engineering-discipline/SKILL.md`) has its own house structure and wording — notably its gates table is headed `## Core Gates` (not `## Four`/`## Six Gates`) and its existing gate rows carry Codex wording. Apply each block to the Codex mirror by INTENT, not byte-identical paste: preserve the Codex headings and the wording of rows that already exist; ADD the new sections/rows/notes; adapt only surface-specific cross-references. This is the same "adapters render shared intent, not byte-identical text" rule the bootloader block (L5) already states — it binds the SKILL.md blocks too. Never overwrite a Codex-worded row with Claude wording to force a byte match; that violates verbatim/surgical for the Codex surface.

## [L1 gate-zero-arbiter] → both SKILL.md surfaces, before the gates table

~~~~markdown
## Gate Zero — Declared-Contract Arbiter

The arbiter runs FIRST, before the five gates, whenever the gates tension —
Simplicity-First or Surgical-Changes pulling one way and a contract already in
the repo pulling the other. It answers exactly one binary question:

```text
Does the minimal solution silently violate a contract already DECLARED and ENUMERABLE in this repo?
```

The question is yes/no with exactly one answer, in the spirit of `tes-mine`: it
works because it is hard and accepts no questioning. `YES` requires a NAMED
declared fact on the table; anything that is not `YES` is `NO`. Gradation —
"partially declared", "sort of a peer-convergence", "mostly violated" — is
forbidden; it is the entry door of ambiguity. This mirrors the oracle grammar:
`maturity_layer` resolves to exactly one enum value or fails, `is_generic`
returns `True`/`False`, `selected_layer` returns one layer or `None`. The
`declared_contract` state resolves to exactly one of `YES`/`NO` or fails as
`NEEDS_REVIEW` — never "partial".

A declared contract is one an oracle could name from source WITHOUT running it.
There are exactly four types:

1. **Frozen-schema cardinality** — a frozen schema's field-cardinality
   invariant (`strictObject`, `.optional()`). A transform that drops a declared
   field violates it.
2. **Closed-domain coverage** — a union or enum of known size `N` reachable on
   the path, AND an acceptance line saying "all `N`", with the implementation
   capped below `N`.
3. **Peer-convergence** — a structural pattern used by a countable majority of
   in-repo sibling units of the same class, with the unit under change the lone
   deviation.
4. **Affordance-deliverable** — a user-facing control whose label is verb+noun
   naming a concrete artifact that must cross the app boundary.

Decision is three-way:

- **Override-and-bind-oracle.** If `YES` and the contract is satisfiable in
  scope, the broad default (Simplicity-First / Surgical-Changes) is OVERRIDDEN
  and the closure oracle MUST bind to the declared contract.
- **Escalate-collision.** If `YES` but satisfying it would breach a SECOND
  declared boundary — a frozen surface, a SPEC stop-state — you MUST NOT pick
  the broad default silently. NAME the collision to the user as an escalated
  trade-off. Resolving a collision silently is itself a failure the discipline
  oracle's plan check is meant to surface.
- **Broad-default-wins.** If `NO` declared contract is violated,
  Simplicity-First and Surgical-Changes WIN unchanged. Undeclared aspirations —
  craft, polish, "could be nicer" — do NOT trigger the override.

When the override fires, the obligation is per-line rigor, not more lines: route
to the Effort Gate and promote the effort tier to `Premium` (see Effort Gate).
Premium authorizes a heavier oracle bound to the declared contract; it never
authorizes a new abstraction, strategy interface, or config knob to "cover" the
contract.

Worked example (override). Request: "Persist the designer draft by
round-tripping it through `JSON.parse(JSON.stringify(draft))` before save — it's
the smallest serialization and the snapshot looks identical." A frozen
`strictObject` with `.optional()` fields is on the path, and a JSON round-trip
silently drops keys whose value is `undefined`. Verdict: `declared_contract =
YES`, type frozen-schema cardinality. The broad default (smallest
serialization) is OVERRIDDEN; the closure oracle MUST bind to the frozen schema
— a structural clone that preserves declared-optional fields, with a test that
asserts an `undefined`-valued optional field survives the round-trip. Effort
tier promotes to `Premium` (heavier oracle, same scope). Do not add a
serializer abstraction; repair the one path.

Worked example (collision). Request: "Wire the 'Exportar PDF' button to deliver
the file; the export module boundary is frozen and exposes no byte path, so just
have the handler resolve and toast success." Two declared contracts collide: an
affordance-deliverable invariant (a control labeled verb+noun — "Exportar PDF" —
promising a delivered artifact across the app boundary) and a frozen module
boundary that exposes no byte path to deliver it. Verdict: `declared_contract =
YES` on the affordance, but satisfying it breaches the frozen boundary. You MUST
NOT silently ship the toast-only handler (the affordance lies) and MUST NOT
silently widen the frozen boundary (the surface lies). NAME the collision as an
escalated trade-off: stopping at the frozen boundary is correct; the failure is
not escalating the deliverable-vs-boundary collision to the user. Resolve only
after the user picks which boundary moves.
~~~~

Companion note line, appended after the gates table:

```markdown
The Declared-Contract Arbiter (Gate Zero) runs FIRST, before all six gates: when
the gates tension, it can override the broad default, force a collision
escalation, or leave Simplicity-First and Surgical-Changes untouched.
```

## [L2 maturity-reframe] → both SKILL.md surfaces, Maturity Layer Gate section

New paragraph, inserted directly under the `## Maturity Layer Gate` heading, before "Default material work to `Birth`. Promote only with evidence:":

```markdown
Maturity is classificatory, not a phase of execution. The layer is decided
during thinking — which converges before the first line — and the artifact is
born at the layer the thinking settled on. There is no "execute `Birth`, then
promote and re-execute": a `Platform` change is `Platform` from its first line,
a `Birth` change is `Birth` from its first line. Nobody builds a simple house to
demolish it into a palace; the simple phase is the THINKING, and it ends before
the first beam. Promotion is reclassification of the work, never a rebuild of
shipped lines. (Protecting an existing `Platform` baseline is not a rebuild — it
is correctly classifying that the work was `Platform` all along.)
```

Birth row shield — replace the `Simplicity Means` cell of the `Birth` row:

```text
BEFORE: | `Birth` | No higher-layer evidence exists | Less structure; smallest durable runtime slice |
AFTER:  | `Birth` | No higher-layer evidence exists | Less structure; the smallest slice in SCOPE, built at full craft — never an executable draft to be redone |
```

Temporal sentence — replace the trailing sentence at the end of the "`Birth` is invalid when..." paragraph:

```text
BEFORE: Those are promotion evidence. Preserve the baseline first, then simplify inside it.
AFTER:  Those are promotion evidence: classify the work at that higher layer from its first line, and simplify inside that classification — not by building lower and rebuilding up.
```

The `ArchiveStrategy` worked example and the Platform worked example are LEFT UNCHANGED.

## [L3 effort-gate] → both SKILL.md surfaces

**Per-adapter application rule (intent-equivalent, not byte-identical).** The two SKILL.md surfaces do NOT share a byte-identical gates table — the same way the bootloaders render shared intent, not identical text. Apply L3 by INTENT to each surface, honoring its own house structure:

- **Claude** (`src/adapters/claude/skills/tes-engineering-discipline/SKILL.md`): the gates table is headed `## Four Gates`. Apply EDIT 1 byte-for-byte as written below (`## Four Gates` → `## Six Gates`, the five Claude rows preserved verbatim, plus the Gate Zero note row, the Effort Gate row, and the scope/craft axis note).
- **Codex** (`src/adapters/codex/skills/tes-engineering-discipline/SKILL.md`): the gates table is headed `## Core Gates` and its five rows carry the Codex wording (e.g. "Name facts, assumptions, ambiguity..."; "Delete speculative scope before adding machinery..."). Do NOT rename `## Core Gates` and do NOT overwrite the five Codex rows with the Claude wording — that would violate verbatim/surgical for the Codex surface. Instead, ADD only: the Declared-Contract Arbiter (Gate Zero) row, the Effort Gate row, and the scope/craft axis note, preserving the Codex heading and the Codex wording of the existing rows.

EDIT 2 (the `## Effort Gate` section) is intent-shared: insert it in BOTH surfaces at the same logical point — after the Maturity Layer Gate section and before the Diamond section — adapting only surface-specific cross-reference wording if a surface names a section differently.

The block below is the Claude rendering (EDIT 1 byte-for-byte for Claude; the literal source of the rows/notes/section the Codex surface adds by intent).

EDIT 1 — replace the `## Four Gates` section with (Claude surface):

```markdown
## Six Gates

Gate Zero is the Declared-Contract Arbiter; it runs before the six gates and
owns every collision between them. The table below lists Gate Zero plus the six
gates it arbitrates.

| Gate | Rule | Failure Blocked |
|------|------|-----------------|
| Declared-Contract Arbiter (Gate Zero) | Before closing any tensioned change, answer one binary question — does the minimal solution silently violate a contract already declared and source-nameable in this repo? Resolve collisions here, never inside another gate | Silent contract breach and silent collision resolution |
| Think Before Coding | State assumptions, ambiguity, tradeoffs, and blockers before acting | Silent wrong interpretation |
| Maturity Layer Gate | Default to `Birth`; promote only with evidence naming baseline, allowed complexity, forbidden complexity, and oracle | Flattening mature architecture or inflating birth work |
| Simplicity First | Solve only the requested problem with the smallest useful shape for the selected maturity layer | Overbuilt code and API bloat |
| Surgical Changes | Touch only request-traceable lines and self-created orphans | Drive-by refactors and hidden churn |
| Goal-Driven Execution | Define a falsifiable oracle and verify before closure | False completion |
| Effort Gate | Default to `Standard`; promote to `Premium` only when the Declared-Contract Arbiter or named consequence evidence obligates deeper rigor per line, never more lines | Under-rigor on declared-contract lines and invented rigor on undeclared ones |

Scope gates: Maturity Layer, Simplicity First, Surgical Changes. Craft gates:
Think Before Coding, Goal-Driven Execution, Effort Gate. The two axes are
orthogonal: scope decides how many lines exist; effort decides how much rigor
each line carries. Neither gate may move the other axis.
```

EDIT 2 — insert this `## Effort Gate` section between the Maturity Layer Gate section and `## Diamond Build-Test-Fail-Fix`:

```markdown
## Effort Gate

The Effort Gate is an elevation axis, not a barrier, and it is orthogonal to
scope. It sets how much rigor each line carries, never how many lines exist.
Default material work to `Standard`. Promote only with evidence:

| Tier | When | Authorizes |
|------|------|------------|
| `Standard` | No declared-contract or named-consequence evidence obligates deeper rigor | The high-craft project baseline: lint, typecheck, test, surgical diff — already premium-grade, not a mediocrity ceiling |
| `Premium` | The Declared-Contract Arbiter fires, or named consequence evidence (a frozen schema, a closed-domain coverage line, a peer-convergence pattern, an affordance deliverable, a ledger/money/auth/migration surface) obligates deeper rigor per line | More adversarial cases, a heavier named oracle class, mandatory upstream/Context7 verification, adversarial-first Diamond execution — all on the existing lines |

Promote only when the Declared-Contract Arbiter answers YES or named consequence
evidence is on the table. The trigger is always a source-nameable fact — a
declared contract an oracle could name, or a named consequence surface — never
an adjective. "Could be more thorough", "feels important", "deserves polish" are
not `Premium` triggers; they are undeclared aspirations and they leave the tier
at `Standard`. Invalid promotion evidence means `NEEDS_REVIEW`; no evidence
means `Standard`. The tier resolves to exactly one of `Standard` or `Premium` or
fails as `NEEDS_REVIEW`; "partially Premium" is not a state.

Scope isolation (absolute): `Premium` authorizes more rigor per line, never more
lines, abstractions, or features. A `Premium` plan that adds a strategy
interface, an abstract factory, a config knob, or any new seam is a `Birth` hard
stop violation dressed as thoroughness — the Effort Gate cannot buy a scope
promotion. Both `Birth` + `Premium` and `Platform` + `Standard` are legal and
expressible: a one-line fix on a frozen schema is `Birth` scope at `Premium`
craft; a multi-surface release with no declared-contract tension can be
`Platform` scope at `Standard` craft.

When two declared contracts collide on the same line (an affordance-deliverable
that must ship versus a frozen boundary it would breach), the Effort Gate does
not resolve it — the Declared-Contract Arbiter does, and the correct move is to
escalate the conflict, never to silently stop or silently breach.

Worked example — minimal scope plus `Premium` craft. Request: "Flip the credit
approval threshold from 0.70 to 0.75." Scope is `Birth`: one declared constant
changes, no new consumer or contract. The Declared-Contract Arbiter fires —
the threshold gates a money/credit decision surface — so effort promotes to
`Premium`. Correct `Premium` response on the same one-line diff: a failing
boundary fixture at 0.74/0.75/0.76 that proves the new cut, a contract oracle
binding the decision path to the declared value, and rollback reasoning for the
flip. Adding a `ThresholdStrategy` class, a thresholds config map, or a
pluggable policy seam is not `Premium` craft — it is a `Birth` hard stop
violation dressed as thoroughness. Premium deepens the proof on the line that
changed; it never grows the line count.

Worked example — `Premium` not required. Request: "Change a debug log string in
a throwaway script from 'starting' to 'starting run'." No declared contract is
on the path: no frozen schema, no closed-domain coverage line, no peer pattern,
no affordance deliverable, no money/auth/ledger surface. The Declared-Contract
Arbiter answers NO, so the tier stays `Standard` and the standard baseline
closes it. Inventing `Premium` rigor here — an adversarial fixture suite, a
mandated upstream check, a Diamond cycle — is the inverted bug: rigor spent
where no declared contract obligates it is wasted scope-of-effort, the mirror of
under-rigor on a contract line.
```

## [L4 oracle-diff] → discipline_oracle.py (Codex mirror) — five hunks

See the verified literal hunks. Summary of each (full text in the forge artifact, reproduced verbatim into the file at SPEC-040):

- HUNK 1: extend `REQUIRED_TERMS` with `"Declared-Contract Arbiter"`, `"Effort Gate"`, `"Standard"`, `"Premium"`, `"Escalate-collision"`. The term is the enum token `Escalate-collision` (the canonical decision-state name in block [L1], present verbatim in the Codex SKILL.md after SPEC-020) — NOT a prose phrase. Picking the enum token avoids adding redundant text just to satisfy a grep: the required term points at what the gate text already says.
- HUNK 2: extend `PLAN_FIELDS` with `"effort_tier"`, `"consequence_evidence"`, `"declared_contract"`.
- HUNK 3: add `VALID_TIERS`, `DECLARED_CONTRACT_TYPES`, `CONTRACT_ABSENT`, `CONSEQUENCE_SIGNALS`, `EFFORT_WEASEL` after `ORACLE_SIGNALS`. Word-boundary semantics: single-word signals match by token-set membership (so `drop` ≠ `dropdown`, `sign` ≠ `redesign`); multi-word signals match by substring.
- HUNK 4a: add `selected_tier` (binary-hard, mirrors `selected_layer`), `declared_contract` (exactly-one-type-or-absent), `names_consequence_signal` (word-boundary), `is_only_weasel` (rejects only pure-weasel content, not a real consequence co-occurring with a weasel word).
- HUNK 4b: in `validate_plan_text`, skip `declared_contract` in the generic sweep (its absence "none" is legal), and append the Effort Gate block before `return failures`: `effort_tier` must resolve to exactly one tier; `declared_contract` must resolve to one type or be absent; `consequence_evidence` above Standard must not be generic or pure-weasel; UNDER_EFFORT fires when a premium-class signal is named under `Standard`.
- HUNK 5: extend `semantic_self_test` with four new plans + assertions — valid-premium PASSES, under-effort FAILS, benign-Standard PASSES (locks the `dropdown` non-fire), real-Premium PASSES (locks the `important` co-occurrence non-fire). The original Evolution pair is preserved.

The five new `REQUIRED_TERMS` MUST be present as literal substrings in the Codex mirror `.agents/skills/tes-engineering-discipline/SKILL.md` (landed by SPEC-020 /SPEC-030 on that surface), or `--self-test` fails the `missing skill term:` check.

## [L5 bootloader] → CLAUDE.md / AGENTS.md / CURSOR.md (equivalent intent, then re-seal)

CLAUDE.md `## Gate Principles` (replace `## Four Principles`), renumbered to include the two new gates (Gate Zero first, Effort last):

```markdown
## Gate Principles

Apply to non-trivial coding, review, refactor, or instruction-migration work:

1. **Declared-Contract Arbiter** — before closing any change where the gates
   below are in tension, answer one binary question: does the minimal solution
   silently violate a contract already declared and enumerable in this repo's
   source (a frozen schema's field cardinality, a closed enum/union the path
   must fully cover, the structural pattern of a countable majority of sibling
   units, or a verb+noun affordance whose named artifact must cross the app
   boundary)? If yes and it fits in scope, bind the closure oracle to that
   contract; if satisfying it would breach a second declared boundary, name the
   collision to the user instead of resolving silently; if no declared contract
   is violated, Simplicity and Surgical win and undeclared polish does not.
2. **Think Before Coding** — state assumptions, ambiguity, tradeoffs, and
   blockers before acting; never pick a risky interpretation silently.
3. **Maturity Layer Gate** — classify the work at the maturity its thinking
   converges to and default material work to `Birth`; promote only with evidence
   that names the protected baseline, allowed complexity, forbidden complexity,
   and oracle.
4. **Simplicity First** — solve only the requested problem for the selected
   maturity layer; delete speculative scope before adding abstractions or
   configurability.
5. **Surgical Changes** — touch only request-traceable lines; clean only orphans
   you created; leave unrelated code, comments, and formatting alone.
6. **Goal-Driven Execution** — define a falsifiable oracle before closure and
   verify before claiming success.
7. **Effort Gate** — default every line to `Standard` (the premium craft
   baseline already carried by lint, typecheck, test, and surgical edits) and
   elevate to `Premium` only when the Arbiter or named consequence evidence
   obligates deeper rigor per line; `Premium` buys more rigor per line, never
   more scope.
```

Runtime-First shield — replace the first sentence of `## Runtime-First`:

```text
BEFORE: Build the smallest durable runtime slice on the intended execution path before adding governance.
AFTER:  Build the smallest-in-scope durable runtime slice — at full craft, not as a throwaway draft — on the intended execution path before adding governance.
```

`src/adapters/codex/AGENTS.md` (the shipped Codex adapter, `<instructions>` XML) and `src/adapters/cursor/CURSOR.md` (cursor rule) receive the EQUIVALENT intent in their own rendering — not a byte-identical paste. These are PRODUCT-layer adapters under `src/adapters/**`; do NOT edit the repo-root `AGENTS.md` or `.claude/CLAUDE.md` (the work/maintainer layer — out of scope). Keep each bootloader THIN: name the two gates and point to the skill; do not restate the arbiter/effort detail. After editing the unsealed sources, run `scripts/materialize_adapter.py` to re-seal the `TES:CORE` regions; never hand-edit a sealed region or hand-recompute a hash.

## [L6 contract-history] → tes-engineering-discipline docs/CONTRACT-HISTORY.md (append only)

Append to the Changelog table:

```markdown
| 2026-06-15 | Added Gate Zero (Declared-Contract Arbiter) and the sixth Effort Gate; reframed maturity as classificatory; gave the oracle Stage A teeth. | Lived gate-conflict evidence from real protocol use; adversarially verified. | high |
```

Add to "Contracts Preserved":

```markdown
- Gate Zero arbitrates gate tension by binary-hard declared-contract evidence;
  collisions are escalated, never resolved silently.
- Effort is an orthogonal axis: `Premium` raises rigor per line, never scope.
- Maturity is classificatory: the artifact is born at the converged layer.
```

Add to "Known Failure Modes Prevented":

```markdown
- The broad/generic default winning gate tension over the true scenario.
- Treating user-facing craft as a scope question with no axis to be heard.
- "Build small then rebuild" temporal trap of maturity.
- Adjective-as-criteria and graded ("partially premium") effort decisions.
```
