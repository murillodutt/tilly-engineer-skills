---
tds_id: roadmap.tes_tts_skill_roadmap
tds_class: roadmap
status: active
consumer: maintainers, tes-tts maintainers, adapter authors, and release reviewers
source_of_truth: false
evidence_level: L2
---

# TES TTS Skill Roadmap

This roadmap organizes the executive evolution of `tes-tts` from a small
reactive read-aloud skill into a governed TES capability. It records what is
already decided, where each decision lives, and the next sequential work units
needed before acceptance, release identity, or sync can be considered.

This document does not replace ADR 0004 or the normalization SPECs. ADR 0004
is the architectural boundary. The SPECs own architecture and execution
details. This roadmap owns sequencing, registry, and operating visibility.

## Current Position

`tes-tts` is accepted delivered behavior staged in TES source. It is reactive:
it reads or narrates user-provided text only when explicitly requested. It must
not become the proactive `speak` channel, a dependency manager, a bundled
translation stack, or a global voice registry.

The current package state is intentionally pre-release:

- no sync has been authorized;
- no release identity has been closed;
- no provider dependency has been installed, bundled, or certified;
- normalization is instruction-level plus accepted architecture;
- local validators have passed during construction, but final package closure
  still requires the normal release gates and maintainer approval.

## Development Target

The active development and test workbench for the next `tes-tts` capability
migration units is:

`/Users/murillo/Dev/tilly-engineer-skills/.agents/skills/tes-tts`

The canonical Codex adapter target remains:

`/Users/murillo/Dev/tilly-engineer-skills/src/adapters/codex/skills/tes-tts`

The execution rule is develop and test first in `.agents/skills/tes-tts`, then
sync the converged content into `src/adapters/codex/skills/tes-tts` after the
unit passes focused validation. The `.agents` directory is the active workbench
for this skill evolution; the adapter source remains the canonical package
surface for release, materialization, and sync decisions.

## Artifact Registry

