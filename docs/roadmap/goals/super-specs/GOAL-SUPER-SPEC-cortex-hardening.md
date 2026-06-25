---
tds_id: roadmap.goal_super_spec_cortex_hardening
tds_class: roadmap
status: active
consumer: maintainers, MCP reviewers, Cortex maintainers, and execution agents
source_of_truth: false
evidence_level: L2
tver: 0.1.0
---

# GOAL Super SPEC: Cortex Hardening Sequence

Status: complete by `docs/evidence/reports/context-mesh/cortex-hardening-2026-05-26/REPORT.md`.

Capability: harden TES Cortex behavior and audit surfaces for three known findings, in strict sequence, with one material commit per execution unit after preflight unless an owner explicitly changes the commit strategy.

## Canonical Artifact

Canonical Super SPEC: `docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-cortex-hardening.md`

Primary runtime and documentation surfaces:

- `scripts/cortex_mcp.py`
- `scripts/install_mcp.py`
- `scripts/cortex.py`
- `scripts/cortex_quality_oracle.py`
- `docs/mesh/CORTEX-MCP.md`
- Cortex evidence reports under `docs/evidence/**` only when a current report or follow-up note is needed.
- TDS and roadmap indexes only when new governed docs are added.

## Certified Context

Current focused baseline observed before this Super SPEC was created:
- `python3 scripts/cortex.py --self-test`: PASS.
- `python3 scripts/cortex_quality_oracle.py --self-test`: PASS.
- `python3 scripts/cortex_mcp.py --self-test`: PASS.
- `python3 scripts/install_mcp.py --self-test`: PASS.
- Broader `npm run commit:check` previously stopped on a private-vocabulary scan of local ignored temporary material. Treat that as a closeout blocker until reproduced and classified during this run.

Known findings to resolve:
1. `P1_MCP_PROJECT_SCOPE`: `scripts/cortex_mcp.py` exposes `target` on every tool and resolves caller-provided paths, allowing a server initialized for one project to read another project's Cortex cell when given that target. This contradicts the project-scoped MCP claim in `docs/mesh/CORTEX-MCP.md`.
2. `P2_MCP_HELPER_DOC_DRIFT`: `docs/mesh/CORTEX-MCP.md` documents a smaller installed helper list than `scripts/install_mcp.py` actually copies. Older evidence also mentions `.tilly/bin` while current runtime uses `.tes/bin`.
3. `P2_REFLECT_UNTRACKED_UNDERCOUNT`: `scripts/cortex.py` `reflect` detects untracked files in changed file count, but `changed_lines` uses `git diff --numstat HEAD`, which does not include untracked files. Large untracked durable changes can trigger capture without triggering the line-budget curation threshold.

## Phase Boundary

This phase may:
- Change local Cortex helper, MCP, and oracle behavior.
- Change governed docs that describe the changed behavior.
- Add deterministic self-tests or fixtures.
- Add current evidence only when needed to make the changed behavior auditable.

This phase must not:
- Add write-capable MCP operations.
- Add global, remote, cloud, marketplace, push, publish, or live sync behavior.
- Change installer release identity without an explicit release decision.
- Move private project names, private paths, product names, storage backends, or canary identifiers into tracked TES content.
- Patch installed target-project mirrors as the source of truth.

## Non-Objectives

- Redesign the whole Cortex model.
- Convert MCP into a multi-project server.
- Introduce new adapters, providers, or package managers.
- Normalize unrelated evidence reports.
- Fix the prior private-vocabulary blocker unless it is required to close this Cortex hardening run.
- Claim commercial-use certification or release sealing.

## Central Rule

Project-scoped Cortex MCP must be mechanically true, not only documented: a server instance initialized for one project cannot read, summarize, list, or otherwise expose another project's Cortex material through caller-provided input.

## Forbidden Moves

- Do not keep accepting arbitrary `target` paths in MCP runtime tools.
- Do not resolve a cross-project path silently.
- Do not update docs to match unsafe behavior.
- Do not make documentation pass by deleting evidence lineage.
- Do not count untracked files as changed files while excluding their durable line count from curation decisions.
- Do not use broad `npm run commit:check` as a substitute for focused Cortex regression tests.
- Do not commit private project vocabulary.
- Do not use destructive Git commands.
- Do not push or publish.

## Materialization Tree

### 1. Canonical Artifact

Use this file as the canonical Super SPEC. The executor must read this file before implementation and preserve the execution queue exactly.

### 2. Certified Context

Use the observed focused Cortex PASS baseline and the three findings above as the known context. Re-run preflight because the worktree may have changed.

### 3. Phase Boundary

Runtime hardening, docs alignment, and focused oracle coverage are in scope. Remote sync, release identity, target-project mirror edits, and new MCP write surfaces are out of scope.

### 4. Non-Objectives

The run is not a Cortex rewrite, not a release, and not a target-project workaround.

### 5. Central Rule

The project-scoped MCP boundary is the highest priority invariant. The docs and tests must describe and enforce the same boundary.

### 6. Forbidden Moves

