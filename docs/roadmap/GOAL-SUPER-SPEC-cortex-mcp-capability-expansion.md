---
tds_id: roadmap.goal_super_spec_cortex_mcp_capability_expansion
tds_class: roadmap
status: active
consumer: maintainers, Cortex MCP authors, host integration authors, release reviewers, and execution agents
source_of_truth: false
evidence_level: L1
tver: 0.1.0
---

# GOAL Super SPEC: Cortex MCP Capability Expansion

Status: active planning artifact; no delivered capability expansion yet.

Capability: materialize ADR 0003 as an incremental Cortex MCP expansion that
improves host integration, schema authoring, hot-path efficiency, progress
visibility, cell history, and optional local HTTP access without changing the
Cortex source of truth, governed write lane, or zero-dependency posture.

## Canonical Artifact

Canonical Super SPEC:
`docs/roadmap/GOAL-SUPER-SPEC-cortex-mcp-capability-expansion.md`

Primary decision source:
`docs/adr/0003-cortex-mcp-capability-expansion.md`

Archived context records:

- `docs/adr/0001-tes-memory-lifecycle.md`
- `docs/adr/0002-cortex-governed-mcp-write-lane.md`

Primary related surfaces:

- `scripts/cortex_mcp.py`
- `scripts/cortex.py`
- `scripts/install_mcp.py`
- `docs/mesh/CORTEX-MCP.md`
- `docs/governance/MAINTAINER-CORRELATION-RULE.md`
- `docs/tds/DOCS-INDEX.yml`
- `docs/INDEX.md`
- `docs/roadmap/README.md`

## Certified Context

Current baseline from ADR 0003:

- `scripts/cortex_mcp.py` is a zero-dependency JSON-RPC 2.0 stdio server.
- The current MCP surface exposes 14 tools, with 12 visible in read-only mode.
- Existing governed write behavior is already certified by current MCP,
  operator, Cortex, event-ledger, installer, TDS, reference-graph, private
  vocabulary, and whitespace oracles.
- ADR 0001 and ADR 0002 are archived bootstrapping records; ADR 0003 owns the
  active Cortex MCP evolution contract.
- Markdown under `docs/agents/cortex/**` remains durable memory truth.
- Runtime indexes, events, checkpoints, resources, prompts, transports, and
  notifications are access, evidence, acceleration, or operator surfaces.

The execution agent must re-run baseline oracles before editing because the
worktree may contain unrelated pending changes.

## Phase Boundary

This phase may:

- Change `scripts/cortex_mcp.py` to add the ADR 0003 capabilities.
- Add focused self-test fixtures inside existing self-test surfaces.
- Update current MCP documentation only where implemented behavior changes.
- Update roadmap, TDS, and index docs only for traceability.
- Use stdlib Python only.
- Commit one material execution unit at a time.

This phase must not:

- Change Cortex Markdown as source of truth.
- Add destructive MCP surfaces.
- Add automatic capture, update, delete, forget, checkpoint write, direct
  apply, multi-target, or multi-tenant MCP behavior.
- Add Pydantic, FastMCP, Smithery, anyio, aiohttp, starlette, fastapi, or a
  third-party HTTP framework.
- Require installer changes for resources, prompts, progress, HTTP, or
  history.
- Push, publish, tag, bundle, or perform remote sync without explicit owner
  authorization.

## Non-Objectives

- Redesign Cortex memory.
- Replace Markdown with a database, service, graph backend, or hosted memory.
- Create a UI.
- Add broad CRUD.
- Add SSE legacy transport.
- Add resources subscribe or writable resources.
- Treat prompts as tool invocations.
- Claim release sealing or commercial certification from this run alone.
- Patch installed target-project mirrors as source of truth.

## Central Rule

Expand MCP access without expanding memory authority:

```text
Markdown is truth.
MCP is access and operation transport.
Governed remember is the only MCP write lane.
Everything new is inert, read-only, advisory, cached, or opt-in transport.
```

## Forbidden Moves

- Do not expose a caller-provided `target` argument.
- Do not write `sources/**` through MCP.
- Do not overwrite existing cells.
- Do not expose delete, update, forget, checkpoint write, direct apply, bulk
  delete, or entity delete.
- Do not add automatic capture from reflection, hooks, resources, prompts, or
  progress.
- Do not add multi-tenant scope arguments such as `user_id`, `agent_id`,
  `app_id`, or `run_id`.
