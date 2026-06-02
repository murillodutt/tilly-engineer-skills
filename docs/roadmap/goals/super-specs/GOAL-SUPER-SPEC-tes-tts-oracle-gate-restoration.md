---
tds_id: roadmap.goal_super_spec_tes_tts_oracle_gate_restoration
tds_class: roadmap
status: proposed
consumer: maintainers, tes-tts maintainers, adapter authors, validation authors, and execution agents
source_of_truth: false
evidence_level: L1
---

# GOAL Super SPEC: TES TTS Oracle Gate Restoration

Status: open development-reliability line. Closes finding W-1 from the
2026-06-02 systematic audit — the runtime oracle suite is red, ungated, and the
version-gate masks behavior regressions.

Canonical artifact:
`docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-tes-tts-oracle-gate-restoration.md`

Current execution unit:
`OGR-001`

Ready prompt:
`OGR-001 (analise → correção → certificação → local commit)`

Prior line:
`docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-tes-tts-secret-redaction-hardening.md`
(SRH / P-1, locally closed at commit `af46c1c`).

Audit source:
`TES-TTS-SYSTEMATIC-ANALYSIS-2026-06-02.md`, finding W-1.

## Why this line follows the secret-redaction line

The P-1 fix landed, but the runtime oracle suite could not auto-confirm it: 11
of 18 oracles are red on `fixture version drifted`, and the version-gate
early-returns before running any behavior case, so a real regression is
indistinguishable from drift. Proving the P-1 fix did not regress anything
required bypassing the gate by hand. Until the gate is restored, every future
remediation line carries that same blind spot. This line removes it.

## Mantra Gate Snapshot

- `VERIFY`: 11 fixtures are pinned at `0.3.150` while runtime VERSION is
  `0.3.157`; `VERSION` is hardcoded in 17 oracles; `validate_fixtures`
  early-returns at the version check before the case loop (e.g.
  `tes_tts_runtime_ir_oracle.py:42`); no `tes_tts` runtime oracle except
  `roadmap_partition` is in `commit:check`.
- `SCOPE`: re-pin fixtures, single-source the version, de-mask the gate, and
  gate the oracles. Do not change runtime behavior.
- `BEST_PATH`: separate "fixture version" from "behavior" so a real regression
  cannot hide behind drift; then wire the suite into the closure gate.
- `DOCUMENT`: this Super SPEC and one ready `OGR-001` prompt are the authority.
- `ORACLE`: the suite itself is the oracle — all 18 `tes_tts_*_oracle.py` must
  pass `--self-test`, and the new gate must run them.
- `RESOLVE`: camada de trabalho — no delivered runtime behavior changes, no
  bump required. Touch oracles, fixtures, and `package.json` scripts only.
- `STATUS`: `PASS_TO_EXECUTE`.

## Purpose

Make the runtime oracle suite green, single-sourced, non-masking, and gated, so
it actually protects `tes-tts` runtime behavior. A bump should not silently turn
the regression suite red, and a real behavior regression must never be
swallowed by the version check.

## Certified Context

- Baseline: runtime VERSION `0.3.157` (`scripts/tes_tts_runtime_types.py:22`),
  the single-source candidate.
- 11 drifted fixtures (`0.3.150`): chunked-preparation, fast-path-spoken-rendering,
  compiled-lexical-index, hot-path-span-matcher, live-session-utterance,
  pronunciation-catalog, ptbr-lexical-integration, ptbr-lexical-lookup,
  runtime-ir, runtime-latency, request-local-memoization.
- The oracles are camada de trabalho (maintainer gates): not in `tes_bundle.py`
  `HELPER_FILES`, not installed to `.tes/bin/**`, not adopter-visible. No
  `release_identity` bump is triggered by changing them.
- The P-1 line already proved the masking behavior empirically: bypassing the
  version-gate showed the 3 touched oracles pass with 0 behavior failures.

## Protected Invariants (must survive)

- No `tes_tts` runtime helper behavior changes in this line — oracles and
  fixtures only.
- The `secret_redaction` oracle (created by the P-1 line) keeps passing.
- Fixtures keep their behavioral assertions; only the version field and the
  gate logic move.
- The version-gate still catches genuine fixture/version mismatch — it just
  must not skip the behavior cases when it fires.

## Non-Objectives

