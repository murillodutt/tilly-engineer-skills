---
tds_id: roadmap.goal_prompt_tes_tts_rte_003_fast_path_spoken_rendering
tds_class: roadmap
status: archived
consumer: maintainers, tes-tts maintainers, adapter authors, validation authors, and execution agents
source_of_truth: false
evidence_level: L2
---

# GOAL Prompt: TES TTS RTE-003 Fast-Path Spoken Rendering

```text
/goal Continue TES TTS lexical runtime engine and latency reduction.

Canonical artifact:
docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-tes-tts-lexical-runtime-engine-latency-reduction.md

Current unit:
RTE-003 Fast-Path Spoken Rendering

Certified evidence from prior cycle:
- RTE-000 added latency fixtures and `scripts/tes_tts_runtime_latency_oracle.py`.
- RTE-001 added compiled lexical index fixtures and oracle.
- RTE-002 added `benchmarks/tes-tts/hot-path-span-matcher-fixtures.json`.
- RTE-002 added `scripts/tes_tts_hot_path_span_matcher_oracle.py`.
- RTE-002 proved redaction-first matching, longest protected phrase wins,
  exact islands stay scoped, fragile spans are classified, code is never
  executable, source text remains immutable, and provider timing remains
  `out_of_scope`.
- Runtime IPA, phoneme, SSML, PLS, provider lexicon, G2P, provider-backed
  pronunciation, release, sync, full dictionary vendoring, provider install,
  and proactive `speak` remain unauthorized.
- Sync status is REMOTE_SYNC_NOT_REQUESTED.

Task:
Execute only RTE-003 through:
execute -> analyze -> fix -> certify -> create next /goal prompt -> local
commit.

Required actions:
1. Run `git status --short --branch --untracked-files=all`.
2. Re-read the RTE Super SPEC, RTE-000 through RTE-002 fixtures/oracles, and
   focused `tes-tts` sources.
3. Add dependency-free fast-path spoken-rendering fixtures/oracle for simple
   PT-BR prose and mixed technical prose using the compiled index and span
   matcher contracts.
4. Prove the fast path preserves source immutability, redaction, protected
   terms, exact islands, no-summary behavior, code no-execute posture,
   provider timing `out_of_scope`, and no runtime IPA/phoneme/SSML/PLS output.
5. Do not introduce provider calls, durable cache, release/sync behavior, or
   production runtime optimization beyond the fast-path contract.
6. Certify with the new fast-path oracle, matcher oracle, compiled index
   oracle, runtime latency oracle, lexical/focused TTS oracles, materialization,
   TDS/doc-size/reference graph validators, `git diff --check`, and package
   closure when interpretable.
7. Create the next exact RTE `/goal` prompt before closure.
8. Update `docs/roadmap/tes-tts/TES-TTS-SKILL-ROADMAP.md` with RTE-003 outcome, next
   prompt pointer, and sync status.
9. Stage only RTE-003 files and commit locally as the final shell action.

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