Forbidden moves are the exact list in this Super SPEC. The executor must add any newly discovered forbidden move to the closeout rather than quietly working around it.

### 7. Execution Units

#### SPEC-000 Preflight And Baseline

Objective: establish the real baseline and file matrix before edits.

Allowed files:
- No material file edits unless a tiny index correction is required to keep this Super SPEC valid.

Forbidden:
- Runtime edits.
- Commits.
- Remote actions.

Owner: main executor.

Focused oracles:
- `git status --short --branch --untracked-files=all`
- `git log --oneline -12`
- `python3 scripts/cortex.py --self-test`
- `python3 scripts/cortex_quality_oracle.py --self-test`
- `python3 scripts/cortex_mcp.py --self-test`
- `python3 scripts/install_mcp.py --self-test`

Negative checks:
- Identify unrelated pending changes and preserve them.
- Identify whether prior `npm run commit:check` private-vocabulary blocker is still present.

Commit: no commit.

Completion evidence:

- Baseline status.
- Focused oracle outputs.
- File matrix for `SPEC-001` through `SPEC-004`.

#### SPEC-001 Pin MCP Target Boundary

Objective: make project-scoped Cortex MCP a runtime-enforced invariant.

Allowed files:

- `scripts/cortex_mcp.py`
- `docs/mesh/CORTEX-MCP.md`
- Focused fixture or self-test code inside existing Cortex MCP test surfaces.
- TDS/index files only if new governed docs are added.

Forbidden:

- New write-capable MCP tools.
- Global project registries.
- Cross-project allowlists.
- Silent fallback to caller-provided external targets.

Owner: runtime implementer, with read-only reviewer.

Focused oracles:

- `python3 scripts/cortex_mcp.py --self-test`
- A negative fixture proving a server initialized for project A cannot read project B through any MCP tool input.
- `python3 scripts/validate_tds.py` if governed docs change.

Negative checks:

- `rg -n '"target"|resolve_target|Path\\(' scripts/cortex_mcp.py docs/mesh/CORTEX-MCP.md` with reviewer classification of valid remaining references.

Semantic commit:

- `fix(cortex): enforce project-scoped mcp target boundary`

Completion evidence:

- Changed files.
- Focused oracle outputs.
- Negative fixture result.
- Reviewer diff result.
- `git show --stat --oneline <commit>`.
- Post-commit `git status --short --branch --untracked-files=all`.
- Sync status.

#### SPEC-002 Align MCP Helper Documentation And Evidence

Objective: align public MCP helper documentation with installer reality and remove stale `.tilly/bin` ambiguity from active guidance.

Allowed files:

- `docs/mesh/CORTEX-MCP.md`
- `scripts/install_mcp.py` only if docs expose an actual installer bug.
- `docs/evidence/**` only for a current follow-up report or scoped correction.
- `docs/tds/DOCS-INDEX.yml`
- `docs/INDEX.md`
- `docs/roadmap/README.md`

Forbidden:

- Deleting historical evidence to hide drift.
- Renaming `.tes/bin` helpers without runtime need.
- Adding helper scripts just to match old docs.
- Mentioning private target projects.

Owner: docs and evidence maintainer, with runtime reviewer for helper list.

Focused oracles:

- `python3 scripts/install_mcp.py --self-test`
- `python3 scripts/validate_tds.py`
- `python3 scripts/validate_reference_graph.py`
- `python3 scripts/validate_doc_size.py`

Negative checks:

- `rg -n '\\.tilly/bin|SERVER_FILES|\\.tes/bin' docs/mesh/CORTEX-MCP.md docs/evidence scripts/install_mcp.py` with reviewer classification of historical versus active references.

Semantic commit:

- `docs(cortex): align mcp helper inventory`

Completion evidence:

- Exact helper list parity explanation.
- Focused oracle outputs.
- Reviewer result.
- `git show --stat --oneline <commit>`.
- Post-commit status.
- Sync status.

#### SPEC-003 Count Untracked Durable Diff In Reflect

Objective: make `reflect` curation threshold account for durable untracked line volume when untracked files are included in the changed-file surface.

Allowed files:

- `scripts/cortex.py`
- `scripts/cortex_quality_oracle.py`
- Focused fixture code inside existing Cortex self-test surfaces.
- Docs only if user-facing semantics change.

Forbidden:

- Counting ignored build/cache/vendor directories as durable signal.
- Replacing Git-based detection with ad hoc full-tree scanning.
- Treating binary untracked files as line-countable text.
- Inflating curation thresholds to hide the bug.

Owner: runtime implementer, with tests reviewer.

Focused oracles:

- A regression fixture with a large durable untracked text file and small `line_budget` that must set `curation_due: true`.
- A regression fixture or assertion showing ignored/private temporary material is not promoted into durable line count.
- `python3 scripts/cortex.py --self-test`
- `python3 scripts/cortex_quality_oracle.py --self-test`

Negative checks:

- `rg -n 'numstat|changed_lines|curation_due|untracked' scripts/cortex.py scripts/cortex_quality_oracle.py` with reviewer classification of intentional semantics.

