# TES Upstream-First Contract History

## Purpose

`tes-upstream-first` is the design-time discipline gate that fires before a
hand-rolled workaround is written: when facing library/framework/tooling
friction, check for an existing upstream solution (docs, a first-party helper, a
released patch) first. The hand-rolled path is the fallback, not the default.

## Why This Skill Exists

Manual config that "works" still costs: it reinvents maintained wiring and
carries assumptions the ecosystem already solved. The canonical miss this skill
exists to prevent is a hand-wired build/test config that duplicates exactly what
a framework's own first-party helper already does — the manual fix passes the
gate and ships, and the better path is never looked for because nobody pauses at
the instinct to hand-roll. Such a rule needs a vehicle that fires in the moment
of decision; a skill is that vehicle, because its description triggers on the
hand-roll instinct and brings the checklist into context when it matters, rather
than living in a doc that is not auto-loaded.

## Origin Signals

| Source                        | Signal                                                                                                                                              | Confidence |
| ----------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- | ---------- |
| Maintainer directive, 2026-06-10 | After a hand-rolled config duplicated a framework's own first-party test helper, add a logical rule to verify upstream fixes/patches/helper modules before resolving by hand. | high       |
| Maintainer directive, 2026-06-10 | Never update to RC/alpha/beta/pre-release — stable releases only.                                                                                  | high       |
| Maintainer dialogue, 2026-06-10 | A skill is the more adequate vehicle (fires at decision time); pair it with a one-line bootloader pointer so presence is guaranteed each session.   | high       |

## Contracts Preserved

- Fire at design time — before the workaround is written, not after.
- Trigger on the hand-roll instinct: wiring build/test/lint config by hand,
  "doesn't work out of the box", picking a dependency version, integration
  errors from a library where the first instinct is to configure around it,
  and before adding/bumping/updating a dependency.
- Run the checklist in order: read the library's own docs (Context7 first),
  look for a first-party helper in the package `exports` map (not just the
  README), check for a newer patch/minor, scope the helper's peer-dep cost,
  only then hand-roll — leaving a comment citing what was checked.
- Stable releases only: reject any resolved version with a pre-release suffix
  (`-alpha`, `-beta`, `-rc.N`, `-next.N`, `-canary`, `-pre`, `0.0.0-…`); a
  pre-release exception is user-approved, never the default.
- The bootloader keeps one line pointing to the skill; the skill body carries
  the detail — the project's load-then-detail pattern.

## Known Failure Modes Prevented

- Hand-rolling config for a friction that has a named upstream solution.
- Checking the README but not the package `exports` map, missing a `*/vite`,
  `*/vitest`, or `*-testing` helper subpath.
- Coding around a bug a newer patch already fixed.
- Dragging a breaking major just to obtain a helper, without weighing the cost.
- Installing a pre-release because `@latest`-style tooling surfaced one.

## Relationship To Other Skills

`tes-upstream-first` is narrower than `tes-guidelines`: it governs the *approach*
to a single class of decision (library friction / dependency change), where
`tes-guidelines` is the broad engineering-discipline anchor. It pairs with the
global Context7 rule (step 1 of its checklist) and with `tes-bump` when a
dependency change implies a version decision.

## Changelog

| Date       | Change                                                                                                          | Evidence                                                                          | Confidence |
| ---------- | ------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------- | ---------- |
| 2026-06-10 | Created `tes-upstream-first` (prefer-upstream checklist + stable-only rule) with a one-line bootloader pointer. | Maintainer directives; a hand-rolled config that duplicated a first-party helper. | high       |

## Do Not Lose

This is an approach gate, not a `commit:check` test — by the time a workaround
is in the diff, the wrong path is already taken. The leverage is entirely at
design time: a few `npm view` / Context7 lookups before the first line of the
workaround. Keep the description pushy enough to fire on the hand-roll instinct,
and keep the bootloader pointer to a single line so presence is guaranteed
without inflating the bootloader.
