---
tds_id: roadmap.goal_prompt_tes_tts_rte_006_runtime_audit_and_closure
tds_class: roadmap
status: active
consumer: maintainers, tes-tts maintainers, adapter authors, validation authors, and execution agents
source_of_truth: false
evidence_level: L2
---

# GOAL Prompt: TES TTS RTE-006 Runtime Audit And Closure

```text
/goal Continue TES TTS lexical runtime engine and latency reduction.

Canonical artifact:
docs/roadmap/GOAL-SUPER-SPEC-tes-tts-lexical-runtime-engine-latency-reduction.md

Current unit:
RTE-006 Runtime Audit And Closure

Certified evidence from prior cycle:
- RTE-000 added latency fixtures and `scripts/tes_tts_runtime_latency_oracle.py`.
- RTE-001 added compiled lexical index fixtures and oracle.
- RTE-002 added hot-path span matcher fixtures and oracle.
- RTE-003 added fast-path spoken rendering fixtures and oracle.
- RTE-004 added request-local memoization fixtures and oracle.
- RTE-005 added chunked preparation fixtures and oracle.
- RTE-005 proved the first speakable chunk can be prepared quickly while later
  chunks stay request-local, ordered, redacted, and non-executable.
- Source immutability, request-local `spoken_text`, secret redaction, exact
  islands, no-summary behavior, provider timing `out_of_scope`, and no runtime
  IPA/phoneme/SSML/PLS output remain preserved.
- Runtime IPA, phoneme, SSML, PLS, provider lexicon, G2P, provider-backed
  pronunciation, release, sync, full dictionary vendoring, provider install,
  durable conversion cache, and proactive `speak` remain unauthorized.
- Sync status is REMOTE_SYNC_NOT_REQUESTED.

Task:
Execute only RTE-006 through:
execute -> analyze -> fix -> certify -> close convergence or create exact next
/goal prompt -> local commit.

Required actions:
1. Run `git status --short --branch --untracked-files=all`.
2. Re-read the RTE Super SPEC, RTE-000 through RTE-005 fixtures/oracles, and
   focused `tes-tts` sources.
3. Audit the runtime latency line end to end: baseline, compiled index,
   matcher, fast-path rendering, request-local memoization, and chunked
   preparation.
4. Confirm what is complete, degraded, deferred, and unauthorized.
5. Confirm no source mutation, no user-text summary, no command execution, no
   secret leak, no provider timing claim, no durable cache, and no runtime IPA,
   phoneme, SSML, or PLS output.
6. Decide whether the runtime latency line closes locally or needs an exact
   follow-up prompt.
7. Certify with runtime, lexical, focused TTS, materialization,
   TDS/doc-size/reference graph validators, `git diff --check`, and package
   closure when interpretable.
8. Update `docs/roadmap/TES-TTS-SKILL-ROADMAP.md` with RTE-006 outcome,
   closure state or next prompt pointer, and sync status.
9. Stage only RTE-006 files and commit locally as the final shell action.

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
- next prompt artifact or closure statement;
- local commit hash;
- sync status: REMOTE_SYNC_NOT_REQUESTED unless explicitly authorized.
```
