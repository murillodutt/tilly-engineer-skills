# TES Open Obsidian Contract History

## Purpose

`tes-open-obsidian` is the opt-in bridge from TES Markdown knowledge mesh to
the human Obsidian visual surface.

## Why This Skill Exists

TES intentionally treats Obsidian as a visualization tool, not as the source of
truth. The project mesh lives in `docs/agents/**`; `.obsidian/**` remains
human/project-owned state. This skill lets a user open the prepared project in
Obsidian without turning TES into an Obsidian configuration manager.

## Origin Signals

| Source | Signal | Confidence |
|---|---|---|
| 2026-05-09 user directive | User asked for `/tes-open-obsidian` after the `.obsidian/**` boundary decision. | high |
| the TES Align source-of-truth document | TES should produce Obsidian-compatible Markdown and avoid `.obsidian/**` writes. | high |
| Obsidian CLI help | Official CLI can open/read/search a vault when registered; this is the preferred launch path when available. | high |
| `scripts/tes_open_obsidian.py --self-test` | Deterministic helper proves preflight and no `.obsidian/**` dry-run mutation. | high |

## Source Search Ledger

| Window | Query | Occurrences | Meaning |
|---|---:|---:|---|
| 2026-05-09 | `/tes-open-obsidian` | 0 before creation | New trigger surface. |

## Contracts Preserved

- TES Markdown under `docs/agents/**` is the operational source of truth.
- The open target is `docs/agents`, not the repository root.
- Obsidian state under `.obsidian/**` is host-owned.
- Opening Obsidian is a visible local action and must be opt-in.
- The skill certifies context and alignment before opening.

## Known Failure Modes Prevented

- Treating `.obsidian/**` as a TES-owned install surface.
- Opening an uninitialized project and calling that success.
- Opening the repository root and calling that the TES mesh vault.
- Installing plugins or mutating app settings during a context task.
- Confusing Obsidian visualization with TES runtime dependency.

## Relationship To Other Skills

`tes-init` creates the initial mesh. `tes-align` refines it. `tes-open-obsidian`
only preflights and opens the project for human navigation. `tes-doctor`
remains the health check.

## Changelog

| Date | Change | Evidence | Confidence |
|---|---|---|---|
| 2026-05-09 | Created `tes-open-obsidian` contract. | User directive; `scripts/tes_open_obsidian.py --self-test`. | high |
| 2026-05-09 | Preferred official Obsidian CLI when registered, with macOS app fallback. | <https://obsidian.md/help/cli>. | high |
| 2026-05-09 | Corrected the open target to `docs/agents` and added `vault_root` evidence. | Real `tilly-mini-agi` dry-run; `scripts/tes_open_obsidian.py --self-test`. | high |

## Do Not Lose

This skill exists to make the Obsidian workflow convenient without making
Obsidian a TES dependency. Never let convenience become hidden `.obsidian/**`
mutation.
