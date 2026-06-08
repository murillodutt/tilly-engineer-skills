---
tds_id: evidence.context_mesh.release_0_3_178_nested_core_advisories_journal
tds_class: evidence
status: active
consumer: TES maintainers, root-context maintainers, and postinstall advisory maintainers
source_of_truth: false
evidence_level: L3
tver: 0.1.0
---

# Release 0.3.178 — Nested-Core Dedup, First-Session Advisories, Sanctioned-Drift Attestation

## Ledger

- 2026-06-08T00:00:00Z `FRAMED`: TES baseline (pre-cycle)
  `bf8df3ba0f6292b5cde6898c83393e46cd9d25e8` (`0.3.177`). Driven by a real
  external review plus a real-project canary (`<private-canary-path>`, source of
  record kept off TES repository). Inputs: two analysis journals
  (`JOURNAL-UPDATE-v0.3.177`, `JOURNAL-tes-recovery-20260608`) listing five
  residual post-PASS GAPs, plus a sixth GAP discovered while reading the
  canary's root bootloader.
- Hypothesis: the residual GAPs are product decisions (advisories, attestation),
  except one — a real artifact-corruption defect in root-context composition —
  and all fixes belong in TES source, generic, never individualized to the
  canary.
- Acceptance criteria: GAP-6 cures duplicated `TES:CORE` to exactly one,
  preserving the project overlay byte-for-byte; the four advisories fire from
  signals already on the `tes_init` payload without re-running oracles and never
  change PASS; the sanctioned-drift oracle preserves current behavior when no
  attestation exists; release identity synchronizes; the published bundle (not
  just source) demonstrates the cure; commit:check and release certification
  pass.
- False-green risk: a self-test that only exercises synthetic fixtures would
  pass while the installed/distributed surface still misbehaves — so the cure
  must be proven from the published bundle and a real install, not only from
  `scripts/`.
- Failure classification: GAP-6 `generator_contract_conflict` (artifact
  corruption); GAP-1/2/3/4/5 `product_capability_gap`.
- Canary integrity: `<canary-project>` was read-only for this loop. Its
  `CLAUDE.md` was inspected as symptom evidence only; no canary files, remotes,
  secrets, hooks, or commits were changed. Its cure is a downstream consequence
  of the next `/tes-update`, not an edit made here.
- 2026-06-08T00:00:00Z `BUILT`: (Fase A) `strip_nested_core` added to
  `root_context.py`, applied inside `compose_root_context` when the project
  overlay is preserved, anchored on the module markers `CORE_BEGIN_RE`/`CORE_END`
  so a missing END never consumes legitimate overlay. (Fase 0) `collect_advisories`
  added to `tes_install.py` reading the in-memory `tes_init` payload; advisories
  rendered to the Claude channel and the CLI JSON, persisted in the sentinel.
  (Fase 1) new `root_context_sanctioned_oracle.py` cloned from the
  private-vocabulary allowlist pattern (PASS-when-empty), integrated into
  `root_context.classify_file`/`analyze` with a tolerant import. (Fase 2)
  `mesh_scaffold_only` field in `project_alignment_oracle.py`; threshold +
  `pending_advisory` in `field_reports.py` (env `TES_FIELD_REPORTS_PENDING_THRESHOLD`,
  default 30); GAP-1 and GAP-4 consume existing oracle fields.
- 2026-06-08T00:00:00Z `FAILURE_OBSERVED`: the first end-to-end install
  reproduced two collector bugs that synthetic self-tests had not caught — the
  advisories were empty on a fresh install. Root causes (1) `run_helper` parsed
  the helper payload but never attached it to its `command_result`, so the
  collector received `{}`; (2) the Cortex needle `"cortex.py"` matched the
  `verify` gate (no `cell_count`) instead of `audit`. A third packaging gap:
  the new oracle was absent from `.tes/bin/` because it was missing from the
  install/update copy lists, so the attestation was inert on targets.
- 2026-06-08T00:00:00Z `CAUSE_CLASSIFIED`: a herited architectural assumption
  ("run_helper already returns the payload") was false; plus an
  over-broad gate needle; plus packaging-list omission across `install_mcp.py`
  (`SERVER_FILES`), `tes_update.py`, and `validate_reference_package.py`.
