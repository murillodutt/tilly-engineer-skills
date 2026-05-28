# TES Sync Contract History

## Purpose

Capture the bump + commit + push + tag + release certification routine as
local development guidance so future sessions do not re-derive it from
scratch.

## Why This Skill Exists

Two release cycles in a row (0.3.124 and 0.3.125) surfaced the same
class of pain: the sync routine has many synchronized surfaces, and
forgetting one creates a downstream gate failure or a misleading
public artifact. Each cycle re-discovered:

- `bundle_sha256` in `docs/i18n/tes-public.structure.yml` is
  hand-maintained, and the publish phase prints a new sha that must be
  copied over before HTML regeneration.
- `validate_reference_package.py` has zip filenames that embed the
  version, so a global sed against `0.3.X` mutilates filenames inside
  the new dist directory.
- Stale public tags from abandoned bumps point to orphan commits and
  must be moved with explicit user authorization, never silently.
- The 33-gate `npm run commit:check` suite is the only reliable
  detector of sync drift.

`docs/governance/SYNC-AUDIT-CHECKLIST.md` captures the same routine for
human review. This skill is its agent-facing condensation, organized
for fast retrieval during active sync work.

## Origin Signals

| Source | Signal | Confidence |
|--------|--------|------------|
| 0.3.124 release session | tag conflict + missed bundle_sha256 cost ~30 minutes of debugging | high |
| 0.3.125 release session | scoped sed pattern trap on REQUIRED_PATHS zip filenames | high |
| External canary review (2026-05-25) | structured residue.malformed_contract + freshness stopwords + single-current-dist policy | high |
| `docs/governance/SYNC-AUDIT-CHECKLIST.md` | human-readable contract captured the same flow | high |

## Source Search Ledger

| Window | Query | Occurrences | Meaning |
|--------|-------|-------------|---------|
| 2026-05-25 | `/tes-sync` | 0 before creation | New local development surface. |
| 2026-05-25 | `SYNC-AUDIT-CHECKLIST` | governance only | Skill condenses the checklist for agent use. |

## Contracts Preserved

- Skill is local development surface only. Not packaged, not
  materialized to targets, not exposed as a public `/tes-*` product
  command.
- `npm run commit:check` is the authoritative gate. The skill cannot
  skip it.
- Public tags are not moved without explicit user authorization.
- `docs/dist/` keeps exactly one version directory.
- Mechanism in TES, vocabulary in target.
- `/tes-sync` always applies a version bump; the scope decision only chooses
  source-only versus bundle/public refs.

## Known Failure Modes Prevented

- Forgetting `bundle_sha256` update → `[tds-surface] BLOCKER`.
- Global sed on `validate_reference_package.py` → zip filename drift.
- Silent tag force-move → public release identity rewrite without audit
  trail.
- Skipping `commit:check` → silent gate drift surfacing in next cycle.
- Hand-editing `docs/index.html` or `docs/install/USER-MANUAL.html` →
  regenerated on next build, lost.
- Re-adding historical `docs/dist/<old>/` to `main` → violates
  single-current-dist policy.

## Relationship To Other Local Skills

`tes-predictive-operations` decides which reasoning mode to use.
`tes-high-agency-pattern` designs the operating pattern of a single
local skill. `tes-sync` is execution-time guidance for one specific
routine — the complete sync — and pairs with the human checklist at
`docs/governance/SYNC-AUDIT-CHECKLIST.md`.

## Changelog

| Date | Change | Evidence | Confidence |
|------|--------|----------|------------|
| 2026-05-25 | Created `tes-sync` from the audit checklist and the 0.3.124/0.3.125 release evidence. | `docs/governance/SYNC-AUDIT-CHECKLIST.md`, evidence packets under `docs/evidence/reports/2026/05/25/tes-align/**`. | high |
| 2026-05-28 | Removed the no-bump sync route. `/tes-sync` now always applies a bump; governance `PASS` maps to source-only bump unless sync is cancelled. | User directive: "atualize tes-sync para sempre aplicar bump". | high |
| 2026-05-28 | Added an explicit parity lock so scope-rule changes must update `docs/governance/SYNC-AUDIT-CHECKLIST.md` with the skill. | Post-release gap review found the checklist still described `PASS` as no-bump. | high |
| 2026-05-28 | Added discoverability validation after Codex could see the skill directory but could not load the skill because frontmatter YAML was invalid. | `quick_validate.py "$CODEX_HOME/skills/tes-sync"` failed on an unquoted `description` containing `package:`. | high |
| 2026-05-28 | Added live GitHub Pages certification to prevent closing a release while public install docs still serve the previous version. | Post-release gap review found package ref `v0.3.146` certified while GitHub Pages still served `0.3.145`. | high |

## Do Not Lose

The skill exists because every release cycle costs time when the agent
re-derives the sync routine. The 12 phases, the bumped scope choices, and
the trap catalog are the durable knowledge. The version numbers cited
in examples will age, but the structure must not. A skill that exists on disk
but fails Codex frontmatter parsing is operationally absent.
