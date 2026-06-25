---
tds_id: architecture.adr_0006_decision_lens_evolution_and_routable_gate_closure
tds_class: architecture
status: active
consumer: maintainers, Goal Maestro authors, oracle authors, installer authors, lens/stress authors, and release operators
source_of_truth: true
evidence_level: L1
tver: 0.2.0
---

# ADR 0006: Harness Ceiling — From Proof-Validator To Self-Falsifying Proof-Generator

Accepted on 2026-06-25. Supersedes the floor-only draft of this ADR (tver 0.1.0), which treated the harness as fixed and only tuned the lenses around it. After a dogfooded `tes-goal-maestro --execute-loop` rebuilt the harness's own routable-oracle gate (anchor `GOAL-SUPER-SPEC-goal-maestro-routable-oracle-gate.md`, hash `b70acfa7`) and a five-axis ceiling exploration read every load-bearing mechanism against real `file:line`, this ADR redirects the harness toward its ceiling: the harness stops only *validating* proof artifacts brought from outside and starts *producing* them — self-falsified at birth — using the same author-agnostic re-mutation engine it already runs.

```text
ambition_directive="nosso alvo não é atender o piso, é furar o teto"
       (owner, verbatim, this run) — simplest-correct is the floor, not the target.
```

## Core Rule

```text
The harness must not only judge proofs brought to it. It must GENERATE the proof from the
named property and submit that proof to its OWN falsifier before admitting it.
A generated oracle/fixture/anchor that does not fire under mutation of its own named property
is a facade — even if the harness wrote it. Affirmation is never credit, not even self-affirmation.
The objective is never the floor; it is to break the ceiling.
```

## Context

Two bodies of evidence converge here.

**1. The dogfooded loop (floor evidence).** 10 SPECs, ~37 min, walls 27/27 invariant, closed `EXECUTION_LOOP_COMPLETE_WITH_AUDIT_REPAIRS` by an independent auditor. It produced measured facts about lens cost and integrity:

- Lenses that *broke* a decision paid for themselves (the descobribilidade lens broke the naive B3 "discover the gate without a pointer"; the SPEC-003 lens forced gate re-mutation over `.includes` mention).
- Lenses that only *confirmed* were expensive theater (~9 stress agents, ~1 actionable break, ~11% yield; stress/product token ratio ≈ 0.7–1.2×).
- The independent auditor out-yielded predictive stress (caught 2 real integrity defects — stale anchor hash, committed ledger placeholders — that 9 stress agents did not), but intercepted late (~32% of wall-clock in audit-repair).
- Two deterministic gates existed on disk unwired (`anchor-rehash.mjs`, `ledger-no-placeholder.mjs`), letting mechanical defects leak to the ~1400×-more-expensive audit-final point.

**2. The ceiling exploration (ceiling evidence).** Five latent-capability axes, each read against the real harness source. The unifying thesis: **the five axes are one jump seen from five angles.** Today the harness CONSUMES falsifiable artifacts written elsewhere (anchor, oracle, wall, fixture, re-mutation plan, context packet) and VALIDATES them. The ceiling is the harness that PRODUCES those same artifacts from the named property and auto-falsifies each at birth.

The pivot that makes this non-circular already exists and is the same in every axis: **`audit-remutation.mjs:51` iterates `plan.oracles[]` and does not care WHO authored the artifact** — it requires only that the artifact fire under mutation of the named property and revert. It is an *author-agnostic falsifier*. Therefore any artifact the harness generates can be submitted to its own falsifier before admission. That is the axis of symmetry of the entire ceiling vision.

The product direction (ADR 0005): grow by absorbing learning into existing assets, not by adding skills/governance. This ADR follows that posture — it activates latent capability inside `tes-goal-maestro` references and `scripts/*.mjs`, wires existing gates, and creates no new skill.

## The Five Axes — ordered by (ambition × proximity to current mechanism)

Each axis names its current ceiling, the latent mechanism that already exists, and the jump. `ceiling_decision` marks whether this ADR's loop EXECUTES it now or DECLARES it as a bounded extension.

### Axis 1 — Oracle Synthesis (the bottleneck) · `ceiling_decision=oracled_now`

The single highest-leverage capability, because the three organs of generation are already written and merely trapped in validation mode:

