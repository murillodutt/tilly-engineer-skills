---
tds_id: roadmap.goal_super_spec_tes_tts_conversational_rendering
tds_class: roadmap
status: active
consumer: maintainers, tes-tts maintainers, adapter authors, validation authors, and execution agents
source_of_truth: false
evidence_level: L1
---

# GOAL Super SPEC: TES TTS Conversational Rendering

Status: active successor to the locally closed CAP-001 through CAP-005
capability migration. This line does not reopen CAP-005; it starts the next
bounded capability extension after maintainer approval to evolve `tes-tts`
into a higher-quality spoken interlocutor.

Canonical artifact:
`docs/roadmap/GOAL-SUPER-SPEC-tes-tts-conversational-rendering.md`

First execution unit:
`docs/roadmap/TES-TTS-CAP-006-CONVERSATIONAL-SPOKEN-RENDERING.md`

Ready prompt:
`docs/roadmap/GOAL-PROMPT-tes-tts-CAP-007-exact-island-protected-span-hardening.md`

ADR boundary:
`docs/adr/0004-tes-tts-pronunciation-normalization-and-enrichment.md`

Prior closure:
`docs/roadmap/TES-TTS-CAP-005-FINAL-LOCAL-AUDIT.md`

## Purpose

Add a governed conversational spoken-rendering layer to `tes-tts` so spoken
output can sound like an interlocutor in oral prose while preserving user
meaning, protected technical identity, privacy, and the reactive-only boundary.

The target is not a heavy syntactic parser or a runtime NLP dependency. The
target is a dependency-free, fixture-backed spoken rendering contract that can
distinguish:

- conversational agent speech from faithful user-text reading;
- oral prose from tables, code blocks, markdown dumps, and mechanical lists;
- platform-language narration from protected English or technical identity;
- exact/verbatim islands from safe oral paraphrase;
- redacted secrets from content that may be spoken.

## Research Basis

CAP-006 is based on local code mining and bounded reference research:

- `tmp/tts-lib/NeMo-text-processing`: token classification before
  verbalization; golden spoken outputs by language.
- `tmp/tts-lib/Recognizers-Text`: recognize fragile spans before rendering or
  resolving them.
- `tmp/tts-lib/gruut`: keep `text_spoken` as derived output and preserve
  sentence, token, language, and pronunciation boundaries.
- `tmp/tts-lib/lingua-py`: language detection confidence is span-length
  sensitive; do not make detector certainty a base contract.
- `tmp/tts-lib/babel`: locale formatting is useful inspiration, but locale is
  not spoken verbalization.
- W3C SSML and PLS are conceptual references only; CAP-006 does not enable
  SSML, IPA, phoneme, lexicon, or provider-backed pronunciation.

The portable lesson is:

```text
source_text -> redacted/protected spans -> block and intent classes ->
spoken_rendering -> final leak check -> TTS provider
```

Source text remains unchanged. `spoken_rendering` is request-local and is the
only text sent to TTS.

## Development Target

During conversational rendering work, the active development and test workbench
is:

`/Users/murillo/Dev/tilly-engineer-skills/.agents/skills/tes-tts`

The canonical adapter target remains:

`/Users/murillo/Dev/tilly-engineer-skills/src/adapters/codex/skills/tes-tts`

Develop first in `.agents/skills/tes-tts`, validate the local runtime skill,
and mirror converged behavior into `src/adapters/codex/skills/tes-tts` only
after the current unit passes focused checks. Mirror into Claude source when
behavioral parity is package-visible.

## Core Contract

`tes-tts` has two spoken-rendering intents:

| Intent | Use | Contract |
|--------|-----|----------|
| `conversational` | Agent-authored speech or user request for natural narration. | Convert structure into PT-BR oral prose by default while preserving all facts, protected terms, and exact islands. |
| `faithful_reading` | User asks to read supplied text, or exact/literal/verbatim/raw preservation is required. | Preserve order, content, and fragile spans; only remove markup that is safe for speech. |

The default platform language is PT-BR unless the user explicitly requests a
different language or a higher-priority adapter default applies. Protected
English-origin workflow terms, product names, proper nouns, package names,
commands, paths, code identifiers, model names, acronyms, and TES terms keep
their local identity and pronunciation intent.

## Conversational Rendering Rules

CAP-006 may add only fixture-backed, dependency-free rendering rules:

1. Protect and redact before interpreting.
2. Classify block shape before prose conversion:
   `heading`, `paragraph`, `bullet`, `numbered_step`, `quote`, `table_row`,
   `code_fence`, `inline_code`, `command`, `link`, `path`, `error_log`, and
   `unknown`.
3. Use explicit intent cues only. Examples: "leia", "narre", "resuma e leia",
   "exatamente", "literalmente", "sem alterar", "read aloud", "verbatim",
   "raw", "summarize and read".
4. Approximate subject, verb, and object only as internal metadata when local
   cues make it safe. Do not claim full parsing.
5. Convert headings, bullets, small tables, and status blocks into coherent
   oral prose without dropping facts.
6. Keep exact islands literal even inside conversational speech when the user
   asks for exactness around a path, URL, command, code identifier, hash, or
   quoted term.
