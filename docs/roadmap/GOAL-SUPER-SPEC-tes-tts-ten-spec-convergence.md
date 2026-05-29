---
tds_id: roadmap.goal_super_spec_tes_tts_ten_spec_convergence
tds_class: roadmap
status: active
consumer: maintainers, tes-tts maintainers, execution agents, and release reviewers
source_of_truth: false
evidence_level: L1
---

# GOAL Super SPEC: TES TTS Ten-SPEC Convergence

Status: active execution contract for closing `tes-tts` through ten bounded
SPEC units.

Canonical artifact:
`docs/roadmap/GOAL-SUPER-SPEC-tes-tts-ten-spec-convergence.md`

Primary roadmap:
`docs/roadmap/TES-TTS-SKILL-ROADMAP.md`

Architectural boundary:
`docs/adr/0004-tes-tts-pronunciation-normalization-and-enrichment.md`

## Purpose

Run `tes-tts` to convergence through a circular, auditable loop:

```text
execute -> analyze -> fix -> certify -> create next Super SPEC + /goal prompt
or close convergence -> local commit
```

This Super SPEC replaces repeated owner-decision preservation loops with a
technical sequence. Owner decisions still gate ADR acceptance, release
identity, sync, provider install, provider download, push, tag, publish, and
provider certification.

## Certified Context

- `tes-tts` is reactive read-aloud behavior only.
- `speak` remains proactive and separate.
- ADR 0004 is still `proposed` unless explicitly accepted in a later owner
  decision.
- Normalization is instruction-level unless later provider SPECs certify more.
- Provider probing is no-write and non-certifying unless a later SPEC proves
  otherwise.
- Sync, release, push, tag, publish, provider install, provider download,
  global config writes, and durable conversion caches remain forbidden.
- The ten draft SPECs live at `docs/roadmap/TES-TTS-SPEC-001-*.md` through
  `docs/roadmap/TES-TTS-SPEC-010-*.md`.

## Phase Boundary

This Super SPEC may create and refine local docs, fixtures, scripts, and skill
references needed to certify each SPEC. It must not perform release or sync
actions. Release identity is handled only in SPEC 009 after explicit owner
authorization.

## Non-Objectives

- Do not run sync, release, push, tag, publish, or marketplace actions.
- Do not install, download, bundle, or auto-enable providers.
- Do not write global config.
- Do not persist conversion caches.
- Do not import proactive `speak` behavior.
- Do not summarize user text unless explicitly requested.
- Do not claim provider-backed translation or pronunciation until proven.

## Central Rule

One unit at a time, one material trail per unit:

```text
select unit -> execute smallest change -> analyze -> fix -> certify
-> create next Super SPEC + /goal prompt or close -> local commit
```

Every non-converged unit must leave a ready next `/goal` prompt artifact. When
a future unit needs a changed execution contract, update this Super SPEC or
create the next Super SPEC before the local commit.

## Execution Units

