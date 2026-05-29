---
tds_id: roadmap.tes_tts_cap_001_portable_capability_feasibility
tds_class: roadmap
status: active
consumer: maintainers, tes-tts maintainers, adapter authors, and execution agents
source_of_truth: false
evidence_level: L2
---

# TES TTS CAP-001 Portable Capability Feasibility

## Purpose

Reanalyze related local TTS projects and decide what can be migrated into
`tes-tts` before CAP-001 implementation starts.

## Inputs Reviewed

| Source | Role | Finding |
|--------|------|---------|
| `.agents/skills/tes-tts/**` | Active development and test workbench. | Current runtime skill is small, reactive, valid, and already mirrors the Codex source shape. |
| `src/adapters/codex/skills/tes-tts/**` | Canonical Codex adapter target. | Receives converged content after workbench validation. |
| `tmp/skills/speak/SKILL.md` | Related proactive TTS skill. | Useful provider fallback, error classes, voice notes, and speech transformation patterns; proactive/config behavior is not portable. |
| `tmp/skills/speak/references/voice-pools.json` | Voice catalog from `speak`. | Useful as historical voice inventory only; do not migrate as runtime config or auto-assignment. |
| `benchmarks/tes-tts/**` and `scripts/tes_tts_*_oracle.py` | Existing local evidence. | Already cover protected terms, redaction, chunking, provider boundaries, and degraded translation/pronunciation posture. |
| Live TTS test on 2026-05-29 | Runtime evidence. | Voice and rate are good; spoken rendering fails when acronyms, paths, and URLs are interpreted incorrectly. |

## External GitHub Projects Reviewed

These projects are mature learning references. CAP-001 must not add them as
dependencies. The intent is to inspect their code, fixtures, and architecture,
then migrate only small learned patterns into TES-owned, dependency-free
implementation.

Prior research reached the same core conclusion: no single library cleanly
covers language detection, span translation, protected-term preservation, and
TTS pronunciation adaptation. The useful path is a plug-shaped TES pipeline
that can learn from mature projects without depending on them:

```text
cleanup -> language detection -> protected terms -> translation cache ->
pronunciation hints -> TTS
```

| Project | Layer | Code to inspect | TES migration posture |
|---------|-------|-----------------|-----------------------|
| `microsoft/Recognizers-Text` | Multi-language entity recognition for numbers, units, datetime, phone, URL, email, GUID, IP | Sequence recognizers, URL/email/IP/GUID classifiers, specs for generic entities. | Highest priority. Reimplement tiny recognizers for URL/path/acronym classes; no dependency. |
| `NVIDIA/NeMo-text-processing` | TTS text normalization and inverse text normalization | Grammar organization, language-specific TN boundaries, tests/golden outputs. | Study grammar/test shape only. Reimplement small deterministic rules; no WFST/Pynini/OpenFst. |
| `ftfy` | Unicode cleanup | Mojibake and Unicode repair boundaries before downstream detection/rendering. | Study as cleanup inspiration. Reimplement only tiny safe cleanup rules if fixtures justify them. |
| `rhasspy/gruut` | Tokenizer, text cleaner, phonemizer | Token stream shape, text_spoken fields, locale-aware verbalization toggles. | Study pipeline shape. Do not import archived runtime or language packages. |
| `python-humanize/humanize` | Human-friendly number/date/size wording | Small pure helpers and localized wording tests. | Study style and fixture shape; do not summarize user text. |
| `python-babel/babel` | Locale and CLDR-backed formatting | Locale normalization boundaries and CLDR-backed date/number formatting tests. | Study boundaries only; optional future probe, no dependency now. |
| `savoirfairelinux/num2words` | Numbers to words | Language tables and test organization for number verbalization. | Study tests for future number handling; no dependency in CAP-001. |
| `Workable/python-dateparser` | Human-readable date parsing | Locale/date fixtures and failure cases. | Study fixture design only; no broad parser migration. |
| `pemistahl/lingua-py` | Language detection | Short-text detection constraints and confidence posture. | Study confidence/degraded semantics; no detector dependency. |
| `fastText language identification` | Broad language detection | Model-vs-code split, compact model posture, and redistribution/licensing boundary. | Defer runtime use. Learn model-governance caution; do not bundle models. |
| `argosopentech/argos-translate` | Offline translation | Package/language-pair management and local translation boundaries. | Defer. Learn optional translation-cache posture; no model packages or downloads. |
| `bootphon/phonemizer` | Text-to-phone conversion | Backend boundary and output-mode flags. | Study boundary design only; no GPL/backend dependency. |
| `espeak-ng/espeak-ng` | Speech synthesis and phonemization | Acronym/voice/language boundary concepts. | Study provider boundary only; no install or certification. |

