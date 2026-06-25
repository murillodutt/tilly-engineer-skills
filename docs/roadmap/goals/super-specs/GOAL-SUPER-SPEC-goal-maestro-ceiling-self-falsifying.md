---
tds_id: roadmap.goal_super_spec.goal_maestro_ceiling_self_falsifying
tds_class: roadmap
status: active
consumer: maintainers, Goal Maestro authors, oracle authors, lens authors, and execution agents
source_of_truth: true
evidence_level: L2
tver: 0.1.0
---

# GOAL-SUPER-SPEC: Goal Maestro Ceiling — Self-Falsifying Proof Generator

Anchor for `tes-goal-maestro --execute-loop`. Derived from and authorized by
`docs/adr/0006-decision-lens-evolution-and-routable-gate-closure.md`
(anchor_class=ADR, `git hash-object` = `58a53a48323213922b0e0ccd459d60c5fdcfce8d`,
accepted 2026-06-25). The hash is the recomputed blob hash of the anchor file,
not the commit sha — re-derived at the Pre-Edit Gate per execution-loop-runner.md:79.

```text
anchor_class=ADR
anchor_path=docs/adr/0006-decision-lens-evolution-and-routable-gate-closure.md
anchor_hash=58a53a48323213922b0e0ccd459d60c5fdcfce8d
anchor_origin=materialized-from-anchor
anchor_source=docs/adr/0006-decision-lens-evolution-and-routable-gate-closure.md
ambition_directive="nosso alvo não é atender o piso, é furar o teto"
quality_ceiling=the harness GENERATES its own falsifiable proof and cannot credit it
                without its own re-mutation engine firing (oracle synthesis +
                self-construction + adversary panel), all proven by re-mutation.
ceiling_decision=oracled_now
```

## Canonical Artifact

The `tes-goal-maestro` skill across its 4 byte-identical surfaces
(`src/adapters/claude`, `src/adapters/codex`, `.claude/skills`, `.agents/skills`)
plus the maintainer router `scripts/staged_commit_gate.py`. The delivered behavior
that changes: the harness moves from a proof-VALIDATOR to a proof-GENERATOR that
self-falsifies every artifact it produces.

## Capability / Purpose

Break the ceiling described by ADR 0006:

1. **Oracle Synthesis** — given a named property, the harness writes the falsifiable
   wall (fixture + honest measure + re-mutation plan) and runs it against its own
   falsifier before admitting it. `NEEDS_TREE_REPAIR` can emit a candidate oracle
   plus inversion proof; outside the known families it degrades to `NEEDS_HUMAN_ORACLE`.
2. **Self-Construction** — the harness can originate its own next anchor via a
   `derive-anchor-from-defect` path: a committed `GOAL-SUPER-SPEC-<defect>.md`
   carrying the synthesized re-mutation plan, consumable next session as
   `anchor_origin=previous-session`.
3. **Adversary Panel** — the single auditor becomes a panel of R disjoint-lens
   refuters with quorum-with-veto aggregation; the 3 distinction booleans become
   `DISTINCT_REFUTERS>=R`; new stop-state `NEEDS_QUORUM_AUDIT`.

Plus the floor-base that stays valid (ADR Part A residual + Part C lens contract).

## Certified Context

- The dogfooded loop (anchor `GOAL-SUPER-SPEC-goal-maestro-routable-oracle-gate.md`,
  closed `EXECUTION_LOOP_COMPLETE_WITH_AUDIT_REPAIRS`) already wired `validate-walls`
  into the router and `commit:closure`, des-hardcoded check 23 cross-stack, closed
  the src↔src parity gap, and added installer gate detection. **That work is baseline;
  it is NOT re-executed here.**
