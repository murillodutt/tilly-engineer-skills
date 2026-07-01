---
tds_id: roadmap.goal_super_spec_tes_codex_agent_memory_policy
tds_class: roadmap
status: active
consumer: maintainers, Cortex runtime authors, Git Tap authors, installer authors, host adapter authors, oracle authors, release reviewers, and execution agents
source_of_truth: true
evidence_level: L2
tver: 0.1.0
---

# GOAL-SUPER-SPEC: TES Codex Agent Memory Policy

Status: active product Super SPEC.

Purpose: add a project-local policy file at `.tes/tes-codex.md` so each target
project can decide which source material becomes agent memory, which material
remains documentation, which material requires review, and which material is
forbidden from Cortex curation.

This Super SPEC is intended to be executed inside the
`tes-host-transcript-canary` harness. Source-only gates can support a loop, but
they cannot close the product claim.

## Central Rule

```text
Humans own the policy. Agents operate the memory.
```

The Cortex memory lane is for LLM and agent runtime. Human approval must not be
required for every safe memory item after the project owner has declared a
policy. Human review is reserved for ambiguous, conflicting, sensitive,
private, destructive, release, or high-impact memory.

## Product Classification

This work is `Platform` once implemented. It changes delivered installer
behavior, local target configuration, Cortex curation, Git Tap integration,
host-runtime recall, evidence ledgers, and package identity.

Writing this Super SPEC does not deliver runtime behavior.

## Execution Harness Contract

All implementation loops for this Super SPEC must be routed through
`tes-host-transcript-canary`.

Required chain:

```text
frame host command -> run/fingerprint command -> resolve transcript JSONL ->
run sanitized transcript oracle -> classify failure -> patch TES source ->
replay same command -> run runtime signal audit when memory is claimed ->
run related TES gates -> run post-execution gate -> decide
```

Rules:

- use a clean installed target for product evidence;
- use `host_canary_loop.py` for command fingerprinting, stale transcript
  rejection, and same-command replay when practical;
- use `runtime_signal_audit.py` for runtime-memory claims;
- use `post_execution_gate.py` before any `PASS`, `CERTIFIED`, product
  convergence, or ceiling claim;
- keep raw transcript JSONL local and unstaged;
- retain only sanitized transcript hashes, event counts, safe tool names,
  command labels, command fingerprints, statuses, gates, and blockers;
- downgrade to `NEEDS_POLICY_HOST_CANARY`,
  `NEEDS_RUNTIME_SIGNAL_AUDIT`, or `NEEDS_POST_EXECUTION_GATE` when the harness
  cannot prove host-real runtime use;
- early parser or installer units may close as source-gated increments, but
  not as product memory convergence until the host-backed replay succeeds.

Minimum host-real acceptance:

- the host transcript is fresh and parseable;
- the transcript has user and assistant events;
- required tool-use evidence exists when the claim depends on tool execution;
- the runtime ledger connects the host session to policy-loaded recall;
- the first relevant mutation used injected Cortex context or an equivalent
  runtime signal;
- no forbidden manual memory lookup occurred before recall.

## Protected Baseline

Preserve these facts:

- Cortex Markdown remains durable memory truth unless a later ADR changes it.
- Derived indexes and SQLite are runtime acceleration, not canonical memory.
- Git hooks may capture, classify, queue, and propose memory, but must not write
  durable curated memory from inside hook execution.
- The Git Tap proposal loop remains safe when `.tes/tes-codex.md` is missing.
- Existing manual `apply-proposal --yes` behavior remains available as a hard
  fallback.
- Raw diffs, raw prompts, tool payloads, secrets, credentials, and unredacted
  host transcripts do not become memory.
- Host-specific contracts for Codex, Claude, and Cursor remain distinct.
- Runtime recall must be attempted before broad `docs/**` scanning when the
  policy requires recall-first execution.

## Design Decision

Use `.tes/tes-codex.md`: Markdown for owner-readable intent, one fenced TOML
block for the machine contract, and `tomllib`-compatible syntax for the parser.
The name starts with Codex because this controls Codex agent memory first; the
schema must stay host-neutral enough for Claude and Cursor adapters later.

## Required Policy Contract

The first schema is `tes-codex-policy@1`.

