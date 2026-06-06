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

## State — BLOCKED: off-path integration (the private canary finding)

Components shipped in 0.3.172/0.3.173, but the line does NOT meet its objective
on the real install path. A real-project install (private canary, 0.3.173) revealed that
inheritance never runs in production: `tes_install` writes context_governance
roots via `tes_bundle.apply_staged_bundle` → `root_context.compose_root_context`
(the parent's INLINE composer), while SPEC-007's routing lives in
`install_adapter.py` — a branch the production install does not traverse. Every
"delivered" claim below was verified against `install_adapter` directly, the
wrong path. This is the defect; the canary did its job.

| SPEC | Scope | State | Fixture / evidence |
|------|-------|-------|--------------------|
| SPEC-000 | rich-root fixtures | delivered | `context_distill_coverage_oracle.py` self-test |
| SPEC-001 | context-unit model + coverage diff | delivered | self-test: faithful=OVERLAY_COVERED, dropped directive fails |
| SPEC-002 | canonical-source section map | delivered | cross-check vs `project_context_oracle` (merge keeps PASS) |
| SPEC-004 | Claude `@`-pointer render | delivered (component) | self-test RENDER_CLAUDE_OK |
| SPEC-005 | Codex materialized block + src-sha | delivered (component) | self-test RENDER_CODEX_OK, <32 KiB |
| SPEC-006 | idempotency / ALREADY_INHERITED | delivered (component) | self-test stable re-render |
| SPEC-007 | installer routing (turn the default) | **OFF-PATH** | wired in `install_adapter.py`, NOT in the production `apply_staged_bundle` path; never runs on npx/postinstall install |
| SPEC-008 | uninstall restores `.bak` byte-faithful | delivered (component) | `tes_bundle.py` self-test + end-to-end |
| SPEC-003 | `tes-context-distill` skill (Phase 2) | delivered | claude+codex, command-trigger + materialize |
| SPEC-009 | `/tes-doctor` inherited-context recovery | delivered | doctor route + bootloader skill list |
| SPEC-010 | real-project canary replay | **exposed the off-path defect** | private canary 0.3.173: installed, did NOT inherit; parent composed inline instead |

## Blocking architectural decision (unresolved)

Inheritance (overlay → canonical source, root goes thin) and the parent
root-context-composition (overlay INLINE in the root) are the SAME decision made
twice, incompatibly, for the same context_governance root. Integrating SPEC-007
into `apply_staged_bundle` collides with the parent's contract (proven: the
`clean runtime ... project-owned overlay` self-test fails) and would REOPEN the
parent contract, which the Super SPEC's Required Negative Checks forbid. The
2026-06-06 integration attempt was reverted (uncommitted) for this reason.

Resolution required before any reintegration: reconcile the two contracts —
decide whether inherited-context SUPERSEDES the parent's inline composition for
Claude/Codex roots (amend the parent), or COMPLEMENTS it under a narrower
condition, or whether the parent's inline composition already satisfies the
product need and this line is redundant. This is a product/architecture call,
not a wiring fix. Canary evidence: parent inline composition DID preserve project
context (strip-tes-block keeps project_text); no data was lost.

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

## Canary findings — F2 (blocking)

- **F2 (open, blocking):** a real project canary (0.3.173, source-of-record off-repo) installed via the
  production npx/postinstall path and did NOT inherit — the parent's inline
  composer ran instead, because SPEC-007 routing is off-path (see State). The
  components work in isolation; the line does not work end-to-end on the real
  install path. Distinct from F1 (an oracle precision bug, resolved).

## Next cut

BLOCKED on the architectural reconciliation above. Do NOT reintegrate SPEC-007
into `apply_staged_bundle` until the inherit-vs-inline-compose contract is
decided — a blind integration breaks the parent's self-test and reopens a
forbidden contract. The honest status: components delivered, line objective NOT
met on the production path, no data-loss risk (parent preserves project context
inline). Owner decision needed: supersede parent / complement / accept parent
as sufficient and retire this line.