Immediate learning for CAP-001:

- recognize entities before rendering speech;
- keep URL/path handling deterministic and conservative;
- separate "spoken rendering" from source-text mutation;
- keep pronunciation/provider machinery as a later optional boundary;
- keep language detection and translation as optional stages with degraded
  behavior when no local provider is certified;
- build adversarial fixtures before adopting any library behavior.

Migration rule: learned patterns must become TES-owned code, fixtures, or
references. Do not vendor, install, wrap, shell out to, or add package imports
from the reviewed repositories in CAP-001.

## Deep Code Mining Findings

CAP-001 was reanalyzed with local checkouts under `tmp/tts-lib/`. The checkouts
are research inputs only and are not package source, runtime dependencies, or
bundle contents.

| Reference | Portable lesson | CAP-001 implication |
|-----------|-----------------|---------------------|
| `Recognizers-Text` | Detect spans first, resolve/render them second. URL, email, IP, GUID, mention, and hashtag recognizers are split into small patterns plus false-positive guards. | Add a tiny ordered TES recognizer table for speech-shape spans. Start with secret-like values, URLs, paths, acronyms, and exact-read guards. |
| `NeMo-text-processing` | TTS normalization separates token classification from verbalization and validates golden spoken outputs per language. | Keep `normalized_text` separate from `spoken_text`; add explicit fixtures for expected spoken rendering. Do not bring WFST, Pynini, or OpenFst into CAP-001. |
| `gruut` | `text_spoken` is derived output, not a mutation of source text. Token streams keep source, spoken form, language, voice, and pronunciation boundaries distinct. | Introduce a TES-owned spoken-rendering boundary. Acronym rendering must reach TTS text, not remain only a hint. |
| `Lingua` and fastText | Language detection confidence is input-length sensitive and model/data redistribution needs explicit review. | Keep default-language selection deterministic. Mark mixed-language detection and translation as degraded unless a local provider is later certified. |
| `Argos Translate` | Offline translation has package indexes, downloaded artifacts, installed language pairs, cache invalidation, and possible pivot paths. | Translation cache remains optional and future-scoped. CAP-001 must not download packages, certify language pairs, or persist conversion caches. |
| `ftfy`, `Babel`, `humanize`, `num2words`, `dateparser` | Cleanup, locale, number, and date behavior works when it is narrow, fixture-backed, and explicit about unsupported ambiguity. | Defer numbers/dates beyond existing cleanup. Future cuts should use small golden fixtures and leave ambiguous input unchanged. |
| `phonemizer` and `eSpeak NG` | Phoneme, IPA, separator, backend, and CLI/library modes are separate provider capabilities with license/runtime risks. | Keep IPA, SSML, phoneme, lexicon, and provider-backed pronunciation blocked until a later provider-boundary SPEC certifies them. |

The strongest common architecture is:

```text
source_text -> protected/redacted spans -> classified speech spans ->
spoken_rendering -> TTS provider
```

The source text remains unchanged. `spoken_rendering` is the request-local text
sent to TTS.

## Viability Matrix

| Capability | Source | Decision | Reason |
|------------|--------|----------|--------|
| Reactive read-aloud workflow | `tes-tts` | keep | Already correct and validated; remains the product center. |
| Provider order `google -> openai -> elevenlabs -> say` | `speak` | keep as reference | Useful fallback knowledge; no install, config write, or certification. |
| Error classification | `speak` | migrate lightly | Portable as request-local behavior: auth, quota, unavailable provider, voice rejection, generic failure. |
| Voice policy | `speak`, live test | migrate lightly | Respect explicit voice, prefer local/default, keep `Felipe (Enhanced)` at `225` as tested preference when accepted. |
| Voice pools | `speak` JSON | reject for now | Auto-assignment and project voices belong to proactive `speak`, not reactive `tes-tts`. |
| Proactive announcements | `speak` | reject | Violates ADR 0004 and the `tes-tts` reactive contract. |
| `.claude/tts-config.json` and global provider state | `speak` | reject | Would create side effects and persistence outside the read-aloud request. |
| Summary-oriented 15-30 second target | `speak` | reject | `tes-tts` must not summarize user text unless asked. |
| Markdown cleanup | both | migrate/refine | Already present, but needs stronger spoken rendering for paths and links. |
| Acronym spoken rendering | live test, fixtures, `gruut`, NeMo | migrate first | `ADR`, `MCP`, `API`, `SDK`, and `CLI` need emitted speech like separate letters, not only metadata hints. |
| Path spoken rendering | live test, `Recognizers-Text` span model | migrate first | Non-exact reads should say the useful folder/file intent, e.g. "na pasta tes tts" for `.agents/skills/tes-tts`. |
| URL spoken rendering | live test, `speak`, `Recognizers-Text` URL lessons | migrate first | Non-exact reads should say the destination class, e.g. "na pagina do GitHub", not the raw URL. |
| Exact-read guard | live test, `Recognizers-Text` false-positive posture | migrate first | If the user asks for verbatim/exact reading, preserve raw paths, URLs, hashes, commands, and code-like spans. |
| Spoken-rendering field | NeMo, `gruut`, existing oracle gap | migrate first | CAP-001 needs a separate `spoken_text` or equivalent request-local field so source text and metadata do not carry conflicting duties. |
| Optional cleanup/detection libraries | prior research, provider review | defer | `ftfy`, `Babel`, and `Lingua` remain optional probe candidates; CAP-001 does not need new dependencies. |
| Broad language ID model | prior research | defer | fastText `lid.176.ftz` is attractive but model licensing and redistribution need separate owner review. |
| Offline translation | prior research | defer | Argos Translate is a future optional candidate, but language packages and model lifecycle are outside CAP-001. |
| Translation/G2P/IPA/SSML/phoneme output | provider review | defer | Requires separate fixtures, provider probes, local availability, and license evidence. |

