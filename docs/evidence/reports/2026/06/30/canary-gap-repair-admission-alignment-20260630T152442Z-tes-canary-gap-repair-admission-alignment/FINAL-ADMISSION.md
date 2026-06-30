---
tds_id: evidence.canary_gap_repair_admission_alignment.final_admission_20260630
tds_class: evidence
status: active
consumer: maintainers, canary operators, Goal Maestro operators
source_of_truth: false
evidence_level: L2
---

# FINAL-ADMISSION

```text
PACKAGE_READY_FOR_CANARY_REPLAY
```

This SPEC ends at package/source readiness. It explicitly does NOT claim
`READY_FOR_GOAL_MAESTRO_CANARY` — that state belongs only to the later canary
replay session, after `canary_admission_oracle.py` passes against a real canary.

## Confirmed gaps and their package fixes

1. Git / pre-commit / pre-push admission — NEW `canary_admission_oracle.py`
   (maintainer gate) blocks readiness without Git + pre-push + strict pre-commit
   and never claims them without material evidence. Docs updated.
2. Bundle / bytecode hygiene — `tes_bundle.py` excludes/purges/rejects bytecode;
   `public_bundle_oracle.py` rejects bytecode ZIP members;
   `installed_certification_oracle.py` flags delivered-skill/staged bytecode.
   Bundle refreshed clean (378 entries, pycache 0).
3. Stale `mesh.scaffold_only` — `tes_install.py` scopes advisories to the
   producing run (`derived_at`) and writes `advisories_derived_at`; a
   scaffold -> aligned transition drops the advisory.
4. `hook_runtime_health=NEEDS_EVIDENCE` under PASS — per-host truthfulness
   enforced at admission: configured-but-unobserved hosts are
   CONFIGURED_NOT_OBSERVED; no cross-host evidence filling. The existing
   aggregate-PASS-keeps-NEEDS_EVIDENCE-visible guard was confirmed.

All four carry red-capable proofs (see ORACLE-RESULTS.md).

## Release identity

Owner-confirmed: patch bump `0.3.231 -> 0.3.232` + local bundle refresh. No
push / tag / publish. The package is package-ready, NOT release-sealed (no
`commit:closure`, no tag, no `release:check`).

## Stop state

```text
PACKAGE_READY_FOR_CANARY_REPLAY
```

## Claims forbidden until the replay session proves them

precommit_enforced, prepush_installed, git_clean, native Codex/Cursor hook PASS,
absence of mesh.scaffold_only post-align, READY_FOR_GOAL_MAESTRO_CANARY.

## Next session

The dedicated canary replay session, per CANARY-REPLAY-HANDOFF.md, against a
freshly Git-initialized canary installed from
`docs/dist/0.3.232/tilly-engineer-skills-0.3.232.zip`
(sha256 b0f8eee3ad7b3ba115efcd2c3576042029ac2ef8b8573724758952826a88c987).
