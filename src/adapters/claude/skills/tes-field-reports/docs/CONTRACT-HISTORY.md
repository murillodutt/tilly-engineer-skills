# TES Field Reports Contract History

## Purpose

`tes-field-reports` gives Field Reports its own visible runtime route.

## Why This Skill Exists

`/tes-field-reports` was already documented as a preferred TES command trigger, but the skill surface exposed no standalone Field Reports route. The visible runtime surface needed to match the documented primary command without splitting every routed alias into an unnecessary skill.

## Origin Signals

| Source | Signal | Confidence |
|--------|--------|------------|
| `docs/install/COMMAND-TRIGGERS.md` | Documents `/tes-field-reports` as a preferred trigger. | high |
| Runtime trigger screenshot review | Showed no visible `Tes Field Reports` skill. | high |
| User approval on 2026-05-11 | Approved creating the missing visible route while keeping grouped routers simple. | high |

## Source Search Ledger

| Window | Query | Occurrences | Meaning |
|--------|-------|-------------|---------|
| 2026-06-29 | Documented universal Contract History version semantics so skill contract versions, TES package versions, and `tver` metadata are not conflated. | `docs/dist/0.3.229/tilly-engineer-skills-0.3.229.zip`; `scripts/public_bundle_oracle.py` | high |
| 2026-05-11 | `tes-field-reports` skill route | 0 before creation | Missing visible skill route. |
| 2026-05-11 | `/tes-field-reports` | Present in docs and bootloaders | Trigger existed but lacked a dedicated visible skill. |

## Contracts Preserved

- `/tes-update` now has its own visible `tes-update` skill; Field Reports still records only final update certification probes.
- `/tes-curate` remains routed through `tes-cortex`.
- Field Reports remains sanitized operational feedback, not project truth.
- Draining remains explicit user intent or pre-push hook behavior.

## Known Failure Modes Prevented

- Documenting a primary trigger that does not appear in visible skill inventory.
- Creating one skill per alias and making TES noisy.
- Treating Field Reports receipts or GitHub issues as durable project context.
- Expanding report collection while repairing routing.

## Relationship To Other Skills

`tes-init` installs or repairs Field Reports as part of the runtime. `tes-doctor` certifies Field Reports health. `tes-field-reports` handles direct user intent for status, drain, disable, enable, and hook repair.

## Changelog

`Version` records a skill operational contract version only when the skill declares one, followed by the containing TES package version when known. If no operational contract stamp exists, the TES package version is the shipped identity. `tver: 0.1.0` in roadmap, Super SPEC, ledger, or TDS frontmatter is document-template metadata, not a skill runtime or harness version. Patch-level changes can remain inside the same skill contract boundary; in that case the TES package version carries release identity until a future change alters the skill contract boundary itself.

| Date | Change | Evidence | Confidence |
|------|--------|----------|------------|
| 2026-05-11 | Created visible `tes-field-reports` route. | `docs/install/COMMAND-TRIGGERS.md`; `scripts/command_trigger_oracle.py --self-test`. | high |

## Do Not Lose

Field Reports is useful because it is small, sanitized, local-first, and honest about transport blockers. Do not turn it into project memory or analytics.