Example target file:

````markdown
# TES Codex Policy

This file declares how TES agents convert project material into agent memory.
Humans own this policy; agents operate within it.

```toml tes-codex-policy@1
schema = "tes-codex-policy@1"
runtime_recall_first = true
broad_scan_requires_recall_miss = true
default_action = "propose"
[auto_promote]
enabled = true
outside_hook_only = true
max_risk = "low"
write_targets = ["runtime_index", "cortex_cell"]
[review]
required_risks = ["medium", "high", "conflict", "private_identifier", "secret_like", "destructive", "release"]
[source_classes.agent_memory]
path_globs = ["docs/agents/**", "docs/adr/**", "docs/architecture/**", "docs/roadmap/goals/super-specs/**", "docs/mesh/**"]
action = "auto_promote"
risk_ceiling = "low"
[source_classes.documentation]
path_globs = ["README.md", "docs/install/**", "docs/index.html"]
action = "propose"
[source_classes.denied]
path_globs = [".env*", ".tes/runtime/**", "tmp/**"]
action = "deny"
```
````

Allowed actions: `auto_promote`, `propose`, `review_required`, `deny`, and
`ignore`. Allowed write targets: `runtime_index`, `cortex_cell`, and
`proposal_only`.

## Stop States

- `NEEDS_TES_CODEX_POLICY`
- `NEEDS_POLICY_PARSER`
- `NEEDS_POLICY_INSTALLER`
- `NEEDS_POLICY_GIT_TAP_INTEGRATION`
- `NEEDS_POLICY_RUNTIME_RECALL`
- `NEEDS_POLICY_PRIVACY_GUARD`
- `NEEDS_POLICY_HOST_CANARY`
- `NEEDS_RUNTIME_SIGNAL_AUDIT`
- `NEEDS_POST_EXECUTION_GATE`
- `PASS_TES_CODEX_AGENT_MEMORY_POLICY`

## SPEC-000 - Preflight And Contract Boundary

Objective: establish the cut line before runtime changes.

Required evidence:

- classify current worktree state;
- verify whether `.tes/tes-codex.md` already exists in target fixtures;
- identify current Cortex proposal, Git Tap, runtime recall, and installer
  entrypoints;
- frame the `tes-host-transcript-canary` target, safe command label, expected
  transcript evidence, runtime marker, and stop condition;
- name release identity before delivered behavior changes;
- preserve the current Git Tap hook no-write invariant.

Allowed files:

- this Super SPEC;
- `docs/tds/DOCS-INDEX.yml`;
- `docs/INDEX.md` when needed for discoverability.

Forbidden in SPEC-000:

- runtime edits;
- installer edits;
- package version changes;
- bundle changes;
- installed target mutation;
- memory writes.

Oracles:

- `python3 scripts/validate_tds.py`;
- `python3 scripts/validate_doc_size.py`;
- `git diff --check`.

Harness state:

- planning-only may close without a host command;
- implementation must start by recording a host command fingerprint or an
  explicit `LIMITED_NON_HOST_CLAIM`.

Stop state: `NEEDS_TES_CODEX_POLICY`.

## SPEC-001 - Policy Parser And Validation

Objective: create a deterministic parser and validator for
`.tes/tes-codex.md`.

Required behavior:

- read exactly one fenced TOML block tagged `tes-codex-policy@1`;
- reject missing, duplicate, malformed, or unsupported policy blocks;
- validate allowed actions, allowed write targets, risk vocabulary, and glob
  classes;
- classify paths into `agent_memory`, `documentation`, `denied`, or
  `unclassified`;
- produce a JSON summary for oracles and runtime consumers;
- fail closed for malformed policy in write paths;
- fail open with `propose` behavior for read-only advisory paths when policy is
  missing.

Likely surfaces:

- `scripts/tes_codex_policy.py` or an equivalent source-owned helper;
- focused self-test fixtures;
- an architecture reference if the helper grows beyond inline code clarity.

Negative fixtures:

- duplicate policy block fails;
- `auto_promote` with `outside_hook_only=false` fails unless a later ADR
  authorizes hook writes;
- denied path cannot produce a memory write;
- secret-like source cannot be promoted;
- unclassified path uses `default_action`.

