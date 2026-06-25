# TES Manual Authoring Contract History

## Purpose

`tes-manual-authoring` is local-only reference guidance for editing the generated public user manual without breaking its source pipeline or user-task shape.

## Why This Skill Exists

The user manual is generated from i18n source data. This skill keeps edits on the source path, keeps the manual task-oriented, and prevents governance or architecture detail from replacing user action.

## Contracts Preserved

- Edit `docs/i18n/tes-public.content.json` and `docs/i18n/tes-public.structure.yml`, not generated `docs/install/USER-MANUAL.html`.
- Keep all three languages present and structurally aligned.
- Keep section numbers sequential and unique across the manual navigation.
- Keep troubleshooting, update, and uninstall coverage.
- Regenerate public docs before committing generated HTML.
- Treat public content as delivered behavior that requires release-surface correlation.

## Known Failure Modes Prevented

- Hand-editing generated HTML.
- Missing a language branch or desynchronizing section numbers.
- Leaking governance detail into user instructions.
- Omitting troubleshooting or uninstall guidance.
- Committing i18n changes without regenerated HTML.

## Relationship To Other Skills

Use `tes-landing-authoring` for the landing page. Use `tes-sync` when public-content edits require release identity and bundle correlation.

## Changelog

| Date | Change | Evidence | Confidence |
|------|--------|----------|------------|
| 2026-06-06 | Created local manual authoring guidance. | Public docs pipeline and landing/manual split. | high |
| 2026-06-24 | Added contract history per local skill documentation standard. | Skill docs completeness audit. | high |

## Do Not Lose

The manual is generated and must answer user tasks before system architecture.
