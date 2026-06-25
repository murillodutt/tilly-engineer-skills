# TES Landing Authoring Contract History

## Purpose

`tes-landing-authoring` is local-only reference guidance for editing the generated public landing page without breaking its source pipeline or proof discipline.

## Why This Skill Exists

The landing page is generated from i18n source data. This skill keeps edits on the source path, ties claims to evidence, and prevents the page from drifting back into a technical report.

## Contracts Preserved

- Edit `docs/i18n/tes-public.content.json` and `docs/i18n/tes-public.structure.yml`, not generated `docs/index.html`.
- Keep all three languages present and structurally aligned.
- Keep quantified claims inside `docs/evidence/current/CLAIMS.md` scope.
- Regenerate public docs before committing generated HTML.
- Treat public content as delivered behavior that requires release-surface correlation.

## Known Failure Modes Prevented

- Hand-editing generated HTML.
- Missing a language branch.
- Publishing unsupported quantified claims or social proof.
- Turning landing copy into governance narration.
- Committing i18n changes without regenerated HTML.

## Relationship To Other Skills

Use `tes-manual-authoring` for the user manual. Use `tes-sync` when public-content edits require release identity and bundle correlation.

## Changelog

| Date | Change | Evidence | Confidence |
|------|--------|----------|------------|
| 2026-06-06 | Created local landing authoring guidance. | Public docs pipeline and landing/manual split. | high |
| 2026-06-24 | Added contract history per local skill documentation standard. | Skill docs completeness audit. | high |

## Do Not Lose

The landing page is generated; source and generated artifacts move together.
