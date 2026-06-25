---
tds_id: evidence.context_mesh.project_alignment_oracle_false_positive_2026_05_13_journal
tds_class: evidence
status: active
consumer: TES maintainers and project-alignment oracle maintainers
source_of_truth: false
evidence_level: L3
tver: 0.1.0
---

# Project Alignment Oracle False Positive Loop

## Ledger

- 2026-05-13T00:00:00Z `FRAMED`: Target canary `<private-canary-path>`; TES baseline `b221805fb21a725cbf55848b4c52e355036534b5`; canary baseline `fe2230ace58dae3ccbe571ba60e3231dd7c8ced1`.
- Hypothesis: `project_alignment_oracle.py` should ignore placeholder-like terms inside literal filenames and shell commands while still catching real placeholder prose.
- Acceptance criteria: source self-test includes the adversarial fixture; original <canary-project> oracle run no longer fails on `docs-archive/MCP-TESTS-TODO.md` or `vitest run tests/integration`; related package gates pass or blockers are named.
- False-green risk: deleting placeholder detection entirely would make the oracle pass without proving the claim.
- First failure observed: `python3 scripts/project_alignment_oracle.py --target <private-canary-path>` failed with `todo` and `run tests` in `docs/agents/PROJECT-CONTEXT.md`.
- Failure classification: `oracle_gap`.
- Canary integrity: <canary-project> is read-only for this loop; no canary files, remotes, secrets, hooks, or commits will be changed.
- 2026-05-13T00:00:00Z `BUILT`: Added an adversarial self-test fixture with `docs-archive/MCP-TESTS-TODO.md`, `vitest run tests/integration`, and `vitest run tests/validation`.
- 2026-05-13T00:00:00Z `FAILURE_OBSERVED`: The new fixture failed under the old substring scanner with `todo` and `run tests`.
- 2026-05-13T00:00:00Z `CAUSE_CLASSIFIED`: The cause is context-free placeholder scanning across Markdown literals, path literals, and command cells.
- 2026-05-13T00:00:00Z `FIX_APPLIED`: `generic_failures()` now scans a searchable projection that ignores fenced code, inline code spans, path literals, and command-like Markdown table cells, while preserving prose placeholder detection through explicit term regexes.
- 2026-05-13T00:00:00Z `ORIGINAL_RETESTED`: `python3 scripts/project_alignment_oracle.py --target <private-canary-path>` returned `PASS` without changing the canary.
- 2026-05-13T00:00:00Z `RELATED_GATES_RUN`: `python3 scripts/project_alignment_oracle.py --self-test`, `python3 scripts/public_bundle_oracle.py`, `python3 scripts/build_public_docs.py --check`, `python3 scripts/validate_tds.py`, `python3 scripts/validate_reference_package.py`, `python3 scripts/tes_bundle.py --self-test`, `python3 scripts/materialize_adapter.py all --check`, `python3 scripts/adapter_parity_readiness.py`, and `npm run commit:check` returned `PASS`.
- 2026-05-13T00:00:00Z `LEARNING_PROMOTED_OR_DEFERRED`: Portable learning was promoted into the oracle scanner, adversarial source fixture, TDS index, public bundle `0.3.86`, and release identity surfaces. The updater self-update gap and Cursor trigger-block ergonomics remain deferred next loops.

## 4D Scan

```yaml
four_d_scan:
  discovery: >
    Placeholder scanners that read generated Markdown as raw text can punish
    truthful project inventories and command tables, creating false DRIFT in
    real project canaries.
  axis: reusable_pattern
  selection: apply_now
  target: scripts/project_alignment_oracle.py and its self-test fixture
  verification: >
    python3 scripts/project_alignment_oracle.py --self-test;
    python3 scripts/project_alignment_oracle.py --target
    <private-canary-path>; npm run commit:check
  decay: >
    Keep this as an oracle-local scanner rule. Do not move it into broad TES
    governance unless a second oracle shows the same literal-context failure.
```

## Certification Packet

```yaml
build_test_fail_fix:
  mode: persistent_e2e
  final_state: CERTIFIED
  target: <private-canary-path>
  baseline:
    tes: b221805fb21a725cbf55848b4c52e355036534b5
    canary: fe2230ace58dae3ccbe571ba60e3231dd7c8ced1
  hypothesis: >
    The alignment oracle should ignore placeholder-like terms inside literal
    filenames and shell commands while still catching real placeholder prose.
  acceptance_criteria:
    - adversarial fixture fails before scanner repair
    - source self-test passes after repair
    - original <canary-project> canary retest passes without target edits
    - release identity and correlated gates pass
  first_failure_or_falsifiability: >
    Old scanner failed on docs-archive/MCP-TESTS-TODO.md and vitest run
    tests/integration.
  classification: oracle_gap
  fix: >
    Added literal-aware placeholder scanning plus an adversarial self-test and
    bumped local package identity to 0.3.86.
  exact_retest: >
    python3 scripts/project_alignment_oracle.py --target
    <private-canary-path> -> PASS
  related_gates:
    - python3 scripts/project_alignment_oracle.py --self-test -> PASS
    - python3 scripts/public_bundle_oracle.py -> PASS
    - python3 scripts/build_public_docs.py --check -> PASS
    - python3 scripts/validate_tds.py -> PASS
    - python3 scripts/validate_reference_package.py -> PASS
    - python3 scripts/tes_bundle.py --self-test -> PASS
    - python3 scripts/materialize_adapter.py all --check -> PASS
    - python3 scripts/adapter_parity_readiness.py -> GO
    - npm run commit:check -> PASS
  canary_integrity: >
    <canary-project> was only read and tested. No canary files, secrets, hooks, remotes,
    commits, or runtime settings were changed by this loop.
  portable_promotions:
    - literal-aware scanner behavior
    - adversarial source fixture
    - TDS-indexed journal
    - package identity and local public bundle 0.3.86
  deferred_learning:
    - canonical helper self-update route
    - Cursor trigger block delimiter for customized rules
  final_state: CERTIFIED
  next_loop: >
    Build-Test-Fail-Fix the helper-only update route so older meshed installs
    self-update the planner before discovering new helper requirements.
```

## Technical Journal

What became more mature: project alignment now separates placeholder prose from literal project evidence, and the failure is protected by a self-test plus real canary replay.

What still feels weak: the update path still required manual helper overwrite in the <canary-project> report, and Cursor trigger edits still rely on human surgical care when a project owns custom rule prose.

Portable improvement candidates: add a helper-only apply/self-update route to `tes_update.py`; add a managed trigger block for Cursor rules; consider a shared literal-aware scanner helper only after another oracle repeats this failure.

Local-only deferred observations: <canary-project> has valid inventory paths and script tables that should not be rewritten merely to satisfy a scanner.

Next highest-leverage loop: repair `tes_update.py` so stale helper updates can converge without manual GitHub tree inspection or hand-applied SHA-verified overwrites.
