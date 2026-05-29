---
tds_id: roadmap.goal_super_spec_tes_tts_sequential_convergence
tds_class: roadmap
status: active
consumer: maintainers, tes-tts maintainers, adapter authors, oracle authors, release reviewers, and execution agents
source_of_truth: false
evidence_level: L1
---

# GOAL Super SPEC: TES TTS Sequential Convergence

Status: active execution contract for the `tes-tts` convergence loop.

Capability: evolve `tes-tts` through a circular, sequential loop:

```text
execute -> analyze -> fix -> certify -> create next /goal prompt -> repeat
```

The loop continues until `tes-tts` is either certified for the claimed scope or
explicitly remains proposed/degraded with the next unresolved question named.

## Canonical Artifact

Canonical Super SPEC:
`docs/roadmap/GOAL-SUPER-SPEC-tes-tts-sequential-convergence.md`

Primary executive roadmap:
`docs/roadmap/TES-TTS-SKILL-ROADMAP.md`

Architectural boundary:
`docs/adr/0004-tes-tts-pronunciation-normalization-and-enrichment.md`

Companion SPECs:

- `docs/roadmap/TES-TTS-NORMALIZATION-ARCHITECTURE-SPEC.md`
- `docs/roadmap/TES-TTS-NORMALIZATION-EXECUTION-SPEC.md`

Primary source surfaces:

- `src/adapters/codex/skills/tes-tts/**`
- `src/adapters/claude/skills/tes-tts/**`
- `src/adapters/codex/AGENTS.md`
- `src/adapters/claude/CLAUDE.md`
- `src/adapters/cursor/**`
- `docs/adapters/**`
- `docs/install/COMMAND-TRIGGERS.md`
- `scripts/materialize_adapter.py`
- `scripts/command_trigger_oracle.py`
- `scripts/validate_reference_package.py`

## Current Meaning

This Super SPEC is an execution contract, not delivered certification.

`tes-tts` is a small reactive read-aloud skill. It may prepare speech text,
protect secrets, use local TTS when available, and report `TTS_NOT_AVAILABLE`
honestly. It must not become proactive `speak`, a dependency manager, a bundled
translation stack, or a global provider registry.

Current normalization and pronunciation behavior is proposed and
instruction-level. Provider-backed normalization remains uncertified until
fixtures and probes exist.

## Assumptions

- The user has explicitly forbidden sync until the complete skill is ready,
  certified, and approved.
- ADR 0004 remains proposed until fixtures, probes, adapter validation, and
  maintainer approval converge.
- `tes-tts` and `speak` remain separate: `tes-tts` is reactive, `speak` is
  proactive.
- The default-language selector currently treats explicit user language as
  higher priority than the adapter default language.
- Missing provider support degrades enrichment, not basic read-aloud behavior.
- Each execution unit must finish before the next unit opens.

## Non-Objectives

- Do not run sync, release, push, tag, publish, marketplace, or cloud actions.
- Do not install, download, bundle, or auto-enable provider dependencies.
- Do not persist provider state, voice assignments, or conversion caches.
- Do not import proactive `speak` announcements into `tes-tts`.
- Do not summarize user text unless the user explicitly asks for summary.
- Do not claim library-backed normalization without fixtures and provider
  probes.
- Do not fix only installed target mirrors; package source remains the source
  of truth.

## Central Rule

One loop, one unit, one evidence trail:

```text
select one unit
-> execute the smallest material change
-> analyze the result and false-green risk
-> fix only the observed gap
-> certify with the focused oracle
-> write the next /goal prompt or close convergence
```

Parallel research may inform analysis, but write execution stays serialized.
No new branch of work may open until the current unit has a decision,
evidence, and next prompt.

## Circular Execution Model

Each cycle must follow this shape:

| Phase | Required action | Output |
|-------|-----------------|--------|
| Execute | Materialize the selected unit with the smallest source/doc/oracle change. | Diff for one unit only. |
| Analyze | Review diff, contracts, false-green risk, precision, quality, and efficiency. | Senior analysis note. |
| Fix | Repair only observed defects or contract drift. | Smaller corrected diff. |
| Certify | Run the focused oracle set and classify result. | `PASS`, `DEGRADED`, `NEEDS_REVIEW`, or `BLOCKED`. |
| Next Prompt | Generate the next sequential `/goal` prompt when not converged. | Prompt that preserves current evidence and next unit. |
| Local Commit | Commit the certified local execution when the cycle is authorized. | Final local commit for the execution cycle. |

If certification fails, the next cycle remains on the same unit. Do not advance
to a new unit from a failed or ambiguous cycle.

## Required Preflight

Before every cycle:

1. Run `git status --short --branch --untracked-files=all`.
2. Classify inherited staged changes, current-cycle changes, and unrelated
   changes.
