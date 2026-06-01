---
tds_id: roadmap.tes_tts_spec_005_provider_probe_no_write
tds_class: roadmap
status: proposed
consumer: maintainers, tes-tts maintainers, provider reviewers, and validation authors
source_of_truth: false
evidence_level: L2
---

# TES TTS SPEC 005: Provider Probe No-Write

## Purpose

Detect optional local provider availability without installing, downloading,
writing global config, or certifying provider quality.

## Scope

- Probe only local, already-available tools or packages.
- Return local evidence with version, language signal, license note when
  available, and status.
- Keep all probes read-only and no-network.
- Preserve mocked fixtures for unavailable and needs-review states.

## Probe Result Shape

```text
provider_probe:
- provider: candidate name
  status: provider_available | provider_not_available | provider_needs_review
  version: local version when available
  languages: locally verified language codes
  license_note: local package/model license signal when known
  reason: short explanation
```

## Deliverables

- Hardened provider probe oracle.
- Fixture coverage for available, unavailable, needs-review, and degraded
  states.
- Negative check for installer, package manager, network, and write commands.

## SPEC-005 Result

Status: `PASS`.

The provider probe oracle now covers mocked `available`, `unavailable`,
`needs_review`, and `degraded` states. Each fixture explicitly forbids network,
install, download, write, and provider-support certification. Probe output is
limited to local evidence: provider, status, version, languages, license note,
and reason.

Next ready prompt:
`docs/roadmap/goals/prompts/tes-tts/GOAL-PROMPT-tes-tts-SPEC-006-provider-candidate-selection.md`.

Sync status: `REMOTE_SYNC_NOT_REQUESTED`.

## Oracles

```bash
python3 scripts/tes_tts_provider_probe_oracle.py --self-test
python3 scripts/tes_tts_fixture_schema_oracle.py --self-test
python3 scripts/validate_reference_package.py
```

## Exit Criteria

- Provider discovery can inform behavior without creating side effects.
- No provider support claim is made from probe existence alone.
- No install, download, release, sync, or persistent provider registry is
  introduced.
