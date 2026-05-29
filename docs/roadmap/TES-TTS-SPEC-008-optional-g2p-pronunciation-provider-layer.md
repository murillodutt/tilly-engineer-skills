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
