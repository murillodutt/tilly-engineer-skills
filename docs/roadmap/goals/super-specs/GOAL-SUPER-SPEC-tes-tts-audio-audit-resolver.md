---
tds_id: roadmap.goal_super_spec_tes_tts_audio_audit_resolver
tds_class: roadmap
status: proposed
consumer: maintainers, tes-tts maintainers, adapter authors, validation authors, and execution agents
source_of_truth: false
evidence_level: L1
---

# GOAL Super SPEC: TES TTS Audio Audit Resolver

Status: open development-tool line. Closes finding W-3 from the 2026-06-02
systematic audit — the `audio_audit` maintainer tool crashes on a missing chunk
and resolves STT only from the legacy `ROOT/.tes` path.

Canonical artifact:
`docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-tes-tts-audio-audit-resolver.md`

Current execution unit:
`AAR-001`

Ready prompt:
`AAR-001 (analise → correção → certificação → local commit)`

Prior line:
`docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-tes-tts-provider-certification-contract.md`
(PCC / P-3, locally closed).

Audit source:
`TES-TTS-SYSTEMATIC-ANALYSIS-2026-06-02.md`, finding W-3.

## Mantra Gate Snapshot

- `VERIFY`: `audit_session` crashes with `FileNotFoundError` on a missing chunk
  audio file (`scripts/tes_tts_audio_audit.py` audited-chunks loop), and STT
  python/model default to the legacy `ROOT/.tes` path only
  (`:26-27,644-645`), so `--stt` reports STT_NOT_AVAILABLE on a machine where
  OmniVoice lives in the global `$HOME/.tes` runtime.
- `SCOPE`: harden the maintainer audit tool — graceful handling of a missing
  chunk, and STT resolution that also finds the global runtime + the real model
  cache. No change to delivered runtime behavior.
- `BEST_PATH`: add a behavior oracle that proves the missing-chunk path and the
  resolver path, then fix both, then certify.
- `DOCUMENT`: this Super SPEC and one ready `AAR-001` prompt are the authority.
- `ORACLE`: an oracle/self-test must cover the missing-chunk and resolver cases.
- `RESOLVE`: camada de trabalho — `audio_audit` is NOT bundled (not in
  `tes_bundle.py` HELPER_FILES), so no `release_identity` bump is triggered.
- `STATUS`: `PASS_TO_EXECUTE`.

## Purpose

Make the `audio_audit` maintainer tool robust: a missing chunk audio should be
reported as a flagged finding, not crash the run; and `--stt` should resolve the
interpreter and model from the same places the provider does (global
`$HOME/.tes` runtime via the `TES_TTS_OMNIVOICE_PYTHON`/global resolver, and the
real model location), not only the legacy `ROOT/.tes` path.

## Certified Context

- Baseline: commit `a3ffaf4`, runtime VERSION `0.3.157`.
- `audio_audit` is a maintainer diagnostic: not bundled, not installed to
  `.tes/bin/**`, not in `commit:check`, `--stt` is opt-in and non-fatal by
  default. Changing it is camada de trabalho, no bump.
- The provider already solved interpreter resolution
  (`tes_tts_omnivoice_provider.py` resolve order arg→env→global→sys.executable);
  reuse that pattern. The real Whisper model lives in the HF cache, not under the
  omnivoice runtime — the resolver must account for that.

## Protected Invariants

- `--stt` stays opt-in and non-fatal by default (`--require-stt` default False).
- A present, valid session still audits exactly as before.
- No delivered runtime behavior changes; the 20 oracles stay green.

## Non-Objectives

- no new STT model install/download;
- no making `audio_audit` a delivered/bundled helper;
- no release, bump, push, tag, publish, or sync.

## Execution Units

| Unit | Focus | Boundary |
|------|-------|----------|
| AAR-001 | Behavior test (the failing case) | Add a self-test/oracle that builds a session with a missing chunk audio and asserts a flagged finding (not a crash), and that documents the STT resolver expectation. Observe FAIL/crash on current code. |
| AAR-002 | Fix missing-chunk + STT resolver | Handle a missing chunk audio as a flagged finding; resolve STT python from arg→env(`TES_TTS_OMNIVOICE_PYTHON`)→global `$HOME/.tes`→legacy, and the model from the real cache. Smallest change that turns AAR-001 green with invariants intact. |
| AAR-003 | Certify + local commit | Self-test/oracle green; full suite green; local commit. |

## Required Loop

```text
analise -> correção -> certificação -> local commit -> create next line
```

The loop runs once per unit and stops at convergence. Closing this line creates
the next Super SPEC (see Closure).

## Certification

```bash
python3 scripts/tes_tts_audio_audit.py self-test
python3 scripts/tes_tts_oracles_suite.py
python3 scripts/validate_tds.py
python3 scripts/validate_doc_size.py
git diff --check
```

## Stop States

- `PASS`: missing-chunk handled gracefully, STT resolver finds the global
  runtime, self-test green, suite green.
- `DEGRADED`: resolver improved but a real environment still misses — record it.
- `REGRESSION`: a present-session audit changed behavior — stop and revert.
- `NEEDS_OWNER_DECISION`: scope beyond the maintainer tool (e.g. making it
  delivered) needs approval.
- `SAFETY_BLOCKED` / `BLOCKED`: a lock or forbidden side effect would occur.

## Closure

This line is locally closed when AAR-003 records a `PASS` and the suite is green.

Closing this line creates the next one. After W-3, the remaining audit findings
are the low-severity items (IPv4-vs-version, PATH-accent truncation, verbalizer
ordering, combine_wav silent drop, profile flag override, torch.load, dead
oracle code, AST guard, OWNER-DECISION doc bloat).

Next line:
`docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-tes-tts-low-severity-cleanup.md`
(P-LOW / W-LOW). The remediation sequence continues — SRH (P-1) → OGR (W-1) →
LIH (P-2) → PCC (P-3) → AAR (W-3) → low-severity cleanup — each closed Super
SPEC names the next, until the 2026-06-02 audit findings converge. The cleanup
line is the last; its closure marks convergence.