- 2026-06-08T00:00:00Z `FIX_APPLIED`: `run_helper` now attaches the parsed
  `payload` to its `command_result`; the run record strips it again before
  persistence to avoid bloat. Cortex needle narrowed to `"cortex.py audit"`.
  The new oracle registered in every packaging list and shipped in the bundle.
  The `root_context` self-test made tolerant of the oracle being absent in
  isolated installed-helper runs (asserts suppression only when importable,
  degradation otherwise).
- 2026-06-08T00:00:00Z `ORIGINAL_RETESTED`: a fresh install + forced postinstall
  emitted `mesh.scaffold_only` and `cortex.empty`, persisted in the sentinel,
  with `status: PASS` (PASS preserved). The installed `root_context.py` imports
  the shipped oracle and the attestation suppresses the structure gate for a
  declared path while empty attestation preserves `NEEDS_REVIEW`.
- 2026-06-08T00:00:00Z `BUNDLE_REPLAYED`: the GAP-6 fix was re-proven against
  the `root_context.py` extracted from the published bundle
  `tilly-engineer-skills-0.3.178.zip` — a contaminated root (2 cores) composed
  back to exactly 1, overlay preserved, fossil removed, `COMPOSED`, and
  idempotent on a second compose.
- 2026-06-08T00:00:00Z `RELATED_GATES_RUN`: `npm run commit:check` (full suite)
  `PASS`; `python3 scripts/tes_bump.py --governance-check` `PASS: synchronized`;
  per-surface self-tests (`root_context`, `root_context_sanctioned_oracle`,
  `project_alignment_oracle`, `field_reports`, `tes_install`, `tes_init`) `PASS`.
- 2026-06-08T00:00:00Z `RELEASED`: identity bumped `0.3.177 -> 0.3.178` across
  package.json, 44 script VERSION constants, plugin/marketplace manifests,
  public docs, i18n, and the regenerated `docs/dist/0.3.178` bundle
  (single-current-dist pruned `0.3.177`). Commit
  `dad9d5c852d9d66d79f94ec7147d1913f6ae92de`. Pushed to `main`; annotated tag
  `v0.3.178` at HEAD pushed. `npm run release:check` ->
  `status: PASS, classification: certified_local, resolved_commit = HEAD`.
  `public_pages_oracle --version 0.3.178` -> `PASS` (Pages serving `dist/0.3.178`).
- 2026-06-08T00:00:00Z `LEARNING_PROMOTED_OR_DEFERRED`: portable learning
  promoted — the one-core invariant in the compositor, the payload-on-command
  contract in `run_helper`, the unified advisory collector, the sanctioned-drift
  oracle, and the rule that a packaged helper must enter every copy list and the
  bundle before its feature is real on targets. Deferred: GAP-1 freshness
  reconciliation in the canary itself (a project-side `/tes-align`, Plane 2, out
  of TES scope); whether scaffold-only/empty-Cortex advisories should escalate
  beyond informational on mature projects.

## 4D Scan

```yaml
four_d_scan:
  discovery: >
    A deterministic root-context compositor that preserves the project overlay
    verbatim re-injects any TES:CORE block fossilized inside it on every update,
    duplicating the core indefinitely. Self-tests that never feed a contaminated
    overlay pass green while the installed artifact corrupts further each cycle.
  axis: durable_invariant
  selection: apply_now
  target: scripts/root_context.py compose_root_context (strip_nested_core)
  verification: >
    python3 scripts/root_context.py --self-test; compose a contaminated root
    from the published-bundle root_context.py and assert exactly one
    TES:CORE with the overlay preserved; npm run commit:check; npm run
    release:check; public_pages_oracle --version 0.3.178
  decay: >
    Keep the one-core invariant in the compositor. The advisory collector and
    sanctioned-drift attestation are product capabilities, not invariants;
    revisit their escalation policy only if a real project asks for blocking
    behavior.
```

## Certification Packet