| Surface | Role | Status |
|---------|------|--------|
| `.agents/skills/tes-tts/**` | Active local development and test workbench for `tes-tts`. | workbench |
| `src/adapters/codex/skills/tes-tts/SKILL.md` | Codex source skill contract. | staged |
| `src/adapters/claude/skills/tes-tts/SKILL.md` | Claude source skill contract. | staged |
| `src/adapters/*/skills/tes-tts/agents/openai.yaml` | Agent-facing invocation guidance. | staged |
| `src/adapters/*/skills/tes-tts/docs/CONTRACT-HISTORY.md` | Local history, origin signals, preserved contracts, and failure modes. | staged |
| `src/adapters/*/skills/tes-tts/references/language-normalization.md` | Instruction-level default-language, conversion-cache, and pronunciation reference. | staged |
| `src/adapters/*/skills/tes-tts/references/providers-and-fallbacks.md` | Portable provider fallback lessons from `speak`. | staged |
| `docs/adr/0004-tes-tts-pronunciation-normalization-and-enrichment.md` | Architectural GPS and boundary. | active |
| `docs/roadmap/TES-TTS-NORMALIZATION-ARCHITECTURE-SPEC.md` | Optional normalization architecture. | proposed |
| `docs/roadmap/TES-TTS-NORMALIZATION-EXECUTION-SPEC.md` | Sequential execution contract and acceptance gates. | proposed |
| `docs/roadmap/TES-TTS-NORMALIZATION-FIXTURE-SCHEMA.md` | Fixture schema explanation and TTS-004 boundary. | proposed |
| `docs/roadmap/TES-TTS-PROVIDER-CANDIDATE-REVIEW.md` | Ranked provider review queue, not certification. | proposed |
| `docs/roadmap/TES-TTS-SPEC-001-*.md` through `TES-TTS-SPEC-010-*.md` | Ten-step convergence SPEC draft set from roadmap compaction through final audit. | proposed |
| `docs/roadmap/GOAL-SUPER-SPEC-tes-tts-owner-decision-gate.md` | Post-convergence owner decision gate. | archived |
| `docs/roadmap/GOAL-PROMPT-tes-tts-OWNER-001-acceptance-release-sync-decision.md` | OWNER-001 acceptance/release/sync decision prompt. | archived |
| `docs/roadmap/TES-TTS-OWNER-001-ACCEPTANCE-DECISION.md` | ADR 0004 acceptance decision record. | active |
| `docs/roadmap/GOAL-SUPER-SPEC-tes-tts-capability-migration.md` | Post-ADR capability migration execution contract. | active |
| `docs/roadmap/TES-TTS-CAP-001-PORTABLE-CAPABILITY-FEASIBILITY.md` | Feasibility study for migrating portable TTS behavior. | active |
| `docs/roadmap/GOAL-PROMPT-tes-tts-CAP-001-portable-capability-migration.md` | Historical prompt for first portable capability migration cut. | historical |
| `docs/roadmap/GOAL-PROMPT-tes-tts-CAP-002-speech-transformation-hardening.md` | Historical prompt for speech transformation hardening. | historical |
| `docs/roadmap/GOAL-PROMPT-tes-tts-CAP-003-pronunciation-hints-protected-terms.md` | Historical prompt for pronunciation hints and protected terms. | historical |
| `docs/roadmap/GOAL-PROMPT-tes-tts-CAP-004-provider-fallback-catalog-use.md` | Historical prompt for provider fallback catalog use. | historical |
| `docs/roadmap/GOAL-PROMPT-tes-tts-CAP-005-adapter-parity-final-local-audit.md` | Ready prompt for adapter parity and final local audit. | active |
| `docs/roadmap/TES-TTS-ACCEPTANCE-AND-RELEASE-DECISION.md` | TTS-009 acceptance and release decision record. | active |
| `docs/roadmap/TES-TTS-OWNER-*.md` | Historical owner-decision records TTS-010 through TTS-031; retained in TDS and `docs/INDEX.md`. | historical |
| `benchmarks/tes-tts/normalization-fixture.schema.json` | Machine-readable fixture schema. | proposed |
| `benchmarks/tes-tts/normalization-fixtures.json` | Minimal dependency-free fixture corpus. | proposed |
| `benchmarks/tes-tts/instruction-normalizer-fixtures.json` | Instruction-level normalizer oracle fixtures. | proposed |
| `benchmarks/tes-tts/provider-probe-fixtures.json` | Mocked provider probe contract fixtures. | proposed |
| `benchmarks/tes-tts/provider-fallback-fixtures.json` | Mocked request-local provider fallback fixtures. | proposed |
| `benchmarks/tes-tts/provider-candidate-review.json` | Structured provider candidate review queue. | proposed |
| `docs/roadmap/TES-TTS-SKILL-ROADMAP.md` | Executive registry and evolution roadmap. | active |
| `docs/roadmap/GOAL-SUPER-SPEC-tes-tts-sequential-convergence.md` | Circular execution contract for the skill. | active |
| `docs/roadmap/GOAL-PROMPT-tes-tts-TTS-000*.md` through `TTS-009*.md` | Historical prompt artifacts for baseline through acceptance decision. Indexed individually in TDS. | active |
| `docs/roadmap/GOAL-PROMPT-tes-tts-TTS-010*.md` through `TTS-019*.md` | Historical prompt artifacts for owner-decision preservation cycles. Indexed individually in TDS. | active |
| `docs/roadmap/GOAL-PROMPT-tes-tts-TTS-020*.md` through `TTS-031*.md` | Historical prompt artifacts for unresolved owner-decision cycles. Indexed individually in TDS. | historical |
| `docs/roadmap/GOAL-PROMPT-tes-tts-TTS-032-owner-decision-still-open-yet-again.md` | Ready prompt artifact that must be superseded before reuse because the owner-decision loop no longer advances implementation. | needs-rewrite |
| `scripts/materialize_adapter.py` | Adapter materialization inclusion. | staged |
| `scripts/command_trigger_oracle.py` | Slash, alias, and natural trigger oracle inclusion. | staged |
| `scripts/validate_reference_package.py` | Package reference validation inclusion. | staged |
| `scripts/tes_tts_fixture_schema_oracle.py` | Dependency-free fixture schema oracle. | staged |
| `scripts/tes_tts_instruction_normalizer_oracle.py` | Dependency-free instruction normalizer oracle. | staged |
| `scripts/tes_tts_provider_probe_oracle.py` | Mocked no-write provider probe oracle. | staged |
| `scripts/tes_tts_provider_candidate_review_oracle.py` | Provider review queue oracle. | staged |
| `docs/install/COMMAND-TRIGGERS.md` | User-visible command trigger registration. | staged |
| `docs/adapters/CODEX.md`, `docs/adapters/CLAUDE.md`, `docs/adapters/PLATFORM-DIFFERENCES.md` | Adapter-facing discoverability and parity notes. | staged |

