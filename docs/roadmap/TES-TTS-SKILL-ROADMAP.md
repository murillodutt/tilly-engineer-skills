---
tds_id: roadmap.tes_tts_skill_roadmap
tds_class: roadmap
status: active
consumer: maintainers, tes-tts maintainers, adapter authors, and release reviewers
source_of_truth: false
evidence_level: L2
---

# TES TTS Skill Roadmap

This is the active dashboard for `tes-tts`: short, current, and
decision-oriented. Dense pointers live in `TES-TTS-SKILL-ROADMAP-REGISTRY.md`;
closed lineage lives in `TES-TTS-SKILL-ROADMAP-HISTORY.md`. ADR 0004 remains
the architectural boundary.

Partition contract: dashboard for state/decisions/evidence/next cut, registry
for dense pointers, history for closed lineage, and `validate_doc_size.py` for
budgets plus early warnings.

## State

`tes-tts` is reactive delivered behavior only when explicitly requested. PT-BR
is the primary quality target. The durable path is runtime-first speech
preparation plus optional OmniVoice premium local synthesis; `say` with
`Felipe (Enhanced)` at rate `255` remains the offline fallback.

Active surfaces are the local `.agents` workbench, Codex/Claude skill sources,
runtime scripts and oracles, governed TTS benchmarks, optional OmniVoice facade,
and ADR 0004. Dense pointers stay in `TES-TTS-SKILL-ROADMAP-REGISTRY.md`.

Unauthorized until separate owner decision: release identity, sync, push, tag,
publish, provider redistribution, global config writes, durable conversion
cache, and proactive `speak`.

## Decisions

- Source text is immutable; speech uses request-local prepared text.
- Secrets are redacted before rendering and provider handoff.
- PT-BR is platform narration; English/technical identity is preserved.
- OmniVoice is optional local capability, not bundled dependency.
- Version, release, sync, push, tag, and publish need separate approval.

## Evidence

- Recent commits: `eb44ce7` optional OmniVoice provider; `62fbc4b` product
  shortcut.
- Maintainer live rating: OmniVoice cloned voice result `9.5`.
- Optional provider probe: `provider_available`.
- `status` auto-discovers env/reference; `warm-cache` prepares voice prompt
  cache; `speak` delegates synthesis without long CLI arguments.
- `bench --play --open --package` writes WAVs, metrics, review HTML, ZIP
  manifest; `decide-review --review-json <json> --package` seals the decision.
- `product-status --format text --strict` gates `AUDIO_CANDIDATE`; latest run:
  `32.69s` audio, `30.19s` total, RTF `0.9422`, SHA starts `0206b249`.
- `candidate --format text --strict` replays/opens sealed audio without
  regenerating it.

Relevant gates: focused TTS provider/runtime/oracle suite, materialization,
TDS/doc-size/reference validators, and `npm run commit:check` for package
closure.

## Next Cut

Run `warm-cache`, then `bench --play --open --package`; score fixtures, seal
with `decide-review --review-json <json> --package`, gate with
`product-status --format text --strict`, and inspect with `candidate --format
text --strict`. The result decides release identity planning or one targeted
provider/runtime fix.

## Maintenance Rules

- Hard limit: 120 lines. Warning zone starts at 90 lines.
- Keep only current state, active decisions, next decisions, and latest
  evidence here.
- Move dense artifact listings to `TES-TTS-SKILL-ROADMAP-REGISTRY.md`.
- Move historical cycle detail to `TES-TTS-SKILL-ROADMAP-HISTORY.md`.
- Keep the root roadmap index grouped by product line, not by every prompt,
  SPEC, or audit artifact.
- Every `tes-tts` execution cycle must update this dashboard or record an
  explicit no-change rationale in the active audit/commit message.
- Do not use this roadmap to authorize sync, release, provider installs,
  provider downloads, or global config writes.

## Closure Rule

For material `tes-tts` changes, close after the smallest relevant TTS oracles
plus needed package gates. Use `npm run commit:check` before package closure.
Do not claim release closure without a release identity decision.