## Implementation Feasibility

CAP-001 is feasible without new libraries.

The smallest valuable cut is a deterministic speech-shape layer for text that
already reaches TTS:

- acronym and technical-term spoken rendering as emitted speech text;
- path and URL spoken rendering for non-exact read requests;
- exact-read detection that preserves raw technical spans when requested;
- request-local `spoken_text` or equivalent derived field;
- no-summary preservation for user text;
- fixture coverage before changing behavior;
- workbench-first edits in `.agents/skills/tes-tts`;
- mirror to `src/adapters/codex/skills/tes-tts` after validation.

This should not attempt real translation, provider-backed pronunciation,
phoneme output, IPA, SSML, voice-pool assignment, or global provider memory.
It should also not add Lingua, fastText, Argos, ftfy, Babel, NeMo, gruut,
phonemizer, or eSpeak as runtime dependencies.

## Proposed CAP-001 Cut

1. Add or update fixtures for:
   - `ADR` -> spoken as separate letters;
   - `MCP`, `API`, `SDK`, and `CLI` -> spoken as separate letters;
   - `.agents/skills/tes-tts` -> spoken as a useful folder reference when exact
     reading was not requested;
   - `https://github.com/murillodutt/tilly-engineer-skills` -> spoken as a
     GitHub page reference when exact reading was not requested;
   - exact-reading opt-out that preserves raw path or URL when requested;
   - false positives such as time-like `7.am` and non-URL dotted tokens.
2. Update the instruction normalizer oracle so pronunciation hints can be
   converted into speech text, not only cache metadata. The oracle should
   prove that `speech_text` differs from source only through approved
   request-local spoken rendering and redaction.
3. Update `.agents/skills/tes-tts/references/language-normalization.md` and
   `providers-and-fallbacks.md` with the refined spoken-rendering rules.
4. Validate the workbench skill.
5. Mirror converged content to the canonical Codex adapter and then to Claude
   if package parity is required for the cut.

## CAP-001 Acceptance Checks

CAP-001 is ready to implement when the next execution can prove all of these:

- source text is never mutated or written as a durable cache;
- secret-like content is redacted before any spoken rendering;
- protected technical terms are preserved as terms but rendered naturally for
  speech when safe;
- `ADR` is spoken as separate letters in non-exact mode;
- `.agents/skills/tes-tts` is spoken as a useful folder reference in non-exact
  mode;
- GitHub URLs are spoken as GitHub page references in non-exact mode;
- exact/verbatim requests preserve raw paths and URLs;
- no summary behavior enters `tes-tts`;
- no provider install, provider download, model bundle, phoneme output, IPA,
  SSML, global config write, proactive `speak` behavior, or durable conversion
  cache is introduced.

## Risks

| Risk | Mitigation |
|------|------------|
| Over-interpreting paths or URLs. | Use exact reading when the user asks for verbatim text. |
| Hiding information the user wanted to hear. | Apply semantic path/URL rendering only for normal read-aloud, not explicit exact reads. |
| Reintroducing `speak` summary behavior. | Keep no-summary fixture checks mandatory. |
| False provider claim. | Keep all provider-backed behavior degraded/deferred until probes certify it. |
| Workbench/canonical drift. | Validate `.agents/skills/tes-tts` first, then diff/mirror to `src/adapters/codex/skills/tes-tts`. |

## Decision

Proceed to CAP-001 with the deterministic speech-shape layer as the first
migration cut.

Do not migrate provider persistence, proactive announcements, voice-pool
assignment, summary targets, or heavy language/pronunciation libraries in
CAP-001.
