---
tds_id: roadmap.tes_tts_spec_009_release_identity_sync_readiness
tds_class: roadmap
status: proposed
consumer: maintainers, tes-tts maintainers, release reviewers, and sync operators
source_of_truth: false
evidence_level: L2
---

# TES TTS SPEC 009: Release Identity And Sync Readiness

## Purpose

Prepare the release identity decision for `tes-tts` after technical scope is
accepted, without performing release or sync inside this SPEC.

## Scope

- Decide whether ADR 0004 moves from `proposed` to `accepted`.
- Decide version and bundle posture for adopter-visible `tes-tts` behavior.
- Decide whether sync remains forbidden or becomes a separate authorized
  release cycle.
- Preserve provider-backed claims as optional/deferred unless certified.

## Required Checks

| Surface | Check |
|---------|-------|
| ADR 0004 | Status and decision text match owner approval. |
| package identity | Version/bundle decision is explicit. |
| adapter source | Codex and Claude skill parity remains valid. |
| command triggers | `/tes-tts`, `/tes:tts`, and natural intents remain registered. |
| provider claims | No provider overclaim leaks into public docs. |
| sync posture | Sync remains forbidden unless explicitly authorized. |

## Deliverables

- Release identity decision record.
- Next `/goal` prompt for release or explicit deferral.
- No version bump unless the owner explicitly authorizes it.

## SPEC-009 Result

Status: `NEEDS_OWNER_DECISION`.

SPEC-009 confirms the current evidence is sufficient to recommend ADR 0004
acceptance for the bounded instruction-level and provider-boundary scope:
reactive read-aloud behavior, no-summary text preparation, protected-term
preservation, secret redaction, mocked no-write provider probing, optional
provider candidate review, adapter parity, and command trigger coverage.

ADR 0004 remains `proposed` because this cycle contains no explicit
maintainer approval to accept it. No ADR status, version, bundle, release,
tag, push, publish, sync, provider install, provider download, provider
certification, durable conversion cache, global config, or proactive `speak`
behavior changed.

Release identity planning cannot proceed to a bump, bundle, release, tag,
push, publish, or sync without a separate explicit owner decision. Read-only
review found the current package identity anchored at `0.3.147` across the
package, script constants, public bundle references, and release-check
surfaces. That identity is preserved.

Provider-backed claims remain optional, degraded, or deferred. The current
certified behavior is instruction-level normalization and mocked no-write
provider review only; no real provider runtime is certified.

Closure evidence:

- Focused TTS oracles, adapter materialization, command trigger oracle, TDS,
  doc-size, reference graph, and whitespace checks passed for this cycle.
- `python3 scripts/validate_reference_package.py` was run but is not
  interpretable as SPEC-009 package closure evidence because unrelated
  `.agents/**` drift fails development-skill parity outside the `tes-tts`
  scope. That drift remains unstaged and unmodified.
- `npm run commit:check` is therefore deferred as package closure evidence for
  this cycle; running it would include the same unrelated `.agents/**` drift.

Next ready prompt:
`docs/roadmap/GOAL-PROMPT-tes-tts-SPEC-010-final-audit-and-closure.md`.

Sync status: `REMOTE_SYNC_NOT_REQUESTED`.

## Oracles

```bash
python3 scripts/command_trigger_oracle.py --self-test
python3 scripts/materialize_adapter.py all --check
python3 scripts/validate_reference_package.py
npm run commit:check
```

## Exit Criteria

- Release identity is explicit: proceed, defer, or intentionally hold current
  version.
- Sync posture is explicit and separate from implementation certification.
- No push, tag, publish, marketplace action, or sync is performed without
  explicit authorization.
