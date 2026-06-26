# TES Align Contract History

## Purpose

`tes-align` turns the initial `/tes-init` project map into an evidenced project operating mesh.

## Why This Skill Exists

Canary convergence showed that a valid `PROJECT-CONTEXT.md` can still be too shallow to guide future work. The missing layer is semantic alignment: System X-Ray, Convergence Line, state, execution line, gates, boundaries, decisions, glossary, knowledge lifecycle, and evidence.

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
- Mixing target-project `docs/agents/evidence/**` with TES source-package benchmark evidence under `docs/evidence/**`.
- Reporting structural PASS while active docs still assert retired claims or use vocabulary the project has already moved past. The Semantic Residue Gate prevents this false green.
- Outranking a newer accepted ADR with older retained evidence. Freshness reconciliation requires the newest decision to be read before PASS.
- Letting `PROJECT-CONTEXT.md` compete with Tier 2 mesh after `/tes-align`.
- Updating `SKILL.md` without mirroring the change in this contract history.
- Reporting PASS when Tier 3 `contracts/**` contradict Tier 1 or Tier 2.
- Triggering Cortex `NEEDS_ALIGN` drift advice during the explicit `/tes-align` mesh reconciliation flow.

## Relationship To Other Skills

`tes-init` creates the initial map. `tes-align` deepens it. `tes-doctor` certifies health. `tes-cortex` recalls and curates continuity. Build-Test-Fail-Fix loops prove product changes after alignment selects the lane.

## Changelog

| Date | Change | Evidence | Confidence |
|------|--------|----------|------------|
| 2026-05-09 | Created `tes-align` contract. | TES Align source-of-truth document; `scripts/project_alignment_oracle.py --self-test`. | high |
| 2026-05-11 | Made Mermaid roadmap visualization the default presentation. | TES Align source-of-truth document; `scripts/project_alignment_oracle.py --self-test`. | high |
| 2026-05-11 | Added System X-Ray plus Convergence Line as the standard roadmap frame. | TES Align source-of-truth document; `scripts/project_alignment_oracle.py --self-test`. | high |
| 2026-05-21 | Clarified target-project alignment evidence boundary after source-package temporal evidence retention policy. | TES evidence retention policy; TES Align source-of-truth contract; project alignment oracle self-test. | high |
| 2026-05-25 | Added Semantic Residue Gate and freshness reconciliation; vocabulary stays target-owned via `docs/agents/contracts/SEMANTIC-RESIDUE.yml`. | TES Align source-of-truth contract; project alignment oracle self-test fixtures for retired terms, allowlisted history, word-boundary, and malformed contracts. | high |
| 2026-06-08 | Added Documentation Authority Tiers workflow: reconcile Tier 1+2 before Tier 3 mirror; demote `PROJECT-CONTEXT` to init inventory; create `DOCUMENTATION-AUTHORITY.md` when missing. | Consumer pilot ADR for documentation authority tiers; alignment oracle PASS. | high |
| 2026-06-08 | Added Tier 3 inventory hygiene gate via `INVENTORY-HYGIENE.yml` and `scripts/verify_documentation_inventory.py` (oracle + align scrub). | Prospect follow-up; mechanical enforcement of deep-read and HEAD hygiene. | high |
| 2026-06-26 | Added runtime alignment sentinel discipline so Cortex hooks stay no-write and stop emitting `NEEDS_ALIGN` during active `/tes-align` mesh writes. | Hook-agent benchmark report; Cortex runtime self-test; agent host projection oracle. | high |

## Skill Docs Boundary

This file (`docs/CONTRACT-HISTORY.md`) is TES skill contract memory — why `tes-align` exists and what must not regress. It is not project documentation. Project tier ladder lives in the target's `docs/agents/DOCUMENTATION-AUTHORITY.md` when present.

## Do Not Lose

`tes-align` exists to make the project operable for the next agent. It should reduce confusion and duplicated work, not expand documentation for its own sake.
