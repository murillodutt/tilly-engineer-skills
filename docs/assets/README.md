---
tds_id: docs.assets
tds_class: index
status: active
consumer: maintainers, documentation authors, brand asset authors, and release reviewers
source_of_truth: false
evidence_level: L2
owner: project
updated: 2026-06-29
scope: documentation-assets
tver: 0.1.0
---

# Documentation Assets

This directory stores project-owned visual source files and documentation
assets that support repository documentation, brand references, evidence packs,
and design handoffs.

## Scope

Use this directory for reusable documentation assets such as:

- vector sources (`.ai`, `.svg`, `.pdf`);
- raster exports (`.png`, `.jpg`, `.jpeg`, `.webp`);
- brand, logo, diagram, and presentation-support files;
- source artwork that should stay with the repository documentation.

Do not use this directory for runtime application assets, generated build
outputs, dependency caches, temporary exports, screenshots without durable
documentation value, credentials, PII, or vendor material that cannot be
redistributed inside the repository.

## Placement

- Put global or reusable documentation assets in `docs/assets/`.
- Put assets that belong to a single specification under that specification's
  local `assets/` directory.
- Put runtime-served files in `public/` or application-owned asset paths only
  when the product code needs them.

## File Rules

- Prefer stable ASCII kebab-case filenames for new assets.
- Preserve an approved external source filename only when renaming would break
  traceability.
- Keep editable source files and exported preview files together when both are
  needed.
- Reference assets from documentation with relative paths.
- Do not commit `.DS_Store`, editor metadata, caches, or generated output.

## Review Checklist

Before adding an asset here, confirm:

- the file has a clear documentation, brand, evidence, or handoff purpose;
- the source or license allows repository storage;
- the asset does not expose secrets, customer data, or regulated source data;
- the chosen location matches its reuse scope.
