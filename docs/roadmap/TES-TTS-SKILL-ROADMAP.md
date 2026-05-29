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

`tes-tts` is proposed delivered behavior staged in TES source. It is reactive:
it reads or narrates user-provided text only when explicitly requested. It must
not become the proactive `speak` channel, a dependency manager, a bundled
translation stack, or a global voice registry.

The current package state is intentionally pre-release:

- no sync has been authorized;
- no release identity has been closed;
- no provider dependency has been installed, bundled, or certified;
- normalization is instruction-level plus proposed architecture;
- local validators have passed during construction, but final package closure
  still requires the normal release gates and maintainer approval.

## Artifact Registry

| Surface | Role | Status |
|---------|------|--------|
| `src/adapters/codex/skills/tes-tts/SKILL.md` | Codex source skill contract. | staged |
| `src/adapters/claude/skills/tes-tts/SKILL.md` | Claude source skill contract. | staged |
| `src/adapters/*/skills/tes-tts/agents/openai.yaml` | Agent-facing invocation guidance. | staged |
| `src/adapters/*/skills/tes-tts/docs/CONTRACT-HISTORY.md` | Local history, origin signals, preserved contracts, and failure modes. | staged |
| `src/adapters/*/skills/tes-tts/references/language-normalization.md` | Instruction-level default-language, conversion-cache, and pronunciation reference. | staged |
| `src/adapters/*/skills/tes-tts/references/providers-and-fallbacks.md` | Portable provider fallback lessons from `speak`. | staged |
| `docs/adr/0004-tes-tts-pronunciation-normalization-and-enrichment.md` | Architectural GPS and boundary. | proposed |
| `docs/roadmap/TES-TTS-NORMALIZATION-ARCHITECTURE-SPEC.md` | Optional normalization architecture. | proposed |
| `docs/roadmap/TES-TTS-NORMALIZATION-EXECUTION-SPEC.md` | Sequential execution contract and acceptance gates. | proposed |
| `docs/roadmap/TES-TTS-NORMALIZATION-FIXTURE-SCHEMA.md` | Fixture schema explanation and TTS-004 boundary. | proposed |
| `docs/roadmap/TES-TTS-PROVIDER-CANDIDATE-REVIEW.md` | Ranked provider review queue, not certification. | proposed |
| `docs/roadmap/TES-TTS-ACCEPTANCE-AND-RELEASE-DECISION.md` | TTS-009 acceptance and release decision record. | active |
| `docs/roadmap/TES-TTS-OWNER-APPROVAL-GATE.md` | TTS-010 owner approval gate result. | active |
| `docs/roadmap/TES-TTS-OWNER-DECISION-REQUIRED.md` | TTS-011 owner decision result. | active |
| `docs/roadmap/TES-TTS-EXPLICIT-OWNER-DECISION.md` | TTS-012 explicit owner decision result. | active |
| `docs/roadmap/TES-TTS-OWNER-DECISION-PENDING.md` | TTS-013 owner decision pending result. | active |
| `docs/roadmap/TES-TTS-OWNER-DECISION-STILL-PENDING.md` | TTS-014 owner decision still pending result. | active |
| `docs/roadmap/TES-TTS-OWNER-DECISION-STILL-REQUIRED.md` | TTS-015 owner decision still required result. | active |
| `docs/roadmap/TES-TTS-OWNER-DECISION-REMAINS-REQUIRED.md` | TTS-016 owner decision remains required result. | active |
| `docs/roadmap/TES-TTS-OWNER-DECISION-OPEN.md` | TTS-017 owner decision open result. | active |
| `docs/roadmap/TES-TTS-OWNER-DECISION-UNRESOLVED.md` | TTS-018 owner decision unresolved result. | active |
| `docs/roadmap/TES-TTS-OWNER-DECISION-STILL-UNRESOLVED.md` | TTS-019 owner decision still unresolved result. | active |
| `docs/roadmap/TES-TTS-OWNER-DECISION-CONTINUES-UNRESOLVED.md` | TTS-020 owner decision continues unresolved result. | active |
| `docs/roadmap/TES-TTS-OWNER-DECISION-REMAINS-UNRESOLVED.md` | TTS-021 owner decision remains unresolved result. | active |
| `docs/roadmap/TES-TTS-OWNER-DECISION-STILL-REMAINS-UNRESOLVED.md` | TTS-022 owner decision still remains unresolved result. | active |
| `docs/roadmap/TES-TTS-OWNER-DECISION-UNRESOLVED-AGAIN.md` | TTS-023 owner decision unresolved again result. | active |
| `docs/roadmap/TES-TTS-OWNER-DECISION-STILL-UNRESOLVED-AGAIN.md` | TTS-024 owner decision still unresolved again result. | active |
| `docs/roadmap/TES-TTS-OWNER-DECISION-CONTINUES-UNRESOLVED-AGAIN.md` | TTS-025 owner decision continues unresolved again result. | active |
| `docs/roadmap/TES-TTS-OWNER-DECISION-REMAINS-UNRESOLVED-AGAIN.md` | TTS-026 owner decision remains unresolved again result. | active |
| `docs/roadmap/TES-TTS-OWNER-DECISION-STILL-REMAINS-UNRESOLVED-AGAIN.md` | TTS-027 owner decision still remains unresolved again result. | active |
| `docs/roadmap/TES-TTS-OWNER-DECISION-REMAINS-OPEN-AGAIN.md` | TTS-028 owner decision remains open again result. | active |
| `benchmarks/tes-tts/normalization-fixture.schema.json` | Machine-readable fixture schema. | proposed |
| `benchmarks/tes-tts/normalization-fixtures.json` | Minimal dependency-free fixture corpus. | proposed |
| `benchmarks/tes-tts/instruction-normalizer-fixtures.json` | Instruction-level normalizer oracle fixtures. | proposed |
| `benchmarks/tes-tts/provider-probe-fixtures.json` | Mocked provider probe contract fixtures. | proposed |
| `benchmarks/tes-tts/provider-candidate-review.json` | Structured provider candidate review queue. | proposed |
| `docs/roadmap/TES-TTS-SKILL-ROADMAP.md` | Executive registry and evolution roadmap. | active |
| `docs/roadmap/GOAL-SUPER-SPEC-tes-tts-sequential-convergence.md` | Circular execution contract for the skill. | active |
| `docs/roadmap/GOAL-PROMPT-tes-tts-TTS-000*.md` through `TTS-009*.md` | Historical prompt artifacts for baseline through acceptance decision. Indexed individually in TDS. | active |
| `docs/roadmap/GOAL-PROMPT-tes-tts-TTS-010*.md` through `TTS-019*.md` | Historical prompt artifacts for owner-decision preservation cycles. Indexed individually in TDS. | active |
| `docs/roadmap/GOAL-PROMPT-tes-tts-TTS-020*.md` through `TTS-028*.md` | Historical prompt artifacts for unresolved owner-decision cycles. Indexed individually in TDS. | active |
| `docs/roadmap/GOAL-PROMPT-tes-tts-TTS-029-owner-decision-still-open-again.md` | Ready prompt artifact for the next execution cycle. | active |
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
| 7 | Introduce adapter default language as an explicit preference that never overrides user-requested language. | Language reference and execution SPEC. |
| 8 | Require sequential convergence: one unit, one decision, one oracle, one next step. | Execution SPEC. |
| 9 | Require every non-converged execution cycle to create the next `/goal` prompt as a tracked artifact. | GOAL Super SPEC and tracked prompt artifacts. |
| 10 | Require every `tes-tts` execution cycle to update this roadmap before closure. | This roadmap, GOAL Super SPEC, and ready prompt artifacts. |

