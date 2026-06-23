---
tds_id: roadmap.goal_super_spec.goal_maestro_progressive_disclosure
tds_class: roadmap
status: active
consumer: maintainers, Goal Maestro authors, adapter authors, oracle authors, release reviewers, and execution agents
source_of_truth: true
evidence_level: L2
tver: 0.1.0
---

# Goal Maestro Progressive Disclosure Super SPEC

Status: active pre-implementation SPEC.

Purpose: reduce `tes-goal-maestro/SKILL.md` below the recommended Claude and
Codex root-skill budget without compacting, deleting, or weakening certified
behavior. The root skill becomes an executive router; references, templates,
and oracles carry the full operational contract.

## Reverse Analysis

Current root line count is close to the hard document-size ceiling. The defect
is not that the skill knows too much; the defect is that too much of the known
contract is always loaded from `SKILL.md`.

Reverse failure path:

1. If `SKILL.md` keeps growing, future fixes will fail document-size gates or
   force unsafe compression.
2. If lines are deleted to satisfy the budget, Goal Maestro loses execution
   fidelity, loop safety, or structural method enforcement.
3. If detail is moved into the wrong reference, the root becomes smaller but
   the executor may not load the needed contract.
4. If oracles only count terms in the aggregate, the root may become thin while
   critical references drift or disappear.

The correct move is progressive disclosure with explicit load routing:

```text
SKILL.md decides what to load.
References define how to execute.
Templates preserve exact output shape.
Oracles prove nothing was lost.
```

## Three-Layer Mental Simulation

### Layer 1: Root Skill Layer

Goal: `SKILL.md` remains a high-signal executive contract, not a full manual.

Expected shape:

- explicit invocation and non-activation boundary;
- central rule and current operational version;
- mandatory load-routing table;
- short workflow order;
- essential stop states;
- critical locks that prevent immediate damage;
- done criteria.

Failure blocked: root skill exceeds recommended budget, duplicates references,
or lets future agents edit root prose instead of the proper contract surface.

Target budget: 180-260 lines, with a hard stop before 300.

### Layer 2: Lazy Contract Layer

Goal: all detailed execution behavior remains available, but only through
purpose-owned references or templates.

Expected shape:

| Surface | Authority |
|---------|-----------|
| `references/materialization-tree.md` | Tree schema, execution units, material diff, commit rhythm, final delivery |
| `references/quality-gates.md` | Readiness statuses, weak-prompt rejection, closeout checks, stop-state mapping |
| `references/execution-loop-runner.md` | `--execute-loop`, `ACTIVE_SPEC`, attempts, repair, ledger, audit |
| `references/structural-method.md` | Engineering Method Profile, Method Enforcement Packet, structural probes, handoff, `bug_vs_architecture` |
| `references/subagents-and-oracles.md` | Role ownership, reviewer duties, reusable oracle patterns |
| `templates/maestral-goal-prompt.template.md` | Full `/goal` prompt template and evidence block shape |

Failure blocked: text is moved from the root into an overloaded reference,
causing the same line-budget failure elsewhere.

Reference budgets:

- primary references target <= 420 lines;
- no reference may exceed 500 lines;
- template may be longer only if `validate_doc_size.py` explicitly governs the
  path or the template is split.

### Layer 3: Oracle And Materialization Layer

Goal: the package proves the split preserves behavior across product source,
local maintainer mirrors, and generated adapters.

Expected shape:

- `command_trigger_oracle.py` validates the contract across root, references,
  and templates, not root-only term presence;
- `validate_doc_size.py` catches root/reference growth before commit;
- `materialize_adapter.py all --check` proves source-to-adapter delivery;
- byte parity is preserved for Codex and Claude Goal Maestro directories;
- `validate_reference_package.py` and `npm run commit:check` remain final gates.

Failure blocked: a smaller root falsely passes while generated adapters,
bootloaders, or prompt templates lose the method.

## Central Rule

```text
No behavior is removed to reduce line count; behavior moves only to a named
surface with a load rule and an oracle.
```

## Non-Objectives

- No rewrite of Goal Maestro behavior.
- No change to explicit trigger semantics.
- No new command or CLI runner.
- No remote push, tag, release, or publication in this SPEC.
- No canary execution in this SPEC; canary belongs after implementation and
  certification.
- No broad grammar rewrite of every reference.

## Protected Baseline

Last-known-good baseline:

- `tes.goal_maestro@0.3.6`;
- `0.3.187` package identity;
- `npm run commit:check` PASS after structural method loop enforcement;
- Codex and Claude Goal Maestro source parity;
- `.agents/**` and `.claude/**` local mirror parity;
- public bundle `0.3.187` certified.

Protected invariants:

- explicit invocation only;
- no implementation execution by default;
- Super SPEC artifact is the only default file write;
- Next Prompt Handoff is opt-in and chat-only outside `--execute-loop`;
- `--execute-loop` remains explicit, parent-owned, sequential, local-commit
  only, and audit-closed;
- reference implementations remain baseline-only, never execution credit;
- Structural Method Gate keeps `Engineering Method Profile`,
  `STRUCTURAL_METHOD=<profile-id>`, source probes, structural handoff,
  `bug_vs_architecture`, and `structural_repair`;
- no remote sync without explicit user authorization.

## Proposed Topology

Create one new reference and one new template directory:

```text
src/adapters/codex/skills/tes-goal-maestro/
  SKILL.md
  references/
    structural-method.md
    materialization-tree.md
    quality-gates.md
    execution-loop-runner.md
    subagents-and-oracles.md
  templates/
    maestral-goal-prompt.template.md
```

Mirror the same topology to:

- `src/adapters/claude/skills/tes-goal-maestro/**`;
- `.agents/skills/tes-goal-maestro/**`;
- `.claude/skills/tes-goal-maestro/**`.

## Decision Ledger

| Decision | Rationale | Risk | Oracle |
|----------|-----------|------|--------|
| Root becomes router | Root is always loaded once skill triggers; detail belongs to lazy surfaces | Missing load route | `command_trigger_oracle.py --self-test` |
| Structural method gets its own reference | It is now a full method lane, not a subsection | Fragmentation | Required root load route + term oracle |
| Prompt template moves to `templates/` | It is output shape, not reasoning contract | Template not loaded | Generated-prompt fixture in oracle |
| Locks split into critical root locks and detailed reference locks | Root keeps damage prevention; references keep exhaustive cases | Weak root safety | quality-gate fixture and root term checks |
| No semantic compression | Maintains exact concepts while reducing always-loaded body | More files | doc-size and reference-package checks |

## Execution Units

### SPEC-000: Reverse Baseline And Load Map

Objective: prove the current root bloat and design the load map before moving
text.

Allowed files:

- this Super SPEC;
- read-only inspection of `src/adapters/*/skills/tes-goal-maestro/**`;
- read-only inspection of `.agents/**` and `.claude/**` mirrors.

Tasks:

1. Capture line counts for root, references, agent manifest, and future
   template candidates.
2. Classify each `SKILL.md` section as root, reference, template, or duplicate.
3. Produce a section-to-destination map before editing implementation files.
4. Confirm no behavior will be deleted for line count.

Focused oracle:

```bash
wc -l src/adapters/codex/skills/tes-goal-maestro/SKILL.md src/adapters/codex/skills/tes-goal-maestro/references/*.md
git diff --check
```

Commit: none unless the execution framework requires a planning commit.

### SPEC-001: Create Structural Method Reference

Objective: move the full Structural Method Gate details into
`references/structural-method.md` while leaving a short root route.

Allowed files:

- `src/adapters/codex/skills/tes-goal-maestro/SKILL.md`;
- `src/adapters/codex/skills/tes-goal-maestro/references/structural-method.md`;
- directly correlated Claude/local mirrors after source is correct.

Required content:

- Engineering Method Profile;
- Method Enforcement Packet;
- `STRUCTURAL_METHOD=<profile-id>`;
- topology budget;
- allowed modules/internal sections;
- structural debt budget;
- structural source probes;
- structural handoff;
- `bug_vs_architecture`;
- `structural_repair`;
- single-file exception rule.

Focused oracle:

```bash
rg -n "STRUCTURAL_METHOD=|bug_vs_architecture|structural_repair|structural handoff" src/adapters/codex/skills/tes-goal-maestro
python3 scripts/command_trigger_oracle.py --self-test
```

Stop condition: if any structural-method term is present only in root or only
in an unreferenced file, stop with `NEEDS_TREE_REPAIR`.

### SPEC-002: Move Prompt Template To Templates

Objective: preserve the full `/goal` output shape without keeping the complete
prompt body in the root skill or an overloaded reference.

Allowed files:

- `src/adapters/codex/skills/tes-goal-maestro/references/maestral-goal-prompt.md`;
- `src/adapters/codex/skills/tes-goal-maestro/templates/maestral-goal-prompt.template.md`;
- correlated Claude/local mirrors.

