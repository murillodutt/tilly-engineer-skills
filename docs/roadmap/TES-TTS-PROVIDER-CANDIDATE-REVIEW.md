---
tds_id: roadmap.tes_tts_provider_candidate_review
tds_class: roadmap
status: proposed
consumer: maintainers, tes-tts maintainers, provider reviewers, and release reviewers
source_of_truth: false
evidence_level: L2
---

# TES TTS Provider Candidate Review

This review ranks optional normalization and pronunciation provider candidates
after the no-write provider probe contract exists. It does not probe real
providers, install dependencies, fetch model artifacts, write global config,
certify provider behavior, or authorize sync/release.

Structured review:
[`benchmarks/tes-tts/provider-candidate-review.json`](../../benchmarks/tes-tts/provider-candidate-review.json)

Focused oracle:
`python3 scripts/tes_tts_provider_candidate_review_oracle.py --self-test`

## Ranking Policy

The review prefers candidates that can improve instruction-level normalization
with low local risk before heavier language models or quality-sensitive
translation. Every candidate remains optional and must pass the no-write probe
contract before use.

| Priority | Candidate class | Rationale |
|----------|-----------------|-----------|
| 1 | Unicode and locale helpers | Smaller helper surface before language-quality claims. |
| 2 | Language detection | Needed before translation, but requires coverage checks. |
| 3 | Translation | Useful only after fixtures prove meaning and protected terms. |
| 4 | Pronunciation / G2P / IPA | Powerful but language and backend support vary. |
| 5 | Hebrew enrichment | Quality-sensitive and explicitly degraded until proven. |
| 6 | Advanced TTS normalization | Deferred until simpler layers are understood. |

## Review Result

SPEC-006 selects only optional local probe candidates. It does not install,
download, bundle, certify, or claim support for any provider.

| Rank | Candidate | Decision | Notes |
|------|-----------|----------|-------|
| 1 | `ftfy` | selected | First Unicode cleanup probe; Apache-2.0; local-only if already available. |
| 2 | `Babel` | selected | First locale helper probe; Babel license plus Unicode CLDR data license. |
| 3 | `ICU / CLDR` | deferred | Standards reference; direct binding policy is broader than this unit. |
| 4 | `Lingua` | selected | First language-detection probe after cleanup and locale helpers; Apache-2.0. |
| 5 | `CLD3` | degraded | Binding and packaging posture need local evidence. |
| 6 | `fastText lid.176` | deferred | Model artifact policy is unresolved. |
| 7 | `Argos Translate` | deferred | Translation needs SPEC-007 safeguards and local model evidence. |
| 8 | `eSpeak NG` | deferred | Pronunciation boundary belongs to SPEC-008; GPL posture needs review. |
| 9 | `phonemizer` | deferred | Backend dependency and GPL posture follow the eSpeak boundary. |
| 10 | `gruut` | degraded | Partial first-class language coverage and per-language data review needed. |
| 11 | `Epitran` | degraded | Language-script coverage must be proven with fixtures. |
| 12 | `eSpeak NG he` | degraded | Hebrew remains explicitly degraded until pronunciation quality is proven. |
| 13 | `Phonikud` | deferred | Hebrew dataset and model artifact policy require owner review. |
| 14 | `NVIDIA NeMo text processing` | rejected | Too heavyweight and platform-sensitive for current `tes-tts` scope. |

The selected set is a local probe queue only:

1. Unicode cleanup: `ftfy`.
2. Locale normalization: `Babel`.
3. Language detection: `Lingua`.

Every selected candidate still returns only local evidence. A present package
does not certify provider support, translation quality, pronunciation quality,
or language coverage.
