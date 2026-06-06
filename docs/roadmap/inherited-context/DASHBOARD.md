---
tds_id: roadmap.inherited_context.dashboard
tds_class: roadmap
status: active
consumer: maintainers, installer authors, adapter authors, skill authors, release reviewers, and execution agents
source_of_truth: false
evidence_level: L1
tver: 0.1.0
---

# Inherited Context Line — Dashboard

Single live-state surface for the inherited-context line. Read the canonical
Super SPEC for the contract; read this for what is delivered, the evidence, and
the next cut.

Canonical:
`docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-tes-inherited-context-canonical-source.md`

## State

Released in TES `0.3.172` (tag `v0.3.172`, commit `cc04a4fe`, bundle sha
`ced76b7c357a2d7cdd33f0d82dd01bf94976de92cb0244ccc7cba5ad75ea7d79`). Every SPEC
below is delivered with a self-test fixture except SPEC-010.

| SPEC | Scope | State | Fixture / evidence |
|------|-------|-------|--------------------|
| SPEC-000 | rich-root fixtures | delivered | `context_distill_coverage_oracle.py` self-test |
| SPEC-001 | context-unit model + coverage diff | delivered | self-test: faithful=OVERLAY_COVERED, dropped directive fails |
| SPEC-002 | canonical-source section map | delivered | cross-check vs `project_context_oracle` (merge keeps PASS) |
| SPEC-004 | Claude `@`-pointer render | delivered | self-test RENDER_CLAUDE_OK |
| SPEC-005 | Codex materialized block + src-sha | delivered | self-test RENDER_CODEX_OK, <32 KiB |
| SPEC-006 | idempotency / ALREADY_INHERITED | delivered | self-test stable re-render |
| SPEC-007 | installer routing (turn the default) | delivered | `install_adapter.py --self-test` (5 cases) |
| SPEC-008 | uninstall restores `.bak` byte-faithful | delivered | `tes_bundle.py` self-test + end-to-end |
| SPEC-003 | `tes-context-distill` skill (Phase 2) | delivered | claude+codex, command-trigger + materialize |
| SPEC-009 | `/tes-doctor` inherited-context recovery | delivered | doctor route + bootloader skill list |
| SPEC-010 | real-project canary replay | exercised | realistic canary PASS full cycle; F1 found + fixed (see below) |

## Design facts (do not relitigate)

- Claude points (`@docs/agents/PROJECT-CONTEXT.md`), Codex materializes a block.
  Permanent asymmetry — Codex has no `@import` (RULES-FILE-ENGINEERING.md).
- One canonical source: `docs/agents/PROJECT-CONTEXT.md`, no parallel file.
- Phase 1 (archive+extract+render) is installer code (runs headless); Phase 2
  (condense/optimize) is the `tes-context-distill` skill (judgment, opt-in).
- The `<root>.bak-<stamp>` archive is both the non-loss coverage oracle and the
  uninstall restore source. An inherited root is detected by markers AND archive
  — markers alone false-positive on clean installs.

## Canary findings

- **F1 (resolved):** on a realistic canary, `project_context_oracle` expected
  `CURSOR.md`/`.cursor` (TES-installed surfaces) in PROJECT-CONTEXT, failing the
  overlay oracle post-inherit. Root cause: `tes-runtime-capabilities.mdc` was
  missing from the per-file TES-runtime exclusion, plus a stale CURSOR.md
  bootloader marker. Fixed in `scripts/project_context_oracle.py`; full cycle
  (install → inherit → coverage → uninstall byte-faithful) now PASS. Self-test
  fixture strengthened to fail if either exclusion regresses.

## Next cut

The line is field-exercised on one realistic target with no open findings. Per
`<real_project_learning_standard>`, broaden to two more independent real
projects before a commercial-use claim. Until then: engineering-complete and
single-target field-validated.