3. Read the current unit in `TES-TTS-SKILL-ROADMAP.md`.
4. Confirm ADR 0004 boundary still permits the intended change.
5. Name the focused oracle before editing.
6. Confirm no sync/release action is being performed.

Stop if the worktree state cannot be classified, the focused oracle cannot be
named, or the change would require a release identity decision before the user
has approved the complete skill.

## Execution Units

| Unit | Objective | Allowed surfaces | Focused oracle |
|------|-----------|------------------|----------------|
| TTS-000 Preflight And Baseline | Classify current staged work, confirm no sync/release, and record the next unit. | docs only unless a validation script is stale. | `git status --short --branch --untracked-files=all`; `python3 scripts/validate_tds.py`. |
| TTS-001 Roadmap And SPEC Coherence | Keep roadmap, ADR 0004, architecture SPEC, execution SPEC, and references consistent. | `docs/roadmap/**`, `docs/adr/0004-*`, `src/adapters/*/skills/tes-tts/references/**`. | `python3 scripts/validate_tds.py`; `python3 scripts/validate_doc_size.py`; targeted `rg` for contradictions. |
| TTS-002 Default-Language Selector | Make the selector precise and fixture-ready: explicit user language, declared adapter default, request language, dominant text, preserve original. | `language-normalization.md`, architecture SPEC, execution SPEC, roadmap. | targeted `rg`; future selector fixtures. |
| TTS-003 Fixture Schema | Define the minimal fixture schema before writing a corpus. | new fixture docs or script under a later accepted path; correlated roadmap/SPEC updates. | schema lint or deterministic self-test when created. |
| TTS-004 Fixture Corpus | Add first-class language and negative fixtures without provider dependencies. | fixture path selected by TTS-003; docs only if schema stays proposed. | fixture schema check. |
| TTS-005 Instruction Normalizer Oracle | Prove instruction-level cache, protected terms, redaction, and no-summary behavior. | new or existing validation script, fixtures, references. | new focused self-test plus `validate_reference_package.py`. |
| TTS-006 Provider Probe Contract | Add no-write local provider probe contract and mocked states. | execution SPEC, optional probe script/fixtures after approval. | mocked probe self-test; negative check for install/download commands. |
| TTS-007 Provider Candidate Review | Rank provider candidates after probe contract exists. | architecture SPEC, provider reference, optional review table. | provider review checklist; no certification claim. |
| TTS-008 Adapter Parity | Keep Codex and Claude skill content behaviorally aligned and Cursor docs honest. | adapter source/docs/scripts. | `quick_validate.py` for Codex/Claude skills; `materialize_adapter.py all --check`; `command_trigger_oracle.py --self-test`. |
| TTS-009 Acceptance And Release Decision | Decide whether ADR 0004 can move to accepted and whether release identity can proceed. | ADR/SPEC/docs/version surfaces only after owner approval. | `npm run commit:check`; release gate only when explicitly authorized. |

Every unit must preserve its identifier. A future `/goal` may expand a unit
into sub-steps, but must not merge, skip, rename, or reorder these units
without maintainer acceptance.

## Senior Analysis Gate

After execution and before fix/certification, analyze:

- quality: does the change improve the exact user-visible `tes-tts` behavior?
- efficiency: did it avoid provider work, release work, or broad refactors
  before fixtures?
- precision: are selector precedence, protected terms, redaction, and no-summary
  rules unambiguous?
- false-green risk: could a validator pass while the skill behavior remains
  wrong?
- boundary drift: did `tes-tts` absorb proactive `speak` behavior?
- evidence sufficiency: does the oracle actually cover the changed behavior?

The analysis must either approve certification or name the smallest fix.

## Fix Gate

Fixes must be scoped to observed defects:

- prefer one source/doc correction over broad rewrites;
- do not add dependencies while repairing instruction-level contracts;
- do not change ADR status as a side effect;
- do not change release identity as a side effect;
- update correlated docs only when the contract actually changed.

If the defect reveals a new hard-to-reverse architectural choice, stop and ask
whether ADR 0004 or a successor ADR should change.

## Certification Gate

Use the smallest relevant oracle first:

```bash
python3 /Users/murillo/.codex/skills/.system/skill-creator/scripts/quick_validate.py src/adapters/codex/skills/tes-tts
python3 /Users/murillo/.codex/skills/.system/skill-creator/scripts/quick_validate.py src/adapters/claude/skills/tes-tts
python3 scripts/materialize_adapter.py all --check
python3 scripts/command_trigger_oracle.py --self-test
python3 scripts/validate_tds.py
python3 scripts/validate_doc_size.py
python3 scripts/validate_reference_package.py
git diff --check
```

Use `npm run commit:check` only for package closure, not for every small
analysis cycle. It cannot replace missing TTS-specific fixtures.

## Next /goal Prompt Contract

