---
tds_id: roadmap.goal_prompt_tes_tts_opw_001_controlled_prosody_warmup_runtime_option
tds_class: roadmap
status: active
consumer: maintainers, tes-tts maintainers, adapter authors, validation authors, and execution agents
source_of_truth: false
evidence_level: L2
---

# GOAL Prompt: TES TTS OPW-001 Controlled Prosody Warmup Runtime Option

```text
/goal Continue TES TTS OmniVoice prosody warmup.

Canonical artifact:
docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-tes-tts-omnivoice-prosody-warmup.md

Current unit:
OPW-001 Controlled Prosody Warmup Runtime Option

Certified evidence from prior cycle:
- Direct OmniVoice global runtime is active at
  ~/.tes/runtime/tes-tts/omnivoice.
- The active voice profile is tes-tts-local-clone using
  audio-modelo-clone-mono24k.wav.
- Maintainer-ranked A/B evidence found tag-only prosody better than
  CMU-heavy output:
  - omnivoice-control-factorial-20260531-203137/03-tag-only.wav beat
    04-cmu-plus-tag.wav after five comparisons.
  - omnivoice-light-tag-warmup-20260531-204008 first tier:
    03-confirmation-en.wav, 04-question-en.wav, 02-sigh.wav.
  - second tier: 05-natural-warmup.wav, 01-no-tag.wav.
- CMU remains experimental and is not approved as default product behavior.
- Release, sync, provider install, provider download, provider certification,
  global config writes, server route promotion, committed audio/cache/model/venv,
  durable conversion cache, and proactive speak remain unauthorized.

Task:
Execute only OPW-001 through:
execute -> analyze -> fix -> certify -> generate comparison WAV evidence ->
local commit.

Required actions:
1. Run git status --short --branch --untracked-files=all.
2. Classify inherited TTS changes and unrelated .agents/** drift. Do not stage
   or modify unrelated .agents/** changes.
3. Re-read:
   - docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-tes-tts-omnivoice-prosody-warmup.md
   - docs/roadmap/tes-tts/TES-TTS-SKILL-ROADMAP.md
   - docs/install/TES-TTS-OMNIVOICE.md
   - .agents/skills/tes-tts/**
   - src/adapters/codex/skills/tes-tts/**
   - src/adapters/claude/skills/tes-tts/**
   - scripts/tes_tts_omnivoice_provider.py
   - scripts/tes_tts_omnivoice_direct_kernel.py
   - scripts/tes_tts_runtime_adapter.py
   - scripts/tes_tts_omnivoice_provider_oracle.py
4. Implement OPW-001 only:
   - add a controlled OmniVoice prosody warmup option on the direct provider
     path;
   - whitelist only none, confirmation-en, question-en, and sigh;
   - add tags only to request-local provider text;
   - keep faithful, exact, raw, literal, quoted user text, code, and command
     reads tag-free unless the user explicitly requested a tag experiment;
   - keep CMU out of the default product path;
   - preserve source immutability, secret redaction, no-summary behavior,
     exact islands, code no-execute posture, global runtime defaults, and
     protected voice prompt cache permissions.
5. Analyze the diff for provider-tag injection risk, faithful-reading drift,
   privacy, adapter parity, audio quality evidence, latency impact, and line
   fidelity.
6. Fix only observed OPW-001 defects.
7. Certify with the smallest relevant set:
   - python3 -m compileall -q scripts/tes_tts_omnivoice_provider.py scripts/tes_tts_omnivoice_direct_kernel.py scripts/tes_tts_runtime_adapter.py scripts/tes_tts_omnivoice_provider_oracle.py
   - python3 scripts/tes_tts_omnivoice_provider_oracle.py --self-test
   - focused oracle or dry-run proving prosody warmup insertion and tag-free
     faithful/raw behavior
   - python3 /Users/murillo/.codex/skills/.system/skill-creator/scripts/quick_validate.py .agents/skills/tes-tts
   - python3 /Users/murillo/.codex/skills/.system/skill-creator/scripts/quick_validate.py src/adapters/codex/skills/tes-tts
   - python3 /Users/murillo/.codex/skills/.system/skill-creator/scripts/quick_validate.py src/adapters/claude/skills/tes-tts
   - python3 scripts/materialize_adapter.py all --check
   - python3 scripts/validate_tds.py
   - python3 scripts/validate_doc_size.py
   - python3 scripts/validate_reference_graph.py
   - git diff --check
8. Generate local comparison WAVs only under ~/.tes/runtime/** or tmp/**:
   - baseline no warmup;
   - confirmation-en;
   - question-en;
   - sigh.
9. Update docs/roadmap/tes-tts/TES-TTS-SKILL-ROADMAP.md with OPW-001 outcome,
   human-evidence pointer, active warmup posture, and sync status.
10. Stage only OPW-001 files and commit locally as the final shell action.

Forbidden:
- no sync, release, push, tag, publish;
- no provider install or provider download;
- no committed audio, cache, model artifact, or venv;
- no global config writes;
- no server route promotion;
- no proactive speak behavior;
- no durable text conversion cache;
- no command execution from spoken content;
- no user-text summary without explicit request;
- no non-whitelisted provider tag;
- no default CMU catalog;
- no unrelated .agents/** changes without explicit current-cycle approval.

Stop states:
PASS, DEGRADED, QUALITY_REGRESSION, PERFORMANCE_REGRESSION, NEEDS_REVIEW,
SAFETY_BLOCKED, BLOCKED.

Required closeout:
- changed files;
- prosody warmup option and default posture;
- focused oracles and result;
- local comparison WAV paths;
- local commit hash;
- sync status: REMOTE_SYNC_NOT_REQUESTED unless explicitly authorized.
```