Harness requirement:

- source parser proof alone can close only the parser increment;
- no policy-runtime claim is allowed until the harness replay proves the parsed
  policy changed installed-target runtime behavior.

Stop state: `NEEDS_POLICY_PARSER`.

## SPEC-002 - Installer Materialization

Objective: materialize `.tes/tes-codex.md` in installed targets without
clobbering owner edits.

Required behavior:

- fresh install writes the default policy template;
- update preserves local edits;
- repair can add a missing policy file;
- uninstall removes only TES-owned generated policy when it was never edited, or
  leaves an owner-edited policy in place with a clear status;
- installed certification reports policy state:
  `MISSING`, `DEFAULT`, `OWNER_EDITED`, `INVALID`, or `STALE_SCHEMA`;
- package bundle includes the default policy template.

Protected behavior:

- no global host config mutation;
- no hidden opt-in to automatic durable memory writes;
- no private project-specific paths in the template.

Harness requirement:

- installed-target evidence must come from a clean target observed through the
  host-backed canary loop before installer behavior is claimed as product
  converged.

Stop state: `NEEDS_POLICY_INSTALLER`.

## SPEC-003 - Git Tap And Proposal Curation Integration

Objective: let Git Tap and proposal curation use the project policy without
turning hooks into memory writers.

Required behavior:

- Git Tap events include `policy_schema`, `policy_digest`, and
  `policy_decision` when policy is available;
- hook execution may capture and propose only;
- automatic promotion is blocked when `TES_CORTEX_GIT_TAP_HOOK=1`;
- non-hook curation may auto-promote low-risk memory when policy allows it;
- ambiguous, conflicting, private, or high-impact memory becomes
  `review_required`;
- `apply-proposal --yes` remains a manual override path;
- every auto-promotion writes an audit row with source path, content digest,
  policy digest, decision reason, risk, and rollback pointer.

Harness requirement:

- replay the same host command after patching Git Tap or curation behavior;
- classify hook-path auto-promotion as `BLOCKED_IN_HOOK`;
- prove outside-hook auto-promotion with transcript and runtime ledger evidence
  before claiming convergence.

Decision states:

- `AUTO_PROMOTED`
- `PROPOSED`
- `REVIEW_REQUIRED`
- `DENIED_BY_POLICY`
- `BLOCKED_IN_HOOK`
- `BLOCKED_PRIVACY`

Negative fixtures:

- hook-triggered auto-promotion fails;
- policy-denied path never enters proposal or memory;
- low-risk agent-memory path auto-promotes outside hook;
- conflict requires review even when path class says `auto_promote`;
- stale policy digest forces re-evaluation before write.

Stop state: `NEEDS_POLICY_GIT_TAP_INTEGRATION`.

## SPEC-004 - Runtime Recall First

Objective: make agent runtime use Cortex memory before broad documentation
scans when policy requires it.

Required behavior:

- host adapters load the policy status at session or pre-tool time;
- runtime recall runs before broad `docs/**` search when
  `runtime_recall_first=true`;
- broad scan is allowed after recall miss when
  `broad_scan_requires_recall_miss=true`;
- advisory context cites memory source, digest, confidence, and reason;
- ledger records `policy_loaded`, `recall_attempted`, `recall_hit`,
  `broad_scan_after_miss`, and `memory_source_digest`;
- missing policy degrades to current behavior without claiming policy-mode
  ceiling.

Acceptance:

- a prompt answerable from curated Cortex memory is solved from recall evidence;
- transcript evidence shows no broad `docs/**` scan before recall;
- if recall misses, the later scan is recorded as miss-driven, not default
  behavior.

Harness requirement:

- `runtime_signal_audit.py` must pass for runtime-memory claims;
- a transcript with manual `Read`, `Grep`, `Glob`, `LS`, or shell lookup
  against memory paths before injected recall is `false_green`.

Stop state: `NEEDS_POLICY_RUNTIME_RECALL`.

## SPEC-005 - Privacy, Safety, And Rollback

Objective: prevent policy-driven automation from becoming silent
contamination.

Required behavior:

- secret-like content, raw diffs, raw prompts, host transcripts, credentials,
  local absolute private paths, and private vocabulary are rejected before
  promotion;
