---
tds_id: roadmap.tes_align_semantic_drift_hardening_super_prompt
tds_class: roadmap
status: proposed
consumer: maintainers, adapter authors, and TES alignment certifiers
source_of_truth: false
evidence_level: L2
tver: 0.1.0
---

/goal TES Align Semantic Drift Hardening Super Prompt

This prompt defines the next improvement wave for `/tes-align`.

It is based on a real certification failure pattern: a target project passed
the structural project-alignment oracle while current documentation still
contained stale domain claims and retired implementation vocabulary. The
failure was not formatting. The failure was semantic: `/tes-align` could prove
that the mesh shape existed, but it could not prove that the mesh had absorbed
the latest project truth or removed language that the project had already
retired.

## Copy-Paste Execution Prompt

You are operating inside `/Users/murillo/Dev/tilly-engineer-skills`.

Your mission is to harden `/tes-align` across adapter skill surfaces and
project-alignment oracles so TES can detect and correct project-specific
semantic drift, not only structural mesh completeness.

Do not patch installed target-project mirrors as the source of truth. Patch the
TES reference package first. Target projects are canaries and certification
fixtures only.

### Origin

A <project-A> certification loop exposed this class of false PASS:

- `docs/agents/**` had the expected operating mesh shape.
- The alignment oracle passed because required files, frontmatter, roadmap
  sections, wikilinks, and evidence packet shape existed.
- Later review found stale current-state language and retired implementation
  terms still present in documentation.
- The target project had already moved on, but `/tes-align` had no semantic
  residue gate to make that drift fail.

This means `/tes-align` must evolve from structural reconciliation to semantic
truth reconciliation.

### Required Reading

Before editing, read these package anchors:

- `AGENTS.md`
- `docs/INDEX.md`
- `docs/mesh/TES-ALIGN-SKILL-SOURCE-OF-TRUTH.md`
- `src/adapters/codex/skills/tes-align/SKILL.md`
- `src/adapters/claude/skills/tes-align/SKILL.md`
- `src/adapters/cursor/**` routing and prompt surfaces, if present
- `scripts/project_alignment_oracle.py`
- `scripts/materialize_adapter.py`
- `scripts/adapter_parity_readiness.py`
- `docs/adapters/MATERIALIZATION.md`
- `docs/evals/PARITY-GATE.md`

If `docs/mesh/TES-ALIGN-SKILL-SOURCE-OF-TRUTH.md` is stale under its own
`source_refresh_policy`, refresh or explicitly revalidate it before using it
as construction truth.

### Core Objective

Implement a portable Semantic Residue Gate for `/tes-align`.

The gate must let each target project define stale terms, retired claims,
forbidden vocabulary, obsolete architecture names, and required freshness
signals without hard-coding <project-A>-specific Intel language into TES itself.

The result must be:

```text
/tes-align -> structure check + evidence freshness + project semantic residue gate
```

`/tes-align` may still finish with `NEEDS_REVIEW`, `BLOCKED`, or `DEFERRED`
when semantic truth cannot be resolved. It must not report PASS when stale
current-state claims remain in active docs.

### Design Requirements

1. Add a project-local semantic residue contract.

   Define the smallest portable contract that lets a target project declare
   terms or claim patterns that must not appear in active documentation after a
   decision, migration, or certification lane closes.

   Prefer an explicit target-project file under `docs/agents/contracts/**` or
   another already-governed `docs/agents/**` contract path if the target owns a
   stronger convention.

   The contract must support at least:

   - forbidden literal terms;
   - forbidden regex patterns;
   - scope roots to scan, defaulting to `docs/agents/**`;
   - allowed historical paths or evidence paths when a retained timeline must
     mention the old term;
   - reason or successor language for each entry;
   - severity as `fail`, `needs_review`, or `warn`;
   - expiration or review date when appropriate.

2. Add freshness reconciliation.

   `/tes-align` must compare current mesh claims against the latest relevant
   evidence, ADRs, decisions, and change logs. It must detect when a newer
   evidence packet or decision introduces a current claim that `PROJECT-STATE`,
   `PROJECT-ROADMAP`, `EXECUTION-LINE`, or `CONTEXT` failed to absorb.

   Use this precedence:

   ```text
   accepted ADRs and active decisions
   -> current project-state/roadmap/execution mesh
   -> latest retained evidence and changelog packets
   -> historical evidence and generated inventories
   ```

   Historical evidence may remain historical, but it must not silently outrank
   a newer active decision.

