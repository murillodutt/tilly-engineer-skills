---
tds_id: roadmap.tes_tts_cap_006_conversational_spoken_rendering
tds_class: roadmap
status: active
consumer: maintainers, tes-tts maintainers, adapter authors, validation authors, and execution agents
source_of_truth: false
evidence_level: L2
---

# TES TTS CAP-006 Conversational Spoken Rendering

## Purpose

Define the first execution cut for making `tes-tts` speak as an interlocutor
when the content is agent-authored or explicitly requested as natural narration,
while preserving faithful reading for user-supplied text.

## Problem

The current `tes-tts` layer can clean Markdown and protect many technical spans,
but it still treats speech primarily as cleaned text. That is not enough for
session-quality spoken interaction. A user should hear coherent oral prose, not
tables, Markdown structure, YAML-like dumps, or mechanical bullet lists, unless
the user asked for literal reading.

At the same time, conversational rendering must not become silent summary,
translation drift, provider overclaim, proactive `speak`, or a heavy NLP stack.

## First Cut

CAP-006 implements and certifies the contract shape before broad behavior:

1. Add an explicit rendering intent:
   - `conversational` for interlocutor-style oral prose;
   - `faithful_reading` for user text and exact/literal requests.
2. Add fixture coverage for the required CAP-006 cases.
3. Extend the instruction normalizer oracle so it can prove:
   - oral prose removes visible structure without losing facts;
   - faithful reading preserves content and order;
   - exact islands survive inside conversational speech;
   - protected English and technical terms stay un-translated;
   - secret redaction beats exact reading;
   - code blocks are never executed.
4. Update `.agents/skills/tes-tts` only after fixtures express the contract.
5. Mirror converged behavior into Codex source and Claude source only after
   workbench validation.

## Speech Posture

Conversational rendering may add small oral connectors and convert structure:

- "A decisão é..." instead of a table heading;
- "Primeiro..." and "Depois..." instead of raw bullet markers;
- "na pasta tes tts" for non-exact `.agents/skills/tes-tts`;
- "na página do GitHub" for non-exact GitHub URLs;
- `A D R`, `M C P`, `A P I`, `S D K`, and `C L I` for acronyms;
- protected terms like `GitHub`, `provider`, `fallback`, `cache`, `workflow`,
  `fixture`, `oracle`, `branch`, `commit`, and `pull request` preserved with
  English-pronunciation intent.

Conversational rendering must not:

- remove facts;
- merge separate decisions into one vague statement;
- infer missing subject, owner, or cause as fact;
- translate protected terms into approximate Portuguese;
- execute code;
- read secrets;
- claim SSML, IPA, phoneme, lexicon, G2P, or provider-backed pronunciation.

## Parsing Boundary

CAP-006 may approximate speech roles only through safe local cues:

| Role | Allowed signal | Boundary |
|------|----------------|----------|
| Subject | Explicit noun phrase near a verb, product/proper noun, or command context. | If implicit or ambiguous, keep the original wording. |
| Verb | Small lists of PT-BR imperatives/modals and English workflow verbs. | Do not claim full POS parsing. |
| Object | Protected terms, article/preposition patterns, and nearby nouns. | Do not invent omitted objects. |
| Intent | Explicit request cues such as read, narrate, summarize, exact, literal, raw. | Unknown intent remains unknown. |

The implementation should prefer conservative preservation over elegant but
unsafe prose.

## Acceptance Checks

CAP-006 is complete when:

- the new Super SPEC is indexed and roadmap-visible;
- CAP-006 fixtures exist and are enforced by a focused oracle;
- `conversational` and `faithful_reading` are distinct, tested intents;
- source text remains unchanged;
- `spoken_text` remains request-local;
- protected spans are applied before any rendering;
- secret-like content is redacted before rendering and TTS;
- exact islands are preserved even inside conversational speech;
- PT-BR platform narration preserves protected English/technical identity;
- no provider install, download, certification, durable cache, global config
  write, proactive speech, release, sync, push, tag, publish, or version bump
  occurs.

## Validation Plan

Focused CAP-006 validation should include:

```bash
python3 scripts/tes_tts_instruction_normalizer_oracle.py --self-test
python3 scripts/tes_tts_fixture_schema_oracle.py --self-test
python3 /Users/murillo/.codex/skills/.system/skill-creator/scripts/quick_validate.py .agents/skills/tes-tts
python3 /Users/murillo/.codex/skills/.system/skill-creator/scripts/quick_validate.py src/adapters/codex/skills/tes-tts
python3 /Users/murillo/.codex/skills/.system/skill-creator/scripts/quick_validate.py src/adapters/claude/skills/tes-tts
python3 scripts/materialize_adapter.py all --check
python3 scripts/validate_tds.py
python3 scripts/validate_doc_size.py
python3 scripts/validate_reference_graph.py
git diff --check
```

Run provider and command-trigger oracles when the implementation touches those
surfaces. Use `npm run commit:check` as package closure evidence only when
unrelated drift does not obscure the result.

## Next Prompt

Ready prompt:
`docs/roadmap/GOAL-PROMPT-tes-tts-CAP-006-conversational-spoken-rendering.md`