Tasks:

1. Keep `references/maestral-goal-prompt.md` as the template router and
   hardening checklist.
2. Move the large literal prompt body to `templates/`.
3. Ensure the reference explicitly requires loading the template before
   returning `READY_GOAL_PROMPT`.
4. Update oracle fixtures to inspect template terms.

Focused oracle:

```bash
python3 scripts/command_trigger_oracle.py --self-test
python3 scripts/validate_reference_package.py
```

Stop condition: if generated-prompt fixture checks no longer fail when template
terms are removed.

### SPEC-003: Thin Root Skill

Objective: reduce `SKILL.md` to an executive router while preserving all
trigger, stop, lock, and done semantics.

Allowed files:

- `src/adapters/codex/skills/tes-goal-maestro/SKILL.md`;
- correlated Claude/local mirrors.

Root must keep:

- invocation contract;
- central rule;
- progressive-disclosure load routing;
- readiness score pointer;
- workflow order;
- critical locks;
- done criteria.

Root must not keep:

- full prompt template;
- detailed execution loop runner;
- detailed structural method packet;
- exhaustive status definitions;
- exhaustive lockbook that exists in references.

Focused oracle:

```bash
wc -l src/adapters/codex/skills/tes-goal-maestro/SKILL.md
python3 scripts/validate_doc_size.py
python3 scripts/command_trigger_oracle.py --self-test
```

Acceptance: Codex and Claude root Goal Maestro `SKILL.md` files are between
180 and 300 lines, preferably <= 260.

### SPEC-004: Oracle And Parity Hardening

Objective: make the split provable across source, local mirrors, and
materialized adapters.

Allowed files:

- `scripts/command_trigger_oracle.py`;
- `scripts/validate_reference_package.py` only if new required paths must be
  listed;
- `src/adapters/**/skills/tes-goal-maestro/**`;
- `.agents/**`;
- `.claude/**`.

Tasks:

1. Add new reference/template paths to required package paths if needed.
2. Make command-trigger checks validate root, references, and template terms.
3. Add negative fixtures for missing structural reference route and missing
   prompt template terms.
4. Preserve Codex/Claude parity and local bootloader mirror parity.

Focused oracle:

```bash
python3 scripts/command_trigger_oracle.py --self-test
python3 scripts/validate_reference_package.py
python3 scripts/materialize_adapter.py all --check
diff -qr src/adapters/codex/skills/tes-goal-maestro src/adapters/claude/skills/tes-goal-maestro
```

### SPEC-005: Release Identity And Full Certification

Objective: close the delivered-behavior package change with the appropriate
release identity decision and full gate.

Tasks:

1. Run `python3 scripts/tes_bump.py --target . --governance-check`.
2. If delivered behavior changed, apply patch bump and regenerate public bundle.
3. Run focused gates, then `npm run commit:check`.
4. Commit locally only; no remote push unless explicitly authorized.

Focused oracle:

```bash
python3 scripts/tes_bump.py --target . --governance-check
npm run commit:check
git status --short --branch --untracked-files=all
```

Stop condition: any doc-size failure, oracle drift, parity drift, stale public
bundle SHA, or remote action requirement without explicit authorization.

## Senior Audit After SPEC

Before implementation, run an audit against this Super SPEC:

1. Does every proposed move have a source, destination, and oracle?
2. Does root thinning preserve all protected invariants?
3. Does any reference exceed or approach the document-size ceiling after the
   move?
4. Does the command-trigger oracle prove loss, or only term presence?
5. Does the plan avoid release/public work until implementation actually
   changes delivered behavior?
6. Does the plan preserve the two-layer model: product source in `src/**`,
   local development mirrors in `.agents/**` and `.claude/**`?

Audit statuses:

- `READY_FOR_IMPLEMENTATION`
- `NEEDS_SPEC_REPAIR`
- `NEEDS_OWNER_DECISION`
- `BLOCKED`

## Final Acceptance

- `SKILL.md` root is below the recommended budget without semantic loss.
- Full behavior remains in references/templates with explicit load routes.
- Structural method enforcement survives the split.
- Prompt template survives as exact output shape.
- Codex and Claude sources stay aligned.
- Local development mirrors stay aligned.
- `validate_doc_size.py`, `command_trigger_oracle.py --self-test`,
  `validate_reference_package.py`, `materialize_adapter.py all --check`, and
  `npm run commit:check` pass before closure.