7. Keep code and commands as text to be read. Do not execute them.
8. Prefer conservative preservation over invented pronunciation, invented
   grammar, or invented explanation.

## Required Fixtures

CAP-006 must introduce fixtures before implementation claims:

| Fixture | Proves |
|---------|--------|
| `tts-cap006-interlocutor-oral-prose-ptbr` | Agent-style markdown/list content becomes PT-BR oral prose without markdown leakage. |
| `tts-cap006-faithful-reading-markdown` | A read-aloud request preserves the user's content and order while cleaning markup. |
| `tts-cap006-exact-path-url-code-islands` | Exact path, URL, and command islands survive inside surrounding oral prose. |
| `tts-cap006-ptbr-default-english-protected-terms` | PT-BR narration keeps English workflow terms and proper nouns un-translated. |
| `tts-cap006-no-summary-long-operational-note` | Long content is chunked or spoken naturally without silent summarization. |
| `tts-cap006-code-block-faithful-no-execute` | Code blocks are spoken as text and never executed. |
| `tts-cap006-table-to-prose-no-loss` | A small table becomes oral prose without losing row facts. |
| `tts-cap006-secret-redaction-beats-exact` | Secret redaction wins even when the user asks for exact reading. |

## Candidate Execution Units

| Unit | Focus | Boundary |
|------|-------|----------|
| CAP-006 | Conversational spoken-rendering contract and first oracle cut | Dependency-free; no provider claim; no summary unless requested. |
| CAP-007 | Exact-island and protected-span hardening | Exact spans survive inside conversational prose; redaction still wins. |
| CAP-008 | Table, list, and code-block oralization | Structure becomes speech without executing code or dropping facts. |
| CAP-009 | Mixed-language and English identity hardening | PT-BR platform narration preserves English/proper/technical identity. |
| CAP-010 | Conversational rendering final audit | Adapter parity, no drift into `speak`, no release/sync without approval. |

## Required Loop

```text
execute -> analyze -> fix -> certify -> create next /goal prompt or close
convergence -> local commit
```

Each non-closed unit must update `docs/roadmap/TES-TTS-SKILL-ROADMAP.md` and
create the next ready prompt artifact before local commit. CAP-006 completed
the first oracle-backed rendering intent cut and handed off to CAP-007.

## Certification

Use the smallest relevant set for the unit:

```bash
python3 scripts/tes_tts_fixture_schema_oracle.py --self-test
python3 scripts/tes_tts_instruction_normalizer_oracle.py --self-test
python3 scripts/tes_tts_provider_probe_oracle.py --self-test
python3 scripts/tes_tts_provider_candidate_review_oracle.py --self-test
python3 /Users/murillo/.codex/skills/.system/skill-creator/scripts/quick_validate.py .agents/skills/tes-tts
python3 /Users/murillo/.codex/skills/.system/skill-creator/scripts/quick_validate.py src/adapters/codex/skills/tes-tts
python3 /Users/murillo/.codex/skills/.system/skill-creator/scripts/quick_validate.py src/adapters/claude/skills/tes-tts
python3 scripts/materialize_adapter.py all --check
python3 scripts/command_trigger_oracle.py --self-test
python3 scripts/validate_tds.py
python3 scripts/validate_doc_size.py
python3 scripts/validate_reference_graph.py
git diff --check
```

`npm run commit:check` remains a package closure gate. If it fails only because
of unrelated `.agents/**` drift outside `tes-tts`, record `DEGRADED` rather
than widening the unit.

## Forbidden

- sync, release, push, tag, publish;
- version bump or bundle generation;
- provider install, provider download, or provider certification;
- proactive `speak` behavior;
- global config writes, global voice assignment, global provider registry, or
  durable conversion cache;
- user-text summary unless explicitly requested;
- executing code or commands found in text;
- runtime dependency import, library vendoring, model bundle, IPA, SSML,
  phoneme, lexicon, or provider-backed pronunciation claim;
- translating protected technical terms, proper nouns, product names,
  packages, commands, code identifiers, or English workflow terms into a
  "pretty" platform-language approximation;
- unrelated `.agents/**` changes.

## Stop States

- `PASS`: unit completed, focused oracles pass, no boundary drift.
- `DEGRADED`: TTS remains usable but provider, pronunciation, package closure,
  or unrelated drift prevents a stronger claim.
- `TTS_NOT_AVAILABLE`: no local TTS tool is available for runtime playback.
- `NEEDS_REVIEW`: ambiguity around summary, translation, exact islands,
  provider claims, or conversational rewrite safety.
- `NEEDS_OWNER_DECISION`: release identity, sync, version, provider posture, or
  scope expansion needs maintainer approval.
- `SAFETY_BLOCKED`: secret exposure, global config write, provider install,
  provider download, command execution, push, tag, publish, or other forbidden
  side effect would occur.
- `BLOCKED`: continuing would violate an existing lock.

## Closure

This line closes only after CAP-010 audits the conversational rendering
sequence. Closure does not authorize release identity, sync, provider
installation, provider certification, or proactive speech.