3. Update `/tes-align` skill behavior across platforms.

   Update adapter skill sources under:

   - `src/adapters/codex/skills/tes-align/**`
   - `src/adapters/claude/skills/tes-align/**`
   - `src/adapters/cursor/**` only if Cursor exposes equivalent trigger or
     routing text for `/tes-align`

   Keep `SKILL.md` concise. Put deeper implementation guidance in a governed
   reference document only if the skill would otherwise become bloated.

   The skill body must require:

   - reading recent evidence and decisions before claiming alignment;
   - classifying contradictions as first-class evidence;
   - running the Semantic Residue Gate before PASS;
   - reporting exact stale terms and paths when the gate fails;
   - refusing to call scaffold output deep alignment.

4. Harden `scripts/project_alignment_oracle.py`.

   Extend the oracle so it can load the project-local semantic residue contract
   and fail or warn based on severity.

   The implementation must avoid naive substring bugs. Use explicit regex
   boundaries or configured patterns so a term like `<storage-backend>` does not match an
   unrelated word such as `do<storage-backend>`.

   The oracle must:

   - scan active project docs by default;
   - respect configured excluded paths;
   - support allowlisted historical evidence;
   - produce machine-readable failures;
   - include self-tests for at least one semantic drift fixture;
   - keep the existing structural checks intact.

5. Add an adversarial fixture.

   Build a minimal fixture where the old oracle would pass because all mesh
   files exist, but a current active doc still contains a retired term or
   stale claim. The improved oracle must fail this fixture.

   Also include a positive fixture where a historical evidence packet retains
   the same old term under an explicit allowlist, and the oracle passes.

6. Preserve adapter parity.

   After changing sources, run materialization checks. The delivered behavior
   must be consistent across Codex and Claude adapter outputs. Cursor must be
   updated only where its adapter model actually owns an equivalent surface.

   Do not create a fake Cursor skill folder just for symmetry if Cursor uses a
   different routing contract.

7. Keep target projects out of TES source.

   <project-A>, Intel, and any other project may be used as real canary context, but
   their domain-specific terms must not be hard-coded into TES package logic.

   A target project may define:

   ```text
   retired term -> forbidden in active docs -> allowed only in named evidence
   ```

   TES defines the mechanism. The target defines the vocabulary.

### Non-Goals

- Do not redesign the entire TES mesh.
- Do not replace `/tes-align` with `/tes-doctor`.
- Do not add LLM/RAG requirements.
- Do not require Obsidian runtime state.
- Do not mutate installed target mirrors as source behavior.
- Do not hard-code <project-A>, Intel, <storage-backend>, S3, <archive-format>, or any other project-specific
  vocabulary into generic TES code.
- Do not delete historical evidence merely because it contains old language.
- Do not publish, push, tag, or release remotely unless the maintainer asks.

### Expected Implementation Shape

Prefer a small implementation:

```text
docs/mesh/TES-ALIGN-SKILL-SOURCE-OF-TRUTH.md
  -> describes semantic residue and freshness responsibilities

src/adapters/{codex,claude}/skills/tes-align/SKILL.md
  -> concise runtime instruction for agents

scripts/project_alignment_oracle.py
  -> portable contract loader and semantic residue checks

tests or self-test fixtures
  -> old structural PASS becomes semantic FAIL

docs/evidence/current or docs/evidence/reports/YYYY/MM/DD
  -> retained certification packet
```

If a new reference file is necessary, place it under `docs/mesh/**` and index
it through TDS. Do not scatter duplicated prompt text into every adapter.

### Acceptance Gates

Run the smallest focused checks first, then the package gates:

```bash
python3 scripts/project_alignment_oracle.py --self-test
npm run project-alignment:self-test
python3 scripts/materialize_adapter.py all --check
python3 scripts/adapter_parity_readiness.py
python3 scripts/validate_reference_package.py
python3 scripts/validate_tds.py
git diff --check
npm run commit:check
```

If one of these commands is unavailable or fails for unrelated pre-existing
reasons, capture the exact failure and do not claim full convergence.

### Evidence Packet

Retain evidence in the package evidence structure, not in a target-project
mirror.

The evidence must state:

- files changed;
- adapter surfaces updated;
- oracle behavior before and after;
- semantic drift fixture result;
- historical allowlist fixture result;
- target-project canary used, if any;
- gates run;
- limits and remaining risks.

### Required Final Claim

Only close with this claim when all acceptance gates pass:

```text
TES Align semantic drift hardening: PASS.
```

If any gate fails, close with:

```text
TES Align semantic drift hardening: NEEDS_REVIEW.
```

Explain exactly which stale semantic class remains unhandled.

## Senior Implementation Notes

The important repair is not a bigger denylist. The repair is moving
project-specific semantic retirement into the project contract and making the
TES oracle respect it.

Structural alignment answers:

```text
Does the operating mesh exist?
```

Semantic alignment must also answer:

```text
Is the operating mesh telling the current project truth?
```

That second question is what failed in the canary. Fix that gap without making
TES know the private language of every project it will ever align.