## Circular Execution Control

The executable sequence is:

```text
execute -> analyze -> fix -> certify -> create next /goal prompt -> local commit
```

The current circular execution contract is:
`docs/roadmap/GOAL-SUPER-SPEC-tes-tts-sequential-convergence.md`

The current ready prompt artifact is:
`docs/roadmap/GOAL-PROMPT-tes-tts-TTS-029-owner-decision-still-open-again.md`

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

Status: selector contract fixture-ready, pending executable fixtures.

Decision: adapter default language is a default preference, not a hard
priority. Explicit user language overrides adapter default language. A user
request such as "read this in English" must win even if the adapter declares
`pt-BR`.

Required closure:

- Update language references with the precedence rule.
- Update architecture or execution SPEC if needed.
- Record selector fixture candidates before executable fixture work.

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

Status: provider review queue added, pending adapter parity.

Candidate layers:

- language detection;
- translation;
- locale normalization;
- TTS text normalization;
- pronunciation, G2P, IPA, or Hebrew enrichment;
- Unicode cleanup.

Exit state: each provider candidate is either accepted for optional local use,
classified as degraded, or deferred.

### R8: Adapter Parity And Install Surface

Status: adapter parity checked, pending acceptance gate.

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

### R13: Owner Decision Pending

Status: TTS-013 recorded no explicit owner decision; state remains
`NEEDS_OWNER_DECISION`. See `TES-TTS-OWNER-DECISION-PENDING.md`.

