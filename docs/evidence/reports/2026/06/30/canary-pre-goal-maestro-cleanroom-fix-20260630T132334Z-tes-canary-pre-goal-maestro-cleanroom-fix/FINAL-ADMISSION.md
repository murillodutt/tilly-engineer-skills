# FINAL-ADMISSION

Status: **READY_FOR_GOAL_MAESTRO_CANARY**

Execution host: Cursor

Primary target for next run: `/Users/murillo/Dev/tes-canary/cursor`

## Canary matrix

| Canary | Git | Pre-push | Pre-commit | Context | Align | Map | OS residue | Hook class | Admission |
|--------|-----|----------|------------|---------|-------|-----|------------|------------|-----------|
| cursor | PASS (`c0c75da`) | PASS | PASS (`git hook run pre-commit` exit 0) | PASS | PASS | PASS | none | Cursor ledger: RECORDED_SCRIPT_RUN + hook-health NEEDS_EVIDENCE (no false native PASS) | GO |
| claude | PASS (`d9083a7`) | PASS | PASS | PASS | PASS | PASS | none | CONFIGURED_NOT_OBSERVED (Claude native not observed in Cursor) | GO (support) |
| codex | PASS (`cf84c93`) | PASS | PASS | PASS | PASS | PASS | none | CONFIGURED_NOT_OBSERVED (Codex native not observed in Cursor) | GO (support) |

## Source changes

See `SOURCE-CHANGES.md`. Delivered behavior patched in package source; canaries rematerialized via helpers + attach hooks.

## Target changes

See `CANARY-REPAIR.md`. No manual edits to `.tes/tes-install-lock.json` or `.tes/postinstall.json`.

## Git / pre-push / pre-commit proof

See `GIT-GATES.md`. All three targets are Git-backed with executable pre-push (Field Reports) and local pre-commit oracle gate.

## Context / alignment / map proof

See `ORACLE-RESULTS.md` and post-repair matrix tail in `FINAL-ADMISSION-MATRIX.md`. All three targets PASS all three oracles with exit code 0.

## Hook proof classification

See `HOOK-EVIDENCE.md`.

| Host | Classification |
|------|----------------|
| Cursor native | NEEDS_EVIDENCE — config + ledger rows present; hook-health does not claim PASS_CEILING |
| Codex native | CONFIGURED_NOT_OBSERVED — absolute hook paths installed; no Cursor-native Codex session proof |
| Claude native | CONFIGURED_NOT_OBSERVED — hooks configured; no Cursor-native Claude session proof |

## OS residue proof

`find` returns zero files on all three targets after cleanup.

## Remaining downgrades

- `hook_runtime_health`: NEEDS_EVIDENCE on all hosts until native host lifecycle observation (acceptable per Super SPEC).
- Package `tes_init --self-test` still red via `install_smoke.py` (maintainer gate, not canary blocker).

## Forbidden claims for next Goal Maestro run

- Do not claim all hooks native PASS across Codex/Claude from Cursor alone.
- Do not claim TES default installer creates Git or project pre-commit.
- Do not claim `os_residue_absent` if `.DS_Store` reappears on proof surfaces.

## Journal

`docs/evidence/reports/2026/06/30/canary-pre-goal-maestro-cleanroom-fix-20260630T132334Z-tes-canary-pre-goal-maestro-cleanroom-fix/JOURNAL.md`

## Next exact command or prompt

In a **new** Cursor window (Goal Maestro allowed there):

```text
/tes-goal-maestro --execute-loop --target /Users/murillo/Dev/tes-canary/cursor
```

Use the active Super SPEC queue after confirming cursor canary HEAD `c0c75da` and clean `git status`.
