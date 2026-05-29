---
tds_id: roadmap.goal_super_spec_tes_tts_ptbr_lexical_normalization
tds_class: roadmap
status: active
consumer: maintainers, tes-tts maintainers, adapter authors, validation authors, and execution agents
source_of_truth: false
evidence_level: L1
---

# GOAL Super SPEC: TES TTS PT-BR Lexical Normalization

Status: active pivot from the conversational-rendering line. CAP-010 final
audit is intentionally superseded until this lexical foundation converges.

Canonical artifact:
`docs/roadmap/GOAL-SUPER-SPEC-tes-tts-ptbr-lexical-normalization.md`

Current execution unit:
`LEX-005 PT-BR lexical final audit`

Ready prompt:
`docs/roadmap/GOAL-PROMPT-tes-tts-LEX-005-ptbr-lexical-final-audit.md`

Prior line:
`docs/roadmap/GOAL-SUPER-SPEC-tes-tts-conversational-rendering.md`

## Purpose

Move `tes-tts` from growing manual pronunciation rules toward a mature,
NeMo-inspired lexical normalization architecture focused first on PT-BR.

This pivot keeps the local TES constraints:

- no runtime dependency on NeMo or other provider libraries;
- no provider install, provider download, model bundle, release, publish, tag,
  push, or sync;
- no user-text summary unless explicitly requested;
- no proactive `speak` behavior;
- no IPA, SSML, phoneme, lexicon, G2P, or provider-backed runtime claim until
  fixtures and local oracles prove the behavior and the maintainer approves
  that surface.

## Research Basis

Local analysis of `tmp/tts-lib/NeMo` found a stronger architecture than the
current manual-rule path:

- `nemo/collections/tts/g2p/models/i18n_ipa.py` separates graphemes from
  phoneme/IPA representations and loads dictionary sources before fallback.
- `nemo/collections/tts/g2p/utils.py` uses explicit grapheme case handling and
  heteronym span detection as governed preprocessing.
- `scripts/tts_dataset_files/pt_BR/pt_br_prondict-v1.0.dict` provides a large
  PT-BR pronunciation dictionary in `WORD<TAB>IPA` shape.
- G2P training configs use structured manifest fields such as
  `text_graphemes` and `text`, not Markdown prose.

TES will learn from this shape without copying NeMo code into runtime.

## Target Architecture

The target pipeline becomes:

```text
source_text
-> secret redaction
-> protected span classification
-> block/intent classification
-> PT-BR lexical lookup
-> pronunciation evidence metadata
-> spoken_text
-> final leak check
-> TTS provider
```

`source_text` remains immutable. `spoken_text` remains request-local. Lexical
evidence is metadata until a later approved runtime surface decides how to use
it.

## PT-BR First Scope

The first converged scope is PT-BR only:

- build a TES lexical manifest shape for grapheme/pronunciation evidence;
- ingest or sample public PT-BR dictionary material into a governed local
  fixture format;
- create dependency-free lookup oracles;
- keep manual protected-term rendering from CAP-006 through CAP-009;
- prove that lexical metadata does not leak secrets, mutate source text,
  summarize content, execute code, or create provider-backed claims.

Other languages remain deferred until PT-BR converges.

## Dataset Direction

Markdown is no longer the target dataset format for TTS pronunciation
evidence. The target dataset format is JSONL or JSON manifest records:

```json
{
  "id": "ptbr-lexical-000001",
  "language": "pt-BR",
  "text_graphemes": "ABACAXI",
  "pronunciation": "ˌabakaʃˈi",
  "pronunciation_system": "ipa",
  "source": "pt_br_prondict",
  "usage": "evidence_only",
  "status": "reference"
}
```

This does not authorize sending IPA or phonemes to TTS. It authorizes lexical
evidence and deterministic local checks.

## Execution Units

| Unit | Focus | Boundary |
|------|-------|----------|
| LEX-001 | PT-BR lexical dataset and manifest contract | Complete: schema, converter, sample fixtures, provenance fields, and no-runtime-claim rules. |
| LEX-002 | PT-BR lexical lookup oracle | Complete: dependency-free parser/lookup over fixture/sample data; no provider integration. |
| LEX-003 | Spoken-rendering integration boundary | Complete: attach lexical evidence to request-local speech preparation without altering source text or claiming IPA runtime. |
| LEX-004 | Fixture migration from Markdown-shaped TTS cases | Complete: migrated representative pronunciation guidance to JSON fixtures while preserving current oracles. |
| LEX-005 | PT-BR lexical final audit | Confirm local scope, gaps, license/provenance notes, and next language expansion decision. |

## Required Loop

```text
execute -> analyze -> fix -> certify -> create next /goal prompt or close
convergence -> local commit
```

Each non-closed unit must update `docs/roadmap/TES-TTS-SKILL-ROADMAP.md` and
create the next ready prompt artifact before local commit.

## Certification

Use the smallest relevant set for the unit:

```bash
python3 scripts/tes_tts_ptbr_prondict_to_manifest.py --self-test
python3 scripts/tes_tts_fixture_schema_oracle.py --self-test
python3 scripts/tes_tts_instruction_normalizer_oracle.py --self-test
python3 scripts/tes_tts_provider_probe_oracle.py --self-test
python3 scripts/tes_tts_provider_candidate_review_oracle.py --self-test
python3 /Users/murillo/.codex/skills/.system/skill-creator/scripts/quick_validate.py .agents/skills/tes-tts
python3 /Users/murillo/.codex/skills/.system/skill-creator/scripts/quick_validate.py src/adapters/codex/skills/tes-tts
python3 /Users/murillo/.codex/skills/.system/skill-creator/scripts/quick_validate.py src/adapters/claude/skills/tes-tts
python3 scripts/materialize_adapter.py all --check
python3 scripts/validate_tds.py
python3 scripts/validate_doc_size.py
python3 scripts/validate_reference_graph.py
git diff --check
```

Add lexical-specific oracles as LEX units create them.

## Stop States

- `PASS`: unit completed, focused oracles pass, no boundary drift.
- `DEGRADED`: lexical metadata is useful but package closure, provenance,
  provider, or unrelated drift prevents a stronger claim.
- `NEEDS_REVIEW`: ambiguity around provenance, runtime claims, IPA exposure,
  fixture migration, protected identity, or integration boundary.
- `NEEDS_OWNER_DECISION`: release identity, sync, provider posture, language
  expansion, or runtime IPA/phoneme surface needs maintainer approval.
- `SAFETY_BLOCKED`: secret exposure, command execution, global config write,
  provider install/download, push, tag, publish, or forbidden side effect
  would occur.
- `BLOCKED`: continuing would violate an existing lock.

## Closure

This line closes only after LEX-005 audits the PT-BR lexical foundation.
Closure does not authorize release identity, sync, provider installation,
provider certification, IPA runtime output, SSML, phoneme output, or proactive
speech.
