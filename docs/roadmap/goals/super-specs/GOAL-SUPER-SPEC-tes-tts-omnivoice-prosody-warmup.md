---
tds_id: roadmap.goal_super_spec_tes_tts_omnivoice_prosody_warmup
tds_class: roadmap
status: active
consumer: maintainers, tes-tts maintainers, adapter authors, validation authors, and execution agents
source_of_truth: false
evidence_level: L2
---

# GOAL Super SPEC: TES TTS OmniVoice Prosody Warmup

Status: active runtime-quality line.

Canonical artifact:
`docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-tes-tts-omnivoice-prosody-warmup.md`

Current execution unit:
`OPW-001 Controlled Prosody Warmup Runtime Option`

Ready prompt:
`docs/roadmap/goals/prompts/tes-tts/GOAL-PROMPT-tes-tts-OPW-001-controlled-prosody-warmup-runtime-option.md`

## Purpose

Promote a real audio finding into a small runtime feature: OmniVoice light
provider tags can improve fluency, cadence, and technical English clarity when
used as a controlled prosody warmup before conversational narration.

This line must improve generated audio, not create another documentation loop.
It exists because maintainer listening ranked tagged output above untagged and
CMU-heavy output.

## Evidence

Local A/B artifacts live under the user runtime and are not committed:

```text
~/.tes/runtime/tes-tts/omnivoice/provider-cache/audio-reference-runs/
```

Human ranking from `omnivoice-control-factorial-20260531-203137`:

- `03-tag-only.wav` beat `04-cmu-plus-tag.wav` after five comparisons.
- The winning signal was tag-only prosody, not CMU.

Human ranking from `omnivoice-light-tag-warmup-20260531-204008`:

- First tier: `03-confirmation-en.wav`, `04-question-en.wav`,
  `02-sigh.wav`.
- Second tier: `05-natural-warmup.wav`, `01-no-tag.wav`.

Measured synthesis cost was close across variants, so quality should decide.

## OPW-001 Contract

Implement a provider-text-only OmniVoice prosody warmup option with a short
whitelist:

```text
none
confirmation-en
question-en
sigh
```

Rules:

- Keep source text immutable.
- Add any tag only to request-local provider text.
- Never inject tags into faithful, exact, raw, literal, code, command, or user
  quoted reading unless the user explicitly asks for an OmniVoice tag test.
- Redact secrets before adding or sending provider text.
- Keep code and commands as text; never execute spoken content.
- Do not use CMU in the default product path.
- Do not claim non-whitelisted tags such as `[sniff]`, `[gasp]`, `singing`, or
  multi-speaker dialogue.
- Keep the current quality recipe and global runtime defaults.
- Generated WAVs stay under `~/.tes/runtime/**` or `tmp/**` and are never
  committed.

## Runtime Shape

```text
source text
-> redaction and request-local preparation
-> optional OmniVoice prosody warmup tag for conversational provider text
-> direct/resident OmniVoice synthesis
-> WAV review evidence
```

The feature should be explicit first, for example a provider flag or runtime
option. A later human-rated run may decide whether one tag becomes the default
for conversational narration. Faithful reading remains tag-free by default.

## Success

OPW-001 passes when:

- the option exists on the intended direct OmniVoice path;
- provider-tag insertion is request-local and test-covered;
- exact/faithful/raw/code paths do not receive surprise tags;
- the generated comparison WAVs show no regression in privacy or safety
  metadata;
- maintainer can compare baseline and whitelisted warmup output by file.

## Locks

No sync, release, push, tag, publish, provider install, provider download,
committed audio, committed cache, committed model artifact, committed venv,
global config write, proactive speak behavior, durable text conversion cache,
unbounded CMU catalog, non-whitelisted provider tag, or server route promotion
is authorized by this line.
