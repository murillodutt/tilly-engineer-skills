---
name: tes-predictive-operations
description: Local-only self-consumed guidance for choosing how to operate tes-prospect and tes-mine together during project reasoning. Do not present as a user-invoked skill; auto-consume when already balancing planning pressure, evidence mining, or local skill packaging.
license: MIT
---

# TES Predictive Operations

Local development surface only. Do not package, publish, materialize, or treat
as distributable TES.

Self-consume only while already balancing planning pressure, evidence mining,
or local skill packaging. Do not ask the user to invoke this skill.
`tes-prospect` and `tes-mine` are reference skills; do not edit them.

## Contract

Use the smallest reasoning mode:

- `prospect`: risk is in the plan, boundary, dependency, or next decision.
- `mine`: risk is in language, code evidence, contradiction, or durable memory.
- `alternate`: pressure exposes risk, mining checks evidence, pressure returns
  with a sharper decision.
- `package`: behavior is clear, but the local skill surface needs tightening.

Load references only when needed:

- `references/predictive-operations.md` for mode details.
- `references/skill-packaging.md` for packaging checks.

## Brake

On `pause`, `pausa`, `freia`, `segura`, `para`, `hold`, `step back`,
`volta um nivel`, or `resuma onde estamos`, stop pressure, summarize state, and
wait for explicit resume.

## Output

- `Mode`
- `Reason`
- `Next question/check`
- `Recommended answer`
- `Write policy`
- `Packaging check` when relevant

## Locks

- Do not modify `src/adapters/**`.
- Do not edit `tes-mine` or `tes-prospect`.
- Do not expose this as a user command or ask the user to invoke it.
- Do not create a third commercial skill or execution engine.
- Do not ask multiple questions at once.
- Do not package an unclear workflow.
