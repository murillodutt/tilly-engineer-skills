---
tds_id: roadmap.goal_prompt_tes_tts_cap_010_conversational_rendering_final_audit
tds_class: roadmap
status: archived
consumer: maintainers, tes-tts maintainers, adapter authors, validation authors, and execution agents
source_of_truth: false
evidence_level: L2
---

# GOAL Prompt: TES TTS CAP-010 Conversational Rendering Final Audit

Superseded by:
`docs/roadmap/GOAL-SUPER-SPEC-tes-tts-ptbr-lexical-normalization.md`

Reason: maintainer approved a PT-BR lexical normalization pivot before final
auditing the conversational-rendering line. This prompt is retained for
lineage, not active execution.

```text
/goal Continue TES TTS conversational rendering.

Canonical artifact:
docs/roadmap/GOAL-SUPER-SPEC-tes-tts-conversational-rendering.md

Current unit:
CAP-010 Conversational Rendering Final Audit

Certified evidence from prior cycle:
- CAP-009 hardened mixed-language and English identity handling.
- CAP-009 added fixtures for PT-BR narration with English workflow terms,
  degraded mixed-span translation planning, product/package/model identity,
  Hebrew degraded English identity, and structural rendering that preserves
  protected English terms.
- CAP-009 kept pronunciation as instruction-level intent only, without IPA,
  SSML, phoneme, lexicon, G2P, or provider-backed claims.
- CAP-009 kept source text unchanged, `spoken_text` request-local, no-summary
  behavior, exact islands, secret redaction, and CAP-008 structural oralization.
- CAP-009 mirrored converged behavior into Codex and Claude adapter skill
  sources.
- Release identity, sync, provider installs, provider downloads, provider
  certification, durable conversion cache, global config writes, version bump,
  and proactive `speak` behavior remain unauthorized.
- Sync status is REMOTE_SYNC_NOT_REQUESTED.

Task:
Execute only CAP-010 through:
execute -> analyze -> fix -> certify -> create next /goal prompt or close
convergence -> local commit.

Required actions:
1. Run `git status --short --branch --untracked-files=all`.
2. Classify inherited TTS changes and unrelated `.agents/**` drift. Do not
   stage or modify unrelated `.agents/**` changes.
3. Re-read:
   - `docs/roadmap/GOAL-SUPER-SPEC-tes-tts-conversational-rendering.md`
   - `docs/roadmap/TES-TTS-CAP-006-CONVERSATIONAL-SPOKEN-RENDERING.md`
   - `docs/roadmap/TES-TTS-CAP-007-EXACT-ISLAND-PROTECTED-SPAN-HARDENING.md`
   - `docs/roadmap/TES-TTS-CAP-008-TABLE-LIST-CODE-BLOCK-ORALIZATION.md`
   - `docs/roadmap/TES-TTS-CAP-009-MIXED-LANGUAGE-ENGLISH-IDENTITY-HARDENING.md`
   - `docs/roadmap/TES-TTS-SKILL-ROADMAP.md`
   - `.agents/skills/tes-tts/**`
   - `src/adapters/codex/skills/tes-tts/**`
   - `src/adapters/claude/skills/tes-tts/**`
   - focused TTS fixtures and oracles under `benchmarks/tes-tts/**` and
     `scripts/tes_tts_*_oracle.py`
4. Execute CAP-010 only:
   - audit CAP-006 through CAP-009 for adapter parity, no-summary behavior,
     exact islands, secret redaction, protected identity, code no-execute,
     provider posture, and no drift into proactive `speak`;
   - confirm whether the conversational rendering sequence is complete for
     the approved local scope or remains explicitly degraded/deferred;
   - keep release identity, sync, provider certification, version bump, bundle,
     tag, push, publish, and release out of scope unless explicitly authorized
     in the current cycle.
5. Analyze the diff for quality, efficiency, precision, false-green risk,
   adapter parity, privacy, boundary drift, and audit completeness.
6. Fix only observed CAP-010 defects.
7. Certify with focused TTS oracles, workbench and adapter quick validation,
   materialization check, TDS/doc-size/reference graph validators,
   `git diff --check`, and package closure only when unrelated drift does not
   make it impossible to interpret.
8. If the conversational rendering sequence is complete for the approved
   local scope, close convergence with a final audit record and no next prompt.
   If an unresolved decision remains, create the exact next `/goal` prompt.
9. Update `docs/roadmap/TES-TTS-SKILL-ROADMAP.md` with CAP-010 outcome,
   closure state, next prompt pointer or closure statement, and sync status.
10. Stage only CAP-010 files and commit locally as the final shell action.

Forbidden:
- no sync, release, push, tag, publish, provider install, provider download,
  provider certification, proactive speak behavior, global config writes,
  durable conversion cache, version bump, bundle generation, phoneme output,
  IPA, SSML, lexicon, G2P claim, model bundle, library vendoring, runtime
  dependency import, command execution from spoken content, user-text summary
  without explicit request, provider-backed pronunciation claim, or unrelated
  `.agents/**` changes without explicit current-cycle owner approval.

Stop states:
PASS, DEGRADED, TTS_NOT_AVAILABLE, NEEDS_REVIEW, NEEDS_OWNER_DECISION,
SAFETY_BLOCKED, BLOCKED.

Required closeout:
- changed files;
- focused oracles and result;
- next prompt artifact or closure statement;
- local commit hash;
- sync status: REMOTE_SYNC_NOT_REQUESTED unless explicitly authorized.
```