- no runtime classifier/verbalizer/adapter/provider behavior change;
- no release, bump, bundle, push, tag, publish, or sync;
- no new lexical data or pronunciation behavior;
- no rewrite of what each oracle asserts — only version sourcing and gate flow.

## Execution Units

| Unit | Focus | Boundary |
|------|-------|----------|
| OGR-001 | Single-source VERSION + de-mask the gate | Oracles import `VERSION` from `tes_tts_runtime_types` instead of hardcoding it; `validate_fixtures` reports version drift as a failure but still runs behavior cases (no early-return that hides regressions). The suite must distinguish "version drifted" from "behavior failed". |
| OGR-002 | Re-pin the 11 fixtures to `0.3.157` | Bump only the `version` field of the 11 drifted fixtures; behavioral content unchanged. All 18 oracles `--self-test` go green. |
| OGR-003 | Gate the suite + certify + local commit | Add a `tes-tts:oracles` target to `package.json` running all 18 oracles, and include it in `commit:check`. Full closure gate green. Local commit. |

## Required Loop

```text
analise -> correção -> certificação -> local commit -> create next line
```

Per unit: observe the gap, make the smallest fix, certify with the suite, commit
locally. The loop runs once per unit and stops at convergence — do not spawn a
new unit by habit. Closing this line creates the next Super SPEC (see Closure),
keeping the remediation sequence alive until the audit converges.

## Certification

```bash
python3 scripts/tes_tts_secret_redaction_oracle.py --self-test
python3 scripts/tes_tts_runtime_ir_oracle.py --self-test
python3 scripts/tes_tts_runtime_latency_oracle.py --self-test
python3 scripts/tes_tts_hot_path_span_matcher_oracle.py --self-test
python3 scripts/tes_tts_compiled_lexical_index_oracle.py --self-test
python3 scripts/tes_tts_fast_path_spoken_rendering_oracle.py --self-test
python3 scripts/tes_tts_request_local_memoization_oracle.py --self-test
python3 scripts/tes_tts_chunked_preparation_oracle.py --self-test
python3 scripts/tes_tts_live_session_utterance_oracle.py --self-test
python3 scripts/tes_tts_pronunciation_catalog_oracle.py --self-test
python3 scripts/tes_tts_ptbr_lexical_integration_oracle.py --self-test
python3 scripts/tes_tts_ptbr_lexical_lookup_oracle.py --self-test
python3 scripts/tes_tts_ptbr_lexical_manifest_oracle.py --self-test
python3 scripts/tes_tts_fixture_schema_oracle.py --self-test
python3 scripts/tes_tts_instruction_normalizer_oracle.py --self-test
python3 scripts/tes_tts_provider_probe_oracle.py --self-test
python3 scripts/tes_tts_provider_candidate_review_oracle.py --self-test
python3 scripts/tes_tts_roadmap_partition_oracle.py
python3 scripts/validate_tds.py
python3 scripts/validate_doc_size.py
git diff --check
```

## Stop States

- `PASS`: all 18 oracles green, version single-sourced, gate de-masked, suite
  wired into `commit:check`, no runtime behavior changed.
- `DEGRADED`: a fixture cannot be re-pinned without a behavioral edit — record
  which and stop before changing behavior.
- `REGRESSION`: de-masking the gate reveals a real behavior failure that the
  drift was hiding — stop, isolate it, and treat it as its own finding.
- `NEEDS_OWNER_DECISION`: single-sourcing or gating requires a delivered-surface
  change beyond oracles/fixtures/`package.json` scripts.
- `SAFETY_BLOCKED` / `BLOCKED`: a lock or forbidden side effect would occur.

## Closure

This line is locally closed when OGR-003 records a `PASS`, all 18 oracles are
green, and the suite runs in `commit:check`.

Closing this line creates the next one. The next open product-surface finding is
P-2 (mixed pt/en language inference misclassifies English prose as `pt`).

Next line:
`docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-tes-tts-language-inference-hardening.md`
(P-2). The remediation sequence continues — SRH (P-1) → OGR (W-1) → language
(P-2) → provider-certification contract (P-3) → audio-audit resolver (W-3) →
low-severity cleanup — each closed Super SPEC names the next, until the
2026-06-02 audit findings converge. Convergence is when every P- and W- finding
in `TES-TTS-SYSTEMATIC-ANALYSIS-2026-06-02.md` is closed or explicitly deferred
by an owner decision.
