---
tds_id: roadmap.goal_prompt_tes_tts_tts_001_roadmap_and_spec_coherence
tds_class: roadmap
status: active
consumer: maintainers, tes-tts maintainers, execution agents, and release reviewers
source_of_truth: false
evidence_level: L2
---

# GOAL Prompt: TES TTS TTS-001 Roadmap And SPEC Coherence

This is the ready `/goal` prompt for the next circular execution cycle of
`tes-tts`.

```text
/goal Continue TES TTS sequential convergence.

Canonical artifact:
docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-tes-tts-sequential-convergence.md

Current unit:
TTS-001 Roadmap And SPEC Coherence

Certified evidence from prior cycle:
- TTS-000 preflight confirmed `main` is ahead only by local commits.
- No sync, release, push, tag, publish, provider install, provider download,
  proactive speak behavior, global config writes, or durable conversion cache
  was authorized.
- Super SPEC and roadmap were re-read during TTS-000.
- Next unresolved unit was classified as TTS-001.
- Ready prompt artifact for TTS-001 exists at
  docs/roadmap/goals/prompts/tes-tts/GOAL-PROMPT-tes-tts-TTS-001-roadmap-and-spec-coherence.md.
- Focused TTS-000 oracles passed:
  - `python3 scripts/validate_tds.py`
  - `python3 scripts/validate_doc_size.py`
  - `python3 scripts/validate_reference_graph.py`
  - `python3 scripts/validate_reference_package.py`
- TTS-000 final local commit is the commit that introduced this prompt
  artifact; confirm with `git log -1 --oneline`.

Task:
Execute only TTS-001 through the circular sequence:
execute -> analyze -> fix -> certify -> create next /goal prompt -> local commit.

Required actions:
1. Run `git status --short --branch --untracked-files=all`.
2. Re-read:
   - `docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-tes-tts-sequential-convergence.md`
   - `docs/roadmap/tes-tts/TES-TTS-SKILL-ROADMAP.md`
   - `docs/adr/0004-tes-tts-pronunciation-normalization-and-enrichment.md`
   - `docs/roadmap/tes-tts/TES-TTS-NORMALIZATION-ARCHITECTURE-SPEC.md`
   - `docs/roadmap/tes-tts/TES-TTS-NORMALIZATION-EXECUTION-SPEC.md`
   - `src/adapters/codex/skills/tes-tts/references/language-normalization.md`
   - `src/adapters/claude/skills/tes-tts/references/language-normalization.md`
3. Search for contradictions across roadmap, ADR, SPECs, and references:
   - adapter default priority versus explicit user language;
   - proactive `speak` behavior leaking into `tes-tts`;
   - provider install/download claims;
   - durable conversion cache claims;
   - sync/release permission claims.
4. Fix only coherence defects found in TTS-001 scope.
5. Certify with:
   - `python3 scripts/validate_tds.py`
   - `python3 scripts/validate_doc_size.py`
   - targeted `rg` checks for the contradiction classes above.
6. Create the next `/goal` prompt artifact for TTS-002 if TTS-001 is not the
   convergence endpoint.
7. Commit the local execution as the final action of the cycle.

Forbidden:
- no sync, release, push, tag, publish, provider install, provider download,
  proactive speak behavior, global config writes, or durable conversion cache.

Stop states:
BLOCKED, DEGRADED, NEEDS_REVIEW, NEEDS_OWNER_DECISION.
```
