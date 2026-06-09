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

## State — ON-PATH: inheritance runs in production (F2 resolved)

The line meets its objective on the real install path. The off-path defect (F2)
that the real-project canary exposed is fixed: `compose_context_from_staged`
(the function `tes_install` → `apply_staged_bundle` actually calls) now routes a
project-authored root with real human context through inheritance, and a thin
already-inherited root through a stable idempotent re-render. The prior routing
in `install_adapter.py` was the wrong branch; the production path is now the one
that carries it.

| SPEC | Scope | State | Fixture / evidence |
|------|-------|-------|--------------------|
| SPEC-000 | rich-root fixtures | delivered | `context_distill_coverage_oracle.py` self-test |
| SPEC-001 | context-unit model + coverage diff | delivered | self-test: faithful=OVERLAY_COVERED, dropped directive fails |
| SPEC-002 | canonical-source section map | delivered | cross-check vs `project_context_oracle` (merge keeps PASS) |
| SPEC-004 | Claude `@`-pointer render | delivered | self-test RENDER_CLAUDE_OK + production-path canary |
| SPEC-005 | Codex materialized block + src-sha | delivered | self-test RENDER_CODEX_OK, <32 KiB |
| SPEC-006 | idempotency / ALREADY_INHERITED | delivered | `tes_bundle` self-test: 2nd/3rd apply skip-rerender-identical, stable lines |
| SPEC-007 | installer routing (turn the default) | **ON-PATH** | wired in `tes_bundle.compose_context_from_staged`; production-path canary INHERITED |
| SPEC-008 | uninstall restores `.bak` byte-faithful | delivered | `tes_bundle.py` self-test + production-path canary restore |
| SPEC-003 | `tes-context-distill` skill (Phase 2) | delivered | claude+codex, command-trigger + materialize |
| SPEC-009 | `/tes-doctor` inherited-context recovery | delivered | doctor route + bootloader skill list |
| SPEC-010 | real-project canary replay | passed (synthetic prod-path) | build→stage→apply: INHERITED, uninstall byte-faithful, idempotent |

## Architectural decision (resolved)

Inheritance and the parent root-context-composition were the same decision for
the same root, expressed two ways. Owner decision (recorded): inheritance
SUPERSEDES the parent's inline composition for Claude/Codex roots **that carry
substantive human context** (detectable context units); roots without such
content keep the parent inline compose. This is a narrow, conditional
supersession — not a blanket parent rewrite — so the parent contract stays valid
for the prose-only case, proven by its still-green self-test alongside the new
rich-root inheritance fixture.

Three field-class bugs were found and fixed this cycle (off-path routing,
undelivered helper dependency, non-idempotent re-wrap) — see commits `f182e8c2`
and `99823339` for detail. No data-loss risk: the parent inline path preserves
project context; the inheritance path archives the original as
`<root>.bak-<stamp>`.

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

## Canary findings — F2 (resolved)

- **F2 (resolved):** a real-project canary (0.3.173, source-of-record off-repo)
  installed via the production path and did NOT inherit — routing was off-path
  (`install_adapter` instead of `apply_staged_bundle`). Fixed by moving routing
  into `compose_context_from_staged` and propagating the
  `context_distill_coverage_oracle` dependency to the installed helper lists.
  Re-proven on a synthetic production-path canary (build→stage→apply): INHERITED,
  uninstall byte-faithful, idempotent re-render. Distinct from F1 (oracle
  precision bug, also resolved).

## Next cut

The line meets its objective on the production path; all SPECs delivered and
on-path. Remaining work is the line-closing sync: bump to the next patch
(delivered installer behavior changed — bump owed per the deferral exceptions
recorded in commits `f182e8c2` and `99823339`), rebuild the bundle, tag, and
certify. Field-certification for a commercial claim still wants replays on
additional independent real projects per `<learning_and_boundaries>`.
