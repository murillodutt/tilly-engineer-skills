---
tds_id: evidence.canary_gap_repair_admission_alignment.oracle_results_20260630
tds_class: evidence
status: active
consumer: maintainers, oracle authors, canary operators
source_of_truth: false
evidence_level: L2
---

# ORACLE-RESULTS — Focused Self-Tests And Gates

All commands run with `PYTHONDONTWRITEBYTECODE=1` and
`PY=/opt/homebrew/opt/python@3.14/bin/python3.14` from the package root.

## Changed-surface self-tests (final snapshot, all green)

```text
tes_bundle.py --self-test                       PASS
installed_certification_oracle.py --self-test   PASS
canary_admission_oracle.py --self-test          PASS
public_bundle_oracle.py                         PASS
tes_install.py --self-test                      PASS
```

## Red-capability proofs (falsifiable, not report-only)

Each new/changed guard was proven to turn RED when its detector is neutralized,
then restored to green:

```text
Gap 2  tes_bundle.py             neutralize is_build_artifact ->
                                 FAIL: "did not purge source Python bytecode",
                                       "validate_manifest must reject a bytecode entry"
Gap 2  installed_certification   neutralize bytecode detection ->
                                 FAIL: "delivered-skill Python bytecode must drive
                                        artifact_hygiene FAIL" (+3 related)
Gap 3  tes_install.py            force scaffold advisory while aligned ->
                                 FAIL: "after scaffold -> aligned transition,
                                        mesh.scaffold_only must NOT remain"
Gap 1  canary_admission_oracle   neutralize Git gate ->
                                 FAIL: "no-Git target must BLOCK admission"
Gap 4  canary_admission_oracle   neutralize per-host isolation (cross-host fill) ->
                                 FAIL: "no cross-host evidence filling"
```

## Bundle-readiness oracles (SPEC-008)

```text
tes_bundle.py publish --adapter all   BUILT (0.3.232, 378 entries, pycache 0)
public_bundle_oracle.py               PASS
tes_install.py --self-test            PASS
install_smoke.py --self-test          PASS
```

## Package validation gates (SPEC-007)

```text
git diff --check                      clean
validate_doc_size.py                  exit 0 (no doc over threshold)
validate_reference_package.py         0 real failures; only this run's
                                      not-yet-TDS-indexed evidence files (now indexed)
validate_tds.py                       see closeout (after TDS index update)
npm run commit:check                  see closeout
```

## Baseline (before edits)

Every changed-surface self-test was green before edits (regression baseline):
`tes_bundle`, `public_bundle_oracle`, `tes_install`, `installed_certification`,
`tes_init` (56s), `project_alignment_oracle`, `project_context_oracle`,
`tes_map_oracle`, `field_reports` — all exit 0. `validate_reference_package` was
exit 1 only from (a) a spurious empty root `.cursor/` dir [removed] and (b) this
run's not-yet-indexed evidence files — not a pre-existing broken baseline.

## Adversarial verification round (confront-and-certify)

A 5-agent adversarial workflow (Opus only) tried to refute each fix. Verdicts:
all four gaps `closes_gap: true`, `forbidden_claim_leak: false`, confidence
`high`. Three coverage weaknesses were found (none reopen a classified gap) and
each was then fixed with a proven red-capable fixture:

```text
Gap 4 (visibility): installed_certification_oracle self-test had a DEAD guard
  (the healthy fixture writes a full ledger, so its NEEDS_EVIDENCE branch never
  fired). Added a configured-hooks-without-runtime fixture that drives
  hook_runtime_health=NEEDS_EVIDENCE and asserts the finding stays visible AND
  the aggregate stays PASS. Red-capable: deleting the NEEDS_EVIDENCE finding
  emission (the silent collapse) -> FAIL "NEEDS_EVIDENCE finding must remain
  visible (not silently collapsed)".
Gap 2 (suffix branch): the bytecode self-test planted the .pyc INSIDE __pycache__,
  so only the directory branch of is_build_artifact was exercised; the bare
  .pyc/.pyo suffix branch was unprotected. Added bare-.pyc/.pyo assertions and a
  bare-pyc manifest-rejection case. Red-capable: neutralizing ONLY the suffix
  branch -> FAIL on the bare .pyc/.pyo + bare-pyc manifest cases.
Gap 2 (root skills/): installed_certification BYTECODE_GUARDED_ROOTS omitted the
  root-level skills/ territory (OS-residue scan was tree-wide, bytecode scan was
  4 named roots). Added "skills" to BYTECODE_GUARDED_ROOTS.
```

The regression-bump verifier confirmed: non-fix scripts are VERSION-only
(0.3.231 -> 0.3.232), zero contamination staged, new bundle clean (378 entries,
0 bytecode). Its `closes_gap: false` only means "the commit is not a pure
VERSION-only bump" — by design it bundles the gap-repair logic, which is the
intended work, not contamination.

## Post-verification re-validation

```text
installed_certification_oracle.py --self-test   PASS  (+ NEEDS_EVIDENCE fixture red-capable)
tes_bundle.py --self-test                       PASS  (+ suffix/dir fixtures red-capable)
public_bundle_oracle.py                         PASS  (bundle re-published to reconcile helper drift)
npm run commit:check                            PASS  (staged_files 81)
```

Bundle re-published after the coverage fixes:
sha256 `9461e708f5ba1c3b16f6669653581da6dcca37989cf51d2725c4e2f54d9bcf68`
(supersedes the earlier b77c3183 build), 378 entries, pycache 0.
