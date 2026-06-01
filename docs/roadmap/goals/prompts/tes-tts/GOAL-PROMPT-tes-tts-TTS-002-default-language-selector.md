---
tds_id: roadmap.goal_prompt_tes_tts_tts_002_default_language_selector
tds_class: roadmap
status: active
consumer: maintainers, tes-tts maintainers, execution agents, and release reviewers
source_of_truth: false
evidence_level: L2
---

# GOAL Prompt: TES TTS TTS-002 Default-Language Selector

This is the ready `/goal` prompt for the next circular execution cycle of
`tes-tts`.

```text
/goal Continue TES TTS sequential convergence.

Canonical artifact:
docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-tes-tts-sequential-convergence.md

Current unit:
TTS-002 Default-Language Selector

Certified evidence from prior cycle:
- TTS-001 re-read roadmap, ADR 0004, architecture SPEC, execution SPEC, and
  Codex/Claude language-normalization references.
- TTS-001 searched for contradiction classes:
  - adapter default priority versus explicit user language;
  - proactive `speak` behavior leaking into `tes-tts`;
  - provider install/download claims;
  - durable conversion cache claims;
  - sync/release permission claims.
- TTS-001 fixed one coherence defect: protected-term extraction now occurs
  before language detection in the architecture SPEC.
- TTS-001 confirmed Codex and Claude language-normalization references match.
- Ready prompt artifact for TTS-002 exists at
  docs/roadmap/goals/prompts/tes-tts/GOAL-PROMPT-tes-tts-TTS-002-default-language-selector.md.
- Focused TTS-001 oracles passed:
  - `python3 scripts/validate_tds.py`
  - `python3 scripts/validate_doc_size.py`
  - `python3 scripts/validate_reference_graph.py`
  - `python3 scripts/validate_reference_package.py`
  - targeted `rg` contradiction checks.
- TTS-001 final local commit is the commit that introduced this prompt
  artifact; confirm with `git log -1 --oneline`.

Task:
Execute only TTS-002 through the circular sequence:
execute -> analyze -> fix -> certify -> create next /goal prompt -> local commit.

Required actions:
1. Run `git status --short --branch --untracked-files=all`.
2. Re-read:
   - `src/adapters/codex/skills/tes-tts/references/language-normalization.md`
   - `src/adapters/claude/skills/tes-tts/references/language-normalization.md`
   - `docs/roadmap/tes-tts/TES-TTS-NORMALIZATION-ARCHITECTURE-SPEC.md`
   - `docs/roadmap/tes-tts/TES-TTS-NORMALIZATION-EXECUTION-SPEC.md`
   - `docs/roadmap/tes-tts/TES-TTS-SKILL-ROADMAP.md`
3. Verify the selector is precise and fixture-ready:
   - explicit user language wins;
   - declared adapter default is second and only when explicit;
   - request language is third;
   - dominant text language is fourth;
   - unclear input preserves original language.
4. Fix only TTS-002 selector defects or fixture-readiness gaps.
5. Certify with targeted `rg` checks and the smallest docs/package oracles.
6. Create the next `/goal` prompt artifact for TTS-003 if TTS-002 is not the
   convergence endpoint.
7. Commit the local execution as the final action of the cycle.

Forbidden:
- no sync, release, push, tag, publish, provider install, provider download,
  proactive speak behavior, global config writes, or durable conversion cache.

Stop states:
BLOCKED, DEGRADED, NEEDS_REVIEW, NEEDS_OWNER_DECISION.
```