- Do not add a multi-target single process.
- Do not expose `resources/subscribe` or writable resources.
- Do not make prompts call tools.
- Do not introduce third-party dependencies.
- Do not make HTTP default, sessionful, non-localhost by default, or installer
  required.
- Do not mask verify failures through caching.
- Do not treat prior commits as execution credit for this run unless the owner
  explicitly says so.

## Materialization Tree

### 1. Canonical Artifact

Use this file and ADR 0003 as the canonical execution sources. Preserve the
execution units below exactly unless the owner changes the contract.

### 2. Certified Context

Use the current MCP baseline as certified context only. New execution must
create an additive material trail with non-empty commits per material unit.

### 3. Phase Boundary

Runtime MCP capability expansion, focused tests, and correlated documentation
are in scope. Release, remote sync, package publishing, installer behavior
changes, and target-project mirror edits are out of scope unless explicitly
authorized.

### 4. Non-Objectives

The run is not a memory rewrite, not a dependency migration, not a web-service
platform conversion, and not a release.

### 5. Central Rule

Every capability must preserve Cortex source-of-truth and governed-write
invariants while earning certification inside `cortex_mcp.py --self-test`.

### 6. Forbidden Moves

The executor must enforce the forbidden moves listed in this Super SPEC and
ADR 0003. Newly discovered forbidden moves must be reported rather than worked
around silently.

### 7. Execution Units