## Evolution Ledger

| Stage | Decision | Evidence |
|-------|----------|----------|
| 0 | Promote the working local TTS behavior into TES as a simple reactive skill. | `CONTRACT-HISTORY.md`; `SKILL.md` sources. |
| 1 | Keep `tes-tts` separate from proactive `speak`. | Provider/fallback reference and ADR 0004 non-goals. |
| 2 | Absorb only portable `speak` references: provider order, fallback, error classes, voice policy, speech transformation. | `providers-and-fallbacks.md`. |
| 3 | Add multilingual normalization and pronunciation enrichment as optional speech preparation. | `language-normalization.md`; ADR 0004. |
| 4 | Keep ADR 0004 as GPS/boundary, not pipeline detail. | ADR 0004 plus architecture/execution SPEC split. |
| 5 | Treat provider libraries as optional candidates only. | ADR 0004 and architecture SPEC. |
| 6 | Add first-class language scope: `pt-BR`, `en`, `es`, `fr`, `it`, `de`, `he`. | Architecture SPEC. |
| 7 | Introduce adapter default language as an explicit preference that never overrides user-requested language, with Cursor falling back to Codex default first and Claude default second when Cursor has no declaration. | Language reference, execution SPEC, and selector fixture `tts-dls-006`. |
| 8 | Require sequential convergence: one unit, one decision, one oracle, one next step. | Execution SPEC. |
| 9 | Require every non-converged execution cycle to create the next `/goal` prompt as a tracked artifact. | GOAL Super SPEC and tracked prompt artifacts. |
| 10 | Require every `tes-tts` execution cycle to update this roadmap before closure. | This roadmap, GOAL Super SPEC, and ready prompt artifacts. |
| 11 | Accept ADR 0004 as the active pronunciation normalization and enrichment boundary. | `TES-TTS-OWNER-001-ACCEPTANCE-DECISION.md`. |
| 12 | Start capability migration as a new bounded sequence, using mapped simple TTS and `speak` learning as references rather than wholesale copies. | `GOAL-SUPER-SPEC-tes-tts-capability-migration.md`. |
| 13 | Use `.agents/skills/tes-tts` as the active development and test workbench, then mirror converged content into the canonical Codex adapter source. | This roadmap and `GOAL-SUPER-SPEC-tes-tts-capability-migration.md`. |

## Circular Execution Control

The executable sequence is:

```text
execute -> analyze -> fix -> certify -> create next /goal prompt -> local commit
```

The current circular execution contract is:
`docs/roadmap/GOAL-SUPER-SPEC-tes-tts-sequential-convergence.md`

The current ten-SPEC convergence contract is:
`docs/roadmap/GOAL-SUPER-SPEC-tes-tts-ten-spec-convergence.md`

The current ready prompt artifact is:
`docs/roadmap/GOAL-PROMPT-tes-tts-CAP-005-adapter-parity-final-local-audit.md`

Each non-converged cycle must create and index the next prompt artifact before
its local commit. This prevents the execution loop from breaking because the
next `/goal` prompt exists only in chat or only embedded inside the Super SPEC.

Every `tes-tts` execution cycle must update this roadmap before closure, even
when no ADR, source, provider, release, or sync decision changes. The roadmap
update must record at least the current unit status, the ready prompt pointer,
and any newly created decision or evidence artifact. If the cycle produces no
material roadmap change, it must add a short no-change rationale to the current
unit entry instead of silently skipping the roadmap.

## Sequential Roadmap

### R0: Baseline Skill Registration

Status: materially implemented, pending final release identity.

Required closure:

- Codex and Claude skill folders validate with `quick_validate.py`.
- Materialization check passes for Codex and Claude.
- Command trigger oracle covers `/tes-tts`, `/tes:tts`, and natural intents.
- Reference package validation includes the new skill files.

Exit state: `tes-tts` is installable from source adapters, but not yet released
or synced.

### R1: Executive Registry

Status: current work unit.

Required closure:

- This roadmap exists and is indexed.
- TDS document index includes the roadmap.
- ADR/SPEC/skill surfaces have a clear ownership relationship.
- The circular Super SPEC and ready prompt artifact are mapped from this
  roadmap.
- The next unresolved decision is named before continuing.

Exit state: maintainers can see the full skill evolution from one roadmap
without confusing roadmap detail with ADR boundary.

### R2: Default-Language Selector Contract

Status: selector fallback contract fixture-ready, with executable DLS fixtures.

Decision: adapter default language is a default preference, not a hard
priority. Explicit user language overrides adapter default language. A user
request such as "read this in English" must win even if the adapter declares
`pt-BR`.

Required closure:

- Update language references with the precedence rule.
- Update architecture or execution SPEC if needed.
- Record selector fixture candidates before executable fixture work.
- Preserve the concrete source order: explicit user language, active adapter
  declaration, Cursor fallback to Codex default, Cursor fallback to Claude
  default, request language, dominant text language, preserve original.

Exit state: the selector contract is unambiguous and testable.

### R3: Fixture Schema

Status: schema contract defined, pending corpus use.

Required closure:

- Select the fixture file shape before creating the corpus.
- Include selector inputs and expected target language.
- Include source span, protected terms, redaction expectation, provider state,
  expected status, and no-summary expectation.
- Keep schema dependency-free and suitable for deterministic validation.

Exit state: future corpus entries have one governed shape and can be linted.

### R4: Fixture Corpus

Status: minimal selector corpus created, pending broader fixture classes.

Required fixture classes:

- single-language samples for each first-class language;
- mixed-language text with one foreign span;
- protected technical terms across language boundaries;
- Hebrew text without niqqud;
- Markdown with links, paths, code fences, and long hashes;
- secret-like multilingual text;
- explicit voice/provider request;
- provider unavailable and voice unavailable cases.

Exit state: fixture names and expected outcomes exist before any provider
probing or implementation claims.

### R5: Instruction-Level Normalizer Oracle

Status: instruction-level oracle added, pending provider probe contract.

Goal: prove the current instruction-only behavior before introducing optional
libraries.

Required closure:

- The conversion cache shape is produced without disk writes.
- Protected terms survive translation planning.
- Secret-like values are redacted before any provider or TTS step.
- Long text is chunked without summarizing unless requested.

Exit state: `normalization_degraded` remains useful and honest when no
provider exists.

### R6: Provider Probe Contract

Status: mocked no-write contract added, pending provider candidate review.

Goal: detect optional local providers without installation, downloads, network
model fetches, or persistent config writes.

Required closure:

- Probe output matches the execution SPEC.
- Mocked provider tests cover available, unavailable, and needs-review states.
- License and language-coverage notes are recorded as local signals only.

Exit state: provider discovery is safe enough to inform, but not certify,
runtime choices.

### R7: Provider Candidate Review

Status: provider candidate selection complete, pending optional translation
boundary.

Candidate layers:

- language detection;
- translation;
- locale normalization;
- TTS text normalization;
- pronunciation, G2P, IPA, or Hebrew enrichment;
- Unicode cleanup.

Exit state: every provider candidate is classified as selected, deferred,
degraded, or rejected. `ftfy`, `Babel`, and `Lingua` are selected as optional
local probe candidates only; no provider support is certified.

### R8: Adapter Parity And Install Surface

Status: optional pronunciation provider boundary complete, pending release
identity readiness and final parity recheck.

Required closure:

- Codex and Claude skill content remains behaviorally aligned.
- Cursor documentation advertises capability only where the adapter can
  reasonably trigger it.
- Install/manual/command-trigger docs match the real source behavior.
- No hidden root copy or target-project mirror becomes source of truth.

Exit state: materialized adapters behave consistently without duplicating
source.

### R9: Acceptance Gate

Status: TTS-009 decision recorded; ADR acceptance is recommended for the
instruction-level and provider-boundary scope, but owner approval is still
required before changing ADR status, release identity, sync, or release work.

Required closure:

- ADR 0004 can only move from proposed to accepted after fixtures, probes,
  adapter validation, TDS/doc-size validation, and explicit maintainer
  approval.
- Release identity is decided separately.
- Sync remains forbidden until the maintainer approves the complete skill.

Exit state: `tes-tts` has a certified release path or remains explicitly
proposed/degraded.