At the end of each non-converged cycle, create the next executable `/goal`
prompt in this shape. The prompt is a required circular artifact, not optional
chat garnish:

```text
/goal Continue TES TTS sequential convergence.

Canonical artifact:
docs/roadmap/GOAL-SUPER-SPEC-tes-tts-sequential-convergence.md

Current unit:
TTS-<id> <name>

Certified evidence from prior cycle:
- <oracles and result>
- <changed files or no-material-change rationale>

Task:
Execute only the current unit through:
execute -> analyze -> fix -> certify -> create next /goal prompt -> local commit.

Forbidden:
- no sync, release, push, tag, publish, provider install, provider download,
  proactive speak behavior, global config writes, or durable conversion cache.

Stop states:
BLOCKED, DEGRADED, NEEDS_REVIEW, NEEDS_OWNER_DECISION.
```

If convergence is complete, do not create a next prompt. Report closure state
and remaining release identity decision instead.

## Current Ready /goal Prompt

Prompt artifact:
`docs/roadmap/GOAL-PROMPT-tes-tts-TTS-007-provider-candidate-review.md`

Use this prompt to start the next sequential execution cycle:

```text
/goal Continue TES TTS sequential convergence.

Canonical artifact:
docs/roadmap/GOAL-SUPER-SPEC-tes-tts-sequential-convergence.md

Current unit:
TTS-007 Provider Candidate Review

Certified evidence from prior cycle:
- TTS-006 re-read the execution SPEC provider probe contract, roadmap,
  Super SPEC, providers-and-fallbacks references, and instruction normalizer
  oracle.
- TTS-006 added mocked provider probe fixtures at
  benchmarks/tes-tts/provider-probe-fixtures.json.
- TTS-006 added `scripts/tes_tts_provider_probe_oracle.py --self-test`.
- TTS-006 covered `provider_available`, `provider_not_available`, and
  `provider_needs_review` without probing real providers.
- Ready prompt artifact:
  docs/roadmap/GOAL-PROMPT-tes-tts-TTS-007-provider-candidate-review.md.
- TTS-006 focused oracles passed:
  - `python3 scripts/tes_tts_provider_probe_oracle.py --self-test`
  - `python3 scripts/tes_tts_instruction_normalizer_oracle.py --self-test`
  - `python3 scripts/tes_tts_fixture_schema_oracle.py --self-test`
  - `python3 scripts/validate_tds.py`
  - `python3 scripts/validate_doc_size.py`
  - `python3 scripts/validate_reference_package.py`
  - targeted no-provider/no-install `rg` checks.

Task:
Execute only TTS-007 through the circular sequence:
execute -> analyze -> fix -> certify -> create next /goal prompt -> local commit.

Required actions:
1. Run `git status --short --branch --untracked-files=all`.
2. Re-read architecture SPEC provider candidates, execution SPEC, roadmap,
   provider fallback references, and provider probe oracle.
3. Rank provider candidates after the no-write probe contract exists.
4. Fix only TTS-007 provider-review or governance gaps.
5. Certify with targeted `rg` checks and the smallest docs/package oracles.
6. Create the next `/goal` prompt artifact for TTS-008 if not converged.
7. Commit the local execution as the final action of the cycle.

Forbidden:
- no sync, release, push, tag, publish, provider install, provider download,
  proactive speak behavior, global config writes, or durable conversion cache.

Stop states:
BLOCKED, DEGRADED, NEEDS_REVIEW, NEEDS_OWNER_DECISION.
```

## Stop States

| State | Meaning |
|-------|---------|
| `PASS` | The unit's focused oracle and review gate passed. |
| `DEGRADED` | Basic `tes-tts` remains usable, but enrichment or provider support is partial. |
| `NEEDS_REVIEW` | A maintainer decision is needed before the next unit can open. |
| `NEEDS_OWNER_DECISION` | Scope, release identity, ADR acceptance, or provider posture needs owner choice. |
| `BLOCKED` | Continuing would violate sync/release/provider/privacy/boundary locks. |

## Commit Strategy

This Super SPEC does not authorize remote sync, push, release, tag, publish, or
marketplace actions.

When a cycle is authorized for execution, the final state-changing action must
be a local semantic commit after focused certification passes. Prefer one
semantic commit per completed unit. Until commit authorization exists, staged
local changes may be used as review state, but the agent must not claim sealed
package closure.

Remote sync remains forbidden unless explicitly authorized after full skill
approval.

## Final Delivery Contract

Convergence may be claimed only when:

1. every active unit through the current claimed scope is `PASS` or explicitly
   `DEGRADED` with owner acceptance;
2. ADR 0004 status is still honest;
3. all correlated docs and adapter sources are indexed;
4. focused oracles pass;
5. no sync/release/commit/push/tag is claimed without authorization;
6. the final response names the next unresolved unit or states that no next
   prompt is needed.
