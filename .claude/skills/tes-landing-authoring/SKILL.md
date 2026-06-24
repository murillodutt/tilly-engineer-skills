---
name: tes-landing-authoring
description: "Local-only reference guidance for editing the public landing page (docs/index.html) without breaking its pipeline or letting it drift back into a technical report. Use when explicitly useful for landing copy, proof, or section order. Prefer tes-manual-authoring for the user manual instead."
license: MIT
---

# TES Landing Authoring

Operational contract: `tes.landing_authoring@0.1.0`.

Local development surface only. Do not package, publish, materialize, or treat
as distributable TES.

Use only as a reference while editing the public landing page. Do not load it
automatically for ordinary execution, and honor an owner-requested no-skill run.
Prefer `tes-manual-authoring` when the target is the user manual
(`docs/install/USER-MANUAL.html`).

## Golden rule of the pipeline

NEVER hand-edit `docs/index.html`. It is generated. Edit the source, then
regenerate:

1. Text lives in `docs/i18n/tes-public.content.json` under
   `sections.<key>.<lang>` (and `hero.index.<lang>`, `ui.<lang>`).
2. Section order lives in `docs/i18n/tes-public.structure.yml` →
   `pages.index.nav`.
3. Every section needs all three languages: `en` + `es` + `pt`. A missing
   language is a `KeyError` at build time, not a warning.
4. After editing: `npm run public-docs:build`, then `git add` the HTML and the
   i18n files together. `public-docs:check` is exact string equality and runs
   in the pre-commit hook — never commit i18n without rebuilding.

Nine block types exist (`p`, `note`, `aside`, `list`, `steps`, `code`, `table`,
`cards`, `source_map`). You almost never need a new one; adding one means
editing `scripts/build_public_docs.py`.

## Tone ruler

The reader wants to be *certified*, not entertained. Every line should close a
doubt (answer trigger), never open one (doubt trigger). Truth told plainly.
Neither tiring nor empty.

- Benefit over feature: "you get X", not "the system does Y".
- No internal state in the sales copy: never dump `PASS`/`BLOCKED`/`DEGRADED`/
  `NEEDS_REVIEW`/`BYPASS_SUSPECTED` or raw config keys at the reader. Translate
  to a benefit in the same sentence or cut it.
- The hero is promise + visual proof + one copy-paste install command. No
  feature list, no jargon, no disclaimer in the hero.
- Keep the npx command copyable — for a one-command product it is the strongest
  CTA you have.

## Proof calibration

Two strong proofs in focus, support discreet. This is where research (more
proof) and TES discipline (fewer, scoped claims) meet:

1. Reversibility, protagonist: "you can always undo it, nothing leaves your
   repo" answers the dev's dominant fear. It is real and certified.
2. A quantified result, scoped on the same line (e.g. the 6x lift: "one
   retained Claude CLI run, sonnet, graded — not a universal promise").
3. Maturity (version, adapter coverage), one discreet line, not a pillar.

Hard rule: every quantified claim on the landing MUST already be registered in
`docs/evidence/current/CLAIMS.md` with Proof and Boundary, and the landing text
must not exceed that scope. Never fabricate social proof (logos, "used by N
teams", testimonials) TES does not actually have.

## Anti-patterns (what makes it read like a report)

- Long non-claims disclaimers in the sales copy → move to CLAIMS.md / ADRs and
  link.
- A docs routing table (`source_map`) used as if it were proof → it is
  navigation; demote it to one discreet line linking `docs/INDEX.md`.
- Internal-state dumps and governance jargon where a benefit belongs.
- Headline that is a feature or vague slogan instead of an outcome or sharp
  positioning.

## Workflow

1. Edit `sections.<key>.<lang>` in `content.json` for all three languages.
2. If adding/removing a section, also edit `pages.index.nav` in
   `structure.yml`.
3. `npm run public-docs:build`; check `docs/index.html` size stays under its
   limit (`scripts/validate_doc_size.py`, 2800).
4. Serve `docs/` locally and review the changed sections in all three
   languages.
5. `git add` HTML + i18n together.

## Done

The landing edit is done when each changed section reads as benefit and proof
(not system description), every quantified claim is in CLAIMS.md within scope,
the build passes `--check`, size is under budget, and the three languages match
in structure.

## Locks

- Do not hand-edit `docs/index.html`; edit i18n and regenerate.
- Do not modify `src/adapters/**`.
- Do not put a quantified claim on the landing that is not in
  `docs/evidence/current/CLAIMS.md`.
- Do not fabricate social proof TES does not hold.
- Remember: public content is delivered behavior → it triggers a version bump
  and surface correlation (see `tes-sync`). Do not call it sealed without
  `npm run commit:check`.
