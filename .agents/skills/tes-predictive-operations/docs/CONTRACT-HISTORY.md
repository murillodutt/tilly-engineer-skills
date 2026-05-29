# TES Predictive Operations Contract History

## Purpose

`tes-predictive-operations` is local-only self-consumed development guidance
for deciding how to operate `tes-prospect` and `tes-mine` together during
project reasoning.

## Why This Skill Exists

Project reasoning can over-escalate into a broad planning loop, premature
durable-memory mining, or packaging work before behavior is clear. This skill
keeps that choice small: prospect when the risk is in the plan, mine when the
risk is in language or evidence, alternate only when both are needed, and
package only after the behavior is already understood.

## Origin Signals

| Source | Signal | Confidence |
|--------|--------|------------|
| `.agents/skills/tes-prospect/SKILL.md` | Plan-risk pressure pass with explicit invocation, one question at a time, and a cognitive brake. | high |
| `.agents/skills/tes-mine/SKILL.md` | Language, code-evidence, and durable-knowledge mining pass with explicit invocation and a cognitive brake. | high |
| Maintainer directive, 2026-05-22 | This guidance should be self-consumed locally, not exposed as a user command. | high |
| Maintainer directive, 2026-05-29 | Apply review findings: valid skill packaging, docs/agents trace, local-only placement, and clearer contract memory. | high |

## Source Search Ledger

| Window | Query | Occurrences | Meaning |
|--------|-------|-------------|---------|
| 2026-05-29 review | `tes-predictive-operations` across `.agents/**`, `docs/**`, and `AGENTS.md` | local skill only before repair | The new runtime asset needed an explicit `docs/agents/**` trace. |
| 2026-05-29 review | `tes-prospect` and `tes-mine` references in this skill | direct references in `SKILL.md` and references | The skill is a selector over existing workflows, not a third executor. |

## Contracts Preserved

- Keep `tes-prospect` as the plan-risk pressure pass.
- Keep `tes-mine` as the language, code-evidence, and durable-knowledge mining
  pass.
- Self-consume the mode-selection guidance during project reasoning.
- Do not expose it as a user-invoked skill or command.
- Alternate prospecting and mining deliberately instead of creating a third
  execution engine.
- Use skill-packaging checks only after the target behavior is already clear.
- Write durable context only after a term, relationship, contradiction, or
  decision is resolved and the active workflow authorizes the write.

## Known Failure Modes Prevented

- Treating `prospect`, `mine`, `alternate`, and `package` as one large
  always-on reasoning loop.
- Asking the maintainer to invoke a local meta-skill.
- Packaging a workflow before its behavior is clear.
- Writing durable context from unresolved language, contradiction, or plan risk.
- Editing `tes-prospect` or `tes-mine` while trying to coordinate them.

## Relationship To Other Skills

- `tes-prospect` owns plan-risk pressure.
- `tes-mine` owns language, evidence, and durable-knowledge mining.
- `tes-high-agency-pattern` owns one-skill operating-pattern design.
- `tes-predictive-operations` owns the smallest local mode choice between those
  behaviors during active project reasoning.

## Changelog

| Date | Change | Evidence | Confidence |
|------|--------|----------|------------|
| 2026-05-22 | Created local predictive operations skill for coordinated `tes-prospect` and `tes-mine` use. | Maintainer analysis session. | high |
| 2026-05-22 | Added local skill-packaging check from external `write-a-skill` guidance. | Maintainer-provided external skill excerpt; absorbed as local operating check. | high |
| 2026-05-22 | Slimmed `SKILL.md` to the smallest mode-selection contract and moved details into `references/**`. | Maintainer requested extreme progressive disclosure. | high |
| 2026-05-22 | Changed activation posture from user-invoked to self-consumed local guidance. | Maintainer clarified these skills should be autoconsumed, not invoked. | high |
| 2026-05-22 | Added Operating Temperament mode selection so local skill construction can choose sniper, miner, prospector, builder, gate, or curator behavior. | Maintainer clarified that some skills need questions and verbosity while others must be objective and precise. | high |
| 2026-05-22 | Renamed `operating-temperament.md` to `temperament-mode-selection.md` and added cross-routing to `tes-high-agency-pattern`. | Maintainer senior analysis identified false same-name drift between complementary temperament references. | high |
| 2026-05-22 | Tightened frontmatter description to route active project prospect/mine/alternate/package decisions away from one-skill operating-pattern design. | Maintainer approved P4 trigger-alignment pass after senior review. | high |
| 2026-05-29 | Quoted frontmatter description, added operational contract version, validation, done criteria, OpenAI metadata, expanded contract history, and docs/agents trace expectation. | Read-only review found invalid YAML frontmatter, missing local skill metadata, incomplete Tilly contract history, and missing `docs/agents/**` trace. | high |

## Do Not Lose

This guidance helps the agent decide the smallest useful reasoning mode. It
must not be exposed as a command, must not edit `tes-mine` or `tes-prospect`,
must not become a commercial skill, and must not apply packaging work before
behavior is clear. Keep `SKILL.md` lean; use references for depth. Its
temperament reference chooses the mode; `tes-high-agency-pattern` owns profile
design for one local development-layer skill.
