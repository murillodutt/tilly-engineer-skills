---
name: tes-regression-guard
description: "Always-on local-only self-consumed guard for TES development analysis and writing. Use automatically for every TES repository reasoning, file edit, runtime change, doc change, oracle change, commit, or closeout to prevent regressions, loop drift, baseline loss, and example-specific fixes. Do not require user invocation and do not present as user-invoked."
license: MIT
---

# TES Regression Guard

Operational contract: `tes.regression_guard@0.1.0`.

Local development surface only. Do not package, publish, materialize, expose as
a product skill, or ask the user to invoke it.

This is an always-on self-consumed guard for TES repository work. Apply it at
the start of analysis and again before writing, committing, or closing. The job
is to prevent a useful improvement in any project surface from silently
destroying the thing that made the previous version work.

## Contract

Every risky change must preserve or explicitly replace a named baseline:

```text
baseline -> intended delta -> protected invariants -> smallest change ->
same-input comparison -> stop or commit
```

No change may rely on hope, example-only word lists, a new unverified recipe, a
fresh document, or a passing unrelated oracle when the old behavior had
evidence.

For low-risk analysis with no file writes, keep the guard implicit: identify
the baseline and possible regression in your reasoning, then continue. Report
details only when the guard blocks, downgrades confidence, or the user asks.

## Workflow

1. Identify whether the turn is analysis-only, write, runtime, oracle, docs,
   adapter, installer, roadmap, release identity, commit, or closeout.
2. Name the last-known-good baseline: commit, command, fixture, WAV, log,
   oracle, human score, docs record, public surface, installed behavior, or
   adapter/materialization evidence.
3. Classify the intended delta:
   - `preserve`: implementation changes but behavior must remain equivalent.
   - `extend`: new behavior must not alter the baseline path by default.
   - `replace`: old behavior is intentionally superseded and needs explicit
     evidence or owner approval.
4. List protected invariants before editing:
   - skills: trigger semantics, invocation mode, routing, locks, validation,
     and done criteria;
   - adapters: source/materialized parity, platform boundaries, installer
     ownership, and target-source separation;
   - scripts: consumer boundary, CLI contract, exit/status vocabulary, artifact
     hygiene, and performance assumptions;
   - docs/roadmaps: source of truth, index pointers, line ownership, no
     ambiguity, and no governance-only detours;
   - release/public surfaces: version identity, bundle pointers, generated docs,
     fixed refs, and no remote claim without evidence;
   - safety: secrets, command no-execute posture, private vocabulary, rollback,
     and no destructive default.
5. Prefer a general mechanism over special-case literals. A hard-coded list is
   allowed only when it is data, schema, or contract backed; otherwise it is a
   regression seed.
6. Patch the smallest surface that explains the defect.
7. Re-run the same-input comparison against the relevant baseline. For docs,
   compare rendered/generated outputs or index contracts. For adapters, compare
   materialized surfaces. For scripts, compare CLI payloads and exit behavior.
8. If the comparison regresses the baseline, stop, revert or gate the new path
   behind an opt-in flag. Do not stack compensating special cases.

## Stop Conditions

- The baseline cannot be identified and the change can affect behavior.
- The new path changes defaults without explicit replacement evidence.
- The fix depends on narrow examples instead of a stable rule or data surface.
- The comparison cannot be run for the risk being claimed.
- A regression is observed and no rollback or opt-in gate is applied.
- A documentation or roadmap update hides a product regression behind new
  wording.
- A generated or materialized surface is not checked after source changes.

## Output

Use compact prose only when useful or when the guard changes the decision:

- Baseline
- Intended delta
- Protected invariants
- Comparison evidence
- Decision: `PASS`, `DEGRADED`, `NEEDS_REVIEW`, or `BLOCKED`

## Validation

When this skill changes, run:

```bash
python3 $CODEX_HOME/skills/.system/skill-creator/scripts/quick_validate.py .agents/skills/tes-regression-guard
```

## Done

`tes-regression-guard` is done when the risky change has either preserved the
baseline with comparable evidence, been gated behind opt-in, or stopped before
creating a regression loop.

## Locks

- Do not convert this local guard into shipped user documentation.
- Do not require explicit invocation.
- Do not announce routine use unless it affects the answer.
- Do not create governance-only cycles.
- Do not let a passing oracle replace human-rated audio evidence when the risk
  is speech quality.
- Do not let a passing source check replace materialized adapter, public docs,
  installer, or runtime evidence when those surfaces can regress.
- Do not bury regressions under new prompts, roadmaps, or broad refactors.