```yaml
build_test_fail_fix:
  mode: persistent_e2e
  final_state: CERTIFIED
  target: TES source package + published bundle + fresh real install
  baseline:
    tes_pre_cycle: bf8df3ba0f6292b5cde6898c83393e46cd9d25e8
    tes_release_commit: dad9d5c852d9d66d79f94ec7147d1913f6ae92de
    bundle_sha256: f4debae9e772f784a48c36ad19e6e72928fa8c4a8025b0d6fb5c6282e9cc59b4
    tag: v0.3.178
  hypothesis: >
    Five residual post-PASS GAPs are product decisions; a sixth is a real
    artifact-corruption defect. All fixes belong in TES source, generic, with
    automatic target cure on the next update and nothing individualized to the
    canary.
  acceptance_criteria:
    - GAP-6 reduces duplicated TES:CORE to exactly one, overlay preserved, idempotent
    - four advisories fire from the tes_init payload without re-running oracles, PASS preserved
    - sanctioned-drift oracle is PASS-when-empty and suppresses only declared paths
    - the published bundle (not just source) demonstrates the cure
    - release identity synchronized; commit:check, release:check, and Pages pass
  first_failure_or_falsifiability: >
    Fresh-install advisories were empty because run_helper discarded the parsed
    payload and the Cortex needle matched the verify gate; the new oracle was
    absent from .tes/bin/ on targets.
  classification: generator_contract_conflict (GAP-6) plus product_capability_gap (GAP-1..5)
  fix: >
    strip_nested_core enforces the one-core invariant in the compositor;
    run_helper attaches the parsed payload (stripped from the persisted run
    record); Cortex needle narrowed to "cortex.py audit"; the sanctioned-drift
    oracle registered in every packaging list and the bundle; root_context
    self-test tolerant of the oracle's absence.
  exact_retest: >
    fresh install + postinstall --force -> PASS with advisories
    [mesh.scaffold_only, cortex.empty]; published-bundle root_context.py composes
    a 2-core contaminated root to 1 (overlay preserved, COMPOSED, idempotent)
  related_gates:
    - npm run commit:check -> PASS
    - python3 scripts/tes_bump.py --governance-check -> PASS (synchronized)
    - python3 scripts/root_context.py --self-test -> PASS
    - python3 scripts/root_context_sanctioned_oracle.py --self-test -> PASS
    - python3 scripts/project_alignment_oracle.py --self-test -> PASS
    - python3 scripts/field_reports.py --self-test -> PASS
    - python3 scripts/tes_install.py --self-test -> PASS
    - python3 scripts/tes_init.py --self-test -> PASS
    - npm run release:check -> PASS (certified_local, resolved_commit = HEAD)
    - python3 scripts/public_pages_oracle.py --version 0.3.178 -> PASS
  canary_integrity: >
    <canary-project> was only read. Its CLAUDE.md was inspected as symptom
    evidence; no canary files, secrets, hooks, remotes, commits, or runtime
    settings were changed. Its cure follows from the next /tes-update against the
    certified #v0.3.178 installer.
  portable_promotions:
    - one-core invariant in compose_root_context (strip_nested_core)
    - payload-on-command contract in run_helper
    - unified advisory collector reading the tes_init payload
    - root_context_sanctioned_oracle (PASS-when-empty attestation)
    - packaging rule: a shipped helper must enter every copy list and the bundle
  deferred_learning:
    - GAP-1 freshness reconciliation inside the canary (project-side /tes-align, Plane 2)
    - escalation policy for scaffold-only / empty-Cortex advisories on mature projects
  final_state: CERTIFIED
  next_loop: >
    Replay the original project canary against the certified #v0.3.178 installer
    to confirm the root-context cure lands, then decide the advisory escalation
    policy from real-project evidence.
```

## Technical Journal

What became more mature: root-context composition now carries a durable one-core
invariant proven from the distributed artifact, not just source; first-session
PASS is no longer silent on scaffold-only mesh, empty Cortex, freshness drift, or
outbox backlog; and a project can attest sanctioned root-drift to stop recurring
`NEEDS_REVIEW -> RECOVERED` noise.

What still feels weak: the freshness GAP only clears when the project runs
`/tes-align` to reconcile ADR vocabulary into the Tier-2 mesh — that is
project-side work (Plane 2), so a green TES PASS still ships a project that has
not refined its mesh. The advisory only nudges; it does not drive the
reconciliation.

Portable improvement candidates: a single guard that asserts any new delivered
helper is present in every copy list and the bundle before a release closes — the
packaging-list omission found here was caught only by an installed-mode gate, not
at authoring time.

Local-only deferred observations: the canary's contaminated root is a
point-in-time symptom; its repair is the next `/tes-update`, not an edit in this
loop.

Next highest-leverage loop: replay the original project canary against the
certified `#v0.3.178` installer to confirm the cure lands end-to-end, then use
that real-project evidence to settle the advisory escalation policy.