| Unit | Objective | Files and forbidden moves | Owner | Oracles and negative checks | Commit and evidence |
|------|-----------|---------------------------|-------|-----------------------------|---------------------|
| `SPEC-000` Preflight And Baseline | Establish worktree state, current behavior, unrelated changes, and baseline. | Allowed files: none by default. Forbidden: runtime edits, commits, remote actions. | Main executor. | Run `git status --short --branch --untracked-files=all`, `git log --oneline -12`, `python3 scripts/cortex_mcp.py --self-test`, `python3 scripts/cortex_operator_oracle.py --self-test`, `python3 scripts/event_ledger.py --self-test`, `python3 scripts/install_mcp.py --self-test`, `python3 scripts/cortex.py --self-test`, `python3 scripts/validate_tds.py`, `python3 scripts/validate_reference_graph.py`. Identify unrelated pending changes and confirm prior commits are baseline-only by default. | Commit: none. Evidence: baseline status, oracle results, unrelated-change list, and file matrix for the next unit. |
| `SPEC-001` Schema Helper Without Pydantic | Add declarative schema helper and migrate at least one tool with golden schema equality. | Allowed: `scripts/cortex_mcp.py`, focused fixtures inside self-test, docs only if behavior wording changes. Forbidden: third-party schema libraries, broad rewrites, behavior drift. | Contracts Senior with Tests Senior review. | `python3 scripts/cortex_mcp.py --self-test`; golden schema comparison; `git diff --check`; negative check `rg -n "pydantic|FastMCP|fastmcp|Smithery|BaseModel" scripts/cortex_mcp.py` must show no dependency adoption. | Commit: `refactor(cortex-mcp): add stdlib schema helper`. Evidence: changed files, golden result, focused oracle, reviewer result, commit hash, `git show --stat --oneline <commit>`, post-commit status, sync status. |
| `SPEC-002` Optional HTTP Transport Bridge | Add opt-in stdlib HTTP framing while preserving shared JSON-RPC handler and stdio default. | Allowed: `scripts/cortex_mcp.py`, focused fixtures, `docs/mesh/CORTEX-MCP.md` only for implemented behavior. Forbidden: installer-required HTTP registration, third-party frameworks, non-localhost default bind, sessions, SSE, HTTP default. | Runtime Senior with Security/Boundary Senior review. | `python3 scripts/cortex_mcp.py --self-test`; HTTP POST envelope parity with stdio; non-localhost bind requires explicit flag; read-only and approval semantics sampled over both transports; negative check `rg -n "aiohttp|anyio|starlette|fastapi|uvicorn|sse|ServerSent" scripts/cortex_mcp.py`. | Commit: `feat(cortex-mcp): add optional stdlib http transport`. Evidence: dual-transport oracle, reviewer result, commit hash, `git show --stat --oneline <commit>`, post-commit status, sync status. |
| `SPEC-003` MCP Resources For Cells | Expose cell Markdown as read-only MCP resources. | Allowed: `scripts/cortex_mcp.py`, focused fixtures, `docs/mesh/CORTEX-MCP.md` only for implemented behavior. Forbidden: writable resources, `resources/subscribe`, non-cell resources, rendered content, alternate URI schemes. | Runtime Senior with Reviewer Senior read-only review. | `python3 scripts/cortex_mcp.py --self-test`; `resources/list` equals `cells/**`; `resources/read` matches bytes; non-cell/traversal URIs rejected; stdio/HTTP parity once HTTP exists; negative check `rg -n "resources/subscribe|resources/write|tes-cortex://(?!cells)" scripts/cortex_mcp.py` with reviewer classification. | Commit: `feat(cortex-mcp): expose cells as read-only resources`. Evidence: resource fixture, parity status, reviewer result, commit hash, `git show --stat --oneline <commit>`, post-commit status, sync status. |
| `SPEC-004` Server-side Prompts | Expose inert operator prompt templates through `prompts/list` and `prompts/get`. | Allowed: `scripts/cortex_mcp.py`, focused fixtures, `docs/mesh/CORTEX-MCP.md` only for implemented behavior. Forbidden: prompt-triggered tools, credentials, target-specific paths, mutable prompt behavior. | Contracts Senior with Security/Boundary Senior review. | `python3 scripts/cortex_mcp.py --self-test`; declared prompt set listed; every prompt returns non-empty inert body; no target path or credential markers; stdio/HTTP parity once HTTP exists; prompt-body negative check for `tools/call`, `approval_phrase`, absolute private paths, `token`, `secret`, `password`. | Commit: `feat(cortex-mcp): add inert operator prompts`. Evidence: prompt registry result, negative check, reviewer result, commit hash, `git show --stat --oneline <commit>`, post-commit status, sync status. |
| `SPEC-005` Verify Cache By Mtime | Cache `cortex.verify(target)` by maximum Cortex tree mtime without masking failures. | Allowed: `scripts/cortex_mcp.py`, focused fixtures. Forbidden: disk persistence, watchers, hashing, self-test bypass drift, suppressed verify failures. | Runtime Senior with Tests Senior review. | `python3 scripts/cortex_mcp.py --self-test`; cache hit on repeated calls; touched cell invalidates; key failure falls back uncached; self-test bypasses cache where required; negative check `rg -n "watchdog|inotify|sqlite|write_text\\(|open\\(.+w" scripts/cortex_mcp.py` with reviewer classification. | Commit: `perf(cortex-mcp): cache verify by cortex mtime`. Evidence: hit/invalidation/fallback proof, reviewer result, commit hash, `git show --stat --oneline <commit>`, post-commit status, sync status. |
| `SPEC-006` Progress Notifications | Emit advisory progress notifications for long-running MCP tools. | Allowed: `scripts/cortex_mcp.py`, focused fixtures. Forbidden: cancellation support, notification failure causing tool failure, progress on sub-second handlers, hidden writes. | Runtime Senior with Tests Senior review. | `python3 scripts/cortex_mcp.py --self-test`; at least one `notifications/progress` for an instrumented long tool; simulated notification failure does not fail tool result; stdio/HTTP parity once HTTP exists; negative check for cancellation or progress writes with reviewer classification. | Commit: `feat(cortex-mcp): emit advisory progress notifications`. Evidence: progress fixture, failure-tolerance result, reviewer result, commit hash, `git show --stat --oneline <commit>`, post-commit status, sync status. |
| `SPEC-007` Cell History Tool | Add read-only `cortex_cell_history` that structures existing `TRAIL.md` without a new ledger. | Allowed: `scripts/cortex_mcp.py`, focused fixtures, `docs/mesh/CORTEX-MCP.md` only for implemented behavior. Forbidden: new ledger, writes, target override, traversal, broad history store. | Contracts Senior with Runtime Senior implementation. | `python3 scripts/cortex_mcp.py --self-test`; empty trail returns `PASS` and empty entries; populated trail returns timestamp/evidence/claim/links fields where present; traversal and target override rejected; stdio/HTTP parity once HTTP exists; `rg -n "cell_history|TRAIL|target" scripts/cortex_mcp.py` reviewer classification. | Commit: `feat(cortex-mcp): add read-only cell history tool`. Evidence: history fixture, read-only proof, reviewer result, commit hash, `git show --stat --oneline <commit>`, post-commit status, sync status. |
| `SPEC-008` Documentation, Release Identity, And Final Gate | Align active docs, decide release identity, and run final repository gate. | Allowed: ADR 0003, `docs/mesh/CORTEX-MCP.md`, this Super SPEC, roadmap/index/TDS docs, and package/version/bundle surfaces only if owner authorizes release identity change. Forbidden: sealed claim without `npm run commit:check`, silent version change, push, publish, bundle update without decision. | Docs Senior with Evidence/Oracle Senior review. | `python3 scripts/validate_tds.py`, `python3 scripts/validate_doc_size.py`, `python3 scripts/validate_reference_graph.py`, `python3 scripts/cortex_mcp.py --self-test`, `python3 scripts/install_mcp.py --self-test`, `npm run commit:check`, `git diff --check`; negative grep for dependency/framework/resource-write/destructive/multi-tenant adoption with reviewer classification of policy vocabulary. | Commit: `docs(cortex-mcp): certify capability expansion closeout`. Evidence: full oracle output, release identity decision, reviewer result, commit hash, `git show --stat --oneline <commit>`, post-commit status, sync status. |

