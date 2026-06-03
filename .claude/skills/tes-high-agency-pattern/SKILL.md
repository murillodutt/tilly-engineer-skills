---
name: tes-high-agency-pattern
description: "Local-only self-consumed guidance for designing or reviewing one local development-layer skill/workflow operating pattern: agency, question budget, verbosity, evidence posture, output shape, and packaging discipline. Use when refining how a skill should behave. Prefer tes-predictive-operations for choosing prospect/mine/alternate/package modes during active project reasoning. Do not present as user-invoked."
license: MIT
---

# TES High-Agency Pattern

Operational contract: `tes.high_agency_pattern@0.1.0`.

Local development surface only. Do not package, publish, materialize, or treat
as distributable TES.

Self-consume only while already working on local skill or workflow design. Do
not ask the user to invoke this skill. `tes-mine` and `tes-prospect` are
reference skills; do not edit them.

Prefer `tes-predictive-operations` when the active decision is how to alternate
prospecting, mining, and packaging during project reasoning.

## Contract

High-agency work is conservative at activation and intense after activation:
explicit trigger, proactive posture, evidence before questions, one risk at a
time, recommended answer, cognitive brake, and no artifact until resolution.

This meta-skill remains self-consumed. The explicit-trigger rule applies to the
target skill or workflow being designed, not to this local review lens.

Load references only when needed:

- `references/high-agency-pattern.md` for pattern details.
- `references/temperament-profiles.md` for matching a skill's agency,
  verbosity, question budget, and write posture to its job.
- `references/skill-packaging.md` for description, disclosure, scripts, and
  adoption checks.

## Workflow

1. Identify the target local workflow or skill.
2. Name the transferable pattern, risk, or packaging issue.
3. Check whether high agency improves precision.
4. Recommend the smallest local adjustment.
5. State what must remain local and unpromoted.

## Output

- `Pattern`
- `Why it works`
- `Local application`
- `Do not promote`
- `Brake`
- `Packaging` when relevant

## Validation

When this skill changes, run:

```bash
python3 $CODEX_HOME/skills/.system/skill-creator/scripts/quick_validate.py .agents/skills/tes-high-agency-pattern
```

## Done

`tes-high-agency-pattern` is done when one target skill or workflow has a
smaller operating pattern, a named drift lock, and an explicit boundary for what
must remain local and unpromoted.

## Locks

- Do not modify `src/adapters/**`.
- Do not edit `tes-mine` or `tes-prospect`.
- Do not expose this as a user command or ask the user to invoke it.
- Do not create public docs, installer docs, or package manifests.
- Do not convert local observations or external input into commercial claims.
- Do not import external skill text verbatim when local principles are enough.
