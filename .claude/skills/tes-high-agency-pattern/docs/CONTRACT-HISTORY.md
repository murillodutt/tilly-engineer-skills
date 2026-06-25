# TES High-Agency Pattern Contract History

## Purpose

`tes-high-agency-pattern` is local-only reference development guidance that extracts the operating pattern proven by `tes-mine` and `tes-prospect` without changing those reference skills or promoting the pattern into distributable TES.

## Why This Skill Exists

Some local development-layer skills benefit from high agency after activation, but that pattern is dangerous if it becomes always-on, verbose by default, or commercialized before evidence proves it useful. This skill preserves the portable operating pattern while keeping it local, conservative at activation, and bounded to one target skill or workflow at a time.

## Origin Signals

| Source | Signal | Confidence |
|--------|--------|------------|
| `.agents/skills/tes-prospect/SKILL.md` | Explicit invocation, proactive pressure, one question at a time, and cognitive brake. | high |
| `.agents/skills/tes-mine/SKILL.md` | Evidence-first mining, one question at a time, durable writes only after resolution, and cognitive brake. | high |
| Maintainer directive, 2026-05-22 | The pattern was originally made automatic locally and not exposed as a user command. | historical |
| Maintainer directive, 2026-06-24 | Local development meta-skills should not auto-load when they block high-agency execution; keep this as a reference lens and honor no-skill runs. | high |
| Maintainer directive, 2026-05-29 | Apply review findings: valid skill packaging, docs/agents trace, local-only placement, and clearer contract memory. | high |

## Source Search Ledger

| Window | Query | Occurrences | Meaning |
|--------|-------|-------------|---------|
| 2026-05-29 review | `tes-high-agency-pattern` across `.agents/**`, `docs/**`, and `AGENTS.md` | local skill only before repair | The new runtime asset needed an explicit `docs/agents/**` trace. |
| 2026-05-29 review | `explicit invocation` in `tes-prospect`, `tes-mine`, and this skill | direct conceptual lineage | The explicit-trigger rule belongs to target workflows; this meta-skill is now a local reference lens. |

## Contracts Preserved

- Keep `tes-mine` and `tes-prospect` untouched as reference skills.
- Use the high-agency pattern only as a local reference during skill/workflow design.
- Do not expose it as a user-invoked skill or command.
- Apply explicit activation, proactive posture, evidence-before-question, one-risk-at-a-time operation, recommended answers, cognitive brake, and resolved-output discipline only when they improve precision.
- Treat external skill-design input as packaging reinforcement, not as a new authority layer.
- Keep commercial/public TES surfaces out of scope.

## Known Failure Modes Prevented

- Turning a local design lens into an always-on user command.
- Applying high agency to skills that need terse diagnostics or gate output.
- Asking many questions at once instead of resolving one risk at a time.
- Producing artifacts before the target pattern resolves.
- Importing external skill text or commercial claims as TES authority.

## Relationship To Other Skills

- `tes-prospect` proves the plan-risk pressure side of the pattern.
- `tes-mine` proves the language, evidence, and durable-memory side of the pattern.
- `tes-predictive-operations` chooses prospect/mine/alternate/package modes during active reasoning.
- `tes-high-agency-pattern` reviews or designs one local skill/workflow pattern.

## Changelog

| Date | Change | Evidence | Confidence |
|------|--------|----------|------------|
| 2026-05-22 | Created local high-agency pattern skill from `tes-mine` and `tes-prospect` learning. | Maintainer analysis session. | high |
| 2026-05-22 | Added local skill-packaging reinforcement from external `write-a-skill` guidance. | Maintainer-provided external skill excerpt; absorbed as local principles, not copied as product surface. | high |
| 2026-05-22 | Slimmed `SKILL.md` to a local routing contract and moved detail into `references/**`. | Maintainer requested extreme progressive disclosure. | high |
| 2026-05-22 | Changed activation posture from user-invoked to automatic local guidance. | Maintainer clarified these skills should be auto-loaded, not invoked. | historical |
| 2026-05-22 | Added local Operating Temperament guidance for sniper, miner, prospector, builder, gate, and curator skill design. | Maintainer clarified that the development layer should learn how to create powerful skills with different verbosity and question profiles. | high |
| 2026-05-22 | Renamed `operating-temperament.md` to `temperament-profiles.md` and added cross-routing to `tes-predictive-operations`. | Maintainer senior analysis identified false same-name drift between complementary temperament references. | high |
| 2026-05-22 | Tightened frontmatter description to route one-skill operating-pattern design away from active project mode selection. | Maintainer approved P4 trigger-alignment pass after senior review. | high |
| 2026-05-29 | Quoted frontmatter description, added operational contract version, clarified automatic versus explicit-target activation, added validation, done criteria, OpenAI metadata, expanded contract history, and docs/agents trace expectation. | Read-only review found invalid YAML frontmatter, ambiguous automatic placement, missing local skill metadata, incomplete Tilly contract history, and missing `docs/agents/**` trace. | high |
| 2026-06-24 | Demoted from automatic behavior to explicit local reference guidance that honors owner-requested no-skill runs. | Maintainer directive in current session; bootloader update. | high |

## Do Not Lose

This skill is a local learning lens for the agent to consult explicitly. It must not be exposed as a command, must not become a commercial skill, must not weaken or edit `tes-mine` or `tes-prospect`, and must not promote external guidance before repeated local evidence shows it improves precision without increasing contextual noise. Keep `SKILL.md` lean; use references for depth. Its temperament reference defines profiles; `tes-predictive-operations` owns mode selection during active reasoning.