### R14: Owner Decision Still Pending

Status: TTS-014 recorded no explicit owner decision; state remains
`NEEDS_OWNER_DECISION`. See `TES-TTS-OWNER-DECISION-STILL-PENDING.md`.

### R15: Owner Decision Still Required

Status: TTS-015 recorded no explicit owner decision; state remains
`NEEDS_OWNER_DECISION`. See `TES-TTS-OWNER-DECISION-STILL-REQUIRED.md`.

### R16: Owner Decision Remains Required

Status: TTS-016 recorded no explicit owner decision; state remains
`NEEDS_OWNER_DECISION`. See `TES-TTS-OWNER-DECISION-REMAINS-REQUIRED.md`.

### R17: Owner Decision Open

Status: TTS-017 recorded no explicit owner decision; state remains
`NEEDS_OWNER_DECISION`. See `TES-TTS-OWNER-DECISION-OPEN.md`.

R13-R17 required closure: apply only explicit maintainer decisions for ADR
0004, release identity, and sync posture; otherwise keep
`NEEDS_OWNER_DECISION`, update this roadmap, and create the next exact prompt.

### R18: Owner Decision Unresolved

Status: TTS-018 recorded no explicit owner decision; state remains
`NEEDS_OWNER_DECISION`, with roadmap update and TTS-019 prompt pointer done.

### R19: Owner Decision Still Unresolved

Status: TTS-019 recorded no explicit owner decision; state remains
`NEEDS_OWNER_DECISION`, with roadmap update and TTS-020 prompt pointer done.

### R20: Owner Decision Continues Unresolved

Status: TTS-020 recorded no explicit owner decision; state remains
`NEEDS_OWNER_DECISION`, with roadmap update, repeated-history compaction, and
TTS-021 prompt pointer done.

### R21: Owner Decision Remains Unresolved

Status: TTS-021 recorded no explicit owner decision; state remains
`NEEDS_OWNER_DECISION`, with roadmap update and TTS-022 prompt pointer done.

### R22: Owner Decision Still Remains Unresolved

Status: TTS-022 recorded no explicit owner decision; state remains
`NEEDS_OWNER_DECISION`, with roadmap update and TTS-023 prompt pointer done.

### R23: Owner Decision Unresolved Again

Status: TTS-023 recorded no explicit owner decision; state remains
`NEEDS_OWNER_DECISION`, with roadmap update and TTS-024 prompt pointer done.

### R24: Owner Decision Still Unresolved Again

Status: TTS-024 recorded no explicit owner decision; state remains
`NEEDS_OWNER_DECISION`, with roadmap update and TTS-025 prompt pointer done.

### R25: Owner Decision Continues Unresolved Again

Status: TTS-025 recorded no explicit owner decision; state remains
`NEEDS_OWNER_DECISION`, with roadmap update and TTS-026 prompt pointer done.

### R26: Owner Decision Remains Unresolved Again

Status: TTS-026 recorded no explicit owner decision; state remains
`NEEDS_OWNER_DECISION`, with roadmap update, TTS-027 prompt pointer, and
roadmap historical prompt row compaction done.

### R27: Owner Decision Still Remains Unresolved Again

Status: TTS-027 recorded no explicit owner decision; state remains
`NEEDS_OWNER_DECISION`, with roadmap update and TTS-028 prompt pointer done.

### R28: Owner Decision Remains Open Again

Status: TTS-028 recorded no explicit owner decision; state remains
`NEEDS_OWNER_DECISION`, with roadmap update and TTS-029 prompt pointer done.

### R29: Owner Decision Still Open Again

Status: next work unit, awaiting explicit maintainer decision. Required
closure remains ADR 0004, release identity, and sync posture only.

## Current Open Questions

1. Where should a future `agent_default_language` declaration live for each
   adapter?
2. Which TTS fixture class should become the first corpus entry after the
   selector cases?
3. Which provider probe should be built first: local `say`, language
   detection, or translation package discovery?
4. What is the acceptance threshold for Hebrew: preserve, translate, niqqud
   enrich, or explicitly degraded?

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
