---
tds_id: roadmap.goal_prompt_tes_tts_tts_000_preflight_and_baseline
tds_class: roadmap
status: active
consumer: maintainers, tes-tts maintainers, execution agents, and release reviewers
source_of_truth: false
evidence_level: L2
---

# GOAL Prompt: TES TTS TTS-000 Preflight And Baseline

This is the ready `/goal` prompt for the next circular execution cycle of
`tes-tts`.

```text
/goal Continue TES TTS sequential convergence.

Canonical artifact:
docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-tes-tts-sequential-convergence.md

Current unit:
TTS-000 Preflight And Baseline

Certified evidence from prior cycle:
- GOAL Super SPEC exists and is indexed.
- Circular contract includes execute -> analyze -> fix -> certify -> create
  next /goal prompt -> local commit.
- Ready prompt artifact exists at
  docs/roadmap/goals/prompts/tes-tts/GOAL-PROMPT-tes-tts-TTS-000-preflight-and-baseline.md.
- Latest local commits:
  - ff438e5 Add tes-tts skill and convergence roadmap.
  - 2c53adb Add ready goal prompt to tes-tts convergence spec.
- `npm run commit:check` passed before commit ff438e5.

Task:
Execute only TTS-000 through the circular sequence:
execute -> analyze -> fix -> certify -> create next /goal prompt -> local commit.

Required actions:
1. Run `git status --short --branch --untracked-files=all`.
2. Confirm the worktree is ahead only by local commits and no sync/release is
   authorized.
3. Re-read this Super SPEC and `docs/roadmap/tes-tts/TES-TTS-SKILL-ROADMAP.md`.
4. Classify the next unresolved unit after TTS-000.
5. If the preflight contract is coherent, certify with the smallest focused
   oracle and create the next `/goal` prompt artifact for TTS-001.
6. Commit the local execution as the final action of the cycle.

Forbidden:
- no sync, release, push, tag, publish, provider install, provider download,
  proactive speak behavior, global config writes, or durable conversion cache.

Stop states:
BLOCKED, DEGRADED, NEEDS_REVIEW, NEEDS_OWNER_DECISION.
```
