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

The initial order is:

1. `ftfy`
2. `ICU / CLDR`
3. `Babel`
4. `Lingua`
5. `CLD3`
6. `fastText lid.176`
7. `Argos Translate`
8. `eSpeak NG`
9. `phonemizer`
10. `gruut`
11. `Epitran`
12. `eSpeak NG he`
13. `Phonikud`
14. `NVIDIA NeMo text processing`

This order is a review queue, not a provider support claim. A later unit must
keep unavailable, unclear, heavyweight, or language-sensitive candidates in
`provider_needs_review` or degraded states until local evidence exists.