- **The fixture generator already runs.** `validate-walls.mjs:197` `makePng(name, fill)` produces the degenerate scene (`fill=()=>[140,100,60]`, line 90) and the rich scene (`fill=(x,y)=>[(x*4)&255,…]`, line 91). This *is* "given the property, return `{violate, revert}`" — trapped inside the self-test instead of exposed as `synth-fixture(property)`.
- **The measure discriminator is invertible.** `oracle-name-measure.mjs:21-24` (`STRUCTURAL_PROXY`/`NAMED_STRUCTURAL` regex) defines exactly the *complement* of honest measures. The same knowledge that rejects `statSync(.size)` for "luminance" (line 64-65) can PROPOSE "mean RGB of decoded pixels" and self-validate it through its own check before returning.
- **The family→canonical-mutation map already exists as dispersed data** in `validate-walls.mjs:36-187` (luminance→flat frame :90, fk→orphan id, double-entry→remove the paired line).

The jump: `NEEDS_TREE_REPAIR` (`tree-adversary.md:18`) stops being "human, write the oracle" and becomes "here is the candidate oracle + its inversion proof; approve or refine." For a property outside the 7 known families the synthesizer degrades honestly to `NEEDS_HUMAN_ORACLE` rather than inventing a proxy — measure-outside-family never becomes a silent facade. The synthesized trio is run against `audit-remutation.mjs` + `oracle-wiring-check.mjs` in the same pass: a wall is admitted only if it already fires under its own mutation and ignores the decoy. **Auto-falsification at birth.**

### Axis 2 — Self-Construction / self-originated anchor · `ceiling_decision=oracled_now`

The firewall "a generated Super SPEC cannot authorize itself" (`ambition-and-anchor.md:17`) is a SAME-SESSION rule. The `anchor_origin` enum already encodes `previous-session` and `materialized-from-anchor` (`ambition-and-anchor.md:13`), and `anchor-rehash.mjs:34-47` is author-agnostic — it requires only a persisted path + recomputed hash + non-cross-benchmark identity. The two-session bridge is **explicitly permitted by the enum itself.**

Activate = chain two invocations: the first runs a SPEC whose only material product is `GOAL-SUPER-SPEC-<defect>.md` committed (this is already `SPEC_REPAIR_BY_LLM`, `execution-loop-runner.md:166-178`, which already authors+commits a contract); the second cites it as `anchor_origin=previous-session`. Nothing is violated byte-for-byte. The defect SPEC is born carrying the `remutation-plan.json` that Axis 1 synthesizes, so the repair has a falsifiable oracle *before the code exists*. The jump: the human leaves the floor (materializing SPECs) and stays only at the ceiling — `NEEDS_OWNER_DECISION` (decide IF the repair should exist) becomes the single remaining human gate.

### Axis 3 — Adversary depth / multi-mind panel · `ceiling_decision=oracled_now`

Today adversariality is a chain of singulars: one Tree Adversary, one Executive Stop Audit reviewer, three binary distinction flags (`execution-loop-runner.md:315-317`) that prove ≥1 distinct mind, never HOW MANY or with WHICH lenses. The composition already exists in pieces: `audit-remutation.mjs:51,60` already iterates `plan.oracles[]` (moving to `oracles[].refuters[]` is array cardinality, not a new engine); the fan-out of fresh workers (`subagents-and-oracles.md:21`, `execution-loop-runner.md:250-254`) is the mind factory; the D3 decoy (`oracle-wiring-check.mjs:131-139`) is already a second lens running at scale 2; `harness.mjs:23-47` already aggregates N checks into a 3-state exit — the quorum aggregator is already written.

The jump: the DEFAULT shifts from "1 operator → 1 auditor" to "1 operator → PANEL of R refuters with disjoint failure-hypothesis lenses (structural-proxy, decoy-attribution, vacuous-empty, blocked-omission) + a veto aggregator." The three booleans become `DISTINCT_REFUTERS>=R`. New stop-state `NEEDS_QUORUM_AUDIT` mirrors `NEEDS_INDEPENDENT_AUDIT`. The harness stops proving "a second mind exists" and proves "none of R diverse lenses could topple this credit."

### Axis 4 — Cross-domain reach / wall-compiler · `ceiling_decision=owner_deferred`