Semantic commit:

- `fix(cortex): count durable untracked lines for reflect curation`

Completion evidence:

- Focused fixture result.
- Self-test outputs.
- Reviewer result.
- `git show --stat --oneline <commit>`.
- Post-commit status.
- Sync status.

#### SPEC-004 Full Cortex Closeout

Objective: certify the three fixes together without overclaiming release status.

Allowed files:

- Closeout report under `docs/evidence/**` if needed.
- `docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-cortex-hardening.md` only for status update.
- TDS/index files only if new governed docs are added.

Forbidden:

- Release claim.
- Push or publish.
- Empty implementation commits.
- Ignoring a failing focused oracle.

Owner: evidence/oracle maintainer, with read-only reviewer.

Focused oracles:

- `python3 scripts/cortex.py --self-test`
- `python3 scripts/cortex_quality_oracle.py --self-test`
- `python3 scripts/cortex_mcp.py --self-test`
- `python3 scripts/install_mcp.py --self-test`
- `python3 scripts/validate_tds.py`
- `python3 scripts/validate_reference_graph.py`
- `python3 scripts/validate_doc_size.py`
- `git diff --check`
- `npm run commit:check` when private-vocabulary inputs are either clean or explicitly classified as a separate blocker.

Negative checks:

- `rg -n 'target-project|canary-project|real-project|~/Dev/|\\.tilly/bin' docs scripts src` with semantic classification so placeholder policy text is not treated as a violation.
- `rg -n 'push|publish|marketplace|remote sync|write-capable' docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-cortex-hardening.md docs/mesh/CORTEX-MCP.md scripts` with reviewer classification of forbidden action references versus policy text.

Semantic commit:

- `test(cortex): certify mcp and reflect hardening`

Completion evidence:

- Full oracle outputs.
- Known blocker classification if `npm run commit:check` is not green.
- Reviewer result.
- `git show --stat --oneline <commit>`.
- Post-commit status.
- Sync status.

### 8. Subagent Ownership

Subagents are optional. If used, keep them read-only unless their write scope is disjoint and serialized through the main executor.

- Runtime Senior: `scripts/cortex_mcp.py`, `scripts/cortex.py`, focused runtime fixtures.
- Docs/Evidence Senior: `docs/mesh/CORTEX-MCP.md`, governed evidence, TDS index updates.
- Tests Senior: focused self-test fixtures and oracle commands.
- Reviewer Senior: read-only review of scope, private vocabulary, boundary drift, and false closure.

### 9. Per-SPEC Oracles

Use the focused oracles listed in each execution unit. Run the smallest relevant oracle immediately after each material change, then the broader closeout oracle in `SPEC-004`.

### 10. Negative Grep

Negative grep must be semantic:

- Placeholder terms such as `target-project`, `canary-project`, and `real-project` are valid policy vocabulary.
- Blocked-state words are valid when they record a stop condition.
- Forbidden findings are executable bypasses, cross-project reads, stale active `.tilly/bin` guidance, private project vocabulary, and release or remote actions.

### 11. Commit Strategy

- `SPEC-000`: no commit.
- `SPEC-001`, `SPEC-002`, `SPEC-003`, and `SPEC-004`: one local semantic commit per unit after focused oracle and reviewer diff.
- Stage only files for the current unit.
- Do not squash, rebase, rewrite, delete, or mask history.
- Remote sync status defaults to `REMOTE_SYNC_NOT_REQUESTED`.
- Push is forbidden without explicit owner authorization.

### 12. Review Loop

For each material unit:

1. Declare intended files.
2. Apply the smallest change.
3. Run focused oracle.
4. Run negative checks.
5. Review `git diff --check` and unit diff.
6. Commit only the current unit.
7. Capture `git show --stat --oneline <commit>`.
8. Capture post-commit status.
9. Move to the next unit only after the current unit is certified or honestly stopped.

### 13. Stop States

Use these stop states:

- `GO`: unit is implemented, focused oracle is green, reviewer accepted diff, and local commit evidence is captured.
- `NEEDS_REVIEW`: scope, docs, evidence, private vocabulary, or release identity needs owner decision.
- `BLOCKED`: the same blocking condition prevents safe progress after repair attempts or requires external owner input.
- `DEGRADED`: focused behavior improved but a broader non-focused gate remains failing and is classified.
- `FAIL`: focused oracle proves the unit did not meet its contract.

Stop immediately on:

- Cross-project MCP access still possible after `SPEC-001`.
- Helper inventory cannot be reconciled without changing delivered behavior.
- `reflect` still undercounts durable untracked line volume after `SPEC-003`.
- Private vocabulary appears in tracked content outside neutral placeholders.
- Release identity decision is required and not authorized.

### 14. Final Delivery Contract

The final closeout must report:

- Each SPEC id in order.
- Changed files per SPEC.
- Commit hash per material SPEC.
- Focused oracle outputs.
- Negative checks and classifications.
- Any `npm run commit:check` blocker with exact cause.
- Sync status per SPEC.
- Explicit statement that no remote, release, or target-project mirror action was performed.