### R10: Owner Approval Gate

Status: TTS-010 recorded no explicit approval in the current goal context;
state remains `NEEDS_OWNER_DECISION`.

Required closure:

- Maintainer explicitly approves or rejects ADR 0004 acceptance.
- Maintainer explicitly approves or rejects release identity work.
- Maintainer explicitly approves or continues forbidding sync.
- If approval is partial, the next prompt names only the approved sub-unit.

Exit state: `tes-tts` either moves into an authorized acceptance/release
identity cycle or remains proposed/degraded with the next owner decision named.

### R11: Owner Decision Required

Status: TTS-011 recorded no explicit owner decision in the current goal
context; state remains `NEEDS_OWNER_DECISION`.

Required closure:

- If the maintainer accepts ADR 0004, change only the ADR/status and correlated
  decision surfaces.
- If release identity planning is authorized, create the release-identity
  execution prompt without bumping or releasing in the same cycle unless
  explicitly authorized.
- If sync remains forbidden, keep sync out of scope and name the next
  unresolved release or approval decision.

Exit state: the first explicit owner decision is applied or recorded without
crossing into unauthorized release, sync, provider, or global-state work.

### R12: Explicit Owner Decision

Status: TTS-012 recorded no explicit owner decision in the current goal
context; state remains `NEEDS_OWNER_DECISION`. This cycle also made the
roadmap update rule mandatory for every future `tes-tts` execution.

Required closure:

- If ADR 0004 is explicitly accepted or kept proposed, apply only that
  decision and correlated decision surfaces.
- If release identity planning is explicitly authorized or deferred, apply
  only that decision and create the next exact prompt.
- If sync is explicitly authorized without release identity approval, stop at
  `NEEDS_REVIEW`.

Exit state: the explicit owner decision is applied, or the cycle remains
`NEEDS_OWNER_DECISION` with the next unresolved decision named.

### R13-R17: Owner Decision Preservation

Status: TTS-013 through TTS-017 recorded no explicit owner decision and stayed
`NEEDS_OWNER_DECISION`. See the matching `TES-TTS-OWNER-DECISION-*.md`
records. Required closure was to apply only explicit maintainer decisions for
ADR 0004, release identity, and sync posture.

### R18-R31: Owner Decision Preservation Cycles

Status: TTS-018 through TTS-031 each recorded no explicit owner decision; state
remains `NEEDS_OWNER_DECISION`. Each cycle updated this roadmap, preserved ADR
0004 as `proposed`, left release identity deferred, kept sync forbidden, and
created the next tracked prompt artifact. See the corresponding
`TES-TTS-OWNER-DECISION-*.md` records and `GOAL-PROMPT-tes-tts-TTS-019*.md`
through `GOAL-PROMPT-tes-tts-TTS-032*.md`.

### R32: Owner Decision Still Open Yet Again

Status: superseded as the next execution shape. The repeated owner-decision
loop is now classified as non-convergent unless the user message contains a
direct approval decision. The next productive unit should be a technical
closure unit, starting with roadmap compaction and the concrete
`agent_default_language` selector contract.

Required closure:

- Keep ADR 0004 proposed unless explicitly accepted.
- Keep release identity and sync out of scope unless explicitly authorized.
- Compact roadmap index noise so historical prompts are not shown as active
  SPECs.
- Use `~/.codex/config.toml` `[desktop].localeOverride` as Codex default.
- Use `~/.claude/settings.json` `language` as Claude default, normalized by
  TES language policy.
- Treat Cursor as explicit User Rules/project rules first; when absent, use
  Codex default first and Claude default second.

## Ten-SPEC Convergence Draft Set

The remaining execution path is now organized as ten draft SPECs:

| SPEC | Focus | Artifact |
|------|-------|----------|
| 001 | Roadmap compaction and agent default language | `TES-TTS-SPEC-001-roadmap-compaction-agent-default-language.md` |
| 002 | Complete fixture corpus | `TES-TTS-SPEC-002-fixture-corpus-complete.md` |
| 003 | Deterministic instruction normalizer | `TES-TTS-SPEC-003-deterministic-instruction-normalizer.md` |
| 004 | Pronunciation enrichment rules | `TES-TTS-SPEC-004-pronunciation-enrichment-rules.md` |
| 005 | No-write provider probe | `TES-TTS-SPEC-005-provider-probe-no-write.md` |
| 006 | Provider candidate selection | `TES-TTS-SPEC-006-provider-candidate-selection.md` |
| 007 | Optional translation layer | `TES-TTS-SPEC-007-optional-translation-layer.md` |
| 008 | Optional G2P/pronunciation provider layer | `TES-TTS-SPEC-008-optional-g2p-pronunciation-provider-layer.md` |
| 009 | Release identity and sync readiness | `TES-TTS-SPEC-009-release-identity-sync-readiness.md` |
| 010 | Final audit and closure | `TES-TTS-SPEC-010-final-audit-and-closure.md` |

