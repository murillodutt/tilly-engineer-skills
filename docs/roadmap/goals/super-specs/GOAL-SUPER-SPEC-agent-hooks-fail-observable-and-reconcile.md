---
tds_id: roadmap.goal_super_spec_agent_hooks_fail_observable_and_reconcile
tds_class: roadmap
status: proposed
consumer: maintainers, installer authors, hook authors, oracle authors, canary operators, and execution agents
source_of_truth: false
evidence_level: L1
---

# GOAL Super SPEC: Agent Hooks Fail Observable And Reconcile

Status: proposed execution packet for one isolated window.

Run this SPEC after or in parallel with the other agent-hook hardening specs
only from a dedicated branch or worktree. This packet owns degraded execution
visibility and helper reconciliation, not shell intent or provenance semantics.

## New-Window Prompt

```text
/goal Execute docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-agent-hooks-fail-observable-and-reconcile.md with tes-host-transcript-canary for any installed-host claim. Use a dedicated branch or worktree, reproduce helper-missing/ledger-write/sentinel-corruption/orphan-helper gaps first, patch TES source surgically, and close only with focused red-capable oracles plus package identity.
```

## Senior Framing

Protected baseline: hook execution must not break the user's host workflow for
ordinary telemetry failures. But "hook did not supervise" must never be
indistinguishable from "hook supervised and passed".

The mature policy is not global fail-closed. It is risk-typed: security
controls may block; telemetry and evidence failures may allow host execution
only if they emit machine-readable degraded evidence.

Classification: `Platform`. This touches delivered helpers, hook runtime,
ledger evidence, installed target health, and update behavior.

## Findings Owned

- BUG-01: top-level imports of `pretooluse_kernel` and `pretooluse_session` can
  crash the hook without a degraded hook signal.
- BUG-02: ledger write failure is swallowed silently.
- PREC-03: anti-cry-wolf sentinel handles only `OSError`; corrupted bytes can
  escape, and `context_suppressed` is not used as claimed.
- DEBT-01: retired hook runtime helpers are not pruned from `.tes/bin`.
- F1 residual: helper drift is not fully covered by the same materialized
  inventory.

## Non-Goals

- Do not make every hook helper failure block host tool use.
- Do not delete target files by glob or guesswork.
- Do not build a package manager.
- Do not conflate this work with host-real provenance. Provenance has its own
  SPEC.

## Execution Rules

- Use a dedicated branch or worktree.
- If another spec changes `scripts/tes_install.py`, `scripts/tes_update.py`, or
  helper materialization logic, rebase and rerun all install/update gates.
- Prune only files that a TES-owned manifest proves TES materialized.
- Emit degraded evidence without raw command, raw prompt, or raw transcript.

## SPEC-000: Reproduce Degraded Blind Spots

Create focused fixtures before editing:

- missing `pretooluse_kernel.py` or import failure causes host hook to degrade
  observably, not crash silently;
- ledger directory not writable or write failure records a machine-readable
  degraded state;
- sentinel file with invalid UTF-8 does not crash hook flow;
- repeated context returns the intended `context_suppressed` state;
- retired helper remains in `.tes/bin` today and is not detected/pruned.

If any fixture already passes, mark it as baseline and do not patch that path.

## SPEC-001: Degrade Loud For Helper Import Failures

Required behavior:

- Kernel/session import failure produces `SUPERVISION_DEGRADED` or equivalent
  structured reason code.
- Host renderers preserve their protocol: Claude/Codex stderr or additional
  context as appropriate; Cursor JSON protocol remains valid.
- The hook exits according to host contract and does not fake a green
  supervision result.
- Hook-health and installed certification can observe the degraded state.

## SPEC-002: Ledger Failure Visibility

Required behavior:

- Ledger write failure remains non-fatal unless the host action itself is
  forbidden.
- Failure writes a safe breadcrumb where possible.
- Related oracles can distinguish "no hook evidence because write failed" from
  "hook never ran".
- No raw command/path/secret is included in the degraded breadcrumb.

## SPEC-003: Sentinel Robustness

Required behavior:

- Invalid sentinel encoding degrades safely and does not crash the hook.
- `context_suppressed` has one clear contract:
  either repeated context is truly suppressed and recorded, or the field is
  removed/renamed so it cannot lie.
- Anti-cry-wolf remains anti-noise: one session should not spam the same
  context.

## SPEC-004: Materialized Helper Inventory

Required behavior:

- Hook runtime helper materialization records a TES-owned inventory with path
  and sha256.
- Update/install can prune helpers that are in the previous TES-owned inventory
  but no longer in the desired helper set.
- Prune is gated by a non-empty previous inventory; no scan-and-guess delete.
- Helper drift within the same version is detectable by sha256 comparison.
- `__pycache__` cleanup is safe and scoped to TES-owned helper directories.

## SPEC-005: Red-Capable Oracles

Update focused oracles so each gap fails before fix:

```bash
python3 scripts/tes_install.py --self-test
python3 scripts/install_smoke.py --self-test
python3 scripts/installed_certification_oracle.py --self-test
python3 scripts/attach_health_oracle.py --self-test
python3 scripts/tes_update.py --self-test
python3 scripts/materialize_adapter.py all --check
```

For installed-target evidence, run a clean target and verify hook-health reports
degraded states accurately. Use `tes-host-transcript-canary` only for host-real
claims.

## SPEC-006: Release Identity And Closeout

Delivered behavior changed. Unless explicitly deferred:

```bash
python3 scripts/tes_bump.py patch --yes --json
python3 scripts/tes_bundle.py publish --adapter all --allow-dirty --gate
python3 scripts/build_public_docs.py
python3 scripts/public_bundle_oracle.py
python3 scripts/validate_reference_package.py
npm run commit:check
```

Acceptance: helper/import/ledger/sentinel failures are observable, retired
helpers reconcile through a TES-owned inventory, no guessed deletion occurs, and
all related install/update gates pass.
