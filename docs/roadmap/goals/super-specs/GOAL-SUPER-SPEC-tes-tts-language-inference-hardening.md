---
tds_id: roadmap.goal_super_spec_tes_tts_language_inference_hardening
tds_class: roadmap
status: proposed
consumer: maintainers, tes-tts maintainers, adapter authors, validation authors, and execution agents
source_of_truth: false
evidence_level: L1
---

# GOAL Super SPEC: TES TTS Language Inference Hardening

Status: open product-quality line. Closes finding P-2 from the 2026-06-02
systematic audit — mixed pt/en chunk-language inference misclassifies plain
English prose as `pt`.

Canonical artifact:
`docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-tes-tts-language-inference-hardening.md`

Current execution unit:
`LIH-001`

Ready prompt:
`LIH-001 (analise → correção → certificação → local commit)`

Prior line:
`docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-tes-tts-oracle-gate-restoration.md`
(OGR / W-1, locally closed — oracle suite green and gated).

Audit source:
`TES-TTS-SYSTEMATIC-ANALYSIS-2026-06-02.md`, finding P-2.

## Why this line follows the gate-restoration line

The oracle suite is now green, single-sourced, de-masked, and gated. That means
this line finally has a trustworthy instrument: a behavior regression in
language inference will now surface instead of hiding behind version drift. So
this is the right moment to touch a runtime heuristic.

## Mantra Gate Snapshot

- `VERIFY`: `infer_long_read_chunk_language('This is a simple sentence that any
  reader can understand.', 'auto')` returns `pt`. The function
  (`scripts/tes_tts_omnivoice_runtime_support.py:581-662`) uses ~20 hardcoded
  marker words; English prose without technical markers falls through to
  `DEFAULT_LANGUAGE = 'pt'`.
- `SCOPE`: improve mixed pt/en chunk-language inference without changing any
  other runtime behavior; the `--language auto` path is opt-in.
- `BEST_PATH`: prove the misclassification with a behavior fixture/oracle first,
  then improve the heuristic as governed data, not example-specific patches.
- `DOCUMENT`: this Super SPEC and one ready `LIH-001` prompt are the authority.
- `ORACLE`: a behavior oracle over mixed/English/Portuguese cases must catch the
  misclassification before the fix and pass after.
- `RESOLVE`: delivered behavior — `runtime_support` is a bundled helper, so a
  `release_identity` version/bundle decision is required before closeout. No
  release, push, tag, publish, or sync in this line.
- `STATUS`: `PASS_TO_EXECUTE`.

## Purpose

Make mixed pt/en chunk-language inference choose the right language for a chunk
so the provider speaks English technical prose with English phonetics instead of
Portuguese ones. The default-to-`pt` fallback is a deliberate safety net and
stays; the goal is to stop classifying clearly-English chunks as `pt`.

## Certified Context

- Baseline: commit `cddf53e`, runtime VERSION `0.3.157`.
- `infer_long_read_chunk_language` is a delivered helper: shipped in
  `tes_bundle.py` `HELPER_FILES`, installed to `.tes/bin/**`. Changing its
  behavior is delivered behavior under `release_identity`.
- The `--language auto` path is opt-in: provider default is `--language pt`, and
  the function short-circuits when a concrete language is requested, so the blast
  radius is limited to auto-language long reads.
- The oracle suite (restored by the OGR line) is the safety net for this change.

## Protected Invariants (must survive)

- The `pt` default fallback stays for genuinely ambiguous chunks.
- A concrete `--language` request still short-circuits before the heuristic.
- No change to redaction, chunking boundaries, latency, or playback.
- The other 19 oracles stay green.

## Non-Objectives

- no full language-detection library or model dependency;
- no new runtime dependency (core stays dependency-free);
- no expansion beyond pt/en;
- no release, bump, push, tag, publish, or sync executed in this line.

## Execution Units

| Unit | Focus | Boundary |
|------|-------|----------|
| LIH-001 | Behavior fixture + oracle (the failing test) | Add language-inference fixtures (English-without-markers, mixed pt/en, pt) and an oracle asserting expected chunk language; observe FAIL on the English-prose case. No runtime change. |
| LIH-002 | Improve the heuristic as governed data | Strengthen inference (broader/structured markers or a cheap dependency-free signal) so clear English prose resolves to `en` while ambiguity still defaults to `pt`. Smallest change that turns LIH-001 green with invariants intact. |
| LIH-003 | Certify and propagate | Full oracle suite + governed gates green; refresh bundle; record the `release_identity` decision; local commit. |

## Required Loop

```text
analise -> correção -> certificação -> local commit -> create next line
```

The loop runs once per unit and stops at convergence — do not spawn a unit by
habit. Closing this line creates the next Super SPEC (see Closure).

## Certification

```bash
python3 scripts/tes_tts_oracles_suite.py
python3 scripts/materialize_adapter.py all --check
python3 scripts/validate_tds.py
python3 scripts/validate_doc_size.py
python3 scripts/validate_reference_graph.py
python3 scripts/tes_bump.py --governance-check
git diff --check
```

## Stop States

- `PASS`: LIH-001 failed first, LIH-002 made it pass, invariants intact, suite green.
- `DEGRADED`: inference improved but a target case still misclassifies — record which.
- `REGRESSION`: a previously-correct language choice flipped — stop and revert.
- `NEEDS_OWNER_DECISION`: the `release_identity` version/bundle decision, or scope
  beyond a dependency-free heuristic (a detection library/model), needs approval.
- `SAFETY_BLOCKED` / `BLOCKED`: a lock or forbidden side effect would occur.

## Closure

This line is locally closed when LIH-003 records a `PASS`, the suite is green,
and the `release_identity` decision is recorded.

Closing this line creates the next one. The next open finding is P-3
(`certifies_provider_support` live value contradicts the probe oracle and ADR).

Next line:
`docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-tes-tts-provider-certification-contract.md`
(P-3). The remediation sequence continues — SRH (P-1) → OGR (W-1) → LIH (P-2) →
provider-certification (P-3) → audio-audit (W-3) → low-severity cleanup — each
closed Super SPEC names the next, until the 2026-06-02 audit findings converge.
