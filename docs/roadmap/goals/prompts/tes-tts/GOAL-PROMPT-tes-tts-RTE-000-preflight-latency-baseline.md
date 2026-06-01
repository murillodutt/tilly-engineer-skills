---
tds_id: roadmap.goal_prompt_tes_tts_rte_000_preflight_latency_baseline
tds_class: roadmap
status: archived
consumer: maintainers, tes-tts maintainers, adapter authors, validation authors, and execution agents
source_of_truth: false
evidence_level: L2
---

# GOAL Prompt: TES TTS RTE-000 Preflight And Latency Baseline

```text
/goal Continue TES TTS lexical runtime engine and latency reduction.

Canonical artifact:
docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-tes-tts-lexical-runtime-engine-latency-reduction.md

Current unit:
RTE-000 Preflight And Latency Baseline

Certified evidence from prior cycle:
- ADR 0004 is active as the pronunciation normalization and enrichment
  boundary.
- CAP-006 through CAP-009 improved conversational rendering, exact islands,
  structural oralization, and protected English identity.
- LEX-001 through LEX-005 closed the PT-BR lexical foundation locally for
  evidence-only schema, lookup, integration boundary, catalog migration, and
  final audit.
- Live usage identified latency as a serious adoption risk.
- JSON/JSONL remains the canonical TES lexicon format; PLS, SSML, IPA,
  phoneme, provider lexicon, and G2P are not authorized runtime outputs.
- Release identity, sync, provider installs, provider downloads, provider
  certification, durable conversion cache, global config writes, version bump,
  and proactive `speak` behavior remain unauthorized.
- Sync status is REMOTE_SYNC_NOT_REQUESTED.

Task:
Execute only RTE-000 through:
execute -> analyze -> fix -> certify -> create next /goal prompt -> local
commit.

Required actions:
1. Run `git status --short --branch --untracked-files=all`.
2. Classify inherited TTS changes and unrelated `.agents/**` drift. Do not
   stage or modify unrelated `.agents/**` changes.
3. Re-read:
   - `docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-tes-tts-lexical-runtime-engine-latency-reduction.md`
   - `docs/roadmap/tes-tts/TES-TTS-LEX-005-PTBR-LEXICAL-FINAL-AUDIT.md`
   - `docs/roadmap/tes-tts/TES-TTS-SKILL-ROADMAP.md`
   - `benchmarks/tes-tts/**`
   - `scripts/tes_tts_*_oracle.py`
   - `.agents/skills/tes-tts/**`
   - `src/adapters/codex/skills/tes-tts/**`
   - `src/adapters/claude/skills/tes-tts/**`
4. Execute RTE-000 only:
   - define latency fixtures for simple PT-BR prose, mixed technical prose,
     repeated protected terms, paths, URLs, code-like spans, and secret-like
     spans;
   - add a dependency-free runtime latency oracle that measures TES text
     preparation separately from provider/playback latency;
   - report deterministic metrics without provider-backed timing claims;
   - preserve source immutability, request-local `spoken_text`, secret
     redaction, exact islands, code no-execute posture, and no-summary
     behavior;
   - do not optimize runtime behavior yet.
5. Analyze the diff for metric usefulness, false-green risk, privacy,
   adapter parity, no-summary behavior, release/sync boundary drift, and
   performance evidence quality.
6. Fix only observed RTE-000 defects.
7. Certify with:
   - the new runtime latency oracle;
   - lexical oracles;
   - focused TTS oracles;
   - workbench/adapter quick validation when skill docs change;
   - materialization check;
   - TDS/doc-size/reference graph validators;
   - `git diff --check`;
   - package closure only when unrelated drift does not make it impossible to
     interpret.
8. Create the next exact RTE `/goal` prompt for RTE-001 Compiled Lexical Index
   Contract before closure.
9. Update `docs/roadmap/tes-tts/TES-TTS-SKILL-ROADMAP.md` with RTE-000 outcome, next
   prompt pointer, and sync status.
10. Stage only RTE-000 files and commit locally as the final shell action.

Forbidden:
- no sync, release, push, tag, publish, provider install, provider download,
  provider certification, proactive speak behavior, global config writes,
  durable conversion cache, version bump, bundle generation, full dictionary
  vendoring, runtime dependency import, command execution from spoken content,
  user-text summary without explicit request, IPA/phoneme/SSML/PLS runtime
  output, provider-backed pronunciation claim, G2P claim, or unrelated
  `.agents/**` changes without explicit current-cycle owner approval.

Stop states:
PASS, DEGRADED, PERFORMANCE_REGRESSION, NEEDS_REVIEW, NEEDS_OWNER_DECISION,
SAFETY_BLOCKED, BLOCKED.

Required closeout:
- changed files;
- focused oracles and result;
- next prompt artifact;
- local commit hash;
- sync status: REMOTE_SYNC_NOT_REQUESTED unless explicitly authorized.
```