### 8. Subagent Ownership

- Main executor owns sequencing, staging, commits, and final decisions.
- Contracts Senior owns schema helper, prompt registry, and history structure.
- Runtime Senior owns HTTP, resources, cache, progress, and handler routing.
- Tests Senior owns focused adversarial fixtures and self-test extensions.
- Security/Boundary Senior reviews authorization, target, prompt, HTTP, and
  dependency boundaries.
- Reviewer Senior is read-only and checks scope, forbidden moves, diff
  ownership, and false closure.
- Evidence/Oracle Senior tracks per-unit evidence and final closeout.

Parallel research or read-only review is allowed. Material writes must be
serialized by SPEC unit, with one certified commit per material unit.

### 9. Per-SPEC Oracles

Focused oracles are listed per unit. The final gate is `npm run commit:check`
only after focused MCP, installer, TDS, reference-graph, doc-size, private
vocabulary, and whitespace gates are green or honestly classified.

### 10. Negative Grep

Negative grep must distinguish rejected-alternative vocabulary from executable
adoption. ADR 0003 may name forbidden patterns as policy. Runtime and docs must
not implement them.

### 11. Commit Strategy

Use one non-empty semantic commit per material SPEC after `SPEC-000`.
Stage only the current SPEC's files. Do not rewrite, squash, rebase, delete
history, or create empty commits to simulate execution. Default sync is local
commit certification; remote sync requires explicit owner authorization.

### 12. Review Loop

For every SPEC:

1. read the current unit and immediate dependencies;
2. declare allowed files;
3. implement the smallest change;
4. run focused oracles;
5. run negative checks;
6. perform read-only reviewer diff;
7. commit only current-unit files;
8. record material-diff and sync evidence;
9. continue only when the unit is green or honestly stopped.

### 13. Stop States

Use `GO` only when all declared material units are committed, focused oracles
and final gate pass, no forbidden move is present, and sync status is recorded.

Use `NEEDS_OWNER_DECISION` when release identity, non-localhost HTTP policy,
installer behavior, public docs, package version, or remote sync needs owner
authorization.

Use `BLOCKED` when a required oracle fails outside the current unit's control.

Use `SAFETY_BLOCKED` when implementation would require secrets, private data,
destructive git, hidden external access, unauthorized remote action, broad
write authority, or dependency adoption forbidden by ADR 0003.

### 14. Final Delivery Contract

Final closeout must report:

- status: `GO`, `NEEDS_OWNER_DECISION`, `BLOCKED`, or `SAFETY_BLOCKED`;
- every SPEC unit executed or explicitly stopped;
- commit hash and sync status per material unit;
- changed files per unit;
- focused and final oracles run;
- negative checks and reviewer result;
- release identity decision;
- boundaries preserved;
- pending owner decisions.

## Release Identity Rule

This Super SPEC alone does not require a package version bump.

Any delivered behavior change to `scripts/cortex_mcp.py`, package commands,
installer-observed behavior, adapter materialization, public docs, generated
bundle content, or adopter-visible runtime behavior requires release identity
review before closure. Default policy is patch bump for delivered behavior
unless the owner explicitly defers it and closeout records the deferral.

## Ready Goal Prompt Source

The maestral `/goal` prompt for this Super SPEC should reference this file
instead of pasting the full contract into the execution context.
