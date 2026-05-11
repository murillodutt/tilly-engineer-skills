# TES Align Contract History

## Purpose

`tes-align` turns the initial `/tes-init` project map into an evidenced project
operating mesh.

## Why This Skill Exists

Canary convergence showed that a valid `PROJECT-CONTEXT.md` can still be too
shallow to guide future work. The missing layer is semantic alignment:
System X-Ray, Convergence Line, state, execution line, gates, boundaries,
decisions, glossary, knowledge lifecycle, and evidence.

## Origin Signals

| Source | Signal | Confidence |
|--------|--------|------------|
| TES Align source-of-truth document | Defines role boundary, Obsidian-native mesh, oracle requirements, and locks. | high |
| `/tes-init` project-start gate | Initialization is necessary but not enough for operating alignment. | high |
| Wave 1-6 Build-Test-Fail-Fix evidence | False greens appear when context looks complete but cannot guide work. | high |

## Source Search Ledger

| Window | Query | Occurrences | Meaning |
|--------|-------|-------------|---------|
| 2026-05-09 | `/tes-align` | 0 before creation | New trigger surface. |
| 2026-05-09 | `PROJECT-ROADMAP.md` | contract source only | Needed as target-project operating mesh output. |

## Contracts Preserved

- `/tes-init` remains the single initialization command.
- `/tes-align` is not an installer.
- Markdown and Git remain source of truth.
- Obsidian is visualization, not runtime authority.
- Project-owned governance is centrally backed up, clean-applied, and recovered semantically.

## Known Failure Modes Prevented

- Treating scaffold context as deep understanding.
- Recreating existing roadmap or governance docs.
- Writing ambition-theater roadmaps.
- Falling back to a bullet roadmap when the user needs an operating X-Ray and a visual future map.
- Hiding unknowns.
- Polluting `.obsidian/**`.
- Claiming alignment without retained evidence.

## Relationship To Other Skills

`tes-init` creates the initial map. `tes-align` deepens it. `tes-doctor`
certifies health. `tes-cortex` recalls and curates continuity. Build-Test-Fail-
Fix loops prove product changes after alignment selects the lane.

## Changelog

| Date | Change | Evidence | Confidence |
|------|--------|----------|------------|
| 2026-05-09 | Created `tes-align` contract. | TES Align source-of-truth document; `scripts/project_alignment_oracle.py --self-test`. | high |
| 2026-05-11 | Made Mermaid roadmap visualization the default presentation. | TES Align source-of-truth document; `scripts/project_alignment_oracle.py --self-test`. | high |
| 2026-05-11 | Added System X-Ray plus Convergence Line as the standard roadmap frame. | TES Align source-of-truth document; `scripts/project_alignment_oracle.py --self-test`. | high |

## Do Not Lose

`tes-align` exists to make the project operable for the next agent. It should
reduce confusion and duplicated work, not expand documentation for its own
sake.
