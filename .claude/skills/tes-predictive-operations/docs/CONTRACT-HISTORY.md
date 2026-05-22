# TES Predictive Operations Contract History

## Purpose

`tes-predictive-operations` is local-only self-consumed development guidance
for deciding how to operate `tes-prospect` and `tes-mine` together during
project reasoning.

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

## Changelog

| Date | Change | Evidence | Confidence |
|------|--------|----------|------------|
| 2026-05-22 | Created local predictive operations skill for coordinated `tes-prospect` and `tes-mine` use. | Maintainer analysis session. | high |
| 2026-05-22 | Added local skill-packaging check from external `write-a-skill` guidance. | Maintainer-provided external skill excerpt; absorbed as local operating check. | high |
| 2026-05-22 | Slimmed `SKILL.md` to the smallest mode-selection contract and moved details into `references/**`. | Maintainer requested extreme progressive disclosure. | high |
| 2026-05-22 | Changed activation posture from user-invoked to self-consumed local guidance. | Maintainer clarified these skills should be autoconsumed, not invoked. | high |
| 2026-05-22 | Added Operating Temperament mode selection so local skill construction can choose sniper, miner, prospector, builder, gate, or curator behavior. | Maintainer clarified that some skills need questions and verbosity while others must be objective and precise. | high |

## Do Not Lose

This guidance helps the agent decide the smallest useful reasoning mode. It
must not be exposed as a command, must not edit `tes-mine` or `tes-prospect`,
must not become a commercial skill, and must not apply packaging work before
behavior is clear. Keep `SKILL.md` lean; use references for depth.