| Unit | Objective | Allowed files | Focused oracles | Commit message |
|------|-----------|---------------|-----------------|----------------|
| 000 Preflight And Baseline | Classify worktree, inherited TTS changes, unrelated `.agents/**` drift, and current roadmap state. | docs/roadmap/** only if recording baseline. | `git status --short --branch --untracked-files=all`; targeted `rg`. | `Record tes-tts ten-spec preflight baseline` |
| SPEC-001 Roadmap Compaction And Agent Default Language | Close the owner-decision loop, encode Codex/Claude/Cursor default-language fallback, and keep TTS prompts organized. | TTS roadmap docs, language references, selector fixtures, selector oracle. | `python3 scripts/tes_tts_fixture_schema_oracle.py --self-test`; `python3 scripts/validate_tds.py`; `python3 scripts/validate_doc_size.py`. | `Converge tes-tts spec 001 agent default language` |
| SPEC-002 Fixture Corpus Complete | Add first-class language and negative fixtures for the claimed scope. | `benchmarks/tes-tts/**`, fixture docs, roadmap. | `python3 scripts/tes_tts_fixture_schema_oracle.py --self-test`. | `Converge tes-tts spec 002 fixture corpus` |
| SPEC-003 Deterministic Instruction Normalizer | Make selector/cache/protected-term/redaction/chunking behavior deterministic. | `scripts/tes_tts_instruction_normalizer_oracle.py`, fixtures, references. | `python3 scripts/tes_tts_instruction_normalizer_oracle.py --self-test`. | `Converge tes-tts spec 003 instruction normalizer` |
| SPEC-004 Pronunciation Enrichment Rules | Add conservative pronunciation rules without semantic translation. | language references, fixtures, instruction oracle. | instruction normalizer and fixture schema oracles. | `Converge tes-tts spec 004 pronunciation rules` |
| SPEC-005 Provider Probe No-Write | Harden local no-write provider probe contract. | provider probe oracle, provider fixtures, provider docs. | `python3 scripts/tes_tts_provider_probe_oracle.py --self-test`. | `Converge tes-tts spec 005 provider probe` |
| SPEC-006 Provider Candidate Selection | Select optional provider candidates without certifying them. | provider candidate review docs/fixtures/oracle. | `python3 scripts/tes_tts_provider_candidate_review_oracle.py --self-test`. | `Converge tes-tts spec 006 provider selection` |
| SPEC-007 Optional Translation Layer | Define optional local translation boundary and safeguards. | translation fixtures/docs/provider notes only. | fixture schema, instruction normalizer, provider probe. | `Converge tes-tts spec 007 translation layer` |
| SPEC-008 Optional G2P Pronunciation Provider Layer | Define optional G2P/pronunciation provider boundary and degraded Hebrew posture. | provider docs/fixtures/oracles, pronunciation docs. | provider probe, instruction normalizer, fixture schema. | `Converge tes-tts spec 008 pronunciation provider layer` |
| SPEC-009 Release Identity And Sync Readiness | Decide release identity and sync readiness without performing sync unless explicitly authorized. | release decision docs, roadmap, version surfaces only if explicitly authorized. | `python3 scripts/command_trigger_oracle.py --self-test`; `python3 scripts/materialize_adapter.py all --check`; `npm run commit:check`. | `Converge tes-tts spec 009 release readiness` |
| SPEC-010 Final Audit And Closure | Audit all surfaces and either close or name the exact remaining degraded/deferred unit. | final audit docs, roadmap, indexes. | all focused TTS oracles, validators, and `npm run commit:check`. | `Converge tes-tts spec 010 final audit` |

## Current Ready /goal Prompt

Current ready prompt:
`docs/roadmap/GOAL-PROMPT-tes-tts-SPEC-004-pronunciation-enrichment-rules.md`

SPEC-001 through SPEC-003 prompts are retained as historical execution evidence:
`docs/roadmap/GOAL-PROMPT-tes-tts-SPEC-001-roadmap-compaction-agent-default-language.md`
`docs/roadmap/GOAL-PROMPT-tes-tts-SPEC-002-fixture-corpus-complete.md`
`docs/roadmap/GOAL-PROMPT-tes-tts-SPEC-003-deterministic-instruction-normalizer.md`

## Subagent Ownership

- Use subagents only for read-only review, fixture gap analysis, provider
  candidate review, or oracle result review.
- Keep write execution serialized in the main agent unless a later prompt names
  disjoint write scopes.
- Do not parallelize commits. Each material unit gets one local commit or an
  explicit no-commit rationale.

## Negative Grep

Run targeted negative checks when relevant:

```bash
rg -n "sync|push|tag|publish|release" docs/roadmap/TES-TTS* src/adapters/*/skills/tes-tts
rg -n "install|download|pip install|npm install|brew install" docs/roadmap/TES-TTS* scripts/tes_tts_* benchmarks/tes-tts
rg -n "tts-config|tts-assignments|voice-pools|proactive|planning/issue/summary" src/adapters/*/skills/tes-tts docs/roadmap/TES-TTS*
rg -n "write_text|write_bytes|open\\(" scripts/tes_tts_*_oracle.py
```

Allowed policy mentions must be distinguished from executable violations.

## Commit Strategy

- Before each unit: `git status --short --branch --untracked-files=all`.
- Stage only files belonging to the current unit.
- Preserve unrelated `.agents/**` drift as user-owned unless explicitly
  instructed otherwise.
- Commit locally after certification.
- Remote sync is `REMOTE_SYNC_NOT_REQUESTED` unless the user explicitly
  authorizes remote actions.

## Review Loop

Each unit must record:

1. declared unit id;
2. changed files;
3. focused oracles run;
4. negative checks run or no-change rationale;
5. reviewer result: `PASS`, `DEGRADED`, `NEEDS_REVIEW`, or `BLOCKED`;
6. local commit hash or no-commit rationale;
7. next `/goal` prompt artifact or closure statement.

## Stop States

| State | Meaning |
|-------|---------|
| `PASS` | The unit converged and was locally committed. |
| `DEGRADED` | Basic `tes-tts` works, but a scoped capability remains partial. |
| `NEEDS_REVIEW` | Maintainer review is needed before the next material unit. |
| `NEEDS_OWNER_DECISION` | ADR, release, sync, or provider posture needs owner approval. |
| `BLOCKED` | Continuing would violate a forbidden move or unresolved safety boundary. |

## Final Delivery Contract

The final response for each execution unit must summarize changed files,
oracles, stop state, next prompt, commit hash, and sync status. The final
convergence response must say whether `tes-tts` is complete for the approved
scope or explicitly degraded/deferred.
