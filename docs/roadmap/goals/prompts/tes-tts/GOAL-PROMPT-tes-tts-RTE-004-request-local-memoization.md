---
tds_id: roadmap.goal_prompt_tes_tts_rte_004_request_local_memoization
tds_class: roadmap
status: archived
consumer: maintainers, tes-tts maintainers, adapter authors, validation authors, and execution agents
source_of_truth: false
evidence_level: L2
---

# GOAL Prompt: TES TTS RTE-004 Request-Local Memoization

```text
/goal Continue TES TTS lexical runtime engine and latency reduction.

Canonical artifact:
docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-tes-tts-lexical-runtime-engine-latency-reduction.md

Current unit:
RTE-004 Request-Local Memoization

Certified evidence from prior cycle:
- RTE-000 added latency fixtures and `scripts/tes_tts_runtime_latency_oracle.py`.
- RTE-001 added compiled lexical index fixtures and oracle.
- RTE-002 added hot-path span matcher fixtures and oracle.
- RTE-003 added fast-path spoken rendering fixtures and oracle.
- RTE-003 proved simple PT-BR prose and mixed technical prose can render
  dependency-free through matcher/index contracts while preserving source
  immutability, redaction, protected terms, exact islands, no-summary behavior,
  code no-execute posture, provider timing `out_of_scope`, and no runtime IPA,
  phoneme, SSML, or PLS output.
- Runtime IPA, phoneme, SSML, PLS, provider lexicon, G2P, provider-backed
  pronunciation, release, sync, full dictionary vendoring, provider install,
  durable conversion cache, and proactive `speak` remain unauthorized.
- Sync status is REMOTE_SYNC_NOT_REQUESTED.

Task:
Execute only RTE-004 through:
execute -> analyze -> fix -> certify -> create next /goal prompt -> local
commit.

Required actions:
1. Run `git status --short --branch --untracked-files=all`.
2. Re-read the RTE Super SPEC, RTE-000 through RTE-003 fixtures/oracles, and
   focused `tes-tts` sources.
3. Add dependency-free request-local memoization fixtures/oracle over the
   fast-path renderer.
4. Prove repeated protected terms, paths, URLs, and code-like spans are
   resolved once per request where safe, with no cross-request persistence.
5. Preserve source immutability, request-local `spoken_text`, secret redaction,
   exact islands, no-summary behavior, code no-execute posture, provider timing
   `out_of_scope`, and no runtime IPA/phoneme/SSML/PLS output.
6. Do not introduce provider calls, durable cache, global config writes,
   release/sync behavior, or production runtime optimization beyond the
   memoization contract.
7. Certify with the new memoization oracle, fast-path oracle, matcher oracle,
   compiled index oracle, runtime latency oracle, lexical/focused TTS oracles,
   materialization, TDS/doc-size/reference graph validators, `git diff --check`,
   and package closure when interpretable.
8. Create the next exact RTE `/goal` prompt before closure.
9. Update `docs/roadmap/tes-tts/TES-TTS-SKILL-ROADMAP.md` with RTE-004 outcome, next
   prompt pointer, and sync status.
10. Stage only RTE-004 files and commit locally as the final shell action.

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
