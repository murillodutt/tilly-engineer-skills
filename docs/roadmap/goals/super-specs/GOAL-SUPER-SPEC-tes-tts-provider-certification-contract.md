---
tds_id: roadmap.goal_super_spec_tes_tts_provider_certification_contract
tds_class: roadmap
status: proposed
consumer: maintainers, tes-tts maintainers, adapter authors, validation authors, and execution agents
source_of_truth: false
evidence_level: L1
---

# GOAL Super SPEC: TES TTS Provider Certification Contract

Status: open contract-consistency line. Closes finding P-3 from the 2026-06-02
systematic audit — the live probe emits `certifies_provider_support: true` while
the probe oracle and ADR 0004 forbid certifying provider support.

Canonical artifact:
`docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-tes-tts-provider-certification-contract.md`

Current execution unit:
`closed locally`

Ready prompt:
`next line: audio-audit-resolver (W-3)`

## Execution Record (2026-06-02)

- PCC-001 DONE: surfaced the decision. Confirmed the same key meant two things:
  the live probe emitted `certifies_provider_support = available` (true when the
  optional env is usable), while the oracle/ADR require `false` (certified for
  redistribution). **Owner decision: rename the probe key** — report what the
  probe measures separately from the certification claim.
- PCC-002 DONE: the probe (`tes_tts_omnivoice_provider.py:223-224`) now emits
  `environment_usable` (the real measurement) and a fixed
  `certifies_provider_support: False` (ADR-aligned). The
  `omnivoice_provider_oracle` now asserts the live value
  (`certifies_provider_support is not False` fails; `environment_usable` must be
  bool) — closing the gap that let P-3 hide. `environment_usable` added to
  `REQUIRED_PROBE_KEYS`.
- PCC-003 CERTIFY: live probe now reports `certifies_provider_support=False`,
  `environment_usable=True`, `status=provider_available`. provider oracle PASS,
  provider_probe oracle PASS, full suite PASS 20/20. No skill doc referenced the
  key (no documental drift); the `status` command does not emit it. Governed
  gates (materialize/tds) PASS.
- Release identity: provider is a bundled helper; same `DELIVERED_BEHAVIOR_GLOBS`
  condition as P-1 — bump/bundle DEFERRED to an owner decision.

Prior line:
`docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-tes-tts-language-inference-hardening.md`
(LIH / P-2, locally closed).

Audit source:
`TES-TTS-SYSTEMATIC-ANALYSIS-2026-06-02.md`, finding P-3.

## This line carries an owner decision, not just a defect

Unlike the prior lines, P-3 is not a clear-cut bug. The same key
(`certifies_provider_support`) means opposite things in two places, and which
side is "right" is an owner call:

- The live provider emits `"certifies_provider_support": available`
  (`scripts/tes_tts_omnivoice_provider.py:219`) — `true` when OmniVoice is
  installed and usable.
- The probe oracle requires it to be `False`
  (`scripts/tes_tts_provider_probe_oracle.py:293-294`: "plan must not certify
  provider support").
- ADR 0004 forbids provider certification.

The oracle never confronts the live provider output (it validates mocked
fixtures), so the contradiction is invisible to the gate. PCC-001 must surface
the decision before any code changes.

## Mantra Gate Snapshot

- `VERIFY`: live `probe` returns `certifies_provider_support: true` with
  OmniVoice installed; the oracle and ADR say it must be `false`.
- `SCOPE`: reconcile the contract — either the key is mis-named (the live value
  means "environment usable", not "certified for redistribution") or the live
  value must change. No provider behavior change beyond this field's meaning.
- `BEST_PATH`: name the two readings, get the owner decision, then make the live
  output and the oracle agree, and have an oracle assert the live value.
- `DOCUMENT`: this Super SPEC and one ready `PCC-001` prompt are the authority.
- `ORACLE`: after the decision, an oracle must assert the live probe's value of
  this field — today nothing does.
- `RESOLVE`: provider is a delivered helper; a `release_identity` decision is
  required before closeout. No release, push, tag, publish, or sync.
- `STATUS`: `NEEDS_OWNER_DECISION` before correction; `PASS_TO_EXECUTE` for the
  analysis unit.

## Purpose

Make the provider-certification contract internally consistent and gate-checked,
so the live probe and the oracle/ADR cannot silently disagree about whether TES
"certifies" a provider. The likely resolution is naming: separate "the optional
environment is usable" from "the provider is certified for redistribution" —
but the owner decides.

## Certified Context

- Baseline: commit `a3ffaf4`, runtime VERSION `0.3.157`.
- `tes_tts_omnivoice_provider.py` is a delivered helper (bundled, `.tes/bin/**`),
  so changing the probe output is delivered behavior under `release_identity`.
- ADR 0004 and OWNER-001 forbid provider certification; that boundary stands
  unless the owner explicitly re-scopes it.

## Protected Invariants

- The probe still truthfully reports whether the optional environment is usable.
- ADR 0004's "no provider certification for redistribution" boundary is not
  weakened by a rename.
- The other 20 oracles stay green.

## Non-Objectives

- no provider install, download, or actual certification for redistribution;
- no release, bump, push, tag, publish, or sync executed in this line;
- no change to synthesis, redaction, or language behavior.

## Execution Units

| Unit | Focus | Boundary |
|------|-------|----------|
| PCC-001 | Surface the decision | Present the two readings (rename the field vs change the live value) with their consequences; record the owner decision. No code change. |
| PCC-002 | Reconcile + assert | Apply the decided change so the live probe and the oracle agree, and add an oracle assertion over the live probe's value (the gap that let P-3 hide). |
| PCC-003 | Certify + local commit | Full suite + governed gates green; record the release_identity decision; local commit. |

## Required Loop

```text
analise -> owner decision -> correção -> certificação -> local commit -> create next line
```

PCC-001 stops at the owner decision by design — it is a real
`NEEDS_OWNER_DECISION`, not a habit pause. The loop resumes once the owner
chooses. Closing this line creates the next Super SPEC (see Closure).

## Certification

```bash
python3 scripts/tes_tts_provider_probe_oracle.py --self-test
python3 scripts/tes_tts_oracles_suite.py
python3 scripts/materialize_adapter.py all --check
python3 scripts/validate_tds.py
python3 scripts/validate_doc_size.py
python3 scripts/tes_bump.py --governance-check
git diff --check
```

## Stop States

- `PASS`: live probe and oracle agree, an oracle asserts the live value, ADR
  boundary intact, suite green.
- `NEEDS_OWNER_DECISION`: the rename-vs-revalue choice, or any re-scoping of the
  ADR boundary, needs maintainer approval (expected at PCC-001).
- `REGRESSION`: a previously-green oracle flips — stop and revert.
- `SAFETY_BLOCKED` / `BLOCKED`: a lock or forbidden side effect would occur.

## Closure

This line is locally closed when PCC-003 records a `PASS`, the contract is
consistent and gate-asserted, and the release_identity decision is recorded.

Closing this line creates the next one. The next open finding is W-3
(`audio_audit` crashes on a missing chunk and resolves STT only from the legacy
`ROOT/.tes` path).

Next line:
`docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-tes-tts-audio-audit-resolver.md`
(W-3). The remediation sequence continues — SRH (P-1) → OGR (W-1) → LIH (P-2) →
PCC (P-3) → audio-audit (W-3) → low-severity cleanup — each closed Super SPEC
names the next, until the 2026-06-02 audit findings converge.
