---
name: tes-manual-authoring
description: "Local-only reference guidance for editing the public user manual (docs/install/USER-MANUAL.html) without breaking its pipeline or letting it drift into a governance report. Use when explicitly useful for manual copy, sections, or order. Prefer tes-landing-authoring for the landing page instead."
license: MIT
---

# TES Manual Authoring

Operational contract: `tes.manual_authoring@0.1.0`.

Local development surface only. Do not package, publish, materialize, or treat as distributable TES.

Use only as a reference while editing the public user manual. Do not load it automatically for ordinary execution, and honor an owner-requested no-skill run. Prefer `tes-landing-authoring` when the target is the landing page (`docs/index.html`).

## Golden rule of the pipeline

NEVER hand-edit `docs/install/USER-MANUAL.html`. It is generated. Edit the source, then regenerate:

1. Text lives in `docs/i18n/tes-public.content.json` under `sections.<key>.<lang>` (and `hero.manual.<lang>`, `ui.<lang>`).
2. Section order lives in `docs/i18n/tes-public.structure.yml` → `pages.manual.nav`.
3. Every section needs all three languages: `en` + `es` + `pt`. A missing language is a `KeyError` at build time.
4. Section numbers (`num`) are decorative labels — keep them sequential and unique across the nav order; reconcile all three languages after any insert/remove.
5. Links are relative to `docs/install/`: same-dir files (e.g. `REVERSIBILITY.md`) need no prefix; files elsewhere need `../` (e.g. `../adr/0004-...md`). Cross-section anchors are `#<key>-<lang>`.
6. After editing: `npm run public-docs:build`, then `git add` the HTML and i18n together. `public-docs:check` is exact string equality and runs pre-commit.

## Tone ruler

Write FOR the user (imperative how-to), not ABOUT the system (description). Every line closes a doubt. Neither tiring nor empty.

- "If you want X, do Y. If you see Z, do W." Translate every internal state (`STALE_SOURCE`, `NEEDS_REVIEW`, `BLOCKED`, `PENDING_TRUST`) into symptom + next action, never report it raw.
- Almost no architecture belongs here. If a sentence about how it works under the hood does not change what the user types next, move it to a governed doc (`AGENT-MANUAL.md`, `REVERSIBILITY.md`, an ADR) and link it.
- Show the command to type and the expected output, not just the capability.

## Diataxis discipline

Keep the four modes apart. Do not bury explanation inside a how-to — it dilutes the instruction and hides the concept.

- Tutorial: guided first success (the 5-minute "hello world").
- How-to: a real task ("if you see X, do Y").
- Reference: command/flag list, neutral description.
- Explanation: the why/architecture — lives in a separate governed doc, linked.

## Mandatory user-question queue

A good manual answers, in order: is it for me? requirements? how do I install? first success? what commands exist? what do I do when it breaks? how do I update? how do I remove it? Do not skip troubleshooting or uninstall — their absence signals a tool that "sticks".

## Size budget

Limit is in `scripts/validate_doc_size.py` (`docs/install/USER-MANUAL.html`, currently 2500). Each section costs fixed HTML overhead × 3 languages, so growth is structural — trimming paragraphs barely helps. Rule: enxugar → measure → decide. If new legitimate sections overflow, either modularize into a second generated page or consciously raise the limit with a comment explaining why (the 2300→2500 raise on 2026-06-06 is the precedent). Do not raise it silently.

## Workflow

1. Edit `sections.<key>.<lang>` in `content.json` for all three languages.
2. If adding/removing a section, edit `pages.manual.nav` in `structure.yml` and reconcile every `num`.
3. `npm run public-docs:build`; check size with `npm run docs:size`.
4. Serve `docs/` locally and review the changed sections in all three languages.
5. `git add` HTML + i18n together.

## Done

The manual edit is done when each changed section reads as user action (not system description), internal states are translated to symptom+action, the question queue stays covered, the build passes `--check`, size is under budget, and the three languages match in structure with reconciled numbers.

## Locks

- Do not hand-edit `docs/install/USER-MANUAL.html`; edit i18n and regenerate.
- Do not modify `src/adapters/**`.
- Do not leak architecture/governance detail into the manual; link the governed doc instead.
- Do not drop a language or leave `num` labels inconsistent.
- Remember: public content is delivered behavior → it triggers a version bump and surface correlation (see `tes-sync`). Do not call it sealed without `npm run commit:check`.