- Confirmed unwired (this loop's Part A residual): `anchor-rehash.mjs` and
  `ledger-no-placeholder.mjs` are NOT in `staged_commit_gate.py` — the 2 defect
  classes that leaked to audit-final.
- Confirmed absent (this loop's new generative work): `synth-fixture`,
  `NEEDS_HUMAN_ORACLE`, `refuters`, `NEEDS_QUORUM_AUDIT`, `derive-anchor-from-defect`.
- Load-bearing mechanisms (verified file:line): `validate-walls.mjs:197` makePng;
  `oracle-name-measure.mjs:21-24,64-65` invertible discriminator;
  `audit-remutation.mjs:51,60-83` author-agnostic falsifier;
  `oracle-wiring-check.mjs:131-139` decoy/second lens; `lib/harness.mjs:23-47`
  3-state aggregator; `ambition-and-anchor.md:13,17` previous-session enum + firewall;
  `execution-loop-runner.md:166-178` SPEC_REPAIR_BY_LLM, :250-254 fan-out,
  :315-317 distinction booleans; `tree-adversary.md:18,50-57` NEEDS_TREE_REPAIR +
  PROVEN/MEASURED contract.

## Shared Contracts

```text
contract_name: synth-fixture(property) API
declared_in: scripts/lib/synth.mjs (NEW, SPEC-001)
frozen_surface: synthFixture(property) -> {violatePath, revertPath} ; synthMeasure(property) -> {measured_quantity, honest:bool} ; synthMutation(family) -> {mutate, revert, decoy_mutate, decoy_revert}
extension_points: family registry (additive, keyed by family id)
extenders: SPEC-002 (tree-adversary consumes), SPEC-004 (refuter plans consume)
optionality_rule: a property outside the family registry returns honest=false -> NEEDS_HUMAN_ORACLE, never a proxy
declaring_oracles: scripts/synth-selftest.mjs (re-mutation of the synthesized trio)
extension_oracles: validate-walls.mjs (27/27 invariant), oracle-name-measure.mjs (self-validation)
```

```text
contract_name: refuters[] panel schema
declared_in: scripts/audit-remutation.mjs (extended, SPEC-004)
frozen_surface: plan.oracles[].refuters[] = [{lens, mutate, revert, decoy_mutate}] ; aggregate = quorum-with-veto
extension_points: lens taxonomy (structural-proxy, decoy-attribution, vacuous-empty, blocked-omission)
extenders: SPEC-005 (NEEDS_QUORUM_AUDIT + DISTINCT_REFUTERS counter)
optionality_rule: oracles[].refuters absent -> backward-compatible single-plan mode (no regression)
declaring_oracles: audit-remutation.mjs panel-mode selftest
extension_oracles: harness.mjs 3-state aggregator, validate-walls meta-wall (rejects R-1 clones)
```

## Phase Boundary

In scope: the 3 generative axes (synthesis, self-construction, panel), the Part A
residual (wire 2 gates), the Part C lens contract. 4-surface fidelity per skill change.
Local commit per SPEC. Bump stays 0.3.195 (already bumped by the prior loop; this is
the same delivered minor) unless a surface forces otherwise — decided at closeout.

Out of scope (declared owner-deferred, ADR Axes 4-5): wall-compiler cross-domain
codegen; context-economy ledger fields. Release bundle. Remote push.

## Non-Objectives

- Do NOT re-execute the prior loop's work (validate-walls wiring, check-23 des-hardcode,
  parity gap, installer detection) — it is certified baseline.
- Do NOT build the wall-compiler (Axis 4) or context-economy cache (Axis 5).
- Do NOT invent a proxy when synthesis meets an unknown property — degrade to
  NEEDS_HUMAN_ORACLE.
- Do NOT credit a generated artifact without its own re-mutation firing.

## Central Rule

```text
The harness must GENERATE the proof from the named property and submit that proof
to its OWN author-agnostic falsifier before admitting it. Simplest-correct is the
floor, not the target. A generated oracle that does not fire under mutation of its
own named property is a facade — even when the harness wrote it.
```

## Forbidden Moves

- Synthesizing a measure that is a structural proxy (must self-validate via
  oracle-name-measure before returning).
- Admitting a synthesized wall that did not fire under its own mutation or did not
  ignore the decoy.
- A panel where R-1 refuters are clones (vacuous diversity) credited as quorum.
- A self-originated anchor cited in the SAME session (firewall ambition-and-anchor.md:17).
- Lexical negative greps that reject valid blocked-state vocabulary.
- Breaking the validate-walls 27/27 invariant.

## Execution Units

```text
SPEC-000  Preflight And Baseline
  Capture baseline: git status, validate-walls 27/27 (exit 0), confirm Part A
  residual (anchor-rehash/ledger-no-placeholder unwired) and generative axes absent.
  Recompute anchor hash. No material edit. Commit a baseline marker only if the
  ledger needs it; otherwise no-commit rationale.

SPEC-001  Oracle Synthesis core (synth-fixture + synth-measure + synth-mutation)
  NEW scripts/lib/synth.mjs (4 surfaces): promote makePng/degeneracy generators to
  synthFixture(property); invert oracle-name-measure to synthMeasure(property) that
  PROPOSES the honest measured_quantity and self-validates it; extract the
  family->canonical-mutation map to synthMutation(family). NEW scripts/synth-selftest.mjs
  (4 surfaces): the declaring oracle — runs the synthesized trio against
  audit-remutation.mjs, admits only if it fires under its own mutation and ignores
  the decoy. Outside known families -> honest=false.
  Oracle: node synth-selftest.mjs exit 0 ; re-mutation: force synthMeasure to emit a
  proxy -> synth-selftest must exit != 0. validate-walls 27/27 invariant.

SPEC-002  Wire synthesis into the Tree Adversary (NEEDS_TREE_REPAIR -> candidate+proof)
  references/tree-adversary.md (4 surfaces): NEEDS_TREE_REPAIR for a facade/missing
  oracle may emit a synthesized candidate oracle + its inversion proof; for a property
  outside the families, route to NEEDS_HUMAN_ORACLE (NEW stop-state) instead of a
  bare repair request. references/quality-gates.md + SKILL.md stop-state list (4
  surfaces): register NEEDS_HUMAN_ORACLE.
  Oracle: grep proves NEEDS_HUMAN_ORACLE present in all 4 surfaces + quality-gates +
  SKILL; a doc-coherence wall (validate-walls coherence harness) over the changed
  references. Negative: NEEDS_HUMAN_ORACLE never replaces a valid in-family synthesis.

SPEC-003  Self-Construction: derive-anchor-from-defect path
  references/execution-loop-runner.md (4 surfaces): add the derive-anchor-from-defect
  path — a SPEC whose only material product is a committed GOAL-SUPER-SPEC-<defect>.md
  carrying the synthesized remutation-plan.json, consumable next session as
  anchor_origin=previous-session (cite ambition-and-anchor.md:13). The human gate
  collapses to NEEDS_OWNER_DECISION (decide IF the repair exists).
  Oracle (scoped to what the script actually proves — Tree Adversary OBJ-2):
  anchor-rehash.mjs proves byte-identity + benchmark isolation of a fixture
  GOAL-SUPER-SPEC-<defect>.md written this SPEC. The same-session self-authorization
  FIREWALL is NOT executable today (anchor-rehash.mjs does not read anchor_origin), so
  this SPEC proves it via (a) a doc-coherence grep that ambition-and-anchor.md:17 still
  forbids same-session self-authorization, and (b) routing a same-session citation to
  NEEDS_OWNER_DECISION. Do NOT claim anchor-rehash.mjs executably rejects same-session.
  validate-walls 27/27 invariant.

SPEC-004  Adversary Panel: refuters[] + quorum-with-veto in audit-remutation
  scripts/audit-remutation.mjs (4 surfaces): add panel mode — plan.oracles[].refuters[]
  with disjoint-lens entries; aggregate by quorum-with-veto via harness.mjs; absent
  refuters[] = backward-compatible single-plan mode. NEW meta-wall in validate-walls.mjs
  (4 surfaces): proves the aggregator REJECTS a panel of R-1 clone refuters.
  Oracle: audit-remutation panel selftest exit 0 ; re-mutation: a panel where one
  refuter leaves the oracle PASS-under-mutation -> veto -> credit denied (exit != 0).
  The R-1-clone meta-wall fires. validate-walls now 28/28 (the meta-wall is additive)
  — the invariant updates to 28/28 from this SPEC forward, recorded explicitly.

SPEC-005  Panel stop-state + distinction counter (NEEDS_QUORUM_AUDIT, DISTINCT_REFUTERS)
  references/execution-loop-runner.md (4 surfaces): the 3 distinction booleans gain a
  cardinal DISTINCT_REFUTERS>=R; new stop-state NEEDS_QUORUM_AUDIT mirroring
  NEEDS_INDEPENDENT_AUDIT when R distinct refuters cannot be instantiated. SKILL.md +
  quality-gates.md stop-state list (4 surfaces): register NEEDS_QUORUM_AUDIT.
  Oracle: grep proves NEEDS_QUORUM_AUDIT + DISTINCT_REFUTERS in all 4 surfaces +
  SKILL + quality-gates; the ledger schema carries the counter. validate-walls 28/28.

SPEC-006  Part A residual: wire anchor-rehash + ledger-no-placeholder into the router
  SPEC_REPAIR_BY_LLM (this loop, SPEC-006 attempt 1): the earlier "exit-code facade"
  prerequisite was a FALSE premise of mine. Re-execution with the exit code captured in
  ISOLATION (not through a `| tail` pipe, which returns tail's exit, not node's) proves
  anchor-rehash.mjs is already honest: wrong hash -> exit 1, right hash -> exit 0. No
  fix is needed; the gate is wired as-is. Repair recorded by the LLM, not a human.
  Pre-wire REGRESSION GUARD (not a fix): prove the gate is honest before wiring it —
  node anchor-rehash.mjs <adr> <wrong-hash> exits != 0 (isolated), <right-hash> exits 0.
  scripts/staged_commit_gate.py (maintainer): add 2 Gates — anchor-rehash.mjs fires
  when an anchor file or a ledger declaring an anchor hash is staged;
  ledger-no-placeholder.mjs fires when a ledger is staged. Moves the 2 audit-leaked
  defect classes to commit-time.
  Oracle: anchor-rehash exit-code re-mutation (above) exits != 0 on wrong hash;
  commit:check:plan shows both gates RUN when an anchor/ledger is staged, SKIP
  otherwise; gate re-mutation — stage a ledger with a placeholder commit -> the gate
  exits != 0 (ledger-no-placeholder fires); revert -> exit 0. validate-walls invariant.

SPEC-007  Part C: lens contract in the references (break-mandate, discoverability-first,
            risk-gating, audit-over-predict)
  references/tree-adversary.md + references/quality-gates.md (4 surfaces): encode the
  4-rule lens contract from ADR 0006 Part C. A lens declares its attack before running;
  discoverability runs first; lens depth gated by structural_method_id; deterministic
  gate-checkable defects prefer a wired gate over predictive stress. NEW stop-state
  LENS_THEATER (a lens that only confirms).
  Oracle: grep proves the 4 rules + LENS_THEATER + NEEDS_DISCOVERABILITY present in the
  4 surfaces + quality-gates; doc-coherence wall over the changed references.

SPEC-008  Certification And Closeout
  Run validate-walls full suite (28/28 exit 0), reference-package parity (src<->src +
  4-surface), tds, doc-size. Confirm bump correlation (0.3.195 stays unless a surface
  forces it; decide explicitly). Update DOCS-INDEX for the new synth.mjs selftest if a
  doc surface requires it. Executive Stop Audit handoff.
```

## Subagent Ownership

One fresh worker per ACTIVE_SPEC. SPEC-001/004 are code-bearing (`scripts/*.mjs`,
STRUCTURAL_METHOD active). SPEC-002/003/005/007 are reference-bearing (doc-coherence
+ stop-state grep). SPEC-006 is maintainer-router. SPEC-008 is certification.
Executive Stop Audit reviewer MUST be distinct from every operator and re-mutate
every required-axis oracle.

## Per-SPEC Oracles

Each SPEC carries a focused oracle that MUST be run with its literal exit code, plus
the `validate-walls` invariant (27/27 through SPEC-003; 28/28 from SPEC-004). The
generative SPECs (001, 004) additionally carry a re-mutation: the synthesized/extended
artifact must fire under mutation of its own named property — the ADR thesis applied
to the harness's own construction.

## Negative Grep

- No proxy measure admitted by synthesis (oracle-name-measure self-validation gate).
- No `synth-fixture` admitted without its re-mutation firing.
- No clone-refuter panel credited as quorum.
- No same-session self-authorized anchor.
- No `validate-walls` count regression (27/27 then 28/28).
- 4-surface drift: src/adapters/claude == src/adapters/codex == .claude/skills ==
  .agents/skills for every touched skill file (reference-package parity).

## Commit Strategy

Local commit per SPEC, semantic message, no push. Each commit gated by the persistent
Lefthook router (staged-scoped). SPEC repairs committed separately as SPEC_REPAIR_BY_LLM.

## Review Loop

Per-SPEC: parent validates allowed files, runs focused oracle + validate-walls,
captures git show --stat, post-commit + sync status (LOCAL_COMMITTED).
Final: Executive Stop Audit with distinct auditor, re-execution + re-mutation of every
required-axis oracle, ledger-no-placeholder scan, 3 distinction fields yes/yes/ran.

## Stop States

NEEDS_HUMAN_ORACLE, NEEDS_QUORUM_AUDIT, LENS_THEATER, NEEDS_DISCOVERABILITY (new),
plus the standard set: NEEDS_TREE_REPAIR, NEEDS_AMBITION_RECONCILIATION, AXIS_UNPROVEN,
SPEC_BLOCKED, SPEC_CONTRACT_UNSTABLE, NEEDS_MORE_LOOPS, NEEDS_OWNER_DECISION,
SAFETY_BLOCKED, NEEDS_INDEPENDENT_AUDIT, EXECUTION_LOOP_COMPLETE,
EXECUTION_LOOP_COMPLETE_WITH_AUDIT_REPAIRS.

## Final Delivery Contract

The harness generates its own falsifiable proof (synthesis), can originate its own next
anchor (self-construction), and audits by a quorum-with-veto panel (adversary depth) —
each capability proven by re-mutation, with the 2 Part A gates wired to commit-time and
the lens contract encoded. validate-walls green (28/28). 4-surface fidelity intact.
Axes 4-5 declared owner-deferred. No bundle, no push. Closeout by Executive Stop Audit.