The substrate is genuinely domain-blind: `harness.mjs:23-47` knows only `{name, pass, blocked}`; `audit-remutation.mjs:60-83` shells out strings without knowing the domain; the non-deterministic class (`rag-relevance.mjs` frozen-gold/BLOCKED) bridges any stochastic domain. But a declarative wall-compiler that *codegens* the `.mjs` + the mutation-suite entry from a JSON declaration is a **new mechanism** (codegen + self-certified admission), even though each wall fits the existing 3 closure classes. **Declared as a bounded extension, not executed in this loop.** It deserves its own anchor and canary because it widens the delivered surface (ML/security/infra/scientific domains) — release-identity risk that should not ride a self-construction loop.

### Axis 5 — Context economy / cache by structural class · `ceiling_decision=owner_deferred`

The only axis the exploration itself classified `extension-new-mechanism`. The three organs exist (`token-budget.mjs:35-47` measures tokens but points at the app-under-test, never the Worker Packet; the ledger keyed by `structural_method_id` is a cache nobody reads back; re-mutation is the guard against under-provisioning), but closing the loop needs new ledger fields (`packet_tokens`, `worker_exploratory_reads`), a redirected meter, and a sizing reader. **Declared as a bounded extension.** Its ROI depends on Axes 1-2 first: a minimal-context packet only matters once the harness generates many SPECs alone. Last, not for low ambition — for ordering.

## Decision

### Part A — Wire the existing deterministic gates (floor that stays valid)

The floor-only draft's Part A remains correct and is the base the ceiling builds on:

1. **Wire the two existing gates into the router** (`staged_commit_gate.py`): `anchor-rehash.mjs` fires when the anchor file or a ledger declaring an anchor hash is staged; `ledger-no-placeholder.mjs` fires when a ledger is staged. Moves the two audit-caught defect classes from audit-final (~700s) to commit-time (~0.5s) — a ~1400× cost reduction. Machinery already proven (the prior loop routed a `.mjs` as a declarative Gate).
2. **Gate predictive stress by `structural_method_id`** (the signal already in the ledger): run the 3-lens stress only for code-bearing classes; skip it for `doc-surface-edit` and `version-bump`, which never broke.
3. **Make the ledger schema axis-conditional** (emit only blocks whose axis is active) and entry-per-SPEC (`ledger.d/SPEC-XXX.md` concatenated at audit) — removes ~44% dead `not_applicable` lines and the append-only mutex.

### Part B — Break the ceiling: activate the three latent capabilities

The loop driven by the Super-SPEC derived from this ADR executes, in order of leverage:

1. **Oracle Synthesis (Axis 1).** Promote the degeneracy generators (`makePng` and family fixtures) to a callable `synth-fixture(property)`; invert `oracle-name-measure` to PROPOSE the honest `MEASURED_QUANTITY` and self-validate it; extract the family→canonical-mutation map. The synthesized trio is run against `audit-remutation.mjs` + `oracle-wiring-check.mjs` in the same pass; admitted only if it fires under its own mutation and ignores the decoy; degrades to `NEEDS_HUMAN_ORACLE` outside the known families. Wired into the Tree Adversary so `NEEDS_TREE_REPAIR` can emit a candidate oracle + inversion proof.
2. **Self-Construction (Axis 2).** Add the `derive-anchor-from-defect` path: a SPEC whose only material product is a committed `GOAL-SUPER-SPEC-<defect>.md` carrying the synthesized `remutation-plan.json`, consumable next session as `anchor_origin=previous-session`. The human gate collapses to `NEEDS_OWNER_DECISION`.
3. **Adversary Panel (Axis 3).** `audit-remutation.mjs` gains a panel mode (`oracles[].refuters[]`, R disjoint lenses); `harness.mjs` aggregates by quorum-with-veto; the three distinction booleans become `DISTINCT_REFUTERS>=R`; new stop-state `NEEDS_QUORUM_AUDIT`. A meta-wall proves the aggregator REJECTS a panel of R-1 clone refuters (vacuous diversity).

### Part C — Evolve the specialized-lens system (the lens contract)

Promoted from "stress before hard changes" to a **risk-gated, break-mandated decision amplifier**, each rule derived from measured loop evidence:

1. **Break-mandate (anti-elegance).** A lens MUST be charged to falsify the decision, declaring the concrete attack before running. A lens that cannot name an attack is not run; a lens whose output only restates the author's elegance is forbidden as a closure artifact. (Codifies "estressar de forma independente em vez de apaixonar-se pela própria elegância.")
2. **Discoverability-first.** The first lens on any non-trivial decision is descobribilidade: *can the claim be discovered/derived from the repo, or is it self-attested?* This broke B3 (the pointer did not exist) — the highest-yield lens in the loop. Runs before correctness lenses.
3. **Risk-gating (cost discipline).** Lens depth is gated by `structural_method_id` / declared risk axis, not applied uniformly. The gate signal already lives in the materialization tree and ledger.
4. **Audit-over-predict bias.** For a deterministic, gate-checkable defect class, prefer a wired pre-commit gate over predictive stress AND over audit-final. Reserve the independent auditor (now a panel, Axis 3) for re-mutation / facade-hunting, where it out-yielded stress.

The unifying contract:

```text
discover first -> attack to break (never confirm) -> gate by risk
-> generate the proof and submit it to your own falsifier -> wire deterministic checks, panel-audit the rest.
```

### What is NOT in this closure

- **Axes 4 and 5** are declared bounded extensions (`ceiling_decision=owner_deferred`), each needing its own anchor and canary; not executed by this loop. This is a cited owner deferral, not scope hidden in Non-Objectives.
- **The release bundle** is built only at the release ceiling (a sync/publish act needing explicit owner authorization). Until then, `commit:closure` failing on missing `0.3.195` dist paths is expected and honest.

Two axes carried as canary handoffs (not closed by claim): SPEC-009 `regression_target` derivation (`AXIS_UNPROVEN`, prove on an installed target); installer `--install-gate` verb (deferred as highest-risk, own canary).

## Consequences

- The harness gains a generative core that is self-falsifying by construction: every artifact it produces (oracle, fixture, anchor, refuter plan) is run against the author-agnostic re-mutation engine before admission, so "the harness wrote it" earns no more credit than "a human wrote it."
- The human moves off the floor: synthesis removes the human dependency for the PROOF ARTIFACT; self-construction removes it for the STARTING ANCHOR; the panel removes the single-mind blind spot. The remaining human gate is `NEEDS_OWNER_DECISION` (decide IF), exactly where it already is.
- Lens cost drops where it was theater and concentrates where it breaks things; the lens panel itself is held to "affirmation is never credit" — a lens that never breaks anything across a loop is flagged as theater and pruned.
- No new skill; absorbed into `tes-goal-maestro` references, `scripts/*.mjs`, `staged_commit_gate.py`, and the ledger schema, per ADR 0005's asset-transfer posture.

## Stop States

- `NEEDS_AMBITION_RECONCILIATION`: a run cites this ADR but lowers it to the floor (wiring + lenses only, no generative jump) — reconcile to the ceiling before `READY_GOAL_PROMPT`.
- `NEEDS_HUMAN_ORACLE`: synthesis met a property outside the known families — degrade honestly; never invent a proxy.
- `NEEDS_QUORUM_AUDIT`: R distinct refuters could not be instantiated, or R-1 are clones — the panel is vacuous; do not credit.
- `LENS_THEATER`: a declared lens cannot name an attack or only confirms — do not run it; do not cite it as a closure artifact.
- `NEEDS_DISCOVERABILITY`: a claim is self-attested with no repo-derivable pointer — stop until discovered or marked `AXIS_UNPROVEN`.
- `CEILING_NOT_REACHED`: deterministic defects can still leak (unwired gates), a generative axis was skipped without owner deferral, or a declared axis is unproven — closure is to the floor, not the ceiling.

## Done

ADR 0006 is satisfied when: Part A wires the two gates and risk-gates stress; Part B activates the three latent capabilities (synthesis, self-construction, panel) each proven by re-mutation; Part C's lens contract enforces break-mandate, discoverability-first, risk-gating and audit-over-predict; Axes 4-5 are declared owner-deferred extensions; and the release bundle stays excluded until the release ceiling. Reaching the ceiling means the harness can generate its own falsifiable proof and cannot credit it without its own falsifier firing, a deterministic defect cannot survive to audit, a lens cannot survive as theater, and every unproven or deferred axis is declared — not claimed.
