---
tds_id: roadmap.goal_prompt_tes_tts_rte_002_hot_path_span_matcher
tds_class: roadmap
status: archived
consumer: maintainers, tes-tts maintainers, adapter authors, validation authors, and execution agents
source_of_truth: false
evidence_level: L2
---

# GOAL Prompt: TES TTS RTE-002 Hot-Path Span Matcher

```text
/goal Continue TES TTS lexical runtime engine and latency reduction.

Canonical artifact:
docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-tes-tts-lexical-runtime-engine-latency-reduction.md

Current unit:
RTE-002 Hot-Path Span Matcher

Certified evidence from prior cycle:
- RTE-000 added latency fixtures and `scripts/tes_tts_runtime_latency_oracle.py`.
- RTE-001 added `benchmarks/tes-tts/compiled-lexical-index-fixtures.json`.
- RTE-001 added `scripts/tes_tts_compiled_lexical_index_oracle.py`.
- RTE-001 proved deterministic exact, phrase, casefold, locale-boundary, and
  OOV/degraded lookup over governed fixture data.
- RTE-001 proved duplicate handling and priority ordering without runtime IPA,
  phoneme, SSML, PLS, provider lexicon, G2P, or provider-backed pronunciation
  output.
- Release identity, sync, provider installs, provider downloads, provider
  certification, durable conversion cache, global config writes, version bump,
  full dictionary vendoring, and proactive `speak` behavior remain
  unauthorized.
- Sync status is REMOTE_SYNC_NOT_REQUESTED.

Task:
Execute only RTE-002 through:
execute -> analyze -> fix -> certify -> create next /goal prompt -> local
commit.

Required actions:
1. Run `git status --short --branch --untracked-files=all`.
2. Re-read the RTE Super SPEC, RTE-000/RTE-001 fixtures and oracles, and
   focused `tes-tts` sources.
3. Add dependency-free hot-path span matcher fixtures/oracle for protected
   terms, paths, URLs, commands, code, hashes, and secrets.
4. Prove redaction wins before matching, longest protected phrase wins,
   exact islands stay scoped, source text remains immutable, code is never
   executed, and provider timing remains out of scope.
5. Do not optimize production runtime beyond the matcher contract in this
   unit.
6. Certify with the new matcher oracle, compiled index oracle, runtime latency
   oracle, lexical/focused TTS oracles, materialization, TDS/doc-size/reference
   graph validators, `git diff --check`, and package closure when
   interpretable.
7. Create the next exact RTE `/goal` prompt before closure.
8. Update `docs/roadmap/tes-tts/TES-TTS-SKILL-ROADMAP.md` with RTE-002 outcome, next
   prompt pointer, and sync status.
9. Stage only RTE-002 files and commit locally as the final shell action.

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
