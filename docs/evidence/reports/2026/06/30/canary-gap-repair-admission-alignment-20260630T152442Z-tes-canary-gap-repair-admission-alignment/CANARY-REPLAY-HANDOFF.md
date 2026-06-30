---
tds_id: evidence.canary_gap_repair_admission_alignment.canary_replay_handoff_20260630
tds_class: evidence
status: active
consumer: canary replay operators, Goal Maestro operators, maintainers
source_of_truth: false
evidence_level: L2
---

# CANARY-REPLAY-HANDOFF — Instructions For The Later Replay Session

This is the ONLY output of this SPEC that instructs canary recreation. This SPEC
did not install into, reset, or replay any canary. Package source readiness is
done; canary admission is the next session's job.

## Exact package state

- Package commit at this handoff: `89e5ea736db60d8f55761f6b68374165c7ec1715`
  (HEAD), with uncommitted gap-repair changes in the working tree. The replay
  session must run against the COMMITTED package state; commit the gap-repair
  changes first (locally) so the replay input is reproducible.
- Version after bump: `0.3.232` (from `0.3.231`).

## Bundle path / SHA / version decision

```text
version:  0.3.232  (owner-confirmed patch bump; refresh, no push/tag/publish)
bundle:   docs/dist/0.3.232/tilly-engineer-skills-0.3.232.zip
sha256:   9461e708f5ba1c3b16f6669653581da6dcca37989cf51d2725c4e2f54d9bcf68
entries:  378   pycache: 0
```

If the package is committed after this handoff, regenerate or re-verify the
bundle so its `source_commit` / `source_tree_state` reflect the committed tree
(it currently records `dirty`).

## Required replay order (do NOT skip or reorder)

1. `git init` the canary target FIRST (admission requires a Git work tree).
2. Install from the local `0.3.232` bundle (verify SHA before staging).
3. `/tes-setup`.
4. `/tes-align`.
5. `/tes-map`.
6. Post-align postinstall refresh (`tes_install.py postinstall --force` or
   recovery) so the sentinel re-derives advisories against the ALIGNED mesh and
   stamps a fresh `advisories_derived_at`. Required because postinstall is used
   as admission evidence and Gap 3 forbids a stale `mesh.scaffold_only`.
7. Field Reports `pre-push` install (`field_reports.py install-hook`).
8. Strict pre-commit install (canary admission infrastructure only — TES does
   NOT auto-install strict pre-commit for adopters).
9. Baseline commit (clean tree).
10. Final oracle matrix, including the admission gate:
    - `installed_certification_oracle.py --target <canary>`
    - `tes_install.py hook-health --target <canary> --agent <active-host>`
    - `canary_admission_oracle.py --target <canary> --json-only`  <- MUST PASS
    - `project_context_oracle.py` / `project_alignment_oracle.py` /
      `tes_map_oracle.py` against the canary.

## Forbidden claims until replay proves them

- Do NOT claim `precommit_enforced`, `prepush_installed`, or `git_clean` without
  material Git evidence on the actual canary.
- Do NOT claim native hook PASS for a host whose OWN runtime records are absent;
  a configured-but-unobserved host is `CONFIGURED_NOT_OBSERVED`. A Claude-run
  replay may claim ONLY Claude native; Codex/Cursor native require their own
  runtime records observed in those hosts.
- Do NOT present `mesh.scaffold_only` as current-state after `/tes-align` passes
  without a post-align postinstall refresh.
- Do NOT claim `READY_FOR_GOAL_MAESTRO_CANARY` until `canary_admission_oracle.py`
  passes against the canary.

## Exact evidence files the replay session must produce

PREFLIGHT (canary read-only), CLEAN-INSTALL/PROVENANCE (bundle SHA match),
GIT-GATES (live HEADs captured at write time, never copied forward),
HOOK-EVIDENCE (per-host class), POSTINSTALL-REFRESH (advisories_derived_at fresh,
no stale mesh.scaffold_only), ADMISSION-MATRIX (admission oracle PASS + claims),
JOURNAL (per-action), FINAL-ADMISSION.

## Expected final replay state

`READY_FOR_GOAL_MAESTRO_CANARY` only if `canary_admission_oracle.py` PASSES and
the per-host hook claims are truthful; otherwise a named blocker
(`BLOCKED` / `NEEDS_EVIDENCE`) with the specific gate that failed.