- auto-promoted durable memory includes rollback metadata;
- policy digest is stored with every promotion decision;
- changed policy invalidates pending auto-promote decisions;
- curation can report what would be removed or demoted before rollback.

Required negative checks:

- private vocabulary oracle stays clean;
- raw diff in proposal fails;
- stale policy digest blocks promotion;
- rollback metadata is present for durable memory writes;
- documentation-only paths do not silently become agent memory.

Harness requirement:

- transcript evidence must remain sanitized;
- raw transcript lines, raw prompts, tool inputs, tool results, and subagent
  message content are forbidden in tracked reports.

Stop state: `NEEDS_POLICY_PRIVACY_GUARD`.

## SPEC-006 - Host Canary Certification

Objective: prove the contract through real host/runtime evidence, not only
source fixtures.

Required canary:

```text
clean target -> install TES bundle -> materialize .tes/tes-codex.md ->
seed safe agent-memory source -> run Git Tap/proposal curation outside hook ->
auto-promote by policy -> run host prompt -> inspect transcript ->
prove recall-first behavior -> inspect ledgers -> run installed certification
```

Harness:

- use `tes-host-transcript-canary` for host-backed runtime truth;
- execute through the host command loop, not a hand-built transcript narrative;
- enforce same-command replay unless a command change is recorded as a
  justified correction;
- inspect local host transcript JSONL;
- run `canary_transcript_oracle.py` on the resolved transcript;
- run `runtime_signal_audit.py` for the memory-runtime signal;
- run `post_execution_gate.py` before the final claim;
- require host-real evidence before `PASS_TES_CODEX_AGENT_MEMORY_POLICY`;
- downgrade to `NEEDS_POLICY_HOST_CANARY` if the transcript cannot distinguish
  recall from broad docs scanning.

Acceptance:

- `.tes/tes-codex.md` exists in the installed target;
- safe agent-memory source auto-promotes outside hook;
- unsafe source becomes `review_required` or `denied`;
- host runtime surfaces memory without broad docs scan first;
- ledgers record policy, recall, decision, and digest fields;
- hook path remains proposal-only.

Stop state: `PASS_TES_CODEX_AGENT_MEMORY_POLICY`.

## SPEC-007 - Release Identity And Product Boundary

Objective: package the delivered policy behavior without overstating memory
automation.

Required release work when implementation changes delivered behavior:

- bump patch version;
- rebuild local public bundle;
- update SHA and index surfaces;
- update installer/user docs only where adopter-visible behavior changed;
- run source/package/installed gates;
- do not push, tag, publish, or release without explicit owner approval.

Minimum gates:

- `python3 scripts/tes_codex_policy.py --self-test` or equivalent;
- `python3 scripts/cortex_git_tap.py --self-test`;
- `python3 scripts/cortex.py --self-test`;
- `python3 scripts/tes_install.py --self-test`;
- `python3 scripts/install_smoke.py --self-test`;
- `python3 scripts/installed_certification_oracle.py --self-test`;
- `python3 scripts/public_bundle_oracle.py`;
- `python3 scripts/validate_reference_package.py`;
- `python3 scripts/validate_tds.py`;
- `npm run commit:check`;
- host-backed `tes-host-transcript-canary` replay for runtime claims;
- `python3 .agents/skills/tes-host-transcript-canary/scripts/post_execution_gate.py --evidence <sanitized-evidence.json> --json-only`.

## Closeout Decision

Close as `PASS_TES_CODEX_AGENT_MEMORY_POLICY` only when a clean installed target
can prove:

- project policy exists and validates;
- low-risk agent memory auto-promotes outside hook without human item approval;
- risky memory requires review;
- denied memory is blocked;
- runtime recall happens before broad docs scan;
- every promotion or recall is auditable by source digest and policy digest;
- hook-triggered execution cannot perform durable memory writes.

The final decision must come from the `tes-host-transcript-canary` chain. A
source-only green, installed smoke, or narrative report without fresh transcript
hash, runtime signal audit, and post-execution gate is at most a limited
non-host claim.

This SPEC intentionally moves the ceiling from manual curation to governed
agent memory. The human remains policy owner; the agent becomes memory operator.
