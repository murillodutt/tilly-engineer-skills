---
tds_id: roadmap.tes_tts_spec_006_provider_candidate_selection
tds_class: roadmap
status: proposed
consumer: maintainers, tes-tts maintainers, provider reviewers, and release reviewers
source_of_truth: false
evidence_level: L2
---

# TES TTS SPEC 006: Provider Candidate Selection

## Purpose

Choose the first optional provider candidates for real local probes without
turning the review queue into a support claim.

## Scope

- Review candidates from `TES-TTS-PROVIDER-CANDIDATE-REVIEW.md`.
- Prefer low-risk helpers before translation or phoneme providers.
- Classify each candidate as selected, deferred, degraded, or rejected.
- Keep provider use optional.

## Initial Selection Bias

| Priority | Candidate class | Reason |
|----------|-----------------|--------|
| 1 | Unicode cleanup | Lowest risk and helpful before language detection. |
| 2 | Locale normalization | Useful for numbers/dates without translation claims. |
| 3 | Language detection | Needed before translation, but coverage-sensitive. |
| 4 | Translation | Deferred until fixtures prove protected-term safety. |
| 5 | G2P/pronunciation | Deferred until provider probe and language coverage exist. |

## Deliverables

- Updated provider candidate review with selected first probe targets.
- Explicit license, offline, maintenance, and language-coverage notes.
- Next SPEC prompt for the chosen provider layer.

## SPEC-006 Result

Status: `PASS`.

Selected optional local probe candidates:

1. `ftfy` for Unicode cleanup.
2. `Babel` for locale normalization.
3. `Lingua` for language detection after cleanup and locale normalization.

Deferred candidates: `ICU / CLDR`, `fastText lid.176`, `Argos Translate`,
`eSpeak NG`, `phonemizer`, and `Phonikud`.

Degraded candidates: `CLD3`, `gruut`, `Epitran`, and `eSpeak NG he`.

Rejected for current scope: `NVIDIA NeMo text processing`.

The structured review records license, offline, maintenance, and language
coverage notes for every candidate in
`benchmarks/tes-tts/provider-candidate-review.json`. This is still a probe
queue only: no provider was installed, downloaded, bundled, certified, or
claimed as supported.

Next ready prompt:
`docs/roadmap/GOAL-PROMPT-tes-tts-SPEC-007-optional-translation-layer.md`.

Sync status: `REMOTE_SYNC_NOT_REQUESTED`.

## Oracles

```bash
python3 scripts/tes_tts_provider_candidate_review_oracle.py --self-test
python3 scripts/tes_tts_provider_probe_oracle.py --self-test
python3 scripts/validate_reference_graph.py
```

## Exit Criteria

- At least one candidate is selected for optional local probing.
- Heavyweight or unclear candidates remain deferred or needs-review.
- No provider is installed, downloaded, bundled, or certified.
