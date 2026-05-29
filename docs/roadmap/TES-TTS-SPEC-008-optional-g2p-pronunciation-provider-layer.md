---
tds_id: roadmap.tes_tts_spec_008_optional_g2p_pronunciation_provider_layer
tds_class: roadmap
status: proposed
consumer: maintainers, tes-tts maintainers, provider reviewers, and validation authors
source_of_truth: false
evidence_level: L2
---

# TES TTS SPEC 008: Optional G2P Pronunciation Provider Layer

## Purpose

Define how optional G2P, IPA, phonemizer, or Hebrew enrichment providers may
improve speech rendering after provider probes and fixtures exist.

## Scope

- Provider-backed pronunciation is optional.
- Instruction-level hints remain the baseline.
- SSML, lexicon, IPA, and phoneme output are not certified until fixtures prove
  provider behavior.
- Hebrew remains explicitly degraded until niqqud, G2P, or voice support is
  locally verified.

## Candidate Classes

| Class | Examples | Posture |
|-------|----------|---------|
| G2P/phonemizer | eSpeak NG, phonemizer, gruut, Epitran | Probe first, certify per language. |
| Hebrew enrichment | eSpeak NG `he`, Phonikud | Needs-review until quality evidence exists. |
| Advanced TTS normalization | NVIDIA NeMo text processing | Deferred unless simpler layers fail. |

## Deliverables

- Provider probe fixtures for selected G2P/pronunciation candidates.
- Golden pronunciation fixtures for protected technical terms.
- Degraded-state fixtures for unsupported languages, especially Hebrew.

## SPEC-008 Boundary

Instruction-level pronunciation hints remain the baseline. Optional G2P,
phonemizer, Hebrew enrichment, lexicon, IPA, SSML, or provider-backed
pronunciation output can only move beyond `normalization_degraded` after a
later local probe proves provider availability, language support, license
posture, and fixture quality.

Provider-backed pronunciation is not certified by this SPEC. The allowed plan
for now emits only `instruction_level_hints` and blocks `ipa`, `ssml`,
`phoneme`, `lexicon`, and `provider_backed_pronunciation` outputs.

Hebrew acceptance threshold: Hebrew remains `normalization_degraded` until
local evidence proves all of these:

1. provider availability without install, download, bundle, or global write;
2. Hebrew language support for the exact runtime path;
3. quality evidence for unpointed Hebrew and protected technical terms;
4. license review for code, models, lexicons, and datasets.

## SPEC-008 Result

Status: `PASS`.

Instruction-level pronunciation boundary fixtures:

1. `tts-pronunciation-provider-boundary`
2. `tts-pronunciation-hebrew-degraded`
3. `tts-pronunciation-provider-unclear-degraded`

Provider probe fixtures added:

1. `tts-provider-g2p-degraded`
2. `tts-provider-hebrew-pronunciation-needs-review`

The normalizer oracle now produces an optional pronunciation plan that keeps
instruction-level hints as the only emitted output unless future evidence
proves provider-backed behavior. Hebrew remains explicitly degraded.

No provider was installed, downloaded, bundled, certified, or claimed as
supported.

Next ready prompt:
`docs/roadmap/GOAL-PROMPT-tes-tts-SPEC-009-release-identity-sync-readiness.md`.

Sync status: `REMOTE_SYNC_NOT_REQUESTED`.

## Oracles

```bash
python3 scripts/tes_tts_provider_probe_oracle.py --self-test
python3 scripts/tes_tts_instruction_normalizer_oracle.py --self-test
python3 scripts/tes_tts_fixture_schema_oracle.py --self-test
```

## Exit Criteria

- Provider-backed pronunciation is either certified per language or explicitly
  degraded.
- Hebrew acceptance threshold is recorded before any Hebrew quality claim.
- No provider is auto-installed, auto-downloaded, bundled, or globally enabled.