These drafts do not authorize sync, release, provider install, provider
download, global config writes, or durable conversion caches.

SPEC outcomes: SPEC-001 through SPEC-008 are `PASS`; SPEC-009 and SPEC-010
exited `NEEDS_OWNER_DECISION`; OWNER-001 resolved ADR acceptance. The ten-SPEC
technical sequence is complete for the bounded scope, ADR 0004 is `active`,
release identity is deferred, package identity remains at `0.3.147`, provider
claims remain optional/degraded/deferred, and sync remains unauthorized.
Next ready prompt:
`docs/roadmap/GOAL-PROMPT-tes-tts-CAP-005-adapter-parity-final-local-audit.md`.
Sync status: `REMOTE_SYNC_NOT_REQUESTED`.

CAP outcomes:

| CAP | Outcome | Sync |
|-----|---------|------|
| CAP-001 | Closed dependency-free `spoken_text` rendering for acronyms, semantic path/URL handling, exact-read preservation, redaction, and no-summary behavior. | `REMOTE_SYNC_NOT_REQUESTED` |
| CAP-002 | Closed speech transformation hardening for Markdown, code fences, hashes, GUIDs, email, IPv4, mentions, hashtags, false-positive guards, and exact reads. | `REMOTE_SYNC_NOT_REQUESTED` |
| CAP-003 | Closed pronunciation hints and protected-term preservation for URL, HTTP, JSON, YAML, SQL, SPEC, TES, Tilly, Codex, Claude, Cursor, OpenAI, package/model names, commands, and code identifiers. | `REMOTE_SYNC_NOT_REQUESTED` |
| CAP-004 | Closed request-local provider fallback catalog use with mocked fixtures for provider order, error classes, explicit voice preservation, voice-default retry, all-provider failure, and no durable provider state. | `REMOTE_SYNC_NOT_REQUESTED` |

## Current Open Questions

1. Does the maintainer explicitly approve release identity planning or
   continued deferral?
2. Does the maintainer explicitly authorize a later sync cycle after release
   identity is handled?

## Governance Rules

- Do not run sync from this roadmap.
- Do not release from this roadmap.
- Do not install or bundle normalization providers from this roadmap.
- Do not turn `tes-tts` into proactive `speak`.
- Do not summarize user text unless the user asks for summary.
- Do not persist conversion caches by default.
- Do not claim library-backed normalization until fixtures and provider probes
  prove the local behavior.
- Do not close any `tes-tts` execution cycle without updating this roadmap or
  recording why no material roadmap change was needed.
- Do not close a non-converged cycle without a tracked next `/goal` prompt
  artifact.

## Local Oracle Set

Use the smallest relevant oracle for each work unit:

```bash
python3 /Users/murillo/.codex/skills/.system/skill-creator/scripts/quick_validate.py src/adapters/codex/skills/tes-tts
python3 /Users/murillo/.codex/skills/.system/skill-creator/scripts/quick_validate.py src/adapters/claude/skills/tes-tts
python3 scripts/materialize_adapter.py codex --check
python3 scripts/materialize_adapter.py claude --check
python3 scripts/command_trigger_oracle.py --self-test
python3 scripts/tes_tts_fixture_schema_oracle.py --self-test
python3 scripts/tes_tts_instruction_normalizer_oracle.py --self-test
python3 scripts/tes_tts_provider_probe_oracle.py --self-test
python3 scripts/tes_tts_provider_candidate_review_oracle.py --self-test
python3 scripts/validate_tds.py
python3 scripts/validate_doc_size.py
python3 scripts/validate_reference_package.py
```

`npm run commit:check` remains the package closure gate, not a substitute for
the missing TTS-specific fixtures.
